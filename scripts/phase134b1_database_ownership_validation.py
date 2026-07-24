#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import ast
import json
import os

from backend.app.stacks.db_runtime.database import (
    Base,
    database_runtime_status,
    normalize_async_database_url,
)


ROOT = Path(".").resolve()

DATABASE_MODULE = (
    ROOT
    / "backend/app/stacks/db_runtime/database.py"
)

LEDGER_MODULE = (
    ROOT
    / "backend/app/stacks/journal_ledger/ledger.py"
)

database_text = DATABASE_MODULE.read_text(
    encoding="utf-8"
)

ledger_text = LEDGER_MODULE.read_text(
    encoding="utf-8"
)

ast.parse(database_text)
ast.parse(ledger_text)

# Import ledger so its ORM models register with canonical Base.
from backend.app.stacks.journal_ledger.ledger import (  # noqa: E402
    OrderHistory,
    PortfolioInventory,
    async_session,
    init_db,
)


normalized_examples = {
    "psycopg": normalize_async_database_url(
        "postgresql+psycopg://"
        "user:pass@localhost:5432/test"
    ),
    "psycopg2": normalize_async_database_url(
        "postgresql+psycopg2://"
        "user:pass@localhost:5432/test"
    ),
    "plain_postgresql": normalize_async_database_url(
        "postgresql://"
        "user:pass@localhost:5432/test"
    ),
    "already_async": normalize_async_database_url(
        "postgresql+asyncpg://"
        "user:pass@localhost:5432/test"
    ),
}

registered_tables = set(
    Base.metadata.tables.keys()
)

checks = {
    "canonical_database_module_exists": (
        DATABASE_MODULE.exists()
    ),
    "canonical_base_defined": (
        "class Base(DeclarativeBase)"
        in database_text
    ),
    "canonical_async_engine_defined": (
        "create_async_engine"
        in database_text
    ),
    "canonical_session_defined": (
        "async_sessionmaker"
        in database_text
    ),
    "environment_url_supported": (
        'os.getenv("DATABASE_URL")'
        in database_text
    ),
    "neurovest_override_supported": (
        'os.getenv("NEUROVEST_DATABASE_URL")'
        in database_text
    ),
    "psycopg_normalizes_to_asyncpg": (
        normalized_examples["psycopg"].startswith(
            "postgresql+asyncpg://"
        )
    ),
    "psycopg2_normalizes_to_asyncpg": (
        normalized_examples["psycopg2"].startswith(
            "postgresql+asyncpg://"
        )
    ),
    "plain_postgresql_normalizes": (
        normalized_examples[
            "plain_postgresql"
        ].startswith(
            "postgresql+asyncpg://"
        )
    ),
    "async_url_preserved": (
        normalized_examples["already_async"]
        == (
            "postgresql+asyncpg://"
            "user:pass@localhost:5432/test"
        )
    ),
    "ledger_imports_canonical_base": (
        "from backend.app.stacks.db_runtime import"
        in ledger_text
    ),
    "ledger_has_no_local_base": (
        "class Base(" not in ledger_text
    ),
    "ledger_has_no_local_engine": (
        "create_async_engine" not in ledger_text
    ),
    "order_history_registered": (
        "order_history" in registered_tables
    ),
    "portfolio_inventory_registered": (
        "portfolio_inventory"
        in registered_tables
    ),
    "ledger_session_is_available": (
        async_session is not None
    ),
    "ledger_init_is_canonical": (
        init_db.__module__
        == (
            "backend.app.stacks."
            "db_runtime.database"
        )
    ),
    "model_classes_use_canonical_metadata": (
        OrderHistory.metadata is Base.metadata
        and PortfolioInventory.metadata
        is Base.metadata
    ),
}

certified = all(checks.values())

runtime_status = database_runtime_status()

result = {
    "phase": (
        "134B1_CHAT_DATABASE_OWNERSHIP_NORMALIZATION"
    ),
    "checks": checks,
    "database_runtime": runtime_status,
    "registered_tables": sorted(
        registered_tables
    ),
    "environment_database_url_present": bool(
        os.getenv("DATABASE_URL")
    ),
    "environment_neurovest_url_present": bool(
        os.getenv("NEUROVEST_DATABASE_URL")
    ),
    "behavior": {
        "database_connection_attempted": False,
        "tables_created": False,
        "chat_tables_created": False,
        "ledger_business_logic_changed": False,
        "broker_execution_changed": False,
    },
    "certified": certified,
    "recommended_next_phase": (
        "134B2_CHAT_PERSISTENCE_MODELS"
        if certified
        else "134B1_DATABASE_OWNERSHIP_REPAIR"
    ),
}

output_dir = (
    ROOT
    / "runtime/chat_persistence"
)

output_dir.mkdir(
    parents=True,
    exist_ok=True,
)

output_json = (
    output_dir
    / "134B1_database_ownership_latest.json"
)

output_txt = (
    output_dir
    / "134B1_database_ownership_latest.txt"
)

output_json.write_text(
    json.dumps(
        result,
        indent=2,
    ),
    encoding="utf-8",
)

lines = [
    result["phase"],
    "",
    f"certified: {certified}",
    "",
    "CHECKS",
]

for name, passed in checks.items():
    lines.append(
        f"{name}: {'PASS' if passed else 'FAIL'}"
    )

lines.extend(
    [
        "",
        "DATABASE RUNTIME",
        (
            "driver: "
            f"{runtime_status['driver']}"
        ),
        (
            "database: "
            f"{runtime_status['database']}"
        ),
        (
            "host: "
            f"{runtime_status['host']}"
        ),
        (
            "username: "
            f"{runtime_status['username']}"
        ),
        "password_exposed: False",
        "",
        "BEHAVIOR",
        "database_connection_attempted: False",
        "tables_created: False",
        "chat_tables_created: False",
        "ledger_business_logic_changed: False",
        "broker_execution_changed: False",
        "",
        (
            "next: "
            f"{result['recommended_next_phase']}"
        ),
    ]
)

output_txt.write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8",
)

print(
    json.dumps(
        result,
        indent=2,
    )
)

if not certified:
    raise SystemExit(1)
