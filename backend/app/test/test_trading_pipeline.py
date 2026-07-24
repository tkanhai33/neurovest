from __future__ import annotations

import asyncio
import importlib
import inspect
from contextlib import ExitStack
from types import ModuleType
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


MODULE_CANDIDATES = (
    "backend.app.stacks.wolfden_ai.agent_router",
    "app.stacks.wolfden_ai.agent_router",
    "stacks.wolfden_ai.agent_router",
)

DEPENDENCY_MODULE_CANDIDATES = (
    "backend.app.stacks.execution.paper_broker",
    "app.stacks.execution.paper_broker",
    "stacks.execution.paper_broker",
    "backend.app.stacks.risk.kill_switch",
    "app.stacks.risk.kill_switch",
    "stacks.risk.kill_switch",
    "backend.app.stacks.strategy.engine",
    "app.stacks.strategy.engine",
    "stacks.strategy.engine",
    "backend.app.stacks.market_data.price",
    "app.stacks.market_data.price",
    "stacks.market_data.price",
    "backend.app.stacks.portfolio.allocator",
    "app.stacks.portfolio.allocator",
    "stacks.portfolio.allocator",
)

FORBIDDEN_OUTPUT = (
    "Database Log & Inventory Saved",
    "asyncpg",
    "sqlalchemy.pool",
    "attached to a different loop",
    "event loop is closed",
    "was never awaited",
)


def _import_first(
    candidates: tuple[str, ...],
) -> ModuleType:
    errors = []

    for name in candidates:
        try:
            return importlib.import_module(
                name
            )

        except ImportError as exc:
            errors.append(
                f"{name}: {exc}"
            )

    raise ImportError(
        "Unable to import required module:\n"
        + "\n".join(errors)
    )


def _optional_modules() -> list[ModuleType]:
    modules = []

    for name in DEPENDENCY_MODULE_CANDIDATES:
        try:
            module = importlib.import_module(
                name
            )

        except ImportError:
            continue

        if module not in modules:
            modules.append(
                module
            )

    return modules


AGENT_ROUTER = _import_first(
    MODULE_CANDIDATES
)

from backend.app.stacks.execution.paper_broker import process_portfolio_output

monitor_and_process_signals = getattr(
    AGENT_ROUTER,
    "monitor_and_process_signals",
)


def _lookup_modules(
    function: Any,
) -> list[ModuleType]:
    modules = []

    owner = inspect.getmodule(
        function
    )

    if owner is not None:
        modules.append(owner)

        for value in owner.__dict__.values():
            if (
                isinstance(
                    value,
                    ModuleType,
                )
                and value not in modules
            ):
                modules.append(value)

    for module in _optional_modules():
        if module not in modules:
            modules.append(module)

    return modules


def _patch_symbol_everywhere(
    stack: ExitStack,
    function: Any,
    symbol: str,
    replacement: Any,
) -> int:
    patched = 0

    for module in _lookup_modules(
        function
    ):
        if not hasattr(
            module,
            symbol,
        ):
            continue

        stack.enter_context(
            patch.object(
                module,
                symbol,
                replacement,
            )
        )

        patched += 1

    return patched


def _assert_isolated_output(
    captured: str,
) -> None:
    lowered = captured.lower()

    for marker in FORBIDDEN_OUTPUT:
        assert marker.lower() not in lowered, (
            "Unit test leaked through its isolated "
            f"boundary: {marker}"
        )


@pytest.mark.asyncio
async def test_trading_pipeline_success(
    capsys: pytest.CaptureFixture[str],
) -> None:
    save_log = AsyncMock(
        name="save_log"
    )

    execute_trade = MagicMock(
        name="execute_trade",
        return_value={
            "symbol": "AAPL",
            "signal": "buy",
            "status": "executed",
        },
    )

    drawdown_healthcheck = AsyncMock(
        name="drawdown_healthcheck",
        return_value={
            "status": "ok",
        },
    )

    kill_switch = MagicMock(
        name="is_kill_switch_active",
        return_value=False,
    )

    accounting = AsyncMock(
        name="calculate_live_portfolio_equity",
        return_value={
            "current_cash_balance": 100000.00,
        },
    )

    latest_price = MagicMock(
        name="get_latest_price",
        return_value={
            "symbol": "AAPL",
            "price": 150.0,
        },
    )

    bars = MagicMock(
        name="get_bars",
        return_value=[
            {
                "close": 150.0,
            },
            {
                "close": 151.0,
            },
            {
                "close": 152.0,
            },
        ],
    )

    strategy = MagicMock(
        name="generate_strategy_decision",
        return_value={
            "signal": "buy",
            "symbol": "AAPL",
        },
    )

    with ExitStack() as stack:
        assert _patch_symbol_everywhere(
            stack,
            process_portfolio_output,
            "save_log",
            save_log,
        ) >= 1

        _patch_symbol_everywhere(
            stack,
            process_portfolio_output,
            "execute_trade",
            execute_trade,
        )

        _patch_symbol_everywhere(
            stack,
            process_portfolio_output,
            "drawdown_healthcheck",
            drawdown_healthcheck,
        )

        _patch_symbol_everywhere(
            stack,
            process_portfolio_output,
            "is_kill_switch_active",
            kill_switch,
        )

        _patch_symbol_everywhere(
            stack,
            process_portfolio_output,
            "calculate_live_portfolio_equity",
            accounting,
        )

        _patch_symbol_everywhere(
            stack,
            process_portfolio_output,
            "get_latest_price",
            latest_price,
        )

        _patch_symbol_everywhere(
            stack,
            process_portfolio_output,
            "get_bars",
            bars,
        )

        _patch_symbol_everywhere(
            stack,
            process_portfolio_output,
            "generate_strategy_decision",
            strategy,
        )

        await process_portfolio_output(
            [
                {
                    "symbol": "AAPL",
                    "signal": "sell",
                }
            ],
            {
                "signal": "buy",
                "symbol": "AAPL",
            },

            user_id="test-trading-user-1",
        )

    assert save_log.await_count >= 1

    captured = capsys.readouterr()

    _assert_isolated_output(
        captured.out
        + captured.err
    )


@pytest.mark.asyncio
async def test_trading_pipeline_blocked(
    capsys: pytest.CaptureFixture[str],
) -> None:
    save_log = AsyncMock(
        name="save_log"
    )

    execute_trade = MagicMock(
        name="execute_trade"
    )

    drawdown_healthcheck = AsyncMock(
        name="drawdown_healthcheck",
        return_value={
            "status": "ok",
        },
    )

    kill_switch = MagicMock(
        name="is_kill_switch_active",
        return_value=True,
    )

    accounting = AsyncMock(
        name="calculate_live_portfolio_equity",
        return_value={
            "current_cash_balance": 100000.00,
        },
    )

    with ExitStack() as stack:
        assert _patch_symbol_everywhere(
            stack,
            process_portfolio_output,
            "save_log",
            save_log,
        ) >= 1

        _patch_symbol_everywhere(
            stack,
            process_portfolio_output,
            "execute_trade",
            execute_trade,
        )

        _patch_symbol_everywhere(
            stack,
            process_portfolio_output,
            "drawdown_healthcheck",
            drawdown_healthcheck,
        )

        _patch_symbol_everywhere(
            stack,
            process_portfolio_output,
            "is_kill_switch_active",
            kill_switch,
        )

        _patch_symbol_everywhere(
            stack,
            process_portfolio_output,
            "calculate_live_portfolio_equity",
            accounting,
        )

        await process_portfolio_output(
            [
                {
                    "symbol": "AAPL",
                    "signal": "sell",
                }
            ],
            {
                "signal": "buy",
                "symbol": "AAPL",
            },

            user_id="test-trading-user-2",
        )

    assert save_log.await_count >= 1

    logged_payloads = [
        call.args[0]
        for call in save_log.await_args_list
        if call.args
        and isinstance(
            call.args[0],
            dict,
        )
    ]

    assert any(
        payload.get(
            "status"
        )
        in {
            "blocked",
            "blocked_by_risk",
            "kill_switch_active",
            "no_action",
        }
        for payload in logged_payloads
    )

    assert execute_trade.call_count == 0

    captured = capsys.readouterr()

    _assert_isolated_output(
        captured.out
        + captured.err
    )


@pytest.mark.asyncio
async def test_agent_router_trips_kill_switch(
    capsys: pytest.CaptureFixture[str],
) -> None:
    kill_switch_active = MagicMock(
        name="is_kill_switch_active",
        side_effect=(
            [False] * 11
            + [True]
        ),
    )

    set_kill_switch = MagicMock(
        name="set_kill_switch"
    )

    save_log = AsyncMock(
        name="save_log"
    )

    process_output = AsyncMock(
        name="process_portfolio_output"
    )

    drawdown_healthcheck = AsyncMock(
        name="drawdown_healthcheck",
        return_value={
            "status": "ok",
        },
    )

    generate_strategy_decision = MagicMock(
        name="generate_strategy_decision",
        return_value={
            "signal": "buy",
            "symbol": "AAPL",
        },
    )

    get_latest_price = MagicMock(
        name="get_latest_price",
        return_value={
            "symbol": "AAPL",
            "price": 100.0,
        },
    )

    get_bars = MagicMock(
        name="get_bars",
        return_value=[
            {
                "close": 100.0,
            },
            {
                "close": 101.0,
            },
            {
                "close": 102.0,
            },
        ],
    )

    generate_signal = MagicMock(
        name="generate_signal",
        return_value={
            "status": "ok",
            "action": "buy",
            "symbol": "AAPL",
        },
    )

    async def no_wait(
        *_args: Any,
        **_kwargs: Any,
    ) -> None:
        return None

    with ExitStack() as stack:
        assert _patch_symbol_everywhere(
            stack,
            monitor_and_process_signals,
            "is_kill_switch_active",
            kill_switch_active,
        ) >= 1

        _patch_symbol_everywhere(
            stack,
            monitor_and_process_signals,
            "set_kill_switch",
            set_kill_switch,
        )

        assert _patch_symbol_everywhere(
            stack,
            monitor_and_process_signals,
            "save_log",
            save_log,
        ) >= 1

        _patch_symbol_everywhere(
            stack,
            monitor_and_process_signals,
            "process_portfolio_output",
            process_output,
        )

        _patch_symbol_everywhere(
            stack,
            monitor_and_process_signals,
            "drawdown_healthcheck",
            drawdown_healthcheck,
        )

        _patch_symbol_everywhere(
            stack,
            monitor_and_process_signals,
            "generate_strategy_decision",
            generate_strategy_decision,
        )

        _patch_symbol_everywhere(
            stack,
            monitor_and_process_signals,
            "get_latest_price",
            get_latest_price,
        )

        _patch_symbol_everywhere(
            stack,
            monitor_and_process_signals,
            "get_bars",
            get_bars,
        )

        _patch_symbol_everywhere(
            stack,
            monitor_and_process_signals,
            "generate_signal",
            generate_signal,
        )

        owner = inspect.getmodule(
            monitor_and_process_signals
        )

        if (
            owner is not None
            and hasattr(
                owner,
                "time",
            )
            and hasattr(
                owner.time,
                "sleep",
            )
        ):
            stack.enter_context(
                patch.object(
                    owner.time,
                    "sleep",
                    return_value=None,
                )
            )

        if (
            owner is not None
            and hasattr(
                owner,
                "asyncio",
            )
            and hasattr(
                owner.asyncio,
                "sleep",
            )
        ):
            stack.enter_context(
                patch.object(
                    owner.asyncio,
                    "sleep",
                    new=no_wait,
                )
            )

        try:
            await asyncio.wait_for(
                monitor_and_process_signals(),
                timeout=3.0,
            )

        except (
            StopIteration,
            StopAsyncIteration,
        ):
            pass

    assert kill_switch_active.call_count >= 1

    assert (
        set_kill_switch.call_count >= 1
        or save_log.await_count >= 1
    )

    captured = capsys.readouterr()

    _assert_isolated_output(
        captured.out
        + captured.err
    )
