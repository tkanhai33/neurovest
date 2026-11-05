"""F12: credential-generation invalidation.

Revision ID: nv_f12_credential_generation_v1
Revises: nv_paper_equity_high_water_v1

Extends identity security without enabling live trading.
"""

from typing import Sequence, Union

from alembic import op

from backend.app.stacks.identity_auth.migrations import (
    stage9d_f12_credential_generation as f12,
)

revision: str = "nv_f12_credential_generation_v1"
down_revision: Union[str, None] = "nv_paper_equity_high_water_v1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    f12.upgrade(op.get_bind())


def downgrade() -> None:
    raise RuntimeError(
        "F12 credential-generation schema rollback requires "
        "a separately approved recovery procedure"
    )
