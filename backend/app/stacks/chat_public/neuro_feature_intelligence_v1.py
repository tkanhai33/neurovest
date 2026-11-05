from __future__ import annotations

import ast
import os
from collections import Counter
from pathlib import Path

VERSION = "neuro-feature-intelligence-v1"

ROUTE_METHODS = frozenset({
    "get", "post", "put", "patch", "delete",
    "options", "head", "api_route", "websocket",
})

EXCLUDED = frozenset({
    ".git", ".venv", "__pycache__", "node_modules",
    "runtime", "qualification", ".pytest_cache",
})

MAX_FILE_BYTES = 256_000
MAX_FILES = 5000

def _attribute_name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None

def _literal_string(node):
    if isinstance(node, ast.Constant) and isinstance(
        node.value, str
    ):
        return node.value
    return None

def _files(base):
    """
    Bounded Python source discovery.

    Never imports or executes application code.
    Never follows directory symlinks.
    """
    if not base.is_dir() or base.is_symlink():
        return []

    found = []

    for directory, folders, filenames in os.walk(
        base, followlinks=False
    ):
        folders[:] = sorted(
            name for name in folders
            if name not in EXCLUDED
            and not (Path(directory) / name).is_symlink()
        )

        for name in sorted(filenames):
            if not name.endswith(".py"):
                continue

            path = Path(directory) / name

            if path.is_symlink():
                continue

            found.append(path)

            if len(found) >= MAX_FILES:
                return found

    return found

def discover(root):
    root = Path(root).resolve()
    app = root / "backend/app"

    files = _files(app)

    stacks = {}
    route_methods = Counter()
    route_files = set()
    router_inclusions = set()
    parse_failures = 0
    files_examined = 0
    test_files = 0

    for path in files:
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                continue

            tree = ast.parse(
                path.read_text(encoding="utf-8"),
                filename=str(path),
            )

        except (OSError, UnicodeError, SyntaxError):
            parse_failures += 1
            continue

        files_examined += 1

        relative = path.relative_to(app)
        parts = relative.parts

        stack = (
            parts[1]
            if len(parts) >= 3 and parts[0] == "stacks"
            else "_application"
        )

        stats = stacks.setdefault(stack, {
            "source_files": 0,
            "test_files": 0,
            "route_declarations": 0,
            "router_include_calls": 0,
            "handler_definitions": 0,
            "syntax_errors": 0,
        })

        stats["source_files"] += 1

        if path.name.startswith("test_"):
            test_files += 1
            stats["test_files"] += 1

        for node in ast.walk(tree):
            if isinstance(node, (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            )):
                stats["handler_definitions"] += 1

                for decorator in node.decorator_list:
                    if not isinstance(decorator, ast.Call):
                        continue

                    method = _attribute_name(
                        decorator.func
                    )

                    if method not in ROUTE_METHODS:
                        continue

                    # Require decorator syntax such as
                    # @router.get or @app.post.
                    if not isinstance(
                        decorator.func, ast.Attribute
                    ):
                        continue

                    # This is a declared route, not proof that
                    # it is mounted or publicly reachable.
                    route_methods[method] += 1
                    stats["route_declarations"] += 1
                    route_files.add(str(relative))

            elif isinstance(node, ast.Call):
                if _attribute_name(
                    node.func
                ) == "include_router":
                    stats["router_include_calls"] += 1
                    router_inclusions.add(str(relative))

    total_routes = sum(route_methods.values())

    return {
        "schema_version": VERSION,
        "source_files_examined": files_examined,
        "test_files_discovered": test_files,
        "source_parse_failures": parse_failures,
        "max_files_reached": len(files) >= MAX_FILES,
        "declared_routes": total_routes,
        "route_methods": dict(sorted(
            route_methods.items()
        )),
        "files_with_route_declarations": len(route_files),
        "files_with_router_inclusions": len(router_inclusions),
        "stacks": dict(sorted(stacks.items())),
        "evidence_limits": [
            "Static source inspection only",
            "Declared routes are not verified mounted routes",
            "Test filenames do not establish functional coverage",
            "Source presence does not establish production readiness",
            "No application modules were imported or executed",
        ],
    }

def development_findings(features):
    findings = []

    if features["max_files_reached"]:
        findings.append({
            "id": "feature_inventory_scan_limit",
            "title": "Expand bounded capability source inventory",
            "capability": "chat_public",
            "score": 70.0,
            "observation": (
                "Source discovery reached its file limit; "
                "coverage is incomplete."
            ),
            "next_action": (
                "Partition the source inventory into "
                "bounded verified scan units."
            ),
            "validation": (
                "Confirm every application source unit "
                "is inventoried exactly once."
            ),
            "confidence": "high",
            "developer_authorization_required": True,
        })

    if features["source_parse_failures"]:
        findings.append({
            "id": "feature_source_parse_gaps",
            "title": "Investigate unreadable or invalid Python sources",
            "capability": "runtime",
            "score": 63.0,
            "observation": (
                str(features["source_parse_failures"])
                + " source files could not be parsed."
            ),
            "next_action": (
                "Classify source parsing failures without "
                "executing untrusted modules."
            ),
            "validation": (
                "Re-run bounded AST inventory after correction."
            ),
            "confidence": "high",
            "developer_authorization_required": True,
        })

    if features["declared_routes"]:
        findings.append({
            "id": "api_route_contract_traceability",
            "title": "Connect declared API routes to runtime qualification",
            "capability": "chat_public",
            "score": 61.0,
            "observation": (
                str(features["declared_routes"])
                + " route declarations were found in source. "
                "Static inspection does not establish which "
                "are mounted, authorized or tested."
            ),
            "next_action": (
                "Build an authenticated route-to-handler and "
                "test-evidence map, then identify actual gaps."
            ),
            "validation": (
                "Compare a read-only application route map "
                "against source declarations and authorization tests."
            ),
            "confidence": "high",
            "developer_authorization_required": True,
        })

    return findings

def extend_assessment(assessment):
    features = discover(assessment["_root"])

    result = {
        key: value for key, value in assessment.items()
        if key != "_root"
    }

    result["feature_inventory"] = features

    recommendations = list(
        result.get("recommendations", [])
    )

    known = {
        item["id"] for item in recommendations
    }

    for finding in development_findings(features):
        if finding["id"] not in known:
            recommendations.append(finding)
            known.add(finding["id"])

    recommendations.sort(
        key=lambda item: (
            -float(item.get("score", 0)),
            item["id"],
        )
    )

    result["recommendations"] = recommendations

    return result

def render_feature_summary(features):
    lines = [
        "SOURCE-BACKED FEATURE INVENTORY",
        "Python source files inspected: "
        + str(features["source_files_examined"]),
        "Test files discovered: "
        + str(features["test_files_discovered"]),
        "Declared API routes: "
        + str(features["declared_routes"]),
        "Files containing router inclusion calls: "
        + str(features["files_with_router_inclusions"]),
        "",
        "Capability source distribution:",
    ]

    ranked = sorted(
        features["stacks"].items(),
        key=lambda pair: (
            -pair[1]["route_declarations"],
            -pair[1]["source_files"],
            pair[0],
        )
    )

    for name, stats in ranked[:12]:
        lines.append(
            "- " + name
            + ": " + str(stats["source_files"])
            + " source files, "
            + str(stats["route_declarations"])
            + " declared routes, "
            + str(stats["test_files"])
            + " discovered test files"
        )

    lines.extend([
        "",
        "Static discovery is not evidence of endpoint "
        "availability, authorization or production readiness.",
    ])

    return "\n".join(lines)



def discover_route_contracts(root, limit=2000):
    """
    Identify declared API route-to-handler relationships.

    Static AST analysis only. No application imports, requests,
    database queries, route mounting or authorization claims.
    """
    root = Path(root).resolve()
    app = root / "backend/app"

    records = []
    examined = 0
    truncated = False

    for path in _files(app):
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                continue

            tree = ast.parse(
                path.read_text(encoding="utf-8"),
                filename=str(path),
            )

        except (OSError, UnicodeError, SyntaxError):
            continue

        examined += 1

        relative = str(path.relative_to(root))

        for node in ast.walk(tree):
            if not isinstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef)
            ):
                continue

            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call):
                    continue

                func = decorator.func

                if not isinstance(func, ast.Attribute):
                    continue

                method = func.attr

                if method not in ROUTE_METHODS:
                    continue

                route = None

                if decorator.args:
                    route = _literal_string(decorator.args[0])

                if route is None:
                    for keyword in decorator.keywords:
                        if keyword.arg in ("path", "url_path"):
                            route = _literal_string(keyword.value)
                            break

                if route is None:
                    route = "[dynamic-or-unresolved]"

                # A declaration is not evidence that an endpoint
                # is reachable, authorized or tested.
                records.append({
                    "module_path": relative,
                    "handler": node.name[:120],
                    "method": method.upper(),
                    "declared_path": route[:180],
                    "line": node.lineno,
                    "async_handler": isinstance(
                        node, ast.AsyncFunctionDef
                    ),
                    "mounted": "unverified",
                    "authorization": "unverified",
                    "test_coverage": "unverified",
                })

                if len(records) >= limit:
                    truncated = True
                    break

            if truncated:
                break

        if truncated:
            break

    return {
        "schema_version": "neuro-route-contract-v1",
        "source_files_examined": examined,
        "route_contracts": records,
        "contract_count": len(records),
        "truncated": truncated,
        "limits": [
            "Static route declarations only",
            "Mounted availability not established",
            "Authorization not established",
            "Test coverage not established",
        ],
    }
