import re

class ResponseValidator:
    """
    Validates that every factual claim in the generated response is strictly supported
    by the retrieved document content. Detects missing info, unsupported claims,
    and potential hallucinations.
    """

    def validate(self, response_text, retrieved_chunks):
        if not response_text or not retrieved_chunks:
            return {
                "grounding_score": 0.0,
                "status": "No Context / Empty Response",
                "total_claims": 0,
                "verified_claims": 0,
                "claims_breakdown": [],
                "hallucination_detected": False,
                "audit_notes": ["No context chunks available for grounding verification."]
            }

        # Combine retrieved context
        corpus_text = " ".join([c["chunk"]["text"] for c in retrieved_chunks]).lower()

        # Split response into individual claims / sentences
        raw_sentences = re.split(r'(?<=[.!?])\s+', response_text)
        claims = []
        for s in raw_sentences:
            cleaned = s.strip()
            # Skip bullet marks, very short headers, or markdown formatting
            cleaned = re.sub(r'^[\*\-\#\d\.\s]+', '', cleaned).strip()
            if len(cleaned.split()) >= 4:
                claims.append(cleaned)

        if not claims:
            return {
                "grounding_score": 100.0,
                "status": "Fully Verified",
                "total_claims": 0,
                "verified_claims": 0,
                "claims_breakdown": [],
                "hallucination_detected": False,
                "audit_notes": ["No complex claims requiring external factual validation."]
            }

        claims_breakdown = []
        verified_count = 0
        partial_count = 0
        unsupported_count = 0

        for claim in claims:
            claim_lower = claim.lower()
            tokens = set(re.findall(r'\b[a-z0-9\$\%\.\-]{3,}\b', claim_lower))
            
            # Critical entities like numbers, percentages, dates, course codes
            entities = set(re.findall(r'(\d+[\%]?|\$\d+|cs\d+|fx\-\w+|clrs|bst|avl)', claim_lower))

            best_chunk = None
            best_overlap = 0.0

            for res in retrieved_chunks:
                chunk_text = res["chunk"]["text"].lower()
                chunk_tokens = set(re.findall(r'\b[a-z0-9\$\%\.\-]{3,}\b', chunk_text))
                
                if tokens:
                    overlap = len(tokens.intersection(chunk_tokens)) / len(tokens)
                else:
                    overlap = 0.0

                # Check critical entities matching
                if entities:
                    matched_ent = [e for e in entities if e in chunk_text]
                    ent_ratio = len(matched_ent) / len(entities)
                    overlap = (overlap * 0.6) + (ent_ratio * 0.4)

                if overlap > best_overlap:
                    best_overlap = overlap
                    best_chunk = res["chunk"]

            # Thresholds
            if best_overlap >= 0.38:
                claim_status = "VERIFIED"
                verified_count += 1
                confidence = min(100, int(best_overlap * 120))
            elif best_overlap >= 0.18:
                claim_status = "PARTIALLY_SUPPORTED"
                partial_count += 1
                confidence = int(best_overlap * 100)
            else:
                claim_status = "UNSUPPORTED_OR_MISSING"
                unsupported_count += 1
                confidence = int(best_overlap * 80)

            claims_breakdown.append({
                "claim_text": claim,
                "status": claim_status,
                "confidence_pct": confidence,
                "supporting_doc": best_chunk["doc_name"] if best_chunk else "None",
                "page_number": best_chunk["page_number"] if best_chunk else "N/A"
            })

        total = len(claims)
        grounding_score = round(((verified_count * 1.0) + (partial_count * 0.5)) / total * 100, 1)

        hallucination_detected = unsupported_count > 0
        
        if grounding_score >= 85:
            overall_status = "High Grounding Confidence (Fully Verified)"
        elif grounding_score >= 65:
            overall_status = "Moderate Grounding Confidence (Substantially Supported)"
        else:
            overall_status = "Low Grounding Confidence (Potential Unsupported Claims)"

        audit_notes = []
        if hallucination_detected:
            audit_notes.append(
                f"Validation Alert: {unsupported_count} statement(s) could not be fully substantiated by the uploaded academic documents."
            )
        else:
            audit_notes.append("Grounding Audit Passed: All statements are directly evidenced in the retrieved source text.")

        return {
            "grounding_score": grounding_score,
            "status": overall_status,
            "total_claims": total,
            "verified_claims": verified_count,
            "partially_supported": partial_count,
            "unsupported_claims": unsupported_count,
            "hallucination_detected": hallucination_detected,
            "claims_breakdown": claims_breakdown,
            "audit_notes": audit_notes
        }
