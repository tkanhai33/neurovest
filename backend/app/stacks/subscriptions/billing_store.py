from __future__ import annotations

from sqlalchemy import text

from .entitlements import (
    Entitlement, Plan, SubscriptionStatus,
    free_entitlement,
)

def valid_owner(owner: str) -> str:
    if (
        not isinstance(owner, str)
        or not (1 <= len(owner) <= 256)
        or owner != owner.strip()
    ):
        raise ValueError("invalid_authenticated_owner")
    return owner


async def ensure_account(engine, *, owner_subject: str):
    owner = valid_owner(owner_subject)

    async with engine.begin() as conn:
        await conn.execute(text("""
            INSERT INTO public.nv_billing_accounts(owner_subject)
            VALUES (:owner)
            ON CONFLICT (owner_subject) DO NOTHING
        """), {"owner": owner})


async def load_entitlement(engine, *, owner_subject: str):
    """
    Server-derived entitlement, not user-supplied plan.
    Missing account or subscription resolves to FREE.
    """
    owner = valid_owner(owner_subject)

    async with engine.connect() as conn:
        rows = (await conn.execute(text("""
            SELECT s.status, s.cancel_at_period_end
            FROM public.nv_billing_subscriptions s
            JOIN public.nv_billing_accounts a
              ON a.owner_subject = s.owner_subject
             AND a.stripe_customer_id = s.stripe_customer_id
            WHERE s.owner_subject = :owner
        """), {"owner": owner})).mappings().all()

    if not rows:
        return free_entitlement(owner)

    # Multiple active or trialing subscriptions are an
    # abnormal billing state: fail closed, not silently upgrade.
    if len(rows) != 1:
        return free_entitlement(owner)

    row = rows[0]

    try:
        status = SubscriptionStatus(row["status"])
    except ValueError:
        return free_entitlement(owner)

    if status not in {
        SubscriptionStatus.ACTIVE,
        SubscriptionStatus.TRIALING,
    }:
        return free_entitlement(owner)

    return Entitlement(
        owner_subject=owner,
        plan=Plan.RESEARCH,
        status=status,
        cancel_at_period_end=row["cancel_at_period_end"],
    )


async def reserve_checkout(
    engine, *,
    owner_subject: str,
    intent_id: str,
):
    owner = valid_owner(owner_subject)

    if not (
        isinstance(intent_id, str)
        and intent_id.startswith("nvi_")
        and len(intent_id) <= 100
    ):
        raise ValueError("invalid_intent_id")

    async with engine.begin() as conn:
        await conn.execute(text("""
            INSERT INTO public.nv_billing_accounts(owner_subject)
            VALUES (:owner)
            ON CONFLICT (owner_subject) DO NOTHING
        """), {"owner": owner})

        await conn.execute(text("""
            INSERT INTO public.nv_billing_checkout_intents(
                intent_id, owner_subject
            )
            VALUES (:intent, :owner)
        """), {
            "intent": intent_id,
            "owner": owner,
        })


async def attach_checkout_session(
    engine, *,
    owner_subject: str,
    intent_id: str,
    stripe_session_id: str,
):
    owner = valid_owner(owner_subject)

    if not (
        isinstance(stripe_session_id, str)
        and stripe_session_id.startswith("cs_test_")
    ):
        raise ValueError("test_checkout_session_required")

    async with engine.begin() as conn:
        result = await conn.execute(text("""
            UPDATE public.nv_billing_checkout_intents
               SET stripe_session_id = :session,
                   state = 'created'
             WHERE intent_id = :intent
               AND owner_subject = :owner
               AND state = 'pending'
        """), {
            "session": stripe_session_id,
            "intent": intent_id,
            "owner": owner,
        })

        if result.rowcount != 1:
            raise PermissionError("checkout_intent_not_owned")


async def record_verified_event(
    engine, *,
    event_id: str,
    event_type: str,
    event_created: int,
    subscription_id: str | None = None,
):
    """
    Persistent duplicate detection, for qualified processors.

    This records a fully processed event, NOT permission to
    grant access. The future event processor must validate
    ownership, Stripe's current subscription state and price,
    and perform entitlement updates in the SAME transaction.
    """
    if not (
        isinstance(event_id, str)
        and event_id.startswith("evt_")
        and isinstance(event_type, str)
        and type(event_created) is int
        and event_created > 0
    ):
        raise ValueError("invalid_verified_event")

    async with engine.begin() as conn:
        result = await conn.execute(text("""
            INSERT INTO public.nv_billing_events(
                stripe_event_id,
                event_type,
                event_created,
                stripe_subscription_id
            )
            VALUES (:id, :type, :created, :subscription)
            ON CONFLICT (stripe_event_id) DO NOTHING
        """), {
            "id": event_id,
            "type": event_type,
            "created": event_created,
            "subscription": subscription_id,
        })

        return result.rowcount == 1
