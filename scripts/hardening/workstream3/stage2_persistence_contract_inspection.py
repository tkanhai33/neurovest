#!/usr/bin/env python3

"""
NeuroVest Workstream 3
Stage 2 — Canonical Persistence Ownership, Transaction Boundary,
and Append-Only Contract Inspection

READ ONLY.

This inspection corrects Stage 1 heuristic false positives by using
AST-level semantic classification.

It identifies:

- actual SQLAlchemy DeclarativeBase definitions
- declarative_base() calls
- actual engine definitions
- actual sessionmaker/async_sessionmaker definitions
- ORM model ownership
- real AsyncSession/Session transaction scopes
- commit, rollback, flush, refresh, execute, add, merge, delete
- SQLAlchemy insert/update/delete statements
- in-memory collection mutations that must not be counted as DB writes
- append-only persistence candidates
- destructive database mutation candidates
- transaction-boundary safety
- persistence ownership and composition disposition

It does not:

- import backend application modules
- connect to a database
- create tables
- issue SQL
- modify backend source
- enable broker execution
- enable live trading
"""

from __future__ import annotations

import ast
import hashlib
import json
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(".").resolve()

BACKEND_ROOT = (
    ROOT
    / "backend"
    / "app"
)

MAIN_FILE = (
    BACKEND_ROOT
    / "main.py"
)

OUTPUT_DIR = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream3"
    / "stage2"
)

HISTORY_DIR = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream3"
    / "history"
)

OUTPUT_JSON = (
    OUTPUT_DIR
    / "stage2_persistence_contract_inspection_latest.json"
)

OUTPUT_TEXT = (
    OUTPUT_DIR
    / "stage2_persistence_contract_inspection_latest.txt"
)

LEDGER_FILE = (
    ROOT
    / "handoff"
    / "hardening"
    / "WORKSTREAM_3_LEDGER.md"
)


SQLALCHEMY_MODULE_PREFIXES = (
    "sqlalchemy",
    "sqlmodel",
)

SESSION_CLASS_NAMES = {
    "Session",
    "AsyncSession",
}

SESSION_FACTORY_CALLS = {
    "sessionmaker",
    "async_sessionmaker",
}

ENGINE_FACTORY_CALLS = {
    "create_engine",
    "create_async_engine",
}

DECLARATIVE_FACTORY_CALLS = {
    "declarative_base",
}

SQL_MUTATION_CALLS = {
    "insert",
    "update",
    "delete",
}

SESSION_METHODS = {
    "add",
    "add_all",
    "merge",
    "delete",
    "execute",
    "flush",
    "refresh",
    "commit",
    "rollback",
    "begin",
    "begin_nested",
    "close",
}

TRANSACTION_BOUNDARY_METHODS = {
    "begin",
    "begin_nested",
    "commit",
    "rollback",
}

READ_METHODS = {
    "execute",
    "scalar",
    "scalars",
    "get",
}

WRITE_METHODS = {
    "add",
    "add_all",
    "merge",
    "delete",
    "flush",
    "commit",
}

APPEND_ONLY_NAMES = {
    "append",
    "record",
    "record_event",
    "record_decision",
    "append_event",
    "append_record",
    "write_event",
    "create_event",
    "log_event",
    "log_decision",
    "capture",
    "store_evidence",
}

DESTRUCTIVE_NAMES = {
    "delete",
    "remove",
    "purge",
    "truncate",
    "drop",
    "drop_all",
    "clear",
}

IDEMPOTENCY_MARKERS = {
    "idempotency_key",
    "deduplication_key",
    "request_id",
    "correlation_id",
    "event_id",
    "decision_id",
    "unique",
    "uniqueconstraint",
}

CHAIN_INTEGRITY_MARKERS = {
    "previous_hash",
    "content_hash",
    "record_hash",
    "event_hash",
    "hash_chain",
    "sequence_id",
    "sequence_number",
}

IMMUTABILITY_MARKERS = {
    "append_only",
    "append-only",
    "immutable",
    "immutability",
    "no update",
    "no delete",
}

TIMESTAMP_MARKERS = {
    "created_at",
    "recorded_at",
    "occurred_at",
    "timestamp",
}

PERSISTENCE_KEYWORDS = {
    "database",
    "db_runtime",
    "db_model",
    "persistence",
    "repository",
    "ledger",
    "journal",
    "audit",
    "history",
    "event_store",
    "conversation_store",
    "reconciliation",
    "research_loader",
    "ingestor",
}


@dataclass(frozen=True)
class ImportBinding:
    local_name: str
    qualified_name: str


def sha256_file(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def module_name(
    path: Path,
) -> str:
    relative = path.relative_to(
        ROOT
    ).with_suffix("")

    parts = list(
        relative.parts
    )

    if parts[-1] == "__init__":
        parts = parts[:-1]

    return ".".join(
        parts
    )


def dotted_name(
    node: ast.AST | None,
) -> str | None:
    if node is None:
        return None

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
                parent
                + "."
                + node.attr
            )

        return node.attr

    return None


def terminal_name(
    value: str | None,
) -> str | None:
    if not value:
        return None

    return value.rsplit(
        ".",
        1,
    )[-1]


def source_segment(
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


def import_bindings(
    tree: ast.AST,
) -> dict[str, str]:
    bindings: dict[str, str] = {}

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                local_name = (
                    alias.asname
                    or alias.name.split(
                        "."
                    )[0]
                )

                bindings[
                    local_name
                ] = alias.name

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            if node.module is None:
                continue

            for alias in node.names:
                local_name = (
                    alias.asname
                    or alias.name
                )

                bindings[
                    local_name
                ] = (
                    node.module
                    + "."
                    + alias.name
                )

    return bindings


def resolve_name(
    name: str | None,
    bindings: dict[str, str],
) -> str | None:
    if not name:
        return None

    first, *rest = name.split(
        "."
    )

    if first not in bindings:
        return name

    resolved = bindings[
        first
    ]

    if rest:
        resolved += (
            "."
            + ".".join(
                rest
            )
        )

    return resolved


def assignment_names(
    node: ast.Assign | ast.AnnAssign,
) -> list[str]:
    targets: list[ast.AST] = []

    if isinstance(
        node,
        ast.Assign,
    ):
        targets.extend(
            node.targets
        )
    else:
        targets.append(
            node.target
        )

    names: list[str] = []

    for target in targets:
        if isinstance(
            target,
            ast.Name,
        ):
            names.append(
                target.id
            )

        elif isinstance(
            target,
            (
                ast.Tuple,
                ast.List,
            ),
        ):
            for element in target.elts:
                if isinstance(
                    element,
                    ast.Name,
                ):
                    names.append(
                        element.id
                    )

    return names


def class_tablename(
    node: ast.ClassDef,
) -> str | None:
    for statement in node.body:
        if not isinstance(
            statement,
            (
                ast.Assign,
                ast.AnnAssign,
            ),
        ):
            continue

        names = assignment_names(
            statement
        )

        if "__tablename__" not in names:
            continue

        value = statement.value

        if (
            isinstance(
                value,
                ast.Constant,
            )
            and isinstance(
                value.value,
                str,
            )
        ):
            return value.value

    return None


def class_columns(
    node: ast.ClassDef,
    source: str,
    bindings: dict[str, str],
) -> list[dict[str, Any]]:
    columns: list[
        dict[str, Any]
    ] = []

    for statement in node.body:
        if not isinstance(
            statement,
            (
                ast.Assign,
                ast.AnnAssign,
            ),
        ):
            continue

        names = assignment_names(
            statement
        )

        if not names:
            continue

        value = statement.value

        if not isinstance(
            value,
            ast.Call,
        ):
            continue

        call = resolve_name(
            dotted_name(
                value.func
            ),
            bindings,
        )

        terminal = terminal_name(
            call
        )

        if terminal not in {
            "Column",
            "mapped_column",
            "Field",
        }:
            continue

        rendered = source_segment(
            source,
            value,
        ).lower()

        columns.append(
            {
                "name": names[0],
                "line": statement.lineno,
                "call": call,
                "primary_key": (
                    "primary_key=true"
                    in rendered.replace(
                        " ",
                        ""
                    )
                ),
                "unique": (
                    "unique=true"
                    in rendered.replace(
                        " ",
                        ""
                    )
                ),
                "nullable_false": (
                    "nullable=false"
                    in rendered.replace(
                        " ",
                        ""
                    )
                ),
                "source": source_segment(
                    source,
                    statement,
                )[:500],
            }
        )

    return columns


def function_arguments(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[str]:
    arguments: list[str] = []

    for argument in (
        list(
            node.args.posonlyargs
        )
        + list(
            node.args.args
        )
        + list(
            node.args.kwonlyargs
        )
    ):
        arguments.append(
            argument.arg
        )

    if node.args.vararg:
        arguments.append(
            node.args.vararg.arg
        )

    if node.args.kwarg:
        arguments.append(
            node.args.kwarg.arg
        )

    return arguments


def annotation_name(
    node: ast.AST | None,
    bindings: dict[str, str],
) -> str | None:
    rendered = dotted_name(
        node
    )

    if rendered:
        return resolve_name(
            rendered,
            bindings,
        )

    if isinstance(
        node,
        ast.Subscript,
    ):
        return resolve_name(
            dotted_name(
                node.value
            ),
            bindings,
        )

    if isinstance(
        node,
        ast.BinOp,
    ):
        return (
            annotation_name(
                node.left,
                bindings,
            )
            or annotation_name(
                node.right,
                bindings,
            )
        )

    return None


def function_session_names(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    bindings: dict[str, str],
) -> set[str]:
    names: set[str] = set()

    all_args = (
        list(
            node.args.posonlyargs
        )
        + list(
            node.args.args
        )
        + list(
            node.args.kwonlyargs
        )
    )

    for argument in all_args:
        annotation = annotation_name(
            argument.annotation,
            bindings,
        )

        if terminal_name(
            annotation
        ) in SESSION_CLASS_NAMES:
            names.add(
                argument.arg
            )

        elif argument.arg in {
            "session",
            "db",
            "database_session",
        }:
            names.add(
                argument.arg
            )

    for nested in ast.walk(
        node
    ):
        if not isinstance(
            nested,
            (
                ast.With,
                ast.AsyncWith,
            ),
        ):
            continue

        for item in nested.items:
            expression = item.context_expr

            if not isinstance(
                expression,
                ast.Call,
            ):
                continue

            called = terminal_name(
                resolve_name(
                    dotted_name(
                        expression.func
                    ),
                    bindings,
                )
            )

            if called not in {
                "async_session",
                "session",
                "session_factory",
                "get_session",
            }:
                continue

            optional = item.optional_vars

            if isinstance(
                optional,
                ast.Name,
            ):
                names.add(
                    optional.id
                )

    return names


def imported_backend_modules(
    tree: ast.AST,
) -> set[str]:
    discovered: set[str] = set()

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                if alias.name.startswith(
                    "backend.app"
                ):
                    discovered.add(
                        alias.name
                    )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            if (
                node.module
                and node.module.startswith(
                    "backend.app"
                )
            ):
                discovered.add(
                    node.module
                )

    return discovered


def find_reachable(
    graph: dict[str, set[str]],
    root: str,
) -> set[str]:
    reachable: set[str] = set()
    queue: deque[str] = deque(
        [root]
    )

    while queue:
        current = queue.popleft()

        if current in reachable:
            continue

        reachable.add(
            current
        )

        for dependency in graph.get(
            current,
            set(),
        ):
            if dependency not in reachable:
                queue.append(
                    dependency
                )

    return reachable


def inspect_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    *,
    source: str,
    bindings: dict[str, str],
) -> dict[str, Any]:
    session_names = function_session_names(
        node,
        bindings,
    )

    calls: list[
        dict[str, Any]
    ] = []

    sql_mutations: list[
        dict[str, Any]
    ] = []

    in_memory_mutations: list[
        dict[str, Any]
    ] = []

    transaction_methods: list[
        str
    ] = []

    session_reads: list[
        dict[str, Any]
    ] = []

    session_writes: list[
        dict[str, Any]
    ] = []

    rollback_present = False
    commit_present = False
    explicit_begin_present = False
    nested_begin_present = False

    try_count = 0
    except_count = 0

    for nested in ast.walk(
        node
    ):
        if isinstance(
            nested,
            ast.Try,
        ):
            try_count += 1
            except_count += len(
                nested.handlers
            )

        if not isinstance(
            nested,
            ast.Call,
        ):
            continue

        raw_call = dotted_name(
            nested.func
        )

        resolved_call = resolve_name(
            raw_call,
            bindings,
        )

        terminal = terminal_name(
            resolved_call
        )

        receiver = None

        if isinstance(
            nested.func,
            ast.Attribute,
        ):
            receiver = dotted_name(
                nested.func.value
            )

        record = {
            "call": resolved_call,
            "receiver": receiver,
            "terminal": terminal,
            "line": nested.lineno,
            "source": source_segment(
                source,
                nested,
            )[:500],
        }

        calls.append(
            record
        )

        if terminal in SQL_MUTATION_CALLS:
            if (
                resolved_call
                and any(
                    resolved_call.startswith(
                        prefix
                    )
                    for prefix in SQLALCHEMY_MODULE_PREFIXES
                )
            ):
                sql_mutations.append(
                    record
                )

        receiver_root = (
            receiver.split(
                "."
            )[0]
            if receiver
            else None
        )

        is_session_call = (
            receiver_root
            in session_names
        )

        if is_session_call:
            if terminal in SESSION_METHODS:
                transaction_methods.append(
                    terminal
                )

            if terminal in READ_METHODS:
                session_reads.append(
                    record
                )

            if terminal in WRITE_METHODS:
                session_writes.append(
                    record
                )

            if terminal == "rollback":
                rollback_present = True

            elif terminal == "commit":
                commit_present = True

            elif terminal == "begin":
                explicit_begin_present = True

            elif terminal == "begin_nested":
                nested_begin_present = True

        elif terminal in {
            "add",
            "remove",
            "discard",
            "append",
            "extend",
            "clear",
        }:
            in_memory_mutations.append(
                record
            )

    function_source = source_segment(
        source,
        node,
    )

    lowered_source = function_source.lower()

    name_lower = node.name.lower()

    likely_append_only = (
        node.name
        in APPEND_ONLY_NAMES
        or any(
            marker in name_lower
            for marker in (
                "append",
                "record",
                "event",
                "audit",
                "ledger",
                "journal",
                "evidence",
                "decision",
            )
        )
    ) and bool(
        session_writes
        or sql_mutations
    )

    destructive = (
        any(
            marker in name_lower
            for marker in DESTRUCTIVE_NAMES
        )
        or any(
            record[
                "terminal"
            ] == "delete"
            for record in session_writes
        )
        or any(
            record[
                "terminal"
            ] in {
                "update",
                "delete",
            }
            for record in sql_mutations
        )
    )

    return {
        "name": node.name,
        "line": node.lineno,
        "end_line": node.end_lineno,
        "async": isinstance(
            node,
            ast.AsyncFunctionDef,
        ),
        "arguments": function_arguments(
            node
        ),
        "session_variables": sorted(
            session_names
        ),
        "session_reads": session_reads,
        "session_writes": session_writes,
        "sql_mutations": sql_mutations,
        "in_memory_mutations": (
            in_memory_mutations
        ),
        "transaction_methods": sorted(
            set(
                transaction_methods
            )
        ),
        "explicit_begin": explicit_begin_present,
        "nested_begin": nested_begin_present,
        "commit_present": commit_present,
        "rollback_present": rollback_present,
        "try_count": try_count,
        "except_count": except_count,
        "likely_append_only": likely_append_only,
        "destructive": destructive,
        "idempotency_markers": sorted(
            marker
            for marker in IDEMPOTENCY_MARKERS
            if marker in lowered_source
        ),
        "chain_integrity_markers": sorted(
            marker
            for marker in CHAIN_INTEGRITY_MARKERS
            if marker in lowered_source
        ),
        "immutability_markers": sorted(
            marker
            for marker in IMMUTABILITY_MARKERS
            if marker in lowered_source
        ),
    }


def inspect_file(
    path: Path,
) -> dict[str, Any]:
    source = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    relative = path.relative_to(
        ROOT
    ).as_posix()

    result: dict[str, Any] = {
        "path": relative,
        "module": module_name(
            path
        ),
        "sha256": sha256_file(
            path
        ),
        "size_bytes": path.stat().st_size,
        "syntax_error": None,
        "imports": [],
        "declarative_bases": [],
        "engine_definitions": [],
        "session_factories": [],
        "orm_models": [],
        "functions": [],
        "sqlalchemy_imported": False,
        "persistence_candidate": False,
    }

    try:
        tree = ast.parse(
            source,
            filename=str(
                path
            ),
        )

    except SyntaxError as exc:
        result[
            "syntax_error"
        ] = {
            "line": exc.lineno,
            "column": exc.offset,
            "message": exc.msg,
        }

        return result

    bindings = import_bindings(
        tree
    )

    result[
        "imports"
    ] = sorted(
        imported_backend_modules(
            tree
        )
    )

    result[
        "sqlalchemy_imported"
    ] = any(
        qualified.startswith(
            SQLALCHEMY_MODULE_PREFIXES
        )
        for qualified in bindings.values()
    )

    declared_base_names: set[
        str
    ] = set()

    for node in tree.body:
        if isinstance(
            node,
            ast.ClassDef,
        ):
            resolved_bases = [
                resolve_name(
                    dotted_name(
                        base
                    ),
                    bindings,
                )
                for base in node.bases
            ]

            if any(
                terminal_name(
                    base
                ) == "DeclarativeBase"
                for base in resolved_bases
            ):
                result[
                    "declarative_bases"
                ].append(
                    {
                        "name": node.name,
                        "kind": (
                            "DeclarativeBase subclass"
                        ),
                        "line": node.lineno,
                        "resolved_bases": (
                            resolved_bases
                        ),
                    }
                )

                declared_base_names.add(
                    node.name
                )

        if isinstance(
            node,
            (
                ast.Assign,
                ast.AnnAssign,
            ),
        ):
            names = assignment_names(
                node
            )

            value = node.value

            if not isinstance(
                value,
                ast.Call,
            ):
                continue

            resolved_call = resolve_name(
                dotted_name(
                    value.func
                ),
                bindings,
            )

            terminal = terminal_name(
                resolved_call
            )

            if terminal in DECLARATIVE_FACTORY_CALLS:
                for name in names:
                    result[
                        "declarative_bases"
                    ].append(
                        {
                            "name": name,
                            "kind": (
                                "declarative_base factory"
                            ),
                            "line": node.lineno,
                            "factory": resolved_call,
                        }
                    )

                    declared_base_names.add(
                        name
                    )

            if terminal in ENGINE_FACTORY_CALLS:
                for name in names:
                    result[
                        "engine_definitions"
                    ].append(
                        {
                            "name": name,
                            "line": node.lineno,
                            "factory": resolved_call,
                            "async": (
                                terminal
                                == "create_async_engine"
                            ),
                        }
                    )

            if terminal in SESSION_FACTORY_CALLS:
                for name in names:
                    result[
                        "session_factories"
                    ].append(
                        {
                            "name": name,
                            "line": node.lineno,
                            "factory": resolved_call,
                            "async": (
                                terminal
                                == "async_sessionmaker"
                            ),
                        }
                    )

    for node in tree.body:
        if not isinstance(
            node,
            ast.ClassDef,
        ):
            continue

        tablename = class_tablename(
            node
        )

        resolved_bases = [
            resolve_name(
                dotted_name(
                    base
                ),
                bindings,
            )
            for base in node.bases
        ]

        orm_by_tablename = (
            tablename is not None
        )

        orm_by_base = any(
            base
            and (
                terminal_name(
                    base
                )
                in declared_base_names
                or terminal_name(
                    base
                ) == "Base"
            )
            for base in resolved_bases
        )

        columns = class_columns(
            node,
            source,
            bindings,
        )

        if (
            orm_by_tablename
            or (
                orm_by_base
                and columns
            )
        ):
            class_source = source_segment(
                source,
                node,
            ).lower()

            result[
                "orm_models"
            ].append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "table": tablename,
                    "resolved_bases": resolved_bases,
                    "columns": columns,
                    "idempotency_markers": sorted(
                        marker
                        for marker
                        in IDEMPOTENCY_MARKERS
                        if marker
                        in class_source
                    ),
                    "chain_integrity_markers": sorted(
                        marker
                        for marker
                        in CHAIN_INTEGRITY_MARKERS
                        if marker
                        in class_source
                    ),
                    "immutability_markers": sorted(
                        marker
                        for marker
                        in IMMUTABILITY_MARKERS
                        if marker
                        in class_source
                    ),
                    "timestamp_markers": sorted(
                        marker
                        for marker
                        in TIMESTAMP_MARKERS
                        if marker
                        in class_source
                    ),
                }
            )

    for node in tree.body:
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            result[
                "functions"
            ].append(
                inspect_function(
                    node,
                    source=source,
                    bindings=bindings,
                )
            )

    relative_lower = relative.lower()

    result[
        "persistence_candidate"
    ] = (
        result[
            "sqlalchemy_imported"
        ]
        or bool(
            result[
                "declarative_bases"
            ]
        )
        or bool(
            result[
                "engine_definitions"
            ]
        )
        or bool(
            result[
                "session_factories"
            ]
        )
        or bool(
            result[
                "orm_models"
            ]
        )
        or any(
            keyword
            in relative_lower
            for keyword
            in PERSISTENCE_KEYWORDS
        )
        or any(
            function[
                "session_reads"
            ]
            or function[
                "session_writes"
            ]
            or function[
                "sql_mutations"
            ]
            for function
            in result[
                "functions"
            ]
        )
    )

    return result


def primary_disposition(
    item: dict[str, Any],
) -> str:
    if item[
        "declarative_bases"
    ]:
        return (
            "DECLARATIVE_BASE_OWNER"
        )

    if item[
        "engine_definitions"
    ]:
        return (
            "DATABASE_ENGINE_OWNER"
        )

    if item[
        "session_factories"
    ]:
        return (
            "SESSION_FACTORY_OWNER"
        )

    if item[
        "orm_models"
    ]:
        return (
            "ORM_MODEL_OWNER"
        )

    real_writes = [
        function
        for function
        in item[
            "functions"
        ]
        if (
            function[
                "session_writes"
            ]
            or function[
                "sql_mutations"
            ]
        )
    ]

    real_reads = [
        function
        for function
        in item[
            "functions"
        ]
        if function[
            "session_reads"
        ]
    ]

    if real_writes:
        return (
            "DATABASE_WRITE_PATH"
        )

    if real_reads:
        return (
            "DATABASE_READ_PATH"
        )

    if item[
        "sqlalchemy_imported"
    ]:
        return (
            "SQLALCHEMY_SUPPORT_SURFACE"
        )

    return (
        "NON_PERSISTENCE_OR_SUPPORT_SURFACE"
    )


def main() -> int:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    HISTORY_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    LEDGER_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    started_at = datetime.now(
        UTC
    )

    python_files = sorted(
        BACKEND_ROOT.rglob(
            "*.py"
        )
    )

    inventory = [
        inspect_file(
            path
        )
        for path in python_files
    ]

    known_modules = {
        item[
            "module"
        ]
        for item in inventory
    }

    graph: dict[
        str,
        set[str],
    ] = {}

    for item in inventory:
        resolved: set[str] = set()

        for imported in item[
            "imports"
        ]:
            if imported in known_modules:
                resolved.add(
                    imported
                )
                continue

            for candidate in known_modules:
                if candidate.startswith(
                    imported
                    + "."
                ):
                    resolved.add(
                        candidate
                    )

        graph[
            item[
                "module"
            ]
        ] = resolved

    reachable = find_reachable(
        graph,
        module_name(
            MAIN_FILE
        ),
    )

    for item in inventory:
        item[
            "reachable_from_main"
        ] = (
            item[
                "module"
            ]
            in reachable
        )

        item[
            "disposition"
        ] = primary_disposition(
            item
        )

    persistence_inventory = [
        item
        for item in inventory
        if item[
            "persistence_candidate"
        ]
    ]

    declarative_bases = [
        {
            "file": item[
                "path"
            ],
            **base,
        }
        for item in inventory
        for base in item[
            "declarative_bases"
        ]
    ]

    engines = [
        {
            "file": item[
                "path"
            ],
            **engine,
        }
        for item in inventory
        for engine in item[
            "engine_definitions"
        ]
    ]

    session_factories = [
        {
            "file": item[
                "path"
            ],
            **factory,
        }
        for item in inventory
        for factory in item[
            "session_factories"
        ]
    ]

    orm_models = [
        {
            "file": item[
                "path"
            ],
            **model,
        }
        for item in inventory
        for model in item[
            "orm_models"
        ]
    ]

    transaction_paths: list[
        dict[str, Any]
    ] = []

    append_only_candidates: list[
        dict[str, Any]
    ] = []

    destructive_paths: list[
        dict[str, Any]
    ] = []

    false_positive_mutations: list[
        dict[str, Any]
    ] = []

    for item in inventory:
        for function in item[
            "functions"
        ]:
            if (
                function[
                    "session_reads"
                ]
                or function[
                    "session_writes"
                ]
                or function[
                    "sql_mutations"
                ]
                or function[
                    "transaction_methods"
                ]
            ):
                transaction_paths.append(
                    {
                        "file": item[
                            "path"
                        ],
                        "reachable_from_main": item[
                            "reachable_from_main"
                        ],
                        **function,
                    }
                )

            if function[
                "likely_append_only"
            ]:
                append_only_candidates.append(
                    {
                        "file": item[
                            "path"
                        ],
                        "reachable_from_main": item[
                            "reachable_from_main"
                        ],
                        **function,
                    }
                )

            if function[
                "destructive"
            ]:
                destructive_paths.append(
                    {
                        "file": item[
                            "path"
                        ],
                        "reachable_from_main": item[
                            "reachable_from_main"
                        ],
                        **function,
                    }
                )

            if (
                function[
                    "in_memory_mutations"
                ]
                and not function[
                    "session_writes"
                ]
                and not function[
                    "sql_mutations"
                ]
            ):
                false_positive_mutations.append(
                    {
                        "file": item[
                            "path"
                        ],
                        "function": function[
                            "name"
                        ],
                        "line": function[
                            "line"
                        ],
                        "calls": function[
                            "in_memory_mutations"
                        ],
                    }
                )

    model_append_only_candidates = [
        model
        for model in orm_models
        if (
            model[
                "idempotency_markers"
            ]
            or model[
                "chain_integrity_markers"
            ]
            or model[
                "immutability_markers"
            ]
        )
    ]

    timestamp_only_models = [
        model
        for model in orm_models
        if (
            model[
                "timestamp_markers"
            ]
            and not model[
                "idempotency_markers"
            ]
            and not model[
                "chain_integrity_markers"
            ]
            and not model[
                "immutability_markers"
            ]
        )
    ]

    transaction_without_rollback = [
        path
        for path in transaction_paths
        if (
            path[
                "session_writes"
            ]
            and path[
                "commit_present"
            ]
            and not path[
                "rollback_present"
            ]
            and path[
                "except_count"
            ] == 0
        )
    ]

    transaction_with_begin = [
        path
        for path in transaction_paths
        if (
            path[
                "explicit_begin"
            ]
            or path[
                "nested_begin"
            ]
        )
    ]

    syntax_errors = [
        {
            "path": item[
                "path"
            ],
            **item[
                "syntax_error"
            ],
        }
        for item in inventory
        if item[
            "syntax_error"
        ]
    ]

    blockers: list[
        dict[str, Any]
    ] = []

    if len(
        declarative_bases
    ) != 1:
        blockers.append(
            {
                "code": (
                    "DECLARATIVE_BASE_OWNERSHIP_AMBIGUOUS"
                ),
                "message": (
                    "Expected exactly one semantic SQLAlchemy "
                    "declarative Base definition, found "
                    f"{len(declarative_bases)}."
                ),
                "evidence": declarative_bases,
            }
        )

    if len(
        engines
    ) != 1:
        blockers.append(
            {
                "code": (
                    "ENGINE_OWNERSHIP_AMBIGUOUS"
                ),
                "message": (
                    "Expected exactly one semantic SQLAlchemy "
                    "engine definition, found "
                    f"{len(engines)}."
                ),
                "evidence": engines,
            }
        )

    if len(
        session_factories
    ) != 1:
        blockers.append(
            {
                "code": (
                    "SESSION_FACTORY_OWNERSHIP_AMBIGUOUS"
                ),
                "message": (
                    "Expected exactly one semantic SQLAlchemy "
                    "session factory definition, found "
                    f"{len(session_factories)}."
                ),
                "evidence": session_factories,
            }
        )

    if not orm_models:
        blockers.append(
            {
                "code": (
                    "ORM_MODELS_NOT_DISCOVERED"
                ),
                "message": (
                    "No semantic ORM model declarations "
                    "were discovered."
                ),
                "evidence": [],
            }
        )

    if not model_append_only_candidates:
        blockers.append(
            {
                "code": (
                    "APPEND_ONLY_MODEL_CONTRACT_MISSING"
                ),
                "message": (
                    "No ORM model contains explicit append-only, "
                    "idempotency, uniqueness, or hash-chain "
                    "contract evidence."
                ),
                "evidence": [],
            }
        )

    if syntax_errors:
        blockers.append(
            {
                "code": (
                    "PERSISTENCE_SYNTAX_ERRORS"
                ),
                "message": (
                    "Persistence inspection found syntax errors."
                ),
                "evidence": syntax_errors,
            }
        )

    ownership = {
        "declarative_base_owner": (
            declarative_bases[
                0
            ][
                "file"
            ]
            if len(
                declarative_bases
            )
            == 1
            else None
        ),
        "engine_owner": (
            engines[
                0
            ][
                "file"
            ]
            if len(
                engines
            )
            == 1
            else None
        ),
        "session_factory_owner": (
            session_factories[
                0
            ][
                "file"
            ]
            if len(
                session_factories
            )
            == 1
            else None
        ),
        "model_owner_files": sorted(
            {
                model[
                    "file"
                ]
                for model in orm_models
            }
        ),
    }

    disposition_counts: dict[
        str,
        int,
    ] = defaultdict(
        int
    )

    for item in persistence_inventory:
        disposition_counts[
            item[
                "disposition"
            ]
        ] += 1

    summary = {
        "python_files_scanned": len(
            inventory
        ),
        "persistence_candidates": len(
            persistence_inventory
        ),
        "semantic_declarative_bases": len(
            declarative_bases
        ),
        "semantic_engines": len(
            engines
        ),
        "semantic_session_factories": len(
            session_factories
        ),
        "orm_models": len(
            orm_models
        ),
        "transaction_paths": len(
            transaction_paths
        ),
        "transaction_paths_with_begin": len(
            transaction_with_begin
        ),
        "write_paths_without_rollback_guard": len(
            transaction_without_rollback
        ),
        "append_only_function_candidates": len(
            append_only_candidates
        ),
        "append_only_model_candidates": len(
            model_append_only_candidates
        ),
        "timestamp_only_models": len(
            timestamp_only_models
        ),
        "destructive_paths": len(
            destructive_paths
        ),
        "in_memory_mutation_false_positives": len(
            false_positive_mutations
        ),
        "syntax_errors": len(
            syntax_errors
        ),
        "composition_blockers": len(
            blockers
        ),
    }

    completed_at = datetime.now(
        UTC
    )

    report = {
        "workstream": 3,
        "stage": 2,
        "stage_name": (
            "Canonical Persistence Ownership, "
            "Transaction Boundary, and Append-Only "
            "Contract Inspection"
        ),
        "status": "completed",
        "mode": "read_only",
        "started_at": (
            started_at.isoformat()
        ),
        "completed_at": (
            completed_at.isoformat()
        ),
        "duration_seconds": round(
            (
                completed_at
                - started_at
            ).total_seconds(),
            6,
        ),
        "summary": summary,
        "ownership": ownership,
        "declarative_bases": declarative_bases,
        "engines": engines,
        "session_factories": session_factories,
        "orm_models": orm_models,
        "transaction_paths": transaction_paths,
        "transaction_paths_with_begin": (
            transaction_with_begin
        ),
        "transaction_paths_without_rollback_guard": (
            transaction_without_rollback
        ),
        "append_only_function_candidates": (
            append_only_candidates
        ),
        "append_only_model_candidates": (
            model_append_only_candidates
        ),
        "timestamp_only_models": (
            timestamp_only_models
        ),
        "destructive_paths": destructive_paths,
        "in_memory_mutation_false_positives": (
            false_positive_mutations
        ),
        "composition_blockers": blockers,
        "disposition_counts": dict(
            sorted(
                disposition_counts.items()
            )
        ),
        "inventory": persistence_inventory,
        "safety": {
            "source_modified": False,
            "application_modules_imported": False,
            "database_connected": False,
            "sql_executed": False,
            "tables_created": False,
            "records_written": False,
            "broker_execution_enabled": False,
            "live_trading_enabled": False,
        },
        "recommended_next_stage": (
            "Stage 3 — Canonical Append-Only Decision "
            "Event Contract and Transaction Manager Design"
        ),
    }

    serialized = (
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    OUTPUT_JSON.write_text(
        serialized,
        encoding="utf-8",
    )

    history_name = (
        "stage2_persistence_contract_inspection_"
        + completed_at.strftime(
            "%Y%m%dT%H%M%S.%fZ"
        )
        + ".json"
    )

    (
        HISTORY_DIR
        / history_name
    ).write_text(
        serialized,
        encoding="utf-8",
    )

    lines: list[str] = [
        "=" * 80,
        "NEUROVEST WORKSTREAM 3",
        (
            "STAGE 2 — CANONICAL PERSISTENCE OWNERSHIP, "
            "TRANSACTION BOUNDARY, AND APPEND-ONLY "
            "CONTRACT INSPECTION"
        ),
        "=" * 80,
        "",
        "MODE",
        "READ ONLY",
        "",
        "SUMMARY",
        (
            "Python files scanned:                    "
            f"{summary['python_files_scanned']}"
        ),
        (
            "Persistence candidates:                 "
            f"{summary['persistence_candidates']}"
        ),
        (
            "Semantic DeclarativeBase definitions:   "
            f"{summary['semantic_declarative_bases']}"
        ),
        (
            "Semantic engine definitions:            "
            f"{summary['semantic_engines']}"
        ),
        (
            "Semantic session factories:             "
            f"{summary['semantic_session_factories']}"
        ),
        (
            "ORM models:                             "
            f"{summary['orm_models']}"
        ),
        (
            "Transaction paths:                      "
            f"{summary['transaction_paths']}"
        ),
        (
            "Transaction paths with begin():         "
            f"{summary['transaction_paths_with_begin']}"
        ),
        (
            "Writes lacking rollback guard:          "
            f"{summary['write_paths_without_rollback_guard']}"
        ),
        (
            "Append-only function candidates:        "
            f"{summary['append_only_function_candidates']}"
        ),
        (
            "Append-only model candidates:           "
            f"{summary['append_only_model_candidates']}"
        ),
        (
            "Timestamp-only model candidates:        "
            f"{summary['timestamp_only_models']}"
        ),
        (
            "Destructive persistence paths:          "
            f"{summary['destructive_paths']}"
        ),
        (
            "In-memory mutation false positives:     "
            f"{summary['in_memory_mutation_false_positives']}"
        ),
        (
            "Syntax errors:                          "
            f"{summary['syntax_errors']}"
        ),
        (
            "Composition blockers:                   "
            f"{summary['composition_blockers']}"
        ),
        "",
        "CANONICAL OWNERSHIP",
        (
            "- Declarative Base: "
            + (
                ownership[
                    "declarative_base_owner"
                ]
                or "AMBIGUOUS OR NOT FOUND"
            )
        ),
        (
            "- Engine: "
            + (
                ownership[
                    "engine_owner"
                ]
                or "AMBIGUOUS OR NOT FOUND"
            )
        ),
        (
            "- Session factory: "
            + (
                ownership[
                    "session_factory_owner"
                ]
                or "AMBIGUOUS OR NOT FOUND"
            )
        ),
        "",
        "ORM MODEL OWNERS",
    ]

    for file in ownership[
        "model_owner_files"
    ]:
        lines.append(
            "- "
            + file
        )

    if not ownership[
        "model_owner_files"
    ]:
        lines.append(
            "- None"
        )

    lines.extend(
        [
            "",
            "TRANSACTION BOUNDARIES",
        ]
    )

    if transaction_paths:
        for path in transaction_paths:
            methods = ", ".join(
                path[
                    "transaction_methods"
                ]
            ) or "none"

            lines.append(
                "- "
                + path[
                    "file"
                ]
                + "::"
                + path[
                    "name"
                ]
                + " — "
                + methods
            )

            lines.append(
                "    begin="
                + str(
                    path[
                        "explicit_begin"
                    ]
                )
                + " rollback="
                + str(
                    path[
                        "rollback_present"
                    ]
                )
                + " commit="
                + str(
                    path[
                        "commit_present"
                    ]
                )
            )
    else:
        lines.append(
            "- None"
        )

    lines.extend(
        [
            "",
            "APPEND-ONLY MODEL CONTRACT CANDIDATES",
        ]
    )

    if model_append_only_candidates:
        for model in model_append_only_candidates:
            markers = sorted(
                set(
                    model[
                        "idempotency_markers"
                    ]
                    + model[
                        "chain_integrity_markers"
                    ]
                    + model[
                        "immutability_markers"
                    ]
                )
            )

            lines.append(
                "- "
                + model[
                    "file"
                ]
                + "::"
                + model[
                    "name"
                ]
                + " — "
                + ", ".join(
                    markers
                )
            )
    else:
        lines.append(
            "- None"
        )

    lines.extend(
        [
            "",
            "TIMESTAMP-ONLY FALSE POSITIVE CANDIDATES",
        ]
    )

    if timestamp_only_models:
        for model in timestamp_only_models:
            lines.append(
                "- "
                + model[
                    "file"
                ]
                + "::"
                + model[
                    "name"
                ]
                + " — "
                + ", ".join(
                    model[
                        "timestamp_markers"
                    ]
                )
            )
    else:
        lines.append(
            "- None"
        )

    lines.extend(
        [
            "",
            "IN-MEMORY MUTATION FALSE POSITIVES",
        ]
    )

    if false_positive_mutations:
        for item in false_positive_mutations:
            calls = sorted(
                {
                    call[
                        "source"
                    ]
                    for call
                    in item[
                        "calls"
                    ]
                }
            )

            lines.append(
                "- "
                + item[
                    "file"
                ]
                + "::"
                + item[
                    "function"
                ]
                + " — "
                + "; ".join(
                    calls
                )
            )
    else:
        lines.append(
            "- None"
        )

    lines.extend(
        [
            "",
            "DESTRUCTIVE DATABASE PATHS",
        ]
    )

    if destructive_paths:
        for path in destructive_paths:
            lines.append(
                "- "
                + path[
                    "file"
                ]
                + "::"
                + path[
                    "name"
                ]
            )
    else:
        lines.append(
            "- None"
        )

    lines.extend(
        [
            "",
            "COMPOSITION BLOCKERS",
        ]
    )

    if blockers:
        for blocker in blockers:
            lines.append(
                "- "
                + blocker[
                    "code"
                ]
            )

            lines.append(
                "    "
                + blocker[
                    "message"
                ]
            )
    else:
        lines.append(
            "- None"
        )

    lines.extend(
        [
            "",
            "SAFETY",
            "Source modified:                       NO",
            "Application modules imported:          NO",
            "Database connected:                    NO",
            "SQL executed:                          NO",
            "Tables created:                        NO",
            "Records written:                       NO",
            "Broker execution enabled:              NO",
            "Live trading enabled:                  NO",
            "",
            "NEXT",
            (
                "Stage 3 — Canonical Append-Only Decision "
                "Event Contract and Transaction Manager Design"
            ),
            "",
            "=" * 80,
        ]
    )

    rendered = (
        "\n".join(
            lines
        )
        + "\n"
    )

    OUTPUT_TEXT.write_text(
        rendered,
        encoding="utf-8",
    )

    ledger_marker = (
        "## Stage 2 — Canonical Persistence Ownership, "
        "Transaction Boundary, and Append-Only "
        "Contract Inspection"
    )

    existing_ledger = ""

    if LEDGER_FILE.exists():
        existing_ledger = (
            LEDGER_FILE.read_text(
                encoding="utf-8"
            )
        )

    if ledger_marker not in existing_ledger:
        with LEDGER_FILE.open(
            "a",
            encoding="utf-8",
        ) as ledger:
            ledger.write(
                "\n"
                + ledger_marker
                + "\n"
                "\n"
                f"Inspected: `{completed_at.isoformat()}`\n"
                "\n"
                "- Mode: **READ ONLY**\n"
                "- Semantic DeclarativeBase definitions: "
                f"**{summary['semantic_declarative_bases']}**\n"
                "- Semantic engine definitions: "
                f"**{summary['semantic_engines']}**\n"
                "- Semantic session factories: "
                f"**{summary['semantic_session_factories']}**\n"
                "- ORM models: "
                f"**{summary['orm_models']}**\n"
                "- Transaction paths: "
                f"**{summary['transaction_paths']}**\n"
                "- Append-only model candidates: "
                f"**{summary['append_only_model_candidates']}**\n"
                "- In-memory mutation false positives: "
                f"**{summary['in_memory_mutation_false_positives']}**\n"
                "- Source modified: **NO**\n"
                "- Database connected: **NO**\n"
                "- Records written: **NO**\n"
                "- Broker execution enabled: **NO**\n"
                "- Live trading enabled: **NO**\n"
                "\n"
            )

    print(
        rendered
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
