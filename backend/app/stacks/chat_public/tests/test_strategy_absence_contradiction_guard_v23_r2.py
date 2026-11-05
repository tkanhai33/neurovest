from __future__ import annotations

from backend.app.stacks.chat_public.math_tools.live_math import (
    LiveMathBundle,
)
from backend.app.stacks.chat_public.rag.live_retrieval import (
    LiveRetrievalBundle,
)
from backend.app.stacks.chat_public.response_verification import (
    _enforce_authoritative_strategy_presence,
    verify_response,
)


TOKEN = "[chunk_v23r2probe123]"


def _math_bundle() -> LiveMathBundle:
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


def _retrieval_bundle() -> LiveRetrievalBundle:
    return LiveRetrievalBundle(
        requested=True,
        results=(),
        prompt_section="",
        citations=(
            {
                "citation": TOKEN,
                "chunk_id": "chunk_v23r2probe123",
                "document_id": "v23-r2-probe",
                "source_path": "knowledge/research/v23_r2_probe.pdf",
                "title": "V23-R2 Approved Citation Probe",
                "page_number": 1,
                "score": 1.0,
            },
        ),
        error=None,
        authoritative_grounding=False,
    )


def test_exact_v22_false_absence_is_repaired() -> None:
    original = (
        "I could not find reliable information about "
        "SSRN_3247865_090. "
        "This strategy does not exist among the repeated "
        "lifecycle-evidence strategies. "
        + TOKEN
    )

    repaired = _enforce_authoritative_strategy_presence(
        original
    )

    lowered = repaired.lower()

    assert "ssrn_3247865_090" in lowered
    assert (
        "intraday arbitrage between index etfs"
        in lowered
    )
    assert "does not exist" not in lowered
    assert "could not find reliable information" not in lowered
    assert TOKEN in repaired


def test_no_mention_claim_for_known_090_is_repaired() -> None:
    original = (
        "There is no mention of SSRN_3247865_090 "
        "in the available strategy information. "
        + TOKEN
    )

    repaired = _enforce_authoritative_strategy_presence(
        original
    )

    lowered = repaired.lower()

    assert "ssrn_3247865_090" in lowered
    assert (
        "intraday arbitrage between index etfs"
        in lowered
    )
    assert "no mention of ssrn_3247865_090" not in lowered
    assert TOKEN in repaired


def test_correct_authoritative_identity_is_unchanged() -> None:
    original = (
        "090 | SSRN_3247865_090 | "
        "Intraday arbitrage between index ETFs "
        + TOKEN
    )

    repaired = _enforce_authoritative_strategy_presence(
        original
    )

    assert repaired == original


def test_unknown_ssrn_absence_claim_is_not_invented() -> None:
    original = (
        "I could not find information about "
        "SSRN_9999999_999. "
        + TOKEN
    )

    repaired = _enforce_authoritative_strategy_presence(
        original
    )

    assert repaired == original


def test_unrelated_conversation_is_unchanged() -> None:
    original = (
        "Portfolio risk remains within the configured "
        "simulation boundary."
    )

    repaired = _enforce_authoritative_strategy_presence(
        original
    )

    assert repaired == original


def test_full_verify_response_repairs_false_absence_and_preserves_citation() -> None:
    original = (
        "I could not find reliable information about "
        "SSRN_3247865_090. "
        "This strategy does not exist among the repeated "
        "lifecycle-evidence strategies. "
        + TOKEN
    )

    result = verify_response(
        original,
        math_bundle=_math_bundle(),
        retrieval_bundle=_retrieval_bundle(),
    )

    final_response = result.final_response
    lowered = final_response.lower()

    assert result.fail_closed is False
    assert "ssrn_3247865_090" in lowered
    assert (
        "intraday arbitrage between index etfs"
        in lowered
    )
    assert "does not exist" not in lowered
    assert "could not find reliable information" not in lowered
    assert TOKEN in final_response


def test_v21_r3_risk_parity_identity_guard_still_operates() -> None:
    original = (
        "090 | SSRN_3247865_090 | "
        "Risk parity "
        + TOKEN
    )

    result = verify_response(
        original,
        math_bundle=_math_bundle(),
        retrieval_bundle=_retrieval_bundle(),
    )

    lowered = result.final_response.lower()

    assert result.fail_closed is False
    assert "ssrn_3247865_090" in lowered
    assert (
        "intraday arbitrage between index etfs"
        in lowered
    )
    assert "risk parity" not in lowered
    assert TOKEN in result.final_response
