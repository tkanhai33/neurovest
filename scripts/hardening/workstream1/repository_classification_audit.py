#!/usr/bin/env python3

"""
Hardening Workstream 1
Pass 4 — Repository Classification Audit

Read-only classification of modules reported as unreachable by Pass 3.

This audit does not:

- delete files
- move files
- wire modules into main.py
- enable broker execution
- enable live trading
- alter runtime behavior

The purpose is to classify unreachable modules before any composition,
archival, or remediation decision is made.
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

REACHABILITY_REPORT = (
    WORKSTREAM_DIR
    / "reachability"
    / "reachability_audit_latest.json"
)

OUTPUT_DIR = (
    WORKSTREAM_DIR
    / "classification"
)

HISTORY_DIR = (
    WORKSTREAM_DIR
    / "history"
)

LATEST_JSON = (
    OUTPUT_DIR
    / "repository_classification_latest.json"
)

LATEST_TEXT = (
    OUTPUT_DIR
    / "repository_classification_latest.txt"
)

LATEST_CSV = (
    OUTPUT_DIR
    / "repository_classification_latest.csv"
)

LEDGER = (
    ROOT
    / "handoff"
    / "hardening"
    / "WORKSTREAM_1_LEDGER.md"
)


class ClassificationFailure(RuntimeError):
    pass


CLASSIFICATIONS = {
    "READY_FOR_WIRING",
    "DORMANT_FUTURE_FEATURE",
    "CONTRACT_OR_BASE",
    "SANDBOX_ISOLATED",
    "SECURITY_GATED",
    "PROVIDER_ADAPTER",
    "ROUTER_NOT_COMPOSED",
    "LEGACY_REVIEW_REQUIRED",
    "MANUAL_REVIEW_REQUIRED",
}


def load_reachability_report() -> dict[str, Any]:
    if not REACHABILITY_REPORT.is_file():
        raise ClassificationFailure(
            "Pass 3 reachability report is missing."
        )

    payload = json.loads(
        REACHABILITY_REPORT.read_text(
            encoding="utf-8"
        )
    )

    if payload.get("workstream") != 1:
        raise ClassificationFailure(
            "Reachability report does not belong to Workstream 1."
        )

    if payload.get("pass") != 3:
        raise ClassificationFailure(
            "Latest reachability report is not Pass 3."
        )

    if payload.get("status") != "completed":
        raise ClassificationFailure(
            "Pass 3 did not complete successfully."
        )

    return payload


def read_source(path: Path) -> str:
    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def parse_source(path: Path) -> ast.Module:
    return ast.parse(
        read_source(path),
        filename=path.as_posix(),
    )


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


def imported_modules(
    tree: ast.Module,
) -> list[str]:
    modules = []

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.Import,
        ):
            modules.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            if node.module:
                modules.append(
                    node.module
                )

    return sorted(
        set(modules)
    )


def has_name(
    symbols: list[str],
    pattern: str,
) -> bool:
    regex = re.compile(
        pattern,
        re.IGNORECASE,
    )

    return any(
        regex.search(symbol)
        for symbol in symbols
    )


def path_contains(
    path: str,
    *parts: str,
) -> bool:
    lowered = path.lower()

    return any(
        part.lower() in lowered
        for part in parts
    )


def source_contains(
    source: str,
    *terms: str,
) -> bool:
    lowered = source.lower()

    return any(
        term.lower() in lowered
        for term in terms
    )


def classify_module(
    *,
    path: str,
    source: str,
    tree: ast.Module,
    reachability_classification: str,
) -> dict[str, Any]:
    symbols = defined_symbols(tree)
    imports = imported_modules(tree)

    reasons: list[str] = []
    signals: list[str] = []

    lowered_path = path.lower()
    filename = Path(path).name.lower()

    if reachability_classification == (
        "ROUTER_DECLARATION"
    ):
        classification = (
            "ROUTER_NOT_COMPOSED"
        )

        reasons.append(
            "Pass 3 identified an APIRouter declaration "
            "that is not composed into the active FastAPI entrypoint."
        )

        signals.append(
            "uncomposed_router"
        )

    elif path_contains(
        lowered_path,
        "strategy_candidate_sandbox",
    ):
        classification = (
            "SANDBOX_ISOLATED"
        )

        reasons.append(
            "Module belongs to the strategy-candidate sandbox "
            "and should remain isolated from production runtime wiring."
        )

        signals.append(
            "sandbox_path"
        )

    elif path_contains(
        lowered_path,
        "snaptrade",
        "/execution/",
        "/executions/",
    ):
        classification = (
            "SECURITY_GATED"
        )

        reasons.append(
            "Module belongs to broker or execution integration "
            "and must remain gated until authenticated provider "
            "and execution hardening is complete."
        )

        signals.append(
            "broker_or_execution_path"
        )

    elif path_contains(
        lowered_path,
        "/auth_identity/",
    ):
        classification = (
            "SECURITY_GATED"
        )

        reasons.append(
            "Authentication and identity functionality is intentionally "
            "deferred and must remain security-gated."
        )

        signals.append(
            "authentication_path"
        )

    elif (
        filename == "base.py"
        or has_name(
            symbols,
            r"(Protocol|Contract|Base|Interface)$",
        )
        or source_contains(
            source,
            "typing.Protocol",
            "abc.ABC",
            "abstractmethod",
        )
    ):
        classification = (
            "CONTRACT_OR_BASE"
        )

        reasons.append(
            "Module primarily defines contracts, base classes, "
            "interfaces, or abstract ownership boundaries."
        )

        signals.append(
            "contract_or_base"
        )

    elif path_contains(
        lowered_path,
        "adapter.py",
        "provider_",
        "ingestor.py",
        "yfinance",
    ):
        classification = (
            "PROVIDER_ADAPTER"
        )

        reasons.append(
            "Module provides an external data or broker adapter "
            "and should be wired only through the owning provider boundary."
        )

        signals.append(
            "provider_or_adapter"
        )

    elif source_contains(
        source,
        "disabled_stub",
        "dry_run_stub",
        "stub",
        "not implemented",
        "future phase",
        "future implementation",
        "placeholder",
    ):
        classification = (
            "DORMANT_FUTURE_FEATURE"
        )

        reasons.append(
            "Source contains an explicit stub, placeholder, disabled, "
            "or future-phase signal."
        )

        signals.append(
            "stub_or_future_marker"
        )

    elif path_contains(
        lowered_path,
        "legacy",
        "deprecated",
        "obsolete",
        "old_",
        "_old",
    ):
        classification = (
            "LEGACY_REVIEW_REQUIRED"
        )

        reasons.append(
            "Path contains a legacy, deprecated, old, or obsolete marker."
        )

        signals.append(
            "legacy_path_marker"
        )

    elif path_contains(
        lowered_path,
        "/risk/",
        "/market_data/",
        "/portfolio/",
        "/strategy/",
        "/learning_research/",
        "/wolfden_ai/",
        "/chat_public/",
        "/notification/",
    ):
        classification = (
            "READY_FOR_WIRING"
        )

        reasons.append(
            "Module belongs to an active NeuroVest product stack "
            "but is not currently reachable from the composition root."
        )

        signals.append(
            "active_product_stack"
        )

    elif path_contains(
        lowered_path,
        "/core/",
        "/analysis/",
        "/schemas/",
        "/db_model/",
        "/journal_ledger/",
    ):
        classification = (
            "MANUAL_REVIEW_REQUIRED"
        )

        reasons.append(
            "Module belongs to shared infrastructure, schema, analysis, "
            "or ledger code and requires ownership review before wiring."
        )

        signals.append(
            "shared_infrastructure"
        )

    else:
        classification = (
            "MANUAL_REVIEW_REQUIRED"
        )

        reasons.append(
            "No sufficiently strong automated classification signal "
            "was found."
        )

        signals.append(
            "insufficient_evidence"
        )

    if classification not in CLASSIFICATIONS:
        raise ClassificationFailure(
            f"Unexpected classification: {classification}"
        )

    return {
        "classification": classification,
        "reasons": reasons,
        "signals": signals,
        "defined_symbols": symbols,
        "imported_modules": imports,
        "line_count": len(
            source.splitlines()
        ),
    }


def stack_name(path: str) -> str:
    parts = Path(path).parts

    try:
        index = parts.index(
            "stacks"
        )

        return parts[index + 1]

    except (
        ValueError,
        IndexError,
    ):
        if "core" in parts:
            return "core"

        if "analysis" in parts:
            return "analysis"

        if "schemas" in parts:
            return "schemas"

        if "api" in parts:
            return "api"

        return "unowned"


def recommended_action(
    classification: str,
) -> str:
    actions = {
        "READY_FOR_WIRING": (
            "Inspect runtime contract and compose only through "
            "the owning facade or router."
        ),
        "DORMANT_FUTURE_FEATURE": (
            "Keep dormant. Do not wire until its planned phase begins."
        ),
        "CONTRACT_OR_BASE": (
            "Keep as a contract surface. Do not wire directly."
        ),
        "SANDBOX_ISOLATED": (
            "Keep isolated from production runtime."
        ),
        "SECURITY_GATED": (
            "Keep disabled until security and authorization workstreams pass."
        ),
        "PROVIDER_ADAPTER": (
            "Wire only through the provider registry/router."
        ),
        "ROUTER_NOT_COMPOSED": (
            "Inspect whether the route is intended for the active API. "
            "Do not compose automatically."
        ),
        "LEGACY_REVIEW_REQUIRED": (
            "Inspect references and history before archival."
        ),
        "MANUAL_REVIEW_REQUIRED": (
            "Inspect ownership, contracts, and runtime intent manually."
        ),
    }

    return actions[classification]


def main() -> int:
    started_at = datetime.now(
        UTC
    )

    reachability = (
        load_reachability_report()
    )

    candidates = list(
        reachability.get(
            "unreachable_active_modules",
            [],
        )
    )

    candidates.extend(
        reachability.get(
            "unreachable_router_modules",
            [],
        )
    )

    if not candidates:
        raise ClassificationFailure(
            "Pass 3 produced no unreachable modules to classify."
        )

    classified = []
    counts = Counter()
    stack_counts: dict[
        str,
        Counter,
    ] = defaultdict(Counter)

    missing_files = []
    syntax_errors = []

    for item in candidates:
        relative_path = item["path"]
        absolute_path = (
            ROOT
            / relative_path
        )

        if not absolute_path.is_file():
            missing_files.append(
                relative_path
            )

            continue

        source = read_source(
            absolute_path
        )

        try:
            tree = parse_source(
                absolute_path
            )

        except SyntaxError as exc:
            syntax_errors.append(
                {
                    "path": relative_path,
                    "line": exc.lineno,
                    "message": exc.msg,
                }
            )

            continue

        result = classify_module(
            path=relative_path,
            source=source,
            tree=tree,
            reachability_classification=item[
                "classification"
            ],
        )

        classification = result[
            "classification"
        ]

        owner = stack_name(
            relative_path
        )

        record = {
            "path": relative_path,
            "module": item["module"],
            "stack": owner,
            "reachability_classification": item[
                "classification"
            ],
            **result,
            "recommended_action": (
                recommended_action(
                    classification
                )
            ),
            "source_modified": False,
        }

        classified.append(record)
        counts[classification] += 1
        stack_counts[owner][
            classification
        ] += 1

    completed_at = datetime.now(
        UTC
    )

    priority_order = {
        "ROUTER_NOT_COMPOSED": 1,
        "READY_FOR_WIRING": 2,
        "MANUAL_REVIEW_REQUIRED": 3,
        "PROVIDER_ADAPTER": 4,
        "SECURITY_GATED": 5,
        "CONTRACT_OR_BASE": 6,
        "DORMANT_FUTURE_FEATURE": 7,
        "SANDBOX_ISOLATED": 8,
        "LEGACY_REVIEW_REQUIRED": 9,
    }

    classified.sort(
        key=lambda item: (
            priority_order[
                item["classification"]
            ],
            item["stack"],
            item["path"],
        )
    )

    review_queue = [
        item
        for item in classified
        if item["classification"]
        in {
            "ROUTER_NOT_COMPOSED",
            "READY_FOR_WIRING",
            "MANUAL_REVIEW_REQUIRED",
            "PROVIDER_ADAPTER",
            "LEGACY_REVIEW_REQUIRED",
        }
    ]

    protected_queue = [
        item
        for item in classified
        if item["classification"]
        in {
            "SANDBOX_ISOLATED",
            "SECURITY_GATED",
            "CONTRACT_OR_BASE",
            "DORMANT_FUTURE_FEATURE",
        }
    ]

    report = {
        "workstream": 1,
        "pass": 4,
        "pass_name": (
            "Repository Classification Audit"
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
        "files_deleted": False,
        "files_moved": False,
        "runtime_wiring_changed": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
        "summary": {
            "candidate_modules": len(
                candidates
            ),
            "classified_modules": len(
                classified
            ),
            "review_queue_modules": len(
                review_queue
            ),
            "protected_or_deferred_modules": len(
                protected_queue
            ),
            "missing_files": len(
                missing_files
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
        "stack_classification_counts": {
            stack: dict(
                sorted(
                    counter.items()
                )
            )
            for stack, counter in sorted(
                stack_counts.items()
            )
        },
        "review_queue": review_queue,
        "protected_or_deferred_queue": (
            protected_queue
        ),
        "missing_files": missing_files,
        "syntax_errors": syntax_errors,
        "modules": classified,
        "next_action": (
            "Review READY_FOR_WIRING, ROUTER_NOT_COMPOSED, "
            "PROVIDER_ADAPTER, and MANUAL_REVIEW_REQUIRED modules "
            "by stack before changing runtime composition."
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
            "repository_classification_"
            f"{timestamp}.json"
        )
    ).write_text(
        serialized,
        encoding="utf-8",
    )

    csv_lines = [
        (
            "classification,stack,path,module,"
            "reachability_classification,recommended_action"
        )
    ]

    def csv_escape(value: object) -> str:
        text = str(value).replace(
            '"',
            '""',
        )

        return f'"{text}"'

    for item in classified:
        csv_lines.append(
            ",".join(
                [
                    csv_escape(
                        item[
                            "classification"
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
                            "reachability_classification"
                        ]
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

    text_lines = [
        "=" * 80,
        "HARDENING WORKSTREAM 1",
        "PASS 4 — REPOSITORY CLASSIFICATION AUDIT",
        "=" * 80,
        "",
        "MODE",
        "READ ONLY",
        "",
        "SUMMARY",
        (
            "Candidate modules:                  "
            f"{report['summary']['candidate_modules']}"
        ),
        (
            "Classified modules:                 "
            f"{report['summary']['classified_modules']}"
        ),
        (
            "Review queue modules:               "
            f"{report['summary']['review_queue_modules']}"
        ),
        (
            "Protected/deferred modules:         "
            f"{report['summary']['protected_or_deferred_modules']}"
        ),
        (
            "Missing files:                      "
            f"{report['summary']['missing_files']}"
        ),
        (
            "Syntax errors:                      "
            f"{report['summary']['syntax_errors']}"
        ),
        "",
        "CLASSIFICATION COUNTS",
    ]

    for classification, count in sorted(
        counts.items()
    ):
        text_lines.append(
            f"- {classification:<30} "
            f"{count}"
        )

    text_lines.extend(
        [
            "",
            "STACK SUMMARY",
        ]
    )

    for stack, counter in sorted(
        stack_counts.items()
    ):
        text_lines.append(
            f"- {stack}"
        )

        for classification, count in sorted(
            counter.items()
        ):
            text_lines.append(
                f"    {classification:<28} "
                f"{count}"
            )

    text_lines.extend(
        [
            "",
            "REVIEW QUEUE",
        ]
    )

    if review_queue:
        for item in review_queue:
            text_lines.append(
                (
                    f"- [{item['classification']}] "
                    f"{item['path']}"
                )
            )
    else:
        text_lines.append(
            "- None"
        )

    text_lines.extend(
        [
            "",
            "PROTECTED OR DEFERRED",
        ]
    )

    if protected_queue:
        for item in protected_queue:
            text_lines.append(
                (
                    f"- [{item['classification']}] "
                    f"{item['path']}"
                )
            )
    else:
        text_lines.append(
            "- None"
        )

    text_lines.extend(
        [
            "",
            "SAFETY",
            "Files deleted:                      NO",
            "Files moved:                        NO",
            "Runtime wiring changed:             NO",
            "Broker execution enabled:           NO",
            "Live trading enabled:               NO",
            "",
            "NEXT",
            (
                "Review the classification queue by stack. "
                "No module should be wired or archived automatically."
            ),
            "",
            "=" * 80,
        ]
    )

    rendered = (
        "\n".join(
            text_lines
        )
        + "\n"
    )

    LATEST_TEXT.write_text(
        rendered,
        encoding="utf-8",
    )

    (
        HISTORY_DIR
        / (
            "repository_classification_"
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
            "## Pass 4 — Repository Classification Audit\n"
            "\n"
            f"Audit time: `{completed_at.isoformat()}`\n"
            "\n"
            f"- Candidate modules: "
            f"{len(candidates)}\n"
            f"- Classified modules: "
            f"{len(classified)}\n"
            f"- Review queue modules: "
            f"{len(review_queue)}\n"
            f"- Protected/deferred modules: "
            f"{len(protected_queue)}\n"
            f"- Missing files: "
            f"{len(missing_files)}\n"
            f"- Syntax errors: "
            f"{len(syntax_errors)}\n"
            "- Files deleted: **NO**\n"
            "- Files moved: **NO**\n"
            "- Runtime wiring changed: **NO**\n"
            "- Broker execution enabled: **NO**\n"
            "- Live trading enabled: **NO**\n"
            "\n"
            "### Evidence\n"
            "\n"
            "- `runtime/hardening/workstream1/classification/"
            "repository_classification_latest.json`\n"
            "- `runtime/hardening/workstream1/classification/"
            "repository_classification_latest.txt`\n"
            "- `runtime/hardening/workstream1/classification/"
            "repository_classification_latest.csv`\n"
            "\n"
        )

    print(rendered)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(
            main()
        )

    except ClassificationFailure as exc:
        print("=" * 80)
        print("WORKSTREAM 1 PASS 4 BLOCKED")
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
