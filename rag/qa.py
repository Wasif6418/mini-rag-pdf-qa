from __future__ import annotations

import re
from dataclasses import dataclass

from rag.retriever import RetrievedChunk

STOPWORDS = {
    "about",
    "does",
    "from",
    "have",
    "into",
    "that",
    "the",
    "their",
    "them",
    "this",
    "what",
    "when",
    "where",
    "which",
    "with",
    "would",
    "your",
}


@dataclass
class AnswerResult:
    answer: str
    sources: list[dict[str, str | int | float]]


def build_answer(question: str, retrieved_chunks: list[RetrievedChunk]) -> AnswerResult:
    if not retrieved_chunks:
        return AnswerResult(
            answer="I could not find enough relevant information in the PDF to answer that confidently.",
            sources=[],
        )

    keywords = {
        word for word in re.findall(r"\b[a-zA-Z]{3,}\b", question.lower()) if word not in STOPWORDS
    }
    candidate_sentences: list[tuple[int, int, float, str]] = []
    fallback_sentences: list[tuple[int, float, str]] = []

    for index, item in enumerate(retrieved_chunks):
        sentences = re.split(r"(?<=[.!?])\s+", item.chunk.text)
        for sentence in sentences:
            lowered = sentence.lower()
            lexical_hits = sum(1 for word in keywords if word in lowered)
            sentence_score = item.score + (lexical_hits * 0.08)
            if index == 0 and sentence.strip():
                fallback_sentences.append((index, sentence_score, sentence.strip()))
            if lexical_hits > 0:
                candidate_sentences.append((index, lexical_hits, sentence_score, sentence.strip()))

    if not candidate_sentences:
        if fallback_sentences:
            ranked_fallback = sorted(fallback_sentences, key=lambda item: item[1], reverse=True)
            answer_text = " ".join(sentence for _, _, sentence in ranked_fallback[:2]).strip()
        else:
            best_chunk = retrieved_chunks[0].chunk.text
            answer_text = best_chunk[:350].strip()
    else:
        ranked = sorted(candidate_sentences, key=lambda item: (item[1], item[2]), reverse=True)
        selected: list[str] = []
        for _, lexical_hits, _, sentence in ranked:
            if sentence and sentence not in selected:
                selected.append(sentence)
            if len(selected) >= 2 and lexical_hits == 0:
                break
            if len(selected) >= 3 or len(" ".join(selected)) > 260:
                break
        answer_text = " ".join(selected)

    sources = [
        {
            "chunk_id": item.chunk.chunk_id,
            "page": item.chunk.page_number,
            "score": round(item.score, 4),
            "text": item.chunk.text,
        }
        for item in retrieved_chunks
    ]

    return AnswerResult(answer=answer_text, sources=sources)
