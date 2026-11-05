from __future__ import annotations

import asyncio
import sys

from sqlalchemy import text

from backend.app.stacks.db_runtime.database import engine

TABLE_NAME = "identity_terms_acceptances"
INDEX_NAME = "ix_identity_terms_acceptances_user"


async def upgrade() -> None:
    async with engine.begin() as connection:
        await connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS
                identity_terms_acceptances (
                    id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(36) NOT NULL
                        REFERENCES identity_users(id)
                        ON DELETE CASCADE,
                    document_version VARCHAR(128) NOT NULL,
                    accepted_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL
                        DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT
                    uq_identity_terms_acceptances_user_document
                    UNIQUE (user_id, document_version)
                )
                """
            )
        )

        await connection.execute(
            text(
                f"""
                CREATE INDEX IF NOT EXISTS {INDEX_NAME}
                ON {TABLE_NAME} (user_id)
                """
            )
        )


async def downgrade() -> None:
    async with engine.begin() as connection:
        await connection.execute(
            text(
                f"DROP INDEX IF EXISTS {INDEX_NAME}"
            )
        )

        await connection.execute(
            text(
                f"DROP TABLE IF EXISTS {TABLE_NAME}"
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
        print("PASS: terms-acceptance migration upgraded")
        return 0

    if action == "downgrade":
        asyncio.run(downgrade())
        print("PASS: terms-acceptance migration downgraded")
        return 0

    print("Usage: migration.py [upgrade|downgrade]")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
