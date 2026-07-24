#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json
import shutil
import pandas as pd

ROOT = Path(".").resolve()
OUT_DIR = ROOT / "runtime" / "research_datasets" / "statcan_10100125"
RAW = OUT_DIR / "raw"
REGISTRY = OUT_DIR / "65A_research_dataset_intake_registry_latest.json"

PHASE = "65A_RESEARCH_DATASET_INTAKE_REGISTRY_STUB"

SOURCE_DATA = next(iter(sorted((Path.home() / "Downloads").glob("*10100125*.csv"))), Path.home() / "Downloads" / "10100125.csv")
SOURCE_META = next(iter(sorted((Path.home() / "Downloads").glob("*10100125*MetaData*.csv"))), Path.home() / "Downloads" / "10100125_MetaData.csv")

RAW.mkdir(parents=True, exist_ok=True)

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_DATASET_INTAKE_REGISTRY",
    "dataset_id": "statcan_10100125",
    "dataset_name": "Statistics of the Toronto Stock Exchange",
    "source_files": {
        "data": str(SOURCE_DATA),
        "metadata": str(SOURCE_META),
    },
    "copied_files": {},
    "checks": {},
    "errors": [],
    "certified": False,
}

try:
    data_target = RAW / "10100125.csv"
    meta_target = RAW / "10100125_MetaData.csv"

    if SOURCE_DATA.exists():
        shutil.copy2(SOURCE_DATA, data_target)

    if SOURCE_META.exists():
        shutil.copy2(SOURCE_META, meta_target)

    result["copied_files"] = {
        "data": str(data_target),
        "metadata": str(meta_target),
    }

    df = pd.read_csv(data_target, sep=";", encoding="utf-8-sig")
    meta_text = meta_target.read_text(encoding="utf-8-sig", errors="replace")

    result["dataset_profile"] = {
        "rows": int(len(df)),
        "columns": list(df.columns),
        "period_min": str(df["PÉRIODE DE RÉFÉRENCE"].min()) if "PÉRIODE DE RÉFÉRENCE" in df.columns else None,
        "period_max": str(df["PÉRIODE DE RÉFÉRENCE"].max()) if "PÉRIODE DE RÉFÉRENCE" in df.columns else None,
        "series_count": int(df["Statistiques de la Bourse de Toronto"].nunique()) if "Statistiques de la Bourse de Toronto" in df.columns else None,
        "geo_values": sorted(df["GÉO"].dropna().unique().tolist()) if "GÉO" in df.columns else [],
        "sample_series": (
            sorted(df["Statistiques de la Bourse de Toronto"].dropna().unique().tolist())[:20]
            if "Statistiques de la Bourse de Toronto" in df.columns
            else []
        ),
    }

    result["research_use_policy"] = {
        "allowed_uses": [
            "research_reference",
            "canadian_market_context",
            "macro_regime_context",
            "sector_index_context",
            "historical_market_summary",
            "future_feature_candidate",
        ],
        "forbidden_uses": [
            "live_trading_signal",
            "broker_execution",
            "strategy_promotion",
            "autonomous_learning",
            "runtime_mutation",
            "direct_order_routing",
        ],
        "runtime_execution_allowed": False,
        "learning_enabled": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    }

    result["checks"]["source_data_exists"] = SOURCE_DATA.exists()
    result["checks"]["source_metadata_exists"] = SOURCE_META.exists()
    result["checks"]["data_copied"] = data_target.exists()
    result["checks"]["metadata_copied"] = meta_target.exists()
    result["checks"]["rows_present"] = len(df) > 0
    result["checks"]["columns_present"] = len(df.columns) > 0
    result["checks"]["period_column_present"] = "PÉRIODE DE RÉFÉRENCE" in df.columns
    result["checks"]["series_column_present"] = "Statistiques de la Bourse de Toronto" in df.columns
    result["checks"]["value_column_present"] = "VALEUR" in df.columns
    result["checks"]["metadata_mentions_tse"] = "Bourse de Toronto" in meta_text
    result["checks"]["runtime_blocked"] = result["research_use_policy"]["runtime_execution_allowed"] is False
    result["checks"]["learning_blocked"] = result["research_use_policy"]["learning_enabled"] is False
    result["checks"]["promotion_blocked"] = result["research_use_policy"]["promotion_enabled"] is False
    result["checks"]["broker_blocked"] = result["research_use_policy"]["broker_execution_enabled"] is False
    result["checks"]["live_blocked"] = result["research_use_policy"]["live_execution_enabled"] is False

    result["recommended_next_phase"] = "65B_RESEARCH_DATASET_PROFILE_ROLLUP_CERTIFICATION"

    result["certified"] = all(result["checks"].values())

except Exception as exc:
    result["errors"].append({
        "type": type(exc).__name__,
        "message": str(exc),
    })

REGISTRY.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps(result, indent=2, ensure_ascii=False))
print(f"\nWROTE: {REGISTRY}")
