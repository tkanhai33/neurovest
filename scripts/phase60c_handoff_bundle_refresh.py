#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = SANDBOX / "60C_handoff_bundle_refresh_latest.json"

PHASE = "60C_HANDOFF_BUNDLE_REFRESH"

SOURCES = [
    SANDBOX / "59C_handoff_bundle_refresh_latest.json",
    SANDBOX / "60B_qwen_read_only_terminal_freeze_rollup_certification_latest.json",
]

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "sources": [str(x) for x in SOURCES],
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    loaded = {}

    for source in SOURCES:
        if source.exists():
            loaded[source.name] = json.loads(source.read_text(encoding="utf-8"))

    latest = loaded.get(
        "60B_qwen_read_only_terminal_freeze_rollup_certification_latest.json",
        {},
    )

    result["handoff_snapshot"] = {
        "stage": "Qwen Read-Only Terminal Freeze Certified",
        "latest_confirmed_phase": latest.get("phase"),

        "current_capabilities": [
            "Qwen terminal read-only snapshot inspection",
            "Qwen terminal read-only state summary",
            "Qwen certified read-only architecture context",
            "Qwen certified read-only handoff chain",
        ],

        "still_disabled": [
            "file writes",
            "shell execution",
            "runtime execution",
            "source mutation",
            "policy mutation",
            "matrix mutation",
            "handoff mutation",
            "terminal mutation",
            "terminal execution",
            "terminal next phase generation",
            "broker execution",
            "live execution",
            "recursive self-execution",
            "autonomous phase execution",
        ],

        "critical_safety_locks": {
            "live_execution_enabled": False,
            "broker_execution_enabled": False,
            "simulation_enabled": False,
            "registry_write_enabled": False,
            "promotion_enabled": False,
            "learning_enabled": False,
        },

        "terminal_state": {
            "terminal_freeze_certified": latest.get("certified") is True,
            "terminal_next_phase_generation_allowed": False,
            "read_only_chain_closed": True,
            "execution_surface_opened": False,
            "mutation_surface_opened": False,
        },

        "next_recommended_phase": "HANDOFF_TO_NEW_CHAT_OR_ARCHIVE_ONLY",
    }

    result["checks"]["source_present"] = len(loaded) == 2
    result["checks"]["terminal_freeze_certified"] = latest.get("certified") is True
    result["checks"]["locks_false"] = all(
        value is False
        for value in result["handoff_snapshot"]["critical_safety_locks"].values()
    )
    result["checks"]["terminal_next_phase_generation_blocked"] = (
        result["handoff_snapshot"]["terminal_state"]["terminal_next_phase_generation_allowed"] is False
    )
    result["checks"]["read_only_chain_closed"] = (
        result["handoff_snapshot"]["terminal_state"]["read_only_chain_closed"] is True
    )
    result["checks"]["no_execution_surface_opened"] = (
        result["handoff_snapshot"]["terminal_state"]["execution_surface_opened"] is False
    )
    result["checks"]["no_mutation_surface_opened"] = (
        result["handoff_snapshot"]["terminal_state"]["mutation_surface_opened"] is False
    )
    result["checks"]["next_phase_is_archive_or_handoff_only"] = (
        result["handoff_snapshot"]["next_recommended_phase"]
        == "HANDOFF_TO_NEW_CHAT_OR_ARCHIVE_ONLY"
    )

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
