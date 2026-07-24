from pathlib import Path
import json
from collections import defaultdict

ROOT = Path(".").resolve()

OUTPUT = ROOT / "TOPOLOGY_STATE.json"


# -----------------------------
# STACK DETECTION
# -----------------------------

def detect_stack(path: str) -> str:
    if "auth" in path:
        return "auth_identity"
    if "portfolio" in path:
        return "portfolio"
    if "strategy" in path:
        return "strategy"
    if "market_data" in path:
        return "market_data"
    if "risk" in path:
        return "risk"
    if "notification" in path:
        return "notification"
    if "execution" in path:
        return "execution"
    if "journal" in path:
        return "journal_ledger"
    return "ORPHAN"


# -----------------------------
# SCAN SYSTEM
# -----------------------------

def scan():
    state = defaultdict(list)

    for path in ROOT.rglob("*.py"):

        if "venv" in str(path) or ".git" in str(path):
            continue

        rel = str(path)

        if "backend/app" not in rel:
            continue

        # ignore test noise classification separately
        if "/test" in rel:
            state["test"].append(rel)
            continue

        stack = detect_stack(rel)
        state[stack].append(rel)

    return state


# -----------------------------
# BUILD SNAPSHOT
# -----------------------------

def build_snapshot(state):
    snapshot = {
        "stack_counts": {},
        "stacks": {},
        "orphans": state.get("ORPHAN", []),
        "timestamp": str(Path(".").stat().st_mtime)
    }

    for k, v in state.items():
        snapshot["stack_counts"][k] = len(v)
        snapshot["stacks"][k] = v

    return snapshot


# -----------------------------
# MAIN
# -----------------------------

def main():
    print("\n🧠 BUILDING TOPOLOGY STATE SNAPSHOT...\n")

    state = scan()
    snapshot = build_snapshot(state)

    OUTPUT.write_text(json.dumps(snapshot, indent=2))

    print("✔ Snapshot written → TOPOLOGY_STATE.json")
    print("\nSTACK SUMMARY:")

    for k, v in snapshot["stack_counts"].items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
