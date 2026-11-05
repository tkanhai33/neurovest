
"""Bounded, read-only NeuroVest developer improvement journal.

Scans only the existing self-review allowlist.
Does not generate patches, modify source, or expose HTTP routes.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SCHEMA = "neuro_improvement_v1"


def observation_key(module, function, kind):
    payload = json.dumps(
        [module, function, kind],
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def normalize_finding(module, finding, sha256):
    if not isinstance(finding, dict):
        return None

    function = str(
        finding.get("function")
        or finding.get("function_name")
        or finding.get("name")
        or "module"
    )[:160]

    kind = str(
        finding.get("type")
        or finding.get("kind")
        or finding.get("category")
        or "static_finding"
    )[:100]

    priority = str(
        finding.get("priority")
        or finding.get("severity")
        or "P3"
    ).upper()

    if priority not in ("P0", "P1", "P2", "P3"):
        priority = "P3"

    evidence = str(
        finding.get("evidence")
        or finding.get("detail")
        or finding.get("description")
        or "Static finding"
    )[:1000]

    recommendation = str(
        finding.get("recommendation")
        or finding.get("suggestion")
        or "Inspect and test the affected function"
    )[:1000]

    return {
        "finding_id": observation_key(module, function, kind),
        "module": module,
        "function": function,
        "kind": kind,
        "priority": priority,
        "evidence": evidence,
        "recommendation": recommendation,
        "source_sha256": sha256,
    }


def collect_findings():
    """Collect static evidence without running inspected modules."""
    from backend.app.stacks.chat_public.developer_self_review import (
        ALLOWED_MODULES,
        inventory_module,
    )

    results = []
    modules = []
    errors = []

    for module in sorted(ALLOWED_MODULES):
        try:
            report = inventory_module(module)
        except (ValueError, OSError, SyntaxError) as exc:
            errors.append(
                {
                    "module": module,
                    "error": type(exc).__name__,
                }
            )
            continue

        modules.append(module)
        sha256 = str(report.get("sha256") or "")

        if len(sha256) != 64:
            errors.append({
                "module": module,
                "error": "InvalidSourceHash",
            })
            modules.pop()
            continue

        for finding in report.get("findings", []):
            normalized = normalize_finding(
                module,
                finding,
                sha256,
            )
            if normalized:
                results.append(normalized)

    # Deduplicate repeated static findings in one scan.
    unique = {
        item["finding_id"]: item
        for item in results
    }

    return {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "modules": modules,
        "errors": errors,
        "findings": sorted(
            unique.values(),
            key=lambda item: (
                item["priority"],
                item["module"],
                item["function"],
                item["kind"],
            ),
        ),
        "allowed_count": len(ALLOWED_MODULES),
    }


CREATE_RUNS = """
CREATE TABLE IF NOT EXISTS neuro_developer_improvement_runs_v1 (
    scan_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modules_scanned INTEGER NOT NULL,
    modules_allowed INTEGER NOT NULL,
    findings_total INTEGER NOT NULL,
    findings_new INTEGER NOT NULL,
    findings_existing INTEGER NOT NULL,
    errors_json TEXT NOT NULL,
    status TEXT NOT NULL
)
"""

CREATE_FINDINGS = """
CREATE TABLE IF NOT EXISTS neuro_developer_improvement_findings_v1 (
    finding_id VARCHAR(64) PRIMARY KEY,
    module_name TEXT NOT NULL,
    function_name TEXT NOT NULL,
    finding_kind TEXT NOT NULL,
    priority VARCHAR(2) NOT NULL,
    evidence TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    source_sha256 VARCHAR(64) NOT NULL,
    first_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    seen_count INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'observed',
    last_scan_id BIGINT NOT NULL
)
"""


async def persist_scan(report):
    """Commit one bounded scan to the existing PostgreSQL engine."""
    from backend.app.stacks.db_runtime.database import engine

    async with engine.begin() as connection:
        # Prevent concurrent copies from writing overlapping scans.
        locked = (
            await connection.execute(
                text(
                    "SELECT pg_try_advisory_xact_lock("
                    "684209153, 1012)"
                )
            )
        ).scalar()

        if not locked:
            raise RuntimeError(
                "Another improvement journal scan is running."
            )


        keys = [f["finding_id"] for f in report["findings"]]
        existing = set()

        if keys:
            rows = await connection.execute(
                text("""
                    SELECT finding_id
                    FROM neuro_developer_improvement_findings_v1
                    WHERE finding_id = ANY(:keys)
                """),
                {"keys": keys},
            )
            existing = {row[0] for row in rows}

        new_count = sum(
            f["finding_id"] not in existing
            for f in report["findings"]
        )

        status = (
            "complete"
            if not report["errors"]
            else "partial"
        )

        row = await connection.execute(
            text("""
                INSERT INTO neuro_developer_improvement_runs_v1
                    (
                        modules_scanned,
                        modules_allowed,
                        findings_total,
                        findings_new,
                        findings_existing,
                        errors_json,
                        status
                    )
                VALUES
                    (
                        :modules_scanned,
                        :modules_allowed,
                        :findings_total,
                        :findings_new,
                        :findings_existing,
                        :errors_json,
                        :status
                    )
                RETURNING scan_id
            """),
            {
                "modules_scanned": len(report["modules"]),
                "modules_allowed": report["allowed_count"],
                "findings_total": len(report["findings"]),
                "findings_new": new_count,
                "findings_existing": (
                    len(report["findings"]) - new_count
                ),
                "errors_json": json.dumps(report["errors"]),
                "status": status,
            },
        )

        scan_id = row.scalar_one()

        for finding in report["findings"]:
            await connection.execute(
                text("""
                    INSERT INTO neuro_developer_improvement_findings_v1
                    (
                        finding_id, module_name, function_name,
                        finding_kind, priority, evidence,
                        recommendation, source_sha256, last_scan_id
                    )
                    VALUES
                    (
                        :finding_id, :module, :function,
                        :kind, :priority, :evidence,
                        :recommendation, :source_sha256, :scan_id
                    )
                    ON CONFLICT (finding_id)
                    DO UPDATE SET
                        priority = EXCLUDED.priority,
                        evidence = EXCLUDED.evidence,
                        recommendation = EXCLUDED.recommendation,
                        source_sha256 = EXCLUDED.source_sha256,
                        last_seen = NOW(),
                        seen_count =
                            neuro_developer_improvement_findings_v1.seen_count
                            + 1,
                        last_scan_id = EXCLUDED.last_scan_id
                """),
                {**finding, "scan_id": scan_id},
            )

    return {
        "scan_id": scan_id,
        "status": status,
        "new": new_count,
        "existing": len(report["findings"]) - new_count,
    }


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--scan", action="store_true")
    args = parser.parse_args()

    report = collect_findings()

    print("=" * 64)
    print("NEURO — AUTONOMOUS IMPROVEMENT JOURNAL")
    print("=" * 64)
    print("MODE=", "DRY_RUN" if args.dry_run else "PERSIST")
    print("MODULES=", len(report["modules"]), "/", report["allowed_count"])
    print("FINDINGS=", len(report["findings"]))
    print("SCAN_ERRORS=", len(report["errors"]))

    for finding in report["findings"][:6]:
        print(
            "FINDING=",
            finding["priority"],
            finding["module"],
            finding["function"],
            finding["kind"],
        )

    for error in report["errors"]:
        print("SCAN_ERROR=", error)

    if not report["modules"]:
        print("SCAN_BLOCKED=NO_MODULES_INSPECTED")
        return 1

    if args.dry_run:
        print("DATABASE_MODIFIED=False")
        print("SOURCE_MODIFIED=False")
        return 0

    result = asyncio.run(persist_scan(report))

    print("SCAN_ID=", result["scan_id"])
    print("SCAN_STATUS=", result["status"])
    print("NEW_FINDINGS=", result["new"])
    print("RECURRING_FINDINGS=", result["existing"])
    print("DATABASE_JOURNAL=COMMITTED")
    print("SOURCE_MODIFIED=False")
    print("PATCH_APPLIED=False")

    return 0 if result["status"] == "complete" else 2


if __name__ == "__main__":
    sys.exit(main())
