#!/usr/bin/env bash

set +e
set +u
set +H

cd "$(dirname "$0")" || {
    echo "BLOCKED: NeuroVest repository root could not be opened."
    return 0 2>/dev/null || true
}

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

export PYTHONPATH="$PWD"

python3 -m backend.app.llm_bridge.neuro_cli "$@"

echo
echo "Terminal remains open."
