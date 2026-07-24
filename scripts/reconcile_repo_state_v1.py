from pathlib import Path
import json

ROOT = Path(".").resolve()

REPORT_FILE = ROOT / "ARCH_ENFORCEMENT_REPORT.json"


def scan_current_services():
    base = ROOT / "backend/app"

    services = []

    # search for both old and migrated locations
    for path in base.rglob("*.py"):
        if "services" in str(path):
            services.append(str(path))

    return services


def reconcile(plan):
    existing = set(scan_current_services())

    reconciled = []

    print("\n🧠 RECONCILIATION REPORT\n")

    for src, dest in plan:

        # normalize path formats
        normalized = src.replace("/home/tkanhai/Neurovest/", "")
        normalized = normalized.replace("File: ", "").strip()

        if any(normalized in e for e in existing):
            reconciled.append((src, dest))
        else:
            print(f"⚠ Skipping (already moved or missing): {src}")

    return reconciled


def main():

    if not REPORT_FILE.exists():
        print("❌ Missing ARCH_ENFORCEMENT_REPORT.json")
        return

    report = json.loads(REPORT_FILE.read_text())

    plan = list(report.get("service_migration_plan", {}).items())

    fixed_plan = reconcile(plan)

    out = ROOT / "SERVICE_RELOCATION_PLAN_RECONCILED.json"
    out.write_text(json.dumps(fixed_plan, indent=2))

    print("\n✔ Reconciled plan written:")
    print("SERVICE_RELOCATION_PLAN_RECONCILED.json")


if __name__ == "__main__":
    main()
