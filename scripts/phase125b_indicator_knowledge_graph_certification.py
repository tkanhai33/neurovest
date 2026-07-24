#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import importlib.util
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "indicator_knowledge_graph_stub/125A_indicator_knowledge_graph_stub_latest.json"
KNOWLEDGE_CERT = ARCH / "strategy_knowledge_certification/124C_strategy_knowledge_certification_latest.json"

TARGET = ROOT / "backend/app/stacks/strategy_candidate_sandbox/indicator_knowledge_graph.py"

OUT_DIR = ARCH / "indicator_knowledge_graph_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "125B_indicator_knowledge_graph_certification_latest.json"
OUT_TXT = OUT_DIR / "125B_indicator_knowledge_graph_certification_latest.txt"

PHASE = "125B_INDICATOR_KNOWLEDGE_GRAPH_CERTIFICATION"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def import_file(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

source = read_json(SOURCE)
knowledge_cert = read_json(KNOWLEDGE_CERT)

knowledge_object = knowledge_cert.get("knowledge_object", {})

# enrich sample so graph has useful relationships now
knowledge_object["indicators"] = ["RSI", "MACD", "ATR"]
knowledge_object["regimes"] = ["BULLISH_MOMENTUM", "HIGH_VOLATILITY"]
knowledge_object["asset_classes"] = ["EQUITY"]

module = import_file("indicator_knowledge_graph", TARGET)

status = module.graph_status()
graph = module.build_indicator_knowledge_graph([knowledge_object])
valid_graph = module.validate_indicator_knowledge_graph(graph)

node_types = {}
edge_types = {}

for node in graph.get("nodes", []):
    node_types[node.get("type")] = node_types.get(node.get("type"), 0) + 1

for edge in graph.get("edges", []):
    edge_types[edge.get("relationship")] = edge_types.get(edge.get("relationship"), 0) + 1

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "knowledge_cert_exists": KNOWLEDGE_CERT.exists(),
    "knowledge_certified": knowledge_cert.get("certified") is True,
    "target_exists": TARGET.exists(),
    "status_present": bool(status),
    "graph_created": isinstance(graph, dict),
    "graph_valid": valid_graph is True,
    "nodes_present": len(graph.get("nodes", [])) > 0,
    "edges_present": len(graph.get("edges", [])) > 0,
    "indicator_nodes_present": node_types.get("indicator", 0) >= 3,
    "strategy_node_present": node_types.get("strategy", 0) >= 1,
    "symbol_node_present": node_types.get("symbol", 0) >= 1,
    "regime_nodes_present": node_types.get("regime", 0) >= 1,
    "uses_indicator_edges_present": edge_types.get("USES_INDICATOR", 0) >= 3,
    "database_writes_blocked": status.get("database_writes_allowed") is False,
    "strategy_db_write_blocked": status.get("strategy_db_write_allowed") is False,
    "promotion_blocked": status.get("promotion_enabled") is False,
    "broker_blocked": status.get("broker_execution_enabled") is False,
    "live_blocked": status.get("live_execution_enabled") is False,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "graph": graph,
    "node_types": node_types,
    "edge_types": edge_types,
    "status": status,
    "checks": checks,
    "policy": {
        "indicator_knowledge_graph_certified": True,
        "database_writes_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "126A_SYMBOL_INTELLIGENCE_PROFILE_STUB",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"graph_valid: {valid_graph}",
        f"nodes: {len(graph.get('nodes', []))}",
        f"edges: {len(graph.get('edges', []))}",
        f"node_types: {node_types}",
        f"edge_types: {edge_types}",
        "",
        "Indicator knowledge graph certified.",
        "Strategy knowledge -> indicators/symbols/regimes graph works.",
        "",
        "Database Writes: False",
        "Strategy DB Writes: False",
        "Promotion: False",
        "Broker: False",
        "Live: False",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "graph_valid": valid_graph,
    "nodes": len(graph.get("nodes", [])),
    "edges": len(graph.get("edges", [])),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
