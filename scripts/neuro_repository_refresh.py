#!/usr/bin/env python3
"""Transactional refresh of NeuroVest's read-only repository intelligence."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "runtime/qualification/repository_intelligence_v1"
SCANNER = ROOT / "scripts/neuro_repository_intelligence.py"
QUERY = ROOT / "scripts/neuro_repository_query.py"
IMPACT = ROOT / "scripts/neuro_repository_file_impact.py"

INDEX = DATA / "inventory.json"
V1 = DATA / "dependency_graph.json"
V2 = DATA / "dependency_graph_v2.json"
ARTIFACTS = (INDEX, V1, V2)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(args, timeout):
    return subprocess.run(
        [sys.executable, "-B", *map(str, args)],
        cwd=ROOT,
        env={
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": str(Path.home()),
            "PYTHONDONTWRITEBYTECODE": "1",
        },
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )

def check_paths(paths):
    for path in paths:
        if not isinstance(path, str):
            raise ValueError("INVALID_PATH")
        p = Path(path)
        if (
            p.is_absolute()
            or ".." in p.parts
            or not p.parts
            or p.parts[0] not in {
                "backend", "frontend", "scripts",
                "alembic", "tests",
            }
            or any(part.startswith(".next") for part in p.parts)
        ):
            raise ValueError("UNSAFE_INDEX_PATH")

def build_graphs():
    raw = INDEX.read_bytes()
    if len(raw) > 20_000_000:
        raise ValueError("INDEX_SIZE_LIMIT")

    index = json.loads(raw)
    if index.get("schema") != "neurovest.repository_intelligence.v1":
        raise ValueError("INDEX_SCHEMA")

    records = index.get("files")
    imports = index.get("imports")

    if not isinstance(records, list) or not isinstance(imports, list):
        raise ValueError("INVALID_INDEX")

    if len(records) > 30000 or len(imports) > 150000:
        raise ValueError("INDEX_LIMIT")

    paths = {
        item["path"] for item in records
        if isinstance(item, dict)
        and isinstance(item.get("path"), str)
    }
    if len(paths) != len(records):
        raise ValueError("DUPLICATE_OR_INVALID_FILES")

    check_paths(paths)

    modules = {}
    for path in sorted(paths):
        if path.endswith(".py"):
            pieces = path[:-3].split("/")
            if pieces[-1] == "__init__":
                pieces.pop()
            modules[".".join(pieces)] = path

    def python_target(source, target):
        relative = target.startswith(".")
        if relative:
            level = len(target) - len(target.lstrip("."))
            suffix = target[level:]
            package = source[:-3].split("/")[:-1]
            if level > len(package):
                return None, "invalid_relative"
            target = ".".join(
                package[:len(package) - level + 1]
                + ([suffix] if suffix else [])
            )

        if target in modules:
            return modules[target], (
                "resolved_relative" if relative else "resolved"
            )

        if any(m.startswith(target + ".") for m in modules):
            return None, "namespace_or_package"

        if target.startswith(("backend.", "alembic.")):
            return None, "internal_not_resolved"

        return None, "external_or_unclassified"

    def frontend_target(source, target):
        if target.startswith("@/"):
            parts = ["frontend"] + target[2:].split("/")
        elif target.startswith(("./", "../")):
            parts = source.split("/")[:-1]
            for part in target.split("/"):
                if part in ("", "."):
                    continue
                if part == "..":
                    if len(parts) <= 1:
                        return None, "invalid_frontend_relative"
                    parts.pop()
                else:
                    parts.append(part)
        else:
            return None, "frontend_package_or_alias"

        base = "/".join(parts)
        if not base.startswith("frontend/"):
            return None, "invalid_frontend_relative"

        candidates = [base]
        for ext in (".ts", ".tsx", ".js", ".jsx"):
            candidates.extend((base + ext, base + "/index" + ext))

        for candidate in candidates:
            if candidate in paths:
                return candidate, "frontend_resolved"

        return None, "frontend_unresolved"

    edges = set()
    cross = Counter()
    categories = Counter()

    for item in imports:
        if not isinstance(item, dict):
            continue
        source = item.get("source")
        target = item.get("import")
        if (
            not isinstance(source, str)
            or source not in paths
            or not isinstance(target, str)
        ):
            continue

        if source.endswith(".py"):
            destination, status = python_target(source, target)
        elif source.endswith((".ts", ".tsx", ".js", ".jsx")):
            destination, status = frontend_target(source, target)
        else:
            continue

        categories[status] += 1

        if destination is None or destination == source:
            continue

        edges.add((source, destination))
        sp = source.split("/")
        dp = destination.split("/")
        if (
            sp[:3] == ["backend", "app", "stacks"]
            and dp[:3] == ["backend", "app", "stacks"]
            and len(sp) >= 5
            and len(dp) >= 5
            and sp[3] != dp[3]
        ):
            cross[(sp[3], dp[3])] += 1

    cross_records = [
        {
            "source_stack": src,
            "target_stack": dst,
            "references": count,
        }
        for (src, dst), count in cross.most_common()
    ]

    graph1 = {
        "schema": "neurovest.repository_dependency_graph.v1",
        "inventory_sha256": digest(INDEX),
        "files_indexed": len(paths),
        "python_imports_resolved": (
            categories["resolved"] + categories["resolved_relative"]
        ),
        "relative_imports_resolved": categories["resolved_relative"],
        "external_or_dynamic_imports": (
            categories["external_or_unclassified"]
        ),
        "unresolved_imports": {
            "INTERNAL_NOT_RESOLVED":
                categories["internal_not_resolved"]
        },
        "cross_stack_dependencies": cross_records,
        "limitations": [
            "Static dependency approximation",
            "Dynamic and symbol-level imports not resolved",
        ],
    }

    graph2 = {
        "schema": "neurovest.repository_dependency_graph.v2",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "inventory_sha256": digest(INDEX),
        "graph_v1_sha256": hashlib.sha256(
            (json.dumps(graph1, indent=2) + "\n").encode()
        ).hexdigest(),
        "files_indexed": len(paths),
        "resolution_counts": dict(sorted(categories.items())),
        "resolved_file_edges": [
            {"source": source, "destination": destination}
            for source, destination in sorted(edges)
        ],
        "cross_stack_dependencies": cross_records,
        "unresolved_examples": {},
        "frontend_unresolved_top": [],
        "limitations": [
            "Static imports only",
            "Dynamic, symbolic and runtime dependencies incomplete",
            "Sensitive modules excluded from source inventory",
            "Test candidates do not prove regression coverage",
        ],
    }
    return graph1, graph2

def atomic_json(path, value):
    temp = path.with_name("." + path.name + ".refresh_pending")
    if temp.exists():
        raise ValueError("PENDING_OUTPUT_EXISTS")
    try:
        temp.write_text(json.dumps(value, indent=2) + "\n", "utf-8")
        temp.chmod(0o600)
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()

def main():
    print("=" * 70)
    print("NEUROVEST — TRANSACTIONAL REPOSITORY REFRESH V1")
    print("=" * 70)

    if len(sys.argv) != 1:
        raise ValueError("NO_ARGUMENTS_ALLOWED")

    if not all(path.is_file() for path in
               (*ARTIFACTS, SCANNER, QUERY, IMPACT)):
        raise ValueError("REQUIRED_FILES_MISSING")

    stamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%S_%fZ"
    )
    backup = ROOT / "runtime/qualification" / (
        "repository_refresh_backup_" + stamp
    )
    backup.mkdir(parents=True, exist_ok=False)
    backup.chmod(0o700)

    prior = {path: digest(path) for path in ARTIFACTS}
    for path in ARTIFACTS:
        destination = backup / path.name
        shutil.copy2(path, destination)
        destination.chmod(0o600)

    print("BACKUP=", backup)
    print("REFRESH=STARTED", flush=True)

    try:
        scan = run([SCANNER], 120)
        if (
            scan.returncode != 0
            or "REPOSITORY_INTELLIGENCE_V1=PASS" not in scan.stdout
        ):
            raise ValueError("SOURCE_SCAN_FAILED")

        graph1, graph2 = build_graphs()
        atomic_json(V1, graph1)
        graph2["graph_v1_sha256"] = digest(V1)
        atomic_json(V2, graph2)

        checks = (
            [QUERY, "summary"],
            [QUERY, "impact", "market_data"],
            [
                IMPACT,
                "backend/app/stacks/chat_public/chat_runtime.py",
            ],
        )

        for args in checks:
            result = run(args, 25)
            if (
                result.returncode != 0
                or "QUERY_STATUS=PASS" not in result.stdout
            ):
                raise ValueError("POST_REFRESH_QUERY_FAILED")

        if json.loads(V2.read_text())["inventory_sha256"] != digest(INDEX):
            raise ValueError("GRAPH_INVENTORY_HASH_MISMATCH")

        print("SOURCE_FILES=", graph2["files_indexed"])
        print("FILE_DEPENDENCY_EDGES=", len(graph2["resolved_file_edges"]))
        print("CROSS_STACK_RELATIONSHIPS=", len(
            graph2["cross_stack_dependencies"]
        ))
        print("INDEX_TO_GRAPH_CONSISTENCY=PASS")
        print("QUERY_ENGINE=PASS")
        print("FILE_IMPACT_ENGINE=PASS")
        print("REPOSITORY_REFRESH=PASS")

    except Exception as exc:
        print("REFRESH_FAILURE=", type(exc).__name__, str(exc)[:100])
        for path in ARTIFACTS:
            saved = backup / path.name
            if digest(saved) != prior[path]:
                raise RuntimeError("BACKUP_INTEGRITY_FAILURE")
            temp = path.with_name("." + path.name + ".rollback_pending")
            try:
                shutil.copy2(saved, temp)
                os.replace(temp, path)
            finally:
                if temp.exists():
                    temp.unlink()

        print("ROLLBACK=PREVIOUS_SNAPSHOTS_RESTORED")
        raise SystemExit(1)

    print("APPLICATION_SOURCE_MODIFIED=False")
    print("BACKEND_RESTARTED=False")
    print("DATABASE_MODIFIED=False")
    print("PATCH_APPLIED=False")
    print("Terminal remains open.")

if __name__ == "__main__":
    print("LEGACY_REPOSITORY_WRITER=RETIRED")
    print("USE_GENERATION_FIRST_WRITER=True")
    raise SystemExit(2)
