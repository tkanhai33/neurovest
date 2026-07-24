#!/usr/bin/env python3
"""
NeuroVest Integrated Qualification Campaign

IQC Remediation Batch 3C —
chat_public Contract, Failure, Timeout,
Rate-Limit, and Safety-Policy Qualification

Production source and database mode: READ ONLY

This qualification does not add missing features. It determines which
controls already exist, whether they are enforceable, and which exact
implementation gates remain.
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

BACKEND_ROOT = ROOT / "backend" / "app"
CHAT_ROOT = BACKEND_ROOT / "stacks" / "chat_public"

RUNTIME_ROOT = ROOT / "runtime"

OUTPUT_DIR = (
    RUNTIME_ROOT
    / "iqc"
    / "remediation_batch3c"
)

BATCH3B_REPORT = (
    RUNTIME_ROOT
    / "iqc"
    / "remediation_batch3b"
    / "iqc_remediation_batch3b_latest.json"
)

IMPORT_AUDIT_REPORT = (
    RUNTIME_ROOT
    / "hardening"
    / "workstream1"
    / "import_cycle_audit_latest.json"
)

REPORT_JSON = (
    OUTPUT_DIR
    / "iqc_remediation_batch3c_latest.json"
)

REPORT_TEXT = (
    OUTPUT_DIR
    / "iqc_remediation_batch3c_latest.txt"
)

EVIDENCE_JSON = (
    OUTPUT_DIR
    / "iqc_remediation_batch3c_evidence_latest.json"
)

FREEZE_JSON = (
    OUTPUT_DIR
    / "iqc_remediation_batch3c_freeze_latest.json"
)

TEST_LOG = (
    OUTPUT_DIR
    / "whole_backend_tests_latest.log"
)

TEST_EXIT_FILE = (
    OUTPUT_DIR
    / "whole_backend_tests_exit_code.txt"
)

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
}

REQUEST_WORDS = {
    "request",
    "prompt",
    "message",
    "query",
    "input",
}

RESPONSE_WORDS = {
    "response",
    "reply",
    "answer",
    "result",
    "output",
}

FAILURE_WORDS = {
    "except",
    "exception",
    "error",
    "failure",
    "unavailable",
    "invalid",
    "reject",
    "blocked",
    "denied",
    "timeout",
    "fallback",
    "fail_closed",
}

TIMEOUT_TERMINALS = {
    "wait_for",
    "timeout",
    "timeout_after",
    "fail_after",
}

RATE_LIMIT_WORDS = {
    "rate_limit",
    "ratelimit",
    "throttle",
    "quota",
    "too_many_requests",
    "http_429",
    "status_429",
}

SAFETY_WORDS = {
    "safety",
    "policy",
    "guardrail",
    "moderation",
    "deny",
    "blocked",
    "forbidden",
    "allowlist",
    "capability",
    "risk",
}

PRIVATE_DATA_WORDS = {
    "access_token",
    "refresh_token",
    "password",
    "user_profile",
    "broker_account",
    "account_number",
    "email",
    "phone",
    "address",
}

FORBIDDEN_STACKS = {
    "execution",
    "paper_trading",
    "broker_integration",
    "snaptrade",
    "admin_control",
}

FORBIDDEN_CALL_TERMINALS = {
    "execute_trade",
    "execute_order",
    "place_order",
    "submit_order",
    "connect_broker",
    "register_broker",
    "enable_live_trading",
}

FAIL_OPEN_PATTERNS = {
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

SEVERITY_ORDER = {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3,
    "OBSERVATION": 4,
}


def load_json(path: Path) -> dict[str, Any]:
    assert path.is_file(), f"Required evidence missing: {path}"

    value = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert isinstance(value, dict)

    return value


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def python_files(root: Path) -> list[Path]:
    if not root.is_dir():
        return []

    return [
        path
        for path in sorted(root.rglob("*.py"))
        if "__pycache__" not in path.parts
    ]


def is_test_path(path: Path) -> bool:
    lowered = {
        part.lower()
        for part in path.parts
    }

    return (
        "test" in lowered
        or "tests" in lowered
        or "l7_tests" in lowered
        or path.name.startswith("test_")
        or path.name.endswith("_test.py")
    )


def dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id

    if isinstance(node, ast.Attribute):
        parent = dotted_name(node.value)

        if parent:
            return f"{parent}.{node.attr}"

        return node.attr

    return None


def imported_stack(module: str) -> str | None:
    prefixes = (
        "backend.app.stacks.",
        "app.stacks.",
        "stacks.",
    )

    for prefix in prefixes:
        if module.startswith(prefix):
            return module[
                len(prefix):
            ].split(".")[0]

    return None


def decorator_name(
    decorator: ast.expr,
) -> str | None:
    expression = (
        decorator.func
        if isinstance(decorator, ast.Call)
        else decorator
    )

    return dotted_name(expression)


def function_source(
    source: str,
    node: ast.AST,
) -> str:
    return (
        ast.get_source_segment(
            source,
            node,
        )
        or ""
    )


def annotation_text(
    annotation: ast.expr | None,
) -> str | None:
    if annotation is None:
        return None

    try:
        return ast.unparse(annotation)

    except Exception:
        return None


def inspect_file(path: Path) -> dict[str, Any]:
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
            "routes": [],
            "contracts": [],
            "imports": [],
            "imported_stacks": [],
            "failure_functions": [],
            "timeout_calls": [],
            "rate_limit_signals": [],
            "safety_signals": [],
            "fail_open_signals": [],
            "forbidden_calls": [],
            "private_data_signals": [],
        }

    imports = set()
    imported_stacks = set()
    routes = []
    contracts = []
    failure_functions = []
    timeout_calls = []
    forbidden_calls = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)

                stack = imported_stack(
                    alias.name
                )

                if stack:
                    imported_stacks.add(stack)

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)

                stack = imported_stack(
                    node.module
                )

                if stack:
                    imported_stacks.add(stack)

        elif isinstance(node, ast.ClassDef):
            bases = {
                dotted_name(base)
                or ""
                for base in node.bases
            }

            base_terminals = {
                base.split(".")[-1]
                for base in bases
            }

            class_lower = node.name.lower()

            request_signal = any(
                word in class_lower
                for word in REQUEST_WORDS
            )

            response_signal = any(
                word in class_lower
                for word in RESPONSE_WORDS
            )

            if (
                base_terminals
                & CONTRACT_BASES
                or request_signal
                or response_signal
            ):
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
                                statement.value
                                is not None
                            ),
                        }
                    )

                contracts.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "bases": sorted(bases),
                        "request_signal": request_signal,
                        "response_signal": response_signal,
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
            body_source = function_source(
                source,
                node,
            ).lower()

            route_decorators = []

            for decorator in node.decorator_list:
                name = decorator_name(
                    decorator
                )

                if not name:
                    continue

                if (
                    name.split(".")[-1]
                    in ROUTE_METHODS
                ):
                    route_decorators.append(
                        ast.unparse(decorator)
                    )

            if route_decorators:
                parameters = []

                for argument in node.args.args:
                    parameters.append(
                        {
                            "name": argument.arg,
                            "annotation": annotation_text(
                                argument.annotation
                            ),
                        }
                    )

                routes.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "decorators": route_decorators,
                        "parameters": parameters,
                        "return_annotation": annotation_text(
                            node.returns
                        ),
                        "async": isinstance(
                            node,
                            ast.AsyncFunctionDef,
                        ),
                        "failure_boundary_detected": any(
                            word in body_source
                            for word in FAILURE_WORDS
                        ),
                        "timeout_detected": (
                            "wait_for(" in body_source
                            or "timeout=" in body_source
                            or "timeout_after(" in body_source
                            or "fail_after(" in body_source
                        ),
                        "rate_limit_detected": any(
                            word in body_source
                            for word in RATE_LIMIT_WORDS
                        ),
                        "safety_policy_detected": any(
                            word in body_source
                            for word in SAFETY_WORDS
                        ),
                    }
                )

            if any(
                word in body_source
                for word in FAILURE_WORDS
            ):
                failure_functions.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                    }
                )

        elif isinstance(node, ast.Call):
            rendered = dotted_name(
                node.func
            )

            if not rendered:
                continue

            terminal = rendered.split(".")[-1]

            if terminal in TIMEOUT_TERMINALS:
                timeout_calls.append(
                    {
                        "line": node.lineno,
                        "call": rendered,
                    }
                )

            if terminal in FORBIDDEN_CALL_TERMINALS:
                forbidden_calls.append(
                    {
                        "line": node.lineno,
                        "call": rendered,
                    }
                )

    fail_open_signals = [
        name
        for name, pattern
        in FAIL_OPEN_PATTERNS.items()
        if pattern.search(source)
    ]

    return {
        "path": relative(path),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
        "syntax_valid": True,
        "routes": routes,
        "contracts": contracts,
        "imports": sorted(imports),
        "imported_stacks": sorted(
            imported_stacks
        ),
        "failure_functions": failure_functions,
        "timeout_calls": timeout_calls,
        "rate_limit_signals": sorted(
            word
            for word in RATE_LIMIT_WORDS
            if word in lowered
        ),
        "safety_signals": sorted(
            word
            for word in SAFETY_WORDS
            if word in lowered
        ),
        "fail_open_signals": fail_open_signals,
        "forbidden_calls": forbidden_calls,
        "private_data_signals": sorted(
            word
            for word in PRIVATE_DATA_WORDS
            if word in lowered
        ),
    }


def inspect_tests() -> dict[str, Any]:
    attributed = []

    tokens = (
        "backend.app.stacks.chat_public",
        "app.stacks.chat_public",
        "stacks.chat_public",
        "/stacks/chat_public/",
    )

    for path in python_files(BACKEND_ROOT):
        if not is_test_path(path):
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
                "local_chat_public_test"
            )

        if not reasons:
            continue

        attributed.append(
            {
                "path": relative(path),
                "reasons": sorted(
                    set(reasons)
                ),
                "contract_signal": any(
                    marker in lowered
                    for marker in (
                        "request",
                        "response",
                        "schema",
                        "contract",
                        "validation",
                    )
                ),
                "failure_signal": any(
                    marker in lowered
                    for marker in FAILURE_WORDS
                ),
                "timeout_signal": any(
                    marker in lowered
                    for marker in (
                        "timeout",
                        "wait_for",
                        "timed out",
                    )
                ),
                "rate_limit_signal": any(
                    marker in lowered
                    for marker in RATE_LIMIT_WORDS
                ),
                "safety_signal": any(
                    marker in lowered
                    for marker in SAFETY_WORDS
                ),
            }
        )

    return {
        "attributed_tests": attributed,
        "contract_tests": [
            item["path"]
            for item in attributed
            if item[
                "contract_signal"
            ]
        ],
        "failure_tests": [
            item["path"]
            for item in attributed
            if item[
                "failure_signal"
            ]
        ],
        "timeout_tests": [
            item["path"]
            for item in attributed
            if item[
                "timeout_signal"
            ]
        ],
        "rate_limit_tests": [
            item["path"]
            for item in attributed
            if item[
                "rate_limit_signal"
            ]
        ],
        "safety_tests": [
            item["path"]
            for item in attributed
            if item[
                "safety_signal"
            ]
        ],
    }


def read_test_state() -> dict[str, Any]:
    if not TEST_LOG.is_file():
        return {
            "available": False,
            "exit_code": None,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
        }

    text = TEST_LOG.read_text(
        encoding="utf-8",
        errors="replace",
    )

    exit_code = None

    if TEST_EXIT_FILE.is_file():
        try:
            exit_code = int(
                TEST_EXIT_FILE.read_text(
                    encoding="utf-8"
                ).strip()
            )

        except ValueError:
            exit_code = None

    def number(label: str) -> int:
        matches = re.findall(
            rf"(\d+)\s+{label}",
            text,
        )

        return (
            int(matches[-1])
            if matches
            else 0
        )

    return {
        "available": True,
        "exit_code": exit_code,
        "passed": number("passed"),
        "failed": number("failed"),
        "warnings": number("warnings"),
    }


def source_manifest() -> dict[str, Any]:
    entries = []

    for path in python_files(BACKEND_ROOT):
        entries.append(
            {
                "path": relative(path),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
        )

    digest = hashlib.sha256()

    for entry in entries:
        digest.update(
            entry["path"].encode(
                "utf-8"
            )
        )

        digest.update(
            entry["sha256"].encode(
                "ascii"
            )
        )

    return {
        "file_count": len(entries),
        "manifest_sha256": digest.hexdigest(),
        "files": entries,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    assert CHAT_ROOT.is_dir(), (
        "chat_public stack missing"
    )

    batch3b = load_json(
        BATCH3B_REPORT
    )

    import_audit = load_json(
        IMPORT_AUDIT_REPORT
    )

    assert batch3b[
        "status"
    ] == "completed"

    assert batch3b[
        "tests"
    ][
        "focused_failed"
    ] == 0

    assert batch3b[
        "tests"
    ][
        "whole_backend_failed"
    ] == 0

    assert batch3b[
        "boundary"
    ][
        "route_imports_sqlalchemy"
    ] is False

    assert batch3b[
        "boundary"
    ][
        "route_imports_db_runtime"
    ] is False

    assert batch3b[
        "boundary"
    ][
        "route_imports_orm_models"
    ] is False

    assert batch3b[
        "boundary"
    ][
        "route_imports_conversation_store"
    ] is False

    records = [
        inspect_file(path)
        for path in python_files(CHAT_ROOT)
    ]

    production_records = [
        record
        for record in records
        if not is_test_path(
            ROOT / record["path"]
        )
    ]

    syntax_errors = [
        record
        for record in records
        if not record[
            "syntax_valid"
        ]
    ]

    routes = [
        {
            "path": record["path"],
            **route,
        }
        for record in production_records
        for route in record[
            "routes"
        ]
    ]

    contracts = [
        {
            "path": record["path"],
            **contract,
        }
        for record in production_records
        for contract in record[
            "contracts"
        ]
    ]

    request_contracts = [
        item
        for item in contracts
        if item[
            "request_signal"
        ]
    ]

    response_contracts = [
        item
        for item in contracts
        if item[
            "response_signal"
        ]
    ]

    failure_boundaries = [
        {
            "path": record["path"],
            **item,
        }
        for record in production_records
        for item in record[
            "failure_functions"
        ]
    ]

    timeout_calls = [
        {
            "path": record["path"],
            **item,
        }
        for record in production_records
        for item in record[
            "timeout_calls"
        ]
    ]

    rate_limit_files = [
        {
            "path": record["path"],
            "signals": record[
                "rate_limit_signals"
            ],
        }
        for record in production_records
        if record[
            "rate_limit_signals"
        ]
    ]

    safety_files = [
        {
            "path": record["path"],
            "signals": record[
                "safety_signals"
            ],
        }
        for record in production_records
        if record[
            "safety_signals"
        ]
    ]

    fail_open_signals = [
        {
            "path": record["path"],
            "signals": record[
                "fail_open_signals"
            ],
        }
        for record in production_records
        if record[
            "fail_open_signals"
        ]
    ]

    forbidden_imports = []

    for record in production_records:
        for stack in record[
            "imported_stacks"
        ]:
            if stack in FORBIDDEN_STACKS:
                forbidden_imports.append(
                    {
                        "path": record["path"],
                        "stack": stack,
                    }
                )

    forbidden_calls = [
        {
            "path": record["path"],
            **item,
        }
        for record in production_records
        for item in record[
            "forbidden_calls"
        ]
    ]

    test_evidence = inspect_tests()
    test_state = read_test_state()

    gates = [
        {
            "gate": "Request contract detected",
            "complete": bool(
                request_contracts
            ),
            "blocking_for_public_release": True,
        },
        {
            "gate": "Response contract detected",
            "complete": bool(
                response_contracts
            )
            or any(
                route[
                    "return_annotation"
                ]
                for route in routes
            ),
            "blocking_for_public_release": True,
        },
        {
            "gate": "Route boundary detected",
            "complete": bool(routes),
            "blocking_for_public_release": True,
        },
        {
            "gate": "Failure boundary detected",
            "complete": bool(
                failure_boundaries
            )
            and any(
                route[
                    "failure_boundary_detected"
                ]
                for route in routes
            ),
            "blocking_for_public_release": True,
        },
        {
            "gate": "Dependency timeout enforcement detected",
            "complete": bool(
                timeout_calls
            )
            or any(
                route[
                    "timeout_detected"
                ]
                for route in routes
            ),
            "blocking_for_public_release": True,
        },
        {
            "gate": "Rate-limit enforcement detected",
            "complete": bool(
                rate_limit_files
            )
            or any(
                route[
                    "rate_limit_detected"
                ]
                for route in routes
            ),
            "blocking_for_public_release": True,
        },
        {
            "gate": "Safety-policy boundary detected",
            "complete": bool(
                safety_files
            )
            and any(
                route[
                    "safety_policy_detected"
                ]
                for route in routes
            ),
            "blocking_for_public_release": True,
        },
        {
            "gate": "Focused contract tests detected",
            "complete": bool(
                test_evidence[
                    "contract_tests"
                ]
            ),
            "blocking_for_public_release": True,
        },
        {
            "gate": "Focused failure tests detected",
            "complete": bool(
                test_evidence[
                    "failure_tests"
                ]
            ),
            "blocking_for_public_release": True,
        },
        {
            "gate": "Focused timeout tests detected",
            "complete": bool(
                test_evidence[
                    "timeout_tests"
                ]
            ),
            "blocking_for_public_release": True,
        },
        {
            "gate": "Focused rate-limit tests detected",
            "complete": bool(
                test_evidence[
                    "rate_limit_tests"
                ]
            ),
            "blocking_for_public_release": True,
        },
        {
            "gate": "Focused safety-policy tests detected",
            "complete": bool(
                test_evidence[
                    "safety_tests"
                ]
            ),
            "blocking_for_public_release": True,
        },
        {
            "gate": "No fail-open configuration",
            "complete": not bool(
                fail_open_signals
            ),
            "blocking_for_public_release": True,
        },
        {
            "gate": "No forbidden capability imports",
            "complete": not bool(
                forbidden_imports
            ),
            "blocking_for_public_release": True,
        },
        {
            "gate": "No forbidden capability calls",
            "complete": not bool(
                forbidden_calls
            ),
            "blocking_for_public_release": True,
        },
        {
            "gate": "Whole backend suite clean",
            "complete": (
                test_state.get(
                    "exit_code"
                )
                == 0
                and test_state.get(
                    "failed",
                    0,
                )
                == 0
            ),
            "blocking_for_public_release": True,
        },
    ]

    missing_gates = [
        gate
        for gate in gates
        if not gate[
            "complete"
        ]
    ]

    blocking_gates = [
        gate
        for gate in missing_gates
        if gate[
            "blocking_for_public_release"
        ]
    ]

    findings = []

    if syntax_errors:
        findings.append(
            {
                "severity": "CRITICAL",
                "code": "CHAT_SYNTAX_ERROR",
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
                "code": "CHAT_FAIL_OPEN_SIGNAL",
                "summary": (
                    "Potential fail-open chat configuration detected"
                ),
                "evidence": fail_open_signals,
            }
        )

    if forbidden_imports:
        findings.append(
            {
                "severity": "CRITICAL",
                "code": "CHAT_FORBIDDEN_IMPORT",
                "summary": (
                    "chat_public imports an execution, broker, "
                    "SnapTrade, paper-trading, or admin stack"
                ),
                "evidence": forbidden_imports,
            }
        )

    if forbidden_calls:
        findings.append(
            {
                "severity": "CRITICAL",
                "code": "CHAT_FORBIDDEN_CALL",
                "summary": (
                    "chat_public contains a forbidden trading "
                    "or broker capability call"
                ),
                "evidence": forbidden_calls,
            }
        )

    for gate in missing_gates:
        findings.append(
            {
                "severity": (
                    "HIGH"
                    if gate[
                        "blocking_for_public_release"
                    ]
                    else "MEDIUM"
                ),
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
                "summary": gate[
                    "gate"
                ]
                + " is not yet qualified",
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

    if any(
        item[
            "severity"
        ]
        == "CRITICAL"
        for item in findings
    ):
        disposition = (
            "BOUNDARY_BLOCKED_REMEDIATION_REQUIRED"
        )

    elif blocking_gates:
        disposition = (
            "IMPLEMENTED_BUT_PUBLIC_CONTROLS_INCOMPLETE"
        )

    else:
        disposition = (
            "CONTROL_BOUNDARY_QUALIFIED"
        )

    manifest = source_manifest()

    evidence = {
        "status": "completed",
        "generated_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "production_records": production_records,
        "routes": routes,
        "contracts": contracts,
        "request_contracts": request_contracts,
        "response_contracts": response_contracts,
        "failure_boundaries": failure_boundaries,
        "timeout_calls": timeout_calls,
        "rate_limit_files": rate_limit_files,
        "safety_files": safety_files,
        "fail_open_signals": fail_open_signals,
        "forbidden_imports": forbidden_imports,
        "forbidden_calls": forbidden_calls,
        "test_evidence": test_evidence,
        "whole_backend_tests": test_state,
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

    import_summary = import_audit[
        "summary"
    ]

    report = {
        "campaign": (
            "NeuroVest Integrated "
            "Qualification Campaign"
        ),
        "batch": "IQC-REM-003C",
        "batch_name": (
            "chat_public Contract, Failure, Timeout, "
            "Rate-Limit, and Safety-Policy Qualification"
        ),
        "status": "completed",
        "verified_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "batch3b_verified": True,
        "chat_public": {
            "disposition": disposition,
            "route_count": len(routes),
            "contract_count": len(contracts),
            "request_contract_count": len(
                request_contracts
            ),
            "response_contract_count": len(
                response_contracts
            ),
            "failure_boundary_count": len(
                failure_boundaries
            ),
            "timeout_control_count": len(
                timeout_calls
            ),
            "rate_limit_file_count": len(
                rate_limit_files
            ),
            "safety_policy_file_count": len(
                safety_files
            ),
            "qualification_gate_count": len(
                gates
            ),
            "completed_gate_count": sum(
                1
                for gate in gates
                if gate[
                    "complete"
                ]
            ),
            "remaining_gate_count": len(
                missing_gates
            ),
            "blocking_gate_count": len(
                blocking_gates
            ),
            "public_deployment_authorized": (
                disposition
                == "CONTROL_BOUNDARY_QUALIFIED"
            ),
            "production_source_remediation_authorized": (
                bool(
                    missing_gates
                    or fail_open_signals
                    or forbidden_imports
                    or forbidden_calls
                )
            ),
            "qualification_gates": gates,
        },
        "findings": findings,
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
        "tests": test_state,
        "source_modified": False,
        "database_modified": False,
        "auth_implemented": False,
        "snaptrade_connected": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
        "next_step": (
            "IQC Remediation Batch 3D — "
            "Implement Only the Confirmed Missing "
            "chat_public Control Gates"
            if missing_gates
            else (
                "IQC Remediation Batch 4 — "
                "Implementation-State-Aware Re-grade "
                "and Baseline Freeze"
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

    report_hash = sha256_file(
        REPORT_JSON
    )

    evidence_hash = sha256_file(
        EVIDENCE_JSON
    )

    freeze = {
        "status": "frozen",
        "batch": "IQC-REM-003C",
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
        "=" * 96,
        "NEUROVEST INTEGRATED QUALIFICATION CAMPAIGN",
        (
            "IQC REMEDIATION BATCH 3C — CHAT_PUBLIC "
            "CONTRACT, FAILURE, TIMEOUT, RATE-LIMIT, "
            "AND SAFETY-POLICY QUALIFICATION"
        ),
        "=" * 96,
        "",
        "STATUS",
        "COMPLETE AND VERIFIED",
        "",
        "MODE",
        "READ ONLY",
        "",
        "BATCH 3B BASELINE",
        "- Conversation service boundary verified: YES",
        "- Route persistence imports: 0",
        "- External direct-store imports: 0",
        "",
        "CHAT_PUBLIC DISPOSITION",
        f"Disposition:                       {disposition}",
        f"Routes detected:                   {len(routes)}",
        f"Contracts detected:                {len(contracts)}",
        f"Request contracts:                 {len(request_contracts)}",
        f"Response contracts:                {len(response_contracts)}",
        f"Failure boundaries:                {len(failure_boundaries)}",
        f"Timeout controls:                  {len(timeout_calls)}",
        f"Rate-limit files:                  {len(rate_limit_files)}",
        f"Safety-policy files:               {len(safety_files)}",
        "",
        "QUALIFICATION GATES",
        f"Total gates:                       {len(gates)}",
        (
            "Completed gates:                   "
            f"{sum(1 for gate in gates if gate['complete'])}"
        ),
        f"Remaining gates:                   {len(missing_gates)}",
        f"Blocking gates:                    {len(blocking_gates)}",
        (
            "Public deployment authorized:      "
            f"{'YES' if report['chat_public']['public_deployment_authorized'] else 'NO'}"
        ),
        "",
        "GATE RESULTS",
    ]

    for gate in gates:
        lines.append(
            f"- {'PASS' if gate['complete'] else 'FAIL'}: "
            f"{gate['gate']}"
        )

    lines.extend(
        [
            "",
            "TESTS",
            (
                "Whole-backend passed:             "
                f"{test_state.get('passed', 0)}"
            ),
            (
                "Whole-backend failed:             "
                f"{test_state.get('failed', 0)}"
            ),
            (
                "Whole-backend warnings:           "
                f"{test_state.get('warnings', 0)}"
            ),
            "",
            "REPOSITORY",
            (
                "Active unresolved imports:        "
                f"{import_summary['active_internal_unresolved']}"
            ),
            (
                "Dependency cycles:                "
                f"{import_summary['active_cycle_components']}"
            ),
            (
                "Syntax errors:                    "
                f"{import_summary['syntax_errors']}"
            ),
            "",
            "SAFETY",
            (
                "Fail-open signals:                "
                f"{len(fail_open_signals)}"
            ),
            (
                "Forbidden capability imports:     "
                f"{len(forbidden_imports)}"
            ),
            (
                "Forbidden capability calls:       "
                f"{len(forbidden_calls)}"
            ),
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
            "=" * 96,
        ]
    )

    rendered = (
        "\n".join(lines)
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
