from pathlib import Path
import json
from collections import defaultdict

ROOT = Path(".").resolve()

OUTPUT_STATE = ROOT / "TOPOLOGY_NORMALIZED_STATE.json"
OUTPUT_REPAIR = ROOT / "ARCHITECTURE_REPAIR_PLAN.json"


# =========================================================
# LAYER MODEL (FINAL CANONICAL TRUTH)
# =========================================================

def classify_layer(path: str) -> str:
    p = path.lower()

    # -------------------------
    # INFRASTRUCTURE CORE (NOT STACKS)
    # -------------------------
    if any(x in p for x in [
        "main.py",
        "/routers/",
        "/schemas/",
        "/config/",
        "/core/",
        "/analysis/"
    ]):
        return "INFRASTRUCTURE_CORE"

    # -------------------------
    # TEST LAYER
    # -------------------------
    if "test" in p:
        return "TEST"

    # -------------------------
    # STACK OWNED REALMS
    # -------------------------
    if "/stacks/" in p:
        return "STACK_OWNED"

    # -------------------------
    # DOMAIN CLASSIFICATION (fallback mapping)
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

    return "ORPHAN"


# =========================================================
# SCAN SYSTEM
# =========================================================

def scan_repo():
    state = defaultdict(list)

    for path in ROOT.rglob("*.py"):

        if "venv" in str(path) or ".git" in str(path):
            continue

        rel = str(path)

        if "backend/app" not in rel:
            continue

        layer = classify_layer(rel)
        state[layer].append(rel)

    return state


# =========================================================
# DRIFT DETECTION
# =========================================================

def detect_drift(state):
    drift = []

    infra = set(state.get("INFRASTRUCTURE_CORE", []))
    stacks = set(state.get("STACK_OWNED", []))
    orphans = set(state.get("ORPHAN", []))

    # rule: infra should not be inside stacks folder
    for f in infra:
        if "/stacks/" in f:
            drift.append({"type": "INFRA_LEAK_INTO_STACKS", "file": f})

    # rule: stack files outside stacks folder
    for f in stacks:
        if "/stacks/" not in f:
            drift.append({"type": "STACK_OUTSIDE_STACKS_DIR", "file": f})

    # rule: orphan inflation signal
    if len(orphans) > 20:
        drift.append({
            "type": "ORPHAN_OVERFLOW",
            "count": len(orphans)
        })

    return drift


# =========================================================
# NORMALIZATION OUTPUT
# =========================================================

def build_normalized(state, drift):

    return {
        "stack_counts": {k: len(v) for k, v in state.items()},
        "stacks": state,
        "drift": drift,
        "health_score": compute_health(state, drift)
    }


def compute_health(state, drift):
    base = 100

    base -= len(state.get("ORPHAN", [])) * 0.5
    base -= len(drift) * 5

    return max(0, round(base, 2))


# =========================================================
# REPAIR PLAN GENERATOR
# =========================================================

def build_repair_plan(state, drift):

    plan = []

    for f in state.get("ORPHAN", []):
        plan.append({
            "file": f,
            "action": "REVIEW_AND_ASSIGN_STACK"
        })

    for d in drift:
        plan.append({
            "issue": d,
            "action": "FIX_TOPOLOGY_VIOLATION"
        })

    return plan


# =========================================================
# MAIN ENGINE
# =========================================================

def main():

    print("\n🧠 ARCHITECTURE NORMALIZATION ENGINE STARTED\n")

    state = scan_repo()
    drift = detect_drift(state)

    normalized = build_normalized(state, drift)
    repair = build_repair_plan(state, drift)

    OUTPUT_STATE.write_text(json.dumps(normalized, indent=2))
    OUTPUT_REPAIR.write_text(json.dumps(repair, indent=2))

    print("✔ TOPOLOGY_NORMALIZED_STATE.json written")
    print("✔ ARCHITECTURE_REPAIR_PLAN.json written")

    print("\n============================")
    print("ARCHITECTURE HEALTH REPORT")
    print("============================")

    print(f"Health Score: {normalized['health_score']}")
    print(f"Orphans: {len(state.get('ORPHAN', []))}")
    print(f"Drift Issues: {len(drift)}")


if __name__ == "__main__":
    main()
