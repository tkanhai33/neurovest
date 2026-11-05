from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

STRIPE_API = "https://api.stripe.com/v1"


class StripeTestModeError(RuntimeError):
    pass


def _test_key() -> str:
    key = os.environ.get("NV_STRIPE_TEST_SECRET_KEY", "")

    if not key.startswith("sk_test_") or len(key) < 20:
        raise StripeTestModeError(
            "Stripe test secret key is not configured"
        )

    return key


def _request(
    path: str,
    *,
    fields: dict[str, str] | None = None,
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    if not path.startswith("/") or "://" in path:
        raise StripeTestModeError("invalid_stripe_path")

    key = _test_key()

    headers = {
        "Authorization": "Bearer " + key,
        "Accept": "application/json",
    }

    if fields is not None:
        headers["Content-Type"] = (
            "application/x-www-form-urlencoded"
        )

    if idempotency_key is not None:
        if not (1 <= len(idempotency_key) <= 255):
            raise StripeTestModeError("invalid_idempotency_key")

        headers["Idempotency-Key"] = idempotency_key

    body = (
        urllib.parse.urlencode(fields).encode()
        if fields is not None else None
    )

    request = urllib.request.Request(
        STRIPE_API + path,
        data=body,
        headers=headers,
        method="POST" if fields is not None else "GET",
    )

    try:
        with urllib.request.urlopen(
            request, timeout=15
        ) as response:
            result = json.load(response)
    except (urllib.error.URLError, ValueError) as exc:
        raise StripeTestModeError(
            "stripe_test_request_failed"
        ) from exc

    if not isinstance(result, dict):
        raise StripeTestModeError("invalid_stripe_response")

    if result.get("livemode") is not False:
        raise StripeTestModeError(
            "non_test_stripe_response_rejected"
        )

    return result


def create_checkout_session(
    *,
    intent_id: str,
    stripe_price_id: str,
) -> dict[str, Any]:
    """
    Test-only hosted Stripe subscription Checkout.
    No browser controls these parameters.
    """
    if not (
        isinstance(intent_id, str)
        and intent_id.startswith("nvi_")
        and len(intent_id) <= 100
    ):
        raise StripeTestModeError("invalid_checkout_intent")

    if not (
        isinstance(stripe_price_id, str)
        and stripe_price_id.startswith("price_")
        and len(stripe_price_id) <= 255
    ):
        raise StripeTestModeError("invalid_price_id")

    configured = os.environ.get(
        "NV_STRIPE_TEST_RESEARCH_PRICE_ID", ""
    )

    if not configured or stripe_price_id != configured:
        raise StripeTestModeError(
            "unapproved_research_price"
        )

    fields = {
        "mode": "subscription",
        "line_items[0][price]": stripe_price_id,
        "line_items[0][quantity]": "1",
        "client_reference_id": intent_id,
        "success_url":
            "https://neurovest.ca/?billing=test-success",
        "cancel_url":
            "https://neurovest.ca/?billing=test-cancel",
    }

    result = _request(
        "/checkout/sessions",
        fields=fields,
        idempotency_key=intent_id,
    )

    if (
        not str(result.get("id", "")).startswith("cs_test_")
        or result.get("mode") != "subscription"
        or not str(result.get("url", "")).startswith(
            "https://checkout.stripe.com/"
        )
    ):
        raise StripeTestModeError(
            "invalid_test_checkout_response"
        )

    return {
        "session_id": result["id"],
        "checkout_url": result["url"],
    }


def retrieve_subscription(subscription_id: str):
    if not (
        isinstance(subscription_id, str)
        and subscription_id.startswith("sub_")
        and len(subscription_id) <= 255
    ):
        raise StripeTestModeError("invalid_subscription_id")

    safe_id = urllib.parse.quote(
        subscription_id, safe=""
    )

    result = _request("/subscriptions/" + safe_id)

    if result.get("id") != subscription_id:
        raise StripeTestModeError(
            "subscription_identity_mismatch"
        )

    return result
