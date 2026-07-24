#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"
SOURCE = ARCH / "research_repository_expansion_plan/116A_research_repository_expansion_plan_latest.json"

PHASE = "116B_DATASET_PROVIDER_REGISTRY"

RESEARCH_ROOT = ROOT / "backend/app/stacks/learning_research/research_data"
PROVIDER_DIR = RESEARCH_ROOT / "manifests/providers"
PROVIDER_DIR.mkdir(parents=True, exist_ok=True)

OUT_DIR = ARCH / "dataset_provider_registry"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "116B_dataset_provider_registry_latest.json"
OUT_TXT = OUT_DIR / "116B_dataset_provider_registry_latest.txt"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)

providers = {
    "YFINANCE": {
        "provider_id": "YFINANCE",
        "name": "Yahoo Finance via yfinance",
        "enabled": True,
        "free_provider": True,
        "requires_api_key": False,
        "capabilities": [
            "daily_ohlcv",
            "adjusted_prices",
            "splits",
            "dividends",
            "etfs",
            "indexes"
        ],
        "allowed_asset_classes": [
            "equity",
            "etf",
            "index"
        ],
        "write_policy": "FILE_REPOSITORY_ONLY",
        "db_write_allowed": False,
        "broker_execution_allowed": False,
        "live_execution_allowed": False
    },
    "FRED_CANADA_WORKBOOK": {
        "provider_id": "FRED_CANADA_WORKBOOK",
        "name": "Existing FRED Canada Workbook",
        "enabled": True,
        "free_provider": True,
        "requires_api_key": False,
        "capabilities": [
            "macro_annual",
            "macro_quarterly",
            "macro_monthly",
            "macro_5_year"
        ],
        "allowed_asset_classes": [
            "macro"
        ],
        "write_policy": "FILE_REPOSITORY_ONLY",
        "db_write_allowed": False,
        "broker_execution_allowed": False,
        "live_execution_allowed": False
    },
    "BANK_OF_CANADA": {
        "provider_id": "BANK_OF_CANADA",
        "name": "Bank of Canada",
        "enabled": False,
        "free_provider": True,
        "requires_api_key": False,
        "capabilities": [
            "interest_rates",
            "exchange_rates",
            "macro_series"
        ],
        "allowed_asset_classes": [
            "macro"
        ],
        "write_policy": "REGISTERED_FOR_FUTURE_USE_ONLY",
        "db_write_allowed": False,
        "broker_execution_allowed": False,
        "live_execution_allowed": False
    },
    "FRED_US": {
        "provider_id": "FRED_US",
        "name": "FRED US",
        "enabled": False,
        "free_provider": True,
        "requires_api_key": False,
        "capabilities": [
            "macro_series",
            "rates",
            "inflation",
            "employment",
            "gdp"
        ],
        "allowed_asset_classes": [
            "macro"
        ],
        "write_policy": "REGISTERED_FOR_FUTURE_USE_ONLY",
        "db_write_allowed": False,
        "broker_execution_allowed": False,
        "live_execution_allowed": False
    },
    "HUGGINGFACE_REFERENCE": {
        "provider_id": "HUGGINGFACE_REFERENCE",
        "name": "Hugging Face Reference Datasets and Models",
        "enabled": False,
        "free_provider": True,
        "requires_api_key": False,
        "capabilities": [
            "reference_datasets",
            "sentiment_datasets",
            "financial_text_datasets",
            "external_model_reference"
        ],
        "allowed_asset_classes": [
            "research",
            "sentiment",
            "external_model_reference"
        ],
        "write_policy": "REGISTERED_FOR_FUTURE_USE_ONLY",
        "db_write_allowed": False,
        "broker_execution_allowed": False,
        "live_execution_allowed": False
    }
}

registry = {
    "registry_id": "DATASET_PROVIDER_REGISTRY_V1",
    "created_at": datetime.now(UTC).isoformat(),
    "providers": providers,
    "global_policy": {
        "downloads_allowed_by_registry": False,
        "database_writes_allowed": False,
        "training_execution_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False
    }
}

(PROVIDER_DIR / "dataset_provider_registry.json").write_text(
    json.dumps(registry, indent=2),
    encoding="utf-8"
)

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "research_root_exists": RESEARCH_ROOT.exists(),
    "provider_dir_exists": PROVIDER_DIR.exists(),
    "registry_written": (PROVIDER_DIR / "dataset_provider_registry.json").exists(),
    "yfinance_enabled": providers["YFINANCE"]["enabled"] is True,
    "fred_canada_enabled": providers["FRED_CANADA_WORKBOOK"]["enabled"] is True,
    "future_providers_registered_disabled": (
        providers["BANK_OF_CANADA"]["enabled"] is False
        and providers["FRED_US"]["enabled"] is False
        and providers["HUGGINGFACE_REFERENCE"]["enabled"] is False
    ),
    "downloads_not_enabled_yet": registry["global_policy"]["downloads_allowed_by_registry"] is False,
    "db_write_blocked": registry["global_policy"]["database_writes_allowed"] is False,
    "training_blocked": registry["global_policy"]["training_execution_enabled"] is False,
    "broker_live_blocked": (
        registry["global_policy"]["broker_execution_enabled"] is False
        and registry["global_policy"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "provider_registry": str(PROVIDER_DIR / "dataset_provider_registry.json"),
    "providers_registered": list(providers.keys()),
    "checks": checks,
    "policy": registry["global_policy"],
    "recommended_next_phase": "116C_DOWNLOAD_UNIVERSE_MANIFEST",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"providers_registered: {len(providers)}",
        "enabled_now: YFINANCE, FRED_CANADA_WORKBOOK",
        "downloads_allowed_by_registry: False",
        "",
        "Dataset provider registry created.",
        "No downloads. No DB writes. No broker/live.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "providers_registered": len(providers),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
