#!/usr/bin/env python3
"""Conservative candidate function-call graph from indexed AST metadata."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from neuro_repository_snapshot_reader import read_active_pair

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "runtime/qualification/repository_intelligence_v1"
FUNCTION_INDEX = DATA / "function_intelligence_v1.json"
OUTPUT = DATA / "function_call_graph_v1.json"

MAX_BYTES = 20_000_000
MAX_EDGES = 100000

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def require(condition, reason):
    if not condition:
        raise ValueError(reason)

def load():
    inventory_raw, graph_raw = read_active_pair()

    require(
        FUNCTION_INDEX.is_file() and not FUNCTION_INDEX.is_symlink(),
        "FUNCTION_INDEX_MISSING",
    )

    require(
        FUNCTION_INDEX.stat().st_size <= MAX_BYTES,
        "FUNCTION_INDEX_SIZE_LIMIT",
    )

    raw = FUNCTION_INDEX.read_bytes()
    require(len(raw) <= MAX_BYTES, "FUNCTION_INDEX_SIZE_LIMIT")

    document = json.loads(raw)

    require(
        document.get("schema") == "neurovest.function_intelligence.v1",
        "FUNCTION_INDEX_SCHEMA",
    )
    require(
        document.get("inventory_sha256") == digest(inventory_raw),
        "STALE_FUNCTION_INVENTORY",
    )
    require(
        document.get("graph_v2_sha256") == digest(graph_raw),
        "STALE_FUNCTION_GRAPH",
    )

    functions = document.get("functions")
    require(isinstance(functions, list), "INVALID_FUNCTION_RECORDS")
    require(len(functions) <= 50000, "FUNCTION_COUNT_LIMIT")

    return document, raw, functions

def build(functions):
    by_file = defaultdict(dict)
    records = []
    skipped = Counter()

    for item in functions:
        if not isinstance(item, dict):
            skipped["invalid_record"] += 1
            continue

        file = item.get("file")
        symbol = item.get("symbol")
        calls = item.get("call_names")

        if (
            not isinstance(file, str)
            or not isinstance(symbol, str)
            or not isinstance(calls, list)
            or not all(isinstance(c, str) for c in calls)
        ):
            skipped["invalid_record"] += 1
            continue

        require(len(calls) <= 25, "CALL_NAME_LIMIT")

        key = (file, symbol)
        records.append((key, item))
        by_file[file].setdefault(symbol, []).append(item)

    edges = set()

    for (file, symbol), item in records:
        parts = symbol.split(".")

        for call in item["call_names"]:
            destination = None
            resolution = None

            # Top-level functions invoking other top-level
            # functions defined in the same source file.
            if len(parts) == 1 and call.isidentifier():
                matches = by_file[file].get(call, [])

                if len(matches) == 1:
                    destination = call
                    resolution = "same_file_top_level_candidate"

            # Class methods invoking self.method().
            # Nested functions and ambiguous definitions
            # are deliberately not resolved.
            elif (
                len(parts) == 2
                and call.startswith("self.")
                and call.count(".") == 1
            ):
                method = call[5:]

                if method.isidentifier():
                    candidate = parts[0] + "." + method
                    matches = by_file[file].get(candidate, [])

                    if len(matches) == 1:
                        destination = candidate
                        resolution = "same_class_self_candidate"

            if destination is None:
                skipped["unresolved_or_ambiguous_call"] += 1
                continue

            if destination == symbol:
                skipped["self_recursion"] += 1
                continue

            edges.add((file, symbol, destination, resolution))

            require(len(edges) <= MAX_EDGES, "EDGE_LIMIT")

    result = [
        {
            "file": file,
            "caller": caller,
            "callee": callee,
            "classification": classification,
        }
        for file, caller, callee, classification in sorted(edges)
    ]

    return result, skipped

def main():
    print("=" * 70)
    print("NEUROVEST — FUNCTION CALL GRAPH V1")
    print("=" * 70)

    if len(sys.argv) != 1:
        raise ValueError("UNEXPECTED_ARGUMENTS")

    if OUTPUT.exists() or OUTPUT.is_symlink():
        raise ValueError("GRAPH_ALREADY_EXISTS")

    document, raw_index, functions = load()
    edges, skipped = build(functions)

    counts = Counter(
        edge["classification"]
        for edge in edges
    )

    report = {
        "schema": "neurovest.function_call_graph.v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "function_index_sha256": digest(raw_index),
        "inventory_sha256": document["inventory_sha256"],
        "graph_v2_sha256": document["graph_v2_sha256"],
        "indexed_functions": len(functions),
        "candidate_edges": len(edges),
        "classifications": dict(counts),
        "skipped": dict(skipped),
        "edges": edges,
        "limitations": [
            "Candidate relationships, not verified runtime calls",
            "Only unambiguous same-file top-level and self.method names",
            "Local variable and attribute shadowing not proven absent",
            "Cross-file imports and dynamic dispatch not resolved",
            "Call-name index is truncated to 25 names per function",
            "Changed files excluded by the function index",
            "No source execution or source-body retention",
        ],
    }

    serialized = (
        json.dumps(report, indent=2) + "\n"
    ).encode("utf-8")

    require(len(serialized) <= MAX_BYTES, "OUTPUT_SIZE_LIMIT")

    # Reconfirm the source index did not change during construction.
    require(
        digest(FUNCTION_INDEX.read_bytes()) == digest(raw_index),
        "FUNCTION_INDEX_CHANGED",
    )

    pending = DATA / ".function_call_graph_v1.pending"

    require(
        not pending.exists() and not pending.is_symlink(),
        "PENDING_GRAPH_EXISTS",
    )

    try:
        with pending.open("xb") as handle:
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())

        pending.chmod(0o600)
        os.replace(pending, OUTPUT)
    finally:
        if pending.exists():
            pending.unlink()

    print("INDEXED_FUNCTIONS=", len(functions))
    print("CANDIDATE_CALL_EDGES=", len(edges))

    for name, count in sorted(counts.items()):
        print(name.upper(), "=", count)

    print(
        "UNRESOLVED_OR_AMBIGUOUS_CALLS=",
        skipped["unresolved_or_ambiguous_call"],
    )

    print()
    print("=== CHAT RUNTIME CANDIDATES ===")

    examples = [
        e for e in edges
        if e["file"].endswith("/chat_runtime.py")
    ]

    for edge in examples[:20]:
        print(
            edge["caller"],
            "->",
            edge["callee"],
            "(" + edge["classification"] + ")",
        )

    print("CHAT_RUNTIME_CANDIDATE_EDGES=", len(examples))
    print()
    print("GRAPH_SHA256=", digest(OUTPUT.read_bytes()))
    print("SOURCE_FILES_MODIFIED=False")
    print("BACKEND_RESTARTED=False")
    print("DATABASE_MODIFIED=False")
    print("PATCH_APPLIED=False")
    print("FUNCTION_CALL_GRAPH_V1=PASS")
    print("Terminal remains open.")

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print("FUNCTION_CALL_GRAPH_V1=FAILED")
        print("REASON=", str(exc)[:180])
        raise SystemExit(1)
