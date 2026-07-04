
from pathlib import Path

CANONICAL_STACKS = [
    "execution",
    "risk",
    "portfolio",
    "strategy",
    "snaptrade",
    "chat",
    "learning",
    "security",
    "analysis",
    "test",
    "frontend",
    "core",
    "unknown"
]


def find_repo_root():
    return Path("backend/app").resolve()


def scan_repo(root, limit=1000):
    files = []
    for i, f in enumerate(root.rglob("*.py")):
        if i >= limit:
            break
        files.append(str(f))
    return files


def classify_stack(path: str) -> str:
    p = path.lower()

    # business domain
    if "/execut" in p:
        return "execution"
    if "/risk" in p:
        return "risk"
    if "/portfolio" in p:
        return "portfolio"
    if "/strategy" in p:
        return "strategy"
    if "/snaptrade" in p:
        return "snaptrade"
    if "/chat" in p:
        return "chat"
    if "/learn" in p:
        return "learning"
    if "/security" in p:
        return "security"

    # system layers
    if "/analysis" in p:
        return "analysis"
    if "/test" in p:
        return "test"
    if "/frontend" in p or "l6_frontend" in p:
        return "frontend"
    if "spine" in p:
        return "core"

    return "unknown"


def build_repo_intelligence(limit: int = 1000) -> dict:
    root = find_repo_root()
    files = scan_repo(root, limit=limit)

    structure = {stack: [] for stack in CANONICAL_STACKS}

    for file_path in files:
        stack = classify_stack(file_path)
        structure.setdefault(stack, []).append(file_path)

    return {
        "root": str(root),
        "file_count": len(files),
        "summary": {k: len(v) for k, v in structure.items()},
        "structure": structure,
    }
