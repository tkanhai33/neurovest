"""
129E_REPLAY_EXECUTION_ENGINE_IMPLEMENTATION

PART 1

Replay Runtime Skeleton

Historical Replay Only

NO DATABASE WRITES
NO STRATEGY PROMOTION
NO BROKER
NO LIVE EXECUTION
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, UTC
from typing import Any
import json
import csv

from backend.app.stacks.strategy_candidate_sandbox.L3_service_facade.learning_artifact_pipeline import (
    build_learning_artifact,
)

from backend.app.stacks.strategy_candidate_sandbox.strategy_knowledge_object import (
    build_strategy_knowledge_object_from_learning_artifact,
)

from backend.app.stacks.strategy_candidate_sandbox.indicator_knowledge_graph import (
    build_indicator_knowledge_graph,
)

from backend.app.stacks.strategy.engine import (
    generate_strategy_decision,
)

DATABASE_WRITES_ALLOWED = False
STRATEGY_DB_WRITE_ALLOWED = False
PROMOTION_ENABLED = False
BROKER_EXECUTION_ENABLED = False
LIVE_EXECUTION_ENABLED = False

ENGINE_ENABLED = True

HEARTBEAT_SECONDS = 30
CHECKPOINT_SECONDS = 300


class ReplayExecutionEngine:

    def __init__(self, run_directory: str | Path):

        self.run_directory = Path(run_directory)

        self.manifest = json.loads(
            (self.run_directory / "manifest.json").read_text(encoding="utf-8")
        )

        self.started_at = datetime.now(UTC)

        self.current_cycle = 0

        self.rows_processed = 0

        self.decisions = 0

        self.errors = 0

    def status(self) -> dict[str, Any]:

        return {

            "enabled": ENGINE_ENABLED,

            "run_id": self.manifest["run_id"],

            "current_cycle": self.current_cycle,

            "rows_processed": self.rows_processed,

            "decisions": self.decisions,

            "errors": self.errors,

            "database_writes_allowed": DATABASE_WRITES_ALLOWED,

            "strategy_db_write_allowed": STRATEGY_DB_WRITE_ALLOWED,

            "promotion_enabled": PROMOTION_ENABLED,

            "broker_execution_enabled": BROKER_EXECUTION_ENABLED,

            "live_execution_enabled": LIVE_EXECUTION_ENABLED,

        }

    def write_heartbeat(self):

        payload = {

            "timestamp": datetime.now(UTC).isoformat(),

            "run_id": self.manifest["run_id"],

            "cycle": self.current_cycle,

            "rows_processed": self.rows_processed,

            "decisions": self.decisions,

            "errors": self.errors,

        }

        (
            self.run_directory /
            "heartbeat.json"
        ).write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )

    def write_checkpoint(self):

        checkpoint = {

            "timestamp": datetime.now(UTC).isoformat(),

            "status": self.status(),

        }

        (
            self.run_directory /
            "checkpoint.json"
        ).write_text(
            json.dumps(checkpoint, indent=2),
            encoding="utf-8",
        )

    def replay_rows(self):

        """
        Part 2 supplies the iterator.
        """

        raise NotImplementedError

    def replay_rows(self, csv_file: str | Path):

        csv_file=Path(csv_file)

        with csv_file.open(newline="",encoding="utf-8") as fp:

            rows=list(csv.DictReader(fp))

        if len(rows)<2:
            return

        previous_close=None

        for cycle,row in enumerate(rows[:-1],start=1):

            next_row=rows[cycle]

            next_close = float(
                next_row.get("close") or next_row.get("Close") or 0.0
            )

            start = max(0, cycle - 50)

            replay_window = rows[start:cycle]

            yield{

                "cycle":cycle,
                "row":row,
                "previous_close":previous_close,
                "next_close":next_close,
                "replay_bars":replay_window,
            }

            previous_close = float(
                row.get("close") or row.get("Close") or 0.0
            )


    def process_row(self,item:dict[str,Any])->dict[str,Any]:

        row=item["row"]

        symbol=row.get("symbol") or row.get("Symbol") or "UNKNOWN"

        strategy_result = generate_strategy_decision(
            symbol,
            replay_bars=item.get("replay_bars") or [],
        )

        decision = "HOLD"

        if isinstance(strategy_result, dict):

            signal = strategy_result.get("signal")

            if isinstance(signal, dict):

                decision = str(
                    signal.get("action") or
                    signal.get("decision") or
                    signal.get("signal") or
                    "HOLD"
                ).upper()

            elif isinstance(signal, str):

                decision = signal.upper()

        artifact = build_learning_artifact(

            run_id=self.manifest["run_id"],

            symbol=symbol,

            row=row,

            previous_close=item["previous_close"],

            next_close=item["next_close"],

            decision=decision,

            cycle=item["cycle"],

        )

        knowledge_object = (
            build_strategy_knowledge_object_from_learning_artifact(
                artifact
            )
        )

        graph = build_indicator_knowledge_graph(
            [knowledge_object]
        )

        artifact["knowledge_object"] = knowledge_object
        artifact["indicator_graph"] = graph

        decision_file = self.run_directory / "decision_ledger.jsonl"

        with decision_file.open("a", encoding="utf-8") as fp:

            fp.write(json.dumps({

                "timestamp": datetime.now(UTC).isoformat(),

                "cycle": item["cycle"],

                "symbol": symbol,

                "decision": artifact["decision"],

                "reward": artifact["reward"],

                "confidence": artifact["confidence"],

            }))
            fp.write("\n")

        cycle_file = self.run_directory / "cycle_ledger.jsonl"

        with cycle_file.open("a", encoding="utf-8") as fp:

            fp.write(json.dumps({

                "cycle": item["cycle"],

                "rows_processed": self.rows_processed + 1,

                "decisions": self.decisions + 1,

            }))
            fp.write("\n")

        equity = float(artifact.get("reward") or 0.0)

        with (self.run_directory / "equity_curve.csv").open(
            "a",
            encoding="utf-8",
        ) as fp:

            fp.write(
                f'{item["cycle"]},{equity},0,{equity},0,0,0\n'
            )


        training_health = {

            "timestamp": datetime.now(UTC).isoformat(),

            "current_cycle": self.current_cycle,

            "rows_processed": self.rows_processed,

            "decisions": self.decisions,

            "errors": self.errors,

            "engine_enabled": ENGINE_ENABLED,

        }

        (self.run_directory / "training_health.json").write_text(
            json.dumps(training_health, indent=2),
            encoding="utf-8",
        )

        performance = {

            "rows_processed": self.rows_processed,

            "decisions": self.decisions,

            "reward": artifact.get("reward"),

            "confidence": artifact.get("confidence"),

        }

        (self.run_directory / "performance_metrics.json").write_text(
            json.dumps(performance, indent=2),
            encoding="utf-8",
        )

        confidence = {

            "last_confidence": artifact.get("confidence"),

            "last_reward": artifact.get("reward"),

            "cycle": item["cycle"],

        }

        (self.run_directory / "confidence_calibration.json").write_text(
            json.dumps(confidence, indent=2),
            encoding="utf-8",
        )

        self.write_heartbeat()

        if self.current_cycle % 100 == 0:
            self.write_checkpoint()


        self.current_cycle=item["cycle"]

        self.rows_processed+=1

        self.decisions+=1

        return artifact


    def execute(self, csv_file: str | Path):

        artifact_count = 0

        for item in self.replay_rows(csv_file):

            try:

                self.process_row(item)

                artifact_count += 1

            except Exception as exc:

                self.errors += 1

                import traceback

                print("\n================ REPLAY ERROR ================")
                print("cycle:", item.get("cycle"))
                traceback.print_exc()
                print("=============================================\n")

                raise

        self.write_checkpoint()
        self.write_heartbeat()

        summary = {

            "run_id": self.manifest["run_id"],

            "artifacts_generated": artifact_count,

            "rows_processed": self.rows_processed,

            "decisions": self.decisions,

            "errors": self.errors,

            "completed_at": datetime.now(UTC).isoformat(),

        }

        (self.run_directory / "replay_summary.json").write_text(
            json.dumps(summary, indent=2),
            encoding="utf-8",
        )

        return summary


def engine_status():

    return ReplayExecutionEngine
