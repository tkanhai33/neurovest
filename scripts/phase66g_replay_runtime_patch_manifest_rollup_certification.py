#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

PHASE = "66G_REPLAY_RUNTIME_PATCH_MANIFEST_ROLLUP_CERTIFICATION"

SOURCE = ARCH / "patch_manifest_preview" / "66F_replay_runtime_source_patch_manifest_preview_latest.json"

OUT_DIR = ARCH / "patch_manifest_rollup"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "66G_replay_runtime_patch_manifest_rollup_latest.json"
OUT_TXT = OUT_DIR / "66G_replay_runtime_patch_manifest_rollup_latest.txt"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)
manifest = source.get("patch_manifest", [])

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "manifest_present": len(manifest) > 0,
    "all_writes_blocked": all(item.get("write_allowed_now") is False for item in manifest),
    "all_source_mutation_blocked": all(item.get("source_mutation_allowed_now") is False for item in manifest),
    "global_source_write_blocked": source.get("global_policy", {}).get("source_write_allowed_now") is False,
    "global_replay_blocked": source.get("global_policy", {}).get("historical_replay_allowed_now") is False,
    "global_runtime_execution_blocked": source.get("global_policy", {}).get("runtime_execution_allowed") is False,
    "global_strategy_db_write_blocked": source.get("global_policy", {}).get("strategy_db_write_allowed") is False,
    "global_broker_live_blocked": (
        source.get("global_policy", {}).get("broker_execution_enabled") is False
        and source.get("global_policy", {}).get("live_execution_enabled") is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_PATCH_MANIFEST_ROLLUP_CERTIFICATION",
    "source_manifest_preview": str(SOURCE),
    "patch_manifest_count": len(manifest),
    "rollup_summary": {
        "patch_manifest_preview_certified": source.get("certified") is True,
        "planned_files": len(manifest),
        "source_writes_allowed": False,
        "source_mutation_allowed": False,
        "historical_replay_allowed": False,
        "runtime_execution_allowed": False,
        "strategy_db_write_allowed": False,
        "broker_live_allowed": False,
    },
    "checks": checks,
    "recommended_next_phase": "67A_REPLAY_CONTRACT_SOURCE_CREATION",
    "certified": False,
}

result["certified"] = all(checks.values())

OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

lines = [
    PHASE,
    "",
    f"certified: {result['certified']}",
    f"patch_manifest_count: {len(manifest)}",
    "",
    "Rollup summary:",
    "",
]

for k, v in result["rollup_summary"].items():
    lines.append(f"{k}: {v}")

lines += ["", "Next:", result["recommended_next_phase"]]

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "patch_manifest_count": len(manifest),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
