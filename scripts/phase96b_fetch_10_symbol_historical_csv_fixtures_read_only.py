#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json, csv, hashlib

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "historical_fixture_store" / "96A_fetch_10_symbol_randomized_historical_data_read_only_latest.json"
FIXTURE_DIR = ARCH / "historical_fixture_store" / "TRAINING_RUN_0001"

OUT_JSON = ARCH / "historical_fixture_store" / "96B_fetch_10_symbol_historical_csv_fixtures_read_only_latest.json"
OUT_TXT = ARCH / "historical_fixture_store" / "96B_fetch_10_symbol_historical_csv_fixtures_read_only_latest.txt"

PHASE = "96B_FETCH_10_SYMBOL_HISTORICAL_CSV_FIXTURES_READ_ONLY"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def scalar(value):
    try:
        if hasattr(value, "iloc"):
            return value.iloc[0]
    except Exception:
        pass
    return value


source = read_json(SOURCE)
fixtures = source.get("fixtures", [])

FIXTURE_DIR.mkdir(parents=True, exist_ok=True)

errors = []
written = []

try:
    import yfinance as yf
except Exception as exc:
    errors.append({"type": type(exc).__name__, "message": f"yfinance import failed: {exc}"})
    yf = None

if yf:
    for fixture in fixtures:
        symbol = fixture["symbol"]
        out_csv = Path(fixture["output_file"])
        out_csv.parent.mkdir(parents=True, exist_ok=True)

        rows = []

        try:
            data = yf.download(
                symbol,
                period="10y",
                interval="1d",
                auto_adjust=False,
                progress=False,
                threads=False,
            )

            for idx, row in data.iterrows():
                rows.append({
                    "symbol": symbol,
                    "date": str(idx.date()),
                    "open": float(scalar(row["Open"])),
                    "high": float(scalar(row["High"])),
                    "low": float(scalar(row["Low"])),
                    "close": float(scalar(row["Close"])),
                    "volume": int(scalar(row["Volume"])),
                })

            with out_csv.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["symbol", "date", "open", "high", "low", "close", "volume"])
                writer.writeheader()
                writer.writerows(rows)

            digest = hashlib.sha256(out_csv.read_bytes()).hexdigest()

            written.append({
                "symbol": symbol,
                "csv": str(out_csv),
                "row_count": len(rows),
                "date_min": rows[0]["date"] if rows else None,
                "date_max": rows[-1]["date"] if rows else None,
                "checksum": digest,
            })

        except Exception as exc:
            errors.append({"symbol": symbol, "type": type(exc).__name__, "message": str(exc)})


checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "fixture_dir_exists": FIXTURE_DIR.exists(),
    "symbols_expected_10": len(fixtures) == 10,
    "csv_written_10": len(written) == 10,
    "all_rows_present": all(item["row_count"] > 0 for item in written),
    "all_symbols_unique": len({item["symbol"] for item in written}) == 10,
    "no_errors": len(errors) == 0,
    "training_execution_blocked": True,
    "strategy_db_write_blocked": True,
    "promotion_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "FETCH_10_SYMBOL_HISTORICAL_CSV_FIXTURES_READ_ONLY",
    "source_manifest": str(SOURCE),
    "fixture_dir": str(FIXTURE_DIR),
    "fixtures_written": written,
    "errors": errors,
    "checks": checks,
    "policy": {
        "historical_csv_fixtures_certified": True,
        "training_execution_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase": "97A_DOCUMENT_RESEARCH_INPUT_WHITELIST",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"csv_written: {len(written)}",
        f"errors: {len(errors)}",
        f"fixture_dir: {FIXTURE_DIR}",
        "",
        "Historical CSV fixtures fetched read-only.",
        "Training/db/promotion/broker/live remain blocked.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "csv_written": len(written),
    "errors": errors,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
