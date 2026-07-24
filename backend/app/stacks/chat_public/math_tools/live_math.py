"""
Strict natural-language integration for NeuroVest deterministic math.

This module:
- recognizes only explicitly supported calculation forms;
- extracts bounded named arguments;
- invokes the qualified Decimal math engine;
- never evaluates arbitrary expressions or code;
- returns controlled unavailable/error states;
- builds bounded exact-result evidence for model input.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import re
from typing import Any

from backend.app.stacks.chat_public.math_tools.contracts import (
    MathToolRequest,
    MathToolResult,
)
from backend.app.stacks.chat_public.math_tools.engine import (
    execute_math_tool,
)


NUMBER = (
    r"[-+]?"
    r"(?:\d{1,3}(?:,\d{3})+|\d+)"
    r"(?:\.\d+)?"
)

MAX_MATH_PROMPT_CHARACTERS = 4_000


@dataclass(
    frozen=True,
    slots=True,
)
class ExtractedMathRequest:
    request: MathToolRequest
    source_text: str


@dataclass(
    frozen=True,
    slots=True,
)
class LiveMathBundle:
    requested: bool
    extracted: bool
    succeeded: bool
    operation: str | None
    arguments: dict[str, Any]
    result: dict[str, Any] | None
    prompt_section: str
    error: str | None

    @property
    def grounded(
        self,
    ) -> bool:
        return (
            self.requested
            and self.extracted
            and self.succeeded
            and self.result is not None
        )


def _clean_number(
    value: str,
) -> str:
    return value.replace(
        ",",
        "",
    ).strip()


def _number_list(
    value: str,
) -> list[str]:
    return [
        _clean_number(
            match
        )
        for match in re.findall(
            NUMBER,
            value,
        )
    ]


def _extract_percentage_of(
    message: str,
) -> ExtractedMathRequest | None:
    patterns = (
        re.compile(
            rf"\bwhat\s+is\s+({NUMBER})\s*(?:%|percent)\s+of\s+({NUMBER})\b",
            re.I,
        ),
        re.compile(
            rf"\bcalculate\s+({NUMBER})\s*(?:%|percent)\s+(?:of|on)\s+({NUMBER})\b",
            re.I,
        ),
        re.compile(
            rf"\b({NUMBER})\s*(?:%|percent)\s+(?:of|on)\s+({NUMBER})\b",
            re.I,
        ),
    )

    for pattern in patterns:
        match = pattern.search(
            message
        )

        if match:
            return ExtractedMathRequest(
                request=MathToolRequest(
                    operation="percentage_of",
                    arguments={
                        "percentage":
                            _clean_number(
                                match.group(1)
                            ),
                        "amount":
                            _clean_number(
                                match.group(2)
                            ),
                    },
                ),
                source_text=match.group(0),
            )

    return None


def _extract_percent_change(
    message: str,
) -> ExtractedMathRequest | None:
    patterns = (
        re.compile(
            rf"\bpercent(?:age)?\s+change\s+from\s+({NUMBER})\s+to\s+({NUMBER})\b",
            re.I,
        ),
        re.compile(
            rf"\bchange\s+from\s+({NUMBER})\s+to\s+({NUMBER})\s+as\s+a\s+percent(?:age)?\b",
            re.I,
        ),
    )

    for pattern in patterns:
        match = pattern.search(
            message
        )

        if match:
            return ExtractedMathRequest(
                request=MathToolRequest(
                    operation="percent_change",
                    arguments={
                        "original":
                            _clean_number(
                                match.group(1)
                            ),
                        "new":
                            _clean_number(
                                match.group(2)
                            ),
                    },
                ),
                source_text=match.group(0),
            )

    return None


def _extract_cagr(
    message: str,
) -> ExtractedMathRequest | None:
    patterns = (
        re.compile(
            rf"\bcagr\s+(?:from\s+)?({NUMBER})\s+to\s+({NUMBER})\s+(?:over|for)\s+({NUMBER})\s+years?\b",
            re.I,
        ),
        re.compile(
            rf"\bcalculate\s+cagr\s+from\s+({NUMBER})\s+to\s+({NUMBER})\s+(?:over|for)\s+({NUMBER})\s+years?\b",
            re.I,
        ),
    )

    for pattern in patterns:
        match = pattern.search(
            message
        )

        if match:
            return ExtractedMathRequest(
                request=MathToolRequest(
                    operation="cagr",
                    arguments={
                        "beginning_value":
                            _clean_number(
                                match.group(1)
                            ),
                        "ending_value":
                            _clean_number(
                                match.group(2)
                            ),
                        "years":
                            _clean_number(
                                match.group(3)
                            ),
                    },
                ),
                source_text=match.group(0),
            )

    return None


def _extract_position_size(
    message: str,
) -> ExtractedMathRequest | None:
    patterns = (
        re.compile(
            rf"\bposition\s+size\b.*?"
            rf"(?:account|portfolio)\s+(?:value|size)?\s*(?:of|is|=)?\s*\$?({NUMBER}).*?"
            rf"risk\s+({NUMBER})\s*(?:%|percent).*?"
            rf"entry\s+(?:price\s+)?(?:of|is|=)?\s*\$?({NUMBER}).*?"
            rf"stop\s+(?:price\s+)?(?:of|is|=)?\s*\$?({NUMBER})",
            re.I | re.S,
        ),
        re.compile(
            rf"\bcalculate\s+position\s+size\b.*?"
            rf"\$?({NUMBER}).*?"
            rf"({NUMBER})\s*(?:%|percent).*?"
            rf"entry\s+\$?({NUMBER}).*?"
            rf"stop\s+\$?({NUMBER})",
            re.I | re.S,
        ),
    )

    for pattern in patterns:
        match = pattern.search(
            message
        )

        if match:
            return ExtractedMathRequest(
                request=MathToolRequest(
                    operation="position_size",
                    arguments={
                        "account_value":
                            _clean_number(
                                match.group(1)
                            ),
                        "risk_percent":
                            _clean_number(
                                match.group(2)
                            ),
                        "entry_price":
                            _clean_number(
                                match.group(3)
                            ),
                        "stop_price":
                            _clean_number(
                                match.group(4)
                            ),
                        "whole_units":
                            True,
                    },
                ),
                source_text=match.group(0),
            )

    return None


def _extract_risk_reward(
    message: str,
) -> ExtractedMathRequest | None:
    pattern = re.compile(
        rf"\b(?:risk[\s/-]*reward|reward[\s/-]*risk)\b.*?"
        rf"entry\s+(?:price\s+)?(?:of|is|=)?\s*\$?({NUMBER}).*?"
        rf"stop\s+(?:price\s+)?(?:of|is|=)?\s*\$?({NUMBER}).*?"
        rf"target\s+(?:price\s+)?(?:of|is|=)?\s*\$?({NUMBER})",
        re.I | re.S,
    )

    match = pattern.search(
        message
    )

    if not match:
        return None

    return ExtractedMathRequest(
        request=MathToolRequest(
            operation="risk_reward",
            arguments={
                "entry_price":
                    _clean_number(
                        match.group(1)
                    ),
                "stop_price":
                    _clean_number(
                        match.group(2)
                    ),
                "target_price":
                    _clean_number(
                        match.group(3)
                    ),
            },
        ),
        source_text=match.group(0),
    )


def _extract_compound_return(
    message: str,
) -> ExtractedMathRequest | None:
    pattern = re.compile(
        r"\bcompound(?:ed)?\s+return\b.*?"
        r"(?:returns?|values?)\s*[:=]?\s*"
        r"([0-9.,+\-%\s]+)",
        re.I,
    )

    match = pattern.search(
        message
    )

    if not match:
        return None

    raw_values = _number_list(
        match.group(1)
    )

    if not raw_values:
        return None

    percentage_input = (
        "%"
        in match.group(1)
        or "percent"
        in message.lower()
    )

    returns: list[str] = []

    for value in raw_values:
        decimal_value = Decimal(
            value
        )

        if percentage_input:
            decimal_value /= Decimal(
                "100"
            )

        returns.append(
            format(
                decimal_value,
                "f",
            )
        )

    return ExtractedMathRequest(
        request=MathToolRequest(
            operation="compound_return",
            arguments={
                "returns":
                    returns,
            },
        ),
        source_text=match.group(0),
    )


def _extract_maximum_drawdown(
    message: str,
) -> ExtractedMathRequest | None:
    pattern = re.compile(
        r"\b(?:maximum|max)\s+drawdown\b.*?"
        r"(?:equity\s+curve|values?|series)\s*[:=]?\s*"
        r"([0-9.,+\-\s]+)",
        re.I,
    )

    match = pattern.search(
        message
    )

    if not match:
        return None

    values = _number_list(
        match.group(1)
    )

    if len(values) < 2:
        return None

    return ExtractedMathRequest(
        request=MathToolRequest(
            operation="maximum_drawdown",
            arguments={
                "equity_curve":
                    values,
            },
        ),
        source_text=match.group(0),
    )


def _extract_arithmetic(
    message: str,
) -> ExtractedMathRequest | None:
    pattern = re.compile(
        rf"(?:calculate|compute|solve|what\s+is)?\s*"
        rf"({NUMBER})\s*([+\-*/])\s*({NUMBER})",
        re.I,
    )

    match = pattern.search(
        message
    )

    if not match:
        return None

    operator_map = {
        "+":
            "add",
        "-":
            "subtract",
        "*":
            "multiply",
        "/":
            "divide",
    }

    return ExtractedMathRequest(
        request=MathToolRequest(
            operation="arithmetic",
            arguments={
                "left":
                    _clean_number(
                        match.group(1)
                    ),
                "right":
                    _clean_number(
                        match.group(3)
                    ),
                "operator":
                    operator_map[
                        match.group(2)
                    ],
            },
        ),
        source_text=match.group(0),
    )


EXTRACTORS = (
    _extract_percentage_of,
    _extract_percent_change,
    _extract_cagr,
    _extract_position_size,
    _extract_risk_reward,
    _extract_compound_return,
    _extract_maximum_drawdown,
    _extract_arithmetic,
)


def extract_math_request(
    message: str,
) -> ExtractedMathRequest | None:
    normalized = str(
        message
    ).strip()

    if not normalized:
        return None

    for extractor in EXTRACTORS:
        extracted = extractor(
            normalized
        )

        if extracted is not None:
            return extracted

    return None


def build_math_prompt_section(
    *,
    request: MathToolRequest,
    result: MathToolResult,
) -> str:
    payload = result.as_serializable()

    section = "\n".join(
        (
            "DETERMINISTIC CALCULATION EVIDENCE",
            (
                "The following result was computed by NeuroVest's "
                "read-only Decimal math engine. Treat these exact "
                "values as authoritative for this calculation. "
                "Do not recalculate, replace, or contradict them."
            ),
            f"Operation: {request.operation}",
            f"Arguments: {request.arguments}",
            f"Status: {payload['status']}",
            f"Values: {payload['values']}",
            f"Formula: {payload['formula']}",
            f"Precision: {payload['precision']} decimal digits",
            f"Error: {payload['error']}",
        )
    )

    return section[
        :MAX_MATH_PROMPT_CHARACTERS
    ]


def evaluate_live_math(
    message: str,
    *,
    requested: bool,
) -> LiveMathBundle:
    if not requested:
        return LiveMathBundle(
            requested=False,
            extracted=False,
            succeeded=False,
            operation=None,
            arguments={},
            result=None,
            prompt_section="",
            error=None,
        )

    extracted = extract_math_request(
        message
    )

    if extracted is None:
        return LiveMathBundle(
            requested=True,
            extracted=False,
            succeeded=False,
            operation=None,
            arguments={},
            result=None,
            prompt_section="",
            error=(
                "A deterministic calculation was requested, "
                "but the required operation or named numeric "
                "inputs could not be extracted safely."
            ),
        )

    result = execute_math_tool(
        extracted.request
    )

    payload = result.as_serializable()

    return LiveMathBundle(
        requested=True,
        extracted=True,
        succeeded=result.succeeded,
        operation=(
            extracted.request.operation
        ),
        arguments=dict(
            extracted.request.arguments
        ),
        result=payload,
        prompt_section=(
            build_math_prompt_section(
                request=extracted.request,
                result=result,
            )
        ),
        error=result.error,
    )


__all__ = [
    "ExtractedMathRequest",
    "LiveMathBundle",
    "MAX_MATH_PROMPT_CHARACTERS",
    "build_math_prompt_section",
    "evaluate_live_math",
    "extract_math_request",
]
