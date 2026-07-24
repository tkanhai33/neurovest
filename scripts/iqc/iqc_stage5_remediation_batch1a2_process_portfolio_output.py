#!/usr/bin/env python3
"""
NeuroVest Integrated Qualification Campaign

IQC Stage 5 Remediation Batch 1A2 —
process_portfolio_output Ownership, Side-Effect,
and Boundary Disposition

MODE
READ ONLY

Purpose:
- Locate the authoritative process_portfolio_output definition.
- Inspect direct and transitive calls.
- Determine whether it performs database, ledger, portfolio,
  paper-order, execution, file, network, or global-state mutation.
- Trace all production and test consumers.
- Determine its input and output contract.
- Classify the function and recommend the smallest safe ownership fix.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from collections import defaultdict, deque
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(".").resolve()

BACKEND_ROOT = (
    ROOT
    / "backend"
    / "app"
)

TARGET_FILE = (
    BACKEND_ROOT
    / "stacks"
    / "execution"
    / "paper_broker.py"
)

TARGET_FUNCTION = (
    "process_portfolio_output"
)

OUTPUT_DIR = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "remediation_batch1a2"
)

PRIOR_DISPOSITION = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "remediation_batch1"
    / "iqc_stage5_remediation_batch1_forbidden_import_disposition_latest.json"
)

BATCH1A_REPORT = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "remediation_batch1"
    / "iqc_stage5_remediation_batch1_wolfden_latest.json"
)

IMPORT_AUDIT_REPORT = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream1"
    / "import_cycle_audit_latest.json"
)

REPORT_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1a2_latest.json"
)

REPORT_TEXT = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1a2_latest.txt"
)

EVIDENCE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1a2_evidence_latest.json"
)

FREEZE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1a2_freeze_latest.json"
)

SOURCE_MANIFEST = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1a2_source_manifest_latest.json"
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
    "publish",
    "rollback",
    "save",
    "send_order",
    "set",
    "submit",
    "submit_order",
    "truncate",
    "update",
    "upsert",
    "write",
    "write_text",
    "write_bytes",
}

DATABASE_MARKERS = {
    "sqlalchemy",
    "session",
    "database",
    "db_runtime",
    "engine",
    "repository",
    "orm",
}

LEDGER_MARKERS = {
    "ledger",
    "journal",
    "audit",
    "append_event",
    "decision_event",
}

PORTFOLIO_MUTATION_MARKERS = {
    "position",
    "holding",
    "portfolio",
    "cash_balance",
    "cost_basis",
    "shares",
}

PAPER_EXECUTION_MARKERS = {
    "paper_broker",
    "paper_order",
    "paper_trade",
    "fill_order",
    "execute_order",
    "place_order",
    "submit_order",
    "trade_fill",
}

NETWORK_MARKERS = {
    "httpx",
    "aiohttp",
    "requests",
    "urllib",
    "socket",
    "websocket",
}

FILE_MUTATION_TERMINALS = {
    "open",
    "write",
    "write_text",
    "write_bytes",
    "unlink",
    "rename",
    "replace",
    "mkdir",
    "touch",
}

GLOBAL_MUTATION_NODES = (
    ast.Global,
    ast.Nonlocal,
)

RETURN_CONTAINER_TYPES = {
    "dict",
    "list",
    "tuple",
    "set",
}

READ_ONLY_TERMINALS = {
    "get",
    "read",
    "lookup",
    "find",
    "list",
    "snapshot",
    "status",
    "preview",
    "describe",
    "validate",
    "evaluate",
    "check",
    "calculate",
    "compute",
    "transform",
    "serialize",
    "model_dump",
}

FORBIDDEN_LIVE_TERMINALS = {
    "connect_broker",
    "connect_snaptrade",
    "enable_live_trading",
    "execute_live_order",
}

TEST_MARKERS = (
    "pytest",
    "unittest",
    "test_",
    "raises",
    "assert ",
)


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
            return (
                f"{parent}.{node.attr}"
            )

        return node.attr

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


def source_line(
    source: str,
    line_number: int,
) -> str:
    lines = source.splitlines()

    if (
        line_number < 1
        or line_number > len(lines)
    ):
        return ""

    return lines[
        line_number - 1
    ].strip()


def enclosing_symbol(
    tree: ast.AST,
    target: ast.AST,
) -> str:
    line = getattr(
        target,
        "lineno",
        None,
    )

    if line is None:
        return "<module>"

    matches = []

    for node in ast.walk(
        tree
    ):
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
            and start <= line <= end
        ):
            matches.append(
                (
                    end - start,
                    node.name,
                )
            )

    if not matches:
        return "<module>"

    matches.sort()

    return matches[0][1]


def extract_function(
    path: Path,
    function_name: str,
) -> tuple[
    str,
    ast.AST,
    ast.FunctionDef | ast.AsyncFunctionDef,
]:
    source = path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source,
        filename=str(path),
    )

    matches = [
        node
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
        and node.name == function_name
    ]

    assert len(matches) == 1, (
        f"Expected exactly one {function_name} definition; "
        f"found {len(matches)}"
    )

    return (
        source,
        tree,
        matches[0],
    )


def imports_for_file(
    tree: ast.AST,
) -> list[dict[str, Any]]:
    imports = []

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                imports.append(
                    {
                        "line": node.lineno,
                        "module": alias.name,
                        "name": None,
                        "alias": alias.asname,
                    }
                )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            module = node.module or ""

            for alias in node.names:
                imports.append(
                    {
                        "line": node.lineno,
                        "module": module,
                        "name": alias.name,
                        "alias": alias.asname,
                    }
                )

    return imports


def inspect_function(
    path: Path,
    function_name: str,
) -> dict[str, Any]:
    source, tree, node = extract_function(
        path,
        function_name,
    )

    rendered = (
        ast.get_source_segment(
            source,
            node,
        )
        or ""
    )

    imports = imports_for_file(
        tree
    )

    calls = []
    assignments = []
    returns = []
    global_mutations = []
    attribute_writes = []
    subscript_writes = []
    file_mutations = []
    forbidden_live_calls = []

    for child in ast.walk(
        node
    ):
        if isinstance(
            child,
            ast.Call,
        ):
            name = dotted_name(
                child.func
            )

            if not name:
                continue

            terminal = name.split(
                "."
            )[-1]

            record = {
                "line": child.lineno,
                "scope": enclosing_symbol(
                    tree,
                    child,
                ),
                "call": name,
                "terminal": terminal,
                "argument_count": len(
                    child.args
                ),
                "keyword_names": sorted(
                    keyword.arg
                    for keyword in child.keywords
                    if keyword.arg
                ),
                "source_line": source_line(
                    source,
                    child.lineno,
                ),
            }

            calls.append(
                record
            )

            if terminal in FILE_MUTATION_TERMINALS:
                file_mutations.append(
                    record
                )

            if terminal in FORBIDDEN_LIVE_TERMINALS:
                forbidden_live_calls.append(
                    record
                )

        elif isinstance(
            child,
            (
                ast.Assign,
                ast.AnnAssign,
                ast.AugAssign,
            ),
        ):
            assignments.append(
                {
                    "line": child.lineno,
                    "kind": type(
                        child
                    ).__name__,
                    "source_line": source_line(
                        source,
                        child.lineno,
                    ),
                }
            )

            targets = []

            if isinstance(
                child,
                ast.Assign,
            ):
                targets = child.targets

            elif isinstance(
                child,
                ast.AnnAssign,
            ):
                targets = [
                    child.target
                ]

            elif isinstance(
                child,
                ast.AugAssign,
            ):
                targets = [
                    child.target
                ]

            for target in targets:
                if isinstance(
                    target,
                    ast.Attribute,
                ):
                    attribute_writes.append(
                        {
                            "line": child.lineno,
                            "target": ast.unparse(
                                target
                            ),
                            "source_line": source_line(
                                source,
                                child.lineno,
                            ),
                        }
                    )

                elif isinstance(
                    target,
                    ast.Subscript,
                ):
                    subscript_writes.append(
                        {
                            "line": child.lineno,
                            "target": ast.unparse(
                                target
                            ),
                            "source_line": source_line(
                                source,
                                child.lineno,
                            ),
                        }
                    )

        elif isinstance(
            child,
            ast.Return,
        ):
            returns.append(
                {
                    "line": child.lineno,
                    "expression": (
                        ast.unparse(
                            child.value
                        )
                        if child.value
                        is not None
                        else None
                    ),
                    "expression_type": (
                        type(
                            child.value
                        ).__name__
                        if child.value
                        is not None
                        else "None"
                    ),
                }
            )

        elif isinstance(
            child,
            GLOBAL_MUTATION_NODES,
        ):
            global_mutations.append(
                {
                    "line": child.lineno,
                    "kind": type(
                        child
                    ).__name__,
                    "names": list(
                        child.names
                    ),
                }
            )

    function_parameters = [
        {
            "name": argument.arg,
            "annotation": annotation_text(
                argument.annotation
            ),
            "default": None,
        }
        for argument in node.args.args
    ]

    defaults = list(
        node.args.defaults
    )

    if defaults:
        offset = (
            len(function_parameters)
            - len(defaults)
        )

        for index, default in enumerate(
            defaults
        ):
            function_parameters[
                offset + index
            ][
                "default"
            ] = ast.unparse(
                default
            )

    mutation_calls = [
        item
        for item in calls
        if item[
            "terminal"
        ] in MUTATION_TERMINALS
    ]

    read_only_calls = [
        item
        for item in calls
        if item[
            "terminal"
        ] in READ_ONLY_TERMINALS
    ]

    database_signals = [
        item
        for item in calls
        if any(
            marker in item[
                "call"
            ].lower()
            for marker in DATABASE_MARKERS
        )
    ]

    ledger_signals = [
        item
        for item in calls
        if any(
            marker in item[
                "call"
            ].lower()
            for marker in LEDGER_MARKERS
        )
    ]

    portfolio_signals = [
        item
        for item in calls
        if any(
            marker in item[
                "call"
            ].lower()
            for marker
            in PORTFOLIO_MUTATION_MARKERS
        )
    ]

    paper_execution_signals = [
        item
        for item in calls
        if any(
            marker in item[
                "call"
            ].lower()
            for marker
            in PAPER_EXECUTION_MARKERS
        )
    ]

    network_signals = [
        item
        for item in calls
        if any(
            marker in item[
                "call"
            ].lower()
            for marker in NETWORK_MARKERS
        )
    ]

    imported_database_modules = [
        item
        for item in imports
        if any(
            marker in item[
                "module"
            ].lower()
            for marker in DATABASE_MARKERS
        )
    ]

    imported_ledger_modules = [
        item
        for item in imports
        if any(
            marker in item[
                "module"
            ].lower()
            for marker in LEDGER_MARKERS
        )
    ]

    imported_portfolio_modules = [
        item
        for item in imports
        if "portfolio" in item[
            "module"
        ].lower()
    ]

    imported_broker_modules = [
        item
        for item in imports
        if any(
            marker in item[
                "module"
            ].lower()
            for marker in (
                "broker",
                "snaptrade",
                "execution",
            )
        )
    ]

    return {
        "path": relative(path),
        "function": function_name,
        "line": node.lineno,
        "end_line": getattr(
            node,
            "end_lineno",
            None,
        ),
        "async": isinstance(
            node,
            ast.AsyncFunctionDef,
        ),
        "parameters": function_parameters,
        "return_annotation": annotation_text(
            node.returns
        ),
        "decorators": [
            ast.unparse(
                decorator
            )
            for decorator
            in node.decorator_list
        ],
        "docstring": ast.get_docstring(
            node
        ),
        "source_sha256": hashlib.sha256(
            rendered.encode(
                "utf-8"
            )
        ).hexdigest(),
        "calls": calls,
        "mutation_calls": mutation_calls,
        "read_only_calls": read_only_calls,
        "database_signals": database_signals,
        "ledger_signals": ledger_signals,
        "portfolio_signals": portfolio_signals,
        "paper_execution_signals": (
            paper_execution_signals
        ),
        "network_signals": network_signals,
        "assignments": assignments,
        "attribute_writes": attribute_writes,
        "subscript_writes": subscript_writes,
        "global_mutations": global_mutations,
        "file_mutations": file_mutations,
        "returns": returns,
        "forbidden_live_calls": (
            forbidden_live_calls
        ),
        "imports": imports,
        "imported_database_modules": (
            imported_database_modules
        ),
        "imported_ledger_modules": (
            imported_ledger_modules
        ),
        "imported_portfolio_modules": (
            imported_portfolio_modules
        ),
        "imported_broker_modules": (
            imported_broker_modules
        ),
    }


def local_function_definitions(
    path: Path,
) -> dict[str, dict[str, Any]]:
    source = path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source,
        filename=str(path),
    )

    definitions = {}

    for node in tree.body:
        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        definitions[
            node.name
        ] = {
            "line": node.lineno,
            "end_line": getattr(
                node,
                "end_lineno",
                None,
            ),
            "async": isinstance(
                node,
                ast.AsyncFunctionDef,
            ),
        }

    return definitions


def transitive_local_calls(
    path: Path,
    root_function: str,
    max_depth: int = 5,
) -> list[dict[str, Any]]:
    source = path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source,
        filename=str(path),
    )

    definitions = {
        node.name: node
        for node in tree.body
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
    }

    visited = set()
    queue = deque(
        [
            (
                root_function,
                0,
            )
        ]
    )

    results = []

    while queue:
        function_name, depth = (
            queue.popleft()
        )

        if (
            function_name in visited
            or depth > max_depth
        ):
            continue

        visited.add(
            function_name
        )

        node = definitions.get(
            function_name
        )

        if node is None:
            continue

        calls = []

        for child in ast.walk(
            node
        ):
            if not isinstance(
                child,
                ast.Call,
            ):
                continue

            name = dotted_name(
                child.func
            )

            if not name:
                continue

            terminal = name.split(
                "."
            )[-1]

            calls.append(
                {
                    "line": child.lineno,
                    "call": name,
                    "terminal": terminal,
                }
            )

            if terminal in definitions:
                queue.append(
                    (
                        terminal,
                        depth + 1,
                    )
                )

        results.append(
            {
                "function": function_name,
                "depth": depth,
                "line": node.lineno,
                "calls": calls,
            }
        )

    return results


def find_consumers() -> list[
    dict[str, Any]
]:
    consumers = []

    target_modules = {
        "backend.app.stacks.execution.paper_broker",
        "app.stacks.execution.paper_broker",
        "stacks.execution.paper_broker",
    }

    for path in python_files(
        BACKEND_ROOT
    ):
        source = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        if TARGET_FUNCTION not in source:
            continue

        tree = ast.parse(
            source,
            filename=str(path),
        )

        imports = []
        aliases = set()

        for node in ast.walk(
            tree
        ):
            if isinstance(
                node,
                ast.ImportFrom,
            ):
                module = node.module or ""

                if module not in target_modules:
                    continue

                for alias in node.names:
                    if alias.name != TARGET_FUNCTION:
                        continue

                    local_name = (
                        alias.asname
                        or alias.name
                    )

                    aliases.add(
                        local_name
                    )

                    imports.append(
                        {
                            "line": node.lineno,
                            "module": module,
                            "name": alias.name,
                            "alias": alias.asname,
                        }
                    )

            elif isinstance(
                node,
                ast.Import,
            ):
                for alias in node.names:
                    if alias.name not in target_modules:
                        continue

                    local_name = (
                        alias.asname
                        or alias.name.split(".")[-1]
                    )

                    aliases.add(
                        local_name
                    )

                    imports.append(
                        {
                            "line": node.lineno,
                            "module": alias.name,
                            "name": None,
                            "alias": alias.asname,
                        }
                    )

        direct_definition = any(
            isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
            and node.name == TARGET_FUNCTION
            for node in ast.walk(
                tree
            )
        )

        calls = []

        for node in ast.walk(
            tree
        ):
            if not isinstance(
                node,
                ast.Call,
            ):
                continue

            rendered = dotted_name(
                node.func
            )

            if not rendered:
                continue

            terminal = rendered.split(
                "."
            )[-1]

            if (
                terminal == TARGET_FUNCTION
                or rendered in aliases
                or any(
                    rendered.startswith(
                        alias + "."
                    )
                    and terminal
                    == TARGET_FUNCTION
                    for alias in aliases
                )
            ):
                calls.append(
                    {
                        "line": node.lineno,
                        "scope": enclosing_symbol(
                            tree,
                            node,
                        ),
                        "call": rendered,
                        "source_line": source_line(
                            source,
                            node.lineno,
                        ),
                    }
                )

        if (
            imports
            or calls
            or direct_definition
        ):
            consumers.append(
                {
                    "path": relative(path),
                    "is_test": is_test_path(
                        path
                    ),
                    "defines_target": (
                        direct_definition
                    ),
                    "imports": imports,
                    "calls": calls,
                }
            )

    return consumers


def inspect_tests(
    consumers: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    results = []

    for consumer in consumers:
        if not consumer[
            "is_test"
        ]:
            continue

        path = (
            ROOT
            / consumer[
                "path"
            ]
        )

        source = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        lowered = source.lower()

        results.append(
            {
                "path": consumer[
                    "path"
                ],
                "call_count": len(
                    consumer[
                        "calls"
                    ]
                ),
                "assertion_count": len(
                    re.findall(
                        r"\bassert\b",
                        source,
                    )
                ),
                "failure_test": any(
                    marker in lowered
                    for marker in (
                        "pytest.raises",
                        "raises(",
                        "error",
                        "invalid",
                        "malformed",
                        "failure",
                    )
                ),
                "side_effect_test": any(
                    marker in lowered
                    for marker in (
                        "commit",
                        "rollback",
                        "database",
                        "ledger",
                        "position",
                        "paper_order",
                        "paper_trade",
                    )
                ),
                "return_shape_test": any(
                    marker in lowered
                    for marker in (
                        "isinstance",
                        "dict",
                        "list",
                        "tuple",
                        "result",
                        "output",
                        "keys",
                    )
                ),
            }
        )

    return results


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

    for item in entries:
        digest.update(
            item[
                "path"
            ].encode(
                "utf-8"
            )
        )

        digest.update(
            item[
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

    prior = load_json(
        PRIOR_DISPOSITION
    )

    batch1a = load_json(
        BATCH1A_REPORT
    )

    audit = load_json(
        IMPORT_AUDIT_REPORT
    )

    assert prior[
        "status"
    ] == "completed"

    assert prior[
        "classification"
    ] == (
        "RUNTIME_CROSS_STACK_DEPENDENCY_REQUIRES_REVIEW"
    )

    assert prior[
        "source_path"
    ] == (
        "backend/app/stacks/wolfden_ai/agent_router.py"
    )

    assert prior[
        "reported_stack"
    ] == "execution"

    assert len(
        prior[
            "runtime_calls"
        ]
    ) == 1

    assert len(
        prior[
            "mutation_calls"
        ]
    ) == 0

    assert batch1a[
        "status"
    ] == "completed"

    assert batch1a[
        "wolfden_ai"
    ][
        "remaining_gate_count"
    ] == 2

    summary = audit[
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

    assert TARGET_FILE.is_file(), (
        f"Target owner file missing: {TARGET_FILE}"
    )

    function = inspect_function(
        TARGET_FILE,
        TARGET_FUNCTION,
    )

    local_chain = transitive_local_calls(
        TARGET_FILE,
        TARGET_FUNCTION,
    )

    consumers = find_consumers()

    production_consumers = [
        item
        for item in consumers
        if (
            not item[
                "is_test"
            ]
            and not item[
                "defines_target"
            ]
        )
    ]

    test_consumers = [
        item
        for item in consumers
        if item[
            "is_test"
        ]
    ]

    tests = inspect_tests(
        consumers
    )

    direct_side_effect_signals = {
        "mutation_calls": function[
            "mutation_calls"
        ],
        "database_signals": function[
            "database_signals"
        ],
        "ledger_signals": function[
            "ledger_signals"
        ],
        "portfolio_signals": function[
            "portfolio_signals"
        ],
        "paper_execution_signals": function[
            "paper_execution_signals"
        ],
        "network_signals": function[
            "network_signals"
        ],
        "attribute_writes": function[
            "attribute_writes"
        ],
        "subscript_writes": function[
            "subscript_writes"
        ],
        "global_mutations": function[
            "global_mutations"
        ],
        "file_mutations": function[
            "file_mutations"
        ],
        "forbidden_live_calls": function[
            "forbidden_live_calls"
        ],
    }

    direct_side_effect_count = sum(
        len(items)
        for items
        in direct_side_effect_signals.values()
    )

    transitive_terminals = [
        call[
            "terminal"
        ]
        for record in local_chain
        for call in record[
            "calls"
        ]
    ]

    transitive_mutation_signals = [
        terminal
        for terminal
        in transitive_terminals
        if terminal in MUTATION_TERMINALS
    ]

    transitive_paper_signals = [
        terminal
        for terminal
        in transitive_terminals
        if any(
            marker in terminal.lower()
            for marker
            in PAPER_EXECUTION_MARKERS
        )
    ]

    has_database_ownership = bool(
        function[
            "imported_database_modules"
        ]
        or function[
            "database_signals"
        ]
    )

    has_ledger_ownership = bool(
        function[
            "imported_ledger_modules"
        ]
        or function[
            "ledger_signals"
        ]
    )

    has_portfolio_mutation = bool(
        function[
            "portfolio_signals"
        ]
        and function[
            "mutation_calls"
        ]
    )

    has_paper_execution = bool(
        function[
            "paper_execution_signals"
        ]
        or transitive_paper_signals
    )

    has_global_or_file_mutation = bool(
        function[
            "global_mutations"
        ]
        or function[
            "file_mutations"
        ]
        or function[
            "attribute_writes"
        ]
    )

    has_network_side_effect = bool(
        function[
            "network_signals"
        ]
    )

    pure_candidate = (
        direct_side_effect_count == 0
        and not transitive_mutation_signals
        and not has_database_ownership
        and not has_ledger_ownership
        and not has_portfolio_mutation
        and not has_paper_execution
        and not has_global_or_file_mutation
        and not has_network_side_effect
    )

    return_annotation = (
        function[
            "return_annotation"
        ]
    )

    return_expressions = [
        item[
            "expression"
        ]
        for item in function[
            "returns"
        ]
    ]

    output_contract_explicit = (
        return_annotation is not None
        and return_annotation
        not in {
            "Any",
            "dict",
            "list",
            "tuple",
            "object",
        }
    )

    if function[
        "forbidden_live_calls"
    ]:
        classification = (
            "PAPER_OR_LIVE_EXECUTION_CAPABILITY"
        )

        correct_owner = "execution"

        boundary_action = (
            "Remove wolfden_ai access immediately; "
            "retain capability only inside execution."
        )

    elif (
        has_paper_execution
        or has_portfolio_mutation
    ):
        classification = (
            "PAPER_EXECUTION_OR_PORTFOLIO_MUTATION_CAPABILITY"
        )

        correct_owner = "execution"

        boundary_action = (
            "wolfden_ai must not call this function directly. "
            "Expose only an immutable non-executable result contract."
        )

    elif (
        has_database_ownership
        or has_ledger_ownership
        or has_global_or_file_mutation
        or has_network_side_effect
    ):
        classification = (
            "SIDE_EFFECTING_EXECUTION_SERVICE"
        )

        correct_owner = "execution"

        boundary_action = (
            "Retain in execution and replace the wolfden_ai "
            "import with an approved read-only facade or DTO."
        )

    elif pure_candidate:
        classification = (
            "PURE_TRANSFORMATION_MISOWNED"
        )

        correct_owner = (
            "neutral_contract_or_wolfden_ai"
        )

        boundary_action = (
            "Move the pure transformation out of paper_broker.py "
            "into a neutral transformation module or wolfden_ai-owned "
            "output adapter, then update consumers."
        )

    else:
        classification = (
            "UNRESOLVED_MIXED_OWNERSHIP"
        )

        correct_owner = "undetermined"

        boundary_action = (
            "Do not modify ownership until unresolved transitive "
            "behavior is inspected with focused runtime tests."
        )

    safe_for_wolfden_direct_import = (
        classification
        == "PURE_TRANSFORMATION_MISOWNED"
    )

    source_remediation_authorized = (
        classification
        in {
            "PURE_TRANSFORMATION_MISOWNED",
            "SIDE_EFFECTING_EXECUTION_SERVICE",
            "PAPER_EXECUTION_OR_PORTFOLIO_MUTATION_CAPABILITY",
        }
    )

    if (
        classification
        == "PURE_TRANSFORMATION_MISOWNED"
    ):
        next_step = (
            "IQC Stage 5 Remediation Batch 1A3 — "
            "Extract process_portfolio_output into an approved "
            "pure transformation boundary"
        )

    elif classification in {
        "SIDE_EFFECTING_EXECUTION_SERVICE",
        "PAPER_EXECUTION_OR_PORTFOLIO_MUTATION_CAPABILITY",
    }:
        next_step = (
            "IQC Stage 5 Remediation Batch 1A3 — "
            "Replace wolfden_ai direct execution dependency "
            "with an immutable read-only result facade"
        )

    else:
        next_step = (
            "IQC Stage 5 Remediation Batch 1A3 — "
            "Focused runtime side-effect qualification"
        )

    manifest = source_manifest()

    evidence = {
        "status": "completed",
        "generated_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "target": function,
        "local_transitive_call_chain": (
            local_chain
        ),
        "consumers": consumers,
        "production_consumers": (
            production_consumers
        ),
        "test_consumers": (
            test_consumers
        ),
        "test_evidence": tests,
        "side_effect_signals": (
            direct_side_effect_signals
        ),
        "transitive_mutation_signals": (
            transitive_mutation_signals
        ),
        "transitive_paper_signals": (
            transitive_paper_signals
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
            "IQC-STAGE5-REM-001A2"
        ),
        "batch_name": (
            "process_portfolio_output Ownership, "
            "Side-Effect, and Boundary Disposition"
        ),
        "status": "completed",
        "verified_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "prior_disposition_verified": True,
        "target": {
            "path": relative(
                TARGET_FILE
            ),
            "function": (
                TARGET_FUNCTION
            ),
            "classification": (
                classification
            ),
            "correct_owner": (
                correct_owner
            ),
            "safe_for_wolfden_direct_import": (
                safe_for_wolfden_direct_import
            ),
            "source_remediation_authorized": (
                source_remediation_authorized
            ),
            "boundary_action": (
                boundary_action
            ),
        },
        "contract": {
            "parameters": function[
                "parameters"
            ],
            "return_annotation": (
                return_annotation
            ),
            "return_expressions": (
                return_expressions
            ),
            "explicit_output_contract": (
                output_contract_explicit
            ),
        },
        "side_effects": {
            "direct_side_effect_signal_count": (
                direct_side_effect_count
            ),
            "transitive_mutation_signal_count": len(
                transitive_mutation_signals
            ),
            "database_ownership": (
                has_database_ownership
            ),
            "ledger_ownership": (
                has_ledger_ownership
            ),
            "portfolio_mutation": (
                has_portfolio_mutation
            ),
            "paper_execution": (
                has_paper_execution
            ),
            "global_or_file_mutation": (
                has_global_or_file_mutation
            ),
            "network_side_effect": (
                has_network_side_effect
            ),
            "forbidden_live_calls": len(
                function[
                    "forbidden_live_calls"
                ]
            ),
            "pure_transformation_candidate": (
                pure_candidate
            ),
        },
        "consumers": {
            "production_consumer_count": len(
                production_consumers
            ),
            "test_consumer_count": len(
                test_consumers
            ),
            "production_consumers": (
                production_consumers
            ),
        },
        "tests": {
            "attributed_test_count": len(
                tests
            ),
            "failure_test_count": sum(
                1
                for item in tests
                if item[
                    "failure_test"
                ]
            ),
            "side_effect_test_count": sum(
                1
                for item in tests
                if item[
                    "side_effect_test"
                ]
            ),
            "return_shape_test_count": sum(
                1
                for item in tests
                if item[
                    "return_shape_test"
                ]
            ),
        },
        "wolfden_remaining_completion_gates": [
            (
                "Explicit immutable AI output contract"
            ),
            (
                "Malformed-output and output-contract "
                "qualification test"
            ),
        ],
        "repository": {
            "active_internal_unresolved": 0,
            "syntax_errors": 0,
            "active_cycle_components": 0,
        },
        "source_modified": False,
        "database_modified": False,
        "auth_implemented": False,
        "snaptrade_connected": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
        "next_step": next_step,
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
            "IQC-STAGE5-REM-001A2"
        ),
        "frozen_at": datetime.now(
            UTC
        ).isoformat(),
        "classification": (
            classification
        ),
        "correct_owner": (
            correct_owner
        ),
        "safe_for_wolfden_direct_import": (
            safe_for_wolfden_direct_import
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
            "IQC STAGE 5 REMEDIATION BATCH 1A2 — "
            "PROCESS_PORTFOLIO_OUTPUT OWNERSHIP, "
            "SIDE-EFFECT, AND BOUNDARY DISPOSITION"
        ),
        "=" * 100,
        "",
        "STATUS",
        "COMPLETE AND VERIFIED",
        "",
        "MODE",
        "READ ONLY",
        "",
        "TARGET",
        (
            "Source:                          "
            f"{relative(TARGET_FILE)}"
        ),
        (
            "Function:                        "
            f"{TARGET_FUNCTION}"
        ),
        (
            "Classification:                  "
            f"{classification}"
        ),
        (
            "Correct owner:                   "
            f"{correct_owner}"
        ),
        (
            "Safe for wolfden direct import:  "
            f"{'YES' if safe_for_wolfden_direct_import else 'NO'}"
        ),
        (
            "Source remediation authorized:  "
            f"{'YES' if source_remediation_authorized else 'NO'}"
        ),
        "",
        "FUNCTION CONTRACT",
        (
            "Parameter count:                 "
            f"{len(function['parameters'])}"
        ),
        (
            "Return annotation:               "
            f"{return_annotation}"
        ),
        (
            "Return paths:                    "
            f"{len(function['returns'])}"
        ),
        (
            "Explicit output contract:        "
            f"{'YES' if output_contract_explicit else 'NO'}"
        ),
        "",
        "SIDE-EFFECT DISPOSITION",
        (
            "Direct side-effect signals:      "
            f"{direct_side_effect_count}"
        ),
        (
            "Transitive mutation signals:     "
            f"{len(transitive_mutation_signals)}"
        ),
        (
            "Database ownership:              "
            f"{'YES' if has_database_ownership else 'NO'}"
        ),
        (
            "Ledger ownership:                "
            f"{'YES' if has_ledger_ownership else 'NO'}"
        ),
        (
            "Portfolio mutation:              "
            f"{'YES' if has_portfolio_mutation else 'NO'}"
        ),
        (
            "Paper execution:                 "
            f"{'YES' if has_paper_execution else 'NO'}"
        ),
        (
            "Global or file mutation:         "
            f"{'YES' if has_global_or_file_mutation else 'NO'}"
        ),
        (
            "Network side effect:             "
            f"{'YES' if has_network_side_effect else 'NO'}"
        ),
        (
            "Forbidden live calls:            "
            f"{len(function['forbidden_live_calls'])}"
        ),
        (
            "Pure transformation candidate:   "
            f"{'YES' if pure_candidate else 'NO'}"
        ),
        "",
        "CONSUMERS",
        (
            "Production consumers:            "
            f"{len(production_consumers)}"
        ),
        (
            "Test consumers:                  "
            f"{len(test_consumers)}"
        ),
        "",
        "BOUNDARY ACTION",
        boundary_action,
        "",
        "REMAINING WOLFDEN GATES",
        "1. Explicit immutable AI output contract",
        (
            "2. Malformed-output and output-contract "
            "qualification test"
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
        next_step,
        "",
        "=" * 100,
    ]

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

    print("Production consumers:")

    if production_consumers:
        for consumer in (
            production_consumers
        ):
            print(
                f"- {consumer['path']}"
            )

            for call in consumer[
                "calls"
            ]:
                print(
                    f"  line {call['line']}: "
                    f"{call['call']}"
                )

    else:
        print("- None")

    print()
    print("Report:")
    print(REPORT_JSON)
    print()
    print("Evidence:")
    print(EVIDENCE_JSON)
    print()
    print("Freeze:")
    print(FREEZE_JSON)


if __name__ == "__main__":
    main()
