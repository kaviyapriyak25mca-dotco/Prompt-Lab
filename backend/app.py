import os
import glob
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from document_processor import DocumentProcessor
from retriever import HybridRetriever
from rag_engine import RAGEngine

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SAMPLE_DIR = os.path.join(BASE_DIR, "sample_documents")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR)
CORS(app)

processor = DocumentProcessor()
retriever = HybridRetriever()
rag = RAGEngine(retriever)

def load_initial_documents():
    """Load and index all documents from sample_documents directory."""
    files = glob.glob(os.path.join(SAMPLE_DIR, "*.*"))
    for fpath in files:
        ext = os.path.splitext(fpath)[1].lower()
        if ext in [".pdf", ".docx", ".txt", ".text"]:
            try:
                doc_data = processor.process_file(fpath)
                retriever.add_document(doc_data)
            except Exception as e:
                print(f"Error loading {fpath}: {e}")

load_initial_documents()

# Frontend routes
@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(FRONTEND_DIR, path)

# API Endpoints
@app.route("/api/documents", methods=["GET"])
def get_documents():
    docs_summary = []
    for doc_name, meta in retriever.documents.items():
        doc_chunks = [c for c in retriever.chunks if c["doc_name"] == doc_name]
        docs_summary.append({
            "filename": doc_name,
            "category": meta.get("category", "General"),
            "academic_year": meta.get("academic_year", "Unknown"),
            "date": meta.get("date", "Unknown"),
            "file_type": meta.get("file_type", "Unknown"),
            "total_pages": meta.get("total_pages", 1),
            "total_chunks": len(doc_chunks),
            "authority_tier": meta.get("authority_tier", 2),
            "is_revision": meta.get("is_revision", False)
        })
    docs_summary.sort(key=lambda d: (d["academic_year"], d["filename"]), reverse=True)
    return jsonify({"success": True, "documents": docs_summary, "total": len(docs_summary)})

@app.route("/api/chunks", methods=["GET"])
def get_chunks():
    doc_filter = request.args.get("doc_name")
    if doc_filter:
        filtered = [c for c in retriever.chunks if c["doc_name"] == doc_filter]
    else:
        filtered = retriever.chunks
    return jsonify({"success": True, "chunks": filtered, "total": len(filtered)})

@app.route("/api/upload", methods=["POST"])
def upload_document():
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded."}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "Empty filename."}), 400

    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".pdf", ".docx", ".txt", ".text"]:
        return jsonify({
            "success": False, 
            "error": f"Unsupported file type '{ext}'. Please upload PDF, DOCX, or TXT."
        }), 400

    save_path = os.path.join(SAMPLE_DIR, filename)
    file.save(save_path)

    try:
        doc_data = processor.process_file(save_path, custom_filename=filename)
        retriever.add_document(doc_data)
        meta = doc_data["metadata"]
        return jsonify({
            "success": True,
            "message": f"Successfully indexed '{filename}'",
            "metadata": meta,
            "chunks_count": len(doc_data["chunks"])
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to process file: {str(e)}"}), 500

@app.route("/api/query", methods=["POST"])
def answer_query():
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"success": False, "error": "Query cannot be empty."}), 400

    top_k = int(data.get("top_k", 5))
    api_key = data.get("gemini_api_key", "").strip() or None

    try:
        result = rag.answer_query(query, top_k=top_k, gemini_api_key=api_key)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": f"Error answering query: {str(e)}"}), 500

@app.route("/api/reset", methods=["POST"])
def reset_corpus():
    retriever.chunks = []
    retriever.documents = {}
    load_initial_documents()
    return jsonify({
        "success": True, 
        "message": "Reset to default sample documents.",
        "total_documents": len(retriever.documents),
        "total_chunks": len(retriever.chunks)
    })

@app.route("/api/stats", methods=["GET"])
def get_stats():
    categories = set(meta.get("category", "General") for meta in retriever.documents.values())
    return jsonify({
        "success": True,
        "total_documents": len(retriever.documents),
        "total_chunks": len(retriever.chunks),
        "categories": list(categories),
        "indexed": retriever.is_indexed
    })

if __name__ == "__main__":
    print(f"Academic Document Retrieval Agent Server running at http://localhost:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
