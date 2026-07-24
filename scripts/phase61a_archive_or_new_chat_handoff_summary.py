#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, UTC

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"

OUT = SANDBOX / "61A_archive_or_new_chat_handoff_summary_latest.json"

PHASE = "61A_ARCHIVE_OR_NEW_CHAT_HANDOFF_SUMMARY"

SOURCE = SANDBOX / "60C_handoff_bundle_refresh_latest.json"

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "source": str(SOURCE),
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    handoff = (
        json.loads(SOURCE.read_text(encoding="utf-8"))
        if SOURCE.exists()
        else {}
    )

    snapshot = (
        handoff.get("handoff_snapshot", {})
        if isinstance(handoff.get("handoff_snapshot"), dict)
        else {}
    )

    archive = {
        "status": "archive_ready",
        "archive_mode": "terminal_read_only_archive",

        "latest_certified_phase":
            snapshot.get("latest_confirmed_phase"),

        "terminal_stage":
            snapshot.get("stage"),

        "read_only_chain_closed":
            snapshot.get("terminal_state", {}).get(
                "read_only_chain_closed",
                True,
            ),

        "execution_surface_opened":
            snapshot.get("terminal_state", {}).get(
                "execution_surface_opened",
                False,
            ),

        "mutation_surface_opened":
            snapshot.get("terminal_state", {}).get(
                "mutation_surface_opened",
                False,
            ),

        "critical_safety_locks":
            snapshot.get(
                "critical_safety_locks",
                {},
            ),

        "archive_actions": [
            "retain certified artifacts",
            "retain certification chain",
            "retain safety locks",
            "retain read-only capability summaries",
            "handoff to future chat if required",
        ],

        "forbidden_after_archive": [
            "continue certification chain",
            "open runtime",
            "mutate source",
            "execute runtime",
            "broker execution",
            "live trading",
        ],

        "recommended_next_action":
            "START_NEW_CHAT_FROM_ARCHIVED_HANDOFF",
    }

    result["archive_summary"] = archive

    result["checks"]["source_exists"] = SOURCE.exists()
    result["checks"]["source_certified"] = handoff.get("certified") is True
    result["checks"]["archive_ready"] = archive["status"] == "archive_ready"
    result["checks"]["chain_closed"] = archive["read_only_chain_closed"] is True
    result["checks"]["execution_closed"] = archive["execution_surface_opened"] is False
    result["checks"]["mutation_closed"] = archive["mutation_surface_opened"] is False
    result["checks"]["locks_false"] = all(
        v is False
        for v in archive["critical_safety_locks"].values()
    )
    result["checks"]["archive_actions_present"] = len(
        archive["archive_actions"]
    ) > 0
    result["checks"]["forbidden_present"] = len(
        archive["forbidden_after_archive"]
    ) > 0

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

OUT.write_text(
    json.dumps(result, indent=2),
    encoding="utf-8",
)

print(json.dumps(result, indent=2))
print(f"\nWROTE: {OUT}")
