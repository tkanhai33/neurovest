from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from collections.abc import (
    AsyncIterator,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from backend.app.stacks.db_runtime.database import (
    async_session,
)

from backend.app.stacks.identity_auth.admin_read_dependencies import (
    AdministrativePrincipal,
    require_administrative_principal,
)

from backend.app.stacks.support_ticketing.contracts import (
    AppendSupportMessageRequest,
    SupportTicketDetailResponse,
    SupportTicketResponse,
    UpdateSupportTicketRequest,
)

from backend.app.stacks.support_ticketing.service import (
    SupportTicketClosed,
    SupportTicketNotFound,
    SupportTicketService,
)


router = APIRouter(
    prefix=(
        "/api/v1/admin/support/tickets"
    ),
    tags=[
        "admin-support-ticketing",
    ],
)


async def support_admin_database_session() -> (
    AsyncIterator[AsyncSession]
):
    async with async_session() as session:
        yield session


def service_for(
    session: AsyncSession,
) -> SupportTicketService:
    return SupportTicketService(
        session
    )


@router.get(
    "",
    response_model=list[
        SupportTicketResponse
    ],
)
async def list_all_support_tickets(
    principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
    session: AsyncSession = Depends(
        support_admin_database_session
    ),
):
    del principal

    return list(
        await service_for(
            session
        ).list_all()
    )


@router.get(
    "/{ticket_id}",
    response_model=(
        SupportTicketDetailResponse
    ),
)
async def get_admin_support_ticket(
    ticket_id: str,
    principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
    session: AsyncSession = Depends(
        support_admin_database_session
    ),
):
    del principal

    try:
        return await service_for(
            session
        ).get_any(
            ticket_id
        )

    except SupportTicketNotFound as exc:
        raise HTTPException(
            status_code=404,
            detail=str(
                exc
            ),
        ) from exc


@router.patch(
    "/{ticket_id}",
    response_model=(
        SupportTicketResponse
    ),
)
async def update_admin_support_ticket(
    ticket_id: str,
    request: UpdateSupportTicketRequest,
    principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
    session: AsyncSession = Depends(
        support_admin_database_session
    ),
):
    del principal

    try:
        ticket = await service_for(
            session
        ).update_admin(
            ticket_id=ticket_id,
            status=request.status,
            priority=request.priority,
        )

        await session.commit()

        return ticket

    except SupportTicketNotFound as exc:
        await session.rollback()

        raise HTTPException(
            status_code=404,
            detail=str(
                exc
            ),
        ) from exc


@router.post(
    "/{ticket_id}/messages",
    response_model=(
        SupportTicketDetailResponse
    ),
)
async def append_admin_support_message(
    ticket_id: str,
    request: AppendSupportMessageRequest,
    principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
    session: AsyncSession = Depends(
        support_admin_database_session
    ),
):
    try:
        ticket = await service_for(
            session
        ).append_admin_message(
            ticket_id=ticket_id,
            administrator_user_id=(
                principal.user_id
            ),
            message=request.message,
        )

        await session.commit()

        return ticket

    except SupportTicketNotFound as exc:
        await session.rollback()

        raise HTTPException(
            status_code=404,
            detail=str(
                exc
            ),
        ) from exc

    except SupportTicketClosed as exc:
        await session.rollback()

        raise HTTPException(
            status_code=409,
            detail=str(
                exc
            ),
        ) from exc
