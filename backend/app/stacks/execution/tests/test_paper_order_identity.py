from uuid import uuid4

import pytest

from backend.app.stacks.execution.paper_order_identity import (
    PaperOrderIdentityConflict,
    PaperOrderIdentityError,
    assert_matching_fingerprint,
    fingerprint_order_intent,
    normalize_order_intent,
    normalize_request_id,
)


def test_valid_request_identity():
    value = uuid4()
    assert normalize_request_id(str(value)) == str(value)


def test_request_identity_is_canonical():
    value = str(uuid4())
    assert normalize_request_id(value.upper()) == value


@pytest.mark.parametrize(
    "value",
    ["", "not-a-uuid", "abc", None, 123],
)
def test_invalid_request_identity_rejected(value):
    with pytest.raises(PaperOrderIdentityError):
        normalize_request_id(value)


def test_normalized_original_intent():
    assert normalize_order_intent(
        symbol=" aapl ",
        action=" BUY ",
    ) == {
        "symbol": "AAPL",
        "action": "buy",
    }


def test_same_order_intent_has_same_fingerprint():
    first = fingerprint_order_intent(
        symbol="aapl",
        action="buy",
    )
    second = fingerprint_order_intent(
        symbol=" AAPL ",
        action="BUY",
    )

    assert first == second
    assert len(first) == 64


def test_changed_action_changes_fingerprint():
    assert fingerprint_order_intent(
        symbol="AAPL",
        action="buy",
    ) != fingerprint_order_intent(
        symbol="AAPL",
        action="sell",
    )


def test_changed_symbol_changes_fingerprint():
    assert fingerprint_order_intent(
        symbol="AAPL",
        action="buy",
    ) != fingerprint_order_intent(
        symbol="MSFT",
        action="buy",
    )


@pytest.mark.parametrize(
    "symbol,action",
    [
        ("", "buy"),
        ("BAD SYMBOL", "buy"),
        ("AAPL", "short"),
        ("AAPL", ""),
        (None, "buy"),
        ("AAPL", None),
    ],
)
def test_invalid_intent_rejected(symbol, action):
    with pytest.raises(PaperOrderIdentityError):
        fingerprint_order_intent(
            symbol=symbol,
            action=action,
        )


def test_matching_fingerprint_accepted():
    value = fingerprint_order_intent(
        symbol="AAPL",
        action="buy",
    )

    assert_matching_fingerprint(
        existing_fingerprint=value,
        incoming_fingerprint=value,
    )


def test_changed_intent_is_conflict():
    with pytest.raises(PaperOrderIdentityConflict):
        assert_matching_fingerprint(
            existing_fingerprint=fingerprint_order_intent(
                symbol="AAPL",
                action="buy",
            ),
            incoming_fingerprint=fingerprint_order_intent(
                symbol="AAPL",
                action="sell",
            ),
        )


def test_corrupt_stored_fingerprint_fails_closed():
    with pytest.raises(PaperOrderIdentityError):
        assert_matching_fingerprint(
            existing_fingerprint="invalid",
            incoming_fingerprint=fingerprint_order_intent(
                symbol="AAPL",
                action="buy",
            ),
        )
