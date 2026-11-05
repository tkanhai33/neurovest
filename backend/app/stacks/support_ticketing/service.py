from __future__ import annotations

from datetime import (
    UTC,
    datetime,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from backend.app.stacks.support_ticketing.models import (
    SupportTicket,
    SupportTicketMessage,
)

from backend.app.stacks.support_ticketing.repository import (
    SupportTicketRepository,
)


class SupportTicketNotFound(
    LookupError
):
    pass


class SupportTicketClosed(
    RuntimeError
):
    pass


class SupportTicketService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session
        self._repository = (
            SupportTicketRepository(
                session
            )
        )

    async def create_ticket(
        self,
        *,
        owner_user_id: str,
        subject: str,
        message: str,
        priority: str,
    ) -> SupportTicket:
        ticket = SupportTicket(
            owner_user_id=owner_user_id,
            subject=subject.strip(),
            status="OPEN",
            priority=priority,
        )

        initial_message = (
            SupportTicketMessage(
                ticket=ticket,
                author_user_id=(
                    owner_user_id
                ),
                author_role="USER",
                message=message.strip(),
            )
        )

        await self._repository.create_ticket(
            ticket=ticket,
            initial_message=initial_message,
        )

        return ticket

    async def list_for_owner(
        self,
        owner_user_id: str,
    ) -> tuple[
        SupportTicket,
        ...,
    ]:
        return await self._repository.list_for_owner(
            owner_user_id
        )

    async def get_for_owner(
        self,
        *,
        ticket_id: str,
        owner_user_id: str,
    ) -> SupportTicket:
        ticket = await self._repository.get_for_owner(
            ticket_id=ticket_id,
            owner_user_id=owner_user_id,
        )

        if ticket is None:
            raise SupportTicketNotFound(
                "support ticket not found"
            )

        return ticket

    async def append_user_message(
        self,
        *,
        ticket_id: str,
        owner_user_id: str,
        message: str,
    ) -> SupportTicket:
        ticket = await self.get_for_owner(
            ticket_id=ticket_id,
            owner_user_id=owner_user_id,
        )

        if ticket.status == "CLOSED":
            raise SupportTicketClosed(
                "closed support ticket cannot receive messages"
            )

        record = SupportTicketMessage(
            ticket_id=ticket.id,
            author_user_id=owner_user_id,
            author_role="USER",
            message=message.strip(),
        )

        await self._repository.append_message(
            record
        )

        ticket.status = (
            "WAITING_FOR_ADMINISTRATOR"
        )

        ticket.updated_at = datetime.now(
            UTC
        )

        await self._session.flush()

        await self._session.refresh(
            ticket,
            attribute_names=[
                "messages",
            ],
        )

        return await self.get_for_owner(
            ticket_id=ticket.id,
            owner_user_id=owner_user_id,
        )

    async def list_all(
        self,
    ) -> tuple[
        SupportTicket,
        ...,
    ]:
        return await self._repository.list_all()

    async def get_any(
        self,
        ticket_id: str,
    ) -> SupportTicket:
        ticket = await self._repository.get_any(
            ticket_id
        )

        if ticket is None:
            raise SupportTicketNotFound(
                "support ticket not found"
            )

        return ticket

    async def update_admin(
        self,
        *,
        ticket_id: str,
        status: str | None,
        priority: str | None,
    ) -> SupportTicket:
        ticket = await self.get_any(
            ticket_id
        )

        now = datetime.now(
            UTC
        )

        if status is not None:
            ticket.status = status

            if status == "RESOLVED":
                ticket.resolved_at = now

            if status == "CLOSED":
                ticket.closed_at = now

        if priority is not None:
            ticket.priority = priority

        ticket.updated_at = now

        await self._session.flush()

        return ticket

    async def append_admin_message(
        self,
        *,
        ticket_id: str,
        administrator_user_id: str,
        message: str,
    ) -> SupportTicket:
        ticket = await self.get_any(
            ticket_id
        )

        if ticket.status == "CLOSED":
            raise SupportTicketClosed(
                "closed support ticket cannot receive messages"
            )

        record = SupportTicketMessage(
            ticket_id=ticket.id,
            author_user_id=(
                administrator_user_id
            ),
            author_role=(
                "ADMINISTRATOR"
            ),
            message=message.strip(),
        )

        await self._repository.append_message(
            record
        )

        ticket.status = (
            "WAITING_FOR_USER"
        )

        ticket.updated_at = datetime.now(
            UTC
        )

        await self._session.flush()

        await self._session.refresh(
            ticket,
            attribute_names=[
                "messages",
            ],
        )

        return await self.get_any(
            ticket.id
        )
