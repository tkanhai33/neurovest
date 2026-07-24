#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "rollup" / "66E_replay_runtime_rollup_certification_latest.json"
DRYRUN = ARCH / "dry_run_manifest" / "66D_replay_runtime_dry_run_manifest_latest.json"

OUT_DIR = ARCH / "patch_manifest_preview"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "66F_replay_runtime_source_patch_manifest_preview_latest.json"
OUT_TXT = OUT_DIR / "66F_replay_runtime_source_patch_manifest_preview_latest.txt"

PHASE = "66F_REPLAY_RUNTIME_SOURCE_PATCH_MANIFEST_PREVIEW"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


rollup = read_json(SOURCE)
dryrun = read_json(DRYRUN)

planned_files = dryrun.get("dry_run_manifest", {}).get("planned_files", [])

patch_manifest = []

for item in planned_files:
    target = ROOT / item["path"]

    patch_manifest.append({
        "target_path": item["path"],
        "exists_now": target.exists(),
        "parent_exists_now": target.parent.exists(),
        "planned_action": "CREATE_STUB_FUTURE" if not target.exists() else "REVIEW_EXISTING_FUTURE",
        "purpose": item.get("purpose"),
        "write_allowed_now": False,
        "source_mutation_allowed_now": False,
    })

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_SOURCE_PATCH_MANIFEST_PREVIEW",
    "source_rollup": str(SOURCE),
    "source_dryrun_manifest": str(DRYRUN),
    "patch_manifest_count": len(patch_manifest),
    "patch_manifest": patch_manifest,
    "global_policy": {
        "patch_manifest_preview_allowed": True,
        "source_write_allowed_now": False,
        "source_mutation_allowed_now": False,
        "historical_replay_allowed_now": False,
        "strategy_execution_allowed": False,
        "runtime_execution_allowed": False,
        "runtime_mutation_allowed": False,
        "strategy_db_write_allowed": False,
        "learning_enabled": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "checks": {
        "source_rollup_exists": SOURCE.exists(),
        "source_rollup_certified": rollup.get("certified") is True,
        "dryrun_manifest_exists": DRYRUN.exists(),
        "dryrun_manifest_certified": dryrun.get("certified") is True,
        "patch_manifest_present": len(patch_manifest) > 0,
        "all_writes_blocked_now": all(p["write_allowed_now"] is False for p in patch_manifest),
        "all_source_mutation_blocked_now": all(p["source_mutation_allowed_now"] is False for p in patch_manifest),
        "historical_replay_blocked": False is False,
        "runtime_execution_blocked": False is False,
        "strategy_db_write_blocked": False is False,
        "broker_live_blocked": False is False,
    },
    "recommended_next_phase": "66G_REPLAY_RUNTIME_PATCH_MANIFEST_ROLLUP_CERTIFICATION",
    "certified": False,
}

result["certified"] = all(result["checks"].values())

OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

lines = [
    PHASE,
    "",
    f"certified: {result['certified']}",
    f"patch_manifest_count: {len(patch_manifest)}",
    "",
    "Patch manifest preview:",
    "",
]

for item in patch_manifest:
    lines.append(
        f"- {item['target_path']} | action={item['planned_action']} | "
        f"exists_now={item['exists_now']} | write_allowed_now={item['write_allowed_now']}"
    )

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(json.dumps({
    "phase": PHASE,
    "patch_manifest_count": len(patch_manifest),
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
    "recommended_next_phase": result["recommended_next_phase"],
    "certified": result["certified"],
}, indent=2))
