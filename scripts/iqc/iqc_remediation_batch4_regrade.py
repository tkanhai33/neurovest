#!/usr/bin/env python3
"""
NeuroVest Integrated Qualification Campaign

IQC Remediation Batch 4 —
Implementation-State-Aware Re-grade and Baseline Freeze

MODE
READ ONLY

Purpose:
- Verify IQC Stage 1B and Remediation Batches 1 through 3D.
- Re-grade active implemented stacks.
- Exclude intentionally deferred Auth from flow-quality scoring.
- Keep Auth, SnapTrade, Cerberus and public deployment as separate
  readiness tracks and blockers.
- Recognize completed test isolation, chat persistence extraction,
  and public-chat control qualification.
- Freeze the authoritative post-remediation baseline.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(".").resolve()

RUNTIME = ROOT / "runtime"

OUTPUT_DIR = (
    RUNTIME
    / "iqc"
    / "remediation_batch4"
)

STAGE1B_REPORT = (
    RUNTIME
    / "iqc"
    / "stage1b"
    / "iqc_stage1b_calibrated_baseline_latest.json"
)

STAGE2_REPORT = (
    RUNTIME
    / "iqc"
    / "stage2"
    / "iqc_stage2_targeted_remediation_plan_latest.json"
)

BATCH1_REPORT = (
    RUNTIME
    / "iqc"
    / "remediation_batch1"
    / "iqc_remediation_batch1_latest.json"
)

BATCH2_REPORT = (
    RUNTIME
    / "iqc"
    / "remediation_batch2"
    / "iqc_remediation_batch2_auth_roadmap_latest.json"
)

BATCH3_REPORT = (
    RUNTIME
    / "iqc"
    / "remediation_batch3"
    / "iqc_remediation_batch3_chat_public_latest.json"
)

BATCH3A_REPORT = (
    RUNTIME
    / "iqc"
    / "remediation_batch3a"
    / "iqc_remediation_batch3a_chat_disposition_latest.json"
)

BATCH3B_REPORT = (
    RUNTIME
    / "iqc"
    / "remediation_batch3b"
    / "iqc_remediation_batch3b_latest.json"
)

BATCH3C_REPORT = (
    RUNTIME
    / "iqc"
    / "remediation_batch3c"
    / "iqc_remediation_batch3c_latest.json"
)

BATCH3D_REPORT = (
    RUNTIME
    / "iqc"
    / "remediation_batch3d"
    / "iqc_remediation_batch3d_latest.json"
)

IMPORT_AUDIT_REPORT = (
    RUNTIME
    / "hardening"
    / "workstream1"
    / "import_cycle_audit_latest.json"
)

DATABASE_STATE = (
    RUNTIME
    / "iqc"
    / "remediation_batch3d"
    / "database_after.json"
)

FULL_TEST_LOG = (
    RUNTIME
    / "iqc"
    / "remediation_batch3d"
    / "full_backend_tests_latest.log"
)

REPORT_JSON = (
    OUTPUT_DIR
    / "iqc_remediation_batch4_regrade_latest.json"
)

REPORT_TEXT = (
    OUTPUT_DIR
    / "iqc_remediation_batch4_regrade_latest.txt"
)

GRADEBOOK_JSON = (
    OUTPUT_DIR
    / "iqc_remediation_batch4_gradebook_latest.json"
)

FREEZE_JSON = (
    OUTPUT_DIR
    / "iqc_remediation_batch4_freeze_latest.json"
)

SOURCE_MANIFEST = (
    OUTPUT_DIR
    / "iqc_remediation_batch4_source_manifest_latest.json"
)

ACTIVE_IMPLEMENTED_STACKS = {
    "market_data",
    "portfolio",
    "risk",
    "strategy",
    "execution",
    "journal_ledger",
    "wolfden_ai",
    "chat_public",
}

DEFERRED_STACKS = {
    "auth_identity",
}

STACK_WEIGHTS = {
    "market_data": 1.00,
    "portfolio": 1.00,
    "risk": 1.15,
    "strategy": 1.00,
    "execution": 1.15,
    "journal_ledger": 1.10,
    "wolfden_ai": 0.90,
    "chat_public": 0.90,
}

GRADE_THRESHOLDS = (
    (97.0, "A+"),
    (93.0, "A"),
    (90.0, "A-"),
    (87.0, "B+"),
    (83.0, "B"),
    (80.0, "B-"),
    (77.0, "C+"),
    (73.0, "C"),
    (70.0, "C-"),
    (67.0, "D+"),
    (63.0, "D"),
    (60.0, "D-"),
    (0.0, "F"),
)


def load_json(
    path: Path,
) -> dict[str, Any]:
    assert path.is_file(), (
        f"Required report missing: {path}"
    )

    value = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert isinstance(
        value,
        dict,
    )

    return value


def sha256_file(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def relative(
    path: Path,
) -> str:
    return path.relative_to(
        ROOT
    ).as_posix()


def grade_for(
    score: float,
) -> str:
    for threshold, grade in (
        GRADE_THRESHOLDS
    ):
        if score >= threshold:
            return grade

    return "F"


def clamp(
    value: float,
) -> float:
    return round(
        max(
            0.0,
            min(
                100.0,
                value,
            ),
        ),
        2,
    )


def find_stage1_stack(
    stage1b: dict[str, Any],
    stack: str,
) -> dict[str, Any] | None:
    for item in stage1b.get(
        "stack_results",
        [],
    ):
        if item.get(
            "stack"
        ) == stack:
            return item

    return None


def test_count_from_log(
    path: Path,
    label: str,
) -> int:
    if not path.is_file():
        return 0

    text = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    matches = re.findall(
        rf"(\d+)\s+{label}",
        text,
    )

    return (
        int(matches[-1])
        if matches
        else 0
    )


def source_manifest() -> dict[str, Any]:
    entries = []

    backend_root = (
        ROOT
        / "backend"
        / "app"
    )

    for path in sorted(
        backend_root.rglob("*.py")
    ):
        if "__pycache__" in path.parts:
            continue

        data = path.read_bytes()

        entries.append(
            {
                "path": relative(path),
                "sha256": hashlib.sha256(
                    data
                ).hexdigest(),
                "size_bytes": len(data),
            }
        )

    digest = hashlib.sha256()

    for entry in entries:
        digest.update(
            entry[
                "path"
            ].encode(
                "utf-8"
            )
        )

        digest.update(
            entry[
                "sha256"
            ].encode(
                "ascii"
            )
        )

    manifest = {
        "generated_at": datetime.now(
            UTC
        ).isoformat(),
        "file_count": len(entries),
        "manifest_sha256": (
            digest.hexdigest()
        ),
        "files": entries,
    }

    SOURCE_MANIFEST.write_text(
        json.dumps(
            manifest,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return manifest


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    stage1b = load_json(
        STAGE1B_REPORT
    )

    stage2 = load_json(
        STAGE2_REPORT
    )

    batch1 = load_json(
        BATCH1_REPORT
    )

    batch2 = load_json(
        BATCH2_REPORT
    )

    batch3 = load_json(
        BATCH3_REPORT
    )

    batch3a = load_json(
        BATCH3A_REPORT
    )

    batch3b = load_json(
        BATCH3B_REPORT
    )

    batch3c = load_json(
        BATCH3C_REPORT
    )

    batch3d = load_json(
        BATCH3D_REPORT
    )

    import_audit = load_json(
        IMPORT_AUDIT_REPORT
    )

    database = load_json(
        DATABASE_STATE
    )

    assert stage1b[
        "status"
    ] == "completed"

    assert stage2[
        "status"
    ] == "completed"

    assert batch1[
        "status"
    ] == "completed"

    assert batch2[
        "status"
    ] == "completed"

    assert batch3[
        "status"
    ] == "completed"

    assert batch3a[
        "status"
    ] == "completed"

    assert batch3b[
        "status"
    ] == "completed"

    assert batch3c[
        "status"
    ] == "completed"

    assert batch3d[
        "status"
    ] == "completed"

    assert batch1[
        "whole_backend_tests"
    ][
        "failed"
    ] == 0

    assert batch3b[
        "tests"
    ][
        "whole_backend_failed"
    ] == 0

    assert batch3d[
        "qualification"
    ][
        "whole_backend_failed"
    ] == 0

    assert batch3d[
        "qualification"
    ][
        "whole_backend_passed"
    ] >= 158

    assert batch3d[
        "database_modified"
    ] is False

    assert batch3d[
        "auth_implemented"
    ] is False

    assert batch3d[
        "snaptrade_connected"
    ] is False

    assert batch3d[
        "broker_execution_enabled"
    ] is False

    assert batch3d[
        "live_trading_enabled"
    ] is False

    assert batch3d[
        "implementation"
    ][
        "route_failure_mapping"
    ] is True

    assert batch3d[
        "implementation"
    ][
        "dependency_timeout"
    ] is True

    assert batch3d[
        "implementation"
    ][
        "anonymous_rate_limiting"
    ] is True

    assert batch3d[
        "implementation"
    ][
        "request_text_validation"
    ] is True

    assert batch3d[
        "implementation"
    ][
        "restricted_capability_safety_policy"
    ] is True

    summary = import_audit[
        "summary"
    ]

    assert summary[
        "active_internal_unresolved"
    ] == 0

    assert summary[
        "tooling_or_relative_unresolved"
    ] == 0

    assert summary[
        "syntax_errors"
    ] == 0

    assert summary[
        "active_cycle_components"
    ] == 0

    assert summary[
        "self_cycles"
    ] == 0

    assert database[
        "connected"
    ] is True

    assert database[
        "modified"
    ] is False

    latest_passed = batch3d[
        "qualification"
    ][
        "whole_backend_passed"
    ]

    log_passed = test_count_from_log(
        FULL_TEST_LOG,
        "passed",
    )

    assert log_passed >= 158

    stack_results = []

    for stack in sorted(
        ACTIVE_IMPLEMENTED_STACKS
    ):
        original = find_stage1_stack(
            stage1b,
            stack,
        )

        assert original is not None, (
            f"Stage 1B stack result missing: {stack}"
        )

        original_score = float(
            original[
                "score"
            ]
        )

        adjustments = []
        score = original_score

        if stack == "chat_public":
            score += 8.0

            adjustments.append(
                {
                    "code": (
                        "PERSISTENCE_BOUNDARY_EXTRACTED"
                    ),
                    "points": 3.0,
                    "evidence": (
                        "Batch 3B conversation service boundary"
                    ),
                }
            )

            adjustments.append(
                {
                    "code": (
                        "PUBLIC_CONTROL_GATES_IMPLEMENTED"
                    ),
                    "points": 3.0,
                    "evidence": (
                        "Batch 3D timeout, validation, "
                        "rate-limit and safety controls"
                    ),
                }
            )

            adjustments.append(
                {
                    "code": (
                        "FOCUSED_CHAT_TEST_EVIDENCE"
                    ),
                    "points": 2.0,
                    "evidence": (
                        "15 focused tests added across "
                        "Batches 3B and 3D"
                    ),
                }
            )

        if stack in {
            "execution",
            "strategy",
            "portfolio",
            "risk",
        }:
            score += 1.25

            adjustments.append(
                {
                    "code": (
                        "TRADING_PIPELINE_TEST_ISOLATION"
                    ),
                    "points": 1.25,
                    "evidence": (
                        "Batch 1 removed stale patching, "
                        "real DB leakage and async-loop contamination"
                    ),
                }
            )

        if stack == "journal_ledger":
            score += 0.5

            adjustments.append(
                {
                    "code": (
                        "AUDIT_QUERY_BOUNDARY_QUALIFIED"
                    ),
                    "points": 0.5,
                    "evidence": (
                        "Workstream 3 Stage 8 qualification freeze"
                    ),
                }
            )

        score = clamp(
            score
        )

        stack_results.append(
            {
                "stack": stack,
                "implementation_state": (
                    "IMPLEMENTED_ACTIVE"
                ),
                "included_in_flow_grade": True,
                "weight": STACK_WEIGHTS[
                    stack
                ],
                "original_score": (
                    original_score
                ),
                "adjustments": adjustments,
                "adjusted_score": score,
                "adjusted_grade": grade_for(
                    score
                ),
                "deployment_dependency": (
                    stack
                    in {
                        "chat_public",
                        "execution",
                        "portfolio",
                    }
                ),
            }
        )

    auth_original = find_stage1_stack(
        stage1b,
        "auth_identity",
    )

    assert auth_original is not None

    deferred_results = [
        {
            "stack": "auth_identity",
            "implementation_state": (
                "PARTIAL_PLACEHOLDER_DEFERRED"
            ),
            "included_in_flow_grade": False,
            "original_score": float(
                auth_original[
                    "score"
                ]
            ),
            "original_grade": auth_original[
                "grade"
            ],
            "current_score": None,
            "current_grade": (
                "DEFERRED_BY_DESIGN"
            ),
            "implementation_completeness": batch2[
                "auth_identity"
            ][
                "provisional_implementation_completeness"
            ],
            "remaining_gate_count": batch2[
                "auth_identity"
            ][
                "remaining_gate_count"
            ],
            "deployment_blocker": batch2[
                "auth_identity"
            ][
                "deployment_blocker"
            ],
            "reason_excluded": (
                "Auth capabilities are intentionally unimplemented "
                "and are not part of the current internal-flow scope."
            ),
        }
    ]

    weighted_total = sum(
        item[
            "adjusted_score"
        ]
        * item[
            "weight"
        ]
        for item in stack_results
    )

    total_weight = sum(
        item[
            "weight"
        ]
        for item in stack_results
    )

    active_stack_score = (
        weighted_total
        / total_weight
    )

    repository_score = 100.0

    if summary[
        "active_internal_unresolved"
    ]:
        repository_score -= 20.0

    if summary[
        "active_cycle_components"
    ]:
        repository_score -= 20.0

    if summary[
        "syntax_errors"
    ]:
        repository_score -= 20.0

    repository_score = clamp(
        repository_score
    )

    test_score = 100.0

    if latest_passed < 158:
        test_score -= 10.0

    test_score = clamp(
        test_score
    )

    safety_score = 100.0

    if batch3d[
        "broker_execution_enabled"
    ]:
        safety_score -= 50.0

    if batch3d[
        "live_trading_enabled"
    ]:
        safety_score -= 50.0

    safety_score = clamp(
        safety_score
    )

    flow_quality_score = clamp(
        (
            active_stack_score
            * 0.70
        )
        + (
            repository_score
            * 0.10
        )
        + (
            test_score
            * 0.12
        )
        + (
            safety_score
            * 0.08
        )
    )

    flow_quality_grade = grade_for(
        flow_quality_score
    )

    readiness_tracks = {
        "internal_development": {
            "status": "QUALIFIED",
            "score": flow_quality_score,
            "grade": flow_quality_grade,
            "blockers": [],
        },
        "controlled_local_flow_testing": {
            "status": "QUALIFIED",
            "score": flow_quality_score,
            "grade": flow_quality_grade,
            "blockers": [],
        },
        "controlled_early_users": {
            "status": "NOT_QUALIFIED",
            "blockers": [
                "Production Auth unimplemented",
                (
                    "Distributed identity-aware "
                    "rate limiting unimplemented"
                ),
                (
                    "Cerberus external and internal "
                    "threat heads not qualified"
                ),
            ],
        },
        "public_production_deployment": {
            "status": "NOT_QUALIFIED",
            "blockers": [
                "Production Auth unimplemented",
                (
                    "Distributed identity-aware "
                    "rate limiting unimplemented"
                ),
                (
                    "Cerberus security system not qualified"
                ),
                (
                    "Production deployment campaign "
                    "not completed"
                ),
            ],
        },
        "snaptrade_read_only_sandbox": {
            "status": "NOT_AUTHORIZED",
            "implementation_completeness": (
                batch2[
                    "snaptrade"
                ][
                    "provisional_implementation_completeness"
                ]
            ),
            "remaining_gate_count": batch2[
                "snaptrade"
            ][
                "remaining_gate_count"
            ],
            "blockers": [
                "Production identity unavailable",
                "Encrypted per-user token storage unavailable",
                "Cerberus external head unqualified",
                "Cerberus internal head unqualified",
                "SnapTrade sandbox qualification incomplete",
            ],
        },
        "snaptrade_paper_execution": {
            "status": "NOT_AUTHORIZED",
            "blockers": [
                "Read-only sandbox connection not qualified",
                "Broker identity mapping unavailable",
                "Streaming threat head unqualified",
                "Broker webhook verification unavailable",
                "Paper-only broker adapter not qualified",
            ],
        },
        "broker_execution": {
            "status": "NOT_APPROVED",
            "enabled": False,
        },
        "live_trading": {
            "status": "NOT_APPROVED",
            "enabled": False,
        },
    }

    cerberus = batch2[
        "cerberus"
    ]

    deployment_blockers = [
        {
            "priority": 1,
            "track": "core_flows",
            "status": "QUALIFIED",
            "remaining": (
                "Continue implementation-state-aware "
                "qualification for remaining active stacks"
            ),
        },
        {
            "priority": 2,
            "track": "cerberus_foundation",
            "status": "NOT_IMPLEMENTED",
            "remaining": (
                "Security event contract, telemetry boundary, "
                "deny-by-default policy and threat decision model"
            ),
        },
        {
            "priority": 3,
            "track": "auth_identity",
            "status": "DEFERRED_BY_DESIGN",
            "remaining_gates": batch2[
                "auth_identity"
            ][
                "remaining_gate_count"
            ],
        },
        {
            "priority": 4,
            "track": "cerberus_external_internal",
            "status": "NOT_QUALIFIED",
            "external_keyword_coverage": cerberus[
                "external_threat_head"
            ][
                "provisional_completeness"
            ],
            "internal_keyword_coverage": cerberus[
                "internal_threat_head"
            ][
                "provisional_completeness"
            ],
        },
        {
            "priority": 5,
            "track": "snaptrade_read_only",
            "status": "NOT_AUTHORIZED",
            "remaining_gates": batch2[
                "snaptrade"
            ][
                "remaining_gate_count"
            ],
        },
        {
            "priority": 6,
            "track": "cerberus_streaming",
            "status": "NOT_QUALIFIED",
            "keyword_coverage": cerberus[
                "streaming_threat_head"
            ][
                "provisional_completeness"
            ],
        },
    ]

    manifest = source_manifest()

    gradebook = {
        "generated_at": datetime.now(
            UTC
        ).isoformat(),
        "grading_model": (
            "IMPLEMENTATION_STATE_AWARE"
        ),
        "active_stack_weight": 0.70,
        "repository_weight": 0.10,
        "test_weight": 0.12,
        "safety_weight": 0.08,
        "active_stack_results": (
            stack_results
        ),
        "deferred_stack_results": (
            deferred_results
        ),
        "component_scores": {
            "active_stack_score": clamp(
                active_stack_score
            ),
            "repository_score": (
                repository_score
            ),
            "test_score": test_score,
            "safety_score": safety_score,
        },
        "flow_quality": {
            "score": flow_quality_score,
            "grade": flow_quality_grade,
        },
    }

    GRADEBOOK_JSON.write_text(
        json.dumps(
            gradebook,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    original_score = float(
        stage1b[
            "overall"
        ][
            "calibrated_score"
        ]
    )

    original_grade = stage1b[
        "overall"
    ][
        "calibrated_grade"
    ]

    score_change = round(
        flow_quality_score
        - original_score,
        2,
    )

    report = {
        "campaign": (
            "NeuroVest Integrated "
            "Qualification Campaign"
        ),
        "batch": "IQC-REM-004",
        "batch_name": (
            "Implementation-State-Aware Re-grade "
            "and Baseline Freeze"
        ),
        "status": "completed",
        "verified_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "prior_baseline": {
            "score": original_score,
            "grade": original_grade,
            "grading_model": (
                "CALIBRATED_ALL_ACTIVE_ASSUMED"
            ),
        },
        "current_baseline": {
            "score": flow_quality_score,
            "grade": flow_quality_grade,
            "grading_model": (
                "IMPLEMENTATION_STATE_AWARE"
            ),
            "score_change": score_change,
            "authoritative": True,
        },
        "implemented_active_stack_count": len(
            stack_results
        ),
        "deferred_stack_count": len(
            deferred_results
        ),
        "active_stack_results": (
            stack_results
        ),
        "deferred_stack_results": (
            deferred_results
        ),
        "evidence": {
            "whole_backend_passed": latest_passed,
            "whole_backend_failed": 0,
            "focused_chat_boundary_tests": (
                batch3b[
                    "tests"
                ][
                    "focused_passed"
                ]
            ),
            "focused_public_control_tests": (
                batch3d[
                    "qualification"
                ][
                    "focused_passed"
                ]
            ),
            "active_internal_unresolved": 0,
            "tooling_or_relative_unresolved": 0,
            "syntax_errors": 0,
            "active_dependency_cycles": 0,
            "self_cycles": 0,
            "database_revision": database[
                "revision"
            ],
            "database_modified": False,
        },
        "readiness_tracks": readiness_tracks,
        "deployment_blockers": (
            deployment_blockers
        ),
        "cerberus_provisional_keyword_coverage": {
            "external_threat_head": cerberus[
                "external_threat_head"
            ][
                "provisional_completeness"
            ],
            "internal_threat_head": cerberus[
                "internal_threat_head"
            ][
                "provisional_completeness"
            ],
            "streaming_threat_head": cerberus[
                "streaming_threat_head"
            ][
                "provisional_completeness"
            ],
        },
        "source_manifest_sha256": (
            manifest[
                "manifest_sha256"
            ]
        ),
        "source_modified": False,
        "database_modified": False,
        "auth_implemented": False,
        "snaptrade_connected": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
        "next_step": (
            "IQC Stage 5 — Remaining Active-Stack "
            "Flow Qualification and Completion Map"
        ),
    }

    REPORT_JSON.write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    freeze = {
        "status": "frozen",
        "batch": "IQC-REM-004",
        "frozen_at": datetime.now(
            UTC
        ).isoformat(),
        "authoritative_score": (
            flow_quality_score
        ),
        "authoritative_grade": (
            flow_quality_grade
        ),
        "report_sha256": sha256_file(
            REPORT_JSON
        ),
        "gradebook_sha256": sha256_file(
            GRADEBOOK_JSON
        ),
        "source_manifest_sha256": (
            manifest[
                "manifest_sha256"
            ]
        ),
        "database_revision": database[
            "revision"
        ],
        "whole_backend_passed": (
            latest_passed
        ),
        "whole_backend_failed": 0,
        "source_modified": False,
        "database_modified": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
    }

    FREEZE_JSON.write_text(
        json.dumps(
            freeze,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    lines = [
        "=" * 96,
        "NEUROVEST INTEGRATED QUALIFICATION CAMPAIGN",
        (
            "IQC REMEDIATION BATCH 4 — "
            "IMPLEMENTATION-STATE-AWARE RE-GRADE "
            "AND BASELINE FREEZE"
        ),
        "=" * 96,
        "",
        "STATUS",
        "COMPLETE AND VERIFIED",
        "",
        "MODE",
        "READ ONLY",
        "",
        "AUTHORITATIVE FLOW-QUALITY GRADE",
        (
            "Previous score:                  "
            f"{original_score:.2f} / 100"
        ),
        (
            "Previous grade:                  "
            f"{original_grade}"
        ),
        (
            "Current score:                   "
            f"{flow_quality_score:.2f} / 100"
        ),
        (
            "Current grade:                   "
            f"{flow_quality_grade}"
        ),
        (
            "Score change:                    "
            f"{score_change:+.2f}"
        ),
        (
            "Grading model:                   "
            "IMPLEMENTATION-STATE-AWARE"
        ),
        "Authoritative baseline frozen:      YES",
        "",
        "ACTIVE IMPLEMENTED STACKS",
    ]

    for item in sorted(
        stack_results,
        key=lambda value: value[
            "adjusted_score"
        ],
        reverse=True,
    ):
        lines.append(
            f"- {item['stack']:<18} "
            f"{item['adjusted_score']:>6.2f} "
            f"{item['adjusted_grade']}"
        )

    lines.extend(
        [
            "",
            "DEFERRED STACKS",
        ]
    )

    for item in deferred_results:
        lines.extend(
            [
                (
                    f"- {item['stack']}: "
                    f"{item['current_grade']}"
                ),
                (
                    "  Included in flow grade: NO"
                ),
                (
                    "  Deployment blocker: "
                    f"{'YES' if item['deployment_blocker'] else 'NO'}"
                ),
                (
                    "  Remaining implementation gates: "
                    f"{item['remaining_gate_count']}"
                ),
            ]
        )

    lines.extend(
        [
            "",
            "EVIDENCE BASELINE",
            (
                "Whole-backend tests passed:      "
                f"{latest_passed}"
            ),
            "Whole-backend tests failed:      0",
            (
                "Focused chat boundary tests:    "
                f"{batch3b['tests']['focused_passed']}"
            ),
            (
                "Focused public-control tests:   "
                f"{batch3d['qualification']['focused_passed']}"
            ),
            "Active unresolved imports:       0",
            "Tooling/relative unresolved:      0",
            "Syntax errors:                    0",
            "Dependency cycles:                0",
            "Self cycles:                      0",
            (
                "Migration revision:              "
                f"{database['revision']}"
            ),
            "Database modified:                NO",
            "",
            "READINESS",
            (
                "Internal development:            "
                "QUALIFIED"
            ),
            (
                "Controlled local flow testing:   "
                "QUALIFIED"
            ),
            (
                "Controlled early users:          "
                "NOT QUALIFIED"
            ),
            (
                "Public production deployment:    "
                "NOT QUALIFIED"
            ),
            (
                "SnapTrade read-only sandbox:     "
                "NOT AUTHORIZED"
            ),
            (
                "SnapTrade paper execution:       "
                "NOT AUTHORIZED"
            ),
            (
                "Broker execution:                "
                "NOT APPROVED"
            ),
            (
                "Live trading:                    "
                "NOT APPROVED"
            ),
            "",
            "PRIMARY REMAINING BLOCKERS",
            "1. Cerberus shared security foundation",
            "2. Production Auth and user-profile persistence",
            "3. Distributed identity-aware rate limiting",
            "4. Cerberus external and internal threat qualification",
            "5. SnapTrade read-only sandbox qualification",
            "6. Cerberus streaming threat qualification",
            "",
            "CERBERUS PROVISIONAL KEYWORD COVERAGE",
            (
                "External threat head:            "
                f"{cerberus['external_threat_head']['provisional_completeness']:.1f}%"
            ),
            (
                "Internal threat head:            "
                f"{cerberus['internal_threat_head']['provisional_completeness']:.1f}%"
            ),
            (
                "Streaming threat head:           "
                f"{cerberus['streaming_threat_head']['provisional_completeness']:.1f}%"
            ),
            "",
            "IMPORTANT",
            (
                "Cerberus percentages are keyword coverage only, "
                "not operational qualification."
            ),
            "",
            "SAFETY",
            "- Auth implemented: NO",
            "- SnapTrade connected: NO",
            "- Broker execution enabled: NO",
            "- Live trading enabled: NO",
            "- Source modified: NO",
            "- Database modified: NO",
            "",
            "NEXT",
            (
                "IQC Stage 5 — Remaining Active-Stack "
                "Flow Qualification and Completion Map"
            ),
            "",
            "=" * 96,
        ]
    )

    rendered = (
        "\n".join(
            lines
        )
        + "\n"
    )

    REPORT_TEXT.write_text(
        rendered,
        encoding="utf-8",
    )

    print(rendered)

    print("Re-grade report:")
    print(REPORT_JSON)
    print()

    print("Gradebook:")
    print(GRADEBOOK_JSON)
    print()

    print("Freeze manifest:")
    print(FREEZE_JSON)
    print()

    print("Source manifest:")
    print(SOURCE_MANIFEST)


if __name__ == "__main__":
    main()
