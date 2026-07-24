#!/usr/bin/env python3

"""
NeuroVest Workstream 2
Stage 4A — Scaffold Source and Compatibility Inspection

Read-only inspection of the market-data surfaces planned for Stage 4.

This inspection determines:

- exact scaffold contents
- current imports and callers
- public symbols
- callable signatures
- whether existing code depends on scaffold behavior
- yfinance adapter input and output shapes
- compatibility with canonical Stage 3 DTOs
- safe replacement boundaries for Stage 4

No source files are modified.
No runtime wiring is changed.
"""

from __future__ import annotations

import ast
import inspect
import json
from collections import Counter, defaultdict
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
    / "compatibility"
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
    / "stage4a_compatibility_latest.json"
)

LATEST_TEXT = (
    OUTPUT_DIR
    / "stage4a_compatibility_latest.txt"
)

LEDGER = (
    ROOT
    / "handoff"
    / "hardening"
    / "WORKSTREAM_2_LEDGER.md"
)

TARGET_FILES = [
    MARKET_ROOT / "provider_registry.py",
    MARKET_ROOT / "provider_cache.py",
    MARKET_ROOT / "market_session.py",
    MARKET_ROOT / "provider_router.py",
    MARKET_ROOT / "base.py",
    MARKET_ROOT / "price.py",
    MARKET_ROOT / "feed.py",
    MARKET_ROOT / "market_data_service.py",
    MARKET_ROOT / "bars.py",
    MARKET_ROOT / "yfinance_historical_bars_adapter.py",
    MARKET_ROOT / "yfinance_ingestor.py",
    MARKET_ROOT / "dto.py",
    MARKET_ROOT / "provider_contract.py",
]

STAGE4_PRIMARY_FILES = {
    "backend/app/stacks/market_data/provider_registry.py",
    "backend/app/stacks/market_data/provider_cache.py",
    "backend/app/stacks/market_data/market_session.py",
    "backend/app/stacks/market_data/provider_router.py",
}

PROTECTED_COMPATIBILITY_FILES = {
    "backend/app/stacks/market_data/base.py",
    "backend/app/stacks/market_data/price.py",
    "backend/app/stacks/market_data/feed.py",
    "backend/app/stacks/market_data/market_data_service.py",
    "backend/app/stacks/market_data/bars.py",
    "backend/app/stacks/market_data/yfinance_historical_bars_adapter.py",
    "backend/app/stacks/market_data/yfinance_ingestor.py",
}

EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "backups",
}


class CompatibilityInspectionFailure(RuntimeError):
    pass


def relative(path: Path) -> str:
    return path.relative_to(
        ROOT
    ).as_posix()


def module_from_path(path: Path) -> str:
    parts = list(
        path.relative_to(ROOT).parts
    )

    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = path.stem

    return ".".join(parts)


def read_source(path: Path) -> str:
    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def parse_source(path: Path) -> ast.Module:
    return ast.parse(
        read_source(path),
        filename=relative(path),
    )


def expression_text(
    node: ast.AST | None,
) -> str | None:
    if node is None:
        return None

    try:
        return ast.unparse(node)

    except Exception:
        return type(node).__name__


def callable_signatures(
    tree: ast.Module,
) -> list[dict[str, Any]]:
    records = []

    for node in tree.body:
        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
            ),
        ):
            continue

        if isinstance(node, ast.ClassDef):
            methods = []

            for child in node.body:
                if isinstance(
                    child,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                    ),
                ):
                    methods.append(
                        function_signature_record(
                            child
                        )
                    )

            records.append(
                {
                    "name": node.name,
                    "kind": "class",
                    "line": node.lineno,
                    "bases": [
                        expression_text(base)
                        for base in node.bases
                    ],
                    "methods": methods,
                    "docstring": ast.get_docstring(
                        node,
                        clean=True,
                    ),
                }
            )

        else:
            records.append(
                function_signature_record(
                    node
                )
            )

    return records


def function_signature_record(
    node: ast.FunctionDef
    | ast.AsyncFunctionDef,
) -> dict[str, Any]:
    positional = (
        list(node.args.posonlyargs)
        + list(node.args.args)
    )

    defaults = [
        None
    ] * (
        len(positional)
        - len(node.args.defaults)
    ) + list(node.args.defaults)

    parameters = []

    for argument, default in zip(
        positional,
        defaults,
    ):
        parameters.append(
            {
                "name": argument.arg,
                "annotation": (
                    expression_text(
                        argument.annotation
                    )
                ),
                "default": (
                    expression_text(default)
                ),
                "kind": "positional",
            }
        )

    if node.args.vararg:
        parameters.append(
            {
                "name": node.args.vararg.arg,
                "annotation": expression_text(
                    node.args.vararg.annotation
                ),
                "default": None,
                "kind": "vararg",
            }
        )

    for argument, default in zip(
        node.args.kwonlyargs,
        node.args.kw_defaults,
    ):
        parameters.append(
            {
                "name": argument.arg,
                "annotation": (
                    expression_text(
                        argument.annotation
                    )
                ),
                "default": (
                    expression_text(default)
                ),
                "kind": "keyword_only",
            }
        )

    if node.args.kwarg:
        parameters.append(
            {
                "name": node.args.kwarg.arg,
                "annotation": expression_text(
                    node.args.kwarg.annotation
                ),
                "default": None,
                "kind": "kwarg",
            }
        )

    return {
        "name": node.name,
        "kind": (
            "async_function"
            if isinstance(
                node,
                ast.AsyncFunctionDef,
            )
            else "function"
        ),
        "line": node.lineno,
        "parameters": parameters,
        "return_annotation": expression_text(
            node.returns
        ),
        "decorators": [
            expression_text(item)
            for item in node.decorator_list
        ],
        "docstring": ast.get_docstring(
            node,
            clean=True,
        ),
    }


def public_symbols(
    tree: ast.Module,
) -> list[str]:
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
            if not node.name.startswith("_"):
                symbols.append(node.name)

        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if (
                    isinstance(target, ast.Name)
                    and not target.id.startswith("_")
                ):
                    symbols.append(target.id)

        elif isinstance(node, ast.AnnAssign):
            if (
                isinstance(node.target, ast.Name)
                and not node.target.id.startswith("_")
            ):
                symbols.append(
                    node.target.id
                )

    return sorted(set(symbols))


def import_records(
    tree: ast.Module,
) -> list[dict[str, Any]]:
    records = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                records.append(
                    {
                        "module": alias.name,
                        "symbol": None,
                        "alias": alias.asname,
                        "line": node.lineno,
                        "kind": "import",
                    }
                )

        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                records.append(
                    {
                        "module": (
                            node.module or ""
                        ),
                        "symbol": alias.name,
                        "alias": alias.asname,
                        "line": node.lineno,
                        "kind": "from",
                        "level": node.level,
                    }
                )

    return records


def return_shapes(
    tree: ast.Module,
) -> list[dict[str, Any]]:
    records = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Return):
            continue

        value = node.value

        if value is None:
            shape = "None"

        elif isinstance(value, ast.Dict):
            keys = []

            for key in value.keys:
                if isinstance(
                    key,
                    ast.Constant,
                ):
                    keys.append(
                        str(key.value)
                    )
                else:
                    keys.append(
                        expression_text(key)
                    )

            shape = {
                "type": "dict",
                "keys": keys,
            }

        elif isinstance(value, ast.List):
            shape = {
                "type": "list",
                "length": len(
                    value.elts
                ),
            }

        elif isinstance(value, ast.Tuple):
            shape = {
                "type": "tuple",
                "length": len(
                    value.elts
                ),
            }

        elif isinstance(value, ast.Call):
            shape = {
                "type": "call",
                "callable": expression_text(
                    value.func
                ),
            }

        else:
            shape = {
                "type": type(
                    value
                ).__name__,
                "expression": (
                    expression_text(value)
                ),
            }

        records.append(
            {
                "line": node.lineno,
                "shape": shape,
            }
        )

    return records


def source_signals(
    source: str,
    tree: ast.Module,
) -> dict[str, Any]:
    lowered = source.lower()

    function_names = {
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

    scaffold_markers = [
        "placeholder",
        "stub",
        "future phase",
        "future implementation",
        "not implemented",
        "todo",
        "scaffold",
        "disabled",
        "deferred",
    ]

    return {
        "has_only_healthcheck": (
            function_names
            == {"healthcheck"}
        ),
        "scaffold_markers": [
            marker
            for marker in scaffold_markers
            if marker in lowered
        ],
        "uses_yfinance": (
            "yfinance" in lowered
            or "import yf" in lowered
        ),
        "uses_requests": (
            "requests" in lowered
        ),
        "uses_httpx": (
            "httpx" in lowered
        ),
        "uses_canonical_dto": (
            "market_data.dto"
            in lowered
        ),
        "uses_provider_contract": (
            "provider_contract"
            in lowered
        ),
        "contains_default_prices": (
            "default_prices"
            in lowered
        ),
        "contains_random_fallback": (
            "random" in lowered
        ),
        "contains_network_call": any(
            token in lowered
            for token in [
                ".download(",
                ".history(",
                "requests.get(",
                "httpx.get(",
                "client.get(",
            ]
        ),
    }


def discover_python_files() -> list[Path]:
    files = []

    for path in sorted(
        BACKEND_ROOT.rglob("*.py")
    ):
        if any(
            part in EXCLUDED_PARTS
            for part in path.parts
        ):
            continue

        files.append(path)

    return files


def normalized_module_candidates(
    module: str,
) -> set[str]:
    candidates = {
        module,
    }

    aliases = [
        (
            "backend.app.",
            "app.",
        ),
        (
            "backend.app.stacks.",
            "stacks.",
        ),
    ]

    for source, destination in aliases:
        if module.startswith(source):
            candidates.add(
                destination
                + module[len(source):]
            )

    return candidates


def inbound_references(
    *,
    target_module: str,
    target_symbols: list[str],
    parsed_repository: dict[
        str,
        dict[str, Any],
    ],
    target_path: str,
) -> list[dict[str, Any]]:
    references = []

    candidates = (
        normalized_module_candidates(
            target_module
        )
    )

    for source_module, details in (
        parsed_repository.items()
    ):
        if details["path"] == target_path:
            continue

        for record in details["imports"]:
            imported_module = record[
                "module"
            ]

            symbol = record.get(
                "symbol"
            )

            full_symbol = (
                f"{imported_module}.{symbol}"
                if imported_module
                and symbol
                else None
            )

            match_type = None

            if imported_module in candidates:
                match_type = "MODULE_IMPORT"

            elif (
                full_symbol
                and full_symbol in candidates
            ):
                match_type = (
                    "CHILD_MODULE_IMPORT"
                )

            elif (
                imported_module in candidates
                and symbol in target_symbols
            ):
                match_type = (
                    "SYMBOL_IMPORT"
                )

            if match_type:
                references.append(
                    {
                        "source_module": (
                            source_module
                        ),
                        "source_path": (
                            details["path"]
                        ),
                        "line": record["line"],
                        "match_type": (
                            match_type
                        ),
                        "imported_module": (
                            imported_module
                        ),
                        "symbol": symbol,
                    }
                )

    return sorted(
        references,
        key=lambda item: (
            item["source_path"],
            item["line"],
        ),
    )


def direct_symbol_references(
    *,
    symbols: list[str],
    repository_files: list[Path],
    target_path: str,
) -> list[dict[str, Any]]:
    if not symbols:
        return []

    results = []

    for path in repository_files:
        relative_path = relative(path)

        if relative_path == target_path:
            continue

        source = read_source(path)

        hits = []

        for line_number, line in enumerate(
            source.splitlines(),
            start=1,
        ):
            matched = [
                symbol
                for symbol in symbols
                if symbol in line
            ]

            if matched:
                hits.append(
                    {
                        "line": line_number,
                        "symbols": sorted(
                            set(matched)
                        ),
                        "text": (
                            line.strip()[:300]
                        ),
                    }
                )

            if len(hits) >= 20:
                break

        if hits:
            results.append(
                {
                    "path": relative_path,
                    "hits": hits,
                }
            )

    return results


def compatibility_status(
    record: dict[str, Any],
) -> dict[str, Any]:
    path = record["path"]
    inbound_count = len(
        record["inbound_references"]
    )

    symbols = set(
        record["public_symbols"]
    )

    signals = record["signals"]

    if path in STAGE4_PRIMARY_FILES:
        if inbound_count == 0:
            status = (
                "SAFE_TO_REPLACE_WITH_VERIFIED_IMPLEMENTATION"
            )

            reason = (
                "Stage 4 scaffold has no detected inbound "
                "backend imports."
            )

        else:
            status = (
                "IMPLEMENT_WITH_COMPATIBILITY_WRAPPER"
            )

            reason = (
                "Stage 4 scaffold has existing inbound "
                "references that must be preserved."
            )

    elif path.endswith(
        "/price.py"
    ):
        status = (
            "PROTECTED_EXISTING_RUNTIME_SURFACE"
        )

        reason = (
            "price.py is already part of the reachable "
            "runtime path and must not be overwritten in Stage 4."
        )

    elif path.endswith(
        "/base.py"
    ):
        if symbols == {"init"}:
            status = (
                "LEGACY_INITIALIZATION_SURFACE_REVIEW"
            )

            reason = (
                "base.py exposes an initialization function, "
                "not the canonical provider contract."
            )

        else:
            status = (
                "OWNERSHIP_REVIEW_REQUIRED"
            )

            reason = (
                "base.py contains behavior beyond the "
                "canonical provider contract."
            )

    elif (
        path.endswith(
            "yfinance_historical_bars_adapter.py"
        )
        or path.endswith(
            "yfinance_ingestor.py"
        )
    ):
        status = (
            "ADAPTER_NORMALIZATION_REQUIRED_LATER"
        )

        reason = (
            "Existing yfinance integration must remain unchanged "
            "until the registry, cache, session, and router are verified."
        )

    elif signals[
        "uses_canonical_dto"
    ]:
        status = (
            "CANONICAL_COMPATIBILITY_PRESENT"
        )

        reason = (
            "Module already imports the canonical DTO layer."
        )

    else:
        status = (
            "PRESERVE_UNTIL_INTEGRATION_STAGE"
        )

        reason = (
            "Module is not a Stage 4 scaffold and should "
            "remain unchanged during the next implementation."
        )

    return {
        "status": status,
        "reason": reason,
    }


def main() -> int:
    started_at = datetime.now(
        UTC
    )

    missing = [
        relative(path)
        for path in TARGET_FILES
        if not path.is_file()
    ]

    if missing:
        raise CompatibilityInspectionFailure(
            "Required market-data files are missing: "
            + ", ".join(missing)
        )

    repository_files = (
        discover_python_files()
    )

    parsed_repository: dict[
        str,
        dict[str, Any],
    ] = {}

    syntax_errors = []

    for path in repository_files:
        try:
            tree = parse_source(path)

        except SyntaxError as exc:
            syntax_errors.append(
                {
                    "path": relative(path),
                    "line": exc.lineno,
                    "message": exc.msg,
                }
            )

            continue

        parsed_repository[
            module_from_path(path)
        ] = {
            "path": relative(path),
            "imports": import_records(
                tree
            ),
        }

    records = []

    for path in TARGET_FILES:
        tree = parse_source(path)
        source = read_source(path)
        module = module_from_path(path)
        public = public_symbols(tree)

        inbound = inbound_references(
            target_module=module,
            target_symbols=public,
            parsed_repository=(
                parsed_repository
            ),
            target_path=relative(path),
        )

        symbol_refs = (
            direct_symbol_references(
                symbols=public,
                repository_files=(
                    repository_files
                ),
                target_path=relative(
                    path
                ),
            )
        )

        record = {
            "path": relative(path),
            "module": module,
            "line_count": len(
                source.splitlines()
            ),
            "module_docstring": (
                ast.get_docstring(
                    tree,
                    clean=True,
                )
            ),
            "public_symbols": public,
            "callable_signatures": (
                callable_signatures(
                    tree
                )
            ),
            "imports": import_records(
                tree
            ),
            "return_shapes": (
                return_shapes(tree)
            ),
            "signals": source_signals(
                source,
                tree,
            ),
            "inbound_references": (
                inbound
            ),
            "symbol_references": (
                symbol_refs
            ),
            "source_modified": False,
        }

        record[
            "compatibility"
        ] = compatibility_status(
            record
        )

        records.append(record)

    stage4_records = [
        record
        for record in records
        if record["path"]
        in STAGE4_PRIMARY_FILES
    ]

    protected_records = [
        record
        for record in records
        if record["path"]
        in PROTECTED_COMPATIBILITY_FILES
    ]

    safe_replace = [
        record
        for record in stage4_records
        if record[
            "compatibility"
        ]["status"]
        == (
            "SAFE_TO_REPLACE_WITH_VERIFIED_IMPLEMENTATION"
        )
    ]

    compatibility_wrappers = [
        record
        for record in stage4_records
        if record[
            "compatibility"
        ]["status"]
        == (
            "IMPLEMENT_WITH_COMPATIBILITY_WRAPPER"
        )
    ]

    yfinance_records = [
        record
        for record in records
        if "yfinance" in record[
            "path"
        ]
    ]

    adapter_contract_status = []

    for record in yfinance_records:
        signatures = {
            item["name"]
            for item in record[
                "callable_signatures"
            ]
            if item["kind"]
            in {
                "function",
                "async_function",
            }
        }

        required_provider_methods = {
            "supports",
            "get_quote",
            "get_historical_bars",
            "healthcheck",
        }

        adapter_contract_status.append(
            {
                "path": record["path"],
                "currently_satisfies_provider_contract": (
                    required_provider_methods
                    .issubset(signatures)
                ),
                "present_callable_names": sorted(
                    signatures
                ),
                "missing_provider_methods": sorted(
                    required_provider_methods
                    - signatures
                ),
                "uses_canonical_dto": record[
                    "signals"
                ]["uses_canonical_dto"],
            }
        )

    completed_at = datetime.now(
        UTC
    )

    report = {
        "workstream": 2,
        "stage": "4A",
        "stage_name": (
            "Scaffold Source and "
            "Compatibility Inspection"
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
            "files_inspected": len(
                records
            ),
            "stage4_primary_files": len(
                stage4_records
            ),
            "safe_to_replace": len(
                safe_replace
            ),
            "compatibility_wrappers_required": len(
                compatibility_wrappers
            ),
            "protected_existing_surfaces": len(
                protected_records
            ),
            "yfinance_adapter_files": len(
                yfinance_records
            ),
            "syntax_errors": len(
                syntax_errors
            ),
        },
        "safe_replacement_files": [
            record["path"]
            for record in safe_replace
        ],
        "compatibility_wrapper_files": [
            record["path"]
            for record
            in compatibility_wrappers
        ],
        "protected_files": [
            {
                "path": record[
                    "path"
                ],
                "status": record[
                    "compatibility"
                ]["status"],
                "reason": record[
                    "compatibility"
                ]["reason"],
            }
            for record
            in protected_records
        ],
        "adapter_contract_status": (
            adapter_contract_status
        ),
        "syntax_errors": syntax_errors,
        "files": records,
        "stage4_constraints": [
            (
                "Do not modify price.py during Stage 4."
            ),
            (
                "Do not modify feed.py, market_data_service.py, "
                "or bars.py during Stage 4."
            ),
            (
                "Do not normalize yfinance adapters until the "
                "registry, cache, session, and router pass focused tests."
            ),
            (
                "Preserve all detected public symbols and callers."
            ),
            (
                "Do not wire Stage 4 components into main.py yet."
            ),
            (
                "Broker execution and live trading remain disabled."
            ),
        ],
        "recommended_stage4_scope": [
            (
                "Implement provider_registry.py as an in-memory "
                "provider ownership registry."
            ),
            (
                "Implement provider_cache.py as a bounded TTL cache "
                "for canonical DTO results."
            ),
            (
                "Implement market_session.py as a deterministic "
                "session-state service."
            ),
            (
                "Implement provider_router.py as a provider-selection "
                "and fail-closed capability router."
            ),
            (
                "Add focused unit tests using fixture providers only."
            ),
            (
                "Leave external yfinance calls and main.py composition "
                "unchanged until Stage 5."
            ),
        ],
        "next_stage": (
            "Stage 4B — Provider Registry, Cache, "
            "Market Session, and Router Implementation"
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
            "stage4a_compatibility_"
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
            "STAGE 4A — SCAFFOLD SOURCE "
            "AND COMPATIBILITY INSPECTION"
        ),
        "=" * 80,
        "",
        "MODE",
        "READ ONLY",
        "",
        "SUMMARY",
        (
            "Files inspected:                    "
            f"{report['summary']['files_inspected']}"
        ),
        (
            "Stage 4 primary files:              "
            f"{report['summary']['stage4_primary_files']}"
        ),
        (
            "Safe to replace:                    "
            f"{report['summary']['safe_to_replace']}"
        ),
        (
            "Compatibility wrappers required:    "
            f"{report['summary']['compatibility_wrappers_required']}"
        ),
        (
            "Protected existing surfaces:        "
            f"{report['summary']['protected_existing_surfaces']}"
        ),
        (
            "Yfinance adapter files:             "
            f"{report['summary']['yfinance_adapter_files']}"
        ),
        (
            "Syntax errors:                      "
            f"{report['summary']['syntax_errors']}"
        ),
        "",
        "STAGE 4 PRIMARY FILES",
    ]

    for record in stage4_records:
        lines.extend(
            [
                "",
                f"- {record['path']}",
                (
                    "    Public symbols: "
                    + (
                        ", ".join(
                            record[
                                "public_symbols"
                            ]
                        )
                        or "None"
                    )
                ),
                (
                    "    Inbound imports: "
                    f"{len(record['inbound_references'])}"
                ),
                (
                    "    Compatibility status: "
                    f"{record['compatibility']['status']}"
                ),
                (
                    "    Reason: "
                    f"{record['compatibility']['reason']}"
                ),
            ]
        )

    lines.extend(
        [
            "",
            "PROTECTED EXISTING SURFACES",
        ]
    )

    for item in report[
        "protected_files"
    ]:
        lines.extend(
            [
                f"- {item['path']}",
                (
                    "    Status: "
                    f"{item['status']}"
                ),
                (
                    "    Reason: "
                    f"{item['reason']}"
                ),
            ]
        )

    lines.extend(
        [
            "",
            "YFINANCE CONTRACT COMPATIBILITY",
        ]
    )

    for item in adapter_contract_status:
        lines.extend(
            [
                f"- {item['path']}",
                (
                    "    Satisfies canonical provider contract: "
                    f"{str(item['currently_satisfies_provider_contract']).upper()}"
                ),
                (
                    "    Uses canonical DTOs: "
                    f"{str(item['uses_canonical_dto']).upper()}"
                ),
                (
                    "    Present callables: "
                    + (
                        ", ".join(
                            item[
                                "present_callable_names"
                            ]
                        )
                        or "None"
                    )
                ),
                (
                    "    Missing provider methods: "
                    + (
                        ", ".join(
                            item[
                                "missing_provider_methods"
                            ]
                        )
                        or "None"
                    )
                ),
            ]
        )

    lines.extend(
        [
            "",
            "STAGE 4 CONSTRAINTS",
        ]
    )

    for constraint in report[
        "stage4_constraints"
    ]:
        lines.append(
            f"- {constraint}"
        )

    lines.extend(
        [
            "",
            "APPROVED STAGE 4 SCOPE",
        ]
    )

    for item in report[
        "recommended_stage4_scope"
    ]:
        lines.append(
            f"- {item}"
        )

    lines.extend(
        [
            "",
            "SAFETY",
            "Source modified:                    NO",
            "Runtime wiring changed:             NO",
            "Broker execution enabled:           NO",
            "Live trading enabled:               NO",
            "",
            "NEXT",
            (
                "Stage 4B — Provider Registry, Cache, "
                "Market Session, and Router Implementation"
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
            "stage4a_compatibility_"
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
            "## Stage 4A — Scaffold Source "
            "and Compatibility Inspection\n"
            "\n"
            f"Completed: `{completed_at.isoformat()}`\n"
            "\n"
            f"- Files inspected: "
            f"{len(records)}\n"
            f"- Stage 4 primary files: "
            f"{len(stage4_records)}\n"
            f"- Safe replacement files: "
            f"{len(safe_replace)}\n"
            f"- Compatibility wrappers required: "
            f"{len(compatibility_wrappers)}\n"
            f"- Protected existing surfaces: "
            f"{len(protected_records)}\n"
            f"- Syntax errors: "
            f"{len(syntax_errors)}\n"
            "- Source modified: **NO**\n"
            "- Runtime wiring changed: **NO**\n"
            "- Broker execution enabled: **NO**\n"
            "- Live trading enabled: **NO**\n"
            "\n"
            "### Evidence\n"
            "\n"
            "- `runtime/hardening/workstream2/"
            "compatibility/stage4a_compatibility_latest.json`\n"
            "- `runtime/hardening/workstream2/"
            "compatibility/stage4a_compatibility_latest.txt`\n"
            "\n"
        )

    print(rendered)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())

    except CompatibilityInspectionFailure as exc:
        print("=" * 80)
        print("WORKSTREAM 2 STAGE 4A BLOCKED")
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
