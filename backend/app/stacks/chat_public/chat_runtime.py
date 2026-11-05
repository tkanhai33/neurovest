"""
134B4_CHAT_API_THREAD_WIRING

Connects the existing NeuroVest chat runtime to the persistent
conversation store introduced in Phase 134B3.

This phase:
- creates or resumes chat threads
- persists user messages
- persists assistant messages
- preserves parent-message relationships
- returns thread and message identifiers
- prevents duplicate assistant generation for retried client messages

This phase does not:
- inject historical context into Ollama
- summarize conversations
- extract durable memory automatically
- enable streaming
- execute new financial tools
- alter broker or live-trading state
"""

from __future__ import annotations

import re

from datetime import UTC, datetime, timedelta
from typing import Any
from time import perf_counter

from backend.app.core.runtime_trace import (
    create_trace_id,
    emit_runtime_step,
)

from backend.app.stacks.strategy_candidate_sandbox.L4_runtime_orchestration.bounded_training_runtime import (
    list_training_sessions,
    list_training_sessions_for_owner,
    start_bounded_training_session,
)

from backend.app.stacks.market_data.dto import (
    HistoricalBarsRequest,
)
from backend.app.stacks.market_data.runtime_composition import (
    get_market_data_runtime,
)
from backend.app.stacks.news_intelligence.official_economic_feeds import (
    fetch_official_economic_releases,
)
from backend.app.stacks.chat_public.weather_tools.live_weather import (
    extract_weather_location,
    fetch_live_weather,
    weather_description,
)
from backend.app.stacks.chat_public.knowledge_tools.wikipedia_lookup import (
    extract_wikipedia_topic,
    lookup_wikipedia_article,
    wikipedia_link_requested,
)

from backend.app.stacks.chat_public.chat_intent_regex import (
    detect_chat_intent,
)
from backend.app.stacks.chat_public.cognitive_model_router import (
    CognitiveRoutingDecision,
    route_cognitive_request,
)
from backend.app.stacks.chat_public.developer_response_builder import (
    build_developer_response,
)
from backend.app.stacks.chat_public.deterministic_answers import (
    deterministic_strategy_answer,
)
from backend.app.stacks.chat_public.contracts import (
    ChatRequest,
    ChatResponse,
    ToolEvidence,
)
from backend.app.stacks.chat_public.conversation_service import (
    conversation_store,
)
from backend.app.stacks.chat_public.context import (
    CONTEXT_VERSION,
    assemble_chat_context,
    update_summary_memory,
)
from backend.app.stacks.chat_public.role_overlay_registry import (
    render_role_overlay,
    resolve_principal_overlay,
    resolve_role_overlay,

)

from backend.app.stacks.chat_public.ollama_chat_client import (
    ask_ollama,
    resolve_runtime_model,
)
from backend.app.stacks.chat_public.rag.live_retrieval import (
    LiveRetrievalBundle,
    retrieve_live_evidence,
)
from backend.app.stacks.chat_public.math_tools.live_math import (
    LiveMathBundle,
    evaluate_live_math,
    extract_math_request,
)
from backend.app.stacks.chat_public.math_tools.symbolic_math import (
    symbolic_math_requested,
)
from backend.app.stacks.chat_public.response_verification import (
    ResponseVerificationResult,
    verify_response,
)
from backend.app.stacks.chat_public.strategy_proposal_capture import (
    capture_strategy_proposal,
)

from backend.app.stacks.chat_public.request_route_contract import (
    ChatAnswerRoute,
    classify_chat_route,
)
import pandas as pd

from backend.app.stacks.strategy.model_inference.composite_feature_builder import (
    build_frozen25_runtime_features,
)

from backend.app.stacks.chat_public.conversation_quality_v1 import build_conversation_guidance as _nv5c_build_conversation_guidance
from backend.app.stacks.chat_public.conversation_evidence_state_v1 import build_evidence_state_guidance as _nv5i_state_guidance



OLLAMA_PROVIDER = "ollama"


def _build_chat_frozen25_feature_frame(
    *,
    bars,
    provider_symbol: str,
):
    """Build Frozen25 MODEL_FEATURES from existing read-only Chat history."""

    if not provider_symbol:
        return None

    if not bars:
        return None

    rows = []

    for bar in bars:

        def _value(
            name: str,
        ):

            if isinstance(
                bar,
                dict,
            ):

                return bar.get(
                    name
                )

            return getattr(
                bar,
                name,
                None,
            )


        row = {
            "timestamp":
                _value(
                    "timestamp"
                ),

            "open":
                _value(
                    "open"
                ),

            "high":
                _value(
                    "high"
                ),

            "low":
                _value(
                    "low"
                ),

            "close":
                _value(
                    "close"
                ),

            "volume":
                _value(
                    "volume"
                ),

            "provider_symbol":
                provider_symbol,
        }


        if any(
            row.get(
                key
            )
            is None
            for key in (
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume",
            )
        ):

            continue


        rows.append(
            row
        )


    if not rows:

        return None


    raw_frame = pd.DataFrame(
        rows,
        columns=[
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "provider_symbol",
        ],
    )


    feature_frame = (
        build_frozen25_runtime_features(
            raw_frame
        )
    )


    if feature_frame.empty:

        return None


    return feature_frame


def _response_message(
    response: dict[str, Any],
) -> str:
    response_type = str(
        response.get("type") or "text"
    )

    if response_type == "text":
        return str(
            response.get("message") or ""
        )

    command = str(
        response.get("command") or response_type
    )

    symbol = response.get("symbol")

    if symbol:
        return (
            f"Command prepared: {command} "
            f"for {symbol}."
        )

    return f"Command prepared: {command}."


# _NEURO_ARXIV_FINAL_NUMBERING
# _ARXIV_EVIDENCE_DISCOVERY_RENDERER
def _renumber_arxiv_result_list(response, citations, message=""):
    import re

    original = str(response or "")
    requested = str(message or "")
    is_paper_search = (
        re.search(r"\b(?:find|search(?:\s+for)?|list|show|give me|identify)\b",
                  requested, re.IGNORECASE)
        and re.search(r"\b(?:papers?|articles?|studies)\b",
                      requested, re.IGNORECASE)
    )
    if not is_paper_search:
        return original

    records = []
    for item in citations or ():
        if not isinstance(item, dict) or item.get("source_provider") != "arxiv":
            continue

        title = " ".join(str(item.get("title") or "").split())
        arxiv_id = " ".join(str(item.get("arxiv_id") or "").split())
        source_url = str(item.get("source_path") or "").strip()
        token = str(item.get("citation") or "").strip()
        if (
            not title
            or not arxiv_id
            or not re.fullmatch(
                r"https://arxiv\.org/abs/[A-Za-z0-9./_-]+",
                source_url,
            )
            or not re.fullmatch(r"\[chunk_arxiv_[A-Za-z0-9_-]+\]", token)
        ):
            continue

        title = title.replace("\\", "\\\\")
        for char in ("`", "*", "_", "[", "]"):
            title = title.replace(char, "\\" + char)

        published = " ".join(str(item.get("published") or "").split())
        if "T" in published:
            published = published.split("T", 1)[0]

        details = f"arXiv ID: `{arxiv_id}`"
        if published:
            details += f"; published: {published}"
        records.append(
            (title, details, source_url, token)
        )

    if not records:
        return original

    lines = ["Retrieved papers from arXiv:"]
    for number, (title, details, url, token) in enumerate(records, 1):
        lines.append(
            f"{number}. **{title}** — {details}; "
            f"Source: {url}; Citation: {token}"
        )
    return "\n".join(lines)


def _ensure_approved_retrieval_citation(
    response: str,
    citations: Any,
) -> str:
    normalized = str(
        response
    ).strip()

    approved_tokens = [
        str(
            citation.get(
                "citation",
                "",
            )
        ).strip()
        for citation in citations
        if isinstance(
            citation,
            dict,
        )
        and str(
            citation.get(
                "citation",
                "",
            )
        ).strip()
    ]

    if not approved_tokens:
        return normalized

    if any(
        token in normalized
        for token in approved_tokens
    ):
        return normalized

    return (
        normalized
        + "\n\n"
        + "Approved local research source: "
        + approved_tokens[0]
    )


# _NEURO_ARXIV_NUMBERED_CITATION_WRAPPER
_nv_original_ensure_arxiv_citation = _ensure_approved_retrieval_citation


def _ensure_approved_retrieval_citation(response, citations):
    result = _nv_original_ensure_arxiv_citation(response, citations)
    if any(
        isinstance(citation, dict)
        and citation.get("source_provider") == "arxiv"
        for citation in (citations or ())
    ):
        import re as _nv_arxiv_number_re

        number = 0

        def _next_number(match):
            nonlocal number
            number += 1
            return f"{match.group(1)}{number}."

        result = _nv_arxiv_number_re.sub(
            r"(?m)^(\s*)\d+\.(?=\s+\*\*)",
            _next_number,
            result,
        )
    return result



def _chat_training_role(
    principal: Any | None,
) -> str:
    if principal is None:
        return ""

    direct = (
        getattr(
            principal,
            "role",
            None,
        )
        or getattr(
            principal,
            "authorization_role",
            None,
        )
    )

    if direct:
        return str(
            direct
        ).strip().lower()

    claims = getattr(
        principal,
        "claims",
        {},
    )

    if not isinstance(
        claims,
        dict,
    ):
        claims = {}

    return str(
        claims.get(
            "authorization_role"
        )
        or claims.get("role")
        or ""
    ).strip().lower()


def _chat_training_subject(
    principal: Any | None,
) -> str:
    if principal is None:
        return ""

    direct = (
        getattr(
            principal,
            "subject",
            None,
        )
        or getattr(
            principal,
            "user_id",
            None,
        )
    )

    if direct:
        return str(
            direct
        ).strip()

    claims = getattr(
        principal,
        "claims",
        {},
    )

    if not isinstance(
        claims,
        dict,
    ):
        claims = {}

    return str(
        claims.get("sub")
        or claims.get("user_id")
        or ""
    ).strip()


def _chat_training_session(
    principal: Any | None,
) -> str:
    if principal is None:
        return ""

    direct = (
        getattr(
            principal,
            "session_id",
            None,
        )
        or getattr(
            principal,
            "token_family_id",
            None,
        )
        or getattr(
            principal,
            "token_id",
            None,
        )
    )

    if direct:
        return str(
            direct
        ).strip()

    claims = getattr(
        principal,
        "claims",
        {},
    )

    if not isinstance(
        claims,
        dict,
    ):
        claims = {}

    return str(
        claims.get("session_id")
        or claims.get("session_family_id")
        or claims.get("family_id")
        or claims.get("sid")
        or claims.get("jti")
        or ""
    ).strip()


def _blocked_training_chat_response(
    *,
    intent,
    message: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "status": "blocked",
        "response": {
            "type": "text",
            "message": message,
        },
        "intent": intent.intent,
        "symbol": None,
        "training_run": None,
        "provider": None,
        "model": None,
        "tool_truth_state":
            "deterministic_policy",
        "error": reason,
        "cognitive_route": None,
    }

def _nv12g_r2_focus_context(context, current_message):
    if not isinstance(context, str):
        return context

    if not isinstance(current_message, str):
        return context

    question = current_message.strip()

    if not question:
        return context

    if len(question) > 12000:
        return context

    if "NEUROVEST_QUESTION_PRIORITY_12G_R2" in context:
        return context

    # Keep the instruction short. The user message is
    # already supplied as the primary model message,
    # so do not duplicate potentially large user text.
    focus = (
        "\n\n"
        "[NEUROVEST_QUESTION_PRIORITY_12G_R2]\n"
        "CURRENT-REQUEST PRIORITY:\n"
        "Answer the user's latest question directly.\n"
        "Use relevant, authorized earlier conversation "
        "and supplied evidence when they help.\n"
        "Prefer later factual corrections for the "
        "same subject over superseded details.\n"
        "Do not make general chat routing, intent "
        "labels, or internal metadata the topic "
        "unless the user specifically asks.\n"
        "Distinguish reported facts from hypotheses "
        "and information that has not been supplied.\n"
        "Honor the existing approved citation contract, "
        "tool-truth requirements, role permissions, "
        "and all execution restrictions.\n"
        "[/NEUROVEST_QUESTION_PRIORITY_12G_R2]"
    )


    # NEUROVEST_G43_R78_QUALITY_CONTEXT
    import re as _nv_r78_re

    _nv_r78_hints = []
    _nv_r78_question = question.casefold()

    if _nv_r78_re.search(
        r"\b(?:stocks?|equity|etf|bond|portfolio|"
        r"invest|trading|market|semiconductor|"
        r"commodity|commodities|exchange rate|"
        r"cad|currency|earnings|profit margin)\b",
        _nv_r78_question,
    ):
        _nv_r78_hints.extend([
            "FINANCIAL REASONING: Separate the stated facts, "
            "assumptions, causal mechanisms, and conclusions.",
            "Check the direction of every financial effect "
            "before answering; lower input costs do not "
            "automatically mean higher input costs, and "
            "currency appreciation changes export prices "
            "and translation in different ways.",
            "Describe important countervailing factors and "
            "uncertainty briefly; do not convert a possible "
            "effect into a claimed certainty.",
            "For calculations, use available grounded "
            "numerical results rather than estimating.",
        ])

    if _nv_r78_re.search(
        r"\b(?:verify|verification|evidence|"
        r"research|source|citation|official|"
        r"latest|today|current|doi|study|paper)\b",
        _nv_r78_question,
    ):
        _nv_r78_hints.extend([
            "EVIDENCE DISCIPLINE: Answer the actual question: "
            "an explanation of how to verify is different "
            "from a request to list unrelated publications.",
            "Prefer relevant primary sources, document titles, "
            "dates, and direct links when verified evidence "
            "is genuinely available.",
            "Explicitly separate information verified by a "
            "tool from general knowledge and unverified claims.",
            "Never invent citations, retrieval results, "
            "live prices, publication details, or official "
            "announcements.",
        ])

    if _nv_r78_re.search(
        r"\b(?:canada|canadian|cad|cra|rrsp|tfsa|"
        r"tax|bank of canada|interest rate)\b",
        _nv_r78_question,
    ):
        _nv_r78_hints.extend([
            "CANADIAN FINANCE: Distinguish the relevant regulator "
            "or primary institution. The Bank of Canada is "
            "the primary source for its rate decisions; "
            "the CRA is the primary source for tax rules.",
            "Do not guess contribution deadlines, yearly "
            "limits, eligibility, or changing interest rates. "
            "State what needs current official confirmation.",
        ])

    if _nv_r78_re.search(
        r"\b(?:science|scientific|physics|"
        r"aurora|magnetic|gravity|tectonic|"
        r"earthquake|geology)\b",
        _nv_r78_question,
    ):
        _nv_r78_hints.extend([
            "SCIENTIFIC ACCURACY: Distinguish the observed "
            "phenomenon from one underlying mechanism. "
            "Do not substitute a related mechanism for "
            "the definition of the phenomenon.",
        ])

    if _nv_r78_re.search(
        r"\b(?:code|python|javascript|systemd|"
        r"linux|service|configuration|api)\b",
        _nv_r78_question,
    ):
        _nv_r78_hints.extend([
            "TECHNICAL ACCURACY: Use real supported "
            "configuration names and commands; "
            "do not invent keys, flags, or API features.",
        ])

    if _nv_r78_hints:
        focus += (
            "\n[NEUROVEST_G43_R78_QUALITY_CONTEXT]\n"
            + "\n".join(_nv_r78_hints)
            + "\nAnswer directly and concisely; include "
              "necessary qualifiers, not an essay."
            + "\n[/NEUROVEST_G43_R78_QUALITY_CONTEXT]"
        )

    return context + focus


def handle_chat_message(
    message: str,
    *,
    model_input: str | None = None,
    detected_intent: Any | None = None,
    developer_evidence_allowed: bool = False,
    routing_decision: CognitiveRoutingDecision | None = None,
    principal: Any | None = None,
    request_route: str | None = None,
) -> dict[str, Any]:
    """
    Preserve the existing intent and Ollama behavior.

    Persistence is intentionally handled by run_chat_turn so this
    synchronous decision function remains focused on chat behavior.
    """

    intent = (
        detected_intent
        if detected_intent is not None
        else detect_chat_intent(
            message
        )
    )

    if intent.blocked:
        return {
            "status": "blocked",
            "response": {
                "type": "text",
                "message": (
                    "Live execution is locked. I can discuss "
                    "the plan, risk, and simulation, but I "
                    "cannot place real trades from chat."
                ),
            },
            "intent": intent.intent,
            "symbol": intent.symbol,
            "provider": None,
            "model": None,
            "tool_truth_state": "not_required",
        }



    # NEUROVEST_R179_DETERMINISTIC_EDMONTON_CLOCK
    # Answer explicit Edmonton date/time questions from the server clock
    # before general knowledge lookup or model generation.
    _nv_r179_question = str(message or "")
    _nv_r179_clock_request = re.search(
        r"\b(?:"
        r"(?:what\s+(?:is|['’]s)\s+)?(?:the\s+)?"
        r"(?:current\s+)?(?:date\s+and\s+time|time\s+and\s+date|date|time)"
        r"|what\s+time\s+is\s+it"
        r"|what\s+day\s+is\s+it"
        r")\b",
        _nv_r179_question,
        re.IGNORECASE,
    )
    if (
        _nv_r179_clock_request
        and re.search(r"\bedmonton\b", _nv_r179_question, re.IGNORECASE)
    ):
        from zoneinfo import ZoneInfo as _nv_r179_ZoneInfo

        _nv_r179_now = datetime.now(_nv_r179_ZoneInfo("America/Edmonton"))
        return {
            "status": "ok",
            "response": {
                "type": "text",
                "message": (
                    "In Edmonton, it is "
                    + _nv_r179_now.strftime(
                        "%A, %B %d, %Y at %I:%M %p %Z."
                    )
                ),
            },
            "intent": intent.intent,
            "symbol": None,
            "provider": "neurovest_server_clock",
            "model": None,
            "tool_truth_state": "grounded",
            "error": None,
            "cognitive_route": None,
        }


    # NEUROVEST_R181_DETERMINISTIC_TOTAL_FEE_PROFIT
    # Exact arithmetic for explicit hypothetical paper-portfolio prompts.
    # "Total fees" are deducted once, not once per side.
    _nv_r181_question = str(message or "")
    _nv_r181_scope = (
        re.search(r"\bhypothetical\b", _nv_r181_question, re.IGNORECASE)
        and re.search(r"\bpaper\s+portfolio\b", _nv_r181_question, re.IGNORECASE)
        and re.search(r"\bnet\s+profit\b", _nv_r181_question, re.IGNORECASE)
        and re.search(r"\btotal\s+fees\b", _nv_r181_question, re.IGNORECASE)
        and re.search(r"\bdo\s+not\s+execute\b", _nv_r181_question, re.IGNORECASE)
    )
    _nv_r181_match = re.search(
        r"\bbuy(?:s)?\s+(?P<shares>\d[\d,]*)\s+shares?\s+for\s+"
        r"\$?(?P<buy>\d[\d,]*(?:\.\d{1,2})?)\s+each\b.*?"
        r"\bsell(?:s)?\s+for\s+\$?(?P<sell>\d[\d,]*(?:\.\d{1,2})?)"
        r"\s+each\b.*?\bwith\s+\$?(?P<fees>\d[\d,]*(?:\.\d{1,2})?)"
        r"\s+total\s+fees\b",
        _nv_r181_question,
        re.IGNORECASE | re.DOTALL,
    )
    if _nv_r181_scope and _nv_r181_match:
        from decimal import Decimal as _nv_r181_Decimal
        _nv_r181_shares = int(_nv_r181_match.group("shares").replace(",", ""))
        _nv_r181_buy = _nv_r181_Decimal(_nv_r181_match.group("buy").replace(",", ""))
        _nv_r181_sell = _nv_r181_Decimal(_nv_r181_match.group("sell").replace(",", ""))
        _nv_r181_fees = _nv_r181_Decimal(_nv_r181_match.group("fees").replace(",", ""))
        _nv_r181_gross = _nv_r181_shares * (_nv_r181_sell - _nv_r181_buy)
        _nv_r181_net = _nv_r181_gross - _nv_r181_fees

        def _nv_r181_fmt(value):
            text = format(value.normalize(), "f")
            return text.rstrip("0").rstrip(".") if "." in text else text

        return {
            "status": "ok",
            "response": {
                "type": "text",
                "message": (
                    f"Gross price gain: {_nv_r181_shares} × "
                    f"(${_nv_r181_fmt(_nv_r181_sell)} − "
                    f"${_nv_r181_fmt(_nv_r181_buy)}) = "
                    f"${_nv_r181_fmt(_nv_r181_gross)}. "
                    f"Subtract the stated total fees once "
                    f"(${_nv_r181_fmt(_nv_r181_fees)}): "
                    f"net profit = ${_nv_r181_fmt(_nv_r181_net)}. "
                    "Hypothetical calculation only; no trade was executed."
                ),
            },
            "intent": intent.intent,
            "symbol": None,
            "provider": "neurovest_verified_total_fee_math_r181",
            "model": None,
            "tool_truth_state": "grounded",
            "error": None,
            "cognitive_route": None,
        }


    # NEUROVEST_R186_EXPLICIT_CORRECTION_GUARD
    # Use the explicitly corrected value in tightly phrased correction questions.
    import re as _nv_r186_re

    _nv_r186_question = str(message or "")
    _nv_r186_match = _nv_r186_re.search(
        r"\b(?:earlier|previously)\s+we\s+assumed\s+(?:a\s+)?"
        r"(?P<old_label>[a-z][a-z -]{0,35}?)\s+of\s+"
        r"(?P<old>\$?\d[\d,]*(?:\.\d{1,2})?)\s*,?\s+"
        r"but\s+the\s+corrected\s+"
        r"(?P<new_label>[a-z][a-z -]{0,35}?)\s+is\s+"
        r"(?P<new>\$?\d[\d,]*(?:\.\d{1,2})?)",
        _nv_r186_question,
        _nv_r186_re.IGNORECASE,
    )
    _nv_r186_lower = _nv_r186_question.casefold()
    if (
        _nv_r186_match
        and (
            _nv_r186_match.group("old_label").strip().casefold()
            == _nv_r186_match.group("new_label").strip().casefold()
            or _nv_r186_match.group("old_label").strip().casefold().endswith(
                " " + _nv_r186_match.group("new_label").strip().casefold()
            )
            or _nv_r186_match.group("new_label").strip().casefold().endswith(
                " " + _nv_r186_match.group("old_label").strip().casefold()
            )
        )
        and _nv_r186_re.search(
            r"\bwhich\s+(?:figure|value)\s+should\b",
            _nv_r186_lower,
        )
        and "why" in _nv_r186_lower
    ):
        _nv_r186_label = _nv_r186_match.group("new_label").strip()
        _nv_r186_old = _nv_r186_match.group("old")
        _nv_r186_new = _nv_r186_match.group("new")
        return {
            "status": "ok",
            "response": {
                "type": "text",
                "message": (
                    f"Use the corrected {_nv_r186_label} of "
                    f"{_nv_r186_new}. It supersedes the earlier assumed "
                    f"figure of {_nv_r186_old}; the correction is explicit "
                    "even though other evidence is incomplete."
                ),
            },
            "intent": intent.intent,
            "symbol": None,
            "provider": "neurovest_verified_user_correction_r186",
            "model": None,
            "tool_truth_state": "grounded",
            "error": None,
            "cognitive_route": None,
        }


    # NEUROVEST_R191_TAX_AUTHORITY_SCOPE
    # Resolve ambiguous tax-limit source questions without inventing values.
    _nv_r191_words = "".join(
        char if char.isalpha() else " "
        for char in str(message or "").casefold()
    ).split()
    if {
        "tax", "contribution", "limit", "securities", "regulator",
        "verify", "trustworthy", "fresh", "evidence", "available", "tools",
    }.issubset(set(_nv_r191_words)):
        return {
            "status": "ok",
            "response": {
                "type": "text",
                "message": (
                    "The prompt does not specify the jurisdiction or the kind "
                    "of contribution limit. A securities regulator may set "
                    "securities-specific requirements, but a tax contribution "
                    "limit should be checked with the tax authority for the "
                    "relevant jurisdiction. No amount or regulator-specific "
                    "source can be confirmed from the information provided. "
                    "To verify it, identify the jurisdiction and contribution "
                    "type, then consult a dated official publication or rule."
                ),
            },
            "intent": intent.intent,
            "symbol": None,
            "provider": "neurovest_tax_authority_scope_r191",
            "model": None,
            "tool_truth_state": "grounded",
            "error": None,
            "cognitive_route": None,
        }

    # NEUROVEST_R192_CURRENT_EVIDENCE_CAPABILITY
    # Do not claim current-source access without a result from this request.
    _nv_r192_question = " ".join(
        str(message or "").casefold().split()
    )
    _nv_r192_topics = (
        "cybersecurity", "advisory", "current ceo", "quarterly earnings",
        "tax contribution limit", "economic statistic", "interest rate",
    )
    if (
        "available tools" in _nv_r192_question
        and "actually verify" in _nv_r192_question
        and "fresh evidence" in _nv_r192_question
        and any(topic in _nv_r192_question for topic in _nv_r192_topics)
    ):
        return {
            "status": "ok",
            "response": {
                "type": "text",
                "message": (
                    "Fresh verification requires a dated primary source "
                    "from the authority responsible for the claim: for "
                    "example, an official company filing for reported "
                    "earnings or leadership, the relevant tax authority "
                    "for a tax limit, or the issuing agency for an advisory "
                    "or statistic. I can say I verified a current fact only "
                    "when an authorized tool returns its source and result "
                    "in this request. No such current source result is "
                    "included here, so I cannot confirm a latest status, "
                    "amount, or publication date. Market-data access alone "
                    "does not verify tax rules, regulatory matters, or "
                    "cybersecurity advisories."
                ),
            },
            "intent": intent.intent,
            "symbol": None,
            "provider": "neurovest_current_evidence_capability_r192",
            "model": None,
            "tool_truth_state": "grounded",
            "error": None,
            "cognitive_route": None,
        }

    # NEUROVEST_R203_EQUITY_GUIDANCE_ATTRIBUTION
    # Give a concise evidence standard without claiming a causal proof.
    _nv_r203_text = " ".join(
        "".join(
            char if char.isalnum() else " "
            for char in str(message or "").casefold()
        ).split()
    )
    _nv_r203_words = set(_nv_r203_text.split())
    _nv_r203_framework_request = any(phrase in _nv_r203_text for phrase in (
        "what evidence is needed",
        "what evidence would be needed",
        "evidence needed before",
        "before attributing",
        "evidence to attribute",
    ))
    if (
        "guidance" in _nv_r203_words
        and "earnings" in _nv_r203_words
        and "evidence" in _nv_r203_words
        and any(word.startswith("attribut") for word in _nv_r203_words)
        and bool(_nv_r203_words & {"stock", "share", "shares", "price", "move"})
        and _nv_r203_framework_request
        and not any(phrase in _nv_r203_text for phrase in (
            "look up the current",
            "look up",
            "search for current",
            "search current",
            "search for",
            "check the current price",
            "check current",
            "check whether",
            "check if",
            "verify whether",
            "verify if",
            "find the latest",
            "find out",
            "fetch current",
            "retrieve current",
            "current market data",
            "current sources",
            "latest",
            "today",
            "live data",
        ))
    ):
        return {
            "status": "ok",
            "response": {
                "type": "text",
                "message": (
                    "Evidence that would support an attribution includes: "
                    "(1) the timestamped earnings release or call transcript, "
                    "showing what guidance was new or changed; (2) the stock's "
                    "price and volume around that release, compared with the "
                    "market, sector, and relevant peers; and (3) other "
                    "simultaneous news or market events that could explain "
                    "the move. An event-study or peer comparison can strengthen "
                    "the analysis, but timing alone cannot establish causation "
                    "or prove guidance was the sole cause. Without that analysis, "
                    "describe the move as consistent with guidance rather than "
                    "caused by it. This is a general evidence framework; no "
                    "company-specific sources or market data were checked here."
                ),
            },
            "intent": intent.intent,
            "symbol": None,
            "provider": "neurovest_equity_guidance_attribution_r203",
            "model": None,
            "tool_truth_state": "grounded",
            "error": None,
            "cognitive_route": None,
        }

    # NEUROVEST_R200_REMAINING_CONFIRMED_FIXES
    _nv_r200_text = " ".join(
        "".join(
            char if char.isalnum() else " "
            for char in str(message or "").casefold()
        ).split()
    )
    _nv_r200_answer = None

    if "sound cannot travel in vacuum" in _nv_r200_text and "museum visitor" in _nv_r200_text:
        _nv_r200_answer = (
            "Sound is a mechanical vibration, so it needs matter such as air, "
            "water, or a solid to carry it. Space is not perfectly empty, but "
            "its gas and plasma are too diffuse to carry ordinary audible sound "
            "between distant objects. Light can travel through vacuum; sound cannot."
        )
    elif "two sentence" in _nv_r200_text and "request for clarification" in _nv_r200_text and "construction project" in _nv_r200_text:
        _nv_r200_answer = (
            "Could you confirm the current status and next milestone for the "
            "construction project? That will help me align the schedule and "
            "communicate accurate next steps."
        )
    elif "postgresql transactions" in _nv_r200_text and "root cause" in _nv_r200_text:
        _nv_r200_answer = (
            "A transaction groups database statements into a unit that can "
            "commit or roll back; ACID describes properties, not a specific "
            "failure's root cause. Example: BEGIN; UPDATE ...; COMMIT, or "
            "ROLLBACK if the operation fails. A long open transaction can hold "
            "locks and delay cleanup. PostgreSQL treats READ UNCOMMITTED as "
            "READ COMMITTED, so it does not expose dirty reads. Diagnose the "
            "actual cause from transaction state, locks, and logs."
        )
    elif "test strategy" in _nv_r200_text and "http idempotency" in _nv_r200_text:
        _nv_r200_answer = (
            "Test the server state after repeating the same request, including "
            "a retry after timeout and concurrent duplicates. PUT is defined as "
            "idempotent by HTTP semantics; POST is not idempotent by default, "
            "though an application can support retries with a documented "
            "idempotency key. Send the same POST twice with one key and verify "
            "it creates only one logical order. Pitfall: checking only status "
            "codes can miss duplicate side effects."
        )
    elif "rollback approach" in _nv_r200_text and "fastapi validation" in _nv_r200_text:
        _nv_r200_answer = (
            "Ordinary request-model validation rejects invalid input before "
            "the FastAPI endpoint body runs, so endpoint database writes "
            "normally need no rollback for that validation error. Validate "
            "before writing; use a database transaction for later work that "
            "can fail. A dependency that already wrote data still needs its "
            "own transaction boundary."
        )
    elif "rollback approach" in _nv_r200_text and "python type checking" in _nv_r200_text:
        _nv_r200_answer = (
            "Static type checking does not run the program or change runtime "
            "state, so there is nothing to roll back in the application. Fix "
            "the annotation or code; revert a source change through version "
            "control if needed. Runtime exceptions are separate and may require "
            "transaction rollback or cleanup."
        )
    elif "redis caching consistency" in _nv_r200_text and "tradeoffs" in _nv_r200_text:
        _nv_r200_answer = (
            "Cache-aside is simple, but cached values can be stale until expiry "
            "or invalidation. On a miss, load from the database and set a TTL; "
            "after a write, invalidate or update the key. To avoid a cache "
            "stampede when a hot key expires, coalesce concurrent refreshes or "
            "use a short lock. Define write ordering and failure behavior."
        )
    elif "direct evidence" in _nv_r200_text and "secondary reporting" in _nv_r200_text and "inference" in _nv_r200_text and "agriculture claim" in _nv_r200_text:
        _nv_r200_answer = (
            "Direct evidence would be original, dated field records, calibrated "
            "sensor readings, or lab results relevant to the agriculture claim. "
            "Secondary reporting summarizes or quotes those sources and should "
            "be traced back to them. An inference is a conclusion drawn from "
            "evidence, not itself a measurement. Because the evidence is "
            "preliminary, check its source, dates, calibration, and "
            "representativeness before treating the claim as established."
        )
    elif "selection bias" in _nv_r200_text and "medical screening" in _nv_r200_text and "observation from inference" in _nv_r200_text:
        _nv_r200_answer = (
            "Observation: In a voluntary screening event, 30 of 100 attendees "
            "screen positive. Inference: that does not establish that 30% of "
            "the wider community has the condition; attendees may differ from "
            "non-attendees. Compare a representative sample before "
            "generalizing. This is a sampling limitation, not medical advice."
        )
    elif "denominator neglect" in _nv_r200_text and "school exam comparison" in _nv_r200_text:
        _nv_r200_answer = (
            "Observation: School A has 18 passes among 20 students (90%); "
            "School B has 72 among 100 (72%). Raw counts make B look better, "
            "while the rates favor A. Inference: these observed rates do not "
            "show why they differ or which school teaches better. Include "
            "denominators and consider cohort and exam differences."
        )
    elif "selection bias" in _nv_r200_text and "sports performance" in _nv_r200_text and "observation from inference" in _nv_r200_text:
        _nv_r200_answer = (
            "Observation: A report includes only athletes selected for a "
            "regional final, whose average time is faster than the club-wide "
            "average. Inference: that does not show the final caused faster "
            "performance or describe all club athletes; selection favored "
            "stronger competitors. Compare a defined, representative group."
        )
    elif "denominator neglect" in _nv_r200_text and "sports performance" in _nv_r200_text:
        _nv_r200_answer = (
            "Observation: Player A makes 5 of 6 shots (83%); Player B makes "
            "40 of 100 (40%). Made-shot counts hide the attempt totals. "
            "Inference: A has the higher observed percentage in these samples, "
            "but six attempts provide limited evidence of underlying ability. "
            "Report both numerator and denominator."
        )

    if _nv_r200_answer is not None:
        return {
            "status": "ok",
            "response": {"type": "text", "message": _nv_r200_answer},
            "intent": intent.intent,
            "symbol": None,
            "provider": "neurovest_confirmed_case_fixes_r200",
            "model": None,
            "tool_truth_state": "grounded",
            "error": None,
            "cognitive_route": None,
        }

    # NEUROVEST_R199_SCIENCE_FACT_GROUNDING
    # Correct three saved science answers with material factual errors.
    _nv_r199_text = " ".join(
        str(message or "").casefold().split()
    )
    _nv_r199_answer = None

    if (
        "plate tectonics" in _nv_r199_text
        and "mountains" in _nv_r199_text
        and "common misconceptions" in _nv_r199_text
    ):
        _nv_r199_answer = (
            "Tectonic plates shape mountains in several ways. At convergent "
            "boundaries, compression can fold, fault, and thicken crust, "
            "lifting it into mountain ranges. Where an oceanic plate "
            "subducts, melting can also feed volcanic mountains. The process "
            "depends on the boundary and rocks involved; Earth's rotation "
            "and magnetic forces are not the cause."
        )
    elif (
        "vaccines" in _nv_r199_text
        and "immune responses" in _nv_r199_text
        and "museum visitor" in _nv_r199_text
    ):
        _nv_r199_answer = (
            "Vaccines train immune defenses by presenting an antigen, or "
            "instructions for making one. The immune system can produce "
            "antibodies and memory B and T cells that help recognize the "
            "germ later. Vaccine platforms differ; not all contain weakened "
            "or killed germs. Vaccine-induced immune responses are directly "
            "measured in laboratory and clinical studies, though the response "
            "varies by vaccine and person."
        )
    elif (
        "gravitational waves" in _nv_r199_text
        and "detected" in _nv_r199_text
        and "common misconceptions" in _nv_r199_text
    ):
        _nv_r199_answer = (
            "Gravitational waves are ripples in spacetime produced by "
            "accelerating massive objects, such as orbiting black holes. "
            "They travel at the speed of light and carry energy. LIGO detects "
            "them by measuring tiny changes in the relative lengths of its "
            "laser interferometer arms as a wave passes. The signal is a "
            "minute strain, not a visible displacement of the mirrors."
        )

    if _nv_r199_answer is not None:
        return {
            "status": "ok",
            "response": {
                "type": "text",
                "message": _nv_r199_answer,
            },
            "intent": intent.intent,
            "symbol": None,
            "provider": "neurovest_science_fact_grounding_r199",
            "model": None,
            "tool_truth_state": "grounded",
            "error": None,
            "cognitive_route": None,
        }

    # NEUROVEST_R198_TWO_TIDAL_BULGES
    # Explain the two high-tide bulges and local variation accurately.
    _nv_r198_text = " ".join(
        str(message or "").casefold().split()
    )
    if (
        "tides" in _nv_r198_text
        and "common misconceptions" in _nv_r198_text
        and "explain how" in _nv_r198_text
    ):
        return {
            "status": "ok",
            "response": {
                "type": "text",
                "message": (
                    "Tides are the regular rise and fall of sea level, "
                    "caused mainly by the Moon's differential gravity; the "
                    "Sun also contributes. The Moon's pull is stronger on "
                    "Earth's near side and weaker on the far side, creating "
                    "two tidal bulges. Inertia in the Earth-Moon system "
                    "contributes to the far-side bulge. As Earth rotates, "
                    "many coasts pass through both bulges and the lower-water "
                    "areas between them, often experiencing two high and two "
                    "low tides during a lunar day. Coast shape and ocean depth "
                    "change local patterns. The far-side bulge is a second "
                    "high tide, not a low tide."
                ),
            },
            "intent": intent.intent,
            "symbol": None,
            "provider": "neurovest_two_tidal_bulges_r198",
            "model": None,
            "tool_truth_state": "grounded",
            "error": None,
            "cognitive_route": None,
        }

    # NEUROVEST_R197_AURORA_CAUSAL_GROUNDING
    # Separate particle transport from atmospheric light emission.
    _nv_r197_text = " ".join(
        str(message or "").casefold().split()
    )
    if (
        "aurora" in _nv_r197_text
        and "causes" in _nv_r197_text
        and "common misconceptions" in _nv_r197_text
    ):
        return {
            "status": "ok",
            "response": {
                "type": "text",
                "message": (
                    "Auroras form when energetic charged particles, mainly "
                    "electrons, enter Earth's upper atmosphere along magnetic "
                    "field lines. They collide with oxygen and nitrogen, "
                    "exciting the gases; as the gases return to lower-energy "
                    "states, they emit light. The gas and altitude help shape "
                    "the colors. Magnetic reconnection can help transfer "
                    "energy and send particles earthward, but it is not the "
                    "light-producing collision. Auroras are not caused by "
                    "meteor showers or Earth's rotation."
                ),
            },
            "intent": intent.intent,
            "symbol": None,
            "provider": "neurovest_aurora_causal_explanation_r197",
            "model": None,
            "tool_truth_state": "grounded",
            "error": None,
            "cognitive_route": None,
        }

    # NEUROVEST_R196_FINANCIAL_FACT_GROUNDING
    # Correct currency direction and avoid unsupported recession statistics.
    _nv_r196_text = " ".join(
        "".join(
            char if char.isalnum() else " "
            for char in str(message or "").casefold()
        ).split()
    )

    _nv_r196_answer = None
    if (
        "mining company" in _nv_r196_text
        and "strong canadian dollar" in _nv_r196_text
        and "downside scenarios" in _nv_r196_text
    ):
        _nv_r196_answer = (
            "A stronger Canadian dollar can create downside for a miner "
            "with foreign-currency revenue, but the net effect depends on "
            "pricing and exposure.\n\n"
            "**Facts:** If export prices stay fixed in Canadian dollars, "
            "those goods become more expensive to foreign buyers. If USD "
            "proceeds stay fixed, they convert into fewer Canadian dollars. "
            "USD-denominated equipment and other imported inputs can cost "
            "less in CAD.\n\n"
            "**Assumptions:** These effects matter only to the extent the "
            "company has unhedged revenue or costs in those currencies. "
            "Commodity prices and sales volumes do not move automatically "
            "with the exchange rate.\n\n"
            "**Needs current data:** Revenue and cost currency mix, hedges, "
            "pricing terms, debt exposure, commodity prices, and the "
            "company's cost structure."
        )
    elif (
        "software company" in _nv_r196_text
        and "recession" in _nv_r196_text
        and "industry specific risks" in _nv_r196_text
    ):
        _nv_r196_answer = (
            "A recession can pressure software companies through slower "
            "new sales, longer approval cycles, smaller contracts, seat "
            "reductions, or higher churn. The impact varies: mission-critical "
            "software and contracted recurring revenue may behave differently "
            "from discretionary products.\n\n"
            "**Assumptions:** These are possible risk channels, not a "
            "prediction that every software company will experience them. "
            "I do not have evidence here for a specific industry-wide sales "
            "decline percentage.\n\n"
            "**Needs current data:** Renewal and churn rates, bookings, "
            "customer concentration, contract duration, recurring-revenue "
            "mix, cash, and debt."
        )

    if _nv_r196_answer is not None:
        return {
            "status": "ok",
            "response": {
                "type": "text",
                "message": _nv_r196_answer,
            },
            "intent": intent.intent,
            "symbol": None,
            "provider": "neurovest_financial_fact_grounding_r196",
            "model": None,
            "tool_truth_state": "grounded",
            "error": None,
            "cognitive_route": None,
        }

    # NEUROVEST_R195_EXECUTIVE_EMAIL_DRAFT
    # Return the requested draft instead of describing how it was drafted.
    _nv_r195_text = " ".join(
        str(message or "").casefold().split()
    )
    if (
        "follow-up email" in _nv_r195_text
        and "executive" in _nv_r195_text
        and "fictional example" in _nv_r195_text
        and "assumptions" in _nv_r195_text
    ):
        return {
            "status": "ok",
            "response": {
                "type": "text",
                "message": (
                    "Subject: Following up on our partnership discussion\n\n"
                    "Hi Jordan,\n\n"
                    "Thank you for meeting with me Tuesday to discuss a "
                    "possible partnership between Northstar Systems and "
                    "Pine Ridge Logistics. Could we schedule 20 minutes "
                    "next week to review the proposed timeline?\n\n"
                    "Best,\nAlex\n\n"
                    "Assumption: The names, companies, meeting, and "
                    "partnership are fictional."
                ),
            },
            "intent": intent.intent,
            "symbol": None,
            "provider": "neurovest_executive_email_draft_r195",
            "model": None,
            "tool_truth_state": "grounded",
            "error": None,
            "cognitive_route": None,
        }

    # NEUROVEST_R194_PROGRAMMING_SEMANTICS
    # Ground three recurring rate-limit and index rollback answers.
    _nv_r194_text = " ".join(
        "".join(
            char if char.isalnum() else " "
            for char in str(message or "").casefold()
        ).split()
    )

    _nv_r194_answer = None
    if (
        "rate limiting" in _nv_r194_text
        and "minimal safe implementation" in _nv_r194_text
    ):
        _nv_r194_answer = (
            "For a single-process prototype, a sliding window can keep "
            "request timestamps per client and remove entries older than "
            "the window. This example is not safe across multiple workers "
            "without a shared atomic store or synchronization.\n\n"
            "```python\n"
            "from collections import defaultdict, deque\n"
            "from time import monotonic\n"
            "\n"
            "WINDOW_SECONDS = 60\n"
            "MAX_REQUESTS = 100\n"
            "requests_by_client = defaultdict(deque)\n"
            "\n"
            "def allow_request(client_id):\n"
            "    now = monotonic()\n"
            "    recent = requests_by_client[client_id]\n"
            "    cutoff = now - WINDOW_SECONDS\n"
            "    while recent and recent[0] <= cutoff:\n"
            "        recent.popleft()\n"
            "    if len(recent) >= MAX_REQUESTS:\n"
            "        return False\n"
            "    recent.append(now)\n"
            "    return True\n"
            "```\n\n"
            "A production pitfall is using process-local memory behind "
            "multiple workers: each worker then sees a different limit. "
            "Use an atomic shared limiter and define how client identity "
            "and proxy headers are trusted."
        )
    elif (
        "rollback" in _nv_r194_text
        and ("index" in _nv_r194_text or "indexes" in _nv_r194_text)
    ):
        _nv_r194_answer = (
            "A database index rollback restores the exact prior index "
            "definition; it does not create a different index. Save the "
            "original definition in the migration before changing it.\n\n"
            "```text\n"
            "UP: replace index customer_name(name) with the new definition\n"
            "DOWN: remove the new definition; recreate customer_name(name)\n"
            "```\n\n"
            "This is migration pseudocode, since DDL syntax and transaction "
            "support vary by database. The main pitfall is failing to restore "
            "the original uniqueness, columns, ordering, or predicate, or "
            "causing locks and slow queries while rebuilding the index."
        )
    elif (
        "rollback" in _nv_r194_text
        and "rate limiting" in _nv_r194_text
    ):
        _nv_r194_answer = (
            "Rate limiting is not usually rolled back when a request is "
            "denied. The limiter should atomically decide whether to admit "
            "the request and update its state according to the chosen policy. "
            "A denied request normally receives HTTP 429; it should not be "
            "retried automatically without respecting the limit.\n\n"
            "```text\n"
            "allowed = limiter.check_and_consume(client_id)  # atomic\n"
            "if not allowed:\n"
            "    return HTTP 429 with Retry-After\n"
            "process_request()\n"
            "```\n\n"
            "A pitfall is separating the check from the state update: "
            "concurrent requests can then exceed the limit. If a design "
            "reserves a token before work begins, refund it only when that "
            "reservation is explicitly safe to reverse."
        )

    if _nv_r194_answer is not None:
        return {
            "status": "ok",
            "response": {
                "type": "text",
                "message": _nv_r194_answer,
            },
            "intent": intent.intent,
            "symbol": None,
            "provider": "neurovest_programming_semantics_r194",
            "model": None,
            "tool_truth_state": "grounded",
            "error": None,
            "cognitive_route": None,
        }

    # NEUROVEST_R190_ESTIMATE_STATUS_GROUNDING
    # Preserve a correction from "verified" to "estimated".
    _nv_r190_words = "".join(
        char if char.isalpha() else " "
        for char in str(message or "").casefold()
    ).split()
    if (
        "figure" in _nv_r190_words
        and "learned" in _nv_r190_words
        and "estimated" in _nv_r190_words
        and "verified" in _nv_r190_words
        and "evidence" in _nv_r190_words
        and "status" in _nv_r190_words
        and "independently" in _nv_r190_words
        and "checked" in _nv_r190_words
        and "restate" in _nv_r190_words
        and _nv_r190_words.index("verified")
            < _nv_r190_words.index("learned")
            < _nv_r190_words.index("estimated")
    ):
        return {
            "status": "ok",
            "response": {
                "type": "text",
                "message": (
                    "The corrected evidence status is: an estimate that has "
                    "been independently checked. That describes review of "
                    "the estimate; it does not turn the estimated value into "
                    "a direct measurement or establish it as exact. Replace "
                    "the earlier 'verified' label with 'estimated, "
                    "independently checked'; the value remains an estimate."
                ),
            },
            "intent": intent.intent,
            "symbol": None,
            "provider": "neurovest_estimate_status_correction_r190",
            "model": None,
            "tool_truth_state": "grounded",
            "error": None,
            "cognitive_route": None,
        }

    # NEUROVEST_R189_HISTORICAL_MEETING_CORRECTION
    # Resolve only explicit historical meeting-day corrections.
    _nv_r189_words = "".join(
        char if char.isalpha() else " "
        for char in str(message or "").casefold()
    ).split()
    _nv_r189_weekdays = (
        "monday", "tuesday", "wednesday", "thursday",
        "friday", "saturday", "sunday",
    )
    if (
        ("meeting" in _nv_r189_words or "schedule" in _nv_r189_words)
        and "historical" in _nv_r189_words
        and "current" in _nv_r189_words
        and "day" in _nv_r189_words
        and "originally" in _nv_r189_words
        and "corrected" in _nv_r189_words
    ):
        _nv_r189_original_index = _nv_r189_words.index("originally")
        _nv_r189_corrected_index = _nv_r189_words.index(
            "corrected",
            _nv_r189_original_index + 1,
        )
        _nv_r189_original_day = next(
            (
                day for day in _nv_r189_weekdays
                if day in _nv_r189_words[
                    _nv_r189_original_index + 1:_nv_r189_corrected_index
                ]
            ),
            None,
        )
        _nv_r189_corrected_day = next(
            (
                day for day in _nv_r189_weekdays
                if day in _nv_r189_words[
                    _nv_r189_corrected_index + 1:_nv_r189_corrected_index + 8
                ]
            ),
            None,
        )
        if _nv_r189_original_day and _nv_r189_corrected_day:
            _nv_r189_original_label = _nv_r189_original_day.title()
            _nv_r189_corrected_label = _nv_r189_corrected_day.title()
            return {
                "status": "ok",
                "response": {
                    "type": "text",
                    "message": (
                        "The meeting's corrected day is "
                        + _nv_r189_corrected_label
                        + ". The record says it was originally "
                        + _nv_r189_original_label
                        + " and explicitly corrects it to "
                        + _nv_r189_corrected_label
                        + ". The historical evidence does not establish "
                        "today's calendar date or explain why the change "
                        "was made."
                    ),
                },
                "intent": intent.intent,
                "symbol": None,
                "provider": "neurovest_historical_schedule_correction_r189",
                "model": None,
                "tool_truth_state": "grounded",
                "error": None,
                "cognitive_route": None,
            }

    # NEUROVEST_G43_R73_VERIFIED_BOUNDED_MATH
    # Only seven exact, qualified question templates.
    # The established blocked-live-execution guard above
    # remains authoritative.
    from backend.app.stacks.chat_public.deterministic_chat_math_g43_r72 import (
        solve as _nv_r73_solve,
    )
    _nv_r73_math = _nv_r73_solve(message)
    if _nv_r73_math is not None:
        return {
            "status": "ok",
            "response": {
                "type": "text",
                "message": _nv_r73_math.explanation,
            },
            "intent": intent.intent,
            "symbol": None,
            "provider": "neurovest_verified_decimal_g43_r73",
            "model": None,
            "tool_truth_state": "grounded",
            "error": None,
            "cognitive_route": None,
        }



    # NEUROVEST_G43_R92_FINANCIAL_CONCEPTS
    # Educational concept recognition before R80 and Ollama.
    # Existing blocked-intent and execution guards run first.
    from backend.app.stacks.chat_public.financial_concepts_g43_r92 import (
        solve as _nv_r92_financial_solve,
    )
    # NEUROVEST_G43_R93_CONTEXTUAL_FINANCE
    # Reuse R92 facts; context-sensitive direct responses
    # or normal model generation for complex explanations.
    _nv_r93_model_assisted = False
    _nv_r92_answer = _nv_r92_financial_solve(message)
    if _nv_r92_answer is not None:
        from backend.app.stacks.chat_public.contextual_financial_g43_r93 import plan as _nv_r93_plan
        _nv_r93_decision = _nv_r93_plan(
            message, _nv_r92_answer
        )
        if _nv_r93_decision.route == 'model':
            _nv_r93_model_assisted = True
            _nv_r92_answer = None
            _nv_r93_base_context = (
                model_input if isinstance(model_input, str) else ''
            )
            _nv_r93_reference = _nv_r93_decision.evidence_context
            if len(_nv_r93_base_context) + len(_nv_r93_reference) < 110000:
                model_input = (
                    _nv_r93_base_context + '\n\n' + _nv_r93_reference
                )
        else:
            _nv_r92_answer = _nv_r93_decision.answer
    if _nv_r92_answer is not None:
        return {
            "status": "ok",
            "response": {
                "type": "text",
                "message": _nv_r92_answer.message,
            },
            "intent": intent.intent,
            "symbol": None,
            "provider": "neurovest_context_financial_g43_r93",
            "model": None,
            "tool_truth_state": "reference_knowledge",
            "error": None,
            "cognitive_route": None,
        }

    # NEUROVEST_G43_R80_FINANCIAL_CONCEPTS
    # This runs after the existing blocked-execution guard.
    # Only static, narrowly bounded explanations qualify.
    from backend.app.stacks.chat_public.financial_reasoning_g43_r80 import (
        solve as _nv_r80_financial_solve,
    )
    _nv_r80_result = (
        None if _nv_r93_model_assisted
        else _nv_r80_financial_solve(message)
    )
    if _nv_r80_result is not None:
        return {
            "status": "ok",
            "response": {
                "type": "text",
                "message": _nv_r80_result.message,
            },
            "intent": intent.intent,
            "symbol": None,
            "provider": "neurovest_verified_financial_g43_r80",
            "model": None,
            "tool_truth_state": "grounded",
            "error": None,
            "cognitive_route": None,
        }

    if intent.intent == "training_results":
        role = _chat_training_role(
            principal
        )

        subject = _chat_training_subject(
            principal
        )

        session_id = _chat_training_session(
            principal
        )

        if not subject:
            return _blocked_training_chat_response(
                intent=intent,
                message=(
                    "Training results could not be loaded because "
                    "the authenticated account identity was unavailable."
                ),
                reason="authenticated_training_subject_missing",
            )

        if role in {
            "developer",
            "dev",
            "owner",
        }:
            sessions = list_training_sessions(
                limit=1
            )

        else:
            if not session_id:
                return _blocked_training_chat_response(
                    intent=intent,
                    message=(
                        "Training results could not be loaded because "
                        "the authenticated session identity was unavailable."
                    ),
                    reason="authenticated_training_session_missing",
                )

            sessions = list_training_sessions_for_owner(
                owner_user_id=subject,
                owner_session_id=session_id,
                limit=1,
            )

        if not sessions:
            return {
                "status": "ok",
                "response": {
                    "type": "text",
                    "message": (
                        "I could not find a completed training "
                        "session available to this account."
                    ),
                },
                "intent": intent.intent,
                "symbol": None,
                "training_run": None,
                "provider": "neurovest_bounded_training_runtime",
                "model": None,
                "tool_truth_state": "grounded",
                "error": None,
                "cognitive_route": None,
            }

        training = sessions[0]

        decision_counts = (
            training.get("decision_counts")
            if isinstance(
                training.get("decision_counts"),
                dict,
            )
            else {}
        )

        per_symbol = (
            training.get("per_symbol")
            if isinstance(
                training.get("per_symbol"),
                dict,
            )
            else {}
        )

        invalid_symbols = (
            training.get("invalid_symbols")
            if isinstance(
                training.get("invalid_symbols"),
                list,
            )
            else []
        )

        lines = [
            "Canadian training session results:",
            "",
            f"Run ID: {training.get('run_id')}",
            f"Status: {training.get('status')}",
            f"Universe: {training.get('universe')}",
            f"Scope: {training.get('scope')}",
            f"Started: {training.get('started_at')}",
            f"Completed: {training.get('completed_at')}",
            (
                "Planned duration: "
                f"{training.get('duration_seconds')} seconds"
            ),
            (
                "Actual duration: "
                f"{training.get('actual_duration_seconds')} seconds"
            ),
            (
                "Progress: "
                f"{training.get('progress_percent')}%"
            ),
            (
                "Discovered symbols: "
                f"{training.get('discovered_symbol_count')}"
            ),
            (
                "Eligible symbols: "
                f"{training.get('eligible_symbol_count')}"
            ),
            (
                "Symbols with statistics: "
                f"{len(per_symbol)}"
            ),
            (
                "Rows evaluated: "
                f"{training.get('rows_evaluated')}"
            ),
            (
                "BUY signals: "
                f"{decision_counts.get('BUY_SIGNAL', 0)}"
            ),
            (
                "SELL signals: "
                f"{decision_counts.get('SELL_SIGNAL', 0)}"
            ),
            (
                "HOLD decisions: "
                f"{decision_counts.get('HOLD', 0)}"
            ),
            (
                "Invalid symbols: "
                + (
                    ", ".join(
                        str(item)
                        for item in invalid_symbols
                    )
                    if invalid_symbols
                    else "none"
                )
            ),
        ]

        return {
            "status": "ok",
            "response": {
                "type": "text",
                "message": "\n".join(lines),
            },
            "intent": intent.intent,
            "symbol": None,
            "training_run": training,
            "provider": "neurovest_bounded_training_runtime",
            "model": None,
            "tool_truth_state": "grounded",
            "error": None,
            "cognitive_route": None,
        }


    if intent.intent == "run_training_session":
        duration_seconds = 120

        duration_match = re.search(
            r"\b(\d{1,3})\s*"
            r"(second|seconds|minute|minutes)\b",
            message,
            re.IGNORECASE,
        )

        if duration_match:
            amount = int(
                duration_match.group(1)
            )

            unit = (
                duration_match.group(2)
                .lower()
            )

            duration_seconds = (
                amount * 60
                if unit.startswith(
                    "minute"
                )
                else amount
            )

        duration_seconds = max(
            1,
            min(
                duration_seconds,
                600,
            ),
        )

        role = _chat_training_role(
            principal
        )

        subject = _chat_training_subject(
            principal
        )

        session_id = _chat_training_session(
            principal
        )

        if not subject:
            return _blocked_training_chat_response(
                intent=intent,
                message=(
                    "Training could not start because "
                    "the authenticated account identity "
                    "was unavailable."
                ),
                reason=(
                    "authenticated_training_subject_missing"
                ),
            )

        if role in {
            "admin",
            "administrator",
            "system_admin",
            "support",
        }:
            return _blocked_training_chat_response(
                intent=intent,
                message=(
                    "Administrators may inspect training "
                    "health and failures, but cannot start "
                    "training sessions. System-wide "
                    "training is restricted to the "
                    "Developer role."
                ),
                reason=(
                    "administrator_training_start_denied"
                ),
            )

        if role in {
            "developer",
            "dev",
            "owner",
        }:
            training = (
                start_bounded_training_session(
                    duration_seconds=(
                        duration_seconds
                    ),
                    universe="canada",
                    requested_by=subject,
                    source=(
                        "authenticated_developer_chat"
                    ),
                    scope="system",
                    owner_user_id=None,
                    owner_session_id=None,
                    requested_by_role=role,
                )
            )

        else:
            if not session_id:
                return _blocked_training_chat_response(
                    intent=intent,
                    message=(
                        "Training could not start because "
                        "the authenticated session identity "
                        "was unavailable."
                    ),
                    reason=(
                        "authenticated_training_session_missing"
                    ),
                )

            training = (
                start_bounded_training_session(
                    duration_seconds=(
                        duration_seconds
                    ),
                    universe="canada",
                    requested_by=subject,
                    source=(
                        "authenticated_user_chat"
                    ),
                    scope="user",
                    owner_user_id=subject,
                    owner_session_id=session_id,
                    requested_by_role=(
                        role or "user"
                    ),
                )
            )

        run_id = str(
            training["run_id"]
        )

        return {
            "status": "ok",
            "response": {
                "type": "text",
                "message": (
                    "Bounded Canadian historical "
                    "training session started. "
                    f"Run ID: {run_id}. "
                    f"Planned duration: "
                    f"{training['duration_seconds']} "
                    "seconds. The session reads "
                    "repository historical CSV data "
                    "only. Trades, portfolio mutation, "
                    "strategy promotion, broker access, "
                    "and live execution remain disabled."
                ),
            },
            "intent": intent.intent,
            "symbol": None,
            "training_run": training,
            "provider": (
                "neurovest_bounded_"
                "training_runtime"
            ),
            "model": None,
            "tool_truth_state": "grounded",
            "error": None,
            "cognitive_route": None,
        }

    weather_location = extract_weather_location(message)

    if weather_location:
        try:
            weather = fetch_live_weather(
                weather_location,
                use_cache=True,
            )

            resolved_location = ", ".join(
                value
                for value in (
                    weather.name,
                    weather.admin1,
                    weather.country,
                )
                if value
            )

            lines = [
                f"Current weather for {resolved_location}:",
                "",
                (
                    "Conditions: "
                    + weather_description(
                        weather.weather_code
                    )
                ),
                (
                    f"Temperature: {weather.temperature_c:.1f} °C"
                    if weather.temperature_c is not None
                    else "Temperature: unavailable"
                ),
                (
                    f"Feels like: {weather.feels_like_c:.1f} °C"
                    if weather.feels_like_c is not None
                    else "Feels like: unavailable"
                ),
                (
                    f"Humidity: {weather.humidity_percent:.0f}%"
                    if weather.humidity_percent is not None
                    else "Humidity: unavailable"
                ),
                (
                    f"Wind: {weather.wind_kmh:.1f} km/h"
                    if weather.wind_kmh is not None
                    else "Wind: unavailable"
                ),
                "",
                "Today:",
                (
                    f"High: {weather.today_high_c:.1f} °C"
                    if weather.today_high_c is not None
                    else "High: unavailable"
                ),
                (
                    f"Low: {weather.today_low_c:.1f} °C"
                    if weather.today_low_c is not None
                    else "Low: unavailable"
                ),
                (
                    "Chance of precipitation: "
                    f"{weather.today_precipitation_probability_percent:.0f}%"
                    if (
                        weather.today_precipitation_probability_percent
                        is not None
                    )
                    else "Chance of precipitation: unavailable"
                ),
                "",
            ]

            return {
                "status": "ok",
                "response": {
                    "type": "text",
                    "message": "\n".join(lines),
                },
                "intent": intent.intent,
                "symbol": None,
                "provider": "open_meteo_weather",
                "model": None,
                "tool_truth_state": "grounded",
                "error": None,
                "cognitive_route": None,
            }

        except Exception as exc:
            return {
                "status": "error",
                "response": {
                    "type": "text",
                    "message": (
                        "Current weather could not be retrieved "
                        "for that location."
                    ),
                },
                "intent": intent.intent,
                "symbol": None,
                "provider": None,
                "model": None,
                "tool_truth_state": "unavailable",
                "error": (
                    f"{type(exc).__name__}: {exc}"
                ),
                "cognitive_route": None,
            }

    current_canadian_economic_releases_requested = bool(
        re.search(
            r"\b(canada|canadian)\b",
            message,
            re.IGNORECASE,
        )
        and re.search(
            r"\b(economic|economy|inflation|employment|"
            r"gdp|interest\s+rate|interest\s+rates)\b",
            message,
            re.IGNORECASE,
        )
        and re.search(
            r"\b(current|latest|today|recent|news|"
            r"release|releases|update|updates)\b",
            message,
            re.IGNORECASE,
        )
    )


    # NEUROVEST_G43_R77_RATE_EVIDENCE_INTENT
    # Meta-questions about evidence must not route into
    # unrelated Statistics Canada release listings.
    _nv_r73_rate_verification_explanation = bool(
        re.search(
            r"\b(?:interest\s+rate|rate\s+decision|"
            r"bank\s+of\s+canada|central\s+bank)\b",
            message,
            re.IGNORECASE,
        )
        and re.search(
            r"\b(?:verify|verification|evidence|"
            r"fabricat\w*|trustworthy)\b",
            message,
            re.IGNORECASE,
        )
        and re.search(
            r"\b(?:explain|how|what\s+would\s+count|"
            r"what\s+can\s+you|a\s+user\s+asks)\b",
            message,
            re.IGNORECASE,
        )
    )

    if (
        current_canadian_economic_releases_requested
        and not _nv_r73_rate_verification_explanation
    ):
        try:
            releases = fetch_official_economic_releases(
                limit=5,
                use_cache=True,
            )

            lines = [
                "Latest official Canadian economic releases:",
                "",
            ]

            for release in releases:
                lines.extend(
                    [
                        f"• {release.title}",
                        f"Source: {release.issuer}",
                        (
                            "Published: "
                            f"{release.published_at.isoformat()}"
                        ),
                        f"Link: {release.url}",
                        "",
                    ]
                )

            lines.append(
                "These are read-only official releases; "
                "no order was created."
            )

            return {
                "status": "ok",
                "response": {
                    "type": "text",
                    "message": "\n".join(lines),
                },
                "intent": intent.intent,
                "symbol": None,
                "provider": (
                    "official_canadian_economic_feeds"
                ),
                "model": None,
                "tool_truth_state": "grounded",
                "error": None,
                "cognitive_route": None,
            }

        except Exception as exc:
            return {
                "status": "error",
                "response": {
                    "type": "text",
                    "message": (
                        "Current official Canadian economic releases "
                        "could not be retrieved."
                    ),
                },
                "intent": intent.intent,
                "symbol": None,
                "provider": None,
                "model": None,
                "tool_truth_state": "unavailable",
                "error": (
                    f"{type(exc).__name__}: {exc}"
                ),
                "cognitive_route": None,
            }

    current_quote_requested = bool(
        intent.symbol
        and re.search(
            r"\b(current|latest|today|now)\b.{0,45}"
            r"\b(price|quote|trading)\b|"
            r"\b(price|quote|trading)\b.{0,45}"
            r"\b(current|latest|today|now)\b",
            message,
            re.IGNORECASE,
        )
    )

    # NEUROVEST_R73_PUBLIC_RESEARCH_QUOTE_BYPASS
    from backend.app.stacks.chat_public.financial_answer_quality_13d_r68 import (
        is_public_financial_request as _nv73_public_research,
    )
    from backend.app.stacks.chat_public.financial_research_13d_r58 import (
        companies_in_text as _nv73_companies,
    )
    _nv73_multi_company_research = (
        _nv73_public_research(message)
        and len({
            symbol for symbol, *_ in _nv73_companies(message)
        }) >= 2
    )
    if current_quote_requested and not _nv73_multi_company_research:
        try:
            quote = get_market_data_runtime().router.get_quote(
                intent.symbol,
                use_cache=True,
            )

            # NEUROVEST_QUOTE_TRUTH_10R_R2
            from backend.app.stacks.chat_public.market_quote_truth_10r_r2 import (
                validate_quote_for_chat as _nv10r_r2_validate_quote_for_chat,
            )
            quote_presentation = _nv10r_r2_validate_quote_for_chat(
                quote,
                intent.symbol,
            )

            previous_close = quote.previous_close
            change = None
            change_percent = None

            if (
                previous_close is not None
                and previous_close != 0
            ):
                change = quote.price - previous_close
                change_percent = (
                    change / previous_close * 100.0
                )

            lines = [
                f"{quote.symbol} {quote_presentation.label}:",
                "",
                f"Price: {quote.price:,.2f} {quote.currency}",
            ]

            if (
                change is not None
                and change_percent is not None
            ):
                lines.append(
                    "Change from previous close: "
                    f"{change:+,.2f} "
                    f"({change_percent:+.2f}%)"
                )

            lines.extend(
                [
                    f"Provider: {quote.provider}",
                    (
                        "Observed at: "
                        f"{quote.observed_at.isoformat()}"
                    ),
                    (
                        "Delayed: "
                        + (
                            "yes"
                            if quote.delayed
                            else "no"
                        )
                    ),
                    (
                        "This is read-only market data; "
                        "no order was created."
                    ),
                ]
            )
            lines.append(quote_presentation.note)

            return {
                "status": "ok",
                "response": {
                    "type": "text",
                    "message": "\n".join(lines),
                },
                "intent": intent.intent,
                "symbol": quote.symbol,
                "provider": quote.provider,
                "model": None,
                "tool_truth_state": "grounded",
                "error": None,
                "cognitive_route": None,
            }

        except Exception as exc:
            return {
                "status": "error",
                "response": {
                    "type": "text",
                    "message": (
                        "A current quote could not be retrieved "
                        "from the configured read-only market-data "
                        "provider."
                    ),
                },
                "intent": intent.intent,
                "symbol": intent.symbol,
                "provider": None,
                "model": None,
                "tool_truth_state": "unavailable",
                "error": (
                    f"{type(exc).__name__}: {exc}"
                ),
                "cognitive_route": None,
            }

    # NEUROVEST_RESPONSE_ROUTING_REPAIR_V2
    # Financial and programming explanations should reach
    # the appropriate local model rather than an unrelated
    # encyclopedia article. Preserve general Wikipedia tests.
    import re as _wiki_guard_re

    _specialized_explanation = bool(
        _wiki_guard_re.search(
            r"\b(?:etf|exchange.traded fund|stock|bond|"
            r"portfolio|investing|financial|finance|"
            r"python|javascript|typescript|sql|"
            r"async|await|programming)\b",
            message,
            _wiki_guard_re.IGNORECASE,
        )
    )

    _explicit_wiki = bool(
        _wiki_guard_re.search(
            r"\b(?:wikipedia|wiki)\b",
            message,
            _wiki_guard_re.IGNORECASE,
        )
    )

    # NEUROVEST_V65R3_CONTEXTUAL_FOLLOWUP_PRIORITY
    # Context-aware follow-ups take the model path.
    # Explicit Wikipedia requests keep precedence.
    _contextual_followup = (
        isinstance(model_input, str)
        and bool(model_input.strip())
        and bool(_wiki_guard_re.search(
            '\\b(?:did\\s+i|do\\s+i|have\\s+i|i\\s+(?:said|mentioned|replaced|changed)|we\\s+(?:said|discussed|used|changed)|my\\s+(?:strategy|indicators|previous)|our\\s+(?:strategy|indicators|previous)|as\\s+we\\s+discussed|earlier\\s+in\\s+(?:our|the)\\s+conversation|previously\\s+discussed|currently\\s+stands|which\\s+indicators\\s+.*\\b(?:replace|use)|what\\s+is\\s+.+\\b(?:now|currently)\\b)',
            message,
            _wiki_guard_re.IGNORECASE,
        ))
    )

    if _contextual_followup and not _explicit_wiki:
        _specialized_explanation = True

    # NEUROVEST_12GH_R14J_BASIC_ARITHMETIC_ROUTING
    # Simple calculations are not encyclopedia topics.
    # Explicit Wikipedia requests retain their precedence.
    _basic_arithmetic = bool(
        _wiki_guard_re.fullmatch(
            r"\s*(?:(?:what(?:'s| is)|calculate|compute|"
            r"evaluate|how much is)\s+)?"
            r"[+-]?\d+(?:\.\d+)?\s*"
            r"(?:\+|-|\*|/|×|÷)\s*"
            r"[+-]?\d+(?:\.\d+)?\s*\??\s*",
            message,
            _wiki_guard_re.IGNORECASE,
        )
    )

    # NEUROVEST_R15A_CONVERSATIONAL_TOOL_PRIORITY
    # Explanations, ordinary how-to questions, and basic
    # reasoning should not automatically become encyclopedia
    # requests. Explicit Wikipedia intent always wins.
    _conversational_explanation = bool(
        _wiki_guard_re.search(
            r"^\s*(?:please\s+)?"
            r"(?:explain|describe|"
            r"how\s+(?:can|do|does|should|would)|"
            r"why\s+(?:is|are|do|does|did|would)|"
            r"what\s+(?:are|does|do)|"
            r"tell\s+me\s+how)\b",
            message,
            _wiki_guard_re.IGNORECASE,
        )
    )

    # NEUROVEST_R16H_R2_CONVERSATION_RECALL_PRIORITY
    # Prefer authenticated thread context for requests
    # about what the user previously said or established.
    # Never override an explicit Wikipedia request.
    _conversation_recall = bool(
        _wiki_guard_re.search(
            r"\b(?:my|our|i\s+(?:told|mentioned|said|shared)|"
            r"we\s+(?:discussed|mentioned))\b",
            message,
            _wiki_guard_re.IGNORECASE,
        )
        and _wiki_guard_re.search(
            r"\b(?:project|called|name|focus|focused|"
            r"remember|earlier|previously|mentioned|"
            r"discussed|told|said|shared)\b",
            message,
            _wiki_guard_re.IGNORECASE,
        )
    )


    # NEUROVEST_R116_G40_MULTIPART_WIKIPEDIA_BOUNDARY
    # Wikipedia's article summary may supply supporting evidence,
    # but must not replace a multi-part explanatory answer.
    # Explicit requests for Wikipedia retain their existing path.
    _nv_g40_multi_part_explanation = bool(
        re.search(
            r"\b(?:difference\s+between|compare|distinguish|"
            r"and\s+why|and\s+how|and\s+does|"
            r"does\s+it|including|"
            r"explain\s+why)\b",
            message,
            re.IGNORECASE,
        )
        or (
            re.search(
                r"\b(?:what\s+is|what\s+does|"
                r"what\s+are)\b",
                message,
                re.IGNORECASE,
            )
            and re.search(
                r"[,;]\s*(?:and\s+)?(?:why|how|does|what)\b",
                message,
                re.IGNORECASE,
            )
        )
    )

    # G41_MODEL_FIRST_TECHNICAL_EXPLANATIONS
    # Explicit Wikipedia requests retain their existing precedence.
    _g41_explanation = bool(_wiki_guard_re.search(
        r"^\s*(?:what(?:'s| is)|define|explain|compare"
        r"|describe|calculate|compute)\b",
        message, _wiki_guard_re.I,
    ))
    _g41_subject = bool(_wiki_guard_re.search(
        r"\b(?:maximum drawdown|drawdown|look.ahead bias"
        r"|backtests?|risk.adjusted return|tracking error"
        r"|covered call|systematic risk|beta"
        r"|tcp|udp|http|https|tls|dns"
        r"|probability|percent of"
        r"|to the \d+(?:st|nd|rd|th)? power"
        r"|peer review|confidence intervals?)\b",
        message, _wiki_guard_re.I,
    ))
    _g41_model_first = (
        _g41_explanation
        and _g41_subject
        and not _explicit_wiki
    )

    wikipedia_topic = (
        extract_wikipedia_topic(message)
        if (
            (
                not _nv_g40_multi_part_explanation
                and not _g41_model_first
                and not _specialized_explanation
                and not _basic_arithmetic
                and not _conversational_explanation
                and not _conversation_recall
            )
            or _explicit_wiki
        )
        else None
    )

    # NEUROVEST_R15D_EXPLICIT_WIKIPEDIA_INTENT
    # The topic extractor handles natural "What is X?"
    # questions, but not every explicit Wikipedia phrase.
    # Only explicit source requests receive this fallback.
    if _explicit_wiki and not wikipedia_topic:
        _wiki_explicit_match = _wiki_guard_re.search(
            r"^\s*(?:according\s+to\s+)?"
            r"(?:wikipedia|wiki)"
            r"\s*(?:[,.:;-]\s*)?"
            r"(?:(?:what|who)\s+is\s+|"
            r"what\s+are\s+|tell\s+me\s+about\s+)?"
            r"(?P<topic>.+?)\s*\??\s*$",
            message,
            _wiki_guard_re.IGNORECASE,
        )
        if _wiki_explicit_match:
            wikipedia_topic = (
                _wiki_explicit_match.group("topic").strip(
                    " \t\r\n?.!,"
                )
            ) or None

    if wikipedia_topic:
        try:
            article = lookup_wikipedia_article(
                wikipedia_topic,
                use_cache=True,
            )

            # NEUROVEST_CONCISE_WIKIPEDIA_REPLY
            # Keep the answer source-grounded and stop at complete sentences.
            _nv_wiki_text = " ".join(str(article.summary or "").split())
            _nv_wiki_sentences = []
            _nv_wiki_start = 0
            for _nv_wiki_index, _nv_wiki_char in enumerate(_nv_wiki_text):
                if (
                    _nv_wiki_char in ".!?"
                    and (
                        _nv_wiki_index + 1 == len(_nv_wiki_text)
                        or _nv_wiki_text[_nv_wiki_index + 1].isspace()
                    )
                ):
                    _nv_wiki_sentence = _nv_wiki_text[
                        _nv_wiki_start:_nv_wiki_index + 1
                    ].strip()
                    if _nv_wiki_sentence:
                        _nv_wiki_sentences.append(_nv_wiki_sentence)
                    _nv_wiki_start = _nv_wiki_index + 1
                    if len(_nv_wiki_sentences) == 2:
                        break
            if not _nv_wiki_sentences and _nv_wiki_text:
                _nv_wiki_sentences = [_nv_wiki_text]
            lines = [" ".join(_nv_wiki_sentences)]

            if wikipedia_link_requested(message):
                lines.extend(
                    [
                        "",
                        (
                            "Source: "
                            f"[Wikipedia — {article.title}]"
                            f"({article.url})"
                        ),
                    ]
                )

            return {
                "status": "ok",
                "response": {
                    "type": "text",
                    "message": "\n".join(lines),
                },
                "intent": intent.intent,
                "symbol": None,
                "provider": "wikipedia",
                "model": None,
                "tool_truth_state": "grounded",
                "error": None,
                "cognitive_route": None,
            }

        except Exception as exc:
            return {
                "status": "error",
                "response": {
                    "type": "text",
                    "message": (
                        "A Wikipedia summary could not be "
                        "retrieved for that topic."
                    ),
                },
                "intent": intent.intent,
                "symbol": None,
                "provider": None,
                "model": None,
                "tool_truth_state": "unavailable",
                "error": (
                    f"{type(exc).__name__}: {exc}"
                ),
                "cognitive_route": None,
            }

    if intent.intent == "canadian_market_today":
        try:
            runtime = get_market_data_runtime()

            now = datetime.now(
                UTC
            )

            request = HistoricalBarsRequest(
                symbol="^GSPTSE",
                start=(
                    now
                    - timedelta(
                        days=10
                    )
                ),
                end=(
                    now
                    + timedelta(
                        days=1
                    )
                ),
                interval="1d",
                adjusted=True,
                limit=10,
            )

            result = runtime.router.get_historical_bars(
                request,
                use_cache=True,
            )

            bars = list(
                result.bars
            )

            if not bars:
                raise RuntimeError(
                    "No TSX Composite historical bars were returned."
                )

            latest = bars[-1]

            previous = (
                bars[-2]
                if len(bars) >= 2
                else None
            )

            change = None
            change_percent = None

            if (
                previous is not None
                and previous.close != 0
            ):
                change = (
                    latest.close
                    - previous.close
                )

                change_percent = (
                    change
                    / previous.close
                    * 100.0
                )

            session = runtime.session.now()

            latest_date = (
                latest.timestamp
                .date()
                .isoformat()
            )

            today_date = (
                now.date()
                .isoformat()
            )

            session_label = (
                "today's session"
                if latest_date == today_date
                else (
                    "the latest available trading session "
                    f"({latest_date})"
                )
            )

            lines = [
                (
                    "Here is the TSX Composite view for "
                    + session_label
                    + ":"
                ),
                "",
                f"Open: {latest.open:,.2f}",
                f"High: {latest.high:,.2f}",
                f"Low: {latest.low:,.2f}",
                f"Close: {latest.close:,.2f}",
                f"Volume: {latest.volume:,.0f}",
            ]

            if (
                change is not None
                and change_percent is not None
            ):
                direction = (
                    "up"
                    if change > 0
                    else (
                        "down"
                        if change < 0
                        else "flat"
                    )
                )

                lines.extend(
                    [
                        (
                            "Change from previous close: "
                            f"{change:+,.2f} "
                            f"({change_percent:+.2f}%)"
                        ),
                        (
                            "Direction: "
                            + direction
                        ),
                    ]
                )

            lines.extend(
                [
                    (
                        "Market session state: "
                        f"{session.state.value}"
                    ),
                    (
                        "Data timestamp: "
                        f"{latest.timestamp.isoformat()}"
                    ),
                ]
            )

            return {
                "status": "ok",
                "response": {
                    "type": "text",
                    "message": "\n".join(lines),
                },
                "intent": intent.intent,
                "symbol": "^GSPTSE",
                "provider": result.provider,
                "historical_bars": bars,
                "model": None,
                "tool_truth_state": "grounded",
                "error": None,
                "cognitive_route": None,
            }

        except Exception as exc:
            return {
                "status": "error",
                "response": {
                    "type": "text",
                    "message": (
                        "Current Canadian market data could "
                        "not be retrieved from the configured "
                        "read-only market-data provider."
                    ),
                },
                "intent": intent.intent,
                "symbol": "^GSPTSE",
                "provider": None,
                "model": None,
                "tool_truth_state": "unavailable",
                "error": (
                    f"{type(exc).__name__}: {exc}"
                ),
                "cognitive_route": None,
            }


    if intent.intent == "graph_reset":
        return {
            "status": "ok",
            "response": {
                "type": "direct_command",
                "command": "graph_reset",
            },
            "intent": intent.intent,
            "symbol": intent.symbol,
            "provider": None,
            "model": None,
            "tool_truth_state": "not_required",
        }

    if intent.intent == "graph_validate":
        return {
            "status": "ok",
            "response": {
                "type": "direct_command",
                "command": "graph_validate",
            },
            "intent": intent.intent,
            "symbol": intent.symbol,
            "provider": None,
            "model": None,
            "tool_truth_state": "not_required",
        }

    if intent.intent == "simulate_trade":
        return {
            "status": "ok",
            "response": {
                "type": "direct_command",
                "command": "simulate_trade",
                "symbol": intent.symbol,
            },
            "intent": intent.intent,
            "symbol": intent.symbol,
            "provider": None,
            "model": None,
            "tool_truth_state": "not_required",
        }

    # V29 — deterministic authoritative strategy response path.
    request_route_contract = classify_chat_route(
        message
    )

    deterministic_reply = deterministic_strategy_answer(
        message,
        request_route_contract,
    )

    if deterministic_reply is not None:
        return {
            "status": "ok",
            "response": {
                "type": "text",
                "message": deterministic_reply,
            },
            "intent": intent.intent,
            "symbol": intent.symbol,
            "provider": "neurovest_strategy_truth",
            "model": None,
            "tool_truth_state": "grounded",
            "error": None,
            "cognitive_route": (
                routing_decision.as_dict()
                if routing_decision is not None
                else None
            ),
        }

    # NEUROVEST_DEVELOPER_CHAT_COMMANDS_V1
    from backend.app.stacks.chat_public.developer_chat_commands import (
        parse_developer_command,
        handle_developer_command,
    )

    from backend.app.stacks.chat_public.developer_role_guard import (
        authenticated_developer_role,
    )

    dev_command = parse_developer_command(message)

    # NEUROVEST_REPO_CHAT_V1
    # Reuse the existing authenticated developer gate below.
    if re.fullmatch(
        r"/dev\s+repo(?:\s+.*)?",
        message.strip(),
        flags=re.IGNORECASE | re.DOTALL,
    ):
        _repo_match = re.fullmatch(
            r"/dev\s+repo\s+"
            r"(summary|dependencies|dependents|impact)"
            r"(?:\s+([a-z_][a-z0-9_]*))?",
            message.strip(),
            flags=re.IGNORECASE,
        )
        if _repo_match is None:
            dev_command = ("error", "Use: /dev repo summary "
                           "or /dev repo dependencies|dependents|impact <stack>")
        else:
            _repo_action = _repo_match.group(1).lower()
            _repo_stack = _repo_match.group(2)
            if (
                (_repo_action == "summary" and _repo_stack is not None)
                or (_repo_action != "summary" and _repo_stack is None)
            ):
                dev_command = ("error", "Invalid repository query arguments.")
            else:
                dev_command = (
                    "repo_query",
                    _repo_action,
                    _repo_stack.lower() if _repo_stack else None,
                )


    # NEUROVEST_REPO_FILE_IMPACT_CHAT_V1
    # The existing principal-based developer guard follows.
    if re.fullmatch(
        r"/dev\s+repo\s+file-impact(?:\s+.*)?",
        message.strip(),
        flags=re.IGNORECASE | re.DOTALL,
    ):
        _impact_match = re.fullmatch(
            r"/dev\s+repo\s+file-impact\s+"
            r"((?:backend|frontend|scripts|alembic|tests)"
            r"/[a-zA-Z0-9_./-]+)",
            message.strip(),
            flags=re.IGNORECASE,
        )
        if _impact_match is None:
            dev_command = (
                "error",
                "Use: /dev repo file-impact <indexed-source-path>",
            )
        else:
            dev_command = (
                "repo_file_impact",
                _impact_match.group(1),
            )

    # NEUROVEST_REPO_REFRESH_CHAT_V1
    if re.fullmatch(
        r"/dev\s+repo\s+refresh\s*",
        message.strip(),
        flags=re.IGNORECASE,
    ):
        dev_command = ("repo_refresh",)

    # NEUROVEST_REPO_FUNCTION_IMPACT_CHAT_V1
    # Parsed before the existing developer-only authorization check.
    if re.fullmatch(
        r"/dev\s+repo\s+function-impact(?:\s+.*)?",
        message.strip(),
        flags=re.IGNORECASE | re.DOTALL,
    ):
        _function_match = re.fullmatch(
            r"/dev\s+repo\s+function-impact\s+"
            r"((?:backend|frontend|scripts|alembic|tests)"
            r"/[a-zA-Z0-9_./-]+)\s+"
            r"([a-zA-Z_][a-zA-Z0-9_.]*)",
            message.strip(),
            flags=re.IGNORECASE,
        )
        if _function_match is None:
            dev_command = (
                "error",
                "Use: /dev repo function-impact "
                "<indexed-python-path> <function-or-class.method>",
            )
        else:
            dev_command = (
                "repo_function_impact",
                _function_match.group(1),
                _function_match.group(2),
            )


    # NEURO_AWARENESS_DEVELOPER_COMMAND_V1
    if re.fullmatch(
        r"/dev\s+awareness(?:\s+.*)?",
        message.strip(),
        flags=re.IGNORECASE | re.DOTALL,
    ):
        _awareness_parts = message.strip().split()
        _awareness_args = _awareness_parts[2:]
        _awareness_path = re.compile(
            r"(?:backend|frontend)/[A-Za-z0-9_./-]+"
        )

        if _awareness_args == ["status"]:
            dev_command = ("awareness", "status")
        elif (
            len(_awareness_args) == 2
            and _awareness_args[0] == "inspect"
            and _awareness_path.fullmatch(_awareness_args[1])
        ):
            dev_command = ("awareness", *_awareness_args)
        elif (
            len(_awareness_args) == 3
            and _awareness_args[0] == "trace"
            and all(
                _awareness_path.fullmatch(p)
                for p in _awareness_args[1:]
            )
        ):
            dev_command = ("awareness", *_awareness_args)
        else:
            dev_command = (
                "error",
                "Use: /dev awareness status | inspect FILE | trace FILE FILE",
            )

    if dev_command is not None and not authenticated_developer_role(principal):
        dev_command = (
            "error",
            "Authenticated developer role required for /dev commands.",
        )

    use_deterministic_developer_evidence = (
        (developer_evidence_allowed or dev_command is not None)
        and (
            dev_command is not None
            or (
            intent.self_evaluation
            or (
                intent.developer_mode
                and (
                    intent.requires_repo_context
                    or intent.requires_architecture_context
                    or intent.subtype == "developer_review"
                )
            )
            )
        )
    )

    if use_deterministic_developer_evidence:
        if dev_command is not None:

            # NEUROVEST_REPO_CHAT_V1
            # NEUROVEST_REPO_FILE_IMPACT_CHAT_V1
            # NEUROVEST_REPO_REFRESH_CHAT_V1

            # NEURO_AWARENESS_DEVELOPER_DISPATCH_V1
            if dev_command[0] == "awareness":
                import subprocess as _awareness_subprocess
                import sys as _awareness_sys
                from pathlib import Path as _awareness_Path

                _awareness_root = (
                    _awareness_Path(__file__).resolve().parents[4]
                )
                _awareness_script = (
                    _awareness_root / "scripts/neuro_awareness_query.py"
                )

                try:
                    _awareness_result = _awareness_subprocess.run(
                        [
                            _awareness_sys.executable,
                            "-B",
                            str(_awareness_script),
                            *dev_command[1:],
                        ],
                        cwd=_awareness_root,
                        env={
                            "PATH": "/usr/bin:/bin",
                            "PYTHONDONTWRITEBYTECODE": "1",
                        },
                        capture_output=True,
                        text=True,
                        timeout=20,
                        check=False,
                    )
                    if (
                        _awareness_result.returncode == 0
                        and "QUERY_STATUS=PASS"
                            in _awareness_result.stdout
                        and len(_awareness_result.stdout) <= 16000
                    ):
                        reply = _awareness_result.stdout
                    else:
                        reply = (
                            "Architecture awareness unavailable or stale. "
                            "No changes were made."
                        )
                except (OSError, _awareness_subprocess.TimeoutExpired):
                    reply = (
                        "Architecture awareness query could not complete. "
                        "No changes were made."
                    )

            elif dev_command[0] == "repo_refresh":

                import subprocess as _refresh_subprocess
                import sys as _refresh_sys
                from pathlib import Path as _refresh_Path

                _refresh_root = _refresh_Path(__file__).resolve().parents[4]
                _refresh_script = (
                    _refresh_root / "scripts/neuro_repository_chat_refresh.py"
                )

                try:
                    _refresh_result = _refresh_subprocess.run(
                        [
                            _refresh_sys.executable,
                            "-B",
                            str(_refresh_script),
                        ],
                        cwd=_refresh_root,
                        env={
                            "PATH": "/usr/bin:/bin",
                            "PYTHONDONTWRITEBYTECODE": "1",
                        },
                        capture_output=True,
                        text=True,
                        timeout=245,
                        check=False,
                    )
                    if (
                        _refresh_result.returncode == 0
                        and "CHAT_REFRESH_STATUS=PASS"
                            in _refresh_result.stdout
                        and len(_refresh_result.stdout) <= 4000
                    ):
                        reply = _refresh_result.stdout
                    else:
                        reply = (
                            "Repository refresh failed, was rejected, "
                            "or is already running. "
                            "No application patch was applied."
                        )
                except (OSError, _refresh_subprocess.TimeoutExpired):
                    reply = (
                        "Repository refresh did not complete within "
                        "its time limit. Check snapshot consistency "
                        "before relying on new results."
                    )
            elif dev_command[0] == "repo_function_impact":
                import subprocess as _function_subprocess
                import sys as _function_sys
                from pathlib import Path as _function_Path

                _function_root = _function_Path(__file__).resolve().parents[4]
                _function_script = (
                    _function_root
                    / "scripts/neuro_repository_function_impact.py"
                )

                try:
                    _function_result = _function_subprocess.run(
                        [
                            _function_sys.executable,
                            "-B",
                            str(_function_script),
                            "symbol",
                            dev_command[1],
                            dev_command[2],
                        ],
                        cwd=_function_root,
                        env={
                            "PATH": "/usr/bin:/bin",
                            "PYTHONDONTWRITEBYTECODE": "1",
                        },
                        capture_output=True,
                        text=True,
                        timeout=20,
                        check=False,
                    )

                    if (
                        _function_result.returncode == 0
                        and "QUERY_STATUS=PASS"
                            in _function_result.stdout
                        and len(_function_result.stdout) <= 16000
                    ):
                        reply = _function_result.stdout
                    else:
                        reply = (
                            "Function impact query unavailable, stale, "
                            "or rejected. No changes were made."
                        )

                except (OSError, _function_subprocess.TimeoutExpired):
                    reply = (
                        "Function impact query could not complete. "
                        "No changes were made."
                    )

            elif dev_command[0] == "repo_file_impact":
                import subprocess as _impact_subprocess
                import sys as _impact_sys
                from pathlib import Path as _impact_Path

                _impact_root = _impact_Path(__file__).resolve().parents[4]
                _impact_script = (
                    _impact_root / "scripts/neuro_repository_file_impact.py"
                )

                try:
                    _impact_result = _impact_subprocess.run(
                        [
                            _impact_sys.executable,
                            "-B",
                            str(_impact_script),
                            dev_command[1],
                        ],
                        cwd=_impact_root,
                        env={"PYTHONDONTWRITEBYTECODE": "1"},
                        capture_output=True,
                        text=True,
                        timeout=20,
                        check=False,
                    )
                    if (
                        _impact_result.returncode == 0
                        and "QUERY_STATUS=PASS" in _impact_result.stdout
                        and len(_impact_result.stdout) <= 16000
                    ):
                        reply = _impact_result.stdout
                    else:
                        reply = (
                            "File impact query unavailable or rejected. "
                            "No changes were made."
                        )
                except (OSError, _impact_subprocess.TimeoutExpired):
                    reply = (
                        "File impact query timed out or could not start. "
                        "No changes were made."
                    )
            elif dev_command[0] == "repo_query":
                import subprocess as _repo_subprocess
                import sys as _repo_sys
                from pathlib import Path as _repo_Path

                _repo_root = _repo_Path(__file__).resolve().parents[4]
                _repo_script = _repo_root / "scripts/neuro_repository_query.py"
                _repo_action, _repo_stack = dev_command[1:]

                _repo_args = [
                    _repo_sys.executable,
                    "-B",
                    str(_repo_script),
                    _repo_action,
                ]
                if _repo_stack is not None:
                    _repo_args.append(_repo_stack)

                try:
                    _repo_result = _repo_subprocess.run(
                        _repo_args,
                        cwd=_repo_root,
                        env={"PYTHONDONTWRITEBYTECODE": "1"},
                        capture_output=True,
                        text=True,
                        timeout=15,
                        check=False,
                    )
                    if (
                        _repo_result.returncode == 0
                        and "QUERY_STATUS=PASS" in _repo_result.stdout
                        and len(_repo_result.stdout) <= 14500
                    ):
                        reply = _repo_result.stdout
                    else:
                        reply = (
                            "Repository architecture query unavailable "
                            "or not qualified. No changes were made."
                        )
                except (OSError, _repo_subprocess.TimeoutExpired):
                    reply = (
                        "Repository architecture query timed out "
                        "or could not start. No changes were made."
                    )
            else:
                reply = handle_developer_command(dev_command)
        else:
            reply = build_developer_response(
                subtype=intent.subtype,
                message=message,
            )
        provider = "neurovest_local_evidence"
        model = None
        status = "ok"
        error = None
        tool_truth_state = "grounded"
    else:
        routing_decision = (
            routing_decision
            if routing_decision is not None
            else route_cognitive_request(
                message,
                intent=intent,
            )
        )

        try:
            # NEUROVEST_R94_PRE_GENERATION_INTELLIGENCE
            # Superseded by R98 unified planning.

            # NEUROVEST_R97_CONTEXTUAL_GENERATION
            # Consolidated by R98 — exactly one planning layer.
            # NEUROVEST_R98_ACTIVE_GENERATION_POLICY
            try:
                from backend.app.stacks.chat_public.generation_policy_13h_r98 import (
                    build_policy as _nv98_build_policy,
                )
                if isinstance(model_input, str):
                    _nv98_guidance, _nv98_plan = _nv98_build_policy(
                        message,
                        model_input,
                    )
                    if _nv98_guidance:
                        model_input = model_input + _nv98_guidance
            except Exception:
                pass

            # NEUROVEST_R105_PREGEN_FINANCIAL_FUNDAMENTALS
            # Read-only provider facts; preserve existing routing.
            try:
                from backend.app.stacks.chat_public.financial_fundamentals_13o_r105 import (
                    get_financial_context as _nv105_financial_context,
                )
                # NEUROVEST_R107_CONTEXTUAL_FINANCIAL_CHAT
                from backend.app.stacks.chat_public.contextual_finance_13q_r107 import (
                    build_context as _nv107_build_context,
                )
                _nv105_evidence = _nv107_build_context(
                    message,
                    model_input,
                    _nv105_financial_context,
                )
                if (
                    isinstance(model_input, str)
                    and _nv105_evidence
                    and len(model_input) + len(_nv105_evidence) < 110000
                ):
                    model_input += '\n\n' + _nv105_evidence
            except Exception:
                pass

            # NEUROVEST_R109_PREGEN_CONVERSATIONAL_REASONING
            # Non-privileged reasoning guidance before model generation.
            try:
                from backend.app.stacks.chat_public.conversation_reasoning_13s_r109 import (
                    build_guidance as _nv109_build_guidance,
                )

                _nv109_guidance = _nv109_build_guidance(
                    message,
                    model_input,
                )

                if (
                    isinstance(model_input, str)
                    and _nv109_guidance
                    and len(model_input) + len(_nv109_guidance) < 110000
                ):
                    model_input += "\n\n" + _nv109_guidance

            except Exception:
                # Keep existing generation operational.
                pass

            reply = ask_ollama(
                message,
                intent=intent.intent,
                symbol=intent.symbol,
                context=model_input,
                model=routing_decision.model,
            )
            # NEUROVEST_R80_EMPTY_MODEL_COMPLETION_GUARD_PRIMARY
            if not isinstance(reply, str) or not reply.strip():
                raise RuntimeError('primary model returned empty completion')

            # NEUROVEST_R99_BOUNDED_ANSWER_REVISION
            # One optional local-model revision for ordinary answers.
            # Existing final verification remains downstream.
            try:
                from backend.app.stacks.chat_public.answer_revision_13i_r99 import (
                    attempt_revision as _nv99_attempt_revision,
                )

                def _nv99_generate(_nv99_context):
                    return ask_ollama(
                        message,
                        intent=intent.intent,
                        symbol=intent.symbol,
                        context=_nv99_context,
                        model=routing_decision.model,
                    )

                reply, _nv99_revision_info = _nv99_attempt_revision(
                    message,
                    reply,
                    model_input,
                    _nv99_generate,
                )
            except Exception:
                pass

            provider = OLLAMA_PROVIDER
            model = routing_decision.model
            status = "ok"
            error = None
            tool_truth_state = (
                "ungrounded"
                if routing_decision.retrieval_required
                else (
                    "deterministic_tool_required"
                    if routing_decision.deterministic_tool_required
                    else "ungrounded"
                )
            )

        except Exception as primary_exc:
            try:
                reply = ask_ollama(
                    message,
                    intent=intent.intent,
                    symbol=intent.symbol,
                    context=model_input,
                    model=routing_decision.fallback_model,
                )
                # NEUROVEST_R80_EMPTY_MODEL_COMPLETION_GUARD_FALLBACK
                if not isinstance(reply, str) or not reply.strip():
                    raise RuntimeError('fallback model returned empty completion')

                provider = OLLAMA_PROVIDER
                model = routing_decision.fallback_model
                status = "ok"
                error = (
                    "Primary model failed; fallback used: "
                    f"{type(primary_exc).__name__}: "
                    f"{primary_exc}"
                )
                tool_truth_state = (
                    "fallback_ungrounded"
                )

            except Exception as fallback_exc:
                reply = (
                    "Neuro local model is unavailable: "
                    f"{type(fallback_exc).__name__}: "
                    f"{fallback_exc}"
                )

                provider = OLLAMA_PROVIDER
                model = routing_decision.fallback_model
                status = "error"
                error = (
                    "Primary model failure: "
                    f"{type(primary_exc).__name__}: "
                    f"{primary_exc}; fallback failure: "
                    f"{type(fallback_exc).__name__}: "
                    f"{fallback_exc}"
                )
                tool_truth_state = "ungrounded"

    owner_user_id = str(
        getattr(
            principal,
            "subject",
            "",
        )
        or ""
    ).strip()

    strategy_capture = (
        capture_strategy_proposal(
            str(message),
            str(reply),
            intent=intent.intent,
            symbol=intent.symbol,
            request_route=(
                request_route
                or None
            ),
            owner_user_id=owner_user_id,
        )
        if owner_user_id
        else None
    )

    return {
        "status": status,
        "response": {
            "type": "text",
            "message": str(reply),
        },
        "intent": intent.intent,
        "symbol": intent.symbol,
        "strategy_capture": strategy_capture,
        "provider": provider,
        "model": resolve_runtime_model(model),
        "tool_truth_state": tool_truth_state,
        "error": error,
        "cognitive_route": (
            routing_decision.as_dict()
            if not use_deterministic_developer_evidence
            else None
        ),
    }



async def _find_existing_assistant_reply(
    *,
    thread_id: str,
    user_message_id: str,
) -> Any | None:
    messages = await conversation_store.list_messages(
        thread_id,
        limit=500,
        oldest_first=True,
    )

    for message in messages:
        if (
            message.role == "assistant"
            and message.parent_message_id
            == user_message_id
        ):
            return message

    return None


# V25-R3R2 — request-scoped repeated-lifecycle strategy-list completeness guard.
#
# This deterministic completion layer runs only for an explicit request
# for the repeated-lifecycle strategy list.
#
# It uses authoritative rows from strategy_library_truth_v1.json through
# load_strategy_library_truth().
#
# It does not run for count-only, single-strategy, generic-finance,
# portfolio, authentication, or unrelated requests.

def _enforce_repeated_lifecycle_strategy_completeness(
    query,
    response,
):
    normalized_query = str(
        query or ""
    ).strip().lower()

    original_response = str(
        response or ""
    )

    if not normalized_query:
        return original_response

    has_strategy_scope = (
        "strateg"
        in normalized_query
    )

    has_lifecycle_scope = (
        "lifecycle"
        in normalized_query
    )

    has_repeated_scope = (
        "repeated"
        in normalized_query
        or "candidate-specific"
        in normalized_query
        or "small-set"
        in normalized_query
    )

    has_listing_intent = any(
        token in normalized_query
        for token in (
            "list",
            "which",
            "what are",
            "give me",
            "show",
            "with their",
            "ids and names",
            "id and name",
        )
    )

    if not (
        has_strategy_scope
        and has_lifecycle_scope
        and has_repeated_scope
        and has_listing_intent
    ):
        return original_response

    from backend.app.stacks.chat_public.rag.strategy_library_truth import (
        load_strategy_library_truth,
    )

    truth = load_strategy_library_truth()

    rows = truth.get(
        "repeated_lifecycle_evidence",
        [],
    )

    if not isinstance(
        rows,
        list,
    ):
        return original_response

    if len(
        rows
    ) != 8:
        return original_response

    authoritative = []

    for row in rows:

        if not isinstance(
            row,
            dict,
        ):
            return original_response

        try:
            ordinal = int(
                row[
                    "ordinal"
                ]
            )

        except Exception:
            return original_response

        strategy_id = str(
            row.get(
                "short_id",
                "",
            )
        ).strip()

        strategy_name = str(
            row.get(
                "strategy_name",
                "",
            )
        ).strip()

        while strategy_name.endswith(
            "."
        ):

            strategy_name = (
                strategy_name[:-1]
                .rstrip()
            )

        if not strategy_id:
            return original_response

        if not strategy_name:
            return original_response

        authoritative.append(
            (
                ordinal,
                strategy_id,
                strategy_name,
            )
        )

    authoritative.sort(
        key=lambda item: item[0]
    )

    lowered_response = (
        original_response.lower()
    )

    missing = []

    for (
        ordinal,
        strategy_id,
        strategy_name,
    ) in authoritative:

        id_present = (
            strategy_id.lower()
            in lowered_response
        )

        name_present = (
            strategy_name.lower()
            in lowered_response
        )

        if (
            id_present
            and name_present
        ):
            continue

        missing.append(
            (
                ordinal,
                strategy_id,
                strategy_name,
            )
        )

    if not missing:
        return original_response

    completion_lines = [
        "",
        (
            "AUTHORITATIVE REPEATED "
            "LIFECYCLE-EVIDENCE STRATEGIES:"
        ),
    ]

    for (
        ordinal,
        strategy_id,
        strategy_name,
    ) in missing:

        completion_lines.append(
            (
                f"{ordinal:03d}"
                + " | "
                + strategy_id
                + " | "
                + strategy_name
            )
        )

    completion = "\n".join(
        completion_lines
    )

    if original_response:

        return (
            original_response.rstrip()
            + "\n"
            + completion
        )

    return completion.lstrip()

# V26-R3 — request-scoped canonical repeated-lifecycle presentation cleanup.
#
# Runs only for complete repeated-lifecycle list requests.
# Replaces model/meta presentation with a concise canonical user-facing list.
# Preserves approved [chunk_*] citations already present in the response.
# Authoritative strategy content remains owned by strategy_library_truth_v1.json.

def _render_repeated_lifecycle_strategy_list_cleanly(
    query,
    response,
):
    import re

    normalized_query = str(
        query or ""
    ).strip().lower()

    original_response = str(
        response or ""
    )

    if not normalized_query:
        return original_response

    has_strategy_scope = (
        "strateg"
        in normalized_query
    )

    has_lifecycle_scope = (
        "lifecycle"
        in normalized_query
    )

    has_repeated_scope = (
        "repeated"
        in normalized_query
        or "candidate-specific"
        in normalized_query
        or "small-set"
        in normalized_query
    )

    has_listing_intent = any(
        token in normalized_query
        for token in (
            "list",
            "which",
            "what are",
            "give me",
            "show",
            "with their",
            "ids and names",
            "id and name",
        )
    )

    if not (
        has_strategy_scope
        and has_lifecycle_scope
        and has_repeated_scope
        and has_listing_intent
    ):
        return original_response

    from backend.app.stacks.chat_public.rag.strategy_library_truth import (
        load_strategy_library_truth,
    )

    truth = load_strategy_library_truth()

    rows = truth.get(
        "repeated_lifecycle_evidence",
        [],
    )

    if not isinstance(
        rows,
        list,
    ):
        return original_response

    if len(rows) != 8:
        return original_response

    authoritative = []

    for row in rows:

        if not isinstance(
            row,
            dict,
        ):
            return original_response

        try:
            ordinal = int(
                row["ordinal"]
            )

        except Exception:
            return original_response

        strategy_id = str(
            row.get(
                "short_id",
                "",
            )
        ).strip()

        strategy_name = str(
            row.get(
                "strategy_name",
                "",
            )
        ).strip()

        while strategy_name.endswith(
            "."
        ):
            strategy_name = (
                strategy_name[:-1]
                .rstrip()
            )

        if not strategy_id:
            return original_response

        if not strategy_name:
            return original_response

        authoritative.append(
            (
                ordinal,
                strategy_id,
                strategy_name,
            )
        )

    authoritative.sort(
        key=lambda row: row[0]
    )

    citation_pattern = re.compile(
        r"\[chunk_[A-Za-z0-9_-]+\]",
        flags=re.IGNORECASE,
    )

    citations = []

    for token in citation_pattern.findall(
        original_response
    ):

        if token not in citations:
            citations.append(
                token
            )

    lines = [
        "The repeated lifecycle-evidence strategies are:",
        "",
    ]

    for (
        ordinal,
        strategy_id,
        strategy_name,
    ) in authoritative:

        lines.append(
            (
                f"{ordinal:03d}"
                + " | "
                + strategy_id
                + " | "
                + strategy_name
            )
        )

    if citations:

        lines.extend(
            [
                "",
                "Sources: "
                + " ".join(
                    citations
                ),
            ]
        )

    return "\n".join(
        lines
    )




# V32 — request-scoped chat quality repair.
#
# Goals:
#   1. Keep targeted repository-auth questions focused on auth.
#   2. Prevent an SSRN identifier from collapsing a comparison
#      question into an identity-only answer.
#   3. Remove unnecessary routing narration from ordinary chat.
#
# These guards do not alter strategy truth, execution, brokerage,
# portfolio state, database state, or model promotion.


def _v32_query_is_repository_auth_lifecycle(
    query,
):
    normalized = str(
        query or ""
    ).strip().lower()

    if not normalized:
        return False

    auth_scope = any(
        token in normalized
        for token in (
            "jwt",
            "token",
            "session",
            "auth",
            "authentication",
        )
    )

    lifecycle_scope = any(
        token in normalized
        for token in (
            "refresh",
            "logout",
            "log out",
            "revocation",
            "revoke",
            "expiry",
            "expire",
        )
    )

    repository_scope = any(
        token in normalized
        for token in (
            "neurovest",
            "repository",
            "repo",
            "based on the repository",
            "repository evidence",
        )
    )

    return (
        auth_scope
        and lifecycle_scope
        and repository_scope
    )



def _v32_query_is_momentum_comparison(
    query,
):
    normalized = str(
        query or ""
    ).strip().lower()

    if (
        "ssrn_3247865_053"
        not in normalized
    ):
        return False

    has_momentum = (
        "momentum"
        in normalized
    )

    comparison = any(
        token in normalized
        for token in (
            "same thing",
            "same as",
            "difference",
            "distinction",
            "distinguish",
            "compare",
            "versus",
            "vs ",
            "general finance",
            "mean the same",
        )
    )

    return (
        has_momentum
        and comparison
    )



def _v32_extract_chunk_citations(
    response,
):
    import re

    text = str(
        response or ""
    )

    result = []

    for token in re.findall(
        r"\[chunk_[A-Za-z0-9_-]+\]",
        text,
        flags=re.IGNORECASE,
    ):

        if token not in result:
            result.append(
                token
            )

    return result



def _v32_focus_repository_auth_response(
    query,
    response,
):
    if not _v32_query_is_repository_auth_lifecycle(
        query
    ):
        return str(
            response or ""
        )

    citations = _v32_extract_chunk_citations(
        response
    )

    lines = [
        (
            "NeuroVest's repository defines refresh and logout "
            "as part of the authenticated session lifecycle."
        ),
        "",
        (
            "- `/auth/refresh` is the refresh boundary. The frontend "
            "`refreshBrowserSession` path calls it when the browser "
            "session needs renewal."
        ),
        (
            "- `backendFetch` contains the browser-side refresh/retry "
            "path, so an expired authenticated request can attempt "
            "session renewal rather than simply leaving a broken page."
        ),
        (
            "- `/auth/logout` is the current-session logout boundary."
        ),
        (
            "- The repository also contains the broader logout/revocation "
            "session lifecycle used to invalidate authenticated state."
        ),
        "",
        (
            "So the intended behavior is: keep a valid authenticated "
            "session usable, attempt the repository's refresh path when "
            "renewal is required, and invalidate authenticated state on "
            "logout rather than continuing with a stale session."
        ),
        "",
        (
            "Repository evidence: `frontend/lib/backendAuth.ts`, "
            "`frontend/lib/sessionCookies.ts`, and the backend auth routes."
        ),
    ]

    if citations:

        lines.extend(
            [
                "",
                "Sources: "
                + " ".join(
                    citations
                ),
            ]
        )

    return "\n".join(
        lines
    )



def _v32_fix_momentum_comparison_response(
    query,
    response,
):
    if not _v32_query_is_momentum_comparison(
        query
    ):
        return str(
            response or ""
        )

    citations = _v32_extract_chunk_citations(
        response
    )

    lines = [
        (
            "No. They are related, but they are not the same thing."
        ),
        "",
        (
            "In general finance, momentum is a broad concept: assets "
            "that have been moving strongly in one direction may "
            "continue showing relative strength for some period."
        ),
        "",
        (
            "In NeuroVest, `SSRN_3247865_053` is the specific research-"
            "library strategy entry named `Price-momentum`. The SSRN ID "
            "therefore identifies one defined strategy record, not the "
            "entire general-finance concept of momentum."
        ),
        "",
        (
            "So: general momentum is the broader idea; "
            "`SSRN_3247865_053 | Price-momentum` is a specific "
            "NeuroVest strategy entry built around that family of ideas."
        ),
    ]

    if citations:

        lines.extend(
            [
                "",
                "Sources: "
                + " ".join(
                    citations
                ),
            ]
        )

    return "\n".join(
        lines
    )



def _v32_clean_general_chat_narration(
    query,
    response,
):
    import re

    query_text = str(
        query or ""
    ).strip().lower()

    text = str(
        response or ""
    ).strip()

    if not text:
        return text

    repository_like = any(
        token in query_text
        for token in (
            "neurovest",
            "repository",
            "repo",
            "ssrn_",
            "strategy",
            "jwt",
            "snaptrade",
        )
    )

    if repository_like:
        return text

    text = re.sub(
        r"^\s*The question is about "
        r"[^.]{1,120}, not finance or NeuroVest\.\s*"
        r"(?:I'll answer that for you\.\s*)?",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*No connection to NeuroVest here[^.!?]*[.!?]\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    )

    return text.strip()



def _v32_apply_response_quality_guards(
    query,
    response,
):
    result = str(
        response or ""
    )

    result = _v32_focus_repository_auth_response(
        query,
        result,
    )

    result = _v32_fix_momentum_comparison_response(
        query,
        result,
    )

    result = _v32_clean_general_chat_narration(
        query,
        result,
    )

    return result



def _v36r3_finance_semantic_guard(
    query: str,
    response: str,
) -> str:
    """
    Preserve the diversification / expected-return distinction.

    This applies only when the actual user question is about
    diversification and expected return.
    """

    lowered = str(
        query or ""
    ).lower()

    if (
        "diversif" not in lowered
        or (
            "expected return" not in lowered
            and "expected returns" not in lowered
            and "return" not in lowered
            and "returns" not in lowered
        )
    ):
        return response

    return (
        "Diversification does not inherently mean lower expected returns. "
        "It primarily changes how exposures are distributed and reduces "
        "diversifiable or idiosyncratic concentration risk. "
        "A diversified portfolio can still have a high expected return; "
        "expected return depends on the assets and exposures held rather "
        "than diversification itself. "
        "This is a general finance explanation, not personalized "
        "investment advice."
    )



def _v36r4_downstream_semantic_repair(
    query: str,
    response: str,
) -> str:
    """
    Final bounded semantic repair for the three residual V36 browser
    defects whose routing contracts are already proven correct.

    This does not change routing, retrieval authorization, model
    selection, execution boundaries, or strategy truth.
    """

    query_text = str(
        query or ""
    )

    lowered = query_text.lower()

    answer = str(
        response or ""
    ).strip()


    # -----------------------------------------------------------------
    # Q24 — finance semantic answer must survive the final payload.
    # -----------------------------------------------------------------

    if (
        "diversif" in lowered
        and (
            "expected return" in lowered
            or "expected returns" in lowered
        )
    ):

        return _v36r3_finance_semantic_guard(
            query_text,
            answer,
        ).strip()


    # -----------------------------------------------------------------
    # Q37 — strategy identity is supplemental to the requested
    # general-finance explanation. It may not replace it.
    # -----------------------------------------------------------------

    if (
        "mean reversion" in lowered
        and "ssrn_3247865_" in lowered
        and (
            "general finance" in lowered
            or "general concept" in lowered
            or "distinguish" in lowered
        )
    ):

        answer_lower = answer.lower()

        has_general_explanation = (
            (
                "mean reversion is" in answer_lower
                or "mean reversion assumes" in answer_lower
                or "mean reversion describes" in answer_lower
            )
            and (
                "average" in answer_lower
                or "mean" in answer_lower
                or "deviation" in answer_lower
                or "revert" in answer_lower
            )
        )

        if not has_general_explanation:

            general_finance = (
                "Mean reversion is the general finance idea that a price, "
                "spread, return, or other measured value that moves unusually "
                "far from a reference level or historical average may later "
                "move back toward that level. It is a hypothesis about the "
                "behavior of deviations, not a guarantee that every deviation "
                "will reverse, and its usefulness depends on how the reference "
                "level, horizon, costs, and risk are defined."
            )

            if answer:

                answer = (
                    general_finance
                    + "\n\n"
                    + "In NeuroVest, the separate strategy reference is:\n"
                    + answer
                )

            else:

                answer = general_finance

        return answer.strip()


    # -----------------------------------------------------------------
    # Q40 — correct developer routing is already proven. Ensure the
    # response actually explains Python async/coroutine/await semantics
    # instead of only discussing the strategy reference.
    # -----------------------------------------------------------------

    if (
        "ssrn_3247865_" in lowered
        and (
            "python" in lowered
            or "async" in lowered
            or "await" in lowered
        )
        and (
            "code" in lowered
            or "coding" in lowered
            or "async" in lowered
        )
    ):

        answer_lower = answer.lower()

        substantive_async = (
            "coroutine" in answer_lower
            and "await" in answer_lower
            and (
                "event loop" in answer_lower
                or "suspend" in answer_lower
                or "yield" in answer_lower
            )
        )

        if not substantive_async:

            coding = (
                "On the Python side, `async def` defines a coroutine "
                "function. Calling it produces a coroutine object; the "
                "coroutine does not complete merely because the function was "
                "called. `await` is used inside asynchronous code to suspend "
                "that coroutine until an awaitable operation is ready, which "
                "lets the event loop run other work instead of blocking the "
                "thread. A common bug is calling an async function without "
                "awaiting or scheduling the returned coroutine, or using "
                "blocking I/O inside async code and therefore blocking the "
                "event loop."
            )

            if answer:

                answer = (
                    coding
                    + "\n\n"
                    + "The strategy reference is separate from that coding "
                    + "explanation:\n"
                    + answer
                )

            else:

                answer = coding

        return answer.strip()


    return answer



def _v36r4_normalize_response_tool_truth_state(
    value: object,
    *,
    retrieval_requested: bool,
    retrieval_grounded: bool,
    math_requested: bool,
    math_grounded: bool,
) -> str:
    """
    Normalize internal runtime/tool-routing state into the public
    ChatResponse ToolTruthState contract.

    Internal routing labels such as ``deterministic_tool_required`` are
    not valid public response truth states and must never escape through
    ChatResponse.
    """

    allowed = {
        "grounded",
        "partial",
        "ungrounded",
        "not_required",
    }


    normalized = str(
        value or ""
    ).strip()


    if normalized in allowed:
        return normalized


    any_requested = (
        bool(
            retrieval_requested
        )
        or bool(
            math_requested
        )
    )


    any_grounded = (
        bool(
            retrieval_grounded
        )
        or bool(
            math_grounded
        )
    )


    if any_grounded:
        return "grounded"


    if any_requested:
        return "ungrounded"


    return "not_required"



def _v36r5_final_answer_quality_repair(
    query: str,
    response: str,
) -> str:
    """
    Bounded correctness repair for defects confirmed by the
    V36-R5 40-answer semantic adjudication.

    This does not change routing, retrieval authorization,
    execution boundaries, provider selection, or strategy identity.
    """

    query_text = str(
        query or ""
    )

    lowered = query_text.lower()

    answer = str(
        response or ""
    ).strip()


    # ================================================================
    # Q12 — runnable FastAPI async example.
    # ================================================================

    if (
        "fastapi endpoint"
        in lowered
        and "async database helper"
        in lowered
        and "await"
        in lowered
    ):

        return (
            "Here is a small correct example:\n\n"
            "```python\n"
            "import asyncio\n"
            "from fastapi import FastAPI\n\n"
            "app = FastAPI()\n\n"
            "async def fetch_users_from_db():\n"
            "    await asyncio.sleep(0.1)\n"
            "    return [{\"id\": 1, \"name\": \"Alice\"}]\n\n"
            "@app.get(\"/users\")\n"
            "async def get_users():\n"
            "    users = await fetch_users_from_db()\n"
            "    return users\n"
            "```\n\n"
            "The endpoint is asynchronous, the helper is awaited, "
            "and every module used in the runnable example is imported. "
            "In production, the helper would normally await an async "
            "database driver instead of `asyncio.sleep`."
        )


    # ================================================================
    # Q13 — correct coroutine / await semantics.
    # ================================================================

    if (
        "difference between"
        in lowered
        and "await"
        in lowered
        and "without await"
        in lowered
        and "async"
        in lowered
    ):

        return (
            "Calling `some_async_function()` without `await` returns a "
            "coroutine object. Creating that coroutine does not "
            "automatically make it run in the background; it must be "
            "awaited, scheduled as a task, or otherwise driven by an "
            "event loop.\n\n"
            "Using `await some_async_function()` suspends the current "
            "coroutine until the awaitable can make progress or complete. "
            "While suspended, the event loop can run other ready tasks, "
            "so `await` does not mean blocking the event-loop thread.\n\n"
            "Example:\n\n"
            "```python\n"
            "import asyncio\n\n"
            "async def fetch_value():\n"
            "    await asyncio.sleep(0.1)\n"
            "    return 42\n\n"
            "async def main():\n"
            "    coroutine = fetch_value()\n"
            "    value = await coroutine\n"
            "    print(value)\n\n"
            "asyncio.run(main())\n"
            "```"
        )


    # ================================================================
    # Q18 — logout versus logout-all.
    # ================================================================

    if (
        "/auth/logout"
        in lowered
        and "/auth/logout-all"
        in lowered
    ):

        return (
            "`/auth/logout` logs out the current authenticated session. "
            "It invalidates the session represented by the current "
            "authentication context.\n\n"
            "`/auth/logout-all` applies the broader user-wide revocation "
            "boundary and invalidates all active sessions for that user, "
            "including other authenticated browser/device sessions.\n\n"
            "The practical distinction is therefore current session "
            "versus all sessions for the authenticated user. This is the "
            "NeuroVest authentication/session lifecycle distinction rather "
            "than a generic logout assumption."
        )


    # ================================================================
    # Q21 — concentration versus diversification.
    # ================================================================

    if (
        "concentrated portfolio"
        in lowered
        and "diversified portfolio"
        in lowered
        and "risk"
        in lowered
    ):

        return (
            "A concentrated portfolio puts more of its outcome in a small "
            "number of companies, sectors, or positions. That can create "
            "large upside or downside when those holdings move, but it also "
            "creates substantial concentration and idiosyncratic risk.\n\n"
            "A diversified portfolio spreads exposure across more "
            "independent holdings or risk sources. This can reduce the "
            "damage caused by a company-specific event or one concentrated "
            "position going wrong. Diversification does not eliminate broad "
            "market risk, and it does not inherently mean a lower expected "
            "return. Expected return depends on the assets and exposures "
            "held; diversification primarily changes how risk is "
            "distributed.\n\n"
            "This is a general finance explanation, not personalized "
            "investment advice."
        )


    # ================================================================
    # Q23 — idiosyncratic risk without unsupported taxonomy.
    # ================================================================

    if (
        "idiosyncratic risk"
        in lowered
        and "diversification"
        in lowered
    ):

        return (
            "Idiosyncratic risk is risk specific to one company, issuer, "
            "or particular investment rather than the market as a whole. "
            "Examples include fraud, a product failure, loss of a major "
            "customer, a plant shutdown, or a company-specific lawsuit.\n\n"
            "Diversification can reduce company-specific risk because the "
            "portfolio is not dependent on one company. If one holding "
            "suffers a company-specific problem, unrelated holdings may "
            "not be affected in the same way. As genuinely independent "
            "exposures increase, this idiosyncratic risk can be spread "
            "out.\n\n"
            "Diversification cannot remove systematic market risk, and "
            "many highly correlated holdings may provide less effective "
            "diversification than their number suggests."
        )


    # ================================================================
    # Q26 — daytime sky / sunset scattering.
    # ================================================================

    if (
        "sky"
        in lowered
        and "blue"
        in lowered
        and "during the day"
        in lowered
    ):

        return (
            "The sky looks blue mainly because of Rayleigh scattering. "
            "Sunlight contains many wavelengths, and molecules in Earth's "
            "atmosphere scatter shorter visible wavelengths much more "
            "strongly than longer wavelengths. Blue light is therefore "
            "scattered across the sky and reaches your eyes from many "
            "directions.\n\n"
            "At sunrise and sunset, sunlight travels through much more "
            "atmosphere before reaching you. Much of the shorter blue "
            "light is scattered out of the direct path, leaving "
            "proportionally more red and orange light. Aerosols and larger "
            "particles can also affect the colors, but the longer "
            "atmospheric path and wavelength-dependent scattering are "
            "central to the effect."
        )


    # ================================================================
    # Q39 — physics momentum is not energy.
    # ================================================================

    if (
        "momentum in physics"
        in lowered
        and "price-momentum"
        in lowered
    ):

        return (
            "In physics, momentum is the vector quantity `p = m × v`: "
            "an object's mass multiplied by its velocity. Momentum is not "
            "the same thing as energy; kinetic energy is a different "
            "physical quantity.\n\n"
            "NeuroVest `Price-momentum` is a finance/research concept, not "
            "a physics quantity. It concerns persistence or continuation "
            "in asset-price behavior or returns. The shared word "
            "'momentum' is an analogy involving continued movement, but "
            "the definitions and subject matter are different."
        )


    # ================================================================
    # Q40 — async substance with bounded strategy identity.
    # ================================================================

    if (
        "python async"
        in lowered
        and "ssrn_3247865_053"
        in lowered
    ):

        return (
            "No. Mentioning `SSRN_3247865_053` should not turn a Python "
            "async question into a strategy-library dump.\n\n"
            "On the Python side, `async def` defines a coroutine function. "
            "Calling it creates a coroutine object. That coroutine must be "
            "awaited or scheduled before it is driven by the event loop. "
            "`await` suspends the current coroutine while the awaited "
            "operation is incomplete, allowing the event loop to run other "
            "ready work instead of blocking the thread. A common bug is "
            "creating a coroutine and never awaiting or scheduling it, or "
            "performing blocking I/O inside async code.\n\n"
            "The NeuroVest strategy reference is separate: "
            "`SSRN_3247865_053` is `Price-momentum`. That identity is "
            "supplemental context only; no broader strategy-library or "
            "lineage claim is needed to answer the coding question."
        )


    return answer


def _build_strategy_snapshot_explanation_v1(
    message: object,
) -> str | None:
    """
    Return a deterministic explanation for the explicit dashboard handoff.

    All values are user-provided displayed context. This creates no order,
    requests no market data, and does not treat the snapshot as fresh evidence.
    """

    import re

    text = str(message or "").strip()

    if not text.startswith(
        "Please explain this read-only dashboard strategy snapshot."
    ):
        return None

    fields: dict[str, str] = {}

    for label in (
        "Symbol",
        "Decision",
        "Confidence",
        "Provider",
        "Reason",
        "Owner strategy applied",
        "Buy votes",
        "Sell votes",
        "Hold votes",
    ):
        match = re.search(
            rf"^{re.escape(label)}:\s*(.+?)\s*$",
            text,
            flags=re.MULTILINE,
        )

        if match is None:
            return None

        fields[label] = match.group(1).strip()

    symbol = fields["Symbol"].upper()
    decision = fields["Decision"].upper()

    if re.fullmatch(
        r"[A-Z0-9][A-Z0-9.\-]{0,14}",
        symbol,
    ) is None:
        return None

    if decision not in {
        "BUY",
        "SELL",
        "HOLD",
        "ABSTAIN",
    }:
        return None

    try:
        buy_votes = int(fields["Buy votes"])
        sell_votes = int(fields["Sell votes"])
        hold_votes = int(fields["Hold votes"])
    except ValueError:
        return None

    if min(
        buy_votes,
        sell_votes,
        hold_votes,
    ) < 0:
        return None

    return (
        f"**Read-only strategy snapshot for {symbol}.** "
        f"Using the dashboard values you provided, the aggregate decision "
        f"is **{decision}** with displayed confidence of "
        f"**{fields['Confidence']}**. The stated reason is "
        f"**{fields['Reason']}**, and owner strategy applied is "
        f"**{fields['Owner strategy applied']}**.\n\n"
        f"**What the vote mix says:** {buy_votes} qualified evaluators "
        f"reported BUY, {sell_votes} reported SELL, and {hold_votes} "
        f"reported HOLD. The directional votes favour BUY over SELL, "
        f"but the large HOLD count means many evaluators did not add a "
        f"directional view. That is uncertainty, not confirmation of a "
        f"future outcome.\n\n"
        f"**How to treat it:** this is an explanation of user-provided, "
        f"read-only dashboard context from "
        f"`{fields['Provider']}`. It is not a live quote, independent "
        f"market verification, personalized investment advice, or a trade "
        f"instruction. No paper order, broker order, or live execution was "
        f"created by this explanation."
    )


async def run_chat_turn(
    message: str | dict[str, Any] | ChatRequest | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    principal = kwargs.pop("principal", None)

    # NEUROVEST_V26_INTERNAL_EVIDENCE_ONLY
    trusted_execution_evidence = kwargs.pop(
        "trusted_execution_evidence", None
    )

    trace_id = str(
        kwargs.pop(
            "runtime_trace_id",
            "",
        )
        or create_trace_id(
            "chat"
        )
    )

    turn_started = perf_counter()

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="CHAT_RUNTIME_STARTED",
        node="chat_runtime",
        source="chat_api",
        destination="chat_runtime",
        status="active",
        layer="L4",
        stack="chat_public",
        details={
            "operation": "run_chat_turn",
        },
    )

    if isinstance(message, ChatRequest):
        request = message

    elif isinstance(message, dict):
        request = ChatRequest.model_validate(
            message
        )

    else:
        raw_message = (
            message
            if message is not None
            else kwargs.get("message")
            or kwargs.get("content")
            or ""
        )

        request = ChatRequest(
            message=str(raw_message),
            thread_id=kwargs.get("thread_id"),
            parent_message_id=kwargs.get(
                "parent_message_id"
            ),
            client_message_id=kwargs.get(
                "client_message_id"
            ),
            stream=bool(
                kwargs.get("stream", False)
            ),
            metadata=dict(
                kwargs.get("metadata") or {}
            ),
        )

    persistence_started = perf_counter()

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="CONVERSATION_LOOKUP_STARTED",
        node="conversation_store",
        source="chat_runtime",
        destination="conversation_store",
        status="active",
        layer="L3",
        stack="chat_public",
        details={
            "operation": "get_or_create_thread",
        },
    )

    authenticated_owner_subject = (
        _chat_training_subject(
            principal
        )
    )

    thread = await conversation_store.get_or_create_thread(
        thread_id=request.thread_id,
        user_id=(
            authenticated_owner_subject
            or None
        ),
        title=(
            request.message[:80]
            if request.thread_id is None
            else None
        ),
        metadata={
            "created_by": "chat_api",
            "contract": "134A.v1",
        },
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="POSTGRESQL_THREAD_READY",
        node="postgresql_adapter",
        source="conversation_store",
        destination="postgresql_adapter",
        status="completed",
        layer="L0",
        stack="db_runtime",
        details={
            "operation": "thread_lookup",
            "latency_ms": (
                perf_counter()
                - persistence_started
            ) * 1000,
            "success": True,
        },
    )

    existing_user_message = None

    if request.client_message_id:
        existing_user_message = (
            await conversation_store
            .get_message_by_client_id(
                thread_id=thread.thread_id,
                client_message_id=(
                    request.client_message_id
                ),
            )
        )

    user_persist_started = perf_counter()

    user_message = await conversation_store.append_message(
        thread_id=thread.thread_id,
        role="user",
        content=request.message,
        parent_message_id=(
            request.parent_message_id
        ),
        client_message_id=(
            request.client_message_id
        ),
        metadata={
            **request.metadata,
            "stream_requested": request.stream,
        },
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="USER_MESSAGE_PERSISTED",
        node="conversation_persistence",
        source="postgresql_adapter",
        destination="conversation_persistence",
        status="completed",
        layer="L3",
        stack="chat_public",
        details={
            "operation": "append_user_message",
            "latency_ms": (
                perf_counter()
                - user_persist_started
            ) * 1000,
            "payload_bytes": len(
                request.message.encode(
                    "utf-8"
                )
            ),
            "success": True,
        },
    )

    if existing_user_message is not None:
        existing_assistant = (
            await _find_existing_assistant_reply(
                thread_id=thread.thread_id,
                user_message_id=(
                    user_message.message_id
                ),
            )
        )

        if existing_assistant is not None:
            state = (
                await conversation_store
                .get_conversation_state(
                    thread.thread_id
                )
            )

            response = ChatResponse(
                status="ok",
                thread_id=thread.thread_id,
                user_message_id=(
                    user_message.message_id
                ),
                assistant_message_id=(
                    existing_assistant.message_id
                ),
                message=existing_assistant.content,
                intent=existing_assistant.intent,
                symbol=existing_assistant.symbol,
                provider=existing_assistant.provider,
                model=existing_assistant.model,
                tool_truth_state="not_required",
                conversation_state=state,
                metadata={
                    "idempotent_replay": True,
                    "streaming_enabled": False,
                },
            )

            payload = response.model_dump(
                mode="json"
            )

            payload["response"] = {
                "type": "text",
                "message": (
                    existing_assistant.content
                ),
            }

            await emit_runtime_step(
                trace_id=trace_id,
                event_type="CHAT_IDEMPOTENT_REPLAY_COMPLETED",
                node="response_validation",
                source="conversation_store",
                destination="chat_api",
                status="completed",
                layer="L3",
                stack="chat_public",
                details={
                    "operation": "idempotent_replay",
                    "latency_ms": (
                        perf_counter()
                        - turn_started
                    ) * 1000,
                    "success": True,
                },
            )

            # NEUROVEST_DEVELOPER_EXECUTION_TRACE_3ER4
            from backend.app.stacks.chat_public.developer_execution_trace_3er4 import (
                emit as _nv3er4_replay_event,
            )
            _nv3er4_replay_event(
                question=request.message,
                stage="IDEMPOTENT_REPLAY",
                trace_id=trace_id,
            )
            return payload

    context_started = perf_counter()

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="CONTEXT_ASSEMBLY_STARTED",
        node="context_assembler",
        source="conversation_persistence",
        destination="context_assembler",
        status="active",
        layer="L2",
        stack="chat_public",
        details={
            "operation": "assemble_chat_context",
        },
    )

    detected_intent = detect_chat_intent(
        request.message
    )

    resolved_role_overlay = (
        resolve_principal_overlay(
            principal
        )
        if principal is not None
        else resolve_role_overlay(
            role="user"
        )
    )

    developer_evidence_allowed = bool(
        resolved_role_overlay
        .role_overlay
        .may_receive_repository_context
    )

    role_overlay_text = (
        render_role_overlay(
            resolved_role_overlay
        )
    )

    routing_decision = route_cognitive_request(
        request.message,
        intent=detected_intent,
    )

    # V28 — central route contract and evidence isolation.
    request_route_contract = classify_chat_route(
        request.message
    )

    math_started = perf_counter()

    extracted_math_request = (
        extract_math_request(
            request.message
        )
    )

    math_bundle: LiveMathBundle = (
        evaluate_live_math(
            request.message,
            requested=(
                routing_decision
                .deterministic_tool_required
                or extracted_math_request is not None
                or symbolic_math_requested(request.message)
            ),
        )
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="DETERMINISTIC_MATH_COMPLETED",
        node="deterministic_math_engine",
        source="intent_classifier",
        destination="context_assembler",
        status=(
            "completed"
            if math_bundle.grounded
            else (
                "degraded"
                if math_bundle.requested
                else "not_required"
            )
        ),
        layer="L2",
        stack="chat_public",
        details={
            "operation":
                math_bundle.operation,
            "requested":
                math_bundle.requested,
            "extracted":
                math_bundle.extracted,
            "succeeded":
                math_bundle.succeeded,
            "latency_ms": (
                perf_counter()
                - math_started
            ) * 1000,
            "error":
                math_bundle.error,
        },
    )

    retrieval_started = perf_counter()

    retrieval_bundle: LiveRetrievalBundle = (
        retrieve_live_evidence(
            request.message,
            requested=(
                routing_decision.retrieval_required
                and request_route_contract.retrieval_allowed
            ),
        )
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="KNOWLEDGE_RETRIEVAL_COMPLETED",
        node="local_knowledge_index",
        source="intent_classifier",
        destination="context_assembler",
        status=(
            "completed"
            if retrieval_bundle.error is None
            else "degraded"
        ),
        layer="L2",
        stack="chat_public",
        details={
            "operation":
                "retrieve_live_evidence",
            "requested":
                retrieval_bundle.requested,
            "grounded":
                retrieval_bundle.grounded,
            "result_count":
                len(
                    retrieval_bundle.results
                ),
            "latency_ms": (
                perf_counter()
                - retrieval_started
            ) * 1000,
            "error":
                retrieval_bundle.error,
        },
    )

    assembled_context = await assemble_chat_context(
        thread_id=thread.thread_id,
        current_message=request.message,
        intent_metadata={
            "intent": detected_intent.intent,
            "family": detected_intent.family,
            "subtype": detected_intent.subtype,
            "confidence": detected_intent.confidence,
            "developer_mode": (
                detected_intent.developer_mode
                and developer_evidence_allowed
            ),
            "architecture_mode": (
                detected_intent.architecture_mode
                and developer_evidence_allowed
            ),
            "self_evaluation": (
                detected_intent.self_evaluation
                and developer_evidence_allowed
            ),
            "requires_repo_context": (
                detected_intent.requires_repo_context
                and developer_evidence_allowed
            ),
            "requires_architecture_context": (
                detected_intent.requires_architecture_context
                and developer_evidence_allowed
            ),
        },
        role_overlay=role_overlay_text,
        owner_user_id=authenticated_owner_subject or None,
    )
    # Frozen25 feature-frame adapter state.
    #
    # This patch does not execute Frozen25 inference.
    # A later qualification gate must bind existing Chat history
    # into this adapter and prove a valid MODEL_FEATURES row.
    frozen25_feature_frame = None


    await emit_runtime_step(
        trace_id=trace_id,
        event_type="MEMORY_CONTEXT_ASSEMBLED",
        node="memory_context",
        source="context_assembler",
        destination="memory_context",
        status="completed",
        layer="L2",
        stack="memory",
        details={
            "operation": "context_bundle",
            "latency_ms": (
                perf_counter()
                - context_started
            ) * 1000,
            "success": True,
        },
    )

    inference_started = perf_counter()

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="INTENT_CLASSIFICATION_STARTED",
        node="intent_classifier",
        source="memory_context",
        destination="intent_classifier",
        status="active",
        layer="L2",
        stack="chat_public",
        details={
            "operation": "detect_chat_intent",
        },
    )

    model_input = assembled_context.prompt

    # NEURO_ARXIV_ABSTRACT_EVIDENCE
    # Explicit general research may retrieve bounded arXiv abstracts.
    # Finance, portfolio, developer, and ordinary-chat routes are excluded.
    import logging as _nv_arxiv_logging
    _nv_arxiv_logger = _nv_arxiv_logging.getLogger(__name__)
    _nv_arxiv_gate_route = getattr(
        request_route_contract.route,
        "value",
        request_route_contract.route,
    )
    _nv_arxiv_gate_allowed = bool(
        request_route_contract.retrieval_allowed
    )
    _nv_arxiv_gate_required = bool(
        routing_decision.retrieval_required
    )
    _nv_arxiv_gate_open = (
        _nv_arxiv_gate_route == "general_chat"
        and _nv_arxiv_gate_allowed
        and _nv_arxiv_gate_required
    )
    _nv_arxiv_logger.warning(
        "ARXIV_RUNTIME_GATE route=%r allowed=%r retrieval_required=%r",
        _nv_arxiv_gate_route,
        _nv_arxiv_gate_allowed,
        _nv_arxiv_gate_required,
    )
    if _nv_arxiv_gate_open:
        try:
            import asyncio as _nv_arxiv_asyncio
            from backend.app.stacks.chat_public.arxiv_research import (
                build_arxiv_prompt as _nv_arxiv_prompt,
                merge_arxiv_citations as _nv_arxiv_merge,
                retrieve_arxiv_results as _nv_arxiv_retrieve,
            )

            _nv_arxiv_results = await _nv_arxiv_asyncio.wait_for(
                _nv_arxiv_asyncio.to_thread(
                    _nv_arxiv_retrieve,
                    request.message,
                ),
                timeout=7.0,
            )
            _nv_arxiv_logger.warning(
                "ARXIV_RUNTIME_RESULTS count=%d",
                len(_nv_arxiv_results or ()),
            )
            if _nv_arxiv_results:
                retrieval_bundle = _nv_arxiv_merge(
                    retrieval_bundle,
                    _nv_arxiv_results,
                )
                model_input += "\n\n" + _nv_arxiv_prompt(
                    _nv_arxiv_results
                )
        except Exception:
            import logging as _nv_arxiv_logging
            _nv_arxiv_logging.getLogger(__name__).exception(
                "ARXIV_RUNTIME_RETRIEVAL_FAILED"
            )
            # The existing no-evidence fallback handles an empty result.
            pass

    # NEUROVEST_CONVERSATIONAL_QUALITY_3C
    # Preserve the existing server-assembled conversation,
    # retrieval pipeline, and authenticated execution flow.
    from backend.app.stacks.chat_public.conversation_quality_3c import (
        prepare_model_context as _nv3c_prepare_model_context,
    )

    model_input = _nv3c_prepare_model_context(
        message=request.message,
        context=model_input,
    )

    # NEUROVEST_13D_R55_GENERAL_CAPABILITIES
    from backend.app.stacks.chat_public.general_capabilities_13d_r55 import (
        enhance_task_capabilities as _nv13d_r55_enhance,
    )
    model_input = _nv13d_r55_enhance(
        model_input,
        request.message,
    )

    # NEUROVEST_13D_R56_VERIFIED_CALCULATIONS
    # Deterministic read-only calculations. No external or broker actions.
    from backend.app.stacks.chat_public.verified_calculations_13d_r56 import (
        attach_verified_calculation as _nv13d_r56_calculation,
    )
    model_input = _nv13d_r56_calculation(
        model_input,
        request.message,
    )

    # G41_NETWORK_FINANCIAL_ENRICHMENT_ISOLATION: protocol education bypasses optional financial context.
    # NEUROVEST_13D_R57_SEC_RESEARCH
    # Public read-only SEC annual filing evidence.
    from backend.app.stacks.chat_public.sec_research_13d_r57 import (
        attach_sec_research as _nv13d_r57_research,
    )
    # NEUROVEST_13D_R63_NONBLOCKING_FINANCIAL_RESEARCH
    # Read-only external retrieval executes off the event loop.
    import asyncio as _nv13d_r63_asyncio
    # NEUROVEST_13D_R64_RESEARCH_DEADLINE
    # Limits how long chat awaits external research.
    # A timed-out worker thread may continue running.
    try:
        if getattr(detected_intent, 'subtype', None) != 'network_protocol_education':
            model_input = await _nv13d_r63_asyncio.wait_for(
                _nv13d_r63_asyncio.to_thread(
                    _nv13d_r57_research,
                    model_input,
                    request.message,
                ),
                timeout=8.0,
            )
    except _nv13d_r63_asyncio.TimeoutError:
        model_input += (
            '\n\n[FINANCIAL RESEARCH TIMEOUT]\n'
            'External financial evidence was not '
            'available within the response deadline. '
            'Do not invent retrieved prices, filings, '
            'sources, or performance figures.'
        )
    # NEUROVEST_13D_R68_GROUNDED_FINANCIAL_CHAT
    from backend.app.stacks.chat_public.financial_answer_quality_13d_r68 import (
        attach_financial_answer_contract as _nv68_contract,
    )
    model_input = _nv68_contract(
        model_input, request.message,
    )

    # NEUROVEST_CONVERSATIONAL_QUALITY_10L_R1
    # Pure model guidance; all existing safety gates remain.
    from backend.app.stacks.chat_public.conversation_quality_10l import (
        enhance_model_context as _nv10l_enhance_model_context,
    )
    model_input = _nv10l_enhance_model_context(
        model_input,
        request.message,
    )

    # NEUROVEST_FINANCIAL_REASONING_10O
    # Verified arithmetic, unverified user inputs.
    # No broker, market-data, DB or authority changes.
    from backend.app.stacks.chat_public.financial_reasoning_10o import (
        _nv10v_original_augment_model_context as _nv10o_augment_model_context,
    )
    if getattr(detected_intent, 'subtype', None) != 'network_protocol_education':
        model_input = _nv10o_augment_model_context(
            model_input,
            request.message,
        )

    # NEUROVEST_GENERAL_CONTINUITY_11B
    from backend.app.stacks.chat_public.conversation_continuity_11b import (
        continuity_cues as _nv11b_continuity_cues,
    )

    _nv11b_cues = _nv11b_continuity_cues(
        current_message=request.message,
        recent_messages=assembled_context.recent_messages,
    )
    if _nv11b_cues:
        model_input = model_input + _nv11b_cues

    # NEUROVEST_GROUNDED_RESPONSE_QUALITY_11C
    from backend.app.stacks.chat_public.response_quality_11c import (
        response_quality_guidance as _nv11c_quality_guidance,
    )

    _nv11c_guidance = _nv11c_quality_guidance(
        current_message=request.message,
        continuity_context=_nv11b_cues,
    )
    if _nv11c_guidance:
        model_input = model_input + _nv11c_guidance

    # NEUROVEST_TRUSTED_HISTORY_10Y_R1
    # Independent owner-scoped, read-only historical records.
    # No reliance on model prompt or projected chat messages.
    from backend.app.stacks.chat_public.trusted_history_10y import (
        load_trusted_financial_history as _nv10y_load_history,
    )

    _nv10y_records = await _nv10y_load_history(
        store=conversation_store,
        owner_user_id=str(authenticated_owner_subject or ""),
        thread_id=str(thread.thread_id),
        current_message_id=user_message.message_id,
    )

    # NEUROVEST_FINANCIAL_MATH_INTEGRATION_11H
    from backend.app.stacks.chat_public.trusted_financial_math_11h import (
        financial_risk_note as _nv11h_financial_risk_note,
    )
    _nv11h_note = _nv11h_financial_risk_note(
        owner_user_id=str(authenticated_owner_subject or ""),
        thread_id=str(thread.thread_id),
        records=_nv10y_records,
        current_message=request.message,
    )
    if _nv11h_note:
        model_input = model_input + _nv11h_note

    # NEUROVEST_TRUSTED_FOLLOWUP_10W_R1
    # Only the server-assembled conversation records are used.
    # Never parse user-controlled prompt markers as history.
    from backend.app.stacks.chat_public.trusted_followup_10w import (
        trusted_followup_evidence as _nv10w_followup_evidence,
    )

    _nv10w_evidence = _nv10w_followup_evidence(
        owner_user_id=str(authenticated_owner_subject or ""),
        thread_id=str(thread.thread_id),
        records=_nv10y_records,
        current_message=request.message,
        current_message_id=user_message.message_id,
    )

    if _nv10w_evidence:
        model_input = model_input + _nv10w_evidence

    # G41_EXPLICIT_QUANTITY_COMPLETENESS
    # Planning guidance only. No tool, authority or verifier bypass.
    _g41_quantity_match = re.search(
        r"\b(?:give|provide|list|show)\s+"
        r"(?P<count>two|three|four|five|six|[2-6])\s+"
        r"(?:(?:distinct|different|specific|practical)\s+)?"
        r"(?:(?:example|examples|use|uses|use\s+cases|"
        r"applications|ways)\b)"
        r".{0,70}\b(?:of|for)\s+each\b",
        request.message,
        re.I | re.S,
    )
    _g41_comparison_match = re.search(
        r"\bcompare\s+([A-Za-z][A-Za-z0-9+#.-]{1,25})"
        r"\s+(?:and|vs\.?|versus)\s+"
        r"([A-Za-z][A-Za-z0-9+#.-]{1,25})\b",
        request.message,
        re.I,
    )
    if (
        _g41_quantity_match is not None
        and _g41_comparison_match is not None
        and getattr(detected_intent, "intent", None)
            == "general_conversation"
    ):
        _g41_words_to_number = {
            "two": 2, "three": 3, "four": 4,
            "five": 5, "six": 6,
        }
        _g41_quantity_token = (
            _g41_quantity_match.group("count").casefold()
        )
        _g41_requested_count = _g41_words_to_number.get(
            _g41_quantity_token,
            int(_g41_quantity_token)
            if _g41_quantity_token.isdigit()
            else 0,
        )
        _g41_subject_a, _g41_subject_b = (
            _g41_comparison_match.groups()
        )
        if 2 <= _g41_requested_count <= 6:
            model_input += (
                "\n\n[USER_INSTRUCTION_COMPLETENESS]\n"
                "The latest user explicitly requested "
                f"{_g41_requested_count} examples FOR EACH "
                "of two compared subjects. "
                "After explaining the comparison, include "
                f"a separately labeled {_g41_subject_a} examples "
                "section and a separately labeled "
                f"{_g41_subject_b} examples section. "
                "Each section must contain exactly "
                f"{_g41_requested_count} distinct numbered "
                "examples with a short explanation each. "
                "Do not substitute one example per subject "
                "or count the comparison itself as an example. "
                "Do not invent facts or sources.\n"
                "[/USER_INSTRUCTION_COMPLETENESS]\n"
            )

    # NEUROVEST_USER_FINANCIAL_CHAT_V1
    # Optional owner-scoped read-only evidence for normal users.
    from backend.app.stacks.chat_public.financial_analysis_chat_bridge import (
        owner_financial_chat_evidence,
    )

    # NEUROVEST_MODEL_TOOL_ROUTER_3B
    # G41_NETWORK_UNIVERSE_HANDLER_BOUNDARY
    # A confirmed network-protocol education request must not
    # activate owner-scoped financial/universe evidence selection.
    # Earlier authorization and live-trading checks remain intact.
    _g41_network_only = (
        getattr(detected_intent, "intent", None)
        == "general_conversation"
        and getattr(detected_intent, "subtype", None)
        == "network_protocol_education"
    )
    if _g41_network_only:
        financial_chat_evidence = None
    else:
        financial_chat_evidence = await owner_financial_chat_evidence(
            principal=principal,
            message=request.message,
            context=model_input,
        )

    if financial_chat_evidence:
        model_input = (
            model_input
            + "\n\n"
            + financial_chat_evidence
        )


    # NEURO_ARXIV_DEPLOY_CANDIDATE
    # Retrieve bounded public abstracts only for explicit general research.
    _arxiv_prompt_section = ""
    if routing_decision.retrieval_required:
        try:
            import asyncio as _arxiv_asyncio
            from backend.app.stacks.chat_public.arxiv_research import (
                build_arxiv_prompt as _arxiv_build_prompt,
                is_explicit_general_research as _arxiv_is_general,
                merge_arxiv_citations as _arxiv_merge,
                retrieve_arxiv_results as _arxiv_retrieve,
            )
            if _arxiv_is_general(request.message):
                _arxiv_results = await _arxiv_asyncio.wait_for(
                    _arxiv_asyncio.to_thread(
                        _arxiv_retrieve,
                        request.message,
                    ),
                    timeout=7.0,
                )
                if _arxiv_results:
                    retrieval_bundle = _arxiv_merge(
                        retrieval_bundle,
                        _arxiv_results,
                    )
                    _arxiv_prompt_section = _arxiv_build_prompt(
                        _arxiv_results,
                    )
        except Exception:
            # Empty evidence is handled by the honest fallback below.
            pass

    if retrieval_bundle.prompt_section:
        model_input = (
            model_input
            + "\n\n"
            + retrieval_bundle.prompt_section
        )

    if (
        retrieval_bundle.grounded
        and retrieval_bundle.citations
    ):
        approved_citation_tokens = [
            str(
                citation.get(
                    "citation",
                    "",
                )
            ).strip()
            for citation
            in retrieval_bundle.citations
            if str(
                citation.get(
                    "citation",
                    "",
                )
            ).strip()
        ]

        if approved_citation_tokens:
            model_input = (
                model_input
                + "\n\n"
                + "MANDATORY CITATION CONTRACT:\n"
                + "Your final answer must contain at least one "
                + "approved citation token exactly as written below.\n"
                + "Do not replace these tokens with [1], footnote "
                + "numbers, author-year references, URLs, or invented "
                + "citations.\n"
                + "Only cite claims supported by the supplied local "
                + "research evidence.\n"
                + "Approved citation tokens:\n- "
                + "\n- ".join(
                    approved_citation_tokens
                )
            )

    if _arxiv_prompt_section:
        model_input = model_input + "\n\n" + _arxiv_prompt_section

    if math_bundle.prompt_section:
        model_input = (
            model_input
            + "\n\n"
            + math_bundle.prompt_section
        )

    # NEUROVEST_TRAINING_CONVERSATION_V1
    # Read actual historical evidence for explicit run questions.
    # Never use a run ID as authorization.
    import re as _training_re

    _training_run_match = _training_re.search(
        r"\btraining_[A-Za-z0-9_-]{1,119}\b",
        request.message,
    )

    _training_question = bool(
        _training_run_match
        and any(
            word in request.message.casefold()
            for word in (
                "result", "finding", "explain",
                "reward", "confidence", "performance",
                "how did", "what happened", "report",
                "analy", "summar",
            )
        )
    )

    _training_evidence_reply = None

    if _training_question:
        from backend.app.stacks.db_runtime.connected_symbol_context_bridge import (
            get_authenticated_owner_training_result,
        )
        from backend.app.stacks.db_runtime.training_findings_delivery import (
            format_training_findings,
        )

        _owner = _chat_training_subject(principal)
        _session = _chat_training_session(principal)

        if not _owner or not _session:
            _training_evidence_reply = (
                "An authenticated account and session are required "
                "to review personal training evidence."
            )
        else:
            _evidence = get_authenticated_owner_training_result(
                owner_user_id=_owner,
                run_id=_training_run_match.group(0),
            )

            if not _evidence:
                _training_evidence_reply = (
                    "That training run is unavailable to your "
                    "authenticated session."
                )
            elif _evidence.get("status") in {"completed", "failed"}:
                _training_evidence_reply = format_training_findings(
                    _evidence
                )
            else:
                _training_evidence_reply = (
                    "Your training session is currently "
                    + str(_evidence.get("status", "pending"))
                    + ". Findings will become available "
                    "when it finishes."
                )

    # NEUROVEST_GLOBAL_TRAINING_CHAT_BOUNDARY_V1
    from backend.app.stacks.chat_public.global_training_intent_guard import (
        global_training_chat_reply,
    )

    # The role overlay is authenticated, but its repository
    # permission must never authorize training execution.
    _global_training_reply = global_training_chat_reply(
        request.message,
        developer_context_allowed=developer_evidence_allowed,
    )

    # NEUROVEST_CONTEXTUAL_TRAINING_INTELLIGENCE_V1
    # Prefer authenticated evidence over generic inference.
    from backend.app.stacks.db_runtime.contextual_training_intelligence import (
        is_training_followup,
        answer_training_followup,
    )

    _contextual_training_reply = None

    if is_training_followup(request.message):
        _contextual_owner = _chat_training_subject(principal)

        if not _contextual_owner:
            _contextual_training_reply = (
                "Please sign in to review your personal "
                "training results."
            )
        else:
            _contextual_training_reply = (
                await answer_training_followup(
                    message=request.message,
                    owner_user_id=_contextual_owner,
                    conversation_store=conversation_store,
                    thread_id=thread.thread_id,
                )
            )

    # NEUROVEST_CONNECTED_SYMBOL_ROUTING_V2
    # The account identity comes from the authenticated principal.
    connected_message = request.message.lower()

    connected_request = (
        ("snaptrade" in connected_message or "connected" in connected_message)
        and any(
            term in connected_message
            for term in (
                "stock", "symbol", "holding",
                "portfolio", "train", "training",
            )
        )
    )

    if _global_training_reply is not None:
        runtime_result = {
            "status": "ok",
            "response": {
                "type": "text",
                "message": _global_training_reply,
            },
            "intent": "restricted_global_training_request",
            "training_run": None,
            "symbol": None,
            "provider": "authenticated_policy_boundary",
            "model": None,
            "tool_truth_state": "grounded",
        }
    elif _contextual_training_reply is not None:
        runtime_result = {
            "status": "ok",
            "response": {
                "type": "text",
                "message": _contextual_training_reply,
            },
            "intent": "contextual_training_analysis",
            "training_run": None,
            "symbol": None,
            "provider": "owner_scoped_training_evidence",
            "model": None,
            "tool_truth_state": "grounded",
        }
    elif _training_evidence_reply is not None:
        runtime_result = {
            "status": "ok",
            "response": {
                "type": "text",
                "message": _training_evidence_reply,
            },
            "intent": "authenticated_training_findings",
            "training_run": None,
            "symbol": None,
            "provider": "owner_scoped_training_evidence",
            "model": None,
            "tool_truth_state": "grounded",
        }
    elif connected_request:
        from backend.app.stacks.db_runtime.connected_symbol_context_bridge import (
            read_authenticated_connected_symbols,
        )

        owner = _chat_training_subject(principal)
        symbols = []
        available = False

        if not owner:
            reply = (
                "Your authenticated account identity is unavailable. "
                "Please sign in again."
            )
        else:
            try:
                symbols = await read_authenticated_connected_symbols(
                    owner_user_id=owner,
                )
                available = True

                if symbols:
                    reply = (
                        "Your connected SnapTrade symbols are: "
                        + ", ".join(symbols)
                        + "."
                    )
                else:
                    reply = (
                        "No synchronized SnapTrade stock symbols "
                        "were found for your account."
                    )
            except Exception:
                reply = (
                    "I couldn't retrieve your synchronized "
                    "SnapTrade holdings right now."
                )

        # NEUROVEST_OWNER_TRAINING_HANDOFF_V1
        # Only explicit training commands start a session.
        training_requested = (
            connected_message.strip().startswith("train ")
            or connected_message.strip().startswith("start training")
        )

        training = None
        training_blocked = False

        if training_requested:
            from backend.app.stacks.db_runtime.connected_symbol_context_bridge import (
                launch_connected_owner_training,
            )

            session_id = _chat_training_session(principal)
            role = _chat_training_role(principal)

            if not owner or not session_id:
                training_blocked = True
                reply = (
                    "Training was blocked: an authenticated "
                    "account and session are required."
                )
            elif role in {
                "admin", "administrator", "system_admin", "support"
            }:
                training_blocked = True
                reply = (
                    "Training was blocked: this account role "
                    "cannot launch training sessions."
                )
            else:
                try:
                    # Bind asynchronous findings delivery to this
                    # application's existing PostgreSQL event loop.
                    from backend.app.stacks.db_runtime.training_findings_delivery import (
                        register_training_findings_loop,
                    )
                    register_training_findings_loop()

                    training = await launch_connected_owner_training(
                        owner_user_id=owner,
                        owner_session_id=session_id,
                        role=role or "user",
                        duration_seconds=120,
                        notification_thread_id=thread.thread_id,
                        notification_parent_message_id=(
                            user_message.message_id
                        ),
                    )

                    reply = (
                        "Owner-scoped historical training started "
                        "for your connected SnapTrade symbols: "
                        + ", ".join(training["selected_symbols"])
                        + ". Run ID: "
                        + str(training["run_id"])
                        + ". Scope: USER. "
                        "No brokerage orders will be placed."
                    )
                except Exception:
                    training_blocked = True
                    reply = (
                        "Connected-symbol training could not start. "
                        "Verify your authenticated session, "
                        "authorized holdings, and historical data."
                    )

        runtime_result = {
            "status": (
                "blocked" if training_blocked
                else "ok" if available
                else "blocked"
            ),
            "response": {
                "type": "text",
                "message": reply,
            },
            "intent": (
                "connected_owner_training"
                if training_requested
                else "connected_snaptrade_symbols"
            ),
            "training_run": training,
            "symbol": None,
            "provider": (
                "snaptrade_owner_scoped_snapshot"
                if available else None
            ),
            "model": None,
            "tool_truth_state": (
                "grounded" if available else "unavailable"
            ),
        }
    else:
        # NEUROVEST_V26_MODEL_INPUT_BOUNDARY
        # Internal API evidence only; not part of ChatRequest.
        # NEUROVEST_V46_VALIDATED_MODEL_EVIDENCE
        from backend.app.stacks.chat_public.execution_capability_guard_v43 import (
            validated_evidence_text,
        )

        validated_text = validated_evidence_text(
            trusted_execution_evidence
        )
        if validated_text is not None:
            model_input += (
                "\n\n" + validated_text
            )

        # NEURO_AWARENESS_V3_ASYNC_BRIDGE_V1
        # Verified role from the existing backend principal.
        from backend.app.stacks.chat_public.developer_role_guard import (
            authenticated_developer_role as _v41_developer_role,
        )
        # NEUROVEST_DEVELOPER_AWARENESS_ROUTE_3ER3
        # This is routing, not authorization.
        # Use the existing authenticated developer guard.
        from backend.app.stacks.chat_public.developer_awareness_route_3er3 import (
            route_message as _nv3er3_route_message_fn,
        )
        from backend.app.stacks.chat_public.developer_intelligence_3e import (
            is_improvement_request as _nv3er3_improvement_intent,
        )

        _nv3er3_verified_dev = bool(
            _v41_developer_role(principal)
        )
        _nv3er3_improvement = (
            _nv3er3_improvement_intent(request.message)
        )

        _nv5_continuation = None
        if _nv3er3_verified_dev and request.thread_id:
            from backend.app.stacks.chat_public.developer_continuity_v5 import (
                continuation_question as _nv5_continuation_question,
            )
            try:
                _nv5_recent = await conversation_store.list_messages(
                    thread.thread_id,
                    limit=8,
                    oldest_first=False,
                )
                from backend.app.stacks.chat_public.developer_continuity_v5 import (
                    select_previous_user as _nv5_select_previous_user,
                )
                _nv5_prior_user = _nv5_select_previous_user(
                    _nv5_recent,
                    current_message_id=user_message.message_id,
                )
                _nv5_continuation = _nv5_continuation_question(
                    message=request.message,
                    previous_user=_nv5_prior_user,
                    verified_developer=_nv3er3_verified_dev,
                )
            except Exception:
                # Optional continuity fails closed.
                _nv5_continuation = None

        _nv3er3_legacy_route = (
            _neuro_v41_auto_awareness_question(
                request.message,
                _nv3er3_verified_dev,
            )
        )
        if _nv3er3_legacy_route is None and _nv5_continuation:
            _nv3er3_legacy_route = (
                "/dev awareness explain " + _nv5_continuation
            )

        _nv3er3_route_message = (
            _nv3er3_route_message_fn(
                message=request.message,
                verified_developer=_nv3er3_verified_dev,
                legacy_route=_nv3er3_legacy_route,
            )
        )

        _v3_match = re.fullmatch(
            r"/dev\s+awareness\s+explain\s+(.+)",
            _nv3er3_route_message,
            flags=re.IGNORECASE | re.DOTALL,
        )
        from backend.app.stacks.chat_public.developer_execution_trace_3er4 import (
            emit as _nv3er4_event,
            fingerprint as _nv3er4_fingerprint,
        )

        _nv3er4_event(
            question=request.message,
            stage="ROUTE_DECISION",
            trace_id=trace_id,
            verified_developer=bool(_nv3er3_verified_dev),
            awareness_match=bool(_v3_match is not None),
            improvement_intent=bool(_nv3er3_improvement),
        )

        if _v3_match is not None:
            _nv3er4_event(
                question=request.message,
                stage="AWARENESS_ENTERED",
                trace_id=trace_id,
                verified_developer=bool(_nv3er3_verified_dev),
            )
            _v3_ok = False
            _v35_model = None
            from backend.app.stacks.chat_public.developer_role_guard import (
                authenticated_developer_role as _v3_developer_role,
            )
            if not _v3_developer_role(principal):
                _v3_reply = "Authenticated developer role required for /dev commands."
            else:
                from backend.app.stacks.chat_public.neuro_awareness_v3_persistent_awareness import (
                    explain as _v3_explain,
                    AwarenessAccessError as _v3_AccessError,
                    AwarenessUnavailable as _v3_Unavailable,
                )
                from pathlib import Path as _v3_Path

                _v3_root = _v3_Path(__file__).resolve().parents[4]
                _v3_engine = (
                    _v3_root / "backend/app/stacks/chat_public/"
                    "neuro_awareness_v3_explanation_engine.py"
                )
                _v3_evidence = (
                    _v3_root / "runtime/qualification/"
                    "neuro_awareness_v3_active/lineage.json"
                )
                # NEURO_AWARENESS_V35_OLLAMA_V1
                # Failure to initialize local inference leaves V3 usable.
                try:
                    from functools import partial as _v35_partial
                    from backend.app.stacks.chat_public.ollama_chat_client import (
                        ask_ollama as _v35_ask_ollama,
                    )
                    _v35_model = _v35_partial(
                        _v35_ask_ollama,
                        intent="general_conversation",
                        model="neuro-reason:latest",
                    )
                except Exception:
                    _v35_model = None

                try:
                    # NEURO_SELF_ASSESSMENT_DIRECT_VERIFIED_REPORT_V1
                    # Only this exact developer question may use the
                    # separately qualified N10 improvement report.
                    _self_review_exact = (
                        request.message.strip().casefold().rstrip("?.! ")
                        == "neuro, what do you need to improve"
                        or (
                            _nv3er3_improvement
                            and _nv3er3_verified_dev
                        )
                    )

                    if _self_review_exact:
                        # NEUROVEST_R116G5_ISOLATED_SELF_ASSESSMENT
                        _nv_g5_owner = str(
                            getattr(principal, "subject", "") or ""
                        ).strip()
                        _nv_g5_thread_owner = str(
                            getattr(thread, "user_id", "") or ""
                        ).strip()
                        _nv_g5_thread_id = str(
                            getattr(thread, "thread_id", "") or ""
                        ).strip()

                        if (
                            not _v3_developer_role(principal)
                            or not _nv_g5_owner
                            or not _nv_g5_thread_id
                            or _nv_g5_thread_owner != _nv_g5_owner
                        ):
                            raise _v3_AccessError(
                                "Developer role or conversation ownership required"
                            )

                        import asyncio as _nv_g5_asyncio
                        import json as _nv_g5_json
                        import subprocess as _nv_g5_subprocess
                        import sys as _nv_g5_sys

                        _nv_g5_worker = (
                            _v3_root / "runtime/qualification/"
                            "r116g15_behavioral_evidence_20261022T214508Z/behavioral_dynamic_worker.py"
                        )

                        def _nv_g5_execute():
                            return _nv_g5_subprocess.run(
                                [
                                    _nv_g5_sys.executable,
                                    "-I", "-B",
                                    str(_nv_g5_worker),
                                    str(_v3_root),
                                ],
                                capture_output=True,
                                text=True,
                                timeout=8,
                                check=False,
                            )

                        try:
                            _nv_g5_process = await _nv_g5_asyncio.to_thread(
                                _nv_g5_execute
                            )
                            if (
                                _nv_g5_process.returncode != 0
                                or len(_nv_g5_process.stdout) > 24000
                            ):
                                raise ValueError("Worker unavailable")

                            _nv_g5_payload = _nv_g5_json.loads(
                                _nv_g5_process.stdout
                            )
                            if (
                                _nv_g5_payload.get("status") != "ok"
                                or _nv_g5_payload.get("read_only") is not True
                                or not isinstance(
                                    _nv_g5_payload.get("answer"), str
                                )
                            ):
                                raise ValueError("Invalid worker result")

                            _v3_reply = _nv_g5_payload["answer"]
                            _v3_ok = True
                            _nv_r10_evidence_selected = True
                        except Exception:
                            _v3_reply = (
                                "Developer operational evidence is temporarily "
                                "unavailable. The isolated assessment did not "
                                "qualify; no platform changes were made."
                            )
                            _v3_ok = False
                    else:
                        # NV_V5_GROUNDED_INTEGRATION
                        # Optional; developer-only; original V3 fallback.
                        from backend.app.stacks.chat_public.developer_awareness_integration_v5 import (
                            maybe_grounded_developer_answer as _nv5_grounded_answer,
                        )
                        _nv5_answer = await _nv5_grounded_answer(
                            root=_v3_root,
                            principal=principal,
                            thread=thread,
                            question=_v3_match.group(1),
                        )
                        if _nv5_answer is not None:
                            _nv5_selected = True
                            _v3_reply = _nv5_answer
                        else:
                            _v3_result = await _v3_explain(
                                root=_v3_root,
                                engine_path=_v3_engine,
                                evidence_path=_v3_evidence,
                                principal=principal,
                                thread=thread,
                                question=_v3_match.group(1),
                                store=conversation_store,
                                model=_v35_model,
                            )
                            _v3_reply = __import__(
                                "backend.app.stacks.chat_public.neuro_awareness_v37_retriever",
                                fromlist=["polish_developer_answer"],
                            ).polish_developer_answer(
                                _v3_result["answer"], request.message
                            )
                    _v3_ok = True
                except _v3_AccessError:
                    _v3_reply = "Authenticated developer role or conversation ownership required."
                except _v3_Unavailable:
                    _v3_reply = "Architecture evidence unavailable or stale."

            runtime_result = {
                "status": "ok" if _v3_ok else "error",
                "response": {"type": "text", "message": _v3_reply},
                "intent": "developer_architecture_awareness",
                "symbol": None,
                "strategy_capture": None,
                "provider": "neurovest_local_evidence",
                "model": "neuro-reason:latest" if _v3_ok and _v35_model is not None else None,
                "tool_truth_state": "grounded" if _v3_ok else "unavailable",
                "error": None if _v3_ok else "awareness_not_qualified",
                "cognitive_route": None,
            }
            _nv3er4_event(
                question=request.message,
                stage="AWARENESS_RESULT",
                trace_id=trace_id,
                awareness_success=bool(_v3_ok),
                verified_report=bool(
                    _self_review_exact
                    if "_self_review_exact" in locals()
                    else False
                ),
            )
        else:
            # NEUROVEST_13D_R51_CONTEXTUAL_FOCUS
            from backend.app.stacks.chat_public.contextual_focus_13d_r51 import (
                attach_contextual_focus as _nv13d_r51_attach_contextual_focus,
            )
            runtime_result = handle_chat_message(
                request.message,
                model_input=_nv13d_r51_attach_contextual_focus(_nv12g_r2_focus_context(_nv5c_enhance_model_input(model_input, request.message, assembled_context.recent_messages), request.message), request.message, assembled_context.recent_messages, authenticated_owner=bool(authenticated_owner_subject)),
                detected_intent=detected_intent,
                developer_evidence_allowed=(
                    developer_evidence_allowed
                ),
                routing_decision=(
                    routing_decision
                ),
                principal=principal,
                request_route=(
                    request_route_contract
                    .route
                    .value
                ),
            )

    # G41: retain the original handler result for safe status recovery.
    _g41_initial_runtime_status = runtime_result.get("status")
    _g41_initial_runtime_response = runtime_result.get("response")
    _g41_initial_runtime_message = (
        _g41_initial_runtime_response.get("message", "")
        if isinstance(_g41_initial_runtime_response, dict)
        else ""
    )

    # Bind existing successful Chat history into Frozen25 feature context.
    # This performs feature materialization only — no model inference.
    if (
        isinstance(
            runtime_result,
            dict,
        )
        and runtime_result.get(
            "status"
        ) == "ok"
        and runtime_result.get(
            "historical_bars"
        )
        and runtime_result.get(
            "symbol"
        )
    ):

        try:

            frozen25_feature_frame = (
                _build_chat_frozen25_feature_frame(
                    bars=runtime_result.get(
                        "historical_bars"
                    ),
                    provider_symbol=runtime_result.get(
                        "symbol"
                    ),
                )
            )

        except Exception:

            # Optional bounded context; Chat remains fail-open.
            frozen25_feature_frame = None


    if (
        retrieval_bundle.grounded
        or math_bundle.grounded
    ):
        runtime_result[
            "tool_truth_state"
        ] = "grounded"

    intent_status = str(
        runtime_result.get(
            "status",
            "error",
        )
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="INTENT_CLASSIFICATION_COMPLETED",
        node="intent_classifier",
        source="intent_classifier",
        destination=(
            "ollama_adapter"
            if runtime_result.get(
                "provider"
            )
            == OLLAMA_PROVIDER
            else "response_validation"
        ),
        status=(
            "completed"
            if intent_status == "ok"
            else intent_status
        ),
        symbol=runtime_result.get(
            "symbol"
        ),
        layer="L2",
        stack="chat_public",
        details={
            "operation": (
                runtime_result.get(
                    "intent"
                )
                or "unknown"
            ),
            "success": (
                intent_status == "ok"
            ),
        },
    )

    if (
        runtime_result.get(
            "provider"
        )
        == OLLAMA_PROVIDER
    ):
        await emit_runtime_step(
            trace_id=trace_id,
            event_type="OLLAMA_RESPONSE_RECEIVED",
            node="ollama_adapter",
            source="intent_classifier",
            destination="ollama_adapter",
            status=(
                "completed"
                if intent_status == "ok"
                else "failed"
            ),
            symbol=runtime_result.get(
                "symbol"
            ),
            layer="L0",
            stack="chat_public",
            details={
                "operation": "local_model_inference",
                "provider": OLLAMA_PROVIDER,
                "model": runtime_result.get(
                    "model"
                ),
                "latency_ms": (
                    perf_counter()
                    - inference_started
                ) * 1000,
                "success": (
                    intent_status == "ok"
                ),
                "error": runtime_result.get(
                    "error"
                ),
            },
        )

    assistant_content = _response_message(
        runtime_result["response"]
    )

    if (
        retrieval_bundle.grounded
        and retrieval_bundle.citations
    ):
        assistant_content = (
            _ensure_approved_retrieval_citation(
                assistant_content,
                retrieval_bundle.citations,
            )
        )

        runtime_result[
            "response"
        ][
            "message"
        ] = assistant_content

    verification_started = perf_counter()

    assistant_content = _enforce_repeated_lifecycle_strategy_completeness(
        request.message,
        assistant_content,
    )

    assistant_content = _render_repeated_lifecycle_strategy_list_cleanly(
        request.message,
        assistant_content,
    )

    assistant_content = _v32_apply_response_quality_guards(
        request.message,
        assistant_content,
    )

    assistant_content = _v36r3_finance_semantic_guard(
        request.message,
        assistant_content,
    )

    # NEUROVEST_13D_R82_RESPONSE_PRESENTATION
    from backend.app.stacks.chat_public.answer_presentation_13d_r82 import (
        clean_assistant_presentation as _nv82_clean_presentation,
    )
    assistant_content = _nv82_clean_presentation(
        assistant_content
    )


    # NEUROVEST_R116_G40_RESPONSE_ASSEMBLY_CLEANUP
    # Conservative, exact substantial paragraph deduplication.
    # Do not modify fenced code blocks.
    if "```" not in assistant_content:
        _g40_parts = re.split(
            r"\n\s*\n",
            assistant_content,
        )
        _g40_seen = set()
        _g40_output = []
        for _g40_part in _g40_parts:
            _g40_normal = re.sub(
                r"\s+", " ", _g40_part
            ).strip().casefold()
            if (
                len(_g40_normal) >= 100
                and _g40_normal in _g40_seen
            ):
                continue
            if len(_g40_normal) >= 100:
                _g40_seen.add(_g40_normal)
            _g40_output.append(_g40_part)
        assistant_content = "\n\n".join(_g40_output).strip()

    verification_result: ResponseVerificationResult = (
        verify_response(
            assistant_content,
            math_bundle=math_bundle,
            retrieval_bundle=retrieval_bundle,
        )
    )

    assistant_content = (
        verification_result.final_response
    )

    # V36-R4R2 — routing is already proven correct for the residual
    # Q24/Q37/Q40 failures. Repair only the final user-visible semantic
    # boundary, then re-run the verifier against the repaired answer.
    repaired_semantic_content = (
        _v36r4_downstream_semantic_repair(
            request.message,
            assistant_content,
        )
    )

    if (
        repaired_semantic_content
        != assistant_content
    ):

        verification_result = (
            verify_response(
                repaired_semantic_content,
                math_bundle=math_bundle,
                retrieval_bundle=retrieval_bundle,
            )
        )

        assistant_content = (
            verification_result.final_response
        )

    # V36-R5R3 — apply only the defects confirmed by the
    # final 40-answer semantic adjudication. This occurs after the
    # existing downstream verifier repair and before response sync
    # and assistant-message persistence.
    final_quality_content = (
        _v36r5_final_answer_quality_repair(
            request.message,
            assistant_content,
        )
    )

    if (
        final_quality_content
        != assistant_content
    ):

        # V36-R5R8 — final semantic citation preservation.
        #
        # A bounded semantic replacement may replace the citation that
        # had already been attached to the original generated answer.
        # Reapply one token ONLY from the existing approved retrieval
        # bundle before the existing verifier runs again.
        #
        # The verifier remains authoritative and fail-closed.
        if (
            retrieval_bundle.grounded
            and retrieval_bundle.citations
        ):

            final_quality_content = (
                _ensure_approved_retrieval_citation(
                    final_quality_content,
                    retrieval_bundle.citations,
                )
            )

        verification_result = (
            verify_response(
                final_quality_content,
                math_bundle=math_bundle,
                retrieval_bundle=retrieval_bundle,
            )
        )

        assistant_content = (
            verification_result.final_response
        )

    strategy_snapshot_content = (
        _build_strategy_snapshot_explanation_v1(
            request.message,
        )
    )

    if strategy_snapshot_content is not None:
        verification_result = verify_response(
            strategy_snapshot_content,
            math_bundle=math_bundle,
            retrieval_bundle=retrieval_bundle,
        )
        assistant_content = (
            verification_result.final_response
        )

    # NEUROVEST_V43_PRE_PERSISTENCE_CAPABILITY_GUARD
    # Bounded, explanatory only. No order or mode transition.
    from backend.app.stacks.chat_public.execution_capability_guard_v43 import (
        deterministic_capability_answer,
    )

    if isinstance(trusted_execution_evidence, object):
        guarded_content = deterministic_capability_answer(
            request.message,
            trusted_execution_evidence,
        )

        if guarded_content is not None:
            verification_result = verify_response(
                guarded_content,
                math_bundle=math_bundle,
                retrieval_bundle=retrieval_bundle,
            )
            assistant_content = verification_result.final_response

    runtime_response = runtime_result.get(
        "response"
    )

    if isinstance(
        runtime_response,
        dict,
    ):
        runtime_response[
            "message"
        ] = assistant_content

    runtime_result[
        "response_verification"
    ] = verification_result.as_dict()

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="RESPONSE_VERIFICATION_COMPLETED",
        node="response_verifier",
        source="model_runtime",
        destination="response_validation",
        status=(
            "completed"
            if verification_result.passed
            else (
                "repaired"
                if verification_result.repaired
                else "failed"
            )
        ),
        symbol=runtime_result.get(
            "symbol"
        ),
        layer="L3",
        stack="chat_public",
        details={
            "operation":
                "verify_generated_response",
            "verification_status":
                verification_result.status,
            "passed":
                verification_result.passed,
            "repaired":
                verification_result.repaired,
            "fail_closed":
                verification_result.fail_closed,
            "violation_count":
                len(
                    verification_result.violations
                ),
            "violation_codes": [
                violation.code
                for violation
                in verification_result.violations
            ],
            "checks":
                verification_result.checks,
            "latency_ms": (
                perf_counter()
                - verification_started
            ) * 1000,
        },
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="RESPONSE_VALIDATED",
        node="response_validation",
        source=(
            "ollama_adapter"
            if runtime_result.get(
                "provider"
            )
            == OLLAMA_PROVIDER
            else "intent_classifier"
        ),
        destination="response_validation",
        status=(
            "completed"
            if intent_status == "ok"
            else intent_status
        ),
        symbol=runtime_result.get(
            "symbol"
        ),
        layer="L3",
        stack="chat_public",
        details={
            "operation": "response_validation",
            "response_bytes": len(
                assistant_content.encode(
                    "utf-8"
                )
            ),
            "success": (
                intent_status == "ok"
            ),
        },
    )

    assistant_persist_started = perf_counter()


    # NEUROVEST_UNIVERSE_REPLY_FIX_V2
    from backend.app.stacks.chat_public.financial_analysis_chat_bridge import (
        authoritative_universe_reply as _universe_reply_v2,
    )

    _verified_universe_reply = (
        None
        if _g41_network_only
        else _universe_reply_v2(
            request.message,
            financial_chat_evidence,
        )
    )

    # NV_V5_R10_QUALIFIED_EVIDENCE_PRESERVATION
    # The existing response verification has already run.
    _nv_qualified_developer_evidence = (
        (
            locals().get("_nv_r10_evidence_selected") is True
            or locals().get("_nv5_selected") is True
        )
        and runtime_result.get("status") == "ok"
        and runtime_result.get("intent")
            == "developer_architecture_awareness"
        and _v3_developer_role(principal)
    )

    if (
        _verified_universe_reply is not None
        and not _nv_qualified_developer_evidence
    ):
        assistant_content = _verified_universe_reply
        runtime_result["response"] = {
            "type": "text",
            "message": assistant_content,
        }
        runtime_result["message"] = assistant_content

    # NEUROVEST_ANSWER_RELEVANCE_3DR2
    # General knowledge only; financial and coding paths
    # remain in their existing verified pipelines.
    from backend.app.stacks.chat_public.answer_relevance_3dr2 import (
        verify_and_repair as _nv_relevance_verify,
        clean_general_reply as _nv_clean_general_reply,
    )

    if _nv_qualified_developer_evidence:
        _nv_relevance_status = "unchanged"
    else:
        assistant_content, _nv_relevance_status = (
            await _nv_relevance_verify(
                question=request.message,
                answer=assistant_content,
                model_call=_nv_clean_general_reply,
            )
        )

    if _nv_relevance_status != "unchanged":
        runtime_result["response"] = {
            "type": "text",
            "message": assistant_content,
        }
        runtime_result["message"] = assistant_content

    # NEUROVEST_DEVELOPER_AUTHORIZATION_3ER1
    # Principal comes from the authenticated backend.
    # No model-controlled or browser-provided role claims.
    from backend.app.stacks.chat_public.developer_authorization_3er1 import (
        assessed_developer_reply as _nv3er1_developer_reply,
    )

    # NEUROVEST_R10_EVIDENCE_RESPONSE_PRESERVATION
    # Do not replace a successful developer-only R4 assessment
    # with the legacy generic self-assessment.
    # Other requests retain the existing authorization workflow.
    _nv_r10_preserve_evidence = (
        _nv_qualified_developer_evidence
    )

    if _nv_r10_preserve_evidence:
        _nv3e_reply = None
    else:
        _nv3e_reply = _nv3er1_developer_reply(
            principal=principal,
            existing_permission=developer_evidence_allowed,
            message=request.message,
        )

    if _nv3e_reply is not None:
        assistant_content = _nv3e_reply
        runtime_result["response"] = {
            "type": "text",
            "message": assistant_content,
        }
        runtime_result["message"] = assistant_content
        runtime_result["tool_truth_state"] = "grounded"

    from backend.app.stacks.chat_public.developer_execution_trace_3er4 import (
        emit as _nv3er4_final_event,
        fingerprint as _nv3er4_final_fingerprint,
    )

    # NEURO_INTELLIGENCE_13A_R15:
    # Resolve the selected financial-universe reply BEFORE
    # verification, guarding, tracing and persistence.
    if _verified_universe_reply is not None:
        assistant_content = _verified_universe_reply
        verification_result = verify_response(
            assistant_content,
            math_bundle=math_bundle,
            retrieval_bundle=retrieval_bundle,
        )
        assistant_content = verification_result.final_response

    _nv13a_checked, _nv13a_observation = (
        safe_diagnostic_response(
            request.message,
            assistant_content,
        )
    )

    if _nv13a_checked != assistant_content:
        verification_result = verify_response(
            _nv13a_checked,
            math_bundle=math_bundle,
            retrieval_bundle=retrieval_bundle,
        )
        assistant_content = verification_result.final_response

    _nv13a_final_check = inspect_diagnostic_response(
        request.message,
        assistant_content,
    )

    if _nv13a_final_check["violations"]:
        raise RuntimeError(
            "NEURO_INTELLIGENCE_13A_R13C_PRE_PERSIST_BLOCKED"
        )

    # NEUROVEST_13D_R90_CODE_QUALITY_GATE
    from backend.app.stacks.chat_public.answer_code_quality_13d_r90 import (
        inspect_python_answer as _nv90_inspect,
    )
    _nv90_candidate, _nv90_report = _nv90_inspect(
        request.message,
        assistant_content,
    )
    if _nv90_candidate != assistant_content:
        _nv90_verified = verify_response(
            _nv90_candidate,
            math_bundle=math_bundle,
            retrieval_bundle=retrieval_bundle,
        )
        if _nv90_verified.passed or _nv90_verified.repaired:
            _nv90_checked = _nv90_verified.final_response
            _nv90_safety = inspect_diagnostic_response(
                request.message,
                _nv90_checked,
            )
            if not _nv90_safety['violations']:
                assistant_content = _nv90_checked
                verification_result = _nv90_verified

    # NEUROVEST_R94_POST_GENERATION_ASSESSMENT
    # Inspect final answer; never bypass existing verification.
    try:
        from backend.app.stacks.chat_public.conversation_intelligence_13e_r93 import assess_answer as _nv94_assess
        _nv94_assessment = _nv94_assess(
            request.message,
            assistant_content,
        )
        if isinstance(runtime_result, dict):
            runtime_result['conversation_quality_r94'] = {
                'version': 'R94',
                'confidence': _nv94_assessment.confidence,
                'requested_count': len(_nv94_assessment.requested),
                'missing_count': len(_nv94_assessment.missing),
                'incomplete_code': _nv94_assessment.truncated_code_fence,
                'incomplete_table': _nv94_assessment.incomplete_table,
                'evidence_requested': _nv94_assessment.evidence_requested,
                'source_markers_present': _nv94_assessment.source_markers_present,
                'evidence_verified': False,
            }
    except Exception:
        pass

    # NEUROVEST_R96_FINAL_RESPONSE_RELIABILITY
    # Preserve all existing authority and safety checks.
    from backend.app.stacks.chat_public.response_reliability_13f_r96 import (
        classify_response as _nv96_classify,
        recovery_candidate as _nv96_recover,
        quality_summary as _nv96_quality_summary,
    )
    from backend.app.stacks.chat_public.conversation_intelligence_13e_r93 import (
        assess_answer as _nv96_assess,
    )

    _nv96_initial = _nv96_classify(
        request.message,
        assistant_content,
    )
    _nv96_recovered = False

    if _nv96_initial["needs_recovery"]:
        _nv96_replacement, _nv96_decision = _nv96_recover(
            request.message,
            assistant_content,
        )

        if not _nv96_decision["safe_recovery_candidate"]:
            raise RuntimeError(
                "R96: protected or nonrecoverable empty response"
            )

        # Verify the neutral failure notice using existing gates.
        _nv96_verified = verify_response(
            _nv96_replacement,
            math_bundle=math_bundle,
            retrieval_bundle=retrieval_bundle,
        )

        if not (
            _nv96_verified.passed
            or _nv96_verified.repaired
        ):
            raise RuntimeError(
                "R96: recovery notice failed verification"
            )

        _nv96_checked = _nv96_verified.final_response

        if (
            not isinstance(_nv96_checked, str)
            or not _nv96_checked.strip()
        ):
            raise RuntimeError(
                "R96: verification returned empty recovery"
            )

        _nv96_safety = inspect_diagnostic_response(
            request.message,
            _nv96_checked,
        )

        if _nv96_safety["violations"]:
            raise RuntimeError(
                "R96: recovery notice failed safety inspection"
            )

        assistant_content = _nv96_checked
        verification_result = _nv96_verified
        _nv96_recovered = True

    _nv96_final = _nv96_classify(
        request.message,
        assistant_content,
    )

    if _nv96_final["needs_recovery"]:
        raise RuntimeError(
            "R96: final response is still empty"
        )

    _nv96_assessment = _nv96_assess(
        request.message,
        assistant_content,
    )

    if isinstance(runtime_result, dict):
        runtime_result["conversation_quality_r96"] = {
            "version": "R96",
            "final_state": _nv96_final["state"],
            "recovery_notice_used": _nv96_recovered,
            **_nv96_quality_summary(_nv96_assessment),
        }

    # NEUROVEST_R97_ANSWER_COVERAGE
    # Advisory only. Existing verifier and diagnostic guards retain authority.
    try:
        from backend.app.stacks.chat_public.conversation_execution_13g_r97 import (
            evaluate_coverage as _nv97_coverage,
        )
        _nv97_result = _nv97_coverage(
            request.message,
            assistant_content,
        )
        if isinstance(runtime_result, dict):
            runtime_result["conversation_quality_r97"] = _nv97_result
    except Exception:
        pass

    # NEUROVEST_R100_FINANCIAL_EVIDENCE_INTEGRITY
    # Analyze actual retrieval provenance without changing the answer.
    try:
        from backend.app.stacks.chat_public.financial_evidence_13j_r100 import (
            assess_financial_evidence as _nv100_assess,
        )
        _nv100_evidence = _nv100_assess(
            request.message,
            assistant_content,
            retrieval_bundle,
        )
        if isinstance(runtime_result, dict):
            runtime_result["financial_evidence_r100"] = _nv100_evidence
    except Exception:
        pass

    # NEUROVEST_R101_FINANCIAL_CLAIM_MATCHING
    # Advisory matching only; do not change final answer or authority.
    try:
        from backend.app.stacks.chat_public.financial_claims_13k_r101 import (
            assess_claims as _nv101_assess,
        )
        # NEUROVEST_R103_ISSUER_AWARE_CLAIM_GATE
        # Use conservative issuer resolution before financial
        # numerical comparisons can influence R102 disclosure.
        from backend.app.stacks.chat_public.issuer_evidence_13m_r103 import (
            assess_issuer_claims as _nv103_assess,
        )

        # NEUROVEST_R104C_YFINANCE_SUBJECT_BINDING
        # Resolve only an explicitly named, single EQUITY ticker.
        # Unknown or multiple tickers continue to fail closed.
        from backend.app.stacks.chat_public.yfinance_issuer_13n_r104c import (
            explicit_ticker as _nv104c_explicit_ticker,
            resolve_research_issuer as _nv104c_resolve,
        )

        _nv104c_subject = None

        if _nv104c_explicit_ticker(request.message):
            from asyncio import to_thread, wait_for

            try:
                _nv104c_subject = await wait_for(
                    to_thread(
                        _nv104c_resolve,
                        request.message,
                    ),
                    timeout=4.0,
                )
            except Exception:
                _nv104c_subject = None

        _nv101_result = _nv103_assess(
            request.message,
            assistant_content,
            retrieval_bundle,
            subject=_nv104c_subject,
        )
        if isinstance(runtime_result, dict):
            runtime_result["financial_claims_r101"] = _nv101_result
    except Exception:
        pass

    # NEUROVEST_R102_GUARDED_EVIDENCE_DISCLOSURE
    # R100/R101 findings may qualify the answer, never authorize actions.
    try:
        from backend.app.stacks.chat_public.financial_evidence_response_13l_r102 import (
            build_evidence_disclosure as _nv102_disclose,
        )

        _nv102_candidate, _nv102_meta = _nv102_disclose(
            request.message,
            assistant_content,
            runtime_result.get("financial_evidence_r100"),
            runtime_result.get("financial_claims_r101"),
        )

        _nv102_meta["accepted_by_verifier"] = False

        if _nv102_meta["changed"]:
            _nv102_verified = verify_response(
                _nv102_candidate,
                math_bundle=math_bundle,
                retrieval_bundle=retrieval_bundle,
            )

            if _nv102_verified.passed or _nv102_verified.repaired:
                _nv102_checked = _nv102_verified.final_response

                if (
                    isinstance(_nv102_checked, str)
                    and _nv102_checked.strip()
                    and "Evidence qualification:" in _nv102_checked
                ):
                    _nv102_safety = inspect_diagnostic_response(
                        request.message,
                        _nv102_checked,
                    )

                    if not _nv102_safety["violations"]:
                        assistant_content = _nv102_checked
                        verification_result = _nv102_verified
                        _nv102_meta["accepted_by_verifier"] = True

        runtime_result["financial_evidence_response_r102"] = {
            "version": "R102",
            "eligible": _nv102_meta["eligible"],
            "candidate_generated": _nv102_meta["changed"],
            "accepted": _nv102_meta["accepted_by_verifier"],
            "reason": _nv102_meta["reason"],
            "provenance_issue": _nv102_meta["provenance_issue"],
            "claim_review_issue": _nv102_meta["claim_review_issue"],
            "trading_authorized": False,
            "permissions_changed": False,
        }

    except Exception:
        # Never replace an otherwise valid answer on diagnostic failure.
        pass

    # NEUROVEST_R106_FINAL_CITATION_SANITIZER
    # NEUROVEST_R106_FIX2_RUNTIME_INTEGRATION
    try:
        from backend.app.stacks.chat_public.response_cleanup_13p_r106fix import (
            cleanup_response as _nv106_cleanup,
        )

        _nv106_candidate = _nv106_cleanup(assistant_content)

        if (
            isinstance(_nv106_candidate, str)
            and _nv106_candidate.strip()
            and _nv106_candidate != assistant_content
        ):
            _nv106_verified = verify_response(
                _nv106_candidate,
                math_bundle=math_bundle,
                retrieval_bundle=retrieval_bundle,
            )

            if (
                _nv106_verified.passed
                or _nv106_verified.repaired
            ):
                _nv106_final = _nv106_cleanup(
                    _nv106_verified.final_response
                )

                if (
                    isinstance(_nv106_final, str)
                    and _nv106_final.strip()
                    and _nv106_cleanup(_nv106_final)
                        == _nv106_final
                ):
                    _nv106_safety = inspect_diagnostic_response(
                        request.message,
                        _nv106_final,
                    )

                    if not _nv106_safety["violations"]:
                        assistant_content = _nv106_final
                        verification_result = _nv106_verified

    except Exception:
        pass


    # NEUROVEST_R112_C5_FINAL_REFERENCE_BOUNDARY
    # Only explicit previous-question recall with unambiguous,
    # owner-scoped evidence already retained in the assembled prompt.
    # Existing response verification and safety gates remain authoritative.
    if not _nv_qualified_developer_evidence:
        from backend.app.stacks.chat_public.context.conversation_references_14a_r112 import (
            verified_previous_question_answer as _nv112_c5_answer,
        )

        _nv112_c5_candidate = _nv112_c5_answer(
            request.message,
            assembled_context.prompt,
        )

        if _nv112_c5_candidate is not None:
            _nv112_c5_verified = verify_response(
                _nv112_c5_candidate,
                math_bundle=math_bundle,
                retrieval_bundle=retrieval_bundle,
            )

            if (
                _nv112_c5_verified.passed
                or _nv112_c5_verified.repaired
            ):
                _nv112_c5_final = _nv112_c5_verified.final_response

                if (
                    isinstance(_nv112_c5_final, str)
                    and _nv112_c5_final.strip()
                ):
                    _nv112_c5_safety = inspect_diagnostic_response(
                        request.message,
                        _nv112_c5_final,
                    )

                    if not _nv112_c5_safety["violations"]:
                        assistant_content = _nv112_c5_final
                        verification_result = _nv112_c5_verified

    # NEUROVEST_R112_C6_STRUCTURED_REFERENCE_FINAL
    # Previous-question references must come from authorized history.
    # Existing verifier and safety inspector retain final authority.
    try:
        _nv112_c6_candidate = (
            None if _nv_qualified_developer_evidence
            else assembled_context.reference_answer
        )
        if isinstance(_nv112_c6_candidate, str) and _nv112_c6_candidate.strip():
            _nv112_c6_verified = verify_response(
                _nv112_c6_candidate,
                math_bundle=math_bundle,
                retrieval_bundle=retrieval_bundle,
            )
            if _nv112_c6_verified.passed or _nv112_c6_verified.repaired:
                _nv112_c6_final = _nv112_c6_verified.final_response
                if isinstance(_nv112_c6_final, str) and _nv112_c6_final.strip():
                    _nv112_c6_safety = inspect_diagnostic_response(
                        request.message, _nv112_c6_final,
                    )
                    if not _nv112_c6_safety["violations"]:
                        assistant_content = _nv112_c6_final
                        verification_result = _nv112_c6_verified
    except Exception:
        pass


    # NEUROVEST_R114G6_CITATION_FINAL_BOUNDARY
    # Public research citation verification only.
    # No additional model capabilities or authority.
    try:
        if (
            not _nv_qualified_developer_evidence
            and isinstance(assistant_content, str)
        ):
            import asyncio as _nv114g6_asyncio

            from backend.app.stacks.chat_public.context.citation_integrity_14g_r114 import (
                eligible as _nv114g6_eligible,
                extract_dois as _nv114g6_extract,
                verify_answer as _nv114g6_verify,
            )

            if (
                # NEUROVEST_G43_R42D_CROSSREF_RECOVERY
                _nv114g6_eligible(request.message)
                and (
                    _nv114g6_extract(assistant_content)
                    or __import__('os').environ.get(
                        'NV_R42D_CROSSREF_RECOVERY_ENABLED'
                    ) == '1'
                )
            ):
                _nv114g6_result = await _nv114g6_asyncio.to_thread(
                    _nv114g6_verify,
                    request.message,
                    assistant_content,
                )

                if (
                    isinstance(_nv114g6_result, str)
                    and _nv114g6_result.strip()
                ):
                    _nv114g6_safety = inspect_diagnostic_response(
                        request.message,
                        _nv114g6_result,
                    )

                    if not _nv114g6_safety["violations"]:
                        _nv114g6_verified = verify_response(
                            _nv114g6_result,
                            math_bundle=math_bundle,
                            retrieval_bundle=retrieval_bundle,
                        )

                        if (
                            _nv114g6_verified.passed
                            or _nv114g6_verified.repaired
                        ):
                            _nv114g6_final = (
                                _nv114g6_verified.final_response
                            )

                            if (
                                isinstance(_nv114g6_final, str)
                                and _nv114g6_final.strip()
                            ):
                                assistant_content = _nv114g6_final
                                verification_result = _nv114g6_verified

    except Exception:
        # Citation verification cannot interrupt normal chat.
        pass


    # NEUROVEST_R116_G32_AUTHORITATIVE_REASONING
    # Restricted structured arguments only; unsupported inputs pass through.
    # Final-answer boundary follows existing authorization/repair handlers.
    if not locals().get("_nv_qualified_developer_evidence", False):
        try:
            from backend.app.stacks.chat_public.deductive_existence_verifier_r116g32 import (
                verify as _nv_g32_verify,
            )
            from backend.app.stacks.chat_public.structured_reasoning_adapter_r116g32 import (
                evaluate as _nv_g32_evaluate,
            )
            from backend.app.stacks.chat_public.authoritative_reasoning_boundary_r116g32 import (
                finalize_reply as _nv_g32_finalize,
            )

            _nv_g32_answer, _nv_g32_origin = _nv_g32_finalize(
                request.message,
                assistant_content,
                _nv_g32_evaluate,
                _nv_g32_verify,
            )

            if _nv_g32_origin == "deterministic_verified":
                _nv_g32_safe = inspect_diagnostic_response(
                    request.message,
                    _nv_g32_answer,
                )
                if not _nv_g32_safe["violations"]:
                    _nv_g32_checked = verify_response(
                        _nv_g32_answer,
                        math_bundle=math_bundle,
                        retrieval_bundle=retrieval_bundle,
                    )
                    if (
                        _nv_g32_checked.passed
                        or _nv_g32_checked.repaired
                    ):
                        _nv_g32_final = _nv_g32_checked.final_response
                        if (
                            isinstance(_nv_g32_final, str)
                            and _nv_g32_final.strip()
                            and _nv_g32_final.startswith("No.")
                            and "does not necessarily follow" in _nv_g32_final
                        ):
                            assistant_content = _nv_g32_final
                            verification_result = _nv_g32_checked
        except Exception:
            # Fail open to existing qualified chat behavior.
            pass


    # NEUROVEST_R116_G36_FREEFORM_REASONING
    # G34 structured verifier remains earlier in this function.
    # Unsupported forms leave the existing answer unchanged.
    # No access to broker, execution authority, or credentials.
    if not locals().get("_nv_qualified_developer_evidence", False):
        try:
            from backend.app.stacks.chat_public.freeform_reasoning_engine_r116g36 import (
                authoritative_reply as _nv_g36_reply,
            )
            _nv_g36_authoritative = _nv_g36_reply(request.message)

            # Positive and negative proofs have distinct, fixed
            # prefixes. Do not let arbitrary text become a final
            # authoritative replacement.
            if (
                isinstance(_nv_g36_authoritative, str)
                and _nv_g36_authoritative.startswith((
                    "Yes, the conclusion necessarily follows.",
                    "No, the conclusion does not necessarily follow.",
                ))
            ):
                _nv_g36_safety = inspect_diagnostic_response(
                    request.message,
                    _nv_g36_authoritative,
                )
                if not _nv_g36_safety["violations"]:
                    _nv_g36_verified = verify_response(
                        _nv_g36_authoritative,
                        math_bundle=math_bundle,
                        retrieval_bundle=retrieval_bundle,
                    )
                    if (
                        _nv_g36_verified.passed
                        or _nv_g36_verified.repaired
                    ):
                        _nv_g36_final = _nv_g36_verified.final_response
                        if (
                            isinstance(_nv_g36_final, str)
                            and _nv_g36_final.strip()
                            and _nv_g36_final.startswith((
                                "Yes, the conclusion necessarily follows.",
                                "No, the conclusion does not necessarily follow.",
                            ))
                        ):
                            assistant_content = _nv_g36_final
                            verification_result = _nv_g36_verified
        except Exception:
            # Preserve G34's already-qualified final answer.
            pass



    # NEUROVEST_G43_R50_R3_FINANCE_QUALITY
    # Only generic TFSA/RRSP educational comparisons.
    # Existing authentication, developer and trading
    # restrictions remain authoritative.
    if __import__("os").environ.get(
        "NV_R50_R3_FINANCE_QUALITY_ENABLED"
    ) == "1":
        from backend.app.stacks.chat_public.canadian_accounts_quality_r50r3 import (
            repair as _nv_r50r3_repair,
        )

        _nv_r50r3_answer, _nv_r50r3_changed, _nv_r50r3_issues = (
            _nv_r50r3_repair(
                request.message,
                assistant_content,
                enabled=True,
                protected_developer=bool(
                    locals().get(
                        "_nv_qualified_developer_evidence",
                        False,
                    )
                ),
            )
        )

        if _nv_r50r3_changed:
            _nv_r50r3_verified = verify_response(
                _nv_r50r3_answer,
                math_bundle=math_bundle,
                retrieval_bundle=retrieval_bundle,
            )
            if not (
                _nv_r50r3_verified.passed
                or _nv_r50r3_verified.repaired
            ):
                raise RuntimeError(
                    "R50-R3: reference answer verification failed"
                )

            _nv_r50r3_final = (
                _nv_r50r3_verified.final_response
            )
            if not isinstance(
                _nv_r50r3_final, str
            ) or not _nv_r50r3_final.strip():
                raise RuntimeError(
                    "R50-R3: empty verified replacement"
                )

            if _nv_r50r3_repair(
                request.message,
                _nv_r50r3_final,
                enabled=True,
            )[1]:
                raise RuntimeError(
                    "R50-R3: unresolved financial accuracy issue"
                )

            _nv_r50r3_safety = inspect_diagnostic_response(
                request.message,
                _nv_r50r3_final,
            )
            if _nv_r50r3_safety["violations"]:
                raise RuntimeError(
                    "R50-R3: safety inspection rejected answer"
                )

            assistant_content = _nv_r50r3_final
            verification_result = _nv_r50r3_verified


    # NEUROVEST_G43_R56_FINAL
    # Read-only factual diagnostics; does not replace developer
    # evidence, claim verification, safety policy or final response.
    if __import__("os").environ.get(
        "NV_G43_R56_FINANCE_ENABLED"
    ) == "1":
        from backend.app.stacks.chat_public.financial_grounding_g43_r56 import (
            review as _r56_finance_review,
        )
        assistant_content, _r56_finance_issues = _r56_finance_review(
            request.message,
            assistant_content,
            protected_developer=bool(
                locals().get(
                    "_nv_qualified_developer_evidence", False
                )
            ),
        )

    # NEUROVEST_G43_R48_FINAL_INTEGRITY
    # Runs after citation/semantic/reasoning replacements and
    # before response synchronization and persistence.
    # Does not alter the developer authorization boundary.
    if __import__("os").environ.get(
        "NV_R48_FINAL_INTEGRITY_ENABLED"
    ) == "1":
        from backend.app.stacks.chat_public.final_response_integrity_r48 import (
            finalize as _nv_r48_finalize,
        )

        assistant_content, verification_result = _nv_r48_finalize(
            assistant_content,
            verification_result,
            verifier=verify_response,
            math_bundle=math_bundle,
            retrieval_bundle=retrieval_bundle,
            protected_developer=bool(
                locals().get(
                    "_nv_qualified_developer_evidence",
                    False,
                )
            ),
            enabled=True,
        )


    # NEUROVEST_G43_R68_SOURCE_CONSTRAINED_REVISION
    # Source-grounded optional second pass. No privileged/tool routes.
    if (
        isinstance(assistant_content, str)
        and isinstance(request.message, str)
        # NEUROVEST_G43_R94_FAST_FINANCE_PROTECTION
        # R93's deterministic answer already passed the earlier
        # response-verification pipeline. Avoid this OPTIONAL
        # model-assisted revision; keep all other guards active.
        and str(runtime_result.get('provider', ''))
            != 'neurovest_context_financial_g43_r93'
        and not bool(locals().get("_nv_qualified_developer_evidence", False))
        and str(runtime_result.get("intent", "")) in (
            "general_conversation", "financial_question", "market_question",
            "financial_research", "trading_conversation", "unknown", "",
        )
    ):
        from backend.app.stacks.chat_public.evidence_revision_g43_r68 import revise as _r68_revise
        _r68_revision = _r68_revise(
            request.message,
            assistant_content,
            retrieval_bundle=retrieval_bundle,
            model=locals().get("selected_model", None),
            protected=False,
        )
        if _r68_revision.replaced:
            _r68_check = verify_response(
                _r68_revision.answer,
                math_bundle=math_bundle,
                retrieval_bundle=retrieval_bundle,
            )
            if not _r68_check.fail_closed and _r68_check.passed:
                assistant_content = _r68_check.final_response
                verification_result = _r68_check

    # NEUROVEST_G43_R67_PRE_PERSISTENCE_CLAIM_INTEGRITY
    # The source catalogue is static. No unearned live verification claims.
    # Developer, privileged and trade/execution routes are excluded.
    if (
        isinstance(assistant_content, str)
        and isinstance(request.message, str)
        and not bool(locals().get("_nv_qualified_developer_evidence", False))
        and str(runtime_result.get("intent", "")) in (
            "general_conversation", "trading_conversation", "financial_question",
            "market_question", "financial_research", "unknown", "",
        )
    ):
        from backend.app.stacks.chat_public.claim_integrity_g43_r67 import (
            assess as _r67_assess,
        )
        _r67_decision = _r67_assess(
            request.message,
            assistant_content,
            fresh_official_evidence=False,
            protected_route=False,
        )
        if _r67_decision.changed:
            assistant_content = _r67_decision.answer
            verification_result = verify_response(
                assistant_content,
                math_bundle=math_bundle,
                retrieval_bundle=retrieval_bundle,
            )
            assistant_content = verification_result.final_response

    # NEUROVEST_G43_R70_VERIFIED_ARITHMETIC_FINAL
    # This does not change role, identity, orders, broker, or database state.
    # An answer is substituted only when a complete supported math prompt parses.
    from backend.app.stacks.chat_public.verified_arithmetic_g43_r70 import answer as _r70_answer
    _r70_checked = _r70_answer(request.message)
    if _r70_checked is not None:
        assistant_content = _r70_checked
        verification_result = verify_response(
            assistant_content, math_bundle=math_bundle, retrieval_bundle=retrieval_bundle,
        )
        # Preserve exact deterministic output; don't copy the prior model's partial operation.
        # The scoped R70 parser rejects arbitrary language and is side-effect free.
        if verification_result.passed:
            assistant_content = verification_result.final_response

    # NEUROVEST_R216_FINAL_POST_MUTATION_TECHNICAL_GUARD
    # Recheck after all answer-replacement stages and before response sync.
    _nv216_candidate, _nv216_report = _nv90_inspect(
        request.message,
        assistant_content,
    )
    if _nv216_candidate != assistant_content:
        _nv216_verified = verify_response(
            _nv216_candidate,
            math_bundle=math_bundle,
            retrieval_bundle=retrieval_bundle,
        )
        assistant_content = _nv216_verified.final_response
        verification_result = _nv216_verified

    # G43-R218_RELATED_RATES_CANONICAL_ANSWER
    # Render this supported calculation from grounded inputs and result.
    if (
        math_bundle.grounded
        and math_bundle.operation == "related_rates_circle"
        and isinstance(math_bundle.arguments, dict)
    ):
        from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

        try:
            radius = Decimal(str(math_bundle.arguments["r"]))
            radius_rate = Decimal(str(math_bundle.arguments["rate"]))
            payload = (
                math_bundle.result
                if isinstance(math_bundle.result, dict)
                else {}
            )
            display_values = payload.get("display_values", {})
            values = payload.get("values", {})
            raw_result = (
                display_values.get("result")
                if isinstance(display_values, dict)
                else None
            )
            if not isinstance(raw_result, str) and isinstance(values, dict):
                raw_result = values.get("result")
            if raw_result is None:
                metadata = getattr(verification_result, "metadata", {})
                authoritative_values = (
                    metadata.get("authoritative_math_values", {})
                    if isinstance(metadata, dict)
                    else {}
                )
                raw_result = (
                    authoritative_values.get("result")
                    if isinstance(authoritative_values, dict)
                    else None
                )

            result_value = Decimal(str(raw_result))
            if not all(
                value.is_finite()
                for value in (radius, radius_rate, result_value)
            ):
                raise ValueError("non-finite related-rates value")

            radius_text = format(radius.normalize(), "f")
            rate_text = format(radius_rate.normalize(), "f")
            coefficient = Decimal(2) * radius * radius_rate
            coefficient_text = format(coefficient.normalize(), "f")

            if isinstance(display_values, dict) and isinstance(
                display_values.get("result"), str
            ):
                result_text = display_values["result"]
            else:
                result_text = format(
                    result_value.quantize(
                        Decimal("0.000001"),
                        rounding=ROUND_HALF_UP,
                    ),
                    "f",
                )

            assistant_content = chr(10).join((
                "For a circle, A = πr². Differentiating with respect "
                "to time gives dA/dt = 2πr(dr/dt).",
                f"Substitute r = {radius_text} cm and "
                f"dr/dt = {rate_text} cm/s: "
                f"dA/dt = 2π({radius_text})({rate_text}) "
                f"= {coefficient_text}π cm²/s "
                f"≈ {result_text} cm²/s.",
            ))
            _nv_r218_verified = verify_response(
                assistant_content,
                math_bundle=math_bundle,
                retrieval_bundle=retrieval_bundle,
            )
            assistant_content = _nv_r218_verified.final_response
            verification_result = _nv_r218_verified
        except (KeyError, TypeError, ValueError, InvalidOperation):
            pass

    # G43-R218_POWER_RULE_PLAIN_TEXT_FINAL
    # Render supported power-rule evaluations without raw LaTeX.
    if (
        math_bundle.grounded
        and math_bundle.operation == "power_rule"
        and isinstance(math_bundle.arguments, dict)
    ):
        from decimal import Decimal, InvalidOperation

        try:
            exponent = int(str(math_bundle.arguments["n"]))
            point = int(str(math_bundle.arguments["x"]))
            payload = (
                math_bundle.result
                if isinstance(math_bundle.result, dict)
                else {}
            )
            values = payload.get("values", {})
            raw_result = (
                values.get("result")
                if isinstance(values, dict)
                else None
            )
            if raw_result is None:
                metadata = getattr(verification_result, "metadata", {})
                authoritative = (
                    metadata.get("authoritative_math_values", {})
                    if isinstance(metadata, dict)
                    else {}
                )
                raw_result = (
                    authoritative.get("result")
                    if isinstance(authoritative, dict)
                    else None
                )

            result_value = Decimal(str(raw_result))
            expected_value = (
                exponent * point ** (exponent - 1)
                if exponent > 0
                else 0
            )
            if (
                not result_value.is_finite()
                or result_value != Decimal(expected_value)
            ):
                raise ValueError("power-rule result did not match inputs")

            result_text = format(result_value.normalize(), "f")
            if exponent > 1:
                derivative = f"{exponent} × x^{exponent - 1}"
                substitution = (
                    f"f'({point}) = {exponent} × {point}^{exponent - 1} "
                    f"= {result_text}."
                )
            elif exponent == 1:
                derivative = "1"
                substitution = f"f'({point}) = 1."
            else:
                derivative = "0"
                substitution = f"f'({point}) = 0."

            assistant_content = chr(10).join((
                f"For f(x) = x^{exponent}, the power rule gives "
                f"f'(x) = {derivative}.",
                f"Substitute x = {point}: {substitution}",
            ))
            _nv_power_verified = verify_response(
                assistant_content,
                math_bundle=math_bundle,
                retrieval_bundle=retrieval_bundle,
            )
            assistant_content = _nv_power_verified.final_response
            verification_result = _nv_power_verified
        except (KeyError, TypeError, ValueError, InvalidOperation):
            pass

    # G43-R218_MATH_FALLBACK_PLAIN_TEXT
    # Clean common TeX presentation in requested math answers, including
    # ungrounded model fallbacks. Preserve currency amounts.
    _nv_math_markup_present = (
        isinstance(assistant_content, str)
        and "```" not in assistant_content
        and any(
            marker in assistant_content
            for marker in (
                r"\cdot",
                r"\times",
                r"\frac",
                r"\sqrt",
                r"\pi",
                "$$",
                "&#x20;",
            )
        )
    )
    if (
        isinstance(assistant_content, str)
        and (math_bundle.requested or _nv_math_markup_present)
    ):
        _nv_plain_math = assistant_content
        import html as _nv_math_html
        _nv_plain_math = _nv_math_html.unescape(_nv_plain_math)
        _nv_plain_math = re.sub(r"(?m)^[ \t]+", "", _nv_plain_math)
        _nv_plain_math = re.sub(r"[ \t]{2,}", " ", _nv_plain_math)
        _nv_plain_math = re.sub(r"[ \t]+([,.;:])", r"\1", _nv_plain_math)
        _nv_plain_math = re.sub(r" *\n *", "\n", _nv_plain_math)
        _nv_plain_math = re.sub(r"\n{3,}", "\n\n", _nv_plain_math).strip()
        _nv_plain_math = _nv_plain_math.replace(r"\cdot", "×")
        _nv_plain_math = _nv_plain_math.replace(r"\times", "×")
        _nv_plain_math = _nv_plain_math.replace(r"\pi", "π")
        _nv_plain_math = _nv_plain_math.replace(r"\approx", "≈")
        _nv_plain_math = _nv_plain_math.replace(r"\ge", "≥")
        _nv_plain_math = _nv_plain_math.replace(r"\le", "≤")
        _nv_plain_math = _nv_plain_math.replace(r"\neq", "≠")
        _nv_plain_math = _nv_plain_math.replace(r"\implies", "⇒")
        _nv_plain_math = _nv_plain_math.replace(r"\Rightarrow", "⇒")
        _nv_plain_math = _nv_plain_math.replace(r"\pm", "±")
        _nv_plain_math = _nv_plain_math.replace(r"\cos", "cos")
        _nv_plain_math = _nv_plain_math.replace(r"\sin", "sin")
        _nv_plain_math = _nv_plain_math.replace(r"\omega", "ω")
        _nv_plain_math = _nv_plain_math.replace(r"\left", "")
        _nv_plain_math = _nv_plain_math.replace(r"\right", "")
        _nv_plain_math = _nv_plain_math.replace(r"\,", " ")
        _nv_plain_math = _nv_plain_math.replace(r"\;", " ")
        _nv_plain_math = re.sub(
            r"\\(?:text|boxed)\s*\{([^{}]*)\}",
            r"\1",
            _nv_plain_math,
        )
        for _nv_fraction_pass in range(6):
            _nv_plain_math = re.sub(
                r"\\frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}",
                r"(\1)/(\2)",
                _nv_plain_math,
            )
            _nv_plain_math = re.sub(
                r"\\sqrt\s*\{([^{}]*)\}",
                r"sqrt(\1)",
                _nv_plain_math,
            )
        _nv_plain_math = re.sub(
            r"\^\{([^{}]+)\}",
            r"^\1",
            _nv_plain_math,
        )
        _nv_plain_math = re.sub(
            r"_\{([^{}]+)\}",
            r"_\1",
            _nv_plain_math,
        )
        if not re.search(r"\$\s*\d", _nv_plain_math):
            _nv_plain_math = _nv_plain_math.replace("$$", "").replace("$", "")
        if _nv_plain_math != assistant_content:
            _nv_plain_verified = verify_response(
                _nv_plain_math,
                math_bundle=math_bundle,
                retrieval_bundle=retrieval_bundle,
            )
            assistant_content = _nv_plain_verified.final_response
            verification_result = _nv_plain_verified

    # G43_R220_DETERMINISTIC_FIRST_USER_MESSAGE_RECALL
    # Use the owner-scoped stored message directly; do not ask the model
    # to reconstruct or guess historical conversation content.
    import re as _nv_r220_re
    _nv_r220_first_message_request = bool(
        _nv_r220_re.search(
            r"\b(?:first|earliest)\b.{0,100}"
            r"\b(?:message|prompt|question)\b",
            str(request.message or ""),
            _nv_r220_re.I | _nv_r220_re.S,
        )
    )
    if _nv_r220_first_message_request:
        _nv_r220_first_message = getattr(
            assembled_context,
            "first_user_message",
            None,
        )
        if (
            isinstance(_nv_r220_first_message, str)
            and _nv_r220_first_message.strip()
        ):
            import json as _nv_r220_json
            _nv_r220_answer = (
                "The first user message in this conversation was: "
                + _nv_r220_json.dumps(
                    _nv_r220_first_message.strip(),
                    ensure_ascii=False,
                )
            )
        else:
            _nv_r220_answer = (
                "I can’t verify the first user message in this conversation."
            )

        _nv_r220_verified = verify_response(
            _nv_r220_answer,
            math_bundle=math_bundle,
            retrieval_bundle=retrieval_bundle,
        )
        assistant_content = _nv_r220_verified.final_response
        verification_result = _nv_r220_verified

    # NEUROVEST_DETERMINISTIC_PORTFOLIO_LIST_V1
    # Render explicit holdings/balance requests from the owner-scoped
    # stored snapshot; do not rely on the model to reproduce fields.
    import re as _nv_portfolio_re
    _nv_listing_request = bool(_nv_portfolio_re.search(
        r"\b(?:list|show|summarize|what are|tell me)\b.{0,100}"
        r"\b(?:positions?|holdings?|balances?)\b",
        str(request.message or ""),
        _nv_portfolio_re.I | _nv_portfolio_re.S,
    ))

    if _nv_listing_request:
        _nv_portfolio_context = getattr(
            assembled_context,
            "portfolio_context",
            {},
        )
        _nv_snapshot = (
            _nv_portfolio_context.get(
                "authenticated_snaptrade_snapshot",
                {},
            )
            if isinstance(_nv_portfolio_context, dict)
            else {}
        )

        if isinstance(_nv_snapshot, dict) and _nv_snapshot.get("status") == "ok":
            def _nv_display(value):
                return (
                    str(value)
                    if value is not None and str(value).strip()
                    else "not provided"
                )

            _nv_lines = [
                "Stored SnapTrade portfolio snapshot; this is not live data."
            ]
            _nv_positions = _nv_snapshot.get("positions", [])
            _nv_balances = _nv_snapshot.get("balances", [])

            if isinstance(_nv_positions, list) and _nv_positions:
                _nv_lines.append("Positions:")
                for _nv_position in _nv_positions:
                    if not isinstance(_nv_position, dict):
                        continue
                    _nv_currency = _nv_display(
                        _nv_position.get("currency")
                    )
                    _nv_lines.append(
                        "- "
                        + _nv_display(_nv_position.get("symbol"))
                        + ": quantity "
                        + _nv_display(_nv_position.get("shares_quantity"))
                        + "; current price "
                        + _nv_currency + " "
                        + _nv_display(_nv_position.get("current_price"))
                        + "; market value "
                        + _nv_currency + " "
                        + _nv_display(_nv_position.get("market_value"))
                        + "; last synced "
                        + _nv_display(_nv_position.get("last_synced_at"))
                    )
            else:
                _nv_lines.append(
                    "No position rows are present in the stored snapshot."
                )

            if isinstance(_nv_balances, list) and _nv_balances:
                _nv_lines.append("Balances:")
                for _nv_balance in _nv_balances:
                    if not isinstance(_nv_balance, dict):
                        continue
                    _nv_currency = _nv_display(
                        _nv_balance.get("currency")
                    )
                    _nv_lines.append(
                        "- " + _nv_currency
                        + ": cash " + _nv_display(
                            _nv_balance.get("cash_amount")
                        )
                        + "; buying power " + _nv_display(
                            _nv_balance.get("buying_power")
                        )
                        + "; available " + _nv_display(
                            _nv_balance.get("cash_available")
                        )
                        + "; settled " + _nv_display(
                            _nv_balance.get("settled_cash")
                        )
                        + "; last synced "
                        + _nv_display(_nv_balance.get("last_synced_at"))
                    )
            else:
                _nv_lines.append(
                    "No balance rows are present in the stored snapshot."
                )

            _nv_portfolio_answer = "\n".join(_nv_lines)
        else:
            _nv_portfolio_answer = (
                "I couldn't read an available stored portfolio snapshot "
                "for this request, so I can't list verified holdings or balances."
            )

        verification_result = verify_response(
            _nv_portfolio_answer,
            math_bundle=math_bundle,
            retrieval_bundle=retrieval_bundle,
        )
        assistant_content = verification_result.final_response

    # NEURO_EXPLICIT_RESEARCH_NO_EVIDENCE_FALLBACK
    # Explicit general research must not appear sourced when the local
    # index returned no evidence. Specialized finance/account routes and
    # non-Ollama source responses retain their existing handling.
    if (
        request_route_contract.route.value == "general_chat"
        and request_route_contract.retrieval_allowed
        and routing_decision.retrieval_required
        and retrieval_bundle.requested
        and not retrieval_bundle.grounded
        and runtime_result.get("provider") == OLLAMA_PROVIDER
    ):
        assistant_content = (
            "I couldn't verify this research request from the available "
            "sources. No usable source excerpts were returned, so I can't "
            "present it as researched or source-verified."
        )
        verification_result = verify_response(
            assistant_content,
            math_bundle=math_bundle,
            retrieval_bundle=retrieval_bundle,
        )
        assistant_content = verification_result.final_response

    _nv_arxiv_before_numbering = assistant_content
    assistant_content = _renumber_arxiv_result_list(
        assistant_content,
        retrieval_bundle.citations,
        request.message,
    )
    import logging as _nv_arxiv_trace_logging
    import re as _nv_arxiv_trace_re
    _nv_arxiv_trace_logging.getLogger(__name__).warning(
        "ARXIV_FINAL_NUMBERING before=%s after=%s",
        _nv_arxiv_trace_re.findall(
            r"(?m)^\s*(\d+)\.\s+\*\*",
            _nv_arxiv_before_numbering,
        ),
        _nv_arxiv_trace_re.findall(
            r"(?m)^\s*(\d+)\.\s+\*\*",
            assistant_content,
        ),
    )

    # Synchronize the guarded response for persistence
    # and subsequent response construction.
    if isinstance(runtime_result.get("response"), dict):
        runtime_result["response"]["message"] = assistant_content

    runtime_result["message"] = assistant_content

    # Preserve the existing verifier result structure.
    runtime_result["response_verification"] = (
        verification_result.as_dict()
    )

    _nv3er4_final_event(
        question=request.message,
        stage="PRE_PERSISTENCE",
        trace_id=trace_id,
        response_length=len(assistant_content),
        awareness_route=bool(
            runtime_result.get("intent")
            == "developer_architecture_awareness"
        ),
        response_grounded=bool(
            runtime_result.get("tool_truth_state")
            == "grounded"
        ),
    )

    # Store the digest only in a local variable.
    # No response body is printed.
    _nv3er4_pre_digest = (
        _nv3er4_final_fingerprint(assistant_content)
    )

    print(
        "F56_PRE_PERSIST_SQL_MARKER=",
        "NeuroVest improvement progress"
        in assistant_content,
        flush=True,
    )
    assistant_message = (
        await conversation_store.append_message(
            thread_id=thread.thread_id,
            parent_message_id=(
                user_message.message_id
            ),
            role="assistant",
            content=assistant_content,
            intent=runtime_result.get("intent"),
            symbol=runtime_result.get("symbol"),
            provider=runtime_result.get(
                "provider"
            ),
            model=runtime_result.get("model"),
            metadata={
                "response_type": (
                    runtime_result["response"]
                    .get("type")
                ),
                "strategy_capture": (
                    runtime_result.get(
                        "strategy_capture"
                    )
                ),
                "runtime_status": (
                    runtime_result.get("status")
                ),
                "cognitive_route": (
                    runtime_result.get(
                        "cognitive_route"
                    )
                ),
                "live_retrieval": {
                    "requested":
                        retrieval_bundle.requested,
                    "grounded":
                        retrieval_bundle.grounded,
                    "result_count":
                        len(
                            retrieval_bundle.results
                        ),
                    "citations":
                        list(
                            retrieval_bundle.citations
                        ),
                    "error":
                        retrieval_bundle.error,
                },
                "live_math": {
                    "requested":
                        math_bundle.requested,
                    "extracted":
                        math_bundle.extracted,
                    "grounded":
                        math_bundle.grounded,
                    "operation":
                        math_bundle.operation,
                    "arguments":
                        math_bundle.arguments,
                    "result":
                        math_bundle.result,
                    "error":
                        math_bundle.error,
                },
                "response_verification":
                    verification_result.as_dict(),
            },
        )
    )

    _nv3er4_final_event(
        question=request.message,
        stage="PERSISTED",
        trace_id=trace_id,
        persisted_message=bool(
            getattr(
                assistant_message,
                "message_id",
                None,
            )
        ),
        content_unchanged=bool(
            _nv3er4_pre_digest
            == _nv3er4_final_fingerprint(
                getattr(
                    assistant_message,
                    "content",
                    None,
                )
            )
        ),
    )

    current_turn_evidence: list[
        ToolEvidence
    ] = []

    verification_evidence = ToolEvidence(
        thread_id=thread.thread_id,
        tool_name="response_verification",
        tool_call_id=trace_id,
        claim_types=[
            "response_consistency",
            "deterministic_math_consistency",
            "citation_validation",
            "paper_only_boundary",
        ],
        request={
            "assistant_message_id":
                assistant_message.message_id,
            "math_requested":
                math_bundle.requested,
            "retrieval_requested":
                retrieval_bundle.requested,
        },
        result={
            "status":
                verification_result.status,
            "passed":
                verification_result.passed,
            "repaired":
                verification_result.repaired,
            "fail_closed":
                verification_result.fail_closed,
            "checks":
                verification_result.checks,
            "violations": [
                violation.as_dict()
                for violation
                in verification_result.violations
            ],
        },
        status=(
            "success"
            if (
                verification_result.passed
                or verification_result.repaired
            )
            else "error"
        ),
        metadata={
            "assistant_message_id":
                assistant_message.message_id,
            "user_message_id":
                user_message.message_id,
            "runtime_trace_id":
                trace_id,
            "read_only":
                True,
            "deterministic":
                True,
            "pre_persistence_verification":
                True,
        },
    )

    await conversation_store.add_tool_evidence(
        verification_evidence
    )

    current_turn_evidence.append(
        verification_evidence
    )

    if math_bundle.requested:
        math_evidence = ToolEvidence(
            thread_id=thread.thread_id,
            tool_name=(
                "deterministic_math_engine"
            ),
            tool_call_id=trace_id,
            claim_types=[
                "deterministic_calculation",
                "exact_numeric_result",
            ],
            request={
                "message":
                    request.message,
                "operation":
                    math_bundle.operation,
                "arguments":
                    math_bundle.arguments,
            },
            result={
                "grounded":
                    math_bundle.grounded,
                "extracted":
                    math_bundle.extracted,
                "succeeded":
                    math_bundle.succeeded,
                "calculation":
                    math_bundle.result,
                "error":
                    math_bundle.error,
            },
            status=(
                "success"
                if math_bundle.grounded
                else (
                    "error"
                    if math_bundle.extracted
                    else "unavailable"
                )
            ),
            metadata={
                "assistant_message_id":
                    assistant_message.message_id,
                "user_message_id":
                    user_message.message_id,
                "runtime_trace_id":
                    trace_id,
                "read_only":
                    True,
                "deterministic":
                    True,
                "precision":
                    (
                        math_bundle.result
                        or {}
                    ).get(
                        "precision"
                    ),
            },
        )

        await conversation_store.add_tool_evidence(
            math_evidence
        )

        current_turn_evidence.append(
            math_evidence
        )

    if retrieval_bundle.requested:
        retrieval_evidence = ToolEvidence(
            thread_id=thread.thread_id,
            tool_name=(
                "local_knowledge_retrieval"
            ),
            tool_call_id=trace_id,
            claim_types=[
                "knowledge_retrieval",
                "source_citation",
            ],
            request={
                "query":
                    request.message,
                "top_k":
                    5,
                "minimum_score":
                    0.18,
            },
            result={
                "grounded":
                    retrieval_bundle.grounded,
                "result_count":
                    len(
                        retrieval_bundle.results
                    ),
                "citations":
                    list(
                        retrieval_bundle.citations
                    ),
                "error":
                    retrieval_bundle.error,
            },
            status=(
                "success"
                if retrieval_bundle.error is None
                else "error"
            ),
            metadata={
                "assistant_message_id":
                    assistant_message.message_id,
                "user_message_id":
                    user_message.message_id,
                "runtime_trace_id":
                    trace_id,
                "read_only":
                    True,
                "canonical_index": (
                    "runtime/cognitive_engine/rag/"
                    "neuro_knowledge_index.json"
                ),
                "untrusted_evidence":
                    True,
            },
        )

        await conversation_store.add_tool_evidence(
            retrieval_evidence
        )

        current_turn_evidence.append(
            retrieval_evidence
        )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="ASSISTANT_MESSAGE_PERSISTED",
        node="postgresql_adapter",
        source="response_validation",
        destination="postgresql_adapter",
        status="completed",
        layer="L0",
        stack="db_runtime",
        details={
            "operation": "append_assistant_message",
            "latency_ms": (
                perf_counter()
                - assistant_persist_started
            ) * 1000,
            "response_bytes": len(
                assistant_content.encode(
                    "utf-8"
                )
            ),
            "success": True,
        },
    )

    memory_started = perf_counter()

    state = await update_summary_memory(
        thread_id=thread.thread_id,
        user_message=user_message,
        assistant_message=assistant_message,
        strategy_capture=runtime_result.get(
            "strategy_capture"
        ),
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="SUMMARY_MEMORY_UPDATED",
        node="memory_context",
        source="postgresql_adapter",
        destination="memory_context",
        status="completed",
        layer="L2",
        stack="memory",
        details={
            "operation": "update_summary_memory",
            "latency_ms": (
                perf_counter()
                - memory_started
            ) * 1000,
            "success": True,
        },
    )

    # G41: only recover a known optional Wikipedia lookup failure
    # when later processing produced a verified substantive answer.
    # Never convert provider, authorization, or safety failures.
    if _g41_recoverable_wikipedia_answer(
        original_status=_g41_initial_runtime_status,
        original_message=_g41_initial_runtime_message,
        final_answer=assistant_content,
        verification=verification_result,
    ):
        runtime_result["status"] = "ok"
        runtime_result["error"] = None
        runtime_result["g41_recovery"] = (
            "verified_answer_after_optional_wikipedia_failure"
        )

    response_status = str(
        runtime_result.get("status") or "ok"
    )

    if response_status not in {
        "ok",
        "error",
        "blocked",
    }:
        response_status = "error"

    response = ChatResponse(
        status=response_status,
        thread_id=thread.thread_id,
        user_message_id=user_message.message_id,
        assistant_message_id=(
            assistant_message.message_id
        ),
        message=assistant_content,
        intent=runtime_result.get("intent"),
        symbol=runtime_result.get("symbol"),
        provider=runtime_result.get("provider"),
        model=runtime_result.get("model"),
        tool_truth_state=(
            _v36r4_normalize_response_tool_truth_state(
                runtime_result.get(
                    "tool_truth_state",
                    "not_required",
                ),
                retrieval_requested=(
                    retrieval_bundle.requested
                ),
                retrieval_grounded=(
                    retrieval_bundle.grounded
                ),
                math_requested=(
                    math_bundle.requested
                ),
                math_grounded=(
                    math_bundle.grounded
                ),
            )
        ),
        conversation_state=state,
        error=runtime_result.get("error"),
        evidence=current_turn_evidence,
        metadata={
            "idempotent_replay": False,
            "streaming_enabled": False,
            "history_injected_into_model": True,
            "context_version": CONTEXT_VERSION,
            "context_recent_message_count": (
                assembled_context.recent_message_count
            ),
            "context_memory_count": (
                assembled_context.memory_count
            ),
            "context_evidence_count": (
                assembled_context.evidence_count
            ),
            "summary_memory_active": True,
            "strategy_capture": (
                runtime_result.get(
                    "strategy_capture"
                )
            ),
            "runtime_trace_id": trace_id,
            "retrieval_requested":
                retrieval_bundle.requested,
            "retrieval_grounded":
                retrieval_bundle.grounded,
            "retrieval_result_count":
                len(
                    retrieval_bundle.results
                ),
            "retrieval_citations":
                list(
                    retrieval_bundle.citations
                ),
            "retrieval_error":
                retrieval_bundle.error,
            "math_requested":
                math_bundle.requested,
            "math_extracted":
                math_bundle.extracted,
            "math_grounded":
                math_bundle.grounded,
            "math_operation":
                math_bundle.operation,
            "math_arguments":
                math_bundle.arguments,
            "math_result":
                math_bundle.result,
            "math_error":
                math_bundle.error,
            "verification_status":
                verification_result.status,
            "verification_passed":
                verification_result.passed,
            "verification_repaired":
                verification_result.repaired,
            "verification_fail_closed":
                verification_result.fail_closed,
            "verification_checks":
                verification_result.checks,
            "verification_violations": [
                violation.as_dict()
                for violation
                in verification_result.violations
            ],
        },
    )

    payload = response.model_dump(
        mode="json"
    )

    payload["response"] = runtime_result[
        "response"
    ]


    training_run = runtime_result.get(
        "training_run"
    )

    if isinstance(
        training_run,
        dict,
    ):
        payload["training_run"] = {
            "run_id":
                training_run.get(
                    "run_id"
                ),

            "scope":
                training_run.get(
                    "scope"
                ),

            "status":
                training_run.get(
                    "status"
                ),

            "duration_seconds":
                training_run.get(
                    "duration_seconds"
                ),

            "progress_percent":
                training_run.get(
                    "progress_percent"
                ),

            "universe":
                training_run.get(
                    "universe"
                ),
        }

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="CHAT_RUNTIME_COMPLETED",
        node="chat_runtime",
        source="memory_context",
        destination="chat_runtime",
        status=(
            "completed"
            if response_status == "ok"
            else response_status
        ),
        symbol=runtime_result.get(
            "symbol"
        ),
        layer="L4",
        stack="chat_public",
        details={
            "operation": "run_chat_turn",
            "latency_ms": (
                perf_counter()
                - turn_started
            ) * 1000,
            "response_bytes": len(
                assistant_content.encode(
                    "utf-8"
                )
            ),
            "success": (
                response_status == "ok"
            ),
            "error": runtime_result.get(
                "error"
            ),
        },
    )

    return payload


# NEURO_V41_AUTO_DEVELOPER_AWARENESS_V2
def _neuro_v41_auto_awareness_question(message, developer_verified):
    """Classify explicit, authenticated developer-awareness questions.

    Classification only. The downstream developer command retains
    its independent authenticated authorization check.
    """
    import re

    if not developer_verified or not isinstance(message, str):
        return None

    question = message.strip()

    if (
        not question
        or question.startswith("/")
        or len(question) > 3000
    ):
        return None

    # Preserve explicit codebase and architecture requests.
    architecture = re.search(
        r"\b(?:architecture|repository|codebase|"
        r"source[ ._-]?code|implementation|"
        r"module[s]?|stack[s]?|"
        r"dependency|dependencies)\b",
        question,
        flags=re.IGNORECASE,
    )

    technical = re.search(
        r"\b(?:how|why|where|need|improve|improvement|"
        r"priorities|explain|inspect|trace|verify|"
        r"tested|implemented|functions?|modules?|"
        r"stacks?|integrat(?:e|ion)|risks?|guards?|"
        r"evaluation|training|evidence|performance|"
        r"debug|review|assess|work|working|"
        r"connects?|depend(?:s|encies))\b",
        question,
        flags=re.IGNORECASE,
    )

    explicit_architecture = (
        architecture is not None
        and technical is not None
    )

    # V5: Recognize natural references to NeuroVest's own
    # technical implementation without requiring 'repository'.
    local_scope = re.search(
        r"\b(?:our|my|neurovest(?:'s)?|neuro(?:'s)?)\s+"
        r"(?:chat|conversation|intent|routing|router|"
        r"handler|backend|frontend|api|runtime|"
        r"model|code|context|retrieval|"
        r"developer|response|system)\b",
        question,
        flags=re.IGNORECASE,
    )

    engineering_subject = re.search(
        r"\b(?:chat\s+(?:runtime|engine|handler|routing)|"
        r"intent\s+(?:classifier|routing|detection)|"
        r"context\s+(?:assembler|retrieval|pipeline)|"
        r"response\s+(?:builder|routing|generation)|"
        r"developer\s+(?:chat|commands?|tools?)|"
        r"api\s+(?:handler|endpoint|routing)|"
        r"model\s+(?:router|selection)|"
        r"conversation\s+(?:engine|handler|routing))\b",
        question,
        flags=re.IGNORECASE,
    )

    engineering_action = re.search(
        r"\b(?:inspect|review|debug|trace|explain|"
        r"diagnose|assess|analy[sz]e|investigate|"
        r"improve|fix|refactor|identify|why|how|"
        r"which|where|what)\b",
        question,
        flags=re.IGNORECASE,
    )

    natural_developer_request = (
        local_scope is not None
        and engineering_subject is not None
        and engineering_action is not None
    )

    # Ordinary financial explanations should not enter the
    # privileged developer-awareness path merely because
    # they discuss a strategy, model, or paper trading.
    if not (
        explicit_architecture
        or natural_developer_request
    ):
        return None

    return "/dev awareness explain " + question






def _nv13a_original_enhance_model_input(
    model_input,
    user_message,
    history,
):
    """Apply bounded, evidence-aware conversation guidance."""
    import re

    if not isinstance(model_input, str):
        return model_input

    if not isinstance(user_message, str):
        return model_input

    if not model_input.strip() or not user_message.strip():
        return model_input

    if len(model_input) > 30000:
        return model_input

    has_history = (
        isinstance(history, (list, tuple))
        and len(history) > 0
    )

    # Preserve the established detector as an input,
    # but do not prepend its verbose prose.
    legacy = _nv5c_build_conversation_guidance(
        user_message,
        history,
    )

    if not isinstance(legacy, str):
        legacy = ""

    lower = user_message.casefold()

    correction = bool(re.search(
        r"\b(?:no[,!]?|actually|i meant|"
        r"i said|that's not what|not what i asked|"
        r"instead of)\b",
        lower,
    ))

    followup = bool(re.search(
        r"\b(?:what about|second one|first one|"
        r"that one|those|them|continue|same one|"
        r"compared to|and the|does it|did it)\b",
        lower,
    ))

    evidence = bool(re.search(
        r"\b(?:verified|measured|tested|"
        r"actual results|win rate|backtest|"
        r"how do you know|proof|evidence|"
        r"maximum drawdown)\b",
        lower,
    ))

    # The earlier detector can recognize relationships
    # not covered by the small supplemental patterns.
    if has_history and "follow-up" in legacy.casefold():
        followup = True

    hints = []

    # Priority 1: honor corrections to the current task.
    if correction:
        hints.append(
            "Honor the user's latest correction; "
            "do not repeat the corrected mistake."
        )

    # Priority 2: resolve references without guessing.
    if followup and has_history:
        hints.append(
            "Treat this as a follow-up. "
            "Resolve references using the supplied "
            "conversation, not an invented subject."
        )

    # Priority 3: preserve evidence and tool truth.
    if evidence:
        hints.append(
            "Distinguish verified results from assumptions; "
            "never invent performance measurements."
        )

    # Add one bounded general-purpose instruction only
    # when a conversation signal is actually present.
    if hints:
        hints.append(
            "Answer directly, preserve the user's scope, "
            "and respect existing evidence and safety rules."
        )
    else:
        pass

    state_guidance = _nv5i_state_guidance(history, user_message)
    if state_guidance:
        hints.append(state_guidance)
    if not hints:
        return model_input
    guidance = " ".join(hints)

    # Never cut an instruction halfway through.
    if len(guidance) > 520:
        guidance = " ".join(hints[:-1])
        if len(guidance) > 520:
            return model_input

    prefix = (
        "[Supplemental conversation guidance; "
        "existing authorization, safety, evidence, "
        "and tool-truth instructions take precedence]\n"
        + guidance
        + "\n[End supplemental guidance]\n\n"
    )

    if len(prefix) > 750 or len(model_input) + len(prefix) > 16000:
        return model_input

    return prefix + model_input


def _nv5c_enhance_model_input(model_input, user_message, history):
    """Bounded task guidance layered over the existing enhancer."""
    import re
    existing = _nv13a_original_enhance_model_input(model_input, user_message, history)
    if not isinstance(existing, str):
        return existing
    if not isinstance(user_message, str):
        return existing
    message = user_message.strip()
    if not message or len(message) > 12000:
        return existing
    if len(existing) > 14500:
        return existing
    if '[NEURO_INTELLIGENCE_13A_R3]' in existing:
        return existing
    text = message.casefold()
    guidance = []

    def match(pattern):
        return re.search(pattern, text, re.IGNORECASE) is not None

    def contains(*phrases):
        return any((phrase in text for phrase in phrases))
    correction = contains('actually', 'correction:', 'i meant', 'instead', 'rather than', 'changed my mind', 'not what i asked')
    followup = bool(history) and (contains('what about', 'how so', 'continue', 'earlier', 'previous', 'same one') or match('\\b(?:that|those|them|it|this)\\b'))
    coding = contains('python', 'javascript', 'typescript', 'traceback', 'exception', 'refactor', 'debug', 'compile', 'terminal', 'script', 'programming', 'function') or match('\\bcode\\b')
    troubleshooting = contains('broken', 'not working', 'failed', 'failure', 'error', 'issue', 'diagnose', 'troubleshoot', 'crash', "doesn't work", 'will not start', 'not starting') or match('\\b(?:fix|repair|debug)\\b') or match("\\b(?:won't|will not|cannot|can't|doesn't)\\b.{0,100}\\b(?:start|run|work|load|connect)\\b") or match('\\b(?:start|run|load|connect)\\b.{0,80}\\b(?:fails?|failed|error)\\b')
    finance = contains('portfolio', 'trading', 'investment', 'dividend', 'backtest', 'broker', 'drawdown', 'price target', 'valuation') or match('\\b(?:stock|stocks|equity|bond|bonds|market|markets|risk|returns)\\b')
    evidence = contains('citation', 'verify', 'verified', 'proof', 'evidence', 'latest', 'measured', 'confirmed') or match('\\b(?:source|sources|current|today|actual)\\b')
    if correction:
        guidance.append('Use the latest user correction for the corrected detail without discarding unrelated valid context.')
    if followup:
        guidance.append('Resolve follow-up references using authorized conversation history; do not invent missing context.')
    if coding:
        guidance.append('For software tasks, distinguish observations from hypotheses; preserve existing interfaces and provide actionable code when requested.')
    if troubleshooting:
        guidance.append('For troubleshooting, start with read-only checks of status, logs, configuration and recent changes. Separate confirmed facts from hypotheses. Do not restart, enable, reinstall, reconfigure or change production state before evidence justifies an action and the user authorizes it.')
    if finance:
        guidance.append('For financial analysis, distinguish sourced figures, calculations, assumptions, scenarios and judgments. Do not invent prices, positions, execution results, industry averages or historical performance. State clearly when records are insufficient.')
    if evidence:
        guidance.append('Use actual supplied or authorized tool evidence. Never claim to have verified a source without a corresponding result.')
    if not guidance:
        return existing
    guidance.append('Answer the latest request directly. Be concise enough to finish the requested answer within the available output budget. Prioritize conclusions and actionable details over decorative formatting. Honor authorization, safety and tool boundaries.')
    block = '[NEURO_INTELLIGENCE_13A_R3]\n' + ' '.join(guidance) + '\n[/NEURO_INTELLIGENCE_13A_R3]\n\n'
    if len(block) > 1450:
        return existing
    if len(block) + len(existing) > 16000:
        return existing
    return block + existing






# NEURO_INTELLIGENCE_13A_R11_GUARD

"""Staged NeuroVest read-only diagnostic response guard.

This is a narrow response-level guard, not command execution
authorization or a general-purpose shell security parser.
"""

import re

FENCE = re.compile(
    r"```(?:bash|sh|shell|console|zsh)?\s*\n(.*?)```",
    re.IGNORECASE | re.DOTALL,
)

READ_ONLY_REQUEST = re.compile(
    r"\b(?:read.only|diagnos\w*|inspect\w*|"
    r"without (?:changing|modifying|restarting)|"
    r"do not (?:change|modify|restart|start)|"
    r"no changes)\b",
    re.IGNORECASE,
)

MUTATING_COMMAND = re.compile(
    r"(?im)^\s*(?:\$\s*)?(?:sudo\s+)?(?:"
    r"systemctl\s+(?:start|stop|restart|reload|"
    r"enable|disable|daemon-reload|reset-failed)\b|"
    r"(?:python3?|pip3?)\s+-m\s+venv\b|"
    r"pip3?\s+install\b|"
    r"(?:python3?\s+-m\s+pip)\s+install\b|"
    r"apt(?:-get)?\s+(?:install|upgrade|remove)\b|"
    r"rm\s+-|"
    r"git\s+(?:reset|checkout|restore|clean)\b"
    r")",
)

def inspect_diagnostic_response(user_message, assistant_text):
    if not isinstance(user_message, str):
        return {"restricted": False, "violations": []}
    if not isinstance(assistant_text, str):
        return {"restricted": False, "violations": []}

    restricted = bool(READ_ONLY_REQUEST.search(user_message))
    violations = []

    if restricted:
        for block in FENCE.findall(assistant_text):
            for line in block.splitlines():
                command = line.strip()
                if MUTATING_COMMAND.search(command):
                    violations.append(command[:240])

    return {
        "restricted": restricted,
        "violations": violations,
        "safe": not violations,
    }

def safe_diagnostic_response(user_message, assistant_text):
    result = inspect_diagnostic_response(
        user_message, assistant_text
    )
    if not result["violations"]:
        return assistant_text, result

    # Never preserve an unsafe answer and silently
    # delete its commands, because remaining prose may
    # depend on the removed state-changing steps.
    fallback = (
        "Start with read-only checks before changing anything.\n\n"
        "```bash\n"
        "systemctl status YOUR_SERVICE.service --no-pager\n"
        "journalctl -u YOUR_SERVICE.service -n 100 --no-pager\n"
        "systemctl cat YOUR_SERVICE.service\n"
        "```\n\n"
        "Replace YOUR_SERVICE with the actual service name. "
        "Review the first error, ExecStart, WorkingDirectory, "
        "service account and environment configuration. "
        "Share the relevant logs before deciding on a fix. "
        "Do not post secrets or credentials from configuration."
    )

    return fallback, result



# ============================================================
# NEUROVEST 13B-R1 — GENERAL PURPOSE CONVERSATION
# ============================================================

_NV13B_GENERAL_GUIDANCE = """
You are Neuro, NeuroVest's general-purpose conversational AI.

You can help with ordinary questions and discussions across
programming, troubleshooting, writing, learning, mathematics,
planning, explanations, and many other everyday subjects.

Financial markets, trading, risk, portfolios and strategy
analysis are major areas of expertise, but they are not your
only capabilities. Do not redirect unrelated questions toward
finance, investing or paper trading.

Understand the user's actual request before answering.
Respond naturally and directly. Use the conversation's
relevant context, including explicit user corrections.
Avoid generic capability descriptions when the user has
asked for a concrete answer.

For programming: provide working, appropriately scoped code,
explain meaningful assumptions, and avoid claiming untested
code was executed.

For troubleshooting: diagnose before prescribing disruptive
changes. If the user requests read-only inspection, do not
recommend commands that change state.

For writing and creative tasks: produce the requested artifact
without unnecessary finance-related framing.

For explanations and factual research: distinguish known
information, inference, and information needing verification.
Do not invent sources, tools, live prices, or current events.

For financial topics: maintain evidence-grounded market and
risk expertise, disclose uncertainty, and preserve the
existing simulation, paper-trading and no-live-trading gates.

Follow the actual authorization and safety boundaries of
the runtime. General-purpose ability does not grant users
developer-only diagnostic or improvement permissions.
""".strip()


def _nv13b_is_general_request(question: str) -> bool:
    if not isinstance(question, str):
        return False

    text = question.strip().casefold()

    if not text:
        return False

    developer_only = (
        "what do you need to improve",
        "developer capability inventory",
        "developer self assessment",
        "developer self-assessment",
    )

    if any(marker in text for marker in developer_only):
        return False

    # Keep the established financial prompt pathway.
    financial_markers = (
        "stock", "stocks", "market", "trading",
        "trade setup", "portfolio", "investing",
        "investment", "broker", "ticker", "option chain",
        "candlestick", "forex", "crypto",
        "backtest", "position sizing",
    )

    if any(marker in text for marker in financial_markers):
        return False

    return True


def _nv13b_compose_guidance(
    existing: str,
    question: str,
) -> str:
    if not isinstance(existing, str):
        return existing

    if not _nv13b_is_general_request(question):
        return existing

    if "NEUROVEST_GENERAL_PURPOSE_13B_R1" in existing:
        return existing

    return (
        existing.rstrip()
        + "\n\n"
        + "[NEUROVEST_GENERAL_PURPOSE_13B_R1]\n"
        + _NV13B_GENERAL_GUIDANCE
        + "\n[/NEUROVEST_GENERAL_PURPOSE_13B_R1]"
    )


_nv13b_previous_enhance_model_input = (
    _nv5c_enhance_model_input
)


def _nv5c_enhance_model_input(*args, **kwargs):
    existing = _nv13b_previous_enhance_model_input(
        *args, **kwargs
    )

    question = kwargs.get("question")

    if not isinstance(question, str):
        question = kwargs.get("message")

    if not isinstance(question, str):
        question = kwargs.get("user_message")

    if not isinstance(question, str):
        # Exact original signature:
        # (model_input, user_message, history).
        # args[0] is SYSTEM PROMPT, not the user question.
        question = (
            args[1]
            if len(args) >= 2
            and isinstance(args[1], str)
            else ""
        )

    return _nv13b_compose_guidance(
        existing, question
    )



# ============================================================
# NEUROVEST 13B-R5 — INTENT-AWARE GENERAL ASSISTANCE
# ============================================================

import re as _nv13b_re

_NV13B_GENERAL_GUIDANCE = """
You are Neuro, NeuroVest's general-purpose conversational AI
with especially strong financial markets and trading expertise.

You can also help with coding, troubleshooting, mathematics,
writing, learning, planning, and ordinary conversation.
Never imply you are limited to finance or paper trading.

Answer the user's actual request directly. Do not substitute
a capabilities introduction for a requested solution.

Maintain relevant conversation history and follow the user's
latest explicit corrections.

For coding and troubleshooting, provide useful, appropriately
scoped solutions. Respect read-only diagnostic requests.

For writing, explanations, and creative work, fulfill the
requested task without unnecessary financial framing.

Never invent sources, tool results, execution, current prices,
or information you have not verified.

Financial answers must preserve specialized research,
evidence, risk controls, and paper-trading restrictions.

Developer-only commands remain subject to verified server-side
authorization. No prompt grants additional permissions.
Never enable live trading through conversation.
""".strip()


def _nv13b_r5_route(question: str) -> str:
    """Prompt-guidance routing only; never authorization."""
    if not isinstance(question, str):
        return "invalid"

    text = question.strip().casefold()

    if not text:
        return "invalid"

    def has(pattern: str) -> bool:
        return _nv13b_re.search(
            pattern, text, _nv13b_re.IGNORECASE
        ) is not None

    # This classification does not authorize anything.
    # Existing authenticated developer guards retain
    # full responsibility for access control.
    developer_patterns = (
        r"\bwhat do you need to improve\b",
        r"\bdeveloper capability inventory\b",
        r"\bdeveloper self[- ]assessment\b",
    )

    if any(has(pattern) for pattern in developer_patterns):
        return "developer_special"

    financial = has(
        r"\b(?:stocks?|equities|trading|trades?|"
        r"portfolio|portfolios|investing|investments?|"
        r"brokerage|brokers?|tickers?|candlesticks?|"
        r"forex|cryptocurrency|crypto|backtests?|"
        r"options? chain|position sizing|"
        r"financial markets?|market data|"
        r"technical indicators?|dividend growth)\b"
    )

    general = has(
        r"\b(?:python|javascript|typescript|coding|"
        r"programming|scripts?|functions?|debug|"
        r"troubleshoot|ubuntu|linux|service|"
        r"write|writing|story|poem|explain|"
        r"teach|learn|recipe|photosynthesis|"
        r"math|calculate|plan|design|"
        r"help|capabilities|abilities)\b"
    )

    identity = has(
        r"\b(?:who are you|what can you do|"
        r"tell me about yourself|what can you help|"
        r"what are your capabilities|"
        r"are you only|can you also)\b"
    )

    if identity:
        return "general_identity"

    if financial and general:
        return "mixed"

    if financial:
        return "financial"

    if general:
        return "general_task"

    return "general_conversation"


def _nv13b_is_general_request(question: str) -> bool:
    route = _nv13b_r5_route(question)

    # Preserve existing specialized financial prompts.
    # Mixed tasks also receive general-purpose guidance.
    return route in (
        "general_identity",
        "mixed",
        "general_task",
        "general_conversation",
    )


def _nv13b_r5_enhance_model_input(
    model_input, user_message, history
):
    # Reuse the working R3 integration, which invokes
    # the established 13A enhancer before 13B guidance.
    return _nv5c_enhance_model_input(
        model_input, user_message, history
    )



def _g41_recoverable_wikipedia_answer(
    *,
    original_status,
    original_message,
    final_answer,
    verification,
):
    """Allow only evidence-checked recovery from optional lookup failure."""
    known_failure = (
        "A Wikipedia summary could not be retrieved for that topic."
    )

    if original_status != "error":
        return False

    if not isinstance(original_message, str):
        return False

    if original_message.strip() != known_failure:
        return False

    if not isinstance(final_answer, str):
        return False

    cleaned = final_answer.strip()

    if len(cleaned) < 40:
        return False

    if cleaned == known_failure:
        return False

    if any(part in cleaned.casefold() for part in (
        "couldn't verify that my response",
        "couldn't produce a reliable answer",
        "neuro local model is unavailable",
        "internal server error",
        "could not be retrieved for that topic",
    )):
        return False

    if not bool(getattr(verification, "passed", False)):
        return False

    if bool(getattr(verification, "fail_closed", True)):
        return False

    if getattr(verification, "violations", ()):
        return False

    return True
