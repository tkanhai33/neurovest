"""
Controlled local knowledge index for NeuroVest.

The index stores allowlisted project documentation and contract
chunks with normalized Ollama embeddings. Retrieval is read-only.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

from pypdf import PdfReader

from backend.app.stacks.chat_public.rag.contracts import (
    KnowledgeChunk,
    RetrievalResult,
)
from backend.app.stacks.chat_public.rag.embedding_client import (
    DEFAULT_EMBEDDING_MODEL,
    OllamaEmbeddingClient,
)


INDEX_VERSION = 1

DEFAULT_CHUNK_WORDS = 180
DEFAULT_OVERLAP_WORDS = 30

# Keep Ollama embedding requests bounded. Large PDF corpora can
# contain thousands of chunks and must never be sent as one request.
DEFAULT_EMBEDDING_BATCH_SIZE = 16

# Normal source files remain tightly bounded. Canonical research
# PDFs may be larger because their extracted text is still scanned,
# chunked, deduplicated, and embedded through bounded batches.
DEFAULT_MAX_TEXT_FILE_BYTES = 2_000_000
DEFAULT_MAX_RESEARCH_PDF_BYTES = 25_000_000

ALLOWED_SUFFIXES = {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".py",
    ".pdf",
}

FORBIDDEN_PATH_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    ".next",
    "node_modules",
    "archive",
    "backups",
    "runtime",
    "quarantine_artifacts",
    "test-results",
}

FORBIDDEN_FILENAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    "id_rsa",
    "id_ed25519",
}

SECRET_PATTERNS = (
    re.compile(
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        re.I,
    ),
    re.compile(
        r"\b(?:api[_-]?key|secret|password|token)\s*[:=]\s*[\"'][^\"']{8,}",
        re.I,
    ),
    re.compile(
        r"\bsk-[A-Za-z0-9_-]{20,}\b",
        re.I,
    ),
)

PROMPT_INJECTION_PATTERNS = (
    re.compile(
        r"\bignore (?:all |the )?previous instructions\b",
        re.I,
    ),
    re.compile(
        r"\bsystem prompt\b",
        re.I,
    ),
    re.compile(
        r"\breveal (?:your |the )?(?:hidden )?instructions\b",
        re.I,
    ),
    re.compile(
        r"\bact as (?:the )?system\b",
        re.I,
    ),
)


def sha256_text(
    value: str,
) -> str:
    return hashlib.sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


def stable_document_id(
    source_path: str,
) -> str:
    normalized = str(
        source_path
    ).replace(
        "\\",
        "/",
    )

    return (
        "doc_"
        + sha256_text(
            normalized
        )[:24]
    )


def stable_chunk_id(
    *,
    document_id: str,
    chunk_index: int,
    content_hash: str,
) -> str:
    material = (
        f"{document_id}:"
        f"{chunk_index}:"
        f"{content_hash}"
    )

    return (
        "chunk_"
        + sha256_text(
            material
        )[:28]
    )


def is_allowed_source(
    path: Path,
    *,
    root: Path,
) -> bool:
    try:
        relative = path.resolve().relative_to(
            root.resolve()
        )
    except ValueError:
        return False

    if not path.is_file():
        return False

    if path.suffix.lower() not in ALLOWED_SUFFIXES:
        return False

    if path.name.lower() in FORBIDDEN_FILENAMES:
        return False

    lowered_parts = {
        part.lower()
        for part in relative.parts
    }

    if lowered_parts & FORBIDDEN_PATH_PARTS:
        return False

    relative_string = relative.as_posix().lower()

    if relative_string.startswith(
        "docs/"
    ):
        return True

    if relative_string.startswith(
        "knowledge/research/"
    ):
        return (
            path.suffix.lower()
            in ALLOWED_SUFFIXES
        )

    if not relative_string.startswith(
        "backend/app/"
    ):
        return False

    allowed_backend_terms = (
        "contract",
        "policy",
        "safety",
        "governance",
        "architecture",
        "manifest",
        "readme",
        "route_protection",
    )

    return any(
        term in relative_string
        for term in allowed_backend_terms
    )


def contains_secret(
    text: str,
) -> bool:
    return any(
        pattern.search(
            text
        )
        for pattern in SECRET_PATTERNS
    )


def contains_prompt_injection(
    text: str,
) -> bool:
    return any(
        pattern.search(
            text
        )
        for pattern in PROMPT_INJECTION_PATTERNS
    )


def normalize_text(
    text: str,
) -> str:
    value = str(
        text
    ).replace(
        "\r\n",
        "\n",
    ).replace(
        "\r",
        "\n",
    )

    lines = [
        line.rstrip()
        for line in value.split(
            "\n"
        )
    ]

    normalized = "\n".join(
        lines
    ).strip()

    return normalized


def extract_pdf_pages(
    path: Path,
) -> list[dict[str, Any]]:
    """
    Extract selectable text from a PDF one page at a time.

    The extractor performs no OCR. PDFs without selectable text
    are rejected by ingestion with an explicit reason.
    """

    try:
        reader = PdfReader(
            str(path)
        )
    except Exception as error:
        raise RuntimeError(
            "PDF could not be opened: "
            f"{type(error).__name__}: {error}"
        ) from error

    pages: list[
        dict[str, Any]
    ] = []

    for page_index, page in enumerate(
        reader.pages,
        start=1,
    ):
        try:
            page_text = normalize_text(
                page.extract_text()
                or ""
            )
        except Exception:
            page_text = ""

        if not page_text:
            continue

        pages.append(
            {
                "page_number":
                    page_index,
                "text":
                    page_text,
            }
        )

    return pages


def extract_source_sections(
    path: Path,
) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".pdf":
        return extract_pdf_pages(
            path
        )

    try:
        content = path.read_text(
            encoding="utf-8"
        )
    except (
        UnicodeDecodeError,
        OSError,
    ) as error:
        raise RuntimeError(
            "Text source could not be read: "
            f"{type(error).__name__}: {error}"
        ) from error

    normalized = normalize_text(
        content
    )

    if not normalized:
        return []

    return [
        {
            "page_number":
                None,
            "text":
                normalized,
        }
    ]


def chunk_text(
    text: str,
    *,
    chunk_words: int = DEFAULT_CHUNK_WORDS,
    overlap_words: int = DEFAULT_OVERLAP_WORDS,
) -> list[str]:
    if chunk_words <= 0:
        raise ValueError(
            "chunk_words must be positive."
        )

    if overlap_words < 0:
        raise ValueError(
            "overlap_words cannot be negative."
        )

    if overlap_words >= chunk_words:
        raise ValueError(
            "overlap_words must be smaller "
            "than chunk_words."
        )

    normalized = normalize_text(
        text
    )

    if not normalized:
        return []

    words = normalized.split()

    if len(words) <= chunk_words:
        return [
            " ".join(
                words
            )
        ]

    step = (
        chunk_words
        - overlap_words
    )

    chunks: list[str] = []

    for start in range(
        0,
        len(words),
        step,
    ):
        end = min(
            start + chunk_words,
            len(words),
        )

        chunk = " ".join(
            words[
                start:end
            ]
        ).strip()

        if chunk:
            chunks.append(
                chunk
            )

        if end >= len(words):
            break

    return chunks


def cosine_similarity(
    left: Sequence[float],
    right: Sequence[float],
) -> float:
    if len(left) != len(right):
        raise ValueError(
            "Vector dimensions differ."
        )

    return float(
        sum(
            a * b
            for a, b in zip(
                left,
                right,
                strict=True,
            )
        )
    )


class LocalKnowledgeIndex:
    def __init__(
        self,
        *,
        index_path: Path,
        embedding_client: OllamaEmbeddingClient | None = None,
    ) -> None:
        self.index_path = Path(
            index_path
        )

        self.embedding_client = (
            embedding_client
            or OllamaEmbeddingClient()
        )

    def _empty_payload(
        self,
    ) -> dict[str, Any]:
        return {
            "version": INDEX_VERSION,
            "embedding_model":
                DEFAULT_EMBEDDING_MODEL,
            "embedding_dimensions": None,
            "generated_at": None,
            "document_count": 0,
            "chunk_count": 0,
            "chunks": [],
        }

    def load(
        self,
    ) -> dict[str, Any]:
        if not self.index_path.exists():
            return self._empty_payload()

        payload = json.loads(
            self.index_path.read_text(
                encoding="utf-8"
            )
        )

        if payload.get(
            "version"
        ) != INDEX_VERSION:
            raise RuntimeError(
                "Unsupported local RAG index version."
            )

        chunks = payload.get(
            "chunks"
        )

        if not isinstance(
            chunks,
            list,
        ):
            raise RuntimeError(
                "Local RAG index chunks are invalid."
            )

        return payload

    def save_atomic(
        self,
        payload: dict[str, Any],
    ) -> None:
        self.index_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        serialized = (
            json.dumps(
                payload,
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=self.index_path.parent,
            prefix=(
                self.index_path.name
                + "."
            ),
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary.write(
                serialized
            )

            temporary_path = Path(
                temporary.name
            )

        os.replace(
            temporary_path,
            self.index_path,
        )

    def build_from_paths(
        self,
        *,
        paths: Iterable[Path],
        root: Path,
        chunk_words: int = DEFAULT_CHUNK_WORDS,
        overlap_words: int = DEFAULT_OVERLAP_WORDS,
        max_file_bytes: int = DEFAULT_MAX_TEXT_FILE_BYTES,
        max_research_pdf_bytes: int = DEFAULT_MAX_RESEARCH_PDF_BYTES,
    ) -> dict[str, Any]:
        root = root.resolve()

        prepared: list[
            dict[str, Any]
        ] = []

        rejected: list[
            dict[str, str]
        ] = []

        seen_content_hashes: set[
            str
        ] = set()

        document_ids: set[
            str
        ] = set()

        for candidate in sorted(
            {
                Path(path).resolve()
                for path in paths
            },
            key=lambda item:
                str(item),
        ):
            if not is_allowed_source(
                candidate,
                root=root,
            ):
                rejected.append(
                    {
                        "path":
                            str(candidate),
                        "reason":
                            "source_not_allowlisted",
                    }
                )
                continue

            try:
                size = candidate.stat().st_size
            except OSError:
                rejected.append(
                    {
                        "path":
                            str(candidate),
                        "reason":
                            "stat_failed",
                    }
                )
                continue

            effective_max_file_bytes = (
                max_research_pdf_bytes
                if (
                    candidate.suffix.lower() == ".pdf"
                    and candidate.relative_to(
                        root
                    ).as_posix().startswith(
                        "knowledge/research/"
                    )
                )
                else max_file_bytes
            )

            if size > effective_max_file_bytes:
                rejected.append(
                    {
                        "path":
                            str(candidate),
                        "reason":
                            "file_too_large",
                    }
                )
                continue

            try:
                sections = extract_source_sections(
                    candidate
                )
            except RuntimeError:
                rejected.append(
                    {
                        "path":
                            str(candidate),
                        "reason":
                            "read_failed",
                    }
                )
                continue

            if not sections:
                rejected.append(
                    {
                        "path":
                            str(candidate),
                        "reason": (
                            "pdf_has_no_extractable_text"
                            if candidate.suffix.lower() == ".pdf"
                            else "empty"
                        ),
                    }
                )
                continue

            combined_text = "\n".join(
                str(
                    section.get(
                        "text",
                        "",
                    )
                )
                for section in sections
            )

            if contains_secret(
                combined_text
            ):
                rejected.append(
                    {
                        "path":
                            str(candidate),
                        "reason":
                            "secret_pattern",
                    }
                )
                continue

            relative = candidate.relative_to(
                root
            ).as_posix()

            document_id = stable_document_id(
                relative
            )

            title = (
                candidate.stem
                .replace(
                    "_",
                    " ",
                )
                .replace(
                    "-",
                    " ",
                )
                .strip()
                .title()
            )

            document_ids.add(
                document_id
            )

            global_chunk_index = 0

            for section in sections:
                section_text = str(
                    section.get(
                        "text",
                        "",
                    )
                )

                page_number = section.get(
                    "page_number"
                )

                section_chunks = chunk_text(
                    section_text,
                    chunk_words=chunk_words,
                    overlap_words=overlap_words,
                )

                for page_chunk_index, chunk in enumerate(
                    section_chunks
                ):
                    content_hash = sha256_text(
                        chunk
                    )

                    if content_hash in seen_content_hashes:
                        continue

                    seen_content_hashes.add(
                        content_hash
                    )

                    injection_detected = (
                        contains_prompt_injection(
                            chunk
                        )
                    )

                    prepared.append(
                        {
                            "document_id":
                                document_id,
                            "source_path":
                                relative,
                            "source_type":
                                candidate.suffix.lower().lstrip(
                                    "."
                                ),
                            "title":
                                title,
                            "chunk_index":
                                global_chunk_index,
                            "text":
                                chunk,
                            "content_hash":
                                content_hash,
                            "metadata": {
                                "untrusted_evidence":
                                    True,
                                "prompt_injection_detected":
                                    injection_detected,
                                "read_only":
                                    True,
                                "page_number":
                                    page_number,
                                "page_chunk_index":
                                    page_chunk_index,
                                "research_corpus":
                                    relative.startswith(
                                        "knowledge/research/"
                                    ),
                                "ssrn_document":
                                    (
                                        "/ssrn/"
                                        in (
                                            "/"
                                            + relative.lower()
                                        )
                                    ),
                            },
                        }
                    )

                    global_chunk_index += 1

        if not prepared:
            raise RuntimeError(
                "No allowlisted knowledge chunks "
                "were available for indexing."
            )

        embedding_vectors: list[
            tuple[float, ...]
        ] = []

        embedding_model: str | None = None
        embedding_dimensions: int | None = None

        total_batches = (
            (
                len(prepared)
                + DEFAULT_EMBEDDING_BATCH_SIZE
                - 1
            )
            // DEFAULT_EMBEDDING_BATCH_SIZE
        )

        for batch_number, batch_start in enumerate(
            range(
                0,
                len(prepared),
                DEFAULT_EMBEDDING_BATCH_SIZE,
            ),
            start=1,
        ):
            batch_end = min(
                batch_start
                + DEFAULT_EMBEDDING_BATCH_SIZE,
                len(prepared),
            )

            print(
                "Embedding batch "
                f"{batch_number}/{total_batches}: "
                f"chunks {batch_start + 1}-{batch_end} "
                f"of {len(prepared)}",
                flush=True,
            )

            embedding_batch = (
                self.embedding_client.embed(
                    [
                        item["text"]
                        for item in prepared[
                            batch_start:batch_end
                        ]
                    ]
                )
            )

            if embedding_model is None:
                embedding_model = (
                    embedding_batch.model
                )
            elif (
                embedding_batch.model
                != embedding_model
            ):
                raise RuntimeError(
                    "Embedding model changed during "
                    "the index build."
                )

            if embedding_dimensions is None:
                embedding_dimensions = (
                    embedding_batch.dimensions
                )
            elif (
                embedding_batch.dimensions
                != embedding_dimensions
            ):
                raise RuntimeError(
                    "Embedding dimensions changed during "
                    "the index build."
                )

            embedding_vectors.extend(
                embedding_batch.vectors
            )

        if (
            len(embedding_vectors)
            != len(prepared)
        ):
            raise RuntimeError(
                "Batched embedding count does not match "
                "the prepared chunk count."
            )

        if (
            embedding_model is None
            or embedding_dimensions is None
        ):
            raise RuntimeError(
                "Batched embedding produced no model metadata."
            )

        chunks: list[
            KnowledgeChunk
        ] = []

        for item, embedding in zip(
            prepared,
            embedding_vectors,
            strict=True,
        ):
            chunks.append(
                KnowledgeChunk(
                    chunk_id=stable_chunk_id(
                        document_id=item[
                            "document_id"
                        ],
                        chunk_index=item[
                            "chunk_index"
                        ],
                        content_hash=item[
                            "content_hash"
                        ],
                    ),
                    document_id=item[
                        "document_id"
                    ],
                    source_path=item[
                        "source_path"
                    ],
                    source_type=item[
                        "source_type"
                    ],
                    title=item[
                        "title"
                    ],
                    chunk_index=item[
                        "chunk_index"
                    ],
                    text=item[
                        "text"
                    ],
                    content_hash=item[
                        "content_hash"
                    ],
                    embedding=embedding,
                    metadata=item[
                        "metadata"
                    ],
                )
            )

        chunks.sort(
            key=lambda chunk: (
                chunk.source_path,
                chunk.chunk_index,
                chunk.chunk_id,
            )
        )

        payload: dict[str, Any] = {
            "version": INDEX_VERSION,
            "embedding_model":
                embedding_model,
            "embedding_dimensions":
                embedding_dimensions,
            "generated_at":
                datetime.now(
                    UTC
                ).isoformat(),
            "document_count":
                len(
                    document_ids
                ),
            "chunk_count":
                len(
                    chunks
                ),
            "chunks": [
                chunk.as_dict()
                for chunk in chunks
            ],
            "rejected_sources":
                rejected,
        }

        self.save_atomic(
            payload
        )

        return payload

    def retrieve(
        self,
        query: str,
        *,
        top_k: int = 5,
        minimum_score: float = 0.25,
    ) -> list[RetrievalResult]:
        normalized_query = str(
            query
        ).strip()

        if not normalized_query:
            raise ValueError(
                "Retrieval query cannot be blank."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be positive."
            )

        payload = self.load()

        chunks = payload.get(
            "chunks",
            [],
        )

        if not chunks:
            return []

        query_batch = (
            self.embedding_client.embed(
                [
                    normalized_query,
                ]
            )
        )

        query_vector = (
            query_batch.vectors[0]
        )

        dimensions = payload.get(
            "embedding_dimensions"
        )

        if dimensions != len(
            query_vector
        ):
            raise RuntimeError(
                "Query embedding dimensions do not "
                "match the local knowledge index."
            )

        ranked: list[
            RetrievalResult
        ] = []

        for raw_chunk in chunks:
            embedding = tuple(
                float(value)
                for value in raw_chunk.get(
                    "embedding",
                    []
                )
            )

            if len(embedding) != dimensions:
                continue

            score = cosine_similarity(
                query_vector,
                embedding,
            )

            if score < minimum_score:
                continue

            metadata = dict(
                raw_chunk.get(
                    "metadata",
                    {},
                )
            )

            ranked.append(
                RetrievalResult(
                    chunk_id=str(
                        raw_chunk[
                            "chunk_id"
                        ]
                    ),
                    document_id=str(
                        raw_chunk[
                            "document_id"
                        ]
                    ),
                    source_path=str(
                        raw_chunk[
                            "source_path"
                        ]
                    ),
                    title=str(
                        raw_chunk[
                            "title"
                        ]
                    ),
                    text=str(
                        raw_chunk[
                            "text"
                        ]
                    ),
                    score=round(
                        score,
                        8,
                    ),
                    citation=(
                        "["
                        + str(
                            raw_chunk[
                                "chunk_id"
                            ]
                        )
                        + "]"
                    ),
                    metadata=metadata,
                )
            )

        ranked.sort(
            key=lambda result: (
                -result.score,
                result.source_path,
                result.chunk_id,
            )
        )

        return ranked[
            :top_k
        ]


def discover_allowlisted_sources(
    root: Path,
) -> list[Path]:
    root = root.resolve()

    candidates: list[
        Path
    ] = []

    docs_root = root / "docs"

    if docs_root.exists():
        candidates.extend(
            path
            for path in docs_root.rglob(
                "*"
            )
            if path.is_file()
        )

    knowledge_root = (
        root
        / "knowledge"
        / "research"
    )

    if knowledge_root.exists():
        candidates.extend(
            path
            for path in knowledge_root.rglob(
                "*"
            )
            if path.is_file()
        )

    backend_root = (
        root
        / "backend"
        / "app"
    )

    if backend_root.exists():
        candidates.extend(
            path
            for path in backend_root.rglob(
                "*"
            )
            if path.is_file()
            and any(
                term in path.as_posix().lower()
                for term in (
                    "contract",
                    "policy",
                    "safety",
                    "governance",
                    "architecture",
                    "manifest",
                    "readme",
                    "route_protection",
                )
            )
        )

    return [
        path
        for path in candidates
        if (
            is_allowed_source(
                path,
                root=root,
            )
            and not (
                "knowledge" in path.relative_to(root).parts
                and "research" in path.relative_to(root).parts
                and "originals" in path.relative_to(root).parts
            )
        )
    ]
