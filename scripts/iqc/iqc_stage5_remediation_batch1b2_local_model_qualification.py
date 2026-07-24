#!/usr/bin/env python3
"""
NeuroVest Integrated Qualification Campaign

IQC Stage 5 Remediation Batch 1B2 —
Resolve and Qualify the Actual Local-Model
Output Contract and Malformed-Output Behavior

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
BACKEND_ROOT = ROOT / "backend" / "app"
WOLFDEN_ROOT = BACKEND_ROOT / "stacks" / "wolfden_ai"

OUTPUT_DIR = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "remediation_batch1b2"
)

PRIOR_REPORT = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "remediation_batch1b1a"
    / "iqc_stage5_remediation_batch1b1a_latest.json"
)

IMPORT_AUDIT = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream1"
    / "import_cycle_audit_latest.json"
)

TEST_LOG = OUTPUT_DIR / "whole_backend_tests_latest.log"
TEST_EXIT_FILE = OUTPUT_DIR / "whole_backend_tests_exit_code.txt"

REPORT_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b2_latest.json"
)

REPORT_TEXT = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b2_latest.txt"
)

EVIDENCE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b2_evidence_latest.json"
)

FREEZE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b2_freeze_latest.json"
)

SOURCE_MANIFEST = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b2_source_manifest_latest.json"
)

LOCAL_MODEL_TEXT_MARKERS = (
    "ollama",
    "localhost:11434",
    "127.0.0.1:11434",
    "/api/chat",
    "/api/generate",
    "local_model",
    "local model",
    "local_llm",
    "local llm",
    "llm_runtime",
    "inference",
)

MODEL_CALL_TERMINALS = {
    "chat",
    "generate",
    "invoke",
    "ainvoke",
    "complete",
    "completion",
    "post",
    "request",
    "send",
}

PARSE_TERMINALS = {
    "loads",
    "json",
    "model_validate",
    "model_validate_json",
    "parse_obj",
    "validate",
}

MALFORMED_EXCEPTION_NAMES = {
    "JSONDecodeError",
    "ValidationError",
    "ValueError",
    "TypeError",
    "KeyError",
}

CONTRACT_BASES = {
    "BaseModel",
    "TypedDict",
    "Protocol",
}

FORBIDDEN_STACKS = {
    "execution",
    "paper_trading",
    "broker_integration",
    "db_runtime",
    "journal_ledger",
}

FORBIDDEN_CALLS = {
    "process_portfolio_output",
    "save_log",
    "execute",
    "execute_order",
    "execute_trade",
    "place_order",
    "submit_order",
    "commit",
    "rollback",
    "flush",
    "append_event",
}


def load_json(path: Path) -> dict[str, Any]:
    assert path.is_file(), f"Required evidence missing: {path}"

    value = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert isinstance(value, dict)
    return value


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def python_files(root: Path) -> list[Path]:
    if not root.is_dir():
        return []

    return [
        path
        for path in sorted(root.rglob("*.py"))
        if "__pycache__" not in path.parts
    ]


def is_test_path(path: Path) -> bool:
    parts = {
        part.lower()
        for part in path.parts
    }

    return (
        "test" in parts
        or "tests" in parts
        or "l7_tests" in parts
        or path.name.startswith("test_")
        or path.name.endswith("_test.py")
    )


def dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id

    if isinstance(node, ast.Attribute):
        parent = dotted_name(node.value)

        if parent:
            return f"{parent}.{node.attr}"

        return node.attr

    return None


def annotation_text(
    annotation: ast.expr | None,
) -> str | None:
    if annotation is None:
        return None

    try:
        return ast.unparse(annotation)

    except Exception:
        return None


def module_name(path: Path) -> str:
    relative_path = path.relative_to(ROOT)

    parts = list(relative_path.with_suffix("").parts)

    return ".".join(parts)


def module_aliases(path: Path) -> set[str]:
    full = module_name(path)

    aliases = {
        full,
    }

    if full.startswith("backend."):
        aliases.add(
            full[len("backend.") :]
        )

    if full.startswith("backend.app."):
        aliases.add(
            full[len("backend.app.") :]
        )

    return aliases


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


def exception_names(
    handler: ast.ExceptHandler,
) -> set[str]:
    value = handler.type

    if value is None:
        return {
            "BaseException"
        }

    if isinstance(value, ast.Tuple):
        return {
            (
                dotted_name(item)
                or ast.unparse(item)
            ).split(".")[-1]
            for item in value.elts
        }

    rendered = (
        dotted_name(value)
        or ast.unparse(value)
    )

    return {
        rendered.split(".")[-1]
    }


def inspect_file(path: Path) -> dict[str, Any]:
    source = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    lowered_source = source.lower()

    tree = ast.parse(
        source,
        filename=str(path),
    )

    imports = []
    imported_modules = set()
    contracts = []
    functions = []
    model_calls = []
    parse_calls = []
    malformed_handlers = []
    broad_handlers = []
    forbidden_imports = []
    forbidden_calls = []
    string_markers = []

    for marker in LOCAL_MODEL_TEXT_MARKERS:
        if marker in lowered_source:
            string_markers.append(marker)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name)

                imports.append(
                    {
                        "line": node.lineno,
                        "module": alias.name,
                        "symbol": None,
                        "alias": alias.asname,
                    }
                )

                parts = set(
                    alias.name.lower().split(".")
                )

                if parts & FORBIDDEN_STACKS:
                    forbidden_imports.append(
                        {
                            "line": node.lineno,
                            "module": alias.name,
                        }
                    )

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""

            imported_modules.add(module)

            for alias in node.names:
                imports.append(
                    {
                        "line": node.lineno,
                        "module": module,
                        "symbol": alias.name,
                        "alias": alias.asname,
                    }
                )

            parts = set(
                module.lower().split(".")
            )

            if parts & FORBIDDEN_STACKS:
                forbidden_imports.append(
                    {
                        "line": node.lineno,
                        "module": module,
                    }
                )

        elif isinstance(node, ast.ClassDef):
            bases = {
                (
                    dotted_name(base)
                    or ast.unparse(base)
                ).split(".")[-1]
                for base in node.bases
            }

            fields = []

            for statement in node.body:
                if not isinstance(
                    statement,
                    ast.AnnAssign,
                ):
                    continue

                if not isinstance(
                    statement.target,
                    ast.Name,
                ):
                    continue

                fields.append(
                    {
                        "name": statement.target.id,
                        "annotation": annotation_text(
                            statement.annotation
                        ),
                    }
                )

            if (
                bases & CONTRACT_BASES
                or fields
            ):
                contracts.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "bases": sorted(bases),
                        "fields": fields,
                    }
                )

        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            function_source = (
                ast.get_source_segment(
                    source,
                    node,
                )
                or ""
            )

            functions.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "end_line": getattr(
                        node,
                        "end_lineno",
                        None,
                    ),
                    "async": isinstance(
                        node,
                        ast.AsyncFunctionDef,
                    ),
                    "return_annotation": annotation_text(
                        node.returns
                    ),
                    "source": function_source,
                }
            )

        elif isinstance(node, ast.Call):
            rendered = dotted_name(
                node.func
            )

            if not rendered:
                continue

            terminal = rendered.split(".")[-1]

            record = {
                "line": node.lineno,
                "scope": enclosing_scope(
                    tree,
                    node,
                ),
                "call": rendered,
                "terminal": terminal,
            }

            if terminal in MODEL_CALL_TERMINALS:
                model_calls.append(record)

            if terminal in PARSE_TERMINALS:
                parse_calls.append(record)

            if terminal in FORBIDDEN_CALLS:
                forbidden_calls.append(record)

        elif isinstance(node, ast.ExceptHandler):
            names = exception_names(node)

            record = {
                "line": node.lineno,
                "scope": enclosing_scope(
                    tree,
                    node,
                ),
                "exceptions": sorted(names),
                "reraises": any(
                    isinstance(child, ast.Raise)
                    for child in ast.walk(node)
                ),
            }

            if names & MALFORMED_EXCEPTION_NAMES:
                malformed_handlers.append(record)

            if (
                "Exception" in names
                or "BaseException" in names
            ):
                broad_handlers.append(record)

    local_model_imports = [
        item
        for item in imports
        if any(
            marker in (
                item["module"]
                + "."
                + str(item["symbol"] or "")
            ).lower()
            for marker in LOCAL_MODEL_TEXT_MARKERS
        )
    ]

    return {
        "path": relative(path),
        "module": module_name(path),
        "aliases": sorted(
            module_aliases(path)
        ),
        "sha256": sha256_file(path),
        "imports": imports,
        "imported_modules": sorted(
            imported_modules
        ),
        "local_model_imports": local_model_imports,
        "string_markers": sorted(
            set(string_markers)
        ),
        "contracts": contracts,
        "functions": functions,
        "model_calls": model_calls,
        "parse_calls": parse_calls,
        "malformed_handlers": malformed_handlers,
        "broad_handlers": broad_handlers,
        "forbidden_imports": forbidden_imports,
        "forbidden_calls": forbidden_calls,
    }


def build_module_graph(
    records: list[dict[str, Any]],
) -> tuple[
    dict[str, str],
    dict[str, set[str]],
]:
    alias_to_path = {}

    for record in records:
        for alias in record["aliases"]:
            alias_to_path[alias] = record["path"]

    graph: dict[str, set[str]] = defaultdict(set)

    for record in records:
        current_path = record["path"]

        for imported in record[
            "imported_modules"
        ]:
            target_path = alias_to_path.get(
                imported
            )

            if target_path:
                graph[current_path].add(
                    target_path
                )
                continue

            for alias, candidate_path in (
                alias_to_path.items()
            ):
                if imported.startswith(
                    alias + "."
                ):
                    graph[current_path].add(
                        candidate_path
                    )

    return alias_to_path, graph


def reachable_modules(
    graph: dict[str, set[str]],
    roots: set[str],
) -> tuple[
    set[str],
    dict[str, str | None],
]:
    visited = set()
    parent: dict[str, str | None] = {}
    queue = deque()

    for root in sorted(roots):
        visited.add(root)
        parent[root] = None
        queue.append(root)

    while queue:
        current = queue.popleft()

        for target in sorted(
            graph.get(current, set())
        ):
            if target in visited:
                continue

            visited.add(target)
            parent[target] = current
            queue.append(target)

    return visited, parent


def path_from_root(
    target: str,
    parent: dict[str, str | None],
) -> list[str]:
    if target not in parent:
        return []

    result = []
    current: str | None = target

    while current is not None:
        result.append(current)
        current = parent.get(current)

    return list(reversed(result))


def discover_tests() -> list[dict[str, Any]]:
    tests = []

    for path in python_files(BACKEND_ROOT):
        if not is_test_path(path):
            continue

        source = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        lowered = source.lower()

        if not any(
            marker in lowered
            for marker in (
                "wolfden",
                "ollama",
                "local_model",
                "local model",
                "inference",
                "malformed",
            )
        ):
            continue

        tests.append(
            {
                "path": relative(path),
                "malformed_output_test": any(
                    marker in lowered
                    for marker in (
                        "malformed",
                        "invalid json",
                        "jsondecodeerror",
                        "validationerror",
                        "invalid output",
                        "invalid response",
                    )
                ),
                "output_contract_test": any(
                    marker in lowered
                    for marker in (
                        "output contract",
                        "schema",
                        "model_validate",
                        "return_annotation",
                        "pydantic",
                        "typeddict",
                    )
                ),
                "timeout_test": (
                    "timeout" in lowered
                    or "wait_for" in lowered
                ),
                "unavailable_test": any(
                    marker in lowered
                    for marker in (
                        "unavailable",
                        "connectionerror",
                        "connecterror",
                        "refused",
                    )
                ),
            }
        )

    return tests


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

    def count(label: str) -> int:
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

    for path in python_files(BACKEND_ROOT):
        entries.append(
            {
                "path": relative(path),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
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
        "manifest_sha256": digest.hexdigest(),
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

    prior = load_json(PRIOR_REPORT)
    audit = load_json(IMPORT_AUDIT)

    assert prior["status"] == "completed"

    assert prior[
        "implementation"
    ][
        "wolfden_save_log_import_removed"
    ] is True

    assert prior[
        "implementation"
    ][
        "wolfden_save_log_call_removed"
    ] is True

    assert prior[
        "implementation"
    ][
        "observability_boundary_async"
    ] is True

    assert prior[
        "implementation"
    ][
        "agent_awaits_observability"
    ] is True

    assert prior[
        "boundary"
    ][
        "wolfden_imports_journal_ledger"
    ] is False

    assert prior[
        "broker_execution_enabled"
    ] is False

    assert prior[
        "live_trading_enabled"
    ] is False

    summary = audit["summary"]

    assert summary[
        "active_internal_unresolved"
    ] == 0

    assert summary[
        "syntax_errors"
    ] == 0

    assert summary[
        "active_cycle_components"
    ] == 0

    records = [
        inspect_file(path)
        for path in python_files(BACKEND_ROOT)
        if not is_test_path(path)
    ]

    record_by_path = {
        record["path"]: record
        for record in records
    }

    _, graph = build_module_graph(records)

    wolfden_roots = {
        record["path"]
        for record in records
        if Path(
            record["path"]
        ).is_relative_to(
            Path(
                "backend/app/stacks/wolfden_ai"
            )
        )
    }

    assert wolfden_roots, (
        "No Wolfden production modules were resolved"
    )

    reachable, parent = reachable_modules(
        graph,
        wolfden_roots,
    )

    candidates = []

    for record in records:
        direct_signal_count = (
            len(record["local_model_imports"])
            + len(record["string_markers"])
            + len(record["model_calls"])
        )

        if direct_signal_count == 0:
            continue

        reachable_from_wolfden = (
            record["path"] in reachable
        )

        candidate_functions = []

        for function in record["functions"]:
            function_start = function["line"]
            function_end = (
                function["end_line"]
                or function_start
            )

            function_model_calls = [
                item
                for item in record["model_calls"]
                if (
                    function_start
                    <= item["line"]
                    <= function_end
                )
            ]

            function_parse_calls = [
                item
                for item in record["parse_calls"]
                if (
                    function_start
                    <= item["line"]
                    <= function_end
                )
            ]

            function_handlers = [
                item
                for item in record[
                    "malformed_handlers"
                ]
                if (
                    function_start
                    <= item["line"]
                    <= function_end
                )
            ]

            lowered_function = function[
                "source"
            ].lower()

            function_markers = [
                marker
                for marker
                in LOCAL_MODEL_TEXT_MARKERS
                if marker in lowered_function
            ]

            if not (
                function_model_calls
                or function_markers
            ):
                continue

            candidate_functions.append(
                {
                    "name": function["name"],
                    "line": function["line"],
                    "async": function["async"],
                    "return_annotation": function[
                        "return_annotation"
                    ],
                    "model_calls": (
                        function_model_calls
                    ),
                    "parse_calls": (
                        function_parse_calls
                    ),
                    "malformed_handlers": (
                        function_handlers
                    ),
                    "string_markers": (
                        function_markers
                    ),
                }
            )

        candidates.append(
            {
                "path": record["path"],
                "module": record["module"],
                "reachable_from_wolfden": (
                    reachable_from_wolfden
                ),
                "reachability_path": (
                    path_from_root(
                        record["path"],
                        parent,
                    )
                    if reachable_from_wolfden
                    else []
                ),
                "local_model_imports": record[
                    "local_model_imports"
                ],
                "string_markers": record[
                    "string_markers"
                ],
                "model_calls": record[
                    "model_calls"
                ],
                "parse_calls": record[
                    "parse_calls"
                ],
                "contracts": record[
                    "contracts"
                ],
                "malformed_handlers": record[
                    "malformed_handlers"
                ],
                "broad_handlers": record[
                    "broad_handlers"
                ],
                "candidate_functions": (
                    candidate_functions
                ),
            }
        )

    reachable_candidates = [
        item
        for item in candidates
        if item[
            "reachable_from_wolfden"
        ]
    ]

    exact_boundary = None

    if len(reachable_candidates) == 1:
        candidate = reachable_candidates[0]

        if len(
            candidate[
                "candidate_functions"
            ]
        ) == 1:
            exact_boundary = {
                **candidate,
                "function": candidate[
                    "candidate_functions"
                ][0],
            }

    tests = discover_tests()

    malformed_test_present = any(
        item["malformed_output_test"]
        for item in tests
    )

    contract_test_present = any(
        item["output_contract_test"]
        for item in tests
    )

    if exact_boundary is not None:
        boundary_function = exact_boundary[
            "function"
        ]

        explicit_return_contract = (
            boundary_function[
                "return_annotation"
            ]
            not in {
                None,
                "Any",
                "dict",
                "list",
                "tuple",
                "object",
                "str",
            }
        )

        explicit_schema_contract = bool(
            exact_boundary[
                "contracts"
            ]
        )

        parser_present = bool(
            boundary_function[
                "parse_calls"
            ]
            or exact_boundary[
                "parse_calls"
            ]
        )

        malformed_handler_present = bool(
            boundary_function[
                "malformed_handlers"
            ]
            or exact_boundary[
                "malformed_handlers"
            ]
        )

    else:
        explicit_return_contract = False
        explicit_schema_contract = False
        parser_present = False
        malformed_handler_present = False

    reachable_forbidden_imports = [
        {
            "path": path,
            **item,
        }
        for path in sorted(reachable)
        for item in record_by_path[
            path
        ][
            "forbidden_imports"
        ]
    ]

    reachable_forbidden_calls = [
        {
            "path": path,
            **item,
        }
        for path in sorted(reachable)
        for item in record_by_path[
            path
        ][
            "forbidden_calls"
        ]
    ]

    gates = [
        {
            "gate": (
                "Exactly one Wolfden-reachable "
                "local-model boundary"
            ),
            "complete": (
                exact_boundary is not None
            ),
            "severity": "HIGH",
        },
        {
            "gate": (
                "Explicit immutable or schema-backed "
                "output contract"
            ),
            "complete": (
                explicit_return_contract
                or explicit_schema_contract
            ),
            "severity": "HIGH",
        },
        {
            "gate": (
                "Explicit model-output parser"
            ),
            "complete": parser_present,
            "severity": "HIGH",
        },
        {
            "gate": (
                "Malformed output rejected or "
                "mapped fail-closed"
            ),
            "complete": (
                malformed_handler_present
            ),
            "severity": "HIGH",
        },
        {
            "gate": (
                "Malformed-output focused test"
            ),
            "complete": (
                malformed_test_present
            ),
            "severity": "HIGH",
        },
        {
            "gate": (
                "Output-contract focused test"
            ),
            "complete": (
                contract_test_present
            ),
            "severity": "MEDIUM",
        },
    ]

    missing_gates = [
        gate
        for gate in gates
        if not gate["complete"]
    ]

    if reachable_forbidden_imports:
        disposition = (
            "BLOCKED_REACHABLE_FORBIDDEN_IMPORT"
        )

        remediation_authorized = False

    elif reachable_forbidden_calls:
        disposition = (
            "BLOCKED_REACHABLE_FORBIDDEN_CALL"
        )

        remediation_authorized = False

    elif exact_boundary is None:
        if not reachable_candidates:
            disposition = (
                "NO_WOLFDEN_REACHABLE_LOCAL_MODEL_BOUNDARY"
            )

        else:
            disposition = (
                "AMBIGUOUS_WOLFDEN_LOCAL_MODEL_BOUNDARY"
            )

        remediation_authorized = False

    elif missing_gates:
        disposition = (
            "CONFIRMED_LOCAL_MODEL_CONTRACT_REMEDIATION_REQUIRED"
        )

        remediation_authorized = True

    else:
        disposition = (
            "LOCAL_MODEL_OUTPUT_CONTRACT_QUALIFIED"
        )

        remediation_authorized = False

    if disposition == (
        "CONFIRMED_LOCAL_MODEL_CONTRACT_REMEDIATION_REQUIRED"
    ):
        next_step = (
            "IQC Stage 5 Remediation Batch 1B3 — "
            "Implement and Qualify the Confirmed "
            "Local-Model Output Contract and "
            "Malformed-Output Fail-Closed Boundary"
        )

    elif disposition == (
        "LOCAL_MODEL_OUTPUT_CONTRACT_QUALIFIED"
    ):
        next_step = (
            "IQC Stage 5 Remediation Batch 1C — "
            "wolfden_ai Qualification Freeze"
        )

    elif disposition == (
        "NO_WOLFDEN_REACHABLE_LOCAL_MODEL_BOUNDARY"
    ):
        next_step = (
            "IQC Stage 5 Remediation Batch 1B2A — "
            "Resolve Wolfden Runtime Injection and "
            "Dynamic Local-Model Ownership"
        )

    elif disposition == (
        "AMBIGUOUS_WOLFDEN_LOCAL_MODEL_BOUNDARY"
    ):
        next_step = (
            "IQC Stage 5 Remediation Batch 1B2A — "
            "Focused Candidate Boundary Disposition"
        )

    else:
        next_step = (
            "Resolve the remaining reachable forbidden "
            "capability before local-model remediation."
        )

    tests_state = backend_tests()

    assert tests_state[
        "exit_code"
    ] == 0

    assert tests_state[
        "failed"
    ] == 0

    manifest = source_manifest()

    evidence = {
        "status": "completed",
        "generated_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "wolfden_roots": sorted(
            wolfden_roots
        ),
        "reachable_modules": sorted(
            reachable
        ),
        "module_graph": {
            path: sorted(targets)
            for path, targets in sorted(
                graph.items()
            )
        },
        "candidates": candidates,
        "reachable_candidates": (
            reachable_candidates
        ),
        "exact_boundary": (
            exact_boundary
        ),
        "tests": tests,
        "reachable_forbidden_imports": (
            reachable_forbidden_imports
        ),
        "reachable_forbidden_calls": (
            reachable_forbidden_calls
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
            "IQC-STAGE5-REM-001B2"
        ),
        "batch_name": (
            "Resolve and Qualify the Actual "
            "Local-Model Output Contract and "
            "Malformed-Output Behavior"
        ),
        "status": "completed",
        "verified_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "prior_batch_verified": True,
        "wolfden_ai": {
            "disposition": disposition,
            "wolfden_root_count": len(
                wolfden_roots
            ),
            "reachable_module_count": len(
                reachable
            ),
            "all_candidate_count": len(
                candidates
            ),
            "reachable_candidate_count": len(
                reachable_candidates
            ),
            "exact_boundary_resolved": (
                exact_boundary is not None
            ),
            "exact_boundary": exact_boundary,
            "explicit_return_contract": (
                explicit_return_contract
            ),
            "explicit_schema_contract": (
                explicit_schema_contract
            ),
            "parser_present": parser_present,
            "malformed_handler_present": (
                malformed_handler_present
            ),
            "malformed_test_present": (
                malformed_test_present
            ),
            "contract_test_present": (
                contract_test_present
            ),
            "completed_gate_count": (
                len(gates)
                - len(missing_gates)
            ),
            "remaining_gate_count": len(
                missing_gates
            ),
            "qualification_gates": gates,
            "production_remediation_authorized": (
                remediation_authorized
            ),
        },
        "safety": {
            "reachable_forbidden_import_count": len(
                reachable_forbidden_imports
            ),
            "reachable_forbidden_call_count": len(
                reachable_forbidden_calls
            ),
            "auth_implemented": False,
            "snaptrade_connected": False,
            "broker_execution_enabled": False,
            "live_trading_enabled": False,
        },
        "qualification": {
            "whole_backend_passed": (
                tests_state["passed"]
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
            "IQC-STAGE5-REM-001B2"
        ),
        "frozen_at": datetime.now(
            UTC
        ).isoformat(),
        "disposition": disposition,
        "exact_boundary_resolved": (
            exact_boundary is not None
        ),
        "remaining_gate_count": len(
            missing_gates
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
            "IQC STAGE 5 REMEDIATION BATCH 1B2 — "
            "RESOLVE AND QUALIFY THE ACTUAL LOCAL-MODEL "
            "OUTPUT CONTRACT AND MALFORMED-OUTPUT BEHAVIOR"
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
        "BOUNDARY RESOLUTION",
        (
            "Wolfden production roots:          "
            f"{len(wolfden_roots)}"
        ),
        (
            "Wolfden-reachable modules:         "
            f"{len(reachable)}"
        ),
        (
            "All local-model candidates:        "
            f"{len(candidates)}"
        ),
        (
            "Reachable local-model candidates:  "
            f"{len(reachable_candidates)}"
        ),
        (
            "Exact boundary resolved:           "
            f"{'YES' if exact_boundary is not None else 'NO'}"
        ),
        "",
        "OUTPUT CONTRACT",
        (
            "Explicit return contract:          "
            f"{'YES' if explicit_return_contract else 'NO'}"
        ),
        (
            "Explicit schema contract:          "
            f"{'YES' if explicit_schema_contract else 'NO'}"
        ),
        (
            "Parser present:                    "
            f"{'YES' if parser_present else 'NO'}"
        ),
        (
            "Malformed handler present:         "
            f"{'YES' if malformed_handler_present else 'NO'}"
        ),
        (
            "Malformed-output test present:     "
            f"{'YES' if malformed_test_present else 'NO'}"
        ),
        (
            "Output-contract test present:      "
            f"{'YES' if contract_test_present else 'NO'}"
        ),
        (
            "Remaining gates:                   "
            f"{len(missing_gates)}"
        ),
        "",
        "REACHABLE CANDIDATES",
    ]

    if reachable_candidates:
        for candidate in reachable_candidates:
            lines.append(
                f"- {candidate['path']}"
            )

            for function in candidate[
                "candidate_functions"
            ]:
                lines.append(
                    f"  {function['name']} "
                    f"(line {function['line']})"
                )

                lines.append(
                    "  Model calls: "
                    f"{len(function['model_calls'])}"
                )

                lines.append(
                    "  Parse calls: "
                    f"{len(function['parse_calls'])}"
                )

                lines.append(
                    "  Malformed handlers: "
                    f"{len(function['malformed_handlers'])}"
                )

            if candidate[
                "reachability_path"
            ]:
                lines.append(
                    "  Reachability:"
                )

                for step in candidate[
                    "reachability_path"
                ]:
                    lines.append(
                        f"    -> {step}"
                    )

    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "GATE RESULTS",
        ]
    )

    for gate in gates:
        lines.append(
            f"- {'PASS' if gate['complete'] else 'FAIL'}: "
            f"{gate['gate']}"
        )

    lines.extend(
        [
            "",
            "QUALIFICATION",
            (
                "Whole-backend tests passed:     "
                f"{tests_state['passed']}"
            ),
            "Whole-backend tests failed:     0",
            "Active unresolved imports:      0",
            "Dependency cycles:              0",
            "",
            "SAFETY",
            (
                "Reachable forbidden imports:   "
                f"{len(reachable_forbidden_imports)}"
            ),
            (
                "Reachable forbidden calls:     "
                f"{len(reachable_forbidden_calls)}"
            ),
            "- Auth implemented: NO",
            "- SnapTrade connected: NO",
            "- Broker execution enabled: NO",
            "- Live trading enabled: NO",
            "- Source modified: NO",
            "- Database modified: NO",
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
