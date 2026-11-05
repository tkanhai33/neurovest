"""Developer improvement journal tables v1.

Revision ID: neuro_improvement_journal_v1
Revises: snaptrade_value_hist_v1

The journal tables were initially provisioned in production.
This migration adopts those tables without deleting their data.
"""

from alembic import op
from sqlalchemy import inspect

revision = "neuro_improvement_journal_v1"
down_revision = "snaptrade_value_hist_v1"
branch_labels = None
depends_on = None

RUNS_TABLE = "neuro_developer_improvement_runs_v1"
FINDINGS_TABLE = "neuro_developer_improvement_findings_v1"

CREATE_RUNS = '\nCREATE TABLE IF NOT EXISTS neuro_developer_improvement_runs_v1 (\n    scan_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,\n    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),\n    modules_scanned INTEGER NOT NULL,\n    modules_allowed INTEGER NOT NULL,\n    findings_total INTEGER NOT NULL,\n    findings_new INTEGER NOT NULL,\n    findings_existing INTEGER NOT NULL,\n    errors_json TEXT NOT NULL,\n    status TEXT NOT NULL\n)\n'
CREATE_FINDINGS = "\nCREATE TABLE IF NOT EXISTS neuro_developer_improvement_findings_v1 (\n    finding_id VARCHAR(64) PRIMARY KEY,\n    module_name TEXT NOT NULL,\n    function_name TEXT NOT NULL,\n    finding_kind TEXT NOT NULL,\n    priority VARCHAR(2) NOT NULL,\n    evidence TEXT NOT NULL,\n    recommendation TEXT NOT NULL,\n    source_sha256 VARCHAR(64) NOT NULL,\n    first_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),\n    last_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),\n    seen_count INTEGER NOT NULL DEFAULT 1,\n    status TEXT NOT NULL DEFAULT 'observed',\n    last_scan_id BIGINT NOT NULL\n)\n"

EXPECTED_RUNS = {
    "scan_id",
    "created_at",
    "modules_scanned",
    "modules_allowed",
    "findings_total",
    "findings_new",
    "findings_existing",
    "errors_json",
    "status",
}

EXPECTED_FINDINGS = {
    "finding_id",
    "module_name",
    "function_name",
    "finding_kind",
    "priority",
    "evidence",
    "recommendation",
    "source_sha256",
    "first_seen",
    "last_seen",
    "seen_count",
    "status",
    "last_scan_id",
}


def _verify_columns(bind, table, expected):
    inspector = inspect(bind)
    columns = inspector.get_columns(table, schema="public")
    actual = {column["name"] for column in columns}

    if actual != expected:
        raise RuntimeError(
            "Journal schema mismatch for " + table
        )


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    runs_exists = inspector.has_table(
        RUNS_TABLE, schema="public"
    )
    findings_exists = inspector.has_table(
        FINDINGS_TABLE, schema="public"
    )

    if runs_exists != findings_exists:
        raise RuntimeError(
            "Partial journal schema detected; "
            "manual inspection required"
        )

    if not runs_exists:
        op.execute(CREATE_RUNS)
        op.execute(CREATE_FINDINGS)

    _verify_columns(bind, RUNS_TABLE, EXPECTED_RUNS)
    _verify_columns(bind, FINDINGS_TABLE, EXPECTED_FINDINGS)

    # Application-role grants are managed by database
    # administration, not by the runtime account.


def downgrade():
    raise RuntimeError(
        "Journal downgrade is intentionally blocked "
        "to protect accumulated improvement history. "
        "Back up and review the data before removal."
    )
