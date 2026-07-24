#!/usr/bin/env python3

"""
==========================================================
PHASE 135

NEUROVEST BLIND PRODUCTION READINESS AUDIT

Stages 1-6
Discovery and graph analysis

Stage 7
Fintech Capability Grader

Stage 8
AI Capability Grader

Stage 9
Production Readiness Grader

Stage 10
Production Blocker Grader

Stage 11
Final Audit Report and Prioritized Remediation Plan

Read-only static repository inspection.

Application code is not executed.

Deployment is not approved.

Live trading is not approved.

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

from scripts.phase135.core.audit_engine import AuditEngine
from scripts.phase135.report.final_report import FinalAuditReportBuilder
from scripts.phase135.report.renderer import render_repository_discovery


AUDIT_DIRECTORY = ROOT / "runtime" / "audits"
HISTORY_DIRECTORY = AUDIT_DIRECTORY / "history"
LATEST_REPORT = AUDIT_DIRECTORY / "latest.json"
FINAL_REPORT_JSON = AUDIT_DIRECTORY / "final_report_latest.json"
FINAL_REPORT_TEXT = AUDIT_DIRECTORY / "final_report_latest.txt"


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
        report = AuditEngine(
            ROOT
        ).run_repository_discovery()

        timestamp = datetime.now(UTC).strftime(
            "%Y%m%dT%H%M%S.%fZ"
        )

        history_report = (
            HISTORY_DIRECTORY
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

        final_report = report["final_report"]

        write_json_atomic(
            FINAL_REPORT_JSON,
            final_report,
        )

        final_text = FinalAuditReportBuilder(
            report
        ).render_text(
            final_report
        )

        FINAL_REPORT_TEXT.write_text(
            final_text + "\n",
            encoding="utf-8",
        )

        print(
            render_repository_discovery(
                report
            )
        )

        print()
        print(final_text)

        return 0

    except KeyboardInterrupt:
        print()
        print("Phase 135 audit interrupted.")
        return 130

    except Exception as exc:
        print("=" * 80)
        print("PHASE 135 AUDIT FAILED")
        print("=" * 80)
        print()
        print(
            f"{type(exc).__name__}: {exc}"
        )
        print()
        print(
            "No deployment or live-trading approval was generated."
        )
        print("=" * 80)

        return 1


if __name__ == "__main__":
    raise SystemExit(main())
