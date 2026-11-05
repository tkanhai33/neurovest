from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, localcontext

# NEUROVEST_13D_R56_VERIFIED_CALCULATIONS
#
# Deterministic, bounded, read-only calculation tools.
# No eval(), execution, network, DB, broker or filesystem access.
# User-provided financial inputs are NOT independently verified.

VERSION = "NEUROVEST_13D_R56_VERIFIED_CALCULATIONS"

MAX_MESSAGE = 1800
MAX_EXPRESSION = 110
MAX_ABS = Decimal("1e24")
MAX_RESULT = 1800

@dataclass(frozen=True)
class CalculationResult:
    kind: str
    expression: str
    result: str
    input_origin: str = "user_supplied"
    verification: str = "arithmetic_verified_only"

def _number(value):
    result = Decimal(str(value).replace(",", ""))

    if not result.is_finite() or abs(result) > MAX_ABS:
        raise ValueError("nonfinite_or_oversized_number")

    return result

def _format(value):
    if not value.is_finite() or abs(value) > MAX_ABS:
        raise ValueError("nonfinite_or_oversized_result")

    result = format(value.normalize(), "f")

    if "." in result:
        result = result.rstrip("0").rstrip(".")

    return result or "0"

def _compute(node, depth=0):
    if depth > 14:
        raise ValueError("expression_too_deep")

    if isinstance(node, ast.Expression):
        return _compute(node.body, depth + 1)

    if isinstance(node, ast.Constant):
        if type(node.value) not in (int, float):
            raise ValueError("invalid_constant")
        return _number(node.value)

    if isinstance(node, ast.UnaryOp):
        value = _compute(node.operand, depth + 1)

        if isinstance(node.op, ast.UAdd):
            return value
        if isinstance(node.op, ast.USub):
            return -value

        raise ValueError("invalid_unary_operator")

    if isinstance(node, ast.BinOp):
        left = _compute(node.left, depth + 1)
        right = _compute(node.right, depth + 1)

        if isinstance(node.op, ast.Add):
            result = left + right
        elif isinstance(node.op, ast.Sub):
            result = left - right
        elif isinstance(node.op, ast.Mult):
            result = left * right
        elif isinstance(node.op, ast.Div):
            if right == 0:
                raise ValueError("division_by_zero")
            result = left / right
        else:
            raise ValueError("unsupported_operator")

        if not result.is_finite() or abs(result) > MAX_ABS:
            raise ValueError("result_out_of_bounds")

        return result

    raise ValueError("unsupported_expression")

def calculate(expression):
    if not isinstance(expression, str):
        raise TypeError("expression_must_be_text")

    expression = expression.strip()

    if not expression or len(expression) > MAX_EXPRESSION:
        raise ValueError("invalid_expression_length")

    if not re.fullmatch(
        r"[0-9.,+\-*/()\s]+",
        expression,
    ):
        raise ValueError("unsupported_characters")

    expression = re.sub(
        r"(?<=\d),(?=\d{3}(?:\D|$))",
        "",
        expression,
    )

    # Remaining commas are invalid.
    if "," in expression:
        raise ValueError("invalid_numeric_format")

    tree = ast.parse(expression, mode="eval")

    if sum(1 for _ in ast.walk(tree)) > 45:
        raise ValueError("expression_too_complex")

    with localcontext() as ctx:
        ctx.prec = 28
        result = _compute(tree)

    return _format(result)

def _amount(token):
    token = token.strip()
    match = re.fullmatch(
        r"\$?\s*([0-9][0-9,]*(?:\.[0-9]+)?)"
        r"\s*(trillion|billion|million|thousand|"
        r"tn|bn|mm|m|k)?",
        token,
        re.I,
    )

    if not match:
        raise ValueError("invalid_amount")

    value = _number(match.group(1))
    unit = (match.group(2) or "").lower()

    multiplier = {
        "": "1",
        "k": "1000",
        "thousand": "1000",
        "m": "1000000",
        "mm": "1000000",
        "million": "1000000",
        "bn": "1000000000",
        "billion": "1000000000",
        "tn": "1000000000000",
        "trillion": "1000000000000",
    }[unit]

    result = value * Decimal(multiplier)

    if abs(result) > MAX_ABS:
        raise ValueError("amount_too_large")

    return result

_AMOUNT = (
    r"\$?\s*[0-9][0-9,]*(?:\.[0-9]+)?"
    r"\s*(?:trillion|billion|million|thousand|"
    r"tn|bn|mm|m|k)?"
)

_FIELD = re.compile(
    r"\b(revenue|sales|cost of revenue|"
    r"cost of goods sold|cogs|"
    r"operating income|net income)\s*"
    r"(?:is|was|=|:)\s*"
    r"(" + _AMOUNT + r")(?=\s*[,;\n.]|\s+and\b|$)",
    re.I,
)

def _financial_values(message):
    values = {}

    aliases = {
        "sales": "revenue",
        "cost of goods sold": "cost_of_revenue",
        "cogs": "cost_of_revenue",
        "cost of revenue": "cost_of_revenue",
        "operating income": "operating_income",
        "net income": "net_income",
        "revenue": "revenue",
    }

    for match in _FIELD.finditer(message):
        key = aliases[match.group(1).lower()]
        value = _amount(match.group(2))

        if key in values and values[key] != value:
            raise ValueError("conflicting_financial_inputs")

        values[key] = value

    return values

def _financial_calculation(message):
    values = _financial_values(message)

    if "revenue" not in values:
        return None

    revenue = values["revenue"]

    if revenue <= 0:
        return None

    lower = message.lower()

    with localcontext() as ctx:
        ctx.prec = 28

        if (
            re.search(r"\bgross\s+(?:profit|margin)\b", lower)
            and "cost_of_revenue" in values
        ):
            cost = values["cost_of_revenue"]
            profit = revenue - cost
            margin = profit / revenue * Decimal(100)

            return CalculationResult(
                kind="financial_gross_margin",
                expression=(
                    "gross_profit = revenue - cost_of_revenue; "
                    "gross_margin = gross_profit / revenue * 100"
                ),
                result=(
                    "gross_profit="
                    + _format(profit)
                    + "; gross_margin_percent="
                    + _format(margin)
                ),
            )

        if (
            re.search(r"\boperating\s+margin\b", lower)
            and "operating_income" in values
        ):
            margin = (
                values["operating_income"]
                / revenue * Decimal(100)
            )

            return CalculationResult(
                kind="financial_operating_margin",
                expression="operating_income / revenue * 100",
                result="operating_margin_percent=" + _format(margin),
            )

        if (
            re.search(r"\bnet\s+margin\b", lower)
            and "net_income" in values
        ):
            margin = (
                values["net_income"]
                / revenue * Decimal(100)
            )

            return CalculationResult(
                kind="financial_net_margin",
                expression="net_income / revenue * 100",
                result="net_margin_percent=" + _format(margin),
            )

    return None

def _arithmetic_calculation(message):
    text = message.strip()

    percent = re.fullmatch(
        r"(?:calculate\s+|what(?:'s| is)\s+)?"
        r"([0-9]+(?:\.[0-9]+)?)\s*%\s+of\s+"
        r"([0-9]+(?:\.[0-9]+)?)\s*[?.]?",
        text,
        re.I,
    )

    if percent:
        with localcontext() as ctx:
            ctx.prec = 28
            result = (
                _number(percent.group(1))
                * _number(percent.group(2))
                / Decimal(100)
            )

        return CalculationResult(
            kind="percentage",
            expression=(
                percent.group(1)
                + "% of "
                + percent.group(2)
            ),
            result=_format(result),
        )

    expression = re.fullmatch(
        r"(?:calculate|compute|evaluate|"
        r"what(?:'s| is))\s+"
        r"([0-9][0-9.,+\-*/()\s]{0,109}?)\s*[?]?",
        text,
        re.I,
    )

    if not expression:
        return None

    expr = expression.group(1).strip()

    if not any(operator in expr for operator in "+-*/"):
        return None

    try:
        value = calculate(expr)
    except (
        SyntaxError, ValueError, InvalidOperation,
        ZeroDivisionError,
    ):
        return None

    return CalculationResult(
        kind="arithmetic",
        expression=expr,
        result=value,
    )

def execute_readonly_calculation(message):
    if not isinstance(message, str):
        return None

    if not message.strip() or len(message) > MAX_MESSAGE:
        return None

    # No tool execution for command, trade, broker, or
    # account-action requests. Preserve existing handlers.
    if re.search(
        r"\b(?:buy|sell|place an order|"
        r"execute trade|withdraw|transfer funds|"
        r"delete account|run shell command)\b",
        message,
        re.I,
    ):
        return None

    try:
        financial = _financial_calculation(message)

        if financial is not None:
            return financial

        return _arithmetic_calculation(message)

    except (
        ValueError, InvalidOperation,
        OverflowError, ZeroDivisionError,
    ):
        return None

def attach_verified_calculation(context, message):
    if not isinstance(context, str):
        return context

    if VERSION in context or len(context) > 60000:
        return context

    result = execute_readonly_calculation(message)

    if result is None:
        return context

    payload = {
        "kind": result.kind,
        "expression": result.expression,
        "result": result.result,
        "input_origin": result.input_origin,
        "verification": result.verification,
    }

    block = (
        "\n\n[" + VERSION + "]\n"
        "DETERMINISTIC READ-ONLY CALCULATION RESULT\n"
        + json.dumps(
            payload,
            sort_keys=True,
            ensure_ascii=True,
        )
        + "\nCalculation performed with bounded Decimal "
        "arithmetic. Mathematical output is verified "
        "relative to the supplied inputs; underlying "
        "financial inputs are not independently verified. "
        "Do not mistake hypothetical or user-supplied "
        "figures for company filings or current prices. "
        "Use this result when answering the user's "
        "calculation question. Do not claim to have "
        "retrieved external financial information. "
        "Do not reveal internal tool markers."
        "\n[/" + VERSION + "]"
    )

    if len(block) > MAX_RESULT:
        return context

    return context + block
