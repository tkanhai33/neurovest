#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import ast
import json

from sqlalchemy import inspect

from backend.app.stacks.db_runtime import Base
from backend.app.stacks.chat_public.persistence import (
    CHAT_PERSISTENCE_TABLES,
    ChatMessageRecord,
    ChatThreadRecord,
    ConversationStateRecord,
    MemoryFactRecord,
    ToolEvidenceRecord,
)


ROOT = Path(".").resolve()

MODELS_FILE = (
    ROOT
    / "backend/app/stacks/chat_public/persistence/chat_models.py"
)

DATABASE_FILE = (
    ROOT
    / "backend/app/stacks/db_runtime/database.py"
)

models_text = MODELS_FILE.read_text(
    encoding="utf-8"
)

database_text = DATABASE_FILE.read_text(
    encoding="utf-8"
)

ast.parse(models_text)
ast.parse(database_text)

registered_tables = set(
    Base.metadata.tables.keys()
)

expected_tables = set(
    CHAT_PERSISTENCE_TABLES
)

model_map = {
    "chat_threads": ChatThreadRecord,
    "chat_messages": ChatMessageRecord,
    "chat_conversation_states": ConversationStateRecord,
    "chat_memory_facts": MemoryFactRecord,
    "chat_tool_evidence": ToolEvidenceRecord,
}


def column_names(model_type) -> set[str]:
    return {
        column.key
        for column in inspect(model_type).columns
    }


def foreign_key_targets(
    table_name: str,
) -> set[str]:
    table = Base.metadata.tables[table_name]

    return {
        foreign_key.target_fullname
        for foreign_key in table.foreign_keys
    }


checks = {
    "models_file_exists": MODELS_FILE.exists(),
    "all_chat_tables_registered": (
        expected_tables.issubset(
            registered_tables
        )
    ),
    "thread_model_uses_canonical_base": (
        ChatThreadRecord.metadata
        is Base.metadata
    ),
    "message_model_uses_canonical_base": (
        ChatMessageRecord.metadata
        is Base.metadata
    ),
    "state_model_uses_canonical_base": (
        ConversationStateRecord.metadata
        is Base.metadata
    ),
    "memory_model_uses_canonical_base": (
        MemoryFactRecord.metadata
        is Base.metadata
    ),
    "evidence_model_uses_canonical_base": (
        ToolEvidenceRecord.metadata
        is Base.metadata
    ),
    "thread_fields_complete": {
        "thread_id",
        "user_id",
        "title",
        "status",
        "summary",
        "message_count",
        "created_at",
        "updated_at",
        "metadata_json",
    }.issubset(
        column_names(ChatThreadRecord)
    ),
    "message_fields_complete": {
        "message_id",
        "thread_id",
        "parent_message_id",
        "client_message_id",
        "role",
        "content",
        "intent",
        "symbol",
        "provider",
        "model",
        "tool_evidence_ids",
        "created_at",
        "metadata_json",
    }.issubset(
        column_names(ChatMessageRecord)
    ),
    "conversation_state_fields_complete": {
        "thread_id",
        "summary",
        "active_entities",
        "active_strategy",
        "portfolio_context",
        "pending_tasks",
        "remembered_terms",
        "last_message_id",
        "updated_at",
        "metadata_json",
    }.issubset(
        column_names(ConversationStateRecord)
    ),
    "memory_fields_complete": {
        "memory_id",
        "thread_id",
        "key",
        "value_json",
        "confidence",
        "status",
        "source_message_id",
        "created_at",
        "updated_at",
        "metadata_json",
    }.issubset(
        column_names(MemoryFactRecord)
    ),
    "evidence_fields_complete": {
        "evidence_id",
        "thread_id",
        "tool_name",
        "tool_call_id",
        "claim_types",
        "request_json",
        "result_json",
        "status",
        "observed_at",
        "expires_at",
        "metadata_json",
    }.issubset(
        column_names(ToolEvidenceRecord)
    ),
    "message_thread_foreign_key": (
        "chat_threads.thread_id"
        in foreign_key_targets(
            "chat_messages"
        )
    ),
    "message_parent_foreign_key": (
        "chat_messages.message_id"
        in foreign_key_targets(
            "chat_messages"
        )
    ),
    "state_thread_foreign_key": (
        "chat_threads.thread_id"
        in foreign_key_targets(
            "chat_conversation_states"
        )
    ),
    "memory_thread_foreign_key": (
        "chat_threads.thread_id"
        in foreign_key_targets(
            "chat_memory_facts"
        )
    ),
    "evidence_thread_foreign_key": (
        "chat_threads.thread_id"
        in foreign_key_targets(
            "chat_tool_evidence"
        )
    ),
    "canonical_init_registers_chat_models": (
        "chat_public.persistence"
        in database_text
    ),
    "no_separate_chat_engine": (
        "create_async_engine"
        not in models_text
    ),
    "no_separate_chat_base": (
        "DeclarativeBase"
        not in models_text
        and "declarative_base"
        not in models_text
    ),
}

certified = all(checks.values())

table_details = {}

for table_name, model_type in model_map.items():
    table_details[table_name] = {
        "columns": sorted(
            column_names(model_type)
        ),
        "foreign_keys": sorted(
            foreign_key_targets(table_name)
        ),
        "indexes": sorted(
            index.name
            for index in Base.metadata.tables[
                table_name
            ].indexes
            if index.name
        ),
    }

result = {
    "phase": "134B2_CHAT_PERSISTENCE_MODELS",
    "checks": checks,
    "registered_chat_tables": sorted(
        expected_tables
        & registered_tables
    ),
    "table_details": table_details,
    "behavior": {
        "database_connection_attempted": False,
        "database_tables_created_now": False,
        "live_chat_wired": False,
        "messages_persisted": False,
        "ollama_context_changed": False,
        "streaming_enabled": False,
        "broker_execution_changed": False,
    },
    "certified": certified,
    "recommended_next_phase": (
        "134B3_CONVERSATION_STORE_IMPLEMENTATION"
        if certified
        else "134B2_CHAT_MODEL_REPAIR"
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
    / "134B2_chat_persistence_models_latest.json"
)

output_txt = (
    output_dir
    / "134B2_chat_persistence_models_latest.txt"
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
        "REGISTERED CHAT TABLES",
    ]
)

for table_name in sorted(
    expected_tables & registered_tables
):
    lines.append(table_name)

lines.extend(
    [
        "",
        "BEHAVIOR",
        "database_connection_attempted: False",
        "database_tables_created_now: False",
        "live_chat_wired: False",
        "messages_persisted: False",
        "ollama_context_changed: False",
        "streaming_enabled: False",
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
