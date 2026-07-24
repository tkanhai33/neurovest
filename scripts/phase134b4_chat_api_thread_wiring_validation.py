#!/usr/bin/env python3

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from unittest.mock import patch

from backend.app.stacks.chat_public.conversation_store import (
    conversation_store,
)
from backend.app.stacks.chat_public.chat_runtime import (
    run_chat_turn,
)
from backend.app.stacks.db_runtime import init_db


ROOT = Path(".").resolve()

PHASE = "134B4_CHAT_API_THREAD_WIRING"

OUT_DIR = ROOT / "runtime/chat_persistence"
OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUT_JSON = (
    OUT_DIR
    / "134B4_chat_api_thread_wiring_latest.json"
)

OUT_TXT = (
    OUT_DIR
    / "134B4_chat_api_thread_wiring_latest.txt"
)


async def validate() -> dict:
    await init_db()

    first_client_id = (
        "134B4-validation-client-message-1"
    )

    second_client_id = (
        "134B4-validation-client-message-2"
    )

    ollama_responses = [
        (
            "ATF is being discussed as "
            "Adaptive Trend Follower."
        ),
        (
            "The same thread is active, but "
            "historical context injection begins "
            "in Phase 134C."
        ),
    ]

    call_count = 0

    def fake_ollama(
        message: str,
        *,
        intent: str | None = None,
        symbol: str | None = None,
    ) -> str:
        nonlocal call_count

        response = ollama_responses[
            min(
                call_count,
                len(ollama_responses) - 1,
            )
        ]

        call_count += 1
        return response

    thread_id = None

    try:
        with patch(
            "backend.app.stacks.chat_public."
            "chat_runtime.ask_ollama",
            side_effect=fake_ollama,
        ):
            first = await run_chat_turn(
                {
                    "message": (
                        "ATF means Adaptive Trend "
                        "Follower."
                    ),
                    "client_message_id": (
                        first_client_id
                    ),
                }
            )

            thread_id = first["thread_id"]

            second = await run_chat_turn(
                {
                    "message": (
                        "Are we still using the same "
                        "conversation thread?"
                    ),
                    "thread_id": thread_id,
                    "parent_message_id": (
                        first[
                            "assistant_message_id"
                        ]
                    ),
                    "client_message_id": (
                        second_client_id
                    ),
                }
            )

            replay = await run_chat_turn(
                {
                    "message": (
                        "This body is ignored because "
                        "the client ID was already used."
                    ),
                    "thread_id": thread_id,
                    "client_message_id": (
                        first_client_id
                    ),
                }
            )

        stored_thread = (
            await conversation_store
            .require_thread(thread_id)
        )

        stored_messages = (
            await conversation_store
            .list_messages(
                thread_id,
                limit=20,
                oldest_first=True,
            )
        )

        roles = [
            message.role
            for message in stored_messages
        ]

        checks = {
            "first_request_created_thread": (
                bool(first["thread_id"])
            ),
            "first_user_message_saved": (
                bool(first["user_message_id"])
            ),
            "first_assistant_message_saved": (
                bool(
                    first["assistant_message_id"]
                )
            ),
            "second_request_reused_thread": (
                second["thread_id"]
                == first["thread_id"]
            ),
            "second_parent_preserved": (
                stored_messages[2]
                .parent_message_id
                == first[
                    "assistant_message_id"
                ]
            ),
            "four_messages_persisted": (
                len(stored_messages) == 4
            ),
            "message_roles_ordered": (
                roles
                == [
                    "user",
                    "assistant",
                    "user",
                    "assistant",
                ]
            ),
            "thread_message_count_correct": (
                stored_thread.message_count == 4
            ),
            "response_contains_thread_id": (
                "thread_id" in first
                and "thread_id" in second
            ),
            "response_contains_message_ids": (
                bool(first["user_message_id"])
                and bool(
                    first[
                        "assistant_message_id"
                    ]
                )
            ),
            "legacy_response_preserved": (
                first.get("response", {}).get(
                    "message"
                )
                == first["message"]
            ),
            "retry_replayed_existing_reply": (
                replay[
                    "assistant_message_id"
                ]
                == first[
                    "assistant_message_id"
                ]
            ),
            "retry_did_not_add_messages": (
                len(
                    await conversation_store
                    .list_messages(
                        thread_id,
                        limit=20,
                    )
                )
                == 4
            ),
            "retry_did_not_call_ollama_again": (
                call_count == 2
            ),
            "streaming_remains_disabled": (
                first["metadata"].get(
                    "streaming_enabled"
                )
                is False
            ),
            "history_not_yet_injected": (
                first["metadata"].get(
                    "history_injected_into_model"
                )
                is False
            ),
        }

        certified = all(checks.values())

        return {
            "phase": PHASE,
            "checks": checks,
            "thread_id": thread_id,
            "message_count": len(
                stored_messages
            ),
            "ollama_call_count": call_count,
            "behavior": {
                "live_chat_backend_wired": True,
                "thread_created_and_reused": True,
                "messages_persisted": True,
                "frontend_thread_retention_wired": False,
                "history_injected_into_ollama": False,
                "streaming_enabled": False,
                "broker_execution_changed": False,
            },
            "certified": certified,
            "recommended_next_phase": (
                "134B5_FRONTEND_THREAD_RETENTION"
                if certified
                else (
                    "134B4_CHAT_API_THREAD_WIRING_REPAIR"
                )
            ),
        }

    finally:
        if thread_id:
            await conversation_store.delete_thread_for_testing(
                thread_id
            )


async def main() -> int:
    result = await validate()

    OUT_JSON.write_text(
        json.dumps(
            result,
            indent=2,
        ),
        encoding="utf-8",
    )

    lines = [
        result["phase"],
        "",
        f"certified: {result['certified']}",
        "",
        "CHECKS",
    ]

    for name, passed in result[
        "checks"
    ].items():
        lines.append(
            f"{name}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

    lines.extend(
        [
            "",
            "BEHAVIOR",
            "live_chat_backend_wired: True",
            "thread_created_and_reused: True",
            "messages_persisted: True",
            "frontend_thread_retention_wired: False",
            "history_injected_into_ollama: False",
            "streaming_enabled: False",
            "broker_execution_changed: False",
            "",
            (
                "next: "
                f"{result['recommended_next_phase']}"
            ),
        ]
    )

    OUT_TXT.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )

    return 0 if result["certified"] else 1


if __name__ == "__main__":
    raise SystemExit(
        asyncio.run(main())
    )
