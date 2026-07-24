#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "human_review_approval_package" / "105A_human_review_approval_package_latest.json"

OUT_DIR = ARCH / "dev_territory_command_registry_preview"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "106A_dev_territory_command_registry_preview_latest.json"
OUT_TXT = OUT_DIR / "106A_dev_territory_command_registry_preview_latest.txt"

PHASE = "106A_DEV_TERRITORY_COMMAND_REGISTRY_PREVIEW"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

commands = [
    {
        "level": 1,
        "name": "SCOUT",
        "command": "Neuro, expand your territory. Scout the approved landscape.",
        "purpose": "Read-only exploration of certified data.",
        "allowed": ["read certified historical data", "read approved research", "produce observations"],
        "forbidden": ["strategy DB writes", "mutation", "promotion", "broker execution", "live execution"],
    },
    {
        "level": 2,
        "name": "HUNTING_PARTY",
        "command": "Neuro, send out a hunting party. Bring back five promising opportunities.",
        "purpose": "Generate sandbox candidate ideas only.",
        "allowed": ["generate candidate ideas", "score hypotheses", "write sandbox-only artifacts"],
        "forbidden": ["strategy DB writes", "promotion", "broker execution", "live execution"],
    },
    {
        "level": 3,
        "name": "EXPLORE_NEW_LANDS",
        "command": "Neuro, explore beyond our territory. Find new hunting grounds.",
        "purpose": "Massive sandbox exploration after approval.",
        "allowed": ["large-scale exploration", "compare territories", "request expansion"],
        "forbidden": ["unapproved expansion", "strategy DB writes", "broker execution", "live execution"],
    },
    {
        "level": 4,
        "name": "ALPHA_TRIALS",
        "command": "Neuro, begin the Alpha Trials. Only the strongest survive.",
        "purpose": "Rank sandbox candidates through replay/stress scoring.",
        "allowed": ["rank candidates", "eliminate weak sandbox ideas", "produce survivor report"],
        "forbidden": ["delete production strategies", "promote candidates", "broker execution"],
    },
    {
        "level": 5,
        "name": "WOLF_MASTER_REPORT",
        "command": "Neuro, return to the den. Report to your Wolf Master.",
        "purpose": "Full human review report.",
        "allowed": ["summarize training", "summarize candidates", "recommend next action"],
        "forbidden": ["approval without human", "DB writes", "promotion", "broker execution"],
    },
    {
        "level": 6,
        "name": "EXPAND_THE_PACK",
        "command": "Neuro, expand the Pack. Move only approved survivors into Candidate Review.",
        "purpose": "Preview candidate review movement only.",
        "allowed": ["prepare candidate review package"],
        "forbidden": ["strategy DB writes", "broker execution", "live execution"],
    },
    {
        "level": 7,
        "name": "DEFEND_TERRITORY",
        "command": "Neuro, defend the Territory. Protect the pack using only certified knowledge.",
        "purpose": "Future production-only certified strategy mode.",
        "allowed": ["use certified knowledge only"],
        "forbidden": ["exploration", "experimentation", "mutation", "uncertified strategy use"],
    },
]

doctrine = {
    "territory_maturity_rule": "Strengthen weakest known territory before requesting new expansion.",
    "expansion_request_phrase": "Wolf Master, we have expanded as much as we can in our current territory. Could we add more prey to search for?",
    "global_rule": "Territory commands grant analytical capability only. They never grant persistence, mutation, promotion, broker execution, or live trading.",
    "confidence_bands": {
        "95_100": "Alpha Territory",
        "90_94": "Stable Territory",
        "80_89": "Developing Territory",
        "70_79": "Weak Territory",
        "below_70": "Unstable Territory",
    },
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "commands_present": len(commands) == 7,
    "doctrine_present": bool(doctrine),
    "global_rule_blocks_persistence": "never grant persistence" in doctrine["global_rule"],
    "approval_still_not_granted": source.get("review_package", {}).get("approval_granted") is False,
    "strategy_db_write_blocked": True,
    "promotion_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "DEV_TERRITORY_COMMAND_REGISTRY_PREVIEW_ONLY",
    "source_human_review": str(SOURCE),
    "commands": commands,
    "doctrine": doctrine,
    "checks": checks,
    "policy": {
        "dev_territory_registry_preview_certified": True,
        "registry_write_to_runtime_enabled": False,
        "training_execution_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "106B_DEV_TERRITORY_COMMAND_REGISTRY_STUB",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"commands: {len(commands)}",
        "mode: preview only",
        "",
        "Territory commands registered as design preview.",
        "No DB. No mutation. No promotion. No broker/live.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "commands": len(commands),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
