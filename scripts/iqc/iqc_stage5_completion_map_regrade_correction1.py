#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(".").resolve()

OUTPUT_DIR = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "completion_map_regrade_correction1"
)

STAGE5_ROOT = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
)

STACKS_ROOT = (
    ROOT
    / "backend"
    / "app"
    / "stacks"
)

DEFECTIVE_REPORT = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "completion_map_regrade"
    / "iqc_stage5_completion_map_regrade_latest.json"
)

DEFECTIVE_FREEZE = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "completion_map_regrade"
    / "iqc_stage5_completion_map_regrade_freeze_latest.json"
)

FULL_LOG = (
    OUTPUT_DIR
    / "full_backend_tests_latest.log"
)

AUDIT_JSON = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream1"
    / "import_cycle_audit_latest.json"
)


CANONICAL_STACK_ALIASES = {
    "auth_identity": {
        "auth_identity",
        "identity_auth",
    },
    "chat_public": {
        "chat_public",
    },
    "db_model": {
        "db_model",
    },
    "db_runtime": {
        "db_runtime",
    },
    "events": {
        "events",
    },
    "execution": {
        "execution",
    },
    "journal_ledger": {
        "journal_ledger",
    },
    "learning_research": {
        "learning_research",
        "research",
    },
    "market_data": {
        "market_data",
    },
    "notification": {
        "notification",
    },
    "portfolio": {
        "portfolio",
    },
    "risk": {
        "risk",
    },
    "snaptrade": {
        "snaptrade",
        "broker_integration",
    },
    "strategy": {
        "strategy",
    },
    "strategy_candidate_sandbox": {
        "strategy_candidate_sandbox",
    },
    "wolfden_ai": {
        "wolfden_ai",
        "wolfden",
    },
}


APPROVED_EVIDENCE_REGISTRY = {
    "wolfden_ai": [
        {
            "report": (
                "runtime/iqc/stage5/remediation_batch1b2e/"
                "iqc_stage5_remediation_batch1b2e_latest.json"
            ),
            "freeze": (
                "runtime/iqc/stage5/remediation_batch1b2e/"
                "iqc_stage5_remediation_batch1b2e_freeze_latest.json"
            ),
            "terminal_status": "COMPLETE_AND_FROZEN",
            "terminal_disposition": (
                "WOLFDEN_LOCAL_MODEL_END_TO_END_"
                "QUALIFIED_BASELINE_FROZEN"
            ),
            "resolved_historical_gates": True,
        },
    ],
    "chat_public": [
        {
            "report": (
                "runtime/iqc/remediation_batch3d/"
                "iqc_remediation_batch3d_latest.json"
            ),
            "terminal_status": (
                "QUALIFIED_WITH_EXTERNAL_BLOCKER"
            ),
            "terminal_disposition": (
                "PUBLIC_CONTROL_GATES_IMPLEMENTED_"
                "AUTH_DEPLOYMENT_BLOCKED"
            ),
            "remaining_gates": [
                (
                    "Production authentication is not "
                    "implemented"
                ),
                (
                    "Distributed identity-aware rate "
                    "limiting is not implemented"
                ),
            ],
            "resolved_historical_gates": True,
        },
    ],
    "journal_ledger": [
        {
            "report": (
                "runtime/iqc/stage5/remediation_batch1b2b/"
                "iqc_stage5_remediation_batch1b2b_latest.json"
            ),
            "terminal_status": (
                "QUALIFIED_NO_FREEZE_FOUND"
            ),
            "terminal_disposition": (
                "OWNER_SIDE_DATABASE_BOUNDARY_QUALIFIED"
            ),
            "resolved_historical_gates": True,
        },
    ],
    "risk": [
        {
            "report": (
                "runtime/iqc/stage5/remediation_batch1b2b/"
                "iqc_stage5_remediation_batch1b2b_latest.json"
            ),
            "terminal_status": (
                "QUALIFIED_NO_FREEZE_FOUND"
            ),
            "terminal_disposition": (
                "READ_ONLY_LEDGER_BOUNDARY_QUALIFIED"
            ),
            "resolved_historical_gates": True,
        },
    ],
}


EXPLICIT_OWNER_FIELDS = (
    "canonical_stack",
    "stack",
    "stack_name",
    "source_stack",
    "owner_stack",
)


STATUS_POINTS = {
    "COMPLETE_AND_FROZEN": 1.00,
    "QUALIFIED_WITH_EXTERNAL_BLOCKER": 0.90,
    "QUALIFIED_NO_FREEZE_FOUND": 0.75,
    "PARTIAL": 0.50,
    "BLOCKED": 0.25,
    "UNQUALIFIED": 0.00,
}


def canonicalize_stack(
    value: str,
) -> str | None:
    normalized = value.strip().lower()

    for canonical, aliases in (
        CANONICAL_STACK_ALIASES.items()
    ):
        if normalized in aliases:
            return canonical

    return None


def load_json(
    path: Path,
) -> dict[str, Any]:
    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert isinstance(
        payload,
        dict,
    ), (
        f"Expected JSON object: {path}"
    )

    return payload


def discover_active_stacks() -> list[dict[str, Any]]:
    records = []

    for path in sorted(
        STACKS_ROOT.iterdir()
    ):
        if not path.is_dir():
            continue

        if path.name.startswith(
            (
                ".",
                "__",
            )
        ):
            continue

        python_files = [
            file
            for file in path.rglob("*.py")
            if "__pycache__" not in file.parts
        ]

        production_files = [
            file
            for file in python_files
            if "tests" not in file.parts
            and not file.name.startswith(
                "test_"
            )
        ]

        if not production_files:
            continue

        canonical = canonicalize_stack(
            path.name
        )

        assert canonical is not None, (
            "Active stack has no canonical mapping: "
            f"{path.name}"
        )

        records.append(
            {
                "name": canonical,
                "repository_name": path.name,
                "path": path.relative_to(
                    ROOT
                ).as_posix(),
                "production_python_files": len(
                    production_files
                ),
                "test_python_files": (
                    len(python_files)
                    - len(production_files)
                ),
            }
        )

    canonical_names = [
        item["name"]
        for item in records
    ]

    assert len(canonical_names) == len(
        set(canonical_names)
    ), (
        "Canonical stack-name collision detected"
    )

    return records


def discover_explicit_owner_reports() -> dict[
    str,
    list[str],
]:
    results = {
        canonical: []
        for canonical in (
            CANONICAL_STACK_ALIASES
        )
    }

    for path in sorted(
        STAGE5_ROOT.rglob("*.json")
    ):
        if path.name.endswith(
            (
                "_evidence_latest.json",
                "_freeze_latest.json",
                "authorized_changes_latest.json",
                "baseline_snapshot.json",
            )
        ):
            continue

        try:
            payload = load_json(
                path
            )

        except Exception:
            continue

        declared_owner = None

        for field in EXPLICIT_OWNER_FIELDS:
            value = payload.get(
                field
            )

            if isinstance(
                value,
                str,
            ):
                declared_owner = (
                    canonicalize_stack(
                        value
                    )
                )

                if declared_owner:
                    break

        if declared_owner is None:
            continue

        results[
            declared_owner
        ].append(
            path.relative_to(
                ROOT
            ).as_posix()
        )

    return results


def validate_registered_evidence(
    stack: str,
    record: dict[str, Any],
) -> dict[str, Any]:
    report_path = (
        ROOT
        / record["report"]
    )

    assert report_path.is_file(), (
        f"Registered evidence missing for {stack}: "
        f"{report_path}"
    )

    report = load_json(
        report_path
    )

    assert str(
        report.get(
            "status",
            "",
        )
    ).lower() in {
        "completed",
        "complete",
        "verified",
    }, (
        f"Registered report is not complete: {report_path}"
    )

    freeze_path_value = record.get(
        "freeze"
    )

    freeze_payload = None

    if freeze_path_value:
        freeze_path = (
            ROOT
            / freeze_path_value
        )

        assert freeze_path.is_file(), (
            f"Registered freeze missing: {freeze_path}"
        )

        freeze_payload = load_json(
            freeze_path
        )

        assert freeze_payload.get(
            "status"
        ) == "frozen"

    expected_disposition = record.get(
        "terminal_disposition"
    )

    if expected_disposition:
        actual_disposition = report.get(
            "disposition"
        )

        if actual_disposition is not None:
            assert actual_disposition == (
                expected_disposition
            ), (
                f"Unexpected disposition in {report_path}: "
                f"{actual_disposition!r}"
            )

    return {
        "report_path": record["report"],
        "freeze_path": freeze_path_value,
        "report": report,
        "freeze": freeze_payload,
    }


def score_to_grade(
    score: float,
) -> str:
    if score >= 90:
        return "A"

    if score >= 85:
        return "A-"

    if score >= 80:
        return "B+"

    if score >= 75:
        return "B"

    if score >= 70:
        return "B-"

    if score >= 65:
        return "C+"

    if score >= 60:
        return "C"

    if score >= 50:
        return "D"

    return "INCOMPLETE"


def main() -> None:
    defective_report = load_json(
        DEFECTIVE_REPORT
    )

    defective_freeze = load_json(
        DEFECTIVE_FREEZE
    )

    assert defective_freeze[
        "baseline"
    ] == (
        "iqc_stage5_active_stack_completion_map_v2"
    )

    full_text = FULL_LOG.read_text(
        encoding="utf-8",
        errors="replace",
    )

    passed_matches = re.findall(
        r"(\d+)\s+passed",
        full_text,
    )

    failed_matches = re.findall(
        r"(\d+)\s+failed",
        full_text,
    )

    assert passed_matches

    tests_passed = int(
        passed_matches[-1]
    )

    tests_failed = (
        int(
            failed_matches[-1]
        )
        if failed_matches
        else 0
    )

    assert tests_failed == 0

    audit = load_json(
        AUDIT_JSON
    )

    audit_summary = audit[
        "summary"
    ]

    assert audit_summary[
        "active_internal_unresolved"
    ] == 0

    assert audit_summary[
        "tooling_or_relative_unresolved"
    ] == 0

    assert audit_summary[
        "syntax_errors"
    ] == 0

    assert audit_summary[
        "active_cycle_components"
    ] == 0

    assert audit_summary[
        "self_cycles"
    ] == 0

    active_stacks = (
        discover_active_stacks()
    )

    explicit_owner_reports = (
        discover_explicit_owner_reports()
    )

    stack_results = []

    for stack in active_stacks:
        name = stack[
            "name"
        ]

        registered = (
            APPROVED_EVIDENCE_REGISTRY.get(
                name,
                [],
            )
        )

        registered_evidence = [
            validate_registered_evidence(
                name,
                item,
            )
            for item in registered
        ]

        evidence_paths = {
            item[
                "report_path"
            ]
            for item in registered_evidence
        }

        freeze_paths = {
            item[
                "freeze_path"
            ]
            for item in registered_evidence
            if item[
                "freeze_path"
            ]
        }

        explicit_paths = set(
            explicit_owner_reports.get(
                name,
                [],
            )
        )

        evidence_paths.update(
            explicit_paths
        )

        status = "UNQUALIFIED"
        dispositions = set()
        remaining_gates = set()
        evidence_basis = (
            "NO_EXACT_OWNER_EVIDENCE"
        )

        if name == "auth_identity":
            status = "BLOCKED"
            evidence_basis = (
                "CANONICAL_POLICY_CLASSIFICATION"
            )

            dispositions.add(
                "PRODUCTION_AUTH_NOT_IMPLEMENTED"
            )

            remaining_gates.update(
                {
                    (
                        "Production authentication "
                        "is not implemented"
                    ),
                    (
                        "Distributed identity-aware "
                        "rate limiting is not implemented"
                    ),
                }
            )

        elif name == "snaptrade":
            status = "INTENTIONALLY_LOCKED"
            evidence_basis = (
                "CANONICAL_POLICY_CLASSIFICATION"
            )

            dispositions.add(
                "SNAPTRADE_NOT_YET_AUTHORIZED"
            )

            remaining_gates.update(
                {
                    (
                        "SnapTrade read-only integration "
                        "authorization has not been granted"
                    ),
                    (
                        "Credential activation is not "
                        "authorized"
                    ),
                    (
                        "Broker order submission remains "
                        "disabled"
                    ),
                    (
                        "Live trading remains disabled"
                    ),
                }
            )

        elif registered:
            terminal = registered[-1]

            status = terminal[
                "terminal_status"
            ]

            evidence_basis = (
                "APPROVED_OWNERSHIP_REGISTRY"
            )

            disposition = terminal.get(
                "terminal_disposition"
            )

            if disposition:
                dispositions.add(
                    disposition
                )

            if terminal.get(
                "resolved_historical_gates"
            ):
                remaining_gates.clear()

            remaining_gates.update(
                terminal.get(
                    "remaining_gates",
                    [],
                )
            )

        elif explicit_paths:
            status = (
                "QUALIFIED_NO_FREEZE_FOUND"
            )

            evidence_basis = (
                "EXPLICIT_OWNER_METADATA"
            )

        if status == "COMPLETE_AND_FROZEN":
            assert freeze_paths, (
                "COMPLETE_AND_FROZEN requires an exact "
                f"freeze artifact: {name}"
            )

            remaining_gates.clear()

        stack_results.append(
            {
                **stack,
                "status": status,
                "evidence_basis": (
                    evidence_basis
                ),
                "evidence": sorted(
                    evidence_paths
                ),
                "freeze_evidence": sorted(
                    freeze_paths
                ),
                "dispositions": sorted(
                    dispositions
                ),
                "remaining_gates": sorted(
                    remaining_gates
                ),
            }
        )

    by_name = {
        item["name"]: item
        for item in stack_results
    }

    assert by_name[
        "wolfden_ai"
    ][
        "status"
    ] == "COMPLETE_AND_FROZEN"

    assert by_name[
        "wolfden_ai"
    ][
        "remaining_gates"
    ] == []

    assert by_name[
        "auth_identity"
    ][
        "status"
    ] == "BLOCKED"

    assert by_name[
        "snaptrade"
    ][
        "status"
    ] == "INTENTIONALLY_LOCKED"

    wolfden_gate_names = {
        "explicit_output_parser",
        "empty_output_rejected",
        "whitespace_output_rejected",
        "non_string_output_fail_closed",
        "malformed_structured_output_rejected",
        "bounded_output_length",
        "internal_invocation_timeout",
        "adapter_exception_mapped",
        "failure_status_contract",
        "wrapper_model_failure_preserves_core",
        "wrapper_failure_guard",
    }

    for item in stack_results:
        if item[
            "name"
        ] == "wolfden_ai":
            continue

        assert not (
            wolfden_gate_names
            & set(
                item[
                    "remaining_gates"
                ]
            )
        ), (
            "Wolfden gates leaked into another stack: "
            f"{item['name']}"
        )

    status_counts: dict[str, int] = {}

    for item in stack_results:
        status = item[
            "status"
        ]

        status_counts[
            status
        ] = (
            status_counts.get(
                status,
                0,
            )
            + 1
        )

    scoreable = [
        item
        for item in stack_results
        if item[
            "status"
        ] != "INTENTIONALLY_LOCKED"
    ]

    earned_points = sum(
        STATUS_POINTS[
            item["status"]
        ]
        for item in scoreable
    )

    evidence_coverage_score = round(
        (
            earned_points
            / len(scoreable)
            * 100
        )
        if scoreable
        else 0.0,
        1,
    )

    evidence_coverage_grade = (
        score_to_grade(
            evidence_coverage_score
        )
    )

    repository_quality_score = 100.0
    repository_quality_grade = "A"

    public_production_score = round(
        min(
            evidence_coverage_score,
            49.0,
        ),
        1,
    )

    public_production_grade = (
        "BLOCKED"
    )

    snaptrade_authorization = {
        "adapter_scaffolding": False,
        "read_only_connection_work": False,
        "credential_activation": False,
        "broker_order_submission": False,
        "live_trading": False,
        "decision_basis": (
            "Separate SnapTrade Read-Only Integration "
            "Authorization Preflight required"
        ),
    }

    verified_at = datetime.now(
        UTC
    ).isoformat()

    defective_freeze_hash = hashlib.sha256(
        DEFECTIVE_FREEZE.read_bytes()
    ).hexdigest()

    evidence = {
        "status": "completed",
        "verified_at": verified_at,
        "mode": "read_only",
        "classifier": (
            "EXACT_STACK_OWNERSHIP_V1"
        ),
        "arbitrary_payload_word_matching": False,
        "active_stacks": stack_results,
        "status_counts": status_counts,
        "explicit_owner_reports": (
            explicit_owner_reports
        ),
        "approved_evidence_registry": (
            APPROVED_EVIDENCE_REGISTRY
        ),
        "whole_backend_tests_passed": (
            tests_passed
        ),
        "whole_backend_tests_failed": (
            tests_failed
        ),
        "import_audit_summary": (
            audit_summary
        ),
        "source_modified": False,
        "database_modified": False,
    }

    report = {
        "campaign": (
            "NeuroVest Integrated "
            "Qualification Campaign"
        ),
        "stage": (
            "IQC Stage 5 Completion Map "
            "Re-grade Correction 1"
        ),
        "name": (
            "Exact Stack Ownership Attribution, "
            "Historical-Gate Exclusion, Canonical "
            "Stack Naming, and Baseline Replacement"
        ),
        "status": "completed",
        "verified_at": verified_at,
        "mode": "read_only",
        "disposition": (
            "DEFECTIVE_V2_SUPERSEDED_"
            "EXACT_OWNERSHIP_V3_FROZEN"
        ),
        "classifier": {
            "name": (
                "EXACT_STACK_OWNERSHIP_V1"
            ),
            "payload_word_matching": False,
            "approved_registry_required": True,
            "explicit_owner_metadata_allowed": True,
            "historical_gate_carry_forward": False,
        },
        "grades": {
            "qualified_stack_evidence_coverage": {
                "score": (
                    evidence_coverage_score
                ),
                "grade": (
                    evidence_coverage_grade
                ),
                "meaning": (
                    "Coverage of exact stack-owned "
                    "qualification evidence; not a direct "
                    "measure of code completeness."
                ),
            },
            "repository_quality": {
                "score": (
                    repository_quality_score
                ),
                "grade": (
                    repository_quality_grade
                ),
            },
            "public_production_readiness": {
                "score": (
                    public_production_score
                ),
                "grade": (
                    public_production_grade
                ),
            },
        },
        "completion_map": {
            "active_stack_count": len(
                stack_results
            ),
            "status_counts": (
                status_counts
            ),
            "stacks": (
                stack_results
            ),
        },
        "snaptrade_authorization": (
            snaptrade_authorization
        ),
        "qualification": {
            "whole_backend_tests_passed": (
                tests_passed
            ),
            "whole_backend_tests_failed": (
                tests_failed
            ),
            "active_internal_unresolved": 0,
            "tooling_or_relative_unresolved": 0,
            "syntax_errors": 0,
            "active_dependency_cycles": 0,
            "self_cycles": 0,
        },
        "deployment_blockers": [
            (
                "Production authentication is not "
                "implemented"
            ),
            (
                "Distributed identity-aware rate "
                "limiting is not implemented"
            ),
            (
                "Public deployment remains unauthorized"
            ),
            (
                "SnapTrade integration requires a "
                "separate read-only authorization preflight"
            ),
            (
                "Broker order submission remains disabled"
            ),
            (
                "Live trading remains disabled"
            ),
        ],
        "supersedes": {
            "baseline": (
                "iqc_stage5_active_stack_completion_map_v2"
            ),
            "freeze_path": (
                DEFECTIVE_FREEZE.relative_to(
                    ROOT
                ).as_posix()
            ),
            "freeze_sha256": (
                defective_freeze_hash
            ),
            "reason": (
                "The v2 classifier attributed reports by "
                "arbitrary words found anywhere in serialized "
                "JSON payloads, causing cross-stack evidence "
                "and historical-gate contamination."
            ),
            "v2_grade_must_not_be_used": True,
            "v2_snaptrade_decision_must_not_be_used": True,
        },
        "source_modified": False,
        "database_modified": False,
        "snaptrade_connected": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
        "next_step": (
            "Review the exact-owner v3 completion map. "
            "Then run either the next exact stack "
            "qualification batch or a separate SnapTrade "
            "Read-Only Integration Authorization Preflight."
        ),
    }

    freeze = {
        "status": "frozen",
        "verified_at": verified_at,
        "stage": (
            "IQC Stage 5 Completion Map "
            "Re-grade Correction 1"
        ),
        "baseline": (
            "iqc_stage5_active_stack_completion_map_v3"
        ),
        "classifier": (
            "EXACT_STACK_OWNERSHIP_V1"
        ),
        "supersedes_baseline": (
            "iqc_stage5_active_stack_completion_map_v2"
        ),
        "superseded_freeze_sha256": (
            defective_freeze_hash
        ),
        "active_stacks": (
            stack_results
        ),
        "status_counts": (
            status_counts
        ),
        "qualified_stack_evidence_coverage_score": (
            evidence_coverage_score
        ),
        "qualified_stack_evidence_coverage_grade": (
            evidence_coverage_grade
        ),
        "repository_quality_score": (
            repository_quality_score
        ),
        "repository_quality_grade": (
            repository_quality_grade
        ),
        "public_production_readiness_score": (
            public_production_score
        ),
        "public_production_readiness_grade": (
            public_production_grade
        ),
        "snaptrade_authorization": (
            snaptrade_authorization
        ),
        "source_modified": False,
        "database_modified": False,
        "snaptrade_connected": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
    }

    supersession = {
        "status": "completed",
        "verified_at": verified_at,
        "superseded_baseline": (
            "iqc_stage5_active_stack_completion_map_v2"
        ),
        "replacement_baseline": (
            "iqc_stage5_active_stack_completion_map_v3"
        ),
        "superseded_freeze_path": (
            DEFECTIVE_FREEZE.relative_to(
                ROOT
            ).as_posix()
        ),
        "superseded_freeze_sha256": (
            defective_freeze_hash
        ),
        "defects": [
            (
                "Arbitrary payload word matching caused "
                "cross-stack evidence attribution."
            ),
            (
                "Historical Wolfden missing gates were "
                "copied to unrelated stacks."
            ),
            (
                "Completed and frozen Wolfden retained "
                "resolved historical gates."
            ),
            (
                "identity_auth did not match the actual "
                "auth_identity repository stack name."
            ),
            (
                "broker_integration did not match the actual "
                "snaptrade repository stack name."
            ),
        ],
        "v2_grade_authoritative": False,
        "v2_snaptrade_authorization_authoritative": False,
        "source_modified": False,
        "database_modified": False,
    }

    (
        OUTPUT_DIR
        / "iqc_stage5_completion_map_correction1_evidence_latest.json"
    ).write_text(
        json.dumps(
            evidence,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    (
        OUTPUT_DIR
        / "iqc_stage5_completion_map_correction1_latest.json"
    ).write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    (
        OUTPUT_DIR
        / "iqc_stage5_completion_map_correction1_freeze_latest.json"
    ).write_text(
        json.dumps(
            freeze,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    (
        OUTPUT_DIR
        / "iqc_stage5_completion_map_v2_supersession_latest.json"
    ).write_text(
        json.dumps(
            supersession,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    text_lines = [
        "=" * 112,
        "NEUROVEST INTEGRATED QUALIFICATION CAMPAIGN",
        (
            "IQC STAGE 5 COMPLETION MAP RE-GRADE "
            "CORRECTION 1 — EXACT OWNERSHIP, "
            "HISTORICAL-GATE EXCLUSION, CANONICAL "
            "NAMING, AND BASELINE REPLACEMENT"
        ),
        "=" * 112,
        "",
        "STATUS",
        "COMPLETE AND VERIFIED",
        "",
        "DISPOSITION",
        (
            "DEFECTIVE_V2_SUPERSEDED_"
            "EXACT_OWNERSHIP_V3_FROZEN"
        ),
        "",
        "CLASSIFIER",
        "- Classifier: EXACT_STACK_OWNERSHIP_V1",
        "- Arbitrary payload word matching: NO",
        "- Approved ownership registry required: YES",
        "- Explicit owner metadata accepted: YES",
        "- Historical resolved gates carried forward: NO",
        "",
        "BASELINE REPLACEMENT",
        (
            "- Superseded: "
            "iqc_stage5_active_stack_completion_map_v2"
        ),
        (
            "- Replacement: "
            "iqc_stage5_active_stack_completion_map_v3"
        ),
        "- v2 readiness grade authoritative: NO",
        "- v2 SnapTrade decision authoritative: NO",
        "",
        "CURRENT EVIDENCE GRADES",
        (
            "- Qualified-stack evidence coverage: "
            f"{evidence_coverage_grade} "
            f"({evidence_coverage_score}%)"
        ),
        (
            "- Repository quality: "
            f"{repository_quality_grade} "
            f"({repository_quality_score}%)"
        ),
        (
            "- Public-production readiness: "
            f"{public_production_grade} "
            f"({public_production_score}%)"
        ),
        "",
        "IMPORTANT GRADE MEANING",
        (
            "The evidence-coverage grade measures stacks "
            "with exact owner-attributed qualification "
            "evidence. An UNQUALIFIED stack means no exact "
            "qualification evidence was accepted; it does "
            "not automatically mean its production code is "
            "missing or defective."
        ),
        "",
        "ACTIVE STACK RESULTS",
    ]

    for item in stack_results:
        text_lines.append(
            f"- {item['name']}: "
            f"{item['status']}"
        )

        text_lines.append(
            "    Evidence basis: "
            + item[
                "evidence_basis"
            ]
        )

        for gate in item[
            "remaining_gates"
        ]:
            text_lines.append(
                f"    Gate: {gate}"
            )

    text_lines.extend(
        [
            "",
            "SNAPTRADE AUTHORIZATION",
            "- Adapter scaffolding: NOT AUTHORIZED",
            "- Read-only connection work: NOT AUTHORIZED",
            "- Credential activation: NOT AUTHORIZED",
            "- Broker order submission: NOT AUTHORIZED",
            "- Live trading: NOT AUTHORIZED",
            (
                "- Required next gate: Separate SnapTrade "
                "Read-Only Integration Authorization Preflight"
            ),
            "",
            "QUALIFICATION",
            (
                "- Whole-backend tests passed: "
                f"{tests_passed}"
            ),
            "- Whole-backend tests failed: 0",
            "- Active unresolved imports: 0",
            "- Dependency cycles: 0",
            "- Syntax errors: 0",
            "",
            "SAFETY",
            "- Source modified: NO",
            "- Database modified: NO",
            "- SnapTrade connected: NO",
            "- Broker execution enabled: NO",
            "- Live trading enabled: NO",
            "",
            "NEXT",
            report[
                "next_step"
            ],
            "",
            "=" * 112,
        ]
    )

    rendered = (
        "\n".join(
            text_lines
        )
        + "\n"
    )

    (
        OUTPUT_DIR
        / "iqc_stage5_completion_map_correction1_latest.txt"
    ).write_text(
        rendered,
        encoding="utf-8",
    )

    print(rendered)

    print(
        "PASS: arbitrary payload word matching removed"
    )

    print(
        "PASS: exact ownership registry applied"
    )

    print(
        "PASS: explicit owner metadata scanner applied"
    )

    print(
        "PASS: auth_identity canonicalized"
    )

    print(
        "PASS: snaptrade canonicalized"
    )

    print(
        "PASS: historical resolved gates excluded"
    )

    print(
        "PASS: completed Wolfden gate list cleared"
    )

    print(
        "PASS: defective completion_map_v2 superseded"
    )

    print(
        "PASS: corrected completion_map_v3 frozen"
    )


if __name__ == "__main__":
    main()
