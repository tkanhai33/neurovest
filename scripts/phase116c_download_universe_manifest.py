#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "dataset_provider_registry/116B_dataset_provider_registry_latest.json"
PHASE = "116C_DOWNLOAD_UNIVERSE_MANIFEST"

RESEARCH_ROOT = ROOT / "backend/app/stacks/learning_research/research_data"
MANIFEST_DIR = RESEARCH_ROOT / "manifests/download_universe"
MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

OUT_DIR = ARCH / "download_universe_manifest"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "116C_download_universe_manifest_latest.json"
OUT_TXT = OUT_DIR / "116C_download_universe_manifest_latest.txt"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)

canada_equities = sorted(set([
    "RY.TO","TD.TO","BNS.TO","BMO.TO","CM.TO","NA.TO",
    "ENB.TO","TRP.TO","PPL.TO","KEY.TO",
    "CNQ.TO","SU.TO","CVE.TO","IMO.TO","ARX.TO","TOU.TO",
    "CNR.TO","CP.TO","WCN.TO",
    "BAM.TO","BN.TO",
    "SHOP.TO","ATZ.TO","CSU.TO","GIB.A.TO",
    "FTS.TO","EMA.TO","AQN.TO",
    "L.TO","DOL.TO",
    "POW.TO","IFC.TO","MFC.TO","SLF.TO",
    "TRI.TO","CCO.TO","NTR.TO",
    "FFH.TO","SAP.TO","MG.TO"
]))

usa_equities = sorted(set([
    "AAPL","MSFT","NVDA","AMD","AMZN",
    "META","GOOGL","NFLX","TSLA","PLTR",
    "JPM","BAC","GS","MS","V","MA",
    "UNH","LLY","JNJ","PFE",
    "XOM","CVX",
    "KO","PEP","MCD","WMT","COST",
    "ORCL","CRM","ADBE","INTC","AVGO",
    "QCOM","TXN","MU","PANW","SNOW",
    "UBER","ABNB","DIS","NKE"
]))

canadian_etfs = sorted(set([
    "VFV.TO","VUN.TO","VCN.TO","XIU.TO","XIC.TO",
    "ZSP.TO","XQQ.TO","XAW.TO","XEQT.TO","VEQT.TO",
    "VGRO.TO","XGRO.TO","HBAL.TO","HXS.TO","HXT.TO"
]))

us_etfs = sorted(set([
    "SPY","VOO","IVV","QQQ","VTI",
    "DIA","IWM","XLF","XLK","XLE",
    "XLV","XLY","XLP","XLU","SMH"
]))

indexes = sorted(set([
    "^GSPTSE","^GSPC","^IXIC","^DJI","^RUT",
    "^VIX","^NDX","^TNX","^TYX"
]))

fx = sorted(set([
    "CADUSD=X","USDCAD=X","EURUSD=X","GBPUSD=X",
    "USDJPY=X","AUDUSD=X","NZDUSD=X","USDCHF=X"
]))

commodities = sorted(set([
    "GC=F","SI=F","CL=F","NG=F",
    "HG=F","ZC=F","ZS=F","ZW=F"
]))

crypto = sorted(set([
    "BTC-USD","ETH-USD","SOL-USD","XRP-USD",
    "ADA-USD","DOGE-USD","AVAX-USD","LINK-USD"
]))

asset_groups = {
    "equities_canada": canada_equities,
    "equities_usa": usa_equities,
    "canadian_etfs": canadian_etfs,
    "us_etfs": us_etfs,
    "indexes": indexes,
    "fx": fx,
    "commodities": commodities,
    "crypto": crypto,
}

total_symbols = sum(len(v) for v in asset_groups.values())

download_universe = {
    "manifest_id": "DOWNLOAD_UNIVERSE_V2",
    "created_at": datetime.now(UTC).isoformat(),
    "provider": "YFINANCE",
    "period": "max",
    "interval": "1d",
    "asset_groups": asset_groups,
    "totals": {**{k: len(v) for k, v in asset_groups.items()}, "total_symbols": total_symbols},
    "download_policy": {
        "downloads_enabled": False,
        "preview_only": True,
        "file_repository_only": True,
        "database_writes_allowed": False,
        "training_execution_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
}

manifest_path = MANIFEST_DIR / "download_universe_v2.json"
manifest_path.write_text(json.dumps(download_universe, indent=2), encoding="utf-8")

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "manifest_written": manifest_path.exists(),
    "total_symbols_expanded": total_symbols >= 140,
    "downloads_disabled": download_universe["download_policy"]["downloads_enabled"] is False,
    "db_write_blocked": download_universe["download_policy"]["database_writes_allowed"] is False,
    "broker_live_blocked": (
        download_universe["download_policy"]["broker_execution_enabled"] is False
        and download_universe["download_policy"]["live_execution_enabled"] is False
    ),
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "download_universe_manifest": str(manifest_path),
    "download_universe": download_universe,
    "checks": checks,
    "policy": download_universe["download_policy"],
    "recommended_next_phase": "116D_DOWNLOAD_UNIVERSE_CERTIFICATION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"manifest_id: {download_universe['manifest_id']}",
        f"total_symbols: {total_symbols}",
        "downloads_enabled: False",
        "",
        "Expanded download universe manifest created.",
        "No downloads executed yet.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "manifest_id": download_universe["manifest_id"],
    "total_symbols": total_symbols,
    "recommended_next_phase": result["recommended_next_phase"],
}, indent=2))
