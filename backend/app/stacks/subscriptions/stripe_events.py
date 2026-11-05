from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Any


MAX_WEBHOOK_BYTES = 262144

SUPPORTED_EVENTS = frozenset({
    "checkout.session.completed",
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "invoice.payment_failed",
})


class WebhookVerificationError(ValueError):
    pass


@dataclass(frozen=True)
class VerifiedWebhook:
    event_id: str
    event_type: str
    created: int
    payload: dict[str, Any]


def verify_stripe_signature(
    *,
    body: bytes,
    signature_header: str,
    endpoint_secret: str,
    now: int | None = None,
    tolerance_seconds: int = 300,
) -> None:
    """Verify Stripe's timestamped HMAC-SHA256 signature."""

    if not isinstance(body, bytes):
        raise WebhookVerificationError("invalid_body")

    if not body or len(body) > MAX_WEBHOOK_BYTES:
        raise WebhookVerificationError("invalid_body_size")

    if (
        not isinstance(endpoint_secret, str)
        or not endpoint_secret.startswith("whsec_")
        or len(endpoint_secret) < 16
    ):
        raise WebhookVerificationError("invalid_secret")

    if not isinstance(signature_header, str):
        raise WebhookVerificationError("missing_signature")

    fields: dict[str, list[str]] = {}

    for part in signature_header.split(","):
        key, separator, value = part.strip().partition("=")
        if separator:
            fields.setdefault(key, []).append(value)

    timestamps = fields.get("t", [])
    signatures = fields.get("v1", [])

    if len(timestamps) != 1 or not signatures:
        raise WebhookVerificationError("signature_missing")

    try:
        timestamp = int(timestamps[0])
    except (ValueError, TypeError):
        raise WebhookVerificationError("invalid_timestamp") from None

    current = int(time.time()) if now is None else int(now)

    if abs(current - timestamp) > tolerance_seconds:
        raise WebhookVerificationError("expired_signature")

    message = str(timestamp).encode("ascii") + b"." + body

    digest = hmac.new(
        endpoint_secret.encode("utf-8"),
        message,
        hashlib.sha256,
    ).hexdigest()

    if not any(
        hmac.compare_digest(digest, signature)
        for signature in signatures
    ):
        raise WebhookVerificationError("signature_invalid")


def parse_verified_webhook(
    *,
    body: bytes,
    signature_header: str,
    endpoint_secret: str,
    now: int | None = None,
) -> VerifiedWebhook:
    verify_stripe_signature(
        body=body,
        signature_header=signature_header,
        endpoint_secret=endpoint_secret,
        now=now,
    )

    try:
        event = json.loads(body)
    except (UnicodeDecodeError, ValueError):
        raise WebhookVerificationError("invalid_json") from None

    if not isinstance(event, dict):
        raise WebhookVerificationError("invalid_event")

    event_id = event.get("id")
    event_type = event.get("type")
    created = event.get("created")
    data = event.get("data")

    if (
        not isinstance(event_id, str)
        or not event_id.startswith("evt_")
        or not isinstance(event_type, str)
        or type(created) is not int
        or not isinstance(data, dict)
        or not isinstance(data.get("object"), dict)
    ):
        raise WebhookVerificationError("invalid_event_contract")

    return VerifiedWebhook(
        event_id=event_id,
        event_type=event_type,
        created=created,
        payload=event,
    )


def subscription_state_from_event(
    event: VerifiedWebhook,
    *,
    expected_customer_id: str,
    expected_subscription_id: str,
) -> str | None:
    """
    Interpret a verified subscription event.

    Customer/subscription identity must come from an
    existing trusted server-side mapping. Never establish
    account ownership from event metadata.
    """
    if event.event_type not in {
        "customer.subscription.created",
        "customer.subscription.updated",
        "customer.subscription.deleted",
    }:
        return None

    obj = event.payload["data"]["object"]

    if (
        obj.get("customer") != expected_customer_id
        or obj.get("id") != expected_subscription_id
    ):
        raise WebhookVerificationError("billing_identity_mismatch")

    status = obj.get("status")

    allowed = {
        "incomplete",
        "trialing",
        "active",
        "past_due",
        "unpaid",
        "canceled",
        "incomplete_expired",
        "paused",
    }

    if event.event_type == "customer.subscription.deleted":
        return "canceled"

    if not isinstance(status, str) or status not in allowed:
        raise WebhookVerificationError("invalid_subscription_status")

    return status


def should_apply_event(
    *,
    event_id: str,
    event_created: int,
    processed_event_ids: set[str],
    latest_applied_created: int | None,
) -> bool:
    """
    Pure decision helper, NOT persistent replay protection.

    Production callers must reserve event IDs atomically
    in the billing database transaction and reconcile
    equal-timestamp or out-of-order subscription events
    against Stripe's authoritative current state.
    """
    if event_id in processed_event_ids:
        return False

    if (
        latest_applied_created is not None
        and event_created <= latest_applied_created
    ):
        return False

    return True
