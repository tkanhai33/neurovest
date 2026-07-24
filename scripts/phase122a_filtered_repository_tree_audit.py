#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

OUT_DIR = ARCH / "filtered_repository_tree_audit"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "122A_filtered_repository_tree_audit_latest.json"
OUT_TXT = OUT_DIR / "122A_filtered_repository_tree_audit_latest.txt"

PHASE = "122A_FILTERED_REPOSITORY_TREE_AUDIT"

IGNORE_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    ".next",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".cache",
    "dist",
    "build",
    "coverage",
    ".idea",
    ".vscode",
}

KEEP_ROOTS = [
    ROOT / "backend",
    ROOT / "frontend",
    ROOT / "runtime",
    ROOT / "scripts",
    ROOT / "docs",
]

VALID_SUFFIXES = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".json",
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".toml",
}

LAYER_NAMES = {
    "L0": "External Data Sources",
    "L1": "Security / Cerberus",
    "L2": "Domain",
    "L3": "Service Facade",
    "L4": "Runtime Orchestration",
    "L5": "API",
    "L6": "Frontend",
    "L7": "Tests",
}

def classify(path: Path):
    rel = path.relative_to(ROOT)
    parts = rel.parts

    stack = None
    layer = None

    if "stacks" in parts:
        idx = parts.index("stacks")
        if idx + 1 < len(parts):
            stack = parts[idx + 1]

    for part in parts:
        if part.startswith("L") and len(part) >= 2 and part[1].isdigit():
            layer = part.split("_")[0]
            break

    if layer is None:
        if "frontend" in parts:
            layer = "L6"
        elif "tests" in parts:
            layer = "L7"

    return {
        "path": str(rel),
        "stack": stack,
        "layer": layer,
        "layer_name": LAYER_NAMES.get(layer),
        "suffix": path.suffix,
        "size_bytes": path.stat().st_size,
    }

files = []

for base in KEEP_ROOTS:
    if not base.exists():
        continue

    for path in base.rglob("*"):

        if any(part in IGNORE_DIRS for part in path.parts):
            continue

        if not path.is_file():
            continue

        if path.suffix.lower() not in VALID_SUFFIXES:
            continue

        files.append(classify(path))

files.sort(key=lambda x: x["path"])

layer_counts = {}
stack_counts = {}
suffix_counts = {}

for item in files:

    layer = item["layer"] or "UNASSIGNED"
    stack = item["stack"] or "UNASSIGNED"

    layer_counts[layer] = layer_counts.get(layer, 0) + 1
    stack_counts[stack] = stack_counts.get(stack, 0) + 1
    suffix_counts[item["suffix"]] = suffix_counts.get(item["suffix"], 0) + 1

checks = {
    "backend_exists": (ROOT / "backend").exists(),
    "frontend_exists": (ROOT / "frontend").exists(),
    "runtime_exists": (ROOT / "runtime").exists(),
    "scripts_exists": (ROOT / "scripts").exists(),
    "repository_files_found": len(files) > 0,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "repository_root": str(ROOT),
    "ignored_directories": sorted(IGNORE_DIRS),
    "files_scanned": len(files),
    "layer_counts": layer_counts,
    "stack_counts": stack_counts,
    "suffix_counts": suffix_counts,
    "files": files,
    "checks": checks,
    "recommended_next_phase": "122B_LAYER_CONNECTIVITY_AUDIT",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(
    json.dumps(result, indent=2),
    encoding="utf-8",
)

lines = [
    PHASE,
    "",
    f"certified: {result['certified']}",
    f"files_scanned: {len(files)}",
    "",
    "Layer Counts",
]

for layer in sorted(layer_counts):
    lines.append(f"- {layer}: {layer_counts[layer]}")

lines.extend([
    "",
    "Stack Counts",
])

for stack in sorted(stack_counts):
    lines.append(f"- {stack}: {stack_counts[stack]}")

lines.extend([
    "",
    "Repository Files",
])

for item in files:
    layer = item["layer"] or "-"
    stack = item["stack"] or "-"
    lines.append(
        f"{item['path']} | stack={stack} | layer={layer}"
    )

lines.extend([
    "",
    "Next:",
    result["recommended_next_phase"],
])

OUT_TXT.write_text(
    "\n".join(lines),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "files_scanned": len(files),
    "layers_found": len(layer_counts),
    "stacks_found": len(stack_counts),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
