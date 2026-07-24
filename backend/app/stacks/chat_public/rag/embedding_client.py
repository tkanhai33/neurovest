"""
Canonical Ollama embedding client for NeuroVest retrieval.
"""

from __future__ import annotations

import json
import math
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Sequence


DEFAULT_EMBEDDING_MODEL = (
    "nomic-embed-text:latest"
)

DEFAULT_EMBEDDING_URL = (
    "http://127.0.0.1:11434/api/embed"
)


class EmbeddingError(
    RuntimeError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class EmbeddingBatch:
    model: str
    dimensions: int
    vectors: tuple[
        tuple[float, ...],
        ...,
    ]


def normalize_vector(
    vector: Sequence[float],
) -> tuple[float, ...]:
    converted = tuple(
        float(value)
        for value in vector
    )

    if not converted:
        raise EmbeddingError(
            "Embedding vector cannot be empty."
        )

    if not all(
        math.isfinite(value)
        for value in converted
    ):
        raise EmbeddingError(
            "Embedding vector contains "
            "a non-finite value."
        )

    magnitude = math.sqrt(
        sum(
            value * value
            for value in converted
        )
    )

    if magnitude <= 0:
        raise EmbeddingError(
            "Embedding vector has zero magnitude."
        )

    return tuple(
        value / magnitude
        for value in converted
    )


class OllamaEmbeddingClient:
    def __init__(
        self,
        *,
        model: str = DEFAULT_EMBEDDING_MODEL,
        endpoint: str = DEFAULT_EMBEDDING_URL,
        timeout_seconds: float = 300.0,
    ) -> None:
        self.model = str(
            model
        ).strip()

        self.endpoint = str(
            endpoint
        ).strip()

        self.timeout_seconds = float(
            timeout_seconds
        )

        if not self.model:
            raise ValueError(
                "Embedding model cannot be empty."
            )

        if not self.endpoint:
            raise ValueError(
                "Embedding endpoint cannot be empty."
            )

    def embed(
        self,
        texts: Sequence[str],
    ) -> EmbeddingBatch:
        normalized_inputs = [
            str(text).strip()
            for text in texts
        ]

        if not normalized_inputs:
            raise EmbeddingError(
                "At least one embedding input is required."
            )

        if any(
            not text
            for text in normalized_inputs
        ):
            raise EmbeddingError(
                "Embedding input cannot be blank."
            )

        payload = json.dumps(
            {
                "model": self.model,
                "input": normalized_inputs,
                "truncate": True,
                "keep_alive": "10m",
            }
        ).encode(
            "utf-8"
        )

        request = urllib.request.Request(
            self.endpoint,
            data=payload,
            headers={
                "Content-Type":
                    "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout_seconds,
            ) as response:
                result: dict[str, Any] = (
                    json.load(
                        response
                    )
                )
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
        ) as error:
            raise EmbeddingError(
                "Ollama embedding request failed: "
                f"{type(error).__name__}: {error}"
            ) from error

        raw_vectors = result.get(
            "embeddings"
        )

        if not isinstance(
            raw_vectors,
            list,
        ):
            raise EmbeddingError(
                "Embedding API returned no vectors."
            )

        if len(raw_vectors) != len(
            normalized_inputs
        ):
            raise EmbeddingError(
                "Embedding count does not match "
                "the input count."
            )

        vectors = tuple(
            normalize_vector(
                vector
            )
            for vector in raw_vectors
            if isinstance(
                vector,
                list,
            )
        )

        if len(vectors) != len(
            normalized_inputs
        ):
            raise EmbeddingError(
                "Embedding response contains "
                "an invalid vector."
            )

        dimensions = {
            len(vector)
            for vector in vectors
        }

        if len(dimensions) != 1:
            raise EmbeddingError(
                "Embedding dimensions are inconsistent."
            )

        return EmbeddingBatch(
            model=self.model,
            dimensions=next(
                iter(
                    dimensions
                )
            ),
            vectors=vectors,
        )
