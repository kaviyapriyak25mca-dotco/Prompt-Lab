import os
import sys
import webbrowser

# Add backend directory to sys.path
backend_dir = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_dir)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Ensure sample documents exist
sample_dir = os.path.join(os.path.dirname(__file__), "sample_documents")
if not os.path.exists(sample_dir) or len(os.listdir(sample_dir)) == 0:
    print("Generating initial academic sample documents...")
    import sample_data_generator
    sample_data_generator.generate_regulations_2023()
    sample_data_generator.generate_regulations_2025()
    sample_data_generator.generate_syllabus_cs301()
    sample_data_generator.generate_calendar_notice()
    sample_data_generator.generate_exam_circular_docx()

from app import app

if __name__ == "__main__":
    PORT = 5000
    URL = f"http://127.0.0.1:{PORT}"
    print("=" * 70)
    print("[ONLINE] ACADEMIC DOCUMENT RETRIEVAL AGENT")
    print(f"[URL] Web Interface & REST API running at: {URL}")
    print("=" * 70)
    app.run(host="127.0.0.1", port=PORT, debug=False)
