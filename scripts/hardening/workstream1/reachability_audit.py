#!/usr/bin/env python3

"""
Hardening Workstream 1
Pass 3 — Module Reachability Analysis

Read-only repository inspection.

This audit determines which Python modules are reachable from known
runtime entrypoints and classifies modules that are not statically
reachable.

An unreachable module is not automatically dead code.

Possible classifications include:

- ENTRYPOINT
- ENTRYPOINT_REACHABLE
- DYNAMICALLY_REACHABLE
- MODEL_REGISTRATION_MODULE
- ROUTER_DECLARATION
- PACKAGE_SURFACE_ONLY
- TOOLING_ONLY
- TEST_ONLY
- ARCHIVED_OR_LEGACY
- UNREACHABLE_ACTIVE
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
from collections import defaultdict, deque
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
    / "reachability"
)

HISTORY_DIR = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream1"
    / "history"
)

LATEST_JSON = (
    OUTPUT_DIR
    / "reachability_audit_latest.json"
)

LATEST_TEXT = (
    OUTPUT_DIR
    / "reachability_audit_latest.txt"
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

PRIMARY_ENTRYPOINTS = {
    "backend.app.main",
}

EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
}

ARCHIVE_MARKERS = {
    "archive",
    "archived",
    "backup",
    "backups",
    "deprecated",
    "legacy",
    "old",
    "obsolete",
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
class ModuleInfo:
    module: str
    path: Path
    relative_path: str
    is_backend: bool
    is_active_backend: bool
    is_tooling: bool
    is_test: bool
    is_archived: bool
    is_package_init: bool


def relative(path: Path) -> str:
    return path.relative_to(
        ROOT
    ).as_posix()


def module_name(path: Path) -> str:
    parts = list(
        path.relative_to(ROOT).parts
    )

    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = path.stem

    return ".".join(parts)


def discover_modules() -> list[ModuleInfo]:
    modules = []

    for scan_root in SCAN_ROOTS:
        if not scan_root.is_dir():
            continue

        for path in sorted(
            scan_root.rglob("*.py")
        ):
            if any(
                part in EXCLUDED_PARTS
                for part in path.parts
            ):
                continue

            rel = relative(path)
            lowered_parts = {
                part.lower()
                for part in path.parts
            }

            is_test = (
                path.name.startswith("test_")
                or path.name.endswith("_test.py")
                or "tests" in lowered_parts
                or "test" in lowered_parts
            )

            is_archived = bool(
                lowered_parts
                & ARCHIVE_MARKERS
            )

            is_backend = rel.startswith(
                "backend/"
            )

            is_active_backend = (
                rel.startswith(
                    "backend/app/"
                )
                and not is_test
                and not is_archived
            )

            modules.append(
                ModuleInfo(
                    module=module_name(path),
                    path=path,
                    relative_path=rel,
                    is_backend=is_backend,
                    is_active_backend=(
                        is_active_backend
                    ),
                    is_tooling=rel.startswith(
                        "scripts/"
                    ),
                    is_test=is_test,
                    is_archived=is_archived,
                    is_package_init=(
                        path.name
                        == "__init__.py"
                    ),
                )
            )

    return modules


def alias_candidates(
    requested: str,
) -> list[str]:
    candidates = [requested]

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
        if requested == source[:-1]:
            candidates.append(
                destination[:-1]
            )

        elif requested.startswith(
            source
        ):
            candidates.append(
                destination
                + requested[len(source):]
            )

    return list(
        dict.fromkeys(candidates)
    )


def resolve_relative_import(
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


def parse_module(
    info: ModuleInfo,
    module_index: dict[
        str,
        ModuleInfo,
    ],
) -> dict[str, Any]:
    try:
        text = info.path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        tree = ast.parse(
            text,
            filename=info.relative_path,
        )

    except SyntaxError as exc:
        return {
            "static_targets": [],
            "dynamic_targets": [],
            "has_main_guard": False,
            "has_fastapi_app": False,
            "has_router": False,
            "has_sqlalchemy_models": False,
            "has_registration_function": False,
            "syntax_error": (
                f"line={exc.lineno} "
                f"message={exc.msg}"
            ),
        }

    static_targets: set[str] = set()
    dynamic_targets: set[str] = set()

    has_main_guard = False
    has_fastapi_app = False
    has_router = False
    has_sqlalchemy_models = False
    has_registration_function = False

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.Import,
        ):
            requested_modules = [
                alias.name
                for alias in node.names
            ]

            for requested in requested_modules:
                for candidate in alias_candidates(
                    requested
                ):
                    if candidate in module_index:
                        static_targets.add(
                            candidate
                        )
                        break

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            if node.level > 0:
                requested = (
                    resolve_relative_import(
                        current_module=(
                            info.module
                        ),
                        path=info.path,
                        imported_module=(
                            node.module
                        ),
                        level=node.level,
                    )
                )
            else:
                requested = (
                    node.module or ""
                )

            if requested is not None:
                base_candidates = (
                    alias_candidates(
                        requested
                    )
                )

                for alias in node.names:
                    candidates = []

                    if alias.name != "*":
                        candidates.extend(
                            f"{base}.{alias.name}"
                            for base
                            in base_candidates
                        )

                    candidates.extend(
                        base_candidates
                    )

                    for candidate in candidates:
                        if candidate in module_index:
                            static_targets.add(
                                candidate
                            )
                            break

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

            elif (
                isinstance(
                    node.func,
                    ast.Attribute,
                )
                and isinstance(
                    node.func.value,
                    ast.Name,
                )
            ):
                function_name = (
                    f"{node.func.value.id}."
                    f"{node.func.attr}"
                )

            if function_name in {
                "__import__",
                "importlib.import_module",
            }:
                if (
                    node.args
                    and isinstance(
                        node.args[0],
                        ast.Constant,
                    )
                    and isinstance(
                        node.args[0].value,
                        str,
                    )
                ):
                    requested = (
                        node.args[0].value
                    )

                    for candidate in alias_candidates(
                        requested
                    ):
                        if candidate in module_index:
                            dynamic_targets.add(
                                candidate
                            )
                            break

            if function_name in {
                "FastAPI",
                "fastapi.FastAPI",
            }:
                has_fastapi_app = True

            if function_name in {
                "APIRouter",
                "fastapi.APIRouter",
            }:
                has_router = True

        elif isinstance(
            node,
            ast.ClassDef,
        ):
            for base in node.bases:
                base_name = None

                if isinstance(
                    base,
                    ast.Name,
                ):
                    base_name = base.id

                elif isinstance(
                    base,
                    ast.Attribute,
                ):
                    base_name = base.attr

                if base_name in {
                    "Base",
                    "DeclarativeBase",
                }:
                    has_sqlalchemy_models = True

        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            lowered = node.name.lower()

            if (
                "register" in lowered
                or "registry" in lowered
            ):
                has_registration_function = True

        elif isinstance(
            node,
            ast.If,
        ):
            test = node.test

            if (
                isinstance(
                    test,
                    ast.Compare,
                )
                and isinstance(
                    test.left,
                    ast.Name,
                )
                and test.left.id
                == "__name__"
            ):
                has_main_guard = True

    return {
        "static_targets": sorted(
            static_targets
        ),
        "dynamic_targets": sorted(
            dynamic_targets
        ),
        "has_main_guard": has_main_guard,
        "has_fastapi_app": has_fastapi_app,
        "has_router": has_router,
        "has_sqlalchemy_models": (
            has_sqlalchemy_models
        ),
        "has_registration_function": (
            has_registration_function
        ),
        "syntax_error": None,
    }


def traverse(
    graph: dict[str, set[str]],
    entrypoints: set[str],
) -> set[str]:
    visited: set[str] = set()
    queue = deque(
        sorted(entrypoints)
    )

    while queue:
        module = queue.popleft()

        if module in visited:
            continue

        visited.add(module)

        for target in sorted(
            graph.get(
                module,
                set(),
            )
        ):
            if target not in visited:
                queue.append(target)

    return visited


def main() -> int:
    started_at = datetime.now(
        UTC
    )

    modules = discover_modules()

    module_index = {
        info.module: info
        for info in modules
    }

    parsed = {
        info.module: parse_module(
            info,
            module_index,
        )
        for info in modules
    }

    static_graph: dict[
        str,
        set[str],
    ] = defaultdict(set)

    dynamic_graph: dict[
        str,
        set[str],
    ] = defaultdict(set)

    detected_entrypoints = set(
        module
        for module in PRIMARY_ENTRYPOINTS
        if module in module_index
    )

    for module, details in parsed.items():
        static_graph[module].update(
            details["static_targets"]
        )

        dynamic_graph[module].update(
            details["dynamic_targets"]
        )

        info = module_index[module]

        if (
            details["has_main_guard"]
            and (
                info.is_tooling
                or module.endswith(".main")
                or module.endswith("_main")
            )
        ):
            detected_entrypoints.add(
                module
            )

        if details["has_fastapi_app"]:
            detected_entrypoints.add(
                module
            )

    runtime_entrypoints = {
        module
        for module in detected_entrypoints
        if (
            module.startswith(
                "backend."
            )
        )
    }

    if not runtime_entrypoints:
        raise RuntimeError(
            "No backend runtime entrypoint was detected."
        )

    statically_reachable = traverse(
        static_graph,
        runtime_entrypoints,
    )

    dynamically_reachable: set[str] = set()

    dynamic_sources = (
        statically_reachable
        | runtime_entrypoints
    )

    for source in dynamic_sources:
        dynamically_reachable.update(
            dynamic_graph.get(
                source,
                set(),
            )
        )

    expanded_reachable = set(
        statically_reachable
    )

    expanded_reachable.update(
        dynamically_reachable
    )

    if dynamically_reachable:
        expanded_reachable.update(
            traverse(
                static_graph,
                dynamically_reachable,
            )
        )

    classifications = []
    counts: dict[
        str,
        int,
    ] = defaultdict(int)

    for info in modules:
        details = parsed[
            info.module
        ]

        reasons = []

        if info.module in runtime_entrypoints:
            classification = "ENTRYPOINT"
            reasons.append(
                "Detected backend runtime entrypoint."
            )

        elif info.module in statically_reachable:
            classification = (
                "ENTRYPOINT_REACHABLE"
            )
            reasons.append(
                "Reachable through the static import graph."
            )

        elif info.module in expanded_reachable:
            classification = (
                "DYNAMICALLY_REACHABLE"
            )
            reasons.append(
                "Reachable through a literal dynamic import."
            )

        elif info.is_test:
            classification = "TEST_ONLY"
            reasons.append(
                "Located in a test scope or named as a test."
            )

        elif info.is_archived:
            classification = (
                "ARCHIVED_OR_LEGACY"
            )
            reasons.append(
                "Path contains an archive, backup, legacy, or obsolete marker."
            )

        elif info.is_tooling:
            classification = "TOOLING_ONLY"
            reasons.append(
                "Located under scripts/ and not part of backend runtime reachability."
            )

        elif (
            details[
                "has_sqlalchemy_models"
            ]
            or details[
                "has_registration_function"
            ]
        ):
            classification = (
                "MODEL_REGISTRATION_MODULE"
            )
            reasons.append(
                "Contains ORM models or explicit registration behavior."
            )

        elif details["has_router"]:
            classification = (
                "ROUTER_DECLARATION"
            )
            reasons.append(
                "Declares a FastAPI APIRouter but was not reached from current entrypoints."
            )

        elif info.is_package_init:
            classification = (
                "PACKAGE_SURFACE_ONLY"
            )
            reasons.append(
                "Package __init__ surface is not directly reachable."
            )

        elif info.is_active_backend:
            classification = (
                "UNREACHABLE_ACTIVE"
            )
            reasons.append(
                "Active backend module is not statically or dynamically reachable from detected runtime entrypoints."
            )

        else:
            classification = (
                "UNCLASSIFIED_NON_RUNTIME"
            )
            reasons.append(
                "Outside the active backend runtime scope."
            )

        counts[classification] += 1

        classifications.append(
            {
                "module": info.module,
                "path": info.relative_path,
                "classification": (
                    classification
                ),
                "reasons": reasons,
                "is_active_backend": (
                    info.is_active_backend
                ),
                "is_tooling": (
                    info.is_tooling
                ),
                "is_test": info.is_test,
                "is_archived": (
                    info.is_archived
                ),
                "is_package_init": (
                    info.is_package_init
                ),
                "static_dependencies": (
                    details[
                        "static_targets"
                    ]
                ),
                "dynamic_dependencies": (
                    details[
                        "dynamic_targets"
                    ]
                ),
                "has_router": (
                    details[
                        "has_router"
                    ]
                ),
                "has_sqlalchemy_models": (
                    details[
                        "has_sqlalchemy_models"
                    ]
                ),
                "has_registration_function": (
                    details[
                        "has_registration_function"
                    ]
                ),
                "syntax_error": (
                    details[
                        "syntax_error"
                    ]
                ),
            }
        )

    unreachable_active = [
        item
        for item in classifications
        if item["classification"]
        == "UNREACHABLE_ACTIVE"
    ]

    unreachable_routers = [
        item
        for item in classifications
        if item["classification"]
        == "ROUTER_DECLARATION"
    ]

    registration_modules = [
        item
        for item in classifications
        if item["classification"]
        == "MODEL_REGISTRATION_MODULE"
    ]

    syntax_errors = [
        item
        for item in classifications
        if item["syntax_error"]
    ]

    completed_at = datetime.now(
        UTC
    )

    report = {
        "workstream": 1,
        "pass": 3,
        "pass_name": (
            "Module Reachability Analysis"
        ),
        "status": "completed",
        "inspection_mode": "read_only",
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
        "entrypoints": sorted(
            runtime_entrypoints
        ),
        "summary": {
            "python_modules_scanned": len(
                modules
            ),
            "backend_runtime_entrypoints": len(
                runtime_entrypoints
            ),
            "statically_reachable_modules": len(
                statically_reachable
            ),
            "dynamically_reachable_modules": len(
                dynamically_reachable
            ),
            "expanded_reachable_modules": len(
                expanded_reachable
            ),
            "unreachable_active_modules": len(
                unreachable_active
            ),
            "unreachable_router_modules": len(
                unreachable_routers
            ),
            "model_registration_modules": len(
                registration_modules
            ),
            "syntax_errors": len(
                syntax_errors
            ),
        },
        "classification_counts": dict(
            sorted(
                counts.items()
            )
        ),
        "unreachable_active_modules": (
            unreachable_active
        ),
        "unreachable_router_modules": (
            unreachable_routers
        ),
        "model_registration_modules": (
            registration_modules
        ),
        "syntax_errors": syntax_errors,
        "modules": classifications,
        "next_action": (
            "Review unreachable active modules and router declarations "
            "before deciding whether they are dormant, obsolete, or "
            "missing composition-root wiring."
        ),
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
        / f"reachability_audit_{timestamp}.json"
    ).write_text(
        json_text,
        encoding="utf-8",
    )

    lines = [
        "=" * 80,
        "HARDENING WORKSTREAM 1",
        "PASS 3 — MODULE REACHABILITY ANALYSIS",
        "=" * 80,
        "",
        "MODE",
        "READ ONLY",
        "",
        "ENTRYPOINTS",
    ]

    for entrypoint in sorted(
        runtime_entrypoints
    ):
        lines.append(
            f"- {entrypoint}"
        )

    lines.extend(
        [
            "",
            "SUMMARY",
            (
                "Python modules scanned:             "
                f"{report['summary']['python_modules_scanned']}"
            ),
            (
                "Backend runtime entrypoints:       "
                f"{report['summary']['backend_runtime_entrypoints']}"
            ),
            (
                "Statically reachable modules:      "
                f"{report['summary']['statically_reachable_modules']}"
            ),
            (
                "Dynamically reachable modules:     "
                f"{report['summary']['dynamically_reachable_modules']}"
            ),
            (
                "Expanded reachable modules:        "
                f"{report['summary']['expanded_reachable_modules']}"
            ),
            (
                "Unreachable active modules:        "
                f"{report['summary']['unreachable_active_modules']}"
            ),
            (
                "Unreachable router modules:        "
                f"{report['summary']['unreachable_router_modules']}"
            ),
            (
                "Model-registration modules:        "
                f"{report['summary']['model_registration_modules']}"
            ),
            (
                "Syntax errors:                     "
                f"{report['summary']['syntax_errors']}"
            ),
            "",
            "CLASSIFICATION COUNTS",
        ]
    )

    for classification, count in report[
        "classification_counts"
    ].items():
        lines.append(
            f"- {classification:<32} "
            f"{count}"
        )

    lines.extend(
        [
            "",
            "UNREACHABLE ACTIVE MODULES",
        ]
    )

    if unreachable_active:
        for item in unreachable_active:
            lines.append(
                f"- {item['path']}"
            )
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "UNREACHABLE ROUTER DECLARATIONS",
        ]
    )

    if unreachable_routers:
        for item in unreachable_routers:
            lines.append(
                f"- {item['path']}"
            )
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "IMPORTANT",
            (
                "Unreachable does not mean dead. Each active module "
                "must be classified before deletion, movement, or wiring."
            ),
            "",
            "SOURCE MODIFIED",
            "NO",
            "",
            "NEXT",
            (
                "Classify unreachable active modules as dormant, "
                "legacy, registration-only, intentionally isolated, "
                "or missing runtime wiring."
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
        / f"reachability_audit_{timestamp}.txt"
    ).write_text(
        rendered,
        encoding="utf-8",
    )

    with LEDGER.open(
        "a",
        encoding="utf-8",
    ) as ledger:
        ledger.write(
            "\n"
            "## Pass 3 — Module Reachability Analysis\n"
            "\n"
            f"Audit time: `{completed_at.isoformat()}`\n"
            "\n"
            f"- Runtime entrypoints: "
            f"{len(runtime_entrypoints)}\n"
            f"- Statically reachable modules: "
            f"{len(statically_reachable)}\n"
            f"- Dynamically reachable modules: "
            f"{len(dynamically_reachable)}\n"
            f"- Unreachable active modules: "
            f"{len(unreachable_active)}\n"
            f"- Unreachable router declarations: "
            f"{len(unreachable_routers)}\n"
            f"- Model-registration modules: "
            f"{len(registration_modules)}\n"
            f"- Syntax errors: "
            f"{len(syntax_errors)}\n"
            "- Source modified: **NO**\n"
            "- Broker execution enabled: **NO**\n"
            "- Live trading enabled: **NO**\n"
            "\n"
            "### Evidence\n"
            "\n"
            "- `runtime/hardening/workstream1/reachability/"
            "reachability_audit_latest.json`\n"
            "- `runtime/hardening/workstream1/reachability/"
            "reachability_audit_latest.txt`\n"
            "\n"
        )

    print(rendered)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
