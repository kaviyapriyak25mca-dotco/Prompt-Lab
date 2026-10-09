import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from docx import Document

SAMPLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sample_documents"))
os.makedirs(SAMPLE_DIR, exist_ok=True)

def create_pdf_page_helper(c, title, doc_meta, page_num, total_pages=3):
    width, height = letter
    # Header bar
    c.setFillColor(colors.HexColor("#1e293b"))
    c.rect(0, height - 55, width, 55, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, height - 35, title)
    c.setFont("Helvetica", 9)
    c.drawString(40, height - 48, doc_meta)
    
    # Footer
    c.setStrokeColor(colors.HexColor("#cbd5e1"))
    c.line(40, 40, width - 40, 40)
    c.setFillColor(colors.HexColor("#64748b"))
    c.setFont("Helvetica", 9)
    c.drawString(40, 26, "Official Academic Repository - Confidential & Authoritative Record")
    c.drawRightString(width - 40, 26, f"Page {page_num} of {total_pages}")


def generate_regulations_2023():
    pdf_path = os.path.join(SAMPLE_DIR, "Academic_Regulations_2023_2024.pdf")
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    meta = "Document: NIT-ACAD-REG-2023 | Effective: Academic Year 2023-2024 | Published: August 1, 2023"
    
    # Page 1
    create_pdf_page_helper(c, "Academic Regulations & Ordinances (2023-2024)", meta, 1, 2)
    y = height - 85
    c.setFillColor(colors.HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Section 1: Preamble and Scope")
    y -= 18
    c.setFont("Helvetica", 10)
    text1 = [
        "These regulations govern undergraduate and postgraduate degree programmes for the academic session 2023-2024.",
        "All enrolled candidates shall abide strictly by the ordinances promulgated herein.",
        "",
        "Section 2: Attendance Requirements (Rule 4.1 - 2023 Policy)",
        "Rule 4.1: A student must maintain a minimum attendance of 75% in each registered course (lectures, tutorials,",
        "and laboratory sessions) to be eligible to appear for the end-semester final examinations.",
        "Rule 4.2: Under no circumstances will any condonation or relaxation below 75% be granted under the 2023 policy.",
        "Students having attendance between 0% and 74.9% shall be awarded an 'FA' (Failure due to Attendance shortage)",
        "grade and must reregister for the course in subsequent academic years.",
        "",
        "Section 3: Grading Scheme (Rule 6.2 - Absolute Grading)",
        "Rule 6.2: The institute follows an Absolute Grading Scale based on the following fixed score brackets:",
        "  - Grade 'S' (Outstanding): 90% and above (Grade Points: 10)",
        "  - Grade 'A' (Excellent): 80% to 89% (Grade Points: 9)",
        "  - Grade 'B' (Very Good): 70% to 79% (Grade Points: 8)",
        "  - Grade 'C' (Good): 60% to 69% (Grade Points: 7)",
        "  - Grade 'D' (Satisfactory): 50% to 59% (Grade Points: 6)",
        "  - Grade 'F' (Fail): Below 50% (Grade Points: 0)",
        "Pass percentage requires a minimum aggregate of 50% in each subject."
    ]
    for line in text1:
        if line.startswith("Section"):
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(colors.HexColor("#1e3a8a"))
        elif line.startswith("Rule"):
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(colors.HexColor("#0f172a"))
        else:
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.HexColor("#334155"))
        c.drawString(40, y, line)
        y -= 16
    c.showPage()
    
    # Page 2
    create_pdf_page_helper(c, "Academic Regulations & Ordinances (2023-2024)", meta, 2, 2)
    y = height - 85
    text2 = [
        "Section 4: Re-examinations and Supplementary Tests",
        "Rule 7.1: A student securing an 'F' grade in any course may appear for a Supplementary Examination conducted",
        "once annually during the summer break (July). A non-refundable re-examination fee of $50 per subject applies.",
        "Rule 7.2: Students are permitted a maximum of 4 active backlog papers at any given time.",
        "",
        "Section 5: Graduation and Degree Criteria",
        "Rule 8.3: Minimum Cumulative Grade Point Average (CGPA) required for the conferral of the B.Tech Degree is 5.00.",
        "Students failing to achieve a CGPA of 5.00 within the maximum permitted duration of 6 academic years shall",
        "forfeit their degree candidature."
    ]
    for line in text2:
        if line.startswith("Section"):
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(colors.HexColor("#1e3a8a"))
        elif line.startswith("Rule"):
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(colors.HexColor("#0f172a"))
        else:
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.HexColor("#334155"))
        c.drawString(40, y, line)
        y -= 16
    c.showPage()
    c.save()
    print("Created:", pdf_path)


def generate_regulations_2025():
    pdf_path = os.path.join(SAMPLE_DIR, "Academic_Regulations_Revised_2025_2026.pdf")
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    meta = "Document: NIT-ACAD-REG-REV-2025 | Effective: Academic Year 2025-2026 | Published: July 15, 2025"
    
    # Page 1
    create_pdf_page_helper(c, "Revised Academic Regulations (2025-2026)", meta, 1, 2)
    y = height - 85
    text1 = [
        "Executive Order & Amendment Notice:",
        "This document supersedes all prior ordinances including the 2023-2024 regulations regarding attendance, grading,",
        "and degree requirements for all students enrolled from Academic Year 2025-2026 onwards.",
        "",
        "Section 1: Revised Attendance Policy & Medical/Sports Condonation (Rule 4.1 Amended 2025)",
        "Rule 4.1 (Revised 2025): Regular attendance requirement remains 75% in each registered course.",
        "Rule 4.2 (Condonation Clause): In exceptional cases, a student who has attendance between 65% and 74.9% may",
        "be granted Attendance Condonation under the following strictly verified circumstances:",
        "  (a) Documented Medical Emergency: Hospitalization of at least 5 consecutive days verified by Institute Health Center.",
        "  (b) Institutional Sports or Academic Representation: Formal participation in AIU/National events approved by Dean.",
        "Rule 4.3: Applications for condonation must be submitted with valid medical/participation certificates to the Head",
        "of Department within 7 calendar days of resumption of classes and approved by the Dean (Academic Affairs).",
        "No condonation shall ever be granted below 65% under any circumstances.",
        "",
        "Section 2: Transition to Relative Grading System (Rule 6.2 Amended 2025)",
        "Rule 6.2 (Revised 2025): Starting Academic Year 2025-2026, the institute has abolished absolute grading for all courses",
        "with class strength exceeding 30 students, replacing it with a Normalized Relative Grading System.",
        "Grades are calculated using the class mean (μ) and standard deviation (σ):",
        "  - Grade 'O' (Outstanding): Marks >= μ + 1.5σ",
        "  - Grade 'A+' (Excellent): μ + 1.0σ <= Marks < μ + 1.5σ",
        "  - Grade 'A' (Very Good): μ + 0.5σ <= Marks < μ + 1.0σ",
        "  - Grade 'B+' (Good): μ <= Marks < μ + 0.5σ",
        "  - Grade 'B' (Above Average): μ - 0.5σ <= Marks < μ",
        "  - Grade 'C' (Average / Pass): μ - 1.0σ <= Marks < μ - 0.5σ (Minimum passing score)",
        "  - Grade 'F' (Fail): Marks < μ - 1.0σ or Marks < 35% absolute cutoff."
    ]
    for line in text1:
        if line.startswith("Section") or line.startswith("Executive"):
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(colors.HexColor("#1e3a8a"))
        elif line.startswith("Rule"):
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(colors.HexColor("#0f172a"))
        else:
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.HexColor("#334155"))
        c.drawString(40, y, line)
        y -= 15
    c.showPage()
    
    # Page 2
    create_pdf_page_helper(c, "Revised Academic Regulations (2025-2026)", meta, 2, 2)
    y = height - 85
    text2 = [
        "Section 3: Summer Makeup Examination Policy",
        "Rule 7.1 (Revised 2025): Makeup examinations will be held in June for candidates who received an 'F' grade or",
        "who were unable to write exams due to approved medical leave. Fee per course is $75.",
        "A maximum of 3 courses can be registered during summer makeup terms.",
        "",
        "Section 4: Revised Graduation Minimum CGPA",
        "Rule 8.3 (Revised 2025): Effective Academic Year 2025-2026, the minimum cumulative grade point average (CGPA)",
        "required for eligibility to receive the B.Tech Degree is raised to 5.50 (increased from 5.00 in earlier regulations).",
        "Students with CGPA between 5.00 and 5.49 must register for grade improvement courses."
    ]
    for line in text2:
        if line.startswith("Section"):
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(colors.HexColor("#1e3a8a"))
        elif line.startswith("Rule"):
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(colors.HexColor("#0f172a"))
        else:
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.HexColor("#334155"))
        c.drawString(40, y, line)
        y -= 16
    c.showPage()
    c.save()
    print("Created:", pdf_path)


def generate_syllabus_cs301():
    pdf_path = os.path.join(SAMPLE_DIR, "CS301_Data_Structures_Algorithms_Syllabus_2025.pdf")
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    meta = "Document: CSE-SYLLABUS-CS301 | Academic Year: 2025-2026 | Credits: 4 (3L + 1T + 2P)"
    
    # Page 1
    create_pdf_page_helper(c, "CS301: Data Structures and Algorithms - Syllabus 2025", meta, 1, 2)
    y = height - 85
    text1 = [
        "Course Overview and Objectives:",
        "CS301 delivers foundational knowledge of core computational structures, design techniques, and algorithm complexity.",
        "Prerequisites: CS101 Programming in C / C++ and MA102 Discrete Mathematics.",
        "",
        "Module 1: Foundations and Asymptotic Analysis (8 Hours)",
        "- Growth of Functions and Asymptotic notations: Big-O, Big-Omega, Big-Theta, Little-o, Little-omega.",
        "- Recurrence Relations: Substitution method, Recursion Tree method, and Master Theorem.",
        "- Abstract Data Types (ADTs): Stacks, Queues, Circular Queues, Deque, Priority Queues.",
        "- Applications: Infix to Postfix expression conversion, evaluation, balanced parenthesis verification.",
        "",
        "Module 2: Non-Linear Structures - Trees and Heaps (10 Hours)",
        "- Binary Tree traversals (Inorder, Preorder, Postorder, Level order).",
        "- Binary Search Trees (BST): Insertion, Deletion, Searching, Successor/Predecessor operations.",
        "- Balanced BSTs: AVL Trees (Single and Double rotations), Red-Black Tree invariant properties.",
        "- Multiway Search Trees: B-Trees and B+ Trees (node splitting, merging, indexing fundamentals).",
        "- Priority Queues: Binary Min-Heap and Max-Heap, Heapify algorithm, HeapSort (O(n log n) runtime).",
        "",
        "Module 3: Graph Representations and Traversal Algorithms (10 Hours)",
        "- Representations: Adjacency Matrix, Adjacency List, Compressed Sparse Row (CSR).",
        "- Graph Traversal: Breadth-First Search (BFS) and Depth-First Search (DFS), Classification of edges.",
        "- Topological Sorting (Kahn's algorithm and DFS-based) and Cycle detection in directed/undirected graphs.",
        "- Minimum Spanning Trees (MST): Kruskal's algorithm (Disjoint Set Union) and Prim's algorithm.",
        "- Single-Source Shortest Paths: Dijkstra's Algorithm (with priority queue), Bellman-Ford (negative weight detection).",
        "- All-Pairs Shortest Path: Floyd-Warshall Algorithm (O(V^3))."
    ]
    for line in text1:
        if line.startswith("Module") or line.startswith("Course"):
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(colors.HexColor("#1e3a8a"))
        else:
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.HexColor("#334155"))
        c.drawString(40, y, line)
        y -= 15
    c.showPage()
    
    # Page 2
    create_pdf_page_helper(c, "CS301: Data Structures and Algorithms - Syllabus 2025", meta, 2, 2)
    y = height - 85
    text2 = [
        "Module 4: Algorithm Design Paradigms (10 Hours)",
        "- Greedy Paradigm: Optimal substructure and greedy-choice property. Fractional Knapsack, Huffman coding.",
        "- Dynamic Programming: Principle of Optimality, Memoization vs Tabulation. 0/1 Knapsack, Longest Common",
        "  Subsequence (LCS), Matrix Chain Multiplication, Subset Sum problem.",
        "- Divide and Conquer: MergeSort, QuickSort (randomized pivot selection, worst vs average case analysis).",
        "",
        "Textbooks and Prescribed References:",
        "1. Primary Textbook: 'Introduction to Algorithms' by Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest,",
        "   and Clifford Stein (CLRS), 4th Edition, MIT Press, 2022.",
        "2. Reference Book 1: 'Data Structures and Algorithm Analysis in C++' by Mark Allen Weiss, 4th Edition, Pearson.",
        "3. Reference Book 2: 'Algorithm Design' by Jon Kleinberg and Eva Tardos, 1st Edition, Pearson.",
        "",
        "Assessment and Examination Scheme:",
        "- Continuous Internal Assessment (CIA): 30% (Mid-Semester Exam)",
        "- Laboratory Practical Assignments & Code Reviews: 20%",
        "- Course Capstone Project: 10%",
        "- End-Semester Final Examination: 40% (Comprehensive Theory, 3 Hours Duration)",
        "- Passing Minimum: 40% overall aggregate marks across theory and laboratory components."
    ]
    for line in text2:
        if line.startswith("Module") or line.startswith("Textbooks") or line.startswith("Assessment"):
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(colors.HexColor("#1e3a8a"))
        else:
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.HexColor("#334155"))
        c.drawString(40, y, line)
        y -= 15
    c.showPage()
    c.save()
    print("Created:", pdf_path)


def generate_calendar_notice():
    txt_path = os.path.join(SAMPLE_DIR, "Academic_Calendar_Deadlines_Fall_2025.txt")
    content = """================================================================================
OFFICE OF THE DEAN (ACADEMIC AFFAIRS)
CENTRAL NOTIFICATION: ACADEMIC CALENDAR & CRITICAL DEADLINES - FALL SEMESTER 2025
Notification Ref: NIT/ACAD/NOT/2025-08/14
Published Date: August 10, 2025
Applicability: All B.Tech, M.Tech, and Research Scholars (Academic Year 2025-2026)
================================================================================

All students, faculty advisors, and department chairs are hereby notified of the official
academic schedule and critical deadlines for the upcoming Fall Semester 2025:

1. COURSE REGISTRATION SCHEDULE
- Student ERP Portal Opens for Registration: August 18, 2025 (9:00 AM)
- Regular Course Registration Deadline (No Fine): August 25, 2025 (5:00 PM)
- Late Course Registration Period: August 26, 2025 to September 2, 2025 (Late fee fine: $100 per student)
- Strictly No Course Registration permitted after: September 2, 2025 (Midnight)
- Last Date for Course Add / Drop without penalty: September 8, 2025
- Last Date for Course Withdrawal with 'W' grade: October 5, 2025

2. INSTRUCTION & TEACHING PERIOD
- Commencement of Classes: August 28, 2025
- First Continuous Assessment Test (CAT-1): September 22 - September 26, 2025
- Mid-Semester Theory & Practical Exams: October 13 - October 18, 2025
- Mid-Semester Marks Publication on ERP: October 27, 2025
- Last Day of Instruction (Classroom Lectures End): December 5, 2025

3. END-SEMESTER EXAMINATIONS & WINTER RECESS
- Hall Ticket Generation & Biometric Verification: December 1 - December 8, 2025
- Laboratory Practical Final Exams: December 8 - December 12, 2025
- End-Semester Theory Final Examinations: December 15 - December 24, 2025
- Winter Vacation for Students: December 25, 2025 to January 11, 2026
- Declaration of Final Semester Results: January 15, 2026
- Spring Semester 2026 Reopening Date: January 12, 2026

4. FEE PAYMENT DEADLINE
- Tuition fee and hostel mess fee must be cleared on or before August 25, 2025.
- Students failing to clear fees will not be permitted to complete ERP course registration.

Issued by:
Prof. S. R. Ramanathan, Dean (Academic Affairs)
Copy to: Director, Deans, HoDs, Examination Controller, Student Notice Boards.
"""
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Created:", txt_path)


def generate_exam_circular_docx():
    docx_path = os.path.join(SAMPLE_DIR, "Examination_Circular_Attendance_and_Malpractice_2025.docx")
    doc = Document()
    doc.add_heading("CONTROLLER OF EXAMINATIONS - URGENT CIRCULAR", level=1)
    doc.add_paragraph("Circular Ref: COE/EXAM/CIR/2025/09 | Academic Year: 2025-2026 | Date: September 20, 2025")
    
    doc.add_heading("1. Hall Ticket Issuance and Attendance Shortage Verification", level=2)
    doc.add_paragraph(
        "Notice to all candidates appearing for the Fall Semester 2025 Examinations:\n"
        "1.1 Hall tickets will be made available for download from the Examination Portal starting December 1, 2025. "
        "Downloading requires prior clearance of all tuition dues and biometric verification.\n"
        "1.2 Hall ticket generation is strictly locked for students with attendance less than 75% in any registered course.\n"
        "1.3 Students eligible for the 65% condonation quota (medical hospitalization of 5+ days or sports representation) "
        "must verify that their approved condonation order signed by Dean (Academic Affairs) is uploaded to the portal "
        "no later than December 1, 2025 at 5:00 PM. No conditional admit cards will be issued at exam halls."
    )
    
    doc.add_heading("2. Permitted Examination Items and Scientific Calculators", level=2)
    doc.add_paragraph(
        "2.1 Only non-programmable scientific calculators without memory storage features are permitted. "
        "Specifically authorized models include Casio fx-82MS, fx-991MS, and Texas Instruments TI-30Xa.\n"
        "2.2 Calculators with matrix programming, symbolic algebraic computation, or alphanumeric storage "
        "(e.g., Casio fx-991EX ClassWiz, TI-84 Plus) are strictly prohibited.\n"
        "2.3 Mobile phones, smart wristwatches, Bluetooth earphones, fitness bands, and study materials must not be brought "
        "inside the examination hall. Safe custody is not guaranteed by the invigilation staff."
    )
    
    doc.add_heading("3. Penalties for Academic Dishonesty and Malpractice", level=2)
    doc.add_paragraph(
        "3.1 Category A Malpractice (Possession of unauthorized written chits, formula sheets, or writing on body parts):\n"
        "Penalty: Cancellation of the examination paper in question and award of 'F' grade for that course.\n"
        "3.2 Category B Malpractice (Possession of unauthorized electronic gadgets, mobile phones, or smart devices inside exam hall whether switched on or off):\n"
        "Penalty: Cancellation of ALL registered course examinations for the entire semester, and forfeiture of eligibility for campus placement drives.\n"
        "3.3 Category C Malpractice (Impersonation, violent behavior, or leaking examination questions):\n"
        "Penalty: Immediate expulsion from the institute for a minimum period of 2 academic years and filing of formal police report."
    )
    
    doc.save(docx_path)
    print("Created:", docx_path)


if __name__ == "__main__":
    generate_regulations_2023()
    generate_regulations_2025()
    generate_syllabus_cs301()
    generate_calendar_notice()
    generate_exam_circular_docx()
    print("All sample documents successfully generated!")
