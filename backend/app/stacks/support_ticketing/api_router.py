from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
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

from backend.app.stacks.identity_auth.api_dependencies import (
    require_authenticated_principal,
)

from backend.app.stacks.identity_auth.contracts import (
    AuthenticatedPrincipal,
)

from backend.app.stacks.support_ticketing.contracts import (
    AppendSupportMessageRequest,
    CreateSupportTicketRequest,
    SupportTicketDetailResponse,
    SupportTicketResponse,
)

from backend.app.stacks.support_ticketing.service import (
    SupportTicketClosed,
    SupportTicketNotFound,
    SupportTicketService,
)


router = APIRouter(
    prefix="/api/v1/support/tickets",
    tags=[
        "support-ticketing",
    ],
)


async def support_database_session() -> (
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


@router.post(
    "",
    response_model=(
        SupportTicketResponse
    ),
    status_code=(
        status.HTTP_201_CREATED
    ),
)
async def create_support_ticket(
    request: CreateSupportTicketRequest,
    principal: AuthenticatedPrincipal = Depends(
        require_authenticated_principal
    ),
    session: AsyncSession = Depends(
        support_database_session
    ),
):
    service = service_for(
        session
    )

    ticket = await service.create_ticket(
        owner_user_id=principal.subject,
        subject=request.subject,
        message=request.message,
        priority=request.priority,
    )

    await session.commit()

    await session.refresh(
        ticket
    )

    return ticket


@router.get(
    "",
    response_model=list[
        SupportTicketResponse
    ],
)
async def list_support_tickets(
    principal: AuthenticatedPrincipal = Depends(
        require_authenticated_principal
    ),
    session: AsyncSession = Depends(
        support_database_session
    ),
):
    service = service_for(
        session
    )

    return list(
        await service.list_for_owner(
            principal.subject
        )
    )


@router.get(
    "/{ticket_id}",
    response_model=(
        SupportTicketDetailResponse
    ),
)
async def get_support_ticket(
    ticket_id: str,
    principal: AuthenticatedPrincipal = Depends(
        require_authenticated_principal
    ),
    session: AsyncSession = Depends(
        support_database_session
    ),
):
    service = service_for(
        session
    )

    try:
        return await service.get_for_owner(
            ticket_id=ticket_id,
            owner_user_id=(
                principal.subject
            ),
        )

    except SupportTicketNotFound as exc:
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
async def append_support_ticket_message(
    ticket_id: str,
    request: AppendSupportMessageRequest,
    principal: AuthenticatedPrincipal = Depends(
        require_authenticated_principal
    ),
    session: AsyncSession = Depends(
        support_database_session
    ),
):
    service = service_for(
        session
    )

    try:
        ticket = (
            await service.append_user_message(
                ticket_id=ticket_id,
                owner_user_id=(
                    principal.subject
                ),
                message=request.message,
            )
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
