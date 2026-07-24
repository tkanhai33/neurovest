#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
GRAPH = ROOT / "runtime" / "repo_memory" / "dependency_graph_v1.json"
OUT_DIR = ROOT / "runtime" / "certifications"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "phase6d_dependency_graph_certification_latest.json"

REQUIRED_NODES = [
    "backend/app/stacks/execution/paper_broker.py",
    "backend/app/stacks/journal_ledger/ledger.py",
    "backend/app/stacks/chat_public/chat_runtime.py",
    "backend/app/main.py",
]

REQUIRED_EDGES = [
    (
        "backend/app/stacks/execution/paper_broker.py",
        "backend/app/stacks/journal_ledger/ledger.py",
    ),
    (
        "backend/app/stacks/chat_public/chat_runtime.py",
        "backend/app/stacks/execution/paper_broker.py",
    ),
    (
        "backend/app/main.py",
        "backend/app/stacks/execution/paper_broker.py",
    ),
]


def run(cmd):
    return subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def main():
    print("🧠 PHASE 6D DEPENDENCY GRAPH CERTIFICATION")

    run(["python3", "scripts/phase4_repo_memory_indexer_v2.py"])
    run(["python3", "scripts/phase6c_dependency_graph_export.py"])

    if not GRAPH.exists():
        print("dependency graph missing")
        sys.exit(1)

    graph = json.loads(GRAPH.read_text())
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    node_ids = {n.get("id") for n in nodes}
    edge_pairs = {(e.get("from"), e.get("to")) for e in edges}

    top_imported = graph.get("top_imported", [])
    top_importers = graph.get("top_importers", [])

    checks = {
        "graph_file_exists": GRAPH.exists(),
        "node_count_ok": graph.get("node_count", 0) > 0,
        "edge_count_ok": graph.get("edge_count", 0) > 0,
        "node_count_matches": graph.get("node_count") == len(nodes),
        "edge_count_matches": graph.get("edge_count") == len(edges),
        "required_nodes_present": all(n in node_ids for n in REQUIRED_NODES),
        "required_edges_present": all(e in edge_pairs for e in REQUIRED_EDGES),
        "top_imported_present": len(top_imported) > 0,
        "top_importers_present": len(top_importers) > 0,
        "ledger_is_top_imported": any(
            x.get("file") == "backend/app/stacks/journal_ledger/ledger.py"
            for x in top_imported[:5]
        ),
        "paper_broker_is_top_importer": any(
            x.get("file") == "backend/app/stacks/execution/paper_broker.py"
            for x in top_importers[:5]
        ),
    }

    certified = all(checks.values())

    report = {
        "phase": "6D_DEPENDENCY_GRAPH_CERTIFICATION",
        "generated_at": datetime.now(UTC).isoformat(),
        "certified": certified,
        "checks": checks,
        "graph_summary": {
            "node_count": graph.get("node_count"),
            "edge_count": graph.get("edge_count"),
            "top_imported": top_imported[:10],
            "top_importers": top_importers[:10],
        },
    }

    OUT_JSON.write_text(json.dumps(report, indent=2))

    print(json.dumps({
        "phase": report["phase"],
        "certified": certified,
        "checks": checks,
        "output": str(OUT_JSON),
    }, indent=2))

    if not certified:
        sys.exit(1)


if __name__ == "__main__":
    main()
