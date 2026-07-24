#!/usr/bin/env python3

"""
Hardening Workstream 1
Pass 4C — Exact Duplicate Intent and Scaffold Inspection

Read-only inspection of modules confirmed by Pass 4B to have exact
source duplication.

This audit determines:

- exact duplicate clusters
- whether duplicated source is a scaffold, placeholder, or real code
- each file's implied responsibility
- inbound imports and symbol references
- test, contract, documentation, and roadmap references
- whether cross-stack consolidation would violate ownership
- recommended disposition for each duplicate module

Possible recommendations:

- PRESERVE_INTENTIONAL_PLACEHOLDER
- IMPLEMENT_SEPARATELY
- SHARED_BASE_CANDIDATE
- OWNERSHIP_REVIEW_REQUIRED
- ARCHIVAL_REVIEW_REQUIRED
- CANONICALIZE_WITHIN_SAME_STACK
- DO_NOT_CONSOLIDATE_CROSS_STACK

No source files are modified.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from collections import Counter, defaultdict, deque
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

PASS4B_REPORT = (
    WORKSTREAM_DIR
    / "duplicate_verification"
    / "duplicate_verification_latest.json"
)

OUTPUT_DIR = (
    WORKSTREAM_DIR
    / "duplicate_intent"
)

HISTORY_DIR = (
    WORKSTREAM_DIR
    / "history"
)

LATEST_JSON = (
    OUTPUT_DIR
    / "exact_duplicate_intent_latest.json"
)

LATEST_TEXT = (
    OUTPUT_DIR
    / "exact_duplicate_intent_latest.txt"
)

LATEST_CSV = (
    OUTPUT_DIR
    / "exact_duplicate_intent_latest.csv"
)

LEDGER = (
    ROOT
    / "handoff"
    / "hardening"
    / "WORKSTREAM_1_LEDGER.md"
)

ALLOWED_RECOMMENDATIONS = {
    "PRESERVE_INTENTIONAL_PLACEHOLDER",
    "IMPLEMENT_SEPARATELY",
    "SHARED_BASE_CANDIDATE",
    "OWNERSHIP_REVIEW_REQUIRED",
    "ARCHIVAL_REVIEW_REQUIRED",
    "CANONICALIZE_WITHIN_SAME_STACK",
    "DO_NOT_CONSOLIDATE_CROSS_STACK",
}


class IntentInspectionFailure(RuntimeError):
    pass


def load_pass4b() -> dict[str, Any]:
    if not PASS4B_REPORT.is_file():
        raise IntentInspectionFailure(
            "Pass 4B duplicate verification report is missing."
        )

    payload = json.loads(
        PASS4B_REPORT.read_text(
            encoding="utf-8"
        )
    )

    if payload.get("workstream") != 1:
        raise IntentInspectionFailure(
            "Pass 4B report belongs to another workstream."
        )

    if payload.get("pass") != "4B":
        raise IntentInspectionFailure(
            "Latest duplicate report is not Pass 4B."
        )

    if payload.get("status") != "completed":
        raise IntentInspectionFailure(
            "Pass 4B did not complete successfully."
        )

    return payload


def sha256_text(
    value: str,
) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def stack_from_path(
    path: str,
) -> str:
    parts = Path(path).parts

    try:
        index = parts.index("stacks")
        return parts[index + 1]

    except (
        ValueError,
        IndexError,
    ):
        if "core" in parts:
            return "core"

        if "api" in parts:
            return "api"

        if "analysis" in parts:
            return "analysis"

        return "unowned"


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


def discover_repository_files() -> list[Path]:
    roots = [
        ROOT / "backend",
        ROOT / "scripts",
        ROOT / "tests",
        ROOT / "docs",
        ROOT / "handoff",
    ]

    supported_suffixes = {
        ".py",
        ".md",
        ".txt",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
    }

    results = []

    for root in roots:
        if not root.exists():
            continue

        for path in root.rglob("*"):
            if not path.is_file():
                continue

            if path.suffix.lower() not in supported_suffixes:
                continue

            if any(
                part in {
                    ".git",
                    ".venv",
                    "__pycache__",
                    "node_modules",
                    "backups",
                }
                for part in path.parts
            ):
                continue

            results.append(path)

    return sorted(results)


def parse_python(
    path: Path,
) -> ast.Module:
    return ast.parse(
        path.read_text(
            encoding="utf-8",
            errors="replace",
        ),
        filename=path.as_posix(),
    )


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

        elif isinstance(
            node,
            ast.Assign,
        ):
            for target in node.targets:
                if (
                    isinstance(target, ast.Name)
                    and not target.id.startswith("_")
                ):
                    symbols.append(target.id)

        elif isinstance(
            node,
            ast.AnnAssign,
        ):
            if (
                isinstance(node.target, ast.Name)
                and not node.target.id.startswith("_")
            ):
                symbols.append(node.target.id)

    return sorted(set(symbols))


def callable_details(
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

        records.append(
            {
                "name": node.name,
                "kind": type(node).__name__,
                "line": node.lineno,
                "decorators": [
                    ast.unparse(item)
                    for item in node.decorator_list
                ],
                "docstring": ast.get_docstring(
                    node,
                    clean=True,
                ),
                "statement_count": len(
                    getattr(
                        node,
                        "body",
                        [],
                    )
                ),
            }
        )

    return records


def module_imports(
    tree: ast.Module,
) -> list[dict[str, Any]]:
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(
                    {
                        "module": alias.name,
                        "symbol": None,
                        "line": node.lineno,
                        "kind": "import",
                    }
                )

        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imports.append(
                    {
                        "module": node.module or "",
                        "symbol": alias.name,
                        "line": node.lineno,
                        "kind": "from",
                    }
                )

    return imports


def scaffold_signals(
    source: str,
    tree: ast.Module,
) -> dict[str, Any]:
    lowered = source.lower()

    explicit_markers = [
        "placeholder",
        "stub",
        "future phase",
        "future implementation",
        "not implemented",
        "todo",
        "pass",
        "temporary",
        "scaffold",
        "disabled",
        "deferred",
    ]

    matched_markers = sorted(
        marker
        for marker in explicit_markers
        if marker in lowered
    )

    pass_statements = sum(
        1
        for node in ast.walk(tree)
        if isinstance(node, ast.Pass)
    )

    not_implemented_raises = 0

    for node in ast.walk(tree):
        if not isinstance(node, ast.Raise):
            continue

        exception = node.exc

        if (
            isinstance(exception, ast.Call)
            and isinstance(exception.func, ast.Name)
            and exception.func.id
            == "NotImplementedError"
        ):
            not_implemented_raises += 1

    ellipsis_expressions = sum(
        1
        for node in ast.walk(tree)
        if (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and node.value.value is Ellipsis
        )
    )

    meaningful_calls = []

    ignored_calls = {
        "print",
        "len",
        "str",
        "int",
        "float",
        "bool",
        "dict",
        "list",
        "set",
        "tuple",
    }

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        name = None

        if isinstance(node.func, ast.Name):
            name = node.func.id

        elif isinstance(node.func, ast.Attribute):
            try:
                name = ast.unparse(node.func)
            except Exception:
                name = node.func.attr

        if name and name not in ignored_calls:
            meaningful_calls.append(name)

    top_level_nodes = [
        node
        for node in tree.body
        if not isinstance(
            node,
            (
                ast.Import,
                ast.ImportFrom,
            ),
        )
    ]

    callable_nodes = [
        node
        for node in tree.body
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
            ),
        )
    ]

    line_count = len(
        source.splitlines()
    )

    scaffold_score = 0

    scaffold_score += min(
        len(matched_markers) * 15,
        45,
    )

    scaffold_score += min(
        pass_statements * 10,
        20,
    )

    scaffold_score += min(
        not_implemented_raises * 20,
        30,
    )

    scaffold_score += min(
        ellipsis_expressions * 10,
        20,
    )

    if line_count <= 25:
        scaffold_score += 20

    elif line_count <= 50:
        scaffold_score += 10

    if len(callable_nodes) <= 1:
        scaffold_score += 10

    if len(set(meaningful_calls)) <= 1:
        scaffold_score += 10

    scaffold_score = min(
        scaffold_score,
        100,
    )

    if scaffold_score >= 60:
        classification = "LIKELY_SCAFFOLD"

    elif scaffold_score >= 35:
        classification = "POSSIBLE_SCAFFOLD"

    else:
        classification = "IMPLEMENTATION_PRESENT"

    return {
        "classification": classification,
        "score": scaffold_score,
        "matched_markers": matched_markers,
        "pass_statements": pass_statements,
        "not_implemented_raises": (
            not_implemented_raises
        ),
        "ellipsis_expressions": (
            ellipsis_expressions
        ),
        "meaningful_calls": sorted(
            set(meaningful_calls)
        ),
        "top_level_node_count": len(
            top_level_nodes
        ),
        "callable_count": len(
            callable_nodes
        ),
    }


def implied_responsibility(
    path: str,
) -> dict[str, Any]:
    filename = Path(path).stem
    stack = stack_from_path(path)

    mappings = {
        "chat_memory": (
            "Own persistent or conversational memory behavior "
            "for the public chat stack."
        ),
        "chat_service": (
            "Own public chat orchestration and response generation."
        ),
        "backtest_engine": (
            "Execute historical strategy backtests."
        ),
        "monte_carlo": (
            "Perform Monte Carlo simulation and probability analysis."
        ),
        "monte_carlo_mix": (
            "Combine Monte Carlo results or simulation variants."
        ),
        "probability_engine": (
            "Calculate probability, confidence, or outcome distributions."
        ),
        "research_runtime": (
            "Compose learning and research operations at runtime."
        ),
        "strategy_evaluator": (
            "Evaluate strategy performance and acceptance criteria."
        ),
        "market_session": (
            "Represent or determine current market-session state."
        ),
        "provider_cache": (
            "Cache provider results and control freshness."
        ),
        "provider_registry": (
            "Register and resolve approved market-data providers."
        ),
        "provider_router": (
            "Route market-data requests to an approved provider."
        ),
        "runtime": (
            "Own runtime orchestration for its containing stack."
        ),
    }

    description = mappings.get(
        filename,
        (
            f"Own the responsibility implied by "
            f"`{filename}` within the `{stack}` stack."
        ),
    )

    return {
        "stack": stack,
        "filename": filename,
        "description": description,
    }


def normalized_module_candidates(
    module: str,
) -> set[str]:
    candidates = {
        module,
    }

    aliases = [
        ("backend.app.", "app."),
        ("backend.app.stacks.", "stacks."),
        ("backend.app.core.", "core."),
        ("backend.app.api.", "api."),
    ]

    for source, destination in aliases:
        if module.startswith(source):
            candidates.add(
                destination
                + module[len(source):]
            )

    return candidates


def find_python_references(
    *,
    target_module: str,
    target_symbols: list[str],
    parsed_python: dict[
        str,
        dict[str, Any],
    ],
    target_path: str,
) -> list[dict[str, Any]]:
    references = []
    candidates = normalized_module_candidates(
        target_module
    )

    for source_module, details in (
        parsed_python.items()
    ):
        if details["path"] == target_path:
            continue

        for record in details["imports"]:
            imported_module = record["module"]
            symbol = record["symbol"]

            full_symbol = (
                f"{imported_module}.{symbol}"
                if imported_module
                and symbol
                else None
            )

            matched = False
            match_type = None

            if imported_module in candidates:
                matched = True
                match_type = "MODULE_IMPORT"

            elif (
                full_symbol
                and full_symbol in candidates
            ):
                matched = True
                match_type = "CHILD_MODULE_IMPORT"

            elif (
                imported_module in candidates
                and symbol in target_symbols
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


def text_references(
    *,
    path: str,
    module: str,
    filename: str,
    repository_files: list[Path],
) -> list[dict[str, Any]]:
    search_terms = {
        path,
        module,
        filename,
        f"{filename}.py",
    }

    results = []

    for candidate in repository_files:
        relative_candidate = candidate.relative_to(
            ROOT
        ).as_posix()

        if relative_candidate == path:
            continue

        try:
            text = candidate.read_text(
                encoding="utf-8",
                errors="replace",
            )

        except Exception:
            continue

        matched_terms = sorted(
            term
            for term in search_terms
            if term and term in text
        )

        if not matched_terms:
            continue

        line_hits = []

        for number, line in enumerate(
            text.splitlines(),
            start=1,
        ):
            if any(
                term in line
                for term in matched_terms
            ):
                line_hits.append(
                    {
                        "line": number,
                        "text": line.strip()[:300],
                    }
                )

            if len(line_hits) >= 10:
                break

        results.append(
            {
                "path": relative_candidate,
                "matched_terms": (
                    matched_terms
                ),
                "line_hits": line_hits,
            }
        )

    return sorted(
        results,
        key=lambda item: item["path"],
    )


def build_exact_clusters(
    pass4b: dict[str, Any],
) -> list[list[str]]:
    graph: dict[
        str,
        set[str],
    ] = defaultdict(set)

    for pair in pass4b.get(
        "confirmed_duplicates",
        [],
    ):
        if pair.get("label") != (
            "EXACT_SOURCE_DUPLICATE"
        ):
            continue

        left = pair["left_path"]
        right = pair["right_path"]

        graph[left].add(right)
        graph[right].add(left)

    visited = set()
    clusters = []

    for node in sorted(graph):
        if node in visited:
            continue

        component = []
        queue = deque([node])

        while queue:
            current = queue.popleft()

            if current in visited:
                continue

            visited.add(current)
            component.append(current)

            for neighbor in sorted(
                graph[current]
            ):
                if neighbor not in visited:
                    queue.append(neighbor)

        clusters.append(
            sorted(component)
        )

    return sorted(
        clusters,
        key=lambda cluster: (
            -len(cluster),
            cluster[0],
        ),
    )


def choose_recommendation(
    *,
    module_record: dict[str, Any],
    cluster_record: dict[str, Any],
) -> tuple[
    str,
    list[str],
    str,
]:
    reasons = []

    cross_stack = (
        cluster_record[
            "cross_stack_cluster"
        ]
    )

    scaffold_class = module_record[
        "scaffold_signals"
    ]["classification"]

    active_refs = module_record[
        "active_backend_reference_count"
    ]

    test_refs = module_record[
        "test_reference_count"
    ]

    doc_refs = module_record[
        "documentation_reference_count"
    ]

    filename = module_record[
        "implied_responsibility"
    ]["filename"]

    same_stack_count = (
        cluster_record[
            "stack_counts"
        ][module_record["stack"]]
    )

    if cross_stack:
        recommendation = (
            "DO_NOT_CONSOLIDATE_CROSS_STACK"
        )

        reasons.append(
            "Exact duplicate cluster crosses stack ownership boundaries."
        )

        reasons.append(
            "Identical current source does not imply identical intended responsibility."
        )

        action = (
            "Preserve each filename and stack boundary. "
            "Inspect whether the duplicated body is a scaffold, "
            "then implement each responsibility separately."
        )

    elif (
        same_stack_count
        == cluster_record["module_count"]
        and scaffold_class
        == "IMPLEMENTATION_PRESENT"
    ):
        recommendation = (
            "CANONICALIZE_WITHIN_SAME_STACK"
        )

        reasons.append(
            "All exact duplicates belong to the same owning stack."
        )

        reasons.append(
            "The duplicated body appears to contain implementation rather than only scaffold code."
        )

        action = (
            "Review for one canonical same-stack implementation "
            "with intentional wrappers or aliases where contracts require them."
        )

    elif scaffold_class in {
        "LIKELY_SCAFFOLD",
        "POSSIBLE_SCAFFOLD",
    }:
        if (
            active_refs == 0
            and test_refs == 0
            and doc_refs == 0
        ):
            recommendation = (
                "PRESERVE_INTENTIONAL_PLACEHOLDER"
            )

            reasons.append(
                "Module appears scaffold-like and currently has no detected runtime, test, or documentation references."
            )

            action = (
                "Keep the module dormant and record its intended responsibility. "
                "Do not compose or delete it automatically."
            )

        else:
            recommendation = (
                "IMPLEMENT_SEPARATELY"
            )

            reasons.append(
                "Module appears scaffold-like but has evidence of expected use or documented intent."
            )

            action = (
                "Replace the shared scaffold with stack-specific implementation "
                "when the owning feature workstream begins."
            )

    elif filename in {
        "provider_registry",
        "provider_router",
        "provider_cache",
        "market_session",
    }:
        recommendation = (
            "IMPLEMENT_SEPARATELY"
        )

        reasons.append(
            "Filename represents a distinct market-data responsibility."
        )

        action = (
            "Implement each provider/session responsibility independently. "
            "A shared base may be introduced only for genuinely common mechanics."
        )

    elif active_refs > 0:
        recommendation = (
            "IMPLEMENT_SEPARATELY"
        )

        reasons.append(
            "Module is already referenced by active backend code."
        )

        action = (
            "Preserve its public contract and replace duplicated internals "
            "with responsibility-specific behavior."
        )

    elif (
        test_refs == 0
        and doc_refs == 0
        and active_refs == 0
        and scaffold_class
        == "IMPLEMENTATION_PRESENT"
    ):
        recommendation = (
            "ARCHIVAL_REVIEW_REQUIRED"
        )

        reasons.append(
            "Module contains implementation-like source but has no detected runtime, test, or documentation references."
        )

        action = (
            "Inspect Git history and phase ownership before deciding whether "
            "the file is obsolete or awaiting future composition."
        )

    else:
        recommendation = (
            "OWNERSHIP_REVIEW_REQUIRED"
        )

        reasons.append(
            "Automated evidence is insufficient to determine intended lifecycle."
        )

        action = (
            "Inspect contracts, roadmap, and stack ownership before implementation or archival."
        )

    if recommendation not in (
        ALLOWED_RECOMMENDATIONS
    ):
        raise IntentInspectionFailure(
            f"Unexpected recommendation: {recommendation}"
        )

    return (
        recommendation,
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

    pass4b = load_pass4b()

    clusters = build_exact_clusters(
        pass4b
    )

    if not clusters:
        raise IntentInspectionFailure(
            "No exact-source duplicate clusters were found."
        )

    repository_files = (
        discover_repository_files()
    )

    parsed_python: dict[
        str,
        dict[str, Any],
    ] = {}

    syntax_errors = []

    for path in repository_files:
        if path.suffix != ".py":
            continue

        module = module_name_from_path(
            path
        )

        relative_path = path.relative_to(
            ROOT
        ).as_posix()

        try:
            tree = parse_python(path)

        except SyntaxError as exc:
            syntax_errors.append(
                {
                    "path": relative_path,
                    "line": exc.lineno,
                    "message": exc.msg,
                }
            )

            continue

        parsed_python[module] = {
            "path": relative_path,
            "tree": tree,
            "imports": module_imports(
                tree
            ),
            "public_symbols": (
                public_symbols(tree)
            ),
        }

    cluster_reports = []
    all_modules = []
    recommendation_counts = Counter()

    for cluster_index, paths in enumerate(
        clusters,
        start=1,
    ):
        hashes = {}
        stack_counts = Counter()

        for relative_path in paths:
            path = ROOT / relative_path

            if not path.is_file():
                raise IntentInspectionFailure(
                    f"Exact duplicate file missing: {relative_path}"
                )

            source = path.read_text(
                encoding="utf-8",
                errors="replace",
            )

            hashes[
                sha256_text(source)
            ] = hashes.get(
                sha256_text(source),
                0,
            ) + 1

            stack_counts[
                stack_from_path(
                    relative_path
                )
            ] += 1

        cluster_record = {
            "cluster_id": (
                f"EXACT_CLUSTER_{cluster_index}"
            ),
            "module_count": len(paths),
            "paths": paths,
            "stacks": sorted(
                stack_counts
            ),
            "stack_counts": dict(
                stack_counts
            ),
            "cross_stack_cluster": (
                len(stack_counts) > 1
            ),
            "single_source_hash": (
                len(hashes) == 1
            ),
            "source_hashes": sorted(
                hashes
            ),
        }

        module_records = []

        for relative_path in paths:
            absolute_path = (
                ROOT
                / relative_path
            )

            module = module_name_from_path(
                absolute_path
            )

            source = absolute_path.read_text(
                encoding="utf-8",
                errors="replace",
            )

            tree = parse_python(
                absolute_path
            )

            symbols = public_symbols(
                tree
            )

            inbound = find_python_references(
                target_module=module,
                target_symbols=symbols,
                parsed_python=parsed_python,
                target_path=relative_path,
            )

            text_refs = text_references(
                path=relative_path,
                module=module,
                filename=absolute_path.name,
                repository_files=(
                    repository_files
                ),
            )

            active_backend_refs = [
                item
                for item in inbound
                if item[
                    "source_path"
                ].startswith(
                    "backend/app/"
                )
                and "/test" not in item[
                    "source_path"
                ]
            ]

            test_refs = [
                item
                for item in inbound
                if (
                    "/test" in item[
                        "source_path"
                    ]
                    or item[
                        "source_path"
                    ].startswith(
                        "tests/"
                    )
                )
            ]

            documentation_refs = [
                item
                for item in text_refs
                if Path(
                    item["path"]
                ).suffix.lower()
                in {
                    ".md",
                    ".txt",
                    ".json",
                    ".yaml",
                    ".yml",
                    ".toml",
                }
            ]

            record = {
                "cluster_id": (
                    cluster_record[
                        "cluster_id"
                    ]
                ),
                "path": relative_path,
                "module": module,
                "stack": stack_from_path(
                    relative_path
                ),
                "source_hash": (
                    sha256_text(source)
                ),
                "line_count": len(
                    source.splitlines()
                ),
                "module_docstring": (
                    ast.get_docstring(
                        tree,
                        clean=True,
                    )
                ),
                "public_symbols": symbols,
                "callables": (
                    callable_details(tree)
                ),
                "imports": (
                    module_imports(tree)
                ),
                "scaffold_signals": (
                    scaffold_signals(
                        source,
                        tree,
                    )
                ),
                "implied_responsibility": (
                    implied_responsibility(
                        relative_path
                    )
                ),
                "inbound_python_references": (
                    inbound
                ),
                "active_backend_reference_count": (
                    len(
                        active_backend_refs
                    )
                ),
                "test_reference_count": len(
                    test_refs
                ),
                "documentation_reference_count": (
                    len(
                        documentation_refs
                    )
                ),
                "text_references": text_refs,
            }

            module_records.append(record)

        for record in module_records:
            (
                recommendation,
                reasons,
                action,
            ) = choose_recommendation(
                module_record=record,
                cluster_record={
                    **cluster_record,
                    "stack_counts": (
                        Counter(
                            cluster_record[
                                "stack_counts"
                            ]
                        )
                    ),
                },
            )

            record[
                "recommendation"
            ] = recommendation

            record[
                "recommendation_reasons"
            ] = reasons

            record[
                "recommended_action"
            ] = action

            record["source_modified"] = False

            recommendation_counts[
                recommendation
            ] += 1

            all_modules.append(record)

        cluster_record[
            "modules"
        ] = module_records

        cluster_record[
            "recommendation_summary"
        ] = dict(
            Counter(
                item["recommendation"]
                for item in module_records
            )
        )

        cluster_reports.append(
            cluster_record
        )

    completed_at = datetime.now(UTC)

    cross_stack_clusters = [
        cluster
        for cluster in cluster_reports
        if cluster[
            "cross_stack_cluster"
        ]
    ]

    same_stack_clusters = [
        cluster
        for cluster in cluster_reports
        if not cluster[
            "cross_stack_cluster"
        ]
    ]

    scaffold_modules = [
        item
        for item in all_modules
        if item[
            "scaffold_signals"
        ]["classification"]
        in {
            "LIKELY_SCAFFOLD",
            "POSSIBLE_SCAFFOLD",
        }
    ]

    referenced_modules = [
        item
        for item in all_modules
        if (
            item[
                "active_backend_reference_count"
            ]
            + item[
                "test_reference_count"
            ]
            + item[
                "documentation_reference_count"
            ]
        )
        > 0
    ]

    report = {
        "workstream": 1,
        "pass": "4C",
        "pass_name": (
            "Exact Duplicate Intent and Scaffold Inspection"
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
            "exact_duplicate_clusters": len(
                cluster_reports
            ),
            "exact_duplicate_modules": len(
                all_modules
            ),
            "cross_stack_clusters": len(
                cross_stack_clusters
            ),
            "same_stack_clusters": len(
                same_stack_clusters
            ),
            "scaffold_or_placeholder_modules": len(
                scaffold_modules
            ),
            "modules_with_detected_references": len(
                referenced_modules
            ),
            "syntax_errors": len(
                syntax_errors
            ),
        },
        "recommendation_counts": dict(
            sorted(
                recommendation_counts.items()
            )
        ),
        "clusters": cluster_reports,
        "modules": sorted(
            all_modules,
            key=lambda item: (
                item["cluster_id"],
                item["stack"],
                item["path"],
            ),
        ),
        "syntax_errors": syntax_errors,
        "next_action": (
            "Do not consolidate cross-stack exact duplicates. "
            "Inspect each cluster's scaffold status and responsibility map, "
            "then assign implementation work to the owning stack."
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
            "exact_duplicate_intent_"
            f"{timestamp}.json"
        )
    ).write_text(
        serialized,
        encoding="utf-8",
    )

    csv_lines = [
        (
            "cluster_id,recommendation,stack,path,module,"
            "scaffold_classification,scaffold_score,"
            "active_backend_references,test_references,"
            "documentation_references,implied_responsibility"
        )
    ]

    for item in report["modules"]:
        csv_lines.append(
            ",".join(
                [
                    csv_escape(
                        item["cluster_id"]
                    ),
                    csv_escape(
                        item[
                            "recommendation"
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
                            "scaffold_signals"
                        ][
                            "classification"
                        ]
                    ),
                    csv_escape(
                        item[
                            "scaffold_signals"
                        ]["score"]
                    ),
                    csv_escape(
                        item[
                            "active_backend_reference_count"
                        ]
                    ),
                    csv_escape(
                        item[
                            "test_reference_count"
                        ]
                    ),
                    csv_escape(
                        item[
                            "documentation_reference_count"
                        ]
                    ),
                    csv_escape(
                        item[
                            "implied_responsibility"
                        ]["description"]
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
        "PASS 4C — EXACT DUPLICATE INTENT AND SCAFFOLD INSPECTION",
        "=" * 80,
        "",
        "MODE",
        "READ ONLY",
        "",
        "SUMMARY",
        (
            "Exact duplicate clusters:           "
            f"{report['summary']['exact_duplicate_clusters']}"
        ),
        (
            "Exact duplicate modules:            "
            f"{report['summary']['exact_duplicate_modules']}"
        ),
        (
            "Cross-stack clusters:               "
            f"{report['summary']['cross_stack_clusters']}"
        ),
        (
            "Same-stack clusters:                "
            f"{report['summary']['same_stack_clusters']}"
        ),
        (
            "Scaffold/placeholder modules:       "
            f"{report['summary']['scaffold_or_placeholder_modules']}"
        ),
        (
            "Modules with detected references:   "
            f"{report['summary']['modules_with_detected_references']}"
        ),
        (
            "Syntax errors:                      "
            f"{report['summary']['syntax_errors']}"
        ),
        "",
        "RECOMMENDATION COUNTS",
    ]

    for recommendation, count in sorted(
        recommendation_counts.items()
    ):
        lines.append(
            f"- {recommendation:<38} {count}"
        )

    lines.extend(
        [
            "",
            "EXACT DUPLICATE CLUSTERS",
        ]
    )

    for cluster in cluster_reports:
        lines.append("")
        lines.append(
            f"{cluster['cluster_id']}"
        )
        lines.append(
            "Modules:                         "
            f"{cluster['module_count']}"
        )
        lines.append(
            "Stacks:                          "
            + ", ".join(
                cluster["stacks"]
            )
        )
        lines.append(
            "Cross-stack:                     "
            f"{str(cluster['cross_stack_cluster']).upper()}"
        )
        lines.append(
            "Single exact source hash:        "
            f"{str(cluster['single_source_hash']).upper()}"
        )

        for item in sorted(
            cluster["modules"],
            key=lambda record: (
                record["stack"],
                record["path"],
            ),
        ):
            lines.append("")
            lines.append(
                f"- {item['path']}"
            )
            lines.append(
                "    Stack: "
                f"{item['stack']}"
            )
            lines.append(
                "    Intended responsibility: "
                f"{item['implied_responsibility']['description']}"
            )
            lines.append(
                "    Scaffold status: "
                f"{item['scaffold_signals']['classification']} "
                f"score={item['scaffold_signals']['score']}/100"
            )
            lines.append(
                "    Public symbols: "
                + (
                    ", ".join(
                        item[
                            "public_symbols"
                        ]
                    )
                    or "None"
                )
            )
            lines.append(
                "    Active backend refs: "
                f"{item['active_backend_reference_count']}"
            )
            lines.append(
                "    Test refs: "
                f"{item['test_reference_count']}"
            )
            lines.append(
                "    Documentation refs: "
                f"{item['documentation_reference_count']}"
            )
            lines.append(
                "    Recommendation: "
                f"{item['recommendation']}"
            )
            lines.append(
                "    Action: "
                f"{item['recommended_action']}"
            )

    lines.extend(
        [
            "",
            "OWNERSHIP RULE",
            (
                "Exact current source equality does not authorize "
                "cross-stack consolidation. Different stack and filename "
                "responsibilities must remain distinct unless a shared "
                "contract or base is explicitly proven."
            ),
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
                "Create an implementation disposition ledger for each "
                "exact duplicate cluster. Preserve cross-stack ownership "
                "and assign responsibility-specific implementation work."
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
            "exact_duplicate_intent_"
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
            "## Pass 4C — Exact Duplicate Intent and Scaffold Inspection\n"
            "\n"
            f"Audit time: `{completed_at.isoformat()}`\n"
            "\n"
            f"- Exact duplicate clusters: "
            f"{len(cluster_reports)}\n"
            f"- Exact duplicate modules: "
            f"{len(all_modules)}\n"
            f"- Cross-stack clusters: "
            f"{len(cross_stack_clusters)}\n"
            f"- Same-stack clusters: "
            f"{len(same_stack_clusters)}\n"
            f"- Scaffold/placeholder modules: "
            f"{len(scaffold_modules)}\n"
            f"- Modules with references: "
            f"{len(referenced_modules)}\n"
            f"- Syntax errors: "
            f"{len(syntax_errors)}\n"
            "- Source modified: **NO**\n"
            "- Runtime wiring changed: **NO**\n"
            "- Broker execution enabled: **NO**\n"
            "- Live trading enabled: **NO**\n"
            "\n"
            "### Evidence\n"
            "\n"
            "- `runtime/hardening/workstream1/duplicate_intent/"
            "exact_duplicate_intent_latest.json`\n"
            "- `runtime/hardening/workstream1/duplicate_intent/"
            "exact_duplicate_intent_latest.txt`\n"
            "- `runtime/hardening/workstream1/duplicate_intent/"
            "exact_duplicate_intent_latest.csv`\n"
            "\n"
        )

    print(rendered)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(
            main()
        )

    except IntentInspectionFailure as exc:
        print("=" * 80)
        print("WORKSTREAM 1 PASS 4C BLOCKED")
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
