from pathlib import Path
import json

ROOT = Path(".").resolve()

SNAPSHOT_FILE = ROOT / "TOPOLOGY_STATE.json"


# -----------------------------
# STACK CLASSIFIER (STRICT)
# -----------------------------

def classify_orphan(path: str) -> str:

    p = path.lower()

    if "auth" in p:
        return "auth_identity"

    if "portfolio" in p:
        return "portfolio"

    if "strategy" in p:
        return "strategy"

    if "risk" in p:
        return "risk"

    if "market" in p:
        return "market_data"

    if "notification" in p:
        return "notification"

    if "execution" in p:
        return "execution"

    if "journal" in p or "ledger" in p:
        return "journal_ledger"

    if "test" in p:
        return "test"

    # IMPORTANT: force review instead of guessing
    return "NEW_STACK_REQUIRED"


# -----------------------------
# MAIN
# -----------------------------

def main():

    if not SNAPSHOT_FILE.exists():
        print("❌ Missing TOPOLOGY_STATE.json")
        return

    snapshot = json.loads(SNAPSHOT_FILE.read_text())

    orphans = snapshot.get("orphans", [])

    print("\n🧠 ORPHAN RESOLUTION ANALYSIS\n")

    plan = []

    for file_path in orphans:

        stack = classify_orphan(file_path)

        plan.append({
            "file": file_path,
            "target_stack": stack
        })

        print(file_path)
        print(f"  → {stack}\n")

    OUT = ROOT / "ORPHAN_RESOLUTION_PLAN.json"
    OUT.write_text(json.dumps(plan, indent=2))

    print("\n✔ Written ORPHAN_RESOLUTION_PLAN.json")
    print(f"Total orphans processed: {len(plan)}")


if __name__ == "__main__":
    main()
