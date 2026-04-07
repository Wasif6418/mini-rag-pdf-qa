from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from rag.chunking import TextChunk


@dataclass
class RetrievedChunk:
    chunk: TextChunk
    score: float


class TfidfRetriever:
    def __init__(self, chunks: list[TextChunk]) -> None:
        if not chunks:
            raise ValueError("At least one chunk is required to build the retriever")

        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform([chunk.text for chunk in chunks])

    def search(self, question: str, top_k: int = 3) -> list[RetrievedChunk]:
        if not question.strip():
            return []

        query_vector = self.vectorizer.transform([question])
        scores = cosine_similarity(query_vector, self.matrix).flatten()

        if not np.any(scores):
            return []

        top_indices = scores.argsort()[::-1][:top_k]
        return [
            RetrievedChunk(chunk=self.chunks[index], score=float(scores[index]))
            for index in top_indices
            if scores[index] > 0
        ]
