from backend.app.stacks.strategy.evaluators.multi_symbol_family_v1 import (
    MULTI_SYMBOL_EVALUATORS_V1,
    MULTI_SYMBOL_STRATEGY_NAMES,
)

SECTORS = ("XLK", "XLF", "XLE", "XLV", "XLY", "XLP", "XLI", "XLU", "XLB", "XLRE")


def bars(daily_return: float):
    close = 100.0
    output = []
    for _ in range(253):
        output.append({"close": close})
        close *= 1.0 + daily_return
    return output


def universe():
    values = {symbol: bars(-0.0005) for symbol in SECTORS}
    values["XLK"] = bars(0.002)
    values.update({"SPY": bars(0.002), "TLT": bars(0.0002), "GLD": bars(-0.0002)})
    return values


def test_exact_four_identity():
    assert tuple(MULTI_SYMBOL_EVALUATORS_V1) == MULTI_SYMBOL_STRATEGY_NAMES


def test_four_strategies_are_canonical_and_non_executable():
    data = universe()
    assert MULTI_SYMBOL_EVALUATORS_V1["Asset Class Momentum"]("SPY", data)["decision"] == "BUY"
    assert MULTI_SYMBOL_EVALUATORS_V1["Cross-Asset Trend Confirmation"]("SPY", data)["decision"] == "BUY"
    assert MULTI_SYMBOL_EVALUATORS_V1["Relative Strength Sector Rotation"]("XLK", data)["decision"] == "BUY"
    assert MULTI_SYMBOL_EVALUATORS_V1["Sector Momentum"]("XLK", data)["decision"] == "BUY"
    for evaluator in MULTI_SYMBOL_EVALUATORS_V1.values():
        assert evaluator("XLK", data)["execution_enabled"] is False


def test_missing_primary_fails_closed():
    output = MULTI_SYMBOL_EVALUATORS_V1["Sector Momentum"]("AAPL", universe())
    assert output["decision"] == "ABSTAIN"
