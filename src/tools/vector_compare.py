from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Sequence

from openai import OpenAI

from src.io_utils import read_markdown_body


def cosine_similarity(vec_a: Sequence[float], vec_b: Sequence[float]) -> float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _simple_bow_vector_pair(text_a: str, text_b: str) -> tuple[list[float], list[float]]:
    tokens_a = text_a.lower().split()
    tokens_b = text_b.lower().split()
    counts_a = Counter(tokens_a)
    counts_b = Counter(tokens_b)
    vocab = sorted(set(counts_a.keys()) | set(counts_b.keys()))
    vec_a = [float(counts_a[token]) for token in vocab]
    vec_b = [float(counts_b[token]) for token in vocab]
    return vec_a, vec_b


def explain_similarity(score: float) -> str:
    if score >= 0.9:
        return "High semantic preservation: the back-translated text is very close to the original meaning."
    if score >= 0.75:
        return "Moderate semantic preservation: the core meaning is mostly preserved with some drift."
    return "Low semantic preservation: substantial meaning drift is likely across the translation chain."


@dataclass(frozen=True)
class ComparisonResult:
    similarity: float
    cosine_distance: float
    method: str
    explanation: str


class VectorComparator:
    def __init__(
        self,
        *,
        mode: str = "openai",
        embedding_model: str = "text-embedding-3-small",
        api_key: str | None = None,
    ) -> None:
        self.mode = mode
        self.embedding_model = embedding_model
        self.client = OpenAI(api_key=api_key) if mode == "openai" else None

    def _embed_openai(self, text: str) -> list[float]:
        if not self.client:
            raise RuntimeError("OpenAI client is not initialized.")
        response = self.client.embeddings.create(model=self.embedding_model, input=text)
        return list(response.data[0].embedding)

    def compare_texts(self, original_text: str, final_text: str) -> ComparisonResult:
        if self.mode == "openai":
            vec_original = self._embed_openai(original_text)
            vec_final = self._embed_openai(final_text)
            method = f"OpenAI embeddings ({self.embedding_model}) + cosine similarity"
        else:
            vec_original, vec_final = _simple_bow_vector_pair(original_text, final_text)
            method = "Local bag-of-words vectors + cosine similarity"

        score = cosine_similarity(vec_original, vec_final)
        score = max(-1.0, min(1.0, score))
        distance = 1.0 - score
        return ComparisonResult(
            similarity=score,
            cosine_distance=distance,
            method=method,
            explanation=explain_similarity(score),
        )

    def compare_files(self, original_path: str, final_path: str, report_path: str) -> ComparisonResult:
        original_text = read_markdown_body(original_path)
        final_text = read_markdown_body(final_path)
        result = self.compare_texts(original_text=original_text, final_text=final_text)
        self._write_report(report_path=report_path, result=result)
        return result

    def _write_report(self, report_path: str, result: ComparisonResult) -> None:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body = (
            "# Vector Comparison Report\n\n"
            f"- Timestamp: {now}\n"
            f"- Method: {result.method}\n"
            f"- Cosine similarity score: {result.similarity:.4f}\n"
            f"- Cosine distance: {result.cosine_distance:.4f}\n\n"
            "## Interpretation\n\n"
            f"{result.explanation}\n"
        )
        target = Path(report_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
