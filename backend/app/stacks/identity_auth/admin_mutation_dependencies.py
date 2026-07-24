from __future__ import annotations

from collections.abc import AsyncIterator

from backend.app.stacks.db_runtime.database import (
    async_session,
)
from backend.app.stacks.identity_auth.admin_mutation_service import (
    AdministrativeUserMutationService,
)


async def get_administrative_user_mutation_service(
) -> AsyncIterator[
    AdministrativeUserMutationService
]:
    async with async_session() as session:
        yield AdministrativeUserMutationService(
            session=session
        )
