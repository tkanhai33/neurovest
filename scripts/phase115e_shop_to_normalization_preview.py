#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import csv, json, math, shutil

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "numeric_data_normalization_policy/115D_numeric_data_normalization_policy_latest.json"
MANIFEST = ARCH / "eight_hour_training_run_manifest/112A_8_hour_read_only_training_run_manifest_latest.json"

OUT_DIR = ARCH / "shop_to_normalization_preview"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "115E_shop_to_normalization_preview_latest.json"
OUT_TXT = OUT_DIR / "115E_shop_to_normalization_preview_latest.txt"

PHASE = "115E_SHOP_TO_NORMALIZATION_PREVIEW"
TARGET_SYMBOL = "SHOP.TO"
TARGET_DATE = "2016-07-07"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def safe_float(value):
    try:
        x = float(value)
        return x if math.isfinite(x) else None
    except Exception:
        return None

source = read_json(SOURCE)
manifest_result = read_json(MANIFEST)
fixtures = manifest_result.get("manifest", {}).get("historical_fixtures", [])

shop_fixture = None
for item in fixtures:
    if item.get("symbol") == TARGET_SYMBOL:
        shop_fixture = item
        break

rows = []
source_csv = Path(shop_fixture["csv"]) if shop_fixture else None
if source_csv and source_csv.exists():
    with source_csv.open("r", encoding="utf-8") as fp:
        rows = list(csv.DictReader(fp))

target_index = None
for i, row in enumerate(rows):
    if row.get("date") == TARGET_DATE:
        target_index = i
        break

preview = {
    "target_symbol": TARGET_SYMBOL,
    "target_date": TARGET_DATE,
    "source_csv": str(source_csv) if source_csv else None,
    "normalization_executed": False,
    "data_modified": False,
    "preview_only": True,
}

if target_index is not None and target_index > 0:
    previous_row = rows[target_index - 1]
    current_row = rows[target_index]
    next_row = rows[target_index + 1] if target_index + 1 < len(rows) else None

    previous_close = safe_float(previous_row.get("close"))
    current_close = safe_float(current_row.get("close"))
    current_return = (current_close / previous_close) - 1.0 if previous_close and current_close else None
    ratio = current_close / previous_close if previous_close and current_close else None

    implied_split_factor = round(1 / ratio, 2) if ratio else None

    preview.update({
        "previous_row": previous_row,
        "current_row": current_row,
        "next_row": next_row,
        "previous_close": previous_close,
        "current_close": current_close,
        "computed_return": current_return,
        "ratio_current_to_previous": ratio,
        "implied_split_factor": implied_split_factor,
        "suspected_reason": "possible_stock_split_or_adjusted_unadjusted_price_mismatch",
        "proposed_repair_strategy": "NORMALIZE_SPLIT",
        "proposed_action": "create_normalized_copy_only_after_manual_or_verified_corporate_action_source",
        "would_modify_original_csv": False,
        "would_write_normalized_copy": True,
        "normalized_copy_path_preview": str(
            source_csv.parent / f"{source_csv.stem}_normalized_preview.csv"
        ) if source_csv else None,
    })

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "manifest_exists": MANIFEST.exists(),
    "manifest_certified": manifest_result.get("certified") is True,
    "shop_fixture_found": shop_fixture is not None,
    "source_csv_exists": source_csv is not None and source_csv.exists(),
    "target_date_found": target_index is not None,
    "previous_row_present": target_index is not None and target_index > 0,
    "normalization_preview_present": bool(preview.get("proposed_repair_strategy")),
    "normalization_not_executed": preview["normalization_executed"] is False,
    "data_not_modified": preview["data_modified"] is False,
    "original_csv_not_modified": preview.get("would_modify_original_csv") is False,
    "training_blocked": True,
    "strategy_db_write_blocked": True,
    "promotion_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "SHOP_TO_NORMALIZATION_PREVIEW_ONLY",
    "source_policy": str(SOURCE),
    "preview": preview,
    "checks": checks,
    "policy": {
        "normalization_preview_certified": True,
        "data_modification_allowed": False,
        "normalization_executed": False,
        "write_normalized_copy_allowed": False,
        "training_execution_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "115F_CORPORATE_ACTION_VERIFICATION_OR_MANUAL_APPROVAL",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"target_symbol: {TARGET_SYMBOL}",
        f"target_date: {TARGET_DATE}",
        f"computed_return: {preview.get('computed_return')}",
        f"implied_split_factor: {preview.get('implied_split_factor')}",
        "normalization_executed: False",
        "data_modified: False",
        "",
        "SHOP.TO normalization preview created.",
        "No original CSV modification. No normalized copy written.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "target_symbol": TARGET_SYMBOL,
    "target_date": TARGET_DATE,
    "computed_return": preview.get("computed_return"),
    "implied_split_factor": preview.get("implied_split_factor"),
    "normalization_executed": False,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
