#!/usr/bin/env python3
import ast
import difflib
import json
import hashlib
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT_DIR = ROOT / "runtime" / "repo_memory"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "phase4d_root_shadow_diff_report_latest.json"
OUT_TXT = OUT_DIR / "phase4d_root_shadow_diff_report_latest.txt"

PAIRS = [
    ("ledger.py", "backend/app/stacks/journal_ledger/ledger.py"),
    ("paper_broker.py", "backend/app/stacks/execution/paper_broker.py"),
]


def sha256(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def ast_symbols(path: Path):
    if not path.exists():
        return {"functions": [], "classes": [], "imports": []}

    try:
        tree = ast.parse(path.read_text(errors="ignore"))
    except Exception as e:
        return {"error": str(e), "functions": [], "classes": [], "imports": []}

    functions = []
    classes = []
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.Import):
            imports.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)

    return {
        "functions": sorted(set(functions)),
        "classes": sorted(set(classes)),
        "imports": sorted(set(imports)),
    }


def diff_files(a: Path, b: Path, limit: int = 200):
    if not a.exists() or not b.exists():
        return []

    a_lines = a.read_text(errors="ignore").splitlines()
    b_lines = b.read_text(errors="ignore").splitlines()

    diff = list(difflib.unified_diff(
        a_lines,
        b_lines,
        fromfile=str(a.relative_to(ROOT)),
        tofile=str(b.relative_to(ROOT)),
        lineterm="",
    ))

    return diff[:limit]


def compare_pair(root_rel: str, canonical_rel: str):
    root = ROOT / root_rel
    canonical = ROOT / canonical_rel

    root_symbols = ast_symbols(root)
    canonical_symbols = ast_symbols(canonical)

    root_functions = set(root_symbols.get("functions", []))
    canonical_functions = set(canonical_symbols.get("functions", []))
    root_classes = set(root_symbols.get("classes", []))
    canonical_classes = set(canonical_symbols.get("classes", []))

    return {
        "root": {
            "path": root_rel,
            "exists": root.exists(),
            "sha256": sha256(root),
            "size_bytes": root.stat().st_size if root.exists() else None,
            "symbols": root_symbols,
        },
        "canonical": {
            "path": canonical_rel,
            "exists": canonical.exists(),
            "sha256": sha256(canonical),
            "size_bytes": canonical.stat().st_size if canonical.exists() else None,
            "symbols": canonical_symbols,
        },
        "same_hash": sha256(root) == sha256(canonical),
        "root_only_functions": sorted(root_functions - canonical_functions),
        "canonical_only_functions": sorted(canonical_functions - root_functions),
        "shared_functions": sorted(root_functions & canonical_functions),
        "root_only_classes": sorted(root_classes - canonical_classes),
        "canonical_only_classes": sorted(canonical_classes - root_classes),
        "shared_classes": sorted(root_classes & canonical_classes),
        "diff_preview": diff_files(root, canonical),
    }


def main():
    comparisons = [
        compare_pair(root_rel, canonical_rel)
        for root_rel, canonical_rel in PAIRS
    ]

    report = {
        "phase": "4D_ROOT_SHADOW_DIFF_REPORT",
        "generated_at": datetime.now(UTC).isoformat(),
        "dry_run_only": True,
        "safe_to_quarantine_now": False,
        "comparisons": comparisons,
    }

    OUT_JSON.write_text(json.dumps(report, indent=2))

    lines = [
        "# PHASE 4D ROOT SHADOW DIFF REPORT",
        "",
        f"generated_at: {report['generated_at']}",
        "dry_run_only: true",
        "safe_to_quarantine_now: false",
        "",
    ]

    for c in comparisons:
        lines += [
            "----------------------------------------",
            f"ROOT: {c['root']['path']}",
            f"CANONICAL: {c['canonical']['path']}",
            f"same_hash: {c['same_hash']}",
            f"root_only_functions: {c['root_only_functions']}",
            f"canonical_only_functions: {c['canonical_only_functions']}",
            f"shared_functions: {c['shared_functions']}",
            f"root_only_classes: {c['root_only_classes']}",
            f"canonical_only_classes: {c['canonical_only_classes']}",
            f"shared_classes: {c['shared_classes']}",
            "",
            "DIFF PREVIEW:",
            *c["diff_preview"],
            "",
        ]

    OUT_TXT.write_text("\n".join(lines))

    print(json.dumps({
        "phase": report["phase"],
        "dry_run_only": True,
        "safe_to_quarantine_now": False,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "summary": [
            {
                "root": c["root"]["path"],
                "canonical": c["canonical"]["path"],
                "same_hash": c["same_hash"],
                "root_only_functions": c["root_only_functions"],
                "canonical_only_functions": c["canonical_only_functions"],
                "root_only_classes": c["root_only_classes"],
                "canonical_only_classes": c["canonical_only_classes"],
            }
            for c in comparisons
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
