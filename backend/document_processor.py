import os
import re
from datetime import datetime
import pypdf
import docx

class DocumentProcessor:
    def __init__(self, chunk_size=350, chunk_overlap=80):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract_metadata_from_text(self, filename, full_text):
        """Extract academic year, date, category, and authority score from filename & text."""
        metadata = {
            "academic_year": "Unknown",
            "date": "Unknown",
            "category": "General Document",
            "authority_tier": 2, # 1: Urgent Circular/Notice, 2: Regulations, 3: Syllabus/Handout
            "year_weight": 2024
        }
        
        # Detect Academic Year (e.g. 2025-2026, 2023-2024, 2025-26)
        all_matches = re.finditer(r"(?:academic\s+year|ay|session|ordinance)?\s*(202[0-9])\s*[-–/]\s*(202[0-9]|\d{2})\b", full_text + " " + filename, re.IGNORECASE)
        for m in all_matches:
            start_yr = int(m.group(1))
            end_val = m.group(2)
            end_yr = int(end_val) if len(end_val) == 4 else (2000 + int(end_val))
            # Validate that end_yr is sensible (start_yr + 1, e.g. 2023-2024 or 2025-2026)
            if end_yr == start_yr + 1 or end_yr == start_yr:
                metadata["academic_year"] = f"{start_yr}-{end_yr}"
                metadata["year_weight"] = start_yr
                break
        
        # Fallback to single year in filename if no span found
        if metadata["academic_year"] == "Unknown":
            single_yr = re.search(r"\b(202[3-9])\b", filename)
            if single_yr:
                y = int(single_yr.group(1))
                metadata["academic_year"] = f"{y}-{y+1}"
                metadata["year_weight"] = y

        # Detect Publication Dates (e.g. July 15, 2025; August 10, 2025; September 20, 2025)
        date_match = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s*(202[0-9])", full_text, re.IGNORECASE)
        if date_match:
            metadata["date"] = date_match.group(0)

        # Detect Category
        lower_all = (filename + " " + full_text[:1000]).lower()
        if "circular" in lower_all or "urgent" in lower_all or "notice" in lower_all:
            metadata["category"] = "Academic Circular / Urgent Notice"
            metadata["authority_tier"] = 1
        elif "syllabus" in lower_all or "curriculum" in lower_all:
            metadata["category"] = "Course Syllabus & Curriculum"
            metadata["authority_tier"] = 3
        elif "calendar" in lower_all or "deadlines" in lower_all:
            metadata["category"] = "Academic Calendar & Notices"
            metadata["authority_tier"] = 1
        elif "regulation" in lower_all or "ordinance" in lower_all:
            metadata["category"] = "Academic Regulations & Ordinances"
            metadata["authority_tier"] = 2
            
        # Revision / Superseding flag
        if "revised" in lower_all or "supersede" in lower_all or "amended" in lower_all:
            metadata["is_revision"] = True
            metadata["authority_tier"] = 1.5
        else:
            metadata["is_revision"] = False

        return metadata

    def parse_pdf(self, file_path):
        """Extract text page by page from PDF using pypdf."""
        reader = pypdf.PdfReader(file_path)
        pages = []
        full_text_list = []
        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            text = re.sub(r"\n\s*\n", "\n\n", text).strip()
            pages.append({"page_number": idx + 1, "text": text})
            full_text_list.append(text)
        return pages, "\n\n".join(full_text_list)

    def parse_docx(self, file_path):
        """Extract text from DOCX preserving heading hierarchy as pseudo-pages."""
        doc = docx.Document(file_path)
        pages = []
        current_section = []
        current_heading = "General Overview"
        section_idx = 1
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            if para.style.name.startswith("Heading 1") or para.style.name.startswith("Heading 2"):
                if current_section:
                    pages.append({
                        "page_number": section_idx,
                        "section_title": current_heading,
                        "text": "\n".join(current_section)
                    })
                    section_idx += 1
                    current_section = []
                current_heading = text
            current_section.append(text)
            
        if current_section:
            pages.append({
                "page_number": section_idx,
                "section_title": current_heading,
                "text": "\n".join(current_section)
            })
            
        full_text = "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return pages, full_text

    def parse_txt(self, file_path):
        """Extract text from TXT splitting into sections or logical pages."""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_text = f.read()
            
        # Split on section dividers or double breaks
        sections = re.split(r"\n(?=[0-9]+\.\s+[A-Z\s]{4,}|\={10,}|\-{10,})", raw_text)
        pages = []
        for idx, sec in enumerate(sections):
            clean_sec = sec.strip()
            if clean_sec:
                pages.append({
                    "page_number": idx + 1,
                    "section_title": f"Section {idx + 1}",
                    "text": clean_sec
                })
        if not pages:
            pages.append({"page_number": 1, "section_title": "Document Content", "text": raw_text})
        return pages, raw_text

    def process_file(self, file_path, custom_filename=None):
        """Extract and chunk any supported document format."""
        filename = custom_filename or os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        
        if ext == ".pdf":
            pages, full_text = self.parse_pdf(file_path)
        elif ext == ".docx":
            pages, full_text = self.parse_docx(file_path)
        elif ext in [".txt", ".text"]:
            pages, full_text = self.parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Only PDF, DOCX, and TXT are supported.")

        metadata = self.extract_metadata_from_text(filename, full_text)
        metadata["filename"] = filename
        metadata["total_pages"] = len(pages)
        metadata["file_type"] = ext.replace(".", "").upper()

        chunks = self.chunk_document(pages, metadata)
        return {
            "metadata": metadata,
            "full_text": full_text,
            "pages": pages,
            "chunks": chunks
        }

    def chunk_document(self, pages, metadata):
        """Split document pages into meaningful overlapping chunks with rich metadata."""
        chunks = []
        chunk_counter = 1
        
        for page_obj in pages:
            page_num = page_obj["page_number"]
            section_title = page_obj.get("section_title", f"Page {page_num}")
            page_text = page_obj["text"]
            
            # Split into paragraphs or bullet items
            paragraphs = [p.strip() for p in re.split(r"\n\s*\n|(?<=\.)\s*\n", page_text) if p.strip()]
            
            current_chunk_text = ""
            for para in paragraphs:
                if len(current_chunk_text) + len(para) < self.chunk_size:
                    current_chunk_text = (current_chunk_text + "\n" + para).strip()
                else:
                    if current_chunk_text:
                        chunks.append(self._build_chunk(current_chunk_text, chunk_counter, page_num, section_title, metadata))
                        chunk_counter += 1
                        # Retain overlap from end of previous text
                        words = current_chunk_text.split()
                        overlap_words = words[-15:] if len(words) >= 15 else words
                        current_chunk_text = " ".join(overlap_words) + "\n" + para
                    else:
                        current_chunk_text = para

            if current_chunk_text:
                chunks.append(self._build_chunk(current_chunk_text, chunk_counter, page_num, section_title, metadata))
                chunk_counter += 1

        return chunks

    def _build_chunk(self, text, chunk_counter, page_num, section_title, metadata):
        return {
            "chunk_id": f"{metadata['filename']}_chunk_{chunk_counter}",
            "doc_name": metadata["filename"],
            "page_number": page_num,
            "section_title": section_title,
            "academic_year": metadata.get("academic_year", "Unknown"),
            "date": metadata.get("date", "Unknown"),
            "category": metadata.get("category", "General"),
            "authority_tier": metadata.get("authority_tier", 2),
            "year_weight": metadata.get("year_weight", 2024),
            "is_revision": metadata.get("is_revision", False),
            "text": text.strip()
        }
