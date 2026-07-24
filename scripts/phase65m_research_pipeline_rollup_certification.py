#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()

LIB = ROOT / "runtime" / "research_library"

PHASE = "65M_RESEARCH_PIPELINE_ROLLUP_CERTIFICATION"

EXPECTED = {
    "65A_dataset_registry":
        ROOT / "runtime/research_datasets/statcan_10100125/65A_research_dataset_intake_registry_latest.json",

    "65B_strategy_source":
        LIB / "strategy_sources/151_trading_strategies/65B_strategy_source_intake_registry_latest.json",

    "65C_strategy_index":
        LIB / "strategy_sources/151_trading_strategies/index/65C_strategy_source_index_latest.json",

    "65D_candidate_registry":
        LIB / "strategy_sources/151_trading_strategies/candidates/65D_research_candidate_registry_latest.json",

    "65E_replay_matching":
        LIB / "strategy_sources/151_trading_strategies/replay_plans/65E_historical_replay_matching_plan_latest.json",

    "65F_formula_requirements":
        LIB / "strategy_sources/151_trading_strategies/formula_signal_requirements/65F_formula_and_signal_requirement_extractor_latest.json",

    "65G_replay_specs":
        LIB / "strategy_sources/151_trading_strategies/replay_specs/65G_replay_spec_draft_builder_latest.json",

    "65H_multi_source_discovery":
        LIB / "strategy_sources/65H_ssrn_downloads_multi_source_discovery_latest.json",

    "65I_master_registry":
        LIB / "master_registry/65I_research_master_registry_latest.json",

    "65J_universal_index":
        LIB / "universal_index/65J_universal_research_paper_index_latest.json",

    "65K_knowledge_graph":
        LIB / "knowledge_graph/65K_research_knowledge_graph_latest.json",

    "65L_candidate_composer":
        LIB / "composed_candidates/65L_research_candidate_composer_stub_latest.json",
}

OUT_DIR = LIB / "pipeline_rollup"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "65M_research_pipeline_rollup_latest.json"
OUT_TXT = OUT_DIR / "65M_research_pipeline_rollup_latest.txt"


def read(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


artifacts = {}
checks = {}

for name, path in EXPECTED.items():
    data = read(path)

    artifacts[name] = {
        "path": str(path),
        "exists": path.exists(),
        "certified": bool(data and data.get("certified") is True),
        "phase": data.get("phase") if data else None,
    }

    checks[f"{name}_exists"] = path.exists()
    checks[f"{name}_certified"] = bool(data and data.get("certified") is True)


pipeline_summary = {
    "dataset_intake_complete": artifacts["65A_dataset_registry"]["certified"],
    "research_sources_registered": artifacts["65B_strategy_source"]["certified"],
    "strategy_index_complete": artifacts["65C_strategy_index"]["certified"],
    "candidate_registry_complete": artifacts["65D_candidate_registry"]["certified"],
    "replay_plan_complete": artifacts["65E_replay_matching"]["certified"],
    "formula_mapping_complete": artifacts["65F_formula_requirements"]["certified"],
    "replay_spec_complete": artifacts["65G_replay_specs"]["certified"],
    "multi_source_discovery_complete": artifacts["65H_multi_source_discovery"]["certified"],
    "master_registry_complete": artifacts["65I_master_registry"]["certified"],
    "universal_index_complete": artifacts["65J_universal_index"]["certified"],
    "knowledge_graph_complete": artifacts["65K_knowledge_graph"]["certified"],
    "candidate_composer_complete": artifacts["65L_candidate_composer"]["certified"],
}

policy = {
    "research_pipeline_complete": True,

    "candidate_generation_allowed": False,
    "historical_replay_allowed": False,
    "strategy_execution_allowed": False,
    "implementation_allowed": False,
    "runtime_execution_allowed": False,
    "runtime_mutation_allowed": False,
    "learning_enabled": False,
    "promotion_enabled": False,
    "broker_execution_enabled": False,
    "live_execution_enabled": False,

    "next_safe_phase":
        "66A_REPLAY_RUNTIME_ARCHITECTURE_PLANNING",
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_RESEARCH_PIPELINE_ROLLUP",
    "artifacts": artifacts,
    "pipeline_summary": pipeline_summary,
    "policy": policy,
    "checks": checks,
    "recommended_next_phase": policy["next_safe_phase"],
    "certified": all(checks.values()),
}

OUT_JSON.write_text(
    json.dumps(result, indent=2, ensure_ascii=False),
    encoding="utf-8",
)

lines = [
    PHASE,
    "",
    f"certified: {result['certified']}",
    "",
    "Research Pipeline",
    "-----------------",
]

for k, v in pipeline_summary.items():
    lines.append(f"{k}: {v}")

lines += [
    "",
    "Safety",
    "------",
]

for k, v in policy.items():
    lines.append(f"{k}: {v}")

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(json.dumps({
    "phase": PHASE,
    "pipeline_complete": all(pipeline_summary.values()),
    "certified": result["certified"],
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
