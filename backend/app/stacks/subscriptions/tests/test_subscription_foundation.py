import hashlib
import hmac
import json

import pytest

from backend.app.stacks.subscriptions.entitlements import (
    Entitlement,
    Plan,
    SubscriptionStatus,
    free_entitlement,
    require_entitlement,
)
from backend.app.stacks.subscriptions.stripe_events import (
    WebhookVerificationError,
    parse_verified_webhook,
    should_apply_event,
    subscription_state_from_event,
)


SECRET = "whsec_test_neurovest_subscription_foundation"


def signed_event(
    event_type="customer.subscription.updated",
    *,
    status="active",
    timestamp=1800000000,
    customer="cus_alice",
    subscription="sub_alice",
):
    event = {
        "id": "evt_neurovest_test_001",
        "type": event_type,
        "created": timestamp,
        "data": {
            "object": {
                "id": subscription,
                "customer": customer,
                "status": status,
            }
        },
    }

    body = json.dumps(event).encode()
    message = str(timestamp).encode() + b"." + body

    signature = hmac.new(
        SECRET.encode(),
        message,
        hashlib.sha256,
    ).hexdigest()

    return body, f"t={timestamp},v1={signature}"


def test_free_access_preserved():
    ent = free_entitlement("alice")

    assert ent.allows("chat")
    assert ent.allows("universe.configure")
    assert ent.allows("analysis.basic")
    assert not ent.allows("analysis.premium")


def test_paid_access():
    ent = Entitlement(
        owner_subject="alice",
        plan=Plan.RESEARCH,
        status=SubscriptionStatus.ACTIVE,
    )

    assert ent.allows("analysis.premium")
    assert ent.allows("research.saved_reports")


def test_cancellation_at_period_end():
    ent = Entitlement(
        owner_subject="alice",
        plan=Plan.RESEARCH,
        status=SubscriptionStatus.ACTIVE,
        cancel_at_period_end=True,
    )

    assert ent.paid_active


@pytest.mark.parametrize("status", [
    SubscriptionStatus.NONE,
    SubscriptionStatus.INCOMPLETE,
    SubscriptionStatus.PAST_DUE,
    SubscriptionStatus.UNPAID,
    SubscriptionStatus.CANCELED,
    SubscriptionStatus.INCOMPLETE_EXPIRED,
    SubscriptionStatus.PAUSED,
])
def test_non_active_statuses_denied(status):
    ent = Entitlement(
        owner_subject="alice",
        plan=Plan.RESEARCH,
        status=status,
    )

    assert not ent.allows("analysis.premium")
    assert ent.allows("chat")


def test_owner_mismatch_denied():
    ent = Entitlement(
        owner_subject="alice",
        plan=Plan.RESEARCH,
        status=SubscriptionStatus.ACTIVE,
    )

    with pytest.raises(PermissionError):
        require_entitlement(
            ent,
            authenticated_owner_subject="bob",
            feature="analysis.premium",
        )


def test_unknown_feature_denied():
    ent = Entitlement(
        owner_subject="alice",
        plan=Plan.RESEARCH,
        status=SubscriptionStatus.ACTIVE,
    )

    assert not ent.allows("broker.live_orders")


def test_valid_signed_event():
    body, header = signed_event()

    event = parse_verified_webhook(
        body=body,
        signature_header=header,
        endpoint_secret=SECRET,
        now=1800000000,
    )

    assert event.event_type == "customer.subscription.updated"

    assert subscription_state_from_event(
        event,
        expected_customer_id="cus_alice",
        expected_subscription_id="sub_alice",
    ) == "active"


def test_tampered_payload_rejected():
    body, header = signed_event()

    with pytest.raises(WebhookVerificationError):
        parse_verified_webhook(
            body=body + b" ",
            signature_header=header,
            endpoint_secret=SECRET,
            now=1800000000,
        )


def test_expired_signature_rejected():
    body, header = signed_event()

    with pytest.raises(WebhookVerificationError):
        parse_verified_webhook(
            body=body,
            signature_header=header,
            endpoint_secret=SECRET,
            now=1800001000,
        )


def test_customer_mismatch_rejected():
    body, header = signed_event()

    event = parse_verified_webhook(
        body=body,
        signature_header=header,
        endpoint_secret=SECRET,
        now=1800000000,
    )

    with pytest.raises(WebhookVerificationError):
        subscription_state_from_event(
            event,
            expected_customer_id="cus_bob",
            expected_subscription_id="sub_alice",
        )


def test_deleted_subscription_denied():
    body, header = signed_event(
        event_type="customer.subscription.deleted",
        status="active",
    )

    event = parse_verified_webhook(
        body=body,
        signature_header=header,
        endpoint_secret=SECRET,
        now=1800000000,
    )

    assert subscription_state_from_event(
        event,
        expected_customer_id="cus_alice",
        expected_subscription_id="sub_alice",
    ) == "canceled"


def test_duplicate_event_decision():
    assert not should_apply_event(
        event_id="evt_123",
        event_created=100,
        processed_event_ids={"evt_123"},
        latest_applied_created=50,
    )


def test_stale_event_decision():
    assert not should_apply_event(
        event_id="evt_new",
        event_created=50,
        processed_event_ids=set(),
        latest_applied_created=100,
    )


def test_new_event_decision():
    assert should_apply_event(
        event_id="evt_new",
        event_created=101,
        processed_event_ids=set(),
        latest_applied_created=100,
    )
