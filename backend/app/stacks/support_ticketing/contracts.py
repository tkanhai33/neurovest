from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


TicketStatus = Literal[
    "OPEN",
    "WAITING_FOR_USER",
    "WAITING_FOR_ADMINISTRATOR",
    "RESOLVED",
    "CLOSED",
]


TicketPriority = Literal[
    "LOW",
    "NORMAL",
    "HIGH",
    "URGENT",
]


class CreateSupportTicketRequest(
    BaseModel,
):
    subject: str = Field(
        min_length=1,
        max_length=255,
    )

    message: str = Field(
        min_length=1,
        max_length=10000,
    )

    priority: TicketPriority = (
        "NORMAL"
    )


class AppendSupportMessageRequest(
    BaseModel,
):
    message: str = Field(
        min_length=1,
        max_length=10000,
    )


class UpdateSupportTicketRequest(
    BaseModel,
):
    status: TicketStatus | None = None
    priority: TicketPriority | None = None


class SupportTicketMessageResponse(
    BaseModel,
):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: str
    ticket_id: str
    author_user_id: str
    author_role: str
    message: str
    created_at: datetime


class SupportTicketResponse(
    BaseModel,
):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: str
    owner_user_id: str
    subject: str
    status: TicketStatus
    priority: TicketPriority
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None
    closed_at: datetime | None


class SupportTicketDetailResponse(
    SupportTicketResponse,
):
    messages: list[
        SupportTicketMessageResponse
    ]
