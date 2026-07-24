#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()

DRIFT = ROOT / "runtime/repo_memory/runtime_static_diff_classification_v1.json"
DIFF = ROOT / "runtime/repo_memory/runtime_static_dependency_diff_v1.json"
LAYER = ROOT / "runtime/repo_memory/canonical_layer_graph_v1.json"
HOTSPOTS = ROOT / "runtime/repo_memory/component_overlay_v1.json"
SERVICE_CHAIN = ROOT / "runtime/repo_memory/service_chain_graph_v1.json"
PORTFOLIO_SERVICE_CHAIN = ROOT / "runtime/repo_memory/portfolio_service_chain_graph_v1.json"
STRATEGY_SERVICE_CHAIN = ROOT / "runtime/repo_memory/strategy_service_chain_graph_v1.json"
RISK_SERVICE_CHAIN = ROOT / "runtime/repo_memory/risk_service_chain_graph_v1.json"

OUT_JSON = ROOT / "runtime/repo_memory/architecture_drift_dashboard_v1.json"
OUT_TXT = ROOT / "runtime/repo_memory/architecture_drift_dashboard_v1.txt"

drift = json.loads(DRIFT.read_text()) if DRIFT.exists() else {}
diff = json.loads(DIFF.read_text()) if DIFF.exists() else {}
layer = json.loads(LAYER.read_text()) if LAYER.exists() else {}
hotspots = json.loads(HOTSPOTS.read_text()) if HOTSPOTS.exists() else {}
service_chain = json.loads(SERVICE_CHAIN.read_text()) if SERVICE_CHAIN.exists() else {}
portfolio_service_chain = json.loads(PORTFOLIO_SERVICE_CHAIN.read_text()) if PORTFOLIO_SERVICE_CHAIN.exists() else {}
strategy_service_chain = json.loads(STRATEGY_SERVICE_CHAIN.read_text()) if STRATEGY_SERVICE_CHAIN.exists() else {}
risk_service_chain = json.loads(RISK_SERVICE_CHAIN.read_text()) if RISK_SERVICE_CHAIN.exists() else {}

components = hotspots.get("components", {})

top_components = []

for name, meta in components.items():
    total = int(meta.get("in_degree", 0)) + int(meta.get("out_degree", 0))
    if total <= 0:
        continue

    top_components.append({
        "component": name,
        "stack": meta.get("stack"),
        "canonical_layer": meta.get("canonical_layer"),
        "total_degree": total,
        "in_degree": int(meta.get("in_degree", 0)),
        "out_degree": int(meta.get("out_degree", 0)),
    })

top_components.sort(
    key=lambda x: (
        x["total_degree"],
        x["out_degree"],
        x["in_degree"],
    ),
    reverse=True,
)

layer_counts = {
    layer_name: len(files)
    for layer_name, files in layer.get("layers", {}).items()
}

dashboard = {
    "phase": "10G_ARCHITECTURE_DRIFT_DASHBOARD_SUMMARY",
    "generated_at": datetime.now(UTC).isoformat(),
    "architecture_health": {
        "status": "PASS" if drift.get("drift_count", 0) == 0 else "FAIL",
        "drift_count": drift.get("drift_count", 0),
        "runtime_only_count": diff.get("runtime_only_edge_count", 0),
        "static_only_count": diff.get("static_only_edge_count", 0),
        "shared_count": diff.get("shared_edge_count", 0),
    },
    "layer_counts": layer_counts,
    "top_components": top_components[:10],
    "runtime_only_edges": drift.get("classified_runtime_only", []),
    "static_only_edges": drift.get("classified_static_only", []),
    "drift_edges": drift.get("drift_edges", []),
    "service_chain": {
        "node_count": service_chain.get("node_count", 0),
        "edge_count": service_chain.get("edge_count", 0),
        "nodes": service_chain.get("nodes", []),
        "edges": service_chain.get("edges", []),
    },
    "portfolio_service_chain": {
        "node_count": portfolio_service_chain.get("node_count", 0),
        "edge_count": portfolio_service_chain.get("edge_count", 0),
        "nodes": portfolio_service_chain.get("nodes", []),
        "edges": portfolio_service_chain.get("edges", []),
    },
    "strategy_service_chain": {
        "node_count": strategy_service_chain.get("node_count", 0),
        "edge_count": strategy_service_chain.get("edge_count", 0),
        "nodes": strategy_service_chain.get("nodes", []),
        "edges": strategy_service_chain.get("edges", []),
    },
    "risk_service_chain": {
        "node_count": risk_service_chain.get("node_count", 0),
        "edge_count": risk_service_chain.get("edge_count", 0),
        "nodes": risk_service_chain.get("nodes", []),
        "edges": risk_service_chain.get("edges", []),
    },
}

OUT_JSON.write_text(json.dumps(dashboard, indent=2))

lines = []
lines.append("=" * 70)
lines.append("NEUROVEST ARCHITECTURE DRIFT DASHBOARD")
lines.append("=" * 70)
lines.append("")
lines.append(f"Status               : {dashboard['architecture_health']['status']}")
lines.append(f"Drift Count          : {dashboard['architecture_health']['drift_count']}")
lines.append(f"Runtime Only Edges   : {dashboard['architecture_health']['runtime_only_count']}")
lines.append(f"Static Only Edges    : {dashboard['architecture_health']['static_only_count']}")
lines.append(f"Shared Edges         : {dashboard['architecture_health']['shared_count']}")
lines.append("")
lines.append("CANONICAL LAYER COUNTS")
lines.append("-" * 70)

for name, count in sorted(layer_counts.items()):
    lines.append(f"{name:<35} {count:>5}")

lines.append("")
lines.append("TOP COMPONENT HOTSPOTS")
lines.append("-" * 70)

for c in top_components[:10]:
    lines.append(
        f"{c['component']:<30} "
        f"{c['stack']:<20} "
        f"deg={c['total_degree']:<3} "
        f"{c['canonical_layer']}"
    )

lines.append("")
lines.append("SERVICE CHAIN GRAPH")
lines.append("-" * 70)
lines.append(f"Nodes                : {dashboard['service_chain']['node_count']}")
lines.append(f"Edges                : {dashboard['service_chain']['edge_count']}")

for edge in dashboard["service_chain"]["edges"]:
    lines.append(f"{edge['from']} -> {edge['to']} :: {edge['type']}")

lines.append("")
lines.append("PORTFOLIO SERVICE CHAIN GRAPH")
lines.append("-" * 70)
lines.append(f"Nodes                : {dashboard['portfolio_service_chain']['node_count']}")
lines.append(f"Edges                : {dashboard['portfolio_service_chain']['edge_count']}")

for edge in dashboard["portfolio_service_chain"]["edges"]:
    lines.append(f"{edge['from']} -> {edge['to']} :: {edge['type']}")

lines.append("")
lines.append("STRATEGY SERVICE CHAIN GRAPH")
lines.append("-" * 70)
lines.append(f"Nodes                : {dashboard['strategy_service_chain']['node_count']}")
lines.append(f"Edges                : {dashboard['strategy_service_chain']['edge_count']}")

for edge in dashboard["strategy_service_chain"]["edges"]:
    lines.append(f"{edge['from']} -> {edge['to']} :: {edge['type']}")

lines.append("")
lines.append("RISK SERVICE CHAIN GRAPH")
lines.append("-" * 70)
lines.append(f"Nodes                : {dashboard['risk_service_chain']['node_count']}")
lines.append(f"Edges                : {dashboard['risk_service_chain']['edge_count']}")

for edge in dashboard["risk_service_chain"]["edges"]:
    lines.append(f"{edge['from']} -> {edge['to']} :: {edge['type']}")

lines.append("")
lines.append("ARCHITECTURE DRIFT")
lines.append("-" * 70)

if dashboard["drift_edges"]:
    for edge in dashboard["drift_edges"]:
        lines.append(
            f"{edge['from']} -> {edge['to']} :: {edge['classification']}"
        )
else:
    lines.append("No architecture drift detected.")

OUT_TXT.write_text("\n".join(lines))

print(json.dumps({
    "phase": dashboard["phase"],
    "status": dashboard["architecture_health"]["status"],
    "drift_count": dashboard["architecture_health"]["drift_count"],
    "top_component": top_components[0] if top_components else {},
    "output_json": str(OUT_JSON),
    "output_txt": str(OUT_TXT),
}, indent=2))
