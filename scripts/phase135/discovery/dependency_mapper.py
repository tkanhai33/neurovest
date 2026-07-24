#!/usr/bin/env python3

"""
Phase 135 blind dependency mapping.

Discovers Python and JavaScript/TypeScript dependencies from source evidence.

This stage does not enforce NeuroVest's intended architecture and does not
declare dependency violations. It records observed dependency relationships,
unresolved references, external packages, cycles, and highly connected files.
"""

from __future__ import annotations

import ast
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from scripts.phase135.utils.filesystem import safe_read_text


PYTHON_SUFFIXES = {".py"}
JAVASCRIPT_SUFFIXES = {".js", ".jsx", ".mjs", ".ts", ".tsx"}

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

PYTHON_STANDARD_LIBRARY = {
    "__future__",
    "abc",
    "argparse",
    "ast",
    "asyncio",
    "base64",
    "bisect",
    "builtins",
    "calendar",
    "collections",
    "concurrent",
    "contextlib",
    "copy",
    "csv",
    "dataclasses",
    "datetime",
    "decimal",
    "enum",
    "functools",
    "glob",
    "hashlib",
    "heapq",
    "hmac",
    "html",
    "http",
    "importlib",
    "inspect",
    "io",
    "itertools",
    "json",
    "logging",
    "math",
    "multiprocessing",
    "operator",
    "os",
    "pathlib",
    "pickle",
    "platform",
    "queue",
    "random",
    "re",
    "secrets",
    "shlex",
    "shutil",
    "signal",
    "socket",
    "sqlite3",
    "statistics",
    "string",
    "subprocess",
    "sys",
    "tempfile",
    "textwrap",
    "threading",
    "time",
    "traceback",
    "types",
    "typing",
    "unittest",
    "urllib",
    "uuid",
    "warnings",
    "weakref",
    "xml",
    "zipfile",
}

JS_BUILTINS = {
    "assert",
    "buffer",
    "child_process",
    "cluster",
    "console",
    "crypto",
    "dns",
    "events",
    "fs",
    "http",
    "https",
    "module",
    "net",
    "os",
    "path",
    "perf_hooks",
    "process",
    "querystring",
    "readline",
    "stream",
    "string_decoder",
    "timers",
    "tls",
    "tty",
    "url",
    "util",
    "v8",
    "vm",
    "worker_threads",
    "zlib",
}

JS_IMPORT_PATTERNS = [
    re.compile(
        r"""(?:import|export)\s+(?:[\s\S]*?\s+from\s+)?["']([^"']+)["']""",
        re.MULTILINE,
    ),
    re.compile(
        r"""require\(\s*["']([^"']+)["']\s*\)""",
        re.MULTILINE,
    ),
    re.compile(
        r"""import\(\s*["']([^"']+)["']\s*\)""",
        re.MULTILINE,
    ),
]


class DependencyMapper:
    """
    Build a static source dependency graph from repository evidence.
    """

    def __init__(
        self,
        repository_root: Path,
        discovery: dict[str, Any],
        layer_mapping: dict[str, Any],
    ) -> None:
        self.repository_root = repository_root.resolve()
        self.discovery = discovery
        self.layer_mapping = layer_mapping

        self.files: list[dict[str, Any]] = list(
            discovery.get("files", [])
        )

        self.source_paths = {
            record["path"]
            for record in self.files
            if record.get("is_source")
        }

        self.python_paths = {
            path
            for path in self.source_paths
            if Path(path).suffix.lower() in PYTHON_SUFFIXES
        }

        self.javascript_paths = {
            path
            for path in self.source_paths
            if Path(path).suffix.lower() in JAVASCRIPT_SUFFIXES
        }

        self.python_module_index = self._build_python_module_index()

    def map_dependencies(self) -> dict[str, Any]:
        python_result = self._map_python_dependencies()
        javascript_result = self._map_javascript_dependencies()

        internal_edges = (
            python_result["internal_edges"]
            + javascript_result["internal_edges"]
        )

        external_dependencies = self._merge_external_dependencies(
            python_result["external_dependencies"],
            javascript_result["external_dependencies"],
        )

        unresolved_dependencies = (
            python_result["unresolved_dependencies"]
            + javascript_result["unresolved_dependencies"]
        )

        cycles = self._find_cycles(internal_edges)
        graph_metrics = self._build_graph_metrics(internal_edges)

        archived_edges = [
            edge
            for edge in internal_edges
            if self._is_archived_or_generated(edge["source"])
            or self._is_archived_or_generated(edge["target"])
        ]

        active_edges = [
            edge
            for edge in internal_edges
            if edge not in archived_edges
        ]

        return {
            "mapping_mode": "static_evidence_based",
            "architecture_assumed": False,
            "summary": {
                "python_files_analyzed": python_result["files_analyzed"],
                "javascript_files_analyzed": javascript_result["files_analyzed"],
                "files_with_parse_errors": (
                    len(python_result["parse_errors"])
                    + len(javascript_result["parse_errors"])
                ),
                "internal_dependency_edges": len(internal_edges),
                "active_internal_edges": len(active_edges),
                "archived_or_generated_edges": len(archived_edges),
                "external_dependencies": len(external_dependencies),
                "unresolved_dependencies": len(unresolved_dependencies),
                "dependency_cycles": len(cycles),
                "graph_nodes": graph_metrics["node_count"],
            },
            "python": python_result,
            "javascript_or_typescript": javascript_result,
            "internal_edges": internal_edges,
            "active_internal_edges": active_edges,
            "archived_or_generated_edges": archived_edges,
            "external_dependencies": external_dependencies,
            "unresolved_dependencies": unresolved_dependencies,
            "cycles": cycles,
            "graph_metrics": graph_metrics,
            "limitations": [
                (
                    "This stage performs static import analysis only and does not "
                    "prove runtime execution."
                ),
                (
                    "Dynamic imports, reflection, plugin registration, shell "
                    "execution, dependency injection, and framework routing may "
                    "require later runtime graph analysis."
                ),
                (
                    "No intended NeuroVest layer direction or forbidden-call "
                    "contract has been enforced."
                ),
            ],
        }

    def _build_python_module_index(self) -> dict[str, str]:
        index: dict[str, str] = {}

        for path_string in sorted(self.python_paths):
            path = Path(path_string)

            if path.name == "__init__.py":
                module_parts = path.parent.parts
            else:
                module_parts = path.with_suffix("").parts

            module_name = ".".join(module_parts)

            if module_name:
                index[module_name] = path_string

            if module_name.startswith("backend."):
                index[module_name.removeprefix("backend.")] = path_string

            if module_name.startswith("backend.app."):
                index[module_name.removeprefix("backend.app.")] = path_string

            if module_name.startswith("scripts."):
                index[module_name] = path_string

        return index

    def _map_python_dependencies(self) -> dict[str, Any]:
        internal_edges: list[dict[str, Any]] = []
        external_counter: Counter[str] = Counter()
        unresolved: list[dict[str, Any]] = []
        parse_errors: list[dict[str, str]] = []

        files_analyzed = 0

        for source_path in sorted(self.python_paths):
            if self._is_archived_or_generated(source_path):
                classification = "archived_or_generated"
            else:
                classification = "active"

            absolute_path = self.repository_root / source_path
            text = safe_read_text(absolute_path, max_bytes=2_000_000)

            if text is None:
                parse_errors.append(
                    {
                        "path": source_path,
                        "error": "file_unreadable_or_too_large",
                    }
                )
                continue

            try:
                tree = ast.parse(text, filename=source_path)
            except SyntaxError as exc:
                parse_errors.append(
                    {
                        "path": source_path,
                        "error": (
                            f"SyntaxError line {exc.lineno}: "
                            f"{exc.msg}"
                        ),
                    }
                )
                continue

            files_analyzed += 1

            imports = self._extract_python_imports(
                tree=tree,
                source_path=source_path,
            )

            seen_edges: set[tuple[str, str, str]] = set()

            for dependency in imports:
                module_name = dependency["module"]
                imported_name = dependency.get("name")
                level = dependency.get("level", 0)

                resolved_module = self._resolve_python_module_name(
                    source_path=source_path,
                    module_name=module_name,
                    imported_name=imported_name,
                    level=level,
                )

                resolved_path = self._resolve_python_internal_path(
                    resolved_module
                )

                if resolved_path:
                    edge_key = (
                        source_path,
                        resolved_path,
                        dependency["import_type"],
                    )

                    if edge_key in seen_edges:
                        continue

                    seen_edges.add(edge_key)

                    internal_edges.append(
                        {
                            "language": "python",
                            "source": source_path,
                            "target": resolved_path,
                            "dependency": resolved_module,
                            "import_type": dependency["import_type"],
                            "source_classification": classification,
                        }
                    )
                    continue

                root_module = (
                    resolved_module.split(".", 1)[0]
                    if resolved_module
                    else ""
                )

                if not root_module:
                    unresolved.append(
                        {
                            "language": "python",
                            "source": source_path,
                            "dependency": module_name,
                            "reason": "empty_or_invalid_import",
                        }
                    )
                elif root_module in PYTHON_STANDARD_LIBRARY:
                    continue
                elif self._looks_internal_python_reference(resolved_module):
                    unresolved.append(
                        {
                            "language": "python",
                            "source": source_path,
                            "dependency": resolved_module,
                            "reason": "internal_module_not_resolved",
                        }
                    )
                else:
                    external_counter[root_module] += 1

        return {
            "files_analyzed": files_analyzed,
            "internal_edges": sorted(
                internal_edges,
                key=lambda item: (
                    item["source"],
                    item["target"],
                    item["import_type"],
                ),
            ),
            "external_dependencies": [
                {
                    "language": "python",
                    "package": package,
                    "reference_count": count,
                }
                for package, count in sorted(
                    external_counter.items(),
                    key=lambda item: (-item[1], item[0]),
                )
            ],
            "unresolved_dependencies": sorted(
                unresolved,
                key=lambda item: (
                    item["source"],
                    item["dependency"],
                ),
            ),
            "parse_errors": sorted(
                parse_errors,
                key=lambda item: item["path"],
            ),
        }

    def _extract_python_imports(
        self,
        tree: ast.AST,
        source_path: str,
    ) -> list[dict[str, Any]]:
        imports: list[dict[str, Any]] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        {
                            "module": alias.name,
                            "name": None,
                            "level": 0,
                            "import_type": "import",
                            "line": getattr(node, "lineno", None),
                        }
                    )

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""

                if not node.names:
                    imports.append(
                        {
                            "module": module,
                            "name": None,
                            "level": node.level,
                            "import_type": "from_import",
                            "line": getattr(node, "lineno", None),
                        }
                    )
                    continue

                for alias in node.names:
                    imports.append(
                        {
                            "module": module,
                            "name": alias.name,
                            "level": node.level,
                            "import_type": "from_import",
                            "line": getattr(node, "lineno", None),
                        }
                    )

        return imports

    def _resolve_python_module_name(
        self,
        source_path: str,
        module_name: str,
        imported_name: str | None,
        level: int,
    ) -> str:
        if level <= 0:
            candidates = []

            if module_name and imported_name:
                candidates.append(f"{module_name}.{imported_name}")

            if module_name:
                candidates.append(module_name)

            for candidate in candidates:
                if self._resolve_python_internal_path(candidate):
                    return candidate

            return module_name or imported_name or ""

        source = Path(source_path)

        if source.name == "__init__.py":
            package_parts = list(source.parent.parts)
        else:
            package_parts = list(source.parent.parts)

        remove_count = max(level - 1, 0)

        if remove_count:
            if remove_count >= len(package_parts):
                package_parts = []
            else:
                package_parts = package_parts[:-remove_count]

        target_parts = list(package_parts)

        if module_name:
            target_parts.extend(module_name.split("."))

        base_module = ".".join(target_parts)

        candidates = []

        if base_module and imported_name and imported_name != "*":
            candidates.append(f"{base_module}.{imported_name}")

        if base_module:
            candidates.append(base_module)

        for candidate in candidates:
            if self._resolve_python_internal_path(candidate):
                return candidate

        return base_module

    def _resolve_python_internal_path(
        self,
        module_name: str,
    ) -> str | None:
        if not module_name:
            return None

        candidates = [
            module_name,
            f"backend.{module_name}",
            f"backend.app.{module_name}",
        ]

        for candidate in candidates:
            path = self.python_module_index.get(candidate)

            if path:
                return path

        parts = module_name.split(".")

        while len(parts) > 1:
            parts.pop()
            candidate = ".".join(parts)

            for variant in (
                candidate,
                f"backend.{candidate}",
                f"backend.app.{candidate}",
            ):
                path = self.python_module_index.get(variant)

                if path:
                    return path

        return None

    def _looks_internal_python_reference(
        self,
        module_name: str,
    ) -> bool:
        return module_name.startswith(
            (
                "app.",
                "backend.",
                "scripts.",
                "spine.",
                "stacks.",
            )
        )

    def _map_javascript_dependencies(self) -> dict[str, Any]:
        internal_edges: list[dict[str, Any]] = []
        external_counter: Counter[str] = Counter()
        unresolved: list[dict[str, Any]] = []
        parse_errors: list[dict[str, str]] = []

        files_analyzed = 0

        for source_path in sorted(self.javascript_paths):
            absolute_path = self.repository_root / source_path
            text = safe_read_text(absolute_path, max_bytes=2_000_000)

            if text is None:
                parse_errors.append(
                    {
                        "path": source_path,
                        "error": "file_unreadable_or_too_large",
                    }
                )
                continue

            files_analyzed += 1
            imports = self._extract_javascript_imports(text)

            for dependency in sorted(set(imports)):
                resolved = self._resolve_javascript_internal_path(
                    source_path=source_path,
                    dependency=dependency,
                )

                if resolved:
                    internal_edges.append(
                        {
                            "language": "javascript_or_typescript",
                            "source": source_path,
                            "target": resolved,
                            "dependency": dependency,
                            "import_type": "static_or_dynamic_import",
                            "source_classification": (
                                "archived_or_generated"
                                if self._is_archived_or_generated(source_path)
                                else "active"
                            ),
                        }
                    )
                    continue

                if dependency.startswith((".", "/", "@/")):
                    unresolved.append(
                        {
                            "language": "javascript_or_typescript",
                            "source": source_path,
                            "dependency": dependency,
                            "reason": "internal_module_not_resolved",
                        }
                    )
                    continue

                package_name = self._javascript_package_root(dependency)

                if package_name in JS_BUILTINS or dependency.startswith("node:"):
                    continue

                external_counter[package_name] += 1

        unique_edges = {
            (
                edge["source"],
                edge["target"],
                edge["dependency"],
            ): edge
            for edge in internal_edges
        }

        return {
            "files_analyzed": files_analyzed,
            "internal_edges": sorted(
                unique_edges.values(),
                key=lambda item: (
                    item["source"],
                    item["target"],
                    item["dependency"],
                ),
            ),
            "external_dependencies": [
                {
                    "language": "javascript_or_typescript",
                    "package": package,
                    "reference_count": count,
                }
                for package, count in sorted(
                    external_counter.items(),
                    key=lambda item: (-item[1], item[0]),
                )
            ],
            "unresolved_dependencies": sorted(
                unresolved,
                key=lambda item: (
                    item["source"],
                    item["dependency"],
                ),
            ),
            "parse_errors": sorted(
                parse_errors,
                key=lambda item: item["path"],
            ),
        }

    @staticmethod
    def _extract_javascript_imports(text: str) -> list[str]:
        imports: list[str] = []

        for pattern in JS_IMPORT_PATTERNS:
            imports.extend(match.group(1) for match in pattern.finditer(text))

        return imports

    def _resolve_javascript_internal_path(
        self,
        source_path: str,
        dependency: str,
    ) -> str | None:
        source = Path(source_path)

        if dependency.startswith("@/"):
            base = Path("frontend")
            target = base / dependency.removeprefix("@/")
        elif dependency.startswith("."):
            target = source.parent / dependency
        elif dependency.startswith("/"):
            target = Path(dependency.lstrip("/"))
        else:
            return None

        candidates = self._javascript_candidate_paths(target)

        for candidate in candidates:
            normalized = candidate.as_posix()

            if normalized in self.javascript_paths:
                return normalized

        return None

    @staticmethod
    def _javascript_candidate_paths(target: Path) -> list[Path]:
        candidates = [target]

        if target.suffix:
            return candidates

        for suffix in (
            ".ts",
            ".tsx",
            ".js",
            ".jsx",
            ".mjs",
        ):
            candidates.append(target.with_suffix(suffix))

        for filename in (
            "index.ts",
            "index.tsx",
            "index.js",
            "index.jsx",
            "index.mjs",
        ):
            candidates.append(target / filename)

        return candidates

    @staticmethod
    def _javascript_package_root(dependency: str) -> str:
        if dependency.startswith("@"):
            parts = dependency.split("/")

            if len(parts) >= 2:
                return "/".join(parts[:2])

        return dependency.split("/", 1)[0]

    @staticmethod
    def _merge_external_dependencies(
        python_dependencies: list[dict[str, Any]],
        javascript_dependencies: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        merged = python_dependencies + javascript_dependencies

        return sorted(
            merged,
            key=lambda item: (
                item["language"],
                -item["reference_count"],
                item["package"],
            ),
        )

    def _find_cycles(
        self,
        edges: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        adjacency: dict[str, set[str]] = defaultdict(set)

        for edge in edges:
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
                elif (
                    component
                    and component[0] in adjacency.get(component[0], set())
                ):
                    components.append(component)

        nodes = set(adjacency)

        for targets in adjacency.values():
            nodes.update(targets)

        for node in sorted(nodes):
            if node not in indices:
                strongconnect(node)

        results: list[dict[str, Any]] = []

        for component in sorted(
            components,
            key=lambda item: (
                -len(item),
                item,
            ),
        ):
            component_set = set(component)

            cycle_edges = [
                {
                    "source": edge["source"],
                    "target": edge["target"],
                    "language": edge["language"],
                }
                for edge in edges
                if edge["source"] in component_set
                and edge["target"] in component_set
            ]

            results.append(
                {
                    "node_count": len(component),
                    "nodes": component,
                    "internal_edges": cycle_edges,
                }
            )

        return results

    @staticmethod
    def _build_graph_metrics(
        edges: list[dict[str, Any]],
    ) -> dict[str, Any]:
        inbound: Counter[str] = Counter()
        outbound: Counter[str] = Counter()
        nodes: set[str] = set()

        for edge in edges:
            source = edge["source"]
            target = edge["target"]

            nodes.add(source)
            nodes.add(target)

            outbound[source] += 1
            inbound[target] += 1

        top_inbound = [
            {
                "path": path,
                "incoming_dependencies": count,
            }
            for path, count in sorted(
                inbound.items(),
                key=lambda item: (-item[1], item[0]),
            )[:50]
        ]

        top_outbound = [
            {
                "path": path,
                "outgoing_dependencies": count,
            }
            for path, count in sorted(
                outbound.items(),
                key=lambda item: (-item[1], item[0]),
            )[:50]
        ]

        isolated_nodes = sorted(
            node
            for node in nodes
            if inbound[node] == 0 and outbound[node] == 0
        )

        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "top_inbound_files": top_inbound,
            "top_outbound_files": top_outbound,
            "isolated_nodes": isolated_nodes,
        }

    @staticmethod
    def _is_archived_or_generated(path_string: str) -> bool:
        path = Path(path_string)
        parts = {part.lower() for part in path.parts}

        if parts.intersection(ARCHIVE_MARKERS):
            return True

        if parts.intersection(GENERATED_MARKERS):
            return True

        lowered = path.name.lower()

        return (
            lowered.endswith(".bak")
            or ".backup" in lowered
            or ".phase" in lowered
            or ".generated." in lowered
        )
