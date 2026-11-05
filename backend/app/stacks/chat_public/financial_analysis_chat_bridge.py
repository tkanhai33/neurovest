from __future__ import annotations

import json
import re
from functools import lru_cache
from typing import Any

from fastapi import HTTPException
from fastapi.routing import APIRoute


# Only requests clearly seeking analysis of the user's own
# market/strategy universe activate this bridge.
_FINANCIAL_INTENT = re.compile(
    r"\b(analy[sz]e|analysis|evaluate|assess|review)\b"
    r".{0,110}\b(my|our)\b"
    r".{0,110}\b("
    r"strateg(?:y|ies)|universe|stocks?|"
    r"market|portfolio|indicators?"
    r")\b"
    r"|"
    r"\b(my|our)\b"
    r".{0,110}\b("
    r"strateg(?:y|ies)|universe|stocks?|"
    r"market|portfolio|indicators?"
    r")\b"
    r".{0,110}\b(analy[sz]e|analysis|evaluate|assess|review)\b",
    re.IGNORECASE,
)


@lru_cache(maxsize=1)
def _analysis_endpoint():
    from backend.app.stacks.financial_analysis_readonly.router import (
        build_router,
    )

    router = build_router()

    matches = [
        route
        for route in router.routes
        if isinstance(route, APIRoute)
        and route.path
        == "/api/v1/financial-analysis/readonly"
        and "GET" in route.methods
    ]

    if len(matches) != 1:
        raise RuntimeError("financial_analysis_route_unavailable")

    return matches[0].endpoint


def _evidence_from_result(result: dict[str, Any]) -> str:
    if (
        result.get("read_only") is not True
        or result.get("execution_enabled") is not False
        or result.get("order_admission_allowed") is not False
        or result.get("live_trading_authorized") is not False
    ):
        return (
            "FINANCIAL_ANALYSIS_STATUS: UNAVAILABLE\n"
            "Reason: The read-only safety contract could not "
            "be verified. Do not infer analytical results."
        )

    analysis = result.get("financial_analysis")

    if not isinstance(analysis, dict):
        return (
            "FINANCIAL_ANALYSIS_STATUS: UNAVAILABLE\n"
            "Reason: No structured analysis was returned."
        )

    # Include only known analysis fields. Avoid transmitting
    # account IDs, token data, credentials, or internal records.
    allowed = (
        "universe_symbols",
        "actual_v4_evaluator_count",
        "analysis_mode",
        "as_of",
        "freshness",
        "freshness_status",
        "data_age_seconds",
        "data_quality",
        "strategy_aggregation",
        "weighted_portfolio_analysis",
        "portfolio_analysis",
        "risk_analysis",
        "market_regime",
        "indicators",
        "signals",
        "evaluators",
        "limitations",
        "warnings",
    )

    selected = {
        key: analysis[key]
        for key in allowed
        if key in analysis
    }

    # Prevent overly large evidence injection.
    encoded = json.dumps(
        selected,
        ensure_ascii=True,
        default=str,
    )

    if len(encoded) > 14000:
        encoded = json.dumps(
            {
                "universe_symbols": analysis.get(
                    "universe_symbols"
                ),
                "actual_v4_evaluator_count": analysis.get(
                    "actual_v4_evaluator_count"
                ),
                "detail": (
                    "Extended results omitted due to size."
                ),
            },
            ensure_ascii=True,
            default=str,
        )

    return (
        "FINANCIAL_ANALYSIS_STATUS: AVAILABLE\n"
        "SOURCE: NeuroVest owner-scoped read-only "
        "financial-analysis engine.\n"
        "This is illustrative research, not actual "
        "broker positions or an executed allocation.\n"
        "Explain only supported findings. Distinguish "
        "observations, uncertainty, and missing evidence. "
        "Never imply orders were submitted.\n"
        "FINANCIAL_ANALYSIS_EVIDENCE_JSON:\n"
        + encoded
    )



# NEUROVEST_USER_UNIVERSE_CHAT_V1
# Explicit owner-scoped chat commands. Never infer a write
# request from ordinary conversation.
async def _handle_universe_chat_command(
    *,
    principal,
    message: str,
) -> str | None:
    import re

    raw = message.strip()
    if not re.match(
        r"^/universe(?:\s|$)",
        raw,
        re.IGNORECASE,
    ):
        return None

    owner = getattr(principal, "subject", None)

    if not isinstance(owner, str) or not owner.strip():
        return (
            "UNIVERSE_COMMAND_STATUS: UNAUTHORIZED\n"
            "The user must be authenticated."
        )

    from backend.app.stacks.strategy.user_activation.service import (
        list_owner_universe_symbols,
        replace_owner_universe_symbols,
    )

    parts = raw.split(maxsplit=2)
    action = parts[1].lower() if len(parts) > 1 else "help"

    instructions = (
        "Available commands:\n"
        "/universe show — view your saved symbols\n"
        "/universe set AAPL MSFT NVDA — replace your symbols\n"
        "/universe help — show these instructions\n"
        "Analysis requires 2–12 distinct uppercase "
        "alphanumeric symbols, each 1–10 characters long."
    )

    if action == "help" and len(parts) == 2:
        return (
            "UNIVERSE_COMMAND_STATUS: HELP\n"
            + instructions
        )

    if action == "help" and len(parts) == 1:
        return (
            "UNIVERSE_COMMAND_STATUS: HELP\n"
            + instructions
        )

    if action == "show" and len(parts) == 2:
        try:
            symbols = await list_owner_universe_symbols(
                owner_subject=owner,
            )
        except Exception:
            return (
                "UNIVERSE_COMMAND_STATUS: UNAVAILABLE\n"
                "The saved universe could not be retrieved."
            )

        eligible = (
            isinstance(symbols, list)
            and 2 <= len(symbols) <= 12
            and len(set(symbols)) == len(symbols)
            and all(
                isinstance(s, str)
                and s.isascii()
                and s.isupper()
                and s.isalnum()
                and 1 <= len(s) <= 10
                for s in symbols
            )
        )

        return (
            "UNIVERSE_COMMAND_STATUS: RETRIEVED\n"
            "Saved symbols: "
            + (", ".join(symbols) if symbols else "(none)")
            + "\nAnalysis eligible: "
            + ("yes" if eligible else "no")
            + "\nThis is a research universe, "
            "not evidence of actual holdings."
        )

    # NEUROVEST_PAID_RESEARCH_BATCH1_SUBSET
    if action == "analyze":
        from backend.app.stacks.chat_public.financial_subset_chat import (
            analyze_selected_universe,
        )

        if len(parts) != 3:
            return (
                "UNIVERSE_COMMAND_STATUS: INVALID_SYMBOLS\\n"
                "Example: /universe analyze SPY QQQ DIA"
            )

        return await analyze_selected_universe(
            principal=principal,
            supplied=parts[2],
        )

    if action != "set":
        return (
            "UNIVERSE_COMMAND_STATUS: INVALID_COMMAND\n"
            + instructions
        )

    if len(parts) != 3:
        return (
            "UNIVERSE_COMMAND_STATUS: INVALID_SYMBOLS\n"
            "Example: /universe set AAPL MSFT NVDA"
        )

    supplied = parts[2].replace(",", " ").split()

    # Reject duplicates rather than silently changing the user's
    # explicitly requested universe.
    symbols = [s.upper() for s in supplied]

    valid = (
        2 <= len(symbols) <= 12
        and len(set(symbols)) == len(symbols)
        and all(
            s.isascii()
            and s.isalnum()
            and 1 <= len(s) <= 10
            for s in symbols
        )
    )

    if not valid:
        return (
            "UNIVERSE_COMMAND_STATUS: INVALID_SYMBOLS\n"
            "Enter 2–12 distinct uppercase alphanumeric "
            "symbols, each containing 1–10 characters.\n"
            "Example: /universe set AAPL MSFT NVDA\n"
            "No changes were made."
        )

    try:
        saved = await replace_owner_universe_symbols(
            owner_subject=owner,
            symbols=symbols,
        )
    except ValueError:
        return (
            "UNIVERSE_COMMAND_STATUS: REJECTED\n"
            "The universe service rejected the symbols. "
            "No successful save was confirmed."
        )
    except Exception:
        return (
            "UNIVERSE_COMMAND_STATUS: UNAVAILABLE\n"
            "The save could not be confirmed. "
            "Check your saved universe before retrying."
        )

    if set(saved) != set(symbols) or len(saved) != len(symbols):
        return (
            "UNIVERSE_COMMAND_STATUS: UNVERIFIED\n"
            "The returned symbols did not match the request."
        )

    return (
        "UNIVERSE_COMMAND_STATUS: SAVED\n"
        "Saved symbols: " + ", ".join(saved)
        + "\nThese are the user's research-universe symbols, "
        "not verified broker holdings.\n"
        "No strategy was activated and no orders were placed.\n"
        "The user can now request financial analysis."
    )



# NEUROVEST_UNIVERSE_REPLY_FIX_V2
def authoritative_universe_reply(message, evidence):
    if not isinstance(message, str):
        return None

    parts = message.strip().split(maxsplit=1)
    if not parts or parts[0].casefold() != "/universe":
        return None

    if not isinstance(evidence, str):
        return "Universe command could not be verified. No save is confirmed."

    prefix = "UNIVERSE_COMMAND_STATUS: "
    if not evidence.startswith(prefix):
        return "Universe command could not be verified. No save is confirmed."

    # Accept the historical bridge's literal escaped newline,
    # as well as a real newline.
    normalized = evidence.replace("\\n", "\n")
    first, _, details = normalized.partition("\n")
    status = first[len(prefix):].strip()

    allowed = {
        "SAVED", "RETRIEVED", "HELP",
        "ANALYZED",  "INVALID_COMMAND",
        "INVALID_SYMBOLS", "REJECTED", "UNVERIFIED",
        "UNAVAILABLE", "UNAUTHORIZED",
    }

    if status not in allowed:
        return "Universe command returned an unrecognized status."

    if status == "SAVED":
        return "Your research universe was saved.\n" + details

    if status == "ANALYZED":
        return details

    if status == "RETRIEVED":
        return "Your saved research universe:\n" + details

    if status == "HELP":
        return details

    if status == "UNVERIFIED":
        return "The universe change could not be verified.\n" + details

    return "Universe command " + status.lower().replace("_", " ") + ".\n" + details

async def owner_financial_chat_evidence(
    *,
    principal: Any,
    message: str,
) -> str | None:
    if not isinstance(message, str):
        return None

    universe_command = await _handle_universe_chat_command(
        principal=principal,
        message=message,
    )

    if universe_command is not None:
        return universe_command

    if not _FINANCIAL_INTENT.search(message[:1200]):
        return None

    # Authentication identity must come from the trusted
    # principal supplied by the existing chat API.
    owner = getattr(principal, "subject", None)

    if not isinstance(owner, str) or not owner.strip():
        return (
            "FINANCIAL_ANALYSIS_STATUS: UNAVAILABLE\n"
            "An authenticated account is required."
        )

    try:
        endpoint = _analysis_endpoint()

        # The financial endpoint itself derives owner identity
        # from this same trusted principal.
        result = await endpoint(
            mode="CURRENT_MARKET_ANALYSIS",
            principal=principal,
        )

    except HTTPException as exc:
        if exc.status_code == 409:
            return (
                "FINANCIAL_ANALYSIS_STATUS: SETUP_REQUIRED\n"
                "The user's configured strategy universe is "
                "not eligible for analysis. Explain that "
                "NeuroVest currently requires 2–12 distinct "
                "uppercase alphanumeric symbols in the "
                "user's own strategy universe. Do not "
                "invent symbols or analysis results."
            )

        if exc.status_code in (401, 403):
            return (
                "FINANCIAL_ANALYSIS_STATUS: UNAUTHORIZED\n"
                "The account could not be authorized "
                "for this analysis."
            )

        return (
            "FINANCIAL_ANALYSIS_STATUS: UNAVAILABLE\n"
            "The read-only analysis service could not "
            "provide a verified result."
        )

    except Exception:
        return (
            "FINANCIAL_ANALYSIS_STATUS: UNAVAILABLE\n"
            "The analysis service is currently unavailable. "
            "Do not invent financial signals."
        )

    if not isinstance(result, dict):
        return (
            "FINANCIAL_ANALYSIS_STATUS: UNAVAILABLE\n"
            "Unexpected analysis result contract."
        )

    return _evidence_from_result(result)



# NEUROVEST_NATURAL_CHAT_3A
#
# Natural-language routing delegates to existing
# authenticated, owner-scoped financial tools.
#
# No new role permissions or execution authority.

_legacy_owner_financial_chat_evidence = (
    owner_financial_chat_evidence
)

_legacy_authoritative_universe_reply = (
    authoritative_universe_reply
)


async def owner_financial_chat_evidence(
    *,
    principal,
    message,
):
    from backend.app.stacks.chat_public import (
        natural_research_orchestrator as natural,
    )

    command = natural.natural_command(message)

    return await _legacy_owner_financial_chat_evidence(
        principal=principal,
        message=command if command else message,
    )


def authoritative_universe_reply(
    message,
    evidence,
):
    from backend.app.stacks.chat_public import (
        natural_research_orchestrator as natural,
    )

    command = natural.natural_command(message)

    if command is None:
        return _legacy_authoritative_universe_reply(
            message,
            evidence,
        )

    verified = _legacy_authoritative_universe_reply(
        command,
        evidence,
    )

    if verified is None:
        return None

    if command.startswith(
        "/universe analyze "
    ):
        return natural.explain_verified_analysis(
            evidence,
            verified,
        )

    return verified


# NEUROVEST_MODEL_TOOL_ROUTER_3B
# Local model-planned tools with server-side validation.
# No new execution, billing, or developer permissions.

_3b_previous_evidence = owner_financial_chat_evidence
_3b_previous_presenter = authoritative_universe_reply


async def owner_financial_chat_evidence(
    *,
    principal,
    message,
    context="",
):
    # NEUROVEST_R115E_MARKET_DISCOVERY

    # NEUROVEST_R117_OWNER_PORTFOLIO_RESEARCH
    from backend.app.stacks.chat_public.portfolio_opportunity_research_r117 import (
        portfolio_opportunity_evidence as _r117_portfolio_evidence,
    )
    _r117_evidence = await _r117_portfolio_evidence(
        message=message,
        principal=principal,
    )
    if _r117_evidence is not None:
        return _r117_evidence

    # NEUROVEST_R116_PUBLIC_FINANCIAL_RESEARCH
    from backend.app.stacks.chat_public.public_financial_research_r116 import (
        route as _r116_route,
        answer as _r116_answer,
    )
    _r116_message = message
    if isinstance(_r116_message, str):
        if _r116_route(_r116_message) is not None:
            return await _r116_answer(_r116_message)
        import re as _r116_re
        if _r116_re.search(
            r"\b(?:DNA|RNA|genetics|photosynthesis)\b",
            _r116_message, _r116_re.I
        ) and not _r116_re.search(
            r"\b(?:stock|ticker|shares|market)\b",
            _r116_message, _r116_re.I
        ):
            return None

    from backend.app.stacks.chat_public.market_discovery_r115 import (
        classify_market_discovery as _r115_classify,
        market_discovery_evidence as _r115_discover,
    )
    if _r115_classify(message) is not None:
        return await _r115_discover(message)

    from backend.app.stacks.chat_public import (
        model_tool_router_3b as tool_router,
    )

    # Prefer the already-qualified 3A path.
    from backend.app.stacks.chat_public import (
        natural_research_orchestrator as natural,
    )

    if (
        not isinstance(message, str)
        or message.strip().startswith("/")
        or natural.natural_command(message) is not None
    ):
        return await _3b_previous_evidence(
            principal=principal,
            message=message,
        )

    plan = await tool_router.plan_tool(
        message=message,
        context=context,
    )

    command = plan.command

    if command is None:
        return await _3b_previous_evidence(
            principal=principal,
            message=message,
        )

    # The existing tool implementation verifies the
    # trusted owner and allowed research symbols.
    evidence = await _3b_previous_evidence(
        principal=principal,
        message=command,
    )

    return tool_router.wrap_evidence(
        command,
        evidence,
    )


def authoritative_universe_reply(
    message,
    evidence,
):
    # NEUROVEST_R115E_MARKET_DISCOVERY_REPLY

    # NEUROVEST_R117_OWNER_PORTFOLIO_RESEARCH_REPLY
    from backend.app.stacks.chat_public.portfolio_opportunity_research_r117 import (
        PREFIX as _r117_prefix,
    )
    if isinstance(evidence, str) and evidence.startswith(_r117_prefix):
        return evidence[len(_r117_prefix):]

    # NEUROVEST_R116_PUBLIC_RESEARCH_REPLY
    from backend.app.stacks.chat_public.public_financial_research_r116 import (
        PREFIX as _r116_prefix,
    )
    if (isinstance(evidence, str)
        and evidence.startswith(_r116_prefix)):
        return evidence[len(_r116_prefix):]

    import re as _r116_re
    if _r116_re.search(
        r"\b(?:DNA|RNA|genetics|photosynthesis)\b",
        message, _r116_re.I
    ) and not _r116_re.search(
        r"\b(?:stock|ticker|shares|market)\b",
        message, _r116_re.I
    ):
        return None

    from backend.app.stacks.chat_public.market_discovery_r115 import (
        PREFIX as _r115_prefix,
    )
    if isinstance(evidence, str) and evidence.startswith(_r115_prefix):
        return evidence[len(_r115_prefix):]

    from backend.app.stacks.chat_public import (
        model_tool_router_3b as tool_router,
        natural_research_orchestrator as natural,
    )

    command, verified_evidence = (
        tool_router.unwrap_evidence(evidence)
    )

    if command is None:
        return _3b_previous_presenter(
            message,
            evidence,
        )

    answer = _3b_previous_presenter(
        command,
        verified_evidence,
    )

    if (
        answer is not None
        and command.startswith(
            "/universe analyze "
        )
    ):
        return natural.explain_verified_analysis(
            verified_evidence,
            answer,
        )

    return answer
