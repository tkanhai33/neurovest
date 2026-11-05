from __future__ import annotations

import json
from pathlib import Path

from fastapi import HTTPException
from fastapi.routing import APIRoute


def _status(code: str, message: str) -> str:
    return "UNIVERSE_COMMAND_STATUS: " + code + "\n" + message


def _valid_symbol(symbol: str) -> bool:
    return (
        isinstance(symbol, str)
        and symbol.isascii()
        and symbol.isalnum()
        and symbol.isupper()
        and 1 <= len(symbol) <= 10
    )


def _format_result(result: dict, selected: list[str]) -> str:
    if not isinstance(result, dict):
        return _status("UNAVAILABLE", "Analysis returned no result.")

    if not (
        result.get("read_only") is True
        and result.get("execution_enabled") is False
        and result.get("order_admission_allowed") is False
        and result.get("live_trading_authorized") is False
    ):
        return _status(
            "UNAVAILABLE",
            "The read-only safety contract could not be verified.",
        )

    analysis = result.get("financial_analysis")

    if not isinstance(analysis, dict):
        return _status(
            "UNAVAILABLE",
            "The engine did not return structured analysis.",
        )

    returned = analysis.get("universe_symbols")

    if (
        not isinstance(returned, list)
        or set(returned) != set(selected)
        or len(returned) != len(selected)
    ):
        return _status(
            "UNAVAILABLE",
            "The returned analysis universe did not match your selection.",
        )

    count = analysis.get("actual_v4_evaluator_count")

    lines = [
        "Read-only financial analysis completed.",
        "Research symbols: " + ", ".join(selected),
        "V4 evaluators reported: " + str(count),
        "Allocation: illustrative equal-weight research only.",
        "Actual broker positions: not used.",
        "Trading execution: disabled.",
    ]

    # Only expose fields returned by the actual engine.
    # No language model may invent indicators for this command.
    allowed = (
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

    details = {
        key: analysis[key]
        for key in allowed
        if key in analysis
    }

    if details:
        encoded = json.dumps(
            details,
            default=str,
            ensure_ascii=True,
            separators=(",", ":"),
        )
        if len(encoded) <= 12000:
            lines.append("Verified engine evidence:")
            lines.append(encoded)
        else:
            lines.append(
                "Detailed evidence exceeds the chat response limit; "
                "no indicators have been inferred or truncated."
            )
    else:
        lines.append(
            "No additional indicator details were supplied "
            "in the engine response contract."
        )

    lines.append(
        "Research only; no orders, automated execution, "
        "or investment guarantees."
    )

    return _status("ANALYZED", "\n".join(lines))


async def analyze_selected_universe(
    *,
    principal,
    supplied: str,
) -> str:
    from backend.app.stacks.strategy.user_activation import service
    from backend.app.stacks.financial_analysis_readonly import (
        financial_api,
    )
    from backend.app.stacks.market_data import multi_symbol_bars

    owner = getattr(principal, "subject", None)

    if not isinstance(owner, str) or not owner.strip():
        return _status(
            "UNAUTHORIZED",
            "An authenticated account is required.",
        )

    symbols = [
        value.strip().upper()
        for value in supplied.replace(",", " ").split()
    ]

    if not (
        2 <= len(symbols) <= 12
        and len(set(symbols)) == len(symbols)
        and all(_valid_symbol(s) for s in symbols)
    ):
        return _status(
            "INVALID_SYMBOLS",
            "Select 2–12 distinct uppercase alphanumeric "
            "symbols, 1–10 characters each. "
            "Example: /universe analyze SPY QQQ DIA",
        )

    try:
        # Always consult the real owner-scoped source.
        saved = await service.list_owner_universe_symbols(
            owner_subject=owner,
        )
    except Exception:
        return _status(
            "UNAVAILABLE",
            "Your saved universe could not be retrieved.",
        )

    if (
        not isinstance(saved, list)
        or len(set(saved)) != len(saved)
        or not set(symbols).issubset(set(saved))
    ):
        return _status(
            "INVALID_SYMBOLS",
            "One or more requested symbols are not in your "
            "saved research universe. Use /universe show "
            "to see your available symbols.",
        )

    async def scoped_owner_loader(*, owner_subject):
        if owner_subject != owner:
            raise PermissionError("owner_mismatch")

        return list(symbols)

    def load_bars(values, *, limit):
        return multi_symbol_bars.get_daily_bars_for_symbols(
            values,
            limit=limit,
        )

    try:
        directory = (
            Path(financial_api.__file__).resolve().parent
        )

        candidate = financial_api.create_candidate_router(
            owner_universe_loader=scoped_owner_loader,
            provider_loader=load_bars,
            b13_directory=directory,
        )

        routes = [
            item
            for item in candidate.routes
            if isinstance(item, APIRoute)
            and item.path
            == "/api/v1/financial-analysis/readonly"
            and "GET" in item.methods
        ]

        if len(routes) != 1:
            raise RuntimeError("analysis_route_missing")

        # The existing authenticated engine still enforces
        # owner identity, safety, provider and evaluator rules.
        result = await routes[0].endpoint(
            mode="CURRENT_MARKET_ANALYSIS",
            principal=principal,
        )

        return _format_result(result, symbols)

    except HTTPException as exc:
        if exc.status_code == 409:
            return _status(
                "UNAVAILABLE",
                "The selected universe was rejected by "
                "the analysis service.",
            )

        return _status(
            "UNAVAILABLE",
            "Market data or verified analysis is currently "
            "unavailable. No results were invented.",
        )

    except Exception:
        return _status(
            "UNAVAILABLE",
            "The analysis engine could not complete this "
            "request. No trading action was taken.",
        )
