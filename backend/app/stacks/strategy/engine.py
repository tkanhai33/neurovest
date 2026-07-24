"""DOMAIN_LOGIC_V1 strategy engine."""

from backend.app.stacks.market_data.price import get_latest_price
from backend.app.stacks.market_data.bars import get_bars
from backend.app.stacks.strategy.signal import generate_signal
from backend.app.stacks.portfolio.rebalance import rebalance_portfolio  # Import the rebalance function

def generate_strategy_decision(
    symbol: str,
    replay_bars: list[dict] | None = None,
) -> dict:
    """
    Produce the canonical synchronous strategy-decision envelope.

    This function remains database-free and audit-free. It preserves
    the original strategy signal while retaining the existing string
    signal surface used by current consumers.
    """

    price = get_latest_price(
        symbol
    )

    if replay_bars is None:
        bars = get_bars(
            symbol,
            limit=50,
        )
    else:
        bars = replay_bars

    strategy_signal = generate_signal(
        symbol,
        price,
        bars,
    )

    status = strategy_signal.get(
        "status",
        "not_ok",
    )

    action = strategy_signal.get(
        "action",
        "hold",
    )

    decision = strategy_signal.get(
        "decision",
        str(
            action
        ).upper(),
    )

    confidence_value = strategy_signal.get(
        "confidence",
        0.0,
    )

    if isinstance(
        confidence_value,
        (
            int,
            float,
        ),
    ):
        confidence = float(
            confidence_value
        )

    else:
        confidence = 0.0

    portfolio_output = None
    envelope_status = status

    if status == "ok":
        portfolio_output = rebalance_portfolio(
            strategy_signal
        )

        envelope_status = portfolio_output.get(
            "status",
            status,
        )

    return {
        "status": envelope_status,
        "symbol": strategy_signal.get(
            "symbol",
            symbol,
        ),
        "signal": str(
            action
        ),
        "decision": str(
            decision
        ),
        "confidence": confidence,
        "strategy_signal": strategy_signal,
        "portfolio_output": portfolio_output,
    }
