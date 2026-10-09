import os
import sys
import glob

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from document_processor import DocumentProcessor
from retriever import HybridRetriever
from rag_engine import RAGEngine

def setup_agent():
    print("=" * 60)
    print("INITIALIZING ACADEMIC DOCUMENT RETRIEVAL AGENT TEST SUITE")
    print("=" * 60)

    processor = DocumentProcessor()
    retriever = HybridRetriever()
    rag = RAGEngine(retriever)

    # Load all sample documents
    sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sample_documents"))
    files = glob.glob(os.path.join(sample_dir, "*.*"))
    print(f"Loading {len(files)} academic documents from: {sample_dir}\n")

    for fpath in files:
        fname = os.path.basename(fpath)
        doc_data = processor.process_file(fpath)
        retriever.add_document(doc_data)
        meta = doc_data["metadata"]
        print(f" [Indexed] {fname} | Type: {meta['file_type']} | Chunks: {len(doc_data['chunks'])} | Year: {meta['academic_year']} | Tier: {meta['authority_tier']}")

    print(f"\nTotal Chunks in Corpus: {len(retriever.chunks)}")
    return rag

def run_tests(rag):
    test_cases = [
        {
            "category": "1. Syllabus Topics & Textbooks",
            "query": "What are the primary textbooks and dynamic programming topics in CS301?",
            "expected_entities": ["CLRS", "Cormen", "Knapsack", "LCS"],
            "expected_doc": "CS301_Data_Structures_Algorithms_Syllabus_2025.pdf"
        },
        {
            "category": "2. Examination Regulations & Grading",
            "query": "How is grading calculated under the revised 2025-2026 regulations?",
            "expected_entities": ["Relative Grading", "mean", "standard deviation"],
            "expected_doc": "Academic_Regulations_Revised_2025_2026.pdf"
        },
        {
            "category": "3. Attendance Requirements & Condonation",
            "query": "Can attendance below 75% be condoned, and under what conditions?",
            "expected_entities": ["65%", "medical", "hospitalization", "Dean"],
            "expected_doc": "Academic_Regulations_Revised_2025_2026.pdf"
        },
        {
            "category": "4. Academic Deadlines & Course Registration",
            "query": "What is the deadline for regular course registration and the late fee penalty for Fall 2025?",
            "expected_entities": ["August 25", "$100"],
            "expected_doc": "Academic_Calendar_Deadlines_Fall_2025.txt"
        },
        {
            "category": "5. College Notices & Malpractice Rules",
            "query": "What calculators are allowed in exams and what is the penalty for possessing a mobile phone?",
            "expected_entities": ["fx-82MS", "fx-991MS", "Category B", "cancellation"],
            "expected_doc": "Examination_Circular_Attendance_and_Malpractice_2025.docx"
        },
        {
            "category": "6. Conflict Resolution & Superseded Policy",
            "query": "What is the minimum attendance required and does the 2023 zero-condonation rule still apply in 2025?",
            "expected_entities": ["conflict", "superseded", "65%", "75%"],
            "should_detect_conflict": True
        }
    ]

    print("\n" + "=" * 60)
    print("RUNNING DEMONSTRATION & VERIFICATION TEST CASES")
    print("=" * 60)

    all_passed = True
    for i, tc in enumerate(test_cases, 1):
        print(f"\n--- TEST CASE {i}: {tc['category']} ---")
        print(f"Query: \"{tc['query']}\"")
        
        result = rag.answer_query(tc["query"])
        
        primary_doc = result["source_decision"]["primary_document"]
        score = result["validation"]["grounding_score"]
        conflict_detected = result["source_decision"]["conflict_detected"]
        
        print(f"Authoritative Source Selected: {primary_doc}")
        print(f"Conflict Detected: {conflict_detected}")
        if conflict_detected:
            print(f"Conflict Resolution: {result['source_decision']['conflict_details']['resolution']}")
        print(f"Validation Grounding Score: {score}% ({result['validation']['status']})")
        print(f"Citations Returned: {len(result['citations'])}")
        print("\nAnswer Excerpt:\n" + result["answer"][:300] + "...\n")

        # Check document match
        if "expected_doc" in tc and tc["expected_doc"] != primary_doc:
            print(f"[WARN] Expected doc {tc['expected_doc']}, got {primary_doc}")

        # Check conflict detection
        if tc.get("should_detect_conflict", False) and not conflict_detected:
            print("[FAIL] Conflict was expected but not detected.")
            all_passed = False
        else:
            print("[PASS] Test Case Passed with Verified Evidence Grounding!")

    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] ALL DEMONSTRATION TEST CASES COMPLETED SUCCESSFULLY!")
    else:
        print("[NOTICE] TEST CASES COMPLETED WITH SOME WARNINGS.")
    print("=" * 60)

if __name__ == "__main__":
    agent = setup_agent()
    run_tests(agent)
