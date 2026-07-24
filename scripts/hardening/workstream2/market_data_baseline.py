#!/usr/bin/env python3

"""
WORKSTREAM 2
MARKET DATA RUNTIME AND PROVIDER COMPOSITION

Stage 1 — Existing Contract and Runtime Baseline

Read-only repository inspection.

Discovers:

- existing market-data modules
- contracts and protocols
- DTOs and schemas
- providers and adapters
- registries and routers
- caches
- session handling
- quote and historical-bar services
- API routes
- tests
- runtime entrypoint reachability
- scaffold files
- missing composition boundaries

No application source is modified.
"""

from __future__ import annotations

import ast
import hashlib
import json
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]

MARKET_ROOT = (
    ROOT
    / "backend"
    / "app"
    / "stacks"
    / "market_data"
)

BACKEND_ROOT = (
    ROOT
    / "backend"
    / "app"
)

OUTPUT_DIR = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream2"
    / "baseline"
)

HISTORY_DIR = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream2"
    / "history"
)

LATEST_JSON = (
    OUTPUT_DIR
    / "market_data_baseline_latest.json"
)

LATEST_TEXT = (
    OUTPUT_DIR
    / "market_data_baseline_latest.txt"
)

LEDGER = (
    ROOT
    / "handoff"
    / "hardening"
    / "WORKSTREAM_2_LEDGER.md"
)

ENTRYPOINT = "backend.app.main"

EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "backups",
}


class BaselineFailure(RuntimeError):
    pass


@dataclass(frozen=True)
class ModuleRecord:
    path: Path
    relative_path: str
    module: str
    inside_market_stack: bool
    is_test: bool


def rel(path: Path) -> str:
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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def discover_modules() -> list[ModuleRecord]:
    if not MARKET_ROOT.is_dir():
        raise BaselineFailure(
            "Market-data stack is missing: "
            f"{rel(MARKET_ROOT)}"
        )

    modules: list[ModuleRecord] = []

    for path in sorted(
        BACKEND_ROOT.rglob("*.py")
    ):
        if any(
            part in EXCLUDED_PARTS
            for part in path.parts
        ):
            continue

        relative_path = rel(path)

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

        modules.append(
            ModuleRecord(
                path=path,
                relative_path=relative_path,
                module=module_from_path(path),
                inside_market_stack=(
                    MARKET_ROOT in path.parents
                ),
                is_test=is_test,
            )
        )

    return modules


def parse_module(
    record: ModuleRecord,
) -> dict[str, Any]:
    source = record.path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    try:
        tree = ast.parse(
            source,
            filename=record.relative_path,
        )

    except SyntaxError as exc:
        return {
            "source": source,
            "tree": None,
            "syntax_error": {
                "line": exc.lineno,
                "offset": exc.offset,
                "message": exc.msg,
            },
        }

    return {
        "source": source,
        "tree": tree,
        "syntax_error": None,
    }


def imported_modules(
    tree: ast.Module,
) -> list[str]:
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    return sorted(set(imports))


def defined_symbols(
    tree: ast.Module,
) -> list[dict[str, Any]]:
    symbols = []

    for node in tree.body:
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
            ),
        ):
            symbols.append(
                {
                    "name": node.name,
                    "kind": type(node).__name__,
                    "line": node.lineno,
                    "public": (
                        not node.name.startswith("_")
                    ),
                    "docstring": ast.get_docstring(
                        node,
                        clean=True,
                    ),
                }
            )

        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    symbols.append(
                        {
                            "name": target.id,
                            "kind": "Assignment",
                            "line": node.lineno,
                            "public": (
                                not target.id.startswith("_")
                            ),
                            "docstring": None,
                        }
                    )

    return symbols


def class_bases(
    tree: ast.Module,
) -> dict[str, list[str]]:
    results = {}

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue

        bases = []

        for base in node.bases:
            try:
                bases.append(ast.unparse(base))
            except Exception:
                bases.append(
                    type(base).__name__
                )

        results[node.name] = bases

    return results


def function_names(
    tree: ast.Module,
) -> set[str]:
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
    }


def source_signals(
    path: str,
    source: str,
    tree: ast.Module,
) -> dict[str, Any]:
    lowered = source.lower()
    filename = Path(path).name.lower()

    symbols = defined_symbols(tree)
    names = {
        item["name"].lower()
        for item in symbols
    }

    bases = class_bases(tree)
    functions = function_names(tree)

    scaffold_markers = [
        "placeholder",
        "stub",
        "future phase",
        "not implemented",
        "todo",
        "scaffold",
        "disabled",
        "deferred",
    ]

    scaffold_hits = [
        marker
        for marker in scaffold_markers
        if marker in lowered
    ]

    has_only_healthcheck = (
        functions == {"healthcheck"}
    )

    has_protocol = any(
        "protocol" in base.lower()
        or "abc" in base.lower()
        for class_base_list in bases.values()
        for base in class_base_list
    ) or "typing.protocol" in lowered

    has_pydantic = (
        "basemodel" in lowered
        or "pydantic" in lowered
    )

    has_dataclass = (
        "@dataclass" in source
        or "dataclasses import dataclass"
        in lowered
    )

    has_router = (
        "apirouter" in lowered
    )

    has_http_client = any(
        token in lowered
        for token in [
            "httpx",
            "requests",
            "aiohttp",
            "urllib",
        ]
    )

    provider_signal = any(
        token in filename
        for token in [
            "provider",
            "adapter",
            "yfinance",
            "alpha_vantage",
            "alphavantage",
            "ingestor",
        ]
    )

    contract_signal = (
        has_protocol
        or any(
            token in filename
            for token in [
                "contract",
                "protocol",
                "interface",
                "base",
            ]
        )
    )

    dto_signal = (
        has_pydantic
        or has_dataclass
        or any(
            token in filename
            for token in [
                "dto",
                "schema",
                "model",
                "types",
            ]
        )
    )

    cache_signal = (
        "cache" in filename
        or any(
            token in names
            for token in [
                "get_cached",
                "set_cached",
                "clear_cache",
            ]
        )
    )

    registry_signal = (
        "registry" in filename
        or any(
            "register" in name
            for name in names
        )
    )

    router_signal = (
        "router" in filename
        or has_router
        or any(
            "route" in name
            for name in names
        )
    )

    session_signal = (
        "session" in filename
        or any(
            "session" in name
            for name in names
        )
    )

    quote_signal = any(
        token in lowered
        for token in [
            "quote",
            "last_price",
            "bid",
            "ask",
        ]
    )

    bars_signal = any(
        token in lowered
        for token in [
            "historical_bars",
            "ohlcv",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
        ]
    )

    return {
        "has_protocol": has_protocol,
        "has_pydantic": has_pydantic,
        "has_dataclass": has_dataclass,
        "has_router": has_router,
        "has_http_client": has_http_client,
        "provider_signal": provider_signal,
        "contract_signal": contract_signal,
        "dto_signal": dto_signal,
        "cache_signal": cache_signal,
        "registry_signal": registry_signal,
        "router_signal": router_signal,
        "session_signal": session_signal,
        "quote_signal": quote_signal,
        "bars_signal": bars_signal,
        "scaffold_markers": scaffold_hits,
        "has_only_healthcheck": (
            has_only_healthcheck
        ),
    }


def classify_module(
    record: ModuleRecord,
    signals: dict[str, Any],
) -> list[str]:
    categories = []

    if signals["contract_signal"]:
        categories.append("CONTRACT")

    if signals["dto_signal"]:
        categories.append("DTO_OR_SCHEMA")

    if signals["provider_signal"]:
        categories.append("PROVIDER_OR_ADAPTER")

    if signals["registry_signal"]:
        categories.append("REGISTRY")

    if signals["router_signal"]:
        categories.append("ROUTER")

    if signals["cache_signal"]:
        categories.append("CACHE")

    if signals["session_signal"]:
        categories.append("MARKET_SESSION")

    if signals["quote_signal"]:
        categories.append("QUOTE_CAPABILITY")

    if signals["bars_signal"]:
        categories.append(
            "HISTORICAL_BARS_CAPABILITY"
        )

    if record.is_test:
        categories.append("TEST")

    if (
        signals["has_only_healthcheck"]
        or signals["scaffold_markers"]
    ):
        categories.append("SCAFFOLD")

    if not categories:
        categories.append("UNCLASSIFIED")

    return sorted(set(categories))


def build_graph(
    parsed: dict[str, dict[str, Any]],
    module_index: dict[str, ModuleRecord],
) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = defaultdict(set)

    aliases = [
        ("app.", "backend.app."),
        ("stacks.", "backend.app.stacks."),
        ("core.", "backend.app.core."),
        ("api.", "backend.app.api."),
    ]

    for module, details in parsed.items():
        tree = details["tree"]

        if tree is None:
            continue

        for imported in imported_modules(tree):
            candidates = [imported]

            for source, destination in aliases:
                if imported.startswith(source):
                    candidates.append(
                        destination
                        + imported[len(source):]
                    )

            for candidate in candidates:
                if candidate in module_index:
                    graph[module].add(candidate)
                    break

    return graph


def reachable_from(
    graph: dict[str, set[str]],
    entrypoint: str,
) -> set[str]:
    visited = set()
    queue = deque([entrypoint])

    while queue:
        current = queue.popleft()

        if current in visited:
            continue

        visited.add(current)

        for target in sorted(
            graph.get(current, set())
        ):
            if target not in visited:
                queue.append(target)

    return visited


def main() -> int:
    started_at = datetime.now(UTC)

    modules = discover_modules()

    module_index = {
        record.module: record
        for record in modules
    }

    parsed = {}

    syntax_errors = []

    for record in modules:
        result = parse_module(record)
        parsed[record.module] = result

        if result["syntax_error"]:
            syntax_errors.append(
                {
                    "path": record.relative_path,
                    **result["syntax_error"],
                }
            )

    graph = build_graph(
        parsed,
        module_index,
    )

    reachable = reachable_from(
        graph,
        ENTRYPOINT,
    )

    records = []
    category_counts = Counter()
    stack_files = []

    for record in modules:
        if not record.inside_market_stack:
            continue

        details = parsed[record.module]

        if details["tree"] is None:
            records.append(
                {
                    "path": record.relative_path,
                    "module": record.module,
                    "categories": [
                        "SYNTAX_ERROR"
                    ],
                    "reachable_from_main": False,
                    "syntax_error": (
                        details["syntax_error"]
                    ),
                }
            )

            category_counts[
                "SYNTAX_ERROR"
            ] += 1

            continue

        tree = details["tree"]
        source = details["source"]

        signals = source_signals(
            record.relative_path,
            source,
            tree,
        )

        categories = classify_module(
            record,
            signals,
        )

        for category in categories:
            category_counts[category] += 1

        symbols = defined_symbols(tree)

        item = {
            "path": record.relative_path,
            "module": record.module,
            "categories": categories,
            "reachable_from_main": (
                record.module in reachable
            ),
            "is_test": record.is_test,
            "line_count": len(
                source.splitlines()
            ),
            "sha256": sha256_file(
                record.path
            ),
            "module_docstring": (
                ast.get_docstring(
                    tree,
                    clean=True,
                )
            ),
            "defined_symbols": symbols,
            "imports": imported_modules(
                tree
            ),
            "signals": signals,
            "syntax_error": None,
        }

        records.append(item)
        stack_files.append(item)

    expected_surfaces = {
        "provider_contract": any(
            "CONTRACT" in item["categories"]
            and "provider" in item["path"].lower()
            for item in stack_files
        ),
        "canonical_dto_surface": any(
            "DTO_OR_SCHEMA"
            in item["categories"]
            for item in stack_files
        ),
        "provider_registry": any(
            "REGISTRY" in item["categories"]
            for item in stack_files
        ),
        "provider_router": any(
            "ROUTER" in item["categories"]
            for item in stack_files
        ),
        "provider_cache": any(
            "CACHE" in item["categories"]
            for item in stack_files
        ),
        "market_session": any(
            "MARKET_SESSION"
            in item["categories"]
            for item in stack_files
        ),
        "quote_capability": any(
            "QUOTE_CAPABILITY"
            in item["categories"]
            for item in stack_files
        ),
        "historical_bars_capability": any(
            "HISTORICAL_BARS_CAPABILITY"
            in item["categories"]
            for item in stack_files
        ),
        "provider_adapter": any(
            "PROVIDER_OR_ADAPTER"
            in item["categories"]
            for item in stack_files
        ),
        "market_data_tests": any(
            "TEST" in item["categories"]
            for item in stack_files
        ),
        "runtime_reachability": any(
            item["reachable_from_main"]
            for item in stack_files
            if not item["is_test"]
        ),
    }

    scaffold_files = [
        item
        for item in stack_files
        if "SCAFFOLD" in item[
            "categories"
        ]
    ]

    reachable_files = [
        item
        for item in stack_files
        if item[
            "reachable_from_main"
        ]
    ]

    missing_surfaces = [
        name
        for name, present
        in expected_surfaces.items()
        if not present
    ]

    composition_blockers = []

    if scaffold_files:
        composition_blockers.append(
            {
                "code": (
                    "SCAFFOLD_SURFACES_PRESENT"
                ),
                "count": len(
                    scaffold_files
                ),
                "paths": [
                    item["path"]
                    for item
                    in scaffold_files
                ],
                "meaning": (
                    "One or more required market-data "
                    "surfaces are still healthcheck-only "
                    "or explicitly scaffolded."
                ),
            }
        )

    if not expected_surfaces[
        "provider_contract"
    ]:
        composition_blockers.append(
            {
                "code": (
                    "PROVIDER_CONTRACT_NOT_PROVEN"
                ),
                "count": 1,
                "paths": [],
                "meaning": (
                    "No canonical provider protocol or "
                    "contract was proven."
                ),
            }
        )

    if not expected_surfaces[
        "canonical_dto_surface"
    ]:
        composition_blockers.append(
            {
                "code": (
                    "CANONICAL_DTO_SURFACE_NOT_PROVEN"
                ),
                "count": 1,
                "paths": [],
                "meaning": (
                    "Canonical market-data DTO ownership "
                    "was not proven."
                ),
            }
        )

    if not expected_surfaces[
        "market_data_tests"
    ]:
        composition_blockers.append(
            {
                "code": (
                    "MARKET_DATA_TEST_SURFACE_NOT_PROVEN"
                ),
                "count": 1,
                "paths": [],
                "meaning": (
                    "No market-data test surface was "
                    "detected."
                ),
            }
        )

    completed_at = datetime.now(UTC)

    report = {
        "workstream": 2,
        "workstream_name": (
            "Market Data Runtime and "
            "Provider Composition"
        ),
        "stage": 1,
        "stage_name": (
            "Existing Contract and "
            "Runtime Baseline"
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
        "runtime_wiring_changed": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
        "summary": {
            "market_data_python_files": len(
                stack_files
            ),
            "reachable_from_main": len(
                reachable_files
            ),
            "scaffold_files": len(
                scaffold_files
            ),
            "syntax_errors": len(
                syntax_errors
            ),
            "missing_required_surfaces": len(
                missing_surfaces
            ),
            "composition_blockers": len(
                composition_blockers
            ),
        },
        "category_counts": dict(
            sorted(
                category_counts.items()
            )
        ),
        "expected_surfaces": (
            expected_surfaces
        ),
        "missing_surfaces": (
            missing_surfaces
        ),
        "composition_blockers": (
            composition_blockers
        ),
        "scaffold_files": scaffold_files,
        "reachable_files": (
            reachable_files
        ),
        "syntax_errors": (
            syntax_errors
        ),
        "modules": sorted(
            records,
            key=lambda item: (
                item["path"]
            ),
        ),
        "recommended_build_order": [
            {
                "order": 1,
                "stage": (
                    "Canonical market-data DTO "
                    "and contract verification"
                ),
            },
            {
                "order": 2,
                "stage": (
                    "Provider registry "
                    "implementation"
                ),
            },
            {
                "order": 3,
                "stage": (
                    "Provider cache "
                    "implementation"
                ),
            },
            {
                "order": 4,
                "stage": (
                    "Market-session "
                    "implementation"
                ),
            },
            {
                "order": 5,
                "stage": (
                    "Provider router "
                    "implementation"
                ),
            },
            {
                "order": 6,
                "stage": (
                    "Existing provider adapter "
                    "normalization"
                ),
            },
            {
                "order": 7,
                "stage": (
                    "Failure-behavior and "
                    "contract tests"
                ),
            },
            {
                "order": 8,
                "stage": (
                    "Composition-root wiring "
                    "after verification"
                ),
            },
        ],
        "next_action": (
            "Review the discovered contract, DTO, "
            "provider, registry, router, cache, session, "
            "and test surfaces before implementing Stage 2."
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

    serialized = (
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n"
    )

    LATEST_JSON.write_text(
        serialized,
        encoding="utf-8",
    )

    (
        HISTORY_DIR
        / (
            "market_data_baseline_"
            f"{timestamp}.json"
        )
    ).write_text(
        serialized,
        encoding="utf-8",
    )

    lines = [
        "=" * 80,
        "NEUROVEST WORKSTREAM 2",
        (
            "MARKET DATA RUNTIME AND "
            "PROVIDER COMPOSITION"
        ),
        "=" * 80,
        "",
        "STAGE 1",
        (
            "Existing Contract and "
            "Runtime Baseline"
        ),
        "",
        "MODE",
        "READ ONLY",
        "",
        "SUMMARY",
        (
            "Market-data Python files:          "
            f"{report['summary']['market_data_python_files']}"
        ),
        (
            "Reachable from main:               "
            f"{report['summary']['reachable_from_main']}"
        ),
        (
            "Scaffold files:                    "
            f"{report['summary']['scaffold_files']}"
        ),
        (
            "Syntax errors:                     "
            f"{report['summary']['syntax_errors']}"
        ),
        (
            "Missing required surfaces:         "
            f"{report['summary']['missing_required_surfaces']}"
        ),
        (
            "Composition blockers:              "
            f"{report['summary']['composition_blockers']}"
        ),
        "",
        "CATEGORY COUNTS",
    ]

    for category, count in report[
        "category_counts"
    ].items():
        lines.append(
            f"- {category:<35} {count}"
        )

    lines.extend(
        [
            "",
            "EXPECTED SURFACES",
        ]
    )

    for name, present in report[
        "expected_surfaces"
    ].items():
        lines.append(
            f"- {name:<35} "
            f"{'FOUND' if present else 'MISSING'}"
        )

    lines.extend(
        [
            "",
            "SCAFFOLD FILES",
        ]
    )

    if scaffold_files:
        for item in scaffold_files:
            lines.append(
                f"- {item['path']}"
            )
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "COMPOSITION BLOCKERS",
        ]
    )

    if composition_blockers:
        for blocker in composition_blockers:
            lines.append(
                f"- {blocker['code']}"
            )
            lines.append(
                f"    {blocker['meaning']}"
            )

            for path in blocker[
                "paths"
            ]:
                lines.append(
                    f"    - {path}"
                )
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "MARKET-DATA MODULE INVENTORY",
        ]
    )

    for item in report["modules"]:
        lines.append("")
        lines.append(
            f"- {item['path']}"
        )
        lines.append(
            "    Categories: "
            + ", ".join(
                item["categories"]
            )
        )
        lines.append(
            "    Reachable from main: "
            f"{str(item['reachable_from_main']).upper()}"
        )

        if item.get(
            "defined_symbols"
        ):
            public_symbols = [
                symbol["name"]
                for symbol in item[
                    "defined_symbols"
                ]
                if symbol["public"]
            ]

            lines.append(
                "    Public symbols: "
                + (
                    ", ".join(
                        public_symbols
                    )
                    or "None"
                )
            )

    lines.extend(
        [
            "",
            "RECOMMENDED BUILD ORDER",
            (
                "1. Canonical DTO and "
                "contract verification"
            ),
            "2. Provider registry",
            "3. Provider cache",
            "4. Market-session service",
            "5. Provider router",
            "6. Provider adapter normalization",
            "7. Failure-behavior tests",
            (
                "8. Composition-root wiring "
                "after verification"
            ),
            "",
            "SAFETY",
            "Source modified:                    NO",
            "Runtime wiring changed:             NO",
            "Broker execution enabled:           NO",
            "Live trading enabled:               NO",
            "",
            "NEXT",
            (
                "Stage 2 — Canonical Market-Data "
                "DTO and Provider Contract Verification"
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
        / (
            "market_data_baseline_"
            f"{timestamp}.txt"
        )
    ).write_text(
        rendered,
        encoding="utf-8",
    )

    LEDGER.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with LEDGER.open(
        "a",
        encoding="utf-8",
    ) as ledger:
        ledger.write(
            "\n"
            "# Workstream 2 — Market Data Runtime "
            "and Provider Composition\n"
            "\n"
            "## Stage 1 — Existing Contract "
            "and Runtime Baseline\n"
            "\n"
            f"Audit time: `{completed_at.isoformat()}`\n"
            "\n"
            f"- Market-data Python files: "
            f"{len(stack_files)}\n"
            f"- Reachable from main: "
            f"{len(reachable_files)}\n"
            f"- Scaffold files: "
            f"{len(scaffold_files)}\n"
            f"- Syntax errors: "
            f"{len(syntax_errors)}\n"
            f"- Missing required surfaces: "
            f"{len(missing_surfaces)}\n"
            f"- Composition blockers: "
            f"{len(composition_blockers)}\n"
            "- Source modified: **NO**\n"
            "- Runtime wiring changed: **NO**\n"
            "- Broker execution enabled: **NO**\n"
            "- Live trading enabled: **NO**\n"
            "\n"
            "### Evidence\n"
            "\n"
            "- `runtime/hardening/workstream2/"
            "baseline/market_data_baseline_latest.json`\n"
            "- `runtime/hardening/workstream2/"
            "baseline/market_data_baseline_latest.txt`\n"
            "\n"
        )

    print(rendered)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())

    except BaselineFailure as exc:
        print("=" * 80)
        print("WORKSTREAM 2 STAGE 1 BLOCKED")
        print("=" * 80)
        print()
        print(
            f"{type(exc).__name__}: {exc}"
        )
        print()
        print("No application source was modified.")
        print("Runtime wiring was not changed.")
        print("Broker execution remains disabled.")
        print("Live trading remains disabled.")
        print("=" * 80)

        raise SystemExit(1)
