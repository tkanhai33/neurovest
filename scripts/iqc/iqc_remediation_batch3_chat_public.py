#!/usr/bin/env python3
"""
NeuroVest Integrated Qualification Campaign

IQC Remediation Batch 3 —
chat_public Implementation-State and Boundary Qualification

This batch is read-only.

It does not:
- implement Auth
- add API routes
- add frontend wiring
- add chat features
- connect chat to portfolio or trading
- connect chat to SnapTrade
- modify production source
- modify the database

It determines:
1. What chat_public currently implements.
2. Whether it is placeholder, partial, or operational.
3. Which production modules consume it.
4. Which stacks and capabilities it imports.
5. Whether it can safely operate before Auth.
6. Whether it exposes private, broker, execution, admin, or mutation access.
7. Which gates remain before public deployment.
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

CHAT_ROOT = (
    STACKS_ROOT
    / "chat_public"
)

RUNTIME_ROOT = (
    ROOT
    / "runtime"
)

OUTPUT_DIR = (
    RUNTIME_ROOT
    / "iqc"
    / "remediation_batch3"
)

BATCH1_REPORT = (
    RUNTIME_ROOT
    / "iqc"
    / "remediation_batch1"
    / "iqc_remediation_batch1_latest.json"
)

BATCH2_REPORT = (
    RUNTIME_ROOT
    / "iqc"
    / "remediation_batch2"
    / "iqc_remediation_batch2_auth_roadmap_latest.json"
)

BATCH2_FREEZE = (
    RUNTIME_ROOT
    / "iqc"
    / "remediation_batch2"
    / "iqc_remediation_batch2_roadmap_freeze_latest.json"
)

IMPORT_AUDIT_REPORT = (
    RUNTIME_ROOT
    / "hardening"
    / "workstream1"
    / "import_cycle_audit_latest.json"
)

REPORT_JSON = (
    OUTPUT_DIR
    / "iqc_remediation_batch3_chat_public_latest.json"
)

REPORT_TEXT = (
    OUTPUT_DIR
    / "iqc_remediation_batch3_chat_public_latest.txt"
)

EVIDENCE_JSON = (
    OUTPUT_DIR
    / "iqc_remediation_batch3_chat_public_evidence_latest.json"
)

FREEZE_JSON = (
    OUTPUT_DIR
    / "iqc_remediation_batch3_chat_public_freeze_latest.json"
)

PLACEHOLDER_MARKERS = (
    "todo",
    "not implemented",
    "notimplementederror",
    "placeholder",
    "stub",
    "coming soon",
)

CHAT_IMPLEMENTATION_MARKERS = {
    "request_contract": (
        "chatrequest",
        "chat_request",
        "messageschema",
        "message_schema",
        "request_model",
    ),
    "response_contract": (
        "chatresponse",
        "chat_response",
        "response_model",
    ),
    "service_boundary": (
        "chatservice",
        "chat_service",
        "facade",
        "handler",
        "controller",
    ),
    "llm_adapter": (
        "ollama",
        "llm",
        "model_adapter",
        "inference",
    ),
    "input_validation": (
        "validate",
        "validator",
        "max_length",
        "min_length",
    ),
    "timeout_control": (
        "timeout",
        "wait_for",
        "connect_timeout",
        "read_timeout",
    ),
    "error_boundary": (
        "except",
        "error",
        "unavailable",
        "fail",
    ),
    "rate_limit_boundary": (
        "rate_limit",
        "throttle",
        "quota",
    ),
    "streaming_support": (
        "stream",
        "streaming",
        "websocket",
        "sse",
    ),
    "observability": (
        "metrics",
        "telemetry",
        "logging",
        "trace",
        "health",
    ),
    "safety_policy": (
        "safety",
        "policy",
        "guardrail",
        "deny",
        "blocked",
    ),
}

SENSITIVE_STACKS = {
    "portfolio",
    "execution",
    "paper_trading",
    "broker_integration",
    "snaptrade",
    "admin_control",
    "db_runtime",
    "db_model",
    "journal_ledger",
    "risk",
    "identity_auth",
    "auth_identity",
}

STRICTLY_FORBIDDEN_PUBLIC_CHAT_STACKS = {
    "execution",
    "paper_trading",
    "broker_integration",
    "snaptrade",
    "admin_control",
}

DIRECT_PERSISTENCE_MODULES = {
    "backend.app.stacks.db_runtime.database",
    "app.stacks.db_runtime.database",
    "stacks.db_runtime.database",
    "sqlalchemy",
    "sqlalchemy.ext.asyncio",
}

MUTATION_CALL_NAMES = {
    "append",
    "add",
    "commit",
    "delete",
    "execute_trade",
    "execute_order",
    "flush",
    "insert",
    "merge",
    "place_order",
    "purge",
    "replace",
    "rollback",
    "save",
    "submit_order",
    "truncate",
    "update",
    "upsert",
}

PRIVATE_DATA_MARKERS = (
    "account_id",
    "broker_account",
    "portfolio",
    "position",
    "holding",
    "balance",
    "order_history",
    "trade_history",
    "user_profile",
    "email",
    "phone",
    "address",
    "access_token",
    "refresh_token",
)

AUTH_MARKERS = (
    "depends(",
    "current_user",
    "require_auth",
    "require_user",
    "authenticated_user",
    "verify_token",
    "oauth2",
    "authorization",
)

ROUTE_PATTERN = re.compile(
    r"@\w+\.(get|post|put|patch|delete|route|websocket)\s*\(",
    re.IGNORECASE,
)

FAIL_OPEN_PATTERNS = {
    "anonymous_privileged_default": re.compile(
        r"\ballow_(?:trading|admin|broker|portfolio)\s*[:=]\s*True\b",
        re.IGNORECASE,
    ),
    "safety_disabled": re.compile(
        r"\bsafety_enabled\s*[:=]\s*False\b",
        re.IGNORECASE,
    ),
    "policy_bypass": re.compile(
        r"\bskip_(?:safety|policy|authorization)\s*[:=]\s*True\b",
        re.IGNORECASE,
    ),
    "execution_enabled": re.compile(
        r"\bexecution_enabled\s*[:=]\s*True\b",
        re.IGNORECASE,
    ),
    "live_trading_enabled": re.compile(
        r"\blive_trading_enabled\s*[:=]\s*True\b",
        re.IGNORECASE,
    ),
}

UNSAFE_DYNAMIC_EXECUTION = {
    "eval",
    "exec",
    "compile",
    "__import__",
}

SEVERITY_ORDER = {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3,
    "OBSERVATION": 4,
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
            return (
                f"{parent}.{node.attr}"
            )

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
        if not module.startswith(
            prefix
        ):
            continue

        remainder = module[
            len(prefix):
        ]

        return remainder.split(
            "."
        )[0]

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
            "size_bytes": path.stat().st_size,
            "syntax_valid": False,
            "syntax_error": str(exc),
            "imports": [],
            "imported_stacks": [],
            "classes": [],
            "functions": [],
            "async_functions": [],
            "public_functions": [],
            "route_functions": [],
            "mutation_calls": [],
            "dynamic_execution_calls": [],
            "placeholder_markers": [],
            "fail_open_signals": [],
            "private_data_markers": [],
            "auth_enforcement_detected": False,
        }

    imports = set()
    imported_stacks = set()
    classes = set()
    functions = set()
    async_functions = set()
    public_functions = set()
    route_functions = []
    mutation_calls = set()
    dynamic_execution_calls = set()

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
            classes.add(
                node.name
            )

        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            functions.add(
                node.name
            )

            if isinstance(
                node,
                ast.AsyncFunctionDef,
            ):
                async_functions.add(
                    node.name
                )

            if not node.name.startswith(
                "_"
            ):
                public_functions.add(
                    node.name
                )

            decorators = [
                ast.unparse(
                    decorator
                )
                for decorator in node.decorator_list
            ]

            if any(
                ROUTE_PATTERN.search(
                    decorator
                )
                for decorator in decorators
            ):
                rendered = ast.get_source_segment(
                    source,
                    node,
                ) or ""

                route_functions.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "decorators": decorators,
                        "auth_enforcement_detected": any(
                            marker in rendered.lower()
                            for marker in AUTH_MARKERS
                        ),
                        "private_data_markers": [
                            marker
                            for marker in PRIVATE_DATA_MARKERS
                            if marker in rendered.lower()
                        ],
                    }
                )

        elif isinstance(
            node,
            ast.Call,
        ):
            name = dotted_name(
                node.func
            )

            if not name:
                continue

            terminal = name.split(
                "."
            )[-1]

            if terminal in MUTATION_CALL_NAMES:
                mutation_calls.add(
                    name
                )

            if terminal in UNSAFE_DYNAMIC_EXECUTION:
                dynamic_execution_calls.add(
                    name
                )

    placeholders = [
        marker
        for marker in PLACEHOLDER_MARKERS
        if marker in lowered
    ]

    fail_open_signals = [
        name
        for name, pattern
        in FAIL_OPEN_PATTERNS.items()
        if pattern.search(
            source
        )
    ]

    private_data_markers = [
        marker
        for marker in PRIVATE_DATA_MARKERS
        if marker in lowered
    ]

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
        "classes": sorted(
            classes
        ),
        "functions": sorted(
            functions
        ),
        "async_functions": sorted(
            async_functions
        ),
        "public_functions": sorted(
            public_functions
        ),
        "route_functions": route_functions,
        "mutation_calls": sorted(
            mutation_calls
        ),
        "dynamic_execution_calls": sorted(
            dynamic_execution_calls
        ),
        "placeholder_markers": placeholders,
        "fail_open_signals": fail_open_signals,
        "private_data_markers": (
            private_data_markers
        ),
        "auth_enforcement_detected": any(
            marker in lowered
            for marker in AUTH_MARKERS
        ),
    }


def implementation_markers(
    text: str,
) -> dict[str, Any]:
    result = {}

    for capability, markers in (
        CHAT_IMPLEMENTATION_MARKERS.items()
    ):
        matched = [
            marker
            for marker in markers
            if marker in text
        ]

        result[
            capability
        ] = {
            "detected": bool(
                matched
            ),
            "evidence": matched,
        }

    return result


def implementation_coverage(
    markers: dict[str, Any],
) -> float:
    if not markers:
        return 0.0

    detected = sum(
        1
        for value in markers.values()
        if value[
            "detected"
        ]
    )

    return round(
        100.0
        * detected
        / len(
            markers
        ),
        1,
    )


def production_consumers() -> list[
    dict[str, Any]
]:
    consumers = []

    tokens = (
        "stacks.chat_public",
        "stacks/chat_public",
        "chat_public.",
    )

    for path in python_files(
        BACKEND_ROOT
    ):
        if CHAT_ROOT in path.parents:
            continue

        source = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        lowered = source.lower()

        if not any(
            token in lowered
            for token in tokens
        ):
            continue

        consumers.append(
            {
                "path": relative(path),
                "is_test": is_test_path(
                    path
                ),
            }
        )

    return consumers


def attributed_tests() -> list[
    dict[str, Any]
]:
    evidence = []

    tokens = (
        "backend.app.stacks.chat_public",
        "app.stacks.chat_public",
        "stacks.chat_public",
        "/stacks/chat_public/",
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

        if CHAT_ROOT in path.parents:
            reasons.append(
                "local_stack_test"
            )

        if not reasons:
            continue

        evidence.append(
            {
                "path": relative(path),
                "reasons": sorted(
                    set(
                        reasons
                    )
                ),
                "failure_signal": any(
                    marker in lowered
                    for marker in (
                        "raises",
                        "error",
                        "failure",
                        "invalid",
                        "blocked",
                        "denied",
                        "timeout",
                        "unavailable",
                    )
                ),
            }
        )

    return evidence


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
                "size_bytes": (
                    path.stat().st_size
                ),
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

    assert CHAT_ROOT.is_dir(), (
        "chat_public stack is missing"
    )

    batch1 = load_json(
        BATCH1_REPORT
    )

    batch2 = load_json(
        BATCH2_REPORT
    )

    batch2_freeze = load_json(
        BATCH2_FREEZE
    )

    import_audit = load_json(
        IMPORT_AUDIT_REPORT
    )

    assert batch1[
        "status"
    ] == "completed"

    assert batch1[
        "whole_backend_tests"
    ][
        "passed"
    ] >= 143

    assert batch1[
        "whole_backend_tests"
    ][
        "failed"
    ] == 0

    assert batch1[
        "source_integrity"
    ][
        "production_source_modified"
    ] is False

    assert batch2[
        "status"
    ] == "completed"

    assert batch2[
        "mode"
    ] == "read_only"

    assert batch2[
        "auth_identity"
    ][
        "production_authentication_available"
    ] is False

    assert batch2[
        "snaptrade"
    ][
        "safe_connection_authorized"
    ] is False

    assert batch2_freeze[
        "status"
    ] == "frozen"

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

    chat_files = python_files(
        CHAT_ROOT
    )

    records = [
        inspect_source(
            path
        )
        for path in chat_files
    ]

    production_records = [
        record
        for record in records
        if not is_test_path(
            ROOT / record[
                "path"
            ]
        )
    ]

    local_test_records = [
        record
        for record in records
        if is_test_path(
            ROOT / record[
                "path"
            ]
        )
    ]

    source_text = "\n".join(
        path.read_text(
            encoding="utf-8",
            errors="replace",
        ).lower()
        for path in chat_files
    )

    implementation = (
        implementation_markers(
            source_text
        )
    )

    coverage = (
        implementation_coverage(
            implementation
        )
    )

    consumers = production_consumers()

    production_consumer_records = [
        item
        for item in consumers
        if not item[
            "is_test"
        ]
    ]

    test_evidence = attributed_tests()

    failure_tests = [
        item
        for item in test_evidence
        if item[
            "failure_signal"
        ]
    ]

    syntax_errors = [
        record
        for record in records
        if not record[
            "syntax_valid"
        ]
    ]

    placeholder_files = [
        {
            "path": record[
                "path"
            ],
            "markers": record[
                "placeholder_markers"
            ],
        }
        for record in production_records
        if record[
            "placeholder_markers"
        ]
    ]

    imported_sensitive_stacks = defaultdict(
        list
    )

    direct_persistence_imports = []
    forbidden_stack_imports = []
    mutation_calls = []
    dynamic_execution_calls = []
    fail_open_signals = []
    private_data_signals = []
    route_records = []

    for record in production_records:
        for stack in record[
            "imported_stacks"
        ]:
            if stack in SENSITIVE_STACKS:
                imported_sensitive_stacks[
                    stack
                ].append(
                    record[
                        "path"
                    ]
                )

            if (
                stack
                in STRICTLY_FORBIDDEN_PUBLIC_CHAT_STACKS
            ):
                forbidden_stack_imports.append(
                    {
                        "path": record[
                            "path"
                        ],
                        "stack": stack,
                    }
                )

        matched_persistence = sorted(
            set(
                record[
                    "imports"
                ]
            )
            & DIRECT_PERSISTENCE_MODULES
        )

        if matched_persistence:
            direct_persistence_imports.append(
                {
                    "path": record[
                        "path"
                    ],
                    "modules": (
                        matched_persistence
                    ),
                }
            )

        if record[
            "mutation_calls"
        ]:
            mutation_calls.append(
                {
                    "path": record[
                        "path"
                    ],
                    "calls": record[
                        "mutation_calls"
                    ],
                }
            )

        if record[
            "dynamic_execution_calls"
        ]:
            dynamic_execution_calls.append(
                {
                    "path": record[
                        "path"
                    ],
                    "calls": record[
                        "dynamic_execution_calls"
                    ],
                }
            )

        if record[
            "fail_open_signals"
        ]:
            fail_open_signals.append(
                {
                    "path": record[
                        "path"
                    ],
                    "signals": record[
                        "fail_open_signals"
                    ],
                }
            )

        if record[
            "private_data_markers"
        ]:
            private_data_signals.append(
                {
                    "path": record[
                        "path"
                    ],
                    "markers": record[
                        "private_data_markers"
                    ],
                    "auth_enforcement_detected": (
                        record[
                            "auth_enforcement_detected"
                        ]
                    ),
                }
            )

        for route in record[
            "route_functions"
        ]:
            route_records.append(
                {
                    "path": record[
                        "path"
                    ],
                    **route,
                }
            )

    unauthenticated_private_routes = [
        route
        for route in route_records
        if (
            route[
                "private_data_markers"
            ]
            and not route[
                "auth_enforcement_detected"
            ]
        )
    ]

    operational_evidence = (
        bool(
            production_records
        )
        and any(
            value[
                "detected"
            ]
            for value in implementation.values()
        )
    )

    mostly_placeholder = (
        bool(
            placeholder_files
        )
        and coverage < 50.0
    )

    sensitive_capability_exposure = (
        bool(
            forbidden_stack_imports
        )
        or bool(
            direct_persistence_imports
        )
        or bool(
            mutation_calls
        )
        or bool(
            unauthenticated_private_routes
        )
    )

    safe_pre_auth_boundary = (
        not syntax_errors
        and not fail_open_signals
        and not forbidden_stack_imports
        and not direct_persistence_imports
        and not mutation_calls
        and not dynamic_execution_calls
        and not unauthenticated_private_routes
    )

    if mostly_placeholder:
        implementation_state = (
            "PARTIAL_PLACEHOLDER"
        )

    elif operational_evidence:
        implementation_state = (
            "IMPLEMENTED_UNQUALIFIED"
        )

    else:
        implementation_state = (
            "DORMANT_OR_EMPTY"
        )

    if sensitive_capability_exposure:
        disposition = (
            "AUTH_REQUIRED_AND_BOUNDARY_REMEDIATION_REQUIRED"
        )

    elif safe_pre_auth_boundary:
        if test_evidence:
            disposition = (
                "SAFE_PRE_AUTH_PUBLIC_BOUNDARY"
            )

        else:
            disposition = (
                "SAFE_PRE_AUTH_BUT_TEST_EVIDENCE_MISSING"
            )

    else:
        disposition = (
            "PARTIAL_REQUIRES_BOUNDARY_REVIEW"
        )

    findings = []

    if syntax_errors:
        findings.append(
            {
                "severity": "CRITICAL",
                "code": (
                    "CHAT_PUBLIC_SYNTAX_ERROR"
                ),
                "summary": (
                    "Syntax-invalid chat_public source detected"
                ),
                "evidence": syntax_errors,
            }
        )

    if fail_open_signals:
        findings.append(
            {
                "severity": "CRITICAL",
                "code": (
                    "CHAT_PUBLIC_FAIL_OPEN_SIGNAL"
                ),
                "summary": (
                    "Potential fail-open public-chat capability detected"
                ),
                "evidence": fail_open_signals,
            }
        )

    if forbidden_stack_imports:
        findings.append(
            {
                "severity": "CRITICAL",
                "code": (
                    "PUBLIC_CHAT_FORBIDDEN_STACK_IMPORT"
                ),
                "summary": (
                    "chat_public imports broker, execution, "
                    "paper-trading, SnapTrade, or admin capability"
                ),
                "evidence": (
                    forbidden_stack_imports
                ),
            }
        )

    if direct_persistence_imports:
        findings.append(
            {
                "severity": "HIGH",
                "code": (
                    "PUBLIC_CHAT_DIRECT_PERSISTENCE_ACCESS"
                ),
                "summary": (
                    "chat_public imports direct database "
                    "or SQLAlchemy dependencies"
                ),
                "evidence": (
                    direct_persistence_imports
                ),
            }
        )

    if mutation_calls:
        findings.append(
            {
                "severity": "HIGH",
                "code": (
                    "PUBLIC_CHAT_MUTATION_CAPABILITY"
                ),
                "summary": (
                    "Potential mutation calls were detected "
                    "inside chat_public"
                ),
                "evidence": mutation_calls,
            }
        )

    if unauthenticated_private_routes:
        findings.append(
            {
                "severity": "HIGH",
                "code": (
                    "UNAUTHENTICATED_PRIVATE_CHAT_ROUTE"
                ),
                "summary": (
                    "A chat route references private-user "
                    "or financial data without detectable Auth"
                ),
                "evidence": (
                    unauthenticated_private_routes
                ),
            }
        )

    if dynamic_execution_calls:
        findings.append(
            {
                "severity": "HIGH",
                "code": (
                    "PUBLIC_CHAT_DYNAMIC_CODE_EXECUTION"
                ),
                "summary": (
                    "Dynamic code execution was detected "
                    "inside chat_public"
                ),
                "evidence": (
                    dynamic_execution_calls
                ),
            }
        )

    if not test_evidence:
        findings.append(
            {
                "severity": "HIGH",
                "code": (
                    "NO_CHAT_PUBLIC_TEST_EVIDENCE"
                ),
                "summary": (
                    "No local or centralized tests target chat_public"
                ),
                "evidence": [],
            }
        )

    elif not failure_tests:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": (
                    "NO_CHAT_PUBLIC_FAILURE_TEST"
                ),
                "summary": (
                    "No failure-behavior tests target chat_public"
                ),
                "evidence": [],
            }
        )

    if not implementation[
        "input_validation"
    ][
        "detected"
    ]:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": (
                    "CHAT_INPUT_VALIDATION_NOT_DETECTED"
                ),
                "summary": (
                    "Input validation evidence was not detected"
                ),
                "evidence": [],
            }
        )

    if not implementation[
        "timeout_control"
    ][
        "detected"
    ]:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": (
                    "CHAT_TIMEOUT_CONTROL_NOT_DETECTED"
                ),
                "summary": (
                    "LLM or dependency timeout control "
                    "was not detected"
                ),
                "evidence": [],
            }
        )

    if not implementation[
        "rate_limit_boundary"
    ][
        "detected"
    ]:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": (
                    "CHAT_RATE_LIMIT_NOT_DETECTED"
                ),
                "summary": (
                    "Public-chat rate limiting was not detected"
                ),
                "evidence": [],
            }
        )

    if not implementation[
        "safety_policy"
    ][
        "detected"
    ]:
        findings.append(
            {
                "severity": "HIGH",
                "code": (
                    "CHAT_SAFETY_POLICY_NOT_DETECTED"
                ),
                "summary": (
                    "No explicit public-chat safety or policy "
                    "boundary was detected"
                ),
                "evidence": [],
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

    qualification_gates = [
        {
            "gate": (
                "No execution, broker, SnapTrade, "
                "paper-trading, or admin imports"
            ),
            "complete": (
                not forbidden_stack_imports
            ),
        },
        {
            "gate": (
                "No direct database or ORM ownership"
            ),
            "complete": (
                not direct_persistence_imports
            ),
        },
        {
            "gate": (
                "No mutation capability"
            ),
            "complete": (
                not mutation_calls
            ),
        },
        {
            "gate": (
                "No dynamic code execution"
            ),
            "complete": (
                not dynamic_execution_calls
            ),
        },
        {
            "gate": (
                "No fail-open capability signal"
            ),
            "complete": (
                not fail_open_signals
            ),
        },
        {
            "gate": (
                "No unauthenticated private-data route"
            ),
            "complete": (
                not unauthenticated_private_routes
            ),
        },
        {
            "gate": (
                "Request contract present"
            ),
            "complete": implementation[
                "request_contract"
            ][
                "detected"
            ],
        },
        {
            "gate": (
                "Response contract present"
            ),
            "complete": implementation[
                "response_contract"
            ][
                "detected"
            ],
        },
        {
            "gate": (
                "Input validation present"
            ),
            "complete": implementation[
                "input_validation"
            ][
                "detected"
            ],
        },
        {
            "gate": (
                "Dependency timeout control present"
            ),
            "complete": implementation[
                "timeout_control"
            ][
                "detected"
            ],
        },
        {
            "gate": (
                "Failure boundary present"
            ),
            "complete": implementation[
                "error_boundary"
            ][
                "detected"
            ],
        },
        {
            "gate": (
                "Safety-policy boundary present"
            ),
            "complete": implementation[
                "safety_policy"
            ][
                "detected"
            ],
        },
        {
            "gate": (
                "Public rate limiting present"
            ),
            "complete": implementation[
                "rate_limit_boundary"
            ][
                "detected"
            ],
        },
        {
            "gate": (
                "Focused contract tests present"
            ),
            "complete": bool(
                test_evidence
            ),
        },
        {
            "gate": (
                "Focused failure tests present"
            ),
            "complete": bool(
                failure_tests
            ),
        },
    ]

    remaining_gates = sum(
        1
        for gate in qualification_gates
        if not gate[
            "complete"
        ]
    )

    manifest = source_manifest()

    evidence = {
        "status": "completed",
        "generated_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "chat_public": {
            "production_file_count": len(
                production_records
            ),
            "local_test_file_count": len(
                local_test_records
            ),
            "implementation_evidence_coverage": (
                coverage
            ),
            "implementation_markers": (
                implementation
            ),
            "records": records,
            "placeholder_files": (
                placeholder_files
            ),
            "syntax_errors": syntax_errors,
            "fail_open_signals": (
                fail_open_signals
            ),
            "forbidden_stack_imports": (
                forbidden_stack_imports
            ),
            "sensitive_stack_imports": {
                stack: sorted(
                    set(paths)
                )
                for stack, paths
                in sorted(
                    imported_sensitive_stacks.items()
                )
            },
            "direct_persistence_imports": (
                direct_persistence_imports
            ),
            "mutation_calls": mutation_calls,
            "dynamic_execution_calls": (
                dynamic_execution_calls
            ),
            "private_data_signals": (
                private_data_signals
            ),
            "routes": route_records,
            "unauthenticated_private_routes": (
                unauthenticated_private_routes
            ),
            "consumers": consumers,
            "production_consumer_count": len(
                production_consumer_records
            ),
            "attributed_tests": (
                test_evidence
            ),
            "attributed_failure_tests": (
                failure_tests
            ),
        },
        "source_manifest": manifest,
        "source_modified": False,
        "database_modified": False,
    }

    EVIDENCE_JSON.write_text(
        json.dumps(
            evidence,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    report = {
        "campaign": (
            "NeuroVest Integrated "
            "Qualification Campaign"
        ),
        "batch": "IQC-REM-003",
        "batch_name": (
            "chat_public Implementation-State "
            "and Boundary Qualification"
        ),
        "status": "completed",
        "verified_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "batch1_verified": True,
        "batch2_verified": True,
        "flow_baseline": {
            "backend_tests_passed": batch1[
                "whole_backend_tests"
            ][
                "passed"
            ],
            "backend_tests_failed": batch1[
                "whole_backend_tests"
            ][
                "failed"
            ],
            "unresolved_imports": 0,
            "dependency_cycles": 0,
        },
        "auth_state": {
            "production_authentication_available": False,
            "auth_deployment_blocker": batch2[
                "auth_identity"
            ][
                "deployment_blocker"
            ],
        },
        "chat_public": {
            "implementation_state": (
                implementation_state
            ),
            "disposition": disposition,
            "implementation_evidence_coverage": (
                coverage
            ),
            "safe_before_auth": (
                safe_pre_auth_boundary
            ),
            "sensitive_capability_exposure": (
                sensitive_capability_exposure
            ),
            "public_deployment_authorized": False,
            "focused_test_addition_authorized": (
                not bool(
                    test_evidence
                )
                or not bool(
                    failure_tests
                )
            ),
            "production_source_remediation_authorized": (
                sensitive_capability_exposure
                or bool(
                    fail_open_signals
                )
                or bool(
                    syntax_errors
                )
            ),
            "remaining_gate_count": (
                remaining_gates
            ),
            "qualification_gates": (
                qualification_gates
            ),
        },
        "findings": findings,
        "recommended_next_actions": [
            {
                "order": 1,
                "action": (
                    "Preserve the current chat_public "
                    "implementation boundary"
                ),
                "required": True,
            },
            {
                "order": 2,
                "action": (
                    "Add focused request, response, validation, "
                    "timeout, and dependency-failure tests"
                ),
                "required": (
                    not test_evidence
                    or not failure_tests
                ),
            },
            {
                "order": 3,
                "action": (
                    "Add or qualify explicit public-chat "
                    "safety and policy enforcement"
                ),
                "required": (
                    not implementation[
                        "safety_policy"
                    ][
                        "detected"
                    ]
                ),
            },
            {
                "order": 4,
                "action": (
                    "Add or qualify public-chat rate limiting"
                ),
                "required": (
                    not implementation[
                        "rate_limit_boundary"
                    ][
                        "detected"
                    ]
                ),
            },
            {
                "order": 5,
                "action": (
                    "Keep portfolio, execution, broker, admin, "
                    "SnapTrade, and private-user data inaccessible "
                    "until Auth is implemented"
                ),
                "required": True,
            },
            {
                "order": 6,
                "action": (
                    "Re-grade active implementation-state-aware stacks"
                ),
                "required": True,
            },
        ],
        "source_modified": False,
        "database_modified": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
        "next_step": (
            "IQC Remediation Batch 4 — "
            "Implementation-State-Aware Re-grade "
            "and Baseline Freeze"
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

    evidence_hash = sha256_file(
        EVIDENCE_JSON
    )

    freeze = {
        "status": "frozen",
        "batch": "IQC-REM-003",
        "frozen_at": datetime.now(
            UTC
        ).isoformat(),
        "report_sha256": report_hash,
        "evidence_sha256": evidence_hash,
        "source_manifest_sha256": (
            manifest[
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
            "IQC REMEDIATION BATCH 3 — "
            "CHAT_PUBLIC IMPLEMENTATION-STATE "
            "AND BOUNDARY QUALIFICATION"
        ),
        "=" * 92,
        "",
        "STATUS",
        "COMPLETE AND VERIFIED",
        "",
        "MODE",
        "READ ONLY",
        "",
        "FLOW BASELINE",
        (
            "Backend tests passed:            "
            f"{batch1['whole_backend_tests']['passed']}"
        ),
        "Backend tests failed:            0",
        "Unresolved imports:              0",
        "Dependency cycles:               0",
        "",
        "CHAT_PUBLIC DISPOSITION",
        (
            "Implementation state:           "
            f"{implementation_state}"
        ),
        (
            "Disposition:                    "
            f"{disposition}"
        ),
        (
            "Implementation evidence found:  "
            f"{coverage:.1f}%"
        ),
        (
            "Safe before Auth:               "
            f"{'YES' if safe_pre_auth_boundary else 'NO'}"
        ),
        (
            "Sensitive capability exposure:  "
            f"{'YES' if sensitive_capability_exposure else 'NO'}"
        ),
        (
            "Production consumers:           "
            f"{len(production_consumer_records)}"
        ),
        (
            "Attributed tests:               "
            f"{len(test_evidence)}"
        ),
        (
            "Failure tests:                  "
            f"{len(failure_tests)}"
        ),
        (
            "Remaining qualification gates:  "
            f"{remaining_gates}"
        ),
        "Public deployment authorized:     NO",
        "",
        "BOUNDARY RESULTS",
        (
            "Forbidden stack imports:        "
            f"{len(forbidden_stack_imports)}"
        ),
        (
            "Direct persistence imports:     "
            f"{len(direct_persistence_imports)}"
        ),
        (
            "Mutation call records:          "
            f"{len(mutation_calls)}"
        ),
        (
            "Dynamic execution records:      "
            f"{len(dynamic_execution_calls)}"
        ),
        (
            "Fail-open signals:              "
            f"{len(fail_open_signals)}"
        ),
        (
            "Unauthenticated private routes: "
            f"{len(unauthenticated_private_routes)}"
        ),
        "",
        "FINDINGS",
    ]

    if not findings:
        lines.append(
            "- None"
        )

    for index, finding in enumerate(
        findings,
        start=1,
    ):
        lines.append(
            f"{index}. [{finding['severity']}] "
            f"{finding['summary']}"
        )

    lines.extend(
        [
            "",
            "SAFETY",
            "- Production Auth available: NO",
            "- Public deployment authorized: NO",
            "- SnapTrade access authorized: NO",
            "- Broker execution enabled: NO",
            "- Live trading enabled: NO",
            "- Source modified: NO",
            "- Database modified: NO",
            "",
            "NEXT",
            (
                "IQC Remediation Batch 4 — "
                "Implementation-State-Aware Re-grade "
                "and Baseline Freeze"
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

    print("Qualification report:")
    print(REPORT_JSON)
    print()

    print("Evidence report:")
    print(EVIDENCE_JSON)
    print()

    print("Freeze manifest:")
    print(FREEZE_JSON)


if __name__ == "__main__":
    main()
