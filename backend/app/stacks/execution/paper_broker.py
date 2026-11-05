"""AUTO GENERATED RUNTIME FILE"""
import random
import math
from backend.app.stacks.portfolio.rebalance import execute_trade
from backend.app.stacks.journal_ledger.ledger import (
    save_log,
    read_portfolio_positions,
    lookup_paper_order_request,
)
from backend.app.stacks.strategy.signal import generate_signal
from backend.app.stacks.market_data.price import get_latest_price
from backend.app.stacks.market_data.bars import get_bars
from backend.app.stacks.risk.drawdown_guard import healthcheck as drawdown_healthcheck
from backend.app.stacks.risk.kill_switch import is_kill_switch_active
from backend.app.stacks.portfolio.allocator import calculate_position_size
from backend.app.stacks.portfolio.accounting import calculate_live_portfolio_equity
from backend.app.stacks.market_data.risk_valuation_quotes import get_risk_valuation_quote
from backend.app.core.runtime_trace import (
    create_trace_id,
    emit_runtime_step,
)

from backend.app.stacks.execution.execution_control import (
    execution_control,
)
from backend.app.stacks.execution.paper_order_identity import (
    normalize_request_id,
    fingerprint_order_intent,
)

def healthcheck():
    return {"status": "ok"}


def _broker_quote_utc_now():
    """UTC clock for broker quote freshness validation."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc)


async def process_portfolio_output(
    portfolio_matrix: list,
    portfolio_output: dict,
    *,
    user_id: str,
    trace_id: str | None = None,
    request_id: str | None = None,
):
    normalized_user_id = str(
        user_id
    ).strip()

    if not normalized_user_id:
        raise ValueError(
            "Paper execution user_id cannot be empty"
        )


    execution_control.assert_paper_execution_allowed()

    keyed_arguments = {}

    if request_id is not None:
        request_id = normalize_request_id(request_id)

        if not isinstance(portfolio_output, dict):
            raise ValueError(
                "Keyed paper order requires order intent"
            )

        raw_action = portfolio_output.get("signal")
        if isinstance(raw_action, dict):
            raw_action = raw_action.get("action")

        fingerprint = fingerprint_order_intent(
            symbol=portfolio_output.get("symbol"),
            action=raw_action,
        )

        keyed_arguments = {
            "request_id": request_id,
            "request_fingerprint": fingerprint,
        }

        committed = await lookup_paper_order_request(
            user_id=normalized_user_id,
            **keyed_arguments,
        )

        if committed is not None:
            execution_control.assert_paper_execution_allowed()
            return committed

    trace_id = trace_id or create_trace_id("paper-flow")

    if not portfolio_output or 'signal' in portfolio_output:
        raw_output_signal = portfolio_output.get('signal', 'hold')
        symbol = portfolio_output.get('symbol', 'UNKNOWN')

        if isinstance(raw_output_signal, dict):
            signal = raw_output_signal.get('action', 'hold')
        else:
            signal = str(raw_output_signal)

        await emit_runtime_step(
            trace_id=trace_id,
            event_type="PORTFOLIO_ACCOUNTING_REQUEST",
            node="portfolio_accounting",
            source="strategy",
            destination="portfolio_accounting",
            status="active",
            symbol=symbol,
            message="Reading live portfolio equity before risk evaluation",
            layer="L2",
            stack="portfolio",
        )

        # 1. Pull real fluctuating capital matrices from our new accounting stack
        equity_matrix = await calculate_live_portfolio_equity(
            user_id=user_id,
        )

        await emit_runtime_step(
            trace_id=trace_id,
            event_type="PORTFOLIO_ACCOUNTING_COMPLETE",
            node="portfolio_accounting",
            status="completed",
            symbol=symbol,
            message="Live portfolio equity loaded",
            layer="L2",
            stack="portfolio",
        )
        if equity_matrix.get("error"):
            raise RuntimeError(
                "Paper buying power is unavailable"
            )

        live_capital = float(
            equity_matrix["current_cash_balance"]
        )

        if not (0.0 <= live_capital < float("inf")):
            raise RuntimeError(
                "Invalid paper buying power"
            )

        await emit_runtime_step(
            trace_id=trace_id,
            event_type="RISK_EVALUATION_STARTED",
            node="risk",
            source="portfolio_accounting",
            destination="risk",
            status="active",
            symbol=symbol,
            message="Evaluating drawdown guard and kill switch",
            layer="L2",
            stack="risk",
        )

        # 2. Await our async drawdown database guard check
        drawdown_status = await drawdown_healthcheck(
            live_capital,
            user_id=user_id,
        )
        kill_switch_active = is_kill_switch_active()

        if not drawdown_status or drawdown_status.get("status") != "ok" or kill_switch_active:
            transaction_status = "blocked_by_risk"

            await emit_runtime_step(
                trace_id=trace_id,
                event_type="RISK_DECISION",
                node="risk",
                status="blocked",
                symbol=symbol,
                message="Execution blocked by risk controls",
                layer="L2",
                stack="risk",
                details={
                    "drawdown_status": drawdown_status,
                    "kill_switch_active": kill_switch_active,
                },
            )

            await save_log(
                {
                    "symbol": symbol,
                    "signal": signal,
                    "status": transaction_status,
                },
                user_id=normalized_user_id,
                trace_id=trace_id,
                **keyed_arguments,
            )
            return {"status": transaction_status, "reason": "risk_controls_blocked"}

        await emit_runtime_step(
            trace_id=trace_id,
            event_type="RISK_DECISION",
            node="risk",
            status="completed",
            symbol=symbol,
            message="Risk controls allowed paper execution",
            layer="L2",
            stack="risk",
        )

        # 3. Calculate dynamic volatility allocation sizes using truthful history.
        sizing_matrix = calculate_position_size(
            symbol,
            total_capital=live_capital,
        )

        sizing_status = str(
            sizing_matrix.get(
                "status",
                "ok",
            )
        )

        allocated_capital = float(
            sizing_matrix.get(
                "allocated_capital",
                0.0,
            )
        )

        if (
            sizing_status != "ok"
            or
            allocated_capital <= 0.0
        ):
            rejection = {
                "symbol": symbol,
                "signal": signal,
                "status": "rejected_history_unavailable",
                "allocated_capital": 0.0,
                "allocation_percentage": 0.0,
                "reason": sizing_matrix.get(
                    "reason",
                    "position_sizing_refused",
                ),
                "sizing_status": sizing_status,
            }

            if sizing_matrix.get(
                "error"
            ):
                rejection["error"] = sizing_matrix[
                    "error"
                ]

            await emit_runtime_step(
                trace_id=trace_id,
                event_type="PAPER_EXECUTION_REJECTED",
                node="execution",
                source="portfolio",
                destination="execution",
                status="blocked",
                symbol=symbol,
                message=(
                    "Paper execution rejected because truthful "
                    "historical sizing data is unavailable"
                ),
                layer="L4",
                stack="execution",
                details={
                    "sizing_status": sizing_status,
                    "reason": rejection["reason"],
                },
            )

            await save_log(
                rejection,
                user_id=normalized_user_id,
                trace_id=trace_id,
                **keyed_arguments,
            )

            return {"status": rejection["status"], "reason": rejection["reason"]}

        await emit_runtime_step(
            trace_id=trace_id,
            event_type="MARKET_QUOTE_REQUEST",
            node="market_data",
            source="risk",
            destination="market_data",
            status="active",
            symbol=symbol,
            message="Requesting execution quote from market data",
            layer="L2",
            stack="market_data",
        )

        # 4. Pull real ticker prices from the yfinance sandbox data stack engine
        # Strict source-bar quote. Never fall back to the
        # legacy price-only feed when provenance is unavailable.
        try:
            live_feed = await get_risk_valuation_quote(symbol)
        except Exception:
            # A missing vendor observation must reject the
            # simulated fill, not produce an invented price.
            live_feed = None

        from datetime import datetime, timezone, timedelta

        quote_verified = False

        if isinstance(live_feed, dict):
            observed_at = live_feed.get("observed_at")
            quote_currency = live_feed.get("currency")
            quote_symbol = live_feed.get("symbol")
            quote_provider = live_feed.get("provider")

            valid_currency = (
                isinstance(quote_currency, str)
                and len(quote_currency) == 3
                and quote_currency.isascii()
                and quote_currency.isalpha()
                and quote_currency == quote_currency.upper()
            )

            valid_timestamp = (
                isinstance(observed_at, datetime)
                and observed_at.tzinfo is not None
                and observed_at.utcoffset() is not None
            )

            if valid_timestamp:
                quote_age = (
                    _broker_quote_utc_now() - observed_at
                )
            else:
                quote_age = None

            quote_verified = (
                live_feed.get("status") == "ok"
                and isinstance(quote_symbol, str)
                and quote_symbol.strip().upper()
                    == str(symbol).strip().upper()
                and quote_provider == "yfinance"
                and valid_currency
                and quote_age is not None
                and timedelta(0) <= quote_age
                and quote_age <= timedelta(seconds=300)
            )

        if not quote_verified:
            live_feed = None
        # A paper fill requires a valid observed market price.
        # Never invent a fallback execution price.
        quote_value = (
            live_feed.get("price")
            if isinstance(live_feed, dict)
            else None
        )

        try:
            raw_price = (
                float(quote_value)
                if quote_value is not None
                and not isinstance(quote_value, bool)
                else float("nan")
            )
        except (TypeError, ValueError, OverflowError):
            raw_price = float("nan")

        if not math.isfinite(raw_price) or raw_price <= 0.0:
            rejection = {
                "symbol": symbol,
                "signal": signal,
                "status": "rejected_market_quote_unavailable",
                "reason": "valid_execution_quote_unavailable",
                "allocated_capital": 0.0,
                "allocation_percentage": 0.0,
            }

            await emit_runtime_step(
                trace_id=trace_id,
                event_type="PAPER_EXECUTION_REJECTED",
                node="execution",
                source="market_data",
                destination="execution",
                status="blocked",
                symbol=symbol,
                message="Paper execution rejected: invalid market quote",
                layer="L4",
                stack="execution",
                details={
                    "reason": rejection["reason"],
                },
            )

            await save_log(
                rejection,
                user_id=normalized_user_id,
                trace_id=trace_id,
                **keyed_arguments,
            )
            return {"status": rejection["status"], "reason": rejection["reason"]}

        await emit_runtime_step(
            trace_id=trace_id,
            event_type="MARKET_QUOTE_RECEIVED",
            node="market_data",
            status="completed",
            symbol=symbol,
            message="Execution quote received",
            layer="L2",
            stack="market_data",
            details={
                "provider": live_feed.get("provider"),
                "quote_status": live_feed.get("status"),
            },
        )

        # 5. Simulate randomized market execution slippage (0.01% - 0.05%)
        slippage_factor = 1.0 + random.uniform(0.0001, 0.0005) if str(signal).lower() == "buy" else 1.0 - random.uniform(0.0001, 0.0005)
        slippage_price = raw_price * slippage_factor

        # 6. Deduct structural commission transaction friction fees ($1 flat fee)
        commission = 1.00

        await emit_runtime_step(
            trace_id=trace_id,
            event_type="PAPER_EXECUTION_STARTED",
            node="execution",
            source="market_data",
            destination="execution",
            status="active",
            symbol=symbol,
            message="Executing paper-trade simulation",
            layer="L4",
            stack="execution",
        )

        # Revalidate after asynchronous processing.
        # A separate worker may have activated EMERGENCY_STOP.
        execution_control.assert_paper_execution_allowed()

        # Check the original observation again immediately
        # before generating a simulated fill.
        quote_age_before_fill = (
            _broker_quote_utc_now() - observed_at
        )

        if (
            quote_age_before_fill < timedelta(0)
            or quote_age_before_fill > timedelta(seconds=300)
        ):
            raise RuntimeError(
                "paper_quote_expired_before_fill"
            )

        trade_result = execute_trade(symbol, signal)

        await emit_runtime_step(
            trace_id=trace_id,
            event_type="PAPER_EXECUTION_RESULT",
            node="execution",
            status=str(trade_result.get("status", "completed")),
            symbol=symbol,
            message="Paper execution returned a result",
            layer="L4",
            stack="execution",
        )

        # Ingest structural allocation, sizing, and friction parameters into the final log payload mapping
        trade_result["allocated_capital"] = allocated_capital
        trade_result["allocation_percentage"] = sizing_matrix.get("allocation_percentage", 1.0)
        trade_result["slippage_price"] = slippage_price
        trade_result["commission_paid"] = commission

        # Reject a stop issued after the simulated fill event.
        # This check does not serialize with the DB commit.
        execution_control.assert_paper_execution_allowed()

        persisted = await save_log(
            trade_result,
            user_id=normalized_user_id,
            trace_id=trace_id,
            **keyed_arguments,
        )

        if keyed_arguments:
            return persisted

        return {
            "status": str(trade_result.get("status", "unknown")),
            "symbol": symbol,
        }




async def get_positions_snapshot(
    *,
    user_id: str,
):
    normalized_user_id = str(
        user_id
    ).strip()

    if not normalized_user_id:
        raise ValueError(
            "Portfolio snapshot user_id cannot be empty"
        )

    positions = await read_portfolio_positions(
        user_id=normalized_user_id,
    )

    return {
        "status": "ok",
        "positions": positions,
        "count": len(positions),
        "provider": "paper_broker",
        "scope": "authenticated_account",
    }
