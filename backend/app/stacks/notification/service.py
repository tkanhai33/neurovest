from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import (
    select,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from backend.app.stacks.notification.models import (
    NotificationRecord,
)


class NotificationRejectedError(
    RuntimeError
):
    pass


def utc_now() -> datetime:
    return datetime.now(UTC)


class NotificationService:
    """
    Canonical persistent notification service.

    Every read and mutation is owner scoped.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def emit_notification(
        self,
        *,
        user_id: str,
        title: str,
        message: str,
        category: str = "system",
        severity: str = "info",
    ) -> NotificationRecord:
        owner = str(user_id).strip()
        normalized_title = str(title).strip()
        normalized_message = str(message).strip()

        if not owner:
            raise NotificationRejectedError(
                "Notification owner is required"
            )

        if not normalized_title:
            raise NotificationRejectedError(
                "Notification title is required"
            )

        if not normalized_message:
            raise NotificationRejectedError(
                "Notification message is required"
            )

        record = NotificationRecord(
            user_id=owner,
            title=normalized_title[:200],
            message=normalized_message,
            category=(
                str(category).strip()
                or "system"
            )[:64],
            severity=(
                str(severity).strip()
                or "info"
            )[:32],
            delivery_status="delivered",
            delivered_at=utc_now(),
        )

        self._session.add(record)

        await self._session.commit()
        await self._session.refresh(record)

        return record

    async def list_notifications(
        self,
        *,
        user_id: str,
        limit: int = 100,
    ) -> list[NotificationRecord]:
        owner = str(user_id).strip()

        if not owner:
            raise NotificationRejectedError(
                "Notification owner is required"
            )

        result = await self._session.execute(
            select(NotificationRecord)
            .where(
                NotificationRecord.user_id
                == owner
            )
            .order_by(
                NotificationRecord.created_at.desc(),
                NotificationRecord.id.desc(),
            )
            .limit(
                max(
                    1,
                    min(int(limit), 500),
                )
            )
        )

        return list(
            result.scalars().all()
        )

    async def mark_read(
        self,
        *,
        user_id: str,
        notification_id: str,
    ) -> NotificationRecord:
        record = await self._owned_record(
            user_id=user_id,
            notification_id=notification_id,
        )

        if not record.is_read:
            record.is_read = True
            record.read_at = utc_now()

            await self._session.commit()
            await self._session.refresh(record)

        return record

    async def acknowledge_notification(
        self,
        *,
        user_id: str,
        notification_id: str,
    ) -> NotificationRecord:
        record = await self._owned_record(
            user_id=user_id,
            notification_id=notification_id,
        )

        now = utc_now()

        if not record.is_read:
            record.is_read = True
            record.read_at = now

        if record.acknowledged_at is None:
            record.acknowledged_at = now

        await self._session.commit()
        await self._session.refresh(record)

        return record

    async def _owned_record(
        self,
        *,
        user_id: str,
        notification_id: str,
    ) -> NotificationRecord:
        owner = str(user_id).strip()
        record_id = str(
            notification_id
        ).strip()

        if not owner or not record_id:
            raise NotificationRejectedError(
                "Notification identity is invalid"
            )

        result = await self._session.execute(
            select(NotificationRecord)
            .where(
                NotificationRecord.id
                == record_id,
                NotificationRecord.user_id
                == owner,
            )
        )

        record = result.scalar_one_or_none()

        if record is None:
            raise NotificationRejectedError(
                "Notification was not found"
            )

        return record
