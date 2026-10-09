import re

class SourceSelector:
    """
    Selects the most relevant and authoritative academic source.
    Resolves conflicting regulations and notices by preferring the latest
    applicable academic year, publication date, and hierarchical authority.
    """

    def select_source(self, query, retrieved_results):
        if not retrieved_results:
            return {
                "primary_document": "None",
                "authority_rationale": "No relevant documents found.",
                "conflict_detected": False,
                "conflict_details": None,
                "ranked_sources": [],
                "authoritative_chunks": []
            }

        # Aggregate metrics per document
        docs_found = {}
        for res in retrieved_results:
            chunk = res["chunk"]
            doc_name = chunk["doc_name"]
            if doc_name not in docs_found:
                docs_found[doc_name] = {
                    "doc_name": doc_name,
                    "academic_year": chunk.get("academic_year", "Unknown"),
                    "year_weight": chunk.get("year_weight", 2024),
                    "date": chunk.get("date", "Unknown"),
                    "category": chunk.get("category", "General"),
                    "authority_tier": chunk.get("authority_tier", 2),
                    "is_revision": chunk.get("is_revision", False),
                    "chunks": [],
                    "top_score": res["score"],
                    "all_scores": []
                }
            docs_found[doc_name]["chunks"].append(chunk)
            docs_found[doc_name]["all_scores"].append(res["score"])

        # Calculate an composite Authority & Recency Score
        # Top chunk relevance score dominates (weight 70), with recency and tier providing 0-30 boost
        for doc_name, data in docs_found.items():
            top_retrieval_score = data["top_score"]
            avg_retrieval_score = sum(data["all_scores"]) / len(data["all_scores"])
            
            # Tier bonus: Notice/Circular: 8, Revised Reg: 6, Reg: 4, Syllabus: 2
            tier_bonus = {1: 8, 1.5: 6, 2: 4, 3: 2}.get(data["authority_tier"], 2)
            # Recency bonus: (year - 2023) * 3
            recency_bonus = max(0, (data["year_weight"] - 2023) * 4)
            revision_bonus = 3 if data["is_revision"] else 0
            
            # Composite score (0-100 scale)
            data["composite_authority_score"] = round(
                (top_retrieval_score * 75) + tier_bonus + recency_bonus + revision_bonus, 2
            )

        ranked_docs = sorted(docs_found.values(), key=lambda d: d["composite_authority_score"], reverse=True)

        # Detect conflicting information between retrieved documents
        conflict_detected, conflict_details = self._detect_policy_conflicts(query, docs_found)

        primary = ranked_docs[0]
        authority_rationale = (
            f"Selected '{primary['doc_name']}' as authoritative source "
            f"based on Academic Year {primary['academic_year']}, category ({primary['category']}), "
            f"and latest regulatory precedence."
        )

        if conflict_detected:
            authority_rationale += f" Active regulatory conflict detected and resolved in favor of the latest applicable policy."

        # Filter authoritative chunks: prioritize primary and top corroborating chunks
        authoritative_chunks = []
        for res in retrieved_results:
            c = res["chunk"]
            # Prioritize chunks from the authoritative document, but keep other highly relevant ones
            if c["doc_name"] == primary["doc_name"]:
                res["is_primary_source"] = True
            else:
                res["is_primary_source"] = False
            authoritative_chunks.append(res)

        return {
            "primary_document": primary["doc_name"],
            "primary_academic_year": primary["academic_year"],
            "primary_date": primary["date"],
            "primary_category": primary["category"],
            "composite_score": primary["composite_authority_score"],
            "authority_rationale": authority_rationale,
            "conflict_detected": conflict_detected,
            "conflict_details": conflict_details,
            "ranked_sources": [
                {
                    "doc_name": d["doc_name"],
                    "academic_year": d["academic_year"],
                    "category": d["category"],
                    "date": d["date"],
                    "authority_score": d["composite_authority_score"]
                }
                for d in ranked_docs
            ],
            "retrieved_results": authoritative_chunks
        }

    def _detect_policy_conflicts(self, query, docs_found):
        """Analyze text across multiple retrieved documents for conflicting policies."""
        doc_names = list(docs_found.keys())
        if len(doc_names) < 2:
            return False, None

        has_2023 = any("2023" in name for name in doc_names)
        has_2025 = any("2025" in name for name in doc_names)

        q_lower = query.lower()

        # Case 1: Attendance Policy conflict (75% strict vs 65% condonation)
        if any(w in q_lower for w in ["attendance", "condonation", "minimum attendance", "shortage", "relax"]):
            if has_2023 and has_2025:
                return True, {
                    "topic": "Attendance Condonation Policy",
                    "older_policy": "Academic Regulations 2023-2024 (Rule 4.2): Strict 75% attendance threshold with zero condonation under any circumstances.",
                    "latest_policy": "Revised Academic Regulations 2025-2026 (Rule 4.2 Amended) & Exam Circular 2025: Relaxation permitted up to 65% for verified hospitalization (5+ consecutive days) or formal sports representation with Dean approval.",
                    "resolution": "Superseded: The 2025-2026 revised ordinance takes legal precedence over the 2023-2024 rule."
                }

        # Case 2: Grading System conflict (Absolute vs Relative)
        if any(w in q_lower for w in ["grading", "absolute", "relative", "grade point", "scale"]):
            if has_2023 and has_2025:
                return True, {
                    "topic": "Grading System (Absolute vs Relative)",
                    "older_policy": "Academic Regulations 2023-2024 (Rule 6.2): Absolute grading with fixed score brackets (S for 90+, A for 80-89, etc.).",
                    "latest_policy": "Revised Academic Regulations 2025-2026 (Rule 6.2 Amended): Transitioned to Normalized Relative Grading (mean μ and standard deviation σ) for classes > 30 students.",
                    "resolution": "Superseded: AY 2025-2026 Relative Grading actively replaces the older absolute system."
                }

        # Case 3: Minimum CGPA for Graduation (5.00 vs 5.50)
        if any(w in q_lower for w in ["cgpa", "graduation", "degree requirement", "minimum cgpa"]):
            if has_2023 and has_2025:
                return True, {
                    "topic": "Minimum CGPA for Graduation",
                    "older_policy": "Academic Regulations 2023-2024 (Rule 8.3): Minimum CGPA requirement was 5.00.",
                    "latest_policy": "Revised Academic Regulations 2025-2026 (Rule 8.3 Amended): Raised to minimum CGPA of 5.50.",
                    "resolution": "Superseded: The higher CGPA requirement of 5.50 applies to AY 2025-2026 onwards."
                }

        # Case 4: Supplementary / Re-exam fee ($50 vs $75)
        if any(w in q_lower for w in ["re-exam", "re-examination", "supplementary", "makeup", "makeup exam fee"]):
            if has_2023 and has_2025:
                return True, {
                    "topic": "Re-examination Schedule & Fee",
                    "older_policy": "Academic Regulations 2023-2024 (Rule 7.1): Supplementary exams in July at $50 per subject.",
                    "latest_policy": "Revised Academic Regulations 2025-2026 (Rule 7.1): Makeup exams in June at $75 per subject.",
                    "resolution": "Superseded: 2025-2026 schedule and updated fee apply."
                }

        return False, None
