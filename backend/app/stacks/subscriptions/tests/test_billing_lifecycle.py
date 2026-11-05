import pytest

from backend.app.stacks.subscriptions import (
    billing_lifecycle as lifecycle,
)


def subscription(
    status="active",
    price="price_test_approved",
):
    return {
        "id": "sub_test_abc",
        "customer": "cus_test_abc",
        "livemode": False,
        "status": status,
        "cancel_at_period_end": False,
        "items": {
            "data": [{
                "price": {
                    "id": price,
                    "livemode": False,
                },
                "current_period_end": 1800000000,
            }]
        },
    }


def session():
    return {
        "id": "cs_test_abc",
        "mode": "subscription",
        "livemode": False,
        "status": "complete",
        "client_reference_id": "nvi_test_abc",
        "customer": "cus_test_abc",
        "subscription": "sub_test_abc",
    }


@pytest.fixture(autouse=True)
def configure_test_price(monkeypatch):
    monkeypatch.setenv(
        "NV_STRIPE_TEST_RESEARCH_PRICE_ID",
        "price_test_approved",
    )


def test_valid_subscription():
    result = lifecycle.verify_subscription(subscription())
    assert result["status"] == "active"
    assert result["price_id"] == "price_test_approved"


@pytest.mark.parametrize("state", [
    "incomplete", "trialing", "active",
    "past_due", "unpaid", "canceled",
    "incomplete_expired", "paused",
])
def test_supported_states(state):
    assert lifecycle.verify_subscription(
        subscription(status=state)
    )["status"] == state


def test_unapproved_price_denied():
    with pytest.raises(lifecycle.BillingLifecycleError):
        lifecycle.verify_subscription(
            subscription(price="price_wrong")
        )


def test_live_subscription_denied():
    obj = subscription()
    obj["livemode"] = True

    with pytest.raises(lifecycle.BillingLifecycleError):
        lifecycle.verify_subscription(obj)


def test_live_price_denied():
    obj = subscription()
    obj["items"]["data"][0]["price"]["livemode"] = True

    with pytest.raises(lifecycle.BillingLifecycleError):
        lifecycle.verify_subscription(obj)


def test_multiple_items_denied():
    obj = subscription()
    obj["items"]["data"].append(
        obj["items"]["data"][0]
    )

    with pytest.raises(lifecycle.BillingLifecycleError):
        lifecycle.verify_subscription(obj)


def test_valid_checkout_identity():
    result = lifecycle.verify_checkout_session(
        session(), "cs_test_abc"
    )

    assert result == (
        "nvi_test_abc",
        "cus_test_abc",
        "sub_test_abc",
    )


def test_unknown_session_denied():
    with pytest.raises(lifecycle.BillingLifecycleError):
        lifecycle.verify_checkout_session(
            session(), "cs_test_other"
        )


def test_incomplete_checkout_denied():
    obj = session()
    obj["status"] = "open"

    with pytest.raises(lifecycle.BillingLifecycleError):
        lifecycle.verify_checkout_session(
            obj, "cs_test_abc"
        )


def test_browser_owner_not_accepted():
    import inspect

    params = inspect.signature(
        lifecycle.begin_test_checkout
    ).parameters

    assert "owner_subject" in params
    assert "stripe_price_id" not in params
    assert "plan" not in params


def test_no_live_order_operations():
    assert not hasattr(
        lifecycle,
        "place_broker_order",
    )
