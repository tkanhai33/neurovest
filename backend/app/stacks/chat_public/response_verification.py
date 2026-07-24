"""
Canonical NeuroVest response verifier.

This boundary validates generated assistant text against trusted
deterministic-math and retrieval evidence before persistence.

It performs no model call, network request, database operation,
broker action, order placement, account mutation, or live execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import (
    Decimal,
    InvalidOperation,
)
import re
from typing import Any

from backend.app.stacks.chat_public.math_tools.live_math import (
    LiveMathBundle,
)
from backend.app.stacks.chat_public.rag.live_retrieval import (
    LiveRetrievalBundle,
)


NUMBER_PATTERN = re.compile(
    r"""
    (?<![\w.])
    [-+]?
    (?:
        \d{1,3}(?:,\d{3})+
        |
        \d+
    )
    (?:\.\d+)?
    %?
    (?!\w)
    """,
    re.VERBOSE,
)

CITATION_PATTERN = re.compile(
    r"\[chunk_[A-Za-z0-9_-]+\]"
)

MAX_VERIFIED_RESPONSE_CHARACTERS = 20_000

MATH_OUTPUT_KEYS: dict[
    str,
    tuple[str, ...],
] = {
    "arithmetic": (
        "result",
    ),
    "percentage_of": (
        "result",
    ),
    "percent_change": (
        "percent_change",
    ),
    "simple_return": (
        "return_decimal",
        "return_percent",
    ),
    "compound_return": (
        "return_decimal",
        "return_percent",
    ),
    "cagr": (
        "cagr_decimal",
        "cagr_percent",
    ),
    "expected_value": (
        "expected_value",
    ),
    "risk_reward": (
        "reward_to_risk",
    ),
    "position_size": (
        "quantity",
        "risk_amount",
        "risk_per_unit",
        "allocated_capital",
    ),
    "portfolio_weights": (
        "total_value",
        "weight_sum",
    ),
    "descriptive_statistics": (
        "mean",
        "variance",
        "standard_deviation",
    ),
    "sharpe_ratio": (
        "sharpe_ratio",
    ),
    "sortino_ratio": (
        "sortino_ratio",
    ),
    "maximum_drawdown": (
        "maximum_drawdown_decimal",
        "maximum_drawdown_percent",
    ),
    "trade_statistics": (
        "win_rate_decimal",
        "win_rate_percent",
        "profit_factor",
        "payoff_ratio",
    ),
}

LIVE_EXECUTION_CONTRADICTION_PATTERNS = (
    re.compile(
        r"\blive\s+(?:broker\s+)?"
        r"(?:trading|execution)\s+"
        r"(?:is|has\s+been)\s+enabled\b",
        re.I,
    ),
    re.compile(
        r"\bproduction\s+broker\s+"
        r"execution\s+(?:is|has\s+been)\s+enabled\b",
        re.I,
    ),
    re.compile(
        r"\bi\s+can\s+(?:now\s+)?"
        r"(?:place|submit|execute)\s+"
        r"(?:real|live)\s+(?:trades|orders)\b",
        re.I,
    ),
    re.compile(
        r"\bi\s+(?:placed|submitted|executed)\s+"
        r"(?:a\s+)?(?:real|live)\s+(?:trade|order)\b",
        re.I,
    ),
    re.compile(
        r"\byour\s+(?:real|live)\s+"
        r"(?:trade|order)\s+(?:was|has\s+been)\s+"
        r"(?:placed|submitted|executed)\b",
        re.I,
    ),
    re.compile(
        r"\bbroker\s+orders?\s+"
        r"(?:are|is)\s+enabled\b",
        re.I,
    ),
)


@dataclass(
    frozen=True,
    slots=True,
)
class VerificationViolation:
    code: str
    message: str
    severity: str
    metadata: dict[str, Any]

    def as_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "code":
                self.code,
            "message":
                self.message,
            "severity":
                self.severity,
            "metadata":
                dict(
                    self.metadata
                ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class ResponseVerificationResult:
    status: str
    original_response: str
    final_response: str
    passed: bool
    repaired: bool
    fail_closed: bool
    checks: dict[str, bool]
    violations: tuple[
        VerificationViolation,
        ...
    ]
    metadata: dict[str, Any]

    def as_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "status":
                self.status,
            "original_response":
                self.original_response,
            "final_response":
                self.final_response,
            "passed":
                self.passed,
            "repaired":
                self.repaired,
            "fail_closed":
                self.fail_closed,
            "checks":
                dict(
                    self.checks
                ),
            "violations": [
                violation.as_dict()
                for violation in self.violations
            ],
            "metadata":
                dict(
                    self.metadata
                ),
        }


def _decimal(
    value: Any,
) -> Decimal | None:
    if isinstance(
        value,
        bool,
    ):
        return None

    normalized = str(
        value
    ).strip()

    if not normalized:
        return None

    percentage = normalized.endswith(
        "%"
    )

    if percentage:
        normalized = normalized[
            :-1
        ].strip()

    normalized = normalized.replace(
        ",",
        "",
    )

    try:
        result = Decimal(
            normalized
        )
    except InvalidOperation:
        return None

    if not result.is_finite():
        return None

    if percentage:
        return result

    return result


def _extract_numeric_values(
    text: str,
) -> tuple[Decimal, ...]:
    values: list[Decimal] = []

    for match in NUMBER_PATTERN.finditer(
        text
    ):
        value = _decimal(
            match.group(0)
        )

        if value is not None:
            values.append(
                value
            )

    return tuple(
        values
    )


def _decimal_equivalent(
    left: Decimal,
    right: Decimal,
) -> bool:
    return left == right


def _authoritative_math_values(
    math_bundle: LiveMathBundle,
) -> dict[str, Decimal]:
    if (
        not math_bundle.grounded
        or math_bundle.result is None
    ):
        return {}

    operation = str(
        math_bundle.operation
        or ""
    )

    values = math_bundle.result.get(
        "values",
        {},
    )

    if not isinstance(
        values,
        dict,
    ):
        return {}

    output_keys = MATH_OUTPUT_KEYS.get(
        operation,
        tuple(
            str(key)
            for key in values
        ),
    )

    authoritative: dict[
        str,
        Decimal
    ] = {}

    for key in output_keys:
        if key not in values:
            continue

        value = _decimal(
            values[
                key
            ]
        )

        if value is not None:
            authoritative[
                key
            ] = value

    return authoritative


def _math_values_present(
    response: str,
    authoritative: dict[
        str,
        Decimal
    ],
) -> tuple[
    bool,
    tuple[str, ...],
]:
    if not authoritative:
        return (
            True,
            (),
        )

    response_values = (
        _extract_numeric_values(
            response
        )
    )

    matched_keys: list[str] = []

    for key, expected in authoritative.items():
        if any(
            _decimal_equivalent(
                observed,
                expected,
            )
            for observed in response_values
        ):
            matched_keys.append(
                key
            )

    return (
        bool(
            matched_keys
        ),
        tuple(
            matched_keys
        ),
    )


def _allowed_citations(
    retrieval_bundle: LiveRetrievalBundle,
) -> set[str]:
    return {
        str(
            citation.get(
                "citation",
                "",
            )
        )
        for citation
        in retrieval_bundle.citations
        if citation.get(
            "citation"
        )
    }


def _citation_contract_valid(
    response: str,
    retrieval_bundle: LiveRetrievalBundle,
) -> tuple[
    bool,
    set[str],
    set[str],
]:
    observed = set(
        CITATION_PATTERN.findall(
            response
        )
    )

    allowed = _allowed_citations(
        retrieval_bundle
    )

    invalid = observed - allowed

    if invalid:
        return (
            False,
            observed,
            invalid,
        )

    citation_required = (
        retrieval_bundle.requested
        and bool(
            allowed
        )
    )

    if (
        citation_required
        and not observed
    ):
        return (
            False,
            observed,
            set(),
        )

    return (
        True,
        observed,
        set(),
    )


def _paper_only_boundary_valid(
    response: str,
) -> bool:
    return not any(
        pattern.search(
            response
        )
        for pattern
        in LIVE_EXECUTION_CONTRADICTION_PATTERNS
    )


def _format_decimal(
    value: Decimal,
) -> str:
    normalized = format(
        value,
        "f",
    )

    if "." in normalized:
        normalized = (
            normalized.rstrip(
                "0"
            ).rstrip(
                "."
            )
        )

    return normalized or "0"


def _safe_math_replacement(
    math_bundle: LiveMathBundle,
    authoritative: dict[
        str,
        Decimal
    ],
) -> str:
    operation = str(
        math_bundle.operation
        or "calculation"
    ).replace(
        "_",
        " ",
    )

    lines = [
        (
            "I verified this using NeuroVest's "
            "deterministic Decimal calculation engine."
        ),
        f"Operation: {operation}.",
    ]

    for key, value in authoritative.items():
        label = key.replace(
            "_",
            " ",
        )

        lines.append(
            f"{label.title()}: "
            f"{_format_decimal(value)}."
        )

    lines.append(
        (
            "This calculation is read-only and does not "
            "place or execute any live trade."
        )
    )

    return "\n".join(
        lines
    )


def _safe_citation_replacement(
    retrieval_bundle: LiveRetrievalBundle,
) -> str:
    if not retrieval_bundle.citations:
        return (
            "I could not verify the generated response "
            "against an approved citation source."
        )

    lines = [
        (
            "I retrieved relevant local research evidence, "
            "but the generated explanation did not satisfy "
            "the citation-verification contract."
        ),
        "Approved evidence:",
    ]

    for citation in retrieval_bundle.citations:
        token = str(
            citation.get(
                "citation",
                "",
            )
        )

        title = str(
            citation.get(
                "title",
                "Untitled source",
            )
        )

        page = citation.get(
            "page_number"
        )

        page_label = (
            str(page)
            if page is not None
            else "n/a"
        )

        lines.append(
            f"- {token} {title}, page {page_label}"
        )

    return "\n".join(
        lines
    )


def _safe_boundary_replacement() -> str:
    return (
        "Live-money broker execution remains disabled. "
        "I can discuss strategy, risk, market research, "
        "portfolio analysis, and simulated paper trades, "
        "but I cannot place or claim to have placed a real trade."
    )


def verify_response(
    response: str,
    *,
    math_bundle: LiveMathBundle,
    retrieval_bundle: LiveRetrievalBundle,
) -> ResponseVerificationResult:
    original = str(
        response
    ).strip()

    bounded = original[
        :MAX_VERIFIED_RESPONSE_CHARACTERS
    ]

    violations: list[
        VerificationViolation
    ] = []

    authoritative = (
        _authoritative_math_values(
            math_bundle
        )
    )

    (
        math_valid,
        matched_math_keys,
    ) = _math_values_present(
        bounded,
        authoritative,
    )

    if not math_valid:
        violations.append(
            VerificationViolation(
                code=(
                    "deterministic_math_value_missing"
                ),
                message=(
                    "The generated response did not include "
                    "an authoritative deterministic result."
                ),
                severity="critical",
                metadata={
                    "operation":
                        math_bundle.operation,
                    "expected_keys":
                        sorted(
                            authoritative
                        ),
                    "matched_keys":
                        list(
                            matched_math_keys
                        ),
                },
            )
        )

    (
        citations_valid,
        observed_citations,
        invalid_citations,
    ) = _citation_contract_valid(
        bounded,
        retrieval_bundle,
    )

    if invalid_citations:
        violations.append(
            VerificationViolation(
                code="unapproved_citation",
                message=(
                    "The generated response included a "
                    "citation outside the approved retrieval set."
                ),
                severity="critical",
                metadata={
                    "invalid_citations":
                        sorted(
                            invalid_citations
                        ),
                    "allowed_citations":
                        sorted(
                            _allowed_citations(
                                retrieval_bundle
                            )
                        ),
                },
            )
        )

    elif (
        retrieval_bundle.requested
        and bool(
            _allowed_citations(
                retrieval_bundle
            )
        )
        and not observed_citations
    ):
        violations.append(
            VerificationViolation(
                code="required_citation_missing",
                message=(
                    "Grounded retrieval evidence existed, "
                    "but the generated response contained no "
                    "approved citation token."
                ),
                severity="high",
                metadata={
                    "allowed_citations":
                        sorted(
                            _allowed_citations(
                                retrieval_bundle
                            )
                        ),
                },
            )
        )

    boundary_valid = (
        _paper_only_boundary_valid(
            bounded
        )
    )

    if not boundary_valid:
        violations.append(
            VerificationViolation(
                code=(
                    "paper_only_boundary_contradiction"
                ),
                message=(
                    "The generated response contradicted "
                    "NeuroVest's locked live-execution boundary."
                ),
                severity="critical",
                metadata={
                    "live_execution_allowed":
                        False,
                    "broker_execution_allowed":
                        False,
                },
            )
        )

    checks = {
        "response_not_empty":
            bool(
                bounded
            ),
        "deterministic_math_consistent":
            math_valid,
        "citation_contract_valid":
            citations_valid,
        "paper_only_boundary_valid":
            boundary_valid,
    }

    if not bounded:
        violations.append(
            VerificationViolation(
                code="empty_response",
                message=(
                    "The generated assistant response was empty."
                ),
                severity="critical",
                metadata={},
            )
        )

    critical_codes = {
        violation.code
        for violation in violations
        if violation.severity
        == "critical"
    }

    final_response = bounded
    repaired = False
    fail_closed = False

    if (
        "paper_only_boundary_contradiction"
        in critical_codes
    ):
        final_response = (
            _safe_boundary_replacement()
        )

        repaired = True
        fail_closed = True

    elif (
        "deterministic_math_value_missing"
        in critical_codes
    ):
        final_response = (
            _safe_math_replacement(
                math_bundle,
                authoritative,
            )
        )

        repaired = True
        fail_closed = True

    elif (
        "unapproved_citation"
        in critical_codes
        or any(
            violation.code
            == "required_citation_missing"
            for violation in violations
        )
    ):
        final_response = (
            _safe_citation_replacement(
                retrieval_bundle
            )
        )

        repaired = True
        fail_closed = True

    elif not bounded:
        final_response = (
            "Neuro could not produce a response that "
            "passed verification."
        )

        repaired = True
        fail_closed = True

    passed = not violations

    status = (
        "passed"
        if passed
        else (
            "repaired"
            if repaired
            else "failed"
        )
    )

    return ResponseVerificationResult(
        status=status,
        original_response=original,
        final_response=final_response,
        passed=passed,
        repaired=repaired,
        fail_closed=fail_closed,
        checks=checks,
        violations=tuple(
            violations
        ),
        metadata={
            "authoritative_math_values": {
                key:
                    _format_decimal(
                        value
                    )
                for key, value
                in authoritative.items()
            },
            "matched_math_keys":
                list(
                    matched_math_keys
                ),
            "observed_citations":
                sorted(
                    observed_citations
                ),
            "allowed_citations":
                sorted(
                    _allowed_citations(
                        retrieval_bundle
                    )
                ),
            "bounded":
                len(original)
                > len(bounded),
            "maximum_response_characters":
                MAX_VERIFIED_RESPONSE_CHARACTERS,
        },
    )


__all__ = [
    "MAX_VERIFIED_RESPONSE_CHARACTERS",
    "ResponseVerificationResult",
    "VerificationViolation",
    "verify_response",
]
