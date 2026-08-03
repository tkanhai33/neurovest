"""Immutable historical-window and bounded candidate-decision support."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, TypeVar
import hashlib
import json
import math
import re


T = TypeVar("T")

TRAINING_WINDOW_CONTRACT_VERSION = 1

_WINDOW_ID_PATTERN = re.compile(
    r"^training_window_[0-9a-f]{24}$"
)

_HASH_PATTERN = re.compile(
    r"^[0-9a-f]{64}$"
)


@dataclass(frozen=True, slots=True)
class TrainingWindowContract:
    training_window_id: str
    window_version: int
    window_start: str | None
    window_end: str | None
    lookback_rows: int | None
    row_offset: int
    round_number: int
    maximum_rounds: int
    contract_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_boundary(value: Any) -> str | None:
    if value is None:
        return None

    normalized = str(value).strip()
    return normalized or None


def _validated_values(
    *,
    window_version: Any,
    window_start: Any,
    window_end: Any,
    lookback_rows: Any,
    row_offset: Any,
    round_number: Any,
    maximum_rounds: Any,
) -> tuple[
    int,
    str | None,
    str | None,
    int | None,
    int,
    int,
    int,
]:
    if (
        not isinstance(window_version, int)
        or isinstance(window_version, bool)
        or window_version != TRAINING_WINDOW_CONTRACT_VERSION
    ):
        raise ValueError(
            "unsupported training window version"
        )

    start = _normalize_boundary(window_start)
    end = _normalize_boundary(window_end)

    if (
        start is not None
        and end is not None
        and start > end
    ):
        raise ValueError(
            "window_start cannot follow window_end"
        )

    if lookback_rows is not None:
        if (
            not isinstance(lookback_rows, int)
            or isinstance(lookback_rows, bool)
            or not 2 <= lookback_rows <= 100000
        ):
            raise ValueError(
                "lookback_rows must be between 2 and 100000"
            )

    if (
        not isinstance(row_offset, int)
        or isinstance(row_offset, bool)
        or row_offset < 0
    ):
        raise ValueError(
            "row_offset must be a non-negative integer"
        )

    if (
        not isinstance(round_number, int)
        or isinstance(round_number, bool)
        or round_number < 1
    ):
        raise ValueError(
            "round_number must be at least 1"
        )

    if (
        not isinstance(maximum_rounds, int)
        or isinstance(maximum_rounds, bool)
        or not 1 <= maximum_rounds <= 100
    ):
        raise ValueError(
            "maximum_rounds must be between 1 and 100"
        )

    if round_number > maximum_rounds:
        raise ValueError(
            "round_number cannot exceed maximum_rounds"
        )

    return (
        window_version,
        start,
        end,
        lookback_rows,
        row_offset,
        round_number,
        maximum_rounds,
    )


def _payload(
    *,
    window_version: int,
    window_start: str | None,
    window_end: str | None,
    lookback_rows: int | None,
    row_offset: int,
    round_number: int,
    maximum_rounds: int,
) -> dict[str, Any]:
    return {
        "window_version": window_version,
        "window_start": window_start,
        "window_end": window_end,
        "lookback_rows": lookback_rows,
        "row_offset": row_offset,
        "round_number": round_number,
        "maximum_rounds": maximum_rounds,
    }


def _payload_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def build_training_window_contract(
    *,
    window_start: str | None = None,
    window_end: str | None = None,
    lookback_rows: int | None = None,
    row_offset: int = 0,
    round_number: int = 1,
    maximum_rounds: int = 1,
    window_version: int = TRAINING_WINDOW_CONTRACT_VERSION,
) -> TrainingWindowContract:
    (
        version,
        start,
        end,
        lookback,
        offset,
        round_value,
        maximum,
    ) = _validated_values(
        window_version=window_version,
        window_start=window_start,
        window_end=window_end,
        lookback_rows=lookback_rows,
        row_offset=row_offset,
        round_number=round_number,
        maximum_rounds=maximum_rounds,
    )

    payload = _payload(
        window_version=version,
        window_start=start,
        window_end=end,
        lookback_rows=lookback,
        row_offset=offset,
        round_number=round_value,
        maximum_rounds=maximum,
    )

    contract_hash = _payload_hash(payload)

    return TrainingWindowContract(
        training_window_id=(
            "training_window_"
            + contract_hash[:24]
        ),
        window_version=version,
        window_start=start,
        window_end=end,
        lookback_rows=lookback,
        row_offset=offset,
        round_number=round_value,
        maximum_rounds=maximum,
        contract_hash=contract_hash,
    )


def validate_training_window_contract(
    window: dict[str, Any],
) -> bool:
    if not isinstance(window, dict):
        return False

    required = {
        "training_window_id",
        "window_version",
        "window_start",
        "window_end",
        "lookback_rows",
        "row_offset",
        "round_number",
        "maximum_rounds",
        "contract_hash",
    }

    if set(window) != required:
        return False

    try:
        rebuilt = build_training_window_contract(
            window_version=window["window_version"],
            window_start=window["window_start"],
            window_end=window["window_end"],
            lookback_rows=window["lookback_rows"],
            row_offset=window["row_offset"],
            round_number=window["round_number"],
            maximum_rounds=window["maximum_rounds"],
        )
    except (TypeError, ValueError):
        return False

    supplied_id = window.get(
        "training_window_id"
    )

    supplied_hash = window.get(
        "contract_hash"
    )

    return (
        isinstance(supplied_id, str)
        and isinstance(supplied_hash, str)
        and _WINDOW_ID_PATTERN.fullmatch(
            supplied_id
        )
        is not None
        and _HASH_PATTERN.fullmatch(
            supplied_hash
        )
        is not None
        and rebuilt.to_dict() == window
    )


def apply_training_window(
    rows: list[T],
    *,
    timestamps: list[str | None],
    window: dict[str, Any],
) -> list[T]:
    if not validate_training_window_contract(window):
        raise ValueError(
            "invalid training window contract"
        )

    if len(rows) != len(timestamps):
        raise ValueError(
            "rows and timestamps must have equal length"
        )

    start = window["window_start"]
    end = window["window_end"]

    selected: list[T] = []

    for row, timestamp in zip(
        rows,
        timestamps,
    ):
        normalized = (
            str(timestamp).strip()
            if timestamp is not None
            else ""
        )

        if (
            start is not None
            and (
                not normalized
                or normalized < start
            )
        ):
            continue

        if (
            end is not None
            and (
                not normalized
                or normalized > end
            )
        ):
            continue

        selected.append(row)

    offset = int(window["row_offset"])

    if offset:
        selected = selected[offset:]

    lookback = window["lookback_rows"]

    if lookback is not None:
        selected = selected[:int(lookback)]

    return selected


def build_close_prefix_sums(
    closes: list[float],
) -> list[float]:
    prefix = [0.0]
    total = 0.0

    for value in closes:
        number = float(value)

        if not math.isfinite(number):
            raise ValueError(
                "close values must be finite"
            )

        total += number
        prefix.append(total)

    return prefix


def candidate_decision_from_prefix(
    *,
    closes: list[float],
    prefix_sums: list[float],
    index: int,
    candidate: dict[str, Any],
) -> str:
    from backend.app.stacks.strategy_candidate_sandbox.training_candidate_contract import (
        validate_training_candidate_contract,
    )

    if not validate_training_candidate_contract(candidate):
        raise ValueError(
            "invalid training candidate contract"
        )

    if len(prefix_sums) != len(closes) + 1:
        raise ValueError(
            "prefix sums do not match close rows"
        )

    if index < 0 or index >= len(closes):
        raise ValueError(
            "decision index is outside close rows"
        )

    short_rows = int(
        candidate["short_lookback_rows"]
    )

    long_rows = int(
        candidate["long_lookback_rows"]
    )

    if index + 1 < long_rows:
        return "HOLD"

    short_start = index - short_rows + 1
    long_start = index - long_rows + 1

    short_total = (
        prefix_sums[index + 1]
        - prefix_sums[short_start]
    )

    long_total = (
        prefix_sums[index + 1]
        - prefix_sums[long_start]
    )

    short_average = short_total / short_rows
    long_average = long_total / long_rows

    if long_average == 0:
        return "HOLD"

    strength = (
        short_average
        - long_average
    ) / abs(long_average)

    minimum = float(
        candidate["minimum_signal_strength"]
    )

    if strength >= minimum:
        return "BUY_SIGNAL"

    if strength <= -minimum:
        return "SELL_SIGNAL"

    return "HOLD"


__all__ = [
    "TRAINING_WINDOW_CONTRACT_VERSION",
    "TrainingWindowContract",
    "apply_training_window",
    "build_close_prefix_sums",
    "build_training_window_contract",
    "candidate_decision_from_prefix",
    "validate_training_window_contract",
]
