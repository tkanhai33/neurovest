#!/usr/bin/env python3

from __future__ import annotations

import ast
import importlib.util
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]

OUTPUT_DIR = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream1"
)

HISTORY_DIR = OUTPUT_DIR / "history"

LATEST_JSON = (
    OUTPUT_DIR
    / "import_cycle_audit_latest.json"
)

LATEST_TEXT = (
    OUTPUT_DIR
    / "import_cycle_audit_latest.txt"
)

LEDGER = (
    ROOT
    / "handoff"
    / "hardening"
    / "WORKSTREAM_1_LEDGER.md"
)

SCAN_ROOTS = [
    ROOT / "backend",
    ROOT / "scripts",
]

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "backups",
    "architecture_backup",
}

INTERNAL_PREFIXES = {
    "backend",
    "app",
    "spine",
    "stacks",
    "services",
    "schemas",
    "routers",
    "api",
    "core",
    "analysis",
    "models",
    "snaptrade",
    "scripts",
}


@dataclass(frozen=True)
class SourceModule:
    path: Path
    relative_path: str
    module: str
    application_active: bool
    tooling: bool


def relative_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def module_from_path(path: Path) -> str:
    parts = list(
        path.relative_to(ROOT).parts
    )

    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = path.stem

    return ".".join(parts)


def discover_sources() -> list[SourceModule]:
    sources: list[SourceModule] = []

    for scan_root in SCAN_ROOTS:
        if not scan_root.is_dir():
            continue

        for path in sorted(
            scan_root.rglob("*.py")
        ):
            if any(
                part in EXCLUDED_DIRS
                for part in path.parts
            ):
                continue

            rel = relative_path(path)

            active = (
                rel.startswith("backend/app/")
                and "/tests/" not in rel
                and "/test/" not in rel
                and not path.name.startswith(
                    "test_"
                )
            )

            sources.append(
                SourceModule(
                    path=path,
                    relative_path=rel,
                    module=module_from_path(path),
                    application_active=active,
                    tooling=rel.startswith(
                        "scripts/"
                    ),
                )
            )

    return sources


def alias_candidates(
    module: str,
) -> list[str]:
    candidates = [module]

    aliases = [
        ("app.", "backend.app."),
        ("spine.", "backend.app.spine."),
        ("stacks.", "backend.app.stacks."),
        ("services.", "backend.app.services."),
        ("schemas.", "backend.app.schemas."),
        ("routers.", "backend.app.routers."),
        ("api.", "backend.app.api."),
        ("core.", "backend.app.core."),
        ("analysis.", "backend.app.analysis."),
        ("models.", "backend.app.models."),
        ("snaptrade.", "backend.app.snaptrade."),
    ]

    for source, destination in aliases:
        if module == source[:-1]:
            candidates.append(
                destination[:-1]
            )

        elif module.startswith(source):
            candidates.append(
                destination
                + module[len(source):]
            )

    return list(
        dict.fromkeys(candidates)
    )


def external_or_stdlib(
    module: str,
) -> bool:
    root = module.split(
        ".",
        1,
    )[0]

    if root in sys.stdlib_module_names:
        return True

    return root not in INTERNAL_PREFIXES


def resolve_relative(
    *,
    current_module: str,
    path: Path,
    imported_module: str | None,
    level: int,
) -> str | None:
    package = current_module

    if path.name != "__init__.py":
        package = current_module.rsplit(
            ".",
            1,
        )[0]

    target = "." * level

    if imported_module:
        target += imported_module

    try:
        return importlib.util.resolve_name(
            target,
            package,
        )
    except (
        ImportError,
        ValueError,
    ):
        return None


def parse_source(
    source: SourceModule,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    str | None,
]:
    try:
        text = source.path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        tree = ast.parse(
            text,
            filename=source.relative_path,
        )

    except SyntaxError as exc:
        return (
            [],
            [],
            (
                f"line={exc.lineno} "
                f"offset={exc.offset} "
                f"message={exc.msg}"
            ),
        )

    imports: list[
        dict[str, Any]
    ] = []

    dynamic_imports: list[
        dict[str, Any]
    ] = []

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                imports.append(
                    {
                        "kind": "import",
                        "module": alias.name,
                        "name": None,
                        "level": 0,
                        "line": node.lineno,
                    }
                )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            for alias in node.names:
                imports.append(
                    {
                        "kind": "from",
                        "module": node.module,
                        "name": alias.name,
                        "level": node.level,
                        "line": node.lineno,
                    }
                )

        elif isinstance(
            node,
            ast.Call,
        ):
            function_name = None

            if isinstance(
                node.func,
                ast.Name,
            ):
                function_name = (
                    node.func.id
                )

            elif isinstance(
                node.func,
                ast.Attribute,
            ):
                if isinstance(
                    node.func.value,
                    ast.Name,
                ):
                    function_name = (
                        f"{node.func.value.id}."
                        f"{node.func.attr}"
                    )

            if function_name in {
                "__import__",
                "importlib.import_module",
            }:
                literal_module = None

                if node.args:
                    argument = node.args[0]

                    if (
                        isinstance(
                            argument,
                            ast.Constant,
                        )
                        and isinstance(
                            argument.value,
                            str,
                        )
                    ):
                        literal_module = (
                            argument.value
                        )

                dynamic_imports.append(
                    {
                        "function": (
                            function_name
                        ),
                        "literal_module": (
                            literal_module
                        ),
                        "line": node.lineno,
                    }
                )

    return (
        imports,
        dynamic_imports,
        None,
    )


def classify_import(
    *,
    source: SourceModule,
    record: dict[str, Any],
    module_index: dict[
        str,
        SourceModule,
    ],
) -> dict[str, Any]:
    imported_module = (
        record["module"]
    )

    level = int(
        record["level"]
    )

    if level > 0:
        requested = resolve_relative(
            current_module=source.module,
            path=source.path,
            imported_module=imported_module,
            level=level,
        )

        if requested is None:
            return {
                **record,
                "requested_module": (
                    imported_module
                ),
                "resolved_module": None,
                "target_path": None,
                "classification": (
                    "RELATIVE_IMPORT_UNRESOLVED"
                ),
            }

    else:
        requested = (
            imported_module or ""
        )

    candidates = alias_candidates(
        requested
    )

    if (
        record["kind"] == "from"
        and record["name"] != "*"
    ):
        child_candidates = [
            f"{candidate}.{record['name']}"
            for candidate in candidates
        ]

        candidates = (
            child_candidates
            + candidates
        )

    for candidate in candidates:
        target = module_index.get(
            candidate
        )

        if target is None:
            continue

        return {
            **record,
            "requested_module": requested,
            "resolved_module": candidate,
            "target_path": (
                target.relative_path
            ),
            "classification": (
                "INTERNAL_RESOLVED"
                if candidate == requested
                else "INTERNAL_ALIAS_RESOLVED"
            ),
        }

    if external_or_stdlib(
        requested
    ):
        return {
            **record,
            "requested_module": requested,
            "resolved_module": None,
            "target_path": None,
            "classification": (
                "EXTERNAL_OR_STDLIB"
            ),
        }

    return {
        **record,
        "requested_module": requested,
        "resolved_module": None,
        "target_path": None,
        "classification": (
            "ACTIVE_INTERNAL_UNRESOLVED"
            if source.application_active
            else "TOOLING_INTERNAL_UNRESOLVED"
        ),
    }


def strongly_connected_components(
    graph: dict[
        str,
        set[str],
    ],
) -> list[list[str]]:
    index = 0
    indices: dict[
        str,
        int,
    ] = {}

    lowlinks: dict[
        str,
        int,
    ] = {}

    stack: list[str] = []
    on_stack: set[str] = set()
    components: list[
        list[str]
    ] = []

    def visit(node: str) -> None:
        nonlocal index

        indices[node] = index
        lowlinks[node] = index
        index += 1

        stack.append(node)
        on_stack.add(node)

        for neighbor in graph.get(
            node,
            set(),
        ):
            if neighbor not in indices:
                visit(neighbor)

                lowlinks[node] = min(
                    lowlinks[node],
                    lowlinks[neighbor],
                )

            elif neighbor in on_stack:
                lowlinks[node] = min(
                    lowlinks[node],
                    indices[neighbor],
                )

        if lowlinks[node] != indices[node]:
            return

        component = []

        while True:
            member = stack.pop()
            on_stack.remove(member)
            component.append(member)

            if member == node:
                break

        components.append(
            sorted(component)
        )

    nodes = set(graph)

    for targets in graph.values():
        nodes.update(targets)

    for node in sorted(nodes):
        if node not in indices:
            visit(node)

    return components


def main() -> int:
    started_at = datetime.now(
        UTC
    )

    sources = discover_sources()

    module_index = {
        source.module: source
        for source in sources
    }

    graph: dict[
        str,
        set[str],
    ] = defaultdict(set)

    classification_counts: dict[
        str,
        int,
    ] = defaultdict(int)

    unresolved_active = []
    unresolved_tooling = []
    dynamic_imports = []
    syntax_errors = []
    files = []

    for source in sources:
        (
            import_records,
            dynamic_records,
            syntax_error,
        ) = parse_source(source)

        classified_records = []

        if syntax_error:
            syntax_errors.append(
                {
                    "file": (
                        source.relative_path
                    ),
                    "error": syntax_error,
                }
            )

        for record in import_records:
            classified = classify_import(
                source=source,
                record=record,
                module_index=module_index,
            )

            classification = (
                classified[
                    "classification"
                ]
            )

            classification_counts[
                classification
            ] += 1

            classified_records.append(
                classified
            )

            if classification in {
                "INTERNAL_RESOLVED",
                "INTERNAL_ALIAS_RESOLVED",
            }:
                target = classified[
                    "resolved_module"
                ]

                if target:
                    graph[
                        source.module
                    ].add(target)

            elif classification == (
                "ACTIVE_INTERNAL_UNRESOLVED"
            ):
                unresolved_active.append(
                    {
                        "source_file": (
                            source.relative_path
                        ),
                        "source_module": (
                            source.module
                        ),
                        **classified,
                    }
                )

            elif classification in {
                "TOOLING_INTERNAL_UNRESOLVED",
                "RELATIVE_IMPORT_UNRESOLVED",
            }:
                unresolved_tooling.append(
                    {
                        "source_file": (
                            source.relative_path
                        ),
                        "source_module": (
                            source.module
                        ),
                        **classified,
                    }
                )

        for dynamic in dynamic_records:
            entry = {
                "source_file": (
                    source.relative_path
                ),
                "source_module": (
                    source.module
                ),
                "application_active": (
                    source.application_active
                ),
                "classification": (
                    "DYNAMIC_IMPORT_REFERENCE"
                ),
                **dynamic,
            }

            dynamic_imports.append(entry)

            classification_counts[
                "DYNAMIC_IMPORT_REFERENCE"
            ] += 1

        files.append(
            {
                "path": (
                    source.relative_path
                ),
                "module": source.module,
                "application_active": (
                    source.application_active
                ),
                "tooling": (
                    source.tooling
                ),
                "syntax_error": (
                    syntax_error
                ),
                "imports": (
                    classified_records
                ),
                "dynamic_imports": (
                    dynamic_records
                ),
            }
        )

    components = (
        strongly_connected_components(
            graph
        )
    )

    cycle_components = [
        component
        for component in components
        if len(component) > 1
    ]

    self_cycles = sorted(
        module
        for module, targets
        in graph.items()
        if module in targets
    )

    cycle_details = []

    for component in cycle_components:
        active_members = [
            module
            for module in component
            if (
                module in module_index
                and module_index[
                    module
                ].application_active
            )
        ]

        cycle_details.append(
            {
                "modules": component,
                "files": [
                    module_index[
                        module
                    ].relative_path
                    for module in component
                    if module in module_index
                ],
                "size": len(component),
                "active_members": (
                    active_members
                ),
                "contains_active_application_code": bool(
                    active_members
                ),
            }
        )

    active_cycles = [
        item
        for item in cycle_details
        if item[
            "contains_active_application_code"
        ]
    ]

    completed_at = datetime.now(
        UTC
    )

    summary = {
        "python_files": len(sources),
        "application_active_files": sum(
            1
            for source in sources
            if source.application_active
        ),
        "tooling_files": sum(
            1
            for source in sources
            if source.tooling
        ),
        "static_import_records": sum(
            len(file["imports"])
            for file in files
        ),
        "dynamic_import_records": len(
            dynamic_imports
        ),
        "active_internal_unresolved": len(
            unresolved_active
        ),
        "tooling_or_relative_unresolved": len(
            unresolved_tooling
        ),
        "syntax_errors": len(
            syntax_errors
        ),
        "dependency_graph_nodes": len(
            graph
        ),
        "dependency_graph_edges": sum(
            len(targets)
            for targets in graph.values()
        ),
        "cycle_components_total": len(
            cycle_components
        ),
        "active_cycle_components": len(
            active_cycles
        ),
        "self_cycles": len(
            self_cycles
        ),
    }

    report = {
        "workstream": 1,
        "workstream_name": (
            "Repository Connectivity Remediation"
        ),
        "passes": [
            {
                "pass": 1,
                "name": (
                    "Active Import Resolution Audit"
                ),
                "mode": "read_only",
            },
            {
                "pass": 2,
                "name": (
                    "Dependency-Cycle Verification"
                ),
                "mode": "read_only",
            },
        ],
        "status": "audit_completed",
        "started_at": (
            started_at.isoformat()
        ),
        "completed_at": (
            completed_at.isoformat()
        ),
        "duration_seconds": round(
            (
                completed_at
                - started_at
            ).total_seconds(),
            6,
        ),
        "source_modified": False,
        "runtime_executed": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
        "summary": summary,
        "classification_counts": dict(
            sorted(
                classification_counts.items()
            )
        ),
        "active_internal_unresolved": (
            unresolved_active
        ),
        "tooling_or_relative_unresolved": (
            unresolved_tooling
        ),
        "dynamic_imports": (
            dynamic_imports
        ),
        "syntax_errors": (
            syntax_errors
        ),
        "dependency_cycles": (
            cycle_details
        ),
        "active_dependency_cycles": (
            active_cycles
        ),
        "self_cycles": (
            self_cycles
        ),
        "files": files,
    }

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    HISTORY_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = completed_at.strftime(
        "%Y%m%dT%H%M%S.%fZ"
    )

    json_text = (
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n"
    )

    LATEST_JSON.write_text(
        json_text,
        encoding="utf-8",
    )

    (
        HISTORY_DIR
        / f"import_cycle_audit_{timestamp}.json"
    ).write_text(
        json_text,
        encoding="utf-8",
    )

    lines = [
        "=" * 80,
        "HARDENING WORKSTREAM 1",
        "REPOSITORY CONNECTIVITY REMEDIATION",
        "=" * 80,
        "",
        "PASS 1",
        "Active Import Resolution Audit",
        "",
        "PASS 2",
        "Dependency-Cycle Verification",
        "",
        "MODE",
        "READ ONLY",
        "",
        (
            "Python files scanned:                 "
            f"{summary['python_files']}"
        ),
        (
            "Active backend files:                "
            f"{summary['application_active_files']}"
        ),
        (
            "Tooling files:                       "
            f"{summary['tooling_files']}"
        ),
        (
            "Static import records:               "
            f"{summary['static_import_records']}"
        ),
        (
            "Dynamic import records:              "
            f"{summary['dynamic_import_records']}"
        ),
        (
            "Active internal unresolved:          "
            f"{summary['active_internal_unresolved']}"
        ),
        (
            "Tooling/relative unresolved:         "
            f"{summary['tooling_or_relative_unresolved']}"
        ),
        (
            "Syntax errors:                       "
            f"{summary['syntax_errors']}"
        ),
        (
            "Dependency graph nodes:              "
            f"{summary['dependency_graph_nodes']}"
        ),
        (
            "Dependency graph edges:              "
            f"{summary['dependency_graph_edges']}"
        ),
        (
            "Cycle components total:              "
            f"{summary['cycle_components_total']}"
        ),
        (
            "Active cycle components:             "
            f"{summary['active_cycle_components']}"
        ),
        (
            "Self cycles:                         "
            f"{summary['self_cycles']}"
        ),
        "",
        "CLASSIFICATION COUNTS",
    ]

    for classification, count in report[
        "classification_counts"
    ].items():
        lines.append(
            f"- {classification:<34} "
            f"{count}"
        )

    lines.extend(
        [
            "",
            "ACTIVE INTERNAL UNRESOLVED IMPORTS",
        ]
    )

    if unresolved_active:
        for item in unresolved_active:
            lines.append(
                f"- {item['source_file']}:"
                f"{item['line']} "
                f"requested="
                f"{item['requested_module']} "
                f"name={item['name']}"
            )
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "ACTIVE DEPENDENCY CYCLES",
        ]
    )

    if active_cycles:
        for index, cycle in enumerate(
            active_cycles,
            start=1,
        ):
            lines.append(
                f"Cycle {index} "
                f"size={cycle['size']}"
            )

            for module in cycle[
                "modules"
            ]:
                lines.append(
                    f"  - {module}"
                )
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "SOURCE MODIFIED",
            "NO",
            "",
            "NEXT",
            (
                "Review each active unresolved import "
                "and active dependency cycle before remediation."
            ),
            "",
            "=" * 80,
        ]
    )

    rendered = (
        "\n".join(lines)
        + "\n"
    )

    LATEST_TEXT.write_text(
        rendered,
        encoding="utf-8",
    )

    (
        HISTORY_DIR
        / f"import_cycle_audit_{timestamp}.txt"
    ).write_text(
        rendered,
        encoding="utf-8",
    )

    LEDGER.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    LEDGER.write_text(
        "\n".join(
            [
                "# Hardening Workstream 1 Ledger",
                "",
                "## Repository Connectivity Remediation",
                "",
                (
                    f"Audit time: "
                    f"`{completed_at.isoformat()}`"
                ),
                "",
                "### Pass 1 — Active Import Resolution",
                "",
                (
                    "- Active internal unresolved imports: "
                    f"{len(unresolved_active)}"
                ),
                (
                    "- Tooling or relative unresolved imports: "
                    f"{len(unresolved_tooling)}"
                ),
                "",
                "### Pass 2 — Dependency-Cycle Verification",
                "",
                (
                    "- Active application cycle components: "
                    f"{len(active_cycles)}"
                ),
                (
                    f"- Self cycles: "
                    f"{len(self_cycles)}"
                ),
                "",
                "### Safety State",
                "",
                "- Source modified: **NO**",
                "- Runtime executed: **NO**",
                "- Broker execution enabled: **NO**",
                "- Live trading enabled: **NO**",
                "",
                "### Evidence",
                "",
                (
                    "- `runtime/hardening/workstream1/"
                    "import_cycle_audit_latest.json`"
                ),
                (
                    "- `runtime/hardening/workstream1/"
                    "import_cycle_audit_latest.txt`"
                ),
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(rendered)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
