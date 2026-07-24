#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "download_universe_manifest/116C_download_universe_manifest_latest.json"

OUT_DIR = ARCH / "download_universe_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "116D_download_universe_certification_latest.json"
OUT_TXT = OUT_DIR / "116D_download_universe_certification_latest.txt"

PHASE = "116D_DOWNLOAD_UNIVERSE_CERTIFICATION"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)
universe = source.get("download_universe", {})
asset_groups = universe.get("asset_groups", {})
totals = universe.get("totals", {})
policy = universe.get("download_policy", {})

all_symbols = []
duplicates = []

for group, symbols in asset_groups.items():
    for symbol in symbols:
        if symbol in all_symbols:
            duplicates.append(symbol)
        all_symbols.append(symbol)

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "manifest_id_v2": universe.get("manifest_id") == "DOWNLOAD_UNIVERSE_V2",
    "provider_yfinance": universe.get("provider") == "YFINANCE",
    "period_max": universe.get("period") == "max",
    "interval_daily": universe.get("interval") == "1d",
    "total_symbols_144": totals.get("total_symbols") == 144,
    "asset_groups_present": len(asset_groups) == 8,
    "no_duplicates": len(duplicates) == 0,
    "all_symbols_non_empty": all(isinstance(s, str) and s.strip() for s in all_symbols),
    "downloads_disabled": policy.get("downloads_enabled") is False,
    "preview_only": policy.get("preview_only") is True,
    "file_repository_only": policy.get("file_repository_only") is True,
    "db_write_blocked": policy.get("database_writes_allowed") is False,
    "training_blocked": policy.get("training_execution_enabled") is False,
    "broker_live_blocked": (
        policy.get("broker_execution_enabled") is False
        and policy.get("live_execution_enabled") is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "source_manifest": str(SOURCE),
    "manifest_id": universe.get("manifest_id"),
    "provider": universe.get("provider"),
    "totals": totals,
    "asset_group_counts": {k: len(v) for k, v in asset_groups.items()},
    "duplicates": duplicates,
    "checks": checks,
    "policy": policy,
    "recommended_next_phase": "116E_BULK_DOWNLOAD_EXECUTION_PLAN",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"manifest_id: {result['manifest_id']}",
        f"provider: {result['provider']}",
        f"total_symbols: {totals.get('total_symbols')}",
        f"asset_groups: {len(asset_groups)}",
        f"duplicates: {len(duplicates)}",
        "",
        "Download universe certified.",
        "No downloads executed.",
        "No DB writes. No training. No broker/live.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "manifest_id": result["manifest_id"],
    "total_symbols": totals.get("total_symbols"),
    "duplicates": len(duplicates),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
