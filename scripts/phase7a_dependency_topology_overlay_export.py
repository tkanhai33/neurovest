#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()

DEP_GRAPH = ROOT / "runtime" / "repo_memory" / "dependency_graph_v1.json"
OUT_DIR = ROOT / "runtime" / "repo_memory"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "dependency_topology_overlay_v1.json"

STACK_TO_TOPOLOGY = {
    "chat_public": "Chat Runtime\n(chat_public)",
    "execution": "Execution Engine\n(execution.paper_broker)",
    "journal_ledger": "PostgreSQL Container\n(journal_ledger.ledger)",
    "portfolio": "Equity Calculator\n(portfolio.accounting)",
    "risk": "Risk Engine\n(risk)",
    "strategy": "Strategy Engine\n(strategy.engine)",
    "market_data": "Market Data\n(market_data)",
    "wolfden_ai": "Intent Engine\n(Ollama Router)",
    "events": "Event Bus Broker\n(events.broker)",
    "api_gateway": "FastAPI Gateway\n(app.main)",
    "core": "Live Graph State\n(/api/v1/graph/live)",
}


def load_graph():
    if not DEP_GRAPH.exists():
        raise FileNotFoundError(f"Missing dependency graph: {DEP_GRAPH}")
    return json.loads(DEP_GRAPH.read_text())


def main():
    dep = load_graph()

    nodes_by_file = {
        node["id"]: node
        for node in dep.get("nodes", [])
    }

    overlay_edges = []
    skipped_edges = []

    for edge in dep.get("edges", []):
        src_file = edge.get("from")
        dst_file = edge.get("to")

        src_node = nodes_by_file.get(src_file, {})
        dst_node = nodes_by_file.get(dst_file, {})

        src_stack = src_node.get("stack")
        dst_stack = dst_node.get("stack")

        src_topology = STACK_TO_TOPOLOGY.get(src_stack)
        dst_topology = STACK_TO_TOPOLOGY.get(dst_stack)

        if not src_topology or not dst_topology:
            skipped_edges.append({
                "from": src_file,
                "to": dst_file,
                "from_stack": src_stack,
                "to_stack": dst_stack,
                "reason": "missing_topology_mapping",
            })
            continue

        if src_topology == dst_topology:
            continue

        overlay_edges.append({
            "from_file": src_file,
            "to_file": dst_file,
            "from_stack": src_stack,
            "to_stack": dst_stack,
            "from_topology_node": src_topology,
            "to_topology_node": dst_topology,
            "import": edge.get("import"),
        })

    dedup = {}
    for edge in overlay_edges:
        key = (
            edge["from_topology_node"],
            edge["to_topology_node"],
            edge["from_stack"],
            edge["to_stack"],
        )
        dedup.setdefault(key, {
            "from_topology_node": edge["from_topology_node"],
            "to_topology_node": edge["to_topology_node"],
            "from_stack": edge["from_stack"],
            "to_stack": edge["to_stack"],
            "dependency_count": 0,
            "examples": [],
        })
        dedup[key]["dependency_count"] += 1
        if len(dedup[key]["examples"]) < 5:
            dedup[key]["examples"].append({
                "from_file": edge["from_file"],
                "to_file": edge["to_file"],
                "import": edge["import"],
            })

    report = {
        "phase": "7A_DEPENDENCY_TOPOLOGY_OVERLAY_EXPORT",
        "generated_at": datetime.now(UTC).isoformat(),
        "source_dependency_graph": str(DEP_GRAPH.relative_to(ROOT)),
        "raw_overlay_edge_count": len(overlay_edges),
        "topology_overlay_edge_count": len(dedup),
        "skipped_edge_count": len(skipped_edges),
        "topology_overlay_edges": list(dedup.values()),
        "skipped_edges": skipped_edges[:100],
    }

    OUT_JSON.write_text(json.dumps(report, indent=2))

    print(json.dumps({
        "phase": report["phase"],
        "raw_overlay_edge_count": report["raw_overlay_edge_count"],
        "topology_overlay_edge_count": report["topology_overlay_edge_count"],
        "skipped_edge_count": report["skipped_edge_count"],
        "output": str(OUT_JSON),
        "preview": report["topology_overlay_edges"][:10],
    }, indent=2))


if __name__ == "__main__":
    main()
