#!/usr/bin/env python3
"""NeuroVest bounded, read-only architectural query engine."""
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

MAX_OUTPUT = 14000
MAX_DEPTH = 8

def load():
    if not INDEX.is_file() or not GRAPH.is_file():
        raise ValueError("ARCHITECTURE_DATA_MISSING")

    raw_index, raw_graph = read_active_pair()

    if len(raw_index) > 20_000_000 or len(raw_graph) > 20_000_000:
        raise ValueError("ARCHITECTURE_DATA_TOO_LARGE")

    inventory = json.loads(raw_index)
    graph = json.loads(raw_graph)

    if inventory.get("schema") != "neurovest.repository_intelligence.v1":
        raise ValueError("INVALID_INVENTORY_SCHEMA")

    if graph.get("schema") != "neurovest.repository_dependency_graph.v2":
        raise ValueError("INVALID_GRAPH_SCHEMA")

    if graph.get("inventory_sha256") != hashlib.sha256(
        raw_index
    ).hexdigest():
        raise ValueError("STALE_OR_MODIFIED_DEPENDENCY_GRAPH")

    stacks = inventory.get("backend_stacks")
    edges = graph.get("cross_stack_dependencies")

    if not isinstance(stacks, dict) or not isinstance(edges, list):
        raise ValueError("INVALID_ARCHITECTURE_DATA")

    if len(stacks) > 200 or len(edges) > 10000:
        raise ValueError("ARCHITECTURE_LIMIT_EXCEEDED")

    for name in stacks:
        if not isinstance(name, str) or not name.isidentifier():
            raise ValueError("INVALID_STACK_NAME")

    outgoing = defaultdict(dict)
    incoming = defaultdict(dict)

    for edge in edges:
        if not isinstance(edge, dict):
            raise ValueError("INVALID_EDGE")

        src = edge.get("source_stack")
        dst = edge.get("target_stack")
        count = edge.get("references")

        if (
            src not in stacks
            or dst not in stacks
            or type(count) is not int
            or count < 1
            or count > 100000
        ):
            raise ValueError("INVALID_EDGE_DATA")

        outgoing[src][dst] = count
        incoming[dst][src] = count

    return inventory, graph, stacks, outgoing, incoming

def impact(start, incoming):
    """Follow reverse dependency edges with bounded BFS."""
    queue = deque([(start, 0)])
    seen = {start: 0}

    while queue:
        current, depth = queue.popleft()

        if depth >= MAX_DEPTH:
            continue

        for dependent in sorted(incoming.get(current, {})):
            if dependent not in seen:
                seen[dependent] = depth + 1
                queue.append((dependent, depth + 1))

    return seen

def main():
    if len(sys.argv) not in (2, 3):
        print(
            "USAGE: neuro_repository_query.py "
            "summary|dependencies|dependents|impact [stack]"
        )
        return 2

    action = sys.argv[1]

    if action not in {
        "summary", "dependencies", "dependents", "impact"
    }:
        print("ERROR=UNSUPPORTED_QUERY")
        return 2

    if (action == "summary") != (len(sys.argv) == 2):
        print("ERROR=INVALID_ARGUMENT_COUNT")
        return 2

    try:
        inventory, graph, stacks, outgoing, incoming = load()
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print("ERROR=" + str(exc)[:120])
        return 1

    lines = [
        "NEUROVEST REPOSITORY INTELLIGENCE",
        "Mode: READ_ONLY",
        "Evidence: dependency_graph_v2.json",
        "Warning: static import relationships; not runtime call tracing.",
        "",
    ]

    if action == "summary":
        lines.extend([
            "SOURCE_FILES=" + str(graph["files_indexed"]),
            "BACKEND_STACKS=" + str(len(stacks)),
            "FILE_DEPENDENCY_EDGES=" + str(
                len(graph.get("resolved_file_edges", []))
            ),
            "CROSS_STACK_RELATIONSHIPS=" + str(
                len(graph["cross_stack_dependencies"])
            ),
            "",
            "INDEXED BACKEND STACKS:",
        ])

        for stack in sorted(stacks):
            lines.append(
                f"  {stack}: {stacks[stack]} indexed files"
            )

    else:
        name = sys.argv[2]

        if name not in stacks:
            print("ERROR=STACK_NOT_IN_INDEX")
            return 2

        lines.append("STACK=" + name)
        lines.append("INDEXED_FILES=" + str(stacks[name]))
        lines.append("")

        if action == "dependencies":
            lines.append("DIRECT DEPENDENCIES:")
            records = outgoing.get(name, {})
            for other, count in sorted(records.items()):
                lines.append(
                    f"  {name} -> {other} ({count} import references)"
                )
            if not records:
                lines.append("  None detected")

        elif action == "dependents":
            lines.append("DIRECT DEPENDENTS:")
            records = incoming.get(name, {})
            for other, count in sorted(records.items()):
                lines.append(
                    f"  {other} -> {name} ({count} import references)"
                )
            if not records:
                lines.append("  None detected")

        elif action == "impact":
            affected = impact(name, incoming)
            lines.append("POTENTIALLY AFFECTED STACKS:")
            lines.append("  depth 0: " + name + " (selected stack)")

            for other, depth in sorted(
                affected.items(), key=lambda pair: (pair[1], pair[0])
            ):
                if other != name:
                    lines.append(
                        f"  depth {depth}: {other}"
                    )

            lines.extend([
                "",
                "This is a conservative static dependency estimate.",
                "It does not prove an actual regression or select tests.",
                "Dynamic imports, service calls, and excluded modules",
                "may add dependencies not shown here.",
            ])

    report = "\n".join(lines)

    if len(report) > MAX_OUTPUT:
        print("ERROR=QUERY_OUTPUT_LIMIT")
        return 1

    print(report)
    print()
    print("QUERY_STATUS=PASS")
    print("PATCH_APPLIED=False")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
