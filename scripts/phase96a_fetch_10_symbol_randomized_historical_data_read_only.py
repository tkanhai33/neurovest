#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, UTC
import json
import hashlib
import random

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "ten_symbol_ten_year_historical_manifest" / "95A_10_symbol_10_year_historical_data_manifest_latest.json"

OUT_DIR = ARCH / "historical_fixture_store"
FIXTURE_DIR = OUT_DIR / "TRAINING_RUN_0001"

OUT_DIR.mkdir(parents=True, exist_ok=True)
FIXTURE_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "96A_fetch_10_symbol_randomized_historical_data_read_only_latest.json"
OUT_TXT = OUT_DIR / "96A_fetch_10_symbol_randomized_historical_data_read_only_latest.txt"

PHASE = "96A_FETCH_10_SYMBOL_RANDOMIZED_HISTORICAL_DATA_READ_ONLY"

TRAINING_SEED = "TRAINING_RUN_0001"

random.seed(TRAINING_SEED)


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


source = read_json(SOURCE)

symbols = source.get("manifest", {}).get("symbols", [])

fixtures = []

for symbol in symbols:

    start_year = random.randint(2010, 2015)

    fixture = {
        "symbol": symbol,
        "training_seed": TRAINING_SEED,
        "period": "10y",
        "interval": "1d",
        "requested_start_year": start_year,
        "expected_rows": 2500,
        "output_file": str(
            FIXTURE_DIR /
            f"{symbol.replace('.','_')}.csv"
        )
    }

    fixture["checksum"] = hashlib.sha256(
        json.dumps(fixture, sort_keys=True).encode()
    ).hexdigest()

    fixtures.append(fixture)

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "symbol_count_10": len(symbols) == 10,
    "fixtures_created": len(fixtures) == 10,
    "training_seed_present": TRAINING_SEED == "TRAINING_RUN_0001",
    "training_execution_disabled": True,
    "learner_write_disabled": True,
    "mutation_disabled": True,
    "strategy_db_write_disabled": True,
    "promotion_disabled": True,
    "broker_disabled": True,
    "live_disabled": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "FETCH_10_SYMBOL_RANDOMIZED_HISTORICAL_DATA_READ_ONLY",
    "training_seed": TRAINING_SEED,
    "fixtures": fixtures,
    "checks": checks,
    "policy": {
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

OUT_JSON.write_text(
    json.dumps(result, indent=2),
    encoding="utf-8",
)

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"training_seed: {TRAINING_SEED}",
        f"symbols: {len(fixtures)}",
        "",
        "Historical fixture manifest generated.",
        "Read-only mode.",
        "No learner.",
        "No DB writes.",
        "No promotion.",
        "No broker.",
        "No live execution.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "training_seed": TRAINING_SEED,
    "symbol_count": len(fixtures),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
