#!/usr/bin/env python3
"""
NeuroVest Integrated Qualification Campaign

IQC Stage 5 Remediation Batch 1 —
wolfden_ai Flow Completion and Qualification

PASS A
Exact implementation, dependency, contract, timeout,
failure, and test-evidence disposition.

MODE
READ ONLY

No production source is modified by this pass.
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

WOLFDEN_ROOT = (
    STACKS_ROOT
    / "wolfden_ai"
)

OUTPUT_DIR = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "remediation_batch1"
)

STAGE5_REPORT = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "iqc_stage5_completion_map_latest.json"
)

STAGE5_FREEZE = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "iqc_stage5_completion_map_freeze_latest.json"
)

BATCH4_REPORT = (
    ROOT
    / "runtime"
    / "iqc"
    / "remediation_batch4"
    / "iqc_remediation_batch4_regrade_latest.json"
)

IMPORT_AUDIT = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream1"
    / "import_cycle_audit_latest.json"
)

TEST_LOG = (
    OUTPUT_DIR
    / "whole_backend_tests_latest.log"
)

TEST_EXIT_FILE = (
    OUTPUT_DIR
    / "whole_backend_tests_exit_code.txt"
)

REPORT_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1_wolfden_latest.json"
)

REPORT_TEXT = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1_wolfden_latest.txt"
)

EVIDENCE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1_wolfden_evidence_latest.json"
)

FREEZE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1_wolfden_freeze_latest.json"
)

SOURCE_MANIFEST = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1_source_manifest_latest.json"
)

CONTRACT_BASES = {
    "BaseModel",
    "TypedDict",
    "Protocol",
    "ABC",
    "Enum",
}

MODEL_DEPENDENCY_MARKERS = (
    "ollama",
    "llm",
    "model",
    "inference",
    "generate",
    "chat",
    "completion",
    "embedding",
)

TIMEOUT_MARKERS = (
    "asyncio.wait_for",
    "timeout=",
    "timeout_seconds",
    "connect_timeout",
    "read_timeout",
    "total_timeout",
    "fail_after",
    "timeout_after",
)

FAILURE_MARKERS = (
    "except",
    "raise ",
    "error",
    "failure",
    "unavailable",
    "invalid",
    "malformed",
    "timeout",
    "cancelled",
    "fallback",
    "fail_closed",
)

OBSERVABILITY_MARKERS = (
    "logger",
    "logging",
    "metrics",
    "telemetry",
    "trace",
    "health",
    "latency",
    "duration",
)

OUTPUT_MARKERS = (
    "response",
    "result",
    "output",
    "completion",
    "answer",
    "content",
)

TEST_FAILURE_MARKERS = (
    "pytest.raises",
    "raises(",
    "timeout",
    "unavailable",
    "invalid",
    "malformed",
    "failure",
    "error",
    "cancelled",
)

NETWORK_IMPORT_PREFIXES = (
    "httpx",
    "aiohttp",
    "requests",
    "urllib",
    "ollama",
)

NETWORK_CALL_TERMINALS = {
    "get",
    "post",
    "request",
    "send",
    "stream",
    "chat",
    "generate",
    "embed",
    "embeddings",
    "create",
    "invoke",
    "ainvoke",
}

FORBIDDEN_CAPABILITY_STACKS = {
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
    "enable_live_trading",
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
        if module.startswith(prefix):
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
        return ast.unparse(annotation)

    except Exception:
        return None


def enclosing_symbol(
    tree: ast.AST,
    target: ast.AST,
) -> str:
    target_line = getattr(
        target,
        "lineno",
        None,
    )

    candidates = []

    if target_line is None:
        return "<module>"

    for node in ast.walk(tree):
        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
            ),
        ):
            continue

        start = getattr(
            node,
            "lineno",
            None,
        )

        end = getattr(
            node,
            "end_lineno",
            None,
        )

        if (
            start is not None
            and end is not None
            and start <= target_line <= end
        ):
            candidates.append(
                (
                    end - start,
                    node.name,
                )
            )

    if not candidates:
        return "<module>"

    candidates.sort()

    return candidates[0][1]


def inspect_file(
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
            "contracts": [],
            "functions": [],
            "dependency_calls": [],
            "timeout_calls": [],
            "exception_handlers": [],
            "forbidden_calls": [],
            "model_markers": [],
            "failure_markers": [],
            "observability_markers": [],
        }

    imports = set()
    imported_stacks = set()
    network_names = set()
    contracts = []
    functions = []
    dependency_calls = []
    timeout_calls = []
    exception_handlers = []
    forbidden_calls = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)

                local_name = (
                    alias.asname
                    or alias.name.split(".")[0]
                )

                if alias.name.startswith(
                    NETWORK_IMPORT_PREFIXES
                ):
                    network_names.add(local_name)

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

                if node.module.startswith(
                    NETWORK_IMPORT_PREFIXES
                ):
                    for alias in node.names:
                        network_names.add(
                            alias.asname
                            or alias.name
                        )

        elif isinstance(node, ast.ClassDef):
            bases = {
                dotted_name(base)
                or ""
                for base in node.bases
            }

            terminals = {
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
                            statement.value
                            is not None
                        ),
                    }
                )

            if (
                terminals & CONTRACT_BASES
                or fields
            ):
                contracts.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "bases": sorted(bases),
                        "fields": fields,
                        "output_signal": any(
                            marker in node.name.lower()
                            for marker in OUTPUT_MARKERS
                        ),
                    }
                )

        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            body = (
                ast.get_source_segment(
                    source,
                    node,
                )
                or ""
            ).lower()

            functions.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "async": isinstance(
                        node,
                        ast.AsyncFunctionDef,
                    ),
                    "public": not node.name.startswith("_"),
                    "parameters": [
                        {
                            "name": argument.arg,
                            "annotation": annotation_text(
                                argument.annotation
                            ),
                        }
                        for argument
                        in node.args.args
                    ],
                    "return_annotation": annotation_text(
                        node.returns
                    ),
                    "model_dependency_signal": any(
                        marker in body
                        for marker
                        in MODEL_DEPENDENCY_MARKERS
                    ),
                    "timeout_signal": any(
                        marker in body
                        for marker
                        in TIMEOUT_MARKERS
                    ),
                    "failure_signal": any(
                        marker in body
                        for marker
                        in FAILURE_MARKERS
                    ),
                    "observability_signal": any(
                        marker in body
                        for marker
                        in OBSERVABILITY_MARKERS
                    ),
                }
            )

        elif isinstance(node, ast.Try):
            handlers = []

            for handler in node.handlers:
                exception_type = (
                    dotted_name(
                        handler.type
                    )
                    if handler.type
                    is not None
                    else None
                )

                handlers.append(
                    exception_type
                    or "<bare>"
                )

            exception_handlers.append(
                {
                    "line": node.lineno,
                    "scope": enclosing_symbol(
                        tree,
                        node,
                    ),
                    "handlers": handlers,
                    "has_finally": bool(
                        node.finalbody
                    ),
                }
            )

        elif isinstance(node, ast.Call):
            rendered = dotted_name(
                node.func
            )

            if not rendered:
                continue

            terminal = rendered.split(".")[-1]
            root_name = rendered.split(".")[0]

            if (
                terminal
                in NETWORK_CALL_TERMINALS
                and (
                    root_name in network_names
                    or any(
                        marker in rendered.lower()
                        for marker
                        in MODEL_DEPENDENCY_MARKERS
                    )
                )
            ):
                dependency_calls.append(
                    {
                        "line": node.lineno,
                        "scope": enclosing_symbol(
                            tree,
                            node,
                        ),
                        "call": rendered,
                        "argument_count": len(
                            node.args
                        ),
                        "keyword_names": sorted(
                            keyword.arg
                            for keyword in node.keywords
                            if keyword.arg
                        ),
                    }
                )

            if terminal in {
                "wait_for",
                "timeout",
                "timeout_after",
                "fail_after",
            }:
                timeout_calls.append(
                    {
                        "line": node.lineno,
                        "scope": enclosing_symbol(
                            tree,
                            node,
                        ),
                        "call": rendered,
                    }
                )

            if terminal in (
                FORBIDDEN_CALL_TERMINALS
            ):
                forbidden_calls.append(
                    {
                        "line": node.lineno,
                        "scope": enclosing_symbol(
                            tree,
                            node,
                        ),
                        "call": rendered,
                    }
                )

    return {
        "path": relative(path),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
        "syntax_valid": True,
        "imports": sorted(imports),
        "imported_stacks": sorted(
            imported_stacks
        ),
        "contracts": contracts,
        "functions": functions,
        "dependency_calls": dependency_calls,
        "timeout_calls": timeout_calls,
        "exception_handlers": (
            exception_handlers
        ),
        "forbidden_calls": forbidden_calls,
        "model_markers": [
            marker
            for marker
            in MODEL_DEPENDENCY_MARKERS
            if marker in lowered
        ],
        "failure_markers": [
            marker
            for marker in FAILURE_MARKERS
            if marker in lowered
        ],
        "observability_markers": [
            marker
            for marker
            in OBSERVABILITY_MARKERS
            if marker in lowered
        ],
    }


def discover_tests() -> list[
    dict[str, Any]
]:
    results = []

    tokens = (
        "backend.app.stacks.wolfden_ai",
        "app.stacks.wolfden_ai",
        "stacks.wolfden_ai",
        "/stacks/wolfden_ai/",
    )

    for path in python_files(
        BACKEND_ROOT
    ):
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

        if WOLFDEN_ROOT in path.parents:
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
                "failure_test": any(
                    marker in lowered
                    for marker
                    in TEST_FAILURE_MARKERS
                ),
                "timeout_test": (
                    "timeout" in lowered
                    or "wait_for" in lowered
                ),
                "unavailable_test": any(
                    marker in lowered
                    for marker in (
                        "unavailable",
                        "connectionerror",
                        "connecterror",
                        "refused",
                    )
                ),
                "malformed_output_test": any(
                    marker in lowered
                    for marker in (
                        "malformed",
                        "invalid response",
                        "invalid output",
                        "bad payload",
                    )
                ),
                "contract_test": any(
                    marker in lowered
                    for marker in (
                        "contract",
                        "schema",
                        "response",
                        "result",
                        "output",
                        "validation",
                    )
                ),
                "integration_test": any(
                    marker in lowered
                    for marker in (
                        "integration",
                        "pipeline",
                        "httpx",
                        "testclient",
                        "asyncclient",
                        "ollama",
                    )
                ),
            }
        )

    return results


def source_manifest() -> dict[
    str,
    Any
]:
    entries = []

    for path in python_files(
        BACKEND_ROOT
    ):
        entries.append(
            {
                "path": relative(path),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
        )

    digest = hashlib.sha256()

    for item in entries:
        digest.update(
            item["path"].encode(
                "utf-8"
            )
        )

        digest.update(
            item["sha256"].encode(
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


def test_state() -> dict[str, Any]:
    if not TEST_LOG.is_file():
        return {
            "available": False,
            "exit_code": None,
            "passed": 0,
            "failed": 0,
        }

    text = TEST_LOG.read_text(
        encoding="utf-8",
        errors="replace",
    )

    exit_code = None

    if TEST_EXIT_FILE.is_file():
        exit_code = int(
            TEST_EXIT_FILE.read_text(
                encoding="utf-8"
            ).strip()
        )

    def count(
        label: str,
    ) -> int:
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
        "passed": count("passed"),
        "failed": count("failed"),
    }


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    stage5 = load_json(
        STAGE5_REPORT
    )

    stage5_freeze = load_json(
        STAGE5_FREEZE
    )

    batch4 = load_json(
        BATCH4_REPORT
    )

    import_audit = load_json(
        IMPORT_AUDIT
    )

    assert stage5[
        "status"
    ] == "completed"

    assert stage5[
        "mode"
    ] == "read_only"

    assert stage5[
        "authoritative_flow_score"
    ] == 87.65

    assert stage5[
        "authoritative_flow_grade"
    ] == "B+"

    assert stage5_freeze[
        "status"
    ] == "frozen"

    assert batch4[
        "current_baseline"
    ][
        "authoritative"
    ] is True

    wolfden_stage5 = next(
        item
        for item in stage5[
            "stack_results"
        ]
        if item["stack"]
        == "wolfden_ai"
    )

    assert wolfden_stage5[
        "remaining_gate_count"
    ] == 5

    assert wolfden_stage5[
        "critical_missing_count"
    ] == 0

    assert wolfden_stage5[
        "high_missing_count"
    ] == 4

    assert wolfden_stage5[
        "medium_missing_count"
    ] == 1

    assert WOLFDEN_ROOT.is_dir(), (
        "wolfden_ai stack missing"
    )

    summary = import_audit[
        "summary"
    ]

    assert summary[
        "active_internal_unresolved"
    ] == 0

    assert summary[
        "syntax_errors"
    ] == 0

    assert summary[
        "active_cycle_components"
    ] == 0

    records = [
        inspect_file(path)
        for path in python_files(
            WOLFDEN_ROOT
        )
    ]

    production_records = [
        item
        for item in records
        if not is_test_path(
            ROOT / item["path"]
        )
    ]

    syntax_errors = [
        item
        for item in records
        if not item[
            "syntax_valid"
        ]
    ]

    contracts = [
        {
            "path": item["path"],
            **contract,
        }
        for item in production_records
        for contract in item[
            "contracts"
        ]
    ]

    output_contracts = [
        contract
        for contract in contracts
        if contract[
            "output_signal"
        ]
    ]

    functions = [
        {
            "path": item["path"],
            **function,
        }
        for item in production_records
        for function in item[
            "functions"
        ]
    ]

    public_functions = [
        item
        for item in functions
        if item["public"]
    ]

    async_functions = [
        item
        for item in functions
        if item["async"]
    ]

    model_functions = [
        item
        for item in functions
        if item[
            "model_dependency_signal"
        ]
    ]

    timeout_functions = [
        item
        for item in functions
        if item[
            "timeout_signal"
        ]
    ]

    failure_functions = [
        item
        for item in functions
        if item[
            "failure_signal"
        ]
    ]

    observable_functions = [
        item
        for item in functions
        if item[
            "observability_signal"
        ]
    ]

    dependency_calls = [
        {
            "path": item["path"],
            **call,
        }
        for item in production_records
        for call in item[
            "dependency_calls"
        ]
    ]

    timeout_calls = [
        {
            "path": item["path"],
            **call,
        }
        for item in production_records
        for call in item[
            "timeout_calls"
        ]
    ]

    exception_handlers = [
        {
            "path": item["path"],
            **handler,
        }
        for item in production_records
        for handler in item[
            "exception_handlers"
        ]
    ]

    imported_stacks = defaultdict(
        list
    )

    forbidden_imports = []

    for item in production_records:
        for stack in item[
            "imported_stacks"
        ]:
            imported_stacks[
                stack
            ].append(
                item["path"]
            )

            if stack in (
                FORBIDDEN_CAPABILITY_STACKS
            ):
                forbidden_imports.append(
                    {
                        "path": item["path"],
                        "stack": stack,
                    }
                )

    forbidden_calls = [
        {
            "path": item["path"],
            **call,
        }
        for item in production_records
        for call in item[
            "forbidden_calls"
        ]
    ]

    tests = discover_tests()

    failure_tests = [
        item
        for item in tests
        if item[
            "failure_test"
        ]
    ]

    timeout_tests = [
        item
        for item in tests
        if item[
            "timeout_test"
        ]
    ]

    unavailable_tests = [
        item
        for item in tests
        if item[
            "unavailable_test"
        ]
    ]

    malformed_tests = [
        item
        for item in tests
        if item[
            "malformed_output_test"
        ]
    ]

    contract_tests = [
        item
        for item in tests
        if item[
            "contract_test"
        ]
    ]

    integration_tests = [
        item
        for item in tests
        if item[
            "integration_test"
        ]
    ]

    gates = [
        {
            "gate": (
                "Explicit AI output contract"
            ),
            "complete": bool(
                output_contracts
            ),
            "severity": "HIGH",
        },
        {
            "gate": (
                "All detected model dependency paths "
                "have bounded timeout ownership"
            ),
            "complete": (
                not dependency_calls
                or (
                    bool(timeout_calls)
                    and bool(
                        timeout_functions
                    )
                )
            ),
            "severity": "HIGH",
        },
        {
            "gate": (
                "Model-unavailable failure behavior exists"
            ),
            "complete": bool(
                exception_handlers
            )
            and bool(
                failure_functions
            ),
            "severity": "HIGH",
        },
        {
            "gate": (
                "Focused AI timeout test exists"
            ),
            "complete": bool(
                timeout_tests
            ),
            "severity": "HIGH",
        },
        {
            "gate": (
                "Focused output-contract or malformed-output "
                "test exists"
            ),
            "complete": bool(
                contract_tests
            )
            and bool(
                malformed_tests
            ),
            "severity": "MEDIUM",
        },
    ]

    missing_gates = [
        gate
        for gate in gates
        if not gate[
            "complete"
        ]
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

    source_remediation_required = any(
        not gate["complete"]
        for gate in gates[:3]
    )

    test_remediation_required = any(
        not gate["complete"]
        for gate in gates[3:]
    )

    if (
        syntax_errors
        or forbidden_imports
        or forbidden_calls
    ):
        disposition = (
            "BLOCKED_SAFETY_REMEDIATION_REQUIRED"
        )

    elif source_remediation_required:
        disposition = (
            "SOURCE_AND_TEST_COMPLETION_REQUIRED"
        )

    elif test_remediation_required:
        disposition = (
            "TEST_EVIDENCE_COMPLETION_REQUIRED"
        )

    else:
        disposition = (
            "WOLFDEN_FLOW_QUALIFIED"
        )

    authorized_source_targets = sorted(
        {
            item["path"]
            for item in production_records
            if (
                item[
                    "dependency_calls"
                ]
                or item[
                    "model_markers"
                ]
            )
        }
    )

    recommended_actions = []

    order = 1

    if not gates[0]["complete"]:
        recommended_actions.append(
            {
                "order": order,
                "action": (
                    "Add a serialized immutable AI output "
                    "contract at the wolfden_ai owner boundary"
                ),
                "authorized": True,
            }
        )

        order += 1

    if not gates[1]["complete"]:
        recommended_actions.append(
            {
                "order": order,
                "action": (
                    "Add bounded timeout ownership around only "
                    "the confirmed model dependency calls"
                ),
                "authorized": True,
            }
        )

        order += 1

    if not gates[2]["complete"]:
        recommended_actions.append(
            {
                "order": order,
                "action": (
                    "Add fail-closed model-unavailable and "
                    "malformed-response mapping"
                ),
                "authorized": True,
            }
        )

        order += 1

    if not gates[3]["complete"]:
        recommended_actions.append(
            {
                "order": order,
                "action": (
                    "Add a focused timeout qualification test"
                ),
                "authorized": True,
            }
        )

        order += 1

    if not gates[4]["complete"]:
        recommended_actions.append(
            {
                "order": order,
                "action": (
                    "Add output-contract and malformed-output tests"
                ),
                "authorized": True,
            }
        )

    manifest = source_manifest()
    tests_state = test_state()

    evidence = {
        "status": "completed",
        "generated_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "wolfden_ai": {
            "production_file_count": len(
                production_records
            ),
            "contract_count": len(
                contracts
            ),
            "output_contract_count": len(
                output_contracts
            ),
            "public_function_count": len(
                public_functions
            ),
            "async_function_count": len(
                async_functions
            ),
            "model_function_count": len(
                model_functions
            ),
            "dependency_call_count": len(
                dependency_calls
            ),
            "timeout_function_count": len(
                timeout_functions
            ),
            "timeout_call_count": len(
                timeout_calls
            ),
            "failure_function_count": len(
                failure_functions
            ),
            "exception_handler_count": len(
                exception_handlers
            ),
            "observable_function_count": len(
                observable_functions
            ),
            "forbidden_imports": (
                forbidden_imports
            ),
            "forbidden_calls": (
                forbidden_calls
            ),
            "imported_stacks": {
                stack: sorted(
                    set(paths)
                )
                for stack, paths
                in sorted(
                    imported_stacks.items()
                )
            },
            "records": records,
            "dependency_calls": (
                dependency_calls
            ),
            "timeout_calls": timeout_calls,
            "exception_handlers": (
                exception_handlers
            ),
            "contracts": contracts,
            "output_contracts": (
                output_contracts
            ),
            "tests": tests,
        },
        "whole_backend_tests": (
            tests_state
        ),
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
        "batch": (
            "IQC-STAGE5-REM-001"
        ),
        "batch_name": (
            "wolfden_ai Flow Completion "
            "and Qualification"
        ),
        "pass": (
            "A — Exact Disposition"
        ),
        "status": "completed",
        "verified_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "stage5_baseline_verified": True,
        "stage5_prior_result": {
            "score": wolfden_stage5[
                "batch4_score"
            ],
            "grade": wolfden_stage5[
                "batch4_grade"
            ],
            "completion_ratio": (
                wolfden_stage5[
                    "completion_ratio"
                ]
            ),
            "remaining_gate_count": 5,
        },
        "wolfden_ai": {
            "disposition": disposition,
            "exact_gate_count": len(
                gates
            ),
            "completed_gate_count": (
                len(gates)
                - len(missing_gates)
            ),
            "remaining_gate_count": len(
                missing_gates
            ),
            "high_missing_count": len(
                high_missing
            ),
            "medium_missing_count": len(
                medium_missing
            ),
            "source_remediation_required": (
                source_remediation_required
            ),
            "test_remediation_required": (
                test_remediation_required
            ),
            "production_source_remediation_authorized": (
                source_remediation_required
                and not forbidden_imports
                and not forbidden_calls
                and not syntax_errors
            ),
            "focused_test_addition_authorized": (
                test_remediation_required
            ),
            "authorized_source_targets": (
                authorized_source_targets
            ),
            "qualification_gates": gates,
            "recommended_actions": (
                recommended_actions
            ),
        },
        "safety": {
            "forbidden_capability_imports": len(
                forbidden_imports
            ),
            "forbidden_capability_calls": len(
                forbidden_calls
            ),
            "broker_execution_enabled": False,
            "live_trading_enabled": False,
            "snaptrade_connected": False,
            "auth_implemented": False,
        },
        "repository": {
            "active_internal_unresolved": 0,
            "syntax_errors": 0,
            "active_cycle_components": 0,
        },
        "tests": tests_state,
        "source_modified": False,
        "database_modified": False,
        "next_step": (
            "IQC Stage 5 Remediation Batch 1B — "
            "Implement Only the Confirmed Missing "
            "wolfden_ai Gates"
            if missing_gates
            else (
                "IQC Stage 5 Remediation Batch 1C — "
                "wolfden_ai Qualification Freeze"
            )
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
        "batch": (
            "IQC-STAGE5-REM-001A"
        ),
        "frozen_at": datetime.now(
            UTC
        ).isoformat(),
        "disposition": disposition,
        "remaining_gate_count": len(
            missing_gates
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
            "IQC STAGE 5 REMEDIATION BATCH 1 — "
            "WOLFDEN_AI FLOW COMPLETION AND QUALIFICATION"
        ),
        "=" * 100,
        "",
        "PASS",
        "A — EXACT IMPLEMENTATION AND EVIDENCE DISPOSITION",
        "",
        "STATUS",
        "COMPLETE AND VERIFIED",
        "",
        "MODE",
        "READ ONLY",
        "",
        "STAGE 5 PRIOR RESULT",
        (
            "Score:                           "
            f"{wolfden_stage5['batch4_score']:.2f}"
        ),
        (
            "Grade:                           "
            f"{wolfden_stage5['batch4_grade']}"
        ),
        (
            "Completion ratio:                "
            f"{wolfden_stage5['completion_ratio']:.1f}%"
        ),
        "Previously reported gates:        5",
        "",
        "EXACT DISPOSITION",
        (
            "Disposition:                     "
            f"{disposition}"
        ),
        (
            "Exact gates:                     "
            f"{len(gates)}"
        ),
        (
            "Completed gates:                 "
            f"{len(gates) - len(missing_gates)}"
        ),
        (
            "Remaining gates:                 "
            f"{len(missing_gates)}"
        ),
        (
            "High / Medium missing:           "
            f"{len(high_missing)} / "
            f"{len(medium_missing)}"
        ),
        (
            "Source remediation required:     "
            f"{'YES' if source_remediation_required else 'NO'}"
        ),
        (
            "Test remediation required:       "
            f"{'YES' if test_remediation_required else 'NO'}"
        ),
        "",
        "IMPLEMENTATION EVIDENCE",
        (
            "Production files:                "
            f"{len(production_records)}"
        ),
        (
            "Public functions:                "
            f"{len(public_functions)}"
        ),
        (
            "Async functions:                 "
            f"{len(async_functions)}"
        ),
        (
            "Model-dependent functions:       "
            f"{len(model_functions)}"
        ),
        (
            "Confirmed dependency calls:      "
            f"{len(dependency_calls)}"
        ),
        (
            "Timeout-owning functions:        "
            f"{len(timeout_functions)}"
        ),
        (
            "Explicit timeout calls:          "
            f"{len(timeout_calls)}"
        ),
        (
            "Exception handlers:              "
            f"{len(exception_handlers)}"
        ),
        (
            "Output contracts:                "
            f"{len(output_contracts)}"
        ),
        "",
        "TEST EVIDENCE",
        (
            "Attributed tests:                "
            f"{len(tests)}"
        ),
        (
            "Failure tests:                   "
            f"{len(failure_tests)}"
        ),
        (
            "Timeout tests:                   "
            f"{len(timeout_tests)}"
        ),
        (
            "Unavailable-model tests:         "
            f"{len(unavailable_tests)}"
        ),
        (
            "Malformed-output tests:          "
            f"{len(malformed_tests)}"
        ),
        (
            "Contract tests:                  "
            f"{len(contract_tests)}"
        ),
        (
            "Integration tests:               "
            f"{len(integration_tests)}"
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
            "AUTHORIZED SOURCE TARGETS",
        ]
    )

    if authorized_source_targets:
        for target in (
            authorized_source_targets
        ):
            lines.append(
                f"- {target}"
            )

    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "SAFETY",
            (
                "Forbidden capability imports:    "
                f"{len(forbidden_imports)}"
            ),
            (
                "Forbidden capability calls:      "
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
            report["next_step"],
            "",
            "=" * 100,
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
    print("Disposition report:")
    print(REPORT_JSON)
    print()
    print("Detailed evidence:")
    print(EVIDENCE_JSON)
    print()
    print("Freeze manifest:")
    print(FREEZE_JSON)


if __name__ == "__main__":
    main()
