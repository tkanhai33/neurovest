#!/usr/bin/env python3
"""Bounded, read-only NeuroVest file impact analysis."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import defaultdict, deque
from pathlib import Path
from neuro_repository_snapshot_reader import read_active_pair

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "runtime/qualification/repository_intelligence_v1"
INDEX = DATA / "inventory.json"
GRAPH = DATA / "dependency_graph_v2.json"

MAX_DEPTH = 5
MAX_OUTPUT_FILES = 60
MAX_DATA_BYTES = 20_000_000

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def fail(reason):
    print("QUERY_STATUS=BLOCKED")
    print("REASON=" + reason)
    return 1

def load():
    raw_index, raw_graph = read_active_pair()

    if (
        len(raw_index) > MAX_DATA_BYTES
        or len(raw_graph) > MAX_DATA_BYTES
    ):
        raise ValueError("DATA_SIZE_LIMIT")

    index = json.loads(raw_index)
    graph = json.loads(raw_graph)

    if index.get("schema") != "neurovest.repository_intelligence.v1":
        raise ValueError("INDEX_SCHEMA")

    if graph.get("schema") != "neurovest.repository_dependency_graph.v2":
        raise ValueError("GRAPH_SCHEMA")

    if graph.get("inventory_sha256") != digest(raw_index):
        raise ValueError("STALE_GRAPH")

    records = index.get("files")
    edges = graph.get("resolved_file_edges")

    if not isinstance(records, list) or not isinstance(edges, list):
        raise ValueError("INVALID_GRAPH_DATA")

    if len(records) > 30000 or len(edges) > 100000:
        raise ValueError("GRAPH_LIMIT")

    indexed = {}

    for item in records:
        if not isinstance(item, dict):
            raise ValueError("INVALID_FILE_RECORD")

        path = item.get("path")
        fingerprint = item.get("sha256")

        if not isinstance(path, str) or not isinstance(fingerprint, str):
            raise ValueError("INVALID_FILE_RECORD")

        parts = Path(path).parts
        if (
            not parts
            or parts[0] not in {
                "backend", "frontend", "scripts", "tests", "alembic"
            }
            or ".." in parts
            or Path(path).is_absolute()
            or len(path) > 500
        ):
            raise ValueError("UNSAFE_FILE_RECORD")

        indexed[path] = fingerprint

    reverse = defaultdict(set)

    for edge in edges:
        if not isinstance(edge, dict):
            raise ValueError("INVALID_EDGE")

        source = edge.get("source")
        destination = edge.get("destination")

        if source not in indexed or destination not in indexed:
            raise ValueError("EDGE_OUTSIDE_INDEX")

        reverse[destination].add(source)

    return indexed, reverse, graph

def test_file(path):
    name = Path(path).name
    return (
        name.startswith("test_")
        or name.endswith((".test.ts", ".test.tsx", ".test.js",
                          ".spec.ts", ".spec.tsx", ".spec.js"))
    )

def freshness(path, expected):
    current = ROOT

    for part in Path(path).parts:
        current = current / part
        if current.is_symlink():
            return "UNSAFE_SYMLINK"

    try:
        if not current.is_file():
            return "MISSING"
        if current.stat().st_size > 1_048_576:
            return "SIZE_LIMIT"
        actual = hashlib.sha256(current.read_bytes()).hexdigest()
        return "CURRENT" if actual == expected else "CHANGED"
    except OSError:
        return "UNREADABLE"

def analyze(target, indexed, reverse):
    found = {target: 0}
    queue = deque([target])

    while queue:
        node = queue.popleft()
        depth = found[node]

        if depth >= MAX_DEPTH:
            continue

        for dependent in sorted(reverse.get(node, ())):
            if dependent not in found:
                found[dependent] = depth + 1
                queue.append(dependent)

    return found

def main():
    if len(sys.argv) != 2:
        return fail("USAGE_FILE_PATH_REQUIRED")

    target = sys.argv[1]

    try:
        indexed, reverse, graph = load()
    except (OSError, ValueError, TypeError) as exc:
        return fail(type(exc).__name__)

    if target not in indexed:
        return fail("FILE_NOT_IN_INDEX")

    affected = analyze(target, indexed, reverse)
    dependents = [
        (path, depth)
        for path, depth in affected.items()
        if path != target
    ]
    dependents.sort(key=lambda entry: (entry[1], entry[0]))

    tests = [
        (path, depth)
        for path, depth in dependents
        if test_file(path)
    ]
    other_files = [
        (path, depth)
        for path, depth in dependents
        if not test_file(path)
    ]

    stale = [
        (path, freshness(path, indexed[path]))
        for path in affected
    ]
    stale = [
        (path, state)
        for path, state in stale
        if state != "CURRENT"
    ]

    print("NEUROVEST FILE IMPACT INTELLIGENCE")
    print("MODE=READ_ONLY")
    print("TARGET=" + target)
    print("TARGET_FRESHNESS=" + freshness(target, indexed[target]))
    print("STATIC_DEPENDENT_FILES=" + str(len(dependents)))
    print("STATIC_TEST_CANDIDATES=" + str(len(tests)))
    print("SNAPSHOT_MISMATCHES_IN_REACHABLE_FILES=" + str(len(stale)))

    print("\nDIRECT/INDIRECT FILE DEPENDENTS:")
    for path, depth in other_files[:MAX_OUTPUT_FILES]:
        print(f"  depth {depth}: {path}")

    if len(other_files) > MAX_OUTPUT_FILES:
        print("  ADDITIONAL_FILES_OMITTED=" +
              str(len(other_files) - MAX_OUTPUT_FILES))

    print("\nTEST CANDIDATES FROM IMPORT EVIDENCE:")
    for path, depth in tests[:MAX_OUTPUT_FILES]:
        print(f"  depth {depth}: {path}")

    if not tests:
        print("  None resolved through static imports")

    print("\nCHANGED OR UNVERIFIED SNAPSHOT FILES:")
    for path, state in sorted(stale)[:30]:
        print(f"  {state}: {path}")

    if len(stale) > 30:
        print("  ADDITIONAL_MISMATCHES=" + str(len(stale) - 30))

    print("\nLIMITATIONS:")
    print("  Static imports only; dynamic dependencies not included.")
    print("  Test suggestions are candidates, not guaranteed coverage.")
    print("  No tests were executed.")
    print("  A current target does not prove the entire index is fresh.")
    print("  Snapshot mismatches require inventory regeneration.")

    print("\nQUERY_STATUS=PASS")
    print("PATCH_APPLIED=False")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
