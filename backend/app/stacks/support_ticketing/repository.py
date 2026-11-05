from __future__ import annotations

from sqlalchemy import (
    select,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from sqlalchemy.orm import (
    selectinload,
)

from backend.app.stacks.support_ticketing.models import (
    SupportTicket,
    SupportTicketMessage,
)


class SupportTicketRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create_ticket(
        self,
        *,
        ticket: SupportTicket,
        initial_message: SupportTicketMessage,
    ) -> SupportTicket:
        self._session.add(
            ticket
        )

        self._session.add(
            initial_message
        )

        await self._session.flush()

        return ticket

    async def list_for_owner(
        self,
        owner_user_id: str,
    ) -> tuple[
        SupportTicket,
        ...,
    ]:
        result = await self._session.execute(
            select(
                SupportTicket
            )
            .where(
                SupportTicket.owner_user_id
                ==
                owner_user_id
            )
            .order_by(
                SupportTicket.updated_at.desc()
            )
        )

        return tuple(
            result.scalars().all()
        )

    async def list_all(
        self,
    ) -> tuple[
        SupportTicket,
        ...,
    ]:
        result = await self._session.execute(
            select(
                SupportTicket
            )
            .order_by(
                SupportTicket.updated_at.desc()
            )
        )

        return tuple(
            result.scalars().all()
        )

    async def get_for_owner(
        self,
        *,
        ticket_id: str,
        owner_user_id: str,
    ) -> SupportTicket | None:
        result = await self._session.execute(
            select(
                SupportTicket
            )
            .options(
                selectinload(
                    SupportTicket.messages
                )
            )
            .where(
                SupportTicket.id
                ==
                ticket_id
            )
            .where(
                SupportTicket.owner_user_id
                ==
                owner_user_id
            )
        )

        return (
            result.scalar_one_or_none()
        )

    async def get_any(
        self,
        ticket_id: str,
    ) -> SupportTicket | None:
        result = await self._session.execute(
            select(
                SupportTicket
            )
            .options(
                selectinload(
                    SupportTicket.messages
                )
            )
            .where(
                SupportTicket.id
                ==
                ticket_id
            )
        )

        return (
            result.scalar_one_or_none()
        )

    async def append_message(
        self,
        message: SupportTicketMessage,
    ) -> SupportTicketMessage:
        self._session.add(
            message
        )

        await self._session.flush()

        return message
