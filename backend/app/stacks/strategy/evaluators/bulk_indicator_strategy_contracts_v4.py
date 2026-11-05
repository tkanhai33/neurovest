"""Deterministic contracts for the fourth fifteen-strategy batch.

Contracts only. This module performs no provider, database, portfolio,
execution, or registry work.
"""

from types import MappingProxyType

from backend.app.stacks.strategy.evaluators.bulk_indicator_strategy_contracts_v3 import (
    _contract,
    _parameters,
)


ON_BALANCE_VOLUME_TREND = _contract(
    strategy_name="On-Balance Volume Trend",
    evaluator_id="on_balance_volume_trend_v1",
    family="volume_trend",
    minimum_bars=22,
    parameters=_parameters(
        lookback=20,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when the current OBV is above its value 20 bars earlier "
        "and the previous bar was not above its corresponding "
        "20-bar-earlier OBV value."
    ),
    sell_rule=(
        "SELL when the current OBV is below its value 20 bars earlier "
        "and the previous bar was not below its corresponding "
        "20-bar-earlier OBV value."
    ),
    hold_rule="HOLD when no new 20-bar OBV trend transition occurs.",
)

VOLUME_BREAKOUT = _contract(
    strategy_name="Volume Breakout",
    evaluator_id="volume_breakout_v1",
    family="volume_surge",
    minimum_bars=22,
    parameters=_parameters(
        volume_window=20,
        volume_multiplier=1.5,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when volume crosses from below to at least 1.5 times "
        "its respective prior 20-bar mean and current close is above "
        "the prior close."
    ),
    sell_rule=(
        "SELL when volume crosses from below to at least 1.5 times "
        "its respective prior 20-bar mean and current close is below "
        "the prior close."
    ),
    hold_rule=(
        "HOLD when no new volume-surge transition occurs or current "
        "close equals the prior close."
    ),
)

CHAIKIN_MONEY_FLOW = _contract(
    strategy_name="Chaikin Money Flow",
    evaluator_id="chaikin_money_flow_v1",
    family="volume_flow",
    minimum_bars=21,
    parameters=_parameters(
        window=20,
        positive_threshold=0.05,
        negative_threshold=-0.05,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when 20-bar CMF crosses from at or below 0.05 to above "
        "0.05."
    ),
    sell_rule=(
        "SELL when 20-bar CMF crosses from at or above -0.05 to below "
        "-0.05."
    ),
    hold_rule=(
        "HOLD when neither CMF threshold is newly crossed; when high equals low, that bar's money-flow multiplier is zero."
    ),
)

ACCUMULATION_DISTRIBUTION_LINE = _contract(
    strategy_name="Accumulation Distribution Line",
    evaluator_id="accumulation_distribution_line_v1",
    family="volume_flow_trend",
    minimum_bars=22,
    parameters=_parameters(
        lookback=20,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when the current ADL is above its value 20 bars earlier "
        "and the previous comparison was not positive."
    ),
    sell_rule=(
        "SELL when the current ADL is below its value 20 bars earlier "
        "and the previous comparison was not negative."
    ),
    hold_rule=(
        "HOLD when no new 20-bar ADL direction transition occurs; "
        "when high equals low, that bar's money-flow multiplier is "
        "zero."
    ),
)

BOLLINGER_BANDWIDTH_EXPANSION = _contract(
    strategy_name="Bollinger Bandwidth Expansion",
    evaluator_id="bollinger_bandwidth_expansion_v1",
    family="volatility_breakout",
    minimum_bars=121,
    parameters=_parameters(
        band_window=20,
        deviations=2.0,
        baseline_window=100,
        compression_percentile=0.20,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when the prior bar's 20-bar Bollinger bandwidth was at "
        "or below the nearest-rank twentieth percentile of the "
        "preceding 100 completed bandwidth values and current close "
        "breaks above the current upper band."
    ),
    sell_rule=(
        "SELL under the same prior-bar compression condition when "
        "current close breaks below the current lower band."
    ),
    hold_rule=(
        "HOLD when compression is absent or no directional band break "
        "occurs; ABSTAIN when the middle band is zero."
    ),
)

CHANNEL_TREND_FOLLOWING = _contract(
    strategy_name="Channel Trend Following",
    evaluator_id="channel_trend_following_v1",
    family="channel_breakout",
    minimum_bars=22,
    parameters=_parameters(
        window=20,
    ),
    transition_only=True,
    buy_rule="BUY when close newly exceeds the high of the prior 20 bars.",
    sell_rule="SELL when close newly falls below the low of the prior 20 bars.",
    hold_rule="HOLD when no new prior-channel boundary break occurs.",
)

REGRESSION_TREND = _contract(
    strategy_name="Regression Trend",
    evaluator_id="regression_trend_v1",
    family="regression_trend",
    minimum_bars=21,
    parameters=_parameters(
        window=20,
        normalized_slope_threshold=0.001,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when the 20-bar least-squares close slope divided by the "
        "window mean close crosses above 0.001."
    ),
    sell_rule=(
        "SELL when the normalized 20-bar regression slope crosses "
        "below -0.001."
    ),
    hold_rule=(
        "HOLD when neither normalized slope threshold is crossed; "
        "ABSTAIN when mean close is zero."
    ),
)

REGRESSION_CHANNEL_BREAKOUT = _contract(
    strategy_name="Regression Channel Breakout",
    evaluator_id="regression_channel_breakout_v1",
    family="regression_breakout",
    minimum_bars=21,
    parameters=_parameters(
        window=20,
        residual_deviations=2.0,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when close newly exceeds the 20-bar regression endpoint "
        "plus two population standard deviations of regression "
        "residuals."
    ),
    sell_rule=(
        "SELL when close newly falls below the regression endpoint "
        "minus two population standard deviations of residuals."
    ),
    hold_rule=(
        "HOLD when no new regression-channel break occurs; when "
        "residual deviation is zero, use the zero-width regression "
        "endpoint as both channel boundaries."
    ),
)

MOMENTUM_WITH_VOLATILITY_FILTER = _contract(
    strategy_name="Momentum with Volatility Filter",
    evaluator_id="momentum_with_volatility_filter_v1",
    family="filtered_momentum",
    minimum_bars=22,
    parameters=_parameters(
        momentum_window=20,
        atr_window=14,
        maximum_atr_fraction=0.05,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when 20-bar close return newly becomes positive while "
        "14-bar ATR divided by close is at or below 0.05."
    ),
    sell_rule=(
        "SELL when 20-bar close return newly becomes negative while "
        "14-bar ATR divided by close is at or below 0.05."
    ),
    hold_rule=(
        "HOLD when volatility exceeds the filter or momentum has no "
        "new directional transition; ABSTAIN when close is zero."
    ),
)

BREAKOUT_WITH_VOLUME_CONFIRMATION = _contract(
    strategy_name="Breakout with Volume Confirmation",
    evaluator_id="breakout_with_volume_confirmation_v1",
    family="volume_breakout",
    minimum_bars=22,
    parameters=_parameters(
        window=20,
        volume_multiplier=1.5,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when close newly exceeds the prior 20-bar high and "
        "volume is at least 1.5 times prior 20-bar mean volume."
    ),
    sell_rule=(
        "SELL when close newly falls below the prior 20-bar low and "
        "volume is at least 1.5 times prior 20-bar mean volume."
    ),
    hold_rule="HOLD when no volume-confirmed boundary break occurs.",
)

BREAKOUT_RETEST = _contract(
    strategy_name="Breakout Retest",
    evaluator_id="breakout_retest_v1",
    family="breakout_retest",
    minimum_bars=27,
    parameters=_parameters(
        boundary_window=20,
        retest_window=5,
        tolerance=0.005,
    ),
    transition_only=True,
    buy_rule=(
        "BUY using the most recent breakout when a close above its "
        "preceding 20-bar high occurred within the prior five "
        "completed bars and the absolute current-low-to-boundary "
        "distance divided by the absolute nonzero boundary is at "
        "most 0.005 while current close remains above the boundary."
    ),
    sell_rule=(
        "SELL using the most recent breakout when a close below its "
        "preceding 20-bar low occurred within the prior five "
        "completed bars and the absolute current-high-to-boundary "
        "distance divided by the absolute nonzero boundary is at "
        "most 0.005 while current close remains below the boundary."
    ),
    hold_rule=(
        "HOLD when the most recent unexpired breakout boundary has "
        "no successful first qualifying retest; ABSTAIN when that "
        "boundary is zero."
    ),
)

SUPPORT_RESISTANCE_REVERSION = _contract(
    strategy_name="Support Resistance Reversion",
    evaluator_id="support_resistance_reversion_v1",
    family="channel_reversion",
    minimum_bars=22,
    parameters=_parameters(
        window=20,
        tolerance=0.005,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when the absolute current-low-to-prior-20-bar-low "
        "distance divided by the absolute nonzero boundary is at "
        "most 0.005 and current close finishes above both open and "
        "the prior close."
    ),
    sell_rule=(
        "SELL when the absolute current-high-to-prior-20-bar-high "
        "distance divided by the absolute nonzero boundary is at "
        "most 0.005 and current close finishes below both open and "
        "the prior close."
    ),
    hold_rule=(
        "HOLD when neither objective boundary rejection occurs; "
        "ABSTAIN when the applicable boundary is zero."
    ),
)

MEDIAN_REVERSION = _contract(
    strategy_name="Median Reversion",
    evaluator_id="median_reversion_v1",
    family="median_reversion",
    minimum_bars=21,
    parameters=_parameters(
        window=20,
        deviation_fraction=0.03,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when close crosses below 97 percent of the rolling "
        "20-bar median close."
    ),
    sell_rule=(
        "SELL when close crosses above 103 percent of the rolling "
        "20-bar median close."
    ),
    hold_rule="HOLD when neither median-deviation boundary is crossed.",
)

MAD_Z_SCORE_REVERSION = _contract(
    strategy_name="MAD Z-Score Reversion",
    evaluator_id="mad_z_score_reversion_v1",
    family="robust_zscore_reversion",
    minimum_bars=21,
    parameters=_parameters(
        window=20,
        entry_z=2.5,
        scale=1.4826,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when robust z-score using median and 1.4826 times MAD "
        "crosses below -2.5."
    ),
    sell_rule=(
        "SELL when the robust z-score crosses above 2.5."
    ),
    hold_rule=(
        "HOLD when neither threshold is crossed; "
        "ABSTAIN when MAD is zero."
    ),
)

KAMA_TREND = _contract(
    strategy_name="KAMA Trend",
    evaluator_id="kama_trend_v1",
    family="adaptive_trend",
    minimum_bars=31,
    parameters=_parameters(
        efficiency_window=10,
        fast_period=2,
        slow_period=30,
    ),
    transition_only=True,
    buy_rule=(
        "BUY when close crosses from at or below KAMA to above KAMA; "
        "KAMA uses a 10-bar efficiency ratio, 2-period fast constant, "
        "30-period slow constant, squared smoothing constant, and a "
        "10-bar SMA seed."
    ),
    sell_rule=(
        "SELL when close crosses from at or above KAMA to below KAMA."
    ),
    hold_rule=(
        "HOLD when close does not cross KAMA; when the "
        "sum of absolute price changes is zero, the efficiency ratio is zero."
    ),
)

BULK_INDICATOR_STRATEGY_CONTRACTS_V4 = (
    ON_BALANCE_VOLUME_TREND,
    VOLUME_BREAKOUT,
    CHAIKIN_MONEY_FLOW,
    ACCUMULATION_DISTRIBUTION_LINE,
    BOLLINGER_BANDWIDTH_EXPANSION,
    CHANNEL_TREND_FOLLOWING,
    REGRESSION_TREND,
    REGRESSION_CHANNEL_BREAKOUT,
    MOMENTUM_WITH_VOLATILITY_FILTER,
    BREAKOUT_WITH_VOLUME_CONFIRMATION,
    BREAKOUT_RETEST,
    SUPPORT_RESISTANCE_REVERSION,
    MEDIAN_REVERSION,
    MAD_Z_SCORE_REVERSION,
    KAMA_TREND,
)

BULK_INDICATOR_STRATEGY_CONTRACTS_V4_BY_NAME = MappingProxyType(
    {
        contract.strategy_name: contract
        for contract in BULK_INDICATOR_STRATEGY_CONTRACTS_V4
    }
)

assert len(BULK_INDICATOR_STRATEGY_CONTRACTS_V4) == 15
assert len(BULK_INDICATOR_STRATEGY_CONTRACTS_V4_BY_NAME) == 15
assert all(
    (
        contract.strategy_name
        and contract.evaluator_id
        and contract.family
        and contract.minimum_bars >= 2
        and contract.buy_rule
        and contract.sell_rule
        and contract.hold_rule
    )
    for contract in BULK_INDICATOR_STRATEGY_CONTRACTS_V4
)
