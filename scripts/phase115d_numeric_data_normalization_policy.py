#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "shop_to_numeric_anomaly_inspection/115C_shop_to_numeric_anomaly_inspection_latest.json"

OUT_DIR = ARCH / "numeric_data_normalization_policy"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "115D_numeric_data_normalization_policy_latest.json"
OUT_TXT = OUT_DIR / "115D_numeric_data_normalization_policy_latest.txt"

PHASE = "115D_NUMERIC_DATA_NORMALIZATION_POLICY"


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)
summary = source.get("summary", {})

policy = {
    "policy_id": "NUMERIC_NORMALIZATION_POLICY_V1",
    "mode": "POLICY_ONLY_NO_DATA_MODIFICATION",
    "rules": [
        {
            "name": "finite_real_numbers_only",
            "action": "REJECT_EVENT",
            "applies_to": ["open", "high", "low", "close", "volume", "returns"],
        },
        {
            "name": "price_bounds",
            "action": "REJECT_EVENT",
            "min_exclusive": 0.0,
            "max_exclusive": 1000000.0,
        },
        {
            "name": "volume_non_negative",
            "action": "REJECT_EVENT",
            "min_inclusive": 0,
        },
        {
            "name": "corporate_action_discontinuity",
            "action": "MARK_FOR_NORMALIZATION",
            "condition": "daily_return < -0.95 or daily_return > 10.0",
            "repair_strategy": "NORMALIZE_SPLIT_OR_EXCLUDE_UNTIL_CORPORATE_ACTION_VERIFIED",
        },
        {
            "name": "close_inside_high_low",
            "action": "REJECT_EVENT",
            "condition": "low <= close <= high",
        }
    ],
    "known_anomalies": [
        {
            "symbol": "SHOP.TO",
            "date": "2016-07-07",
            "reason": "possible_stock_split_or_adjusted_unadjusted_price_mismatch",
            "repair_strategy": "NORMALIZE_SPLIT",
            "approved_for_auto_fix": False,
            "requires_manual_or_verified_corporate_action_source": True,
        }
    ],
    "hard_blocks": {
        "data_modification_allowed": False,
        "normalization_executed": False,
        "training_execution_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
}

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "policy_id_present": bool(policy["policy_id"]),
    "policy_only_no_data_modification": policy["mode"] == "POLICY_ONLY_NO_DATA_MODIFICATION",
    "known_shop_to_anomaly_registered": any(
        item["symbol"] == "SHOP.TO" and item["date"] == "2016-07-07"
        for item in policy["known_anomalies"]
    ),
    "normalization_required_from_115c": summary.get("normalization_required") is True,
    "auto_fix_not_approved": all(
        item["approved_for_auto_fix"] is False
        for item in policy["known_anomalies"]
    ),
    "normalization_not_executed": policy["hard_blocks"]["normalization_executed"] is False,
    "data_modification_blocked": policy["hard_blocks"]["data_modification_allowed"] is False,
    "training_blocked": policy["hard_blocks"]["training_execution_enabled"] is False,
    "strategy_db_write_blocked": policy["hard_blocks"]["strategy_db_write_allowed"] is False,
    "promotion_blocked": policy["hard_blocks"]["promotion_enabled"] is False,
    "broker_live_blocked": (
        policy["hard_blocks"]["broker_execution_enabled"] is False
        and policy["hard_blocks"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "NUMERIC_DATA_NORMALIZATION_POLICY",
    "source_anomaly_inspection": str(SOURCE),
    "policy": policy,
    "checks": checks,
    "recommended_next_phase": "115E_SHOP_TO_NORMALIZATION_PREVIEW",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"policy_id: {policy['policy_id']}",
        "known_anomaly: SHOP.TO 2016-07-07",
        "normalization_executed: False",
        "auto_fix_approved: False",
        "",
        "Numeric normalization policy created.",
        "No data modification. No DB writes. No broker/live.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "policy_id": policy["policy_id"],
    "known_anomalies": len(policy["known_anomalies"]),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
