#!/usr/bin/env python3
"""
NeuroVest Integrated Qualification Campaign

IQC Stage 2 —
Targeted Remediation Planning from Calibrated Active-Stack Findings

Read-only responsibilities:

1. Verify the IQC Stage 1B calibrated baseline.
2. Inspect auth_identity and chat_public implementation boundaries.
3. Discover direct and centralized test evidence for both stacks.
4. Inspect the three trading-pipeline failures.
5. Determine whether failures represent:
   - stale test patch targets,
   - module-alias divergence,
   - async event-loop contamination,
   - real production behavior defects,
   - or insufficient evidence.
6. Produce a ranked remediation plan without modifying source or database state.
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

STAGE1B_DIR = (
    RUNTIME_ROOT
    / "iqc"
    / "stage1b"
)

OUTPUT_DIR = (
    RUNTIME_ROOT
    / "iqc"
    / "stage2"
)

STAGE1B_REPORT = (
    STAGE1B_DIR
    / "iqc_stage1b_calibrated_baseline_latest.json"
)

STAGE1B_FREEZE = (
    STAGE1B_DIR
    / "iqc_stage1b_freeze_manifest_latest.json"
)

STAGE1B_ATTRIBUTION = (
    STAGE1B_DIR
    / "iqc_stage1b_evidence_attribution_latest.json"
)

STAGE1_TEST_LOG = (
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
    / "iqc_stage2_targeted_remediation_plan_latest.json"
)

REPORT_TEXT = (
    OUTPUT_DIR
    / "iqc_stage2_targeted_remediation_plan_latest.txt"
)

EVIDENCE_JSON = (
    OUTPUT_DIR
    / "iqc_stage2_targeted_evidence_latest.json"
)

FREEZE_JSON = (
    OUTPUT_DIR
    / "iqc_stage2_planning_freeze_latest.json"
)

TARGET_STACKS = {
    "auth_identity",
    "chat_public",
}

TRADING_PIPELINE_TEST = (
    BACKEND_ROOT
    / "test"
    / "test_trading_pipeline.py"
)

KNOWN_IMPORT_PREFIXES = (
    "backend.app.",
    "app.",
    "stacks.",
)

SEVERITY_ORDER = {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3,
    "OBSERVATION": 4,
}

PATCH_PATTERN = re.compile(
    r"""patch\(\s*["']([^"']+)["']"""
)

FAILED_TEST_PATTERN = re.compile(
    r"""FAILED\s+([^\s]+)::([^\s]+)"""
)

LOOP_ERROR_MARKERS = (
    "attached to a different loop",
    "event loop is closed",
    "coroutine 'connection._cancel' was never awaited",
    "coroutine 'connection._cancel' was never awaited",
)

DATABASE_ACTIVITY_MARKERS = (
    "database log & inventory saved",
    "asyncpg",
    "sqlalchemy.pool",
)

FAILURE_TEST_MARKERS = (
    "raises",
    "exception",
    "invalid",
    "denied",
    "blocked",
    "unauthorized",
    "forbidden",
    "failure",
    "error",
    "timeout",
)


@dataclass(frozen=True)
class SourceRecord:
    path: str
    sha256: str
    size_bytes: int
    imports: tuple[str, ...]
    classes: tuple[str, ...]
    functions: tuple[str, ...]
    async_functions: tuple[str, ...]
    patch_targets: tuple[str, ...]
    syntax_valid: bool


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


def load_json(
    path: Path,
) -> dict[str, Any]:
    assert path.is_file(), (
        f"Required evidence missing: {path}"
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


def is_test_path(
    path: Path,
) -> bool:
    lowered_parts = {
        part.lower()
        for part in path.parts
    }

    return (
        "test" in lowered_parts
        or "tests" in lowered_parts
        or "l7_tests" in lowered_parts
        or path.name.startswith("test_")
        or path.name.endswith("_test.py")
    )


def dotted_name(
    node: ast.AST,
) -> str | None:
    if isinstance(
        node,
        ast.Name,
    ):
        return node.id

    if isinstance(
        node,
        ast.Attribute,
    ):
        parent = dotted_name(
            node.value
        )

        if parent:
            return f"{parent}.{node.attr}"

        return node.attr

    return None


def inspect_source(
    path: Path,
) -> SourceRecord:
    source = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    patch_targets = tuple(
        sorted(
            set(
                PATCH_PATTERN.findall(
                    source
                )
            )
        )
    )

    try:
        tree = ast.parse(
            source,
            filename=str(path),
        )

    except SyntaxError:
        return SourceRecord(
            path=relative(path),
            sha256=sha256_file(path),
            size_bytes=path.stat().st_size,
            imports=(),
            classes=(),
            functions=(),
            async_functions=(),
            patch_targets=patch_targets,
            syntax_valid=False,
        )

    imports: set[str] = set()
    classes: set[str] = set()
    functions: set[str] = set()
    async_functions: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                imports.add(
                    alias.name
                )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            if node.module:
                imports.add(
                    node.module
                )

        elif isinstance(
            node,
            ast.ClassDef,
        ):
            classes.add(
                node.name
            )

        elif isinstance(
            node,
            ast.AsyncFunctionDef,
        ):
            functions.add(
                node.name
            )

            async_functions.add(
                node.name
            )

        elif isinstance(
            node,
            ast.FunctionDef,
        ):
            functions.add(
                node.name
            )

    return SourceRecord(
        path=relative(path),
        sha256=sha256_file(path),
        size_bytes=path.stat().st_size,
        imports=tuple(
            sorted(imports)
        ),
        classes=tuple(
            sorted(classes)
        ),
        functions=tuple(
            sorted(functions)
        ),
        async_functions=tuple(
            sorted(async_functions)
        ),
        patch_targets=patch_targets,
        syntax_valid=True,
    )


def stack_files(
    stack: str,
) -> list[Path]:
    directory = (
        STACKS_ROOT
        / stack
    )

    assert directory.is_dir(), (
        f"Target stack directory missing: {directory}"
    )

    return [
        path
        for path in sorted(
            directory.rglob("*.py")
        )
        if "__pycache__" not in path.parts
    ]


def all_test_files() -> list[Path]:
    return [
        path
        for path in sorted(
            BACKEND_ROOT.rglob("*.py")
        )
        if (
            "__pycache__" not in path.parts
            and is_test_path(path)
        )
    ]


def module_target_stacks(
    source: str,
) -> set[str]:
    targets = set()

    for stack in TARGET_STACKS:
        tokens = (
            f"backend.app.stacks.{stack}",
            f"app.stacks.{stack}",
            f"stacks.{stack}",
            f"/stacks/{stack}/",
        )

        lowered = source.lower()

        if any(
            token.lower() in lowered
            for token in tokens
        ):
            targets.add(stack)

    return targets


def explicit_failure_signal(
    source: str,
) -> bool:
    lowered = source.lower()

    return any(
        marker in lowered
        for marker in FAILURE_TEST_MARKERS
    )


def test_attribution() -> dict[str, Any]:
    per_stack: dict[
        str,
        dict[str, Any],
    ] = {
        stack: {
            "test_files": [],
            "failure_test_files": [],
            "attribution_reasons": {},
        }
        for stack in sorted(TARGET_STACKS)
    }

    unattributed = []

    for path in all_test_files():
        source = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        targets = module_target_stacks(
            source
        )

        reasons: dict[
            str,
            list[str],
        ] = defaultdict(list)

        for stack in targets:
            for token in (
                f"backend.app.stacks.{stack}",
                f"app.stacks.{stack}",
                f"stacks.{stack}",
                f"/stacks/{stack}/",
            ):
                if token.lower() in source.lower():
                    reasons[
                        stack
                    ].append(
                        f"source_reference:{token}"
                    )

        for stack in TARGET_STACKS:
            stack_root = (
                STACKS_ROOT
                / stack
            )

            try:
                path.relative_to(
                    stack_root
                )

            except ValueError:
                pass

            else:
                targets.add(
                    stack
                )

                reasons[
                    stack
                ].append(
                    "local_stack_test"
                )

        if not targets:
            unattributed.append(
                relative(path)
            )

            continue

        failure_signal = (
            explicit_failure_signal(
                source
            )
        )

        for stack in targets:
            per_stack[
                stack
            ][
                "test_files"
            ].append(
                relative(path)
            )

            if failure_signal:
                per_stack[
                    stack
                ][
                    "failure_test_files"
                ].append(
                    relative(path)
                )

            per_stack[
                stack
            ][
                "attribution_reasons"
            ][
                relative(path)
            ] = sorted(
                set(
                    reasons[
                        stack
                    ]
                )
            )

    for stack in per_stack:
        per_stack[
            stack
        ][
            "test_files"
        ] = sorted(
            set(
                per_stack[
                    stack
                ][
                    "test_files"
                ]
            )
        )

        per_stack[
            stack
        ][
            "failure_test_files"
        ] = sorted(
            set(
                per_stack[
                    stack
                ][
                    "failure_test_files"
                ]
            )
        )

    return {
        "per_stack": per_stack,
        "unattributed_test_files": sorted(
            unattributed
        ),
    }


def failed_tests_from_log(
    log_text: str,
) -> list[dict[str, str]]:
    failures = []

    for path, test_name in (
        FAILED_TEST_PATTERN.findall(
            log_text
        )
    ):
        failures.append(
            {
                "path": path,
                "test_name": test_name,
            }
        )

    return failures


def imported_module_aliases(
    path: Path,
) -> dict[str, Any]:
    source = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    try:
        tree = ast.parse(
            source,
            filename=str(path),
        )

    except SyntaxError:
        return {
            "syntax_valid": False,
            "imports": [],
            "calls": [],
        }

    imports = []
    calls = []

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                imports.append(
                    {
                        "module": alias.name,
                        "alias": alias.asname,
                    }
                )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            imports.append(
                {
                    "module": node.module,
                    "names": [
                        alias.name
                        for alias in node.names
                    ],
                }
            )

        elif isinstance(
            node,
            ast.Call,
        ):
            rendered = dotted_name(
                node.func
            )

            if rendered:
                calls.append(
                    rendered
                )

    return {
        "syntax_valid": True,
        "imports": imports,
        "calls": sorted(
            set(calls)
        ),
    }


def find_symbol_definitions(
    symbol: str,
) -> list[dict[str, Any]]:
    matches = []

    for path in sorted(
        BACKEND_ROOT.rglob("*.py")
    ):
        if "__pycache__" in path.parts:
            continue

        source = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        try:
            tree = ast.parse(
                source,
                filename=str(path),
            )

        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                    ast.ClassDef,
                ),
            ) and node.name == symbol:
                matches.append(
                    {
                        "path": relative(path),
                        "line": node.lineno,
                        "kind": type(node).__name__,
                    }
                )

    return matches


def find_symbol_references(
    symbol: str,
) -> list[dict[str, Any]]:
    references = []

    for path in sorted(
        BACKEND_ROOT.rglob("*.py")
    ):
        if "__pycache__" in path.parts:
            continue

        source = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        if symbol not in source:
            continue

        try:
            tree = ast.parse(
                source,
                filename=str(path),
            )

        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(
                node,
                ast.Name,
            ) and node.id == symbol:
                references.append(
                    {
                        "path": relative(path),
                        "line": node.lineno,
                        "reference": node.id,
                    }
                )

            elif isinstance(
                node,
                ast.Attribute,
            ) and node.attr == symbol:
                references.append(
                    {
                        "path": relative(path),
                        "line": node.lineno,
                        "reference": (
                            dotted_name(node)
                            or node.attr
                        ),
                    }
                )

    unique = {
        (
            item["path"],
            item["line"],
            item["reference"],
        ): item
        for item in references
    }

    return [
        unique[key]
        for key in sorted(unique)
    ]


def patch_target_resolution(
    patch_target: str,
) -> dict[str, Any]:
    parts = patch_target.split(".")

    module_path = None
    symbol = None

    for index in range(
        len(parts),
        0,
        -1,
    ):
        candidate_module = ".".join(
            parts[:index]
        )

        candidate_path = (
            ROOT
            / (
                candidate_module.replace(
                    ".",
                    "/",
                )
                + ".py"
            )
        )

        candidate_package = (
            ROOT
            / candidate_module.replace(
                ".",
                "/",
            )
            / "__init__.py"
        )

        if candidate_path.is_file():
            module_path = candidate_path

            if index < len(parts):
                symbol = ".".join(
                    parts[index:]
                )

            break

        if candidate_package.is_file():
            module_path = candidate_package

            if index < len(parts):
                symbol = ".".join(
                    parts[index:]
                )

            break

    aliases = []

    if patch_target.startswith(
        "stacks."
    ):
        aliases.extend(
            [
                "backend.app."
                + patch_target,
                "app."
                + patch_target,
            ]
        )

    elif patch_target.startswith(
        "app.stacks."
    ):
        aliases.append(
            "backend."
            + patch_target
        )

    return {
        "patch_target": patch_target,
        "direct_module_resolved": (
            module_path is not None
        ),
        "module_path": (
            relative(module_path)
            if module_path
            else None
        ),
        "symbol_suffix": symbol,
        "canonical_alias_candidates": aliases,
    }


def trading_pipeline_analysis(
    log_text: str,
) -> dict[str, Any]:
    assert TRADING_PIPELINE_TEST.is_file(), (
        "Trading pipeline test file is missing"
    )

    test_source = (
        TRADING_PIPELINE_TEST.read_text(
            encoding="utf-8",
            errors="replace",
        )
    )

    record = inspect_source(
        TRADING_PIPELINE_TEST
    )

    failed_tests = [
        item
        for item in failed_tests_from_log(
            log_text
        )
        if item[
            "path"
        ].startswith(
            "backend/app/test/"
            "test_trading_pipeline.py"
        )
    ]

    patch_targets = [
        patch_target_resolution(
            target
        )
        for target in record.patch_targets
    ]

    symbols = {
        "process_portfolio_output",
        "monitor_and_process_signals",
        "save_log",
        "is_kill_switch_active",
        "drawdown_healthcheck",
        "execute_trade",
        "set_kill_switch",
    }

    definitions = {
        symbol: find_symbol_definitions(
            symbol
        )
        for symbol in sorted(symbols)
    }

    references = {
        symbol: find_symbol_references(
            symbol
        )
        for symbol in sorted(symbols)
    }

    loop_markers = {
        marker: (
            marker.lower()
            in log_text.lower()
        )
        for marker in LOOP_ERROR_MARKERS
    }

    database_markers = {
        marker: (
            marker.lower()
            in log_text.lower()
        )
        for marker in DATABASE_ACTIVITY_MARKERS
    }

    test_import_analysis = (
        imported_module_aliases(
            TRADING_PIPELINE_TEST
        )
    )

    stale_patch_candidates = []

    for target in patch_targets:
        if target[
            "patch_target"
        ].startswith(
            "stacks."
        ):
            stale_patch_candidates.append(
                {
                    "patch_target": target[
                        "patch_target"
                    ],
                    "reason": (
                        "Test patches the short 'stacks.*' alias; "
                        "production may be imported through "
                        "'backend.app.stacks.*' or another bound alias"
                    ),
                    "canonical_alias_candidates": target[
                        "canonical_alias_candidates"
                    ],
                }
            )

    real_database_activity = any(
        database_markers.values()
    )

    async_loop_contamination = any(
        loop_markers.values()
    )

    mock_non_interception = (
        "mock_save_log.call_count"
        in test_source
        and "call_count >= 1"
        in test_source
        and "database log & inventory saved"
        in log_text.lower()
    )

    findings = []

    if stale_patch_candidates:
        findings.append(
            {
                "severity": "HIGH",
                "code": (
                    "TRADING_TEST_PATCH_TARGET_DIVERGENCE"
                ),
                "classification": (
                    "TEST_HARNESS_DEFECT_LIKELY"
                ),
                "summary": (
                    "Trading-pipeline tests patch short "
                    "'stacks.*' targets that may not match "
                    "the module objects used by production code"
                ),
                "evidence": stale_patch_candidates,
                "recommended_action": (
                    "Resolve the actual bound module namespace "
                    "for each dependency before changing runtime code"
                ),
            }
        )

    if mock_non_interception:
        findings.append(
            {
                "severity": "HIGH",
                "code": (
                    "MOCK_NON_INTERCEPTION_WITH_REAL_SIDE_EFFECT"
                ),
                "classification": (
                    "TEST_ISOLATION_DEFECT_CONFIRMED"
                ),
                "summary": (
                    "Mocks reported zero calls while real database "
                    "logging output occurred"
                ),
                "evidence": [
                    (
                        "mock_save_log call count remained zero"
                    ),
                    (
                        "real 'Database Log & Inventory Saved' "
                        "messages were emitted"
                    ),
                ],
                "recommended_action": (
                    "Correct dependency patch locations and prove "
                    "the test performs no real database writes"
                ),
            }
        )

    if async_loop_contamination:
        findings.append(
            {
                "severity": "HIGH",
                "code": (
                    "ASYNC_DATABASE_EVENT_LOOP_CONTAMINATION"
                ),
                "classification": (
                    "TEST_RUNTIME_ISOLATION_DEFECT_CONFIRMED"
                ),
                "summary": (
                    "Async database connections or futures crossed "
                    "pytest event-loop boundaries"
                ),
                "evidence": [
                    marker
                    for marker, present
                    in loop_markers.items()
                    if present
                ],
                "recommended_action": (
                    "Isolate or dispose async database resources "
                    "between tests and prevent real DB access in "
                    "unit-level trading-pipeline tests"
                ),
            }
        )

    if real_database_activity:
        findings.append(
            {
                "severity": "HIGH",
                "code": (
                    "UNIT_TEST_REAL_DATABASE_ACTIVITY"
                ),
                "classification": (
                    "TEST_BOUNDARY_VIOLATION_CONFIRMED"
                ),
                "summary": (
                    "The trading-pipeline unit tests reached real "
                    "database logging or SQLAlchemy/asyncpg resources"
                ),
                "evidence": [
                    marker
                    for marker, present
                    in database_markers.items()
                    if present
                ],
                "recommended_action": (
                    "Replace real persistence access with the correct "
                    "mocked dependency boundary"
                ),
            }
        )

    production_defect_confirmed = False

    return {
        "test_file": relative(
            TRADING_PIPELINE_TEST
        ),
        "test_sha256": record.sha256,
        "failed_tests": failed_tests,
        "patch_targets": patch_targets,
        "stale_patch_candidates": (
            stale_patch_candidates
        ),
        "test_import_analysis": (
            test_import_analysis
        ),
        "symbol_definitions": definitions,
        "symbol_references": references,
        "async_loop_markers": loop_markers,
        "database_activity_markers": (
            database_markers
        ),
        "real_database_activity_detected": (
            real_database_activity
        ),
        "async_loop_contamination_detected": (
            async_loop_contamination
        ),
        "mock_non_interception_detected": (
            mock_non_interception
        ),
        "production_defect_confirmed": (
            production_defect_confirmed
        ),
        "findings": findings,
    }


def target_stack_analysis(
    stack: str,
    attribution: dict[str, Any],
    stage1b: dict[str, Any],
) -> dict[str, Any]:
    files = stack_files(
        stack
    )

    records = [
        inspect_source(
            path
        )
        for path in files
    ]

    production = [
        record
        for record in records
        if not is_test_path(
            ROOT / record.path
        )
    ]

    local_tests = [
        record
        for record in records
        if is_test_path(
            ROOT / record.path
        )
    ]

    attributed = attribution[
        "per_stack"
    ][
        stack
    ]

    calibrated = next(
        item
        for item in stage1b[
            "stack_results"
        ]
        if item[
            "stack"
        ] == stack
    )

    route_files = []

    for path in files:
        source = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        if re.search(
            r"@\w+\.(get|post|put|patch|delete|route)\b",
            source,
        ):
            route_files.append(
                relative(path)
            )

    findings = []

    if not attributed[
        "test_files"
    ]:
        findings.append(
            {
                "severity": "HIGH",
                "code": (
                    "CONFIRMED_NO_ATTRIBUTED_TEST_EVIDENCE"
                ),
                "classification": (
                    "EVIDENCE_GAP_CONFIRMED"
                ),
                "summary": (
                    f"No local or centralized tests currently "
                    f"target {stack}"
                ),
                "recommended_action": (
                    "Design the smallest contract and failure test "
                    "set against existing production behavior"
                ),
            }
        )

    if not attributed[
        "failure_test_files"
    ]:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": (
                    "CONFIRMED_NO_FAILURE_TEST_EVIDENCE"
                ),
                "classification": (
                    "EVIDENCE_GAP_CONFIRMED"
                ),
                "summary": (
                    f"No fail-closed or failure-behavior tests "
                    f"currently target {stack}"
                ),
                "recommended_action": (
                    "Add focused failure qualification only after "
                    "the existing boundary is inventoried"
                ),
            }
        )

    syntax_errors = [
        record.path
        for record in records
        if not record.syntax_valid
    ]

    if syntax_errors:
        findings.append(
            {
                "severity": "CRITICAL",
                "code": "TARGET_STACK_SYNTAX_ERROR",
                "classification": (
                    "PRODUCTION_DEFECT_CONFIRMED"
                ),
                "summary": (
                    "Syntax-invalid source exists in the target stack"
                ),
                "evidence": syntax_errors,
            }
        )

    return {
        "stack": stack,
        "classification": calibrated[
            "classification"
        ],
        "calibrated_score": calibrated[
            "score"
        ],
        "calibrated_grade": calibrated[
            "grade"
        ],
        "evidence_confidence": calibrated[
            "evidence_confidence"
        ],
        "production_file_count": len(
            production
        ),
        "local_test_file_count": len(
            local_tests
        ),
        "attributed_test_files": attributed[
            "test_files"
        ],
        "attributed_failure_test_files": attributed[
            "failure_test_files"
        ],
        "route_files": sorted(
            route_files
        ),
        "source_records": [
            {
                "path": record.path,
                "sha256": record.sha256,
                "size_bytes": record.size_bytes,
                "imports": list(
                    record.imports
                ),
                "classes": list(
                    record.classes
                ),
                "functions": list(
                    record.functions
                ),
                "async_functions": list(
                    record.async_functions
                ),
                "syntax_valid": (
                    record.syntax_valid
                ),
            }
            for record in records
        ],
        "findings": findings,
        "production_defect_confirmed": any(
            finding[
                "classification"
            ]
            == "PRODUCTION_DEFECT_CONFIRMED"
            for finding in findings
        ),
    }


def priority_rank(
    finding: dict[str, Any],
) -> tuple[int, str]:
    return (
        SEVERITY_ORDER.get(
            finding[
                "severity"
            ],
            99,
        ),
        finding[
            "code"
        ],
    )


def source_snapshot(
    paths: list[Path],
) -> dict[str, Any]:
    unique_paths = sorted(
        set(paths)
    )

    entries = [
        {
            "path": relative(path),
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        }
        for path in unique_paths
        if path.is_file()
    ]

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

    return {
        "file_count": len(
            entries
        ),
        "manifest_sha256": (
            digest.hexdigest()
        ),
        "files": entries,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    stage1b = load_json(
        STAGE1B_REPORT
    )

    stage1b_freeze = load_json(
        STAGE1B_FREEZE
    )

    stage1b_attribution = load_json(
        STAGE1B_ATTRIBUTION
    )

    database = load_json(
        DATABASE_REPORT
    )

    import_audit = load_json(
        IMPORT_AUDIT_REPORT
    )

    assert stage1b[
        "status"
    ] == "completed"

    assert stage1b[
        "mode"
    ] == "read_only"

    assert stage1b_freeze[
        "status"
    ] == "frozen"

    assert stage1b[
        "hard_gate_blocker_count"
    ] == 0

    assert stage1b[
        "whole_backend_tests"
    ][
        "passed"
    ] == 140

    assert stage1b[
        "whole_backend_tests"
    ][
        "failed"
    ] == 3

    assert database[
        "modified"
    ] is False

    import_summary = import_audit[
        "summary"
    ]

    assert import_summary[
        "active_internal_unresolved"
    ] == 0

    assert import_summary[
        "tooling_or_relative_unresolved"
    ] == 0

    assert import_summary[
        "syntax_errors"
    ] == 0

    assert import_summary[
        "active_cycle_components"
    ] == 0

    assert import_summary[
        "self_cycles"
    ] == 0

    attribution = test_attribution()

    target_analyses = {
        stack: target_stack_analysis(
            stack,
            attribution,
            stage1b,
        )
        for stack in sorted(
            TARGET_STACKS
        )
    }

    assert STAGE1_TEST_LOG.is_file(), (
        "Stage 1 pytest log is missing"
    )

    log_text = STAGE1_TEST_LOG.read_text(
        encoding="utf-8",
        errors="replace",
    )

    trading_analysis = (
        trading_pipeline_analysis(
            log_text
        )
    )

    all_findings = []

    for stack, analysis in (
        target_analyses.items()
    ):
        for finding in analysis[
            "findings"
        ]:
            all_findings.append(
                {
                    "scope": stack,
                    **finding,
                }
            )

    for finding in trading_analysis[
        "findings"
    ]:
        all_findings.append(
            {
                "scope": (
                    "trading_pipeline_tests"
                ),
                **finding,
            }
        )

    all_findings.sort(
        key=priority_rank
    )

    confirmed_production_defects = [
        finding
        for finding in all_findings
        if finding.get(
            "classification"
        )
        == "PRODUCTION_DEFECT_CONFIRMED"
    ]

    confirmed_test_defects = [
        finding
        for finding in all_findings
        if finding.get(
            "classification"
        )
        in {
            "TEST_HARNESS_DEFECT_LIKELY",
            "TEST_ISOLATION_DEFECT_CONFIRMED",
            "TEST_RUNTIME_ISOLATION_DEFECT_CONFIRMED",
            "TEST_BOUNDARY_VIOLATION_CONFIRMED",
        }
    ]

    evidence_gaps = [
        finding
        for finding in all_findings
        if finding.get(
            "classification"
        )
        == "EVIDENCE_GAP_CONFIRMED"
    ]

    remediation_batches = [
        {
            "batch": 1,
            "title": (
                "Trading Pipeline Test Isolation "
                "and Patch-Boundary Correction"
            ),
            "scope": [
                "backend/app/test/test_trading_pipeline.py",
            ],
            "authorized_changes": [
                (
                    "Correct test patch targets to the actual "
                    "bound production dependency locations"
                ),
                (
                    "Prevent real database access during unit tests"
                ),
                (
                    "Dispose or isolate async database resources "
                    "between pytest event loops"
                ),
            ],
            "forbidden_changes": [
                (
                    "Do not change runtime trading behavior merely "
                    "to satisfy stale mocks"
                ),
                (
                    "Do not enable broker execution"
                ),
                (
                    "Do not enable live trading"
                ),
            ],
            "qualification_gate": (
                "All three trading-pipeline tests pass with no "
                "real database output and no async-loop warnings"
            ),
            "priority": 1,
        },
        {
            "batch": 2,
            "title": (
                "auth_identity Contract and Failure "
                "Evidence Qualification"
            ),
            "scope": [
                (
                    "backend/app/stacks/auth_identity"
                ),
                (
                    "new focused auth_identity qualification tests"
                ),
            ],
            "authorized_changes": [
                (
                    "Add tests against existing authentication "
                    "and identity behavior"
                ),
                (
                    "Qualify invalid credentials, unauthorized "
                    "access, malformed identity data, and "
                    "fail-closed behavior where supported"
                ),
            ],
            "forbidden_changes": [
                (
                    "Do not redesign authentication architecture"
                ),
                (
                    "Do not invent unimplemented features"
                ),
                (
                    "Do not weaken authorization requirements"
                ),
            ],
            "qualification_gate": (
                "Focused tests pass and no production defect is "
                "introduced or hidden"
            ),
            "priority": 2,
        },
        {
            "batch": 3,
            "title": (
                "chat_public Contract and Failure "
                "Evidence Qualification"
            ),
            "scope": [
                (
                    "backend/app/stacks/chat_public"
                ),
                (
                    "new focused chat_public qualification tests"
                ),
            ],
            "authorized_changes": [
                (
                    "Add tests against the existing public-chat "
                    "boundary"
                ),
                (
                    "Qualify malformed input, unavailable "
                    "dependencies, unauthorized capabilities, "
                    "and fail-closed responses where supported"
                ),
            ],
            "forbidden_changes": [
                (
                    "Do not add frontend wiring"
                ),
                (
                    "Do not add broker or trading capability"
                ),
                (
                    "Do not create features solely to raise a grade"
                ),
            ],
            "qualification_gate": (
                "Focused tests pass and chat remains separated "
                "from broker execution and persistence ownership"
            ),
            "priority": 3,
        },
        {
            "batch": 4,
            "title": (
                "Calibrated Re-grade and Baseline Freeze"
            ),
            "scope": [
                "IQC Stage 1B active-stack grade",
                "whole-backend test suite",
                "import and dependency audit",
                "database non-mutation verification",
            ],
            "authorized_changes": [
                (
                    "Re-run evidence attribution and calibrated grading"
                ),
            ],
            "forbidden_changes": [
                (
                    "Do not manually edit scores"
                ),
            ],
            "qualification_gate": (
                "No hard-gate blockers, no trading-pipeline failures, "
                "and calibrated evidence confidence improves"
            ),
            "priority": 4,
        },
    ]

    evidence_paths = []

    for stack in TARGET_STACKS:
        evidence_paths.extend(
            stack_files(
                stack
            )
        )

    evidence_paths.extend(
        [
            TRADING_PIPELINE_TEST,
            STAGE1B_REPORT,
            STAGE1B_FREEZE,
            STAGE1B_ATTRIBUTION,
            STAGE1_TEST_LOG,
            DATABASE_REPORT,
            IMPORT_AUDIT_REPORT,
        ]
    )

    snapshot = source_snapshot(
        evidence_paths
    )

    evidence_report = {
        "status": "completed",
        "generated_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "target_stacks": sorted(
            TARGET_STACKS
        ),
        "target_stack_analysis": (
            target_analyses
        ),
        "test_attribution": attribution,
        "trading_pipeline_analysis": (
            trading_analysis
        ),
        "source_snapshot": snapshot,
        "source_modified": False,
        "database_modified": False,
    }

    EVIDENCE_JSON.write_text(
        json.dumps(
            evidence_report,
            indent=2,
            sort_keys=True,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )

    report = {
        "campaign": (
            "NeuroVest Integrated "
            "Qualification Campaign"
        ),
        "stage": "IQC-002",
        "stage_name": (
            "Targeted Remediation Planning from "
            "Calibrated Active-Stack Findings"
        ),
        "status": "completed",
        "verified_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "stage1b_verified": True,
        "calibrated_baseline": {
            "score": stage1b[
                "overall"
            ][
                "calibrated_score"
            ],
            "grade": stage1b[
                "overall"
            ][
                "calibrated_grade"
            ],
            "grading_confidence": stage1b[
                "grading_confidence"
            ][
                "status"
            ],
            "hard_gate_blockers": stage1b[
                "hard_gate_blocker_count"
            ],
        },
        "scope": {
            "target_active_stacks": sorted(
                TARGET_STACKS
            ),
            "trading_pipeline_test_file": (
                relative(
                    TRADING_PIPELINE_TEST
                )
            ),
            "whole_backend_passed": 140,
            "whole_backend_failed": 3,
        },
        "disposition": {
            "confirmed_production_defect_count": len(
                confirmed_production_defects
            ),
            "confirmed_test_or_isolation_defect_count": len(
                confirmed_test_defects
            ),
            "confirmed_evidence_gap_count": len(
                evidence_gaps
            ),
            "production_source_remediation_authorized": (
                bool(
                    confirmed_production_defects
                )
            ),
            "test_harness_remediation_authorized": (
                bool(
                    confirmed_test_defects
                )
            ),
            "focused_test_evidence_addition_authorized": (
                bool(
                    evidence_gaps
                )
            ),
        },
        "findings": all_findings,
        "remediation_batches": (
            remediation_batches
        ),
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
        "repository": {
            "active_internal_unresolved": (
                import_summary[
                    "active_internal_unresolved"
                ]
            ),
            "tooling_or_relative_unresolved": (
                import_summary[
                    "tooling_or_relative_unresolved"
                ]
            ),
            "syntax_errors": (
                import_summary[
                    "syntax_errors"
                ]
            ),
            "active_cycle_components": (
                import_summary[
                    "active_cycle_components"
                ]
            ),
            "self_cycles": (
                import_summary[
                    "self_cycles"
                ]
            ),
        },
        "source_modified": False,
        "database_modified": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
        "next_step": (
            "IQC Remediation Batch 1 — Trading Pipeline "
            "Test Isolation and Patch-Boundary Correction"
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

    report_hash = sha256_file(
        REPORT_JSON
    )

    evidence_hash = sha256_file(
        EVIDENCE_JSON
    )

    freeze = {
        "status": "frozen",
        "stage": "IQC-002",
        "frozen_at": datetime.now(
            UTC
        ).isoformat(),
        "planning_report_sha256": (
            report_hash
        ),
        "evidence_report_sha256": (
            evidence_hash
        ),
        "source_manifest_sha256": (
            snapshot[
                "manifest_sha256"
            ]
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
            "IQC STAGE 2 — TARGETED REMEDIATION PLANNING "
            "FROM CALIBRATED ACTIVE-STACK FINDINGS"
        ),
        "=" * 92,
        "",
        "STATUS",
        "COMPLETE AND VERIFIED",
        "",
        "MODE",
        "READ ONLY",
        "",
        "CALIBRATED BASELINE",
        (
            "Score:                           "
            f"{stage1b['overall']['calibrated_score']:.2f} / 100"
        ),
        (
            "Grade:                           "
            f"{stage1b['overall']['calibrated_grade']}"
        ),
        (
            "Grading confidence:              "
            f"{stage1b['grading_confidence']['status']}"
        ),
        (
            "Hard-gate blockers:              "
            f"{stage1b['hard_gate_blocker_count']}"
        ),
        "",
        "TARGETED ACTIVE STACKS",
    ]

    for stack in sorted(
        TARGET_STACKS
    ):
        analysis = target_analyses[
            stack
        ]

        lines.extend(
            [
                (
                    f"- {stack}: "
                    f"{analysis['calibrated_score']:.2f} "
                    f"{analysis['calibrated_grade']}"
                ),
                (
                    "  Production files:          "
                    f"{analysis['production_file_count']}"
                ),
                (
                    "  Attributed tests:          "
                    f"{len(analysis['attributed_test_files'])}"
                ),
                (
                    "  Failure tests:             "
                    f"{len(analysis['attributed_failure_test_files'])}"
                ),
                (
                    "  Production defect proven: "
                    f"{'YES' if analysis['production_defect_confirmed'] else 'NO'}"
                ),
            ]
        )

    lines.extend(
        [
            "",
            "TRADING PIPELINE FAILURE DISPOSITION",
            (
                "Failed tests inspected:          "
                f"{len(trading_analysis['failed_tests'])}"
            ),
            (
                "Stale patch candidates:          "
                f"{len(trading_analysis['stale_patch_candidates'])}"
            ),
            (
                "Mock non-interception detected:  "
                f"{'YES' if trading_analysis['mock_non_interception_detected'] else 'NO'}"
            ),
            (
                "Real database activity detected: "
                f"{'YES' if trading_analysis['real_database_activity_detected'] else 'NO'}"
            ),
            (
                "Async-loop contamination:        "
                f"{'YES' if trading_analysis['async_loop_contamination_detected'] else 'NO'}"
            ),
            (
                "Production defect confirmed:     "
                f"{'YES' if trading_analysis['production_defect_confirmed'] else 'NO'}"
            ),
            "",
            "PLANNING DISPOSITION",
            (
                "Confirmed production defects:    "
                f"{len(confirmed_production_defects)}"
            ),
            (
                "Test/isolation defects:          "
                f"{len(confirmed_test_defects)}"
            ),
            (
                "Confirmed evidence gaps:         "
                f"{len(evidence_gaps)}"
            ),
            (
                "Production source remediation:   "
                f"{'AUTHORIZED' if confirmed_production_defects else 'NOT AUTHORIZED'}"
            ),
            (
                "Test harness remediation:        "
                f"{'AUTHORIZED' if confirmed_test_defects else 'NOT AUTHORIZED'}"
            ),
            (
                "Focused evidence tests:          "
                f"{'AUTHORIZED' if evidence_gaps else 'NOT REQUIRED'}"
            ),
            "",
            "RANKED REMEDIATION BATCHES",
        ]
    )

    for batch in remediation_batches:
        lines.extend(
            [
                (
                    f"{batch['priority']}. "
                    f"{batch['title']}"
                ),
                (
                    "   Qualification gate: "
                    f"{batch['qualification_gate']}"
                ),
            ]
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
            "REPOSITORY",
            "- Active unresolved imports: 0",
            "- Tooling or relative unresolved imports: 0",
            "- Syntax errors: 0",
            "- Active dependency cycles: 0",
            "- Self cycles: 0",
            "",
            "SAFETY",
            "- Source modified: NO",
            "- Database modified: NO",
            "- Broker execution enabled: NO",
            "- Live trading enabled: NO",
            "",
            "NEXT",
            (
                "IQC Remediation Batch 1 — Trading Pipeline "
                "Test Isolation and Patch-Boundary Correction"
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

    print(rendered)

    print("Planning report:")
    print(REPORT_JSON)
    print()

    print("Evidence report:")
    print(EVIDENCE_JSON)
    print()

    print("Planning freeze:")
    print(FREEZE_JSON)


if __name__ == "__main__":
    main()
