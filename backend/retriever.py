import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class HybridRetriever:
    def __init__(self, semantic_weight=0.55, keyword_weight=0.45):
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight
        self.chunks = []
        self.documents = {}
        
        # Word-level TF-IDF for semantic & topical matching
        self.word_vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            sublinear_tf=True,
            stop_words='english',
            token_pattern=r'(?u)\b[\w\-\.\$\%]{2,}\b'
        )
        
        # Character n-gram vectorizer for subword/entity/code matching
        self.char_vectorizer = TfidfVectorizer(
            analyzer='char_wb',
            ngram_range=(3, 5),
            sublinear_tf=True
        )
        
        self.is_indexed = False
        self.word_matrix = None
        self.char_matrix = None

    def add_document(self, doc_data):
        """Index a document and its chunks into the retriever store."""
        filename = doc_data["metadata"]["filename"]
        self.documents[filename] = doc_data["metadata"]
        
        # Remove any existing chunks for this doc to allow re-upload
        self.chunks = [c for c in self.chunks if c["doc_name"] != filename]
        self.chunks.extend(doc_data["chunks"])
        self.rebuild_index()

    def rebuild_index(self):
        """Re-fit vectorizers on all loaded text chunks."""
        if not self.chunks:
            self.is_indexed = False
            return
            
        corpus = [c["text"] for c in self.chunks]
        self.word_matrix = self.word_vectorizer.fit_transform(corpus)
        self.char_matrix = self.char_vectorizer.fit_transform(corpus)
        self.is_indexed = True

    def extract_keywords(self, text):
        """Extract meaningful alphanumeric tokens, codes, and numbers."""
        tokens = re.findall(r'[a-zA-Z0-9\$\%\.\-]+', text.lower())
        stopwords = {"what", "is", "the", "for", "and", "or", "to", "in", "of", "a", "an", "on", "are", "can", "how", "does", "do", "tell", "me", "about"}
        return set([t for t in tokens if t not in stopwords and len(t) > 1])

    def search(self, query, top_k=6):
        """Perform hybrid semantic and keyword retrieval over indexed chunks."""
        if not self.is_indexed or not self.chunks:
            return []

        # Vector space similarities
        query_word_vec = self.word_vectorizer.transform([query])
        query_char_vec = self.char_vectorizer.transform([query])

        semantic_scores = cosine_similarity(query_word_vec, self.word_matrix).flatten()
        subword_scores = cosine_similarity(query_char_vec, self.char_matrix).flatten()

        query_keywords = self.extract_keywords(query)
        results = []

        for idx, chunk in enumerate(self.chunks):
            sem_score = float(semantic_scores[idx])
            sub_score = float(subword_scores[idx])
            
            # Exact keyword overlap matching
            chunk_keywords = self.extract_keywords(chunk["text"])
            matched_keywords = list(query_keywords.intersection(chunk_keywords))
            
            if len(query_keywords) > 0:
                lexical_score = len(matched_keywords) / len(query_keywords)
            else:
                lexical_score = 0.0

            # Boost if specific numeric/academic entities match (e.g., 75%, 65%, $100, cs301)
            exact_entity_bonus = 0.0
            for kw in query_keywords:
                if any(char.isdigit() or char in "%$" for char in kw):
                    if kw in chunk["text"].lower():
                        exact_entity_bonus += 0.15

            # Authority & Recency calibration
            # Later academic years get a modest boost (e.g., 2025 vs 2023)
            year_boost = 0.0
            if chunk.get("year_weight"):
                year_boost = (chunk["year_weight"] - 2023) * 0.02
                
            # Urgent circulars/notices get tier boost
            tier = chunk.get("authority_tier", 2)
            tier_boost = (3 - tier) * 0.02

            # Combined hybrid score
            combined_score = (
                self.semantic_weight * sem_score +
                self.keyword_weight * (0.6 * lexical_score + 0.4 * sub_score) +
                exact_entity_bonus +
                year_boost +
                tier_boost
            )

            # Keep only chunks that have at least some relevance
            if combined_score > 0.04 or sem_score > 0.08 or len(matched_keywords) > 0:
                results.append({
                    "chunk": chunk,
                    "score": round(float(combined_score), 4),
                    "semantic_score": round(float(sem_score), 4),
                    "keyword_score": round(float(lexical_score), 4),
                    "matched_keywords": matched_keywords
                })

        # Sort by combined score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
