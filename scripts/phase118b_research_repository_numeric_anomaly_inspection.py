#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
from collections import Counter, defaultdict
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "research_repository_numeric_integrity_scan/118A_research_repository_numeric_integrity_scan_latest.json"

OUT_DIR = ARCH / "research_repository_numeric_anomaly_inspection"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "118B_research_repository_numeric_anomaly_inspection_latest.json"
OUT_TXT = OUT_DIR / "118B_research_repository_numeric_anomaly_inspection_latest.txt"

PHASE = "118B_RESEARCH_REPOSITORY_NUMERIC_ANOMALY_INSPECTION"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)
bad = source.get("bad_sample", [])

reason_counts = Counter()
symbol_counts = Counter()
file_counts = Counter()
asset_group_counts = Counter()

for item in bad:
    reason = item.get("reason", "unknown")
    symbol = item.get("symbol", "unknown")
    file_path = item.get("file", "unknown")

    reason_counts[reason] += 1
    symbol_counts[symbol] += 1
    file_counts[file_path] += 1

    parts = Path(file_path).parts
    asset_group = "unknown"
    if "research_data" in parts:
        idx = parts.index("research_data")
        if idx + 1 < len(parts):
            asset_group = parts[idx + 1]
    asset_group_counts[asset_group] += 1

suspected_causes = []

if reason_counts.get("close_outside_high_low_range", 0) > 0:
    suspected_causes.append({
        "reason": "close_outside_high_low_range",
        "likely_cause": "adjusted close or provider adjusted value being compared against raw intraday high/low",
        "recommended_policy": "do not reject until adjusted/unadjusted column semantics are classified"
    })

if reason_counts.get("price_out_of_bounds", 0) > 0:
    suspected_causes.append({
        "reason": "price_out_of_bounds",
        "likely_cause": "zero or invalid OHLC field from provider",
        "recommended_policy": "inspect individual rows and mark symbol/date for exclusion or provider retry"
    })

if reason_counts.get("not_finite_number", 0) > 0:
    suspected_causes.append({
        "reason": "not_finite_number",
        "likely_cause": "missing numeric provider field or NaN written through CSV",
        "recommended_policy": "reject affected row unless provider retry fixes it"
    })

if reason_counts.get("daily_return_out_of_bounds", 0) > 0:
    suspected_causes.append({
        "reason": "daily_return_out_of_bounds",
        "likely_cause": "corporate action, asset-specific discontinuity, or unadjusted/adjusted mismatch",
        "recommended_policy": "route to corporate action / adjustment policy before training"
    })

inspection = {
    "bad_sample_size": len(bad),
    "source_bad_count": source.get("bad_count"),
    "reason_counts_sample": dict(reason_counts),
    "top_symbols_sample": symbol_counts.most_common(25),
    "top_files_sample": file_counts.most_common(25),
    "asset_group_counts_sample": dict(asset_group_counts),
    "suspected_causes": suspected_causes,
    "important_note": "This phase inspects the sampled anomalies from 118A. A full anomaly export phase is required to inspect all 4806 bad rows.",
    "full_export_required": True,
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_failed_expected": source.get("certified") is False,
    "bad_sample_present": len(bad) > 0,
    "source_bad_count_present": source.get("bad_count", 0) > 0,
    "reason_counts_present": len(reason_counts) > 0,
    "suspected_causes_present": len(suspected_causes) > 0,
    "full_export_required": inspection["full_export_required"] is True,
    "db_write_blocked": True,
    "training_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "NUMERIC_ANOMALY_INSPECTION_SAMPLE_ONLY",
    "inspection": inspection,
    "checks": checks,
    "policy": {
        "inspection_only": True,
        "data_modification_allowed": False,
        "approved_for_training": False,
        "database_writes_allowed": False,
        "training_execution_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "118C_RESEARCH_REPOSITORY_FULL_ANOMALY_EXPORT",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"source_bad_count: {source.get('bad_count')}",
        f"bad_sample_size: {len(bad)}",
        f"reason_counts_sample: {dict(reason_counts)}",
        f"top_symbols_sample: {symbol_counts.most_common(10)}",
        "",
        "Sample anomaly inspection completed.",
        "Full anomaly export required before normalization policy.",
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
    "source_bad_count": source.get("bad_count"),
    "bad_sample_size": len(bad),
    "reason_counts_sample": dict(reason_counts),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
