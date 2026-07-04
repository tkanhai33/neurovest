"""TEMP_DOCSTRING"""
from stacks.market_data.price import get_latest_price
from stacks.market_data.bars import get_bars
from stacks.market_data.feed import get_feed_snapshot
from stacks.risk.exposure import calculate_exposure
from stacks.risk.limits import check_risk_limits
from stacks.strategy.engine import generate_strategy_decision
from stacks.portfolio.rebalance import build_rebalance_plan
from stacks.journal_ledger.ledger import record_event
def test_market_data_domain_flow():
    price = get_latest_price("RY.TO")
    bars = get_bars("RY.TO", limit=5)
    feed = get_feed_snapshot(["RY.TO"])
    assert price["symbol"] == "RY.TO"
    assert len(bars) == 5
    assert feed["status"] == "ok"
def test_risk_strategy_portfolio_ledger_flow():
    decision = generate_strategy_decision("RY.TO")
    rebalance = build_rebalance_plan(decision, cash=1000)
    exposure = calculate_exposure([{"quantity": 1, "price": decision["signal"]["price"]}])
    risk = check_risk_limits({"quantity": 1, "price": decision["signal"]["price"]}, exposure)
    ledger = record_event("rebalance_planned", rebalance)
    assert decision["status"] == "ok"
    assert rebalance["status"] == "planned"
    assert risk["approved"] is True
    assert len(ledger) == 1
