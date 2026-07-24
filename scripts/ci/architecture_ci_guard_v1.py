from pathlib import Path
import ast
import sys

ROOT = Path(".").resolve()

VIOLATIONS = []


# ================================
# LAYER RULES (HARD ENFORCEMENT)
# ================================

RULES = {
    "L0": ["strategy", "risk", "portfolio", "execution"],
    "L1": ["execution", "broker", "snaptrade"],
    "L2": ["fastapi", "uvicorn", "routers"],
    "L3": ["strategy", "risk", "market_data"],  # service logic forbidden
}


def detect_layer(path: str) -> str:
    p = path.lower()

    if "stacks" in p:
        return "L2"

    if "routers" in p or "api" in p:
        return "L3"

    if "core" in p or "config" in p:
        return "L1"

    return "L2"


def scan_imports(file_path: Path):
    try:
        tree = ast.parse(file_path.read_text())
    except Exception:
        return []

    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name)

        if isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    return imports


def check_file(file_path: Path):
    layer = detect_layer(str(file_path))
    imports = scan_imports(file_path)

    forbidden = RULES.get(layer, [])

    for imp in imports:
        for f in forbidden:
            if f in imp:
                VIOLATIONS.append(
                    f"{file_path} | {layer} violated import rule: {imp}"
                )


def scan_repo():
    for path in ROOT.rglob("*.py"):
        if "venv" in str(path) or ".git" in str(path):
            continue

        if "backend/app" not in str(path):
            continue

        check_file(path)


def main():
    print("\n🧠 CI ARCHITECTURE GUARD RUNNING\n")

    scan_repo()

    if VIOLATIONS:
        print("\n🚨 ARCHITECTURE VIOLATIONS DETECTED:\n")
        for v in VIOLATIONS:
            print(v)

        print("\n❌ CI FAILED: Architecture rules violated")
        sys.exit(1)

    print("\n✔ CI PASSED: Architecture clean")
    sys.exit(0)


if __name__ == "__main__":
    main()
