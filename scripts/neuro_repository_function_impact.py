#!/usr/bin/env python3
"""Snapshot-bound, read-only function impact query."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from neuro_repository_snapshot_reader import read_active_pair
from neuro_repository_five_artifact_reader import read_bundle, CURRENT as FUNCTION_CURRENT

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "runtime/qualification/repository_intelligence_v1"
INDEX = DATA / "function_intelligence_v1.json"
GRAPH = DATA / "function_call_graph_v1.json"
LIMIT = 30
MAX_BYTES = 20_000_000

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def require(value, message):
    if not value:
        raise ValueError(message)

def read_json(path):
    require(path.is_file() and not path.is_symlink(),
            "MISSING_OR_UNSAFE_ARTIFACT")
    require(path.stat().st_size <= MAX_BYTES, "SIZE_LIMIT")
    raw = path.read_bytes()
    require(len(raw) <= MAX_BYTES, "SIZE_LIMIT")
    return json.loads(raw), raw

def load():
    """Read either a complete five-artifact generation or verified V1 legacy.

    Legacy compatibility is allowed ONLY for manifests that explicitly
    lack both function-artifact entries. Five-artifact corruption never
    falls back to separate legacy files.
    """
    require(FUNCTION_CURRENT.is_symlink(),
            "ACTIVE_GENERATION_MISSING")

    pinned = __import__("os").readlink(FUNCTION_CURRENT)

    # Verify repository artifacts using the established reader.
    inventory_raw, dependency_raw = read_active_pair()

    require(
        __import__("os").readlink(FUNCTION_CURRENT) == pinned,
        "ACTIVE_GENERATION_CHANGED",
    )

    manifest_path = DATA / pinned / "manifest.json"
    manifest, _manifest_raw = read_json(manifest_path)

    hashes = manifest.get("sha256")
    require(isinstance(hashes, dict), "INVALID_MANIFEST_HASHES")

    function_names = (
        "function_intelligence_v1.json",
        "function_call_graph_v1.json",
    )

    present = [name in hashes for name in function_names]

    if any(present):
        require(all(present), "INCOMPLETE_FUNCTION_MANIFEST")

        generation, blobs = read_bundle()

        require(
            generation == Path(pinned).name,
            "GENERATION_MISMATCH",
        )
        require(
            __import__("os").readlink(FUNCTION_CURRENT) == pinned,
            "ACTIVE_GENERATION_CHANGED",
        )

        index_raw = blobs["function_intelligence_v1.json"]
        graph_raw = blobs["function_call_graph_v1.json"]

        index = json.loads(index_raw)
        graph = json.loads(graph_raw)

    else:
        # Transitional three-artifact generation only.
        # The independent legacy files must match the pinned snapshot.
        index, index_raw = read_json(INDEX)
        graph, graph_raw = read_json(GRAPH)

        require(
            __import__("os").readlink(FUNCTION_CURRENT) == pinned,
            "ACTIVE_GENERATION_CHANGED",
        )

    require(
        index.get("schema") == "neurovest.function_intelligence.v1",
        "INDEX_SCHEMA_MISMATCH",
    )
    require(
        graph.get("schema") == "neurovest.function_call_graph.v1",
        "GRAPH_SCHEMA_MISMATCH",
    )

    require(
        index.get("inventory_sha256") == digest(inventory_raw),
        "STALE_FUNCTION_INDEX",
    )
    require(
        index.get("graph_v2_sha256") == digest(dependency_raw),
        "STALE_DEPENDENCY_GRAPH",
    )
    require(
        graph.get("function_index_sha256") == digest(index_raw),
        "STALE_FUNCTION_CALL_GRAPH",
    )
    require(
        graph.get("inventory_sha256") == digest(inventory_raw),
        "CALL_GRAPH_INVENTORY_MISMATCH",
    )
    require(
        graph.get("graph_v2_sha256") == digest(dependency_raw),
        "CALL_GRAPH_DEPENDENCY_MISMATCH",
    )

    functions = index.get("functions")
    edges = graph.get("edges")

    require(
        isinstance(functions, list)
        and len(functions) <= 50000
        and index.get("function_count") == len(functions),
        "INVALID_FUNCTIONS",
    )
    require(
        isinstance(edges, list)
        and len(edges) <= 100000
        and graph.get("indexed_functions") == len(functions)
        and graph.get("candidate_edges") == len(edges),
        "INVALID_EDGES",
    )

    require(
        __import__("os").readlink(FUNCTION_CURRENT) == pinned,
        "ACTIVE_GENERATION_CHANGED",
    )

    return functions, edges

def main():
    functions, edges = load()
    args = sys.argv[1:]

    if args == ["summary"]:
        print("INDEXED_FUNCTIONS=", len(functions))
        print("CANDIDATE_EDGES=", len(edges))
        print("QUERY_STATUS=PASS")
        return 0

    require(len(args) == 3 and args[0] == "symbol",
            "USAGE: symbol FILE SYMBOL")
    _, file, symbol = args

    require(
        file.startswith(("backend/", "frontend/", "scripts/",
                         "tests/", "alembic/"))
        and ".." not in Path(file).parts
        and not Path(file).is_absolute(),
        "INVALID_FILE_PATH",
    )
    require(len(file) <= 400 and len(symbol) <= 200,
            "INPUT_LIMIT")

    matches = [
        item for item in functions
        if item.get("file") == file
        and item.get("symbol") == symbol
    ]

    require(len(matches) == 1, "SYMBOL_NOT_UNIQUE_OR_MISSING")
    item = matches[0]

    callers = [
        e for e in edges
        if e.get("file") == file and e.get("callee") == symbol
    ]
    callees = [
        e for e in edges
        if e.get("file") == file and e.get("caller") == symbol
    ]

    # These are name-based suggestions only, not verified coverage.
    leaf = symbol.split(".")[-1].lower()
    test_candidates = [
        f for f in functions
        if (
            "/test_" in "/" + f.get("file", "")
            or f.get("file", "").startswith("tests/test_")
        )
        and (
            leaf in f.get("symbol", "").lower()
            or leaf in [
                str(c).lower()
                for c in f.get("call_names", [])
            ]
        )
    ]

    test_files = sorted({
        t["file"] for t in test_candidates
    })

    print("FILE=", file)
    print("SYMBOL=", symbol)
    print("LINES=", item.get("line_start"),
          "-", item.get("line_end"))
    print("DIRECT_CALLER_CANDIDATES=", len(callers))
    print("DIRECT_CALLEE_CANDIDATES=", len(callees))
    print("NAME_MATCH_TEST_FILES=", len(test_files))

    print()
    print("=== CALLER CANDIDATES ===")
    for edge in callers[:LIMIT]:
        print(edge["caller"], "->", symbol,
              "[" + edge["classification"] + "]")

    print()
    print("=== CALLEE CANDIDATES ===")
    for edge in callees[:LIMIT]:
        print(symbol, "->", edge["callee"],
              "[" + edge["classification"] + "]")

    print()
    print("=== NAME-MATCH TEST CANDIDATES ===")
    for name in test_files[:LIMIT]:
        print(name)

    print()
    print("CALLERS_TRUNCATED=", len(callers) > LIMIT)
    print("CALLEES_TRUNCATED=", len(callees) > LIMIT)
    print("TESTS_TRUNCATED=", len(test_files) > LIMIT)
    print("RUNTIME_CALLS_VERIFIED=False")
    print("TEST_COVERAGE_VERIFIED=False")
    print("TESTS_EXECUTED=False")
    print("PATCH_APPLIED=False")
    print("QUERY_STATUS=PASS")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("QUERY_STATUS=FAILED")
        print("REASON=", str(exc)[:200])
        raise SystemExit(1)
