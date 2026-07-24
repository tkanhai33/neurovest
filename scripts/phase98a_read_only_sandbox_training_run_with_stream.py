#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json, csv, statistics

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "research_whitelist_and_training_input_certification" / "97A_research_whitelist_and_training_input_certification_latest.json"

OUT_DIR = ARCH / "read_only_sandbox_training_run_with_stream"
SANDBOX = OUT_DIR / "sandbox" / "TRAINING_RUN_0001"
SANDBOX.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "98A_read_only_sandbox_training_run_with_stream_latest.json"
OUT_TXT = OUT_DIR / "98A_read_only_sandbox_training_run_with_stream_latest.txt"
STREAM = OUT_DIR / "training_stream.jsonl"
OBS = SANDBOX / "observations.json"
CANDIDATES = SANDBOX / "candidate_ideas.json"
SUMMARY = SANDBOX / "training_summary.txt"

PHASE = "98A_READ_ONLY_SANDBOX_TRAINING_RUN_WITH_STREAM"

def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def emit(event: dict):
    event["ts"] = datetime.now(UTC).isoformat()
    with STREAM.open("a", encoding="utf-8") as h:
        h.write(json.dumps(event) + "\n")

def read_rows(path: Path):
    with path.open("r", encoding="utf-8") as h:
        return list(csv.DictReader(h))

source = read_json(SOURCE)
manifest = source.get("manifest", {})
fixtures = manifest.get("historical_fixtures", [])
research_docs = manifest.get("research_documents", [])

STREAM.parent.mkdir(parents=True, exist_ok=True)
STREAM.write_text("", encoding="utf-8")

observations = []
candidates = []
errors = []

emit({"event": "training_started", "phase": PHASE})

for i, fixture in enumerate(fixtures, start=1):
    symbol = fixture.get("symbol")
    path = Path(fixture.get("csv", ""))

    try:
        rows = read_rows(path)
        closes = [float(r["close"]) for r in rows if r.get("close")]
        returns = [(b / a) - 1.0 for a, b in zip(closes, closes[1:]) if a]

        cumulative = (closes[-1] / closes[0]) - 1.0 if len(closes) > 1 and closes[0] else 0.0
        volatility = statistics.pstdev(returns) if len(returns) > 1 else 0.0

        obs = {
            "symbol": symbol,
            "row_count": len(rows),
            "date_min": rows[0]["date"] if rows else None,
            "date_max": rows[-1]["date"] if rows else None,
            "cumulative_return": cumulative,
            "volatility": volatility,
            "read_only": True,
        }
        observations.append(obs)

        emit({
            "event": "symbol_processed",
            "progress": f"{i}/{len(fixtures)}",
            "symbol": symbol,
            "rows": len(rows),
            "cumulative_return": cumulative,
            "volatility": volatility,
        })

        candidates.append({
            "candidate_id": f"CANDIDATE_{len(candidates)+1:03d}",
            "symbol": symbol,
            "strategy_family": "sandbox_observation",
            "hypothesis": f"{symbol} generated a read-only training observation.",
            "confidence": 0.60,
            "status": "SANDBOX_IDEA_ONLY",
            "writes_allowed": False,
            "promotion_allowed": False,
        })

    except Exception as exc:
        errors.append({"symbol": symbol, "type": type(exc).__name__, "message": str(exc)})
        emit({"event": "symbol_error", "symbol": symbol, "error": str(exc)})

OBS.write_text(json.dumps(observations, indent=2), encoding="utf-8")
CANDIDATES.write_text(json.dumps(candidates, indent=2), encoding="utf-8")
SUMMARY.write_text(
    f"READ ONLY TRAINING RUN\nobservations: {len(observations)}\ncandidate_ideas: {len(candidates)}\nerrors: {len(errors)}\n",
    encoding="utf-8",
)

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "training_result": {
        "training_run_id": "TRAINING_RUN_0001",
        "training_execution_simulated": True,
        "permanent_learning_enabled": False,
        "observations_count": len(observations),
        "candidate_ideas_count": len(candidates),
        "research_documents_count": len(research_docs),
        "errors": errors,
        "hard_blocks": {
            "learner_write_executed": False,
            "mutation_executed": False,
            "queue_write_executed": False,
            "strategy_db_write_executed": False,
            "promotion_executed": False,
            "broker_execution_executed": False,
            "live_execution_executed": False,
        },
    },
    "artifacts": {
        "observations": str(OBS),
        "candidate_ideas": str(CANDIDATES),
        "summary": str(SUMMARY),
        "stream": str(STREAM),
    },
    "checks": {
        "source_exists": SOURCE.exists(),
        "source_certified": source.get("certified") is True,
        "fixtures_present": len(fixtures) == 10,
        "observations_written": OBS.exists(),
        "candidate_ideas_written": CANDIDATES.exists(),
        "summary_written": SUMMARY.exists(),
        "stream_written": STREAM.exists(),
        "errors_none": len(errors) == 0,
    },
    "recommended_next_phase": "99A_100A_TRAINING_SAFETY_CERTIFICATION_AND_RESULT_STORE",
    "certified": SOURCE.exists() and source.get("certified") is True and len(fixtures) == 10 and len(errors) == 0,
}

emit({"event": "training_completed", "certified": result["certified"], "candidate_ideas": len(candidates)})

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(f"{PHASE}\n\ncertified: {result['certified']}\nobservations: {len(observations)}\ncandidate_ideas: {len(candidates)}\nerrors: {len(errors)}\n", encoding="utf-8")

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "observations": len(observations),
    "candidate_ideas": len(candidates),
    "errors": errors,
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
