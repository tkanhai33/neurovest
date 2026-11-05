from __future__ import annotations

import os
import secrets
from datetime import datetime, timezone

from sqlalchemy import text

from . import billing_store, stripe_test_client
from .stripe_events import (
    parse_verified_webhook,
    WebhookVerificationError,
)

SUB_EVENTS = {
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
}


class BillingLifecycleError(ValueError):
    pass


def approved_price():
    price = os.getenv(
        "NV_STRIPE_TEST_RESEARCH_PRICE_ID", ""
    )

    if not price.startswith("price_"):
        raise BillingLifecycleError("test_price_not_configured")

    return price


def verify_subscription(sub):
    """Validate authoritative Stripe subscription data."""
    if not isinstance(sub, dict):
        raise BillingLifecycleError("invalid_subscription")

    if sub.get("livemode") is not False:
        raise BillingLifecycleError("live_object_forbidden")

    sid = sub.get("id")
    customer = sub.get("customer")
    status = sub.get("status")
    items = sub.get("items", {}).get("data", [])

    if not (
        isinstance(sid, str)
        and sid.startswith("sub_")
        and isinstance(customer, str)
        and customer.startswith("cus_")
    ):
        raise BillingLifecycleError("invalid_subscription_identity")

    if status not in {
        "incomplete", "trialing", "active", "past_due",
        "unpaid", "canceled", "incomplete_expired", "paused",
    }:
        raise BillingLifecycleError("invalid_subscription_status")

    if not isinstance(items, list) or len(items) != 1:
        raise BillingLifecycleError("unexpected_subscription_items")

    item = items[0]
    if not isinstance(item, dict):
        raise BillingLifecycleError("invalid_subscription_item")

    price = item.get("price")
    if not isinstance(price, dict):
        raise BillingLifecycleError("missing_subscription_price")

    if price.get("id") != approved_price():
        raise BillingLifecycleError("unapproved_subscription_price")

    if price.get("livemode") is not False:
        raise BillingLifecycleError("live_price_forbidden")

    end = item.get("current_period_end")
    if end is not None and (
        type(end) is not int or end <= 0
    ):
        raise BillingLifecycleError("invalid_period_end")

    return {
        "subscription_id": sid,
        "customer_id": customer,
        "price_id": price["id"],
        "status": status,
        "cancel_at_period_end": (
            sub.get("cancel_at_period_end") is True
        ),
        "period_end": (
            datetime.fromtimestamp(end, timezone.utc)
            if end is not None else None
        ),
    }


def verify_checkout_session(session, expected_session_id):
    if not isinstance(session, dict):
        raise BillingLifecycleError("invalid_checkout_session")

    if (
        session.get("id") != expected_session_id
        or session.get("livemode") is not False
        or session.get("mode") != "subscription"
        or session.get("status") != "complete"
    ):
        raise BillingLifecycleError("checkout_not_verified")

    intent = session.get("client_reference_id")
    customer = session.get("customer")
    subscription = session.get("subscription")

    if not (
        isinstance(intent, str)
        and intent.startswith("nvi_")
        and isinstance(customer, str)
        and customer.startswith("cus_")
        and isinstance(subscription, str)
        and subscription.startswith("sub_")
    ):
        raise BillingLifecycleError("checkout_identity_invalid")

    return intent, customer, subscription


def _stripe_session(session_id):
    if not (
        isinstance(session_id, str)
        and session_id.startswith("cs_test_")
        and len(session_id) <= 255
    ):
        raise BillingLifecycleError("invalid_test_session")

    from urllib.parse import quote

    return stripe_test_client._request(
        "/checkout/sessions/" + quote(session_id, safe="")
    )


async def begin_test_checkout(engine, *, owner_subject):
    """
    Called only after future authenticated route checks.

    No plan, owner or Stripe price is accepted from a browser.
    This function has no public route in this batch.
    """
    owner = billing_store.valid_owner(owner_subject)
    price = approved_price()

    # Test API configuration is mandatory before DB work.
    stripe_test_client._test_key()

    async with engine.connect() as conn:
        existing = (await conn.execute(text("""
            SELECT stripe_customer_id
            FROM public.nv_billing_accounts
            WHERE owner_subject = :owner
        """), {"owner": owner})).scalar_one_or_none()

        subscriptions = (await conn.execute(text("""
            SELECT status
            FROM public.nv_billing_subscriptions
            WHERE owner_subject = :owner
              AND status NOT IN (
                'canceled','incomplete_expired'
              )
        """), {"owner": owner})).scalars().all()

    if subscriptions:
        raise BillingLifecycleError(
            "existing_subscription_requires_management"
        )

    intent = "nvi_" + secrets.token_hex(20)

    await billing_store.reserve_checkout(
        engine,
        owner_subject=owner,
        intent_id=intent,
    )

    fields = {
        "mode": "subscription",
        "line_items[0][price]": price,
        "line_items[0][quantity]": "1",
        "client_reference_id": intent,
        "success_url":
            "https://neurovest.ca/?billing=test-success",
        "cancel_url":
            "https://neurovest.ca/?billing=test-cancel",
    }

    if existing:
        fields["customer"] = existing

    session = stripe_test_client._request(
        "/checkout/sessions",
        fields=fields,
        idempotency_key=intent,
    )

    session_id = session.get("id")

    if (
        not isinstance(session_id, str)
        or not session_id.startswith("cs_test_")
        or session.get("mode") != "subscription"
        or session.get("client_reference_id") != intent
    ):
        raise BillingLifecycleError(
            "test_checkout_response_invalid"
        )

    await billing_store.attach_checkout_session(
        engine,
        owner_subject=owner,
        intent_id=intent,
        stripe_session_id=session_id,
    )

    url = session.get("url")

    if (
        not isinstance(url, str)
        or not url.startswith(
            "https://checkout.stripe.com/"
        )
    ):
        raise BillingLifecycleError("checkout_url_invalid")

    return {
        "intent_id": intent,
        "session_id": session_id,
        "checkout_url": url,
        "mode": "test",
    }


async def process_signed_event(
    engine, *, body: bytes, signature_header: str,
    webhook_secret: str,
):
    """
    Verify signature, reconcile authoritative Stripe data,
    and update owner mapping, subscription and event ledger
    in one PostgreSQL transaction.

    Requires a trusted server-side webhook secret.
    No HTTP endpoint is mounted in this batch.
    """
    verified = parse_verified_webhook(
        body=body,
        signature_header=signature_header,
        endpoint_secret=webhook_secret,
    )

    event = verified.payload

    if event.get("livemode") is not False:
        raise BillingLifecycleError(
            "live_billing_event_forbidden"
        )

    event_type = verified.event_type
    obj = event["data"]["object"]

    if event_type == "checkout.session.completed":
        session_id = obj.get("id")
        session = _stripe_session(session_id)
        intent, customer, sid = verify_checkout_session(
            session, session_id
        )

        sub = verify_subscription(
            stripe_test_client.retrieve_subscription(sid)
        )

        if sub["customer_id"] != customer:
            raise BillingLifecycleError(
                "checkout_customer_subscription_mismatch"
            )

    elif event_type in SUB_EVENTS:
        sid = obj.get("id")
        if not (
            isinstance(sid, str)
            and sid.startswith("sub_")
        ):
            raise BillingLifecycleError(
                "missing_subscription_identity"
            )

        sub = verify_subscription(
            stripe_test_client.retrieve_subscription(sid)
        )

        if obj.get("customer") != sub["customer_id"]:
            raise BillingLifecycleError(
                "subscription_customer_mismatch"
            )

        session_id = None
        intent = None
        customer = sub["customer_id"]

    else:
        # Unsupported events do not modify entitlements.
        return {"result": "ignored", "event_type": event_type}

    async with engine.begin() as conn:
        # The event ID is locked transactionally through
        # its primary-key unique constraint.
        prior = (await conn.execute(text("""
            SELECT stripe_event_id
            FROM public.nv_billing_events
            WHERE stripe_event_id = :id
        """), {"id": verified.event_id})).first()

        if prior:
            return {"result": "duplicate"}

        if session_id is not None:
            checkout = (await conn.execute(text("""
                SELECT owner_subject, stripe_session_id, state
                FROM public.nv_billing_checkout_intents
                WHERE intent_id = :intent
                FOR UPDATE
            """), {"intent": intent})).mappings().first()

            if (
                checkout is None
                or checkout["stripe_session_id"] != session_id
                or checkout["state"] not in (
                    "created", "completed"
                )
            ):
                raise BillingLifecycleError(
                    "checkout_intent_not_owned_or_unknown"
                )

            owner = checkout["owner_subject"]

        else:
            mapping = (await conn.execute(text("""
                SELECT owner_subject, stripe_customer_id
                FROM public.nv_billing_subscriptions
                WHERE stripe_subscription_id = :sid
                FOR UPDATE
            """), {"sid": sid})).mappings().first()

            if (
                mapping is None
                or mapping["stripe_customer_id"] != customer
            ):
                raise BillingLifecycleError(
                    "unmapped_subscription"
                )

            owner = mapping["owner_subject"]

        account = (await conn.execute(text("""
            SELECT owner_subject, stripe_customer_id
            FROM public.nv_billing_accounts
            WHERE owner_subject = :owner
            FOR UPDATE
        """), {"owner": owner})).mappings().first()

        if account is None:
            raise BillingLifecycleError("billing_account_missing")

        if account["stripe_customer_id"] not in (
            None, customer
        ):
            raise BillingLifecycleError(
                "stripe_customer_owner_conflict"
            )

        if (
            session_id is None
            and account["stripe_customer_id"] != customer
        ):
            raise BillingLifecycleError(
                "unbound_stripe_customer"
            )

        if session_id is not None:
            await conn.execute(text("""
                UPDATE public.nv_billing_accounts
                SET stripe_customer_id = :customer,
                    updated_at = now()
                WHERE owner_subject = :owner
                  AND (
                    stripe_customer_id IS NULL
                    OR stripe_customer_id = :customer
                  )
            """), {
                "owner": owner, "customer": customer
            })

        # Serialize concurrent subscription updates.
        previous = (await conn.execute(text("""
            SELECT owner_subject, stripe_customer_id
            FROM public.nv_billing_subscriptions
            WHERE stripe_subscription_id = :sid
            FOR UPDATE
        """), {"sid": sid})).mappings().first()

        if previous and (
            previous["owner_subject"] != owner
            or previous["stripe_customer_id"] != customer
        ):
            raise BillingLifecycleError(
                "subscription_owner_conflict"
            )

        if session_id is None and previous is None:
            raise BillingLifecycleError(
                "subscription_not_registered"
            )

        await conn.execute(text("""
            INSERT INTO public.nv_billing_subscriptions (
                stripe_subscription_id,
                owner_subject,
                stripe_customer_id,
                stripe_price_id,
                status,
                cancel_at_period_end,
                current_period_end,
                last_event_created
            )
            VALUES (
                :sid, :owner, :customer, :price,
                :status, :cancel, :period_end, :created
            )
            ON CONFLICT (stripe_subscription_id)
            DO UPDATE SET
                status = EXCLUDED.status,
                stripe_price_id = EXCLUDED.stripe_price_id,
                cancel_at_period_end =
                    EXCLUDED.cancel_at_period_end,
                current_period_end =
                    EXCLUDED.current_period_end,
                last_event_created =
                    EXCLUDED.last_event_created,
                updated_at = now()
            WHERE
                nv_billing_subscriptions.owner_subject =
                    EXCLUDED.owner_subject
                AND
                nv_billing_subscriptions.stripe_customer_id =
                    EXCLUDED.stripe_customer_id
        """), {
            "sid": sub["subscription_id"],
            "owner": owner,
            "customer": customer,
            "price": sub["price_id"],
            "status": sub["status"],
            "cancel": sub["cancel_at_period_end"],
            "period_end": sub["period_end"],
            "created": verified.created,
        })

        if session_id is not None:
            await conn.execute(text("""
                UPDATE public.nv_billing_checkout_intents
                SET state = 'completed'
                WHERE intent_id = :intent
                  AND owner_subject = :owner
            """), {"intent": intent, "owner": owner})

        await conn.execute(text("""
            INSERT INTO public.nv_billing_events (
                stripe_event_id,
                event_type,
                event_created,
                stripe_subscription_id
            )
            VALUES (:id, :type, :created, :sid)
        """), {
            "id": verified.event_id,
            "type": event_type,
            "created": verified.created,
            "sid": sub["subscription_id"],
        })

    return {
        "result": "processed",
        "event_type": event_type,
        "subscription_status": sub["status"],
    }
