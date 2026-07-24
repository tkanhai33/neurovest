from __future__ import annotations

import os
import ast
from pathlib import Path
from collections import defaultdict
import json

ROOT = Path(".").resolve()

# -----------------------------
# LAYER DEFINITIONS (LOCKED)
# -----------------------------

LAYERS = {
    "L0": ["snaptrade", "finnhub", "alpha_vantage", "broker", "db_driver"],
    "L1": ["risk", "auth", "drawdown", "security"],
    "L2": ["strategy", "portfolio", "market_data"],
    "L3": ["services"],
    "L4": ["execution", "events", "runtime"],
    "L5": ["api", "routers"],
    "L6": ["frontend", "next"],
    "L7": ["test"]
}

FORBIDDEN_IMPORTS = {
    "L2": ["fastapi", "uvicorn", "snaptrade", "execution"],
    "L1": ["execution", "broker", "portfolio_service"],
    "L0": ["strategy", "risk", "portfolio", "services"],
    "L3": ["strategy", "risk", "market_data"],  # service layer must not contain logic
    "L4": ["strategy", "portfolio", "risk"]
}

# -----------------------------
# DETECTION RESULTS
# -----------------------------

violations = []
service_layer_hits = []
stack_map = defaultdict(list)


# -----------------------------
# HELPERS
# -----------------------------

def detect_layer(file_path: str) -> str | None:
    for layer, keywords in LAYERS.items():
        if any(k in file_path for k in keywords):
            return layer
    return None


def scan_imports(file: Path):
    try:
        tree = ast.parse(file.read_text())
    except Exception:
        return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


# -----------------------------
# CORE SCAN
# -----------------------------

def scan_repo():
    print("🧠 Starting architecture enforcement scan...\n")

    for path in ROOT.rglob("*.py"):
        if "venv" in str(path) or ".git" in str(path):
            continue

        layer = detect_layer(str(path))
        imports = scan_imports(path)

        if layer:
            stack_map[layer].append(str(path))

        # -----------------------------
        # SERVICE LAYER DETECTION
        # -----------------------------
        if "services" in str(path):
            service_layer_hits.append(str(path))

        # -----------------------------
        # VIOLATION DETECTION
        # -----------------------------
        if layer in FORBIDDEN_IMPORTS:
            for imp in imports:
                for forbidden in FORBIDDEN_IMPORTS[layer]:
                    if forbidden in imp:
                        violations.append({
                            "file": str(path),
                            "layer": layer,
                            "import": imp,
                            "violation": f"{layer} importing forbidden module {imp}"
                        })

    print("\n✔ Scan Complete\n")


# -----------------------------
# SERVICE LAYER COLLAPSE REPORT
# -----------------------------

def generate_service_migration_plan():
    plan = {}

    for svc in service_layer_hits:
        name = Path(svc).stem

        if "market" in name:
            target = "stacks/market_data"
        elif "risk" in name:
            target = "stacks/risk"
        elif "portfolio" in name:
            target = "stacks/portfolio"
        elif "strategy" in name:
            target = "stacks/strategy"
        elif "auth" in name:
            target = "stacks/auth_identity"
        else:
            target = "UNKNOWN_STACK"

        plan[svc] = target

    return plan


# -----------------------------
# REPORT GENERATION
# -----------------------------

def generate_report():
    report = {
        "violations_count": len(violations),
        "service_layer_files": len(service_layer_hits),
        "stack_distribution": {k: len(v) for k, v in stack_map.items()},
        "violations": violations[:50],
        "service_migration_plan": generate_service_migration_plan()
    }

    out_file = ROOT / "ARCH_ENFORCEMENT_REPORT.json"
    out_file.write_text(json.dumps(report, indent=2))

    print("📄 Report written to ARCH_ENFORCEMENT_REPORT.json")

    return report


# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":
    scan_repo()
    report = generate_report()

    print("\n==============================")
    print("NEUROVEST ARCHITECTURE CHECK")
    print("==============================")
    print(f"Violations: {report['violations_count']}")
    print(f"Service-layer files: {report['service_layer_files']}")
    print("==============================\n")

    print("Top service migration targets:")
    for k, v in list(report["service_migration_plan"].items())[:10]:
        print(f"{k} → {v}")
