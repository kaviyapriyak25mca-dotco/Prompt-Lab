# Academic Document Retrieval Agent

An AI-powered, evidence-grounded **Academic Document Retrieval Agent** developed for university ecosystems. The agent answers academic queries by retrieving and synthesizing context from syllabus documents, academic ordinances/regulations, and official circulars/notices while strictly validating facts, identifying authoritative sources, resolving policy conflicts, and preventing hallucinations.

---

## 🌟 Key Capabilities & Requirements Implemented

1. **Multi-Format Document Ingestion & Smart Chunking**:
   - Parses `.pdf` (page-by-page text extraction with `pypdf`), `.docx` (section/heading hierarchy with `python-docx`), and `.txt` files.
   - Extracts metadata automatically: Academic Year (e.g., `2025-2026`, `2023-2024`), publication dates, document classification (Syllabus, Regulations, Urgent Circular), and authority tier.
   - Overlapping semantic sliding window chunking preserving exact document names and page numbers.

2. **Hybrid Document Retrieval (Semantic + Keyword Matching)**:
   - Combines sublinear TF-IDF word n-grams and character n-grams with cosine vector similarity.
   - Exact term and entity boosting for course codes (`CS301`), numeric criteria (`75%`, `65%`, `5.50`), and calculator models (`Casio fx-82MS`).
   - Authority and recency calibration prioritizing newer regulations and active circulars.

3. **Source Selection & Conflict Resolution**:
   - Compares academic years (`AY 2025-2026` vs `AY 2023-2024`), publication dates, and hierarchy of authority (Urgent Notices > Revised Regulations > Standard Regulations > Course Handouts).
   - Automatically detects regulatory conflicts (e.g., strict 75% attendance without condonation in 2023 vs 65% condonation for medical/sports in 2025; Absolute grading vs Relative grading; Graduation CGPA 5.0 vs 5.5).
   - Marks newer ordinances as legally superseding older policies and explains the precedence rationale.

4. **Retrieval-Augmented Generation (RAG)**:
   - Dual execution engine:
     - **Built-in High-Precision Grounded Fact Engine**: Runs 100% locally with zero external API dependencies or latency.
     - **Google Gemini Generative AI**: Optional cloud LLM synthesis (`gemini-1.5-flash` / `gemini-2.0-flash`) with strict grounding prompts.

5. **Response Validation & Grounding Audit**:
   - Sentence-by-sentence claim decomposition.
   - Cross-references each statement against retrieved context chunks.
   - Computes an Evidentiary Grounding Score (0 - 100%) and flags potential hallucinations or missing information.

6. **Interactive Web Interface**:
   - Modern glassmorphic dark theme built with vanilla CSS and responsive design.
   - Document upload dropzone (PDF, DOCX, TXT), active corpus cards, and raw chunk inspector.
   - Quick-action test buttons for all academic domains.
   - Conflict resolution banner, validation progress meter, and source citation cards with page numbers.

---

## 📂 Architecture & Directory Structure

```
c:\Users\Student\Documents\PE LAB\
├── backend/
│   ├── app.py                     # Flask REST API server & frontend router
│   ├── document_processor.py      # PDF, DOCX, TXT text extraction, metadata detection, and chunking
│   ├── retriever.py               # Hybrid semantic + lexical retrieval engine
│   ├── source_selector.py         # Source prioritization & policy conflict resolver
│   ├── rag_engine.py              # Dual RAG synthesis engine (Local Fact Engine + Gemini AI)
│   ├── validator.py               # Sentence claim verification & grounding audit
│   ├── sample_data_generator.py   # Generates realistic sample academic documents
│   └── test_agent.py              # Automated programmatic test suite
├── sample_documents/             # Realistic academic files
│   ├── Academic_Regulations_2023_2024.pdf
│   ├── Academic_Regulations_Revised_2025_2026.pdf
│   ├── CS301_Data_Structures_Algorithms_Syllabus_2025.pdf
│   ├── Academic_Calendar_Deadlines_Fall_2025.txt
│   └── Examination_Circular_Attendance_and_Malpractice_2025.docx
├── frontend/
│   ├── index.html                 # Modern single-page interface
│   ├── style.css                  # Custom styling (glassmorphism, color palette, animations)
│   └── app.js                     # Client logic (uploads, live search, claims inspector, citations)
├── run.py                         # Application launcher script
└── README.md                      # Comprehensive documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9+ (or Anaconda)
- Required packages (already installed):
  ```bash
  pip install --user pypdf python-docx scikit-learn reportlab flask flask-cors google-generativeai
  ```

### 2. Run the Automated Test Suite
To verify the retrieval agent across all 6 test scenarios (including conflict resolution and factual grounding):
```powershell
python backend/test_agent.py
```

### 3. Launch the Web Interface & Server
To start the backend server and web application:
```powershell
python run.py
```
Open your browser and navigate to:
**`http://127.0.0.1:5000`**

---

## 🧪 Demonstration & Test Cases Walkthrough

| # | Academic Domain | Sample Query | Selected Authoritative Document | Expected Key Findings |
|---|---|---|---|---|
| **1** | **Syllabus & References** | *"What are the primary textbooks and dynamic programming topics in CS301?"* | `CS301_Data_Structures_Algorithms_Syllabus_2025.pdf` | Cormen (CLRS) 4th Ed, Mark Allen Weiss; 0/1 Knapsack, LCS, Matrix Chain Multiplication. |
| **2** | **Examination Regulations** | *"How is grading calculated under the revised 2025-2026 regulations?"* | `Academic_Regulations_Revised_2025_2026.pdf` | Normalized Relative Grading based on class mean ($\mu$) and standard deviation ($\sigma$). |
| **3** | **Attendance Condonation** | *"Can attendance below 75% be condoned, and under what conditions?"* | `Academic_Regulations_Revised_2025_2026.pdf` | Relaxed up to 65% for verified hospitalization ($5+$ days) or sports representation with Dean approval. |
| **4** | **Academic Deadlines** | *"What is the deadline for regular course registration and the late fee penalty for Fall 2025?"* | `Academic_Calendar_Deadlines_Fall_2025.txt` | Regular registration ends August 25, 2025; late fee fine is $100 up to September 2, 2025. |
| **5** | **College Notices & Malpractice** | *"What calculators are allowed in exams and what is the penalty for possessing a mobile phone?"* | `Examination_Circular_Attendance_and_Malpractice_2025.docx` | Allowed: Non-programmable Casio fx-82MS, fx-991MS; Mobile penalty: Category B malpractice (cancellation of all exams). |
| **6** | **Conflict Resolution** | *"What is the minimum attendance required and does the 2023 zero-condonation rule still apply in 2025?"* | `Academic_Regulations_Revised_2025_2026.pdf` | **Conflict Detected:** 2023 absolute 75% rule was superseded by 2025-2026 ordinance permitting 65% condonation. |

---

## 📡 REST API Reference

- **`GET /api/documents`**: Returns metadata and chunk counts for all indexed documents.
- **`GET /api/chunks?doc_name=<name>`**: Returns individual text chunks with page numbers.
- **`POST /api/upload`**: Multipart file upload (`.pdf`, `.docx`, `.txt`) with instantaneous chunking and indexing.
- **`POST /api/query`**: Executes hybrid retrieval, source selection, RAG answer generation, and grounding validation.
  ```json
  {
    "query": "What is the minimum attendance requirement?",
    "top_k": 5,
    "gemini_api_key": ""
  }
  ```
- **`POST /api/reset`**: Restores the default sample document repository.
- **`GET /api/stats`**: Returns corpus statistics.
