"""Deterministic offline evaluators for the fourth fifteen-strategy batch.

This module performs no provider, database, portfolio, registry, order,
or execution work.
"""

from __future__ import annotations

from math import isfinite, sqrt
from statistics import fmean, median, pstdev
from types import MappingProxyType
from typing import Any, Callable, Mapping, Sequence

from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v3 import (
    _extract,
    _linear_regression,
    _rolling_atr,
)
from backend.app.stacks.strategy.evaluators.bulk_indicator_strategy_contracts_v4 import (
    BULK_INDICATOR_STRATEGY_CONTRACTS_V4_BY_NAME,
)


Bar = Mapping[str, Any]
Result = dict[str, object]


def _result(
    contract: object,
    decision: str,
    reason: str,
    confidence: float = 0.0,
    **evidence: object,
) -> Result:
    bounded = (
        0.0
        if decision in ("HOLD", "ABSTAIN")
        else max(0.0, min(1.0, float(confidence)))
    )

    output: Result = {
        "status": "abstain" if decision == "ABSTAIN" else "ok",
        "strategy_name": getattr(contract, "strategy_name"),
        "evaluator_id": getattr(contract, "evaluator_id"),
        "decision": decision,
        "signal": decision,
        "confidence": bounded,
        "reason": reason,
    }
    output.update(evidence)
    return output


def _abstain(contract: object, reason: str) -> Result:
    return _result(contract, "ABSTAIN", reason)


def _direction(
    contract: object,
    *,
    buy: bool,
    sell: bool,
    strength: float,
    **evidence: object,
) -> Result:
    if buy and not sell:
        return _result(
            contract, "BUY", "buy_transition",
            strength, **evidence,
        )
    if sell and not buy:
        return _result(
            contract, "SELL", "sell_transition",
            strength, **evidence,
        )
    return _result(
        contract, "HOLD", "no_new_transition",
        0.0, **evidence,
    )


def _ratio_distance(value: float, boundary: float) -> float | None:
    if boundary == 0.0:
        return None
    return abs(value - boundary) / abs(boundary)


def _obv(closes: Sequence[float], volumes: Sequence[float]) -> list[float]:
    output = [0.0]
    for index in range(1, len(closes)):
        if closes[index] > closes[index - 1]:
            change = volumes[index]
        elif closes[index] < closes[index - 1]:
            change = -volumes[index]
        else:
            change = 0.0
        output.append(output[-1] + change)
    return output


def _money_flow_multiplier(
    high: float,
    low: float,
    close: float,
) -> float:
    spread = high - low
    if spread == 0.0:
        return 0.0
    return ((close - low) - (high - close)) / spread


def _money_flow_volumes(
    highs: Sequence[float],
    lows: Sequence[float],
    closes: Sequence[float],
    volumes: Sequence[float],
) -> list[float]:
    return [
        _money_flow_multiplier(high, low, close) * volume
        for high, low, close, volume in zip(
            highs, lows, closes, volumes, strict=True
        )
    ]


def _cmf(
    highs: Sequence[float],
    lows: Sequence[float],
    closes: Sequence[float],
    volumes: Sequence[float],
    end: int,
    window: int,
) -> float | None:
    start = end - window + 1
    selected_volume = volumes[start:end + 1]
    denominator = sum(selected_volume)
    if denominator == 0.0:
        return None
    flows = _money_flow_volumes(
        highs[start:end + 1],
        lows[start:end + 1],
        closes[start:end + 1],
        selected_volume,
    )
    return sum(flows) / denominator


def _adl(
    highs: Sequence[float],
    lows: Sequence[float],
    closes: Sequence[float],
    volumes: Sequence[float],
) -> list[float]:
    output: list[float] = []
    total = 0.0
    for high, low, close, volume in zip(
        highs, lows, closes, volumes, strict=True
    ):
        total += _money_flow_multiplier(high, low, close) * volume
        output.append(total)
    return output


def _bandwidth(
    values: Sequence[float],
    end: int,
    window: int,
    deviations: float,
) -> tuple[float, float, float] | None:
    selected = values[end - window + 1:end + 1]
    middle = fmean(selected)
    if middle == 0.0:
        return None
    deviation = pstdev(selected)
    upper = middle + deviations * deviation
    lower = middle - deviations * deviation
    return (upper - lower) / middle, upper, lower


def _nearest_rank(values: Sequence[float], fraction: float) -> float:
    ordered = sorted(values)
    rank = max(1, int((len(ordered) * fraction) + 0.999999999))
    return ordered[rank - 1]


def _regression_channel(
    values: Sequence[float],
) -> tuple[float, float]:
    slope, intercept = _linear_regression(values)
    endpoint = intercept + slope * (len(values) - 1)
    residuals = [
        value - (intercept + slope * index)
        for index, value in enumerate(values)
    ]
    return endpoint, pstdev(residuals)


def _mad_z(values: Sequence[float], scale: float) -> float | None:
    center = median(values)
    mad = median(abs(value - center) for value in values)
    if mad == 0.0:
        return None
    return (values[-1] - center) / (scale * mad)


def _kama(
    values: Sequence[float],
    efficiency_window: int,
    fast_period: int,
    slow_period: int,
) -> list[float | None]:
    output: list[float | None] = [None] * len(values)
    seed = fmean(values[:efficiency_window])
    output[efficiency_window - 1] = seed

    fast = 2.0 / (fast_period + 1.0)
    slow = 2.0 / (slow_period + 1.0)
    current = seed

    for index in range(efficiency_window, len(values)):
        direction = abs(values[index] - values[index - efficiency_window])
        volatility = sum(
            abs(values[position] - values[position - 1])
            for position in range(
                index - efficiency_window + 1,
                index + 1,
            )
        )
        efficiency = 0.0 if volatility == 0.0 else direction / volatility
        smoothing = (efficiency * (fast - slow) + slow) ** 2
        current = current + smoothing * (values[index] - current)
        output[index] = current

    return output


def _evaluate(contract: object, bars: Sequence[Bar]) -> Result:
    extracted = _extract(bars)
    if extracted is None:
        return _abstain(contract, "invalid_truthful_daily_ohlcv")

    opens, highs, lows, closes, volumes = extracted
    minimum = int(getattr(contract, "minimum_bars"))

    if len(closes) < minimum:
        return _abstain(contract, "insufficient_history")

    name = str(getattr(contract, "strategy_name"))
    parameters = getattr(contract, "parameters")

    if name == "On-Balance Volume Trend":
        window = int(parameters["lookback"])
        values = _obv(closes, volumes)
        previous = values[-2] - values[-window - 2]
        current = values[-1] - values[-window - 1]
        return _direction(
            contract,
            buy=previous <= 0.0 < current,
            sell=previous >= 0.0 > current,
            strength=min(1.0, abs(current) / max(sum(volumes[-window:]), 1.0)),
            previous_obv_change=previous,
            current_obv_change=current,
        )

    if name == "Volume Breakout":
        window = int(parameters["volume_window"])
        multiplier = float(parameters["volume_multiplier"])
        previous_mean = fmean(volumes[-window - 2:-2])
        current_mean = fmean(volumes[-window - 1:-1])
        previous_surge = volumes[-2] >= multiplier * previous_mean
        current_surge = volumes[-1] >= multiplier * current_mean
        transition = current_surge and not previous_surge
        return _direction(
            contract,
            buy=transition and closes[-1] > closes[-2],
            sell=transition and closes[-1] < closes[-2],
            strength=min(1.0, volumes[-1] / max(current_mean * multiplier, 1.0) - 1.0),
            previous_volume_surge=previous_surge,
            current_volume_surge=current_surge,
        )

    if name == "Chaikin Money Flow":
        window = int(parameters["window"])
        previous = _cmf(highs, lows, closes, volumes, len(closes) - 2, window)
        current = _cmf(highs, lows, closes, volumes, len(closes) - 1, window)
        if previous is None or current is None:
            return _abstain(contract, "zero_volume_denominator")
        positive = float(parameters["positive_threshold"])
        negative = float(parameters["negative_threshold"])
        return _direction(
            contract,
            buy=previous <= positive < current,
            sell=previous >= negative > current,
            strength=min(1.0, abs(current)),
            previous_cmf=previous,
            current_cmf=current,
        )

    if name == "Accumulation Distribution Line":
        window = int(parameters["lookback"])
        values = _adl(highs, lows, closes, volumes)
        previous = values[-2] - values[-window - 2]
        current = values[-1] - values[-window - 1]
        return _direction(
            contract,
            buy=previous <= 0.0 < current,
            sell=previous >= 0.0 > current,
            strength=min(1.0, abs(current) / max(sum(volumes[-window:]), 1.0)),
            previous_adl_change=previous,
            current_adl_change=current,
        )

    if name == "Bollinger Bandwidth Expansion":
        window = int(parameters["band_window"])
        deviations = float(parameters["deviations"])
        baseline = int(parameters["baseline_window"])
        fraction = float(parameters["compression_percentile"])

        prior = _bandwidth(closes, len(closes) - 2, window, deviations)
        current = _bandwidth(closes, len(closes) - 1, window, deviations)
        historical = [
            _bandwidth(closes, end, window, deviations)
            for end in range(
                len(closes) - baseline - 2,
                len(closes) - 2,
            )
        ]

        if prior is None or current is None or any(item is None for item in historical):
            return _abstain(contract, "zero_middle_band")

        threshold = _nearest_rank(
            [item[0] for item in historical if item is not None],
            fraction,
        )
        compressed = prior[0] <= threshold
        return _direction(
            contract,
            buy=compressed and closes[-1] > current[1],
            sell=compressed and closes[-1] < current[2],
            strength=min(1.0, current[0]),
            prior_bandwidth=prior[0],
            compression_threshold=threshold,
            current_upper_band=current[1],
            current_lower_band=current[2],
        )

    if name in (
        "Channel Trend Following",
        "Breakout with Volume Confirmation",
    ):
        window = int(parameters["window"])
        previous_high = max(highs[-window - 2:-2])
        previous_low = min(lows[-window - 2:-2])
        current_high = max(highs[-window - 1:-1])
        current_low = min(lows[-window - 1:-1])
        buy = closes[-2] <= previous_high and closes[-1] > current_high
        sell = closes[-2] >= previous_low and closes[-1] < current_low

        evidence: dict[str, object] = {
            "prior_window_high": current_high,
            "prior_window_low": current_low,
        }

        if name == "Breakout with Volume Confirmation":
            multiplier = float(parameters["volume_multiplier"])
            previous_mean = fmean(volumes[-window - 2:-2])
            current_mean = fmean(volumes[-window - 1:-1])
            buy = buy and volumes[-1] >= multiplier * current_mean
            sell = sell and volumes[-1] >= multiplier * current_mean
            evidence.update(
                current_mean_volume=current_mean,
                volume_confirmed=volumes[-1] >= multiplier * current_mean,
                previous_mean_volume=previous_mean,
            )

        return _direction(
            contract,
            buy=buy,
            sell=sell,
            strength=min(
                1.0,
                abs(closes[-1] - (current_high if buy else current_low))
                / max(abs(closes[-1]), 1e-12) * 10.0,
            ),
            **evidence,
        )

    if name == "Regression Trend":
        window = int(parameters["window"])
        threshold = float(parameters["normalized_slope_threshold"])
        previous_values = closes[-window - 1:-1]
        current_values = closes[-window:]
        previous_mean = fmean(previous_values)
        current_mean = fmean(current_values)
        if previous_mean == 0.0 or current_mean == 0.0:
            return _abstain(contract, "zero_mean_close")
        previous = _linear_regression(previous_values)[0] / previous_mean
        current = _linear_regression(current_values)[0] / current_mean
        return _direction(
            contract,
            buy=previous <= threshold < current,
            sell=previous >= -threshold > current,
            strength=min(1.0, abs(current) / threshold),
            previous_normalized_slope=previous,
            current_normalized_slope=current,
        )

    if name == "Regression Channel Breakout":
        window = int(parameters["window"])
        width = float(parameters["residual_deviations"])
        previous_endpoint, previous_deviation = _regression_channel(
            closes[-window - 1:-1]
        )
        endpoint, deviation = _regression_channel(closes[-window:])
        previous_upper = previous_endpoint + width * previous_deviation
        previous_lower = previous_endpoint - width * previous_deviation
        upper = endpoint + width * deviation
        lower = endpoint - width * deviation
        return _direction(
            contract,
            buy=closes[-2] <= previous_upper and closes[-1] > upper,
            sell=closes[-2] >= previous_lower and closes[-1] < lower,
            strength=min(1.0, abs(closes[-1] - endpoint) / max(abs(closes[-1]), 1e-12)),
            regression_endpoint=endpoint,
            residual_deviation=deviation,
            upper_channel=upper,
            lower_channel=lower,
        )

    if name == "Momentum with Volatility Filter":
        window = int(parameters["momentum_window"])
        atr_window = int(parameters["atr_window"])
        maximum = float(parameters["maximum_atr_fraction"])
        if closes[-1] == 0.0 or closes[-2] == 0.0:
            return _abstain(contract, "zero_close")
        previous_base = closes[-window - 2]
        current_base = closes[-window - 1]
        if previous_base == 0.0 or current_base == 0.0:
            return _abstain(contract, "zero_momentum_denominator")
        previous = closes[-2] / previous_base - 1.0
        current = closes[-1] / current_base - 1.0
        atr = _rolling_atr(closes, highs, lows, atr_window)[-1]
        if atr is None:
            return _abstain(contract, "atr_unavailable")
        fraction = atr / closes[-1]
        allowed = fraction <= maximum
        return _direction(
            contract,
            buy=allowed and previous <= 0.0 < current,
            sell=allowed and previous >= 0.0 > current,
            strength=min(1.0, abs(current)),
            previous_momentum=previous,
            current_momentum=current,
            atr_fraction=fraction,
            volatility_allowed=allowed,
        )

    if name == "Breakout Retest":
        boundary_window = int(parameters["boundary_window"])
        retest_window = int(parameters["retest_window"])
        tolerance = float(parameters["tolerance"])
        selected: tuple[str, float, int] | None = None

        for breakout_index in range(
            len(closes) - 2,
            len(closes) - retest_window - 2,
            -1,
        ):
            prior_high = max(
                highs[
                    breakout_index - boundary_window:
                    breakout_index
                ]
            )
            prior_low = min(
                lows[
                    breakout_index - boundary_window:
                    breakout_index
                ]
            )
            if closes[breakout_index] > prior_high:
                selected = ("up", prior_high, breakout_index)
                break
            if closes[breakout_index] < prior_low:
                selected = ("down", prior_low, breakout_index)
                break

        if selected is None:
            return _result(contract, "HOLD", "no_unexpired_breakout")

        direction, boundary, breakout_index = selected
        distance = _ratio_distance(
            lows[-1] if direction == "up" else highs[-1],
            boundary,
        )
        if distance is None:
            return _abstain(contract, "zero_breakout_boundary")

        buy = (
            direction == "up"
            and distance <= tolerance
            and closes[-1] > boundary
        )
        sell = (
            direction == "down"
            and distance <= tolerance
            and closes[-1] < boundary
        )
        return _direction(
            contract,
            buy=buy,
            sell=sell,
            strength=max(0.0, 1.0 - distance / tolerance),
            breakout_direction=direction,
            breakout_boundary=boundary,
            breakout_age=len(closes) - 1 - breakout_index,
            relative_retest_distance=distance,
        )

    if name == "Support Resistance Reversion":
        window = int(parameters["window"])
        tolerance = float(parameters["tolerance"])
        support = min(lows[-window - 1:-1])
        resistance = max(highs[-window - 1:-1])
        support_distance = _ratio_distance(lows[-1], support)
        resistance_distance = _ratio_distance(highs[-1], resistance)
        if support_distance is None or resistance_distance is None:
            return _abstain(contract, "zero_channel_boundary")
        return _direction(
            contract,
            buy=(
                support_distance <= tolerance
                and closes[-1] > opens[-1]
                and closes[-1] > closes[-2]
            ),
            sell=(
                resistance_distance <= tolerance
                and closes[-1] < opens[-1]
                and closes[-1] < closes[-2]
            ),
            strength=max(
                0.0,
                1.0 - min(support_distance, resistance_distance) / tolerance,
            ),
            support=support,
            resistance=resistance,
            support_distance=support_distance,
            resistance_distance=resistance_distance,
        )

    if name == "Median Reversion":
        window = int(parameters["window"])
        deviation = float(parameters["deviation_fraction"])
        previous_median = median(closes[-window - 1:-1])
        current_median = median(closes[-window:])
        previous_lower = previous_median * (1.0 - deviation)
        previous_upper = previous_median * (1.0 + deviation)
        current_lower = current_median * (1.0 - deviation)
        current_upper = current_median * (1.0 + deviation)
        return _direction(
            contract,
            buy=closes[-2] >= previous_lower and closes[-1] < current_lower,
            sell=closes[-2] <= previous_upper and closes[-1] > current_upper,
            strength=min(1.0, abs(closes[-1] - current_median) / max(abs(current_median), 1e-12)),
            rolling_median=current_median,
            lower_boundary=current_lower,
            upper_boundary=current_upper,
        )

    if name == "MAD Z-Score Reversion":
        window = int(parameters["window"])
        entry = float(parameters["entry_z"])
        scale = float(parameters["scale"])
        previous = _mad_z(closes[-window - 1:-1], scale)
        current = _mad_z(closes[-window:], scale)
        if previous is None or current is None:
            return _abstain(contract, "zero_mad")
        return _direction(
            contract,
            buy=previous >= -entry and current < -entry,
            sell=previous <= entry and current > entry,
            strength=min(1.0, abs(current) / max(entry, 1e-12)),
            previous_robust_zscore=previous,
            current_robust_zscore=current,
        )

    if name == "KAMA Trend":
        efficiency = int(parameters["efficiency_window"])
        fast = int(parameters["fast_period"])
        slow = int(parameters["slow_period"])
        values = _kama(closes, efficiency, fast, slow)
        previous = values[-2]
        current = values[-1]
        if previous is None or current is None:
            return _abstain(contract, "kama_unavailable")
        return _direction(
            contract,
            buy=closes[-2] <= previous and closes[-1] > current,
            sell=closes[-2] >= previous and closes[-1] < current,
            strength=min(1.0, abs(closes[-1] - current) / max(abs(closes[-1]), 1e-12) * 10.0),
            previous_kama=previous,
            current_kama=current,
        )

    return _abstain(contract, "unsupported_strategy_contract")


def _make_evaluator(strategy_name: str) -> Callable[[Sequence[Bar]], Result]:
    contract = BULK_INDICATOR_STRATEGY_CONTRACTS_V4_BY_NAME[strategy_name]

    def evaluator(bars: Sequence[Bar]) -> Result:
        return _evaluate(contract, bars)

    evaluator.__name__ = (
        "evaluate_"
        + strategy_name.lower().replace("-", "_").replace(" ", "_")
    )
    return evaluator


BULK_OFFLINE_EVALUATORS_V4 = MappingProxyType(
    {
        name: _make_evaluator(name)
        for name in BULK_INDICATOR_STRATEGY_CONTRACTS_V4_BY_NAME
    }
)


def evaluate_bulk_indicator_strategy_v4(
    strategy_name: str,
    bars: Sequence[Bar],
) -> Result:
    normalized = str(strategy_name).strip()
    evaluator = BULK_OFFLINE_EVALUATORS_V4.get(normalized)

    if evaluator is None:
        raise KeyError(
            "No deterministic fourth-batch evaluator: "
            f"{normalized or '<empty>'}"
        )

    return evaluator(bars)


def healthcheck() -> dict[str, object]:
    return {
        "status": "ok",
        "strategy_count": len(BULK_OFFLINE_EVALUATORS_V4),
        "offline_only": True,
        "registry_activated": False,
        "execution_enabled": False,
    }
