#!/usr/bin/env python3

"""
NeuroVest Workstream 3
Stage 1 — Persistence, Transaction, and Append-Only Audit Baseline

READ ONLY.

This scanner inventories:

- database runtime ownership
- SQLAlchemy engines and session factories
- ORM models and tables
- transaction boundaries
- commit, rollback, flush, and refresh calls
- persistence write paths
- append-only and immutable ledger signals
- delete and update capabilities
- decision/audit/journal ownership
- application reachability
- composition blockers

It does not import application modules, connect to a database,
create tables, write records, or modify backend source.
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

MAIN_FILE = (
    BACKEND_ROOT
    / "main.py"
)

OUTPUT_DIR = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream3"
    / "baseline"
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
    / "persistence_transaction_baseline_latest.json"
)

OUTPUT_TEXT = (
    OUTPUT_DIR
    / "persistence_transaction_baseline_latest.txt"
)


PERSISTENCE_PATH_MARKERS = (
    "db_runtime",
    "database",
    "persistence",
    "repository",
    "ledger",
    "journal",
    "audit",
    "event_store",
    "decision",
    "transaction",
    "models",
)

TRANSACTION_CALLS = {
    "commit",
    "rollback",
    "flush",
    "refresh",
    "begin",
    "begin_nested",
    "execute",
    "add",
    "add_all",
    "merge",
    "delete",
    "close",
}

WRITE_CALLS = {
    "add",
    "add_all",
    "merge",
    "delete",
    "commit",
    "flush",
    "execute",
}

MUTATION_METHOD_NAMES = {
    "create",
    "insert",
    "append",
    "record",
    "save",
    "store",
    "write",
    "update",
    "upsert",
    "delete",
    "remove",
    "purge",
    "truncate",
}

APPEND_ONLY_MARKERS = (
    "append_only",
    "append-only",
    "immutable",
    "immutability",
    "event_id",
    "sequence_id",
    "audit_id",
    "decision_id",
    "created_at",
    "recorded_at",
    "occurred_at",
    "correlation_id",
    "causation_id",
    "idempotency",
    "hash_chain",
    "previous_hash",
    "content_hash",
)

DANGEROUS_MUTATION_MARKERS = (
    ".delete(",
    ".update(",
    "delete(",
    "update(",
    "truncate",
    "drop_all",
    "drop table",
    "cascade delete",
)

TRANSACTION_SAFETY_MARKERS = (
    "rollback",
    "try:",
    "except",
    "async with",
    "with session",
    "session.begin",
    "begin_nested",
)

SCAFFOLD_MARKERS = (
    "placeholder",
    "notimplementederror",
    "todo",
    "fixme",
    "healthcheck-only",
    "scaffold",
    "stub",
)

DECISION_MARKERS = (
    "decision",
    "signal",
    "strategy",
    "risk",
    "approval",
    "rejection",
    "blocked",
    "execution_intent",
)

AUDIT_MARKERS = (
    "audit",
    "journal",
    "ledger",
    "history",
    "event",
    "evidence",
    "trace",
)


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
                parent
                + "."
                + node.attr
            )

        return node.attr

    return None


def call_name(
    node: ast.Call,
) -> str | None:
    return dotted_name(
        node.func
    )


def literal_tablename(
    node: ast.ClassDef,
) -> str | None:
    for statement in node.body:
        if not isinstance(
            statement,
            ast.Assign,
        ):
            continue

        for target in statement.targets:
            if (
                isinstance(target, ast.Name)
                and target.id == "__tablename__"
                and isinstance(
                    statement.value,
                    ast.Constant,
                )
                and isinstance(
                    statement.value.value,
                    str,
                )
            ):
                return statement.value.value

    return None


def class_base_names(
    node: ast.ClassDef,
) -> list[str]:
    names: list[str] = []

    for base in node.bases:
        rendered = dotted_name(
            base
        )

        if rendered:
            names.append(
                rendered
            )

    return names


def imported_modules(
    tree: ast.AST,
    current_module: str,
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
            if node.module is None:
                continue

            if node.level:
                current_parts = (
                    current_module.split(".")
                )

                base_parts = current_parts[
                    :-node.level
                ]

                resolved = ".".join(
                    base_parts
                    + node.module.split(".")
                )
            else:
                resolved = node.module

            if resolved.startswith(
                "backend.app"
            ):
                discovered.add(
                    resolved
                )

    return discovered


def find_reachable_modules(
    graph: dict[str, set[str]],
    root_module: str,
) -> set[str]:
    reachable: set[str] = set()

    queue: deque[str] = deque(
        [root_module]
    )

    while queue:
        module = queue.popleft()

        if module in reachable:
            continue

        reachable.add(
            module
        )

        for dependency in graph.get(
            module,
            set(),
        ):
            if dependency not in reachable:
                queue.append(
                    dependency
                )

    return reachable


def source_contains_any(
    source: str,
    markers: tuple[str, ...],
) -> list[str]:
    lowered = source.lower()

    return sorted(
        {
            marker
            for marker in markers
            if marker.lower() in lowered
        }
    )


def inspect_python_file(
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
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(
            path
        ),
        "syntax_error": None,
        "imports": [],
        "classes": [],
        "functions": [],
        "tables": [],
        "transaction_calls": [],
        "write_calls": [],
        "mutation_methods": [],
        "append_only_markers": source_contains_any(
            source,
            APPEND_ONLY_MARKERS,
        ),
        "dangerous_mutation_markers": (
            source_contains_any(
                source,
                DANGEROUS_MUTATION_MARKERS,
            )
        ),
        "transaction_safety_markers": (
            source_contains_any(
                source,
                TRANSACTION_SAFETY_MARKERS,
            )
        ),
        "scaffold_markers": source_contains_any(
            source,
            SCAFFOLD_MARKERS,
        ),
        "decision_markers": source_contains_any(
            source,
            DECISION_MARKERS,
        ),
        "audit_markers": source_contains_any(
            source,
            AUDIT_MARKERS,
        ),
        "persistence_path_candidate": any(
            marker in relative.lower()
            for marker in PERSISTENCE_PATH_MARKERS
        ),
        "defines_base": False,
        "defines_engine": False,
        "defines_session_factory": False,
        "defines_init_db": False,
        "defines_repository": False,
        "uses_sqlalchemy": (
            "sqlalchemy" in source.lower()
        ),
    }

    try:
        tree = ast.parse(
            source,
            filename=str(path),
        )

    except SyntaxError as exc:
        result["syntax_error"] = {
            "line": exc.lineno,
            "column": exc.offset,
            "message": exc.msg,
        }

        return result

    result["imports"] = sorted(
        imported_modules(
            tree,
            result["module"],
        )
    )

    for node in tree.body:
        if isinstance(
            node,
            ast.ClassDef,
        ):
            bases = class_base_names(
                node
            )

            table_name = literal_tablename(
                node
            )

            class_record = {
                "name": node.name,
                "line": node.lineno,
                "bases": bases,
                "table": table_name,
            }

            result["classes"].append(
                class_record
            )

            if table_name:
                result["tables"].append(
                    {
                        "class": node.name,
                        "table": table_name,
                        "line": node.lineno,
                    }
                )

            lowered_name = node.name.lower()

            if (
                "repository" in lowered_name
                or "store" in lowered_name
                or "ledger" in lowered_name
            ):
                result[
                    "defines_repository"
                ] = True

        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            result["functions"].append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "async": isinstance(
                        node,
                        ast.AsyncFunctionDef,
                    ),
                }
            )

            lowered_name = node.name.lower()

            if lowered_name == "init_db":
                result[
                    "defines_init_db"
                ] = True

            if any(
                marker in lowered_name
                for marker in MUTATION_METHOD_NAMES
            ):
                result[
                    "mutation_methods"
                ].append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "async": isinstance(
                            node,
                            ast.AsyncFunctionDef,
                        ),
                    }
                )

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.Assign,
        ):
            names = [
                target.id
                for target in node.targets
                if isinstance(
                    target,
                    ast.Name,
                )
            ]

            lowered_names = {
                name.lower()
                for name in names
            }

            if (
                "base" in lowered_names
                or "declarativebase" in source[
                    node.lineno - 1:
                    node.end_lineno
                ].lower()
            ):
                result[
                    "defines_base"
                ] = True

            if any(
                "engine" in name
                for name in lowered_names
            ):
                result[
                    "defines_engine"
                ] = True

            if any(
                marker in name
                for name in lowered_names
                for marker in (
                    "session",
                    "sessionmaker",
                )
            ):
                result[
                    "defines_session_factory"
                ] = True

        if isinstance(
            node,
            ast.Call,
        ):
            rendered = call_name(
                node
            )

            if not rendered:
                continue

            terminal = rendered.split(
                "."
            )[-1]

            if terminal in TRANSACTION_CALLS:
                call_record = {
                    "call": rendered,
                    "line": node.lineno,
                }

                result[
                    "transaction_calls"
                ].append(
                    call_record
                )

                if terminal in WRITE_CALLS:
                    result[
                        "write_calls"
                    ].append(
                        call_record
                    )

    return result


def main() -> int:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    HISTORY_DIR.mkdir(
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
        inspect_python_file(
            path
        )
        for path in python_files
    ]

    module_graph: dict[
        str,
        set[str],
    ] = {}

    known_modules = {
        item["module"]
        for item in inventory
    }

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

            matches = [
                candidate
                for candidate in known_modules
                if candidate.startswith(
                    imported + "."
                )
            ]

            resolved.update(
                matches
            )

        module_graph[
            item["module"]
        ] = resolved

    main_module = module_name(
        MAIN_FILE
    )

    reachable = find_reachable_modules(
        module_graph,
        main_module,
    )

    for item in inventory:
        item[
            "reachable_from_main"
        ] = (
            item["module"]
            in reachable
        )

    persistence_files = [
        item
        for item in inventory
        if (
            item[
                "persistence_path_candidate"
            ]
            or item[
                "uses_sqlalchemy"
            ]
            or item[
                "tables"
            ]
            or item[
                "transaction_calls"
            ]
            or item[
                "append_only_markers"
            ]
        )
    ]

    orm_tables = [
        {
            "file": item["path"],
            **table,
        }
        for item in inventory
        for table in item[
            "tables"
        ]
    ]

    transaction_files = [
        item
        for item in inventory
        if item[
            "transaction_calls"
        ]
    ]

    write_path_files = [
        item
        for item in inventory
        if item[
            "write_calls"
        ]
    ]

    append_only_candidates = [
        item
        for item in inventory
        if (
            item[
                "append_only_markers"
            ]
            and (
                item[
                    "audit_markers"
                ]
                or item[
                    "decision_markers"
                ]
                or item[
                    "tables"
                ]
            )
        )
    ]

    destructive_candidates = [
        item
        for item in inventory
        if item[
            "dangerous_mutation_markers"
        ]
    ]

    session_factories = [
        item
        for item in inventory
        if item[
            "defines_session_factory"
        ]
    ]

    engines = [
        item
        for item in inventory
        if item[
            "defines_engine"
        ]
    ]

    bases = [
        item
        for item in inventory
        if item[
            "defines_base"
        ]
    ]

    init_db_files = [
        item
        for item in inventory
        if item[
            "defines_init_db"
        ]
    ]

    syntax_errors = [
        {
            "path": item["path"],
            **item["syntax_error"],
        }
        for item in inventory
        if item[
            "syntax_error"
        ]
    ]

    scaffold_candidates = [
        item
        for item in persistence_files
        if item[
            "scaffold_markers"
        ]
    ]

    reachable_persistence_files = [
        item
        for item in persistence_files
        if item[
            "reachable_from_main"
        ]
    ]

    blockers: list[
        dict[str, Any]
    ] = []

    if len(bases) != 1:
        blockers.append(
            {
                "code": "NON_CANONICAL_BASE_COUNT",
                "message": (
                    "Expected exactly one canonical ORM Base "
                    f"definition, found {len(bases)}."
                ),
                "files": [
                    item["path"]
                    for item in bases
                ],
            }
        )

    if not engines:
        blockers.append(
            {
                "code": "DATABASE_ENGINE_NOT_DISCOVERED",
                "message": (
                    "No database engine definition was discovered."
                ),
                "files": [],
            }
        )

    if not session_factories:
        blockers.append(
            {
                "code": "SESSION_FACTORY_NOT_DISCOVERED",
                "message": (
                    "No canonical session factory was discovered."
                ),
                "files": [],
            }
        )

    if not orm_tables:
        blockers.append(
            {
                "code": "ORM_TABLES_NOT_DISCOVERED",
                "message": (
                    "No ORM table declarations were discovered."
                ),
                "files": [],
            }
        )

    if not append_only_candidates:
        blockers.append(
            {
                "code": (
                    "APPEND_ONLY_DECISION_AUDIT_SURFACE_MISSING"
                ),
                "message": (
                    "No verified append-only decision or audit "
                    "persistence surface was discovered."
                ),
                "files": [],
            }
        )

    if syntax_errors:
        blockers.append(
            {
                "code": "PERSISTENCE_SYNTAX_ERRORS",
                "message": (
                    "One or more persistence-related Python "
                    "files contain syntax errors."
                ),
                "files": [
                    item["path"]
                    for item in syntax_errors
                ],
            }
        )

    summary = {
        "python_files_scanned": len(
            inventory
        ),
        "persistence_related_files": len(
            persistence_files
        ),
        "reachable_persistence_files": len(
            reachable_persistence_files
        ),
        "orm_tables": len(
            orm_tables
        ),
        "engine_definitions": len(
            engines
        ),
        "base_definitions": len(
            bases
        ),
        "session_factory_definitions": len(
            session_factories
        ),
        "init_db_definitions": len(
            init_db_files
        ),
        "transaction_files": len(
            transaction_files
        ),
        "write_path_files": len(
            write_path_files
        ),
        "append_only_candidates": len(
            append_only_candidates
        ),
        "destructive_mutation_candidates": len(
            destructive_candidates
        ),
        "scaffold_candidates": len(
            scaffold_candidates
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
        "stage": 1,
        "stage_name": (
            "Persistence, Transaction, and "
            "Append-Only Audit Baseline"
        ),
        "mode": "read_only",
        "status": "completed",
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
        "composition_blockers": blockers,
        "orm_tables": orm_tables,
        "canonical_surfaces": {
            "base_files": [
                item["path"]
                for item in bases
            ],
            "engine_files": [
                item["path"]
                for item in engines
            ],
            "session_factory_files": [
                item["path"]
                for item in session_factories
            ],
            "init_db_files": [
                item["path"]
                for item in init_db_files
            ],
        },
        "transaction_files": [
            {
                "path": item["path"],
                "reachable_from_main": item[
                    "reachable_from_main"
                ],
                "transaction_calls": item[
                    "transaction_calls"
                ],
                "transaction_safety_markers": item[
                    "transaction_safety_markers"
                ],
            }
            for item in transaction_files
        ],
        "write_path_files": [
            {
                "path": item["path"],
                "reachable_from_main": item[
                    "reachable_from_main"
                ],
                "write_calls": item[
                    "write_calls"
                ],
                "mutation_methods": item[
                    "mutation_methods"
                ],
            }
            for item in write_path_files
        ],
        "append_only_candidates": [
            {
                "path": item["path"],
                "reachable_from_main": item[
                    "reachable_from_main"
                ],
                "tables": item[
                    "tables"
                ],
                "append_only_markers": item[
                    "append_only_markers"
                ],
                "decision_markers": item[
                    "decision_markers"
                ],
                "audit_markers": item[
                    "audit_markers"
                ],
            }
            for item in append_only_candidates
        ],
        "destructive_mutation_candidates": [
            {
                "path": item["path"],
                "reachable_from_main": item[
                    "reachable_from_main"
                ],
                "markers": item[
                    "dangerous_mutation_markers"
                ],
            }
            for item in destructive_candidates
        ],
        "scaffold_candidates": [
            {
                "path": item["path"],
                "markers": item[
                    "scaffold_markers"
                ],
            }
            for item in scaffold_candidates
        ],
        "syntax_errors": syntax_errors,
        "inventory": persistence_files,
        "safety": {
            "source_modified": False,
            "database_connected": False,
            "tables_created": False,
            "records_written": False,
            "broker_execution_enabled": False,
            "live_trading_enabled": False,
        },
        "recommended_build_order": [
            (
                "Canonical persistence ownership and "
                "transaction-boundary verification"
            ),
            (
                "Append-only decision and audit event contract"
            ),
            (
                "Transaction manager and rollback semantics"
            ),
            (
                "Idempotency and duplicate-write prevention"
            ),
            (
                "Immutable decision-event repository"
            ),
            (
                "Audit-chain integrity and evidence hashing"
            ),
            (
                "Read-only persistence observability"
            ),
            (
                "Database-backed integration qualification"
            ),
            (
                "Workstream 3 freeze"
            ),
        ],
        "next_stage": (
            "Stage 2 — Canonical Persistence Ownership, "
            "Transaction Boundary, and Append-Only Contract Inspection"
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
        "persistence_transaction_baseline_"
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
            "PERSISTENCE, TRANSACTIONS, AND "
            "APPEND-ONLY DECISION AUDITING"
        ),
        "=" * 80,
        "",
        "STAGE 1",
        (
            "Persistence, Transaction, and "
            "Append-Only Audit Baseline"
        ),
        "",
        "MODE",
        "READ ONLY",
        "",
        "SUMMARY",
        (
            "Python files scanned:                 "
            f"{summary['python_files_scanned']}"
        ),
        (
            "Persistence-related files:            "
            f"{summary['persistence_related_files']}"
        ),
        (
            "Reachable persistence files:          "
            f"{summary['reachable_persistence_files']}"
        ),
        (
            "ORM tables discovered:                "
            f"{summary['orm_tables']}"
        ),
        (
            "ORM Base definitions:                 "
            f"{summary['base_definitions']}"
        ),
        (
            "Engine definitions:                   "
            f"{summary['engine_definitions']}"
        ),
        (
            "Session factory definitions:          "
            f"{summary['session_factory_definitions']}"
        ),
        (
            "init_db definitions:                  "
            f"{summary['init_db_definitions']}"
        ),
        (
            "Transaction files:                    "
            f"{summary['transaction_files']}"
        ),
        (
            "Write-path files:                     "
            f"{summary['write_path_files']}"
        ),
        (
            "Append-only candidates:               "
            f"{summary['append_only_candidates']}"
        ),
        (
            "Destructive mutation candidates:      "
            f"{summary['destructive_mutation_candidates']}"
        ),
        (
            "Scaffold candidates:                  "
            f"{summary['scaffold_candidates']}"
        ),
        (
            "Syntax errors:                        "
            f"{summary['syntax_errors']}"
        ),
        (
            "Composition blockers:                 "
            f"{summary['composition_blockers']}"
        ),
        "",
        "CANONICAL DATABASE SURFACES",
    ]

    for label, key in (
        (
            "ORM Base",
            "base_files",
        ),
        (
            "Engine",
            "engine_files",
        ),
        (
            "Session factory",
            "session_factory_files",
        ),
        (
            "Database initialization",
            "init_db_files",
        ),
    ):
        values = report[
            "canonical_surfaces"
        ][key]

        if values:
            for value in values:
                lines.append(
                    f"- {label}: {value}"
                )
        else:
            lines.append(
                f"- {label}: NOT FOUND"
            )

    lines.extend(
        [
            "",
            "ORM TABLES",
        ]
    )

    if orm_tables:
        for table in orm_tables:
            lines.append(
                "- "
                + table["table"]
                + " — "
                + table["class"]
                + " — "
                + table["file"]
            )
    else:
        lines.append(
            "- None"
        )

    lines.extend(
        [
            "",
            "TRANSACTION FILES",
        ]
    )

    if transaction_files:
        for item in transaction_files:
            calls = sorted(
                {
                    call["call"]
                    for call in item[
                        "transaction_calls"
                    ]
                }
            )

            lines.append(
                "- "
                + item["path"]
                + " — "
                + ", ".join(calls)
            )
    else:
        lines.append(
            "- None"
        )

    lines.extend(
        [
            "",
            "APPEND-ONLY CANDIDATES",
        ]
    )

    if append_only_candidates:
        for item in append_only_candidates:
            lines.append(
                "- "
                + item["path"]
                + " — "
                + ", ".join(
                    item[
                        "append_only_markers"
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
            "COMPOSITION BLOCKERS",
        ]
    )

    if blockers:
        for blocker in blockers:
            lines.append(
                "- "
                + blocker["code"]
            )

            lines.append(
                "    "
                + blocker["message"]
            )

            for file in blocker[
                "files"
            ]:
                lines.append(
                    "    - "
                    + file
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
            "Database connected:                 NO",
            "Tables created:                     NO",
            "Records written:                    NO",
            "Broker execution enabled:           NO",
            "Live trading enabled:               NO",
            "",
            "NEXT",
            (
                "Stage 2 — Canonical Persistence Ownership, "
                "Transaction Boundary, and Append-Only "
                "Contract Inspection"
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

    print(
        rendered
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
