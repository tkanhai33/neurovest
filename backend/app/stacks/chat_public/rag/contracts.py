"""
Canonical contracts for NeuroVest local retrieval.

These contracts are read-only and contain no execution,
account mutation, broker access, or authorization authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(
    frozen=True,
    slots=True,
)
class KnowledgeChunk:
    chunk_id: str
    document_id: str
    source_path: str
    source_type: str
    title: str
    chunk_index: int
    text: str
    content_hash: str
    embedding: tuple[float, ...]
    metadata: dict[str, Any]

    def as_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "source_path": self.source_path,
            "source_type": self.source_type,
            "title": self.title,
            "chunk_index": self.chunk_index,
            "text": self.text,
            "content_hash": self.content_hash,
            "embedding": list(
                self.embedding
            ),
            "metadata": dict(
                self.metadata
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class RetrievalResult:
    chunk_id: str
    document_id: str
    source_path: str
    title: str
    text: str
    score: float
    citation: str
    metadata: dict[str, Any]

    def as_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "source_path": self.source_path,
            "title": self.title,
            "text": self.text,
            "score": self.score,
            "citation": self.citation,
            "metadata": dict(
                self.metadata
            ),
        }
