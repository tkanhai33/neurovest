#!/usr/bin/env python3

"""
Hardening Workstream 1
Pass 4A — Review Queue Evidence Audit

Read-only inspection of modules placed in the Pass 4 review queue.

This audit determines whether each review candidate is:

- ALREADY_USED_INDIRECTLY
- COMPOSITION_ROOT_CANDIDATE
- INTERNAL_HELPER
- DUPLICATE_IMPLEMENTATION
- DORMANT_BUT_VALID
- MISSING_RUNTIME_WIRING
- ROUTER_INTENTIONALLY_DISABLED
- OWNERSHIP_REVIEW_REQUIRED

No application source is modified.
"""

from __future__ import annotations

import ast
import json
import re
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]

WORKSTREAM_DIR = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream1"
)

CLASSIFICATION_REPORT = (
    WORKSTREAM_DIR
    / "classification"
    / "repository_classification_latest.json"
)

REACHABILITY_REPORT = (
    WORKSTREAM_DIR
    / "reachability"
    / "reachability_audit_latest.json"
)

OUTPUT_DIR = (
    WORKSTREAM_DIR
    / "review_queue"
)

HISTORY_DIR = (
    WORKSTREAM_DIR
    / "history"
)

LATEST_JSON = (
    OUTPUT_DIR
    / "review_queue_evidence_latest.json"
)

LATEST_TEXT = (
    OUTPUT_DIR
    / "review_queue_evidence_latest.txt"
)

LATEST_CSV = (
    OUTPUT_DIR
    / "review_queue_evidence_latest.csv"
)

LEDGER = (
    ROOT
    / "handoff"
    / "hardening"
    / "WORKSTREAM_1_LEDGER.md"
)

ALLOWED_RESULTS = {
    "ALREADY_USED_INDIRECTLY",
    "COMPOSITION_ROOT_CANDIDATE",
    "INTERNAL_HELPER",
    "DUPLICATE_IMPLEMENTATION",
    "DORMANT_BUT_VALID",
    "MISSING_RUNTIME_WIRING",
    "ROUTER_INTENTIONALLY_DISABLED",
    "OWNERSHIP_REVIEW_REQUIRED",
}


class ReviewAuditFailure(RuntimeError):
    pass


def load_json(
    path: Path,
) -> dict[str, Any]:
    if not path.is_file():
        raise ReviewAuditFailure(
            f"Required report missing: {path.relative_to(ROOT)}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def module_name_from_path(
    path: Path,
) -> str:
    parts = list(
        path.relative_to(ROOT).parts
    )

    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = path.stem

    return ".".join(parts)


def discover_python_files() -> list[Path]:
    files = []

    for root in [
        ROOT / "backend",
        ROOT / "scripts",
    ]:
        if not root.is_dir():
            continue

        for path in root.rglob("*.py"):
            if any(
                part in {
                    ".git",
                    ".venv",
                    "__pycache__",
                    "node_modules",
                }
                for part in path.parts
            ):
                continue

            files.append(path)

    return sorted(files)


def parse_tree(
    path: Path,
) -> ast.Module:
    return ast.parse(
        path.read_text(
            encoding="utf-8",
            errors="replace",
        ),
        filename=path.as_posix(),
    )


def import_records(
    tree: ast.Module,
) -> list[dict[str, Any]]:
    records = []

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                records.append(
                    {
                        "module": alias.name,
                        "symbol": None,
                        "line": node.lineno,
                        "kind": "import",
                    }
                )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            base = node.module or ""

            for alias in node.names:
                records.append(
                    {
                        "module": base,
                        "symbol": alias.name,
                        "line": node.lineno,
                        "kind": "from",
                    }
                )

    return records


def defined_symbols(
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
            symbols.append(node.name)

        elif isinstance(
            node,
            ast.Assign,
        ):
            for target in node.targets:
                if isinstance(
                    target,
                    ast.Name,
                ):
                    symbols.append(target.id)

        elif isinstance(
            node,
            ast.AnnAssign,
        ):
            if isinstance(
                node.target,
                ast.Name,
            ):
                symbols.append(
                    node.target.id
                )

    return sorted(
        set(symbols)
    )


def public_callables(
    tree: ast.Module,
) -> list[str]:
    names = []

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
                names.append(node.name)

    return sorted(names)


def module_signals(
    path: Path,
    tree: ast.Module,
    source: str,
) -> dict[str, Any]:
    lowered = source.lower()

    decorators = []

    for node in ast.walk(tree):
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            for decorator in node.decorator_list:
                try:
                    decorators.append(
                        ast.unparse(decorator)
                    )
                except Exception:
                    pass

    has_router = any(
        isinstance(node, ast.Call)
        and (
            (
                isinstance(node.func, ast.Name)
                and node.func.id == "APIRouter"
            )
            or (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "APIRouter"
            )
        )
        for node in ast.walk(tree)
    )

    has_websocket = (
        "websocket" in lowered
        or any(
            "websocket" in item.lower()
            for item in decorators
        )
    )

    has_disabled_marker = any(
        marker in lowered
        for marker in [
            "disabled",
            "not enabled",
            "future phase",
            "future implementation",
            "placeholder",
            "stub",
            "deferred",
        ]
    )

    has_runtime_words = any(
        word in path.name.lower()
        for word in [
            "runtime",
            "service",
            "router",
            "registry",
            "orchestrator",
        ]
    )

    has_provider_words = any(
        word in path.name.lower()
        for word in [
            "provider",
            "adapter",
            "ingestor",
            "cache",
        ]
    )

    has_side_effects = False

    harmless = (
        ast.Import,
        ast.ImportFrom,
        ast.FunctionDef,
        ast.AsyncFunctionDef,
        ast.ClassDef,
        ast.Pass,
    )

    for node in tree.body:
        if isinstance(node, harmless):
            continue

        if isinstance(
            node,
            ast.Assign,
        ) and isinstance(
            node.value,
            (
                ast.Constant,
                ast.Dict,
                ast.List,
                ast.Tuple,
                ast.Set,
            ),
        ):
            continue

        has_side_effects = True
        break

    return {
        "has_router": has_router,
        "has_websocket": has_websocket,
        "has_disabled_marker": (
            has_disabled_marker
        ),
        "has_runtime_words": (
            has_runtime_words
        ),
        "has_provider_words": (
            has_provider_words
        ),
        "has_top_level_side_effects": (
            has_side_effects
        ),
        "decorators": sorted(
            set(decorators)
        ),
    }


def normalized_candidates(
    module: str,
) -> set[str]:
    values = {
        module,
    }

    aliases = [
        ("backend.app.", "app."),
        ("backend.app.stacks.", "stacks."),
        ("backend.app.core.", "core."),
        ("backend.app.api.", "api."),
        ("backend.app.analysis.", "analysis."),
    ]

    for source, destination in aliases:
        if module.startswith(source):
            values.add(
                destination
                + module[len(source):]
            )

    return values


def find_inbound_references(
    *,
    target_module: str,
    target_symbols: list[str],
    parsed_files: dict[
        str,
        dict[str, Any],
    ],
    target_path: str,
) -> list[dict[str, Any]]:
    references = []
    module_candidates = normalized_candidates(
        target_module
    )

    for source_module, details in (
        parsed_files.items()
    ):
        if details["path"] == target_path:
            continue

        for record in details[
            "imports"
        ]:
            imported_module = record[
                "module"
            ]

            symbol = record[
                "symbol"
            ]

            matched = False
            match_type = None

            if imported_module in module_candidates:
                matched = True
                match_type = "MODULE_IMPORT"

            elif symbol:
                full_name = (
                    f"{imported_module}.{symbol}"
                    if imported_module
                    else symbol
                )

                if full_name in module_candidates:
                    matched = True
                    match_type = "CHILD_MODULE_IMPORT"

                elif (
                    imported_module
                    in module_candidates
                    and symbol
                    in target_symbols
                ):
                    matched = True
                    match_type = "SYMBOL_IMPORT"

            if matched:
                references.append(
                    {
                        "source_module": (
                            source_module
                        ),
                        "source_path": (
                            details["path"]
                        ),
                        "line": record["line"],
                        "kind": record["kind"],
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


def duplicate_candidates(
    *,
    target: dict[str, Any],
    all_candidates: list[
        dict[str, Any]
    ],
) -> list[dict[str, Any]]:
    target_symbols = set(
        target["public_callables"]
    )

    if not target_symbols:
        return []

    duplicates = []

    for other in all_candidates:
        if other["path"] == target["path"]:
            continue

        other_symbols = set(
            other["public_callables"]
        )

        overlap = sorted(
            target_symbols
            & other_symbols
        )

        if not overlap:
            continue

        similarity = (
            len(overlap)
            / max(
                len(target_symbols),
                len(other_symbols),
            )
        )

        if similarity >= 0.5:
            duplicates.append(
                {
                    "path": other["path"],
                    "module": other["module"],
                    "overlapping_symbols": (
                        overlap
                    ),
                    "symbol_similarity": round(
                        similarity,
                        3,
                    ),
                }
            )

    return sorted(
        duplicates,
        key=lambda item: (
            -item["symbol_similarity"],
            item["path"],
        ),
    )[:10]


def decide_result(
    *,
    original_classification: str,
    path: str,
    signals: dict[str, Any],
    inbound: list[dict[str, Any]],
    duplicates: list[dict[str, Any]],
    public_symbols: list[str],
) -> tuple[
    str,
    list[str],
    str,
]:
    reasons = []

    active_backend_inbound = [
        item
        for item in inbound
        if item["source_path"].startswith(
            "backend/app/"
        )
        and "/test" not in item[
            "source_path"
        ]
    ]

    if active_backend_inbound:
        result = "ALREADY_USED_INDIRECTLY"

        reasons.append(
            "Referenced by active backend modules even though "
            "it is not reachable from backend.app.main."
        )

        action = (
            "Preserve module. Review why its callers are also "
            "outside the active composition graph."
        )

    elif duplicates:
        result = "DUPLICATE_IMPLEMENTATION"

        reasons.append(
            "Shares a substantial public-symbol surface with "
            "another review-queue module."
        )

        action = (
            "Compare implementations and ownership before wiring "
            "or archival."
        )

    elif original_classification == (
        "ROUTER_NOT_COMPOSED"
    ):
        if signals[
            "has_disabled_marker"
        ]:
            result = (
                "ROUTER_INTENTIONALLY_DISABLED"
            )

            reasons.append(
                "Router contains disabled, deferred, stub, "
                "or future-phase language."
            )

            action = (
                "Keep router uncomposed until its explicit phase "
                "or contract enables it."
            )

        else:
            result = (
                "COMPOSITION_ROOT_CANDIDATE"
            )

            reasons.append(
                "Declares an API router with no active composition."
            )

            action = (
                "Inspect endpoint safety and ownership before "
                "including the router."
            )

    elif original_classification == (
        "PROVIDER_ADAPTER"
    ):
        if signals[
            "has_provider_words"
        ]:
            result = "INTERNAL_HELPER"

            reasons.append(
                "Provider adapter is an internal implementation "
                "that should be reached through a provider registry "
                "or router rather than main.py."
            )

            action = (
                "Inspect provider registry composition. Do not "
                "wire the adapter directly into main.py."
            )

        else:
            result = (
                "OWNERSHIP_REVIEW_REQUIRED"
            )

            reasons.append(
                "Provider ownership could not be proven automatically."
            )

            action = (
                "Confirm the owning provider boundary."
            )

    elif signals["has_disabled_marker"]:
        result = "DORMANT_BUT_VALID"

        reasons.append(
            "Module contains explicit disabled, deferred, stub, "
            "placeholder, or future-phase signals."
        )

        action = (
            "Keep dormant. Do not compose until the planned "
            "feature phase begins."
        )

    elif (
        signals["has_runtime_words"]
        and public_symbols
    ):
        result = (
            "COMPOSITION_ROOT_CANDIDATE"
        )

        reasons.append(
            "Module exposes a runtime/service/router/registry "
            "surface and has no active inbound references."
        )

        action = (
            "Inspect contract and compose through the owning "
            "stack facade only if currently required."
        )

    elif public_symbols:
        result = "INTERNAL_HELPER"

        reasons.append(
            "Module exposes reusable public symbols but lacks "
            "evidence that it is a composition boundary."
        )

        action = (
            "Preserve as a helper. Wire only through an owning "
            "runtime or service."
        )

    else:
        result = (
            "OWNERSHIP_REVIEW_REQUIRED"
        )

        reasons.append(
            "No public composition surface or inbound usage "
            "was identified."
        )

        action = (
            "Inspect architectural ownership and history."
        )

    if result not in ALLOWED_RESULTS:
        raise ReviewAuditFailure(
            f"Unexpected review result: {result}"
        )

    return (
        result,
        reasons,
        action,
    )


def csv_escape(
    value: object,
) -> str:
    text = str(value).replace(
        '"',
        '""',
    )

    return f'"{text}"'


def main() -> int:
    started_at = datetime.now(UTC)

    classification = load_json(
        CLASSIFICATION_REPORT
    )

    reachability = load_json(
        REACHABILITY_REPORT
    )

    if classification.get("pass") != 4:
        raise ReviewAuditFailure(
            "Latest classification report is not Pass 4."
        )

    review_queue = classification.get(
        "review_queue",
        [],
    )

    if not review_queue:
        raise ReviewAuditFailure(
            "Pass 4 review queue is empty."
        )

    python_files = discover_python_files()

    parsed_files: dict[
        str,
        dict[str, Any],
    ] = {}

    syntax_errors = []

    for path in python_files:
        relative_path = path.relative_to(
            ROOT
        ).as_posix()

        module = module_name_from_path(
            path
        )

        try:
            tree = parse_tree(path)

        except SyntaxError as exc:
            syntax_errors.append(
                {
                    "path": relative_path,
                    "line": exc.lineno,
                    "message": exc.msg,
                }
            )

            continue

        source = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        parsed_files[module] = {
            "path": relative_path,
            "tree": tree,
            "source": source,
            "imports": import_records(
                tree
            ),
            "defined_symbols": (
                defined_symbols(tree)
            ),
            "public_callables": (
                public_callables(tree)
            ),
            "signals": module_signals(
                path,
                tree,
                source,
            ),
        }

    preliminary = []

    for item in review_queue:
        module = item["module"]
        relative_path = item["path"]

        details = parsed_files.get(
            module
        )

        if details is None:
            raise ReviewAuditFailure(
                f"Unable to parse review module: {relative_path}"
            )

        inbound = find_inbound_references(
            target_module=module,
            target_symbols=details[
                "defined_symbols"
            ],
            parsed_files=parsed_files,
            target_path=relative_path,
        )

        preliminary.append(
            {
                "path": relative_path,
                "module": module,
                "stack": item["stack"],
                "pass4_classification": item[
                    "classification"
                ],
                "line_count": len(
                    details[
                        "source"
                    ].splitlines()
                ),
                "defined_symbols": details[
                    "defined_symbols"
                ],
                "public_callables": details[
                    "public_callables"
                ],
                "signals": details[
                    "signals"
                ],
                "inbound_references": inbound,
                "active_backend_inbound_count": sum(
                    1
                    for reference in inbound
                    if reference[
                        "source_path"
                    ].startswith(
                        "backend/app/"
                    )
                    and "/test" not in reference[
                        "source_path"
                    ]
                ),
            }
        )

    results = []
    counts = Counter()
    stack_counts: dict[
        str,
        Counter,
    ] = defaultdict(Counter)

    for item in preliminary:
        duplicates = duplicate_candidates(
            target=item,
            all_candidates=preliminary,
        )

        result, reasons, action = (
            decide_result(
                original_classification=item[
                    "pass4_classification"
                ],
                path=item["path"],
                signals=item["signals"],
                inbound=item[
                    "inbound_references"
                ],
                duplicates=duplicates,
                public_symbols=item[
                    "public_callables"
                ],
            )
        )

        record = {
            **item,
            "review_result": result,
            "reasons": reasons,
            "duplicate_candidates": (
                duplicates
            ),
            "recommended_action": action,
            "source_modified": False,
        }

        results.append(record)
        counts[result] += 1
        stack_counts[
            item["stack"]
        ][result] += 1

    priority = {
        "COMPOSITION_ROOT_CANDIDATE": 1,
        "MISSING_RUNTIME_WIRING": 2,
        "ROUTER_INTENTIONALLY_DISABLED": 3,
        "ALREADY_USED_INDIRECTLY": 4,
        "INTERNAL_HELPER": 5,
        "DORMANT_BUT_VALID": 6,
        "DUPLICATE_IMPLEMENTATION": 7,
        "OWNERSHIP_REVIEW_REQUIRED": 8,
    }

    results.sort(
        key=lambda item: (
            priority[
                item["review_result"]
            ],
            item["stack"],
            item["path"],
        )
    )

    composition_candidates = [
        item
        for item in results
        if item["review_result"]
        in {
            "COMPOSITION_ROOT_CANDIDATE",
            "MISSING_RUNTIME_WIRING",
        }
    ]

    preserved_helpers = [
        item
        for item in results
        if item["review_result"]
        in {
            "ALREADY_USED_INDIRECTLY",
            "INTERNAL_HELPER",
            "DORMANT_BUT_VALID",
            "ROUTER_INTENTIONALLY_DISABLED",
        }
    ]

    manual_queue = [
        item
        for item in results
        if item["review_result"]
        in {
            "DUPLICATE_IMPLEMENTATION",
            "OWNERSHIP_REVIEW_REQUIRED",
        }
    ]

    completed_at = datetime.now(UTC)

    report = {
        "workstream": 1,
        "pass": "4A",
        "pass_name": (
            "Review Queue Evidence Audit"
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
        "files_deleted": False,
        "files_moved": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
        "summary": {
            "review_candidates": len(
                review_queue
            ),
            "reviewed_modules": len(
                results
            ),
            "composition_candidates": len(
                composition_candidates
            ),
            "preserved_helpers_or_dormant": len(
                preserved_helpers
            ),
            "manual_review_modules": len(
                manual_queue
            ),
            "syntax_errors": len(
                syntax_errors
            ),
        },
        "review_result_counts": dict(
            sorted(
                counts.items()
            )
        ),
        "stack_result_counts": {
            stack: dict(
                sorted(
                    counter.items()
                )
            )
            for stack, counter in sorted(
                stack_counts.items()
            )
        },
        "composition_candidates": (
            composition_candidates
        ),
        "preserved_helpers_or_dormant": (
            preserved_helpers
        ),
        "manual_review_queue": (
            manual_queue
        ),
        "syntax_errors": syntax_errors,
        "modules": results,
        "source_reports": {
            "classification_report": (
                CLASSIFICATION_REPORT
                .relative_to(ROOT)
                .as_posix()
            ),
            "reachability_report": (
                REACHABILITY_REPORT
                .relative_to(ROOT)
                .as_posix()
            ),
        },
        "next_action": (
            "Inspect composition candidates by stack, beginning "
            "with API/router and market-data ownership. No automatic "
            "runtime wiring is authorized."
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
            "review_queue_evidence_"
            f"{timestamp}.json"
        )
    ).write_text(
        serialized,
        encoding="utf-8",
    )

    csv_lines = [
        (
            "review_result,stack,path,module,"
            "pass4_classification,active_backend_inbound_count,"
            "public_callables,recommended_action"
        )
    ]

    for item in results:
        csv_lines.append(
            ",".join(
                [
                    csv_escape(
                        item[
                            "review_result"
                        ]
                    ),
                    csv_escape(
                        item["stack"]
                    ),
                    csv_escape(
                        item["path"]
                    ),
                    csv_escape(
                        item["module"]
                    ),
                    csv_escape(
                        item[
                            "pass4_classification"
                        ]
                    ),
                    csv_escape(
                        item[
                            "active_backend_inbound_count"
                        ]
                    ),
                    csv_escape(
                        ";".join(
                            item[
                                "public_callables"
                            ]
                        )
                    ),
                    csv_escape(
                        item[
                            "recommended_action"
                        ]
                    ),
                ]
            )
        )

    LATEST_CSV.write_text(
        "\n".join(
            csv_lines
        )
        + "\n",
        encoding="utf-8",
    )

    lines = [
        "=" * 80,
        "HARDENING WORKSTREAM 1",
        "PASS 4A — REVIEW QUEUE EVIDENCE AUDIT",
        "=" * 80,
        "",
        "MODE",
        "READ ONLY",
        "",
        "SUMMARY",
        (
            "Review candidates:                  "
            f"{report['summary']['review_candidates']}"
        ),
        (
            "Reviewed modules:                   "
            f"{report['summary']['reviewed_modules']}"
        ),
        (
            "Composition candidates:             "
            f"{report['summary']['composition_candidates']}"
        ),
        (
            "Preserved helpers/dormant:           "
            f"{report['summary']['preserved_helpers_or_dormant']}"
        ),
        (
            "Manual review modules:              "
            f"{report['summary']['manual_review_modules']}"
        ),
        (
            "Syntax errors:                      "
            f"{report['summary']['syntax_errors']}"
        ),
        "",
        "RESULT COUNTS",
    ]

    for result, count in sorted(
        counts.items()
    ):
        lines.append(
            f"- {result:<34} {count}"
        )

    lines.extend(
        [
            "",
            "STACK SUMMARY",
        ]
    )

    for stack, counter in sorted(
        stack_counts.items()
    ):
        lines.append(
            f"- {stack}"
        )

        for result, count in sorted(
            counter.items()
        ):
            lines.append(
                f"    {result:<32} {count}"
            )

    lines.extend(
        [
            "",
            "COMPOSITION CANDIDATES",
        ]
    )

    if composition_candidates:
        for item in composition_candidates:
            lines.append(
                f"- [{item['review_result']}] "
                f"{item['path']}"
            )
            lines.append(
                "    Public symbols: "
                + (
                    ", ".join(
                        item[
                            "public_callables"
                        ]
                    )
                    or "None"
                )
            )
            lines.append(
                "    Inbound active refs: "
                f"{item['active_backend_inbound_count']}"
            )
            lines.append(
                "    Action: "
                f"{item['recommended_action']}"
            )
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "MANUAL REVIEW QUEUE",
        ]
    )

    if manual_queue:
        for item in manual_queue:
            lines.append(
                f"- [{item['review_result']}] "
                f"{item['path']}"
            )

            if item[
                "duplicate_candidates"
            ]:
                lines.append(
                    "    Possible duplicates:"
                )

                for duplicate in item[
                    "duplicate_candidates"
                ]:
                    lines.append(
                        "      - "
                        f"{duplicate['path']} "
                        f"similarity="
                        f"{duplicate['symbol_similarity']}"
                    )
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "PRESERVED HELPERS OR DORMANT MODULES",
        ]
    )

    if preserved_helpers:
        for item in preserved_helpers:
            lines.append(
                f"- [{item['review_result']}] "
                f"{item['path']}"
            )
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "SAFETY",
            "Source modified:                    NO",
            "Runtime wiring changed:             NO",
            "Files deleted:                      NO",
            "Files moved:                        NO",
            "Broker execution enabled:           NO",
            "Live trading enabled:               NO",
            "",
            "NEXT",
            (
                "Inspect composition candidates by stack. "
                "Begin with API/router ownership and market-data "
                "provider composition."
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
            "review_queue_evidence_"
            f"{timestamp}.txt"
        )
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
            "## Pass 4A — Review Queue Evidence Audit\n"
            "\n"
            f"Audit time: `{completed_at.isoformat()}`\n"
            "\n"
            f"- Review candidates: "
            f"{len(review_queue)}\n"
            f"- Reviewed modules: "
            f"{len(results)}\n"
            f"- Composition candidates: "
            f"{len(composition_candidates)}\n"
            f"- Preserved helpers/dormant modules: "
            f"{len(preserved_helpers)}\n"
            f"- Manual review modules: "
            f"{len(manual_queue)}\n"
            f"- Syntax errors: "
            f"{len(syntax_errors)}\n"
            "- Source modified: **NO**\n"
            "- Runtime wiring changed: **NO**\n"
            "- Broker execution enabled: **NO**\n"
            "- Live trading enabled: **NO**\n"
            "\n"
            "### Evidence\n"
            "\n"
            "- `runtime/hardening/workstream1/review_queue/"
            "review_queue_evidence_latest.json`\n"
            "- `runtime/hardening/workstream1/review_queue/"
            "review_queue_evidence_latest.txt`\n"
            "- `runtime/hardening/workstream1/review_queue/"
            "review_queue_evidence_latest.csv`\n"
            "\n"
        )

    print(rendered)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(
            main()
        )

    except ReviewAuditFailure as exc:
        print("=" * 80)
        print("WORKSTREAM 1 PASS 4A BLOCKED")
        print("=" * 80)
        print()
        print(
            f"{type(exc).__name__}: {exc}"
        )
        print()
        print("No source files were modified.")
        print("No runtime wiring was changed.")
        print("Broker execution remains disabled.")
        print("Live trading remains disabled.")
        print("=" * 80)

        raise SystemExit(1)
