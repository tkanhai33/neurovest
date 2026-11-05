#!/usr/bin/env python3
"""Read-only, snapshot-bound Python function intelligence."""
from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from neuro_repository_snapshot_reader import read_active_pair

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "runtime/qualification/repository_intelligence_v1"
OUTPUT = DATA / "function_intelligence_v1.json"

MAX_SOURCE_BYTES = 1_048_576
MAX_FUNCTIONS = 50000
MAX_CALL_NAMES = 25

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def safe_file(relative):
    path = Path(relative)

    if (
        path.is_absolute()
        or ".." in path.parts
        or not path.parts
        or path.parts[0] not in (
            "backend", "frontend", "scripts", "tests", "alembic"
        )
    ):
        return None

    current = ROOT

    for part in path.parts:
        current = current / part
        if current.is_symlink():
            return None

    if not current.is_file():
        return None

    return current

def call_name(node):
    if isinstance(node, ast.Name):
        return node.id

    if isinstance(node, ast.Attribute):
        parts = []
        current = node

        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value

        if isinstance(current, ast.Name):
            parts.append(current.id)
            return ".".join(reversed(parts))

    return None

def metadata(path, tree):
    functions = []

    class Collector(ast.NodeVisitor):
        def __init__(self):
            self.scope = []

        def visit_ClassDef(self, node):
            self.scope.append(node.name)
            for child in node.body:
                self.visit(child)
            self.scope.pop()

        def visit_FunctionDef(self, node):
            self.collect(node, False)

        def visit_AsyncFunctionDef(self, node):
            self.collect(node, True)

        def collect(self, node, asynchronous):
            name = ".".join(self.scope + [node.name])

            # Visit function body separately to avoid treating
            # nested functions as calls in their outer function.
            calls = set()

            class Calls(ast.NodeVisitor):
                def visit_Call(self, call):
                    target = call_name(call.func)
                    if target:
                        calls.add(target[:120])
                    self.generic_visit(call)

                def visit_FunctionDef(self, child):
                    return

                def visit_AsyncFunctionDef(self, child):
                    return

                def visit_ClassDef(self, child):
                    return

            visitor = Calls()
            for child in node.body:
                visitor.visit(child)

            functions.append({
                "file": path,
                "symbol": name,
                "line_start": node.lineno,
                "line_end": node.end_lineno,
                "async": asynchronous,
                "parameters": (
                    len(node.args.posonlyargs)
                    + len(node.args.args)
                    + len(node.args.kwonlyargs)
                    + int(node.args.vararg is not None)
                    + int(node.args.kwarg is not None)
                ),
                "decorator_count": len(node.decorator_list),
                "call_names": sorted(calls)[:MAX_CALL_NAMES],
                "call_names_truncated": len(calls) > MAX_CALL_NAMES,
            })

            self.scope.append(node.name)
            for child in node.body:
                self.visit(child)
            self.scope.pop()

    Collector().visit(tree)
    return functions

def main():
    print("=" * 70)
    print("NEUROVEST — FUNCTION INTELLIGENCE V1")
    print("=" * 70)

    if len(sys.argv) != 1:
        raise SystemExit("STOP=UNEXPECTED_ARGUMENTS")

    index_raw, graph_raw = read_active_pair()
    inventory = json.loads(index_raw)

    records = inventory.get("files")
    if not isinstance(records, list):
        raise SystemExit("STOP=INVALID_INVENTORY")

    results = []
    errors = []
    status = Counter()

    for record in records:
        if not isinstance(record, dict):
            continue

        relative = record.get("path")
        expected = record.get("sha256")

        if not isinstance(relative, str) or not relative.endswith(".py"):
            continue

        if not isinstance(expected, str) or len(expected) != 64:
            status["invalid_fingerprint"] += 1
            continue

        path = safe_file(relative)

        if path is None:
            status["unsafe_or_missing"] += 1
            continue

        try:
            if path.stat().st_size > MAX_SOURCE_BYTES:
                status["size_limit"] += 1
                continue

            raw = path.read_bytes()

            if digest(raw) != expected:
                status["changed_since_snapshot"] += 1
                continue

            tree = ast.parse(raw, filename=relative)
            results.extend(metadata(relative, tree))
            status["parsed"] += 1

            if len(results) > MAX_FUNCTIONS:
                raise ValueError("FUNCTION_INDEX_LIMIT")

        except SyntaxError as exc:
            status["syntax_error"] += 1
            errors.append({
                "file": relative,
                "line": exc.lineno,
                "kind": "SyntaxError",
            })
        except (OSError, ValueError) as exc:
            if isinstance(exc, ValueError) and str(exc) == "FUNCTION_INDEX_LIMIT":
                raise
            status["read_error"] += 1

    report = {
        "schema": "neurovest.function_intelligence.v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "inventory_sha256": digest(index_raw),
        "graph_v2_sha256": digest(graph_raw),
        "python_files_parsed": status["parsed"],
        "function_count": len(results),
        "status": dict(status),
        "syntax_errors": errors[:30],
        "functions": results,
        "limitations": [
            "Static AST metadata only",
            "Call names are not resolved to unique definitions",
            "No function bodies retained",
            "Nested functions indexed with qualified scope names",
            "Changed and excluded files skipped",
            "No execution or semantic analysis performed",
        ],
    }

    serialized = json.dumps(report, indent=2) + "\n"

    if len(serialized.encode("utf-8")) > 20_000_000:
        raise SystemExit("STOP=FUNCTION_INDEX_SIZE_LIMIT")

    if OUTPUT.exists() or OUTPUT.is_symlink():
        raise SystemExit("STOP=FUNCTION_INDEX_ALREADY_EXISTS")

    pending = DATA / ".function_intelligence_v1.pending"

    if pending.exists() or pending.is_symlink():
        raise SystemExit("STOP=PENDING_INDEX_EXISTS")

    try:
        with pending.open("x", encoding="utf-8") as handle:
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())

        pending.chmod(0o600)
        os.replace(pending, OUTPUT)
    finally:
        if pending.exists():
            pending.unlink()

    print("PYTHON_FILES_PARSED=", status["parsed"])
    print("FUNCTIONS_AND_METHODS_INDEXED=", len(results))
    print("CHANGED_FILES_SKIPPED=", status["changed_since_snapshot"])
    print("SYNTAX_ERRORS=", status["syntax_error"])
    print("UNSAFE_OR_MISSING_FILES=", status["unsafe_or_missing"])

    print()
    print("=== LARGEST FUNCTION AREAS ===")
    areas = Counter(
        ".".join(item["file"].split("/")[:4])
        for item in results
    )

    for area, count in areas.most_common(12):
        print(area, count)

    print()
    print("FUNCTION_INDEX_SHA256=", digest(OUTPUT.read_bytes()))
    print("FUNCTION_INDEX_FILE=", OUTPUT)
    print("SOURCE_FILES_MODIFIED=False")
    print("BACKEND_RESTARTED=False")
    print("DATABASE_MODIFIED=False")
    print("PATCH_APPLIED=False")
    print("FUNCTION_INTELLIGENCE_V1=PASS")
    print("Terminal remains open.")

if __name__ == "__main__":
    main()
