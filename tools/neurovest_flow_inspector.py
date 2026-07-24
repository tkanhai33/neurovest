#!/usr/bin/env python3
"""
NeuroVest Standalone Flow Inspector

Read-only architecture verification:

Frontend call
  -> backend route
  -> endpoint
  -> FastAPI dependencies
  -> services/helpers
  -> repositories
  -> models/database boundaries

Outputs:
- runtime/architecture/neurovest_flow_latest.json
- runtime/architecture/neurovest_flow_latest.txt
- runtime/architecture/neurovest_flow_latest.dot
- runtime/architecture/neurovest_flow_latest.svg
- runtime/architecture/neurovest_flow_latest.html

No database writes.
No service restarts.
No broker activity.
No application-source modifications.
"""

from __future__ import annotations

import argparse
import ast
import html
import importlib
import inspect
import json
import re
import shutil
import subprocess
import sys
import traceback
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend" / "app"
FRONTEND_ROOT = ROOT / "frontend"
OUTPUT_ROOT = ROOT / "runtime" / "architecture"

JSON_OUTPUT = OUTPUT_ROOT / "neurovest_flow_latest.json"
TEXT_OUTPUT = OUTPUT_ROOT / "neurovest_flow_latest.txt"
DOT_OUTPUT = OUTPUT_ROOT / "neurovest_flow_latest.dot"
SVG_OUTPUT = OUTPUT_ROOT / "neurovest_flow_latest.svg"
HTML_OUTPUT = OUTPUT_ROOT / "neurovest_flow_latest.html"

MAX_STATIC_DEPTH = 7

HTTP_METHODS = {
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
    "HEAD",
}

IGNORED_DIRECTORY_NAMES = {
    ".git",
    ".next",
    ".venv",
    "__pycache__",
    "node_modules",
    "runtime",
    "backups",
    "architecture_backup",
}

IGNORED_FILE_SIGNALS = (
    ".before_",
    ".phase",
    ".bak",
)

CATEGORY_COLORS = {
    "frontend": "#38bdf8",
    "application": "#22d3ee",
    "middleware": "#06b6d4",
    "router": "#34d399",
    "endpoint": "#facc15",
    "dependency": "#c084fc",
    "service": "#fb923c",
    "repository": "#f87171",
    "model": "#a78bfa",
    "database": "#818cf8",
    "event": "#2dd4bf",
    "background": "#f472b6",
    "unknown": "#94a3b8",
}


@dataclass(frozen=True)
class Node:
    node_id: str
    label: str
    category: str
    file: str | None = None
    symbol: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Edge:
    source: str
    destination: str
    relationship: str
    status: str = "VERIFIED"
    evidence: str | None = None


@dataclass
class FrontendCall:
    file: str
    function: str
    method: str
    path: str
    line: int
    evidence: str


@dataclass
class RuntimeRoute:
    method: str
    path: str
    endpoint_name: str
    endpoint_module: str
    endpoint_file: str | None
    route_name: str
    policy: str | None
    dependencies: list[dict[str, Any]]
    websocket: bool = False


@dataclass
class Issue:
    severity: str
    code: str
    detail: str
    evidence: str | None = None


@dataclass
class FunctionRecord:
    qualified_name: str
    module: str
    name: str
    file: str
    line: int
    calls: set[str]
    imported_names: dict[str, str]


def relative(path: Path | str | None) -> str | None:
    if path is None:
        return None

    resolved = Path(path).resolve()

    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def stable_unique(values: Iterable[str]) -> list[str]:
    return sorted(set(values))


def normalize_path(value: str) -> str:
    path = value.strip()

    path = re.sub(
        r"\$\{([^}]+)\}",
        r"{\1}",
        path,
    )

    path = re.sub(
        r"\[([A-Za-z_][A-Za-z0-9_]*)\]",
        r"{\1}",
        path,
    )

    if not path.startswith("/"):
        slash = path.find("/")

        if slash >= 0:
            path = path[slash:]

    path = path.split("?", 1)[0]
    path = re.sub(r"/+", "/", path)

    if len(path) > 1:
        path = path.rstrip("/")

    return path


def route_shape(path: str) -> str:
    normalized = normalize_path(path)

    return re.sub(
        r"\{[^}/]+\}",
        "{}",
        normalized,
    )


def should_ignore(path: Path) -> bool:
    if any(part in IGNORED_DIRECTORY_NAMES for part in path.parts):
        return True

    name = path.name

    return any(
        signal in name
        for signal in IGNORED_FILE_SIGNALS
    )


def python_module_for(path: Path) -> str:
    relative_path = path.relative_to(ROOT)
    return ".".join(relative_path.with_suffix("").parts)


def parse_python_inventory() -> tuple[
    dict[str, FunctionRecord],
    dict[str, list[FunctionRecord]],
    list[Issue],
]:
    functions: dict[str, FunctionRecord] = {}
    by_simple_name: dict[str, list[FunctionRecord]] = defaultdict(list)
    issues: list[Issue] = []

    for path in sorted(BACKEND_ROOT.rglob("*.py")):
        if should_ignore(path):
            continue

        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
        except Exception as exc:
            issues.append(
                Issue(
                    severity="ERROR",
                    code="PYTHON_PARSE_ERROR",
                    detail=f"Could not parse {relative(path)}",
                    evidence=f"{type(exc).__name__}: {exc}",
                )
            )
            continue

        module = python_module_for(path)
        imports: dict[str, str] = {}

        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    local = alias.asname or alias.name.split(".")[0]
                    imports[local] = alias.name

            elif isinstance(node, ast.ImportFrom):
                base = node.module or ""

                for alias in node.names:
                    local = alias.asname or alias.name
                    imports[local] = (
                        f"{base}.{alias.name}"
                        if base
                        else alias.name
                    )

        class Visitor(ast.NodeVisitor):
            def __init__(self) -> None:
                self.class_stack: list[str] = []

            def visit_ClassDef(self, node: ast.ClassDef) -> Any:
                self.class_stack.append(node.name)
                self.generic_visit(node)
                self.class_stack.pop()

            def record(
                self,
                node: ast.FunctionDef | ast.AsyncFunctionDef,
            ) -> None:
                calls: set[str] = set()

                for child in ast.walk(node):
                    if not isinstance(child, ast.Call):
                        continue

                    target = child.func

                    if isinstance(target, ast.Name):
                        calls.add(target.id)

                    elif isinstance(target, ast.Attribute):
                        parts: list[str] = []
                        current: ast.AST = target

                        while isinstance(current, ast.Attribute):
                            parts.append(current.attr)
                            current = current.value

                        if isinstance(current, ast.Name):
                            parts.append(current.id)

                        calls.add(".".join(reversed(parts)))

                symbol_parts = [
                    module,
                    *self.class_stack,
                    node.name,
                ]

                qualified = ".".join(symbol_parts)

                record = FunctionRecord(
                    qualified_name=qualified,
                    module=module,
                    name=node.name,
                    file=str(relative(path)),
                    line=node.lineno,
                    calls=calls,
                    imported_names=dict(imports),
                )

                functions[qualified] = record
                by_simple_name[node.name].append(record)

            def visit_FunctionDef(
                self,
                node: ast.FunctionDef,
            ) -> Any:
                self.record(node)
                self.generic_visit(node)

            def visit_AsyncFunctionDef(
                self,
                node: ast.AsyncFunctionDef,
            ) -> Any:
                self.record(node)
                self.generic_visit(node)

        Visitor().visit(tree)

    return functions, by_simple_name, issues


def enclosing_frontend_function(
    source: str,
    position: int,
) -> str:
    prefix = source[:position]

    patterns = [
        r"(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(",
        (
            r"(?:const|let|var)\s+([A-Za-z_$][\w$]*)"
            r"\s*=\s*(?:async\s*)?\("
        ),
        (
            r"(?:const|let|var)\s+([A-Za-z_$][\w$]*)"
            r"\s*=\s*(?:async\s*)?[A-Za-z_$][\w$]*\s*=>"
        ),
    ]

    best_name = "<module>"
    best_position = -1

    for pattern in patterns:
        for match in re.finditer(pattern, prefix):
            if match.start() > best_position:
                best_name = match.group(1)
                best_position = match.start()

    return best_name


def discover_frontend_calls() -> list[FrontendCall]:
    calls: list[FrontendCall] = []

    if not FRONTEND_ROOT.is_dir():
        return calls

    source_extensions = {
        ".js",
        ".jsx",
        ".mjs",
        ".ts",
        ".tsx",
    }

    fetch_pattern = re.compile(
        r"""fetch\s*\(\s*([`'"])(?P<path>.+?)\1\s*,?\s*(?P<options>\{.*?\})?\s*\)""",
        re.DOTALL,
    )

    axios_pattern = re.compile(
        r"""axios\.(?P<method>get|post|put|patch|delete)\s*\(\s*([`'"])(?P<path>.+?)\2""",
        re.IGNORECASE | re.DOTALL,
    )

    generic_api_patterns = [
        re.compile(
            r"""(?:apiFetch|request|apiRequest)\s*\(\s*([`'"])(?P<path>.+?)\1\s*,?\s*(?P<options>\{.*?\})?\s*\)""",
            re.DOTALL,
        ),
    ]

    for path in sorted(FRONTEND_ROOT.rglob("*")):
        if (
            not path.is_file()
            or path.suffix not in source_extensions
            or should_ignore(path)
        ):
            continue

        try:
            source = path.read_text(
                encoding="utf-8",
                errors="replace",
            )
        except Exception:
            continue

        for match in fetch_pattern.finditer(source):
            raw_path = match.group("path")

            if "/" not in raw_path:
                continue

            options = match.group("options") or ""
            method_match = re.search(
                r"""method\s*:\s*['"]([A-Za-z]+)['"]""",
                options,
            )

            method = (
                method_match.group(1).upper()
                if method_match
                else "GET"
            )

            line = source.count(
                "\n",
                0,
                match.start(),
            ) + 1

            calls.append(
                FrontendCall(
                    file=str(relative(path)),
                    function=enclosing_frontend_function(
                        source,
                        match.start(),
                    ),
                    method=method,
                    path=normalize_path(raw_path),
                    line=line,
                    evidence=match.group(0)[:300],
                )
            )

        for pattern in generic_api_patterns:
            for match in pattern.finditer(source):
                raw_path = match.group("path")

                if "/" not in raw_path:
                    continue

                options = match.group("options") or ""
                method_match = re.search(
                    r"""method\s*:\s*['"]([A-Za-z]+)['"]""",
                    options,
                )

                method = (
                    method_match.group(1).upper()
                    if method_match
                    else "GET"
                )

                line = source.count(
                    "\n",
                    0,
                    match.start(),
                ) + 1

                calls.append(
                    FrontendCall(
                        file=str(relative(path)),
                        function=enclosing_frontend_function(
                            source,
                            match.start(),
                        ),
                        method=method,
                        path=normalize_path(raw_path),
                        line=line,
                        evidence=match.group(0)[:300],
                    )
                )

        for match in axios_pattern.finditer(source):
            raw_path = match.group("path")

            if "/" not in raw_path:
                continue

            line = source.count(
                "\n",
                0,
                match.start(),
            ) + 1

            calls.append(
                FrontendCall(
                    file=str(relative(path)),
                    function=enclosing_frontend_function(
                        source,
                        match.start(),
                    ),
                    method=match.group("method").upper(),
                    path=normalize_path(raw_path),
                    line=line,
                    evidence=match.group(0)[:300],
                )
            )

    deduplicated: dict[
        tuple[str, str, str, str, int],
        FrontendCall,
    ] = {}

    for call in calls:
        key = (
            call.file,
            call.function,
            call.method,
            call.path,
            call.line,
        )
        deduplicated[key] = call

    return sorted(
        deduplicated.values(),
        key=lambda item: (
            item.file,
            item.line,
            item.method,
            item.path,
        ),
    )


def callable_metadata(call: Any) -> dict[str, Any]:
    module = getattr(
        call,
        "__module__",
        type(call).__module__,
    )

    name = getattr(
        call,
        "__qualname__",
        getattr(
            call,
            "__name__",
            type(call).__qualname__,
        ),
    )

    source_file: str | None = None

    try:
        source_file = relative(
            Path(inspect.getsourcefile(call) or "")
        )
    except Exception:
        source_file = None

    return {
        "module": module,
        "name": name,
        "qualified": f"{module}.{name}",
        "file": source_file,
    }


def walk_fastapi_dependencies(
    dependant: Any,
    *,
    parent: str | None = None,
    seen: set[int] | None = None,
) -> list[dict[str, Any]]:
    if seen is None:
        seen = set()

    output: list[dict[str, Any]] = []

    for dependency in getattr(
        dependant,
        "dependencies",
        [],
    ):
        dependency_id = id(dependency)

        if dependency_id in seen:
            continue

        seen.add(dependency_id)

        call = getattr(dependency, "call", None)

        if call is None:
            continue

        metadata = callable_metadata(call)
        metadata["parent"] = parent
        output.append(metadata)

        output.extend(
            walk_fastapi_dependencies(
                dependency,
                parent=metadata["qualified"],
                seen=seen,
            )
        )

    return output


def resolve_policy(
    method: str,
    path: str,
) -> tuple[str | None, str | None]:
    candidates = [
        (
            "backend.app.stacks.identity_auth.route_protection",
            "resolve_route_policy",
        ),
    ]

    for module_name, symbol in candidates:
        try:
            module = importlib.import_module(module_name)
            resolver = getattr(module, symbol)
            result = resolver(method, path)

            if result is None:
                return None, f"{module_name}.{symbol}"

            value = getattr(result, "value", result)
            return str(value), f"{module_name}.{symbol}"

        except Exception:
            continue

    return None, None


def discover_runtime_routes() -> tuple[
    list[RuntimeRoute],
    list[Issue],
    dict[str, Any],
]:
    issues: list[Issue] = []
    runtime_metadata: dict[str, Any] = {}

    try:
        main_module = importlib.import_module(
            "backend.app.main"
        )
        app = getattr(main_module, "app")

    except Exception as exc:
        issues.append(
            Issue(
                severity="BLOCKING",
                code="APP_IMPORT_FAILED",
                detail=(
                    "Could not import "
                    "backend.app.main:app"
                ),
                evidence=(
                    f"{type(exc).__name__}: {exc}\n"
                    f"{traceback.format_exc()}"
                ),
            )
        )
        return [], issues, runtime_metadata

    runtime_metadata["app_imported"] = True
    runtime_metadata["app_type"] = (
        f"{type(app).__module__}."
        f"{type(app).__qualname__}"
    )

    runtime_metadata["middleware"] = [
        {
            "class": (
                f"{item.cls.__module__}."
                f"{item.cls.__qualname__}"
            ),
            "options": repr(item.kwargs),
        }
        for item in getattr(
            app,
            "user_middleware",
            [],
        )
    ]

    routes: list[RuntimeRoute] = []

    try:
        from fastapi.routing import APIRoute
        from starlette.routing import WebSocketRoute
    except Exception as exc:
        issues.append(
            Issue(
                severity="BLOCKING",
                code="FASTAPI_IMPORT_FAILED",
                detail="Could not inspect FastAPI routes",
                evidence=f"{type(exc).__name__}: {exc}",
            )
        )
        return routes, issues, runtime_metadata

    for route in getattr(app, "routes", []):
        if isinstance(route, APIRoute):
            endpoint = route.endpoint
            endpoint_info = callable_metadata(endpoint)

            methods = sorted(
                route.methods or {"GET"}
            )

            dependencies = walk_fastapi_dependencies(
                route.dependant,
                parent=endpoint_info["qualified"],
            )

            for method in methods:
                policy, _ = resolve_policy(
                    method,
                    route.path,
                )

                routes.append(
                    RuntimeRoute(
                        method=method,
                        path=normalize_path(route.path),
                        endpoint_name=endpoint_info["name"],
                        endpoint_module=endpoint_info["module"],
                        endpoint_file=endpoint_info["file"],
                        route_name=route.name,
                        policy=policy,
                        dependencies=dependencies,
                    )
                )

        elif isinstance(route, WebSocketRoute):
            endpoint_info = callable_metadata(
                route.endpoint
            )

            routes.append(
                RuntimeRoute(
                    method="WEBSOCKET",
                    path=normalize_path(route.path),
                    endpoint_name=endpoint_info["name"],
                    endpoint_module=endpoint_info["module"],
                    endpoint_file=endpoint_info["file"],
                    route_name=route.name,
                    policy=None,
                    dependencies=[],
                    websocket=True,
                )
            )

    return routes, issues, runtime_metadata


def classify_symbol(
    *,
    name: str,
    module: str,
    file: str | None,
) -> str:
    combined = " ".join(
        value.lower()
        for value in (
            name,
            module,
            file or "",
        )
    )

    if "frontend" in combined:
        return "frontend"

    if "repository" in combined or "repositories.py" in combined:
        return "repository"

    if (
        "model" in combined
        or "models.py" in combined
        or "schema" in combined
    ):
        return "model"

    if (
        "database" in combined
        or "db_runtime" in combined
        or "async_session" in combined
        or "postgres" in combined
    ):
        return "database"

    if "middleware" in combined:
        return "middleware"

    if "router" in combined:
        return "router"

    if (
        "dependenc" in combined
        or name.startswith("get_")
        or name.startswith("require_")
        or name.startswith("optional_")
        or name.startswith("authenticate_")
    ):
        return "dependency"

    if "event" in combined or "broker" in combined:
        return "event"

    if (
        "daemon" in combined
        or "background" in combined
        or "reconciliation" in combined
    ):
        return "background"

    if (
        "service" in combined
        or "facade" in combined
        or "runtime" in combined
        or "adapter" in combined
        or "provider" in combined
        or "client" in combined
    ):
        return "service"

    return "unknown"


def best_static_targets(
    record: FunctionRecord,
    by_simple_name: dict[str, list[FunctionRecord]],
) -> list[FunctionRecord]:
    targets: list[FunctionRecord] = []

    for call in sorted(record.calls):
        root_name = call.split(".", 1)[0]
        leaf_name = call.rsplit(".", 1)[-1]

        imported = record.imported_names.get(root_name)

        if imported:
            exact = [
                candidate
                for candidate in by_simple_name.get(
                    leaf_name,
                    [],
                )
                if (
                    candidate.module == imported
                    or candidate.qualified_name.startswith(
                        f"{imported}."
                    )
                )
            ]

            if exact:
                targets.extend(exact)
                continue

        candidates = by_simple_name.get(
            leaf_name,
            [],
        )

        local_candidates = [
            candidate
            for candidate in candidates
            if candidate.module == record.module
        ]

        if len(local_candidates) == 1:
            targets.extend(local_candidates)

        elif len(candidates) == 1:
            targets.extend(candidates)

    result: dict[str, FunctionRecord] = {}

    for target in targets:
        result[target.qualified_name] = target

    return sorted(
        result.values(),
        key=lambda item: item.qualified_name,
    )


def matching_function_record(
    *,
    module: str,
    name: str,
    functions: dict[str, FunctionRecord],
) -> FunctionRecord | None:
    candidates = [
        record
        for record in functions.values()
        if (
            record.module == module
            and (
                record.name == name
                or record.qualified_name.endswith(
                    f".{name}"
                )
            )
        )
    ]

    if len(candidates) == 1:
        return candidates[0]

    return None


def add_node(
    nodes: dict[str, Node],
    node: Node,
) -> None:
    existing = nodes.get(node.node_id)

    if existing is None:
        nodes[node.node_id] = node


def add_edge(
    edges: dict[tuple[str, str, str], Edge],
    edge: Edge,
) -> None:
    key = (
        edge.source,
        edge.destination,
        edge.relationship,
    )

    if key not in edges:
        edges[key] = edge


def build_flow_graph(
    frontend_calls: list[FrontendCall],
    runtime_routes: list[RuntimeRoute],
    functions: dict[str, FunctionRecord],
    by_simple_name: dict[str, list[FunctionRecord]],
) -> tuple[
    dict[str, Node],
    dict[tuple[str, str, str], Edge],
    list[dict[str, Any]],
    list[Issue],
]:
    nodes: dict[str, Node] = {}
    edges: dict[tuple[str, str, str], Edge] = {}
    flows: list[dict[str, Any]] = []
    issues: list[Issue] = []

    app_node = "app:backend.app.main:app"

    add_node(
        nodes,
        Node(
            node_id=app_node,
            label="backend.app.main:app",
            category="application",
            file="backend/app/main.py",
            symbol="app",
        ),
    )

    route_lookup: dict[
        tuple[str, str],
        list[RuntimeRoute],
    ] = defaultdict(list)

    shape_lookup: dict[
        tuple[str, str],
        list[RuntimeRoute],
    ] = defaultdict(list)

    for route in runtime_routes:
        route_lookup[
            (
                route.method,
                normalize_path(route.path),
            )
        ].append(route)

        shape_lookup[
            (
                route.method,
                route_shape(route.path),
            )
        ].append(route)

        endpoint_id = (
            "endpoint:"
            f"{route.method}:"
            f"{route.path}:"
            f"{route.endpoint_module}."
            f"{route.endpoint_name}"
        )

        add_node(
            nodes,
            Node(
                node_id=endpoint_id,
                label=(
                    f"{route.method} {route.path}\n"
                    f"{route.endpoint_name}"
                ),
                category="endpoint",
                file=route.endpoint_file,
                symbol=route.endpoint_name,
                metadata={
                    "policy": route.policy,
                    "route_name": route.route_name,
                },
            ),
        )

        add_edge(
            edges,
            Edge(
                source=app_node,
                destination=endpoint_id,
                relationship="MOUNTS",
                status="VERIFIED",
                evidence="Runtime FastAPI route table",
            ),
        )

        parent_id = endpoint_id

        for dependency in route.dependencies:
            dependency_id = (
                "dependency:"
                f"{dependency['qualified']}"
            )

            category = classify_symbol(
                name=dependency["name"],
                module=dependency["module"],
                file=dependency["file"],
            )

            if category == "unknown":
                category = "dependency"

            add_node(
                nodes,
                Node(
                    node_id=dependency_id,
                    label=dependency["name"],
                    category=category,
                    file=dependency["file"],
                    symbol=dependency["name"],
                ),
            )

            dependency_parent = dependency.get("parent")
            source_id = parent_id

            if dependency_parent:
                candidate = (
                    "dependency:"
                    f"{dependency_parent}"
                )

                if candidate in nodes:
                    source_id = candidate

            add_edge(
                edges,
                Edge(
                    source=source_id,
                    destination=dependency_id,
                    relationship="DEPENDS",
                    status="VERIFIED",
                    evidence="FastAPI dependant graph",
                ),
            )

        root_record = matching_function_record(
            module=route.endpoint_module,
            name=route.endpoint_name.split(".")[-1],
            functions=functions,
        )

        if root_record is not None:
            queue: deque[
                tuple[FunctionRecord, str, int]
            ] = deque(
                [
                    (
                        root_record,
                        endpoint_id,
                        0,
                    )
                ]
            )

            visited: set[str] = set()

            while queue:
                record, source_id, depth = queue.popleft()

                if (
                    record.qualified_name in visited
                    or depth >= MAX_STATIC_DEPTH
                ):
                    continue

                visited.add(record.qualified_name)

                for target in best_static_targets(
                    record,
                    by_simple_name,
                ):
                    category = classify_symbol(
                        name=target.name,
                        module=target.module,
                        file=target.file,
                    )

                    target_id = (
                        f"{category}:"
                        f"{target.qualified_name}"
                    )

                    add_node(
                        nodes,
                        Node(
                            node_id=target_id,
                            label=target.name,
                            category=category,
                            file=target.file,
                            symbol=target.name,
                            metadata={
                                "line": target.line,
                            },
                        ),
                    )

                    add_edge(
                        edges,
                        Edge(
                            source=source_id,
                            destination=target_id,
                            relationship="CALLS",
                            status="STATIC_VERIFIED",
                            evidence=(
                                f"{record.file}:"
                                f"{record.line}"
                            ),
                        ),
                    )

                    queue.append(
                        (
                            target,
                            target_id,
                            depth + 1,
                        )
                    )

    for call in frontend_calls:
        frontend_id = (
            "frontend:"
            f"{call.file}:"
            f"{call.function}:"
            f"{call.line}"
        )

        add_node(
            nodes,
            Node(
                node_id=frontend_id,
                label=(
                    f"{call.function}\n"
                    f"{call.method} {call.path}"
                ),
                category="frontend",
                file=call.file,
                symbol=call.function,
                metadata={
                    "line": call.line,
                },
            ),
        )

        exact = route_lookup.get(
            (
                call.method,
                normalize_path(call.path),
            ),
            [],
        )

        shape = shape_lookup.get(
            (
                call.method,
                route_shape(call.path),
            ),
            [],
        )

        matches = exact or shape

        flow = {
            "frontend": asdict(call),
            "matched_routes": [],
            "status": "VERIFIED",
            "hops": [],
        }

        flow["hops"].append(
            {
                "hop": 0,
                "node": frontend_id,
                "label": nodes[frontend_id].label,
                "category": "frontend",
            }
        )

        if not matches:
            flow["status"] = "BROKEN"
            issues.append(
                Issue(
                    severity="ERROR",
                    code="FRONTEND_ROUTE_MISSING",
                    detail=(
                        f"{call.method} {call.path} from "
                        f"{call.file}:{call.line} has no "
                        "matching backend route"
                    ),
                    evidence=call.evidence,
                )
            )
            flows.append(flow)
            continue

        if len(matches) > 1:
            flow["status"] = "AMBIGUOUS"
            issues.append(
                Issue(
                    severity="ERROR",
                    code="FRONTEND_ROUTE_AMBIGUOUS",
                    detail=(
                        f"{call.method} {call.path} matches "
                        f"{len(matches)} backend routes"
                    ),
                    evidence=", ".join(
                        (
                            f"{route.method} {route.path} "
                            f"{route.endpoint_module}."
                            f"{route.endpoint_name}"
                        )
                        for route in matches
                    ),
                )
            )

        for route in matches:
            endpoint_id = (
                "endpoint:"
                f"{route.method}:"
                f"{route.path}:"
                f"{route.endpoint_module}."
                f"{route.endpoint_name}"
            )

            add_edge(
                edges,
                Edge(
                    source=frontend_id,
                    destination=endpoint_id,
                    relationship="HTTP_CALL",
                    status=(
                        "VERIFIED"
                        if len(matches) == 1
                        else "AMBIGUOUS"
                    ),
                    evidence=(
                        f"{call.file}:{call.line}"
                    ),
                ),
            )

            flow["matched_routes"].append(
                {
                    "method": route.method,
                    "path": route.path,
                    "endpoint": (
                        f"{route.endpoint_module}."
                        f"{route.endpoint_name}"
                    ),
                    "policy": route.policy,
                }
            )

            flow["hops"].append(
                {
                    "hop": 1,
                    "node": endpoint_id,
                    "label": nodes[endpoint_id].label,
                    "category": "endpoint",
                    "policy": route.policy,
                }
            )

            downstream = downstream_hops(
                endpoint_id,
                nodes,
                edges,
            )

            for hop_number, node_id in downstream:
                flow["hops"].append(
                    {
                        "hop": hop_number + 1,
                        "node": node_id,
                        "label": nodes[node_id].label,
                        "category": nodes[node_id].category,
                    }
                )

        flows.append(flow)

    return nodes, edges, flows, issues


def downstream_hops(
    start: str,
    nodes: dict[str, Node],
    edges: dict[tuple[str, str, str], Edge],
) -> list[tuple[int, str]]:
    adjacency: dict[str, list[str]] = defaultdict(list)

    for edge in edges.values():
        if edge.relationship in {
            "DEPENDS",
            "CALLS",
        }:
            adjacency[edge.source].append(
                edge.destination
            )

    output: list[tuple[int, str]] = []
    queue: deque[tuple[str, int]] = deque(
        [(start, 0)]
    )
    seen = {start}

    while queue:
        current, depth = queue.popleft()

        for destination in sorted(
            adjacency.get(current, [])
        ):
            if destination in seen:
                continue

            seen.add(destination)
            output.append(
                (
                    depth + 1,
                    destination,
                )
            )
            queue.append(
                (
                    destination,
                    depth + 1,
                )
            )

    return output


def inspect_overlaps(
    frontend_calls: list[FrontendCall],
    runtime_routes: list[RuntimeRoute],
    nodes: dict[str, Node],
    edges: dict[tuple[str, str, str], Edge],
) -> list[Issue]:
    issues: list[Issue] = []

    route_pairs: dict[
        tuple[str, str],
        list[RuntimeRoute],
    ] = defaultdict(list)

    route_shapes: dict[
        tuple[str, str],
        list[RuntimeRoute],
    ] = defaultdict(list)

    for route in runtime_routes:
        route_pairs[
            (
                route.method,
                normalize_path(route.path),
            )
        ].append(route)

        route_shapes[
            (
                route.method,
                route_shape(route.path),
            )
        ].append(route)

    for pair, routes in route_pairs.items():
        if len(routes) <= 1:
            continue

        issues.append(
            Issue(
                severity="BLOCKING",
                code="DUPLICATE_RUNTIME_ROUTE",
                detail=(
                    f"{pair[0]} {pair[1]} is mounted "
                    f"{len(routes)} times"
                ),
                evidence=", ".join(
                    (
                        f"{route.endpoint_module}."
                        f"{route.endpoint_name}"
                    )
                    for route in routes
                ),
            )
        )

    for pair, routes in route_shapes.items():
        unique_paths = {
            normalize_path(route.path)
            for route in routes
        }

        if (
            len(routes) > 1
            and len(unique_paths) > 1
        ):
            issues.append(
                Issue(
                    severity="WARNING",
                    code="OVERLAPPING_ROUTE_SHAPES",
                    detail=(
                        f"{pair[0]} route shape "
                        f"{pair[1]} has overlapping paths"
                    ),
                    evidence=", ".join(
                        sorted(unique_paths)
                    ),
                )
            )

    frontend_pairs: dict[
        tuple[str, str],
        list[FrontendCall],
    ] = defaultdict(list)

    for call in frontend_calls:
        frontend_pairs[
            (
                call.method,
                normalize_path(call.path),
            )
        ].append(call)

    for pair, calls in frontend_pairs.items():
        unique_sources = {
            (call.file, call.function)
            for call in calls
        }

        if len(unique_sources) > 1:
            issues.append(
                Issue(
                    severity="INFO",
                    code="SHARED_FRONTEND_ROUTE_CALL",
                    detail=(
                        f"{pair[0]} {pair[1]} is called "
                        f"from {len(unique_sources)} frontend "
                        "locations"
                    ),
                    evidence=", ".join(
                        (
                            f"{call.file}:"
                            f"{call.line}:"
                            f"{call.function}"
                        )
                        for call in calls
                    ),
                )
            )

    for route in runtime_routes:
        if (
            route.method in HTTP_METHODS
            and route.policy is None
            and not route.path.startswith(
                (
                    "/openapi",
                    "/docs",
                    "/redoc",
                )
            )
        ):
            issues.append(
                Issue(
                    severity="WARNING",
                    code="ROUTE_WITHOUT_POLICY",
                    detail=(
                        f"{route.method} {route.path} has no "
                        "resolved route policy"
                    ),
                    evidence=(
                        f"{route.endpoint_module}."
                        f"{route.endpoint_name}"
                    ),
                )
            )

    adjacency: dict[str, list[str]] = defaultdict(list)

    for edge in edges.values():
        adjacency[edge.source].append(
            edge.destination
        )

    cycles = find_cycles(adjacency)

    for cycle in cycles:
        issues.append(
            Issue(
                severity="ERROR",
                code="FLOW_CYCLE",
                detail="Cycle detected in flow graph",
                evidence=" -> ".join(cycle),
            )
        )

    reachable: set[str] = set()
    queue = deque(
        node_id
        for node_id, node in nodes.items()
        if node.category in {
            "frontend",
            "application",
        }
    )

    while queue:
        current = queue.popleft()

        if current in reachable:
            continue

        reachable.add(current)
        queue.extend(
            adjacency.get(current, [])
        )

    for node_id, node in nodes.items():
        if (
            node.category
            in {
                "service",
                "repository",
                "database",
                "dependency",
            }
            and node_id not in reachable
        ):
            issues.append(
                Issue(
                    severity="WARNING",
                    code="ORPHAN_FLOW_NODE",
                    detail=(
                        f"{node.category} node is not "
                        "reachable from frontend or app root: "
                        f"{node.label}"
                    ),
                    evidence=node.file,
                )
            )

    return issues


def find_cycles(
    adjacency: dict[str, list[str]],
) -> list[list[str]]:
    cycles: list[list[str]] = []
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def walk(node: str) -> None:
        if node in visiting:
            try:
                start = stack.index(node)
            except ValueError:
                return

            cycle = stack[start:] + [node]

            if cycle not in cycles:
                cycles.append(cycle)

            return

        if node in visited:
            return

        visiting.add(node)
        stack.append(node)

        for destination in adjacency.get(
            node,
            [],
        ):
            walk(destination)

        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for node in sorted(adjacency):
        walk(node)

    return cycles


def escape_dot(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
    )


def write_dot(
    nodes: dict[str, Node],
    edges: dict[tuple[str, str, str], Edge],
) -> None:
    lines = [
        "digraph NeuroVestFlow {",
        '  graph [bgcolor="#020617", rankdir=LR, '
        'splines=ortho, nodesep=0.55, ranksep=1.05, '
        'pad=0.4, fontname="DejaVu Sans"];',
        '  node [shape=box, style="rounded,filled", '
        'fontname="DejaVu Sans", fontsize=10, '
        'fontcolor="#f8fafc", color="#334155", '
        'penwidth=1.4, margin="0.13,0.09"];',
        '  edge [fontname="DejaVu Sans", fontsize=8, '
        'fontcolor="#cbd5e1", color="#64748b", '
        'arrowsize=0.65, penwidth=1.2];',
    ]

    categories: dict[str, list[Node]] = defaultdict(list)

    for node in nodes.values():
        categories[node.category].append(node)

    for category in sorted(categories):
        lines.append(
            f'  subgraph "cluster_{escape_dot(category)}" {{'
        )
        lines.append(
            f'    label="{escape_dot(category.upper())}";'
        )
        lines.append(
            '    color="#1e293b"; '
            'fontcolor="#94a3b8"; '
            'style="rounded,dashed";'
        )

        for node in sorted(
            categories[category],
            key=lambda item: item.label,
        ):
            color = CATEGORY_COLORS.get(
                category,
                CATEGORY_COLORS["unknown"],
            )

            tooltip_parts = [
                node.file or "",
                node.symbol or "",
            ]

            tooltip = " | ".join(
                part
                for part in tooltip_parts
                if part
            )

            lines.append(
                (
                    f'    "{escape_dot(node.node_id)}" '
                    f'[label="{escape_dot(node.label)}", '
                    f'fillcolor="{color}33", '
                    f'color="{color}", '
                    f'tooltip="{escape_dot(tooltip)}"];'
                )
            )

        lines.append("  }")

    for edge in sorted(
        edges.values(),
        key=lambda item: (
            item.source,
            item.destination,
            item.relationship,
        ),
    ):
        style = "solid"
        color = "#64748b"
        penwidth = "1.2"

        if edge.relationship == "HTTP_CALL":
            color = "#facc15"
            penwidth = "2.4"

        elif edge.relationship == "DEPENDS":
            color = "#c084fc"
            style = "dashed"

        elif edge.relationship == "CALLS":
            color = "#fb923c"

        elif edge.relationship == "MOUNTS":
            color = "#34d399"
            penwidth = "1.8"

        if edge.status in {
            "AMBIGUOUS",
            "BROKEN",
        }:
            color = "#ef4444"
            penwidth = "2.6"

        lines.append(
            (
                f'  "{escape_dot(edge.source)}" -> '
                f'"{escape_dot(edge.destination)}" '
                f'[label="{escape_dot(edge.relationship)}", '
                f'color="{color}", '
                f'style="{style}", '
                f'penwidth={penwidth}, '
                f'tooltip="{escape_dot(edge.evidence or "")}"];'
            )
        )

    lines.append("}")

    DOT_OUTPUT.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def render_svg() -> tuple[bool, str]:
    dot_binary = shutil.which("dot")

    if not dot_binary:
        return (
            False,
            "Graphviz dot is unavailable. "
            "Install with: sudo apt install graphviz",
        )

    result = subprocess.run(
        [
            dot_binary,
            "-Tsvg",
            str(DOT_OUTPUT),
            "-o",
            str(SVG_OUTPUT),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    if result.returncode != 0:
        return (
            False,
            result.stderr.strip()
            or "Graphviz rendering failed",
        )

    return True, "SVG generated"


def format_flow(flow: dict[str, Any]) -> list[str]:
    frontend = flow["frontend"]

    lines = [
        (
            f"{frontend['method']} "
            f"{frontend['path']}"
        ),
        (
            f"  Frontend: {frontend['file']}:"
            f"{frontend['line']} "
            f"({frontend['function']})"
        ),
        f"  Status: {flow['status']}",
    ]

    hops_by_number: dict[
        int,
        list[dict[str, Any]],
    ] = defaultdict(list)

    for hop in flow["hops"]:
        hops_by_number[int(hop["hop"])].append(hop)

    for number in sorted(hops_by_number):
        for hop in hops_by_number[number]:
            lines.append(
                (
                    f"  Hop {number}: "
                    f"[{hop['category']}] "
                    f"{hop['label'].replace(chr(10), ' -> ')}"
                )
            )

    return lines


def write_text_report(
    *,
    frontend_calls: list[FrontendCall],
    runtime_routes: list[RuntimeRoute],
    nodes: dict[str, Node],
    edges: dict[tuple[str, str, str], Edge],
    flows: list[dict[str, Any]],
    issues: list[Issue],
    runtime_metadata: dict[str, Any],
) -> None:
    blocking = [
        issue
        for issue in issues
        if issue.severity == "BLOCKING"
    ]

    errors = [
        issue
        for issue in issues
        if issue.severity == "ERROR"
    ]

    warnings = [
        issue
        for issue in issues
        if issue.severity == "WARNING"
    ]

    lines = [
        "=" * 78,
        "NEUROVEST STANDALONE FLOW INSPECTOR",
        "=" * 78,
        "",
        "SUMMARY",
        f"- Frontend calls: {len(frontend_calls)}",
        f"- Runtime routes: {len(runtime_routes)}",
        f"- Graph nodes: {len(nodes)}",
        f"- Graph edges: {len(edges)}",
        f"- Recorded flows: {len(flows)}",
        f"- Blocking issues: {len(blocking)}",
        f"- Errors: {len(errors)}",
        f"- Warnings: {len(warnings)}",
        "",
        "SAFETY",
        "- Repository inspection: READ ONLY",
        "- Database mutation: NO",
        "- Service restart: NO",
        "- Broker activity: NO",
        "- Frontend modification: NO",
        "- Backend source modification: NO",
        "",
        "RUNTIME APP",
        json.dumps(
            runtime_metadata,
            indent=2,
            sort_keys=True,
        ),
        "",
        "=" * 78,
        "FRONTEND TO BACKEND HOP RECORD",
        "=" * 78,
    ]

    if not flows:
        lines.append(
            "No literal frontend API calls were discovered."
        )

    for index, flow in enumerate(flows, start=1):
        lines.extend(
            [
                "",
                f"FLOW {index}",
                "-" * 78,
                *format_flow(flow),
            ]
        )

    lines.extend(
        [
            "",
            "=" * 78,
            "RUNTIME ROUTES",
            "=" * 78,
        ]
    )

    for route in sorted(
        runtime_routes,
        key=lambda item: (
            item.path,
            item.method,
            item.endpoint_name,
        ),
    ):
        lines.extend(
            [
                "",
                f"{route.method} {route.path}",
                (
                    f"  Endpoint: "
                    f"{route.endpoint_module}."
                    f"{route.endpoint_name}"
                ),
                f"  File: {route.endpoint_file}",
                f"  Policy: {route.policy}",
                "  Dependencies:",
            ]
        )

        if not route.dependencies:
            lines.append("    - none")

        for dependency in route.dependencies:
            lines.append(
                (
                    "    - "
                    f"{dependency['qualified']} "
                    f"({dependency['file']})"
                )
            )

    lines.extend(
        [
            "",
            "=" * 78,
            "OVERLAPS, BREAKS, AND RISKS",
            "=" * 78,
        ]
    )

    if not issues:
        lines.append(
            "No blocking, broken, duplicate, ambiguous, "
            "cyclic, or unclassified flow issues found."
        )

    for issue in sorted(
        issues,
        key=lambda item: (
            item.severity,
            item.code,
            item.detail,
        ),
    ):
        lines.extend(
            [
                "",
                f"[{issue.severity}] {issue.code}",
                f"  {issue.detail}",
            ]
        )

        if issue.evidence:
            lines.append(
                f"  Evidence: {issue.evidence}"
            )

    TEXT_OUTPUT.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def write_html_report(
    *,
    payload: dict[str, Any],
    svg_generated: bool,
) -> None:
    summary = payload["summary"]
    issues = payload["issues"]
    flows = payload["flows"]
    routes = payload["runtime_routes"]

    issue_cards = []

    for issue in issues:
        issue_cards.append(
            f"""
            <article class="issue {html.escape(issue['severity'].lower())}">
              <header>
                <strong>{html.escape(issue['severity'])}</strong>
                <code>{html.escape(issue['code'])}</code>
              </header>
              <p>{html.escape(issue['detail'])}</p>
              <pre>{html.escape(issue.get('evidence') or '')}</pre>
            </article>
            """
        )

    flow_sections = []

    for index, flow in enumerate(flows, start=1):
        frontend = flow["frontend"]

        hop_rows = []

        for hop in sorted(
            flow["hops"],
            key=lambda item: (
                int(item["hop"]),
                item["category"],
                item["label"],
            ),
        ):
            hop_rows.append(
                f"""
                <div class="hop">
                  <span class="hop-number">Hop {int(hop['hop'])}</span>
                  <span class="category">{html.escape(hop['category'])}</span>
                  <strong>{html.escape(hop['label'])}</strong>
                </div>
                """
            )

        flow_sections.append(
            f"""
            <details class="flow" {'open' if index <= 5 else ''}>
              <summary>
                <span>Flow {index}</span>
                <strong>{html.escape(frontend['method'])}
                {html.escape(frontend['path'])}</strong>
                <em>{html.escape(flow['status'])}</em>
              </summary>
              <p>
                {html.escape(frontend['file'])}:
                {int(frontend['line'])}
                — {html.escape(frontend['function'])}
              </p>
              <div class="hops">
                {''.join(hop_rows)}
              </div>
            </details>
            """
        )

    route_rows = []

    for route in routes:
        route_rows.append(
            f"""
            <tr>
              <td>{html.escape(route['method'])}</td>
              <td><code>{html.escape(route['path'])}</code></td>
              <td>{html.escape(route['endpoint_module'])}.{
                  html.escape(route['endpoint_name'])
              }</td>
              <td>{html.escape(str(route.get('policy')))}</td>
              <td>{len(route.get('dependencies', []))}</td>
            </tr>
            """
        )

    svg_panel = (
        """
        <section class="panel graph-panel">
          <h2>Architecture Flow Graph</h2>
          <object
            data="neurovest_flow_latest.svg"
            type="image/svg+xml"
            class="graph-object">
          </object>
        </section>
        """
        if svg_generated
        else """
        <section class="panel">
          <h2>Graphviz SVG unavailable</h2>
          <p>
            The DOT graph was generated. Install Graphviz with:
          </p>
          <pre>sudo apt install graphviz</pre>
        </section>
        """
    )

    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta
    name="viewport"
    content="width=device-width, initial-scale=1">
  <title>NeuroVest Flow Inspector</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #020617;
      --panel: #071126;
      --border: #1e293b;
      --text: #e2e8f0;
      --muted: #94a3b8;
      --cyan: #22d3ee;
      --yellow: #facc15;
      --green: #34d399;
      --red: #f87171;
      --orange: #fb923c;
      --purple: #c084fc;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family:
        Inter,
        ui-sans-serif,
        system-ui,
        sans-serif;
    }}

    header.page-header {{
      position: sticky;
      top: 0;
      z-index: 10;
      padding: 18px 24px;
      border-bottom: 1px solid var(--border);
      background: rgba(2, 6, 23, 0.96);
      backdrop-filter: blur(12px);
    }}

    header.page-header h1 {{
      margin: 0;
      color: var(--cyan);
      font-family: monospace;
      font-size: 18px;
    }}

    header.page-header p {{
      margin: 8px 0 0;
      color: var(--muted);
    }}

    main {{
      padding: 20px;
      display: grid;
      gap: 18px;
    }}

    .summary {{
      display: grid;
      grid-template-columns:
        repeat(auto-fit, minmax(160px, 1fr));
      gap: 12px;
    }}

    .metric,
    .panel,
    .flow,
    .issue {{
      border: 1px solid var(--border);
      background: var(--panel);
      border-radius: 12px;
    }}

    .metric {{
      padding: 16px;
    }}

    .metric strong {{
      display: block;
      font-size: 26px;
      color: var(--cyan);
    }}

    .metric span {{
      color: var(--muted);
    }}

    .panel {{
      padding: 18px;
      overflow: auto;
    }}

    .graph-panel {{
      min-height: 780px;
    }}

    .graph-object {{
      display: block;
      width: 100%;
      min-height: 740px;
      border: 1px solid var(--border);
      background: #020617;
    }}

    h2 {{
      margin-top: 0;
      color: var(--yellow);
      font-family: monospace;
    }}

    .flow {{
      margin: 10px 0;
      padding: 12px;
    }}

    .flow summary {{
      cursor: pointer;
      display: flex;
      gap: 14px;
      align-items: center;
    }}

    .flow summary em {{
      margin-left: auto;
      color: var(--yellow);
    }}

    .flow p {{
      color: var(--muted);
      font-family: monospace;
    }}

    .hops {{
      display: grid;
      gap: 7px;
    }}

    .hop {{
      display: grid;
      grid-template-columns: 72px 110px 1fr;
      gap: 12px;
      padding: 9px;
      border-left: 3px solid var(--purple);
      background: #020617;
    }}

    .hop-number {{
      color: var(--yellow);
      font-family: monospace;
    }}

    .category {{
      color: var(--cyan);
      font-family: monospace;
    }}

    .issues {{
      display: grid;
      gap: 10px;
    }}

    .issue {{
      padding: 14px;
    }}

    .issue header {{
      display: flex;
      gap: 12px;
      align-items: center;
    }}

    .issue.blocking,
    .issue.error {{
      border-color: var(--red);
    }}

    .issue.warning {{
      border-color: var(--orange);
    }}

    .issue.info {{
      border-color: var(--cyan);
    }}

    .issue pre {{
      white-space: pre-wrap;
      color: var(--muted);
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
    }}

    th,
    td {{
      text-align: left;
      padding: 10px;
      border-bottom: 1px solid var(--border);
      vertical-align: top;
    }}

    th {{
      color: var(--cyan);
      position: sticky;
      top: 0;
      background: var(--panel);
    }}

    code,
    pre {{
      font-family:
        "JetBrains Mono",
        "Fira Code",
        monospace;
    }}
  </style>
</head>
<body>
  <header class="page-header">
    <h1>NEUROVEST STANDALONE FLOW INSPECTOR</h1>
    <p>
      Read-only frontend → backend → dependency → service →
      repository verification.
    </p>
  </header>

  <main>
    <section class="summary">
      <div class="metric">
        <strong>{summary['frontend_calls']}</strong>
        <span>Frontend calls</span>
      </div>
      <div class="metric">
        <strong>{summary['runtime_routes']}</strong>
        <span>Runtime routes</span>
      </div>
      <div class="metric">
        <strong>{summary['nodes']}</strong>
        <span>Graph nodes</span>
      </div>
      <div class="metric">
        <strong>{summary['edges']}</strong>
        <span>Graph edges</span>
      </div>
      <div class="metric">
        <strong>{summary['blocking_issues']}</strong>
        <span>Blocking issues</span>
      </div>
      <div class="metric">
        <strong>{summary['errors']}</strong>
        <span>Errors</span>
      </div>
    </section>

    {svg_panel}

    <section class="panel">
      <h2>Frontend-to-Backend Hop Records</h2>
      {''.join(flow_sections) or '<p>No frontend calls found.</p>'}
    </section>

    <section class="panel">
      <h2>Runtime Routes</h2>
      <table>
        <thead>
          <tr>
            <th>Method</th>
            <th>Path</th>
            <th>Endpoint</th>
            <th>Policy</th>
            <th>Dependencies</th>
          </tr>
        </thead>
        <tbody>
          {''.join(route_rows)}
        </tbody>
      </table>
    </section>

    <section class="panel">
      <h2>Overlaps, Breaks, and Risks</h2>
      <div class="issues">
        {''.join(issue_cards) or '<p>No issues detected.</p>'}
      </div>
    </section>
  </main>
</body>
</html>
"""

    HTML_OUTPUT.write_text(
        document,
        encoding="utf-8",
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect NeuroVest frontend-to-backend flows "
            "without modifying application state."
        )
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Return a non-zero exit code when blocking "
            "issues or errors are found."
        ),
    )

    parser.add_argument(
        "--no-svg",
        action="store_true",
        help="Skip Graphviz SVG rendering.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 72)
    print("NEUROVEST STANDALONE FLOW INSPECTOR")
    print("=" * 72)
    print("Repository:", ROOT)
    print("Inspection mode: READ ONLY")
    print()

    print("[1/7] Indexing backend Python symbols...")
    functions, by_simple_name, parse_issues = (
        parse_python_inventory()
    )

    print(
        f"      Functions indexed: {len(functions)}"
    )

    print("[2/7] Discovering frontend API calls...")
    frontend_calls = discover_frontend_calls()

    print(
        f"      Frontend calls found: "
        f"{len(frontend_calls)}"
    )

    print("[3/7] Importing FastAPI app read-only...")
    runtime_routes, runtime_issues, runtime_metadata = (
        discover_runtime_routes()
    )

    print(
        f"      Runtime routes found: "
        f"{len(runtime_routes)}"
    )

    print("[4/7] Building hop graph...")
    nodes, edges, flows, graph_issues = (
        build_flow_graph(
            frontend_calls,
            runtime_routes,
            functions,
            by_simple_name,
        )
    )

    print(f"      Nodes: {len(nodes)}")
    print(f"      Edges: {len(edges)}")
    print(f"      Flows: {len(flows)}")

    print("[5/7] Checking overlaps and ambiguity...")
    overlap_issues = inspect_overlaps(
        frontend_calls,
        runtime_routes,
        nodes,
        edges,
    )

    issues = [
        *parse_issues,
        *runtime_issues,
        *graph_issues,
        *overlap_issues,
    ]

    blocking_issues = [
        issue
        for issue in issues
        if issue.severity == "BLOCKING"
    ]

    errors = [
        issue
        for issue in issues
        if issue.severity == "ERROR"
    ]

    warnings = [
        issue
        for issue in issues
        if issue.severity == "WARNING"
    ]

    payload = {
        "schema": "neurovest.flow_inspector.v1",
        "repository": str(ROOT),
        "read_only": True,
        "summary": {
            "frontend_calls": len(frontend_calls),
            "runtime_routes": len(runtime_routes),
            "nodes": len(nodes),
            "edges": len(edges),
            "flows": len(flows),
            "blocking_issues": len(blocking_issues),
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "runtime": runtime_metadata,
        "frontend_calls": [
            asdict(call)
            for call in frontend_calls
        ],
        "runtime_routes": [
            asdict(route)
            for route in runtime_routes
        ],
        "nodes": [
            asdict(node)
            for node in sorted(
                nodes.values(),
                key=lambda item: item.node_id,
            )
        ],
        "edges": [
            asdict(edge)
            for edge in sorted(
                edges.values(),
                key=lambda item: (
                    item.source,
                    item.destination,
                    item.relationship,
                ),
            )
        ],
        "flows": flows,
        "issues": [
            asdict(issue)
            for issue in issues
        ],
        "safety": {
            "database_mutated": False,
            "services_restarted": False,
            "broker_activity": False,
            "frontend_modified": False,
            "backend_source_modified": False,
        },
    }

    print("[6/7] Writing reports...")

    JSON_OUTPUT.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    write_text_report(
        frontend_calls=frontend_calls,
        runtime_routes=runtime_routes,
        nodes=nodes,
        edges=edges,
        flows=flows,
        issues=issues,
        runtime_metadata=runtime_metadata,
    )

    write_dot(
        nodes,
        edges,
    )

    svg_generated = False
    svg_message = "SVG generation skipped"

    if not args.no_svg:
        svg_generated, svg_message = render_svg()

    write_html_report(
        payload=payload,
        svg_generated=svg_generated,
    )

    print("[7/7] Complete")
    print()
    print("Summary:")
    print(
        json.dumps(
            payload["summary"],
            indent=2,
            sort_keys=True,
        )
    )
    print()
    print("Graphviz:", svg_message)
    print()
    print("Outputs:")
    print(" ", relative(JSON_OUTPUT))
    print(" ", relative(TEXT_OUTPUT))
    print(" ", relative(DOT_OUTPUT))

    if svg_generated:
        print(" ", relative(SVG_OUTPUT))

    print(" ", relative(HTML_OUTPUT))
    print()
    print("Database mutated: NO")
    print("Services restarted: NO")
    print("Broker activity: NO")
    print("Application source modified: NO")

    if args.strict and (
        blocking_issues
        or errors
    ):
        print()
        print(
            "STRICT RESULT: FAILED — blocking "
            "or broken flows were detected."
        )
        return 1

    print()
    print(
        "RESULT: REPORT GENERATED"
        + (
            " WITH ISSUES"
            if issues
            else " — NO ISSUES DETECTED"
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
