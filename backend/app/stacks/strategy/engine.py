"""DOMAIN_LOGIC_V1 strategy engine."""

from backend.app.stacks.market_data.price import get_latest_price
from backend.app.stacks.market_data.bars import (
    HistoricalBarsUnavailableError,
    get_bars,
)
from backend.app.stacks.strategy.signal import generate_signal
from backend.app.stacks.portfolio.rebalance import rebalance_portfolio  # Import the rebalance function
from backend.app.stacks.strategy.model_inference.decision_facade import StrategyDecisionInferenceFacade

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
        try:
            bars = get_bars(
                symbol,
                limit=50,
            )
        except HistoricalBarsUnavailableError as exc:
            strategy_signal = {
                "status": "historical_data_unavailable",
                "symbol": symbol,
                "action": "hold",
                "decision": "ABSTAIN",
                "confidence": 0.0,
                "reason": "truthful_historical_bars_unavailable",
                "error": str(exc),
            }

            return {
                "status": "abstained",
                "symbol": symbol,
                "signal": "hold",
                "decision": "ABSTAIN",
                "confidence": 0.0,
                "strategy_signal": strategy_signal,
                "portfolio_output": None,
            }
    else:
        bars = replay_bars

    if not bars:
        strategy_signal = {
            "status": "insufficient_historical_data",
            "symbol": symbol,
            "action": "hold",
            "decision": "ABSTAIN",
            "confidence": 0.0,
            "reason": "no_truthful_historical_bars",
        }

        return {
            "status": "abstained",
            "symbol": symbol,
            "signal": "hold",
            "decision": "ABSTAIN",
            "confidence": 0.0,
            "strategy_signal": strategy_signal,
            "portfolio_output": None,
        }

    decision_facade = StrategyDecisionInferenceFacade(
        allow_learned_inference=False,
    )

    facade_result = decision_facade.decide(
        fixed_rsi_fallback=lambda: generate_signal(
            symbol,
            price,
            bars,
        ),
        feature_frame=None,
        learned_decider=None,
    )

    strategy_signal = facade_result.signal

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
