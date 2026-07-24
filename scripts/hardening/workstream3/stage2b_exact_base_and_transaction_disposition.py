#!/usr/bin/env python3

"""
NeuroVest Workstream 3
Stage 2B — Exact Declarative Base Ownership and Transaction Disposition

READ ONLY.

This inspection:

- identifies every exact SQLAlchemy declarative Base definition
- resolves imported Base aliases across modules
- maps each ORM model to its actual metadata owner
- detects table-name overlap between metadata registries
- determines reachability from backend.app.main
- determines whether each Base owns an engine/session factory
- classifies canonical, legacy, isolated, or competing Base ownership
- inspects the three Stage 2 write paths lacking rollback guards
- determines transaction disposition without modifying source
- determines whether journal_ledger is suitable for the future
  append-only decision-event persistence surface

It does not import application modules, connect to a database,
execute SQL, create tables, write records, or modify backend source.
"""

from __future__ import annotations

import ast
import hashlib
import json
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

MAIN_FILE = (
    BACKEND_ROOT
    / "main.py"
)

OUTPUT_DIR = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream3"
    / "stage2b"
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
    / "stage2b_exact_base_and_transaction_disposition_latest.json"
)

OUTPUT_TEXT = (
    OUTPUT_DIR
    / "stage2b_exact_base_and_transaction_disposition_latest.txt"
)

LEDGER_FILE = (
    ROOT
    / "handoff"
    / "hardening"
    / "WORKSTREAM_3_LEDGER.md"
)

TARGET_TRANSACTION_PATHS = {
    (
        "backend/app/stacks/learning_research/"
        "research_loader.py"
    ): {
        "add_research",
    },
    (
        "backend/app/stacks/market_data/"
        "yfinance_ingestor.py"
    ): {
        "load_full_history",
        "update_live_price",
    },
}

BASE_FACTORY_TERMINALS = {
    "declarative_base",
}

BASE_CLASS_TERMINALS = {
    "DeclarativeBase",
}

ENGINE_FACTORY_TERMINALS = {
    "create_engine",
    "create_async_engine",
}

SESSION_FACTORY_TERMINALS = {
    "sessionmaker",
    "async_sessionmaker",
}

SESSION_TYPE_TERMINALS = {
    "Session",
    "AsyncSession",
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

WRITE_METHODS = {
    "add",
    "add_all",
    "merge",
    "delete",
    "flush",
    "commit",
}

READ_METHODS = {
    "execute",
    "scalar",
    "scalars",
    "get",
}

SQL_MUTATION_TERMINALS = {
    "insert",
    "update",
    "delete",
}


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
    name: str | None,
) -> str | None:
    if not name:
        return None

    return name.rsplit(
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

    for node in tree.body:
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

    resolved = bindings.get(
        first,
        first,
    )

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
    targets: list[ast.AST]

    if isinstance(
        node,
        ast.Assign,
    ):
        targets = list(
            node.targets
        )
    else:
        targets = [
            node.target
        ]

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

        if "__tablename__" not in assignment_names(
            statement
        ):
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


def imported_backend_modules(
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
                if alias.name.startswith(
                    "backend.app"
                ):
                    modules.add(
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
                modules.add(
                    node.module
                )

    return modules


def reachable_modules(
    graph: dict[str, set[str]],
    root: str,
) -> set[str]:
    seen: set[str] = set()

    queue: deque[str] = deque(
        [root]
    )

    while queue:
        current = queue.popleft()

        if current in seen:
            continue

        seen.add(
            current
        )

        queue.extend(
            graph.get(
                current,
                set(),
            )
            - seen
        )

    return seen


def annotation_terminal(
    node: ast.AST | None,
    bindings: dict[str, str],
) -> str | None:
    if node is None:
        return None

    direct = dotted_name(
        node
    )

    if direct:
        return terminal_name(
            resolve_name(
                direct,
                bindings,
            )
        )

    if isinstance(
        node,
        ast.Subscript,
    ):
        return terminal_name(
            resolve_name(
                dotted_name(
                    node.value
                ),
                bindings,
            )
        )

    if isinstance(
        node,
        ast.BinOp,
    ):
        return (
            annotation_terminal(
                node.left,
                bindings,
            )
            or annotation_terminal(
                node.right,
                bindings,
            )
        )

    return None


def function_session_variables(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    bindings: dict[str, str],
) -> set[str]:
    names: set[str] = set()

    arguments = (
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

    for argument in arguments:
        terminal = annotation_terminal(
            argument.annotation,
            bindings,
        )

        if (
            terminal
            in SESSION_TYPE_TERMINALS
        ):
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


def inspect_transaction_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    *,
    source: str,
    bindings: dict[str, str],
) -> dict[str, Any]:
    session_variables = (
        function_session_variables(
            node,
            bindings,
        )
    )

    session_calls: list[
        dict[str, Any]
    ] = []

    sql_mutations: list[
        dict[str, Any]
    ] = []

    writes: list[
        dict[str, Any]
    ] = []

    reads: list[
        dict[str, Any]
    ] = []

    try_count = 0
    except_count = 0
    finally_count = 0
    raises_count = 0

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

            if nested.finalbody:
                finally_count += 1

        elif isinstance(
            nested,
            ast.Raise,
        ):
            raises_count += 1

        if not isinstance(
            nested,
            ast.Call,
        ):
            continue

        raw = dotted_name(
            nested.func
        )

        resolved = resolve_name(
            raw,
            bindings,
        )

        terminal = terminal_name(
            resolved
        )

        receiver = None

        if isinstance(
            nested.func,
            ast.Attribute,
        ):
            receiver = dotted_name(
                nested.func.value
            )

        receiver_root = (
            receiver.split(
                "."
            )[0]
            if receiver
            else None
        )

        record = {
            "line": nested.lineno,
            "call": resolved,
            "receiver": receiver,
            "terminal": terminal,
            "source": source_segment(
                source,
                nested,
            )[:500],
        }

        if (
            receiver_root
            in session_variables
            and terminal
            in SESSION_METHODS
        ):
            session_calls.append(
                record
            )

            if terminal in WRITE_METHODS:
                writes.append(
                    record
                )

            if terminal in READ_METHODS:
                reads.append(
                    record
                )

        if (
            terminal
            in SQL_MUTATION_TERMINALS
            and resolved
            and resolved.startswith(
                "sqlalchemy"
            )
        ):
            sql_mutations.append(
                record
            )

    terminals = {
        call[
            "terminal"
        ]
        for call in session_calls
    }

    function_source = source_segment(
        source,
        node,
    )

    normalized_source = (
        function_source
        .lower()
        .replace(
            " ",
            ""
        )
    )

    uses_context_transaction = (
        ".begin()" in normalized_source
        or ".begin_nested()"
        in normalized_source
    )

    disposition: str

    if not writes and not sql_mutations:
        disposition = (
            "READ_ONLY_TRANSACTION_PATH"
        )

    elif "rollback" in terminals:
        disposition = (
            "EXPLICIT_ROLLBACK_GUARDED_WRITE"
        )

    elif (
        uses_context_transaction
        and "commit"
        not in terminals
    ):
        disposition = (
            "CONTEXT_MANAGED_ATOMIC_WRITE"
        )

    elif (
        "commit" in terminals
        and except_count == 0
    ):
        disposition = (
            "MANUAL_COMMIT_WITHOUT_ROLLBACK_GUARD"
        )

    elif (
        "commit" in terminals
        and except_count > 0
        and "rollback"
        not in terminals
    ):
        disposition = (
            "MANUAL_COMMIT_WITH_EXCEPTION_HANDLER_BUT_NO_ROLLBACK"
        )

    else:
        disposition = (
            "WRITE_PATH_REQUIRES_MANUAL_REVIEW"
        )

    return {
        "name": node.name,
        "line": node.lineno,
        "end_line": node.end_lineno,
        "async": isinstance(
            node,
            ast.AsyncFunctionDef,
        ),
        "session_variables": sorted(
            session_variables
        ),
        "session_calls": session_calls,
        "writes": writes,
        "reads": reads,
        "sql_mutations": sql_mutations,
        "transaction_methods": sorted(
            terminal
            for terminal in terminals
            if terminal
        ),
        "try_count": try_count,
        "except_count": except_count,
        "finally_count": finally_count,
        "raises_count": raises_count,
        "uses_context_transaction": (
            uses_context_transaction
        ),
        "commit_present": (
            "commit"
            in terminals
        ),
        "rollback_present": (
            "rollback"
            in terminals
        ),
        "flush_present": (
            "flush"
            in terminals
        ),
        "disposition": disposition,
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

    record: dict[str, Any] = {
        "path": relative,
        "module": module_name(
            path
        ),
        "sha256": sha256_file(
            path
        ),
        "syntax_error": None,
        "imports": [],
        "bindings": {},
        "base_definitions": [],
        "engines": [],
        "session_factories": [],
        "models": [],
        "functions": [],
    }

    try:
        tree = ast.parse(
            source,
            filename=str(
                path
            ),
        )

    except SyntaxError as exc:
        record[
            "syntax_error"
        ] = {
            "line": exc.lineno,
            "column": exc.offset,
            "message": exc.msg,
        }

        return record

    bindings = import_bindings(
        tree
    )

    record[
        "bindings"
    ] = bindings

    record[
        "imports"
    ] = sorted(
        imported_backend_modules(
            tree
        )
    )

    local_base_names: set[
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
                )
                in BASE_CLASS_TERMINALS
                for base in resolved_bases
            ):
                record[
                    "base_definitions"
                ].append(
                    {
                        "name": node.name,
                        "qualified_name": (
                            record[
                                "module"
                            ]
                            + "."
                            + node.name
                        ),
                        "line": node.lineno,
                        "kind": (
                            "DeclarativeBase subclass"
                        ),
                        "resolved_bases": (
                            resolved_bases
                        ),
                    }
                )

                local_base_names.add(
                    node.name
                )

        if not isinstance(
            node,
            (
                ast.Assign,
                ast.AnnAssign,
            ),
        ):
            continue

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

        if terminal in BASE_FACTORY_TERMINALS:
            for name in names:
                record[
                    "base_definitions"
                ].append(
                    {
                        "name": name,
                        "qualified_name": (
                            record[
                                "module"
                            ]
                            + "."
                            + name
                        ),
                        "line": node.lineno,
                        "kind": (
                            "declarative_base factory"
                        ),
                        "factory": resolved_call,
                    }
                )

                local_base_names.add(
                    name
                )

        elif terminal in ENGINE_FACTORY_TERMINALS:
            for name in names:
                record[
                    "engines"
                ].append(
                    {
                        "name": name,
                        "qualified_name": (
                            record[
                                "module"
                            ]
                            + "."
                            + name
                        ),
                        "line": node.lineno,
                        "factory": resolved_call,
                        "async": (
                            terminal
                            == "create_async_engine"
                        ),
                    }
                )

        elif terminal in SESSION_FACTORY_TERMINALS:
            for name in names:
                record[
                    "session_factories"
                ].append(
                    {
                        "name": name,
                        "qualified_name": (
                            record[
                                "module"
                            ]
                            + "."
                            + name
                        ),
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

        table = class_tablename(
            node
        )

        if table is None:
            continue

        bases = [
            dotted_name(
                base
            )
            for base in node.bases
        ]

        resolved_bases = [
            resolve_name(
                base,
                bindings,
            )
            for base in bases
        ]

        base_reference = None

        for raw, resolved in zip(
            bases,
            resolved_bases,
            strict=False,
        ):
            if (
                terminal_name(
                    resolved
                )
                in local_base_names
            ):
                base_reference = (
                    record[
                        "module"
                    ]
                    + "."
                    + terminal_name(
                        resolved
                    )
                )

                break

            if (
                raw
                and raw.split(
                    "."
                )[0]
                in bindings
                and terminal_name(
                    resolved
                )
                == "Base"
            ):
                base_reference = resolved
                break

            if (
                terminal_name(
                    resolved
                )
                == "Base"
            ):
                base_reference = resolved
                break

        class_source = source_segment(
            source,
            node,
        ).lower()

        record[
            "models"
        ].append(
            {
                "name": node.name,
                "qualified_name": (
                    record[
                        "module"
                    ]
                    + "."
                    + node.name
                ),
                "line": node.lineno,
                "table": table,
                "raw_bases": bases,
                "resolved_bases": (
                    resolved_bases
                ),
                "base_reference": (
                    base_reference
                ),
                "created_at_present": (
                    "created_at"
                    in class_source
                ),
                "timestamp_present": (
                    "timestamp"
                    in class_source
                ),
                "unique_present": (
                    "unique=true"
                    in class_source.replace(
                        " ",
                        ""
                    )
                ),
                "previous_hash_present": (
                    "previous_hash"
                    in class_source
                ),
                "content_hash_present": (
                    "content_hash"
                    in class_source
                ),
                "idempotency_key_present": (
                    "idempotency_key"
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
            record[
                "functions"
            ].append(
                inspect_transaction_function(
                    node,
                    source=source,
                    bindings=bindings,
                )
            )

    return record


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

    files = sorted(
        BACKEND_ROOT.rglob(
            "*.py"
        )
    )

    inventory = [
        inspect_file(
            path
        )
        for path in files
    ]

    syntax_errors = [
        {
            "file": item[
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
        dependencies: set[str] = set()

        for imported in item[
            "imports"
        ]:
            if imported in known_modules:
                dependencies.add(
                    imported
                )

            dependencies.update(
                candidate
                for candidate
                in known_modules
                if candidate.startswith(
                    imported
                    + "."
                )
            )

        graph[
            item[
                "module"
            ]
        ] = dependencies

    reachable = reachable_modules(
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

    bases = [
        {
            "file": item[
                "path"
            ],
            "module": item[
                "module"
            ],
            "reachable_from_main": item[
                "reachable_from_main"
            ],
            "engine_count_in_file": len(
                item[
                    "engines"
                ]
            ),
            "session_factory_count_in_file": len(
                item[
                    "session_factories"
                ]
            ),
            **base,
        }
        for item in inventory
        for base in item[
            "base_definitions"
        ]
    ]

    engines = [
        {
            "file": item[
                "path"
            ],
            "reachable_from_main": item[
                "reachable_from_main"
            ],
            **engine,
        }
        for item in inventory
        for engine in item[
            "engines"
        ]
    ]

    session_factories = [
        {
            "file": item[
                "path"
            ],
            "reachable_from_main": item[
                "reachable_from_main"
            ],
            **factory,
        }
        for item in inventory
        for factory in item[
            "session_factories"
        ]
    ]

    base_by_qualified_name = {
        base[
            "qualified_name"
        ]: base
        for base in bases
    }

    models: list[
        dict[str, Any]
    ] = []

    unresolved_model_bases: list[
        dict[str, Any]
    ] = []

    for item in inventory:
        for model in item[
            "models"
        ]:
            resolved_owner = None

            reference = model[
                "base_reference"
            ]

            if reference in base_by_qualified_name:
                resolved_owner = reference

            elif reference:
                matching = [
                    qualified
                    for qualified
                    in base_by_qualified_name
                    if qualified.endswith(
                        "."
                        + terminal_name(
                            reference
                        )
                    )
                ]

                if len(
                    matching
                ) == 1:
                    resolved_owner = matching[
                        0
                    ]

            enriched = {
                "file": item[
                    "path"
                ],
                "module": item[
                    "module"
                ],
                "reachable_from_main": item[
                    "reachable_from_main"
                ],
                "resolved_base_owner": (
                    resolved_owner
                ),
                **model,
            }

            models.append(
                enriched
            )

            if resolved_owner is None:
                unresolved_model_bases.append(
                    enriched
                )

    models_by_base: dict[
        str,
        list[dict[str, Any]],
    ] = defaultdict(
        list
    )

    for model in models:
        owner = model[
            "resolved_base_owner"
        ]

        if owner:
            models_by_base[
                owner
            ].append(
                model
            )

    tables_by_base = {
        owner: sorted(
            {
                model[
                    "table"
                ]
                for model
                in owned_models
            }
        )
        for owner, owned_models
        in models_by_base.items()
    }

    table_to_bases: dict[
        str,
        set[str],
    ] = defaultdict(
        set
    )

    for owner, tables in tables_by_base.items():
        for table in tables:
            table_to_bases[
                table
            ].add(
                owner
            )

    overlapping_tables = {
        table: sorted(
            owners
        )
        for table, owners
        in table_to_bases.items()
        if len(
            owners
        ) > 1
    }

    base_dispositions: list[
        dict[str, Any]
    ] = []

    engine_owner_files = {
        engine[
            "file"
        ]
        for engine in engines
    }

    session_owner_files = {
        factory[
            "file"
        ]
        for factory
        in session_factories
    }

    for base in bases:
        qualified = base[
            "qualified_name"
        ]

        owned_models = models_by_base.get(
            qualified,
            [],
        )

        owns_engine = (
            base[
                "file"
            ]
            in engine_owner_files
        )

        owns_session_factory = (
            base[
                "file"
            ]
            in session_owner_files
        )

        active_model_count = sum(
            model[
                "reachable_from_main"
            ]
            for model in owned_models
        )

        if (
            owns_engine
            and owns_session_factory
        ):
            disposition = (
                "CANONICAL_RUNTIME_BASE"
            )

        elif (
            base[
                "reachable_from_main"
            ]
            and active_model_count > 0
        ):
            disposition = (
                "ACTIVE_SECONDARY_BASE"
            )

        elif owned_models:
            disposition = (
                "ISOLATED_OR_LEGACY_MODEL_BASE"
            )

        else:
            disposition = (
                "UNUSED_BASE_DEFINITION"
            )

        base_dispositions.append(
            {
                **base,
                "owns_engine": owns_engine,
                "owns_session_factory": (
                    owns_session_factory
                ),
                "owned_model_count": len(
                    owned_models
                ),
                "reachable_model_count": (
                    active_model_count
                ),
                "owned_tables": tables_by_base.get(
                    qualified,
                    [],
                ),
                "disposition": disposition,
            }
        )

    canonical_bases = [
        base
        for base in base_dispositions
        if base[
            "disposition"
        ] == "CANONICAL_RUNTIME_BASE"
    ]

    competing_bases = [
        base
        for base in base_dispositions
        if base[
            "disposition"
        ] == "ACTIVE_SECONDARY_BASE"
    ]

    isolated_bases = [
        base
        for base in base_dispositions
        if base[
            "disposition"
        ]
        in {
            "ISOLATED_OR_LEGACY_MODEL_BASE",
            "UNUSED_BASE_DEFINITION",
        }
    ]

    target_transaction_results: list[
        dict[str, Any]
    ] = []

    for item in inventory:
        expected_functions = (
            TARGET_TRANSACTION_PATHS.get(
                item[
                    "path"
                ]
            )
        )

        if not expected_functions:
            continue

        functions_by_name = {
            function[
                "name"
            ]: function
            for function
            in item[
                "functions"
            ]
        }

        for expected in sorted(
            expected_functions
        ):
            function = functions_by_name.get(
                expected
            )

            if function is None:
                target_transaction_results.append(
                    {
                        "file": item[
                            "path"
                        ],
                        "function": expected,
                        "found": False,
                        "disposition": (
                            "EXPECTED_FUNCTION_NOT_FOUND"
                        ),
                    }
                )

                continue

            target_transaction_results.append(
                {
                    "file": item[
                        "path"
                    ],
                    "reachable_from_main": item[
                        "reachable_from_main"
                    ],
                    "found": True,
                    **function,
                }
            )

    journal_models = [
        model
        for model in models
        if model[
            "file"
        ] == (
            "backend/app/stacks/"
            "journal_ledger/ledger.py"
        )
    ]

    journal_transactions = [
        function
        for item in inventory
        if item[
            "path"
        ] == (
            "backend/app/stacks/"
            "journal_ledger/ledger.py"
        )
        for function in item[
            "functions"
        ]
        if (
            function[
                "writes"
            ]
            or function[
                "sql_mutations"
            ]
        )
    ]

    journal_append_only_signals = {
        "has_model": bool(
            journal_models
        ),
        "has_write_path": bool(
            journal_transactions
        ),
        "has_unique_model_constraint": any(
            model[
                "unique_present"
            ]
            for model in journal_models
        ),
        "has_idempotency_key": any(
            model[
                "idempotency_key_present"
            ]
            for model in journal_models
        ),
        "has_previous_hash": any(
            model[
                "previous_hash_present"
            ]
            for model in journal_models
        ),
        "has_content_hash": any(
            model[
                "content_hash_present"
            ]
            for model in journal_models
        ),
    }

    journal_suitability: str

    if (
        journal_append_only_signals[
            "has_model"
        ]
        and journal_append_only_signals[
            "has_write_path"
        ]
    ):
        journal_suitability = (
            "SUITABLE_STACK_OWNER_BUT_APPEND_ONLY_CONTRACT_INCOMPLETE"
        )
    else:
        journal_suitability = (
            "INSUFFICIENT_EXISTING_SURFACE"
        )

    blockers: list[
        dict[str, Any]
    ] = []

    if len(
        canonical_bases
    ) != 1:
        blockers.append(
            {
                "code": (
                    "CANONICAL_RUNTIME_BASE_NOT_UNIQUE"
                ),
                "message": (
                    "Expected exactly one Base colocated "
                    "with the canonical engine and session "
                    "factory, found "
                    f"{len(canonical_bases)}."
                ),
                "evidence": canonical_bases,
            }
        )

    if competing_bases:
        blockers.append(
            {
                "code": (
                    "ACTIVE_SECONDARY_BASE_PRESENT"
                ),
                "message": (
                    "A second declarative Base is active "
                    "and owns models reachable from main."
                ),
                "evidence": competing_bases,
            }
        )

    if overlapping_tables:
        blockers.append(
            {
                "code": (
                    "TABLE_NAME_OVERLAP_ACROSS_BASES"
                ),
                "message": (
                    "The same table name is declared under "
                    "multiple metadata registries."
                ),
                "evidence": overlapping_tables,
            }
        )

    if unresolved_model_bases:
        blockers.append(
            {
                "code": (
                    "ORM_MODEL_BASE_OWNER_UNRESOLVED"
                ),
                "message": (
                    "One or more ORM model Base references "
                    "could not be resolved statically."
                ),
                "evidence": unresolved_model_bases,
            }
        )

    unguarded_transactions = [
        transaction
        for transaction
        in target_transaction_results
        if transaction.get(
            "disposition"
        )
        in {
            "MANUAL_COMMIT_WITHOUT_ROLLBACK_GUARD",
            (
                "MANUAL_COMMIT_WITH_EXCEPTION_HANDLER_"
                "BUT_NO_ROLLBACK"
            ),
        }
    ]

    if unguarded_transactions:
        blockers.append(
            {
                "code": (
                    "MANUAL_COMMIT_PATHS_REQUIRE_TRANSACTION_GUARD"
                ),
                "message": (
                    "One or more existing write paths commit "
                    "without an explicit rollback guard or "
                    "context-managed transaction boundary."
                ),
                "evidence": unguarded_transactions,
            }
        )

    if journal_suitability != (
        "SUITABLE_STACK_OWNER_BUT_APPEND_ONLY_CONTRACT_INCOMPLETE"
    ):
        blockers.append(
            {
                "code": (
                    "JOURNAL_LEDGER_OWNERSHIP_NOT_CONFIRMED"
                ),
                "message": (
                    "journal_ledger could not be confirmed as "
                    "the owner for the append-only decision-event "
                    "surface."
                ),
                "evidence": (
                    journal_append_only_signals
                ),
            }
        )

    summary = {
        "python_files_scanned": len(
            inventory
        ),
        "declarative_bases": len(
            bases
        ),
        "canonical_runtime_bases": len(
            canonical_bases
        ),
        "active_secondary_bases": len(
            competing_bases
        ),
        "isolated_or_legacy_bases": len(
            isolated_bases
        ),
        "engines": len(
            engines
        ),
        "session_factories": len(
            session_factories
        ),
        "orm_models": len(
            models
        ),
        "resolved_model_base_owners": (
            len(
                models
            )
            - len(
                unresolved_model_bases
            )
        ),
        "unresolved_model_base_owners": len(
            unresolved_model_bases
        ),
        "overlapping_table_names": len(
            overlapping_tables
        ),
        "target_transaction_paths": len(
            target_transaction_results
        ),
        "unguarded_target_transactions": len(
            unguarded_transactions
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
        "stage": "2B",
        "stage_name": (
            "Exact Declarative Base Ownership "
            "and Transaction Disposition"
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
        "bases": bases,
        "base_dispositions": (
            base_dispositions
        ),
        "canonical_runtime_bases": (
            canonical_bases
        ),
        "active_secondary_bases": (
            competing_bases
        ),
        "isolated_or_legacy_bases": (
            isolated_bases
        ),
        "engines": engines,
        "session_factories": (
            session_factories
        ),
        "models": models,
        "models_by_base": {
            owner: owned_models
            for owner, owned_models
            in models_by_base.items()
        },
        "tables_by_base": (
            tables_by_base
        ),
        "overlapping_tables": (
            overlapping_tables
        ),
        "unresolved_model_bases": (
            unresolved_model_bases
        ),
        "target_transaction_dispositions": (
            target_transaction_results
        ),
        "unguarded_target_transactions": (
            unguarded_transactions
        ),
        "journal_ledger": {
            "models": journal_models,
            "write_paths": (
                journal_transactions
            ),
            "signals": (
                journal_append_only_signals
            ),
            "suitability": (
                journal_suitability
            ),
        },
        "composition_blockers": (
            blockers
        ),
        "syntax_errors": (
            syntax_errors
        ),
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
        "next_stage": (
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
        "stage2b_exact_base_and_transaction_disposition_"
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
            "STAGE 2B — EXACT DECLARATIVE BASE OWNERSHIP "
            "AND TRANSACTION DISPOSITION"
        ),
        "=" * 80,
        "",
        "MODE",
        "READ ONLY",
        "",
        "SUMMARY",
        (
            "Python files scanned:                "
            f"{summary['python_files_scanned']}"
        ),
        (
            "Declarative Bases:                   "
            f"{summary['declarative_bases']}"
        ),
        (
            "Canonical runtime Bases:             "
            f"{summary['canonical_runtime_bases']}"
        ),
        (
            "Active secondary Bases:              "
            f"{summary['active_secondary_bases']}"
        ),
        (
            "Isolated or legacy Bases:            "
            f"{summary['isolated_or_legacy_bases']}"
        ),
        (
            "Engine definitions:                  "
            f"{summary['engines']}"
        ),
        (
            "Session factory definitions:         "
            f"{summary['session_factories']}"
        ),
        (
            "ORM models:                          "
            f"{summary['orm_models']}"
        ),
        (
            "Resolved model Base owners:          "
            f"{summary['resolved_model_base_owners']}"
        ),
        (
            "Unresolved model Base owners:        "
            f"{summary['unresolved_model_base_owners']}"
        ),
        (
            "Overlapping table names:             "
            f"{summary['overlapping_table_names']}"
        ),
        (
            "Target transaction paths:            "
            f"{summary['target_transaction_paths']}"
        ),
        (
            "Unguarded target transactions:       "
            f"{summary['unguarded_target_transactions']}"
        ),
        (
            "Syntax errors:                       "
            f"{summary['syntax_errors']}"
        ),
        (
            "Composition blockers:                "
            f"{summary['composition_blockers']}"
        ),
        "",
        "BASE DISPOSITIONS",
    ]

    for base in base_dispositions:
        lines.append(
            "- "
            + base[
                "qualified_name"
            ]
        )

        lines.append(
            "    file="
            + base[
                "file"
            ]
        )

        lines.append(
            "    disposition="
            + base[
                "disposition"
            ]
        )

        lines.append(
            "    reachable_from_main="
            + str(
                base[
                    "reachable_from_main"
                ]
            )
        )

        lines.append(
            "    owns_engine="
            + str(
                base[
                    "owns_engine"
                ]
            )
            + " owns_session_factory="
            + str(
                base[
                    "owns_session_factory"
                ]
            )
        )

        lines.append(
            "    model_count="
            + str(
                base[
                    "owned_model_count"
                ]
            )
            + " reachable_model_count="
            + str(
                base[
                    "reachable_model_count"
                ]
            )
        )

        lines.append(
            "    tables="
            + (
                ", ".join(
                    base[
                        "owned_tables"
                    ]
                )
                or "none"
            )
        )

    lines.extend(
        [
            "",
            "MODEL OWNERSHIP",
        ]
    )

    for model in models:
        lines.append(
            "- "
            + model[
                "qualified_name"
            ]
            + " -> "
            + (
                model[
                    "resolved_base_owner"
                ]
                or "UNRESOLVED"
            )
            + " ["
            + model[
                "table"
            ]
            + "]"
        )

    lines.extend(
        [
            "",
            "TABLE OVERLAP",
        ]
    )

    if overlapping_tables:
        for table, owners in sorted(
            overlapping_tables.items()
        ):
            lines.append(
                "- "
                + table
                + " -> "
                + ", ".join(
                    owners
                )
            )
    else:
        lines.append(
            "- None"
        )

    lines.extend(
        [
            "",
            "TARGET TRANSACTION DISPOSITIONS",
        ]
    )

    for transaction in (
        target_transaction_results
    ):
        lines.append(
            "- "
            + transaction[
                "file"
            ]
            + "::"
            + transaction[
                "function"
                if not transaction.get(
                    "found",
                    True,
                )
                else "name"
            ]
        )

        lines.append(
            "    disposition="
            + transaction[
                "disposition"
            ]
        )

        if transaction.get(
            "found"
        ):
            lines.append(
                "    methods="
                + (
                    ", ".join(
                        transaction[
                            "transaction_methods"
                        ]
                    )
                    or "none"
                )
            )

            lines.append(
                "    commit="
                + str(
                    transaction[
                        "commit_present"
                    ]
                )
                + " rollback="
                + str(
                    transaction[
                        "rollback_present"
                    ]
                )
                + " context_transaction="
                + str(
                    transaction[
                        "uses_context_transaction"
                    ]
                )
            )

    lines.extend(
        [
            "",
            "JOURNAL LEDGER DISPOSITION",
            (
                "- Suitability: "
                + journal_suitability
            ),
            (
                "- Existing models: "
                + str(
                    len(
                        journal_models
                    )
                )
            ),
            (
                "- Existing write paths: "
                + str(
                    len(
                        journal_transactions
                    )
                )
            ),
            (
                "- Idempotency key present: "
                + str(
                    journal_append_only_signals[
                        "has_idempotency_key"
                    ]
                )
            ),
            (
                "- Previous hash present: "
                + str(
                    journal_append_only_signals[
                        "has_previous_hash"
                    ]
                )
            ),
            (
                "- Content hash present: "
                + str(
                    journal_append_only_signals[
                        "has_content_hash"
                    ]
                )
            ),
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
            "Source modified:                    NO",
            "Application modules imported:       NO",
            "Database connected:                 NO",
            "SQL executed:                       NO",
            "Tables created:                     NO",
            "Records written:                    NO",
            "Broker execution enabled:           NO",
            "Live trading enabled:               NO",
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
        "## Stage 2B — Exact Declarative Base "
        "Ownership and Transaction Disposition"
    )

    existing = ""

    if LEDGER_FILE.exists():
        existing = (
            LEDGER_FILE.read_text(
                encoding="utf-8"
            )
        )

    if ledger_marker not in existing:
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
                "- Declarative Bases: "
                f"**{summary['declarative_bases']}**\n"
                "- Canonical runtime Bases: "
                f"**{summary['canonical_runtime_bases']}**\n"
                "- Active secondary Bases: "
                f"**{summary['active_secondary_bases']}**\n"
                "- ORM models: "
                f"**{summary['orm_models']}**\n"
                "- Unresolved model Base owners: "
                f"**{summary['unresolved_model_base_owners']}**\n"
                "- Overlapping tables: "
                f"**{summary['overlapping_table_names']}**\n"
                "- Unguarded target transactions: "
                f"**{summary['unguarded_target_transactions']}**\n"
                "- Journal ledger suitability: "
                f"**{journal_suitability}**\n"
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
