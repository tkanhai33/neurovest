#!/usr/bin/env python3
"""
NeuroVest Integrated Qualification Campaign

IQC Stage 5 Remediation Batch 1B2A —
Reachable Forbidden Capability Exact Disposition
and Runtime-Injection Qualification

MODE
READ ONLY
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from collections import defaultdict, deque
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(".").resolve()

BACKEND_ROOT = (
    ROOT
    / "backend"
    / "app"
)

OUTPUT_DIR = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "remediation_batch1b2a"
)

PRIOR_REPORT = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "remediation_batch1b2"
    / "iqc_stage5_remediation_batch1b2_latest.json"
)

PRIOR_EVIDENCE = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "remediation_batch1b2"
    / "iqc_stage5_remediation_batch1b2_evidence_latest.json"
)

PRIOR_FREEZE = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "remediation_batch1b2"
    / "iqc_stage5_remediation_batch1b2_freeze_latest.json"
)

IMPORT_AUDIT = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream1"
    / "import_cycle_audit_latest.json"
)

TEST_LOG = (
    OUTPUT_DIR
    / "whole_backend_tests_latest.log"
)

TEST_EXIT_FILE = (
    OUTPUT_DIR
    / "whole_backend_tests_exit_code.txt"
)

REPORT_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b2a_latest.json"
)

REPORT_TEXT = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b2a_latest.txt"
)

EVIDENCE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b2a_evidence_latest.json"
)

FREEZE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b2a_freeze_latest.json"
)

SOURCE_MANIFEST = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b2a_source_manifest_latest.json"
)

MUTATION_TERMINALS = {
    "add",
    "append_event",
    "commit",
    "delete",
    "execute",
    "execute_order",
    "execute_trade",
    "flush",
    "merge",
    "place_order",
    "process_portfolio_output",
    "rollback",
    "save",
    "save_log",
    "submit_order",
    "update",
    "upsert",
}

LOCAL_ONLY_TERMINALS = {
    "append",
    "clear",
    "extend",
    "insert",
    "pop",
    "remove",
    "replace",
    "setdefault",
    "sort",
}

DYNAMIC_TERMINALS = {
    "__import__",
    "eval",
    "exec",
    "getattr",
    "import_module",
}

INJECTION_NAME_MARKERS = {
    "adapter",
    "backend",
    "client",
    "factory",
    "generator",
    "inference",
    "invoke",
    "llm",
    "model",
    "provider",
    "router",
    "runtime",
    "service",
    "transport",
}


def load_json(
    path: Path,
) -> dict[str, Any]:
    assert path.is_file(), (
        f"Required evidence missing: {path}"
    )

    value = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert isinstance(
        value,
        dict,
    )

    return value


def relative(
    path: Path,
) -> str:
    return path.relative_to(
        ROOT
    ).as_posix()


def sha256_file(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def owner_stack(
    relative_path: str,
) -> str | None:
    parts = relative_path.split("/")

    if "stacks" not in parts:
        return None

    index = parts.index(
        "stacks"
    )

    if index + 1 >= len(parts):
        return None

    return parts[index + 1]


def imported_stack(
    module: str,
) -> str | None:
    parts = module.split(".")

    if "stacks" not in parts:
        return None

    index = parts.index(
        "stacks"
    )

    if index + 1 >= len(parts):
        return None

    return parts[index + 1]


def dotted_name(
    node: ast.AST,
) -> str | None:
    if isinstance(
        node,
        ast.Name,
    ):
        return node.id

    if isinstance(
        node,
        ast.Attribute,
    ):
        parent = dotted_name(
            node.value
        )

        if parent:
            return (
                f"{parent}.{node.attr}"
            )

        return node.attr

    return None


def enclosing_scope(
    tree: ast.AST,
    target: ast.AST,
) -> str:
    line = getattr(
        target,
        "lineno",
        None,
    )

    if line is None:
        return "<module>"

    matches = []

    for node in ast.walk(tree):
        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
            ),
        ):
            continue

        start = getattr(
            node,
            "lineno",
            None,
        )

        end = getattr(
            node,
            "end_lineno",
            None,
        )

        if (
            start is not None
            and end is not None
            and start <= line <= end
        ):
            matches.append(
                (
                    end - start,
                    node.name,
                )
            )

    if not matches:
        return "<module>"

    matches.sort()

    return matches[0][1]


def source_line(
    source: str,
    line: int,
) -> str:
    lines = source.splitlines()

    if not (
        1 <= line <= len(lines)
    ):
        return ""

    return lines[
        line - 1
    ].strip()


def inspect_import_signal(
    signal: dict[str, Any],
) -> dict[str, Any]:
    path = ROOT / signal["path"]

    assert path.is_file(), (
        f"Import source missing: {path}"
    )

    source = path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source,
        filename=str(path),
    )

    reported_module = signal[
        "module"
    ]

    line = signal["line"]

    records = []

    for node in ast.walk(tree):
        if getattr(
            node,
            "lineno",
            None,
        ) != line:
            continue

        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                if alias.name != reported_module:
                    continue

                records.append(
                    {
                        "kind": "import",
                        "module": alias.name,
                        "symbol": None,
                        "alias": alias.asname,
                        "local_name": (
                            alias.asname
                            or alias.name.split(
                                "."
                            )[-1]
                        ),
                    }
                )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            module = node.module or ""

            if module != reported_module:
                continue

            for alias in node.names:
                records.append(
                    {
                        "kind": "from_import",
                        "module": module,
                        "symbol": alias.name,
                        "alias": alias.asname,
                        "local_name": (
                            alias.asname
                            or alias.name
                        ),
                    }
                )

    assert records, (
        "Reported forbidden import was not found "
        f"at {signal['path']}:{line}"
    )

    local_names = {
        record["local_name"]
        for record in records
    }

    calls = []
    references = []

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.Name,
        ):
            if node.id not in local_names:
                continue

            references.append(
                {
                    "line": node.lineno,
                    "scope": enclosing_scope(
                        tree,
                        node,
                    ),
                    "name": node.id,
                    "context": type(
                        node.ctx
                    ).__name__,
                }
            )

        elif isinstance(
            node,
            ast.Call,
        ):
            rendered = dotted_name(
                node.func
            )

            if not rendered:
                continue

            root_name = rendered.split(
                "."
            )[0]

            terminal = rendered.split(
                "."
            )[-1]

            if (
                root_name not in local_names
                and terminal not in local_names
            ):
                continue

            calls.append(
                {
                    "line": node.lineno,
                    "scope": enclosing_scope(
                        tree,
                        node,
                    ),
                    "call": rendered,
                    "terminal": terminal,
                    "awaited": any(
                        isinstance(
                            parent,
                            ast.Await,
                        )
                        and parent.value is node
                        for parent in ast.walk(
                            tree
                        )
                    ),
                }
            )

    source_owner = owner_stack(
        signal["path"]
    )

    target_owner = imported_stack(
        reported_module
    )

    same_owner = (
        source_owner is not None
        and source_owner == target_owner
    )

    type_checking_only = False

    for node in ast.walk(tree):
        if not isinstance(
            node,
            ast.If,
        ):
            continue

        try:
            rendered = ast.unparse(
                node.test
            )

        except Exception:
            continue

        if rendered not in {
            "TYPE_CHECKING",
            "typing.TYPE_CHECKING",
        }:
            continue

        import_lines = {
            child.lineno
            for child in ast.walk(
                node
            )
            if isinstance(
                child,
                (
                    ast.Import,
                    ast.ImportFrom,
                ),
            )
        }

        if line in import_lines:
            type_checking_only = True

    if type_checking_only:
        classification = (
            "TYPE_ONLY_FALSE_POSITIVE"
        )

        remediation_required = False

    elif same_owner:
        classification = (
            "ALLOWED_OWNER_SIDE_DEPENDENCY"
        )

        remediation_required = False

    elif not calls and not references:
        classification = (
            "STALE_UNUSED_IMPORT"
        )

        remediation_required = True

    elif calls:
        classification = (
            "CONFIRMED_RUNTIME_CROSS_STACK_DEPENDENCY"
        )

        remediation_required = True

    else:
        classification = (
            "IMPORTED_SYMBOL_REQUIRES_OWNER_REVIEW"
        )

        remediation_required = True

    return {
        **signal,
        "source_owner": source_owner,
        "target_owner": target_owner,
        "same_owner": same_owner,
        "source_line": source_line(
            source,
            line,
        ),
        "import_records": records,
        "references": references,
        "runtime_calls": calls,
        "type_checking_only": (
            type_checking_only
        ),
        "classification": (
            classification
        ),
        "remediation_required": (
            remediation_required
        ),
    }


def inspect_call_signal(
    signal: dict[str, Any],
) -> dict[str, Any]:
    path = ROOT / signal["path"]

    assert path.is_file(), (
        f"Call source missing: {path}"
    )

    source = path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source,
        filename=str(path),
    )

    line = signal["line"]
    reported_call = signal["call"]
    reported_terminal = signal[
        "terminal"
    ]

    matches = []

    for node in ast.walk(tree):
        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        if node.lineno != line:
            continue

        rendered = dotted_name(
            node.func
        )

        if not rendered:
            continue

        terminal = rendered.split(
            "."
        )[-1]

        if (
            rendered == reported_call
            or terminal
            == reported_terminal
        ):
            matches.append(
                {
                    "line": node.lineno,
                    "scope": enclosing_scope(
                        tree,
                        node,
                    ),
                    "call": rendered,
                    "terminal": terminal,
                    "receiver": (
                        rendered.rsplit(
                            ".",
                            1,
                        )[0]
                        if "." in rendered
                        else None
                    ),
                    "awaited": any(
                        isinstance(
                            parent,
                            ast.Await,
                        )
                        and parent.value is node
                        for parent in ast.walk(
                            tree
                        )
                    ),
                }
            )

    assert matches, (
        "Reported forbidden call was not found "
        f"at {signal['path']}:{line}"
    )

    exact = matches[0]

    terminal = exact["terminal"]
    receiver = exact["receiver"]

    if (
        terminal in LOCAL_ONLY_TERMINALS
        and receiver is not None
        and receiver.split(".")[-1]
        in {
            "items",
            "lines",
            "records",
            "results",
            "signals",
            "values",
        }
    ):
        classification = (
            "ACCEPTABLE_LOCAL_STATE_OPERATION"
        )

        remediation_required = False

    elif terminal in DYNAMIC_TERMINALS:
        classification = (
            "RUNTIME_INJECTION_OR_DYNAMIC_DISPATCH"
        )

        remediation_required = True

    elif terminal in MUTATION_TERMINALS:
        classification = (
            "CONFIRMED_CAPABILITY_OR_MUTATION_CALL"
        )

        remediation_required = True

    elif terminal in LOCAL_ONLY_TERMINALS:
        classification = (
            "RECEIVER_OWNERSHIP_REQUIRES_REVIEW"
        )

        remediation_required = True

    else:
        classification = (
            "SCANNER_FALSE_POSITIVE_OR_NON_CAPABILITY_CALL"
        )

        remediation_required = False

    return {
        **signal,
        "source_owner": owner_stack(
            signal["path"]
        ),
        "source_line": source_line(
            source,
            line,
        ),
        "resolved_call": exact,
        "classification": classification,
        "remediation_required": (
            remediation_required
        ),
    }


def deduplicate(
    items: list[dict[str, Any]],
    fields: tuple[str, ...],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    unique = []
    duplicates = []
    seen = {}

    for item in items:
        key = tuple(
            item.get(field)
            for field in fields
        )

        if key in seen:
            duplicates.append(
                {
                    "duplicate": item,
                    "original_index": (
                        seen[key]
                    ),
                }
            )

            continue

        seen[key] = len(unique)
        unique.append(item)

    return unique, duplicates


def inspect_runtime_injection(
    reachable_paths: list[str],
) -> list[dict[str, Any]]:
    findings = []

    for relative_path in reachable_paths:
        path = ROOT / relative_path

        if not path.is_file():
            continue

        source = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        tree = ast.parse(
            source,
            filename=str(path),
        )

        for node in ast.walk(tree):
            if isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            ):
                parameters = []

                all_arguments = (
                    list(
                        node.args.posonlyargs
                    )
                    + list(
                        node.args.args
                    )
                    + list(
                        node.args.kwonlyargs
                    )
                )

                for argument in all_arguments:
                    lowered = argument.arg.lower()

                    if any(
                        marker in lowered
                        for marker
                        in INJECTION_NAME_MARKERS
                    ):
                        parameters.append(
                            argument.arg
                        )

                if parameters:
                    findings.append(
                        {
                            "path": relative_path,
                            "line": node.lineno,
                            "scope": node.name,
                            "kind": (
                                "INJECTABLE_PARAMETER"
                            ),
                            "parameters": parameters,
                        }
                    )

            elif isinstance(
                node,
                ast.Call,
            ):
                rendered = dotted_name(
                    node.func
                )

                if not rendered:
                    continue

                terminal = rendered.split(
                    "."
                )[-1]

                if terminal in DYNAMIC_TERMINALS:
                    findings.append(
                        {
                            "path": relative_path,
                            "line": node.lineno,
                            "scope": enclosing_scope(
                                tree,
                                node,
                            ),
                            "kind": (
                                "DYNAMIC_DISPATCH"
                            ),
                            "call": rendered,
                        }
                    )

            elif isinstance(
                node,
                ast.Assign,
            ):
                for target in node.targets:
                    if not isinstance(
                        target,
                        ast.Name,
                    ):
                        continue

                    lowered = target.id.lower()

                    if not any(
                        marker in lowered
                        for marker
                        in INJECTION_NAME_MARKERS
                    ):
                        continue

                    findings.append(
                        {
                            "path": relative_path,
                            "line": node.lineno,
                            "scope": enclosing_scope(
                                tree,
                                node,
                            ),
                            "kind": (
                                "INJECTABLE_ASSIGNMENT"
                            ),
                            "name": target.id,
                            "value": (
                                ast.unparse(
                                    node.value
                                )
                            ),
                        }
                    )

    return findings


def reverse_graph(
    graph: dict[str, list[str]],
) -> dict[str, list[str]]:
    reverse: dict[
        str,
        list[str],
    ] = defaultdict(list)

    for source, targets in graph.items():
        for target in targets:
            reverse[target].append(source)

    return {
        path: sorted(sources)
        for path, sources in reverse.items()
    }


def shortest_reverse_path(
    target: str,
    roots: set[str],
    reverse: dict[str, list[str]],
) -> list[str]:
    queue = deque(
        [
            (
                target,
                [target],
            )
        ]
    )

    visited = {
        target
    }

    while queue:
        current, path = queue.popleft()

        if current in roots:
            return list(
                reversed(path)
            )

        for parent in reverse.get(
            current,
            [],
        ):
            if parent in visited:
                continue

            visited.add(parent)

            queue.append(
                (
                    parent,
                    path + [parent],
                )
            )

    return []


def backend_tests() -> dict[str, Any]:
    assert TEST_LOG.is_file()
    assert TEST_EXIT_FILE.is_file()

    text = TEST_LOG.read_text(
        encoding="utf-8",
        errors="replace",
    )

    exit_code = int(
        TEST_EXIT_FILE.read_text(
            encoding="utf-8"
        ).strip()
    )

    def count(
        label: str,
    ) -> int:
        matches = re.findall(
            rf"(\d+)\s+{label}",
            text,
        )

        return (
            int(matches[-1])
            if matches
            else 0
        )

    return {
        "exit_code": exit_code,
        "passed": count("passed"),
        "failed": count("failed"),
    }


def source_manifest() -> dict[str, Any]:
    entries = []

    for path in sorted(
        BACKEND_ROOT.rglob("*.py")
    ):
        if "__pycache__" in path.parts:
            continue

        entries.append(
            {
                "path": relative(path),
                "sha256": sha256_file(
                    path
                ),
                "size_bytes": (
                    path.stat().st_size
                ),
            }
        )

    digest = hashlib.sha256()

    for item in entries:
        digest.update(
            item["path"].encode(
                "utf-8"
            )
        )

        digest.update(
            item["sha256"].encode(
                "ascii"
            )
        )

    manifest = {
        "generated_at": datetime.now(
            UTC
        ).isoformat(),
        "file_count": len(entries),
        "manifest_sha256": (
            digest.hexdigest()
        ),
        "files": entries,
    }

    SOURCE_MANIFEST.write_text(
        json.dumps(
            manifest,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return manifest


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    prior_report = load_json(
        PRIOR_REPORT
    )

    prior_evidence = load_json(
        PRIOR_EVIDENCE
    )

    prior_freeze = load_json(
        PRIOR_FREEZE
    )

    audit = load_json(
        IMPORT_AUDIT
    )

    assert prior_report[
        "status"
    ] == "completed"

    assert prior_report[
        "mode"
    ] == "read_only"

    assert prior_report[
        "wolfden_ai"
    ][
        "disposition"
    ] == (
        "BLOCKED_REACHABLE_FORBIDDEN_IMPORT"
    )

    assert prior_report[
        "safety"
    ][
        "reachable_forbidden_import_count"
    ] == 2

    assert prior_report[
        "safety"
    ][
        "reachable_forbidden_call_count"
    ] == 4

    assert prior_report[
        "wolfden_ai"
    ][
        "reachable_candidate_count"
    ] == 0

    assert prior_report[
        "wolfden_ai"
    ][
        "remaining_gate_count"
    ] == 6

    assert prior_freeze[
        "status"
    ] == "frozen"

    summary = audit[
        "summary"
    ]

    assert summary[
        "active_internal_unresolved"
    ] == 0

    assert summary[
        "syntax_errors"
    ] == 0

    assert summary[
        "active_cycle_components"
    ] == 0

    import_signals = prior_evidence[
        "reachable_forbidden_imports"
    ]

    call_signals = prior_evidence[
        "reachable_forbidden_calls"
    ]

    assert len(
        import_signals
    ) == 2

    assert len(
        call_signals
    ) == 4

    import_dispositions = [
        inspect_import_signal(
            signal
        )
        for signal in import_signals
    ]

    call_dispositions = [
        inspect_call_signal(
            signal
        )
        for signal in call_signals
    ]

    unique_imports, duplicate_imports = (
        deduplicate(
            import_dispositions,
            (
                "path",
                "line",
                "module",
            ),
        )
    )

    unique_calls, duplicate_calls = (
        deduplicate(
            call_dispositions,
            (
                "path",
                "line",
                "call",
            ),
        )
    )

    reachable_paths = prior_evidence[
        "reachable_modules"
    ]

    wolfden_roots = set(
        prior_evidence[
            "wolfden_roots"
        ]
    )

    injection_findings = (
        inspect_runtime_injection(
            reachable_paths
        )
    )

    graph = prior_evidence[
        "module_graph"
    ]

    reverse = reverse_graph(
        graph
    )

    unreachable_candidates = []

    for candidate in prior_evidence[
        "candidates"
    ]:
        if candidate[
            "reachable_from_wolfden"
        ]:
            continue

        path = candidate["path"]

        reverse_path = shortest_reverse_path(
            path,
            wolfden_roots,
            reverse,
        )

        incoming = reverse.get(
            path,
            [],
        )

        unreachable_candidates.append(
            {
                "path": path,
                "candidate_functions": (
                    candidate[
                        "candidate_functions"
                    ]
                ),
                "incoming_modules": incoming,
                "reverse_path_to_wolfden": (
                    reverse_path
                ),
                "classification": (
                    "NOT_IMPORTED_BY_WOLFDEN_GRAPH"
                    if not incoming
                    else (
                        "EXISTS_OUTSIDE_WOLFDEN_REACHABLE_GRAPH"
                    )
                ),
            }
        )

    import_defects = [
        item
        for item in unique_imports
        if item[
            "remediation_required"
        ]
    ]

    call_defects = [
        item
        for item in unique_calls
        if item[
            "remediation_required"
        ]
    ]

    runtime_injection_present = bool(
        injection_findings
    )

    if import_defects:
        disposition = (
            "CONFIRMED_REACHABLE_IMPORT_REMEDIATION_REQUIRED"
        )

        authorized_targets = sorted(
            {
                item["path"]
                for item in import_defects
            }
        )

        next_step = (
            "IQC Stage 5 Remediation Batch 1B2B — "
            "Remediate Only the Confirmed Reachable "
            "Cross-Stack Import Boundaries"
        )

    elif call_defects:
        disposition = (
            "CONFIRMED_REACHABLE_CALL_REMEDIATION_REQUIRED"
        )

        authorized_targets = sorted(
            {
                item["path"]
                for item in call_defects
            }
        )

        next_step = (
            "IQC Stage 5 Remediation Batch 1B2B — "
            "Remediate Only the Confirmed Reachable "
            "Capability Calls"
        )

    elif runtime_injection_present:
        disposition = (
            "RUNTIME_INJECTION_BOUNDARY_REQUIRES_QUALIFICATION"
        )

        authorized_targets = []

        next_step = (
            "IQC Stage 5 Remediation Batch 1B2B — "
            "Resolve and Qualify the Confirmed "
            "Runtime-Injection Composition Boundary"
        )

    else:
        disposition = (
            "STATIC_REACHABILITY_GAP_CONFIRMED"
        )

        authorized_targets = []

        next_step = (
            "IQC Stage 5 Remediation Batch 1B2B — "
            "Resolve Wolfden Local-Model Composition "
            "and Ownership Wiring"
        )

    tests = backend_tests()

    assert tests[
        "exit_code"
    ] == 0

    assert tests[
        "failed"
    ] == 0

    manifest = source_manifest()

    evidence = {
        "status": "completed",
        "generated_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "raw_import_signal_count": len(
            import_signals
        ),
        "raw_call_signal_count": len(
            call_signals
        ),
        "unique_import_signal_count": len(
            unique_imports
        ),
        "unique_call_signal_count": len(
            unique_calls
        ),
        "duplicate_imports": (
            duplicate_imports
        ),
        "duplicate_calls": (
            duplicate_calls
        ),
        "import_dispositions": (
            unique_imports
        ),
        "call_dispositions": (
            unique_calls
        ),
        "runtime_injection_findings": (
            injection_findings
        ),
        "unreachable_model_candidates": (
            unreachable_candidates
        ),
        "authorized_targets": (
            authorized_targets
        ),
        "source_manifest": manifest,
        "source_modified": False,
        "database_modified": False,
    }

    EVIDENCE_JSON.write_text(
        json.dumps(
            evidence,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    report = {
        "campaign": (
            "NeuroVest Integrated "
            "Qualification Campaign"
        ),
        "batch": (
            "IQC-STAGE5-REM-001B2A"
        ),
        "batch_name": (
            "Reachable Forbidden Capability "
            "Exact Disposition and Runtime-"
            "Injection Qualification"
        ),
        "status": "completed",
        "verified_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "prior_batch_verified": True,
        "disposition": disposition,
        "signals": {
            "raw_forbidden_imports": len(
                import_signals
            ),
            "unique_forbidden_imports": len(
                unique_imports
            ),
            "duplicate_forbidden_imports": len(
                duplicate_imports
            ),
            "confirmed_import_defects": len(
                import_defects
            ),
            "raw_forbidden_calls": len(
                call_signals
            ),
            "unique_forbidden_calls": len(
                unique_calls
            ),
            "duplicate_forbidden_calls": len(
                duplicate_calls
            ),
            "confirmed_call_defects": len(
                call_defects
            ),
        },
        "runtime_injection": {
            "finding_count": len(
                injection_findings
            ),
            "present": (
                runtime_injection_present
            ),
            "findings": (
                injection_findings
            ),
        },
        "local_model_reachability": {
            "candidate_count": len(
                unreachable_candidates
            ),
            "reachable_candidate_count": 0,
            "candidates": (
                unreachable_candidates
            ),
        },
        "authorized_source_targets": (
            authorized_targets
        ),
        "qualification": {
            "whole_backend_passed": (
                tests["passed"]
            ),
            "whole_backend_failed": 0,
        },
        "repository": {
            "active_internal_unresolved": 0,
            "syntax_errors": 0,
            "active_cycle_components": 0,
        },
        "source_modified": False,
        "database_modified": False,
        "auth_implemented": False,
        "snaptrade_connected": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
        "next_step": next_step,
    }

    REPORT_JSON.write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    freeze = {
        "status": "frozen",
        "batch": (
            "IQC-STAGE5-REM-001B2A"
        ),
        "frozen_at": datetime.now(
            UTC
        ).isoformat(),
        "disposition": disposition,
        "confirmed_import_defects": len(
            import_defects
        ),
        "confirmed_call_defects": len(
            call_defects
        ),
        "runtime_injection_present": (
            runtime_injection_present
        ),
        "authorized_source_targets": (
            authorized_targets
        ),
        "report_sha256": sha256_file(
            REPORT_JSON
        ),
        "evidence_sha256": sha256_file(
            EVIDENCE_JSON
        ),
        "source_manifest_sha256": (
            manifest[
                "manifest_sha256"
            ]
        ),
        "source_modified": False,
        "database_modified": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
    }

    FREEZE_JSON.write_text(
        json.dumps(
            freeze,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    lines = [
        "=" * 104,
        "NEUROVEST INTEGRATED QUALIFICATION CAMPAIGN",
        (
            "IQC STAGE 5 REMEDIATION BATCH 1B2A — "
            "REACHABLE FORBIDDEN CAPABILITY EXACT "
            "DISPOSITION AND RUNTIME-INJECTION QUALIFICATION"
        ),
        "=" * 104,
        "",
        "STATUS",
        "COMPLETE AND VERIFIED",
        "",
        "MODE",
        "READ ONLY",
        "",
        "DISPOSITION",
        disposition,
        "",
        "SIGNAL SUMMARY",
        (
            "Raw forbidden imports:          "
            f"{len(import_signals)}"
        ),
        (
            "Unique forbidden imports:       "
            f"{len(unique_imports)}"
        ),
        (
            "Duplicate forbidden imports:    "
            f"{len(duplicate_imports)}"
        ),
        (
            "Confirmed import defects:       "
            f"{len(import_defects)}"
        ),
        (
            "Raw forbidden calls:            "
            f"{len(call_signals)}"
        ),
        (
            "Unique forbidden calls:         "
            f"{len(unique_calls)}"
        ),
        (
            "Duplicate forbidden calls:      "
            f"{len(duplicate_calls)}"
        ),
        (
            "Confirmed call defects:         "
            f"{len(call_defects)}"
        ),
        "",
        "IMPORT DISPOSITIONS",
    ]

    for index, item in enumerate(
        unique_imports,
        start=1,
    ):
        lines.extend(
            [
                (
                    f"{index}. {item['path']}:"
                    f"{item['line']}"
                ),
                (
                    "   Module: "
                    f"{item['module']}"
                ),
                (
                    "   Source owner: "
                    f"{item['source_owner']}"
                ),
                (
                    "   Target owner: "
                    f"{item['target_owner']}"
                ),
                (
                    "   Classification: "
                    f"{item['classification']}"
                ),
                (
                    "   Runtime calls: "
                    f"{len(item['runtime_calls'])}"
                ),
                (
                    "   Remediation required: "
                    f"{'YES' if item['remediation_required'] else 'NO'}"
                ),
                (
                    "   Source: "
                    f"{item['source_line']}"
                ),
            ]
        )

    lines.extend(
        [
            "",
            "CALL DISPOSITIONS",
        ]
    )

    for index, item in enumerate(
        unique_calls,
        start=1,
    ):
        resolved = item[
            "resolved_call"
        ]

        lines.extend(
            [
                (
                    f"{index}. {item['path']}:"
                    f"{item['line']}"
                ),
                (
                    "   Call: "
                    f"{resolved['call']}"
                ),
                (
                    "   Scope: "
                    f"{resolved['scope']}"
                ),
                (
                    "   Awaited: "
                    f"{'YES' if resolved['awaited'] else 'NO'}"
                ),
                (
                    "   Classification: "
                    f"{item['classification']}"
                ),
                (
                    "   Remediation required: "
                    f"{'YES' if item['remediation_required'] else 'NO'}"
                ),
                (
                    "   Source: "
                    f"{item['source_line']}"
                ),
            ]
        )

    lines.extend(
        [
            "",
            "RUNTIME INJECTION",
            (
                "Findings:                       "
                f"{len(injection_findings)}"
            ),
            (
                "Runtime injection present:      "
                f"{'YES' if runtime_injection_present else 'NO'}"
            ),
            "",
            "LOCAL-MODEL REACHABILITY",
            (
                "Unreachable candidates:         "
                f"{len(unreachable_candidates)}"
            ),
            "Reachable candidates:           0",
        ]
    )

    for candidate in (
        unreachable_candidates
    ):
        lines.extend(
            [
                (
                    f"- {candidate['path']}"
                ),
                (
                    "  Classification: "
                    f"{candidate['classification']}"
                ),
                (
                    "  Incoming modules: "
                    f"{len(candidate['incoming_modules'])}"
                ),
            ]
        )

    lines.extend(
        [
            "",
            "AUTHORIZED SOURCE TARGETS",
        ]
    )

    if authorized_targets:
        for target in authorized_targets:
            lines.append(
                f"- {target}"
            )

    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "QUALIFICATION",
            (
                "Whole-backend tests passed:     "
                f"{tests['passed']}"
            ),
            "Whole-backend tests failed:     0",
            "Active unresolved imports:      0",
            "Dependency cycles:              0",
            "",
            "SAFETY",
            "- Source modified: NO",
            "- Database modified: NO",
            "- Auth implemented: NO",
            "- SnapTrade connected: NO",
            "- Broker execution enabled: NO",
            "- Live trading enabled: NO",
            "",
            "NEXT",
            next_step,
            "",
            "=" * 104,
        ]
    )

    rendered = (
        "\n".join(lines)
        + "\n"
    )

    REPORT_TEXT.write_text(
        rendered,
        encoding="utf-8",
    )

    print(rendered)

    print("Report:")
    print(REPORT_JSON)

    print()
    print("Evidence:")
    print(EVIDENCE_JSON)

    print()
    print("Freeze:")
    print(FREEZE_JSON)


if __name__ == "__main__":
    main()
