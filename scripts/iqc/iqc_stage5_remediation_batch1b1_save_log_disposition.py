#!/usr/bin/env python3
"""
NeuroVest Integrated Qualification Campaign

IQC Stage 5 Remediation Batch 1B1 —
save_log Ownership, Persistence, Side-Effect,
and Boundary Disposition

MODE
READ ONLY

This stage:
- Resolves the authoritative save_log definition.
- Inspects direct and transitive behavior.
- Detects database, ledger, file, network, global-state,
  portfolio, execution, broker, and live-trading capability.
- Finds all production and test consumers.
- Determines the correct owner and smallest safe correction.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from collections import deque
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(".").resolve()

BACKEND_ROOT = (
    ROOT
    / "backend"
    / "app"
)

TARGET_MODULES = {
    "backend.app.stacks.journal_ledger.ledger",
    "app.stacks.journal_ledger.ledger",
    "stacks.journal_ledger.ledger",
}

TARGET_FILE = (
    BACKEND_ROOT
    / "stacks"
    / "journal_ledger"
    / "ledger.py"
)

TARGET_FUNCTION = "save_log"

OUTPUT_DIR = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "remediation_batch1b1"
)

PRIOR_REVIEW = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "remediation_batch1b"
    / "iqc_stage5_remediation_batch1b_boundary_review_latest.json"
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
    / "iqc_stage5_remediation_batch1b1_latest.json"
)

REPORT_TEXT = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b1_latest.txt"
)

EVIDENCE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b1_evidence_latest.json"
)

FREEZE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b1_freeze_latest.json"
)

SOURCE_MANIFEST = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b1_source_manifest_latest.json"
)

DATABASE_MARKERS = {
    "sqlalchemy",
    "db_runtime",
    "database",
    "session",
    "repository",
    "engine",
    "orm",
}

LEDGER_MARKERS = {
    "ledger",
    "journal",
    "audit",
    "event",
    "append_event",
    "decision_event",
}

FILE_TERMINALS = {
    "open",
    "write",
    "write_text",
    "write_bytes",
    "mkdir",
    "touch",
    "unlink",
    "rename",
}

PERSISTENCE_TERMINALS = {
    "add",
    "append",
    "commit",
    "delete",
    "execute",
    "flush",
    "insert",
    "merge",
    "rollback",
    "save",
    "update",
    "upsert",
}

EXECUTION_TERMINALS = {
    "process_portfolio_output",
    "execute_order",
    "execute_trade",
    "place_order",
    "submit_order",
    "fill_order",
}

BROKER_TERMINALS = {
    "connect_broker",
    "connect_snaptrade",
    "submit_broker_order",
    "enable_live_trading",
}

NETWORK_MARKERS = {
    "httpx",
    "aiohttp",
    "requests",
    "urllib",
    "socket",
    "websocket",
}

OBSERVABILITY_MARKERS = {
    "logging",
    "logger",
    "telemetry",
    "metrics",
    "trace",
    "counter",
    "histogram",
}

READ_ONLY_TERMINALS = {
    "get",
    "read",
    "lookup",
    "find",
    "list",
    "status",
    "snapshot",
    "describe",
    "validate",
    "serialize",
    "model_dump",
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

    assert isinstance(value, dict)

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
    parts = {
        part.lower()
        for part in path.parts
    }

    return (
        "test" in parts
        or "tests" in parts
        or "l7_tests" in parts
        or path.name.startswith("test_")
        or path.name.endswith("_test.py")
    )


def dotted_name(
    node: ast.AST,
) -> str | None:
    if isinstance(node, ast.Name):
        return node.id

    if isinstance(node, ast.Attribute):
        parent = dotted_name(
            node.value
        )

        if parent:
            return f"{parent}.{node.attr}"

        return node.attr

    return None


def annotation_text(
    node: ast.expr | None,
) -> str | None:
    if node is None:
        return None

    try:
        return ast.unparse(node)

    except Exception:
        return None


def enclosing_scope(
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

    candidates = []

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
            and start <= line <= end
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


def extract_definition() -> tuple[
    str,
    ast.Module,
    ast.FunctionDef | ast.AsyncFunctionDef,
]:
    assert TARGET_FILE.is_file(), (
        f"Target file missing: {TARGET_FILE}"
    )

    source = TARGET_FILE.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source,
        filename=str(TARGET_FILE),
    )

    matches = [
        node
        for node in ast.walk(tree)
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
        and node.name == TARGET_FUNCTION
    ]

    assert len(matches) == 1, (
        f"Expected one {TARGET_FUNCTION} definition; "
        f"found {len(matches)}"
    )

    return source, tree, matches[0]


def inspect_target() -> dict[str, Any]:
    source, tree, function = (
        extract_definition()
    )

    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(
                    {
                        "line": node.lineno,
                        "module": alias.name,
                        "symbol": None,
                        "alias": alias.asname,
                    }
                )

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""

            for alias in node.names:
                imports.append(
                    {
                        "line": node.lineno,
                        "module": module,
                        "symbol": alias.name,
                        "alias": alias.asname,
                    }
                )

    calls = []
    returns = []
    global_mutations = []
    attribute_writes = []
    subscript_writes = []

    for node in ast.walk(function):
        if isinstance(node, ast.Call):
            rendered = dotted_name(
                node.func
            )

            if not rendered:
                continue

            calls.append(
                {
                    "line": node.lineno,
                    "scope": enclosing_scope(
                        tree,
                        node,
                    ),
                    "call": rendered,
                    "terminal": rendered.split(".")[-1],
                    "argument_count": len(node.args),
                    "keyword_names": sorted(
                        keyword.arg
                        for keyword in node.keywords
                        if keyword.arg
                    ),
                }
            )

        elif isinstance(node, ast.Return):
            returns.append(
                {
                    "line": node.lineno,
                    "expression": (
                        ast.unparse(node.value)
                        if node.value is not None
                        else None
                    ),
                    "expression_type": (
                        type(node.value).__name__
                        if node.value is not None
                        else "None"
                    ),
                }
            )

        elif isinstance(
            node,
            (
                ast.Global,
                ast.Nonlocal,
            ),
        ):
            global_mutations.append(
                {
                    "line": node.lineno,
                    "kind": type(node).__name__,
                    "names": list(node.names),
                }
            )

        elif isinstance(
            node,
            (
                ast.Assign,
                ast.AnnAssign,
                ast.AugAssign,
            ),
        ):
            if isinstance(node, ast.Assign):
                targets = node.targets

            else:
                targets = [node.target]

            for target in targets:
                if isinstance(
                    target,
                    ast.Attribute,
                ):
                    attribute_writes.append(
                        {
                            "line": node.lineno,
                            "target": ast.unparse(
                                target
                            ),
                        }
                    )

                elif isinstance(
                    target,
                    ast.Subscript,
                ):
                    subscript_writes.append(
                        {
                            "line": node.lineno,
                            "target": ast.unparse(
                                target
                            ),
                        }
                    )

    persistence_calls = [
        item
        for item in calls
        if item["terminal"]
        in PERSISTENCE_TERMINALS
    ]

    file_calls = [
        item
        for item in calls
        if item["terminal"]
        in FILE_TERMINALS
    ]

    execution_calls = [
        item
        for item in calls
        if item["terminal"]
        in EXECUTION_TERMINALS
    ]

    broker_calls = [
        item
        for item in calls
        if item["terminal"]
        in BROKER_TERMINALS
    ]

    read_only_calls = [
        item
        for item in calls
        if item["terminal"]
        in READ_ONLY_TERMINALS
    ]

    database_imports = [
        item
        for item in imports
        if any(
            marker in item["module"].lower()
            for marker in DATABASE_MARKERS
        )
    ]

    ledger_imports = [
        item
        for item in imports
        if any(
            marker in item["module"].lower()
            for marker in LEDGER_MARKERS
        )
    ]

    network_imports = [
        item
        for item in imports
        if any(
            marker in item["module"].lower()
            for marker in NETWORK_MARKERS
        )
    ]

    observability_imports = [
        item
        for item in imports
        if any(
            marker in item["module"].lower()
            for marker in OBSERVABILITY_MARKERS
        )
    ]

    parameters = [
        {
            "name": argument.arg,
            "annotation": annotation_text(
                argument.annotation
            ),
        }
        for argument in function.args.args
    ]

    rendered_function = (
        ast.get_source_segment(
            source,
            function,
        )
        or ""
    )

    return {
        "path": relative(TARGET_FILE),
        "function": TARGET_FUNCTION,
        "line": function.lineno,
        "end_line": getattr(
            function,
            "end_lineno",
            None,
        ),
        "async": isinstance(
            function,
            ast.AsyncFunctionDef,
        ),
        "parameters": parameters,
        "return_annotation": annotation_text(
            function.returns
        ),
        "docstring": ast.get_docstring(
            function
        ),
        "function_sha256": hashlib.sha256(
            rendered_function.encode(
                "utf-8"
            )
        ).hexdigest(),
        "imports": imports,
        "calls": calls,
        "persistence_calls": persistence_calls,
        "file_calls": file_calls,
        "execution_calls": execution_calls,
        "broker_calls": broker_calls,
        "read_only_calls": read_only_calls,
        "database_imports": database_imports,
        "ledger_imports": ledger_imports,
        "network_imports": network_imports,
        "observability_imports": (
            observability_imports
        ),
        "returns": returns,
        "global_mutations": global_mutations,
        "attribute_writes": attribute_writes,
        "subscript_writes": subscript_writes,
    }


def local_call_chain(
    max_depth: int = 5,
) -> list[dict[str, Any]]:
    source = TARGET_FILE.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source,
        filename=str(TARGET_FILE),
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

    queue = deque(
        [
            (
                TARGET_FUNCTION,
                0,
            )
        ]
    )

    visited = set()
    records = []

    while queue:
        name, depth = queue.popleft()

        if (
            name in visited
            or depth > max_depth
        ):
            continue

        visited.add(name)

        node = definitions.get(name)

        if node is None:
            continue

        calls = []

        for child in ast.walk(node):
            if not isinstance(
                child,
                ast.Call,
            ):
                continue

            rendered = dotted_name(
                child.func
            )

            if not rendered:
                continue

            terminal = rendered.split(".")[-1]

            calls.append(
                {
                    "line": child.lineno,
                    "call": rendered,
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

        records.append(
            {
                "function": name,
                "line": node.lineno,
                "depth": depth,
                "calls": calls,
            }
        )

    return records


def find_consumers() -> list[
    dict[str, Any]
]:
    consumers = []

    for path in python_files(
        BACKEND_ROOT
    ):
        source = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        if TARGET_FUNCTION not in source:
            continue

        try:
            tree = ast.parse(
                source,
                filename=str(path),
            )

        except SyntaxError:
            continue

        imported_names = set()
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""

                if module not in TARGET_MODULES:
                    continue

                for alias in node.names:
                    if alias.name != TARGET_FUNCTION:
                        continue

                    local_name = (
                        alias.asname
                        or alias.name
                    )

                    imported_names.add(
                        local_name
                    )

                    imports.append(
                        {
                            "line": node.lineno,
                            "module": module,
                            "symbol": alias.name,
                            "alias": alias.asname,
                            "local_name": local_name,
                        }
                    )

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name not in TARGET_MODULES:
                        continue

                    local_name = (
                        alias.asname
                        or alias.name.split(".")[-1]
                    )

                    imported_names.add(
                        local_name
                    )

                    imports.append(
                        {
                            "line": node.lineno,
                            "module": alias.name,
                            "symbol": None,
                            "alias": alias.asname,
                            "local_name": local_name,
                        }
                    )

        defines_target = any(
            isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
            and node.name == TARGET_FUNCTION
            for node in ast.walk(tree)
        )

        calls = []

        for node in ast.walk(tree):
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

            terminal = rendered.split(".")[-1]

            if (
                terminal == TARGET_FUNCTION
                or rendered in imported_names
            ):
                calls.append(
                    {
                        "line": node.lineno,
                        "scope": enclosing_scope(
                            tree,
                            node,
                        ),
                        "call": rendered,
                    }
                )

        if (
            imports
            or calls
            or defines_target
        ):
            relative_path = relative(path)

            owner_stack = None
            parts = relative_path.split("/")

            if "stacks" in parts:
                index = parts.index("stacks")

                if index + 1 < len(parts):
                    owner_stack = parts[
                        index + 1
                    ]

            consumers.append(
                {
                    "path": relative_path,
                    "owner_stack": owner_stack,
                    "is_test": is_test_path(path),
                    "defines_target": defines_target,
                    "imports": imports,
                    "calls": calls,
                }
            )

    return consumers


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


def backend_tests() -> dict[str, Any]:
    assert TEST_LOG.is_file()
    assert TEST_EXIT_FILE.is_file()

    text = TEST_LOG.read_text(
        encoding="utf-8",
        errors="replace",
    )

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
        "exit_code": exit_code,
        "passed": count("passed"),
        "failed": count("failed"),
    }


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    prior = load_json(
        PRIOR_REVIEW
    )

    audit = load_json(
        IMPORT_AUDIT
    )

    assert prior["status"] == "completed"
    assert prior["mode"] == "read_only"

    assert prior[
        "forbidden_import"
    ][
        "source_path"
    ] == (
        "backend/app/stacks/"
        "wolfden_ai/agent_router.py"
    )

    assert prior[
        "forbidden_import"
    ][
        "reported_module"
    ] == (
        "backend.app.stacks."
        "journal_ledger.ledger"
    )

    assert prior[
        "forbidden_import"
    ][
        "classification"
    ] == (
        "RUNTIME_CROSS_STACK_DEPENDENCY"
    )

    assert len(
        prior[
            "forbidden_import"
        ][
            "runtime_calls"
        ]
    ) == 1

    summary = audit["summary"]

    assert summary[
        "active_internal_unresolved"
    ] == 0

    assert summary[
        "syntax_errors"
    ] == 0

    assert summary[
        "active_cycle_components"
    ] == 0

    target = inspect_target()
    call_chain = local_call_chain()
    consumers = find_consumers()

    production_consumers = [
        item
        for item in consumers
        if (
            not item["is_test"]
            and not item[
                "defines_target"
            ]
        )
    ]

    test_consumers = [
        item
        for item in consumers
        if item["is_test"]
    ]

    transitive_calls = [
        call
        for record in call_chain
        for call in record["calls"]
    ]

    transitive_persistence = [
        item
        for item in transitive_calls
        if item["terminal"]
        in PERSISTENCE_TERMINALS
    ]

    transitive_execution = [
        item
        for item in transitive_calls
        if item["terminal"]
        in EXECUTION_TERMINALS
    ]

    transitive_broker = [
        item
        for item in transitive_calls
        if item["terminal"]
        in BROKER_TERMINALS
    ]

    database_ownership = bool(
        target["database_imports"]
    )

    ledger_ownership = bool(
        target["ledger_imports"]
        or target[
            "persistence_calls"
        ]
    )

    file_side_effect = bool(
        target["file_calls"]
    )

    persistence_side_effect = bool(
        target["persistence_calls"]
        or transitive_persistence
    )

    execution_side_effect = bool(
        target["execution_calls"]
        or transitive_execution
    )

    broker_side_effect = bool(
        target["broker_calls"]
        or transitive_broker
    )

    global_state_mutation = bool(
        target["global_mutations"]
        or target["attribute_writes"]
    )

    network_side_effect = bool(
        target["network_imports"]
    )

    observability_only_candidate = (
        not database_ownership
        and not ledger_ownership
        and not file_side_effect
        and not persistence_side_effect
        and not execution_side_effect
        and not broker_side_effect
        and not global_state_mutation
        and not network_side_effect
        and bool(
            target[
                "observability_imports"
            ]
        )
    )

    pure_candidate = (
        not database_ownership
        and not ledger_ownership
        and not file_side_effect
        and not persistence_side_effect
        and not execution_side_effect
        and not broker_side_effect
        and not global_state_mutation
        and not network_side_effect
    )

    if broker_side_effect:
        classification = (
            "BROKER_OR_LIVE_CAPABILITY"
        )

        correct_owner = (
            "broker_integration"
        )

        wolfden_direct_access_allowed = False

        boundary_action = (
            "Remove Wolfden access immediately. "
            "Broker capability must remain behind "
            "broker and execution safety gates."
        )

    elif execution_side_effect:
        classification = (
            "EXECUTION_CAPABILITY"
        )

        correct_owner = "execution"

        wolfden_direct_access_allowed = False

        boundary_action = (
            "Replace Wolfden access with an immutable "
            "non-executable observability or audit request."
        )

    elif (
        database_ownership
        or ledger_ownership
        or persistence_side_effect
    ):
        classification = (
            "JOURNAL_LEDGER_PERSISTENCE_CAPABILITY"
        )

        correct_owner = (
            "journal_ledger"
        )

        wolfden_direct_access_allowed = False

        boundary_action = (
            "Retain save_log inside journal_ledger. "
            "Wolfden must not import the persistence "
            "implementation directly. Use an approved "
            "append facade or neutral observability port."
        )

    elif file_side_effect:
        classification = (
            "FILE_LOGGING_SIDE_EFFECT"
        )

        correct_owner = (
            "observability_or_runtime"
        )

        wolfden_direct_access_allowed = False

        boundary_action = (
            "Move file-writing responsibility behind "
            "an observability service or runtime adapter."
        )

    elif observability_only_candidate:
        classification = (
            "OBSERVABILITY_SERVICE_MISOWNED"
        )

        correct_owner = (
            "observability_or_runtime"
        )

        wolfden_direct_access_allowed = False

        boundary_action = (
            "Replace the journal-ledger import with a "
            "neutral observability boundary."
        )

    elif pure_candidate:
        classification = (
            "PURE_HELPER_MISOWNED"
        )

        correct_owner = (
            "neutral_utility_or_wolfden_ai"
        )

        wolfden_direct_access_allowed = True

        boundary_action = (
            "Move the pure helper out of journal_ledger "
            "or replace it with a Wolfden-owned helper."
        )

    else:
        classification = (
            "UNRESOLVED_MIXED_SIDE_EFFECT"
        )

        correct_owner = "undetermined"

        wolfden_direct_access_allowed = False

        boundary_action = (
            "Do not change source until focused runtime "
            "side-effect qualification resolves ownership."
        )

    source_remediation_authorized = (
        classification
        in {
            "JOURNAL_LEDGER_PERSISTENCE_CAPABILITY",
            "FILE_LOGGING_SIDE_EFFECT",
            "OBSERVABILITY_SERVICE_MISOWNED",
            "PURE_HELPER_MISOWNED",
        }
    )

    if classification == (
        "JOURNAL_LEDGER_PERSISTENCE_CAPABILITY"
    ):
        next_step = (
            "IQC Stage 5 Remediation Batch 1B1A — "
            "Replace Wolfden Direct save_log Persistence "
            "Dependency with an Approved Audit or "
            "Observability Boundary"
        )

    elif classification in {
        "FILE_LOGGING_SIDE_EFFECT",
        "OBSERVABILITY_SERVICE_MISOWNED",
    }:
        next_step = (
            "IQC Stage 5 Remediation Batch 1B1A — "
            "Extract Wolfden Logging into a Neutral "
            "Observability Boundary"
        )

    elif classification == (
        "PURE_HELPER_MISOWNED"
    ):
        next_step = (
            "IQC Stage 5 Remediation Batch 1B1A — "
            "Relocate the Pure save_log Helper"
        )

    elif classification in {
        "BROKER_OR_LIVE_CAPABILITY",
        "EXECUTION_CAPABILITY",
    }:
        next_step = (
            "Focused safety-boundary remediation "
            "before any local-model qualification."
        )

    else:
        next_step = (
            "Focused runtime side-effect "
            "qualification for save_log."
        )

    tests = backend_tests()

    assert tests["exit_code"] == 0
    assert tests["failed"] == 0

    manifest = source_manifest()

    evidence = {
        "status": "completed",
        "generated_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "target": target,
        "local_transitive_call_chain": (
            call_chain
        ),
        "consumers": consumers,
        "production_consumers": (
            production_consumers
        ),
        "test_consumers": test_consumers,
        "transitive_persistence_calls": (
            transitive_persistence
        ),
        "transitive_execution_calls": (
            transitive_execution
        ),
        "transitive_broker_calls": (
            transitive_broker
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
            "IQC-STAGE5-REM-001B1"
        ),
        "batch_name": (
            "save_log Ownership, Persistence, "
            "Side-Effect, and Boundary Disposition"
        ),
        "status": "completed",
        "verified_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "prior_boundary_review_verified": True,
        "target": {
            "path": target["path"],
            "function": target["function"],
            "classification": (
                classification
            ),
            "correct_owner": correct_owner,
            "wolfden_direct_access_allowed": (
                wolfden_direct_access_allowed
            ),
            "source_remediation_authorized": (
                source_remediation_authorized
            ),
            "boundary_action": (
                boundary_action
            ),
        },
        "contract": {
            "parameters": target[
                "parameters"
            ],
            "return_annotation": target[
                "return_annotation"
            ],
            "return_paths": target[
                "returns"
            ],
        },
        "side_effects": {
            "database_ownership": (
                database_ownership
            ),
            "ledger_ownership": (
                ledger_ownership
            ),
            "persistence_side_effect": (
                persistence_side_effect
            ),
            "file_side_effect": (
                file_side_effect
            ),
            "execution_side_effect": (
                execution_side_effect
            ),
            "broker_side_effect": (
                broker_side_effect
            ),
            "network_side_effect": (
                network_side_effect
            ),
            "global_state_mutation": (
                global_state_mutation
            ),
            "observability_only_candidate": (
                observability_only_candidate
            ),
            "pure_helper_candidate": (
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
        "qualification": {
            "whole_backend_passed": (
                tests["passed"]
            ),
            "whole_backend_failed": 0,
        },
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
            "IQC-STAGE5-REM-001B1"
        ),
        "frozen_at": datetime.now(
            UTC
        ).isoformat(),
        "classification": classification,
        "correct_owner": correct_owner,
        "wolfden_direct_access_allowed": (
            wolfden_direct_access_allowed
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
            "IQC STAGE 5 REMEDIATION BATCH 1B1 — "
            "SAVE_LOG OWNERSHIP, PERSISTENCE, "
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
            f"{target['path']}"
        ),
        (
            "Function:                        "
            f"{target['function']}"
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
            "Wolfden direct access allowed:   "
            f"{'YES' if wolfden_direct_access_allowed else 'NO'}"
        ),
        (
            "Source remediation authorized:   "
            f"{'YES' if source_remediation_authorized else 'NO'}"
        ),
        "",
        "SIDE EFFECTS",
        (
            "Database ownership:              "
            f"{'YES' if database_ownership else 'NO'}"
        ),
        (
            "Ledger ownership:                "
            f"{'YES' if ledger_ownership else 'NO'}"
        ),
        (
            "Persistence side effect:         "
            f"{'YES' if persistence_side_effect else 'NO'}"
        ),
        (
            "File side effect:                "
            f"{'YES' if file_side_effect else 'NO'}"
        ),
        (
            "Execution side effect:           "
            f"{'YES' if execution_side_effect else 'NO'}"
        ),
        (
            "Broker side effect:              "
            f"{'YES' if broker_side_effect else 'NO'}"
        ),
        (
            "Network side effect:             "
            f"{'YES' if network_side_effect else 'NO'}"
        ),
        (
            "Global-state mutation:           "
            f"{'YES' if global_state_mutation else 'NO'}"
        ),
        (
            "Observability-only candidate:    "
            f"{'YES' if observability_only_candidate else 'NO'}"
        ),
        (
            "Pure helper candidate:           "
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
        "QUALIFICATION",
        (
            "Whole-backend tests passed:      "
            f"{tests['passed']}"
        ),
        "Whole-backend tests failed:      0",
        "Active unresolved imports:       0",
        "Dependency cycles:               0",
        "",
        "SAFETY",
        "- Source modified: NO",
        "- Database modified: NO",
        "- Auth implemented: NO",
        "- SnapTrade connected: NO",
        "- Broker execution enabled: NO",
        "- Live trading enabled: NO",
        "",
        "NEXT",
        next_step,
        "",
        "=" * 100,
    ]

    rendered = (
        "\n".join(lines)
        + "\n"
    )

    REPORT_TEXT.write_text(
        rendered,
        encoding="utf-8",
    )

    print(rendered)

    print("Production consumers:")

    if production_consumers:
        for consumer in production_consumers:
            print(
                f"- {consumer['path']}"
            )

            for call in consumer["calls"]:
                print(
                    f"  line {call['line']} "
                    f"{call['scope']}: "
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
