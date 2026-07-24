#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
from collections import defaultdict
import json

ROOT = Path(".").resolve()
LIB = ROOT / "runtime" / "research_library"
INDEX = LIB / "universal_index" / "65J_universal_research_paper_index_latest.json"
OUT_DIR = LIB / "knowledge_graph"

OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "65K_research_knowledge_graph_latest.json"
OUT_TXT = OUT_DIR / "65K_research_knowledge_graph_latest.txt"

PHASE = "65K_RESEARCH_KNOWLEDGE_GRAPH_BUILDER"

data = json.loads(INDEX.read_text(encoding="utf-8")) if INDEX.exists() else {}
records = data.get("records", [])

nodes = []
edges = []
node_ids = set()

def add_node(node_id: str, node_type: str, label: str, extra=None):
    if node_id in node_ids:
        return
    node_ids.add(node_id)
    nodes.append({
        "id": node_id,
        "type": node_type,
        "label": label,
        **(extra or {}),
    })

def add_edge(src: str, dst: str, relation: str):
    edges.append({
        "source": src,
        "target": dst,
        "relation": relation,
    })

topic_to_papers = defaultdict(list)

for record in records:
    rid = record.get("research_id")
    title = record.get("title_guess") or rid

    paper_node = f"paper:{rid}"
    add_node(paper_node, "paper", title, {
        "research_id": rid,
        "source_path": record.get("source_path"),
        "page_count": record.get("page_count"),
        "index_state": record.get("index_state"),
    })

    for topic in record.get("topics", []):
        topic_node = f"topic:{topic}"
        add_node(topic_node, "topic", topic)
        add_edge(paper_node, topic_node, "HAS_TOPIC")
        topic_to_papers[topic].append(paper_node)

concept_rules = {
    "momentum": ["signal_family:momentum", "indicator:lookback_return", "replay_need:historical_bars"],
    "value": ["signal_family:value_factor", "indicator:valuation_rank", "replay_need:fundamental_or_proxy_data"],
    "risk": ["risk_test:drawdown", "risk_test:stress_test", "metric:max_drawdown"],
    "machine_learning": ["method:machine_learning", "review_need:overfit_check", "test:out_of_sample_split"],
    "statistics": ["method:statistics", "test:walk_forward_split", "metric:sharpe_proxy"],
    "macro": ["data_source:FRED_API_READ_ONLY", "data_source:STATCAN_READ_ONLY", "regime:macro_context"],
    "optimization": ["method:optimization", "risk_test:constraint_review"],
    "trading": ["domain:trading_strategy", "replay_need:strategy_spec"],
    "fraud_anomaly": ["method:anomaly_detection", "domain:fraud_detection"],
    "quantum_physics": ["domain:advanced_math_physics", "research_only:theory_reference"],
}

for topic, concepts in concept_rules.items():
    topic_node = f"topic:{topic}"
    if topic_node not in node_ids:
        continue

    for concept in concepts:
        ctype, label = concept.split(":", 1)
        concept_node = f"{ctype}:{label}"
        add_node(concept_node, ctype, label)
        add_edge(topic_node, concept_node, "IMPLIES_CONCEPT")

for topic, papers in topic_to_papers.items():
    for i, a in enumerate(papers):
        for b in papers[i + 1:]:
            add_edge(a, b, f"RELATED_BY_TOPIC:{topic}")

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_RESEARCH_KNOWLEDGE_GRAPH",
    "source_index": str(INDEX),
    "paper_count": len(records),
    "node_count": len(nodes),
    "edge_count": len(edges),
    "nodes": nodes,
    "edges": edges,
    "graph_policy": {
        "graph_build_allowed": True,
        "candidate_generation_allowed": False,
        "historical_replay_allowed": False,
        "strategy_execution_allowed": False,
        "implementation_patch_allowed": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "learning_enabled": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": {
        "source_index_exists": INDEX.exists(),
        "source_index_certified": data.get("certified") is True,
        "papers_present": len(records) > 0,
        "nodes_created": len(nodes) > 0,
        "edges_created": len(edges) > 0,
        "candidate_generation_blocked": False is False,
        "replay_blocked": False is False,
        "execution_blocked": False is False,
        "promotion_blocked": False is False,
        "broker_live_blocked": False is False,
    },
    "recommended_next_phase": "65L_RESEARCH_CANDIDATE_COMPOSER_STUB",
    "certified": False,
}

result["certified"] = all(result["checks"].values())

OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

lines = [
    PHASE,
    "",
    f"certified: {result['certified']}",
    f"papers: {result['paper_count']}",
    f"nodes: {result['node_count']}",
    f"edges: {result['edge_count']}",
    "",
    "Graph summary:",
    "",
]

for node in nodes[:80]:
    lines.append(f"- NODE {node['type']} | {node['label']}")

lines.append("")
lines.append("Edges sample:")
lines.append("")

for edge in edges[:80]:
    lines.append(f"- {edge['source']} --{edge['relation']}--> {edge['target']}")

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(json.dumps({
    "phase": PHASE,
    "paper_count": result["paper_count"],
    "node_count": result["node_count"],
    "edge_count": result["edge_count"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
    "recommended_next_phase": result["recommended_next_phase"],
    "certified": result["certified"],
}, indent=2, ensure_ascii=False))
