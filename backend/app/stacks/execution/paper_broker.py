"""AUTO GENERATED RUNTIME FILE"""
import random
from backend.app.stacks.portfolio.rebalance import execute_trade
from backend.app.stacks.journal_ledger.ledger import save_log
from backend.app.stacks.strategy.signal import generate_signal
from backend.app.stacks.market_data.price import get_latest_price
from backend.app.stacks.market_data.bars import get_bars
from backend.app.stacks.risk.drawdown_guard import healthcheck as drawdown_healthcheck
from backend.app.stacks.risk.kill_switch import is_kill_switch_active
from backend.app.stacks.portfolio.allocator import calculate_position_size
from backend.app.stacks.portfolio.accounting import calculate_live_portfolio_equity
from backend.app.stacks.market_data.feed import get_live_market_price
from backend.app.core.runtime_trace import (
    create_trace_id,
    emit_runtime_step,
)

def healthcheck():
    return {"status": "ok"}

async def process_portfolio_output(
    portfolio_matrix: list,
    portfolio_output: dict,
    *,
    user_id: str,
    trace_id: str | None = None,
):
    normalized_user_id = str(
        user_id
    ).strip()

    if not normalized_user_id:
        raise ValueError(
            "Paper execution user_id cannot be empty"
        )

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
        live_capital = float(equity_matrix.get("current_cash_balance", 100000.00))

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
            )
            return

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

        # 3. Calculate dynamic volatility allocation sizes using the live balance
        sizing_matrix = calculate_position_size(symbol, total_capital=live_capital)
        allocated_capital = float(sizing_matrix.get("allocated_capital", live_capital * 0.01))

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
        live_feed = await get_live_market_price(symbol)
        raw_price = float(live_feed.get("price", 100.00))

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

        await save_log(
            trade_result,
            user_id=normalized_user_id,
            trace_id=trace_id,
        )

        # Execute trade loop over positions matrix
        for position in portfolio_matrix:
            if isinstance(position, dict) and position.get('symbol') == symbol and position.get('signal') != signal:
                new_signal = generate_signal(symbol, get_latest_price(symbol), get_bars(symbol))
                execute_trade(symbol, new_signal)
                await save_log(
                    new_signal,
                    user_id=normalized_user_id,
                )



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

    return {
        "status": "ok",
        "positions": [],
        "count": 0,
        "provider": "paper_broker",
        "scope": "authenticated_account",
    }
