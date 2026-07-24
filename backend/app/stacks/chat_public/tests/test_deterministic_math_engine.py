from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from backend.app.stacks.chat_public.math_tools import (
    MAX_SEQUENCE_LENGTH,
    MathToolRequest,
    execute_math_tool,
    supported_operations,
)


def calculate(
    operation: str,
    **arguments,
):
    return execute_math_tool(
        MathToolRequest(
            operation=operation,
            arguments=arguments,
        )
    )


def decimal_value(
    result,
    key: str,
) -> Decimal:
    value = result.values[
        key
    ]

    assert isinstance(
        value,
        Decimal,
    )

    return value


def test_registry_is_explicit_and_complete() -> None:
    assert supported_operations() == (
        "arithmetic",
        "cagr",
        "compound_return",
        "descriptive_statistics",
        "expected_value",
        "maximum_drawdown",
        "percent_change",
        "percentage_of",
        "portfolio_weights",
        "position_size",
        "risk_reward",
        "sharpe_ratio",
        "simple_return",
        "sortino_ratio",
        "trade_statistics",
    )


@pytest.mark.parametrize(
    (
        "operator",
        "expected",
    ),
    [
        (
            "add",
            Decimal("0.3"),
        ),
        (
            "subtract",
            Decimal("-0.1"),
        ),
        (
            "multiply",
            Decimal("0.02"),
        ),
        (
            "divide",
            Decimal("0.5"),
        ),
    ],
)
def test_exact_decimal_arithmetic(
    operator: str,
    expected: Decimal,
) -> None:
    result = calculate(
        "arithmetic",
        left="0.1",
        right="0.2",
        operator=operator,
    )

    assert result.succeeded

    assert decimal_value(
        result,
        "result",
    ) == expected


def test_percentage_of() -> None:
    result = calculate(
        "percentage_of",
        percentage="17.5",
        amount="2480",
    )

    assert result.succeeded

    assert decimal_value(
        result,
        "result",
    ) == Decimal(
        "434.000"
    )


def test_percent_change() -> None:
    result = calculate(
        "percent_change",
        original="80",
        new="100",
    )

    assert result.succeeded

    assert decimal_value(
        result,
        "percent_change",
    ) == Decimal(
        "25.00"
    )


def test_simple_return() -> None:
    result = calculate(
        "simple_return",
        beginning_value="100",
        ending_value="125",
    )

    assert decimal_value(
        result,
        "return_decimal",
    ) == Decimal(
        "0.25"
    )


def test_compound_return() -> None:
    result = calculate(
        "compound_return",
        returns=[
            "0.10",
            "-0.05",
            "0.08",
        ],
    )

    assert result.succeeded

    assert decimal_value(
        result,
        "return_decimal",
    ) == Decimal(
        "0.128600"
    )


def test_cagr() -> None:
    result = calculate(
        "cagr",
        beginning_value="10000",
        ending_value="16105.1",
        years="5",
    )

    assert result.succeeded

    assert decimal_value(
        result,
        "cagr_decimal",
    ).quantize(
        Decimal(
            "0.0000001"
        )
    ) == Decimal(
        "0.1000000"
    )


def test_expected_value() -> None:
    result = calculate(
        "expected_value",
        probabilities=[
            "0.6",
            "0.4",
        ],
        outcomes=[
            "100",
            "-50",
        ],
    )

    assert result.succeeded

    assert decimal_value(
        result,
        "expected_value",
    ) == Decimal(
        "40.0"
    )


def test_risk_reward() -> None:
    result = calculate(
        "risk_reward",
        entry_price="50",
        stop_price="48",
        target_price="56",
    )

    assert result.succeeded

    assert decimal_value(
        result,
        "reward_to_risk",
    ) == Decimal(
        "3"
    )


def test_position_size() -> None:
    result = calculate(
        "position_size",
        account_value="25000",
        risk_percent="1",
        entry_price="52.50",
        stop_price="50.00",
    )

    assert result.succeeded

    assert decimal_value(
        result,
        "risk_amount",
    ) == Decimal(
        "250"
    )

    assert decimal_value(
        result,
        "quantity",
    ) == Decimal(
        "100"
    )

    assert decimal_value(
        result,
        "allocated_capital",
    ) == Decimal(
        "5250.00"
    )


def test_portfolio_weights() -> None:
    result = calculate(
        "portfolio_weights",
        values=[
            "100",
            "200",
            "700",
        ],
    )

    assert result.succeeded

    assert decimal_value(
        result,
        "weight_sum",
    ) == Decimal(
        "1.0"
    )

    assert result.values[
        "weights"
    ] == (
        "0.1,0.2,0.7"
    )


def test_descriptive_statistics() -> None:
    result = calculate(
        "descriptive_statistics",
        values=[
            "1",
            "2",
            "3",
            "4",
        ],
        sample=False,
    )

    assert result.succeeded

    assert decimal_value(
        result,
        "mean",
    ) == Decimal(
        "2.5"
    )

    assert decimal_value(
        result,
        "variance",
    ) == Decimal(
        "1.25"
    )


def test_sharpe_ratio_is_deterministic() -> None:
    arguments = {
        "returns": [
            "0.01",
            "0.02",
            "-0.005",
            "0.015",
            "0.004",
        ],
        "risk_free_rate":
            "0.03",
        "periods_per_year":
            "252",
    }

    first = calculate(
        "sharpe_ratio",
        **arguments,
    )

    second = calculate(
        "sharpe_ratio",
        **arguments,
    )

    assert first.succeeded
    assert second.succeeded

    assert first.values == (
        second.values
    )


def test_sortino_ratio_is_deterministic() -> None:
    arguments = {
        "returns": [
            "0.01",
            "0.02",
            "-0.005",
            "0.015",
            "-0.004",
        ],
        "target_return":
            "0",
        "periods_per_year":
            "252",
    }

    first = calculate(
        "sortino_ratio",
        **arguments,
    )

    second = calculate(
        "sortino_ratio",
        **arguments,
    )

    assert first.succeeded
    assert first.values == (
        second.values
    )


def test_maximum_drawdown() -> None:
    result = calculate(
        "maximum_drawdown",
        equity_curve=[
            "100",
            "120",
            "90",
            "95",
            "80",
            "130",
        ],
    )

    assert result.succeeded

    assert decimal_value(
        result,
        "maximum_drawdown_decimal",
    ) == Decimal(
        "-0.33333333333333333333333333333333333333333333333333"
    )

    assert result.values[
        "peak_index"
    ] == 1

    assert result.values[
        "trough_index"
    ] == 4


def test_trade_statistics() -> None:
    result = calculate(
        "trade_statistics",
        profits=[
            "100",
            "-50",
            "200",
            "-100",
            "0",
        ],
    )

    assert result.succeeded

    assert decimal_value(
        result,
        "win_rate_decimal",
    ) == Decimal(
        "0.4"
    )

    assert decimal_value(
        result,
        "profit_factor",
    ) == Decimal(
        "2"
    )

    assert decimal_value(
        result,
        "payoff_ratio",
    ) == Decimal(
        "2"
    )


@pytest.mark.parametrize(
    (
        "operation",
        "arguments",
        "message",
    ),
    [
        (
            "arithmetic",
            {
                "left": "1",
                "right": "0",
                "operator": "divide",
            },
            "Division by zero",
        ),
        (
            "percent_change",
            {
                "original": "0",
                "new": "1",
            },
            "original cannot be zero",
        ),
        (
            "position_size",
            {
                "account_value": "10000",
                "risk_percent": "1",
                "entry_price": "50",
                "stop_price": "50",
            },
            "cannot be equal",
        ),
        (
            "expected_value",
            {
                "probabilities": [
                    "0.4",
                    "0.4",
                ],
                "outcomes": [
                    "10",
                    "20",
                ],
            },
            "must sum to 1",
        ),
    ],
)
def test_invalid_inputs_fail_closed(
    operation: str,
    arguments: dict,
    message: str,
) -> None:
    result = execute_math_tool(
        MathToolRequest(
            operation=operation,
            arguments=arguments,
        )
    )

    assert not result.succeeded
    assert result.status == "error"
    assert result.error is not None
    assert message in result.error


def test_unsupported_operation_fails_closed() -> None:
    result = calculate(
        "eval_python",
        expression="2 + 2",
    )

    assert not result.succeeded
    assert result.error is not None
    assert (
        "Unsupported operation"
        in result.error
    )


def test_sequence_boundary_is_enforced() -> None:
    result = calculate(
        "descriptive_statistics",
        values=[
            "1"
        ] * (
            MAX_SEQUENCE_LENGTH
            + 1
        ),
    )

    assert not result.succeeded
    assert result.error is not None
    assert (
        "maximum sequence length"
        in result.error
    )


@pytest.mark.parametrize(
    "bad_value",
    [
        "NaN",
        "Infinity",
        "-Infinity",
        "",
        None,
        True,
    ],
)
def test_non_finite_or_invalid_values_are_rejected(
    bad_value,
) -> None:
    result = calculate(
        "percentage_of",
        percentage=bad_value,
        amount="100",
    )

    assert not result.succeeded


def test_serialized_result_contains_no_float_values() -> None:
    result = calculate(
        "percentage_of",
        percentage="17.5",
        amount="2480",
    )

    payload = result.as_serializable()

    assert payload[
        "values"
    ][
        "result"
    ] == "434.000"

    assert payload[
        "deterministic"
    ] is True

    assert payload[
        "read_only"
    ] is True


def test_math_engine_has_no_execution_or_network_authority() -> None:
    import ast

    path = Path(
        "backend/app/stacks/chat_public/"
        "math_tools/engine.py"
    )

    source = path.read_text(
        encoding="utf-8",
    )

    tree = ast.parse(
        source
    )

    forbidden_calls = {
        "eval",
        "exec",
        "compile",
        "__import__",
    }

    forbidden_import_roots = {
        "asyncio",
        "httpx",
        "requests",
        "socket",
        "subprocess",
        "urllib",
        "sqlalchemy",
    }

    forbidden_attribute_calls = {
        "place_order",
        "submit_order",
        "execute_order",
        "send_order",
    }

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                root = alias.name.split(
                    "."
                )[0]

                assert (
                    root
                    not in forbidden_import_roots
                )

        if isinstance(
            node,
            ast.ImportFrom,
        ):
            module = (
                node.module
                or ""
            )

            root = module.split(
                "."
            )[0]

            assert (
                root
                not in forbidden_import_roots
            )

        if isinstance(
            node,
            ast.Call,
        ):
            if isinstance(
                node.func,
                ast.Name,
            ):
                assert (
                    node.func.id
                    not in forbidden_calls
                )

            if isinstance(
                node.func,
                ast.Attribute,
            ):
                assert (
                    node.func.attr
                    not in forbidden_attribute_calls
                )
