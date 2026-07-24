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
]:
    from backend.app.stacks.chat_public.persistence import (
        chat_models,
    )
    from backend.app.stacks.journal_ledger import (
        ledger,
    )

    return (
        ledger,
        chat_models,
    )
