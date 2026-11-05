
"""Read-only explanation of NeuroVest's persisted developer scan journal.

Internal CLI only. No HTTP routes, source mutation, or patch execution.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def hypothesis_for(kind):
    """Return a bounded, falsifiable hypothesis, not a verified fact."""
    if kind == "branch_complexity":
        return (
            "Separating one independent decision-making responsibility "
            "into a private helper may reduce the target function's "
            "estimated branch complexity without changing its outputs.",
            "Compare static complexity before and after, run focused "
            "regressions, and compare representative output cases.",
            "Branches may behave differently after extraction.",
        )

    if kind == "large_function":
        return (
            "Extracting an independent responsibility may reduce the "
            "target function's length and make it easier to test.",
            "Measure function length and run before/after behavior "
            "comparisons on representative inputs.",
            "Moving code may change dependencies or side effects.",
        )

    if kind == "missing_docstring":
        return (
            "Documenting the function's actual contract may make "
            "future maintenance and reviews easier.",
            "Confirm only the function docstring changes, check "
            "its accuracy, and run the focused tests.",
            "An inaccurate docstring can mislead developers.",
        )

    return (
        "Investigating this finding may reveal a narrowly scoped "
        "reliability or maintainability improvement.",
        "Identify a measurable expected outcome and write a "
        "focused regression test before modifying code.",
        "The finding may not indicate a real defect.",
    )


def summarize(runs, findings):
    """Explain persisted evidence without inventing test outcomes."""
    if not runs:
        return (
            "## Neuro Developer — Improvement Memory\n\n"
            "I don't have any completed journal runs to analyze yet. "
            "I cannot form an evidence-backed recommendation from "
            "missing history."
        )

    latest = runs[0]
    scan_id = latest["scan_id"]

    lines = [
        "## Neuro Developer — Improvement Memory",
        "",
        "I've consulted my persisted, read-only improvement journal.",
        "",
        "**Latest scan:** #" + str(scan_id),
        "**Scan status:** " + str(latest["status"]),
        "**Modules inspected:** "
        + str(latest["modules_scanned"]) + " / "
        + str(latest["modules_allowed"]),
        "**Findings in latest scan:** "
        + str(latest["findings_total"]),
        "**New in latest scan:** "
        + str(latest["findings_new"]),
        "**Previously recorded in latest scan:** "
        + str(latest["findings_existing"]),
        "**Journal runs examined:** " + str(len(runs)),
        "",
        "### What I've learned",
        "",
    ]

    active = [
        f for f in findings
        if f["last_scan_id"] == scan_id
    ]

    older = [
        f for f in findings
        if f["last_scan_id"] != scan_id
    ]

    if active:
        for number, finding in enumerate(active[:4], 1):
            lines.extend([
                str(number) + ". **"
                + finding["module_name"] + " / "
                + finding["function_name"] + "** — "
                + finding["finding_kind"]
                + " (" + finding["priority"] + ")",
                "   - Evidence: " + finding["evidence"],
                "   - Observed in "
                + str(finding["seen_count"])
                + " committed scan(s)",
                "   - Suggested action: "
                + finding["recommendation"],
                "",
            ])
    else:
        lines.append(
            "The latest scan has no recorded active findings."
        )

    lines.extend([
        "### Recurring issues",
        "",
    ])

    recurring = [
        f for f in active if f["seen_count"] >= 2
    ]

    if recurring:
        for finding in recurring[:4]:
            lines.append(
                "- " + finding["module_name"] + " / "
                + finding["function_name"] + ": "
                + finding["finding_kind"] + " ("
                + str(finding["seen_count"]) + " scans)"
            )
    else:
        lines.append(
            "No active issue has been observed in multiple "
            "committed scans yet."
        )

    if older:
        lines.extend([
            "",
            "**Historical note:** "
            + str(len(older))
            + " recorded finding(s) were not observed in "
            "the latest committed scan. This alone does not "
            "prove they were fixed.",
        ])

    lines.extend([
        "",
        "### My highest-priority hypothesis",
        "",
    ])

    if active:
        top = active[0]
        prediction, verification, risk = hypothesis_for(
            top["finding_kind"]
        )

        lines.extend([
            "**Target:** `" + top["module_name"] + " / "
            + top["function_name"] + "`",
            "",
            "**Observation:** " + top["evidence"],
            "",
            "**Hypothesis:** " + prediction,
            "",
            "**Where:** The existing allowlisted source module "
            "containing that function.",
            "",
            "**Proposed experiment:** " + verification,
            "",
            "**Potential risk:** " + risk,
            "",
            "**Current evidence:** Static observations only. "
            "The proposed experiment has not been executed.",
        ])
    else:
        lines.append(
            "I have no current finding to support a new "
            "improvement hypothesis."
        )

    lines.extend([
        "",
        "### What happens next",
        "",
        "I recommend reviewing the target, preparing an isolated "
        "candidate, and testing it against the current version. "
        "Any code proposal must pass the existing validators "
        "and receive explicit developer approval.",
        "",
        "**Available next decisions:**",
        "",
        "1. Mock up the proposed improvement and test it.",
        "2. Revise the hypothesis or proposed change.",
        "3. Review the validated patch for explicit approval.",
        "",
        "These are suggested next steps, not automatically "
        "executed actions.",
        "",
        "**Safety:** No code changed, no patch applied, "
        "no trading action performed. This report reflects "
        "stored observations rather than a new full-repository scan.",
    ])

    if latest["status"] != "complete":
        lines.extend([
            "",
            "**Warning:** The latest scan was partial; "
            "missing observations must not be treated "
            "as resolved issues.",
        ])

    return "\n".join(lines)


async def read_history():
    """Read bounded journal rows from PostgreSQL."""
    from backend.app.stacks.db_runtime.database import engine

    async with engine.connect() as connection:
        transaction = await connection.begin()
        try:
            await connection.execute(
                text("SET TRANSACTION READ ONLY")
            )

            runs_result = await connection.execute(text("""
                SELECT scan_id, status, modules_scanned,
                       modules_allowed, findings_total,
                       findings_new, findings_existing
                FROM neuro_developer_improvement_runs_v1
                ORDER BY scan_id DESC
                LIMIT 5
            """))

            findings_result = await connection.execute(text("""
                SELECT module_name, function_name,
                       finding_kind, priority, evidence,
                       recommendation, seen_count, last_scan_id
                FROM neuro_developer_improvement_findings_v1
                ORDER BY
                    CASE priority
                        WHEN 'P0' THEN 0
                        WHEN 'P1' THEN 1
                        WHEN 'P2' THEN 2
                        ELSE 3
                    END,
                    seen_count DESC,
                    module_name, function_name, finding_kind
                LIMIT 80
            """))

            runs = [
                dict(row)
                for row in runs_result.mappings().all()
            ]
            findings = [
                dict(row)
                for row in findings_result.mappings().all()
            ]

            await transaction.commit()
            return runs, findings

        except Exception:
            await transaction.rollback()
            raise


def main():
    try:
        runs, findings = asyncio.run(read_history())
        print(summarize(runs, findings))
        return 0
    except Exception as exc:
        print(
            "Improvement journal unavailable ("
            + type(exc).__name__
            + "). No source code was modified."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
