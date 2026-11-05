"""
Authoritative compact strategy-library grounding for NeuroVest chat.

The underlying application-owned JSON is derived from the qualified
strategy-library truth contract. This module performs read-only local
loading only.

It does not:
- run a strategy;
- run training;
- promote a model;
- mutate the repository at runtime;
- access a broker;
- perform live execution.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import re
from typing import Any


STRATEGY_LIBRARY_TRUTH_PATH = Path(
    __file__
).with_name(
    "strategy_library_truth_v1.json"
)


_GLOBAL_STRATEGY_PATTERNS = (
    re.compile(
        r"\bhow\s+many\s+strateg(?:y|ies)\b",
        re.I,
    ),
    re.compile(
        r"\bstrateg(?:y|ies)\s+(?:library|count)\b",
        re.I,
    ),
    re.compile(
        r"\b(?:current|available|pre[- ]?built)\s+strateg(?:y|ies)\b",
        re.I,
    ),
    re.compile(
        r"\bstrateg(?:y|ies)\s+(?:have|has|were|are)\s+"
        r"(?:you\s+)?(?:developed|trained|qualified|promoted|built)\b",
        re.I,
    ),
    re.compile(
        r"\b(?:developed|trained|qualified|promoted|built)\s+"
        r"strateg(?:y|ies)\b",
        re.I,
    ),
    re.compile(
        r"\breview\s+(?:the\s+)?(?:current\s+)?"
        r"(?:pre[- ]?built\s+)?strateg(?:y|ies)\b",
        re.I,
    ),
)


@lru_cache(
    maxsize=1
)
def load_strategy_library_truth() -> dict[str, Any]:
    payload = json.loads(
        STRATEGY_LIBRARY_TRUTH_PATH.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(
        payload,
        dict,
    ):
        raise RuntimeError(
            "strategy-library truth must be a JSON object"
        )

    expected = {
        "research_library_count":
            173,

        "unique_normalized_id_count":
            173,

        "repeated_lifecycle_evidence_count":
            8,

        "structured_model_lineage_count":
            5,
    }

    for key, value in expected.items():

        if payload.get(
            key
        ) != value:
            raise RuntimeError(
                "strategy-library truth contract changed: "
                f"{key}={payload.get(key)!r}; "
                f"expected {value!r}"
            )

    return payload


def strategy_library_truth_requested(
    query: str,
) -> bool:

    normalized = str(
        query
    ).strip()

    if not normalized:
        return False

    # V24-R3 — authoritative strategy-query trigger expansion.
    #
    # Specific SSRN strategy-ID questions and repeated-lifecycle
    # strategy questions require the authoritative strategy-library
    # truth before model generation.
    normalized_lower = normalized.lower()

    # User-specific enabled Strategy Library state is authoritative
    # account context, not global repository strategy-library truth.
    #
    # These questions must be answered from the authenticated user's
    # ENABLED REFERENCE STRATEGY LIBRARY context and must not inject
    # the global 173 / lifecycle / lineage answer contract.
    if (
        "enabled" in normalized_lower
        and "strateg" in normalized_lower
        and "library" in normalized_lower
    ):
        return False

    if "ssrn_3247865_" in normalized_lower:
        return True

    if (
        "strateg" in normalized_lower
        and "lifecycle" in normalized_lower
        and (
            "repeated" in normalized_lower
            or "candidate-specific" in normalized_lower
            or "small-set" in normalized_lower
        )
    ):
        return True

    return any(
        pattern.search(
            normalized
        )
        is not None
        for pattern
        in _GLOBAL_STRATEGY_PATTERNS
    )


def build_strategy_library_truth_prompt(
    query: str,
) -> str:

    if not strategy_library_truth_requested(
        query
    ):
        return ""

    truth = load_strategy_library_truth()

    structured = truth.get(
        "structured_model_lineage",
        [],
    )

    repeated = truth.get(
        "repeated_lifecycle_evidence",
        [],
    )

    lines = [
        "AUTHORITATIVE NEUROVEST STRATEGY LIBRARY TRUTH",
        (
            "This section is trusted local application evidence for "
            "global NeuroVest strategy-library and lifecycle-count claims."
        ),
        (
            "It takes precedence over partial similarity-retrieval excerpts "
            "when answering global library/count/lifecycle questions."
        ),
        "",
        (
            "Normalized research-library strategy count: "
            f"{truth['research_library_count']}"
        ),
        (
            "Unique normalized strategy IDs: "
            f"{truth['unique_normalized_id_count']}"
        ),
        (
            "Strategies with repeated candidate-specific or small-set "
            "lifecycle evidence: "
            f"{truth['repeated_lifecycle_evidence_count']}"
        ),
        (
            "Strategies with strong structured model lineage: "
            f"{truth['structured_model_lineage_count']}"
        ),
        "",
        "MANDATORY CLAIM BOUNDARY:",
        (
            "Repository evidence DOES NOT currently prove an exact count "
            "of strategies developed by NeuroVest."
        ),
        (
            "173 research-library strategies DOES NOT mean NeuroVest "
            "developed, trained, qualified, or promoted all 173."
        ),
        (
            "Research-library membership also does NOT prove that "
            "NeuroVest refined any strategy."
        ),
        (
            "The 5 strategies with strong structured model lineage are "
            "contained within the 8 strategies with repeated lifecycle "
            "evidence."
        ),
        (
            "Therefore the counts 8 and 5 overlap. They are NOT additive. "
            "Never describe them as 13 distinct strategies."
        ),
        (
            "Repeated lifecycle evidence does NOT itself prove a strategy "
            "was developed, trained, qualified, refined, or promoted."
        ),
        (
            "Structured model lineage does NOT itself prove a strategy "
            "was developed, trained, qualified, refined, or promoted."
        ),
        (
            "When asked how many strategies NeuroVest has developed, "
            "explicitly say the exact developed count is not proven by "
            "current repository evidence. Then report the supported facts: "
            "173 normalized research-library entries; 8 with repeated "
            "lifecycle evidence; and 5 of those 8 with structured model "
            "lineage."
        ),
        (
            "Do not infer 'actively developed', 'actively refined', "
            "'developed 8', 'developed 5', or 'developed 13' unless "
            "separate evidence explicitly proves that claim."
        ),
        "",
        "Structured model-lineage strategies:",
    ]

    for row in structured:

        lines.append(
            "  "
            + f"{int(row['ordinal']):03d}"
            + " | "
            + str(
                row[
                    "short_id"
                ]
            )
            + " | "
            + str(
                row[
                    "strategy_name"
                ]
            )
        )

    structured_ordinals = {
        int(
            row[
                "ordinal"
            ]
        )
        for row
        in structured
    }

    additional = [
        row
        for row
        in repeated
        if int(
            row[
                "ordinal"
            ]
        )
        not in structured_ordinals
    ]

    if additional:

        lines.extend(
            [
                "",
                "Additional repeated lifecycle-evidence strategies:",
            ]
        )

        for row in additional:

            lines.append(
                "  "
                + f"{int(row['ordinal']):03d}"
                + " | "
                + str(
                    row[
                        "short_id"
                    ]
                )
                + " | "
                + str(
                    row[
                        "strategy_name"
                    ]
                )
            )

    # V24-R4R1 — request-specific authoritative strategy contract.
    #
    # Explicit SSRN requests must receive a direct authoritative answer.
    import re as _strategy_truth_re

    requested_ids = []

    for match in _strategy_truth_re.findall(
        r"(?i)\bSSRN_[0-9]+_[0-9]+\b",
        str(
            query
        ),
    ):

        canonical = str(
            match
        ).upper()

        if canonical not in requested_ids:

            requested_ids.append(
                canonical
            )

    authoritative_rows = {}

    for row in (
        list(
            structured
        )
        + list(
            repeated
        )
    ):

        short_id = str(
            row.get(
                "short_id",
                "",
            )
        ).strip()

        strategy_name = str(
            row.get(
                "strategy_name",
                "",
            )
        ).strip()

        if short_id and strategy_name:

            normalized_name = _strategy_truth_re.sub(
                r"(?:\s*\.)+\s*$",
                "",
                strategy_name,
            ).strip()

            authoritative_rows[
                short_id.upper()
            ] = normalized_name

    requested_authoritative = [
        (
            strategy_id,
            authoritative_rows[
                strategy_id
            ],
        )
        for strategy_id in requested_ids
        if strategy_id
        in authoritative_rows
    ]

    if requested_authoritative:

        lines.extend(
            [
                "",
                "REQUEST-SPECIFIC AUTHORITATIVE REQUIREMENT:",
                (
                    "The user explicitly requested one or more "
                    "authoritative SSRN strategy IDs."
                ),
                (
                    "You MUST directly answer every requested authoritative "
                    "strategy ID listed below."
                ),
                (
                    "Do NOT omit the requested strategy."
                ),
                (
                    "Do NOT replace the direct answer with only aggregate "
                    "library counts, lifecycle counts, model-lineage counts, "
                    "or the general ANSWER CONTRACT."
                ),
                (
                    "The general claim boundary still applies, but it must "
                    "not prevent answering the specifically requested "
                    "authoritative identity."
                ),
                "",
                "REQUESTED AUTHORITATIVE STRATEGIES:",
            ]
        )

        for strategy_id, strategy_name in requested_authoritative:

            lines.append(
                "  "
                + strategy_id
                + " | "
                + strategy_name
            )

        lines.extend(
            [
                "",
                (
                    "Your final answer MUST visibly include each requested "
                    "SSRN ID together with its authoritative strategy name."
                ),
                (
                    "If the user asks whether a listed authoritative "
                    "strategy exists, answer that question directly."
                ),
            ]
        )

    # V36-R4R2 — an explicit SSRN identifier can be one component
    # of a mixed-domain question. Authoritative identity grounding is
    # supplemental in that case and must not consume the other request.
    _mixed_query_lower = str(
        query
    ).lower()

    _mixed_finance_request = (
        bool(
            requested_ids
        )
        and (
            "general finance" in _mixed_query_lower
            or "general concept" in _mixed_query_lower
            or "distinguish" in _mixed_query_lower
            or "mean reversion" in _mixed_query_lower
        )
    )

    _mixed_developer_request = (
        bool(
            requested_ids
        )
        and (
            "python" in _mixed_query_lower
            or "async" in _mixed_query_lower
            or "await" in _mixed_query_lower
            or "coding" in _mixed_query_lower
            or "code" in _mixed_query_lower
        )
    )

    if (
        _mixed_finance_request
        or _mixed_developer_request
    ):

        lines.extend(
            [
                "",
                "MIXED-DOMAIN REQUEST CONTRACT:",
                (
                    "The SSRN strategy identity is supplemental grounding "
                    "for this request. It MUST NOT replace the user's "
                    "separate finance or developer question."
                ),
                (
                    "Answer the non-strategy concept substantively first, "
                    "then distinguish or mention the authoritative strategy "
                    "identity separately."
                ),
            ]
        )

    lines.extend(
        [
            "",
            "ANSWER CONTRACT:",
            str(
                truth[
                    "answer_contract"
                ]
            ),
        ]
    )

    return "\n".join(
        lines
    )


__all__ = [
    "STRATEGY_LIBRARY_TRUTH_PATH",
    "load_strategy_library_truth",
    "strategy_library_truth_requested",
    "build_strategy_library_truth_prompt",
]
