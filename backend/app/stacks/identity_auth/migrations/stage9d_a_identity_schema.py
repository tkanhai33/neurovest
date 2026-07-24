from __future__ import annotations

from sqlalchemy import text

from backend.app.stacks.db_runtime.database import (
    engine,
)


MIGRATION_ID = (
    "workstream3_stage9d_a_identity_schema"
)

APPROVED_ROLES = (
    "user",
    "admin",
    "owner",
)


async def upgrade() -> None:
    async with engine.begin() as connection:
        await connection.execute(
            text(
                """
                ALTER TABLE identity_users
                ADD COLUMN IF NOT EXISTS role
                VARCHAR(32)
                """
            )
        )

        await connection.execute(
            text(
                """
                UPDATE identity_users
                SET role = 'user'
                WHERE role IS NULL
                   OR role NOT IN (
                       'user',
                       'admin',
                       'owner'
                   )
                """
            )
        )

        await connection.execute(
            text(
                """
                ALTER TABLE identity_users
                ALTER COLUMN role
                SET DEFAULT 'user'
                """
            )
        )

        await connection.execute(
            text(
                """
                ALTER TABLE identity_users
                ALTER COLUMN role
                SET NOT NULL
                """
            )
        )

        await connection.execute(
            text(
                """
                ALTER TABLE identity_users
                ADD COLUMN IF NOT EXISTS
                must_change_password
                BOOLEAN
                """
            )
        )

        await connection.execute(
            text(
                """
                UPDATE identity_users
                SET must_change_password = FALSE
                WHERE must_change_password IS NULL
                """
            )
        )

        await connection.execute(
            text(
                """
                ALTER TABLE identity_users
                ALTER COLUMN must_change_password
                SET DEFAULT FALSE
                """
            )
        )

        await connection.execute(
            text(
                """
                ALTER TABLE identity_users
                ALTER COLUMN must_change_password
                SET NOT NULL
                """
            )
        )

        await connection.execute(
            text(
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM pg_constraint
                        WHERE conname =
                            'ck_identity_users_role'
                    ) THEN
                        ALTER TABLE identity_users
                        ADD CONSTRAINT
                            ck_identity_users_role
                        CHECK (
                            role IN (
                                'user',
                                'admin',
                                'owner'
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
                """
                CREATE INDEX IF NOT EXISTS
                    ix_identity_users_role
                ON identity_users (role)
                """
            )
        )


async def downgrade() -> None:
    async with engine.begin() as connection:
        await connection.execute(
            text(
                """
                DROP INDEX IF EXISTS
                    ix_identity_users_role
                """
            )
        )

        await connection.execute(
            text(
                """
                ALTER TABLE identity_users
                DROP CONSTRAINT IF EXISTS
                    ck_identity_users_role
                """
            )
        )

        await connection.execute(
            text(
                """
                ALTER TABLE identity_users
                DROP COLUMN IF EXISTS
                    must_change_password
                """
            )
        )

        await connection.execute(
            text(
                """
                ALTER TABLE identity_users
                DROP COLUMN IF EXISTS role
                """
            )
        )


async def dispose() -> None:
    await engine.dispose()
