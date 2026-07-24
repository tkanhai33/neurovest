from __future__ import annotations

import asyncio
import sys

from sqlalchemy import text

from backend.app.stacks.db_runtime.database import engine


TABLE_NAME = "identity_users"
COLUMN_NAME = "subscription_tier"

CONSTRAINT_NAME = (
    "ck_identity_users_subscription_tier"
)

INDEX_NAME = (
    "ix_identity_users_subscription_tier"
)

APPROVED_TIERS_SQL = (
    "'free', "
    "'basic', "
    "'pro', "
    "'elite', "
    "'enterprise', "
    "'internal'"
)


async def upgrade() -> None:
    async with engine.begin() as connection:
        await connection.execute(
            text(
                f"""
                ALTER TABLE {TABLE_NAME}
                ADD COLUMN IF NOT EXISTS {COLUMN_NAME}
                VARCHAR(32)
                """
            )
        )

        await connection.execute(
            text(
                f"""
                UPDATE {TABLE_NAME}
                SET {COLUMN_NAME} = 'free'
                WHERE {COLUMN_NAME} IS NULL
                """
            )
        )

        await connection.execute(
            text(
                f"""
                ALTER TABLE {TABLE_NAME}
                ALTER COLUMN {COLUMN_NAME}
                SET DEFAULT 'free'
                """
            )
        )

        await connection.execute(
            text(
                f"""
                ALTER TABLE {TABLE_NAME}
                ALTER COLUMN {COLUMN_NAME}
                SET NOT NULL
                """
            )
        )

        await connection.execute(
            text(
                f"""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM pg_constraint
                        WHERE conname = '{CONSTRAINT_NAME}'
                    ) THEN
                        ALTER TABLE {TABLE_NAME}
                        ADD CONSTRAINT {CONSTRAINT_NAME}
                        CHECK (
                            {COLUMN_NAME} IN (
                                {APPROVED_TIERS_SQL}
                            )
                        );
                    END IF;
                END
                $$;
                """
            )
        )

        await connection.execute(
            text(
                f"""
                CREATE INDEX IF NOT EXISTS {INDEX_NAME}
                ON {TABLE_NAME} ({COLUMN_NAME})
                """
            )
        )


async def downgrade() -> None:
    async with engine.begin() as connection:
        await connection.execute(
            text(
                f"""
                DROP INDEX IF EXISTS {INDEX_NAME}
                """
            )
        )

        await connection.execute(
            text(
                f"""
                ALTER TABLE {TABLE_NAME}
                DROP CONSTRAINT IF EXISTS {CONSTRAINT_NAME}
                """
            )
        )

        await connection.execute(
            text(
                f"""
                ALTER TABLE {TABLE_NAME}
                DROP COLUMN IF EXISTS {COLUMN_NAME}
                """
            )
        )


def main() -> int:
    action = (
        sys.argv[1].strip().lower()
        if len(sys.argv) > 1
        else ""
    )

    if action == "upgrade":
        asyncio.run(upgrade())
        print(
            "PASS: subscription-tier migration upgraded"
        )
        return 0

    if action == "downgrade":
        asyncio.run(downgrade())
        print(
            "PASS: subscription-tier migration downgraded"
        )
        return 0

    print(
        "Usage: "
        "python stage9d_c5_j1_subscription_tier.py "
        "[upgrade|downgrade]"
    )

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
