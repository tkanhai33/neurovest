"""DOMAIN_LOGIC_V1 portfolio rebalance planning."""

from stacks.portfolio.allocator import allocate_cash


def build_rebalance_plan(strategy_decision: dict, cash: float = 1000.0) -> dict:
    signal = strategy_decision["signal"]
    allocation = allocate_cash(signal, cash=cash)
    return {
        "symbol": strategy_decision["symbol"],
        "allocation": allocation,
        "status": "planned",
    }
