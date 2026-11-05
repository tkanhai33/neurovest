from __future__ import annotations

from backend.app.stacks.chat_public.rag.live_retrieval import (
    LIVE_RAG_CANDIDATE_TOP_K,
    LIVE_RAG_TOP_K,
    retrieve_live_evidence,
)

from backend.app.stacks.chat_public.rag.strategy_library_truth import (
    build_strategy_library_truth_prompt,
    load_strategy_library_truth,
    strategy_library_truth_requested,
)


def test_authoritative_strategy_truth_counts() -> None:

    truth = load_strategy_library_truth()

    assert truth[
        "research_library_count"
    ] == 173

    assert truth[
        "unique_normalized_id_count"
    ] == 173

    assert truth[
        "repeated_lifecycle_evidence_count"
    ] == 8

    assert truth[
        "structured_model_lineage_count"
    ] == 5


def test_how_many_strategies_question_is_detected() -> None:

    assert strategy_library_truth_requested(
        "How many strategies have you developed?"
    )

    assert strategy_library_truth_requested(
        "Analyze and review the current library of pre-built strategies"
    )

    assert strategy_library_truth_requested(
        "How many strategies are in the current strategy library?"
    )


def test_specific_strategy_question_does_not_force_global_truth() -> None:

    assert not strategy_library_truth_requested(
        "Explain how sector momentum rotation works."
    )

    assert not strategy_library_truth_requested(
        "What is mean reversion?"
    )


def test_enabled_strategy_library_identity_does_not_force_global_truth() -> None:

    assert not strategy_library_truth_requested(
        "Which reference strategy is currently enabled in my Strategy Library? "
        "Answer using my enabled Strategy Library context."
    )

    assert not strategy_library_truth_requested(
        "What strategies are enabled in my Strategy Library?"
    )

    assert not strategy_library_truth_requested(
        "How many strategies are enabled in my Strategy Library?"
    )


def test_authoritative_prompt_preserves_claim_boundary() -> None:

    prompt = build_strategy_library_truth_prompt(
        "How many strategies have you developed?"
    )

    assert (
        "Normalized research-library strategy count: 173"
        in prompt
    )

    assert (
        "lifecycle evidence: 8"
        in prompt
    )

    assert (
        "strong structured model lineage: 5"
        in prompt
    )

    assert (
        "DOES NOT mean NeuroVest developed, trained, "
        "qualified, or promoted all 173"
        in prompt
    )


def test_strategy_truth_grounding_does_not_require_semantic_index() -> None:

    bundle = retrieve_live_evidence(
        "How many strategies have you developed?",
        requested=False,
    )

    assert bundle.requested is True
    assert bundle.authoritative_grounding is True
    assert bundle.grounded is True
    assert bundle.results == ()
    assert bundle.citations == ()

    assert (
        "AUTHORITATIVE NEUROVEST STRATEGY LIBRARY TRUTH"
        in bundle.prompt_section
    )

    assert (
        "173"
        in bundle.prompt_section
    )

    assert (
        "8"
        in bundle.prompt_section
    )

    assert (
        "5"
        in bundle.prompt_section
    )


def test_unrelated_nonretrieval_query_remains_not_requested() -> None:

    bundle = retrieve_live_evidence(
        "Hello Neuro",
        requested=False,
    )

    assert bundle.requested is False
    assert bundle.authoritative_grounding is False
    assert bundle.grounded is False
    assert bundle.results == ()
    assert bundle.prompt_section == ""
    assert bundle.citations == ()
    assert bundle.error is None


def test_existing_semantic_retrieval_bounds_are_unchanged() -> None:

    assert LIVE_RAG_CANDIDATE_TOP_K == 12
    assert LIVE_RAG_TOP_K == 5
def test_strategy_truth_semantic_contract_v11() -> None:

    from backend.app.stacks.chat_public.rag.strategy_library_truth import (
        build_strategy_library_truth_prompt,
        load_strategy_library_truth,
    )

    truth = load_strategy_library_truth()

    assert truth[
        "research_library_count"
    ] == 173

    assert truth[
        "repeated_lifecycle_evidence_count"
    ] == 8

    assert truth[
        "structured_model_lineage_count"
    ] == 5

    relationship = truth[
        "evidence_set_relationship"
    ]

    assert relationship[
        "structured_model_lineage_is_subset_of_repeated_lifecycle"
    ] is True

    assert relationship[
        "intersection_count"
    ] == 5

    assert relationship[
        "distinct_union_count"
    ] == 8

    assert relationship[
        "counts_are_additive"
    ] is False

    prompt = build_strategy_library_truth_prompt(
        "How many strategies have you developed?"
    )

    lowered = prompt.lower()

    assert (
        "does not currently prove an exact count"
        in lowered
    )

    assert (
        "5 strategies with strong structured model lineage"
        in lowered
    )

    assert (
        "contained within the 8 strategies"
        in lowered
    )

    assert (
        "not additive"
        in lowered
    )

    assert (
        "never describe them as 13 distinct strategies"
        in lowered
    )

    assert (
        "actively developed"
        in lowered
    )

    assert (
        "do not infer"
        in lowered
    )


def test_strategy_truth_developed_count_is_not_derived_from_evidence_sets_v11() -> None:

    from backend.app.stacks.chat_public.rag.strategy_library_truth import (
        load_strategy_library_truth,
    )

    truth = load_strategy_library_truth()

    lifecycle_ids = {
        row[
            "short_id"
        ]
        for row
        in truth[
            "repeated_lifecycle_evidence"
        ]
    }

    structured_ids = {
        row[
            "short_id"
        ]
        for row
        in truth[
            "structured_model_lineage"
        ]
    }

    assert len(
        lifecycle_ids
    ) == 8

    assert len(
        structured_ids
    ) == 5

    assert structured_ids.issubset(
        lifecycle_ids
    )

    assert len(
        lifecycle_ids
        | structured_ids
    ) == 8

    assert len(
        lifecycle_ids
    ) + len(
        structured_ids
    ) == 13

    assert len(
        lifecycle_ids
        | structured_ids
    ) != 13


def test_strategy_truth_answer_contract_forbids_development_overclaim_v11() -> None:

    from backend.app.stacks.chat_public.rag.strategy_library_truth import (
        load_strategy_library_truth,
    )

    truth = load_strategy_library_truth()

    contract = truth[
        "answer_contract"
    ].lower()

    boundaries = "\n".join(
        truth[
            "claim_boundaries"
        ]
    ).lower()

    combined = (
        contract
        + "\n"
        + boundaries
    )

    assert (
        "does not currently prove an exact number"
        in contract
    )

    assert (
        "five of those eight"
        in contract
    )

    assert (
        "8 + 5 must never be presented as 13"
        in contract
    )

    assert (
        "developed 13"
        in combined
    )

    assert (
        "exact developed count is not proven"
        in combined
    )

    assert (
        "refined"
        in combined
    )
