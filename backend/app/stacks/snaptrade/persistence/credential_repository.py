from __future__ import annotations

from datetime import datetime

from cryptography.fernet import Fernet
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.stacks.snaptrade.persistence.credential_models import (
    SnapTradeUserCredential,
)
from backend.app.stacks.snaptrade.security.user_secret_cipher import (
    decrypt_snaptrade_user_secret,
    encrypt_snaptrade_user_secret,
)


class SnapTradeCredentialRepository:
    """
    Persistent owner-scoped SnapTrade credential boundary.

    Plaintext secrets exist only during encryption or an authorized
    provider call and are never returned by public serialization.
    """

    def __init__(
        self,
        session: AsyncSession,
        *,
        cipher: Fernet | None = None,
    ) -> None:
        self._session = session
        self._cipher = cipher

    async def get_for_owner(
        self,
        neurovest_user_id: str,
    ) -> SnapTradeUserCredential | None:
        owner = str(
            neurovest_user_id
        ).strip()

        if not owner:
            raise ValueError(
                "NeuroVest owner identity is required"
            )

        result = await self._session.execute(
            select(
                SnapTradeUserCredential
            ).where(
                SnapTradeUserCredential
                .neurovest_user_id
                == owner
            )
        )

        return result.scalar_one_or_none()

    async def store_registered_credential(
        self,
        *,
        neurovest_user_id: str,
        snaptrade_user_id: str,
        user_secret: str,
    ) -> SnapTradeUserCredential:
        owner = str(
            neurovest_user_id
        ).strip()

        provider_user = str(
            snaptrade_user_id
        ).strip()

        if not owner:
            raise ValueError(
                "NeuroVest owner identity is required"
            )

        if not provider_user:
            raise ValueError(
                "SnapTrade user identity is required"
            )

        encrypted_secret = (
            encrypt_snaptrade_user_secret(
                user_secret,
                cipher=self._cipher,
            )
        )

        record = await self.get_for_owner(
            owner
        )

        if record is None:
            record = SnapTradeUserCredential(
                neurovest_user_id=owner,
                snaptrade_user_id=(
                    provider_user
                ),
                encrypted_user_secret=(
                    encrypted_secret
                ),
                connection_status=(
                    "registered"
                ),
            )

            self._session.add(
                record
            )
        else:
            record.snaptrade_user_id = (
                provider_user
            )

            record.encrypted_user_secret = (
                encrypted_secret
            )

            record.connection_status = (
                "registered"
            )

        await self._session.flush()

        return record

    async def load_provider_identity(
        self,
        *,
        neurovest_user_id: str,
    ) -> tuple[str, str]:
        record = await self.get_for_owner(
            neurovest_user_id
        )

        if record is None:
            raise LookupError(
                "SnapTrade credential is unavailable"
            )

        plaintext_secret = (
            decrypt_snaptrade_user_secret(
                record.encrypted_user_secret,
                cipher=self._cipher,
            )
        )

        return (
            record.snaptrade_user_id,
            plaintext_secret,
        )

    async def update_sync_state(
        self,
        *,
        neurovest_user_id: str,
        sync_status: str,
        synced_at: datetime,
    ) -> SnapTradeUserCredential:
        record = await self.get_for_owner(
            neurovest_user_id
        )

        if record is None:
            raise LookupError(
                "SnapTrade credential is unavailable"
            )

        normalized_status = str(
            sync_status
        ).strip()

        if not normalized_status:
            raise ValueError(
                "SnapTrade synchronization status is required"
            )

        record.last_sync_status = (
            normalized_status[:64]
        )

        record.last_synced_at = (
            synced_at
        )

        record.connection_status = (
            "connected"
        )

        await self._session.flush()

        return record


def serialize_snaptrade_credential_state(
    record: SnapTradeUserCredential,
) -> dict[str, object]:
    """
    Safe representation. Provider secrets and ciphertext are excluded.
    """

    return {
        "registered": True,
        "snaptrade_user_id": (
            record.snaptrade_user_id
        ),
        "connection_status": (
            record.connection_status
        ),
        "last_sync_status": (
            record.last_sync_status
        ),
        "last_synced_at": (
            record.last_synced_at.isoformat()
            if record.last_synced_at
            else None
        ),
        "created_at": (
            record.created_at.isoformat()
            if record.created_at
            else None
        ),
        "updated_at": (
            record.updated_at.isoformat()
            if record.updated_at
            else None
        ),
        "user_secret_exposed": False,
        "ciphertext_exposed": False,
    }
