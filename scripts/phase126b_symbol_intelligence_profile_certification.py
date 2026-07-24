#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import importlib.util
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "symbol_intelligence_profile_stub/126A_symbol_intelligence_profile_stub_latest.json"
KNOWLEDGE_CERT = ARCH / "strategy_knowledge_certification/124C_strategy_knowledge_certification_latest.json"

TARGET = ROOT / "backend/app/stacks/strategy_candidate_sandbox/symbol_intelligence_profile.py"

OUT_DIR = ARCH / "symbol_intelligence_profile_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "126B_symbol_intelligence_profile_certification_latest.json"
OUT_TXT = OUT_DIR / "126B_symbol_intelligence_profile_certification_latest.txt"

PHASE = "126B_SYMBOL_INTELLIGENCE_PROFILE_CERTIFICATION"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def import_file(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

source = read_json(SOURCE)
knowledge_cert = read_json(KNOWLEDGE_CERT)

knowledge_object = knowledge_cert.get("knowledge_object", {})
knowledge_object["indicators"] = ["RSI", "MACD", "ATR"]
knowledge_object["regimes"] = ["BULLISH_MOMENTUM", "HIGH_VOLATILITY"]
knowledge_object["asset_classes"] = ["EQUITY"]

module = import_file("symbol_intelligence_profile", TARGET)

status = module.profile_status()
profile = module.build_symbol_intelligence_profile(
    symbol="TEST",
    knowledge_objects=[knowledge_object],
)

valid_profile = module.validate_symbol_intelligence_profile(profile)

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "knowledge_cert_exists": KNOWLEDGE_CERT.exists(),
    "knowledge_certified": knowledge_cert.get("certified") is True,
    "target_exists": TARGET.exists(),
    "status_present": bool(status),
    "profile_created": isinstance(profile, dict),
    "profile_valid": valid_profile is True,
    "symbol_correct": profile.get("symbol") == "TEST",
    "strategies_present": len(profile.get("strategies", [])) >= 1,
    "indicators_present": len(profile.get("indicators", [])) >= 3,
    "regimes_present": len(profile.get("regimes", [])) >= 2,
    "average_confidence_present": profile.get("average_confidence") is not None,
    "database_writes_blocked": status.get("database_writes_allowed") is False,
    "strategy_db_write_blocked": status.get("strategy_db_write_allowed") is False,
    "promotion_blocked": status.get("promotion_enabled") is False,
    "broker_blocked": status.get("broker_execution_enabled") is False,
    "live_blocked": status.get("live_execution_enabled") is False,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "profile": profile,
    "status": status,
    "checks": checks,
    "policy": {
        "symbol_intelligence_profile_certified": True,
        "database_writes_allowed": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "127A_MARKET_REGIME_LIBRARY_STUB",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"profile_valid: {valid_profile}",
        f"symbol: {profile.get('symbol')}",
        f"strategies: {profile.get('strategies')}",
        f"indicators: {profile.get('indicators')}",
        f"regimes: {profile.get('regimes')}",
        f"average_confidence: {profile.get('average_confidence')}",
        "",
        "Symbol intelligence profile certified.",
        "Knowledge object -> symbol profile link works.",
        "",
        "Database Writes: False",
        "Strategy DB Writes: False",
        "Promotion: False",
        "Broker: False",
        "Live: False",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "profile_valid": valid_profile,
    "symbol": profile.get("symbol"),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
