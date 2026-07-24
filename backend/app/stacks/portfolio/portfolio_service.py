from backend.app.stacks.execution.paper_broker import (
    get_positions_snapshot,
)
from backend.app.stacks.identity_auth.contracts import (
    AuthenticatedPrincipal,
)


def _principal_subject(
    principal: AuthenticatedPrincipal,
) -> str:
    subject = str(
        getattr(
            principal,
            "subject",
            "",
        )
    ).strip()

    if not subject:
        raise ValueError(
            "Authenticated portfolio principal subject cannot be empty"
        )

    return subject


async def get_portfolio_positions_for_api(
    principal: AuthenticatedPrincipal,
) -> dict[str, object]:
    """
    Return only portfolio information belonging to the authenticated
    principal.

    The persistence layer is not yet ownership-aware, so this facade
    deliberately fails closed to an empty account-scoped snapshot
    instead of exposing the legacy global inventory.
    """

    user_id = _principal_subject(
        principal
    )

    return await get_positions_snapshot(
        user_id=user_id
    )
