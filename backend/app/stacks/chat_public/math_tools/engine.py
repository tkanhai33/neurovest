"""
Canonical deterministic math engine for NeuroVest.

Design constraints:
- Decimal arithmetic for monetary and financial calculations;
- strict operation registry;
- explicit named arguments only;
- bounded scalar and sequence inputs;
- no eval, exec, AST execution, expression language, or arbitrary code;
- no network, database, broker, order, or live-trading access;
- controlled failures returned as MathToolResult values.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from decimal import (
    Decimal,
    InvalidOperation,
    ROUND_FLOOR,
    localcontext,
)
from typing import Any

from backend.app.stacks.chat_public.math_tools.contracts import (
    MathToolRequest,
    MathToolResult,
)


MATH_PRECISION = 50
MAX_ABSOLUTE_INPUT = Decimal(
    "1e100"
)
MAX_SEQUENCE_LENGTH = 10_000

ZERO = Decimal("0")
ONE = Decimal("1")
TWO = Decimal("2")
HUNDRED = Decimal("100")
TRADING_PERIODS_PER_YEAR = Decimal(
    "252"
)


class MathToolError(
    ValueError
):
    """Controlled deterministic calculation error."""


def _decimal(
    value: Any,
    *,
    name: str,
) -> Decimal:
    if isinstance(
        value,
        bool,
    ):
        raise MathToolError(
            f"{name} must be numeric."
        )

    if isinstance(
        value,
        Decimal,
    ):
        number = value
    elif isinstance(
        value,
        int,
    ):
        number = Decimal(
            value
        )
    elif isinstance(
        value,
        float,
    ):
        number = Decimal(
            str(value)
        )
    elif isinstance(
        value,
        str,
    ):
        normalized = value.strip()

        if not normalized:
            raise MathToolError(
                f"{name} cannot be blank."
            )

        try:
            number = Decimal(
                normalized
            )
        except InvalidOperation as error:
            raise MathToolError(
                f"{name} is not a valid decimal number."
            ) from error
    else:
        raise MathToolError(
            f"{name} must be numeric."
        )

    if not number.is_finite():
        raise MathToolError(
            f"{name} must be finite."
        )

    if abs(number) > MAX_ABSOLUTE_INPUT:
        raise MathToolError(
            f"{name} exceeds the supported numeric boundary."
        )

    return number


def _positive(
    value: Any,
    *,
    name: str,
) -> Decimal:
    number = _decimal(
        value,
        name=name,
    )

    if number <= ZERO:
        raise MathToolError(
            f"{name} must be greater than zero."
        )

    return number


def _non_negative(
    value: Any,
    *,
    name: str,
) -> Decimal:
    number = _decimal(
        value,
        name=name,
    )

    if number < ZERO:
        raise MathToolError(
            f"{name} cannot be negative."
        )

    return number


def _sequence(
    value: Any,
    *,
    name: str,
    minimum_length: int = 1,
) -> tuple[Decimal, ...]:
    if (
        isinstance(
            value,
            (str, bytes, dict),
        )
        or not isinstance(
            value,
            Iterable,
        )
    ):
        raise MathToolError(
            f"{name} must be a numeric sequence."
        )

    raw_values = list(
        value
    )

    if len(raw_values) < minimum_length:
        raise MathToolError(
            f"{name} requires at least "
            f"{minimum_length} value(s)."
        )

    if len(raw_values) > MAX_SEQUENCE_LENGTH:
        raise MathToolError(
            f"{name} exceeds the maximum sequence length "
            f"of {MAX_SEQUENCE_LENGTH}."
        )

    return tuple(
        _decimal(
            item,
            name=(
                f"{name}[{index}]"
            ),
        )
        for index, item in enumerate(
            raw_values
        )
    )


def _mean(
    values: tuple[Decimal, ...],
) -> Decimal:
    return sum(
        values,
        ZERO,
    ) / Decimal(
        len(values)
    )


def _population_variance(
    values: tuple[Decimal, ...],
) -> Decimal:
    average = _mean(
        values
    )

    return (
        sum(
            (
                value
                - average
            ) ** 2
            for value in values
        )
        / Decimal(
            len(values)
        )
    )


def _sample_variance(
    values: tuple[Decimal, ...],
) -> Decimal:
    if len(values) < 2:
        raise MathToolError(
            "Sample variance requires at least two values."
        )

    average = _mean(
        values
    )

    return (
        sum(
            (
                value
                - average
            ) ** 2
            for value in values
        )
        / Decimal(
            len(values)
            - 1
        )
    )


def _sqrt(
    value: Decimal,
) -> Decimal:
    if value < ZERO:
        raise MathToolError(
            "Cannot calculate the square root of a negative value."
        )

    with localcontext() as context:
        context.prec = (
            MATH_PRECISION
        )

        return value.sqrt(
            context=context
        )


def _power_fraction(
    base: Decimal,
    exponent: Decimal,
) -> Decimal:
    if base <= ZERO:
        raise MathToolError(
            "Fractional powers require a positive base."
        )

    with localcontext() as context:
        context.prec = (
            MATH_PRECISION
        )

        return (
            exponent
            * base.ln(
                context=context
            )
        ).exp(
            context=context
        )


def _success(
    operation: str,
    *,
    values: dict[
        str,
        Decimal | int | str | bool | None
    ],
    formula: str,
) -> MathToolResult:
    return MathToolResult(
        operation=operation,
        status="success",
        values=values,
        formula=formula,
        precision=MATH_PRECISION,
        error=None,
    )


def _failure(
    operation: str,
    error: Exception,
) -> MathToolResult:
    return MathToolResult(
        operation=operation,
        status="error",
        values={},
        formula="",
        precision=MATH_PRECISION,
        error=(
            f"{type(error).__name__}: "
            f"{error}"
        ),
    )


def _arithmetic(
    arguments: dict[str, Any],
) -> MathToolResult:
    left = _decimal(
        arguments.get(
            "left"
        ),
        name="left",
    )

    right = _decimal(
        arguments.get(
            "right"
        ),
        name="right",
    )

    operator = str(
        arguments.get(
            "operator",
            "",
        )
    ).strip()

    if operator == "add":
        result = left + right
        symbol = "+"
    elif operator == "subtract":
        result = left - right
        symbol = "-"
    elif operator == "multiply":
        result = left * right
        symbol = "*"
    elif operator == "divide":
        if right == ZERO:
            raise MathToolError(
                "Division by zero is not permitted."
            )

        result = left / right
        symbol = "/"
    else:
        raise MathToolError(
            "operator must be one of: "
            "add, subtract, multiply, divide."
        )

    return _success(
        "arithmetic",
        values={
            "result":
                result,
        },
        formula=(
            f"left {symbol} right"
        ),
    )


def _percentage_of(
    arguments: dict[str, Any],
) -> MathToolResult:
    percentage = _decimal(
        arguments.get(
            "percentage"
        ),
        name="percentage",
    )

    amount = _decimal(
        arguments.get(
            "amount"
        ),
        name="amount",
    )

    result = (
        percentage
        / HUNDRED
        * amount
    )

    return _success(
        "percentage_of",
        values={
            "result":
                result,
            "percentage":
                percentage,
            "amount":
                amount,
        },
        formula=(
            "(percentage / 100) * amount"
        ),
    )


def _percent_change(
    arguments: dict[str, Any],
) -> MathToolResult:
    original = _decimal(
        arguments.get(
            "original"
        ),
        name="original",
    )

    new = _decimal(
        arguments.get(
            "new"
        ),
        name="new",
    )

    if original == ZERO:
        raise MathToolError(
            "original cannot be zero."
        )

    change = new - original
    percent = (
        change
        / original
        * HUNDRED
    )

    return _success(
        "percent_change",
        values={
            "change":
                change,
            "percent_change":
                percent,
        },
        formula=(
            "((new - original) / original) * 100"
        ),
    )


def _simple_return(
    arguments: dict[str, Any],
) -> MathToolResult:
    beginning = _positive(
        arguments.get(
            "beginning_value"
        ),
        name="beginning_value",
    )

    ending = _decimal(
        arguments.get(
            "ending_value"
        ),
        name="ending_value",
    )

    result = (
        ending
        / beginning
    ) - ONE

    return _success(
        "simple_return",
        values={
            "return_decimal":
                result,
            "return_percent":
                result * HUNDRED,
        },
        formula=(
            "(ending_value / beginning_value) - 1"
        ),
    )


def _compound_return(
    arguments: dict[str, Any],
) -> MathToolResult:
    returns = _sequence(
        arguments.get(
            "returns"
        ),
        name="returns",
    )

    growth = ONE

    for value in returns:
        if value <= -ONE:
            raise MathToolError(
                "Each return must be greater than -1."
            )

        growth *= (
            ONE
            + value
        )

    result = growth - ONE

    return _success(
        "compound_return",
        values={
            "return_decimal":
                result,
            "return_percent":
                result * HUNDRED,
            "period_count":
                len(returns),
        },
        formula=(
            "product(1 + return_i) - 1"
        ),
    )


def _cagr(
    arguments: dict[str, Any],
) -> MathToolResult:
    beginning = _positive(
        arguments.get(
            "beginning_value"
        ),
        name="beginning_value",
    )

    ending = _positive(
        arguments.get(
            "ending_value"
        ),
        name="ending_value",
    )

    years = _positive(
        arguments.get(
            "years"
        ),
        name="years",
    )

    ratio = (
        ending
        / beginning
    )

    result = (
        _power_fraction(
            ratio,
            ONE / years,
        )
        - ONE
    )

    return _success(
        "cagr",
        values={
            "cagr_decimal":
                result,
            "cagr_percent":
                result * HUNDRED,
        },
        formula=(
            "(ending_value / beginning_value) "
            "** (1 / years) - 1"
        ),
    )


def _expected_value(
    arguments: dict[str, Any],
) -> MathToolResult:
    probabilities = _sequence(
        arguments.get(
            "probabilities"
        ),
        name="probabilities",
    )

    outcomes = _sequence(
        arguments.get(
            "outcomes"
        ),
        name="outcomes",
    )

    if len(
        probabilities
    ) != len(
        outcomes
    ):
        raise MathToolError(
            "probabilities and outcomes must have equal lengths."
        )

    if any(
        probability < ZERO
        or probability > ONE
        for probability in probabilities
    ):
        raise MathToolError(
            "Each probability must be between 0 and 1."
        )

    probability_total = sum(
        probabilities,
        ZERO,
    )

    tolerance = Decimal(
        "1e-12"
    )

    if abs(
        probability_total
        - ONE
    ) > tolerance:
        raise MathToolError(
            "Probabilities must sum to 1."
        )

    result = sum(
        probability
        * outcome
        for probability, outcome in zip(
            probabilities,
            outcomes,
            strict=True,
        )
    )

    return _success(
        "expected_value",
        values={
            "expected_value":
                result,
            "outcome_count":
                len(outcomes),
        },
        formula=(
            "sum(probability_i * outcome_i)"
        ),
    )


def _risk_reward(
    arguments: dict[str, Any],
) -> MathToolResult:
    entry = _decimal(
        arguments.get(
            "entry_price"
        ),
        name="entry_price",
    )

    stop = _decimal(
        arguments.get(
            "stop_price"
        ),
        name="stop_price",
    )

    target = _decimal(
        arguments.get(
            "target_price"
        ),
        name="target_price",
    )

    risk = abs(
        entry
        - stop
    )

    reward = abs(
        target
        - entry
    )

    if risk == ZERO:
        raise MathToolError(
            "Entry and stop prices cannot be equal."
        )

    ratio = reward / risk

    return _success(
        "risk_reward",
        values={
            "risk_per_unit":
                risk,
            "reward_per_unit":
                reward,
            "reward_to_risk":
                ratio,
        },
        formula=(
            "abs(target - entry) / abs(entry - stop)"
        ),
    )


def _position_size(
    arguments: dict[str, Any],
) -> MathToolResult:
    account_value = _positive(
        arguments.get(
            "account_value"
        ),
        name="account_value",
    )

    risk_percent = _positive(
        arguments.get(
            "risk_percent"
        ),
        name="risk_percent",
    )

    entry = _decimal(
        arguments.get(
            "entry_price"
        ),
        name="entry_price",
    )

    stop = _decimal(
        arguments.get(
            "stop_price"
        ),
        name="stop_price",
    )

    whole_units = bool(
        arguments.get(
            "whole_units",
            True,
        )
    )

    risk_amount = (
        account_value
        * risk_percent
        / HUNDRED
    )

    risk_per_unit = abs(
        entry
        - stop
    )

    if risk_per_unit == ZERO:
        raise MathToolError(
            "Entry and stop prices cannot be equal."
        )

    exact_quantity = (
        risk_amount
        / risk_per_unit
    )

    quantity: Decimal

    if whole_units:
        quantity = exact_quantity.to_integral_value(
            rounding=ROUND_FLOOR
        )
    else:
        quantity = exact_quantity

    allocated_capital = (
        quantity
        * entry
    )

    return _success(
        "position_size",
        values={
            "risk_amount":
                risk_amount,
            "risk_per_unit":
                risk_per_unit,
            "exact_quantity":
                exact_quantity,
            "quantity":
                quantity,
            "allocated_capital":
                allocated_capital,
            "whole_units":
                whole_units,
        },
        formula=(
            "(account_value * risk_percent / 100) "
            "/ abs(entry_price - stop_price)"
        ),
    )


def _portfolio_weights(
    arguments: dict[str, Any],
) -> MathToolResult:
    values = _sequence(
        arguments.get(
            "values"
        ),
        name="values",
    )

    if any(
        value < ZERO
        for value in values
    ):
        raise MathToolError(
            "Portfolio values cannot be negative."
        )

    total = sum(
        values,
        ZERO,
    )

    if total == ZERO:
        raise MathToolError(
            "Portfolio total cannot be zero."
        )

    weights = tuple(
        value
        / total
        for value in values
    )

    serializable_weights = ",".join(
        format(
            weight,
            "f",
        )
        for weight in weights
    )

    return _success(
        "portfolio_weights",
        values={
            "total_value":
                total,
            "weights":
                serializable_weights,
            "weight_sum":
                sum(
                    weights,
                    ZERO,
                ),
            "position_count":
                len(values),
        },
        formula=(
            "position_value_i / total_portfolio_value"
        ),
    )


def _descriptive_statistics(
    arguments: dict[str, Any],
) -> MathToolResult:
    values = _sequence(
        arguments.get(
            "values"
        ),
        name="values",
    )

    sample = bool(
        arguments.get(
            "sample",
            False,
        )
    )

    average = _mean(
        values
    )

    variance = (
        _sample_variance(
            values
        )
        if sample
        else _population_variance(
            values
        )
    )

    standard_deviation = _sqrt(
        variance
    )

    return _success(
        "descriptive_statistics",
        values={
            "mean":
                average,
            "variance":
                variance,
            "standard_deviation":
                standard_deviation,
            "sample":
                sample,
            "count":
                len(values),
        },
        formula=(
            "mean, variance, and square root of variance"
        ),
    )


def _sharpe_ratio(
    arguments: dict[str, Any],
) -> MathToolResult:
    returns = _sequence(
        arguments.get(
            "returns"
        ),
        name="returns",
        minimum_length=2,
    )

    risk_free_rate = _decimal(
        arguments.get(
            "risk_free_rate",
            ZERO,
        ),
        name="risk_free_rate",
    )

    periods_per_year = _positive(
        arguments.get(
            "periods_per_year",
            TRADING_PERIODS_PER_YEAR,
        ),
        name="periods_per_year",
    )

    average_return = _mean(
        returns
    )

    standard_deviation = _sqrt(
        _sample_variance(
            returns
        )
    )

    if standard_deviation == ZERO:
        raise MathToolError(
            "Sharpe ratio is undefined when return volatility is zero."
        )

    period_risk_free_rate = (
        risk_free_rate
        / periods_per_year
    )

    ratio = (
        (
            average_return
            - period_risk_free_rate
        )
        / standard_deviation
        * _sqrt(
            periods_per_year
        )
    )

    return _success(
        "sharpe_ratio",
        values={
            "sharpe_ratio":
                ratio,
            "mean_period_return":
                average_return,
            "period_standard_deviation":
                standard_deviation,
            "periods_per_year":
                periods_per_year,
        },
        formula=(
            "((mean_return - annual_risk_free_rate / periods_per_year) "
            "/ sample_standard_deviation) * sqrt(periods_per_year)"
        ),
    )


def _sortino_ratio(
    arguments: dict[str, Any],
) -> MathToolResult:
    returns = _sequence(
        arguments.get(
            "returns"
        ),
        name="returns",
        minimum_length=2,
    )

    target_return = _decimal(
        arguments.get(
            "target_return",
            ZERO,
        ),
        name="target_return",
    )

    periods_per_year = _positive(
        arguments.get(
            "periods_per_year",
            TRADING_PERIODS_PER_YEAR,
        ),
        name="periods_per_year",
    )

    downside_differences = tuple(
        min(
            value
            - target_return,
            ZERO,
        )
        for value in returns
    )

    downside_variance = (
        sum(
            difference ** 2
            for difference in downside_differences
        )
        / Decimal(
            len(
                downside_differences
            )
        )
    )

    downside_deviation = _sqrt(
        downside_variance
    )

    if downside_deviation == ZERO:
        raise MathToolError(
            "Sortino ratio is undefined when downside deviation is zero."
        )

    average_return = _mean(
        returns
    )

    ratio = (
        (
            average_return
            - target_return
        )
        / downside_deviation
        * _sqrt(
            periods_per_year
        )
    )

    return _success(
        "sortino_ratio",
        values={
            "sortino_ratio":
                ratio,
            "mean_period_return":
                average_return,
            "downside_deviation":
                downside_deviation,
            "periods_per_year":
                periods_per_year,
        },
        formula=(
            "((mean_return - target_return) / downside_deviation) "
            "* sqrt(periods_per_year)"
        ),
    )


def _maximum_drawdown(
    arguments: dict[str, Any],
) -> MathToolResult:
    equity_curve = _sequence(
        arguments.get(
            "equity_curve"
        ),
        name="equity_curve",
    )

    if any(
        value <= ZERO
        for value in equity_curve
    ):
        raise MathToolError(
            "Equity-curve values must be greater than zero."
        )

    peak = equity_curve[0]
    maximum_drawdown = ZERO
    peak_index = 0
    trough_index = 0
    active_peak_index = 0

    for index, value in enumerate(
        equity_curve
    ):
        if value > peak:
            peak = value
            active_peak_index = index

        drawdown = (
            value
            / peak
        ) - ONE

        if drawdown < maximum_drawdown:
            maximum_drawdown = drawdown
            peak_index = active_peak_index
            trough_index = index

    return _success(
        "maximum_drawdown",
        values={
            "maximum_drawdown_decimal":
                maximum_drawdown,
            "maximum_drawdown_percent":
                maximum_drawdown
                * HUNDRED,
            "peak_index":
                peak_index,
            "trough_index":
                trough_index,
        },
        formula=(
            "minimum((equity_i / running_peak_i) - 1)"
        ),
    )


def _trade_statistics(
    arguments: dict[str, Any],
) -> MathToolResult:
    profits = _sequence(
        arguments.get(
            "profits"
        ),
        name="profits",
    )

    wins = tuple(
        value
        for value in profits
        if value > ZERO
    )

    losses = tuple(
        value
        for value in profits
        if value < ZERO
    )

    breakeven = tuple(
        value
        for value in profits
        if value == ZERO
    )

    trade_count = len(
        profits
    )

    win_rate = (
        Decimal(
            len(wins)
        )
        / Decimal(
            trade_count
        )
    )

    gross_profit = sum(
        wins,
        ZERO,
    )

    gross_loss = abs(
        sum(
            losses,
            ZERO,
        )
    )

    profit_factor: Decimal | None

    if gross_loss == ZERO:
        profit_factor = None
    else:
        profit_factor = (
            gross_profit
            / gross_loss
        )

    average_win = (
        _mean(
            wins
        )
        if wins
        else ZERO
    )

    average_loss = (
        abs(
            _mean(
                losses
            )
        )
        if losses
        else ZERO
    )

    payoff_ratio: Decimal | None

    if average_loss == ZERO:
        payoff_ratio = None
    else:
        payoff_ratio = (
            average_win
            / average_loss
        )

    return _success(
        "trade_statistics",
        values={
            "trade_count":
                trade_count,
            "win_count":
                len(wins),
            "loss_count":
                len(losses),
            "breakeven_count":
                len(breakeven),
            "win_rate_decimal":
                win_rate,
            "win_rate_percent":
                win_rate
                * HUNDRED,
            "gross_profit":
                gross_profit,
            "gross_loss":
                gross_loss,
            "profit_factor":
                profit_factor,
            "average_win":
                average_win,
            "average_loss":
                average_loss,
            "payoff_ratio":
                payoff_ratio,
        },
        formula=(
            "win rate, gross profit / gross loss, "
            "and average win / average loss"
        ),
    )


OperationHandler = Callable[
    [dict[str, Any]],
    MathToolResult,
]


OPERATION_REGISTRY: dict[
    str,
    OperationHandler,
] = {
    "arithmetic":
        _arithmetic,
    "percentage_of":
        _percentage_of,
    "percent_change":
        _percent_change,
    "simple_return":
        _simple_return,
    "compound_return":
        _compound_return,
    "cagr":
        _cagr,
    "expected_value":
        _expected_value,
    "risk_reward":
        _risk_reward,
    "position_size":
        _position_size,
    "portfolio_weights":
        _portfolio_weights,
    "descriptive_statistics":
        _descriptive_statistics,
    "sharpe_ratio":
        _sharpe_ratio,
    "sortino_ratio":
        _sortino_ratio,
    "maximum_drawdown":
        _maximum_drawdown,
    "trade_statistics":
        _trade_statistics,
}


def supported_operations() -> tuple[
    str,
    ...,
]:
    return tuple(
        sorted(
            OPERATION_REGISTRY
        )
    )


def execute_math_tool(
    request: MathToolRequest,
) -> MathToolResult:
    operation = str(
        request.operation
    ).strip()

    if not operation:
        return _failure(
            operation,
            MathToolError(
                "operation cannot be blank."
            ),
        )

    handler = OPERATION_REGISTRY.get(
        operation
    )

    if handler is None:
        return _failure(
            operation,
            MathToolError(
                "Unsupported operation. Supported operations: "
                + ", ".join(
                    supported_operations()
                )
            ),
        )

    if not isinstance(
        request.arguments,
        dict,
    ):
        return _failure(
            operation,
            MathToolError(
                "arguments must be a dictionary."
            ),
        )

    try:
        with localcontext() as context:
            context.prec = (
                MATH_PRECISION
            )

            return handler(
                dict(
                    request.arguments
                )
            )

    except (
        ArithmeticError,
        InvalidOperation,
        MathToolError,
        TypeError,
        ValueError,
    ) as error:
        return _failure(
            operation,
            error,
        )


__all__ = [
    "MATH_PRECISION",
    "MAX_ABSOLUTE_INPUT",
    "MAX_SEQUENCE_LENGTH",
    "MathToolError",
    "OPERATION_REGISTRY",
    "execute_math_tool",
    "supported_operations",
]
