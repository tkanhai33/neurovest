from pathlib import Path
import json

ROOT = Path(".").resolve()

STATE_FILE = ROOT / "TOPOLOGY_NORMALIZED_STATE.json"
REPAIR_FILE = ROOT / "ARCHITECTURE_REPAIR_PLAN.json"

OUTPUT_FINAL = ROOT / "FINAL_ARCHITECTURE_STATE.json"


# -----------------------------
# FINAL STACK RESOLUTION
# -----------------------------

def resolve_final_stack(path: str) -> str:

    p = path.lower()

    # -------------------------
    # CORE INFRASTRUCTURE
    # -------------------------
    if any(x in p for x in [
        "main.py",
        "routers",
        "schemas",
        "config",
        "core",
        "analysis"
    ]):
        return "INFRASTRUCTURE_CORE"

    # -------------------------
    # TESTS
    # -------------------------
    if "test" in p:
        return "test"

    # -------------------------
    # DOMAIN STACKS
    # -------------------------
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

    if "ledger" in p or "journal" in p:
        return "journal_ledger"

    if "chat" in p:
        return "chat_public"

    if "wolfden" in p:
        return "wolfden_ai"

    if "snaptrade" in p:
        return "snaptrade"

    if "db" in p:
        return "db_model"

    # -------------------------
    # TRUE EDGE CASE
    # -------------------------
    return "UNRESOLVED_FINAL"


# -----------------------------
# MAIN
# -----------------------------

def main():

    if not STATE_FILE.exists():
        print("❌ Missing TOPOLOGY_NORMALIZED_STATE.json")
        return

    state = json.loads(STATE_FILE.read_text())

    orphans = state.get("stacks", {}).get("ORPHAN", [])

    print("\n🧠 FINAL ORPHAN RESOLUTION PASS\n")

    final_map = []
    unresolved = []

    for file_path in orphans:

        stack = resolve_final_stack(file_path)

        if stack == "UNRESOLVED_FINAL":
            unresolved.append(file_path)

        final_map.append({
            "file": file_path,
            "final_stack": stack
        })

        print(file_path)
        print(f"  → {stack}\n")

    output = {
        "resolved": final_map,
        "unresolved": unresolved,
        "summary": {
            "total_orphans": len(orphans),
            "resolved": len(final_map) - len(unresolved),
            "unresolved": len(unresolved)
        }
    }

    OUTPUT_FINAL.write_text(json.dumps(output, indent=2))

    print("\n✔ FINAL_ARCHITECTURE_STATE.json written")

    print("\n======================")
    print("FINALIZATION SUMMARY")
    print("======================")
    print(f"Total Orphans: {len(orphans)}")
    print(f"Resolved: {len(final_map) - len(unresolved)}")
    print(f"Unresolved: {len(unresolved)}")


if __name__ == "__main__":
    main()
