#!/usr/bin/env python3

"""
==========================================================
PHASE 135
FREEZE VERIFICATION

Purpose

Freeze the completed Phase 135 audit system as a reproducible,
read-only L7 assurance baseline.

The freeze verifier:

- validates every required Phase 135 source file
- compiles every Phase 135 Python module
- runs the complete Phase 135 audit
- verifies all completed stages
- verifies read-only invariants
- verifies prior scores are preserved
- verifies final reports exist
- hashes every Phase 135 source file
- proves audit source files were not modified by execution
- creates a deterministic freeze manifest
- creates a human-readable freeze report

The freeze verifier does not:

- execute NeuroVest application entrypoints
- start FastAPI
- start Next.js
- connect to a database
- connect to Ollama
- connect to SnapTrade
- connect to Wealthsimple
- modify NeuroVest application code
- approve deployment
- approve live trading

==========================================================
"""

from __future__ import annotations

import hashlib
import json
import os
import py_compile
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

PHASE_DIRECTORY = ROOT / "scripts" / "phase135"
AUDIT_DIRECTORY = ROOT / "runtime" / "audits"
HISTORY_DIRECTORY = AUDIT_DIRECTORY / "history"

LATEST_AUDIT = AUDIT_DIRECTORY / "latest.json"
FINAL_REPORT_JSON = AUDIT_DIRECTORY / "final_report_latest.json"
FINAL_REPORT_TEXT = AUDIT_DIRECTORY / "final_report_latest.txt"

FREEZE_MANIFEST = (
    AUDIT_DIRECTORY
    / "phase135_freeze_manifest_latest.json"
)

FREEZE_REPORT = (
    AUDIT_DIRECTORY
    / "phase135_freeze_report_latest.txt"
)

FREEZE_HISTORY_DIRECTORY = (
    HISTORY_DIRECTORY
    / "phase135_freeze"
)

FREEZE_VERSION = "phase135-stage12-v1"

EXPECTED_COMPLETED_STAGES = [
    "repository_discovery",
    "layer_mapping",
    "dependency_mapping",
    "import_graph_normalization",
    "runtime_graph_discovery",
    "contract_discovery",
    "fintech_capability_grading",
    "ai_capability_grading",
    "production_readiness_grading",
    "production_blocker_grading",
    "final_audit_report",
]

REQUIRED_FILES = [
    "scripts/phase135/README.md",
    "scripts/phase135/__init__.py",
    "scripts/phase135/phase135_main.py",
    "scripts/phase135/phase135_freeze_verify.py",
    "scripts/phase135/core/__init__.py",
    "scripts/phase135/core/audit_engine.py",
    "scripts/phase135/discovery/__init__.py",
    "scripts/phase135/discovery/repository_scanner.py",
    "scripts/phase135/discovery/layer_mapper.py",
    "scripts/phase135/discovery/dependency_mapper.py",
    "scripts/phase135/discovery/contract_discovery.py",
    "scripts/phase135/graph/__init__.py",
    "scripts/phase135/graph/import_graph.py",
    "scripts/phase135/graph/runtime_graph.py",
    "scripts/phase135/grading/__init__.py",
    "scripts/phase135/grading/fintech_grader.py",
    "scripts/phase135/grading/ai_grader.py",
    "scripts/phase135/grading/production_grader.py",
    "scripts/phase135/grading/blocker_grader.py",
    "scripts/phase135/report/__init__.py",
    "scripts/phase135/report/renderer.py",
    "scripts/phase135/report/final_report.py",
    "scripts/phase135/utils/__init__.py",
    "scripts/phase135/utils/filesystem.py",
]

READ_ONLY_FALSE_INVARIANTS = [
    (
        "runtime_graph",
        "application_executed",
    ),
    (
        "contract_discovery",
        "application_executed",
    ),
    (
        "fintech_capability",
        "application_executed",
    ),
    (
        "fintech_capability",
        "repository_rescanned",
    ),
    (
        "fintech_capability",
        "architecture_assumed",
    ),
    (
        "fintech_capability",
        "production_readiness_assessed",
    ),
    (
        "fintech_capability",
        "production_blockers_assessed",
    ),
    (
        "ai_capability",
        "application_executed",
    ),
    (
        "ai_capability",
        "repository_rescanned",
    ),
    (
        "ai_capability",
        "architecture_assumed",
    ),
    (
        "ai_capability",
        "production_readiness_assessed",
    ),
    (
        "ai_capability",
        "production_blockers_assessed",
    ),
    (
        "production_readiness",
        "application_executed",
    ),
    (
        "production_readiness",
        "repository_rescanned",
    ),
    (
        "production_readiness",
        "architecture_assumed",
    ),
    (
        "production_readiness",
        "production_blockers_assessed",
    ),
    (
        "production_readiness",
        "deployment_approved",
    ),
    (
        "production_readiness",
        "live_trading_approved",
    ),
    (
        "production_blockers",
        "application_executed",
    ),
    (
        "production_blockers",
        "repository_rescanned",
    ),
    (
        "production_blockers",
        "architecture_assumed",
    ),
    (
        "production_blockers",
        "deployment_approved",
    ),
    (
        "production_blockers",
        "live_trading_approved",
    ),
    (
        "final_report",
        "application_executed",
    ),
    (
        "final_report",
        "repository_rescanned",
    ),
    (
        "final_report",
        "application_modified",
    ),
    (
        "final_report",
        "prior_scores_modified",
    ),
    (
        "final_report",
        "new_findings_created",
    ),
    (
        "final_report",
        "deployment_approved",
    ),
    (
        "final_report",
        "live_trading_approved",
    ),
]

SCORE_PATHS = {
    "fintech_capability_score": (
        "fintech_capability",
        "summary",
        "total_score",
    ),
    "fintech_capability_percentage": (
        "fintech_capability",
        "summary",
        "percentage",
    ),
    "ai_capability_score": (
        "ai_capability",
        "summary",
        "total_score",
    ),
    "ai_capability_percentage": (
        "ai_capability",
        "summary",
        "percentage",
    ),
    "production_readiness_score": (
        "production_readiness",
        "summary",
        "total_score",
    ),
    "production_readiness_percentage": (
        "production_readiness",
        "summary",
        "percentage",
    ),
}


class FreezeFailure(RuntimeError):
    """
    Raised when the Phase 135 freeze contract is violated.
    """


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


def write_json_atomic(
    destination: Path,
    payload: dict[str, Any],
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


def nested_get(
    payload: dict[str, Any],
    path: tuple[str, ...],
) -> Any:
    value: Any = payload

    for key in path:
        if not isinstance(value, dict):
            raise FreezeFailure(
                "Expected dictionary while resolving "
                + ".".join(path)
            )

        if key not in value:
            raise FreezeFailure(
                "Missing required path: "
                + ".".join(path)
            )

        value = value[key]

    return value


def required_file_paths() -> list[Path]:
    paths = []

    for relative in REQUIRED_FILES:
        path = ROOT / relative

        if not path.is_file():
            raise FreezeFailure(
                f"Required Phase 135 file missing: {relative}"
            )

        paths.append(path)

    return paths


def discover_phase_source_files() -> list[Path]:
    source_files = sorted(
        path
        for path in PHASE_DIRECTORY.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix in {
            ".py",
            ".md",
        }
    )

    if not source_files:
        raise FreezeFailure(
            "No Phase 135 source files discovered."
        )

    return source_files


def hash_inventory(
    paths: list[Path],
) -> dict[str, dict[str, Any]]:
    inventory = {}

    for path in paths:
        relative = path.relative_to(ROOT).as_posix()

        inventory[relative] = {
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        }

    return dict(
        sorted(inventory.items())
    )


def compile_phase_sources(
    paths: list[Path],
) -> list[str]:
    compiled = []

    for path in paths:
        if path.suffix != ".py":
            continue

        try:
            py_compile.compile(
                str(path),
                doraise=True,
            )
        except py_compile.PyCompileError as exc:
            raise FreezeFailure(
                f"Python compilation failed for "
                f"{path.relative_to(ROOT)}: {exc}"
            ) from exc

        compiled.append(
            path.relative_to(ROOT).as_posix()
        )

    return sorted(compiled)


def run_phase135_audit() -> dict[str, Any]:
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(ROOT)

    command = [
        sys.executable,
        str(
            ROOT
            / "scripts"
            / "phase135"
            / "phase135_main.py"
        ),
    ]

    result = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=300,
    )

    if result.returncode != 0:
        raise FreezeFailure(
            "Phase 135 audit execution failed.\n"
            f"Return code: {result.returncode}\n"
            f"STDOUT:\n{result.stdout[-10000:]}\n"
            f"STDERR:\n{result.stderr[-10000:]}"
        )

    if not LATEST_AUDIT.is_file():
        raise FreezeFailure(
            "Phase 135 audit did not produce latest.json."
        )

    payload = json.loads(
        LATEST_AUDIT.read_text(
            encoding="utf-8"
        )
    )

    return {
        "payload": payload,
        "stdout_tail": result.stdout[-10000:],
        "stderr_tail": result.stderr[-10000:],
        "returncode": result.returncode,
    }


def validate_stage_contract(
    payload: dict[str, Any],
) -> dict[str, Any]:
    if payload.get("phase") != 135:
        raise FreezeFailure(
            "Audit phase is not 135."
        )

    if payload.get("audit_mode") != "read_only":
        raise FreezeFailure(
            "Audit mode is not read_only."
        )

    if payload.get("status") != "completed":
        raise FreezeFailure(
            "Audit status is not completed."
        )

    completed_stages = payload.get(
        "completed_stages"
    )

    if completed_stages != EXPECTED_COMPLETED_STAGES:
        raise FreezeFailure(
            "Completed stage sequence changed.\n"
            f"Expected: {EXPECTED_COMPLETED_STAGES}\n"
            f"Actual:   {completed_stages}"
        )

    grading = payload.get("grading", {})

    if grading.get("status") != "completed":
        raise FreezeFailure(
            "Grading status is not completed."
        )

    if grading.get(
        "pending_grading_stages"
    ) != []:
        raise FreezeFailure(
            "Pending grading stages remain."
        )

    if grading.get(
        "deployment_approved"
    ) is not False:
        raise FreezeFailure(
            "Deployment approval invariant violated."
        )

    if grading.get(
        "live_trading_approved"
    ) is not False:
        raise FreezeFailure(
            "Live-trading approval invariant violated."
        )

    return {
        "phase": payload["phase"],
        "audit_mode": payload["audit_mode"],
        "status": payload["status"],
        "completed_stages": completed_stages,
        "grading_status": grading["status"],
        "pending_grading_stages": grading[
            "pending_grading_stages"
        ],
        "deployment_approved": grading[
            "deployment_approved"
        ],
        "live_trading_approved": grading[
            "live_trading_approved"
        ],
    }


def validate_false_invariants(
    payload: dict[str, Any],
) -> list[str]:
    verified = []

    for section, key in READ_ONLY_FALSE_INVARIANTS:
        section_payload = payload.get(section)

        if not isinstance(section_payload, dict):
            raise FreezeFailure(
                f"Missing invariant section: {section}"
            )

        if section_payload.get(key) is not False:
            raise FreezeFailure(
                f"False invariant violated: "
                f"{section}.{key}"
            )

        verified.append(
            f"{section}.{key}=false"
        )

    return verified


def validate_scores(
    payload: dict[str, Any],
) -> dict[str, Any]:
    scores = {}

    for name, path in SCORE_PATHS.items():
        value = nested_get(
            payload,
            path,
        )

        if not isinstance(
            value,
            (int, float),
        ):
            raise FreezeFailure(
                f"Score is not numeric: {name}"
            )

        scores[name] = value

    if scores[
        "fintech_capability_score"
    ] != 900.0:
        raise FreezeFailure(
            "Fintech capability baseline changed."
        )

    if scores[
        "fintech_capability_percentage"
    ] != 81.82:
        raise FreezeFailure(
            "Fintech capability percentage changed."
        )

    if scores[
        "ai_capability_score"
    ] != 840.0:
        raise FreezeFailure(
            "AI capability baseline changed."
        )

    if scores[
        "ai_capability_percentage"
    ] != 70.0:
        raise FreezeFailure(
            "AI capability percentage changed."
        )

    if scores[
        "production_readiness_score"
    ] != 540.0:
        raise FreezeFailure(
            "Production-readiness baseline changed."
        )

    if scores[
        "production_readiness_percentage"
    ] != 45.0:
        raise FreezeFailure(
            "Production-readiness percentage changed."
        )

    return scores


def validate_final_report(
    payload: dict[str, Any],
) -> dict[str, Any]:
    if not FINAL_REPORT_JSON.is_file():
        raise FreezeFailure(
            "Final JSON report is missing."
        )

    if not FINAL_REPORT_TEXT.is_file():
        raise FreezeFailure(
            "Final text report is missing."
        )

    final_report = payload.get(
        "final_report"
    )

    if not isinstance(final_report, dict):
        raise FreezeFailure(
            "Embedded final report is missing."
        )

    disk_report = json.loads(
        FINAL_REPORT_JSON.read_text(
            encoding="utf-8"
        )
    )

    if final_report != disk_report:
        raise FreezeFailure(
            "Embedded and standalone final reports differ."
        )

    if final_report.get(
        "report_type"
    ) != (
        "final_audit_and_prioritized_remediation_plan"
    ):
        raise FreezeFailure(
            "Final report type changed."
        )

    if final_report.get(
        "raw_finding_count"
    ) != 43:
        raise FreezeFailure(
            "Raw finding baseline changed."
        )

    if final_report.get(
        "root_workstream_count"
    ) != 15:
        raise FreezeFailure(
            "Root workstream baseline changed."
        )

    if final_report.get(
        "duplicate_reduction"
    ) != 28:
        raise FreezeFailure(
            "Duplicate reduction baseline changed."
        )

    orders = [
        item.get("order")
        for item in final_report.get(
            "root_workstreams",
            [],
        )
    ]

    if orders != list(
        range(
            1,
            len(orders) + 1,
        )
    ):
        raise FreezeFailure(
            "Root workstream order is not contiguous."
        )

    text = FINAL_REPORT_TEXT.read_text(
        encoding="utf-8"
    )

    required_text_markers = [
        (
            "FINAL AUDIT REPORT AND "
            "PRIORITIZED REMEDIATION PLAN"
        ),
        "Deployment approved: NO",
        "Live trading approved: NO",
    ]

    for marker in required_text_markers:
        if marker not in text:
            raise FreezeFailure(
                f"Final text report marker missing: {marker}"
            )

    return {
        "report_type": final_report[
            "report_type"
        ],
        "raw_finding_count": final_report[
            "raw_finding_count"
        ],
        "root_workstream_count": final_report[
            "root_workstream_count"
        ],
        "duplicate_reduction": final_report[
            "duplicate_reduction"
        ],
        "json_sha256": sha256_file(
            FINAL_REPORT_JSON
        ),
        "text_sha256": sha256_file(
            FINAL_REPORT_TEXT
        ),
    }


def validate_blocker_report(
    payload: dict[str, Any],
) -> dict[str, Any]:
    blockers = payload.get(
        "production_blockers"
    )

    if not isinstance(blockers, dict):
        raise FreezeFailure(
            "Production blocker report missing."
        )

    summary = blockers.get(
        "summary",
        {}
    )

    expected = {
        "finding_count": 43,
        "critical_blockers": 8,
        "high_blockers": 18,
        "deferred_integrations": 7,
        "maturity_gaps": 10,
        "informational_findings": 0,
        "overall_status": "BLOCKED_CRITICAL",
    }

    for key, expected_value in expected.items():
        actual = summary.get(key)

        if actual != expected_value:
            raise FreezeFailure(
                f"Blocker baseline changed for {key}: "
                f"expected {expected_value!r}, "
                f"actual {actual!r}"
            )

    eligibility = blockers.get(
        "eligibility",
        {},
    )

    for mode in [
        "paper_mode",
        "authenticated_broker_integration",
        "live_trading",
    ]:
        mode_payload = eligibility.get(mode)

        if not isinstance(mode_payload, dict):
            raise FreezeFailure(
                f"Eligibility mode missing: {mode}"
            )

        if mode_payload.get(
            "approved"
        ) is not False:
            raise FreezeFailure(
                f"Mode approval invariant violated: {mode}"
            )

    return {
        **expected,
        "paper_mode_eligible": eligibility[
            "paper_mode"
        ]["eligible"],
        "broker_integration_eligible": eligibility[
            "authenticated_broker_integration"
        ]["eligible"],
        "live_trading_eligible": eligibility[
            "live_trading"
        ]["eligible"],
    }


def render_freeze_report(
    manifest: dict[str, Any],
) -> str:
    lines = []

    lines.append("=" * 80)
    lines.append("PHASE 135")
    lines.append("FREEZE VERIFICATION REPORT")
    lines.append("=" * 80)
    lines.append("")
    lines.append("FREEZE")
    lines.append(
        f"Version:                    "
        f"{manifest['freeze_version']}"
    )
    lines.append(
        f"Status:                     "
        f"{manifest['freeze_status']}"
    )
    lines.append(
        f"Verified at:                "
        f"{manifest['verified_at']}"
    )
    lines.append("")
    lines.append("SOURCE INTEGRITY")
    lines.append(
        f"Files frozen:               "
        f"{manifest['source_integrity']['file_count']}"
    )
    lines.append(
        f"Python files compiled:      "
        f"{manifest['source_integrity']['compiled_python_files']}"
    )
    lines.append(
        f"Source mutations detected:  "
        f"{manifest['source_integrity']['mutation_count']}"
    )
    lines.append("")
    lines.append("AUDIT CONTRACT")
    lines.append(
        f"Audit mode:                 "
        f"{manifest['audit_contract']['audit_mode']}"
    )
    lines.append(
        f"Completed stages:           "
        f"{len(manifest['audit_contract']['completed_stages'])}"
    )
    lines.append(
        f"False invariants verified:  "
        f"{len(manifest['false_invariants'])}"
    )
    lines.append("")
    lines.append("BASELINE SCORES")
    lines.append(
        f"Fintech capability:         "
        f"{manifest['scores']['fintech_capability_percentage']}%"
    )
    lines.append(
        f"AI capability:              "
        f"{manifest['scores']['ai_capability_percentage']}%"
    )
    lines.append(
        f"Production readiness:       "
        f"{manifest['scores']['production_readiness_percentage']}%"
    )
    lines.append("")
    lines.append("FINAL REPORT")
    lines.append(
        f"Raw findings:               "
        f"{manifest['final_report']['raw_finding_count']}"
    )
    lines.append(
        f"Root workstreams:           "
        f"{manifest['final_report']['root_workstream_count']}"
    )
    lines.append(
        f"Duplicates consolidated:    "
        f"{manifest['final_report']['duplicate_reduction']}"
    )
    lines.append("")
    lines.append("BLOCKER BASELINE")
    lines.append(
        f"Critical blockers:          "
        f"{manifest['blocker_report']['critical_blockers']}"
    )
    lines.append(
        f"High blockers:              "
        f"{manifest['blocker_report']['high_blockers']}"
    )
    lines.append(
        f"Deferred integrations:      "
        f"{manifest['blocker_report']['deferred_integrations']}"
    )
    lines.append(
        f"Maturity gaps:              "
        f"{manifest['blocker_report']['maturity_gaps']}"
    )
    lines.append("")
    lines.append("APPROVAL")
    lines.append("Deployment approved:        NO")
    lines.append("Live trading approved:      NO")
    lines.append("")
    lines.append("RESULT")
    lines.append(
        "Phase 135 is frozen as the read-only L7 audit baseline."
    )
    lines.append(
        "Future remediation must be measured against this manifest."
    )
    lines.append("")
    lines.append("=" * 80)

    return "\n".join(lines)


def main() -> int:
    started_at = datetime.now(UTC)

    try:
        required_file_paths()

        phase_sources = discover_phase_source_files()

        before_inventory = hash_inventory(
            phase_sources
        )

        compiled_files = compile_phase_sources(
            phase_sources
        )

        run_result = run_phase135_audit()
        payload = run_result["payload"]

        after_inventory = hash_inventory(
            phase_sources
        )

        changed_files = sorted(
            path
            for path in before_inventory
            if (
                before_inventory[path]
                != after_inventory.get(path)
            )
        )

        if changed_files:
            raise FreezeFailure(
                "Phase 135 source files changed during execution:\n"
                + "\n".join(changed_files)
            )

        audit_contract = validate_stage_contract(
            payload
        )

        false_invariants = validate_false_invariants(
            payload
        )

        scores = validate_scores(
            payload
        )

        final_report = validate_final_report(
            payload
        )

        blocker_report = validate_blocker_report(
            payload
        )

        completed_at = datetime.now(UTC)
        timestamp = completed_at.strftime(
            "%Y%m%dT%H%M%S.%fZ"
        )

        manifest = {
            "phase": 135,
            "freeze_version": FREEZE_VERSION,
            "freeze_status": "FROZEN_VERIFIED",
            "verification_mode": "read_only_l7_baseline",
            "started_at": started_at.isoformat(),
            "verified_at": completed_at.isoformat(),
            "duration_seconds": round(
                (
                    completed_at
                    - started_at
                ).total_seconds(),
                6,
            ),
            "repository_root": str(ROOT),
            "application_executed": False,
            "application_modified": False,
            "deployment_approved": False,
            "live_trading_approved": False,
            "source_integrity": {
                "file_count": len(
                    after_inventory
                ),
                "compiled_python_files": len(
                    compiled_files
                ),
                "mutation_count": len(
                    changed_files
                ),
                "changed_files": changed_files,
                "files": after_inventory,
            },
            "audit_contract": audit_contract,
            "false_invariants": false_invariants,
            "scores": scores,
            "final_report": final_report,
            "blocker_report": blocker_report,
            "audit_execution": {
                "returncode": run_result[
                    "returncode"
                ],
                "stderr_empty": (
                    not run_result[
                        "stderr_tail"
                    ].strip()
                ),
            },
            "freeze_rules": [
                (
                    "Phase 135 remains physically located under "
                    "scripts/phase135."
                ),
                (
                    "NeuroVest application code may never import "
                    "scripts.phase135."
                ),
                (
                    "Phase 135 may inspect NeuroVest but may not "
                    "modify application code."
                ),
                (
                    "Generated audit artifacts remain under "
                    "runtime/audits."
                ),
                (
                    "Any Phase 135 source change invalidates this "
                    "manifest and requires a new freeze verification."
                ),
                (
                    "No audit result constitutes deployment or "
                    "live-trading approval."
                ),
            ],
        }

        FREEZE_HISTORY_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        history_manifest = (
            FREEZE_HISTORY_DIRECTORY
            / f"{timestamp}.json"
        )

        history_report = (
            FREEZE_HISTORY_DIRECTORY
            / f"{timestamp}.txt"
        )

        report_text = render_freeze_report(
            manifest
        )

        write_json_atomic(
            FREEZE_MANIFEST,
            manifest,
        )

        write_json_atomic(
            history_manifest,
            manifest,
        )

        FREEZE_REPORT.write_text(
            report_text + "\n",
            encoding="utf-8",
        )

        history_report.write_text(
            report_text + "\n",
            encoding="utf-8",
        )

        print(report_text)

        return 0

    except (
        FreezeFailure,
        json.JSONDecodeError,
        subprocess.TimeoutExpired,
        OSError,
    ) as exc:
        print("=" * 80)
        print("PHASE 135 FREEZE VERIFICATION FAILED")
        print("=" * 80)
        print()
        print(
            f"{type(exc).__name__}: {exc}"
        )
        print()
        print("Phase 135 was not frozen.")
        print("Deployment remains unapproved.")
        print("Live trading remains unapproved.")
        print("=" * 80)

        return 1


if __name__ == "__main__":
    raise SystemExit(main())
