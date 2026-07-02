#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/backend"

DB_NAME="neurovest"
DB_USER="neurovest"
DB_PASS="neurovest_dev_password"
DB_HOST="localhost"
DB_PORT="5432"

echo "========================================="
echo "PHASE 1C - POSTGRESQL DATABASE SKELETON"
echo "========================================="
echo

#############################################
# Install PostgreSQL if missing
#############################################

if ! command -v psql >/dev/null 2>&1; then
  echo "PostgreSQL client not found. Installing PostgreSQL..."
  sudo apt update
  sudo apt install -y postgresql postgresql-contrib
else
  echo "PostgreSQL client found."
fi

#############################################
# Start PostgreSQL
#############################################

echo
echo "Starting PostgreSQL service..."
sudo systemctl enable postgresql
sudo systemctl start postgresql
sudo systemctl status postgresql --no-pager || true

#############################################
# Create database user and database
#############################################

echo
echo "Creating PostgreSQL user/database if missing..."

sudo -u postgres psql <<SQL
DO
\$do\$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles WHERE rolname = '${DB_USER}'
   ) THEN
      CREATE ROLE ${DB_USER} LOGIN PASSWORD '${DB_PASS}';
   END IF;
END
\$do\$;

SELECT 'CREATE DATABASE ${DB_NAME} OWNER ${DB_USER}'
WHERE NOT EXISTS (
  SELECT FROM pg_database WHERE datname = '${DB_NAME}'
)\\gexec

GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
SQL

#############################################
# Ensure .env exists
#############################################

echo
echo "Writing local .env if missing..."

if [ ! -f "$ROOT/.env" ]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
fi

grep -q "^DATABASE_URL=" "$ROOT/.env" || cat >> "$ROOT/.env" <<EOF

DATABASE_URL=postgresql+psycopg://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}
EOF

#############################################
# Write database skeleton files
#############################################

echo
echo "Writing database skeleton files..."

mkdir -p "$BACKEND/app/shared/db"
mkdir -p "$BACKEND/alembic/versions"

cat > "$BACKEND/app/shared/db/session.py" <<'EOF'
from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def create_database_engine(database_url: str) -> Engine:
    return create_engine(database_url, pool_pre_ping=True)


def verify_database_connection(database_url: str) -> bool:
    engine = create_database_engine(database_url)

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return result.scalar_one() == 1
EOF

cat > "$BACKEND/app/shared/config/settings.py" <<'EOF'
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[4]
ENV_FILE = ROOT_DIR / ".env"


class Settings(BaseSettings):
    app_env: str = "local"
    app_name: str = "NeuroVest"
    database_url: str

    broker_enabled: bool = False
    live_trading_enabled: bool = False
    canary_trading_enabled: bool = False

    ollama_base_url: str = "http://localhost:11434"
    ollama_default_chat_model: str = "qwen3:8b"
    ollama_coder_model: str = "qwen2.5-coder:14b"
    ollama_heavy_coder_model: str = "qwen3-coder:30b"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
EOF

cat > "$BACKEND/alembic/README.md" <<'EOF'
# Alembic

Phase 1C placeholder only.

No schema migrations yet.
No business tables yet.
EOF

cat > "$BACKEND/alembic.ini" <<'EOF'
[alembic]
script_location = alembic
prepend_sys_path = .
sqlalchemy.url = postgresql+psycopg://neurovest:neurovest_dev_password@localhost:5432/neurovest

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARNING
handlers = console
qualname =

[logger_sqlalchemy]
level = WARNING
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
EOF

cat > "$BACKEND/alembic/env.py" <<'EOF'
from __future__ import annotations

from logging.config import fileConfig

from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    from sqlalchemy import engine_from_config
    from sqlalchemy import pool

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
EOF

#############################################
# Write tests
#############################################

echo
echo "Writing database tests..."

cat > "$BACKEND/tests/smoke/test_database_connection.py" <<'EOF'
from app.shared.config.settings import get_settings
from app.shared.db.session import verify_database_connection


def test_database_connection() -> None:
    settings = get_settings()
    assert verify_database_connection(settings.database_url) is True
EOF

cat > "$BACKEND/tests/smoke/test_safety_settings_locked.py" <<'EOF'
from app.shared.config.settings import get_settings


def test_safety_settings_locked_by_default() -> None:
    settings = get_settings()

    assert settings.broker_enabled is False
    assert settings.live_trading_enabled is False
    assert settings.canary_trading_enabled is False
EOF

#############################################
# Update contract docs
#############################################

echo
echo "Writing Phase 1C certification doc..."

cat > "$ROOT/docs/contracts/PHASE_1C_DATABASE_SKELETON_CONTRACT.md" <<'EOF'
# Phase 1C Database Skeleton Contract

## Decision

PostgreSQL is installed and used as the primary local database.

## Scope

Allowed in Phase 1C:

```text
PostgreSQL service
local database
local database user
database connection test
settings loader
Alembic placeholder
no schema migrations yet

Forbidden in Phase 1C:

business tables
trading tables
broker tables
strategy tables
risk engine tables
AI memory tables
runtime tables
Safety

Database exists only as infrastructure.

No application business state is created yet.
EOF

cat > "$ROOT/certification/phase_01/PHASE_1C_DATABASE_SKELETON_CERTIFICATION.md" <<'EOF'

Phase 1C Database Skeleton Certification

Status: pending until tests pass.

Checks:

PostgreSQL installed
PostgreSQL running
neurovest user exists
neurovest database exists
.env contains DATABASE_URL
SQLAlchemy connection works
Safety settings remain locked
No business schema created
EOF

#############################################
# Verify
#############################################

echo
echo "Verifying database connection using backend venv..."

cd "$BACKEND"
source .venv/bin/activate

python - <<'PY'
from app.shared.config.settings import get_settings
from app.shared.db.session import verify_database_connection

settings = get_settings()
assert settings.database_url.startswith("postgresql+psycopg://")
assert verify_database_connection(settings.database_url) is True

print("PASS: PostgreSQL connection verified.")
PY

echo
echo "Running pytest..."
pytest

echo
echo "Updating certification status..."

cat > "$ROOT/certification/phase_01/PHASE_1C_DATABASE_SKELETON_CERTIFICATION.md" <<'EOF'

Phase 1C Database Skeleton Certification

Status: PASS

Checks:

PostgreSQL installed
PostgreSQL running
neurovest user exists
neurovest database exists
.env contains DATABASE_URL
SQLAlchemy connection works
Safety settings remain locked
No business schema created
EOF

echo
echo "========================================="
echo "PHASE 1C COMPLETE"
echo "========================================="
echo
echo "PASS: PostgreSQL database skeleton is installed and verified."
