#!/usr/bin/env python3

"""
==========================================================
PHASE 136
NEUROVEST INFRASTRUCTURE QUALIFICATION

Stage 1
Hardware and Platform Discovery

Stage 2
Thermal Qualification

Stage 2 performs a controlled CPU load with an automatic
temperature-abort threshold.

No NeuroVest application execution.
No system configuration modification.
No deployment approval.
No live-trading approval.

==========================================================
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT),
    )

from scripts.phase136.core.qualification_engine import (
    QualificationEngine,
)
from scripts.phase136.report.renderer import (
    render_qualification,
)


AUDIT_DIRECTORY = (
    ROOT
    / "runtime"
    / "infrastructure_audits"
)

HISTORY_DIRECTORY = (
    AUDIT_DIRECTORY
    / "history"
)

THERMAL_DIRECTORY = (
    AUDIT_DIRECTORY
    / "thermal"
)

THERMAL_HISTORY_DIRECTORY = (
    HISTORY_DIRECTORY
    / "thermal"
)

LATEST_REPORT = (
    AUDIT_DIRECTORY
    / "latest.json"
)

LATEST_THERMAL_REPORT = (
    THERMAL_DIRECTORY
    / "latest.json"
)


def write_json_atomic(
    destination: Path,
    payload: dict,
) -> None:
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = destination.with_suffix(
        destination.suffix + ".tmp"
    )

    temporary.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    temporary.replace(destination)


def main() -> int:
    try:
        report = QualificationEngine(
            ROOT
        ).run_stage_2()

        timestamp = datetime.now(UTC).strftime(
            "%Y%m%dT%H%M%S.%fZ"
        )

        history_report = (
            HISTORY_DIRECTORY
            / f"{timestamp}.json"
        )

        thermal_history_report = (
            THERMAL_HISTORY_DIRECTORY
            / f"{timestamp}.json"
        )

        write_json_atomic(
            LATEST_REPORT,
            report,
        )

        write_json_atomic(
            history_report,
            report,
        )

        write_json_atomic(
            LATEST_THERMAL_REPORT,
            report["thermal_qualification"],
        )

        write_json_atomic(
            thermal_history_report,
            report["thermal_qualification"],
        )

        print(
            render_qualification(
                report
            )
        )

        return 0

    except KeyboardInterrupt:
        print()
        print(
            "Phase 136 thermal qualification interrupted."
        )

        return 130

    except Exception as exc:
        print("=" * 80)
        print("PHASE 136 STAGE 2 FAILED")
        print("=" * 80)
        print()
        print(
            f"{type(exc).__name__}: {exc}"
        )
        print()
        print("Deployment remains unapproved.")
        print("Live trading remains unapproved.")
        print("=" * 80)

        return 1


if __name__ == "__main__":
    raise SystemExit(main())
