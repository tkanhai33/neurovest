#!/usr/bin/env python3
"""
NeuroVest Integrated Qualification Campaign

IQC Stage 5 —
Remaining Active-Stack Flow Qualification
and Completion Map

MODE
READ ONLY

Purpose:
- Verify the authoritative IQC Batch 4 baseline.
- Inspect remaining weaker implemented stacks.
- Determine what each stack currently implements.
- Identify missing contracts, failure qualification, timeout controls,
  observability, boundary evidence, integration evidence, and safety gates.
- Separate production defects from qualification gaps.
- Produce a ranked completion and remediation map.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from collections import defaultdict
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
    / "stage5"
)

BATCH4_REPORT = (
    RUNTIME_ROOT
    / "iqc"
    / "remediation_batch4"
    / "iqc_remediation_batch4_regrade_latest.json"
)

BATCH4_GRADEBOOK = (
    RUNTIME_ROOT
    / "iqc"
    / "remediation_batch4"
    / "iqc_remediation_batch4_gradebook_latest.json"
)

BATCH4_FREEZE = (
    RUNTIME_ROOT
    / "iqc"
    / "remediation_batch4"
    / "iqc_remediation_batch4_freeze_latest.json"
)

IMPORT_AUDIT_REPORT = (
    RUNTIME_ROOT
    / "hardening"
    / "workstream1"
    / "import_cycle_audit_latest.json"
)

DATABASE_REPORT = (
    RUNTIME_ROOT
    / "iqc"
    / "remediation_batch3d"
    / "database_after.json"
)

FULL_TEST_LOG = (
    RUNTIME_ROOT
    / "iqc"
    / "remediation_batch3d"
    / "full_backend_tests_latest.log"
)

REPORT_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_completion_map_latest.json"
)

REPORT_TEXT = (
    OUTPUT_DIR
    / "iqc_stage5_completion_map_latest.txt"
)

EVIDENCE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_completion_evidence_latest.json"
)

FREEZE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_completion_map_freeze_latest.json"
)

SOURCE_MANIFEST = (
    OUTPUT_DIR
    / "iqc_stage5_source_manifest_latest.json"
)

TARGET_STACKS = (
    "wolfden_ai",
    "execution",
    "chat_public",
    "portfolio",
    "risk",
    "strategy",
)

EXPECTED_BATCH4_SCORE = 87.65
EXPECTED_BATCH4_GRADE = "B+"

ROUTE_METHODS = {
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "route",
    "websocket",
}

CONTRACT_BASES = {
    "BaseModel",
    "TypedDict",
    "Protocol",
    "ABC",
    "Enum",
}

FAILURE_MARKERS = (
    "except",
    "raise ",
    "error",
    "failure",
    "invalid",
    "denied",
    "blocked",
    "unavailable",
    "timeout",
    "fail_closed",
)

TIMEOUT_MARKERS = (
    "asyncio.wait_for",
    "timeout=",
    "timeout_after",
    "fail_after",
    "connect_timeout",
    "read_timeout",
)

OBSERVABILITY_MARKERS = (
    "logger",
    "logging",
    "metrics",
    "telemetry",
    "trace",
    "health",
    "counter",
    "histogram",
)

VALIDATION_MARKERS = (
    "validate",
    "validator",
    "validation",
    "field_validator",
    "model_validator",
    "min_length",
    "max_length",
    "ge=",
    "le=",
)

IDEMPOTENCY_MARKERS = (
    "idempotency",
    "idempotent",
    "request_id",
    "operation_id",
    "dedup",
)

RETRY_MARKERS = (
    "retry",
    "backoff",
    "max_attempts",
)

TRANSACTION_MARKERS = (
    "commit",
    "rollback",
    "transaction",
    "begin",
    "flush",
)

MUTATION_TERMINALS = {
    "add",
    "append",
    "commit",
    "delete",
    "execute",
    "execute_order",
    "execute_trade",
    "flush",
    "insert",
    "merge",
    "place_order",
    "rollback",
    "save",
    "submit_order",
    "update",
    "upsert",
}

FORBIDDEN_LIVE_MARKERS = (
    "live_trading_enabled = true",
    "live_trading_enabled: true",
    "broker_execution_enabled = true",
    "broker_execution_enabled: true",
    "execution_enabled = true",
    "execution_enabled: true",
)

TEST_FAILURE_MARKERS = (
    "pytest.raises",
    "raises(",
    "invalid",
    "failure",
    "error",
    "timeout",
    "blocked",
    "denied",
    "unavailable",
)

TEST_INTEGRATION_MARKERS = (
    "testclient",
    "httpx",
    "asyncclient",
    "database",
    "session",
    "end_to_end",
    "integration",
    "pipeline",
)

SEVERITY_ORDER = {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3,
    "OBSERVATION": 4,
}

STACK_PRIORITY = {
    "execution": 1,
    "risk": 2,
    "portfolio": 3,
    "strategy": 4,
    "wolfden_ai": 5,
    "chat_public": 6,
}


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


def relative(
    path: Path,
) -> str:
    return path.relative_to(
        ROOT
    ).as_posix()


def sha256_file(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def python_files(
    root: Path,
) -> list[Path]:
    if not root.is_dir():
        return []

    return [
        path
        for path in sorted(
            root.rglob("*.py")
        )
        if "__pycache__" not in path.parts
    ]


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


def imported_stack(
    module: str,
) -> str | None:
    prefixes = (
        "backend.app.stacks.",
        "app.stacks.",
        "stacks.",
    )

    for prefix in prefixes:
        if module.startswith(
            prefix
        ):
            return module[
                len(prefix):
            ].split(".")[0]

    return None


def annotation_text(
    annotation: ast.expr | None,
) -> str | None:
    if annotation is None:
        return None

    try:
        return ast.unparse(
            annotation
        )

    except Exception:
        return None


def inspect_source(
    path: Path,
) -> dict[str, Any]:
    source = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    lowered = source.lower()

    try:
        tree = ast.parse(
            source,
            filename=str(path),
        )

    except SyntaxError as exc:
        return {
            "path": relative(path),
            "sha256": sha256_file(path),
            "syntax_valid": False,
            "syntax_error": str(exc),
            "imports": [],
            "imported_stacks": [],
            "classes": [],
            "contracts": [],
            "functions": [],
            "public_functions": [],
            "async_functions": [],
            "routes": [],
            "mutation_calls": [],
            "failure_markers": [],
            "timeout_markers": [],
            "observability_markers": [],
            "validation_markers": [],
            "idempotency_markers": [],
            "retry_markers": [],
            "transaction_markers": [],
            "forbidden_live_markers": [],
        }

    imports = set()
    imported_stacks = set()
    classes = []
    contracts = []
    functions = []
    public_functions = []
    async_functions = []
    routes = []
    mutation_calls = []

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                imports.add(
                    alias.name
                )

                stack = imported_stack(
                    alias.name
                )

                if stack:
                    imported_stacks.add(
                        stack
                    )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            if node.module:
                imports.add(
                    node.module
                )

                stack = imported_stack(
                    node.module
                )

                if stack:
                    imported_stacks.add(
                        stack
                    )

        elif isinstance(
            node,
            ast.ClassDef,
        ):
            bases = sorted(
                {
                    dotted_name(base)
                    or ""
                    for base in node.bases
                }
            )

            base_terminals = {
                base.split(".")[-1]
                for base in bases
            }

            fields = []

            for statement in node.body:
                if not isinstance(
                    statement,
                    ast.AnnAssign,
                ):
                    continue

                if not isinstance(
                    statement.target,
                    ast.Name,
                ):
                    continue

                fields.append(
                    {
                        "name": statement.target.id,
                        "annotation": annotation_text(
                            statement.annotation
                        ),
                        "has_default": (
                            statement.value is not None
                        ),
                    }
                )

            classes.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "bases": bases,
                    "field_count": len(
                        fields
                    ),
                }
            )

            if (
                base_terminals
                & CONTRACT_BASES
                or fields
            ):
                contracts.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "bases": bases,
                        "fields": fields,
                    }
                )

        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            function = {
                "name": node.name,
                "line": node.lineno,
                "async": isinstance(
                    node,
                    ast.AsyncFunctionDef,
                ),
                "return_annotation": annotation_text(
                    node.returns
                ),
                "parameter_count": len(
                    node.args.args
                ),
            }

            functions.append(
                function
            )

            if not node.name.startswith("_"):
                public_functions.append(
                    function
                )

            if isinstance(
                node,
                ast.AsyncFunctionDef,
            ):
                async_functions.append(
                    function
                )

            route_decorators = []

            for decorator in node.decorator_list:
                expression = (
                    decorator.func
                    if isinstance(
                        decorator,
                        ast.Call,
                    )
                    else decorator
                )

                name = dotted_name(
                    expression
                )

                if not name:
                    continue

                if (
                    name.split(".")[-1]
                    in ROUTE_METHODS
                ):
                    route_decorators.append(
                        ast.unparse(
                            decorator
                        )
                    )

            if route_decorators:
                routes.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "decorators": route_decorators,
                        "return_annotation": (
                            annotation_text(
                                node.returns
                            )
                        ),
                    }
                )

        elif isinstance(
            node,
            ast.Call,
        ):
            rendered = dotted_name(
                node.func
            )

            if not rendered:
                continue

            terminal = rendered.split(".")[-1]

            if terminal in MUTATION_TERMINALS:
                mutation_calls.append(
                    {
                        "line": node.lineno,
                        "call": rendered,
                    }
                )

    return {
        "path": relative(path),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
        "syntax_valid": True,
        "imports": sorted(
            imports
        ),
        "imported_stacks": sorted(
            imported_stacks
        ),
        "classes": classes,
        "contracts": contracts,
        "functions": functions,
        "public_functions": public_functions,
        "async_functions": async_functions,
        "routes": routes,
        "mutation_calls": mutation_calls,
        "failure_markers": [
            marker
            for marker in FAILURE_MARKERS
            if marker in lowered
        ],
        "timeout_markers": [
            marker
            for marker in TIMEOUT_MARKERS
            if marker in lowered
        ],
        "observability_markers": [
            marker
            for marker in OBSERVABILITY_MARKERS
            if marker in lowered
        ],
        "validation_markers": [
            marker
            for marker in VALIDATION_MARKERS
            if marker in lowered
        ],
        "idempotency_markers": [
            marker
            for marker in IDEMPOTENCY_MARKERS
            if marker in lowered
        ],
        "retry_markers": [
            marker
            for marker in RETRY_MARKERS
            if marker in lowered
        ],
        "transaction_markers": [
            marker
            for marker in TRANSACTION_MARKERS
            if marker in lowered
        ],
        "forbidden_live_markers": [
            marker
            for marker in FORBIDDEN_LIVE_MARKERS
            if marker in lowered
        ],
    }


def discover_tests(
    stack: str,
) -> list[dict[str, Any]]:
    results = []

    tokens = (
        f"backend.app.stacks.{stack}",
        f"app.stacks.{stack}",
        f"stacks.{stack}",
        f"/stacks/{stack}/",
    )

    stack_root = (
        STACKS_ROOT
        / stack
    )

    for path in python_files(
        BACKEND_ROOT
    ):
        if not is_test_path(
            path
        ):
            continue

        source = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        lowered = source.lower()

        reasons = [
            token
            for token in tokens
            if token.lower() in lowered
        ]

        if stack_root in path.parents:
            reasons.append(
                "local_stack_test"
            )

        if not reasons:
            continue

        results.append(
            {
                "path": relative(path),
                "reasons": sorted(
                    set(reasons)
                ),
                "failure_evidence": any(
                    marker in lowered
                    for marker in TEST_FAILURE_MARKERS
                ),
                "integration_evidence": any(
                    marker in lowered
                    for marker in TEST_INTEGRATION_MARKERS
                ),
                "timeout_evidence": (
                    "timeout" in lowered
                    or "wait_for" in lowered
                ),
                "contract_evidence": any(
                    marker in lowered
                    for marker in (
                        "contract",
                        "schema",
                        "request",
                        "response",
                        "validation",
                    )
                ),
                "mutation_evidence": any(
                    marker in lowered
                    for marker in (
                        "commit",
                        "rollback",
                        "save",
                        "execute_trade",
                        "place_order",
                        "append",
                    )
                ),
            }
        )

    return results


def stack_grade(
    gradebook: dict[str, Any],
    stack: str,
) -> dict[str, Any]:
    for item in gradebook[
        "active_stack_results"
    ]:
        if item[
            "stack"
        ] == stack:
            return item

    raise AssertionError(
        f"Batch 4 grade missing for {stack}"
    )


def stack_analysis(
    stack: str,
    gradebook: dict[str, Any],
) -> dict[str, Any]:
    stack_root = (
        STACKS_ROOT
        / stack
    )

    assert stack_root.is_dir(), (
        f"Target stack missing: {stack_root}"
    )

    files = python_files(
        stack_root
    )

    records = [
        inspect_source(
            path
        )
        for path in files
    ]

    production_records = [
        record
        for record in records
        if not is_test_path(
            ROOT
            / record[
                "path"
            ]
        )
    ]

    local_test_records = [
        record
        for record in records
        if is_test_path(
            ROOT
            / record[
                "path"
            ]
        )
    ]

    attributed_tests = discover_tests(
        stack
    )

    failure_tests = [
        item
        for item in attributed_tests
        if item[
            "failure_evidence"
        ]
    ]

    integration_tests = [
        item
        for item in attributed_tests
        if item[
            "integration_evidence"
        ]
    ]

    timeout_tests = [
        item
        for item in attributed_tests
        if item[
            "timeout_evidence"
        ]
    ]

    contract_tests = [
        item
        for item in attributed_tests
        if item[
            "contract_evidence"
        ]
    ]

    syntax_errors = [
        record
        for record in records
        if not record[
            "syntax_valid"
        ]
    ]

    contracts = [
        {
            "path": record[
                "path"
            ],
            **contract,
        }
        for record in production_records
        for contract in record[
            "contracts"
        ]
    ]

    routes = [
        {
            "path": record[
                "path"
            ],
            **route,
        }
        for record in production_records
        for route in record[
            "routes"
        ]
    ]

    public_functions = [
        {
            "path": record[
                "path"
            ],
            **function,
        }
        for record in production_records
        for function in record[
            "public_functions"
        ]
    ]

    async_functions = [
        {
            "path": record[
                "path"
            ],
            **function,
        }
        for record in production_records
        for function in record[
            "async_functions"
        ]
    ]

    mutation_calls = [
        {
            "path": record[
                "path"
            ],
            **call,
        }
        for record in production_records
        for call in record[
            "mutation_calls"
        ]
    ]

    imported_stacks = defaultdict(
        list
    )

    for record in production_records:
        for imported in record[
            "imported_stacks"
        ]:
            imported_stacks[
                imported
            ].append(
                record[
                    "path"
                ]
            )

    failure_files = [
        record[
            "path"
        ]
        for record in production_records
        if record[
            "failure_markers"
        ]
    ]

    timeout_files = [
        record[
            "path"
        ]
        for record in production_records
        if record[
            "timeout_markers"
        ]
    ]

    observability_files = [
        record[
            "path"
        ]
        for record in production_records
        if record[
            "observability_markers"
        ]
    ]

    validation_files = [
        record[
            "path"
        ]
        for record in production_records
        if record[
            "validation_markers"
        ]
    ]

    idempotency_files = [
        record[
            "path"
        ]
        for record in production_records
        if record[
            "idempotency_markers"
        ]
    ]

    retry_files = [
        record[
            "path"
        ]
        for record in production_records
        if record[
            "retry_markers"
        ]
    ]

    transaction_files = [
        record[
            "path"
        ]
        for record in production_records
        if record[
            "transaction_markers"
        ]
    ]

    forbidden_live_signals = [
        {
            "path": record[
                "path"
            ],
            "markers": record[
                "forbidden_live_markers"
            ],
        }
        for record in production_records
        if record[
            "forbidden_live_markers"
        ]
    ]

    gates = [
        {
            "gate": "Production source exists",
            "complete": bool(
                production_records
            ),
            "severity": "CRITICAL",
            "category": "implementation",
        },
        {
            "gate": "Public contract evidence exists",
            "complete": bool(
                contracts
            )
            or all(
                item[
                    "return_annotation"
                ]
                for item in public_functions
            ),
            "severity": "HIGH",
            "category": "contract",
        },
        {
            "gate": "Input validation evidence exists",
            "complete": bool(
                validation_files
            )
            or bool(
                contracts
            ),
            "severity": "HIGH",
            "category": "validation",
        },
        {
            "gate": "Failure behavior exists",
            "complete": bool(
                failure_files
            ),
            "severity": "HIGH",
            "category": "failure",
        },
        {
            "gate": "Timeout control exists where async work exists",
            "complete": (
                not async_functions
                or bool(
                    timeout_files
                )
            ),
            "severity": "HIGH",
            "category": "timeout",
        },
        {
            "gate": "Observability evidence exists",
            "complete": bool(
                observability_files
            ),
            "severity": "MEDIUM",
            "category": "observability",
        },
        {
            "gate": "Focused tests exist",
            "complete": bool(
                attributed_tests
            ),
            "severity": "HIGH",
            "category": "tests",
        },
        {
            "gate": "Failure tests exist",
            "complete": bool(
                failure_tests
            ),
            "severity": "HIGH",
            "category": "tests",
        },
        {
            "gate": "Integration tests exist",
            "complete": bool(
                integration_tests
            ),
            "severity": "MEDIUM",
            "category": "tests",
        },
        {
            "gate": "Contract tests exist",
            "complete": bool(
                contract_tests
            ),
            "severity": "MEDIUM",
            "category": "tests",
        },
        {
            "gate": "Timeout tests exist when timeout control is required",
            "complete": (
                not async_functions
                or bool(
                    timeout_tests
                )
            ),
            "severity": "MEDIUM",
            "category": "tests",
        },
        {
            "gate": "No syntax errors",
            "complete": not bool(
                syntax_errors
            ),
            "severity": "CRITICAL",
            "category": "repository",
        },
        {
            "gate": "No live or broker enablement markers",
            "complete": not bool(
                forbidden_live_signals
            ),
            "severity": "CRITICAL",
            "category": "safety",
        },
    ]

    if stack == "execution":
        gates.extend(
            [
                {
                    "gate": "Idempotency evidence exists",
                    "complete": bool(
                        idempotency_files
                    ),
                    "severity": "HIGH",
                    "category": "execution_safety",
                },
                {
                    "gate": "Transaction or rollback evidence exists",
                    "complete": bool(
                        transaction_files
                    ),
                    "severity": "HIGH",
                    "category": "execution_safety",
                },
                {
                    "gate": "Execution mutation tests exist",
                    "complete": any(
                        item[
                            "mutation_evidence"
                        ]
                        for item in attributed_tests
                    ),
                    "severity": "HIGH",
                    "category": "execution_safety",
                },
            ]
        )

    if stack == "risk":
        gates.extend(
            [
                {
                    "gate": "Fail-closed risk behavior tested",
                    "complete": bool(
                        failure_tests
                    ),
                    "severity": "CRITICAL",
                    "category": "risk_safety",
                },
                {
                    "gate": "Risk observability exists",
                    "complete": bool(
                        observability_files
                    ),
                    "severity": "HIGH",
                    "category": "risk_safety",
                },
            ]
        )

    if stack == "portfolio":
        gates.extend(
            [
                {
                    "gate": "Portfolio mutation boundaries tested",
                    "complete": any(
                        item[
                            "mutation_evidence"
                        ]
                        for item in attributed_tests
                    ),
                    "severity": "HIGH",
                    "category": "portfolio_integrity",
                },
                {
                    "gate": "Portfolio integration tests exist",
                    "complete": bool(
                        integration_tests
                    ),
                    "severity": "HIGH",
                    "category": "portfolio_integrity",
                },
            ]
        )

    if stack == "strategy":
        gates.extend(
            [
                {
                    "gate": "Strategy failure and no-signal behavior tested",
                    "complete": bool(
                        failure_tests
                    ),
                    "severity": "HIGH",
                    "category": "strategy_safety",
                },
                {
                    "gate": "Strategy integration evidence exists",
                    "complete": bool(
                        integration_tests
                    ),
                    "severity": "MEDIUM",
                    "category": "strategy_safety",
                },
            ]
        )

    if stack == "wolfden_ai":
        gates.extend(
            [
                {
                    "gate": "AI dependency timeout exists",
                    "complete": bool(
                        timeout_files
                    ),
                    "severity": "HIGH",
                    "category": "ai_safety",
                },
                {
                    "gate": "AI dependency failure tests exist",
                    "complete": bool(
                        failure_tests
                    ),
                    "severity": "HIGH",
                    "category": "ai_safety",
                },
                {
                    "gate": "AI output contract evidence exists",
                    "complete": bool(
                        contracts
                    ),
                    "severity": "HIGH",
                    "category": "ai_safety",
                },
            ]
        )

    if stack == "chat_public":
        gates.extend(
            [
                {
                    "gate": "Public-control implementation remains present",
                    "complete": any(
                        record[
                            "path"
                        ].endswith(
                            "public_controls.py"
                        )
                        for record in production_records
                    ),
                    "severity": "CRITICAL",
                    "category": "chat_safety",
                },
                {
                    "gate": "Public-control focused tests remain present",
                    "complete": any(
                        item[
                            "path"
                        ].endswith(
                            "test_public_chat_controls.py"
                        )
                        for item in attributed_tests
                    ),
                    "severity": "CRITICAL",
                    "category": "chat_safety",
                },
            ]
        )

    missing_gates = [
        gate
        for gate in gates
        if not gate[
            "complete"
        ]
    ]

    critical_missing = [
        gate
        for gate in missing_gates
        if gate[
            "severity"
        ] == "CRITICAL"
    ]

    high_missing = [
        gate
        for gate in missing_gates
        if gate[
            "severity"
        ] == "HIGH"
    ]

    medium_missing = [
        gate
        for gate in missing_gates
        if gate[
            "severity"
        ] == "MEDIUM"
    ]

    if critical_missing:
        disposition = (
            "BLOCKED_PRODUCTION_DEFECT_OR_SAFETY_GAP"
        )

    elif high_missing:
        disposition = (
            "IMPLEMENTED_REQUIRES_HIGH_PRIORITY_QUALIFICATION"
        )

    elif medium_missing:
        disposition = (
            "IMPLEMENTED_REQUIRES_EVIDENCE_COMPLETION"
        )

    else:
        disposition = (
            "FLOW_QUALIFIED"
        )

    grade = stack_grade(
        gradebook,
        stack,
    )

    completion_ratio = round(
        (
            sum(
                1
                for gate in gates
                if gate[
                    "complete"
                ]
            )
            / len(gates)
        )
        * 100.0,
        1,
    )

    estimated_remaining_effort = (
        len(critical_missing)
        * 5
        + len(high_missing)
        * 3
        + len(medium_missing)
        * 1
    )

    findings = []

    for gate in missing_gates:
        findings.append(
            {
                "severity": gate[
                    "severity"
                ],
                "code": (
                    "MISSING_"
                    + re.sub(
                        r"[^A-Z0-9]+",
                        "_",
                        gate[
                            "gate"
                        ].upper(),
                    ).strip("_")
                ),
                "summary": (
                    gate[
                        "gate"
                    ]
                    + " is not yet qualified"
                ),
                "category": gate[
                    "category"
                ],
            }
        )

    findings.sort(
        key=lambda item: (
            SEVERITY_ORDER[
                item[
                    "severity"
                ]
            ],
            item[
                "code"
            ],
        )
    )

    return {
        "stack": stack,
        "batch4_score": grade[
            "adjusted_score"
        ],
        "batch4_grade": grade[
            "adjusted_grade"
        ],
        "implementation_state": (
            grade[
                "implementation_state"
            ]
        ),
        "disposition": disposition,
        "production_file_count": len(
            production_records
        ),
        "local_test_file_count": len(
            local_test_records
        ),
        "attributed_test_count": len(
            attributed_tests
        ),
        "failure_test_count": len(
            failure_tests
        ),
        "integration_test_count": len(
            integration_tests
        ),
        "contract_test_count": len(
            contract_tests
        ),
        "timeout_test_count": len(
            timeout_tests
        ),
        "public_function_count": len(
            public_functions
        ),
        "async_function_count": len(
            async_functions
        ),
        "route_count": len(
            routes
        ),
        "contract_count": len(
            contracts
        ),
        "mutation_call_count": len(
            mutation_calls
        ),
        "failure_file_count": len(
            failure_files
        ),
        "timeout_file_count": len(
            timeout_files
        ),
        "observability_file_count": len(
            observability_files
        ),
        "validation_file_count": len(
            validation_files
        ),
        "idempotency_file_count": len(
            idempotency_files
        ),
        "retry_file_count": len(
            retry_files
        ),
        "transaction_file_count": len(
            transaction_files
        ),
        "imported_stacks": {
            imported: sorted(
                set(paths)
            )
            for imported, paths
            in sorted(
                imported_stacks.items()
            )
        },
        "syntax_errors": syntax_errors,
        "forbidden_live_signals": (
            forbidden_live_signals
        ),
        "qualification_gates": gates,
        "total_gate_count": len(
            gates
        ),
        "completed_gate_count": (
            len(gates)
            - len(missing_gates)
        ),
        "remaining_gate_count": len(
            missing_gates
        ),
        "critical_missing_count": len(
            critical_missing
        ),
        "high_missing_count": len(
            high_missing
        ),
        "medium_missing_count": len(
            medium_missing
        ),
        "completion_ratio": (
            completion_ratio
        ),
        "estimated_remaining_effort_points": (
            estimated_remaining_effort
        ),
        "findings": findings,
        "source_records": records,
        "attributed_tests": attributed_tests,
    }


def source_manifest() -> dict[str, Any]:
    entries = []

    for path in python_files(
        BACKEND_ROOT
    ):
        entries.append(
            {
                "path": relative(path),
                "sha256": sha256_file(
                    path
                ),
                "size_bytes": path.stat().st_size,
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
        "file_count": len(
            entries
        ),
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

    batch4 = load_json(
        BATCH4_REPORT
    )

    gradebook = load_json(
        BATCH4_GRADEBOOK
    )

    freeze = load_json(
        BATCH4_FREEZE
    )

    import_audit = load_json(
        IMPORT_AUDIT_REPORT
    )

    database = load_json(
        DATABASE_REPORT
    )

    assert batch4[
        "status"
    ] == "completed"

    assert batch4[
        "mode"
    ] == "read_only"

    assert batch4[
        "current_baseline"
    ][
        "authoritative"
    ] is True

    assert batch4[
        "current_baseline"
    ][
        "score"
    ] == EXPECTED_BATCH4_SCORE

    assert batch4[
        "current_baseline"
    ][
        "grade"
    ] == EXPECTED_BATCH4_GRADE

    assert gradebook[
        "grading_model"
    ] == (
        "IMPLEMENTATION_STATE_AWARE"
    )

    assert freeze[
        "status"
    ] == "frozen"

    assert freeze[
        "authoritative_score"
    ] == EXPECTED_BATCH4_SCORE

    assert freeze[
        "authoritative_grade"
    ] == EXPECTED_BATCH4_GRADE

    assert batch4[
        "evidence"
    ][
        "whole_backend_passed"
    ] >= 158

    assert batch4[
        "evidence"
    ][
        "whole_backend_failed"
    ] == 0

    assert batch4[
        "auth_implemented"
    ] is False

    assert batch4[
        "snaptrade_connected"
    ] is False

    assert batch4[
        "broker_execution_enabled"
    ] is False

    assert batch4[
        "live_trading_enabled"
    ] is False

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

    analyses = [
        stack_analysis(
            stack,
            gradebook,
        )
        for stack in TARGET_STACKS
    ]

    critical_stacks = [
        item
        for item in analyses
        if item[
            "critical_missing_count"
        ] > 0
    ]

    high_priority_stacks = [
        item
        for item in analyses
        if (
            item[
                "critical_missing_count"
            ] == 0
            and item[
                "high_missing_count"
            ] > 0
        )
    ]

    evidence_only_stacks = [
        item
        for item in analyses
        if (
            item[
                "critical_missing_count"
            ] == 0
            and item[
                "high_missing_count"
            ] == 0
            and item[
                "medium_missing_count"
            ] > 0
        )
    ]

    qualified_stacks = [
        item
        for item in analyses
        if item[
            "remaining_gate_count"
        ] == 0
    ]

    ranked = sorted(
        analyses,
        key=lambda item: (
            0
            if item[
                "critical_missing_count"
            ] > 0
            else (
                1
                if item[
                    "high_missing_count"
                ] > 0
                else (
                    2
                    if item[
                        "medium_missing_count"
                    ] > 0
                    else 3
                )
            ),
            -item[
                "estimated_remaining_effort_points"
            ],
            STACK_PRIORITY[
                item[
                    "stack"
                ]
            ],
        ),
    )

    remediation_batches = []

    batch_number = 1

    for item in ranked:
        if item[
            "remaining_gate_count"
        ] == 0:
            continue

        scope = []

        categories = sorted(
            {
                finding[
                    "category"
                ]
                for finding in item[
                    "findings"
                ]
            }
        )

        for category in categories:
            scope.append(
                category
            )

        remediation_batches.append(
            {
                "priority": batch_number,
                "stack": item[
                    "stack"
                ],
                "title": (
                    f"{item['stack']} Flow Completion "
                    "and Qualification"
                ),
                "disposition": item[
                    "disposition"
                ],
                "batch4_score": item[
                    "batch4_score"
                ],
                "batch4_grade": item[
                    "batch4_grade"
                ],
                "completion_ratio": item[
                    "completion_ratio"
                ],
                "remaining_gate_count": item[
                    "remaining_gate_count"
                ],
                "critical_missing_count": item[
                    "critical_missing_count"
                ],
                "high_missing_count": item[
                    "high_missing_count"
                ],
                "medium_missing_count": item[
                    "medium_missing_count"
                ],
                "estimated_effort_points": item[
                    "estimated_remaining_effort_points"
                ],
                "scope_categories": scope,
                "authorized_work": [
                    (
                        "Add only missing contract, failure, timeout, "
                        "observability, integration, or safety evidence"
                    ),
                    (
                        "Preserve existing stack ownership and public APIs"
                    ),
                    (
                        "Re-run focused and whole-backend qualification"
                    ),
                ],
                "forbidden_work": [
                    "Do not implement Auth",
                    "Do not connect SnapTrade",
                    "Do not enable broker execution",
                    "Do not enable live trading",
                    "Do not redesign unrelated stacks",
                ],
                "qualification_gate": (
                    "All stack-specific gates pass, whole-backend "
                    "tests remain clean, imports and cycles remain zero, "
                    "and database state remains unchanged unless a "
                    "separately authorized migration is required"
                ),
            }
        )

        batch_number += 1

    total_gates = sum(
        item[
            "total_gate_count"
        ]
        for item in analyses
    )

    completed_gates = sum(
        item[
            "completed_gate_count"
        ]
        for item in analyses
    )

    remaining_gates = sum(
        item[
            "remaining_gate_count"
        ]
        for item in analyses
    )

    completion_ratio = round(
        (
            completed_gates
            / total_gates
        )
        * 100.0,
        1,
    )

    total_effort_points = sum(
        item[
            "estimated_remaining_effort_points"
        ]
        for item in analyses
    )

    manifest = source_manifest()

    evidence = {
        "status": "completed",
        "generated_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "batch4_baseline": {
            "score": EXPECTED_BATCH4_SCORE,
            "grade": EXPECTED_BATCH4_GRADE,
        },
        "target_stacks": list(
            TARGET_STACKS
        ),
        "stack_analyses": analyses,
        "source_manifest": manifest,
        "source_modified": False,
        "database_modified": False,
    }

    EVIDENCE_JSON.write_text(
        json.dumps(
            evidence,
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
        "stage": "IQC-005",
        "stage_name": (
            "Remaining Active-Stack Flow "
            "Qualification and Completion Map"
        ),
        "status": "completed",
        "verified_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "batch4_baseline_verified": True,
        "authoritative_flow_score": (
            EXPECTED_BATCH4_SCORE
        ),
        "authoritative_flow_grade": (
            EXPECTED_BATCH4_GRADE
        ),
        "target_stack_count": len(
            TARGET_STACKS
        ),
        "stack_results": analyses,
        "completion_summary": {
            "total_gate_count": total_gates,
            "completed_gate_count": (
                completed_gates
            ),
            "remaining_gate_count": (
                remaining_gates
            ),
            "completion_ratio": (
                completion_ratio
            ),
            "estimated_remaining_effort_points": (
                total_effort_points
            ),
            "critical_stack_count": len(
                critical_stacks
            ),
            "high_priority_stack_count": len(
                high_priority_stacks
            ),
            "evidence_only_stack_count": len(
                evidence_only_stacks
            ),
            "qualified_stack_count": len(
                qualified_stacks
            ),
        },
        "ranked_remediation_batches": (
            remediation_batches
        ),
        "readiness": {
            "internal_development": (
                "QUALIFIED"
            ),
            "controlled_local_flow_testing": (
                "QUALIFIED"
            ),
            "controlled_early_users": (
                "NOT_QUALIFIED"
            ),
            "public_production_deployment": (
                "NOT_QUALIFIED"
            ),
            "snaptrade_read_only_sandbox": (
                "NOT_AUTHORIZED"
            ),
            "snaptrade_paper_execution": (
                "NOT_AUTHORIZED"
            ),
            "broker_execution": (
                "NOT_APPROVED"
            ),
            "live_trading": (
                "NOT_APPROVED"
            ),
        },
        "repository": {
            "active_internal_unresolved": 0,
            "tooling_or_relative_unresolved": 0,
            "syntax_errors": 0,
            "active_cycle_components": 0,
            "self_cycles": 0,
        },
        "database": {
            "connected": True,
            "revision": database[
                "revision"
            ],
            "modified": False,
        },
        "source_modified": False,
        "database_modified": False,
        "auth_implemented": False,
        "snaptrade_connected": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
        "next_step": (
            (
                "IQC Stage 5 Remediation Batch 1 — "
                + remediation_batches[0][
                    "title"
                ]
            )
            if remediation_batches
            else (
                "IQC Stage 6 — Cerberus Foundation "
                "Readiness and Architecture Qualification"
            )
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

    freeze = {
        "status": "frozen",
        "stage": "IQC-005",
        "frozen_at": datetime.now(
            UTC
        ).isoformat(),
        "authoritative_flow_score": (
            EXPECTED_BATCH4_SCORE
        ),
        "authoritative_flow_grade": (
            EXPECTED_BATCH4_GRADE
        ),
        "target_stack_count": len(
            TARGET_STACKS
        ),
        "remaining_gate_count": (
            remaining_gates
        ),
        "completion_ratio": (
            completion_ratio
        ),
        "report_sha256": sha256_file(
            REPORT_JSON
        ),
        "evidence_sha256": sha256_file(
            EVIDENCE_JSON
        ),
        "source_manifest_sha256": (
            manifest[
                "manifest_sha256"
            ]
        ),
        "database_revision": database[
            "revision"
        ],
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
        "=" * 100,
        "NEUROVEST INTEGRATED QUALIFICATION CAMPAIGN",
        (
            "IQC STAGE 5 — REMAINING ACTIVE-STACK "
            "FLOW QUALIFICATION AND COMPLETION MAP"
        ),
        "=" * 100,
        "",
        "STATUS",
        "COMPLETE AND VERIFIED",
        "",
        "MODE",
        "READ ONLY",
        "",
        "AUTHORITATIVE BASELINE",
        (
            "Flow score:                       "
            f"{EXPECTED_BATCH4_SCORE:.2f} / 100"
        ),
        (
            "Flow grade:                       "
            f"{EXPECTED_BATCH4_GRADE}"
        ),
        "Batch 4 freeze verified:           YES",
        "",
        "COMPLETION SUMMARY",
        (
            "Target stacks:                    "
            f"{len(TARGET_STACKS)}"
        ),
        (
            "Total qualification gates:        "
            f"{total_gates}"
        ),
        (
            "Completed qualification gates:    "
            f"{completed_gates}"
        ),
        (
            "Remaining qualification gates:    "
            f"{remaining_gates}"
        ),
        (
            "Completion ratio:                 "
            f"{completion_ratio:.1f}%"
        ),
        (
            "Estimated effort points:          "
            f"{total_effort_points}"
        ),
        (
            "Critical stacks:                  "
            f"{len(critical_stacks)}"
        ),
        (
            "High-priority stacks:             "
            f"{len(high_priority_stacks)}"
        ),
        (
            "Evidence-only stacks:             "
            f"{len(evidence_only_stacks)}"
        ),
        (
            "Fully qualified target stacks:    "
            f"{len(qualified_stacks)}"
        ),
        "",
        "STACK COMPLETION MAP",
    ]

    for item in sorted(
        analyses,
        key=lambda value: (
            value[
                "completion_ratio"
            ],
            value[
                "batch4_score"
            ],
        ),
    ):
        lines.extend(
            [
                (
                    f"- {item['stack']}"
                ),
                (
                    "  Batch 4 grade:                "
                    f"{item['batch4_score']:.2f} "
                    f"{item['batch4_grade']}"
                ),
                (
                    "  Disposition:                  "
                    f"{item['disposition']}"
                ),
                (
                    "  Completion ratio:             "
                    f"{item['completion_ratio']:.1f}%"
                ),
                (
                    "  Remaining gates:              "
                    f"{item['remaining_gate_count']}"
                ),
                (
                    "  Critical / High / Medium:     "
                    f"{item['critical_missing_count']} / "
                    f"{item['high_missing_count']} / "
                    f"{item['medium_missing_count']}"
                ),
                (
                    "  Estimated effort points:      "
                    f"{item['estimated_remaining_effort_points']}"
                ),
                (
                    "  Attributed tests:             "
                    f"{item['attributed_test_count']}"
                ),
                (
                    "  Failure / Integration tests:  "
                    f"{item['failure_test_count']} / "
                    f"{item['integration_test_count']}"
                ),
            ]
        )

    lines.extend(
        [
            "",
            "RANKED REMEDIATION BATCHES",
        ]
    )

    if not remediation_batches:
        lines.append(
            "- None"
        )

    for batch in remediation_batches:
        lines.extend(
            [
                (
                    f"{batch['priority']}. "
                    f"{batch['title']}"
                ),
                (
                    "   Current grade:       "
                    f"{batch['batch4_score']:.2f} "
                    f"{batch['batch4_grade']}"
                ),
                (
                    "   Completion ratio:    "
                    f"{batch['completion_ratio']:.1f}%"
                ),
                (
                    "   Remaining gates:     "
                    f"{batch['remaining_gate_count']}"
                ),
                (
                    "   Effort points:       "
                    f"{batch['estimated_effort_points']}"
                ),
                (
                    "   Scope:               "
                    + ", ".join(
                        batch[
                            "scope_categories"
                        ]
                    )
                ),
            ]
        )

    lines.extend(
        [
            "",
            "READINESS",
            "- Internal development: QUALIFIED",
            "- Controlled local flow testing: QUALIFIED",
            "- Controlled early users: NOT QUALIFIED",
            "- Public production deployment: NOT QUALIFIED",
            "- SnapTrade read-only sandbox: NOT AUTHORIZED",
            "- SnapTrade paper execution: NOT AUTHORIZED",
            "- Broker execution: NOT APPROVED",
            "- Live trading: NOT APPROVED",
            "",
            "REPOSITORY",
            "- Active unresolved imports: 0",
            "- Tooling or relative unresolved imports: 0",
            "- Syntax errors: 0",
            "- Active dependency cycles: 0",
            "- Self cycles: 0",
            "",
            "DATABASE",
            (
                "- Migration revision: "
                f"{database['revision']}"
            ),
            "- Database modified: NO",
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
            report[
                "next_step"
            ],
            "",
            "=" * 100,
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

    print("Completion map:")
    print(REPORT_JSON)
    print()

    print("Detailed evidence:")
    print(EVIDENCE_JSON)
    print()

    print("Freeze manifest:")
    print(FREEZE_JSON)
    print()

    print("Source manifest:")
    print(SOURCE_MANIFEST)


if __name__ == "__main__":
    main()
