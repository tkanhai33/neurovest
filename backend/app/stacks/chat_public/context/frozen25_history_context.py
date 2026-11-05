from __future__ import annotations

from typing import Any


from backend.app.stacks.strategy.model_inference.frozen25_history_adapter import (
    FROZEN25_STRATEGY_FINGERPRINT,
    load_frozen25_history,
)


FROZEN25_STRATEGY_ID = "challenger_02952"

FROZEN25_HISTORY_SHA256 = (
    "4658b9dd12f969b2db036be0441d459b0690214a71e97728544a83a0735075f8"
)

MAX_CHAT_HISTORY_ROWS = 20


def _timestamp_text(
    value: Any,
) -> str:

    isoformat = getattr(
        value,
        "isoformat",
        None,
    )

    if callable(
        isoformat
    ):

        try:

            return isoformat(
                sep=" "
            )

        except TypeError:

            return isoformat()

    return str(
        value
    )


def _number_for_context(
    value: Any,
) -> int | float | str | None:

    if value is None:
        return None

    if isinstance(
        value,
        bool,
    ):
        return str(
            value
        )

    if isinstance(
        value,
        int,
    ):
        return value

    if isinstance(
        value,
        float,
    ):
        return value

    try:

        number = float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return str(
            value
        )

    return number


def _serialize_history_row(
    row: Any,
) -> dict[str, Any]:

    return {
        "timestamp":
            _timestamp_text(
                row.timestamp
            ),

        "symbol":
            str(
                row.symbol
            ),

        "open":
            _number_for_context(
                row.open
            ),

        "high":
            _number_for_context(
                row.high
            ),

        "low":
            _number_for_context(
                row.low
            ),

        "close":
            _number_for_context(
                row.close
            ),

        "volume":
            _number_for_context(
                row.volume
            ),
    }


def enrich_frozen25_chat_history(
    rows: list[dict[str, Any]],
    *,
    history_row_limit: int = MAX_CHAT_HISTORY_ROWS,
) -> list[dict[str, Any]]:
    """
    Return a copied StrategyKnowledge payload with bounded Frozen25 history.

    Read-only Chat enrichment only.

    The adapter is invoked only for the canonical challenger_02952 identity
    and exact canonical fingerprint.

    Adapter/history failures preserve the original StrategyKnowledge row.
    """

    bounded_limit = max(
        1,
        min(
            int(
                history_row_limit
            ),
            MAX_CHAT_HISTORY_ROWS,
        ),
    )

    enriched_rows = [
        dict(
            row
        )
        for row
        in rows
    ]


    for index, row in enumerate(
        enriched_rows
    ):

        if row.get(
            "strategy_id"
        ) != FROZEN25_STRATEGY_ID:

            continue


        if row.get(
            "strategy_fingerprint"
        ) != FROZEN25_STRATEGY_FINGERPRINT:

            continue


        try:

            history = load_frozen25_history(
                strategy_id=
                    FROZEN25_STRATEGY_ID,

                strategy_fingerprint=
                    FROZEN25_STRATEGY_FINGERPRINT,
            )


            if history.source_sha256 != (
                FROZEN25_HISTORY_SHA256
            ):

                continue


            recent_rows = list(
                history.rows[
                    -bounded_limit:
                ]
            )


            history_context = {
                "source_digest":
                    history.source_sha256,

                "total_row_count":
                    history.row_count,

                "history_start":
                    _timestamp_text(
                        history.first_timestamp
                    ),

                "history_end":
                    _timestamp_text(
                        history.last_timestamp
                    ),

                "bounded_row_count":
                    len(
                        recent_rows
                    ),

                "rows":
                    [
                        _serialize_history_row(
                            history_row
                        )
                        for history_row
                        in recent_rows
                    ],
            }


            updated = dict(
                row
            )

            updated[
                "history_context"
            ] = history_context


            enriched_rows[
                index
            ] = updated


        except Exception:

            # History enrichment is supplementary.
            # Preserve the existing server-authoritative StrategyKnowledge
            # context if the local history source is unavailable or invalid.
            continue


    return enriched_rows
