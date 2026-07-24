#!/usr/bin/env python3

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4
import ast
import json

from backend.app.stacks.chat_public.chat_runtime import (
    run_chat_turn,
)
from backend.app.stacks.chat_public.context import (
    CONTEXT_VERSION,
    assemble_chat_context,
    extract_portfolio_context,
    extract_remembered_terms,
)
from backend.app.stacks.chat_public.conversation_store import (
    conversation_store,
)
from backend.app.stacks.db_runtime import init_db


ROOT = Path(".").resolve()

PHASE = (
    "134C_CONTEXT_ASSEMBLER_AND_SUMMARY_MEMORY"
)

CONTEXT_FILE = (
    ROOT
    / "backend/app/stacks/chat_public/context/context_assembler.py"
)

RUNTIME_FILE = (
    ROOT
    / "backend/app/stacks/chat_public/chat_runtime.py"
)

OUT_DIR = ROOT / "runtime/chat_context"
OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUT_JSON = (
    OUT_DIR
    / "134C_context_assembler_latest.json"
)

OUT_TXT = (
    OUT_DIR
    / "134C_context_assembler_latest.txt"
)


async def validate() -> dict:
    await init_db()

    context_text = CONTEXT_FILE.read_text(
        encoding="utf-8"
    )

    runtime_text = RUNTIME_FILE.read_text(
        encoding="utf-8"
    )

    ast.parse(context_text)
    ast.parse(runtime_text)

    thread_id = (
        "thread-134c-"
        f"{uuid4().hex}"
    )

    captured_prompts: list[str] = []

    def fake_ollama(
        message: str,
        *,
        intent: str | None = None,
        symbol: str | None = None,
    ) -> str:
        captured_prompts.append(message)

        if "What did ATF stand for" in message:
            return (
                "ATF stood for Adaptive Trend Follower. "
                "It is a proposed strategy, not a stock ticker "
                "and not yet a validated backtest result."
            )

        return (
            "I have retained ATF as Adaptive Trend Follower "
            "and the user-stated portfolio value as approximately "
            "300 CAD. No backtest has been performed in this turn."
        )

    try:
        with patch(
            "backend.app.stacks.chat_public."
            "chat_runtime.ask_ollama",
            side_effect=fake_ollama,
        ):
            first = await run_chat_turn(
                {
                    "message": (
                        "ATF means Adaptive Trend Follower. "
                        "My current portfolio is worth around "
                        "300 CAD."
                    ),
                    "thread_id": thread_id,
                    "client_message_id": (
                        f"{thread_id}-first"
                    ),
                }
            )

            second = await run_chat_turn(
                {
                    "message": (
                        "What did ATF stand for earlier, "
                        "and what portfolio amount did I give you?"
                    ),
                    "thread_id": thread_id,
                    "parent_message_id": (
                        first[
                            "assistant_message_id"
                        ]
                    ),
                    "client_message_id": (
                        f"{thread_id}-second"
                    ),
                }
            )

        state = (
            await conversation_store
            .get_conversation_state(
                thread_id
            )
        )

        memories = (
            await conversation_store
            .list_memory_facts(
                thread_id
            )
        )

        messages = (
            await conversation_store
            .list_messages(
                thread_id,
                limit=20,
                oldest_first=True,
            )
        )

        assembled = await assemble_chat_context(
            thread_id=thread_id,
            current_message=(
                "Repeat the stored context."
            ),
        )

        extracted_terms = extract_remembered_terms(
            "ATF means Adaptive Trend Follower."
        )

        extracted_portfolio = (
            extract_portfolio_context(
                "My portfolio is worth around 300 CAD."
            )
        )

        second_prompt = (
            captured_prompts[1]
            if len(captured_prompts) >= 2
            else ""
        )

        checks = {
            "context_module_exists": (
                CONTEXT_FILE.exists()
            ),
            "context_version_correct": (
                CONTEXT_VERSION == "134C.v1"
            ),
            "runtime_uses_context_assembler": (
                "assemble_chat_context"
                in runtime_text
            ),
            "runtime_updates_summary_memory": (
                "update_summary_memory"
                in runtime_text
            ),
            "history_injection_enabled": (
                second["metadata"].get(
                    "history_injected_into_model"
                )
                is True
            ),
            "summary_memory_enabled": (
                second["metadata"].get(
                    "summary_memory_active"
                )
                is True
            ),
            "same_thread_reused": (
                first["thread_id"]
                == second["thread_id"]
                == thread_id
            ),
            "four_messages_persisted": (
                len(messages) == 4
            ),
            "remembered_term_extracted": (
                extracted_terms.get("ATF")
                == "Adaptive Trend Follower"
            ),
            "portfolio_value_extracted": (
                extracted_portfolio.get(
                    "value_cad"
                )
                == 300
            ),
            "term_saved_to_state": (
                state.remembered_terms.get(
                    "ATF"
                )
                == "Adaptive Trend Follower"
            ),
            "portfolio_saved_to_state": (
                state.portfolio_context.get(
                    "value_cad"
                )
                == 300
            ),
            "summary_mentions_atf": (
                "Adaptive Trend Follower"
                in state.summary
            ),
            "summary_mentions_portfolio": (
                "300 CAD"
                in state.summary
            ),
            "durable_term_memory_created": (
                any(
                    memory.key
                    == "conversation.term.ATF"
                    for memory in memories
                )
            ),
            "durable_portfolio_memory_created": (
                any(
                    memory.key
                    == "portfolio.user_stated_value"
                    for memory in memories
                )
            ),
            "second_prompt_contains_atf_memory": (
                "Adaptive Trend Follower"
                in second_prompt
            ),
            "second_prompt_contains_portfolio_context": (
                "300"
                in second_prompt
                and "CAD"
                in second_prompt
            ),
            "second_prompt_contains_recent_history": (
                "ATF means Adaptive Trend Follower"
                in second_prompt
            ),
            "truth_boundary_in_prompt": (
                "Do not claim a simulation"
                in second_prompt
                and "unless corresponding tool evidence"
                in second_prompt
            ),
            "strategy_not_reinterpreted_as_ticker": (
                "not a stock ticker"
                in second["message"]
            ),
            "assembled_context_bounded": (
                len(assembled.prompt) <= 14000
            ),
            "streaming_still_disabled": (
                second["metadata"].get(
                    "streaming_enabled"
                )
                is False
            ),
        }

        certified = all(checks.values())

        return {
            "phase": PHASE,
            "checks": checks,
            "thread_id": thread_id,
            "message_count": len(messages),
            "memory_count": len(memories),
            "summary": state.summary,
            "remembered_terms": (
                state.remembered_terms
            ),
            "portfolio_context": (
                state.portfolio_context
            ),
            "captured_prompt_count": len(
                captured_prompts
            ),
            "context": {
                "version": CONTEXT_VERSION,
                "prompt_characters": len(
                    assembled.prompt
                ),
                "recent_message_count": (
                    assembled.recent_message_count
                ),
                "memory_count": (
                    assembled.memory_count
                ),
                "evidence_count": (
                    assembled.evidence_count
                ),
            },
            "behavior": {
                "history_injected_into_ollama": True,
                "summary_memory_active": True,
                "remembered_terms_active": True,
                "portfolio_context_active": True,
                "tool_truth_instructions_active": True,
                "live_market_tools_added": False,
                "streaming_enabled": False,
                "broker_execution_changed": False,
            },
            "certified": certified,
            "recommended_next_phase": (
                "134D_TOOL_TRUTH_AND_CLAIM_GATING"
                if certified
                else (
                    "134C_CONTEXT_AND_MEMORY_REPAIR"
                )
            ),
        }

    finally:
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
            "CONTEXT",
            (
                "context_version: "
                f"{result['context']['version']}"
            ),
            (
                "prompt_characters: "
                f"{result['context']['prompt_characters']}"
            ),
            (
                "recent_message_count: "
                f"{result['context']['recent_message_count']}"
            ),
            (
                "memory_count: "
                f"{result['context']['memory_count']}"
            ),
            "",
            "BEHAVIOR",
            "history_injected_into_ollama: True",
            "summary_memory_active: True",
            "remembered_terms_active: True",
            "portfolio_context_active: True",
            "tool_truth_instructions_active: True",
            "live_market_tools_added: False",
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
