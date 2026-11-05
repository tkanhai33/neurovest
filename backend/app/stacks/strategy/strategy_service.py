from __future__ import annotations

from backend.app.core.runtime_trace import (
    create_trace_id,
    emit_runtime_step,
)
from backend.app.stacks.market_data.bars import (
    HistoricalBarsUnavailableError,
    get_bars,
)
from backend.app.stacks.market_data.multi_symbol_bars import (
    get_daily_bars_for_symbols,
)
from backend.app.stacks.strategy.engine import (
    generate_strategy_decision,
)
from backend.app.stacks.strategy.evaluators.aggregation import (
    aggregate_strategy_results,
)
from backend.app.stacks.strategy.evaluators.registry import (
    ALLOWLISTED_EVALUATORS,
    MULTI_SYMBOL_STRATEGY_NAMES,
    evaluate_allowlisted_strategy,
)
from backend.app.stacks.strategy.user_activation.service import (
    list_enabled_strategy_names,
    list_owner_universe_symbols,
)


def _abstention(
    *,
    symbol: str,
    reason: str,
    provider: str,
    error: str | None = None,
) -> dict:
    result = {
        "status": "abstained",
        "symbol": symbol,
        "signal": "hold",
        "decision": "ABSTAIN",
        "confidence": 0.0,
        "provider": provider,
        "owner_strategy_applied": False,
        "reason": reason,
        "portfolio_output": None,
    }

    if error:
        result[
            "error"
        ] = error

    return result


async def get_strategy_decision_for_api(
    symbol: str,
    *,
    owner_subject: str,
):
    trace_id = create_trace_id(
        "strategy-api"
    )

    clean_symbol = str(
        symbol
    ).strip().upper()

    clean_owner = str(
        owner_subject
    ).strip()

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="STRATEGY_API_REQUEST_RECEIVED",
        node="strategy_api",
        source="http_api",
        destination="strategy_api",
        status="active",
        symbol=clean_symbol,
        message=(
            "Authenticated owner-scoped strategy request received"
        ),
        layer="L5",
        stack="strategy",
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="STRATEGY_FACADE_REQUEST",
        node="strategy_facade",
        source="strategy_api",
        destination="strategy_facade",
        status="active",
        symbol=clean_symbol,
        message=(
            "Strategy API delegated authenticated owner request "
            "to the strategy facade"
        ),
        layer="L3",
        stack="strategy",
    )

    if not clean_symbol:
        return {
            "status": "error",
            "symbol": clean_symbol,
            "signal": "hold",
            "decision": "ABSTAIN",
            "confidence": 0.0,
            "provider": "strategy_service",
            "owner_strategy_applied": False,
            "error": "missing_symbol",
        }

    if not clean_owner:
        return {
            "status": "error",
            "symbol": clean_symbol,
            "signal": "hold",
            "decision": "ABSTAIN",
            "confidence": 0.0,
            "provider": "strategy_service",
            "owner_strategy_applied": False,
            "error": "missing_owner_subject",
        }

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="OWNER_STRATEGY_SELECTION_REQUEST",
        node="strategy_activation",
        source="strategy_api",
        destination="strategy_activation",
        status="active",
        symbol=clean_symbol,
        message=(
            "Reading authenticated owner's enabled strategies"
        ),
        layer="L3",
        stack="strategy",
    )

    try:
        enabled_names = (
            await list_enabled_strategy_names(
                owner_subject=clean_owner,
            )
        )
    except Exception as exc:
        await emit_runtime_step(
            trace_id=trace_id,
            event_type="OWNER_STRATEGY_SELECTION_RESULT",
            node="strategy_activation",
            status="blocked",
            symbol=clean_symbol,
            message=(
                "Owner strategy selection could not be verified"
            ),
            layer="L3",
            stack="strategy",
            details={
                "error_type":
                    type(
                        exc
                    ).__name__,
            },
        )

        return _abstention(
            symbol=clean_symbol,
            reason="owner_strategy_selection_unavailable",
            provider="owner_strategy_activation",
            error=(
                f"{type(exc).__name__}: {exc}"
            ),
        )

    enabled_name_set = {
        str(
            name
        ).strip()
        for name in enabled_names
        if str(
            name
        ).strip()
    }

    qualified_enabled_names = tuple(
        strategy_name
        for strategy_name in ALLOWLISTED_EVALUATORS
        if strategy_name in enabled_name_set
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="OWNER_STRATEGY_SELECTION_RESULT",
        node="strategy_activation",
        status="completed",
        symbol=clean_symbol,
        message=(
            "Owner strategy selection loaded"
        ),
        layer="L3",
        stack="strategy",
        details={
            "enabled_count":
                len(
                    enabled_names
                ),

            "qualified_enabled_count":
                len(
                    qualified_enabled_names
                ),

            "qualified_enabled_names":
                list(
                    qualified_enabled_names
                ),
        },
    )

    if qualified_enabled_names:
        await emit_runtime_step(
            trace_id=trace_id,
            event_type="OWNER_STRATEGY_EVALUATION_STARTED",
            node="strategy_runtime",
            source="strategy_activation",
            destination="strategy_runtime",
            status="active",
            symbol=clean_symbol,
            message=(
                "Evaluating qualified owner-enabled strategies"
            ),
            layer="L4",
            stack="strategy",
            details={
                "strategy_count":
                    len(
                        qualified_enabled_names
                    ),

                "strategy_names":
                    list(
                        qualified_enabled_names
                    ),

                "bars_limit":
                    253,
            },
        )

        try:
            bars = get_bars(clean_symbol, limit=253)
            multi_enabled = tuple(
                name for name in qualified_enabled_names
                if name in MULTI_SYMBOL_STRATEGY_NAMES
            )
            universe_bars = None

            if multi_enabled:
                owner_universe = await list_owner_universe_symbols(
                    owner_subject=clean_owner,
                )
                if clean_symbol in owner_universe:
                    universe_bars = get_daily_bars_for_symbols(
                        owner_universe,
                        limit=253,
                    )

            evaluator_results = []

            for strategy_name in qualified_enabled_names:
                if strategy_name in MULTI_SYMBOL_STRATEGY_NAMES:
                    evaluated = evaluate_allowlisted_strategy(
                        strategy_name,
                        bars,
                        primary_symbol=clean_symbol,
                        universe_bars=universe_bars,
                    )
                else:
                    # Preserve the established two-argument evaluator API
                    # for every existing single-symbol strategy.
                    evaluated = evaluate_allowlisted_strategy(
                        strategy_name,
                        bars,
                    )

                evaluator_results.append(dict(evaluated))

            result = dict(
                aggregate_strategy_results(
                    evaluator_results
                )
            )

        except HistoricalBarsUnavailableError as exc:
            return _abstention(
                symbol=clean_symbol,
                reason="truthful_historical_bars_unavailable",
                provider="owner_enabled_reference_strategy_aggregation",
                error=(
                    f"{type(exc).__name__}: {exc}"
                ),
            )

        except Exception as exc:
            return _abstention(
                symbol=clean_symbol,
                reason="owner_enabled_evaluator_failed_closed",
                provider="owner_enabled_reference_strategy_aggregation",
                error=(
                    f"{type(exc).__name__}: {exc}"
                ),
            )

        result[
            "symbol"
        ] = clean_symbol

        result[
            "provider"
        ] = (
            "owner_enabled_reference_strategy"
            if len(
                qualified_enabled_names
            ) == 1
            else
            "owner_enabled_reference_strategy_aggregation"
        )

        result[
            "owner_strategy_applied"
        ] = True

        result[
            "enabled_strategy_names"
        ] = list(
            qualified_enabled_names
        )

        result[
            "enabled_strategy_count"
        ] = len(
            qualified_enabled_names
        )

        if len(
            qualified_enabled_names
        ) == 1:
            result[
                "enabled_strategy_name"
            ] = qualified_enabled_names[
                0
            ]

            sole_result = evaluator_results[
                0
            ]

            for key, value in sole_result.items():
                if key not in result:
                    result[
                        key
                    ] = value
        else:
            result[
                "enabled_strategy_name"
            ] = (
                "Aggregated qualified owner strategies"
            )

        result[
            "portfolio_output"
        ] = None

        result[
            "execution_enabled"
        ] = False

        await emit_runtime_step(
            trace_id=trace_id,
            event_type="OWNER_STRATEGY_EVALUATION_RESULT",
            node="strategy_runtime",
            status=str(
                result.get(
                    "status",
                    "completed",
                )
            ),
            symbol=clean_symbol,
            message=(
                "Qualified owner-enabled strategy aggregation completed"
            ),
            layer="L4",
            stack="strategy",
            details={
                "strategy_count":
                    len(
                        qualified_enabled_names
                    ),

                "strategy_names":
                    list(
                        qualified_enabled_names
                    ),

                "decision":
                    result.get(
                        "decision"
                    ),

                "evaluator_id":
                    result.get(
                        "evaluator_id"
                    ),

                "buy_votes":
                    result.get(
                        "buy_votes"
                    ),

                "sell_votes":
                    result.get(
                        "sell_votes"
                    ),

                "hold_votes":
                    result.get(
                        "hold_votes"
                    ),

                "abstaining_results":
                    result.get(
                        "abstaining_results"
                    ),
            },
        )

        return result

        return result

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="SYSTEM_STRATEGY_FALLBACK_STARTED",
        node="strategy_runtime",
        source="strategy_activation",
        destination="strategy_runtime",
        status="active",
        symbol=clean_symbol,
        message=(
            "No qualified owner strategy is enabled; using system strategy engine"
        ),
        layer="L4",
        stack="strategy",
    )

    try:
        result = generate_strategy_decision(
            clean_symbol
        )

        if hasattr(
            result,
            "__await__",
        ):
            result = await result

        if isinstance(
            result,
            dict,
        ):
            result = dict(
                result
            )

            result.setdefault(
                "status",
                "ok",
            )

            result.setdefault(
                "symbol",
                clean_symbol,
            )

            result.setdefault(
                "provider",
                "strategy_engine",
            )

            result[
                "owner_strategy_applied"
            ] = False

            result[
                "owner_strategy_reason"
            ] = (
                "qualified_sma_not_enabled"
            )

            return result

        return {
            "status": "ok",
            "symbol": clean_symbol,
            "decision": str(
                result
            ),
            "confidence": 0.0,
            "provider": "strategy_engine",
            "owner_strategy_applied": False,
            "owner_strategy_reason":
                "qualified_sma_not_enabled",
        }

    except Exception as exc:
        return _abstention(
            symbol=clean_symbol,
            reason="system_strategy_engine_unavailable",
            provider="strategy_service",
            error=(
                f"{type(exc).__name__}: {exc}"
            ),
        )
