from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

import csv
import hashlib


FROZEN25_STRATEGY_ID = "challenger_02952"

FROZEN25_STRATEGY_FINGERPRINT = (
    "40a6c489519db0c9f4408ee14759d827c2aad56ceda62a2bcbd074f04ccc9131"
)

FROZEN25_HISTORY_SHA256 = (
    "4658b9dd12f969b2db036be0441d459b0690214a71e97728544a83a0735075f8"
)

FROZEN25_HISTORY_ROW_COUNT = 7930

FROZEN25_HISTORY_SYMBOL = "TD.TO"

FROZEN25_HISTORY_FIRST_TIMESTAMP = (
    "1995-01-12 00:00:00+00:00"
)

FROZEN25_HISTORY_LAST_TIMESTAMP = (
    "2026-07-31 00:00:00+00:00"
)


def _repository_root() -> Path:
    """
    Resolve the NeuroVest repository root from this module location.

    This performs no filesystem mutation.
    """

    return Path(
        __file__
    ).resolve().parents[5]


def frozen25_history_path() -> Path:
    """
    Return the one qualified local historical source for Frozen25.

    No fallback path, network source, or discovery behavior is allowed.
    """

    return (
        _repository_root()
        / "runtime"
        / "training"
        / "generation274_isolated_history_extension_20260806_114523"
        / "extended"
        / "TD_TO.csv"
    )


class Frozen25HistoryError(RuntimeError):
    pass


class Frozen25HistoryIdentityError(Frozen25HistoryError):
    pass


class Frozen25HistoryIntegrityError(Frozen25HistoryError):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class Frozen25HistoryRow:
    timestamp: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(
    frozen=True,
    slots=True,
)
class Frozen25History:
    strategy_id: str
    strategy_fingerprint: str
    source_path: Path
    source_sha256: str
    rows: tuple[Frozen25HistoryRow, ...]

    @property
    def row_count(self) -> int:
        return len(
            self.rows
        )

    @property
    def first_timestamp(self) -> datetime:
        return self.rows[
            0
        ].timestamp

    @property
    def last_timestamp(self) -> datetime:
        return self.rows[
            -1
        ].timestamp


def _parse_timestamp(
    value: str,
) -> datetime:

    text = str(
        value
    ).strip()

    candidate = (
        text[:-1] + "+00:00"
        if text.endswith(
            "Z"
        )
        else text
    )

    try:
        parsed = datetime.fromisoformat(
            candidate
        )
    except ValueError as exc:
        raise Frozen25HistoryIntegrityError(
            "Invalid Frozen25 history timestamp: "
            + repr(
                text
            )
        ) from exc

    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=timezone.utc
        )
    else:
        parsed = parsed.astimezone(
            timezone.utc
        )

    return parsed


def _digest(
    path: Path,
) -> str:

    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _validate_identity(
    *,
    strategy_id: str,
    strategy_fingerprint: str | None,
) -> None:

    if strategy_id != FROZEN25_STRATEGY_ID:
        raise Frozen25HistoryIdentityError(
            "Frozen25 history may only bind to "
            + FROZEN25_STRATEGY_ID
            + "."
        )

    if (
        strategy_fingerprint is not None
        and strategy_fingerprint
        != FROZEN25_STRATEGY_FINGERPRINT
    ):
        raise Frozen25HistoryIdentityError(
            "Frozen25 strategy fingerprint mismatch."
        )


def _load_qualified_history_file(
    *,
    path: Path,
    expected_sha256: str,
) -> tuple[Frozen25HistoryRow, ...]:

    resolved = path.resolve()

    if not resolved.is_file():
        raise Frozen25HistoryIntegrityError(
            "Qualified Frozen25 history source is missing: "
            + str(
                resolved
            )
        )

    digest = _digest(
        resolved
    )

    if digest != expected_sha256:
        raise Frozen25HistoryIntegrityError(
            "Frozen25 history SHA256 mismatch."
        )

    with resolved.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:

        reader = csv.DictReader(
            handle
        )

        fieldnames = (
            reader.fieldnames
            or []
        )

        lower_map = {
            str(
                name
            ).strip().lower():
                name
            for name
            in fieldnames
        }

        required = (
            "timestamp",
            "symbol",
            "open",
            "high",
            "low",
            "close",
            "volume",
        )

        missing = [
            name
            for name
            in required
            if name
            not in lower_map
        ]

        if missing:
            raise Frozen25HistoryIntegrityError(
                "Frozen25 history schema mismatch: missing "
                + repr(
                    missing
                )
            )

        parsed_rows = []

        previous_timestamp = None

        for line_number, source_row in enumerate(
            reader,
            start=2,
        ):

            try:

                timestamp = _parse_timestamp(
                    source_row[
                        lower_map[
                            "timestamp"
                        ]
                    ]
                )

                symbol = str(
                    source_row[
                        lower_map[
                            "symbol"
                        ]
                    ]
                ).strip()

                row = Frozen25HistoryRow(
                    timestamp=timestamp,
                    symbol=symbol,
                    open=float(
                        source_row[
                            lower_map[
                                "open"
                            ]
                        ]
                    ),
                    high=float(
                        source_row[
                            lower_map[
                                "high"
                            ]
                        ]
                    ),
                    low=float(
                        source_row[
                            lower_map[
                                "low"
                            ]
                        ]
                    ),
                    close=float(
                        source_row[
                            lower_map[
                                "close"
                            ]
                        ]
                    ),
                    volume=float(
                        source_row[
                            lower_map[
                                "volume"
                            ]
                        ]
                    ),
                )

            except (
                KeyError,
                TypeError,
                ValueError,
            ) as exc:

                raise Frozen25HistoryIntegrityError(
                    "Invalid Frozen25 OHLCV row at CSV line "
                    + str(
                        line_number
                    )
                    + "."
                ) from exc


            if symbol != FROZEN25_HISTORY_SYMBOL:
                raise Frozen25HistoryIntegrityError(
                    "Unexpected Frozen25 history symbol at line "
                    + str(
                        line_number
                    )
                    + ": "
                    + repr(
                        symbol
                    )
                )


            if (
                previous_timestamp
                is not None
                and timestamp
                <= previous_timestamp
            ):
                raise Frozen25HistoryIntegrityError(
                    "Frozen25 timestamps are not strictly increasing."
                )


            previous_timestamp = timestamp

            parsed_rows.append(
                row
            )


    rows = tuple(
        parsed_rows
    )


    if len(
        rows
    ) != FROZEN25_HISTORY_ROW_COUNT:

        raise Frozen25HistoryIntegrityError(
            "Frozen25 history row-count mismatch."
        )


    if not rows:

        raise Frozen25HistoryIntegrityError(
            "Frozen25 history is empty."
        )


    if (
        rows[
            0
        ].timestamp.isoformat(
            sep=" "
        )
        != FROZEN25_HISTORY_FIRST_TIMESTAMP
    ):

        raise Frozen25HistoryIntegrityError(
            "Frozen25 first timestamp mismatch."
        )


    if (
        rows[
            -1
        ].timestamp.isoformat(
            sep=" "
        )
        != FROZEN25_HISTORY_LAST_TIMESTAMP
    ):

        raise Frozen25HistoryIntegrityError(
            "Frozen25 last timestamp mismatch."
        )


    return rows


def load_frozen25_history(
    *,
    strategy_id: str,
    strategy_fingerprint: str | None = None,
) -> Frozen25History:
    """
    Load the one qualified Frozen25 historical source.

    This function is intentionally dormant. Merely defining/importing it
    performs no read. It performs no model load, prediction, database
    operation, network request, runtime activation, or execution.
    """

    _validate_identity(
        strategy_id=strategy_id,
        strategy_fingerprint=strategy_fingerprint,
    )

    path = frozen25_history_path()

    rows = _load_qualified_history_file(
        path=path,
        expected_sha256=FROZEN25_HISTORY_SHA256,
    )

    return Frozen25History(
        strategy_id=FROZEN25_STRATEGY_ID,
        strategy_fingerprint=FROZEN25_STRATEGY_FINGERPRINT,
        source_path=path.resolve(),
        source_sha256=FROZEN25_HISTORY_SHA256,
        rows=rows,
    )


def frozen25_history_contract() -> Mapping[str, object]:
    """
    Return immutable static binding metadata without reading the CSV.
    """

    return MappingProxyType(
        {
            "strategy_id":
                FROZEN25_STRATEGY_ID,

            "strategy_fingerprint":
                FROZEN25_STRATEGY_FINGERPRINT,

            "history_path":
                str(
                    frozen25_history_path()
                ),

            "history_sha256":
                FROZEN25_HISTORY_SHA256,

            "history_row_count":
                FROZEN25_HISTORY_ROW_COUNT,

            "history_symbol":
                FROZEN25_HISTORY_SYMBOL,

            "history_first_timestamp":
                FROZEN25_HISTORY_FIRST_TIMESTAMP,

            "history_last_timestamp":
                FROZEN25_HISTORY_LAST_TIMESTAMP,

            "binding_mode":
                "dormant_read_only",

            "model_load":
                False,

            "prediction":
                False,

            "database_write":
                False,

            "network_request":
                False,

            "runtime_activation":
                False,

            "execution":
                False,
        }
    )
