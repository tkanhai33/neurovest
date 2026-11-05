"""
Canonical runtime ORM model registration.

Database infrastructure owns Base, engine, sessions, and schema creation.
Domain stacks own their ORM models.
The application composition root registers those models before init_db().
"""

from __future__ import annotations

from types import ModuleType


def register_runtime_models() -> tuple[
    ModuleType,
    ModuleType,
    ModuleType,
    ModuleType,
]:

    from backend.app.stacks.snaptrade.persistence.external_portfolio_models import (
        SnapTradeExternalPortfolioPosition,
    )

    from backend.app.stacks.snaptrade.persistence.external_balance_models import (
        SnapTradeExternalBalance,
    )

    _ = SnapTradeExternalPortfolioPosition
    _ = SnapTradeExternalBalance
    from backend.app.stacks.chat_public.persistence import (
        chat_models,
    )
    from backend.app.stacks.support_ticketing import (
        models as support_ticketing_models,
    )
    from backend.app.stacks.identity_auth import (
        models as identity_models,
    )
    from backend.app.stacks.journal_ledger import (
        ledger,
    )
    from backend.app.stacks.notification import (
        models as notification_models,
    )
    from backend.app.stacks.snaptrade.persistence import (
        credential_models as snaptrade_credential_models,
    )

    return (
        ledger,
        notification_models,
        snaptrade_credential_models,
        chat_models,
    )
