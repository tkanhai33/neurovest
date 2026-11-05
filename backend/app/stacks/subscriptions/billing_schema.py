from __future__ import annotations

from sqlalchemy import text

# PostgreSQL-only, additive tables. These tables do not
# modify existing identity, strategy or financial-analysis data.

DDL = """
CREATE TABLE IF NOT EXISTS public.nv_billing_accounts (
    owner_subject TEXT PRIMARY KEY,
    stripe_customer_id TEXT UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (length(owner_subject) BETWEEN 1 AND 256),
    CHECK (
        stripe_customer_id IS NULL
        OR stripe_customer_id LIKE 'cus_%'
    )
);

CREATE TABLE IF NOT EXISTS public.nv_billing_checkout_intents (
    intent_id TEXT PRIMARY KEY,
    owner_subject TEXT NOT NULL REFERENCES
        public.nv_billing_accounts(owner_subject),
    stripe_session_id TEXT UNIQUE,
    state TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (state IN ('pending','created','completed','expired'))
);

CREATE TABLE IF NOT EXISTS public.nv_billing_subscriptions (
    stripe_subscription_id TEXT PRIMARY KEY,
    owner_subject TEXT NOT NULL REFERENCES
        public.nv_billing_accounts(owner_subject),
    stripe_customer_id TEXT NOT NULL,
    stripe_price_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'incomplete',
    cancel_at_period_end BOOLEAN NOT NULL DEFAULT false,
    current_period_end TIMESTAMPTZ,
    last_event_created BIGINT NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (stripe_subscription_id LIKE 'sub_%'),
    CHECK (stripe_customer_id LIKE 'cus_%'),
    CHECK (stripe_price_id LIKE 'price_%'),
    CHECK (
        status IN (
            'incomplete','trialing','active','past_due',
            'unpaid','canceled','incomplete_expired','paused'
        )
    )
);

CREATE TABLE IF NOT EXISTS public.nv_billing_events (
    stripe_event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    event_created BIGINT NOT NULL,
    stripe_subscription_id TEXT,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (stripe_event_id LIKE 'evt_%')
);

CREATE INDEX IF NOT EXISTS nv_billing_subscription_owner_idx
    ON public.nv_billing_subscriptions(owner_subject);

CREATE INDEX IF NOT EXISTS nv_billing_checkout_owner_idx
    ON public.nv_billing_checkout_intents(owner_subject);
"""

TABLE_NAMES = (
    "nv_billing_accounts",
    "nv_billing_checkout_intents",
    "nv_billing_subscriptions",
    "nv_billing_events",
)

async def apply_schema(engine):
    """
    Add missing billing tables atomically.

    Existing table definitions must be reviewed before
    reusing them; IF NOT EXISTS alone is not validation.
    """
    from sqlalchemy import inspect

    async with engine.connect() as conn:
        existing = await conn.run_sync(
            lambda sync_conn: set(
                inspect(sync_conn).get_table_names(schema="public")
            )
        )

    already = set(TABLE_NAMES) & existing

    if already:
        raise RuntimeError(
            "Billing tables already present; migration blocked "
            "pending schema review: " + ", ".join(sorted(already))
        )

    async with engine.begin() as conn:
        for statement in DDL.split(";"):
            if statement.strip():
                await conn.execute(text(statement))
