#!/usr/bin/env python3
"""
Build the controlled NeuroVest local knowledge index.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from backend.app.stacks.chat_public.rag.local_index import (
    LocalKnowledgeIndex,
    discover_allowlisted_sources,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build the NeuroVest controlled "
            "local retrieval index."
        )
    )

    parser.add_argument(
        "--root",
        default=".",
    )

    parser.add_argument(
        "--index",
        default=(
            "runtime/cognitive_engine/rag/"
            "neuro_knowledge_index.json"
        ),
    )

    parser.add_argument(
        "--chunk-words",
        type=int,
        default=180,
    )

    parser.add_argument(
        "--overlap-words",
        type=int,
        default=30,
    )

    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()

    root = Path(
        arguments.root
    ).resolve()

    index_path = Path(
        arguments.index
    )

    sources = discover_allowlisted_sources(
        root
    )

    if not sources:
        raise SystemExit(
            "BLOCKED: no allowlisted RAG sources found."
        )

    index = LocalKnowledgeIndex(
        index_path=index_path,
    )

    result = index.build_from_paths(
        paths=sources,
        root=root,
        chunk_words=arguments.chunk_words,
        overlap_words=arguments.overlap_words,
    )

    summary = {
        "status": "qualified",
        "index_path":
            str(
                index_path
            ),
        "embedding_model":
            result[
                "embedding_model"
            ],
        "embedding_dimensions":
            result[
                "embedding_dimensions"
            ],
        "document_count":
            result[
                "document_count"
            ],
        "chunk_count":
            result[
                "chunk_count"
            ],
        "rejected_source_count":
            len(
                result.get(
                    "rejected_sources",
                    []
                )
            ),
    }

    print(
        json.dumps(
            summary,
            indent=2,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
