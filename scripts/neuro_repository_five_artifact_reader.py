#!/usr/bin/env python3
"""Read five repository artifacts from one manifest-verified generation."""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "runtime/qualification/repository_intelligence_v1"
GENERATIONS = DATA / "generations"
CURRENT = DATA / "current"

NAMES = (
    "inventory.json",
    "dependency_graph.json",
    "dependency_graph_v2.json",
    "function_intelligence_v1.json",
    "function_call_graph_v1.json",
)

GENERATION_PATTERN = re.compile(
    r"generation_[0-9]{8}T[0-9]{6}_[0-9a-f]{12}\Z"
)

LIMIT = 20_000_000

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def require(condition, reason):
    if not condition:
        raise ValueError(reason)

def read_safe(path):
    require(
        not path.is_symlink() and path.is_file(),
        "UNSAFE_OR_MISSING_ARTIFACT",
    )
    require(path.stat().st_size <= LIMIT, "ARTIFACT_SIZE_LIMIT")
    raw = path.read_bytes()
    require(len(raw) <= LIMIT, "ARTIFACT_SIZE_LIMIT")
    return raw

def read_bundle():
    """Pin current once; return five verified blobs and generation ID."""
    require(
        CURRENT.is_symlink()
        and not DATA.is_symlink()
        and not GENERATIONS.is_symlink(),
        "UNSAFE_GENERATION_ROOT",
    )

    target = os.readlink(CURRENT)
    parts = Path(target).parts

    require(
        not Path(target).is_absolute()
        and len(parts) == 2
        and parts[0] == "generations"
        and GENERATION_PATTERN.fullmatch(parts[1]) is not None,
        "INVALID_ACTIVE_POINTER",
    )

    name = parts[1]
    directory = GENERATIONS / name

    require(
        directory.is_dir() and not directory.is_symlink(),
        "GENERATION_MISSING",
    )

    manifest = json.loads(read_safe(directory / "manifest.json"))

    require(
        isinstance(manifest, dict)
        and manifest.get("schema") == "neurovest.snapshot.v1"
        and manifest.get("generation") == name,
        "MANIFEST_MISMATCH",
    )

    hashes = manifest.get("sha256")

    require(isinstance(hashes, dict), "INVALID_MANIFEST_HASHES")

    # Five artifacts are mandatory. No legacy-file fallback.
    blobs = {
        filename: read_safe(directory / filename)
        for filename in NAMES
    }

    for filename, raw in blobs.items():
        require(
            hashes.get(filename) == sha(raw),
            "ARTIFACT_INTEGRITY_FAILURE_" + filename,
        )

    docs = {
        filename: json.loads(raw)
        for filename, raw in blobs.items()
    }

    inventory = docs["inventory.json"]
    graph1 = docs["dependency_graph.json"]
    graph2 = docs["dependency_graph_v2.json"]
    function_index = docs["function_intelligence_v1.json"]
    function_graph = docs["function_call_graph_v1.json"]

    require(
        inventory.get("schema")
            == "neurovest.repository_intelligence.v1"
        and graph1.get("schema")
            == "neurovest.repository_dependency_graph.v1"
        and graph2.get("schema")
            == "neurovest.repository_dependency_graph.v2"
        and function_index.get("schema")
            == "neurovest.function_intelligence.v1"
        and function_graph.get("schema")
            == "neurovest.function_call_graph.v1",
        "ARTIFACT_SCHEMA_MISMATCH",
    )

    inventory_hash = sha(blobs["inventory.json"])
    graph1_hash = sha(blobs["dependency_graph.json"])
    graph2_hash = sha(blobs["dependency_graph_v2.json"])
    function_hash = sha(blobs["function_intelligence_v1.json"])

    require(
        graph1.get("inventory_sha256") == inventory_hash
        and graph2.get("inventory_sha256") == inventory_hash
        and graph2.get("graph_v1_sha256") == graph1_hash,
        "REPOSITORY_HASH_CHAIN_FAILED",
    )

    require(
        function_index.get("inventory_sha256") == inventory_hash
        and function_index.get("graph_v2_sha256") == graph2_hash
        and function_graph.get("function_index_sha256") == function_hash
        and function_graph.get("inventory_sha256") == inventory_hash
        and function_graph.get("graph_v2_sha256") == graph2_hash,
        "FUNCTION_HASH_CHAIN_FAILED",
    )

    functions = function_index.get("functions")
    edges = function_graph.get("edges")

    require(
        isinstance(functions, list)
        and len(functions) <= 50000
        and isinstance(edges, list)
        and len(edges) <= 100000
        and function_index.get("function_count") == len(functions)
        and function_graph.get("indexed_functions") == len(functions)
        and function_graph.get("candidate_edges") == len(edges),
        "FUNCTION_COUNT_INCONSISTENCY",
    )

    return name, blobs
