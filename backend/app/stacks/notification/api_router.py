from __future__ import annotations

from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from pydantic import (
    BaseModel,
    Field,
)

from backend.app.stacks.db_runtime.database import (
    async_session,
)
from backend.app.stacks.identity_auth.api_dependencies import (
    require_authenticated_principal,
)
from backend.app.stacks.notification.models import (
    NotificationRecord,
)
from backend.app.stacks.notification.service import (
    NotificationRejectedError,
    NotificationService,
)


router = APIRouter(
    prefix="/api/v1/notifications",
    tags=[
        "notifications",
    ],
)


class CreateNotificationRequest(
    BaseModel
):
    title: str = Field(
        min_length=1,
        max_length=200,
    )

    message: str = Field(
        min_length=1,
        max_length=8000,
    )

    category: str = Field(
        default="system",
        min_length=1,
        max_length=64,
    )

    severity: str = Field(
        default="info",
        min_length=1,
        max_length=32,
    )


def principal_subject(
    principal: Any,
) -> str:
    subject = getattr(
        principal,
        "subject",
        None,
    )

    if not isinstance(
        subject,
        str,
    ) or not subject.strip():
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Authentication required",
        )

    return subject.strip()


def serialize_notification(
    record: NotificationRecord,
) -> dict[str, Any]:
    return {
        "id": record.id,
        "category": record.category,
        "title": record.title,
        "message": record.message,
        "severity": record.severity,
        "delivery_status": (
            record.delivery_status
        ),
        "delivered_at": (
            record.delivered_at.isoformat()
            if record.delivered_at
            else None
        ),
        "is_read": record.is_read,
        "read_at": (
            record.read_at.isoformat()
            if record.read_at
            else None
        ),
        "acknowledged_at": (
            record.acknowledged_at.isoformat()
            if record.acknowledged_at
            else None
        ),
        "created_at": (
            record.created_at.isoformat()
            if record.created_at
            else None
        ),
    }


@router.get("")
async def list_notifications(
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    principal=Depends(
        require_authenticated_principal
    ),
) -> dict[str, Any]:
    owner = principal_subject(
        principal
    )

    async with async_session() as session:
        service = NotificationService(
            session
        )

        records = await service.list_notifications(
            user_id=owner,
            limit=limit,
        )

    return {
        "status": "available",
        "owner_scoped": True,
        "count": len(records),
        "unread_count": sum(
            1
            for record in records
            if not record.is_read
        ),
        "records": [
            serialize_notification(
                record
            )
            for record in records
        ],
    }


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_notification(
    request: CreateNotificationRequest,
    principal=Depends(
        require_authenticated_principal
    ),
) -> dict[str, Any]:
    owner = principal_subject(
        principal
    )

    try:
        async with async_session() as session:
            service = NotificationService(
                session
            )

            record = (
                await service.emit_notification(
                    user_id=owner,
                    title=request.title,
                    message=request.message,
                    category=request.category,
                    severity=request.severity,
                )
            )

    except NotificationRejectedError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail="Notification could not be created",
        ) from exc

    return {
        "status": "delivered",
        "delivery_evidence": {
            "notification_id": record.id,
            "delivery_status": (
                record.delivery_status
            ),
            "delivered_at": (
                record.delivered_at.isoformat()
            ),
        },
        "record": serialize_notification(
            record
        ),
    }


@router.patch(
    "/{notification_id}/read"
)
async def mark_notification_read(
    notification_id: str,
    principal=Depends(
        require_authenticated_principal
    ),
) -> dict[str, Any]:
    owner = principal_subject(
        principal
    )

    try:
        async with async_session() as session:
            service = NotificationService(
                session
            )

            record = await service.mark_read(
                user_id=owner,
                notification_id=(
                    notification_id
                ),
            )

    except NotificationRejectedError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Notification was not found",
        ) from exc

    return {
        "status": "read",
        "record": serialize_notification(
            record
        ),
    }


@router.patch(
    "/{notification_id}/acknowledge"
)
async def acknowledge_notification(
    notification_id: str,
    principal=Depends(
        require_authenticated_principal
    ),
) -> dict[str, Any]:
    owner = principal_subject(
        principal
    )

    try:
        async with async_session() as session:
            service = NotificationService(
                session
            )

            record = (
                await service
                .acknowledge_notification(
                    user_id=owner,
                    notification_id=(
                        notification_id
                    ),
                )
            )

    except NotificationRejectedError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Notification was not found",
        ) from exc

    return {
        "status": "acknowledged",
        "record": serialize_notification(
            record
        ),
    }
