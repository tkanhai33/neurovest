#!/usr/bin/env python3
"""
NeuroVest Integrated Qualification Campaign

IQC Remediation Batch 3A —
chat_public Persistence, Mutation,
and Dynamic-Execution Disposition

Read-only goals:

1. Resolve the exact direct-persistence imports detected in Batch 3.
2. Resolve each mutation-like call to its file, line, function and receiver.
3. Resolve each dynamic-execution-like call.
4. Identify both production consumers and how they use chat_public.
5. Determine whether chat_public owns API routes.
6. Classify each signal as:
   - CONFIRMED_BOUNDARY_DEFECT
   - CONFIRMED_MUTATION_CAPABILITY
   - CONFIRMED_DYNAMIC_EXECUTION
   - ACCEPTABLE_READ_ONLY_BEHAVIOR
   - ACCEPTABLE_LOCAL_STATE_OPERATION
   - TEST_OR_TOOLING_ONLY
   - SCANNER_FALSE_POSITIVE
   - REQUIRES_TARGETED_REMEDIATION
7. Produce the smallest remediation disposition without changing source.
"""

from __future__ import annotations

import ast
import hashlib
import json
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
    / "remediation_batch3a"
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

BATCH3_REPORT = (
    RUNTIME_ROOT
    / "iqc"
    / "remediation_batch3"
    / "iqc_remediation_batch3_chat_public_latest.json"
)

BATCH3_EVIDENCE = (
    RUNTIME_ROOT
    / "iqc"
    / "remediation_batch3"
    / "iqc_remediation_batch3_chat_public_evidence_latest.json"
)

BATCH3_FREEZE = (
    RUNTIME_ROOT
    / "iqc"
    / "remediation_batch3"
    / "iqc_remediation_batch3_chat_public_freeze_latest.json"
)

IMPORT_AUDIT_REPORT = (
    RUNTIME_ROOT
    / "hardening"
    / "workstream1"
    / "import_cycle_audit_latest.json"
)

REPORT_JSON = (
    OUTPUT_DIR
    / "iqc_remediation_batch3a_chat_disposition_latest.json"
)

REPORT_TEXT = (
    OUTPUT_DIR
    / "iqc_remediation_batch3a_chat_disposition_latest.txt"
)

EVIDENCE_JSON = (
    OUTPUT_DIR
    / "iqc_remediation_batch3a_chat_disposition_evidence_latest.json"
)

FREEZE_JSON = (
    OUTPUT_DIR
    / "iqc_remediation_batch3a_chat_disposition_freeze_latest.json"
)

DIRECT_PERSISTENCE_PREFIXES = (
    "backend.app.stacks.db_runtime",
    "app.stacks.db_runtime",
    "stacks.db_runtime",
    "backend.app.stacks.db_model",
    "app.stacks.db_model",
    "stacks.db_model",
    "sqlalchemy",
)

MUTATION_TERMINALS = {
    "add",
    "append",
    "commit",
    "delete",
    "execute_order",
    "execute_trade",
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

DYNAMIC_TERMINALS = {
    "__import__",
    "compile",
    "eval",
    "exec",
}

ROUTE_DECORATOR_TERMINALS = {
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "route",
    "websocket",
}

PERSISTENCE_MUTATION_TERMINALS = {
    "add",
    "commit",
    "delete",
    "execute",
    "flush",
    "insert",
    "merge",
    "rollback",
    "save",
    "truncate",
    "update",
    "upsert",
}

TRADING_MUTATION_TERMINALS = {
    "execute_order",
    "execute_trade",
    "place_order",
    "submit_order",
}

HARMLESS_COLLECTION_MUTATIONS = {
    "append",
    "add",
    "update",
}

SAFE_COMPILE_MODULE_PREFIXES = {
    "re",
    "regex",
}

CHAT_IMPORT_TOKENS = (
    "backend.app.stacks.chat_public",
    "app.stacks.chat_public",
    "stacks.chat_public",
)


@dataclass(frozen=True)
class CallRecord:
    path: str
    line: int
    column: int
    enclosing_symbol: str
    rendered_call: str
    receiver: str | None
    terminal: str
    argument_count: int
    keyword_names: tuple[str, ...]
    source_line: str


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
        or path.name.startswith(
            "test_"
        )
        or path.name.endswith(
            "_test.py"
        )
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


def enclosing_symbol(
    tree: ast.AST,
    target: ast.AST,
) -> str:
    candidates = []

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

        target_line = getattr(
            target,
            "lineno",
            None,
        )

        if (
            start is None
            or end is None
            or target_line is None
        ):
            continue

        if start <= target_line <= end:
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


def source_line(
    source: str,
    line: int,
) -> str:
    lines = source.splitlines()

    if line < 1 or line > len(
        lines
    ):
        return ""

    return lines[
        line - 1
    ].strip()


def inspect_imports(
    path: Path,
) -> list[dict[str, Any]]:
    source = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    tree = ast.parse(
        source,
        filename=str(path),
    )

    imports = []

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                module = alias.name

                imports.append(
                    {
                        "path": relative(
                            path
                        ),
                        "line": node.lineno,
                        "kind": "import",
                        "module": module,
                        "name": None,
                        "alias": alias.asname,
                        "direct_persistence": (
                            module.startswith(
                                DIRECT_PERSISTENCE_PREFIXES
                            )
                        ),
                        "source_line": source_line(
                            source,
                            node.lineno,
                        ),
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
                        "path": relative(
                            path
                        ),
                        "line": node.lineno,
                        "kind": "from_import",
                        "module": module,
                        "name": alias.name,
                        "alias": alias.asname,
                        "direct_persistence": (
                            module.startswith(
                                DIRECT_PERSISTENCE_PREFIXES
                            )
                        ),
                        "source_line": source_line(
                            source,
                            node.lineno,
                        ),
                    }
                )

    return imports


def inspect_calls(
    path: Path,
) -> list[CallRecord]:
    source = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    tree = ast.parse(
        source,
        filename=str(path),
    )

    records = []

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

        receiver = None

        if "." in rendered:
            receiver = rendered.rsplit(
                ".",
                1,
            )[0]

        records.append(
            CallRecord(
                path=relative(
                    path
                ),
                line=node.lineno,
                column=node.col_offset,
                enclosing_symbol=(
                    enclosing_symbol(
                        tree,
                        node,
                    )
                ),
                rendered_call=rendered,
                receiver=receiver,
                terminal=terminal,
                argument_count=len(
                    node.args
                ),
                keyword_names=tuple(
                    sorted(
                        keyword.arg
                        for keyword in node.keywords
                        if keyword.arg
                    )
                ),
                source_line=source_line(
                    source,
                    node.lineno,
                ),
            )
        )

    return records


def inspect_routes(
    path: Path,
) -> list[dict[str, Any]]:
    source = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    tree = ast.parse(
        source,
        filename=str(path),
    )

    routes = []

    for node in ast.walk(
        tree
    ):
        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        for decorator in node.decorator_list:
            expression = decorator

            if isinstance(
                decorator,
                ast.Call,
            ):
                expression = decorator.func

            name = dotted_name(
                expression
            )

            if not name:
                continue

            terminal = name.split(
                "."
            )[-1]

            if terminal not in (
                ROUTE_DECORATOR_TERMINALS
            ):
                continue

            routes.append(
                {
                    "path": relative(
                        path
                    ),
                    "line": node.lineno,
                    "function": node.name,
                    "decorator": ast.unparse(
                        decorator
                    ),
                    "method": terminal,
                }
            )

    return routes


def classify_persistence_import(
    item: dict[str, Any],
    all_calls: list[CallRecord],
) -> dict[str, Any]:
    module = item[
        "module"
    ]

    imported_name = item.get(
        "alias"
    ) or item.get(
        "name"
    )

    related_calls = []

    if imported_name:
        for call in all_calls:
            if (
                call.rendered_call
                == imported_name
                or call.rendered_call.startswith(
                    imported_name
                    + "."
                )
                or call.receiver
                == imported_name
            ):
                related_calls.append(
                    call
                )

    mutation_related = [
        call
        for call in related_calls
        if call.terminal
        in PERSISTENCE_MUTATION_TERMINALS
    ]

    if mutation_related:
        classification = (
            "CONFIRMED_BOUNDARY_DEFECT"
        )

        disposition = (
            "Direct persistence import participates "
            "in mutation-capable behavior and must be "
            "hidden behind an approved service or facade."
        )

    elif related_calls:
        classification = (
            "REQUIRES_TARGETED_REMEDIATION"
        )

        disposition = (
            "Direct persistence import is used, but no "
            "confirmed persistence mutation was identified. "
            "Move it behind an approved read/service boundary."
        )

    else:
        classification = (
            "CONFIRMED_BOUNDARY_DEFECT"
        )

        disposition = (
            "Direct persistence ownership exists in "
            "chat_public even though its use was not "
            "resolved through the imported symbol."
        )

    return {
        **item,
        "classification": classification,
        "disposition": disposition,
        "related_calls": [
            call.__dict__
            for call in related_calls
        ],
        "mutation_related_calls": [
            call.__dict__
            for call in mutation_related
        ],
    }


def classify_mutation_call(
    call: CallRecord,
    direct_import_names: set[str],
) -> dict[str, Any]:
    receiver = call.receiver or ""

    persistence_receiver = (
        receiver in direct_import_names
        or any(
            token in receiver.lower()
            for token in (
                "session",
                "repository",
                "repo",
                "database",
                "db",
                "model",
                "ledger",
            )
        )
    )

    trading_receiver = any(
        token in receiver.lower()
        for token in (
            "broker",
            "execution",
            "trade",
            "order",
        )
    )

    local_collection_receiver = any(
        token in receiver.lower()
        for token in (
            "list",
            "set",
            "dict",
            "messages",
            "history",
            "records",
            "results",
            "items",
            "parts",
            "lines",
            "tokens",
            "payload",
            "context",
        )
    )

    if (
        call.terminal
        in TRADING_MUTATION_TERMINALS
        or trading_receiver
    ):
        classification = (
            "CONFIRMED_MUTATION_CAPABILITY"
        )

        disposition = (
            "Trading or execution mutation signal "
            "requires immediate boundary remediation."
        )

    elif (
        call.terminal
        in PERSISTENCE_MUTATION_TERMINALS
        and persistence_receiver
    ):
        classification = (
            "CONFIRMED_BOUNDARY_DEFECT"
        )

        disposition = (
            "Persistence mutation is owned inside "
            "chat_public and must move behind a service."
        )

    elif (
        call.terminal
        in HARMLESS_COLLECTION_MUTATIONS
        and local_collection_receiver
    ):
        classification = (
            "ACCEPTABLE_LOCAL_STATE_OPERATION"
        )

        disposition = (
            "The call appears to mutate only a local "
            "in-memory collection."
        )

    elif call.terminal == "append":
        classification = (
            "ACCEPTABLE_LOCAL_STATE_OPERATION"
        )

        disposition = (
            "append() is treated as local collection "
            "mutation unless receiver evidence proves "
            "persistent ownership."
        )

    elif call.terminal == "update":
        classification = (
            "REQUIRES_TARGETED_REMEDIATION"
        )

        disposition = (
            "update() receiver could not be conclusively "
            "classified as local or persistent."
        )

    else:
        classification = (
            "REQUIRES_TARGETED_REMEDIATION"
        )

        disposition = (
            "Mutation-like call requires receiver-level "
            "inspection before source changes."
        )

    return {
        **call.__dict__,
        "classification": classification,
        "disposition": disposition,
        "persistence_receiver_detected": (
            persistence_receiver
        ),
        "trading_receiver_detected": (
            trading_receiver
        ),
        "local_collection_receiver_detected": (
            local_collection_receiver
        ),
    }


def classify_dynamic_call(
    call: CallRecord,
) -> dict[str, Any]:
    receiver = call.receiver or ""

    if (
        call.terminal == "compile"
        and receiver
        in SAFE_COMPILE_MODULE_PREFIXES
    ):
        classification = (
            "SCANNER_FALSE_POSITIVE"
        )

        disposition = (
            "Regular-expression compilation is not "
            "dynamic Python code execution."
        )

    elif call.terminal == "compile":
        classification = (
            "REQUIRES_TARGETED_REMEDIATION"
        )

        disposition = (
            "compile() was detected outside a recognized "
            "regular-expression receiver."
        )

    elif call.terminal in {
        "eval",
        "exec",
    }:
        classification = (
            "CONFIRMED_DYNAMIC_EXECUTION"
        )

        disposition = (
            "Dynamic Python execution is unsafe for "
            "a public chat boundary."
        )

    elif call.terminal == "__import__":
        classification = (
            "CONFIRMED_DYNAMIC_EXECUTION"
        )

        disposition = (
            "Runtime module importing was detected and "
            "requires an explicit allowlist or removal."
        )

    else:
        classification = (
            "REQUIRES_TARGETED_REMEDIATION"
        )

        disposition = (
            "Dynamic-execution signal could not be "
            "safely classified."
        )

    return {
        **call.__dict__,
        "classification": classification,
        "disposition": disposition,
    }


def inspect_consumers() -> list[dict[str, Any]]:
    consumers = []

    for path in python_files(
        BACKEND_ROOT
    ):
        if CHAT_ROOT in path.parents:
            continue

        source = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        if not any(
            token in source
            for token in CHAT_IMPORT_TOKENS
        ):
            continue

        tree = ast.parse(
            source,
            filename=str(path),
        )

        imports = []
        imported_names = set()

        for node in ast.walk(
            tree
        ):
            if isinstance(
                node,
                ast.Import,
            ):
                for alias in node.names:
                    if alias.name.startswith(
                        CHAT_IMPORT_TOKENS
                    ):
                        imports.append(
                            {
                                "line": node.lineno,
                                "module": alias.name,
                                "name": None,
                                "alias": alias.asname,
                            }
                        )

                        imported_names.add(
                            alias.asname
                            or alias.name.split(
                                "."
                            )[-1]
                        )

            elif isinstance(
                node,
                ast.ImportFrom,
            ):
                module = node.module or ""

                if not module.startswith(
                    CHAT_IMPORT_TOKENS
                ):
                    continue

                for alias in node.names:
                    imports.append(
                        {
                            "line": node.lineno,
                            "module": module,
                            "name": alias.name,
                            "alias": alias.asname,
                        }
                    )

                    imported_names.add(
                        alias.asname
                        or alias.name
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

            name = dotted_name(
                node.func
            )

            if not name:
                continue

            root_name = name.split(
                "."
            )[0]

            if root_name not in imported_names:
                continue

            calls.append(
                {
                    "line": node.lineno,
                    "call": name,
                    "enclosing_symbol": (
                        enclosing_symbol(
                            tree,
                            node,
                        )
                    ),
                    "source_line": source_line(
                        source,
                        node.lineno,
                    ),
                }
            )

        consumers.append(
            {
                "path": relative(
                    path
                ),
                "is_test": is_test_path(
                    path
                ),
                "imports": imports,
                "calls": calls,
                "route_owner": bool(
                    inspect_routes(
                        path
                    )
                ),
            }
        )

    return consumers


def source_manifest() -> dict[str, Any]:
    entries = []

    for path in python_files(
        BACKEND_ROOT
    ):
        entries.append(
            {
                "path": relative(
                    path
                ),
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
        "chat_public stack missing"
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

    batch3_evidence = load_json(
        BATCH3_EVIDENCE
    )

    batch3_freeze = load_json(
        BATCH3_FREEZE
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

    assert batch2[
        "status"
    ] == "completed"

    assert batch3[
        "status"
    ] == "completed"

    assert batch3[
        "mode"
    ] == "read_only"

    assert batch3[
        "chat_public"
    ][
        "public_deployment_authorized"
    ] is False

    assert batch3_freeze[
        "status"
    ] == "frozen"

    previous = batch3_evidence[
        "chat_public"
    ]

    assert len(
        previous[
            "direct_persistence_imports"
        ]
    ) == 2

    assert len(
        previous[
            "mutation_calls"
        ]
    ) == 4

    assert len(
        previous[
            "dynamic_execution_calls"
        ]
    ) == 2

    assert previous[
        "production_consumer_count"
    ] == 2

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

    chat_files = python_files(
        CHAT_ROOT
    )

    all_imports = []

    all_calls = []

    all_routes = []

    for path in chat_files:
        all_imports.extend(
            inspect_imports(
                path
            )
        )

        all_calls.extend(
            inspect_calls(
                path
            )
        )

        all_routes.extend(
            inspect_routes(
                path
            )
        )

    direct_imports = [
        item
        for item in all_imports
        if item[
            "direct_persistence"
        ]
    ]

    direct_import_names = {
        item.get(
            "alias"
        )
        or item.get(
            "name"
        )
        or item[
            "module"
        ].split(
            "."
        )[-1]
        for item in direct_imports
    }

    persistence_dispositions = [
        classify_persistence_import(
            item,
            all_calls,
        )
        for item in direct_imports
    ]

    mutation_candidates = [
        call
        for call in all_calls
        if call.terminal
        in MUTATION_TERMINALS
    ]

    mutation_dispositions = [
        classify_mutation_call(
            call,
            direct_import_names,
        )
        for call in mutation_candidates
    ]

    dynamic_candidates = [
        call
        for call in all_calls
        if call.terminal
        in DYNAMIC_TERMINALS
    ]

    dynamic_dispositions = [
        classify_dynamic_call(
            call
        )
        for call in dynamic_candidates
    ]

    consumers = inspect_consumers()

    production_consumers = [
        item
        for item in consumers
        if not item[
            "is_test"
        ]
    ]

    confirmed_boundary_defects = [
        item
        for item in (
            persistence_dispositions
            + mutation_dispositions
        )
        if item[
            "classification"
        ]
        == "CONFIRMED_BOUNDARY_DEFECT"
    ]

    confirmed_mutation_capabilities = [
        item
        for item in mutation_dispositions
        if item[
            "classification"
        ]
        == "CONFIRMED_MUTATION_CAPABILITY"
    ]

    confirmed_dynamic_execution = [
        item
        for item in dynamic_dispositions
        if item[
            "classification"
        ]
        == "CONFIRMED_DYNAMIC_EXECUTION"
    ]

    false_positives = [
        item
        for item in (
            mutation_dispositions
            + dynamic_dispositions
        )
        if item[
            "classification"
        ]
        == "SCANNER_FALSE_POSITIVE"
    ]

    acceptable_local_operations = [
        item
        for item in mutation_dispositions
        if item[
            "classification"
        ]
        == "ACCEPTABLE_LOCAL_STATE_OPERATION"
    ]

    unresolved_dispositions = [
        item
        for item in (
            persistence_dispositions
            + mutation_dispositions
            + dynamic_dispositions
        )
        if item[
            "classification"
        ]
        == "REQUIRES_TARGETED_REMEDIATION"
    ]

    chat_owns_routes = bool(
        all_routes
    )

    consumer_route_owners = [
        item[
            "path"
        ]
        for item in production_consumers
        if item[
            "route_owner"
        ]
    ]

    if (
        confirmed_mutation_capabilities
        or confirmed_dynamic_execution
    ):
        remediation_priority = (
            "IMMEDIATE"
        )

    elif confirmed_boundary_defects:
        remediation_priority = (
            "HIGH"
        )

    elif unresolved_dispositions:
        remediation_priority = (
            "MEDIUM"
        )

    else:
        remediation_priority = (
            "LOW"
        )

    production_source_remediation_authorized = bool(
        confirmed_boundary_defects
        or confirmed_mutation_capabilities
        or confirmed_dynamic_execution
    )

    recommended_changes = []

    if persistence_dispositions:
        recommended_changes.append(
            {
                "order": 1,
                "change": (
                    "Move direct persistence ownership out of "
                    "chat_public and behind a narrow approved "
                    "read/service facade."
                ),
                "required": True,
            }
        )

    if confirmed_mutation_capabilities:
        recommended_changes.append(
            {
                "order": 2,
                "change": (
                    "Remove trading, broker or persistent mutation "
                    "capability from chat_public."
                ),
                "required": True,
            }
        )

    if confirmed_dynamic_execution:
        recommended_changes.append(
            {
                "order": 3,
                "change": (
                    "Remove dynamic code execution or replace it "
                    "with a strict allowlisted dispatcher."
                ),
                "required": True,
            }
        )

    if unresolved_dispositions:
        recommended_changes.append(
            {
                "order": 4,
                "change": (
                    "Resolve remaining receiver ambiguity with "
                    "focused tests before editing runtime behavior."
                ),
                "required": True,
            }
        )

    recommended_changes.append(
        {
            "order": 5,
            "change": (
                "Add focused chat_public contract, failure, "
                "timeout, rate-limit and safety-policy tests."
            ),
            "required": True,
        }
    )

    recommended_changes.append(
        {
            "order": 6,
            "change": (
                "Re-run Batch 3 qualification and the "
                "implementation-state-aware re-grade."
            ),
            "required": True,
        }
    )

    manifest = source_manifest()

    evidence = {
        "status": "completed",
        "generated_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "chat_files": [
            relative(
                path
            )
            for path in chat_files
        ],
        "direct_persistence_imports": (
            persistence_dispositions
        ),
        "mutation_dispositions": (
            mutation_dispositions
        ),
        "dynamic_execution_dispositions": (
            dynamic_dispositions
        ),
        "routes_owned_by_chat_public": (
            all_routes
        ),
        "consumers": consumers,
        "production_consumers": (
            production_consumers
        ),
        "consumer_route_owners": (
            consumer_route_owners
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
        "batch": "IQC-REM-003A",
        "batch_name": (
            "chat_public Persistence, Mutation, "
            "and Dynamic-Execution Disposition"
        ),
        "status": "completed",
        "verified_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "batch1_verified": True,
        "batch2_verified": True,
        "batch3_verified": True,
        "flow_baseline": {
            "backend_tests_passed": (
                batch1[
                    "whole_backend_tests"
                ][
                    "passed"
                ]
            ),
            "backend_tests_failed": 0,
            "unresolved_imports": 0,
            "dependency_cycles": 0,
        },
        "chat_public": {
            "implementation_state": (
                batch3[
                    "chat_public"
                ][
                    "implementation_state"
                ]
            ),
            "previous_disposition": (
                batch3[
                    "chat_public"
                ][
                    "disposition"
                ]
            ),
            "chat_owns_api_routes": (
                chat_owns_routes
            ),
            "chat_route_count": len(
                all_routes
            ),
            "production_consumer_count": len(
                production_consumers
            ),
            "consumer_route_owner_count": len(
                consumer_route_owners
            ),
        },
        "disposition_counts": {
            "direct_persistence_imports": len(
                persistence_dispositions
            ),
            "mutation_candidates": len(
                mutation_dispositions
            ),
            "dynamic_execution_candidates": len(
                dynamic_dispositions
            ),
            "confirmed_boundary_defects": len(
                confirmed_boundary_defects
            ),
            "confirmed_mutation_capabilities": len(
                confirmed_mutation_capabilities
            ),
            "confirmed_dynamic_execution": len(
                confirmed_dynamic_execution
            ),
            "scanner_false_positives": len(
                false_positives
            ),
            "acceptable_local_state_operations": len(
                acceptable_local_operations
            ),
            "unresolved_dispositions": len(
                unresolved_dispositions
            ),
        },
        "remediation": {
            "priority": (
                remediation_priority
            ),
            "production_source_remediation_authorized": (
                production_source_remediation_authorized
            ),
            "public_deployment_authorized": False,
            "recommended_changes": (
                recommended_changes
            ),
        },
        "source_modified": False,
        "database_modified": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
        "next_step": (
            "IQC Remediation Batch 3B — "
            "chat_public Boundary Remediation "
            "or Focused Evidence Qualification"
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
        "batch": "IQC-REM-003A",
        "frozen_at": datetime.now(
            UTC
        ).isoformat(),
        "report_sha256": (
            report_hash
        ),
        "evidence_sha256": (
            evidence_hash
        ),
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
            "IQC REMEDIATION BATCH 3A — CHAT_PUBLIC "
            "PERSISTENCE, MUTATION, AND DYNAMIC-EXECUTION DISPOSITION"
        ),
        "=" * 96,
        "",
        "STATUS",
        "COMPLETE AND VERIFIED",
        "",
        "MODE",
        "READ ONLY",
        "",
        "FLOW BASELINE",
        (
            "Backend tests passed:                 "
            f"{batch1['whole_backend_tests']['passed']}"
        ),
        "Backend tests failed:                 0",
        "Unresolved imports:                   0",
        "Dependency cycles:                    0",
        "",
        "CHAT_PUBLIC OWNERSHIP",
        (
            "Own API routes:                       "
            f"{'YES' if chat_owns_routes else 'NO'}"
        ),
        (
            "Owned route count:                    "
            f"{len(all_routes)}"
        ),
        (
            "Production consumers:                 "
            f"{len(production_consumers)}"
        ),
        (
            "Consumer route owners:                "
            f"{len(consumer_route_owners)}"
        ),
        "",
        "EXACT DISPOSITION COUNTS",
        (
            "Direct persistence imports:           "
            f"{len(persistence_dispositions)}"
        ),
        (
            "Mutation candidates:                  "
            f"{len(mutation_dispositions)}"
        ),
        (
            "Dynamic-execution candidates:         "
            f"{len(dynamic_dispositions)}"
        ),
        (
            "Confirmed boundary defects:           "
            f"{len(confirmed_boundary_defects)}"
        ),
        (
            "Confirmed mutation capabilities:      "
            f"{len(confirmed_mutation_capabilities)}"
        ),
        (
            "Confirmed dynamic execution:          "
            f"{len(confirmed_dynamic_execution)}"
        ),
        (
            "Scanner false positives:              "
            f"{len(false_positives)}"
        ),
        (
            "Acceptable local-state operations:    "
            f"{len(acceptable_local_operations)}"
        ),
        (
            "Still requiring remediation review:   "
            f"{len(unresolved_dispositions)}"
        ),
        "",
        "PERSISTENCE IMPORT DISPOSITIONS",
    ]

    for index, item in enumerate(
        persistence_dispositions,
        start=1,
    ):
        lines.extend(
            [
                (
                    f"{index}. {item['path']}:{item['line']}"
                ),
                (
                    f"   Import: {item['source_line']}"
                ),
                (
                    f"   Classification: "
                    f"{item['classification']}"
                ),
                (
                    f"   Disposition: "
                    f"{item['disposition']}"
                ),
            ]
        )

    lines.extend(
        [
            "",
            "MUTATION CALL DISPOSITIONS",
        ]
    )

    for index, item in enumerate(
        mutation_dispositions,
        start=1,
    ):
        lines.extend(
            [
                (
                    f"{index}. {item['path']}:{item['line']} "
                    f"{item['rendered_call']}"
                ),
                (
                    f"   Scope: {item['enclosing_symbol']}"
                ),
                (
                    f"   Classification: "
                    f"{item['classification']}"
                ),
                (
                    f"   Disposition: "
                    f"{item['disposition']}"
                ),
            ]
        )

    lines.extend(
        [
            "",
            "DYNAMIC-EXECUTION DISPOSITIONS",
        ]
    )

    for index, item in enumerate(
        dynamic_dispositions,
        start=1,
    ):
        lines.extend(
            [
                (
                    f"{index}. {item['path']}:{item['line']} "
                    f"{item['rendered_call']}"
                ),
                (
                    f"   Scope: {item['enclosing_symbol']}"
                ),
                (
                    f"   Classification: "
                    f"{item['classification']}"
                ),
                (
                    f"   Disposition: "
                    f"{item['disposition']}"
                ),
            ]
        )

    lines.extend(
        [
            "",
            "REMEDIATION",
            (
                "Priority:                            "
                f"{remediation_priority}"
            ),
            (
                "Production source remediation:       "
                f"{'AUTHORIZED' if production_source_remediation_authorized else 'NOT AUTHORIZED'}"
            ),
            "Public deployment authorized:          NO",
            "",
            "SAFETY",
            "- Production Auth available: NO",
            "- SnapTrade access authorized: NO",
            "- Broker execution enabled: NO",
            "- Live trading enabled: NO",
            "- Source modified: NO",
            "- Database modified: NO",
            "",
            "NEXT",
            (
                "IQC Remediation Batch 3B — "
                "chat_public Boundary Remediation "
                "or Focused Evidence Qualification"
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

    print(
        rendered
    )

    print(
        "Disposition report:"
    )

    print(
        REPORT_JSON
    )

    print()

    print(
        "Detailed evidence:"
    )

    print(
        EVIDENCE_JSON
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
