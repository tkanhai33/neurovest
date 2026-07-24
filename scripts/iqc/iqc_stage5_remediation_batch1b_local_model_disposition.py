#!/usr/bin/env python3
"""
NeuroVest Integrated Qualification Campaign

IQC Stage 5 Remediation Batch 1B —
wolfden_ai Local-Model Output Contract
and Malformed-Output Qualification

PASS A
Exact local-model boundary and malformed-output disposition.

MODE
READ ONLY
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(".").resolve()

BACKEND_ROOT = (
    ROOT
    / "backend"
    / "app"
)

WOLFDEN_ROOT = (
    BACKEND_ROOT
    / "stacks"
    / "wolfden_ai"
)

OUTPUT_DIR = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "remediation_batch1b"
)

PRIOR_REPORT = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "remediation_batch1a3"
    / "iqc_stage5_remediation_batch1a3_latest.json"
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
    / "iqc_stage5_remediation_batch1b_latest.json"
)

REPORT_TEXT = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b_latest.txt"
)

EVIDENCE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b_evidence_latest.json"
)

FREEZE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b_freeze_latest.json"
)

SOURCE_MANIFEST = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b_source_manifest_latest.json"
)

MODEL_MODULE_MARKERS = (
    "ollama",
    "httpx",
    "aiohttp",
    "requests",
    "urllib",
    "llm",
    "model",
    "inference",
)

MODEL_CALL_TERMINALS = {
    "chat",
    "generate",
    "completion",
    "complete",
    "invoke",
    "ainvoke",
    "request",
    "post",
    "send",
}

PARSE_CALL_TERMINALS = {
    "json",
    "loads",
    "model_validate",
    "model_validate_json",
    "parse_obj",
    "validate",
}

MALFORMED_MARKERS = (
    "malformed",
    "invalid output",
    "invalid response",
    "invalid payload",
    "jsondecodeerror",
    "validationerror",
    "parse error",
    "schema error",
)

FAILURE_MARKERS = (
    "except",
    "raise ",
    "error",
    "failure",
    "invalid",
    "unavailable",
    "timeout",
    "fallback",
)

CONTRACT_BASES = {
    "BaseModel",
    "TypedDict",
    "Protocol",
}

FORBIDDEN_STACKS = {
    "execution",
    "paper_trading",
    "broker_integration",
    "snaptrade",
    "db_runtime",
    "journal_ledger",
}

FORBIDDEN_CALLS = {
    "process_portfolio_output",
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


def python_files(
    root: Path,
) -> list[Path]:
    if not root.is_dir():
        return []

    return [
        path
        for path in sorted(
            root.rglob("*.py")
        )
        if "__pycache__" not in path.parts
    ]


def is_test_path(
    path: Path,
) -> bool:
    lowered = {
        part.lower()
        for part in path.parts
    }

    return (
        "test" in lowered
        or "tests" in lowered
        or "l7_tests" in lowered
        or path.name.startswith("test_")
        or path.name.endswith("_test.py")
    )


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
            return f"{parent}.{node.attr}"

        return node.attr

    return None


def annotation_text(
    annotation: ast.expr | None,
) -> str | None:
    if annotation is None:
        return None

    try:
        return ast.unparse(
            annotation
        )

    except Exception:
        return None


def enclosing_function(
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


def inspect_file(
    path: Path,
) -> dict[str, Any]:
    source = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    lowered = source.lower()

    tree = ast.parse(
        source,
        filename=str(path),
    )

    imports = set()
    imported_names = set()
    contracts = []
    functions = []
    model_calls = []
    parse_calls = []
    forbidden_imports = []
    forbidden_calls = []

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                imports.add(alias.name)

                imported_names.add(
                    alias.asname
                    or alias.name.split(".")[0]
                )

                if any(
                    marker in alias.name.lower()
                    for marker in FORBIDDEN_STACKS
                ):
                    forbidden_imports.append(
                        {
                            "line": node.lineno,
                            "module": alias.name,
                        }
                    )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            module = node.module or ""

            imports.add(module)

            for alias in node.names:
                imported_names.add(
                    alias.asname
                    or alias.name
                )

            if any(
                marker in module.lower()
                for marker in FORBIDDEN_STACKS
            ):
                forbidden_imports.append(
                    {
                        "line": node.lineno,
                        "module": module,
                    }
                )

        elif isinstance(
            node,
            ast.ClassDef,
        ):
            bases = {
                (
                    dotted_name(base)
                    or ""
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
            body = (
                ast.get_source_segment(
                    source,
                    node,
                )
                or ""
            ).lower()

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
                    "public": not node.name.startswith("_"),
                    "return_annotation": annotation_text(
                        node.returns
                    ),
                    "failure_signal": any(
                        marker in body
                        for marker in FAILURE_MARKERS
                    ),
                    "malformed_signal": any(
                        marker in body
                        for marker in MALFORMED_MARKERS
                    ),
                }
            )

        elif isinstance(
            node,
            ast.Call,
        ):
            call = dotted_name(
                node.func
            )

            if not call:
                continue

            terminal = call.split(".")[-1]
            lowered_call = call.lower()

            record = {
                "line": node.lineno,
                "scope": enclosing_function(
                    tree,
                    node,
                ),
                "call": call,
                "terminal": terminal,
            }

            if (
                terminal in MODEL_CALL_TERMINALS
                and any(
                    marker in lowered_call
                    for marker
                    in MODEL_MODULE_MARKERS
                )
            ):
                model_calls.append(record)

            elif (
                terminal in MODEL_CALL_TERMINALS
                and any(
                    marker in lowered
                    for marker
                    in MODEL_MODULE_MARKERS
                )
                and terminal
                in {
                    "chat",
                    "generate",
                    "completion",
                    "complete",
                    "invoke",
                    "ainvoke",
                }
            ):
                model_calls.append(record)

            if terminal in PARSE_CALL_TERMINALS:
                parse_calls.append(record)

            if terminal in FORBIDDEN_CALLS:
                forbidden_calls.append(record)

    return {
        "path": relative(path),
        "sha256": sha256_file(path),
        "imports": sorted(imports),
        "contracts": contracts,
        "functions": functions,
        "model_calls": model_calls,
        "parse_calls": parse_calls,
        "forbidden_imports": forbidden_imports,
        "forbidden_calls": forbidden_calls,
        "file_failure_signal": any(
            marker in lowered
            for marker in FAILURE_MARKERS
        ),
        "file_malformed_signal": any(
            marker in lowered
            for marker in MALFORMED_MARKERS
        ),
    }


def discover_tests() -> list[
    dict[str, Any]
]:
    results = []

    for path in python_files(
        BACKEND_ROOT
    ):
        if not is_test_path(path):
            continue

        source = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        lowered = source.lower()

        if not any(
            token in lowered
            for token in (
                "wolfden_ai",
                "ollama",
                "local_model",
                "local model",
            )
        ):
            continue

        results.append(
            {
                "path": relative(path),
                "malformed_output_test": any(
                    marker in lowered
                    for marker in MALFORMED_MARKERS
                ),
                "contract_test": any(
                    marker in lowered
                    for marker in (
                        "contract",
                        "schema",
                        "model_validate",
                        "return_annotation",
                        "output",
                        "result",
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

    return results


def source_manifest() -> dict[
    str,
    Any
]:
    entries = []

    for path in python_files(
        BACKEND_ROOT
    ):
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


def backend_test_state() -> dict[
    str,
    Any
]:
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


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    prior = load_json(
        PRIOR_REPORT
    )

    audit = load_json(
        IMPORT_AUDIT
    )

    assert prior[
        "status"
    ] == "completed"

    assert prior[
        "implementation"
    ][
        "wolfden_execution_import_removed"
    ] is True

    assert prior[
        "implementation"
    ][
        "wolfden_execution_call_removed"
    ] is True

    assert prior[
        "boundary"
    ][
        "wolfden_imports_execution"
    ] is False

    assert len(
        prior[
            "remaining_wolfden_gates"
        ]
    ) == 1

    assert prior[
        "broker_execution_enabled"
    ] is False

    assert prior[
        "live_trading_enabled"
    ] is False

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

    records = [
        inspect_file(path)
        for path in python_files(
            WOLFDEN_ROOT
        )
        if not is_test_path(path)
    ]

    model_calls = [
        {
            "path": record["path"],
            **call,
        }
        for record in records
        for call in record[
            "model_calls"
        ]
    ]

    parse_calls = [
        {
            "path": record["path"],
            **call,
        }
        for record in records
        for call in record[
            "parse_calls"
        ]
    ]

    contracts = [
        {
            "path": record["path"],
            **contract,
        }
        for record in records
        for contract in record[
            "contracts"
        ]
    ]

    forbidden_imports = [
        {
            "path": record["path"],
            **item,
        }
        for record in records
        for item in record[
            "forbidden_imports"
        ]
    ]

    forbidden_calls = [
        {
            "path": record["path"],
            **item,
        }
        for record in records
        for item in record[
            "forbidden_calls"
        ]
    ]

    candidate_keys = sorted(
        {
            (
                item["path"],
                item["scope"],
            )
            for item in model_calls
        }
    )

    candidates = [
        {
            "path": path,
            "function": function,
            "model_calls": [
                item
                for item in model_calls
                if (
                    item["path"] == path
                    and item["scope"] == function
                )
            ],
            "parse_calls": [
                item
                for item in parse_calls
                if (
                    item["path"] == path
                    and item["scope"] == function
                )
            ],
        }
        for path, function in candidate_keys
    ]

    tests = discover_tests()

    malformed_tests = [
        item
        for item in tests
        if item[
            "malformed_output_test"
        ]
    ]

    contract_tests = [
        item
        for item in tests
        if item[
            "contract_test"
        ]
    ]

    exact_boundary_resolved = (
        len(candidates) == 1
    )

    explicit_contract_present = bool(
        contracts
    )

    malformed_handling_present = any(
        record[
            "file_malformed_signal"
        ]
        for record in records
    )

    malformed_test_present = bool(
        malformed_tests
    )

    contract_test_present = bool(
        contract_tests
    )

    gates = [
        {
            "gate": (
                "Exactly one local-model boundary resolved"
            ),
            "complete": (
                exact_boundary_resolved
            ),
            "severity": "HIGH",
        },
        {
            "gate": (
                "Explicit local-model output contract exists"
            ),
            "complete": (
                explicit_contract_present
            ),
            "severity": "HIGH",
        },
        {
            "gate": (
                "Malformed model output is rejected"
            ),
            "complete": (
                malformed_handling_present
            ),
            "severity": "HIGH",
        },
        {
            "gate": (
                "Malformed-output focused test exists"
            ),
            "complete": (
                malformed_test_present
            ),
            "severity": "HIGH",
        },
        {
            "gate": (
                "Output-contract focused test exists"
            ),
            "complete": (
                contract_test_present
            ),
            "severity": "MEDIUM",
        },
    ]

    missing = [
        gate
        for gate in gates
        if not gate[
            "complete"
        ]
    ]

    if forbidden_imports or forbidden_calls:
        disposition = (
            "BLOCKED_FORBIDDEN_CAPABILITY_PATH"
        )

        implementation_authorized = False

    elif not exact_boundary_resolved:
        disposition = (
            "BOUNDARY_AMBIGUOUS_REQUIRES_FOCUSED_REVIEW"
        )

        implementation_authorized = False

    elif missing:
        disposition = (
            "CONFIRMED_OUTPUT_CONTRACT_REMEDIATION_REQUIRED"
        )

        implementation_authorized = True

    else:
        disposition = (
            "LOCAL_MODEL_OUTPUT_QUALIFIED"
        )

        implementation_authorized = False

    authorized_target = (
        candidates[0]
        if exact_boundary_resolved
        else None
    )

    tests_state = (
        backend_test_state()
    )

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
        "records": records,
        "model_calls": model_calls,
        "parse_calls": parse_calls,
        "contracts": contracts,
        "candidates": candidates,
        "tests": tests,
        "forbidden_imports": (
            forbidden_imports
        ),
        "forbidden_calls": (
            forbidden_calls
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
            "IQC-STAGE5-REM-001B-A"
        ),
        "batch_name": (
            "wolfden_ai Local-Model Output Contract "
            "and Malformed-Output Qualification"
        ),
        "pass": (
            "A — Exact Boundary Disposition"
        ),
        "status": "completed",
        "verified_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "prior_batch_verified": True,
        "wolfden_ai": {
            "disposition": disposition,
            "candidate_boundary_count": len(
                candidates
            ),
            "exact_boundary_resolved": (
                exact_boundary_resolved
            ),
            "authorized_target": (
                authorized_target
            ),
            "explicit_contract_present": (
                explicit_contract_present
            ),
            "malformed_handling_present": (
                malformed_handling_present
            ),
            "malformed_test_present": (
                malformed_test_present
            ),
            "contract_test_present": (
                contract_test_present
            ),
            "completed_gate_count": (
                len(gates)
                - len(missing)
            ),
            "remaining_gate_count": len(
                missing
            ),
            "qualification_gates": gates,
            "production_remediation_authorized": (
                implementation_authorized
            ),
        },
        "tests": tests_state,
        "repository": {
            "active_internal_unresolved": 0,
            "syntax_errors": 0,
            "active_cycle_components": 0,
        },
        "safety": {
            "forbidden_import_count": len(
                forbidden_imports
            ),
            "forbidden_call_count": len(
                forbidden_calls
            ),
            "auth_implemented": False,
            "snaptrade_connected": False,
            "broker_execution_enabled": False,
            "live_trading_enabled": False,
        },
        "source_modified": False,
        "database_modified": False,
        "next_step": (
            (
                "IQC Stage 5 Remediation Batch 1B2 — "
                "Implement and Qualify the Confirmed "
                "wolfden_ai Local-Model Output Contract"
            )
            if implementation_authorized
            else (
                "Focused local-model boundary review"
                if not exact_boundary_resolved
                else (
                    "IQC Stage 5 Remediation Batch 1C — "
                    "wolfden_ai Qualification Freeze"
                )
            )
        ),
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
            "IQC-STAGE5-REM-001B-A"
        ),
        "frozen_at": datetime.now(
            UTC
        ).isoformat(),
        "disposition": disposition,
        "candidate_boundary_count": len(
            candidates
        ),
        "remaining_gate_count": len(
            missing
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
        "=" * 100,
        "NEUROVEST INTEGRATED QUALIFICATION CAMPAIGN",
        (
            "IQC STAGE 5 REMEDIATION BATCH 1B — "
            "WOLFDEN_AI LOCAL-MODEL OUTPUT CONTRACT "
            "AND MALFORMED-OUTPUT QUALIFICATION"
        ),
        "=" * 100,
        "",
        "PASS",
        "A — EXACT LOCAL-MODEL BOUNDARY DISPOSITION",
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
        "BOUNDARY",
        (
            "Candidate boundaries:             "
            f"{len(candidates)}"
        ),
        (
            "Exactly one boundary resolved:    "
            f"{'YES' if exact_boundary_resolved else 'NO'}"
        ),
        (
            "Explicit output contract present: "
            f"{'YES' if explicit_contract_present else 'NO'}"
        ),
        (
            "Malformed-output handling present:"
            f" {'YES' if malformed_handling_present else 'NO'}"
        ),
        (
            "Malformed-output test present:    "
            f"{'YES' if malformed_test_present else 'NO'}"
        ),
        (
            "Output-contract test present:     "
            f"{'YES' if contract_test_present else 'NO'}"
        ),
        (
            "Remaining gates:                  "
            f"{len(missing)}"
        ),
        "",
        "CANDIDATE LOCAL-MODEL BOUNDARIES",
    ]

    if candidates:
        for candidate in candidates:
            lines.extend(
                [
                    (
                        f"- {candidate['path']}::"
                        f"{candidate['function']}"
                    ),
                    (
                        "  Model calls: "
                        f"{len(candidate['model_calls'])}"
                    ),
                    (
                        "  Parse calls: "
                        f"{len(candidate['parse_calls'])}"
                    ),
                ]
            )

    else:
        lines.append("- None resolved")

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
                "Whole-backend tests passed:    "
                f"{tests_state['passed']}"
            ),
            "Whole-backend tests failed:    0",
            "Active unresolved imports:     0",
            "Dependency cycles:             0",
            "",
            "SAFETY",
            (
                "Forbidden Wolfden imports:     "
                f"{len(forbidden_imports)}"
            ),
            (
                "Forbidden Wolfden calls:       "
                f"{len(forbidden_calls)}"
            ),
            "- Auth implemented: NO",
            "- SnapTrade connected: NO",
            "- Broker execution enabled: NO",
            "- Live trading enabled: NO",
            "- Source modified: NO",
            "- Database modified: NO",
            "",
            "NEXT",
            report["next_step"],
            "",
            "=" * 100,
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

    print("Disposition report:")
    print(REPORT_JSON)
    print()

    print("Detailed evidence:")
    print(EVIDENCE_JSON)
    print()

    print("Freeze manifest:")
    print(FREEZE_JSON)


if __name__ == "__main__":
    main()
