"""
Persistent confidence-baseline comparison for bounded training.

The comparison uses only sanitized learning-ledger contributions.
Customer identity, session identity, chat content, portfolio data,
authentication data, orders, and broker information are excluded.
"""

from __future__ import annotations

from typing import Any
import math

from backend.app.stacks.strategy_candidate_sandbox.persistent_learning_ledger import (
    list_learning_contributions,
)


_BASELINE_VERSION = 1

_FORBIDDEN_KEYS = {
    "owner_user_id",
    "owner_session_id",
    "user_id",
    "session_id",
    "requested_by",
    "requested_by_role",
    "email",
    "password",
    "prompt",
    "raw_prompt",
    "message",
    "chat",
    "portfolio",
    "positions",
    "holdings",
    "orders",
    "account",
    "account_id",
    "access_token",
    "refresh_token",
    "credential",
    "credentials",
    "broker",
    "broker_token",
}


def _finite_float(
    value: Any,
    *,
    default: float = 0.0,
) -> float:
    try:
        resolved = float(value)
    except (
        TypeError,
        ValueError,
    ):
        return default

    if not math.isfinite(resolved):
        return default

    return resolved


def _confidence_by_symbol(
    contribution: dict[str, Any],
) -> dict[str, float]:
    result: dict[str, float] = {}

    records = contribution.get(
        "symbol_confidence",
        [],
    )

    if not isinstance(records, list):
        return result

    for item in records:
        if not isinstance(item, dict):
            continue

        symbol = str(
            item.get("symbol")
            or ""
        ).strip().upper()

        if not symbol:
            continue

        confidence = max(
            0.0,
            min(
                _finite_float(
                    item.get(
                        "average_confidence"
                    )
                ),
                1.0,
            ),
        )

        result[symbol] = confidence

    return result


def _contains_forbidden_key(
    value: Any,
) -> str | None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(
                key
            ).strip().lower()

            if normalized in _FORBIDDEN_KEYS:
                return normalized

            nested = _contains_forbidden_key(
                child
            )

            if nested:
                return nested

    elif isinstance(value, list):
        for child in value:
            nested = _contains_forbidden_key(
                child
            )

            if nested:
                return nested

    return None


def _ledger_records() -> list[dict[str, Any]]:
    records = list_learning_contributions()

    if isinstance(records, dict):
        for key in (
            "items",
            "records",
            "contributions",
            "entries",
        ):
            value = records.get(key)

            if isinstance(value, list):
                return [
                    item
                    for item in value
                    if isinstance(item, dict)
                ]

        return []

    if isinstance(records, list):
        return [
            item
            for item in records
            if isinstance(item, dict)
        ]

    return []


def _extract_contribution(
    record: dict[str, Any],
) -> dict[str, Any] | None:
    contribution = record.get(
        "contribution"
    )

    if isinstance(
        contribution,
        dict,
    ):
        resolved = dict(
            contribution
        )

        wrapper_contribution_id = str(
            record.get(
                "contribution_id"
            )
            or record.get(
                "id"
            )
            or ""
        ).strip()

        nested_contribution_id = str(
            resolved.get(
                "contribution_id"
            )
            or ""
        ).strip()

        if (
            wrapper_contribution_id
            and not nested_contribution_id
        ):
            resolved[
                "contribution_id"
            ] = wrapper_contribution_id

        return resolved

    if (
        "contribution_id" in record
        and "average_confidence" in record
    ):
        return dict(
            record
        )

    return None


def find_latest_confidence_baseline(
    *,
    current_contribution_id: str,
    universe: str,
) -> dict[str, Any] | None:
    candidates: list[
        tuple[str, dict[str, Any]]
    ] = []

    for record in _ledger_records():
        contribution = _extract_contribution(
            record
        )

        if not contribution:
            continue

        contribution_id = str(
            contribution.get(
                "contribution_id"
            )
            or ""
        )

        if (
            not contribution_id
            or contribution_id
            == current_contribution_id
        ):
            continue

        if str(
            contribution.get(
                "universe"
            )
            or ""
        ).strip().lower() != universe:
            continue

        if contribution.get(
            "completed"
        ) is not True:
            continue

        if not isinstance(
            contribution.get(
                "symbol_confidence"
            ),
            list,
        ):
            continue

        ordering_value = str(
            record.get(
                "created_at"
            )
            or record.get(
                "persisted_at"
            )
            or record.get(
                "timestamp"
            )
            or contribution_id
        )

        candidates.append(
            (
                ordering_value,
                contribution,
            )
        )

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: item[0]
    )

    return dict(
        candidates[-1][1]
    )


def build_confidence_baseline_comparison(
    *,
    current_contribution: dict[str, Any],
) -> dict[str, Any]:
    current_id = str(
        current_contribution.get(
            "contribution_id"
        )
        or ""
    )

    universe = str(
        current_contribution.get(
            "universe"
        )
        or ""
    ).strip().lower()

    current_average = max(
        0.0,
        min(
            _finite_float(
                current_contribution.get(
                    "average_confidence"
                )
            ),
            1.0,
        ),
    )

    current_symbols = _confidence_by_symbol(
        current_contribution
    )

    baseline = find_latest_confidence_baseline(
        current_contribution_id=current_id,
        universe=universe,
    )

    if baseline is None:
        comparison = {
            "confidence_baseline_version":
                _BASELINE_VERSION,

            "confidence_baseline_available":
                False,

            "baseline_contribution_id":
                None,

            "baseline_average_confidence":
                None,

            "current_average_confidence":
                round(
                    current_average,
                    8,
                ),

            "average_confidence_delta":
                None,

            "symbols_compared":
                0,

            "symbols_improved":
                0,

            "symbols_unchanged":
                0,

            "symbols_declined":
                0,

            "minimum_symbol_confidence_delta":
                None,

            "maximum_symbol_confidence_delta":
                None,

            "all_compared_symbols_improved":
                False,

            "confidence_improved":
                False,

            "symbol_confidence_delta":
                [],
        }

    else:
        baseline_id = str(
            baseline.get(
                "contribution_id"
            )
            or ""
        )

        baseline_average = max(
            0.0,
            min(
                _finite_float(
                    baseline.get(
                        "average_confidence"
                    )
                ),
                1.0,
            ),
        )

        baseline_symbols = (
            _confidence_by_symbol(
                baseline
            )
        )

        common_symbols = sorted(
            set(current_symbols)
            & set(baseline_symbols)
        )

        symbol_delta = []
        improved = 0
        unchanged = 0
        declined = 0

        for symbol in common_symbols:
            before = baseline_symbols[
                symbol
            ]

            after = current_symbols[
                symbol
            ]

            delta = after - before

            if delta > 1e-12:
                state = "improved"
                improved += 1
            elif delta < -1e-12:
                state = "declined"
                declined += 1
            else:
                state = "unchanged"
                unchanged += 1

            symbol_delta.append(
                {
                    "symbol":
                        symbol,

                    "baseline_confidence":
                        round(
                            before,
                            8,
                        ),

                    "current_confidence":
                        round(
                            after,
                            8,
                        ),

                    "confidence_delta":
                        round(
                            delta,
                            8,
                        ),

                    "state":
                        state,
                }
            )

        deltas = [
            float(
                item["confidence_delta"]
            )
            for item in symbol_delta
        ]

        average_delta = (
            current_average
            - baseline_average
        )

        comparison = {
            "confidence_baseline_version":
                _BASELINE_VERSION,

            "confidence_baseline_available":
                True,

            "baseline_contribution_id":
                baseline_id,

            "baseline_average_confidence":
                round(
                    baseline_average,
                    8,
                ),

            "current_average_confidence":
                round(
                    current_average,
                    8,
                ),

            "average_confidence_delta":
                round(
                    average_delta,
                    8,
                ),

            "symbols_compared":
                len(common_symbols),

            "symbols_improved":
                improved,

            "symbols_unchanged":
                unchanged,

            "symbols_declined":
                declined,

            "minimum_symbol_confidence_delta":
                (
                    round(
                        min(deltas),
                        8,
                    )
                    if deltas
                    else None
                ),

            "maximum_symbol_confidence_delta":
                (
                    round(
                        max(deltas),
                        8,
                    )
                    if deltas
                    else None
                ),

            "all_compared_symbols_improved":
                bool(
                    common_symbols
                )
                and improved
                == len(common_symbols),

            "confidence_improved":
                average_delta > 1e-12,

            "symbol_confidence_delta":
                symbol_delta,
        }

    forbidden = _contains_forbidden_key(
        comparison
    )

    if forbidden:
        raise ValueError(
            "Confidence comparison contains "
            f"forbidden key: {forbidden}"
        )

    return comparison


__all__ = [
    "build_confidence_baseline_comparison",
    "find_latest_confidence_baseline",
]
