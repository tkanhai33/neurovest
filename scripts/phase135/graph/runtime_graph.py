#!/usr/bin/env python3

"""
Phase 135 blind runtime graph discovery.

Performs read-only static inspection for observable runtime signals:

- Python and shell entrypoints
- FastAPI application construction
- FastAPI router registration
- HTTP route declarations
- Next.js pages and route handlers
- subprocess and shell execution
- scheduler and background-task registration
- event publication and subscription
- database initialization
- external HTTP access
- runtime environment access
- executable main guards
- static reachability from detected entrypoints

This stage does not execute application code and does not assume the intended
NeuroVest architecture.
"""

from __future__ import annotations

import ast
import re
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any

from scripts.phase135.utils.filesystem import safe_read_text


PYTHON_SUFFIXES = {".py"}
WEB_SUFFIXES = {".js", ".jsx", ".mjs", ".ts", ".tsx"}
SHELL_SUFFIXES = {".sh"}

ARCHIVE_MARKERS = {
    "archive",
    "archives",
    "architecture_backup",
    "backup",
    "backups",
    "deprecated",
    "legacy",
    "old",
    "quarantine",
    "quarantine_artifacts",
}

GENERATED_MARKERS = {
    ".next",
    "build",
    "coverage",
    "dist",
    "generated",
    "htmlcov",
    "node_modules",
    "output",
    "outputs",
    "reports",
    "runtime",
}

TOOLING_MARKERS = {
    "bin",
    "script",
    "scripts",
    "tool",
    "tools",
}

HTTP_METHODS = {
    "delete",
    "get",
    "head",
    "options",
    "patch",
    "post",
    "put",
    "trace",
    "websocket",
}

NEXT_ROUTE_EXPORTS = {
    "DELETE",
    "GET",
    "HEAD",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
}

RUNTIME_CALL_PATTERNS = {
    "subprocess_execution": {
        "subprocess.call",
        "subprocess.check_call",
        "subprocess.check_output",
        "subprocess.Popen",
        "subprocess.run",
        "os.popen",
        "os.spawnl",
        "os.spawnlp",
        "os.spawnv",
        "os.spawnvp",
        "os.system",
    },
    "thread_or_process_start": {
        "multiprocessing.Process",
        "threading.Thread",
        "Thread",
        "Process",
    },
    "async_task_creation": {
        "asyncio.create_task",
        "asyncio.ensure_future",
        "create_task",
    },
    "background_task_registration": {
        "add_task",
        "BackgroundTasks",
    },
    "scheduler_registration": {
        "add_job",
        "schedule.every",
        "scheduler.add_job",
        "APScheduler",
    },
    "event_publication": {
        "emit",
        "publish",
        "send_event",
        "dispatch",
    },
    "event_subscription": {
        "subscribe",
        "register_handler",
        "add_listener",
        "on",
    },
    "database_initialization": {
        "create_engine",
        "create_async_engine",
        "sessionmaker",
        "async_sessionmaker",
    },
    "external_http_access": {
        "requests.delete",
        "requests.get",
        "requests.patch",
        "requests.post",
        "requests.put",
        "httpx.AsyncClient",
        "httpx.Client",
        "httpx.delete",
        "httpx.get",
        "httpx.patch",
        "httpx.post",
        "httpx.put",
        "aiohttp.ClientSession",
    },
}

SHELL_EXECUTION_PATTERN = re.compile(
    r"^\s*(?:"
    r"python(?:3)?\s+|"
    r"uvicorn\s+|"
    r"gunicorn\s+|"
    r"npm\s+(?:run|start)|"
    r"pnpm\s+(?:run|start)|"
    r"yarn\s+(?:run|start)|"
    r"node\s+|"
    r"bash\s+|"
    r"sh\s+"
    r")(.+)$"
)

NEXT_FETCH_PATTERN = re.compile(
    r"\bfetch\s*\(\s*([\"'`])(?P<url>.+?)\1",
    re.MULTILINE,
)

NEXT_ROUTE_EXPORT_PATTERN = re.compile(
    r"\bexport\s+(?:async\s+)?function\s+"
    r"(?P<method>GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\b"
)

NEXT_ROUTE_CONST_PATTERN = re.compile(
    r"\bexport\s+const\s+"
    r"(?P<method>GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\b"
)

ENV_ACCESS_PATTERN = re.compile(
    r"\b(?:os\.environ(?:\.get)?|os\.getenv|process\.env)\b"
)


class RuntimeGraphDiscovery:
    """
    Discover statically observable runtime paths without executing code.
    """

    def __init__(
        self,
        repository_root: Path,
        discovery: dict[str, Any],
        dependency_mapping: dict[str, Any],
        import_graph: dict[str, Any],
    ) -> None:
        self.repository_root = repository_root.resolve()
        self.discovery = discovery
        self.dependency_mapping = dependency_mapping
        self.import_graph = import_graph

        self.files: list[dict[str, Any]] = list(
            discovery.get("files", [])
        )

        self.file_index = {
            record["path"]: record
            for record in self.files
        }

        self.source_paths = {
            record["path"]
            for record in self.files
            if record.get("is_source")
        }

        self.active_dependency_edges = [
            edge
            for edge in import_graph.get("file_graph", {}).get("edges", [])
            if edge.get("classification") == "active"
        ]

    def discover(self) -> dict[str, Any]:
        python_evidence = self._scan_python_files()
        web_evidence = self._scan_web_files()
        shell_evidence = self._scan_shell_files()

        entrypoints = self._merge_entrypoints(
            python_evidence["entrypoints"],
            web_evidence["entrypoints"],
            shell_evidence["entrypoints"],
        )

        route_nodes = (
            python_evidence["routes"]
            + web_evidence["routes"]
        )

        runtime_signals = (
            python_evidence["runtime_signals"]
            + web_evidence["runtime_signals"]
            + shell_evidence["runtime_signals"]
        )

        runtime_edges = self._build_runtime_edges(
            python_evidence=python_evidence,
            web_evidence=web_evidence,
            shell_evidence=shell_evidence,
        )

        reachability = self._build_entrypoint_reachability(
            entrypoints=entrypoints,
        )

        runtime_cycles = self._find_runtime_cycles(runtime_edges)

        active_entrypoints = [
            item
            for item in entrypoints
            if item["classification"] == "active"
        ]

        non_active_entrypoints = [
            item
            for item in entrypoints
            if item["classification"] != "active"
        ]

        signal_counts = Counter(
            signal["signal_type"]
            for signal in runtime_signals
        )

        route_counts = Counter(
            route["framework"]
            for route in route_nodes
        )

        unreachable_active_files = self._discover_unreachable_active_files(
            reachability
        )

        return {
            "discovery_mode": "static_evidence_based",
            "application_executed": False,
            "architecture_assumed": False,
            "summary": {
                "entrypoints": len(entrypoints),
                "active_entrypoints": len(active_entrypoints),
                "non_active_entrypoints": len(non_active_entrypoints),
                "routes": len(route_nodes),
                "runtime_signals": len(runtime_signals),
                "runtime_edges": len(runtime_edges),
                "runtime_cycles": len(runtime_cycles),
                "reachable_files": reachability["reachable_file_count"],
                "unreachable_active_files": len(unreachable_active_files),
                "parse_errors": (
                    len(python_evidence["parse_errors"])
                    + len(web_evidence["parse_errors"])
                    + len(shell_evidence["parse_errors"])
                ),
            },
            "entrypoints": entrypoints,
            "active_entrypoints": active_entrypoints,
            "non_active_entrypoints": non_active_entrypoints,
            "routes": sorted(
                route_nodes,
                key=lambda item: (
                    item["framework"],
                    item["path"],
                    item.get("method", ""),
                    item["source"],
                ),
            ),
            "runtime_signals": sorted(
                runtime_signals,
                key=lambda item: (
                    item["signal_type"],
                    item["source"],
                    item.get("line") or 0,
                ),
            ),
            "runtime_edges": runtime_edges,
            "runtime_cycles": runtime_cycles,
            "reachability": reachability,
            "unreachable_active_files": unreachable_active_files,
            "signal_counts": dict(
                sorted(
                    signal_counts.items(),
                    key=lambda item: (-item[1], item[0]),
                )
            ),
            "route_counts": dict(
                sorted(route_counts.items())
            ),
            "python": python_evidence,
            "javascript_or_typescript": web_evidence,
            "shell": shell_evidence,
            "limitations": [
                (
                    "Runtime discovery is static and does not execute imports, "
                    "framework startup hooks, schedulers, workers, or services."
                ),
                (
                    "Dependency-injected calls, reflection, plugin loading, "
                    "configuration-driven routing, and dynamically constructed "
                    "commands may not be fully resolved."
                ),
                (
                    "Reachability means statically connected by detected imports; "
                    "it does not prove the code executes in production."
                ),
                (
                    "No intended NeuroVest runtime ownership or forbidden-call "
                    "contract has been enforced."
                ),
            ],
        }

    def _scan_python_files(self) -> dict[str, Any]:
        entrypoints: list[dict[str, Any]] = []
        routes: list[dict[str, Any]] = []
        runtime_signals: list[dict[str, Any]] = []
        router_registrations: list[dict[str, Any]] = []
        app_constructions: list[dict[str, Any]] = []
        parse_errors: list[dict[str, Any]] = []

        for path_string in sorted(self.source_paths):
            if Path(path_string).suffix.lower() not in PYTHON_SUFFIXES:
                continue

            absolute_path = self.repository_root / path_string
            text = safe_read_text(absolute_path, max_bytes=2_000_000)

            if text is None:
                parse_errors.append(
                    {
                        "path": path_string,
                        "error": "file_unreadable_or_too_large",
                    }
                )
                continue

            try:
                tree = ast.parse(text, filename=path_string)
            except SyntaxError as exc:
                parse_errors.append(
                    {
                        "path": path_string,
                        "error": (
                            f"SyntaxError line {exc.lineno}: {exc.msg}"
                        ),
                    }
                )
                continue

            classification = self._classify_path(path_string)

            if self._has_main_guard(tree):
                entrypoints.append(
                    {
                        "source": path_string,
                        "entrypoint_type": "python_main_guard",
                        "classification": classification,
                        "evidence": '__name__ == "__main__"',
                    }
                )

            if Path(path_string).name in {
                "main.py",
                "app.py",
                "server.py",
                "manage.py",
                "wsgi.py",
                "asgi.py",
                "__main__.py",
            }:
                entrypoints.append(
                    {
                        "source": path_string,
                        "entrypoint_type": "python_entrypoint_filename",
                        "classification": classification,
                        "evidence": Path(path_string).name,
                    }
                )

            aliases = self._build_python_alias_index(tree)

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    callable_name = self._callable_name(node.func)
                    canonical_name = self._canonical_call_name(
                        callable_name,
                        aliases,
                    )

                    if canonical_name in {"FastAPI", "fastapi.FastAPI"}:
                        app_constructions.append(
                            {
                                "source": path_string,
                                "framework": "FastAPI",
                                "callable": canonical_name,
                                "line": getattr(node, "lineno", None),
                                "classification": classification,
                            }
                        )

                        entrypoints.append(
                            {
                                "source": path_string,
                                "entrypoint_type": "fastapi_application",
                                "classification": classification,
                                "evidence": canonical_name,
                            }
                        )

                    if canonical_name in {
                        "APIRouter",
                        "fastapi.APIRouter",
                    }:
                        runtime_signals.append(
                            {
                                "source": path_string,
                                "signal_type": "router_construction",
                                "callable": canonical_name,
                                "line": getattr(node, "lineno", None),
                                "classification": classification,
                            }
                        )

                    if canonical_name.endswith(".include_router"):
                        registration = {
                            "source": path_string,
                            "signal_type": "router_registration",
                            "callable": canonical_name,
                            "router_argument": self._safe_ast_value(
                                node.args[0]
                                if node.args
                                else None
                            ),
                            "prefix": self._keyword_value(
                                node,
                                "prefix",
                            ),
                            "line": getattr(node, "lineno", None),
                            "classification": classification,
                        }

                        router_registrations.append(registration)
                        runtime_signals.append(registration)

                    matched_signal = self._match_runtime_call(
                        canonical_name
                    )

                    if matched_signal:
                        runtime_signals.append(
                            {
                                "source": path_string,
                                "signal_type": matched_signal,
                                "callable": canonical_name,
                                "arguments": [
                                    self._safe_ast_value(argument)
                                    for argument in node.args[:5]
                                ],
                                "line": getattr(node, "lineno", None),
                                "classification": classification,
                            }
                        )

                route = self._extract_fastapi_route(
                    node=node,
                    path_string=path_string,
                    classification=classification,
                )

                if route:
                    routes.append(route)

            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute):
                    attribute_name = self._attribute_name(node)

                    if attribute_name in {
                        "os.environ",
                        "os.environ.get",
                        "os.getenv",
                    }:
                        runtime_signals.append(
                            {
                                "source": path_string,
                                "signal_type": "environment_access",
                                "callable": attribute_name,
                                "line": getattr(node, "lineno", None),
                                "classification": classification,
                            }
                        )

        return {
            "entrypoints": self._deduplicate_records(
                entrypoints,
                keys=("source", "entrypoint_type", "evidence"),
            ),
            "routes": self._deduplicate_records(
                routes,
                keys=("source", "method", "path", "handler"),
            ),
            "runtime_signals": self._deduplicate_records(
                runtime_signals,
                keys=("source", "signal_type", "callable", "line"),
            ),
            "router_registrations": router_registrations,
            "application_constructions": app_constructions,
            "parse_errors": parse_errors,
        }

    def _scan_web_files(self) -> dict[str, Any]:
        entrypoints: list[dict[str, Any]] = []
        routes: list[dict[str, Any]] = []
        runtime_signals: list[dict[str, Any]] = []
        parse_errors: list[dict[str, Any]] = []

        for path_string in sorted(self.source_paths):
            suffix = Path(path_string).suffix.lower()

            if suffix not in WEB_SUFFIXES:
                continue

            absolute_path = self.repository_root / path_string
            text = safe_read_text(absolute_path, max_bytes=2_000_000)

            if text is None:
                parse_errors.append(
                    {
                        "path": path_string,
                        "error": "file_unreadable_or_too_large",
                    }
                )
                continue

            classification = self._classify_path(path_string)
            path = Path(path_string)

            if self._is_next_page(path):
                route_path = self._next_route_path(path, is_api=False)

                entrypoints.append(
                    {
                        "source": path_string,
                        "entrypoint_type": "nextjs_page",
                        "classification": classification,
                        "evidence": route_path,
                    }
                )

                routes.append(
                    {
                        "source": path_string,
                        "framework": "Next.js",
                        "route_type": "page",
                        "method": "GET",
                        "path": route_path,
                        "handler": "default_page_component",
                        "classification": classification,
                    }
                )

            if self._is_next_route_handler(path):
                route_path = self._next_route_path(path, is_api=True)
                methods = set()

                for pattern in (
                    NEXT_ROUTE_EXPORT_PATTERN,
                    NEXT_ROUTE_CONST_PATTERN,
                ):
                    methods.update(
                        match.group("method")
                        for match in pattern.finditer(text)
                    )

                if not methods:
                    methods.add("UNKNOWN")

                entrypoints.append(
                    {
                        "source": path_string,
                        "entrypoint_type": "nextjs_route_handler",
                        "classification": classification,
                        "evidence": route_path,
                    }
                )

                for method in sorted(methods):
                    routes.append(
                        {
                            "source": path_string,
                            "framework": "Next.js",
                            "route_type": "route_handler",
                            "method": method,
                            "path": route_path,
                            "handler": method,
                            "classification": classification,
                        }
                    )

            for match in NEXT_FETCH_PATTERN.finditer(text):
                runtime_signals.append(
                    {
                        "source": path_string,
                        "signal_type": "external_or_internal_http_fetch",
                        "callable": "fetch",
                        "target": match.group("url"),
                        "line": self._line_number(text, match.start()),
                        "classification": classification,
                    }
                )

            for match in ENV_ACCESS_PATTERN.finditer(text):
                runtime_signals.append(
                    {
                        "source": path_string,
                        "signal_type": "environment_access",
                        "callable": match.group(0),
                        "line": self._line_number(text, match.start()),
                        "classification": classification,
                    }
                )

            if re.search(r"\bsetInterval\s*\(", text):
                runtime_signals.append(
                    {
                        "source": path_string,
                        "signal_type": "interval_scheduler",
                        "callable": "setInterval",
                        "line": None,
                        "classification": classification,
                    }
                )

            if re.search(r"\bsetTimeout\s*\(", text):
                runtime_signals.append(
                    {
                        "source": path_string,
                        "signal_type": "delayed_task",
                        "callable": "setTimeout",
                        "line": None,
                        "classification": classification,
                    }
                )

            if re.search(r"\bnew\s+Worker\s*\(", text):
                runtime_signals.append(
                    {
                        "source": path_string,
                        "signal_type": "worker_creation",
                        "callable": "Worker",
                        "line": None,
                        "classification": classification,
                    }
                )

        return {
            "entrypoints": self._deduplicate_records(
                entrypoints,
                keys=("source", "entrypoint_type", "evidence"),
            ),
            "routes": self._deduplicate_records(
                routes,
                keys=("source", "method", "path", "handler"),
            ),
            "runtime_signals": self._deduplicate_records(
                runtime_signals,
                keys=("source", "signal_type", "callable", "line"),
            ),
            "parse_errors": parse_errors,
        }

    def _scan_shell_files(self) -> dict[str, Any]:
        entrypoints: list[dict[str, Any]] = []
        runtime_signals: list[dict[str, Any]] = []
        parse_errors: list[dict[str, Any]] = []

        for path_string in sorted(self.source_paths):
            if Path(path_string).suffix.lower() not in SHELL_SUFFIXES:
                continue

            absolute_path = self.repository_root / path_string
            text = safe_read_text(absolute_path, max_bytes=2_000_000)

            if text is None:
                parse_errors.append(
                    {
                        "path": path_string,
                        "error": "file_unreadable_or_too_large",
                    }
                )
                continue

            classification = self._classify_path(path_string)

            if text.startswith("#!"):
                entrypoints.append(
                    {
                        "source": path_string,
                        "entrypoint_type": "shell_shebang",
                        "classification": classification,
                        "evidence": text.splitlines()[0],
                    }
                )

            for line_number, line in enumerate(
                text.splitlines(),
                start=1,
            ):
                stripped = line.strip()

                if (
                    not stripped
                    or stripped.startswith("#")
                    or stripped.startswith("echo ")
                    or stripped.startswith("printf ")
                ):
                    continue

                match = SHELL_EXECUTION_PATTERN.match(stripped)

                if match:
                    runtime_signals.append(
                        {
                            "source": path_string,
                            "signal_type": "shell_runtime_launch",
                            "callable": stripped.split()[0],
                            "command": stripped,
                            "line": line_number,
                            "classification": classification,
                        }
                    )

        return {
            "entrypoints": self._deduplicate_records(
                entrypoints,
                keys=("source", "entrypoint_type", "evidence"),
            ),
            "runtime_signals": self._deduplicate_records(
                runtime_signals,
                keys=("source", "signal_type", "command", "line"),
            ),
            "parse_errors": parse_errors,
        }

    def _build_runtime_edges(
        self,
        python_evidence: dict[str, Any],
        web_evidence: dict[str, Any],
        shell_evidence: dict[str, Any],
    ) -> list[dict[str, Any]]:
        edges: list[dict[str, Any]] = []

        for edge in self.active_dependency_edges:
            edges.append(
                {
                    "source": edge["source"],
                    "target": edge["target"],
                    "edge_type": "static_import",
                    "classification": "active",
                    "evidence": edge.get("dependencies", []),
                }
            )

        for registration in python_evidence["router_registrations"]:
            router_argument = registration.get("router_argument")

            if not router_argument:
                continue

            edges.append(
                {
                    "source": registration["source"],
                    "target": str(router_argument),
                    "edge_type": "router_registration",
                    "classification": registration["classification"],
                    "evidence": {
                        "prefix": registration.get("prefix"),
                        "line": registration.get("line"),
                    },
                }
            )

        for signal in (
            python_evidence["runtime_signals"]
            + web_evidence["runtime_signals"]
            + shell_evidence["runtime_signals"]
        ):
            target = (
                signal.get("target")
                or signal.get("command")
                or signal.get("callable")
            )

            if not target:
                continue

            edges.append(
                {
                    "source": signal["source"],
                    "target": str(target),
                    "edge_type": signal["signal_type"],
                    "classification": signal["classification"],
                    "evidence": {
                        "line": signal.get("line"),
                    },
                }
            )

        return self._deduplicate_records(
            edges,
            keys=("source", "target", "edge_type", "classification"),
        )

    def _build_entrypoint_reachability(
        self,
        entrypoints: list[dict[str, Any]],
    ) -> dict[str, Any]:
        adjacency: dict[str, set[str]] = defaultdict(set)

        for edge in self.active_dependency_edges:
            adjacency[edge["source"]].add(edge["target"])

        entrypoint_paths = sorted(
            {
                item["source"]
                for item in entrypoints
                if item["classification"] == "active"
            }
        )

        reachable_by_entrypoint: list[dict[str, Any]] = []
        all_reachable: set[str] = set()

        for entrypoint in entrypoint_paths:
            visited: set[str] = set()
            queue: deque[str] = deque([entrypoint])

            while queue:
                node = queue.popleft()

                if node in visited:
                    continue

                visited.add(node)

                for target in sorted(adjacency.get(node, set())):
                    if target not in visited:
                        queue.append(target)

            all_reachable.update(visited)

            reachable_by_entrypoint.append(
                {
                    "entrypoint": entrypoint,
                    "reachable_file_count": len(visited),
                    "reachable_files": sorted(visited),
                }
            )

        return {
            "entrypoint_count": len(entrypoint_paths),
            "reachable_file_count": len(all_reachable),
            "reachable_files": sorted(all_reachable),
            "by_entrypoint": sorted(
                reachable_by_entrypoint,
                key=lambda item: (
                    -item["reachable_file_count"],
                    item["entrypoint"],
                ),
            ),
        }

    def _discover_unreachable_active_files(
        self,
        reachability: dict[str, Any],
    ) -> list[str]:
        reachable = set(reachability.get("reachable_files", []))

        active_files = {
            path
            for path in self.source_paths
            if self._classify_path(path) == "active"
            and Path(path).suffix.lower()
            in PYTHON_SUFFIXES.union(WEB_SUFFIXES)
        }

        return sorted(active_files - reachable)

    @staticmethod
    def _find_runtime_cycles(
        edges: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        file_edges = [
            edge
            for edge in edges
            if edge["edge_type"] == "static_import"
        ]

        adjacency: dict[str, set[str]] = defaultdict(set)

        for edge in file_edges:
            adjacency[edge["source"]].add(edge["target"])

        index = 0
        stack: list[str] = []
        on_stack: set[str] = set()
        indices: dict[str, int] = {}
        lowlinks: dict[str, int] = {}
        components: list[list[str]] = []

        def strongconnect(node: str) -> None:
            nonlocal index

            indices[node] = index
            lowlinks[node] = index
            index += 1
            stack.append(node)
            on_stack.add(node)

            for target in sorted(adjacency.get(node, set())):
                if target not in indices:
                    strongconnect(target)
                    lowlinks[node] = min(
                        lowlinks[node],
                        lowlinks[target],
                    )
                elif target in on_stack:
                    lowlinks[node] = min(
                        lowlinks[node],
                        indices[target],
                    )

            if lowlinks[node] == indices[node]:
                component: list[str] = []

                while stack:
                    member = stack.pop()
                    on_stack.remove(member)
                    component.append(member)

                    if member == node:
                        break

                if len(component) > 1:
                    components.append(sorted(component))

        nodes = set(adjacency)

        for targets in adjacency.values():
            nodes.update(targets)

        for node in sorted(nodes):
            if node not in indices:
                strongconnect(node)

        return [
            {
                "node_count": len(component),
                "nodes": component,
            }
            for component in sorted(
                components,
                key=lambda item: (-len(item), item),
            )
        ]

    def _extract_fastapi_route(
        self,
        node: ast.AST,
        path_string: str,
        classification: str,
    ) -> dict[str, Any] | None:
        if not isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef),
        ):
            return None

        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue

            decorator_name = self._callable_name(decorator.func)
            method = decorator_name.rsplit(".", 1)[-1].lower()

            if method not in HTTP_METHODS:
                continue

            path_value = (
                self._safe_ast_value(decorator.args[0])
                if decorator.args
                else None
            )

            return {
                "source": path_string,
                "framework": "FastAPI",
                "route_type": (
                    "websocket"
                    if method == "websocket"
                    else "http"
                ),
                "method": method.upper(),
                "path": (
                    path_value
                    if isinstance(path_value, str)
                    else "<dynamic_or_missing>"
                ),
                "handler": node.name,
                "line": getattr(node, "lineno", None),
                "classification": classification,
            }

        return None

    @staticmethod
    def _has_main_guard(tree: ast.AST) -> bool:
        for node in ast.walk(tree):
            if not isinstance(node, ast.If):
                continue

            test = node.test

            if not isinstance(test, ast.Compare):
                continue

            if not isinstance(test.left, ast.Name):
                continue

            if test.left.id != "__name__":
                continue

            values = [
                comparator.value
                for comparator in test.comparators
                if isinstance(comparator, ast.Constant)
                and isinstance(comparator.value, str)
            ]

            if "__main__" in values:
                return True

        return False

    @staticmethod
    def _build_python_alias_index(
        tree: ast.AST,
    ) -> dict[str, str]:
        aliases: dict[str, str] = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    local_name = alias.asname or alias.name.split(".")[0]
                    aliases[local_name] = alias.name

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""

                for alias in node.names:
                    local_name = alias.asname or alias.name
                    canonical = (
                        f"{module}.{alias.name}"
                        if module
                        else alias.name
                    )
                    aliases[local_name] = canonical

        return aliases

    @staticmethod
    def _canonical_call_name(
        callable_name: str,
        aliases: dict[str, str],
    ) -> str:
        if not callable_name:
            return ""

        root, separator, remainder = callable_name.partition(".")
        canonical_root = aliases.get(root, root)

        if separator:
            return f"{canonical_root}.{remainder}"

        return canonical_root

    @staticmethod
    def _match_runtime_call(
        canonical_name: str,
    ) -> str | None:
        for signal_type, names in RUNTIME_CALL_PATTERNS.items():
            if canonical_name in names:
                return signal_type

            if any(
                canonical_name.endswith(f".{name}")
                for name in names
                if "." not in name
            ):
                return signal_type

        return None

    @staticmethod
    def _callable_name(node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id

        if isinstance(node, ast.Attribute):
            parent = RuntimeGraphDiscovery._callable_name(node.value)

            return (
                f"{parent}.{node.attr}"
                if parent
                else node.attr
            )

        return ""

    @staticmethod
    def _attribute_name(node: ast.Attribute) -> str:
        return RuntimeGraphDiscovery._callable_name(node)

    @staticmethod
    def _safe_ast_value(node: ast.AST | None) -> Any:
        if node is None:
            return None

        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.Name):
            return node.id

        if isinstance(node, ast.Attribute):
            return RuntimeGraphDiscovery._callable_name(node)

        if isinstance(node, ast.List):
            return [
                RuntimeGraphDiscovery._safe_ast_value(item)
                for item in node.elts
            ]

        if isinstance(node, ast.Tuple):
            return [
                RuntimeGraphDiscovery._safe_ast_value(item)
                for item in node.elts
            ]

        return ast.dump(node, include_attributes=False)[:500]

    @staticmethod
    def _keyword_value(
        node: ast.Call,
        keyword_name: str,
    ) -> Any:
        for keyword in node.keywords:
            if keyword.arg == keyword_name:
                return RuntimeGraphDiscovery._safe_ast_value(
                    keyword.value
                )

        return None

    @staticmethod
    def _is_next_page(path: Path) -> bool:
        return (
            len(path.parts) >= 3
            and path.parts[0] == "frontend"
            and path.parts[1] == "app"
            and path.stem == "page"
            and path.suffix.lower() in WEB_SUFFIXES
        )

    @staticmethod
    def _is_next_route_handler(path: Path) -> bool:
        return (
            len(path.parts) >= 3
            and path.parts[0] == "frontend"
            and path.parts[1] == "app"
            and path.stem == "route"
            and path.suffix.lower() in WEB_SUFFIXES
        )

    @staticmethod
    def _next_route_path(
        path: Path,
        is_api: bool,
    ) -> str:
        try:
            relative = path.relative_to("frontend/app")
        except ValueError:
            return "/"

        route_parts = list(relative.parent.parts)

        visible_parts: list[str] = []

        for part in route_parts:
            if part.startswith("(") and part.endswith(")"):
                continue

            if part.startswith("@"):
                continue

            visible_parts.append(part)

        if not visible_parts:
            return "/"

        return "/" + "/".join(visible_parts)

    @staticmethod
    def _line_number(
        text: str,
        character_offset: int,
    ) -> int:
        return text.count("\n", 0, character_offset) + 1

    @staticmethod
    def _merge_entrypoints(
        *groups: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        merged: list[dict[str, Any]] = []

        for group in groups:
            merged.extend(group)

        return RuntimeGraphDiscovery._deduplicate_records(
            merged,
            keys=("source", "entrypoint_type", "evidence"),
        )

    @staticmethod
    def _deduplicate_records(
        records: list[dict[str, Any]],
        keys: tuple[str, ...],
    ) -> list[dict[str, Any]]:
        deduplicated: dict[tuple[str, ...], dict[str, Any]] = {}

        for record in records:
            key = tuple(
                repr(record.get(field))
                for field in keys
            )

            deduplicated[key] = record

        return sorted(
            deduplicated.values(),
            key=lambda item: tuple(
                repr(item.get(field))
                for field in keys
            ),
        )

    @staticmethod
    def _classify_path(path_string: str) -> str:
        path = Path(path_string)
        parts = {part.lower() for part in path.parts}
        lowered = path.name.lower()

        if parts.intersection(ARCHIVE_MARKERS):
            return "archive_or_quarantine"

        if parts.intersection(GENERATED_MARKERS):
            return "generated_or_output"

        if parts.intersection(TOOLING_MARKERS):
            return "tooling"

        if (
            lowered.endswith(".bak")
            or ".backup" in lowered
            or ".phase" in lowered
            or ".generated." in lowered
        ):
            return "generated_or_backup"

        return "active"
