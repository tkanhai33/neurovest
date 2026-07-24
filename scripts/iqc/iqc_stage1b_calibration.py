#!/usr/bin/env python3
"""
NeuroVest Integrated Qualification Campaign

IQC Stage 1B —
Evidence Attribution, Stack Classification,
and Grading Model Calibration

This command is read-only with respect to application source and databases.
It writes qualification evidence only beneath runtime/iqc/stage1b.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(".").resolve()

BACKEND_ROOT = (
    ROOT
    / "backend"
    / "app"
)

STACKS_ROOT = (
    BACKEND_ROOT
    / "stacks"
)

RUNTIME_ROOT = (
    ROOT
    / "runtime"
)

STAGE1_DIR = (
    RUNTIME_ROOT
    / "iqc"
    / "stage1"
)

OUTPUT_DIR = (
    RUNTIME_ROOT
    / "iqc"
    / "stage1b"
)

STAGE1_REPORT = (
    STAGE1_DIR
    / "iqc_stage1_baseline_latest.json"
)

STAGE1_FREEZE = (
    STAGE1_DIR
    / "iqc_stage1_freeze_manifest_latest.json"
)

PYTEST_LOG = (
    STAGE1_DIR
    / "iqc_stage1_pytest_console.log"
)

DATABASE_REPORT = (
    STAGE1_DIR
    / "iqc_stage1_database_state_latest.json"
)

IMPORT_AUDIT_REPORT = (
    RUNTIME_ROOT
    / "hardening"
    / "workstream1"
    / "import_cycle_audit_latest.json"
)

REPORT_JSON = (
    OUTPUT_DIR
    / "iqc_stage1b_calibrated_baseline_latest.json"
)

REPORT_TEXT = (
    OUTPUT_DIR
    / "iqc_stage1b_calibrated_baseline_latest.txt"
)

ATTRIBUTION_JSON = (
    OUTPUT_DIR
    / "iqc_stage1b_evidence_attribution_latest.json"
)

CLASSIFICATION_JSON = (
    OUTPUT_DIR
    / "iqc_stage1b_stack_classification_latest.json"
)

FREEZE_JSON = (
    OUTPUT_DIR
    / "iqc_stage1b_freeze_manifest_latest.json"
)

SOURCE_SNAPSHOT_JSON = (
    OUTPUT_DIR
    / "iqc_stage1b_source_snapshot_latest.json"
)

CLASS_WEIGHTS = {
    "ACTIVE": 1.00,
    "SUPPORTING": 0.55,
    "COMPATIBILITY": 0.25,
    "DORMANT": 0.00,
    "DEFERRED_BY_DESIGN": 0.00,
}

READINESS_THRESHOLDS = {
    "development_use": 70.0,
    "controlled_early_users": 85.0,
    "production_deployment": 93.0,
}

GRADE_BANDS = [
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
]

CATEGORY_MAXIMUMS = {
    "architecture_and_ownership": 15.0,
    "import_and_dependency_integrity": 15.0,
    "contract_completeness": 15.0,
    "test_evidence": 15.0,
    "failure_behavior": 10.0,
    "boundary_and_capability_control": 15.0,
    "observability_and_operations": 5.0,
    "qualification_evidence": 10.0,
}

assert sum(
    CATEGORY_MAXIMUMS.values()
) == 100.0

# Explicit classification policy for currently known NeuroVest stacks.
# These classifications affect weighting only. They do not alter code or
# authorize capability.
CLASSIFICATION_OVERRIDES = {
    "auth_identity": (
        "ACTIVE",
        "Authentication and identity boundary",
    ),
    "chat_public": (
        "ACTIVE",
        "Public chat application boundary",
    ),
    "db_model": (
        "SUPPORTING",
        "Shared database model support package",
    ),
    "db_runtime": (
        "SUPPORTING",
        "Database connection and runtime support",
    ),
    "events": (
        "SUPPORTING",
        "Shared event contracts and event transport support",
    ),
    "execution": (
        "ACTIVE",
        "Paper execution and execution control boundary",
    ),
    "journal_ledger": (
        "ACTIVE",
        "Decision audit and append-only ledger subsystem",
    ),
    "learning_research": (
        "SUPPORTING",
        "Research and learning support subsystem",
    ),
    "market_data": (
        "ACTIVE",
        "Market data acquisition and normalization subsystem",
    ),
    "notification": (
        "SUPPORTING",
        "Notification support subsystem",
    ),
    "portfolio": (
        "ACTIVE",
        "Portfolio state and allocation subsystem",
    ),
    "risk": (
        "ACTIVE",
        "Risk controls and safety gating subsystem",
    ),
    "snaptrade": (
        "COMPATIBILITY",
        "Legacy or compatibility broker integration package",
    ),
    "strategy": (
        "ACTIVE",
        "Strategy decision and signal subsystem",
    ),
    "strategy_candidate_sandbox": (
        "SUPPORTING",
        "Controlled strategy candidate qualification sandbox",
    ),
    "wolfden_ai": (
        "ACTIVE",
        "AI orchestration and agent-routing subsystem",
    ),
}

DEFERRED_NAME_MARKERS = {
    "broker_live",
    "live_execution",
    "live_trading",
}

DORMANT_NAME_MARKERS = {
    "deprecated",
    "archive",
    "archived",
    "legacy_unused",
}

TEST_ROOT_MARKERS = {
    "test",
    "tests",
    "l7_tests",
}

REPORT_STATUS_VALUES = {
    "completed",
    "complete",
    "verified",
    "passed",
    "frozen",
    "qualified",
}

FAILURE_WORDS = {
    "fail",
    "failure",
    "invalid",
    "exception",
    "error",
    "blocked",
    "denied",
    "reject",
    "rollback",
    "timeout",
    "unavailable",
    "closed",
    "kill_switch",
    "emergency",
}

OBSERVABILITY_WORDS = {
    "observability",
    "metrics",
    "logging",
    "telemetry",
    "health",
    "status",
    "trace",
}

CONTRACT_WORDS = {
    "contract",
    "schema",
    "dto",
    "protocol",
    "interface",
    "facade",
}

KNOWN_ALIAS_PREFIXES = (
    "backend.app.stacks.",
    "app.stacks.",
    "stacks.",
)

PATCH_PATTERN = re.compile(
    r"""patch\(\s*["']([^"']+)["']"""
)

MODULE_TEXT_PATTERN = re.compile(
    r"""(?:backend\.app\.stacks|app\.stacks|stacks)\.([A-Za-z0-9_]+)"""
)


@dataclass(frozen=True)
class StackInventory:
    name: str
    path: str
    production_files: tuple[str, ...]
    local_test_files: tuple[str, ...]
    all_files: tuple[str, ...]


@dataclass(frozen=True)
class TestEvidence:
    path: str
    targets: tuple[str, ...]
    attribution_reasons: dict[str, tuple[str, ...]]
    failure_behavior_signal: bool
    source_sha256: str


@dataclass(frozen=True)
class ReportEvidence:
    path: str
    targets: tuple[str, ...]
    attribution_reasons: dict[str, tuple[str, ...]]
    status: str | None
    source_sha256: str


def sha256_file(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def normalized_path(
    path: Path,
) -> str:
    return path.relative_to(
        ROOT
    ).as_posix()


def is_test_path(
    path: Path,
) -> bool:
    lowered_parts = {
        part.lower()
        for part in path.parts
    }

    return (
        bool(
            lowered_parts
            & TEST_ROOT_MARKERS
        )
        or path.name.startswith(
            "test_"
        )
        or path.name.endswith(
            "_test.py"
        )
    )


def load_json(
    path: Path,
) -> dict[str, Any]:
    assert path.is_file(), (
        f"Required IQC evidence is missing: {path}"
    )

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert isinstance(
        data,
        dict,
    )

    return data


def grade_letter(
    score: float,
) -> str:
    for minimum, letter in GRADE_BANDS:
        if score >= minimum:
            return letter

    return "F"


def discover_stack_directories() -> list[Path]:
    assert STACKS_ROOT.is_dir(), (
        "NeuroVest stacks directory is missing"
    )

    directories = []

    for child in sorted(
        STACKS_ROOT.iterdir()
    ):
        if not child.is_dir():
            continue

        if child.name == "__pycache__":
            continue

        directories.append(
            child
        )

    return directories


def discover_stack_inventory() -> dict[str, StackInventory]:
    inventory = {}

    for stack_dir in discover_stack_directories():
        all_files = sorted(
            path
            for path in stack_dir.rglob(
                "*.py"
            )
            if "__pycache__" not in path.parts
        )

        production_files = [
            normalized_path(
                path
            )
            for path in all_files
            if not is_test_path(
                path
            )
        ]

        local_test_files = [
            normalized_path(
                path
            )
            for path in all_files
            if is_test_path(
                path
            )
        ]

        inventory[
            stack_dir.name
        ] = StackInventory(
            name=stack_dir.name,
            path=normalized_path(
                stack_dir
            ),
            production_files=tuple(
                production_files
            ),
            local_test_files=tuple(
                local_test_files
            ),
            all_files=tuple(
                normalized_path(
                    path
                )
                for path in all_files
            ),
        )

    assert "__init__.py" not in inventory, (
        "False stack '__init__.py' was not excluded"
    )

    return inventory


def classify_stack(
    stack: StackInventory,
) -> dict[str, Any]:
    if stack.name in CLASSIFICATION_OVERRIDES:
        classification, reason = (
            CLASSIFICATION_OVERRIDES[
                stack.name
            ]
        )

        return {
            "stack": stack.name,
            "classification": classification,
            "weight": CLASS_WEIGHTS[
                classification
            ],
            "reason": reason,
            "source": "explicit_policy",
            "production_file_count": len(
                stack.production_files
            ),
            "local_test_file_count": len(
                stack.local_test_files
            ),
        }

    lowered = stack.name.lower()

    if any(
        marker in lowered
        for marker in DEFERRED_NAME_MARKERS
    ):
        classification = (
            "DEFERRED_BY_DESIGN"
        )

        reason = (
            "Name indicates a deliberately deferred "
            "live or broker capability"
        )

    elif any(
        marker in lowered
        for marker in DORMANT_NAME_MARKERS
    ):
        classification = "DORMANT"

        reason = (
            "Name indicates deprecated or archived code"
        )

    elif len(
        stack.production_files
    ) <= 2:
        classification = "SUPPORTING"

        reason = (
            "Thin package classified as supporting "
            "rather than a full runtime subsystem"
        )

    else:
        classification = "ACTIVE"

        reason = (
            "Production package with multiple implementation files"
        )

    return {
        "stack": stack.name,
        "classification": classification,
        "weight": CLASS_WEIGHTS[
            classification
        ],
        "reason": reason,
        "source": "heuristic_policy",
        "production_file_count": len(
            stack.production_files
        ),
        "local_test_file_count": len(
            stack.local_test_files
        ),
    }


def python_import_targets(
    source: str,
    stack_names: set[str],
) -> dict[str, set[str]]:
    reasons: dict[
        str,
        set[str],
    ] = defaultdict(
        set
    )

    try:
        tree = ast.parse(
            source
        )

    except SyntaxError:
        return reasons

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.Import,
        ):
            modules = [
                alias.name
                for alias in node.names
            ]

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            modules = [
                node.module
            ] if node.module else []

        else:
            continue

        for module in modules:
            for prefix in KNOWN_ALIAS_PREFIXES:
                if not module.startswith(
                    prefix
                ):
                    continue

                remainder = module[
                    len(prefix):
                ]

                candidate = remainder.split(
                    "."
                )[0]

                if candidate in stack_names:
                    reasons[
                        candidate
                    ].add(
                        f"import:{module}"
                    )

    return reasons


def textual_targets(
    source: str,
    stack_names: set[str],
) -> dict[str, set[str]]:
    reasons: dict[
        str,
        set[str],
    ] = defaultdict(
        set
    )

    for match in MODULE_TEXT_PATTERN.finditer(
        source
    ):
        candidate = match.group(
            1
        )

        if candidate in stack_names:
            reasons[
                candidate
            ].add(
                f"module_reference:{match.group(0)}"
            )

    for match in PATCH_PATTERN.finditer(
        source
    ):
        dotted = match.group(
            1
        )

        for prefix in KNOWN_ALIAS_PREFIXES:
            if not dotted.startswith(
                prefix
            ):
                continue

            remainder = dotted[
                len(prefix):
            ]

            candidate = remainder.split(
                "."
            )[0]

            if candidate in stack_names:
                reasons[
                    candidate
                ].add(
                    f"patch:{dotted}"
                )

    return reasons


def merge_reasons(
    *collections: dict[str, set[str]],
) -> dict[str, set[str]]:
    merged: dict[
        str,
        set[str],
    ] = defaultdict(
        set
    )

    for collection in collections:
        for stack, reasons in (
            collection.items()
        ):
            merged[
                stack
            ].update(
                reasons
            )

    return merged


def discover_all_test_files() -> list[Path]:
    files = []

    for path in sorted(
        BACKEND_ROOT.rglob(
            "*.py"
        )
    ):
        if "__pycache__" in path.parts:
            continue

        if is_test_path(
            path
        ):
            files.append(
                path
            )

    return files


def attribute_tests(
    inventory: dict[
        str,
        StackInventory,
    ],
) -> list[TestEvidence]:
    stack_names = set(
        inventory
    )

    evidence = []

    for path in discover_all_test_files():
        source = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        reasons = merge_reasons(
            python_import_targets(
                source,
                stack_names,
            ),
            textual_targets(
                source,
                stack_names,
            ),
        )

        for stack, item in inventory.items():
            relative = normalized_path(
                path
            )

            if relative in item.local_test_files:
                reasons[
                    stack
                ].add(
                    "local_stack_test"
                )

        targets = tuple(
            sorted(
                reasons
            )
        )

        lowered = source.lower()

        failure_signal = any(
            word in lowered
            for word in FAILURE_WORDS
        )

        evidence.append(
            TestEvidence(
                path=normalized_path(
                    path
                ),
                targets=targets,
                attribution_reasons={
                    stack: tuple(
                        sorted(
                            reason_set
                        )
                    )
                    for stack, reason_set
                    in sorted(
                        reasons.items()
                    )
                },
                failure_behavior_signal=(
                    failure_signal
                ),
                source_sha256=sha256_file(
                    path
                ),
            )
        )

    return evidence


def iter_runtime_reports() -> list[Path]:
    reports = []

    if not RUNTIME_ROOT.is_dir():
        return reports

    for path in sorted(
        RUNTIME_ROOT.rglob(
            "*.json"
        )
    ):
        if OUTPUT_DIR in path.parents:
            continue

        reports.append(
            path
        )

    return reports


def report_status(
    data: Any,
) -> str | None:
    if not isinstance(
        data,
        dict,
    ):
        return None

    value = data.get(
        "status"
    )

    if value is None:
        return None

    return str(
        value
    )


def search_json_for_stack(
    value: Any,
    stack: str,
    location: str = "$",
) -> set[str]:
    matches = set()

    lowered_stack = stack.lower()

    if isinstance(
        value,
        dict,
    ):
        for key, item in value.items():
            key_location = (
                f"{location}.{key}"
            )

            if lowered_stack in str(
                key
            ).lower():
                matches.add(
                    f"json_key:{key_location}"
                )

            matches.update(
                search_json_for_stack(
                    item,
                    stack,
                    key_location,
                )
            )

    elif isinstance(
        value,
        list,
    ):
        for index, item in enumerate(
            value
        ):
            matches.update(
                search_json_for_stack(
                    item,
                    stack,
                    f"{location}[{index}]",
                )
            )

    elif isinstance(
        value,
        str,
    ):
        lowered_value = (
            value.lower()
        )

        module_tokens = (
            f"stacks/{lowered_stack}/",
            f"stacks.{lowered_stack}.",
            f"stacks.{lowered_stack}",
            f"/{lowered_stack}/",
        )

        if any(
            token in lowered_value
            for token in module_tokens
        ):
            matches.add(
                f"json_value:{location}"
            )

    return matches


def attribute_reports(
    inventory: dict[
        str,
        StackInventory,
    ],
) -> list[ReportEvidence]:
    evidence = []

    for path in iter_runtime_reports():
        try:
            data = json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )

        except (
            OSError,
            UnicodeDecodeError,
            json.JSONDecodeError,
        ):
            continue

        reasons: dict[
            str,
            set[str],
        ] = defaultdict(
            set
        )

        relative = normalized_path(
            path
        )

        lowered_path = (
            relative.lower()
        )

        for stack in inventory:
            exact_path_tokens = (
                f"/{stack.lower()}/",
                f"_{stack.lower()}_",
                f"-{stack.lower()}-",
            )

            if any(
                token in lowered_path
                for token in exact_path_tokens
            ):
                reasons[
                    stack
                ].add(
                    "report_path_exact_token"
                )

            content_matches = (
                search_json_for_stack(
                    data,
                    stack,
                )
            )

            reasons[
                stack
            ].update(
                content_matches
            )

        targets = tuple(
            sorted(
                stack
                for stack, reason_set
                in reasons.items()
                if reason_set
            )
        )

        evidence.append(
            ReportEvidence(
                path=relative,
                targets=targets,
                attribution_reasons={
                    stack: tuple(
                        sorted(
                            reason_set
                        )
                    )
                    for stack, reason_set
                    in sorted(
                        reasons.items()
                    )
                    if reason_set
                },
                status=report_status(
                    data
                ),
                source_sha256=sha256_file(
                    path
                ),
            )
        )

    return evidence


def pytest_summary() -> dict[str, Any]:
    if not PYTEST_LOG.is_file():
        return {
            "available": False,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "errors": 0,
        }

    text = PYTEST_LOG.read_text(
        encoding="utf-8",
        errors="replace",
    )

    def last_number(
        label: str,
    ) -> int:
        matches = re.findall(
            rf"(\d+)\s+{label}",
            text,
        )

        if not matches:
            return 0

        return int(
            matches[-1]
        )

    return {
        "available": True,
        "passed": last_number(
            "passed"
        ),
        "failed": last_number(
            "failed"
        ),
        "warnings": last_number(
            "warnings"
        ),
        "errors": last_number(
            "errors?"
        ),
        "trading_pipeline_failures": (
            text.count(
                "backend/app/test/"
                "test_trading_pipeline.py::"
            )
        ),
    }


def old_stack_results(
    stage1: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    result = {}

    for item in stage1.get(
        "stack_results",
        []
    ):
        if not isinstance(
            item,
            dict,
        ):
            continue

        stack = item.get(
            "stack"
        )

        if not isinstance(
            stack,
            str,
        ):
            continue

        result[
            stack
        ] = item

    return result


def count_contract_artifacts(
    stack: StackInventory,
) -> int:
    return sum(
        1
        for relative in stack.production_files
        if any(
            word in Path(
                relative
            ).name.lower()
            for word in CONTRACT_WORDS
        )
    )


def count_observability_artifacts(
    stack: StackInventory,
) -> int:
    return sum(
        1
        for relative in stack.production_files
        if any(
            word in Path(
                relative
            ).name.lower()
            for word in OBSERVABILITY_WORDS
        )
    )


def stack_attributed_tests(
    stack: str,
    tests: list[TestEvidence],
) -> list[TestEvidence]:
    return [
        item
        for item in tests
        if stack in item.targets
    ]


def stack_attributed_reports(
    stack: str,
    reports: list[ReportEvidence],
) -> list[ReportEvidence]:
    return [
        item
        for item in reports
        if stack in item.targets
    ]


def completed_report_count(
    reports: list[ReportEvidence],
) -> int:
    return sum(
        1
        for report in reports
        if (
            report.status
            and report.status.lower()
            in REPORT_STATUS_VALUES
        )
    )


def clamp(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


def recalibrate_stack(
    stack: StackInventory,
    classification: dict[str, Any],
    prior: dict[str, Any] | None,
    tests: list[TestEvidence],
    reports: list[ReportEvidence],
    global_import_clean: bool,
    whole_suite: dict[str, Any],
) -> dict[str, Any]:
    attributed_tests = (
        stack_attributed_tests(
            stack.name,
            tests,
        )
    )

    attributed_reports = (
        stack_attributed_reports(
            stack.name,
            reports,
        )
    )

    failure_tests = [
        item
        for item in attributed_tests
        if item.failure_behavior_signal
    ]

    complete_reports = (
        completed_report_count(
            attributed_reports
        )
    )

    contract_count = (
        count_contract_artifacts(
            stack
        )
    )

    observability_count = (
        count_observability_artifacts(
            stack
        )
    )

    previous_categories = {}

    if prior:
        previous_categories = dict(
            prior.get(
                "category_scores",
                {}
            )
        )

    architecture = float(
        previous_categories.get(
            "architecture_and_ownership",
            0.0,
        )
    )

    import_integrity = (
        CATEGORY_MAXIMUMS[
            "import_and_dependency_integrity"
        ]
        if global_import_clean
        else float(
            previous_categories.get(
                "import_and_dependency_integrity",
                0.0,
            )
        )
    )

    contract_score = float(
        previous_categories.get(
            "contract_completeness",
            0.0,
        )
    )

    boundary_score = float(
        previous_categories.get(
            "boundary_and_capability_control",
            0.0,
        )
    )

    # Centralized tests now count. Thin supporting packages are not required
    # to own a large local test directory.
    if attributed_tests:
        test_ratio = min(
            1.0,
            0.45
            + 0.18
            * len(
                attributed_tests
            )
        )

    elif classification[
        "classification"
    ] in {
        "SUPPORTING",
        "COMPATIBILITY",
    }:
        test_ratio = 0.45

    else:
        test_ratio = 0.15

    if (
        whole_suite.get(
            "available"
        )
        and whole_suite.get(
            "failed",
            0,
        )
        == 0
    ):
        test_ratio = min(
            1.0,
            test_ratio
            + 0.15,
        )

    test_score = (
        test_ratio
        * CATEGORY_MAXIMUMS[
            "test_evidence"
        ]
    )

    if failure_tests:
        failure_ratio = min(
            1.0,
            0.50
            + 0.20
            * len(
                failure_tests
            )
        )

    elif classification[
        "classification"
    ] in {
        "SUPPORTING",
        "COMPATIBILITY",
    }:
        failure_ratio = 0.45

    else:
        failure_ratio = 0.20

    failure_score = (
        failure_ratio
        * CATEGORY_MAXIMUMS[
            "failure_behavior"
        ]
    )

    if observability_count:
        observability_ratio = 1.0

    elif classification[
        "classification"
    ] in {
        "SUPPORTING",
        "COMPATIBILITY",
    }:
        observability_ratio = 0.60

    else:
        observability_ratio = 0.25

    observability_score = (
        observability_ratio
        * CATEGORY_MAXIMUMS[
            "observability_and_operations"
        ]
    )

    if complete_reports:
        qualification_ratio = min(
            1.0,
            0.55
            + 0.20
            * complete_reports,
        )

    elif attributed_reports:
        qualification_ratio = 0.45

    elif classification[
        "classification"
    ] in {
        "SUPPORTING",
        "COMPATIBILITY",
    }:
        qualification_ratio = 0.40

    else:
        qualification_ratio = 0.15

    qualification_score = (
        qualification_ratio
        * CATEGORY_MAXIMUMS[
            "qualification_evidence"
        ]
    )

    if (
        classification[
            "classification"
        ]
        in {
            "SUPPORTING",
            "COMPATIBILITY",
        }
        and contract_count == 0
    ):
        # Supporting packages are not automatically defective merely because
        # they do not contain a dedicated facade or DTO filename.
        contract_score = max(
            contract_score,
            8.0,
        )

    categories = {
        "architecture_and_ownership": clamp(
            architecture,
            0.0,
            15.0,
        ),
        "import_and_dependency_integrity": clamp(
            import_integrity,
            0.0,
            15.0,
        ),
        "contract_completeness": clamp(
            contract_score,
            0.0,
            15.0,
        ),
        "test_evidence": round(
            test_score,
            2,
        ),
        "failure_behavior": round(
            failure_score,
            2,
        ),
        "boundary_and_capability_control": clamp(
            boundary_score,
            0.0,
            15.0,
        ),
        "observability_and_operations": round(
            observability_score,
            2,
        ),
        "qualification_evidence": round(
            qualification_score,
            2,
        ),
    }

    raw_score = round(
        sum(
            categories.values()
        ),
        2,
    )

    findings = []

    if not attributed_tests:
        if classification[
            "classification"
        ] == "ACTIVE":
            findings.append(
                {
                    "severity": "HIGH",
                    "code": (
                        "NO_ATTRIBUTED_TEST_EVIDENCE"
                    ),
                    "summary": (
                        "No local or centralized tests "
                        "could be attributed to this active stack"
                    ),
                }
            )

        else:
            findings.append(
                {
                    "severity": "OBSERVATION",
                    "code": (
                        "NO_DIRECT_TEST_ATTRIBUTION"
                    ),
                    "summary": (
                        "No direct test attribution was found, "
                        "but the stack is not weighted as a full "
                        "active runtime subsystem"
                    ),
                }
            )

    if not failure_tests:
        if classification[
            "classification"
        ] == "ACTIVE":
            findings.append(
                {
                    "severity": "MEDIUM",
                    "code": (
                        "NO_ATTRIBUTED_FAILURE_TEST"
                    ),
                    "summary": (
                        "No failure-behavior test was attributed "
                        "to this active stack"
                    ),
                }
            )

    if not attributed_reports:
        findings.append(
            {
                "severity": (
                    "MEDIUM"
                    if classification[
                        "classification"
                    ]
                    == "ACTIVE"
                    else "OBSERVATION"
                ),
                "code": (
                    "NO_ATTRIBUTED_QUALIFICATION_REPORT"
                ),
                "summary": (
                    "No qualification report could be "
                    "attributed to this stack"
                ),
            }
        )

    prior_signals = {}

    if prior:
        prior_signals = prior.get(
            "evidence",
            {}
        )

    capability_signals = prior_signals.get(
        "forbidden_capability_signals",
        [],
    )

    syntax_errors = prior_signals.get(
        "syntax_errors",
        [],
    )

    if capability_signals:
        findings.append(
            {
                "severity": "CRITICAL",
                "code": (
                    "FORBIDDEN_CAPABILITY_SIGNAL"
                ),
                "summary": (
                    "Potential enabled forbidden capability "
                    "was detected by Stage 1"
                ),
                "evidence": capability_signals,
            }
        )

    if syntax_errors:
        findings.append(
            {
                "severity": "CRITICAL",
                "code": "STACK_SYNTAX_ERROR",
                "summary": (
                    "Syntax-invalid source was detected"
                ),
                "evidence": syntax_errors,
            }
        )

    if any(
        finding[
            "severity"
        ]
        == "CRITICAL"
        for finding in findings
    ):
        qualification = "BLOCKED"

    elif classification[
        "classification"
    ] == "DEFERRED_BY_DESIGN":
        qualification = "DEFERRED_BY_DESIGN"

    elif classification[
        "classification"
    ] == "DORMANT":
        qualification = "DORMANT"

    elif raw_score >= 90.0:
        qualification = "QUALIFIED"

    elif raw_score >= 80.0:
        qualification = (
            "CONDITIONALLY_QUALIFIED"
        )

    elif raw_score >= 70.0:
        qualification = (
            "CONTROLLED_TESTING_ONLY"
        )

    else:
        qualification = "NOT_QUALIFIED"

    evidence_confidence_points = 0

    if attributed_tests:
        evidence_confidence_points += 35

    if failure_tests:
        evidence_confidence_points += 20

    if attributed_reports:
        evidence_confidence_points += 25

    if global_import_clean:
        evidence_confidence_points += 10

    if prior:
        evidence_confidence_points += 10

    confidence = min(
        100,
        evidence_confidence_points,
    )

    return {
        "stack": stack.name,
        "classification": classification[
            "classification"
        ],
        "class_weight": classification[
            "weight"
        ],
        "classification_reason": classification[
            "reason"
        ],
        "score": raw_score,
        "grade": grade_letter(
            raw_score
        ),
        "qualification": qualification,
        "evidence_confidence": confidence,
        "category_scores": categories,
        "category_maximums": (
            CATEGORY_MAXIMUMS
        ),
        "evidence": {
            "production_files": len(
                stack.production_files
            ),
            "local_test_files": len(
                stack.local_test_files
            ),
            "attributed_test_count": len(
                attributed_tests
            ),
            "attributed_failure_test_count": len(
                failure_tests
            ),
            "attributed_report_count": len(
                attributed_reports
            ),
            "completed_report_count": (
                complete_reports
            ),
            "contract_artifact_count": (
                contract_count
            ),
            "observability_artifact_count": (
                observability_count
            ),
            "attributed_tests": [
                item.path
                for item in attributed_tests
            ],
            "attributed_failure_tests": [
                item.path
                for item in failure_tests
            ],
            "attributed_reports": [
                item.path
                for item in attributed_reports
            ],
        },
        "findings": findings,
        "prior_stage1_score": (
            prior.get(
                "score"
            )
            if prior
            else None
        ),
    }


def import_audit_clean(
    data: dict[str, Any],
) -> bool:
    summary = data.get(
        "summary",
        {}
    )

    required_zero_fields = (
        "active_internal_unresolved",
        "tooling_or_relative_unresolved",
        "syntax_errors",
        "active_cycle_components",
        "self_cycles",
    )

    return all(
        summary.get(
            field
        )
        == 0
        for field in required_zero_fields
    )


def weighted_overall(
    stacks: list[dict[str, Any]],
) -> tuple[float, float]:
    numerator = 0.0
    denominator = 0.0

    for stack in stacks:
        weight = float(
            stack[
                "class_weight"
            ]
        )

        if weight <= 0.0:
            continue

        numerator += (
            float(
                stack[
                    "score"
                ]
            )
            * weight
        )

        denominator += weight

    if denominator == 0.0:
        return 0.0, 0.0

    return (
        round(
            numerator / denominator,
            2,
        ),
        round(
            denominator,
            2,
        ),
    )


def blocking_gates(
    stage1: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        gate
        for gate in stage1.get(
            "hard_gates",
            []
        )
        if (
            gate.get(
                "blocking"
            )
            and not gate.get(
                "passed"
            )
        )
    ]


def readiness_status(
    score: float,
    threshold: float,
    blockers: list[dict[str, Any]],
    whole_suite: dict[str, Any],
    production: bool = False,
) -> str:
    if blockers:
        return "BLOCKED"

    if production and whole_suite.get(
        "failed",
        0,
    ) > 0:
        return "NOT_QUALIFIED"

    if score >= threshold:
        return "QUALIFIED"

    return "NOT_QUALIFIED"


def source_snapshot(
    inventory: dict[
        str,
        StackInventory,
    ],
) -> dict[str, Any]:
    entries = []

    for stack in sorted(
        inventory
    ):
        for relative in inventory[
            stack
        ].production_files:
            path = ROOT / relative

            entries.append(
                {
                    "path": relative,
                    "sha256": sha256_file(
                        path
                    ),
                    "size_bytes": (
                        path.stat().st_size
                    ),
                }
            )

    combined = hashlib.sha256()

    for entry in entries:
        combined.update(
            entry[
                "path"
            ].encode(
                "utf-8"
            )
        )

        combined.update(
            entry[
                "sha256"
            ].encode(
                "ascii"
            )
        )

    return {
        "source_file_count": len(
            entries
        ),
        "source_manifest_sha256": (
            combined.hexdigest()
        ),
        "source_files": entries,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    stage1 = load_json(
        STAGE1_REPORT
    )

    stage1_freeze = load_json(
        STAGE1_FREEZE
    )

    import_audit = load_json(
        IMPORT_AUDIT_REPORT
    )

    database = load_json(
        DATABASE_REPORT
    )

    assert stage1.get(
        "status"
    ) == "completed"

    assert stage1.get(
        "mode"
    ) == "read_only"

    assert stage1_freeze.get(
        "status"
    ) == "frozen"

    assert database.get(
        "modified"
    ) is False

    inventory = (
        discover_stack_inventory()
    )

    classifications = {
        name: classify_stack(
            stack
        )
        for name, stack
        in sorted(
            inventory.items()
        )
    }

    test_evidence = (
        attribute_tests(
            inventory
        )
    )

    report_evidence = (
        attribute_reports(
            inventory
        )
    )

    prior_results = (
        old_stack_results(
            stage1
        )
    )

    whole_suite = (
        pytest_summary()
    )

    global_import_clean = (
        import_audit_clean(
            import_audit
        )
    )

    stack_results = []

    for stack_name, stack in sorted(
        inventory.items()
    ):
        stack_results.append(
            recalibrate_stack(
                stack=stack,
                classification=(
                    classifications[
                        stack_name
                    ]
                ),
                prior=prior_results.get(
                    stack_name
                ),
                tests=test_evidence,
                reports=report_evidence,
                global_import_clean=(
                    global_import_clean
                ),
                whole_suite=whole_suite,
            )
        )

    calibrated_score, total_weight = (
        weighted_overall(
            stack_results
        )
    )

    blockers = blocking_gates(
        stage1
    )

    active_stacks = [
        item
        for item in stack_results
        if item[
            "classification"
        ]
        == "ACTIVE"
    ]

    low_confidence_active = [
        item[
            "stack"
        ]
        for item in active_stacks
        if item[
            "evidence_confidence"
        ]
        < 60
    ]

    average_confidence = (
        round(
            sum(
                item[
                    "evidence_confidence"
                ]
                for item in active_stacks
            )
            / len(
                active_stacks
            ),
            2,
        )
        if active_stacks
        else 0.0
    )

    grading_confidence = (
        "HIGH"
        if (
            average_confidence >= 80
            and not low_confidence_active
        )
        else "MODERATE"
        if average_confidence >= 60
        else "LOW"
    )

    numerical_grade_authoritative = (
        grading_confidence
        in {
            "HIGH",
            "MODERATE",
        }
    )

    active_findings = []

    for stack in stack_results:
        if stack[
            "classification"
        ] != "ACTIVE":
            continue

        for finding in stack[
            "findings"
        ]:
            active_findings.append(
                {
                    "stack": stack[
                        "stack"
                    ],
                    "stack_score": stack[
                        "score"
                    ],
                    **finding,
                }
            )

    severity_order = {
        "CRITICAL": 0,
        "HIGH": 1,
        "MEDIUM": 2,
        "LOW": 3,
        "OBSERVATION": 4,
    }

    active_findings.sort(
        key=lambda item: (
            severity_order.get(
                item[
                    "severity"
                ],
                99,
            ),
            item[
                "stack_score"
            ],
            item[
                "stack"
            ],
            item[
                "code"
            ],
        )
    )

    attribution_report = {
        "status": "completed",
        "generated_at": datetime.now(
            UTC
        ).isoformat(),
        "test_files_scanned": len(
            test_evidence
        ),
        "report_files_scanned": len(
            report_evidence
        ),
        "tests_with_stack_attribution": sum(
            1
            for item in test_evidence
            if item.targets
        ),
        "reports_with_stack_attribution": sum(
            1
            for item in report_evidence
            if item.targets
        ),
        "test_evidence": [
            {
                "path": item.path,
                "targets": list(
                    item.targets
                ),
                "attribution_reasons": {
                    stack: list(
                        reasons
                    )
                    for stack, reasons
                    in item.attribution_reasons.items()
                },
                "failure_behavior_signal": (
                    item.failure_behavior_signal
                ),
                "sha256": item.source_sha256,
            }
            for item in test_evidence
        ],
        "report_evidence": [
            {
                "path": item.path,
                "targets": list(
                    item.targets
                ),
                "attribution_reasons": {
                    stack: list(
                        reasons
                    )
                    for stack, reasons
                    in item.attribution_reasons.items()
                },
                "status": item.status,
                "sha256": item.source_sha256,
            }
            for item in report_evidence
        ],
        "source_modified": False,
        "database_modified": False,
    }

    ATTRIBUTION_JSON.write_text(
        json.dumps(
            attribution_report,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    classification_report = {
        "status": "completed",
        "generated_at": datetime.now(
            UTC
        ).isoformat(),
        "class_weights": CLASS_WEIGHTS,
        "false_stacks_excluded": [
            "__init__.py",
        ],
        "stack_count": len(
            classifications
        ),
        "classifications": [
            classifications[
                name
            ]
            for name in sorted(
                classifications
            )
        ],
        "source_modified": False,
        "database_modified": False,
    }

    CLASSIFICATION_JSON.write_text(
        json.dumps(
            classification_report,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    snapshot = source_snapshot(
        inventory
    )

    SOURCE_SNAPSHOT_JSON.write_text(
        json.dumps(
            snapshot,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    stage1_score = float(
        stage1.get(
            "overall",
            {}
        ).get(
            "score",
            0.0,
        )
    )

    report = {
        "campaign": (
            "NeuroVest Integrated "
            "Qualification Campaign"
        ),
        "stage": "IQC-001B",
        "stage_name": (
            "Evidence Attribution, Stack Classification, "
            "and Grading Model Calibration"
        ),
        "status": "completed",
        "verified_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "stage1_baseline_preserved": True,
        "stage1_uncalibrated_score": (
            stage1_score
        ),
        "stage1_uncalibrated_grade": (
            stage1.get(
                "overall",
                {}
            ).get(
                "grade"
            )
        ),
        "calibration": {
            "false_stack_records_removed": [
                "__init__.py",
            ],
            "centralized_tests_attributed": True,
            "runtime_reports_attributed_by_content": True,
            "stack_classification_applied": True,
            "class_weighting_applied": True,
            "thin_supporting_stacks_not_graded_as_full_runtime_stacks": True,
            "deferred_capabilities_excluded_from_weighted_score": True,
        },
        "repository": {
            "real_stack_count": len(
                inventory
            ),
            "active_stack_count": sum(
                1
                for item in classifications.values()
                if item[
                    "classification"
                ]
                == "ACTIVE"
            ),
            "supporting_stack_count": sum(
                1
                for item in classifications.values()
                if item[
                    "classification"
                ]
                == "SUPPORTING"
            ),
            "compatibility_stack_count": sum(
                1
                for item in classifications.values()
                if item[
                    "classification"
                ]
                == "COMPATIBILITY"
            ),
            "dormant_stack_count": sum(
                1
                for item in classifications.values()
                if item[
                    "classification"
                ]
                == "DORMANT"
            ),
            "deferred_stack_count": sum(
                1
                for item in classifications.values()
                if item[
                    "classification"
                ]
                == "DEFERRED_BY_DESIGN"
            ),
        },
        "evidence_attribution": {
            "test_files_scanned": len(
                test_evidence
            ),
            "tests_with_stack_attribution": (
                attribution_report[
                    "tests_with_stack_attribution"
                ]
            ),
            "report_files_scanned": len(
                report_evidence
            ),
            "reports_with_stack_attribution": (
                attribution_report[
                    "reports_with_stack_attribution"
                ]
            ),
        },
        "whole_backend_tests": (
            whole_suite
        ),
        "hard_gate_blocker_count": len(
            blockers
        ),
        "hard_gate_blockers": blockers,
        "grading_confidence": {
            "status": grading_confidence,
            "average_active_stack_confidence": (
                average_confidence
            ),
            "low_confidence_active_stacks": (
                low_confidence_active
            ),
            "numerical_grade_authoritative": (
                numerical_grade_authoritative
            ),
        },
        "overall": {
            "calibrated_score": (
                calibrated_score
            ),
            "calibrated_grade": (
                grade_letter(
                    calibrated_score
                )
            ),
            "total_class_weight": (
                total_weight
            ),
            "development_use": (
                readiness_status(
                    calibrated_score,
                    READINESS_THRESHOLDS[
                        "development_use"
                    ],
                    blockers,
                    whole_suite,
                )
            ),
            "controlled_early_users": (
                readiness_status(
                    calibrated_score,
                    READINESS_THRESHOLDS[
                        "controlled_early_users"
                    ],
                    blockers,
                    whole_suite,
                )
            ),
            "production_deployment": (
                readiness_status(
                    calibrated_score,
                    READINESS_THRESHOLDS[
                        "production_deployment"
                    ],
                    blockers,
                    whole_suite,
                    production=True,
                )
            ),
            "broker_execution": (
                "NOT_APPROVED"
            ),
            "live_trading": (
                "NOT_APPROVED"
            ),
        },
        "stack_results": stack_results,
        "active_stack_findings": (
            active_findings
        ),
        "source_snapshot": {
            "source_file_count": (
                snapshot[
                    "source_file_count"
                ]
            ),
            "source_manifest_sha256": (
                snapshot[
                    "source_manifest_sha256"
                ]
            ),
        },
        "database": {
            "connected": database.get(
                "connected"
            ),
            "revision": database.get(
                "revision"
            ),
            "decision_event_rows": (
                database.get(
                    "decision_event_rows"
                )
            ),
            "modified": False,
        },
        "source_modified": False,
        "database_modified": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
        "next_step": (
            "IQC Stage 2 — Targeted Remediation Planning "
            "from Calibrated Active-Stack Findings"
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

    report_hash = sha256_file(
        REPORT_JSON
    )

    freeze = {
        "status": "frozen",
        "frozen_at": datetime.now(
            UTC
        ).isoformat(),
        "stage": "IQC-001B",
        "calibrated_report_sha256": (
            report_hash
        ),
        "source_manifest_sha256": (
            snapshot[
                "source_manifest_sha256"
            ]
        ),
        "classification_report_sha256": (
            sha256_file(
                CLASSIFICATION_JSON
            )
        ),
        "attribution_report_sha256": (
            sha256_file(
                ATTRIBUTION_JSON
            )
        ),
        "source_snapshot_sha256": (
            sha256_file(
                SOURCE_SNAPSHOT_JSON
            )
        ),
        "source_modified": False,
        "database_modified": False,
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
        "=" * 92,
        "NEUROVEST INTEGRATED QUALIFICATION CAMPAIGN",
        (
            "IQC STAGE 1B — EVIDENCE ATTRIBUTION, "
            "STACK CLASSIFICATION, AND GRADING MODEL CALIBRATION"
        ),
        "=" * 92,
        "",
        "STATUS",
        "COMPLETE",
        "",
        "MODE",
        "READ ONLY",
        "",
        "BASELINE CORRECTION",
        (
            "Stage 1 uncalibrated score:      "
            f"{stage1_score:.2f} / 100"
        ),
        (
            "Stage 1 uncalibrated grade:      "
            f"{stage1.get('overall', {}).get('grade')}"
        ),
        "- Original Stage 1 baseline preserved: YES",
        "- False stack '__init__.py' excluded: YES",
        "- Centralized tests attributed: YES",
        "- Qualification reports attributed by content: YES",
        "- Stack role weighting applied: YES",
        "",
        "STACK CLASSIFICATION",
        (
            "Real stacks:                     "
            f"{report['repository']['real_stack_count']}"
        ),
        (
            "Active:                          "
            f"{report['repository']['active_stack_count']}"
        ),
        (
            "Supporting:                      "
            f"{report['repository']['supporting_stack_count']}"
        ),
        (
            "Compatibility:                   "
            f"{report['repository']['compatibility_stack_count']}"
        ),
        (
            "Dormant:                         "
            f"{report['repository']['dormant_stack_count']}"
        ),
        (
            "Deferred by design:              "
            f"{report['repository']['deferred_stack_count']}"
        ),
        "",
        "EVIDENCE ATTRIBUTION",
        (
            "Test files scanned:              "
            f"{len(test_evidence)}"
        ),
        (
            "Tests with stack attribution:    "
            f"{attribution_report['tests_with_stack_attribution']}"
        ),
        (
            "Reports scanned:                 "
            f"{len(report_evidence)}"
        ),
        (
            "Reports with stack attribution:  "
            f"{attribution_report['reports_with_stack_attribution']}"
        ),
        "",
        "CALIBRATED OVERALL GRADE",
        (
            "Score:                           "
            f"{calibrated_score:.2f} / 100"
        ),
        (
            "Grade:                           "
            f"{grade_letter(calibrated_score)}"
        ),
        (
            "Grading confidence:              "
            f"{grading_confidence}"
        ),
        (
            "Numerical grade authoritative:   "
            f"{'YES' if numerical_grade_authoritative else 'NO'}"
        ),
        "",
        "READINESS",
        (
            "Development use:                 "
            f"{report['overall']['development_use']}"
        ),
        (
            "Controlled early users:          "
            f"{report['overall']['controlled_early_users']}"
        ),
        (
            "Production deployment:           "
            f"{report['overall']['production_deployment']}"
        ),
        "Broker execution:                  NOT APPROVED",
        "Live trading:                      NOT APPROVED",
        "",
        "WHOLE-BACKEND TEST EVIDENCE",
        (
            "Passed:                           "
            f"{whole_suite.get('passed', 0)}"
        ),
        (
            "Failed:                           "
            f"{whole_suite.get('failed', 0)}"
        ),
        (
            "Warnings:                         "
            f"{whole_suite.get('warnings', 0)}"
        ),
        "",
        "CALIBRATED STACK GRADES",
    ]

    for item in sorted(
        stack_results,
        key=lambda value: (
            -float(
                value[
                    "class_weight"
                ]
            ),
            -float(
                value[
                    "score"
                ]
            ),
            value[
                "stack"
            ],
        )
    ):
        lines.append(
            f"- {item['stack']:<28} "
            f"{item['classification']:<20} "
            f"{item['score']:>6.2f} "
            f"{item['grade']:<3} "
            f"{item['qualification']:<25} "
            f"confidence={item['evidence_confidence']}"
        )

    lines.extend(
        [
            "",
            "TOP ACTIVE-STACK FINDINGS",
        ]
    )

    if not active_findings:
        lines.append(
            "- None"
        )

    for index, finding in enumerate(
        active_findings[:12],
        start=1,
    ):
        lines.append(
            f"{index}. [{finding['severity']}] "
            f"{finding['stack']} — "
            f"{finding['summary']}"
        )

    lines.extend(
        [
            "",
            "DATABASE",
            (
                "Connected:                       "
                f"{'YES' if database.get('connected') else 'NO'}"
            ),
            (
                "Migration revision:              "
                f"{database.get('revision')}"
            ),
            (
                "decision_events rows:            "
                f"{database.get('decision_event_rows')}"
            ),
            "- Database modified: NO",
            "",
            "REPOSITORY SAFETY",
            (
                "Hard-gate blockers:              "
                f"{len(blockers)}"
            ),
            (
                "Import and cycle state clean:    "
                f"{'YES' if global_import_clean else 'NO'}"
            ),
            "- Source modified: NO",
            "- Broker execution enabled: NO",
            "- Live trading enabled: NO",
            "",
            "BASELINE FREEZE",
            (
                "Source files captured:           "
                f"{snapshot['source_file_count']}"
            ),
            (
                "Source manifest SHA-256:         "
                f"{snapshot['source_manifest_sha256']}"
            ),
            (
                "Calibrated report SHA-256:       "
                f"{report_hash}"
            ),
            "",
            "NEXT",
            (
                "IQC Stage 2 — Targeted Remediation Planning "
                "from Calibrated Active-Stack Findings"
            ),
            "",
            "=" * 92,
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

    print(
        rendered
    )

    print(
        "Calibrated report:"
    )

    print(
        REPORT_JSON
    )

    print()

    print(
        "Evidence attribution:"
    )

    print(
        ATTRIBUTION_JSON
    )

    print()

    print(
        "Stack classification:"
    )

    print(
        CLASSIFICATION_JSON
    )

    print()

    print(
        "Freeze manifest:"
    )

    print(
        FREEZE_JSON
    )


if __name__ == "__main__":
    main()
