from backend.app.stacks.chat_public.response_verification import (
    _enforce_authoritative_strategy_identity,
    _load_authoritative_strategy_identity_pairs,
)


def test_v21r3_authoritative_090_identity_exists():

    identities = (
        _load_authoritative_strategy_identity_pairs()
    )

    assert (
        identities[
            "SSRN_3247865_090"
        ]
        ==
        "Intraday arbitrage between index ETFs"
    )


def test_v21r3_correct_090_identity_is_unchanged():

    original = (
        "090 | SSRN_3247865_090 | "
        "Intraday arbitrage between index ETFs"
    )

    assert (
        _enforce_authoritative_strategy_identity(
            original
        )
        == original
    )


def test_v21r3_bad_090_risk_parity_identity_is_repaired():

    original = (
        "090 | SSRN_3247865_090 | Risk parity"
    )

    repaired = (
        _enforce_authoritative_strategy_identity(
            original
        )
    )

    assert (
        "090 | SSRN_3247865_090 | "
        "Intraday arbitrage between index ETFs"
        in repaired
    )

    assert (
        "SSRN_3247865_090 | Risk parity"
        not in repaired
    )


def test_v21r3_citation_token_survives_identity_repair():

    original = (
        "090 | SSRN_3247865_090 | Risk parity "
        "[chunk_deadbeef123]"
    )

    repaired = (
        _enforce_authoritative_strategy_identity(
            original
        )
    )

    assert (
        "[chunk_deadbeef123]"
        in repaired
    )


def test_v21r3_unrelated_response_is_unchanged():

    original = (
        "The portfolio remains within the configured "
        "risk envelope."
    )

    assert (
        _enforce_authoritative_strategy_identity(
            original
        )
        == original
    )


def test_v21r3_does_not_modify_id_without_explicit_name_association():

    original = (
        "Evidence exists for SSRN_3247865_090."
    )

    assert (
        _enforce_authoritative_strategy_identity(
            original
        )
        == original
    )
