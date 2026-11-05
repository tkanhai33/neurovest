from __future__ import annotations

import re

from backend.app.stacks.chat_public.request_route_contract import (
    ChatAnswerRoute,
    ChatRouteContract,
)

from backend.app.stacks.chat_public.rag.strategy_library_truth import (
    load_strategy_library_truth,
)


_SSRN_PATTERN = re.compile(
    r"\bSSRN_3247865_\d{3}\b",
    re.IGNORECASE,
)


def _clean_name(
    value,
) -> str:

    result = str(
        value or ""
    ).strip()

    while result.endswith("."):
        result = result[:-1].rstrip()

    return result


def _rows():

    truth = load_strategy_library_truth()

    rows = []

    for raw in truth.get(
        "repeated_lifecycle_evidence",
        [],
    ):

        rows.append(
            {
                "ordinal":
                    int(
                        raw["ordinal"]
                    ),

                "short_id":
                    str(
                        raw["short_id"]
                    ).strip(),

                "strategy_name":
                    _clean_name(
                        raw[
                            "strategy_name"
                        ]
                    ),
            }
        )

    rows.sort(
        key=lambda row:
            row["ordinal"]
    )

    return truth, rows


def deterministic_strategy_answer(
    query: str,
    route_contract: ChatRouteContract,
):

    route = route_contract.route

    if route not in (
        ChatAnswerRoute.STRATEGY_LIBRARY_LIST,
        ChatAnswerRoute.STRATEGY_LIBRARY_COUNT,
        ChatAnswerRoute.STRATEGY_LIBRARY_IDENTITY,
    ):
        return None

    truth, rows = _rows()

    if route == ChatAnswerRoute.STRATEGY_LIBRARY_LIST:

        lines = [
            "The repeated lifecycle-evidence strategies are:",
            "",
        ]

        for row in rows:

            lines.append(
                f'{row["ordinal"]:03d}'
                + " | "
                + row["short_id"]
                + " | "
                + row["strategy_name"]
            )

        return "\n".join(
            lines
        )

    if route == ChatAnswerRoute.STRATEGY_LIBRARY_COUNT:

        count = int(
            truth[
                "repeated_lifecycle_evidence_count"
            ]
        )

        return (
            "NeuroVest has "
            + str(count)
            + " strategies with repeated "
            "candidate-specific or small-set "
            "lifecycle evidence."
        )

    query_text = str(
        query or ""
    )

    match = _SSRN_PATTERN.search(
        query_text
    )

    if match is None:

        normalized_query = re.sub(
            r"[^a-z0-9]+",
            " ",
            query_text.lower(),
        ).strip()

        matching_rows = []

        for row in rows:

            strategy_name = str(
                row.get(
                    "strategy_name",
                    "",
                )
            ).strip()

            normalized_name = re.sub(
                r"[^a-z0-9]+",
                " ",
                strategy_name.lower(),
            ).strip()

            if (
                normalized_name
                and normalized_name
                in normalized_query
            ):
                matching_rows.append(
                    row
                )

        if len(
            matching_rows
        ) == 1:

            row = matching_rows[0]

            return (
                row["strategy_name"]
                + " is "
                + row["short_id"]
                + "."
            )

        return None

    wanted = match.group(0).upper()

    for row in rows:

        if row["short_id"].upper() != wanted:
            continue

        return (
            row["short_id"]
            + " is "
            + row["strategy_name"]
            + "."
        )

    return (
        wanted
        + " is not present in the authoritative "
        "repeated-lifecycle strategy set."
    )


__all__ = [
    "deterministic_strategy_answer",
]
