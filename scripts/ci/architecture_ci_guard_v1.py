from collections import Counter
from pathlib import Path
import argparse
import ast
import subprocess
import sys

ROOT = Path(".").resolve()
APP_ROOT = ROOT / "backend" / "app"

RULES = {
    "L0": ["strategy", "risk", "portfolio", "execution"],
    "L1": ["execution", "broker", "snaptrade"],
    "L2": ["fastapi", "uvicorn", "routers"],
    "L3": ["strategy", "risk", "market_data"],
}


def detect_layer(path: str) -> str:
    lowered = path.lower()
    if "stacks" in lowered:
        return "L2"
    if "routers" in lowered or "api" in lowered:
        return "L3"
    if "core" in lowered or "config" in lowered:
        return "L1"
    return "L2"


def imports_from_source(source: str, filename: str) -> list[str]:
    try:
        tree = ast.parse(source, filename=filename)
    except Exception:
        return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(item.name for item in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return imports


def violations_for_source(relative_path: str, source: str) -> list[str]:
    layer = detect_layer(relative_path)
    forbidden = RULES.get(layer, [])
    return [
        f"{relative_path} | {layer} violated import rule: {module}"
        for module in imports_from_source(source, relative_path)
        for rule in forbidden
        if rule in module
    ]


def current_violations() -> Counter:
    found = Counter()
    if not APP_ROOT.exists():
        return found

    for path in APP_ROOT.rglob("*.py"):
        path_text = str(path)
        if "venv" in path_text or ".git" in path_text:
            continue
        relative = path.relative_to(ROOT).as_posix()
        try:
            source = path.read_text(encoding="utf-8")
        except Exception:
            continue
        found.update(violations_for_source(relative, source))
    return found


def ref_violations(ref: str) -> Counter:
    verified = subprocess.run(
        ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    listing = subprocess.run(
        ["git", "ls-tree", "-r", "-z", "--name-only", verified, "--", "backend/app"],
        check=True,
        capture_output=True,
    ).stdout

    found = Counter()
    for raw_path in listing.split(b"\0"):
        if not raw_path:
            continue
        relative = raw_path.decode("utf-8", errors="surrogateescape")
        if not relative.endswith(".py") or "venv" in relative or ".git" in relative:
            continue

        content = subprocess.run(
            ["git", "show", f"{verified}:{relative}"],
            check=True,
            capture_output=True,
        ).stdout.decode("utf-8", errors="replace")
        found.update(violations_for_source(relative, content))
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--baseline-ref",
        help="Fail only when the current tree adds violations beyond this Git ref.",
    )
    args = parser.parse_args()

    print("\n🧠 CI ARCHITECTURE GUARD RUNNING\n")
    current = current_violations()

    if not args.baseline_ref:
        if current:
            print("🚨 ARCHITECTURE VIOLATIONS DETECTED:\n")
            for item, count in sorted(current.items()):
                for _ in range(count):
                    print(item)
            print("\n❌ CI FAILED: Architecture rules violated")
            return 1
        print("✔ CI PASSED: Architecture clean")
        return 0

    baseline = ref_violations(args.baseline_ref)
    new = current - baseline
    inherited = current & baseline
    resolved = baseline - current

    print(f"Baseline ref: {args.baseline_ref}")
    print(f"Inherited violations still present: {sum(inherited.values())}")
    print(f"Baseline violations resolved: {sum(resolved.values())}")
    print(f"New violations: {sum(new.values())}")

    if inherited:
        print("\nExisting baseline violations (reported, not blocking):")
        for item, count in sorted(inherited.items()):
            for _ in range(count):
                print(item)

    if new:
        print("\n🚨 NEW ARCHITECTURE VIOLATIONS:")
        for item, count in sorted(new.items()):
            for _ in range(count):
                print(item)
        print("\n❌ CI FAILED: New architecture violations detected")
        return 1

    print("\n✔ CI PASSED: No new architecture violations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
