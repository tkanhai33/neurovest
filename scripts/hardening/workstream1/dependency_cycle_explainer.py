#!/usr/bin/env python3

"""
Hardening Workstream 1
Pass 2A — Dependency-Cycle Evidence Collection

Read-only inspection of the confirmed active dependency cycle.

The script:

- loads the latest Workstream 1 audit
- isolates confirmed active cycle modules
- parses imports between cycle members
- records imported symbols and line numbers
- detects TYPE_CHECKING guards
- detects local/lazy imports
- records top-level executable statements
- estimates edge risk and blast radius
- recommends the lowest-risk cycle edge to break

It does not modify application source.
"""

from __future__ import annotations

import ast
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]

WORKSTREAM_DIRECTORY = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream1"
)

HISTORY_DIRECTORY = (
    WORKSTREAM_DIRECTORY
    / "history"
)

SOURCE_AUDIT = (
    WORKSTREAM_DIRECTORY
    / "import_cycle_audit_latest.json"
)

LATEST_JSON = (
    WORKSTREAM_DIRECTORY
    / "cycle_explainer_latest.json"
)

LATEST_TEXT = (
    WORKSTREAM_DIRECTORY
    / "cycle_explainer_latest.txt"
)

LEDGER = (
    ROOT
    / "handoff"
    / "hardening"
    / "WORKSTREAM_1_LEDGER.md"
)


class CycleExplainerFailure(RuntimeError):
    pass


@dataclass(frozen=True)
class ModuleRecord:
    module: str
    path: Path
    relative_path: str


def load_source_audit() -> dict[str, Any]:
    if not SOURCE_AUDIT.is_file():
        raise CycleExplainerFailure(
            "Workstream 1 import-cycle audit is missing."
        )

    payload = json.loads(
        SOURCE_AUDIT.read_text(
            encoding="utf-8"
        )
    )

    if payload.get("workstream") != 1:
        raise CycleExplainerFailure(
            "The source audit does not belong to Workstream 1."
        )

    if payload.get("status") != "audit_completed":
        raise CycleExplainerFailure(
            "The source audit did not complete."
        )

    active_cycles = payload.get(
        "active_dependency_cycles",
        [],
    )

    if not active_cycles:
        raise CycleExplainerFailure(
            "No active dependency cycle was found."
        )

    return payload


def module_to_path(
    audit: dict[str, Any],
) -> dict[str, Path]:
    mapping: dict[str, Path] = {}

    for file_record in audit.get(
        "files",
        [],
    ):
        module = file_record.get(
            "module"
        )

        relative = file_record.get(
            "path"
        )

        if not module or not relative:
            continue

        mapping[module] = (
            ROOT
            / relative
        )

    return mapping


def resolve_relative_module(
    *,
    current_module: str,
    current_path: Path,
    imported_module: str | None,
    level: int,
) -> str | None:
    package_parts = current_module.split(".")

    if current_path.name != "__init__.py":
        package_parts = package_parts[:-1]

    if level > len(package_parts):
        return None

    base_parts = (
        package_parts[
            :len(package_parts) - level + 1
        ]
    )

    if imported_module:
        base_parts.extend(
            imported_module.split(".")
        )

    return ".".join(base_parts)


def normalize_import_target(
    *,
    current_module: str,
    current_path: Path,
    node: ast.Import | ast.ImportFrom,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    if isinstance(
        node,
        ast.Import,
    ):
        for alias in node.names:
            records.append(
                {
                    "requested_module": alias.name,
                    "imported_symbol": None,
                    "alias": alias.asname,
                    "line": node.lineno,
                    "kind": "import",
                    "level": 0,
                }
            )

        return records

    base_module = node.module

    if node.level > 0:
        base_module = resolve_relative_module(
            current_module=current_module,
            current_path=current_path,
            imported_module=node.module,
            level=node.level,
        )

    for alias in node.names:
        records.append(
            {
                "requested_module": (
                    base_module
                    or ""
                ),
                "imported_symbol": alias.name,
                "alias": alias.asname,
                "line": node.lineno,
                "kind": "from",
                "level": node.level,
            }
        )

    return records


def node_inside_type_checking(
    node: ast.AST,
    parents: dict[ast.AST, ast.AST],
) -> bool:
    current = node

    while current in parents:
        current = parents[current]

        if not isinstance(
            current,
            ast.If,
        ):
            continue

        test = current.test

        if isinstance(
            test,
            ast.Name,
        ) and test.id == "TYPE_CHECKING":
            return True

        if (
            isinstance(
                test,
                ast.Attribute,
            )
            and isinstance(
                test.value,
                ast.Name,
            )
            and test.value.id == "typing"
            and test.attr == "TYPE_CHECKING"
        ):
            return True

    return False


def node_inside_function(
    node: ast.AST,
    parents: dict[ast.AST, ast.AST],
) -> bool:
    current = node

    while current in parents:
        current = parents[current]

        if isinstance(
            current,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.Lambda,
            ),
        ):
            return True

    return False


def collect_parent_map(
    tree: ast.AST,
) -> dict[ast.AST, ast.AST]:
    parents: dict[
        ast.AST,
        ast.AST,
    ] = {}

    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(
            parent
        ):
            parents[child] = parent

    return parents


def top_level_side_effects(
    tree: ast.Module,
) -> list[dict[str, Any]]:
    side_effects = []

    harmless = (
        ast.Import,
        ast.ImportFrom,
        ast.FunctionDef,
        ast.AsyncFunctionDef,
        ast.ClassDef,
        ast.Pass,
    )

    for node in tree.body:
        if isinstance(
            node,
            harmless,
        ):
            continue

        if isinstance(
            node,
            ast.Assign,
        ):
            if isinstance(
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

        if isinstance(
            node,
            ast.AnnAssign,
        ):
            if node.value is None or isinstance(
                node.value,
                ast.Constant,
            ):
                continue

        side_effects.append(
            {
                "line": getattr(
                    node,
                    "lineno",
                    None,
                ),
                "node_type": type(
                    node
                ).__name__,
            }
        )

    return side_effects


def symbols_defined(
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
                    symbols.append(
                        target.id
                    )

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


def inspect_module(
    record: ModuleRecord,
    cycle_modules: set[str],
) -> dict[str, Any]:
    text = record.path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    tree = ast.parse(
        text,
        filename=record.relative_path,
    )

    parents = collect_parent_map(
        tree
    )

    internal_edges = []
    all_imports = []

    for node in ast.walk(tree):
        if not isinstance(
            node,
            (
                ast.Import,
                ast.ImportFrom,
            ),
        ):
            continue

        normalized = normalize_import_target(
            current_module=record.module,
            current_path=record.path,
            node=node,
        )

        for import_record in normalized:
            requested = import_record[
                "requested_module"
            ]

            possible_targets = [
                requested
            ]

            symbol = import_record.get(
                "imported_symbol"
            )

            if (
                import_record["kind"]
                == "from"
                and symbol
                and symbol != "*"
            ):
                possible_targets.insert(
                    0,
                    f"{requested}.{symbol}",
                )

            resolved_target = next(
                (
                    candidate
                    for candidate in possible_targets
                    if candidate in cycle_modules
                ),
                None,
            )

            enriched = {
                **import_record,
                "inside_type_checking": (
                    node_inside_type_checking(
                        node,
                        parents,
                    )
                ),
                "inside_function": (
                    node_inside_function(
                        node,
                        parents,
                    )
                ),
                "runtime_import": (
                    not node_inside_type_checking(
                        node,
                        parents,
                    )
                ),
                "lazy_import": (
                    node_inside_function(
                        node,
                        parents,
                    )
                ),
                "resolved_cycle_target": (
                    resolved_target
                ),
            }

            all_imports.append(
                enriched
            )

            if resolved_target:
                internal_edges.append(
                    enriched
                )

    return {
        "module": record.module,
        "path": record.relative_path,
        "line_count": len(
            text.splitlines()
        ),
        "defined_symbols": (
            symbols_defined(tree)
        ),
        "top_level_side_effects": (
            top_level_side_effects(tree)
        ),
        "all_imports": all_imports,
        "cycle_imports": internal_edges,
    }


def edge_score(
    edge: dict[str, Any],
    source_module: dict[str, Any],
    target_module: dict[str, Any],
) -> dict[str, Any]:
    score = 100
    reasons = []

    if edge["inside_type_checking"]:
        score -= 70
        reasons.append(
            "Import is guarded by TYPE_CHECKING."
        )

    if edge["lazy_import"]:
        score -= 35
        reasons.append(
            "Import is already local to a function."
        )

    if edge["imported_symbol"] is not None:
        score -= 10
        reasons.append(
            "Import targets a specific symbol."
        )

    source_side_effects = len(
        source_module[
            "top_level_side_effects"
        ]
    )

    target_side_effects = len(
        target_module[
            "top_level_side_effects"
        ]
    )

    if source_side_effects == 0:
        score -= 10
        reasons.append(
            "Source module has no detected top-level side effects."
        )

    if target_side_effects == 0:
        score -= 10
        reasons.append(
            "Target module has no detected top-level side effects."
        )

    score = max(
        0,
        score,
    )

    if edge["inside_type_checking"]:
        recommendation = (
            "Confirm the imported symbol is used only for typing, "
            "then preserve it behind TYPE_CHECKING with postponed annotations."
        )

    elif not edge["lazy_import"]:
        recommendation = (
            "Candidate for conversion to a local import, protocol, "
            "factory injection, or lower-level contract."
        )

    else:
        recommendation = (
            "Already lazy; inspect whether the dependency can be "
            "replaced with an injected callable or protocol."
        )

    return {
        "break_risk_score": score,
        "lower_is_safer": True,
        "reasons": reasons,
        "candidate_repair": recommendation,
    }


def main() -> int:
    started_at = datetime.now(
        UTC
    )

    audit = load_source_audit()

    cycle = audit[
        "active_dependency_cycles"
    ][0]

    cycle_modules = set(
        cycle["modules"]
    )

    path_mapping = module_to_path(
        audit
    )

    module_records = []

    for module in sorted(
        cycle_modules
    ):
        path = path_mapping.get(
            module
        )

        if path is None:
            raise CycleExplainerFailure(
                f"No source path found for cycle module: {module}"
            )

        if not path.is_file():
            raise CycleExplainerFailure(
                f"Cycle source file is missing: {path}"
            )

        module_records.append(
            ModuleRecord(
                module=module,
                path=path,
                relative_path=path.relative_to(
                    ROOT
                ).as_posix(),
            )
        )

    module_details = {
        record.module: inspect_module(
            record,
            cycle_modules,
        )
        for record in module_records
    }

    edges = []

    for source_module, details in (
        module_details.items()
    ):
        for import_record in details[
            "cycle_imports"
        ]:
            target = import_record[
                "resolved_cycle_target"
            ]

            if not target:
                continue

            score = edge_score(
                import_record,
                module_details[
                    source_module
                ],
                module_details[
                    target
                ],
            )

            edges.append(
                {
                    "source_module": (
                        source_module
                    ),
                    "source_path": (
                        details["path"]
                    ),
                    "target_module": target,
                    "target_path": (
                        module_details[
                            target
                        ]["path"]
                    ),
                    "line": import_record[
                        "line"
                    ],
                    "kind": import_record[
                        "kind"
                    ],
                    "requested_module": (
                        import_record[
                            "requested_module"
                        ]
                    ),
                    "imported_symbol": (
                        import_record[
                            "imported_symbol"
                        ]
                    ),
                    "alias": import_record[
                        "alias"
                    ],
                    "runtime_import": (
                        import_record[
                            "runtime_import"
                        ]
                    ),
                    "inside_type_checking": (
                        import_record[
                            "inside_type_checking"
                        ]
                    ),
                    "lazy_import": (
                        import_record[
                            "lazy_import"
                        ]
                    ),
                    **score,
                }
            )

    if not edges:
        raise CycleExplainerFailure(
            "The cycle exists in the audit graph, but no direct "
            "cycle imports were recovered from source."
        )

    ranked_edges = sorted(
        edges,
        key=lambda item: (
            item[
                "break_risk_score"
            ],
            item["source_module"],
            item["line"],
        ),
    )

    best_edge = ranked_edges[0]

    inbound_counts: dict[
        str,
        int,
    ] = defaultdict(int)

    outbound_counts: dict[
        str,
        int,
    ] = defaultdict(int)

    for edge in edges:
        outbound_counts[
            edge["source_module"]
        ] += 1

        inbound_counts[
            edge["target_module"]
        ] += 1

    completed_at = datetime.now(
        UTC
    )

    report = {
        "workstream": 1,
        "pass": "2A",
        "pass_name": (
            "Dependency-Cycle Evidence Collection"
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
        "cycle": {
            "module_count": len(
                cycle_modules
            ),
            "edge_count": len(
                edges
            ),
            "modules": sorted(
                cycle_modules
            ),
            "files": [
                module_details[
                    module
                ]["path"]
                for module in sorted(
                    cycle_modules
                )
            ],
        },
        "module_details": (
            module_details
        ),
        "edges": edges,
        "ranked_break_candidates": (
            ranked_edges
        ),
        "best_break_candidate": (
            best_edge
        ),
        "graph_metrics": {
            "inbound_edge_counts": dict(
                sorted(
                    inbound_counts.items()
                )
            ),
            "outbound_edge_counts": dict(
                sorted(
                    outbound_counts.items()
                )
            ),
        },
        "next_action": (
            "Inspect the best break candidate and apply only the "
            "smallest contract-compliant repair."
        ),
    }

    WORKSTREAM_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    HISTORY_DIRECTORY.mkdir(
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
        HISTORY_DIRECTORY
        / f"cycle_explainer_{timestamp}.json"
    ).write_text(
        serialized,
        encoding="utf-8",
    )

    lines = []

    lines.append("=" * 80)
    lines.append("HARDENING WORKSTREAM 1")
    lines.append("PASS 2A — DEPENDENCY-CYCLE EVIDENCE COLLECTION")
    lines.append("=" * 80)

    lines.append("")
    lines.append("MODE")
    lines.append("READ ONLY")

    lines.append("")
    lines.append("CYCLE SUMMARY")
    lines.append(
        "Modules:                     "
        f"{report['cycle']['module_count']}"
    )
    lines.append(
        "Direct cycle edges:          "
        f"{report['cycle']['edge_count']}"
    )

    lines.append("")
    lines.append("CYCLE MODULES")

    for module in report[
        "cycle"
    ]["modules"]:
        lines.append(
            f"- {module}"
        )

    lines.append("")
    lines.append("DIRECT CYCLE EDGES")

    for index, edge in enumerate(
        ranked_edges,
        start=1,
    ):
        lines.append("")
        lines.append(
            f"Candidate {index}"
        )
        lines.append(
            f"Source:  {edge['source_module']}"
        )
        lines.append(
            f"Target:  {edge['target_module']}"
        )
        lines.append(
            f"File:    {edge['source_path']}:{edge['line']}"
        )
        lines.append(
            "Symbol:  "
            f"{edge['imported_symbol']}"
        )
        lines.append(
            "Runtime: "
            f"{str(edge['runtime_import']).upper()}"
        )
        lines.append(
            "Type-only: "
            f"{str(edge['inside_type_checking']).upper()}"
        )
        lines.append(
            "Lazy:    "
            f"{str(edge['lazy_import']).upper()}"
        )
        lines.append(
            "Break risk score: "
            f"{edge['break_risk_score']}/100"
        )
        lines.append(
            "Suggested repair: "
            f"{edge['candidate_repair']}"
        )

        if edge["reasons"]:
            lines.append(
                "Reasons:"
            )

            for reason in edge[
                "reasons"
            ]:
                lines.append(
                    f"  - {reason}"
                )

    lines.append("")
    lines.append("BEST BREAK CANDIDATE")
    lines.append(
        "Source module:               "
        f"{best_edge['source_module']}"
    )
    lines.append(
        "Target module:               "
        f"{best_edge['target_module']}"
    )
    lines.append(
        "Source location:             "
        f"{best_edge['source_path']}:{best_edge['line']}"
    )
    lines.append(
        "Imported symbol:             "
        f"{best_edge['imported_symbol']}"
    )
    lines.append(
        "Break risk score:            "
        f"{best_edge['break_risk_score']}/100"
    )
    lines.append(
        "Recommendation:              "
        f"{best_edge['candidate_repair']}"
    )

    lines.append("")
    lines.append("SOURCE MODIFIED")
    lines.append("NO")

    lines.append("")
    lines.append("NEXT")
    lines.append(
        "Apply the smallest repair to the selected edge, then "
        "rerun the Workstream 1 import and cycle audit."
    )

    lines.append("")
    lines.append("=" * 80)

    rendered = (
        "\n".join(lines)
        + "\n"
    )

    LATEST_TEXT.write_text(
        rendered,
        encoding="utf-8",
    )

    (
        HISTORY_DIRECTORY
        / f"cycle_explainer_{timestamp}.txt"
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
            "## Pass 2A — Dependency-Cycle Evidence Collection\n"
            "\n"
            f"- Cycle modules: {len(cycle_modules)}\n"
            f"- Direct cycle edges: {len(edges)}\n"
            f"- Best break candidate: "
            f"`{best_edge['source_module']}` → "
            f"`{best_edge['target_module']}`\n"
            f"- Source location: "
            f"`{best_edge['source_path']}:{best_edge['line']}`\n"
            f"- Break risk score: "
            f"{best_edge['break_risk_score']}/100\n"
            "- Source modified: **NO**\n"
            "\n"
            "### Evidence\n"
            "\n"
            "- `runtime/hardening/workstream1/"
            "cycle_explainer_latest.json`\n"
            "- `runtime/hardening/workstream1/"
            "cycle_explainer_latest.txt`\n"
            "\n"
        )

    print(rendered)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())

    except CycleExplainerFailure as exc:
        print("=" * 80)
        print("WORKSTREAM 1 PASS 2A BLOCKED")
        print("=" * 80)
        print()
        print(
            f"{type(exc).__name__}: {exc}"
        )
        print()
        print("No application source was modified.")
        print("Broker execution remains disabled.")
        print("Live trading remains disabled.")
        print("=" * 80)

        raise SystemExit(1)
