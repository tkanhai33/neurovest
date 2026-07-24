#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
from collections import defaultdict
import json

ROOT = Path(".").resolve()
LIB = ROOT / "runtime" / "research_library"

GRAPH = LIB / "knowledge_graph" / "65K_research_knowledge_graph_latest.json"
OUT_DIR = LIB / "composed_candidates"

OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "65L_research_candidate_composer_stub_latest.json"
OUT_TXT = OUT_DIR / "65L_research_candidate_composer_stub_latest.txt"

PHASE = "65L_RESEARCH_CANDIDATE_COMPOSER_STUB"

graph = json.loads(GRAPH.read_text(encoding="utf-8")) if GRAPH.exists() else {}
nodes = graph.get("nodes", [])
edges = graph.get("edges", [])

topic_nodes = [n for n in nodes if n.get("type") == "topic"]
paper_nodes = [n for n in nodes if n.get("type") == "paper"]

topic_to_concepts = defaultdict(list)
paper_to_topics = defaultdict(list)

for edge in edges:
    src = edge.get("source")
    dst = edge.get("target")
    rel = edge.get("relation")

    if rel == "IMPLIES_CONCEPT":
        topic_to_concepts[src].append(dst)

    if rel == "HAS_TOPIC":
        paper_to_topics[src].append(dst)

ideas = []

templates = [
    {
        "idea_family": "momentum_macro_risk_filter",
        "required_topics": ["topic:momentum", "topic:macro", "topic:risk"],
        "candidate_title": "Momentum strategy with macro and drawdown filter",
        "hypothesis": "Momentum signals may improve when filtered by macro regime context and constrained by drawdown stress rules.",
    },
    {
        "idea_family": "value_risk_overlay",
        "required_topics": ["topic:value", "topic:risk"],
        "candidate_title": "Value-factor strategy with risk overlay",
        "hypothesis": "Value-factor candidates may improve when paired with drawdown and stress-test filters.",
    },
    {
        "idea_family": "ml_signal_validation",
        "required_topics": ["topic:machine_learning", "topic:trading", "topic:risk"],
        "candidate_title": "Machine-learning signal candidate with overfit control",
        "hypothesis": "Machine-learning trading signals require out-of-sample and overfit controls before replay eligibility.",
    },
    {
        "idea_family": "optimization_portfolio_filter",
        "required_topics": ["topic:optimization", "topic:risk", "topic:trading"],
        "candidate_title": "Optimization-based portfolio candidate with constraint review",
        "hypothesis": "Optimization can propose portfolio weights, but constraints and stress tests must control overfitting and concentration.",
    },
]

available_topics = {n["id"] for n in topic_nodes}

for idx, template in enumerate(templates, start=1):
    present = [t for t in template["required_topics"] if t in available_topics]
    missing = [t for t in template["required_topics"] if t not in available_topics]

    related_papers = []
    for paper, topics in paper_to_topics.items():
        if any(t in topics for t in present):
            related_papers.append(paper)

    idea = {
        "idea_id": f"COMPOSED_RESEARCH_IDEA_{idx:03d}",
        "status": "IDEA_STUB_ONLY",
        "idea_family": template["idea_family"],
        "candidate_title": template["candidate_title"],
        "hypothesis": template["hypothesis"],
        "required_topics": template["required_topics"],
        "topics_present": present,
        "topics_missing": missing,
        "related_papers": sorted(set(related_papers)),
        "related_concepts": sorted(set(
            concept
            for topic in present
            for concept in topic_to_concepts.get(topic, [])
        )),
        "readiness": (
            "COMPOSABLE_RESEARCH_IDEA"
            if not missing
            else "PARTIAL_RESEARCH_IDEA_MISSING_TOPICS"
        ),
        "next_required_work": [
            "human_review",
            "formal_candidate_specification",
            "formula_extraction",
            "data_requirement_confirmation",
            "replay_spec_review",
        ],
        "safety": {
            "idea_stub_only": True,
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
    }

    ideas.append(idea)

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_RESEARCH_CANDIDATE_COMPOSER_STUB",
    "source_graph": str(GRAPH),
    "paper_count": len(paper_nodes),
    "topic_count": len(topic_nodes),
    "idea_count": len(ideas),
    "ideas": ideas,
    "global_policy": {
        "idea_composition_allowed": True,
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
        "source_graph_exists": GRAPH.exists(),
        "source_graph_certified": graph.get("certified") is True,
        "papers_present": len(paper_nodes) > 0,
        "topics_present": len(topic_nodes) > 0,
        "ideas_created": len(ideas) > 0,
        "all_ideas_stub_only": all(i["safety"]["idea_stub_only"] is True for i in ideas),
        "candidate_generation_blocked": all(i["safety"]["candidate_generation_allowed"] is False for i in ideas),
        "replay_blocked": all(i["safety"]["historical_replay_allowed"] is False for i in ideas),
        "execution_blocked": all(i["safety"]["strategy_execution_allowed"] is False for i in ideas),
        "promotion_blocked": all(i["safety"]["promotion_enabled"] is False for i in ideas),
        "broker_live_blocked": all(
            i["safety"]["broker_execution_enabled"] is False
            and i["safety"]["live_execution_enabled"] is False
            for i in ideas
        ),
    },
    "recommended_next_phase": "65M_RESEARCH_PIPELINE_ROLLUP_CERTIFICATION",
    "certified": False,
}

result["certified"] = all(result["checks"].values())

OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

lines = [
    PHASE,
    "",
    f"certified: {result['certified']}",
    f"paper_count: {result['paper_count']}",
    f"topic_count: {result['topic_count']}",
    f"idea_count: {result['idea_count']}",
    "",
    "Composed idea stubs:",
    "",
]

for idea in ideas:
    lines.append(f"- {idea['idea_id']} | {idea['candidate_title']} | {idea['readiness']}")

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(json.dumps({
    "phase": PHASE,
    "paper_count": result["paper_count"],
    "topic_count": result["topic_count"],
    "idea_count": result["idea_count"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
    "recommended_next_phase": result["recommended_next_phase"],
    "certified": result["certified"],
}, indent=2, ensure_ascii=False))
