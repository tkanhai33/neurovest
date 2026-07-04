#!/bin/bash

set -e

echo "🧠 Installing Neuro Architecture Memory System..."

BASE_DIR="spine/L5_api"

mkdir -p "$BASE_DIR"

# =========================================================
# 1. CREATE CACHE FILE
# =========================================================
CACHE_FILE="$BASE_DIR/.neuro_arch_cache.json"

if [ ! -f "$CACHE_FILE" ]; then
  echo '{"snapshot": {}, "history": []}' > "$CACHE_FILE"
  echo "✔ Created architecture cache"
fi


# =========================================================
# 2. CREATE MEMORY MODULE
# =========================================================
cat > "$BASE_DIR/neuro_memory.py" << 'EOF'
import json
from pathlib import Path

CACHE_FILE = Path("spine/L5_api/.neuro_arch_cache.json")


def load_cache():
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    return {"snapshot": {}, "history": []}


def save_cache(cache):
    CACHE_FILE.write_text(json.dumps(cache, indent=2))


def update_cache(cache, snapshot):
    cache["history"].append(snapshot)
    cache["snapshot"] = snapshot
    cache["history"] = cache["history"][-10:]
    save_cache(cache)


def diff_architecture(old, new):
    old_files = set(old.get("forward", {}).keys())
    new_files = set(new.get("forward", {}).keys())

    return {
        "added_files": list(new_files - old_files),
        "removed_files": list(old_files - new_files)
    }
EOF

echo "✔ Created neuro memory module"


# =========================================================
# 3. CREATE UPDATED CLI (STATEFUL COMPANION)
# =========================================================
cat > "$BASE_DIR/neuro_cli_stateful.py" << 'EOF'
import subprocess
import json
from spine.L5_api.repo_introspector import run_scan
from spine.L5_api.neuro_memory import (
    load_cache, save_cache, update_cache, diff_architecture
)

MODEL = "llama3.1"


def safe(obj):
    if isinstance(obj, dict):
        return {k: safe(v) for k, v in obj.items()}
    if isinstance(obj, set):
        return list(obj)
    if isinstance(obj, tuple):
        return [safe(x) for x in obj]
    if isinstance(obj, list):
        return [safe(x) for x in obj]
    return obj


def ask_llm(prompt):
    result = subprocess.run(
        ["ollama", "run", MODEL],
        input=prompt.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return result.stdout.decode().strip()


def build_snapshot(forward, reverse):
    return {
        "forward": forward,
        "reverse": reverse,
        "metrics": {
            "files": len(forward),
            "edges": sum(len(v) for v in forward.values())
        }
    }


def main():
    print("\n🧠 NEURO STATEFUL CLI ONLINE\n")

    cache = load_cache()

    summary, forward, reverse = run_scan()
    snapshot = build_snapshot(forward, reverse)

    diff = diff_architecture(cache["snapshot"], snapshot)

    update_cache(cache, snapshot)

    prompt = f"""
You are NEURO ARCHITECTURE COMPANION.

You understand fintech AI trading systems.

REPO SNAPSHOT:
{json.dumps(snapshot, indent=2)}

ARCHITECTURE CHANGE (since last run):
{json.dumps(diff, indent=2)}

TASK:
- explain system state
- identify missing trading system components
- give next build step
- respect L0–L7 spine

Be concise and technical.
"""

    print(ask_llm(prompt))


if __name__ == "__main__":
    main()
EOF

echo "✔ Created stateful CLI"

echo ""
echo "🚀 INSTALL COMPLETE"
echo ""
echo "Run with:"
echo "cd backend/app"
echo "PYTHONPATH=. python3 spine/L5_api/neuro_cli_stateful.py"
