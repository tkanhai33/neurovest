"""
134C_CONTEXT_ASSEMBLER_AND_SUMMARY_MEMORY

Builds bounded, persistent conversation context for NeuroVest chat.

Context sources:
- persistent thread summary
- active conversation state
- remembered terms
- durable memory facts
- recent messages
- stored tool evidence

This module also performs conservative deterministic memory extraction.

It does not:
- invent tool results
- claim market simulations occurred
- fetch current market data
- enable streaming
- change broker execution
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import json
import re

from backend.app.stacks.chat_public.contracts import (
    ChatMessage,
    ConversationState,
    MemoryFact,
)
from backend.app.stacks.chat_public.context_loader import (
    architecture_dashboard,
    load_component_overlay_v1,
    load_dependency_graph_v1,
    load_repo_context,
    repo_component_hotspots,
    repo_hotspots,
)

from backend.app.stacks.chat_public.conversation_service import (
    conversation_store,
)

from backend.app.stacks.chat_public.prompt_composer import (
    compose_prompt,
)


CONTEXT_VERSION = "134C.v1"

MAX_RECENT_MESSAGES = 16
MAX_MEMORY_FACTS = 40
MAX_TOOL_EVIDENCE = 12
MAX_SUMMARY_CHARACTERS = 3000
MAX_PROMPT_CHARACTERS = 14000


@dataclass(frozen=True)
class AssembledChatContext:
    thread_id: str
    prompt: str
    summary: str
    recent_message_count: int
    memory_count: int
    evidence_count: int
    remembered_terms: dict[str, str]
    active_strategy: dict[str, Any] | None
    portfolio_context: dict[str, Any]
    context_version: str = CONTEXT_VERSION


def _compact_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def _clean_text(value: str) -> str:
    return " ".join(value.strip().split())


def _bounded(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value

    return value[: max(0, limit - 3)].rstrip() + "..."


def _format_recent_messages(
    messages: list[ChatMessage],
) -> str:
    lines: list[str] = []

    for message in messages:
        role = message.role.upper()
        content = _bounded(
            _clean_text(message.content),
            1200,
        )

        lines.append(f"{role}: {content}")

    return "\n".join(lines) or "(none)"


def _format_memories(
    memories: list[MemoryFact],
) -> str:
    lines: list[str] = []

    for memory in memories:
        lines.append(
            "- "
            f"{memory.key} = "
            f"{_bounded(_compact_json(memory.value), 700)} "
            f"(confidence={memory.confidence:.2f})"
        )

    return "\n".join(lines) or "(none)"


def _format_evidence(
    evidence: list[Any],
) -> str:
    lines: list[str] = []

    for item in evidence:
        lines.append(
            "- "
            f"tool={item.tool_name}; "
            f"status={item.status}; "
            f"claims={','.join(item.claim_types) or 'none'}; "
            f"result={_bounded(_compact_json(item.result), 700)}"
        )

    return "\n".join(lines) or "(none)"


def _safe_loader(
    loader: Any,
    fallback: Any,
) -> Any:
    try:
        return loader()
    except Exception as exc:
        return {
            "available": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "fallback": fallback,
        }


def _build_intent_overlay(
    intent_metadata: dict[str, Any] | None,
) -> list[tuple[str, str]]:
    """
    Build bounded, evidence-grounded prompt overlays.

    This function does not execute trades, brokers, mutations, external
    providers, tests, or repository modifications.
    """

    metadata = dict(intent_metadata or {})

    family = str(
        metadata.get(
            "family",
            "GENERAL",
        )
    ).upper()

    subtype = str(
        metadata.get(
            "subtype",
            "discussion",
        )
    )

    developer_mode = bool(
        metadata.get(
            "developer_mode",
            False,
        )
    )

    self_evaluation = bool(
        metadata.get(
            "self_evaluation",
            False,
        )
    )

    architecture_mode = bool(
        metadata.get(
            "architecture_mode",
            False,
        )
    )

    requires_repo_context = bool(
        metadata.get(
            "requires_repo_context",
            False,
        )
    )

    requires_architecture_context = bool(
        metadata.get(
            "requires_architecture_context",
            False,
        )
    )

    sections: list[tuple[str, str]] = [
        (
            "CONVERSATION CLASSIFICATION",
            (
                f"family={family}; "
                f"subtype={subtype}; "
                f"developer_mode={developer_mode}; "
                f"self_evaluation={self_evaluation}; "
                f"architecture_mode={architecture_mode}"
            ),
        )
    ]

    if not developer_mode:
        return sections

    sections.append(
        (
            "DEVELOPER MODE",
            (
                "The current user message is classified as a NeuroVest "
                "developer conversation. Respond as the software assistant "
                "inside NeuroVest, not as a generic chatbot. Be direct, "
                "technical, practical, and grounded in the evidence included "
                "in this prompt."
            ),
        )
    )

    if self_evaluation:
        sections.append(
            (
                "SELF-REFLECTION MODE",
                (
                    "Perform bounded software self-evaluation. Assess Neuro's "
                    "current implemented capabilities, observable limitations, "
                    "missing integrations, reliability concerns, and the "
                    "highest-impact next engineering steps. Do not describe "
                    "emotions, personal desires, private experiences, or "
                    "imaginary training needs. Do not claim that a remote "
                    "server, network issue, tool, test, API, provider, or "
                    "repository inspection occurred unless evidence below "
                    "supports that claim. Clearly separate proven facts, "
                    "reasonable inferences, and unknowns."
                ),
            )
        )

    if architecture_mode:
        sections.append(
            (
                "ARCHITECTURE REVIEW MODE",
                (
                    "Review architecture using only the repository and "
                    "architecture evidence provided below. Identify active "
                    "boundaries, coupling, drift, hotspots, missing context, "
                    "and minimal repair or improvement boundaries. Do not "
                    "invent files, services, routes, tests, or qualifications."
                ),
            )
        )

    if requires_repo_context:
        repo_context = _safe_loader(
            lambda: load_repo_context(
                limit=10,
            ),
            {
                "file_count": 0,
                "sample_files": [],
            },
        )

        dependency_graph = _safe_loader(
            load_dependency_graph_v1,
            {
                "nodes": [],
                "edges": [],
                "top_imported": [],
                "top_importers": [],
            },
        )

        dependency_hotspots = _safe_loader(
            lambda: repo_hotspots(
                limit=8,
            ),
            {
                "hotspot_count": 0,
                "hotspots": [],
            },
        )

        component_overlay = _safe_loader(
            load_component_overlay_v1,
            {
                "components": {},
                "component_edges": {},
            },
        )

        component_hotspots = _safe_loader(
            lambda: repo_component_hotspots(
                limit=8,
            ),
            {
                "hotspot_count": 0,
                "hotspots": [],
            },
        )

        dependency_summary = {
            "node_count": len(
                dependency_graph.get(
                    "nodes",
                    [],
                )
            )
            if isinstance(
                dependency_graph,
                dict,
            )
            else 0,
            "edge_count": len(
                dependency_graph.get(
                    "edges",
                    [],
                )
            )
            if isinstance(
                dependency_graph,
                dict,
            )
            else 0,
            "top_imported": (
                dependency_graph.get(
                    "top_imported",
                    [],
                )[:8]
                if isinstance(
                    dependency_graph,
                    dict,
                )
                else []
            ),
            "top_importers": (
                dependency_graph.get(
                    "top_importers",
                    [],
                )[:8]
                if isinstance(
                    dependency_graph,
                    dict,
                )
                else []
            ),
        }

        component_summary = {
            "component_count": len(
                component_overlay.get(
                    "components",
                    {},
                )
            )
            if isinstance(
                component_overlay,
                dict,
            )
            else 0,
            "component_edge_groups": len(
                component_overlay.get(
                    "component_edges",
                    {},
                )
            )
            if isinstance(
                component_overlay,
                dict,
            )
            else 0,
        }

        sections.extend(
            [
                (
                    "REPOSITORY SNAPSHOT",
                    _bounded(
                        _compact_json(
                            repo_context
                        ),
                        1800,
                    ),
                ),
                (
                    "DEPENDENCY GRAPH SUMMARY",
                    _bounded(
                        _compact_json(
                            dependency_summary
                        ),
                        1800,
                    ),
                ),
                (
                    "REPOSITORY HOTSPOTS",
                    _bounded(
                        _compact_json(
                            dependency_hotspots
                        ),
                        1800,
                    ),
                ),
                (
                    "COMPONENT SUMMARY",
                    _bounded(
                        _compact_json(
                            component_summary
                        ),
                        1000,
                    ),
                ),
                (
                    "COMPONENT HOTSPOTS",
                    _bounded(
                        _compact_json(
                            component_hotspots
                        ),
                        1800,
                    ),
                ),
            ]
        )

    if requires_architecture_context:
        dashboard = _safe_loader(
            architecture_dashboard,
            {
                "found": False,
                "status": None,
                "drift_count": None,
                "summary_text": "",
                "dashboard": {},
            },
        )

        if isinstance(
            dashboard,
            dict,
        ):
            architecture_summary = {
                "found": dashboard.get(
                    "found",
                    False,
                ),
                "status": dashboard.get(
                    "status",
                ),
                "drift_count": dashboard.get(
                    "drift_count",
                ),
                "summary_text": _bounded(
                    str(
                        dashboard.get(
                            "summary_text",
                            "",
                        )
                    ),
                    2200,
                ),
            }
        else:
            architecture_summary = {
                "found": False,
                "status": None,
                "drift_count": None,
                "summary_text": "",
            }

        sections.append(
            (
                "ARCHITECTURE HEALTH",
                _bounded(
                    _compact_json(
                        architecture_summary
                    ),
                    2600,
                ),
            )
        )

    sections.append(
        (
            "DEVELOPER RESPONSE FORMAT",
            (
                "When the user asks how to improve Neuro, answer with: "
                "1) what is currently working, "
                "2) the most important proven limitations, "
                "3) the highest-impact next improvements in priority order, "
                "4) what evidence is still missing. "
                "Avoid generic statements such as needing more training data "
                "unless repository evidence specifically proves that need."
            ),
        )
    )

    return sections


async def assemble_chat_context(
    *,
    thread_id: str,
    current_message: str,
    intent_metadata: dict[str, Any] | None = None,
    role_overlay: str | None = None,
) -> AssembledChatContext:
    bundle = await conversation_store.load_context_bundle(
        thread_id,
        message_limit=MAX_RECENT_MESSAGES,
        memory_limit=MAX_MEMORY_FACTS,
        evidence_limit=MAX_TOOL_EVIDENCE,
    )

    state = bundle["conversation_state"]
    memories = bundle["memory_facts"]
    evidence = bundle["tool_evidence"]
    messages = bundle["messages"]

    summary = _bounded(
        state.summary or "",
        MAX_SUMMARY_CHARACTERS,
    )

    remembered_terms = dict(
        state.remembered_terms or {}
    )

    active_strategy = (
        dict(state.active_strategy)
        if state.active_strategy
        else None
    )

    portfolio_context = dict(
        state.portfolio_context or {}
    )

    intent_sections = _build_intent_overlay(
        intent_metadata
    )

    sections = [
        (
            "SYSTEM ROLE\n"
            "You are Neuro, the local NeuroVest assistant. "
            "You are protective, direct, and evidence-aware."
        ),
        (
            "TRUTH BOUNDARY\n"
            "Stored conversation memory may be used to recall what "
            "the user or assistant previously discussed. "
            "Do not claim a simulation, live quote, stock gain, trade, "
            "backtest, provider result, or tool execution occurred unless "
            "corresponding tool evidence is included below. "
            "Clearly distinguish user-provided facts, proposed ideas, "
            "validated results, and current external facts. "
            "Never reinterpret a remembered strategy abbreviation as a "
            "stock ticker when the stored memory defines it as a strategy."
        ),
        *[
            (
                f"{title}\n"
                f"{body}"
            )
            for title, body in intent_sections
        ],
        (
            "THREAD SUMMARY\n"
            f"{summary or '(none)'}"
        ),
        (
            "REMEMBERED TERMS\n"
            f"{_compact_json(remembered_terms) if remembered_terms else '(none)'}"
        ),
        (
            "ACTIVE STRATEGY\n"
            f"{_compact_json(active_strategy) if active_strategy else '(none)'}"
        ),
        (
            "PORTFOLIO CONTEXT\n"
            f"{_compact_json(portfolio_context) if portfolio_context else '(none)'}"
        ),
        (
            "DURABLE MEMORY FACTS\n"
            f"{_format_memories(memories)}"
        ),
        (
            "AVAILABLE TOOL EVIDENCE\n"
            f"{_format_evidence(evidence)}"
        ),
        (
            "RECENT CONVERSATION\n"
            f"{_format_recent_messages(messages)}"
        ),
        (
            "CURRENT USER MESSAGE\n"
            f"{_clean_text(current_message)}"
        ),
        (
            "RESPONSE REQUIREMENTS\n"
            "Answer the current user message using the retained thread "
            "context when relevant. Correct prior misunderstandings. "
            "Do not pretend unavailable tools ran. Do not promise a specific "
            "investment return. Keep paper and live execution boundaries clear."
        ),
    ]

    if role_overlay:
        sections.insert(
            2,
            role_overlay,
        )

    composition = compose_prompt(
        sections,
        max_characters=MAX_PROMPT_CHARACTERS,
        bounder=_bounded,
    )

    return AssembledChatContext(
        thread_id=thread_id,
        prompt=composition.prompt,
        summary=summary,
        recent_message_count=len(messages),
        memory_count=len(memories),
        evidence_count=len(evidence),
        remembered_terms=remembered_terms,
        active_strategy=active_strategy,
        portfolio_context=portfolio_context,
    )


def extract_remembered_terms(
    user_message: str,
) -> dict[str, str]:
    clean = _clean_text(user_message)

    patterns = [
        re.compile(
            r"\b([A-Z][A-Z0-9-]{1,12})\s+"
            r"(?:means|stands\s+for|refers\s+to)\s+"
            r"(.+?)(?:[.!?]|$)",
            re.IGNORECASE,
        ),
        re.compile(
            r"\bdefine\s+([A-Z][A-Z0-9-]{1,12})\s+"
            r"as\s+(.+?)(?:[.!?]|$)",
            re.IGNORECASE,
        ),
    ]

    found: dict[str, str] = {}

    for pattern in patterns:
        for match in pattern.finditer(clean):
            abbreviation = match.group(1).upper()
            meaning = _clean_text(match.group(2))

            if (
                2 <= len(abbreviation) <= 12
                and 2 <= len(meaning) <= 160
            ):
                found[abbreviation] = meaning

    return found


def extract_portfolio_context(
    user_message: str,
) -> dict[str, Any]:
    clean = _clean_text(user_message)

    patterns = [
        re.compile(
            r"(?:portfolio|account)"
            r".{0,45}?"
            r"(?:worth|value|valued\s+at|around|approximately)"
            r".{0,20}?"
            r"\$?\s*([0-9][0-9,]*(?:\.[0-9]+)?)"
            r"\s*(CAD|USD)?",
            re.IGNORECASE,
        ),
        re.compile(
            r"\$?\s*([0-9][0-9,]*(?:\.[0-9]+)?)"
            r"\s*(CAD|USD)"
            r".{0,45}?"
            r"(?:portfolio|account)",
            re.IGNORECASE,
        ),
    ]

    for pattern in patterns:
        match = pattern.search(clean)

        if not match:
            continue

        value = float(
            match.group(1).replace(",", "")
        )

        currency = (
            match.group(2).upper()
            if match.lastindex
            and match.lastindex >= 2
            and match.group(2)
            else "CAD"
        )

        return {
            "value": value,
            "currency": currency,
            "value_cad": (
                value
                if currency == "CAD"
                else None
            ),
            "source": "user_statement",
            "verification": "unverified_user_context",
        }

    return {}


def extract_strategy_context(
    *,
    user_message: str,
    assistant_message: str,
    strategy_capture: Any,
    remembered_terms: dict[str, str],
) -> dict[str, Any] | None:
    if isinstance(strategy_capture, dict):
        candidate = dict(strategy_capture)

        name = (
            candidate.get("name")
            or candidate.get("strategy_name")
        )

        if name:
            candidate.setdefault(
                "status",
                "proposed_not_validated",
            )
            candidate.setdefault(
                "source",
                "strategy_proposal_capture",
            )
            return candidate

    combined = (
        f"{user_message}\n{assistant_message}"
    )

    for abbreviation, meaning in remembered_terms.items():
        if (
            "strategy" in combined.lower()
            and abbreviation in combined
        ):
            return {
                "name": meaning,
                "abbreviation": abbreviation,
                "status": "proposed_not_validated",
                "source": "conversation_memory",
            }

    return None


def build_summary(
    *,
    previous_summary: str,
    remembered_terms: dict[str, str],
    active_strategy: dict[str, Any] | None,
    portfolio_context: dict[str, Any],
    latest_user_message: str,
    latest_assistant_message: str,
) -> str:
    summary_lines: list[str] = []

    previous = _clean_text(previous_summary)

    if previous:
        summary_lines.append(previous)

    if remembered_terms:
        terms = ", ".join(
            f"{key} means {value}"
            for key, value in sorted(
                remembered_terms.items()
            )
        )
        summary_lines.append(
            f"Remembered terminology: {terms}."
        )

    if active_strategy:
        strategy_name = (
            active_strategy.get("name")
            or active_strategy.get(
                "strategy_name"
            )
            or "unnamed strategy"
        )

        strategy_status = active_strategy.get(
            "status",
            "proposed_not_validated",
        )

        summary_lines.append(
            "Active strategy discussion: "
            f"{strategy_name} "
            f"(status: {strategy_status})."
        )

    if portfolio_context:
        value = (
            portfolio_context.get("value_cad")
            or portfolio_context.get("value")
        )
        currency = portfolio_context.get(
            "currency",
            "CAD",
        )

        if value is not None:
            summary_lines.append(
                "User-stated portfolio context: "
                f"approximately {value:g} {currency}; "
                "not independently verified."
            )

    summary_lines.append(
        "Latest turn: user asked "
        f"'{_bounded(_clean_text(latest_user_message), 350)}' "
        "and Neuro replied "
        f"'{_bounded(_clean_text(latest_assistant_message), 500)}'."
    )

    deduplicated: list[str] = []

    for line in summary_lines:
        if line and line not in deduplicated:
            deduplicated.append(line)

    return _bounded(
        " ".join(deduplicated),
        MAX_SUMMARY_CHARACTERS,
    )


async def update_summary_memory(
    *,
    thread_id: str,
    user_message: ChatMessage,
    assistant_message: ChatMessage,
    strategy_capture: Any = None,
) -> ConversationState:
    state = await conversation_store.get_conversation_state(
        thread_id
    )

    extracted_terms = extract_remembered_terms(
        user_message.content
    )

    remembered_terms = {
        **dict(state.remembered_terms or {}),
        **extracted_terms,
    }

    extracted_portfolio = extract_portfolio_context(
        user_message.content
    )

    portfolio_context = {
        **dict(state.portfolio_context or {}),
        **extracted_portfolio,
    }

    active_strategy = extract_strategy_context(
        user_message=user_message.content,
        assistant_message=assistant_message.content,
        strategy_capture=strategy_capture,
        remembered_terms=remembered_terms,
    )

    if active_strategy is None:
        active_strategy = state.active_strategy

    for abbreviation, meaning in extracted_terms.items():
        await conversation_store.upsert_memory_fact(
            MemoryFact(
                thread_id=thread_id,
                key=(
                    "conversation.term."
                    f"{abbreviation}"
                ),
                value={
                    "abbreviation": abbreviation,
                    "meaning": meaning,
                    "source": "user_statement",
                },
                confidence=1.0,
                source_message_id=(
                    user_message.message_id
                ),
                metadata={
                    "phase": (
                        "134C_CONTEXT_ASSEMBLER_AND_SUMMARY_MEMORY"
                    ),
                    "memory_type": "remembered_term",
                },
            )
        )

    if extracted_portfolio:
        await conversation_store.upsert_memory_fact(
            MemoryFact(
                thread_id=thread_id,
                key="portfolio.user_stated_value",
                value=extracted_portfolio,
                confidence=1.0,
                source_message_id=(
                    user_message.message_id
                ),
                metadata={
                    "phase": (
                        "134C_CONTEXT_ASSEMBLER_AND_SUMMARY_MEMORY"
                    ),
                    "memory_type": "portfolio_context",
                    "independently_verified": False,
                },
            )
        )

    summary = build_summary(
        previous_summary=state.summary,
        remembered_terms=remembered_terms,
        active_strategy=active_strategy,
        portfolio_context=portfolio_context,
        latest_user_message=user_message.content,
        latest_assistant_message=(
            assistant_message.content
        ),
    )

    updated_state = ConversationState(
        thread_id=thread_id,
        summary=summary,
        active_entities=dict(
            state.active_entities or {}
        ),
        active_strategy=active_strategy,
        portfolio_context=portfolio_context,
        pending_tasks=state.pending_tasks,
        remembered_terms=remembered_terms,
        last_message_id=(
            assistant_message.message_id
        ),
        metadata={
            **dict(state.metadata or {}),
            "context_version": CONTEXT_VERSION,
            "history_injected_into_model": True,
            "summary_memory_active": True,
        },
    )

    return await conversation_store.upsert_conversation_state(
        updated_state
    )
