#!/usr/bin/env python3

"""
Phase 135 import graph normalization.

Consumes raw static dependency evidence and creates deterministic:

- file nodes
- canonical module nodes
- package nodes
- normalized file edges
- module edges
- package edges
- unresolved dependency groups
- graph degree metrics
- strongly connected package components

This stage remains architecture-neutral and read-only.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


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


class ImportGraphNormalizer:
    """
    Normalize raw dependency mappings into file, module, and package graphs.
    """

    def __init__(
        self,
        repository_root: Path,
        discovery: dict[str, Any],
        layer_mapping: dict[str, Any],
        dependency_mapping: dict[str, Any],
    ) -> None:
        self.repository_root = repository_root.resolve()
        self.discovery = discovery
        self.layer_mapping = layer_mapping
        self.dependency_mapping = dependency_mapping

        self.files: list[dict[str, Any]] = list(
            discovery.get("files", [])
        )

        self.file_index = {
            record["path"]: record
            for record in self.files
        }

        self.raw_edges: list[dict[str, Any]] = list(
            dependency_mapping.get("internal_edges", [])
        )

        self.unresolved_dependencies: list[dict[str, Any]] = list(
            dependency_mapping.get("unresolved_dependencies", [])
        )

    def normalize(self) -> dict[str, Any]:
        file_nodes = self._build_file_nodes()
        normalized_file_edges = self._normalize_file_edges()

        module_nodes = self._build_module_nodes(file_nodes)
        module_edges = self._build_module_edges(normalized_file_edges)

        package_nodes = self._build_package_nodes(file_nodes)
        package_edges = self._build_package_edges(normalized_file_edges)

        unresolved_groups = self._group_unresolved_dependencies()

        file_metrics = self._build_degree_metrics(
            nodes=[node["id"] for node in file_nodes],
            edges=normalized_file_edges,
        )

        module_metrics = self._build_degree_metrics(
            nodes=[node["id"] for node in module_nodes],
            edges=module_edges,
        )

        package_metrics = self._build_degree_metrics(
            nodes=[node["id"] for node in package_nodes],
            edges=package_edges,
        )

        package_cycles = self._find_strongly_connected_components(
            package_edges
        )

        self_edges = [
            edge
            for edge in normalized_file_edges
            if edge["source"] == edge["target"]
        ]

        active_file_edges = [
            edge
            for edge in normalized_file_edges
            if edge["classification"] == "active"
        ]

        non_active_file_edges = [
            edge
            for edge in normalized_file_edges
            if edge["classification"] != "active"
        ]

        return {
            "normalization_mode": "static_evidence_based",
            "architecture_assumed": False,
            "summary": {
                "file_nodes": len(file_nodes),
                "module_nodes": len(module_nodes),
                "package_nodes": len(package_nodes),
                "normalized_file_edges": len(normalized_file_edges),
                "module_edges": len(module_edges),
                "package_edges": len(package_edges),
                "active_file_edges": len(active_file_edges),
                "non_active_file_edges": len(non_active_file_edges),
                "self_edges": len(self_edges),
                "unresolved_groups": len(unresolved_groups),
                "package_cycles": len(package_cycles),
            },
            "file_graph": {
                "nodes": file_nodes,
                "edges": normalized_file_edges,
                "metrics": file_metrics,
                "self_edges": self_edges,
            },
            "module_graph": {
                "nodes": module_nodes,
                "edges": module_edges,
                "metrics": module_metrics,
            },
            "package_graph": {
                "nodes": package_nodes,
                "edges": package_edges,
                "metrics": package_metrics,
                "cycles": package_cycles,
            },
            "active_file_edges": active_file_edges,
            "non_active_file_edges": non_active_file_edges,
            "unresolved_groups": unresolved_groups,
            "limitations": [
                (
                    "Normalized imports represent static source references and "
                    "do not prove runtime execution."
                ),
                (
                    "Package boundaries are inferred from paths and package "
                    "markers rather than intended architecture contracts."
                ),
                (
                    "No dependency direction rule or forbidden-call policy has "
                    "been enforced."
                ),
            ],
        }

    def _build_file_nodes(self) -> list[dict[str, Any]]:
        referenced_paths: set[str] = set()

        for edge in self.raw_edges:
            referenced_paths.add(edge["source"])
            referenced_paths.add(edge["target"])

        nodes: list[dict[str, Any]] = []

        for path in sorted(referenced_paths):
            record = self.file_index.get(path, {})
            classification = self._classify_path(path)

            nodes.append(
                {
                    "id": path,
                    "path": path,
                    "language": self._language_from_path(path),
                    "module": self._canonical_module_name(path),
                    "package": self._canonical_package_name(path),
                    "classification": classification,
                    "is_test": bool(record.get("is_test", False)),
                    "is_entrypoint_candidate": bool(
                        record.get("is_entrypoint_candidate", False)
                    ),
                    "size_bytes": int(record.get("size_bytes", 0)),
                }
            )

        return nodes

    def _normalize_file_edges(self) -> list[dict[str, Any]]:
        merged: dict[tuple[str, str, str], dict[str, Any]] = {}

        for edge in self.raw_edges:
            source = edge["source"]
            target = edge["target"]
            language = edge["language"]

            key = (source, target, language)

            item = merged.setdefault(
                key,
                {
                    "source": source,
                    "target": target,
                    "language": language,
                    "source_module": self._canonical_module_name(source),
                    "target_module": self._canonical_module_name(target),
                    "source_package": self._canonical_package_name(source),
                    "target_package": self._canonical_package_name(target),
                    "import_types": set(),
                    "dependencies": set(),
                    "reference_count": 0,
                    "classification": self._edge_classification(
                        source,
                        target,
                    ),
                },
            )

            item["import_types"].add(
                edge.get("import_type", "unknown")
            )

            dependency = edge.get("dependency")

            if dependency:
                item["dependencies"].add(dependency)

            item["reference_count"] += 1

        results: list[dict[str, Any]] = []

        for _, item in sorted(merged.items()):
            results.append(
                {
                    **item,
                    "import_types": sorted(item["import_types"]),
                    "dependencies": sorted(item["dependencies"]),
                }
            )

        return results

    def _build_module_nodes(
        self,
        file_nodes: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        grouped: dict[str, dict[str, Any]] = {}

        for node in file_nodes:
            module = node["module"]

            item = grouped.setdefault(
                module,
                {
                    "id": module,
                    "module": module,
                    "files": [],
                    "languages": set(),
                    "packages": set(),
                    "classifications": Counter(),
                },
            )

            item["files"].append(node["path"])
            item["languages"].add(node["language"])
            item["packages"].add(node["package"])
            item["classifications"][node["classification"]] += 1

        results: list[dict[str, Any]] = []

        for module, item in sorted(grouped.items()):
            results.append(
                {
                    "id": module,
                    "module": module,
                    "file_count": len(item["files"]),
                    "files": sorted(item["files"]),
                    "languages": sorted(item["languages"]),
                    "packages": sorted(item["packages"]),
                    "classification_counts": dict(
                        sorted(item["classifications"].items())
                    ),
                }
            )

        return results

    def _build_module_edges(
        self,
        file_edges: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        grouped: dict[tuple[str, str], dict[str, Any]] = {}

        for edge in file_edges:
            source = edge["source_module"]
            target = edge["target_module"]

            key = (source, target)

            item = grouped.setdefault(
                key,
                {
                    "source": source,
                    "target": target,
                    "languages": set(),
                    "file_edges": 0,
                    "reference_count": 0,
                    "classifications": Counter(),
                },
            )

            item["languages"].add(edge["language"])
            item["file_edges"] += 1
            item["reference_count"] += edge["reference_count"]
            item["classifications"][edge["classification"]] += 1

        results: list[dict[str, Any]] = []

        for _, item in sorted(grouped.items()):
            results.append(
                {
                    "source": item["source"],
                    "target": item["target"],
                    "languages": sorted(item["languages"]),
                    "file_edges": item["file_edges"],
                    "reference_count": item["reference_count"],
                    "classification_counts": dict(
                        sorted(item["classifications"].items())
                    ),
                }
            )

        return results

    def _build_package_nodes(
        self,
        file_nodes: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        grouped: dict[str, dict[str, Any]] = {}

        for node in file_nodes:
            package = node["package"]

            item = grouped.setdefault(
                package,
                {
                    "id": package,
                    "package": package,
                    "files": [],
                    "modules": set(),
                    "languages": set(),
                    "classifications": Counter(),
                },
            )

            item["files"].append(node["path"])
            item["modules"].add(node["module"])
            item["languages"].add(node["language"])
            item["classifications"][node["classification"]] += 1

        results: list[dict[str, Any]] = []

        for package, item in sorted(grouped.items()):
            results.append(
                {
                    "id": package,
                    "package": package,
                    "file_count": len(item["files"]),
                    "module_count": len(item["modules"]),
                    "files": sorted(item["files"]),
                    "modules": sorted(item["modules"]),
                    "languages": sorted(item["languages"]),
                    "classification_counts": dict(
                        sorted(item["classifications"].items())
                    ),
                }
            )

        return results

    def _build_package_edges(
        self,
        file_edges: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        grouped: dict[tuple[str, str], dict[str, Any]] = {}

        for edge in file_edges:
            source = edge["source_package"]
            target = edge["target_package"]

            key = (source, target)

            item = grouped.setdefault(
                key,
                {
                    "source": source,
                    "target": target,
                    "languages": set(),
                    "file_edges": 0,
                    "reference_count": 0,
                    "source_files": set(),
                    "target_files": set(),
                    "classifications": Counter(),
                },
            )

            item["languages"].add(edge["language"])
            item["file_edges"] += 1
            item["reference_count"] += edge["reference_count"]
            item["source_files"].add(edge["source"])
            item["target_files"].add(edge["target"])
            item["classifications"][edge["classification"]] += 1

        results: list[dict[str, Any]] = []

        for _, item in sorted(grouped.items()):
            results.append(
                {
                    "source": item["source"],
                    "target": item["target"],
                    "languages": sorted(item["languages"]),
                    "file_edges": item["file_edges"],
                    "reference_count": item["reference_count"],
                    "source_file_count": len(item["source_files"]),
                    "target_file_count": len(item["target_files"]),
                    "classification_counts": dict(
                        sorted(item["classifications"].items())
                    ),
                }
            )

        return results

    def _group_unresolved_dependencies(self) -> list[dict[str, Any]]:
        grouped: dict[tuple[str, str, str], dict[str, Any]] = {}

        for item in self.unresolved_dependencies:
            language = item.get("language", "unknown")
            dependency = item.get("dependency", "")
            reason = item.get("reason", "unknown")

            probable_cause = self._probable_unresolved_cause(
                language=language,
                dependency=dependency,
                reason=reason,
            )

            key = (language, reason, probable_cause)

            group = grouped.setdefault(
                key,
                {
                    "language": language,
                    "reason": reason,
                    "probable_cause": probable_cause,
                    "references": [],
                    "dependencies": Counter(),
                },
            )

            group["references"].append(
                {
                    "source": item.get("source", ""),
                    "dependency": dependency,
                }
            )

            group["dependencies"][dependency] += 1

        results: list[dict[str, Any]] = []

        for _, group in sorted(grouped.items()):
            common_dependencies = [
                {
                    "dependency": dependency,
                    "reference_count": count,
                }
                for dependency, count in sorted(
                    group["dependencies"].items(),
                    key=lambda entry: (-entry[1], entry[0]),
                )
            ]

            results.append(
                {
                    "language": group["language"],
                    "reason": group["reason"],
                    "probable_cause": group["probable_cause"],
                    "reference_count": len(group["references"]),
                    "unique_dependencies": len(group["dependencies"]),
                    "common_dependencies": common_dependencies[:50],
                    "references": sorted(
                        group["references"],
                        key=lambda entry: (
                            entry["source"],
                            entry["dependency"],
                        ),
                    ),
                }
            )

        return results

    @staticmethod
    def _probable_unresolved_cause(
        language: str,
        dependency: str,
        reason: str,
    ) -> str:
        if reason == "empty_or_invalid_import":
            return "invalid_or_incomplete_import"

        if language == "javascript_or_typescript":
            if dependency.startswith("@/"):
                return "typescript_alias_resolution"
            if dependency.startswith("."):
                return "missing_relative_module_or_extension"
            if dependency.startswith("/"):
                return "absolute_path_resolution"

        if language == "python":
            if dependency.startswith("app."):
                return "python_path_or_package_root_mismatch"
            if dependency.startswith("backend."):
                return "repository_root_package_resolution"
            if dependency.startswith("spine."):
                return "legacy_or_alternate_python_root"
            if dependency.startswith("stacks."):
                return "application_package_alias_resolution"
            if dependency.startswith("scripts."):
                return "tooling_package_resolution"

        return "unresolved_static_reference"

    @staticmethod
    def _build_degree_metrics(
        nodes: list[str],
        edges: list[dict[str, Any]],
    ) -> dict[str, Any]:
        inbound: Counter[str] = Counter()
        outbound: Counter[str] = Counter()

        for edge in edges:
            outbound[edge["source"]] += 1
            inbound[edge["target"]] += 1

        all_nodes = set(nodes)

        top_inbound = [
            {
                "id": node,
                "in_degree": count,
            }
            for node, count in sorted(
                inbound.items(),
                key=lambda item: (-item[1], item[0]),
            )[:100]
        ]

        top_outbound = [
            {
                "id": node,
                "out_degree": count,
            }
            for node, count in sorted(
                outbound.items(),
                key=lambda item: (-item[1], item[0]),
            )[:100]
        ]

        source_only = sorted(
            node
            for node in all_nodes
            if outbound[node] > 0 and inbound[node] == 0
        )

        sink_only = sorted(
            node
            for node in all_nodes
            if inbound[node] > 0 and outbound[node] == 0
        )

        isolated = sorted(
            node
            for node in all_nodes
            if inbound[node] == 0 and outbound[node] == 0
        )

        return {
            "node_count": len(all_nodes),
            "edge_count": len(edges),
            "top_inbound": top_inbound,
            "top_outbound": top_outbound,
            "source_only_nodes": source_only,
            "sink_only_nodes": sink_only,
            "isolated_nodes": isolated,
        }

    @staticmethod
    def _find_strongly_connected_components(
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
            key=lambda item: (-len(item), item),
        ):
            component_set = set(component)

            component_edges = [
                {
                    "source": edge["source"],
                    "target": edge["target"],
                    "file_edges": edge.get("file_edges", 0),
                    "reference_count": edge.get("reference_count", 0),
                }
                for edge in edges
                if edge["source"] in component_set
                and edge["target"] in component_set
            ]

            results.append(
                {
                    "node_count": len(component),
                    "nodes": component,
                    "edges": component_edges,
                }
            )

        return results

    @staticmethod
    def _canonical_module_name(path_string: str) -> str:
        path = Path(path_string)
        suffix = path.suffix.lower()

        if suffix == ".py":
            if path.name == "__init__.py":
                parts = path.parent.parts
            else:
                parts = path.with_suffix("").parts

            return ".".join(parts) or "<root>"

        if suffix in {".ts", ".tsx", ".js", ".jsx", ".mjs"}:
            without_suffix = path.with_suffix("")

            if without_suffix.name == "index":
                without_suffix = without_suffix.parent

            return "/".join(without_suffix.parts) or "<root>"

        return path_string

    @staticmethod
    def _canonical_package_name(path_string: str) -> str:
        path = Path(path_string)
        parts = path.parts

        if not parts:
            return "<root>"

        if parts[0] == "backend":
            if len(parts) >= 4 and parts[1:3] == ("app", "stacks"):
                return "/".join(parts[:4])

            if len(parts) >= 4 and parts[1:3] == ("app", "spine"):
                return "/".join(parts[:4])

            if len(parts) >= 3 and parts[1] == "app":
                return "/".join(parts[:3])

            return "backend"

        if parts[0] == "frontend":
            if len(parts) >= 3 and parts[1] in {
                "app",
                "components",
                "features",
                "lib",
                "src",
            }:
                return "/".join(parts[:3])

            return "frontend"

        if parts[0] == "scripts":
            if len(parts) >= 2:
                return "/".join(parts[:2])

            return "scripts"

        if len(parts) >= 2:
            return "/".join(parts[:2])

        return parts[0]

    @staticmethod
    def _language_from_path(path_string: str) -> str:
        suffix = Path(path_string).suffix.lower()

        if suffix == ".py":
            return "python"

        if suffix in {".ts", ".tsx", ".js", ".jsx", ".mjs"}:
            return "javascript_or_typescript"

        return suffix.removeprefix(".") or "unknown"

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

    def _edge_classification(
        self,
        source: str,
        target: str,
    ) -> str:
        source_classification = self._classify_path(source)
        target_classification = self._classify_path(target)

        classifications = {
            source_classification,
            target_classification,
        }

        if "archive_or_quarantine" in classifications:
            return "archive_or_quarantine"

        if classifications.intersection(
            {"generated_or_output", "generated_or_backup"}
        ):
            return "generated_or_output"

        if "tooling" in classifications:
            return "tooling"

        return "active"
