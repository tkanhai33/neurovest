#!/usr/bin/env python3
"""
NeuroVest Integrated Qualification Campaign
IQC Stage 1 — Whole-System Discovery, Grading Model,
and Baseline Qualification

This scanner is read-only with respect to application source and databases.
It writes qualification evidence only beneath runtime/iqc/stage1.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
import sys
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

OUTPUT_DIR = (
    RUNTIME_ROOT
    / "iqc"
    / "stage1"
)

REPORT_JSON = (
    OUTPUT_DIR
    / "iqc_stage1_baseline_latest.json"
)

REPORT_TEXT = (
    OUTPUT_DIR
    / "iqc_stage1_baseline_latest.txt"
)

FREEZE_JSON = (
    OUTPUT_DIR
    / "iqc_stage1_freeze_manifest_latest.json"
)

IMPORT_AUDIT_JSON = (
    RUNTIME_ROOT
    / "hardening"
    / "workstream1"
    / "import_cycle_audit_latest.json"
)

PYTEST_LOG = (
    OUTPUT_DIR
    / "iqc_stage1_pytest_console.log"
)

DATABASE_REPORT = (
    OUTPUT_DIR
    / "iqc_stage1_database_state_latest.json"
)

GRADING_MODEL = {
    "architecture_and_ownership": 15,
    "import_and_dependency_integrity": 15,
    "contract_completeness": 15,
    "test_evidence": 15,
    "failure_behavior": 10,
    "boundary_and_capability_control": 15,
    "observability_and_operations": 5,
    "qualification_evidence": 10,
}

assert sum(
    GRADING_MODEL.values()
) == 100

GRADE_BANDS = [
    (97, "A+"),
    (93, "A"),
    (90, "A-"),
    (87, "B+"),
    (83, "B"),
    (80, "B-"),
    (77, "C+"),
    (73, "C"),
    (70, "C-"),
    (67, "D+"),
    (63, "D"),
    (60, "D-"),
    (0, "F"),
]

PRODUCTION_READINESS_THRESHOLDS = {
    "development_use": 70,
    "controlled_early_users": 85,
    "production_deployment": 93,
}

TEST_PATH_MARKERS = {
    "test",
    "tests",
    "__pycache__",
}

CONTRACT_MARKERS = (
    "contract",
    "schema",
    "dto",
    "interface",
    "protocol",
    "facade",
)

FUNCTION_MARKERS = (
    "service",
    "engine",
    "controller",
    "handler",
    "adapter",
    "repository",
    "runtime",
)

FAILURE_MARKERS = (
    "fail",
    "failure",
    "invalid",
    "exception",
    "error",
    "rollback",
    "timeout",
    "unavailable",
    "reject",
    "denied",
    "closed",
)

OBSERVABILITY_MARKERS = (
    "observability",
    "metrics",
    "logging",
    "telemetry",
    "health",
    "status",
    "trace",
)

QUALIFICATION_MARKERS = (
    "qualification",
    "verification",
    "audit",
    "freeze",
    "baseline",
    "hardening",
)

FORBIDDEN_PRODUCTION_PATTERNS = {
    "live_trading_enabled_true": re.compile(
        r"\blive_trading_enabled\s*[:=]\s*True\b"
    ),
    "broker_execution_enabled_true": re.compile(
        r"\bbroker_execution_enabled\s*[:=]\s*True\b"
    ),
    "execution_enabled_true": re.compile(
        r"\bexecution_enabled\s*[:=]\s*True\b"
    ),
    "runtime_allowed_true": re.compile(
        r"\bruntime_allowed\s*[:=]\s*True\b"
    ),
}

DIRECT_PERSISTENCE_IMPORTS = {
    "backend.app.stacks.db_runtime.database",
    "sqlalchemy.ext.asyncio",
}

SEVERITY_ORDER = {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3,
    "OBSERVATION": 4,
}


@dataclass(frozen=True)
class PythonFileRecord:
    path: str
    stack: str | None
    is_test: bool
    syntax_valid: bool
    imports: tuple[str, ...]
    classes: tuple[str, ...]
    functions: tuple[str, ...]
    source_lower: str
    sha256: str
    size_bytes: int


def sha256_bytes(
    value: bytes,
) -> str:
    return hashlib.sha256(
        value
    ).hexdigest()


def sha256_file(
    path: Path,
) -> str:
    return sha256_bytes(
        path.read_bytes()
    )


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
            & TEST_PATH_MARKERS
        )
        or path.name.startswith(
            "test_"
        )
        or path.name.endswith(
            "_test.py"
        )
    )


def stack_from_path(
    path: Path,
) -> str | None:
    try:
        relative = path.relative_to(
            STACKS_ROOT
        )

    except ValueError:
        return None

    if not relative.parts:
        return None

    return relative.parts[0]


def import_modules(
    tree: ast.AST,
) -> set[str]:
    modules: set[str] = set()

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                modules.add(
                    alias.name
                )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            if node.module:
                modules.add(
                    node.module
                )

    return modules


def inspect_python_file(
    path: Path,
) -> PythonFileRecord:
    data = path.read_bytes()
    digest = sha256_bytes(
        data
    )

    try:
        source = data.decode(
            "utf-8"
        )

    except UnicodeDecodeError:
        return PythonFileRecord(
            path=path.relative_to(
                ROOT
            ).as_posix(),
            stack=stack_from_path(
                path
            ),
            is_test=is_test_path(
                path
            ),
            syntax_valid=False,
            imports=(),
            classes=(),
            functions=(),
            source_lower="",
            sha256=digest,
            size_bytes=len(
                data
            ),
        )

    try:
        tree = ast.parse(
            source,
            filename=str(
                path
            ),
        )

    except SyntaxError:
        return PythonFileRecord(
            path=path.relative_to(
                ROOT
            ).as_posix(),
            stack=stack_from_path(
                path
            ),
            is_test=is_test_path(
                path
            ),
            syntax_valid=False,
            imports=(),
            classes=(),
            functions=(),
            source_lower=source.lower(),
            sha256=digest,
            size_bytes=len(
                data
            ),
        )

    classes = sorted(
        {
            node.name
            for node in ast.walk(
                tree
            )
            if isinstance(
                node,
                ast.ClassDef,
            )
        }
    )

    functions = sorted(
        {
            node.name
            for node in ast.walk(
                tree
            )
            if isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
        }
    )

    return PythonFileRecord(
        path=path.relative_to(
            ROOT
        ).as_posix(),
        stack=stack_from_path(
            path
        ),
        is_test=is_test_path(
            path
        ),
        syntax_valid=True,
        imports=tuple(
            sorted(
                import_modules(
                    tree
                )
            )
        ),
        classes=tuple(
            classes
        ),
        functions=tuple(
            functions
        ),
        source_lower=source.lower(),
        sha256=digest,
        size_bytes=len(
            data
        ),
    )


def discover_python_files() -> list[
    PythonFileRecord
]:
    records = []

    if not BACKEND_ROOT.is_dir():
        return records

    for path in sorted(
        BACKEND_ROOT.rglob(
            "*.py"
        )
    ):
        if "__pycache__" in path.parts:
            continue

        records.append(
            inspect_python_file(
                path
            )
        )

    return records


def discover_reports() -> list[
    dict[str, Any]
]:
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

        status = None

        if isinstance(
            data,
            dict,
        ):
            status = data.get(
                "status"
            )

        reports.append(
            {
                "path": path.relative_to(
                    ROOT
                ).as_posix(),
                "status": status,
                "sha256": sha256_file(
                    path
                ),
                "size_bytes": path.stat().st_size,
            }
        )

    return reports


def read_import_audit() -> dict[
    str,
    Any
]:
    if not IMPORT_AUDIT_JSON.is_file():
        return {
            "available": False,
            "summary": {},
        }

    try:
        data = json.loads(
            IMPORT_AUDIT_JSON.read_text(
                encoding="utf-8"
            )
        )

    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ):
        return {
            "available": False,
            "summary": {},
        }

    return {
        "available": True,
        "summary": data.get(
            "summary",
            {}
        ),
    }


def read_pytest_state() -> dict[
    str,
    Any
]:
    if not PYTEST_LOG.is_file():
        return {
            "available": False,
            "exit_code": None,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "timed_out": False,
        }

    text = PYTEST_LOG.read_text(
        encoding="utf-8",
        errors="replace",
    )

    exit_file = (
        OUTPUT_DIR
        / "iqc_stage1_pytest_exit_code.txt"
    )

    exit_code = None

    if exit_file.is_file():
        try:
            exit_code = int(
                exit_file.read_text(
                    encoding="utf-8"
                ).strip()
            )

        except ValueError:
            exit_code = None

    def number(
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

    timed_out = (
        exit_code == 124
    )

    return {
        "available": True,
        "exit_code": exit_code,
        "passed": number(
            "passed"
        ),
        "failed": number(
            "failed"
        ),
        "errors": number(
            "errors?"
        ),
        "skipped": number(
            "skipped"
        ),
        "timed_out": timed_out,
    }


def read_database_state() -> dict[
    str,
    Any
]:
    if not DATABASE_REPORT.is_file():
        return {
            "available": False,
            "connected": False,
        }

    try:
        data = json.loads(
            DATABASE_REPORT.read_text(
                encoding="utf-8"
            )
        )

    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ):
        return {
            "available": False,
            "connected": False,
        }

    return data


def grade_letter(
    score: float,
) -> str:
    for threshold, letter in GRADE_BANDS:
        if score >= threshold:
            return letter

    return "F"


def normalized_ratio(
    value: int,
    target: int,
) -> float:
    if target <= 0:
        return 1.0

    return min(
        1.0,
        value / target,
    )


def count_filename_markers(
    records: list[
        PythonFileRecord
    ],
    markers: tuple[
        str,
        ...,
    ],
) -> int:
    return sum(
        1
        for record in records
        if any(
            marker
            in Path(
                record.path
            ).name.lower()
            for marker in markers
        )
    )


def count_source_markers(
    records: list[
        PythonFileRecord
    ],
    markers: tuple[
        str,
        ...,
    ],
) -> int:
    return sum(
        1
        for record in records
        if any(
            marker in record.source_lower
            for marker in markers
        )
    )


def calculate_stack_grade(
    stack: str,
    records: list[
        PythonFileRecord
    ],
    import_audit: dict[
        str,
        Any
    ],
    pytest_state: dict[
        str,
        Any
    ],
    report_records: list[
        dict[str, Any]
    ],
) -> dict[str, Any]:
    production = [
        record
        for record in records
        if not record.is_test
    ]

    tests = [
        record
        for record in records
        if record.is_test
    ]

    syntax_errors = [
        record.path
        for record in records
        if not record.syntax_valid
    ]

    contract_files = count_filename_markers(
        production,
        CONTRACT_MARKERS,
    )

    functional_files = count_filename_markers(
        production,
        FUNCTION_MARKERS,
    )

    failure_test_files = count_source_markers(
        tests,
        FAILURE_MARKERS,
    )

    observability_files = count_filename_markers(
        production,
        OBSERVABILITY_MARKERS,
    )

    qualification_test_files = count_source_markers(
        tests,
        QUALIFICATION_MARKERS,
    )

    stack_report_count = sum(
        1
        for report in report_records
        if stack.lower()
        in report[
            "path"
        ].lower()
    )

    direct_persistence_imports = []

    for record in production:
        matched = sorted(
            set(
                record.imports
            )
            & DIRECT_PERSISTENCE_IMPORTS
        )

        if matched:
            direct_persistence_imports.append(
                {
                    "path": record.path,
                    "modules": matched,
                }
            )

    capability_signals = []

    for record in production:
        for signal, pattern in (
            FORBIDDEN_PRODUCTION_PATTERNS.items()
        ):
            if pattern.search(
                record.source_lower
            ):
                capability_signals.append(
                    {
                        "path": record.path,
                        "signal": signal,
                    }
                )

    import_summary = import_audit.get(
        "summary",
        {}
    )

    global_import_clean = (
        import_audit.get(
            "available"
        )
        and import_summary.get(
            "active_internal_unresolved",
            1,
        )
        == 0
        and import_summary.get(
            "tooling_or_relative_unresolved",
            1,
        )
        == 0
        and import_summary.get(
            "syntax_errors",
            1,
        )
        == 0
        and import_summary.get(
            "active_cycle_components",
            1,
        )
        == 0
        and import_summary.get(
            "self_cycles",
            1,
        )
        == 0
    )

    architecture_ratio = (
        0.35
        if production
        else 0.0
    )

    architecture_ratio += (
        0.25
        if any(
            Path(
                record.path
            ).name
            == "__init__.py"
            for record in production
        )
        else 0.0
    )

    architecture_ratio += (
        0.25
        * normalized_ratio(
            functional_files,
            2,
        )
    )

    architecture_ratio += (
        0.15
        if not syntax_errors
        else 0.0
    )

    import_ratio = (
        1.0
        if global_import_clean
        else 0.25
    )

    contract_ratio = (
        0.20
        if production
        else 0.0
    )

    contract_ratio += (
        0.55
        * normalized_ratio(
            contract_files,
            2,
        )
    )

    contract_ratio += (
        0.25
        if any(
            "service"
            in Path(
                record.path
            ).name.lower()
            or "facade"
            in Path(
                record.path
            ).name.lower()
            for record in production
        )
        else 0.0
    )

    test_ratio = (
        0.15
        if tests
        else 0.0
    )

    test_ratio += (
        0.50
        * normalized_ratio(
            len(
                tests
            ),
            max(
                2,
                len(
                    production
                )
                // 4,
            ),
        )
    )

    if pytest_state.get(
        "available"
    ):
        if pytest_state.get(
            "exit_code"
        ) == 0:
            test_ratio += 0.35

        elif pytest_state.get(
            "passed",
            0,
        ) > 0:
            test_ratio += 0.15

    failure_ratio = (
        0.20
        if tests
        else 0.0
    )

    failure_ratio += (
        0.80
        * normalized_ratio(
            failure_test_files,
            2,
        )
    )

    boundary_ratio = 1.0

    boundary_ratio -= min(
        0.50,
        0.10
        * len(
            direct_persistence_imports
        ),
    )

    boundary_ratio -= min(
        1.0,
        0.50
        * len(
            capability_signals
        ),
    )

    boundary_ratio = max(
        0.0,
        boundary_ratio,
    )

    observability_ratio = (
        normalized_ratio(
            observability_files,
            1,
        )
    )

    qualification_ratio = (
        0.45
        * normalized_ratio(
            qualification_test_files,
            2,
        )
        + 0.55
        * normalized_ratio(
            stack_report_count,
            2,
        )
    )

    ratios = {
        "architecture_and_ownership": min(
            1.0,
            architecture_ratio,
        ),
        "import_and_dependency_integrity": min(
            1.0,
            import_ratio,
        ),
        "contract_completeness": min(
            1.0,
            contract_ratio,
        ),
        "test_evidence": min(
            1.0,
            test_ratio,
        ),
        "failure_behavior": min(
            1.0,
            failure_ratio,
        ),
        "boundary_and_capability_control": min(
            1.0,
            boundary_ratio,
        ),
        "observability_and_operations": min(
            1.0,
            observability_ratio,
        ),
        "qualification_evidence": min(
            1.0,
            qualification_ratio,
        ),
    }

    category_scores = {
        name: round(
            ratios[name]
            * weight,
            2,
        )
        for name, weight
        in GRADING_MODEL.items()
    }

    score = round(
        sum(
            category_scores.values()
        ),
        2,
    )

    findings = []

    if syntax_errors:
        findings.append(
            {
                "severity": "CRITICAL",
                "code": "STACK_SYNTAX_ERROR",
                "summary": (
                    f"{len(syntax_errors)} syntax-invalid "
                    "Python file(s)"
                ),
                "evidence": syntax_errors,
                "estimated_gain": 8.0,
            }
        )

    if not tests:
        findings.append(
            {
                "severity": "HIGH",
                "code": "NO_STACK_TESTS",
                "summary": (
                    "No stack-local test files discovered"
                ),
                "evidence": [],
                "estimated_gain": 7.0,
            }
        )

    elif failure_test_files == 0:
        findings.append(
            {
                "severity": "HIGH",
                "code": "NO_FAILURE_TEST_EVIDENCE",
                "summary": (
                    "No explicit failure-behavior test "
                    "evidence discovered"
                ),
                "evidence": [],
                "estimated_gain": 5.0,
            }
        )

    if contract_files == 0:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "NO_CONTRACT_ARTIFACT",
                "summary": (
                    "No explicit contract, schema, DTO, "
                    "interface, protocol, or facade file"
                ),
                "evidence": [],
                "estimated_gain": 4.0,
            }
        )

    if direct_persistence_imports:
        findings.append(
            {
                "severity": "HIGH",
                "code": "DIRECT_PERSISTENCE_IMPORT",
                "summary": (
                    "Production modules import direct "
                    "persistence dependencies"
                ),
                "evidence": (
                    direct_persistence_imports
                ),
                "estimated_gain": 6.0,
            }
        )

    if capability_signals:
        findings.append(
            {
                "severity": "CRITICAL",
                "code": "FORBIDDEN_CAPABILITY_ENABLED",
                "summary": (
                    "Potential enabled execution or live "
                    "trading capability detected"
                ),
                "evidence": capability_signals,
                "estimated_gain": 12.0,
            }
        )

    if observability_files == 0:
        findings.append(
            {
                "severity": "LOW",
                "code": "NO_OBSERVABILITY_ARTIFACT",
                "summary": (
                    "No explicit observability, metrics, "
                    "health, status, or telemetry module"
                ),
                "evidence": [],
                "estimated_gain": 2.0,
            }
        )

    if stack_report_count == 0:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "NO_QUALIFICATION_REPORT",
                "summary": (
                    "No stack-specific runtime "
                    "qualification report discovered"
                ),
                "evidence": [],
                "estimated_gain": 3.0,
            }
        )

    findings.sort(
        key=lambda item: (
            SEVERITY_ORDER[
                item[
                    "severity"
                ]
            ],
            -float(
                item[
                    "estimated_gain"
                ]
            ),
            item[
                "code"
            ],
        )
    )

    if any(
        item[
            "severity"
        ]
        == "CRITICAL"
        for item in findings
    ):
        qualification = "BLOCKED"

    elif score >= 90:
        qualification = "QUALIFIED"

    elif score >= 80:
        qualification = (
            "CONDITIONALLY_QUALIFIED"
        )

    elif score >= 70:
        qualification = (
            "CONTROLLED_TESTING_ONLY"
        )

    else:
        qualification = "NOT_QUALIFIED"

    return {
        "stack": stack,
        "score": score,
        "grade": grade_letter(
            score
        ),
        "qualification": qualification,
        "category_scores": category_scores,
        "category_maximums": (
            GRADING_MODEL
        ),
        "evidence": {
            "production_python_files": len(
                production
            ),
            "test_python_files": len(
                tests
            ),
            "contract_artifacts": (
                contract_files
            ),
            "functional_artifacts": (
                functional_files
            ),
            "failure_test_artifacts": (
                failure_test_files
            ),
            "observability_artifacts": (
                observability_files
            ),
            "qualification_test_artifacts": (
                qualification_test_files
            ),
            "qualification_reports": (
                stack_report_count
            ),
            "syntax_errors": (
                syntax_errors
            ),
            "direct_persistence_imports": (
                direct_persistence_imports
            ),
            "forbidden_capability_signals": (
                capability_signals
            ),
        },
        "findings": findings,
    }


def global_hard_gates(
    import_audit: dict[
        str,
        Any
    ],
    records: list[
        PythonFileRecord
    ],
    database_state: dict[
        str,
        Any
    ],
) -> list[dict[str, Any]]:
    gates = []

    summary = import_audit.get(
        "summary",
        {},
    )

    checks = [
        (
            "ACTIVE_INTERNAL_UNRESOLVED",
            summary.get(
                "active_internal_unresolved",
                None,
            ),
        ),
        (
            "TOOLING_OR_RELATIVE_UNRESOLVED",
            summary.get(
                "tooling_or_relative_unresolved",
                None,
            ),
        ),
        (
            "SYNTAX_ERRORS",
            summary.get(
                "syntax_errors",
                None,
            ),
        ),
        (
            "ACTIVE_DEPENDENCY_CYCLES",
            summary.get(
                "active_cycle_components",
                None,
            ),
        ),
        (
            "SELF_CYCLES",
            summary.get(
                "self_cycles",
                None,
            ),
        ),
    ]

    for name, value in checks:
        gates.append(
            {
                "gate": name,
                "passed": value == 0,
                "value": value,
                "blocking": value != 0,
            }
        )

    production_capability_signals = []

    for record in records:
        if record.is_test:
            continue

        for signal, pattern in (
            FORBIDDEN_PRODUCTION_PATTERNS.items()
        ):
            if pattern.search(
                record.source_lower
            ):
                production_capability_signals.append(
                    {
                        "path": record.path,
                        "signal": signal,
                    }
                )

    gates.append(
        {
            "gate": (
                "FORBIDDEN_PRODUCTION_CAPABILITY"
            ),
            "passed": not bool(
                production_capability_signals
            ),
            "value": (
                production_capability_signals
            ),
            "blocking": bool(
                production_capability_signals
            ),
        }
    )

    gates.append(
        {
            "gate": "DATABASE_CONNECTIVITY",
            "passed": bool(
                database_state.get(
                    "connected"
                )
            ),
            "value": database_state,
            "blocking": False,
        }
    )

    return gates


def remediation_priorities(
    stack_results: list[
        dict[str, Any]
    ],
) -> list[dict[str, Any]]:
    candidates = []

    for stack in stack_results:
        for finding in stack[
            "findings"
        ]:
            candidates.append(
                {
                    "stack": stack[
                        "stack"
                    ],
                    "current_score": stack[
                        "score"
                    ],
                    "severity": finding[
                        "severity"
                    ],
                    "code": finding[
                        "code"
                    ],
                    "summary": finding[
                        "summary"
                    ],
                    "estimated_gain": finding[
                        "estimated_gain"
                    ],
                    "evidence": finding[
                        "evidence"
                    ],
                }
            )

    candidates.sort(
        key=lambda item: (
            SEVERITY_ORDER[
                item[
                    "severity"
                ]
            ],
            -float(
                item[
                    "estimated_gain"
                ]
            ),
            float(
                item[
                    "current_score"
                ]
            ),
            item[
                "stack"
            ],
        )
    )

    return candidates[:20]


def qualification_status(
    score: float,
    hard_gates: list[
        dict[str, Any]
    ],
    threshold: int,
) -> str:
    blocked = any(
        gate[
            "blocking"
        ]
        and not gate[
            "passed"
        ]
        for gate in hard_gates
    )

    if blocked:
        return "BLOCKED"

    if score >= threshold:
        return "QUALIFIED"

    return "NOT_QUALIFIED"


def build_freeze_manifest(
    records: list[
        PythonFileRecord
    ],
    report_sha256: str,
) -> dict[str, Any]:
    source_entries = [
        {
            "path": record.path,
            "sha256": record.sha256,
            "size_bytes": record.size_bytes,
        }
        for record in records
        if not record.is_test
    ]

    source_entries.sort(
        key=lambda item: item[
            "path"
        ]
    )

    combined = hashlib.sha256()

    for entry in source_entries:
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

    combined.update(
        report_sha256.encode(
            "ascii"
        )
    )

    return {
        "status": "frozen",
        "frozen_at": datetime.now(
            UTC
        ).isoformat(),
        "source_file_count": len(
            source_entries
        ),
        "source_manifest_sha256": (
            combined.hexdigest()
        ),
        "qualification_report_sha256": (
            report_sha256
        ),
        "source_files": source_entries,
        "source_modified": False,
        "database_modified": False,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    records = discover_python_files()
    reports = discover_reports()
    import_audit = read_import_audit()
    pytest_state = read_pytest_state()
    database_state = read_database_state()

    stacks: dict[
        str,
        list[PythonFileRecord],
    ] = defaultdict(
        list
    )

    for record in records:
        if record.stack:
            stacks[
                record.stack
            ].append(
                record
            )

    stack_results = [
        calculate_stack_grade(
            stack,
            stack_records,
            import_audit,
            pytest_state,
            reports,
        )
        for stack, stack_records
        in sorted(
            stacks.items()
        )
    ]

    hard_gates = global_hard_gates(
        import_audit,
        records,
        database_state,
    )

    if stack_results:
        overall_score = round(
            sum(
                item[
                    "score"
                ]
                for item in stack_results
            )
            / len(
                stack_results
            ),
            2,
        )

    else:
        overall_score = 0.0

    priorities = remediation_priorities(
        stack_results
    )

    hard_gate_blockers = [
        gate
        for gate in hard_gates
        if gate[
            "blocking"
        ]
        and not gate[
            "passed"
        ]
    ]

    severity_counts = defaultdict(
        int
    )

    for stack in stack_results:
        for finding in stack[
            "findings"
        ]:
            severity_counts[
                finding[
                    "severity"
                ]
            ] += 1

    report = {
        "campaign": (
            "NeuroVest Integrated "
            "Qualification Campaign"
        ),
        "stage": "IQC-001",
        "stage_name": (
            "Whole-System Discovery, "
            "Grading Model, and "
            "Baseline Qualification"
        ),
        "status": "completed",
        "verified_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "grading_model": GRADING_MODEL,
        "grade_bands": [
            {
                "minimum": minimum,
                "grade": grade,
            }
            for minimum, grade
            in GRADE_BANDS
        ],
        "repository_discovery": {
            "python_files": len(
                records
            ),
            "production_python_files": sum(
                1
                for record in records
                if not record.is_test
            ),
            "test_python_files": sum(
                1
                for record in records
                if record.is_test
            ),
            "stacks_discovered": len(
                stacks
            ),
            "qualification_reports_discovered": len(
                reports
            ),
            "syntax_invalid_files": [
                record.path
                for record in records
                if not record.syntax_valid
            ],
        },
        "import_audit": import_audit,
        "pytest": pytest_state,
        "database": database_state,
        "hard_gates": hard_gates,
        "hard_gate_blocker_count": len(
            hard_gate_blockers
        ),
        "hard_gate_blockers": (
            hard_gate_blockers
        ),
        "overall": {
            "score": overall_score,
            "grade": grade_letter(
                overall_score
            ),
            "development_use": (
                qualification_status(
                    overall_score,
                    hard_gates,
                    PRODUCTION_READINESS_THRESHOLDS[
                        "development_use"
                    ],
                )
            ),
            "controlled_early_users": (
                qualification_status(
                    overall_score,
                    hard_gates,
                    PRODUCTION_READINESS_THRESHOLDS[
                        "controlled_early_users"
                    ],
                )
            ),
            "production_deployment": (
                qualification_status(
                    overall_score,
                    hard_gates,
                    PRODUCTION_READINESS_THRESHOLDS[
                        "production_deployment"
                    ],
                )
            ),
            "broker_execution": (
                "NOT_APPROVED"
            ),
            "live_trading": (
                "NOT_APPROVED"
            ),
        },
        "finding_counts": {
            severity: severity_counts[
                severity
            ]
            for severity in (
                "CRITICAL",
                "HIGH",
                "MEDIUM",
                "LOW",
                "OBSERVATION",
            )
        },
        "stack_results": stack_results,
        "remediation_priorities": priorities,
        "source_modified": False,
        "database_modified": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
        "next_step": (
            "IQC Remediation Batch 1 — "
            "Critical Blockers and "
            "Highest-Value Findings"
        ),
    }

    REPORT_JSON.write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )

    report_sha256 = sha256_file(
        REPORT_JSON
    )

    freeze_manifest = (
        build_freeze_manifest(
            records,
            report_sha256,
        )
    )

    FREEZE_JSON.write_text(
        json.dumps(
            freeze_manifest,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    lines = [
        "=" * 88,
        "NEUROVEST INTEGRATED QUALIFICATION CAMPAIGN",
        (
            "IQC-001 — WHOLE-SYSTEM DISCOVERY, "
            "GRADING MODEL, AND BASELINE QUALIFICATION"
        ),
        "=" * 88,
        "",
        "STATUS",
        "COMPLETE",
        "",
        "MODE",
        "READ ONLY",
        "",
        "REPOSITORY DISCOVERY",
        (
            "Python files:                 "
            f"{report['repository_discovery']['python_files']}"
        ),
        (
            "Production Python files:      "
            f"{report['repository_discovery']['production_python_files']}"
        ),
        (
            "Test Python files:            "
            f"{report['repository_discovery']['test_python_files']}"
        ),
        (
            "Stacks discovered:            "
            f"{report['repository_discovery']['stacks_discovered']}"
        ),
        (
            "Qualification reports:        "
            f"{report['repository_discovery']['qualification_reports_discovered']}"
        ),
        "",
        "OVERALL GRADE",
        (
            f"Score:                        "
            f"{overall_score:.2f} / 100"
        ),
        (
            f"Grade:                        "
            f"{grade_letter(overall_score)}"
        ),
        "",
        "READINESS",
        (
            "Development use:              "
            f"{report['overall']['development_use']}"
        ),
        (
            "Controlled early users:       "
            f"{report['overall']['controlled_early_users']}"
        ),
        (
            "Production deployment:        "
            f"{report['overall']['production_deployment']}"
        ),
        "Broker execution:               NOT APPROVED",
        "Live trading:                   NOT APPROVED",
        "",
        "HARD GATES",
        (
            "Blocking gates:               "
            f"{len(hard_gate_blockers)}"
        ),
    ]

    for gate in hard_gates:
        lines.append(
            f"- {gate['gate']}: "
            f"{'PASS' if gate['passed'] else 'FAIL'}"
        )

    lines.extend(
        [
            "",
            "FINDINGS",
            (
                "Critical:                     "
                f"{severity_counts['CRITICAL']}"
            ),
            (
                "High:                         "
                f"{severity_counts['HIGH']}"
            ),
            (
                "Medium:                       "
                f"{severity_counts['MEDIUM']}"
            ),
            (
                "Low:                          "
                f"{severity_counts['LOW']}"
            ),
            "",
            "STACK GRADES",
        ]
    )

    for stack in sorted(
        stack_results,
        key=lambda item: (
            -item[
                "score"
            ],
            item[
                "stack"
            ],
        ),
    ):
        lines.append(
            f"- {stack['stack']:<28} "
            f"{stack['score']:>6.2f}  "
            f"{stack['grade']:<3}  "
            f"{stack['qualification']}"
        )

    lines.extend(
        [
            "",
            "TOP REMEDIATION PRIORITIES",
        ]
    )

    if not priorities:
        lines.append(
            "- None"
        )

    for index, item in enumerate(
        priorities[:10],
        start=1,
    ):
        lines.append(
            f"{index}. [{item['severity']}] "
            f"{item['stack']} — "
            f"{item['summary']} "
            f"(estimated gain +"
            f"{item['estimated_gain']:.1f})"
        )

    lines.extend(
        [
            "",
            "BASELINE FREEZE",
            (
                "Source files frozen:          "
                f"{freeze_manifest['source_file_count']}"
            ),
            (
                "Source manifest SHA-256:      "
                f"{freeze_manifest['source_manifest_sha256']}"
            ),
            (
                "Qualification report SHA-256: "
                f"{report_sha256}"
            ),
            "",
            "SAFETY",
            "- Source modified: NO",
            "- Database modified: NO",
            "- Broker execution enabled: NO",
            "- Live trading enabled: NO",
            "",
            "NEXT",
            (
                "IQC Remediation Batch 1 — "
                "Critical Blockers and "
                "Highest-Value Findings"
            ),
            "",
            "=" * 88,
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
        "JSON report:"
    )

    print(
        REPORT_JSON
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
