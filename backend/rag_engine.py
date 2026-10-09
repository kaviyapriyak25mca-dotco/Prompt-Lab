import os
import re
from source_selector import SourceSelector
from validator import ResponseValidator

class RAGEngine:
    def __init__(self, retriever):
        self.retriever = retriever
        self.source_selector = SourceSelector()
        self.validator = ResponseValidator()

    def generate_local_response(self, query, top_chunks, source_decision):
        """
        Deterministic, fully grounded local extraction and synthesis engine.
        Synthesizes accurate academic answers with exact citations and conflict notes.
        Works offline without requiring external API keys.
        """
        primary_doc = source_decision["primary_document"]
        conflict_detected = source_decision["conflict_detected"]
        conflict_details = source_decision["conflict_details"]
        
        # Sort chunks: primary doc chunks first, then by score
        sorted_chunks = sorted(
            top_chunks, 
            key=lambda x: (x["chunk"]["doc_name"] == primary_doc, x["score"]), 
            reverse=True
        )

        # Collect citations
        citations = []
        seen_citations = set()
        for c in sorted_chunks[:4]:
            chunk = c["chunk"]
            cite_key = f"{chunk['doc_name']}_p{chunk['page_number']}"
            if cite_key not in seen_citations:
                seen_citations.add(cite_key)
                # First 120 chars as excerpt
                excerpt = chunk["text"].split("\n")[0][:140] + ("..." if len(chunk["text"]) > 140 else "")
                citations.append({
                    "document": chunk["doc_name"],
                    "page": chunk["page_number"],
                    "section": chunk["section_title"],
                    "academic_year": chunk["academic_year"],
                    "excerpt": excerpt,
                    "relevance_score": c["score"]
                })

        # Synthesize grounded answer
        answer_parts = []
        primary_chunks = [c for c in sorted_chunks if c["chunk"]["doc_name"] == primary_doc]
        if not primary_chunks:
            primary_chunks = sorted_chunks

        top_chunk_text = primary_chunks[0]["chunk"]["text"]
        
        # Format key points from text
        sentences = [s.strip() for s in re.split(r'\n+|\.\s+', top_chunk_text) if len(s.strip()) > 15]
        
        answer_parts.append(f"Based on the official academic documentation from **{primary_doc}**:")
        
        # Add conflict alert if applicable
        if conflict_detected and conflict_details:
            answer_parts.append(
                f"\n> **[POLICY CONFLICT RESOLVED]**\n"
                f"> **Active Rule:** {conflict_details['latest_policy']}\n"
                f"> **Older Rule:** {conflict_details['older_policy']}\n"
                f"> **Resolution Precedence:** {conflict_details['resolution']}\n"
            )

        # Key details
        answer_parts.append("\n**Key Provisions & Retrieved Details:**")
        for s in sentences[:4]:
            if not s.endswith("."):
                s += "."
            answer_parts.append(f"- {s}")

        # Check secondary chunk if adds value
        if len(primary_chunks) > 1:
            sec_text = primary_chunks[1]["chunk"]["text"]
            sec_sentences = [s.strip() for s in re.split(r'\n+|\.\s+', sec_text) if len(s.strip()) > 15]
            for s in sec_sentences[:2]:
                if s not in sentences:
                    if not s.endswith("."):
                        s += "."
                    answer_parts.append(f"- {s}")

        # Citation footer
        answer_parts.append(
            f"\n**Authoritative Source:** *{primary_doc}* (Page {primary_chunks[0]['chunk']['page_number']}, "
            f"Academic Year: {source_decision['primary_academic_year']})."
        )

        return "\n".join(answer_parts), citations

    def generate_gemini_response(self, query, top_chunks, source_decision, api_key):
        """Call Google Gemini Generative AI for fluid, strictly grounded synthesis."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            # Context building
            context_blocks = []
            for idx, c in enumerate(top_chunks):
                chunk = c["chunk"]
                context_blocks.append(
                    f"--- DOCUMENT {idx+1}: {chunk['doc_name']} (Page {chunk['page_number']}, Academic Year: {chunk['academic_year']}) ---\n"
                    f"{chunk['text']}\n"
                )
            context_str = "\n".join(context_blocks)

            conflict_guidance = ""
            if source_decision["conflict_detected"]:
                cd = source_decision["conflict_details"]
                conflict_guidance = (
                    f"\nREGULATORY CONFLICT DETECTED:\n"
                    f"- Topic: {cd['topic']}\n"
                    f"- Latest Policy: {cd['latest_policy']}\n"
                    f"- Older Policy: {cd['older_policy']}\n"
                    f"- Instruction: Prioritize the latest policy. Explicitly note that the older policy is superseded.\n"
                )

            system_prompt = (
                "You are an Academic Document Retrieval AI Assistant.\n"
                "Your objective is to answer academic questions accurately, concisely, and with complete factual grounding.\n"
                "Rules:\n"
                "1. Answer using ONLY information found in the retrieved documents below.\n"
                "2. Explicitly cite the document name and page number for each fact (e.g., '[Academic Regulations 2025, Page 1]').\n"
                "3. If multiple documents conflict, prioritize the latest applicable regulation/notice and explain the superseding rule.\n"
                "4. If a requested detail or fact is missing from the documents, state clearly: 'The retrieved documents do not mention...'\n"
                "5. Do NOT hallucinate or assume unstated institutional policies.\n"
            )

            prompt = (
                f"{system_prompt}\n"
                f"RETRIEVED ACADEMIC CONTEXT:\n{context_str}\n"
                f"{conflict_guidance}\n"
                f"USER QUESTION: {query}\n\n"
                f"ANSWER (Clear, concise, evidence-based with source citations):"
            )

            # Try gemini-1.5-flash or gemini-2.0-flash or fallback
            for model_name in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-pro"]:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    if response and response.text:
                        citations = [
                            {
                                "document": c["chunk"]["doc_name"],
                                "page": c["chunk"]["page_number"],
                                "section": c["chunk"]["section_title"],
                                "academic_year": c["chunk"]["academic_year"],
                                "excerpt": c["chunk"]["text"][:120] + "...",
                                "relevance_score": c["score"]
                            }
                            for c in top_chunks[:4]
                        ]
                        return response.text.strip(), citations
                except Exception as model_err:
                    continue

            # If all model attempts failed, fallback to local
            return self.generate_local_response(query, top_chunks, source_decision)
        except Exception as e:
            # Fallback to local grounded generator
            return self.generate_local_response(query, top_chunks, source_decision)

    def answer_query(self, query, top_k=5, gemini_api_key=None):
        """Full RAG Pipeline: Retrieve -> Select Source -> Generate -> Validate."""
        # 1. Hybrid Retrieval
        retrieved_results = self.retriever.search(query, top_k=top_k)
        
        if not retrieved_results:
            return {
                "query": query,
                "answer": "No relevant academic documents or sections were found matching your inquiry. Please ensure appropriate syllabus, regulation, or notice files are uploaded.",
                "source_decision": {
                    "primary_document": "None",
                    "authority_rationale": "No matching text found.",
                    "conflict_detected": False,
                    "conflict_details": None,
                    "ranked_sources": []
                },
                "citations": [],
                "validation": {
                    "grounding_score": 0.0,
                    "status": "No Retrieved Data",
                    "total_claims": 0,
                    "verified_claims": 0,
                    "claims_breakdown": [],
                    "hallucination_detected": False,
                    "audit_notes": ["No documents retrieved."]
                },
                "retrieved_chunks": []
            }

        # 2. Source Selection & Conflict Resolution
        source_decision = self.source_selector.select_source(query, retrieved_results)

        # 3. Generation (Gemini AI or Grounded Local Engine)
        api_key = gemini_api_key or os.environ.get("GEMINI_API_KEY")
        if api_key and api_key.strip():
            answer, citations = self.generate_gemini_response(query, retrieved_results, source_decision, api_key.strip())
            engine_mode = "Gemini AI (Cloud LLM)"
        else:
            answer, citations = self.generate_local_response(query, retrieved_results, source_decision)
            engine_mode = "Grounded Fact Engine (Local High-Precision)"

        # 4. Response Validation
        validation = self.validator.validate(answer, retrieved_results)

        # Format chunks for inspectability in UI
        formatted_chunks = [
            {
                "chunk_id": r["chunk"]["chunk_id"],
                "doc_name": r["chunk"]["doc_name"],
                "page_number": r["chunk"]["page_number"],
                "section_title": r["chunk"]["section_title"],
                "academic_year": r["chunk"]["academic_year"],
                "score": r["score"],
                "semantic_score": r["semantic_score"],
                "keyword_score": r["keyword_score"],
                "matched_keywords": r["matched_keywords"],
                "text": r["chunk"]["text"]
            }
            for r in retrieved_results
        ]

        return {
            "query": query,
            "engine_mode": engine_mode,
            "answer": answer,
            "source_decision": source_decision,
            "citations": citations,
            "validation": validation,
            "retrieved_chunks": formatted_chunks
        }
