#!/usr/bin/env python3

"""
Phase 135 blind layer mapping.

This module does not assume NeuroVest's intended architecture.

It infers observable repository regions, package boundaries, source roots,
framework signals, API surfaces, test regions, generated artifacts, archived
regions, and possible application layers strictly from filesystem evidence.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ARCHIVE_DIRECTORY_MARKERS = {
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

GENERATED_DIRECTORY_MARKERS = {
    ".next",
    "build",
    "coverage",
    "dist",
    "generated",
    "htmlcov",
    "output",
    "outputs",
    "reports",
}

TEST_DIRECTORY_MARKERS = {
    "__tests__",
    "spec",
    "specs",
    "test",
    "tests",
}

DOCUMENTATION_DIRECTORY_MARKERS = {
    "docs",
    "documentation",
    "handoff",
    "handovers",
}

SCRIPT_DIRECTORY_MARKERS = {
    "bin",
    "script",
    "scripts",
    "tools",
}

CONFIG_DIRECTORY_MARKERS = {
    ".github",
    "config",
    "configs",
    "configuration",
}

FRONTEND_SIGNALS = {
    "app",
    "components",
    "features",
    "hooks",
    "pages",
    "public",
    "src",
    "styles",
}

BACKEND_SIGNALS = {
    "api",
    "app",
    "controllers",
    "core",
    "domain",
    "infrastructure",
    "models",
    "repositories",
    "services",
    "spine",
    "stacks",
}

API_DIRECTORY_MARKERS = {
    "api",
    "controllers",
    "endpoints",
    "handlers",
    "routes",
    "routers",
}

DOMAIN_DIRECTORY_MARKERS = {
    "domain",
    "domains",
    "entities",
    "models",
    "schemas",
    "value_objects",
}

SERVICE_DIRECTORY_MARKERS = {
    "application",
    "facade",
    "facades",
    "service",
    "services",
    "use_cases",
}

INFRASTRUCTURE_DIRECTORY_MARKERS = {
    "adapter",
    "adapters",
    "database",
    "db",
    "external",
    "infrastructure",
    "integration",
    "integrations",
    "persistence",
    "provider",
    "providers",
    "repository",
    "repositories",
}

RUNTIME_DIRECTORY_MARKERS = {
    "engine",
    "engines",
    "execution",
    "orchestration",
    "runtime",
    "scheduler",
    "workers",
}

PRESENTATION_DIRECTORY_MARKERS = {
    "components",
    "frontend",
    "pages",
    "presentation",
    "templates",
    "ui",
    "views",
}

SECURITY_DIRECTORY_MARKERS = {
    "auth",
    "authentication",
    "authorization",
    "identity",
    "security",
}

CONTRACT_DIRECTORY_MARKERS = {
    "contract",
    "contracts",
    "dto",
    "dtos",
    "interface",
    "interfaces",
    "protocol",
    "protocols",
    "schema",
    "schemas",
    "types",
}

STATE_DIRECTORY_MARKERS = {
    "state",
    "store",
    "stores",
}

PYTHON_PACKAGE_MARKER = "__init__.py"

SOURCE_SUFFIXES = {
    ".c",
    ".cc",
    ".cpp",
    ".css",
    ".go",
    ".h",
    ".hpp",
    ".html",
    ".java",
    ".js",
    ".jsx",
    ".mjs",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".scss",
    ".sh",
    ".sql",
    ".svelte",
    ".ts",
    ".tsx",
    ".vue",
}

GENERATED_FILENAME_MARKERS = (
    ".bak",
    ".backup",
    ".generated.",
    ".min.js",
    ".min.css",
    ".phase",
)

REPORT_FILENAME_MARKERS = (
    "_report",
    "_state",
    "_plan",
    "_graph",
    "audit",
    "topology",
)


class LayerMapper:
    """
    Infer repository regions and candidate layers from discovered evidence.
    """

    def __init__(
        self,
        repository_root: Path,
        discovery: dict[str, Any],
    ) -> None:
        self.repository_root = repository_root.resolve()
        self.discovery = discovery

        self.files: list[dict[str, Any]] = list(
            discovery.get("files", [])
        )

        self.directories: list[str] = list(
            discovery.get("directories", [])
        )

        self.files_by_directory: dict[str, list[dict[str, Any]]] = defaultdict(list)

        for record in self.files:
            path = Path(record["path"])
            directory = path.parent.as_posix()
            self.files_by_directory[directory].append(record)

    def map_layers(self) -> dict[str, Any]:
        package_roots = self._discover_package_roots()
        source_roots = self._discover_source_roots()
        repository_regions = self._map_repository_regions()
        candidate_layers = self._map_candidate_layers()
        framework_signals = self._discover_framework_signals()
        boundary_signals = self._discover_boundary_signals()
        ambiguous_regions = self._discover_ambiguous_regions(candidate_layers)
        ownership_summary = self._build_ownership_summary(
            repository_regions=repository_regions,
            candidate_layers=candidate_layers,
        )

        return {
            "mapping_mode": "blind_evidence_based",
            "architecture_assumed": False,
            "summary": {
                "package_roots": len(package_roots),
                "source_roots": len(source_roots),
                "repository_regions": len(repository_regions),
                "candidate_layers": len(candidate_layers),
                "framework_signals": len(framework_signals),
                "boundary_signals": len(boundary_signals),
                "ambiguous_regions": len(ambiguous_regions),
            },
            "package_roots": package_roots,
            "source_roots": source_roots,
            "repository_regions": repository_regions,
            "candidate_layers": candidate_layers,
            "framework_signals": framework_signals,
            "boundary_signals": boundary_signals,
            "ambiguous_regions": ambiguous_regions,
            "ownership_summary": ownership_summary,
            "limitations": [
                (
                    "Layer names are candidate classifications derived from "
                    "directory names, file names, extensions, and package markers."
                ),
                (
                    "No intended NeuroVest spine, stack, ownership, or forbidden-call "
                    "contract has been assumed."
                ),
                (
                    "Import direction and runtime execution evidence are deferred to "
                    "later audit stages."
                ),
            ],
        }

    def _discover_package_roots(self) -> list[dict[str, Any]]:
        package_roots: list[dict[str, Any]] = []

        python_packages: set[str] = set()

        for record in self.files:
            path = Path(record["path"])

            if path.name == PYTHON_PACKAGE_MARKER:
                python_packages.add(path.parent.as_posix())

        for package_path in sorted(python_packages):
            package_roots.append(
                {
                    "path": package_path,
                    "package_type": "python",
                    "evidence": [
                        f"{package_path}/{PYTHON_PACKAGE_MARKER}"
                    ],
                    "source_file_count": self._count_source_files(package_path),
                }
            )

        javascript_roots = self._discover_javascript_package_roots()

        package_roots.extend(javascript_roots)

        return sorted(
            package_roots,
            key=lambda item: (
                item["path"],
                item["package_type"],
            ),
        )

    def _discover_javascript_package_roots(self) -> list[dict[str, Any]]:
        roots: list[dict[str, Any]] = []

        package_files = {
            record["path"]: record
            for record in self.files
            if Path(record["path"]).name == "package.json"
        }

        for package_path in sorted(package_files):
            root = Path(package_path).parent.as_posix()

            roots.append(
                {
                    "path": root,
                    "package_type": "javascript_or_typescript",
                    "evidence": [package_path],
                    "source_file_count": self._count_source_files(root),
                }
            )

        return roots

    def _discover_source_roots(self) -> list[dict[str, Any]]:
        candidates: dict[str, dict[str, Any]] = {}

        for record in self.files:
            if not record.get("is_source"):
                continue

            path = Path(record["path"])
            parts = path.parts

            if not parts:
                continue

            if len(parts) == 1:
                root = "."
            elif parts[0] in {"backend", "frontend"} and len(parts) >= 2:
                root = "/".join(parts[:2])
            else:
                root = parts[0]

            candidate = candidates.setdefault(
                root,
                {
                    "path": root,
                    "source_file_count": 0,
                    "extensions": Counter(),
                    "evidence": [],
                },
            )

            candidate["source_file_count"] += 1
            candidate["extensions"][record.get("suffix") or "<none>"] += 1

            if len(candidate["evidence"]) < 10:
                candidate["evidence"].append(record["path"])

        result: list[dict[str, Any]] = []

        for path, candidate in sorted(candidates.items()):
            result.append(
                {
                    "path": path,
                    "source_file_count": candidate["source_file_count"],
                    "extensions": dict(
                        sorted(
                            candidate["extensions"].items(),
                            key=lambda item: (-item[1], item[0]),
                        )
                    ),
                    "evidence": candidate["evidence"],
                }
            )

        return result

    def _map_repository_regions(self) -> list[dict[str, Any]]:
        regions: list[dict[str, Any]] = []

        top_level_entries = self.discovery.get("top_level_entries", [])

        for entry in top_level_entries:
            name = entry["name"]
            path = Path(name)

            if entry["type"] == "directory":
                classification, evidence = self._classify_repository_region(path)
                file_count = self._count_files(name)
                source_file_count = self._count_source_files(name)
            else:
                classification, evidence = self._classify_root_file(path)
                file_count = 1
                source_file_count = int(
                    path.suffix.lower() in SOURCE_SUFFIXES
                )

            regions.append(
                {
                    "path": name,
                    "entry_type": entry["type"],
                    "classification": classification,
                    "file_count": file_count,
                    "source_file_count": source_file_count,
                    "evidence": evidence,
                }
            )

        return sorted(regions, key=lambda item: item["path"].lower())

    def _classify_repository_region(
        self,
        path: Path,
    ) -> tuple[str, list[str]]:
        lowered = path.name.lower()
        evidence = [f"top-level directory name: {path.name}"]

        if lowered in ARCHIVE_DIRECTORY_MARKERS:
            return "archive_or_quarantine", evidence

        if lowered in GENERATED_DIRECTORY_MARKERS:
            return "generated_or_runtime_output", evidence

        if lowered in TEST_DIRECTORY_MARKERS:
            return "test", evidence

        if lowered in DOCUMENTATION_DIRECTORY_MARKERS:
            return "documentation", evidence

        if lowered in SCRIPT_DIRECTORY_MARKERS:
            return "tooling_or_scripts", evidence

        if lowered in CONFIG_DIRECTORY_MARKERS:
            return "configuration_or_automation", evidence

        if lowered == "frontend":
            return "frontend_application_region", evidence

        if lowered == "backend":
            return "backend_application_region", evidence

        source_count = self._count_source_files(path.as_posix())

        if source_count > 0:
            evidence.append(f"contains {source_count} source files")
            return "unclassified_source_region", evidence

        return "unclassified_repository_region", evidence

    def _classify_root_file(
        self,
        path: Path,
    ) -> tuple[str, list[str]]:
        name = path.name.lower()
        suffix = path.suffix.lower()

        evidence = [f"top-level file: {path.name}"]

        if self._is_generated_or_report_file(path):
            return "generated_report_or_artifact", evidence

        if suffix in SOURCE_SUFFIXES:
            return "root_source_or_tooling_file", evidence

        if name in {
            "docker-compose.yml",
            "docker-compose.yaml",
            "compose.yml",
            "compose.yaml",
            "pytest.ini",
            "pyproject.toml",
            "package.json",
            "tsconfig.json",
        }:
            return "root_configuration", evidence

        if suffix in {".md", ".rst", ".txt"}:
            return "root_documentation", evidence

        if suffix in {".png", ".svg", ".jpg", ".jpeg", ".webp"}:
            return "generated_visual_artifact", evidence

        if suffix in {".json", ".yaml", ".yml", ".toml", ".ini"}:
            return "root_structured_data_or_configuration", evidence

        return "unclassified_root_file", evidence

    def _map_candidate_layers(self) -> list[dict[str, Any]]:
        grouped: dict[str, dict[str, Any]] = {}

        for directory in self.directories:
            path = Path(directory)

            if self._is_archived_path(path):
                layer = "archive_or_quarantine"
                evidence = ["path contains archive or quarantine marker"]
            elif self._is_generated_path(path):
                layer = "generated_or_output"
                evidence = ["path contains generated or output marker"]
            elif self._contains_marker(path, TEST_DIRECTORY_MARKERS):
                layer = "test"
                evidence = ["path contains test marker"]
            elif self._contains_marker(path, DOCUMENTATION_DIRECTORY_MARKERS):
                layer = "documentation"
                evidence = ["path contains documentation marker"]
            elif self._contains_marker(path, API_DIRECTORY_MARKERS):
                layer = "api_or_transport"
                evidence = ["path contains API, route, handler, or controller marker"]
            elif self._contains_marker(path, PRESENTATION_DIRECTORY_MARKERS):
                layer = "presentation"
                evidence = ["path contains frontend, UI, page, view, or component marker"]
            elif self._contains_marker(path, SECURITY_DIRECTORY_MARKERS):
                layer = "security_or_identity"
                evidence = ["path contains authentication, identity, or security marker"]
            elif self._contains_marker(path, CONTRACT_DIRECTORY_MARKERS):
                layer = "contracts_or_types"
                evidence = ["path contains contract, DTO, schema, interface, or type marker"]
            elif self._contains_marker(path, DOMAIN_DIRECTORY_MARKERS):
                layer = "domain_or_model"
                evidence = ["path contains domain, entity, model, or value-object marker"]
            elif self._contains_marker(path, SERVICE_DIRECTORY_MARKERS):
                layer = "application_or_service"
                evidence = ["path contains service, facade, application, or use-case marker"]
            elif self._contains_marker(path, INFRASTRUCTURE_DIRECTORY_MARKERS):
                layer = "infrastructure_or_integration"
                evidence = ["path contains adapter, database, provider, or repository marker"]
            elif self._contains_marker(path, RUNTIME_DIRECTORY_MARKERS):
                layer = "runtime_or_execution"
                evidence = ["path contains runtime, engine, worker, or execution marker"]
            elif self._contains_marker(path, STATE_DIRECTORY_MARKERS):
                layer = "state_management"
                evidence = ["path contains state or store marker"]
            elif self._contains_marker(path, SCRIPT_DIRECTORY_MARKERS):
                layer = "tooling_or_scripts"
                evidence = ["path contains script, tool, or bin marker"]
            else:
                layer = "unclassified"
                evidence = ["no known layer marker was found"]

            group = grouped.setdefault(
                layer,
                {
                    "layer": layer,
                    "directories": [],
                    "file_count": 0,
                    "source_file_count": 0,
                    "evidence": set(),
                },
            )

            group["directories"].append(directory)
            group["file_count"] += self._count_direct_files(directory)
            group["source_file_count"] += self._count_direct_source_files(directory)
            group["evidence"].update(evidence)

        results: list[dict[str, Any]] = []

        for layer, group in sorted(grouped.items()):
            directories = sorted(group["directories"])

            results.append(
                {
                    "layer": layer,
                    "directory_count": len(directories),
                    "file_count": group["file_count"],
                    "source_file_count": group["source_file_count"],
                    "directories": directories,
                    "evidence": sorted(group["evidence"]),
                }
            )

        return results

    def _discover_framework_signals(self) -> list[dict[str, Any]]:
        signals: list[dict[str, Any]] = []

        path_set = {record["path"] for record in self.files}

        framework_rules = [
            (
                "FastAPI_or_Python_API",
                {
                    "backend/app/main.py",
                },
            ),
            (
                "Next.js",
                {
                    "frontend/package.json",
                    "frontend/app/page.tsx",
                },
            ),
            (
                "Docker_Compose",
                {
                    "docker-compose.yml",
                    "docker-compose.yaml",
                    "compose.yml",
                    "compose.yaml",
                },
            ),
            (
                "Pytest",
                {
                    "pytest.ini",
                    "pyproject.toml",
                },
            ),
        ]

        for framework_name, evidence_paths in framework_rules:
            found = sorted(path_set.intersection(evidence_paths))

            if found:
                signals.append(
                    {
                        "framework_or_system": framework_name,
                        "confidence": (
                            "high"
                            if len(found) >= 2
                            else "medium"
                        ),
                        "evidence": found,
                    }
                )

        suffix_counts = Counter(
            record.get("suffix") or "<none>"
            for record in self.files
        )

        if suffix_counts[".py"] > 0:
            signals.append(
                {
                    "framework_or_system": "Python",
                    "confidence": "high",
                    "evidence": [
                        f"{suffix_counts['.py']} Python source files"
                    ],
                }
            )

        ts_count = (
            suffix_counts[".ts"]
            + suffix_counts[".tsx"]
            + suffix_counts[".js"]
            + suffix_counts[".jsx"]
            + suffix_counts[".mjs"]
        )

        if ts_count > 0:
            signals.append(
                {
                    "framework_or_system": "JavaScript_or_TypeScript",
                    "confidence": "high",
                    "evidence": [
                        f"{ts_count} JavaScript or TypeScript source files"
                    ],
                }
            )

        return sorted(
            signals,
            key=lambda item: item["framework_or_system"],
        )

    def _discover_boundary_signals(self) -> list[dict[str, Any]]:
        boundaries: list[dict[str, Any]] = []

        for directory in self.directories:
            path = Path(directory)
            parts = {part.lower() for part in path.parts}

            boundary_types: list[str] = []

            if parts.intersection(API_DIRECTORY_MARKERS):
                boundary_types.append("api_boundary")

            if parts.intersection(CONTRACT_DIRECTORY_MARKERS):
                boundary_types.append("contract_boundary")

            if parts.intersection(INFRASTRUCTURE_DIRECTORY_MARKERS):
                boundary_types.append("external_or_persistence_boundary")

            if parts.intersection(SECURITY_DIRECTORY_MARKERS):
                boundary_types.append("security_boundary")

            if "frontend" in parts and "api" in parts:
                boundary_types.append("frontend_server_boundary")

            if boundary_types:
                boundaries.append(
                    {
                        "path": directory,
                        "boundary_types": sorted(set(boundary_types)),
                        "direct_file_count": self._count_direct_files(directory),
                        "direct_source_file_count": self._count_direct_source_files(
                            directory
                        ),
                    }
                )

        return sorted(boundaries, key=lambda item: item["path"])

    def _discover_ambiguous_regions(
        self,
        candidate_layers: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        ambiguous: list[dict[str, Any]] = []

        for layer in candidate_layers:
            if layer["layer"] != "unclassified":
                continue

            for directory in layer["directories"]:
                source_count = self._count_direct_source_files(directory)
                file_count = self._count_direct_files(directory)

                if source_count == 0:
                    continue

                ambiguous.append(
                    {
                        "path": directory,
                        "direct_file_count": file_count,
                        "direct_source_file_count": source_count,
                        "reason": (
                            "Source-bearing directory has no recognized "
                            "layer classification marker."
                        ),
                    }
                )

        return sorted(
            ambiguous,
            key=lambda item: (
                -item["direct_source_file_count"],
                item["path"],
            ),
        )

    def _build_ownership_summary(
        self,
        repository_regions: list[dict[str, Any]],
        candidate_layers: list[dict[str, Any]],
    ) -> dict[str, Any]:
        region_counts = Counter(
            region["classification"]
            for region in repository_regions
        )

        layer_source_counts = {
            layer["layer"]: layer["source_file_count"]
            for layer in candidate_layers
        }

        active_source_files = 0
        archived_source_files = 0
        generated_source_files = 0

        for record in self.files:
            if not record.get("is_source"):
                continue

            path = Path(record["path"])

            if self._is_archived_path(path):
                archived_source_files += 1
            elif self._is_generated_path(path) or self._is_generated_or_report_file(path):
                generated_source_files += 1
            else:
                active_source_files += 1

        return {
            "repository_region_classification_counts": dict(
                sorted(region_counts.items())
            ),
            "candidate_layer_source_counts": dict(
                sorted(
                    layer_source_counts.items(),
                    key=lambda item: (-item[1], item[0]),
                )
            ),
            "source_ownership_estimate": {
                "active_source_files": active_source_files,
                "archived_or_quarantined_source_files": archived_source_files,
                "generated_or_report_source_files": generated_source_files,
            },
        }

    def _count_files(self, prefix: str) -> int:
        normalized = prefix.rstrip("/") + "/"

        return sum(
            1
            for record in self.files
            if record["path"] == prefix
            or record["path"].startswith(normalized)
        )

    def _count_source_files(self, prefix: str) -> int:
        if prefix == ".":
            return sum(
                1
                for record in self.files
                if record.get("is_source")
                and "/" not in record["path"]
            )

        normalized = prefix.rstrip("/") + "/"

        return sum(
            1
            for record in self.files
            if record.get("is_source")
            and (
                record["path"] == prefix
                or record["path"].startswith(normalized)
            )
        )

    def _count_direct_files(self, directory: str) -> int:
        return len(self.files_by_directory.get(directory, []))

    def _count_direct_source_files(self, directory: str) -> int:
        return sum(
            1
            for record in self.files_by_directory.get(directory, [])
            if record.get("is_source")
        )

    @staticmethod
    def _contains_marker(
        path: Path,
        markers: set[str],
    ) -> bool:
        return bool(
            {part.lower() for part in path.parts}.intersection(markers)
        )

    def _is_archived_path(self, path: Path) -> bool:
        return self._contains_marker(path, ARCHIVE_DIRECTORY_MARKERS)

    def _is_generated_path(self, path: Path) -> bool:
        return self._contains_marker(path, GENERATED_DIRECTORY_MARKERS)

    @staticmethod
    def _is_generated_or_report_file(path: Path) -> bool:
        lowered = path.name.lower()

        if any(marker in lowered for marker in GENERATED_FILENAME_MARKERS):
            return True

        if (
            path.suffix.lower() in {".json", ".png", ".svg"}
            and any(marker in lowered for marker in REPORT_FILENAME_MARKERS)
        ):
            return True

        return False
