#!/usr/bin/env bash

set +e
set +u
set +H

REPO_ROOT="$(
    cd "$(dirname "${BASH_SOURCE[0]}")/.." \
      && pwd
)"

cd "$REPO_ROOT" || {
    echo "BLOCKED: NeuroVest repository could not be opened."
    return 1 2>/dev/null || exit 1
}

VENV_ACTIVATE="$REPO_ROOT/.venv/bin/activate"

if [ ! -f "$VENV_ACTIVATE" ]; then
    echo "BLOCKED: Python virtual environment is missing:"
    echo "  $VENV_ACTIVATE"
    return 1 2>/dev/null || exit 1
fi

source "$VENV_ACTIVATE"

JWT_ENV_CANDIDATES=(
    "$REPO_ROOT/runtime/dev_auth/dev_jwt_env.sh"
    "$REPO_ROOT/runtime/dev_auth/dev_jwt_env.before_aiq003_20260727_124234.sh"
)

JWT_ENV=""

for CANDIDATE in "${JWT_ENV_CANDIDATES[@]}"
do
    if [ -f "$CANDIDATE" ]; then
        JWT_ENV="$CANDIDATE"
        break
    fi
done

if [ -z "$JWT_ENV" ]; then
    echo "BLOCKED: no local JWT environment file was found."
    echo
    echo "Expected one of:"
    printf '  %s\n' "${JWT_ENV_CANDIDATES[@]}"
    echo
    echo "The JWT secret must remain outside Git."
    return 1 2>/dev/null || exit 1
fi

set -a

# Local secret file is intentionally ignored by Git.
# shellcheck disable=SC1090
source "$JWT_ENV"

set +a

if [ -z "${NEUROVEST_JWT_SECRET-}" ]; then
    echo "BLOCKED: JWT environment file did not provide"
    echo "NEUROVEST_JWT_SECRET."
    return 1 2>/dev/null || exit 1
fi

if [ "${#NEUROVEST_JWT_SECRET}" -lt 32 ]; then
    echo "BLOCKED: loaded JWT secret is unexpectedly short."
    return 1 2>/dev/null || exit 1
fi

HOST="${NEUROVEST_BACKEND_HOST:-127.0.0.1}"
PORT="${NEUROVEST_BACKEND_PORT:-8000}"

echo
echo "======================================================================"
echo "NEUROVEST BACKEND"
echo "======================================================================"
echo
echo "Repository:"
echo "  $REPO_ROOT"
echo
echo "JWT environment:"
echo "  $JWT_ENV"
echo
echo "JWT secret:"
echo "  PRESENT — REDACTED"
echo
echo "Listening:"
echo "  http://${HOST}:${PORT}"
echo

exec uvicorn \
  backend.app.main:app \
  --host "$HOST" \
  --port "$PORT"
