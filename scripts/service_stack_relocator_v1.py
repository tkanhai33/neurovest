from pathlib import Path
import json

ROOT = Path(".").resolve()

REPORT_FILE = ROOT / "ARCH_ENFORCEMENT_REPORT.json"


# -----------------------------
# STACK RESOLUTION LOGIC
# -----------------------------

def resolve_stack(file_path: str) -> str:
    name = Path(file_path).stem.lower()

    if "notification" in name:
        return "stacks/notification"

    if "dashboard" in name:
        return "stacks/portfolio"  # dashboard usually portfolio + analytics

    if "auth" in name:
        return "stacks/auth_identity"

    if "risk" in name:
        return "stacks/risk"

    if "market" in name:
        return "stacks/market_data"

    if "portfolio" in name:
        return "stacks/portfolio"

    if "strategy" in name:
        return "stacks/strategy"

    return "STACK_REVIEW_REQUIRED"


# -----------------------------
# MAIN
# -----------------------------

def main():
    if not REPORT_FILE.exists():
        print("❌ ARCH_ENFORCEMENT_REPORT.json not found")
        return

    report = json.loads(REPORT_FILE.read_text())

    service_map = report.get("service_migration_plan", {})

    print("\n🧠 SERVICE → STACK RELOCATION PLAN\n")

    final_plan = []

    for file_path, stack in service_map.items():

        if stack == "UNKNOWN_STACK":
            stack = resolve_stack(file_path)

        final_plan.append((file_path, stack))

        print(f"{file_path}")
        print(f"  → {stack}\n")

    # Write safe migration plan
    out = ROOT / "SERVICE_RELOCATION_PLAN.json"
    out.write_text(json.dumps(final_plan, indent=2))

    print("\n✔ Written SERVICE_RELOCATION_PLAN.json")
    print("⚠ No files moved yet (safe dry-run mode)")


if __name__ == "__main__":
    main()
