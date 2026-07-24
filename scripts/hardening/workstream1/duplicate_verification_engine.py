#!/usr/bin/env python3

"""
Hardening Workstream 1
Pass 4B — Duplicate Verification Engine

Read-only verification of Pass 4A duplicate candidates.

This engine compares implementation structure rather than only
public symbol names.

Signals:

- normalized module AST similarity
- normalized callable-body similarity
- statement fingerprint similarity
- token similarity
- line-count similarity
- shared public callable names

The engine ignores:

- comments
- whitespace
- file paths
- module names
- line numbers
- column offsets

No source files are modified.
"""

from __future__ import annotations

import ast
import hashlib
import io
import json
import math
import tokenize
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]

WORKSTREAM_DIR = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream1"
)

PASS4A_REPORT = (
    WORKSTREAM_DIR
    / "review_queue"
    / "review_queue_evidence_latest.json"
)

OUTPUT_DIR = (
    WORKSTREAM_DIR
    / "duplicate_verification"
)

HISTORY_DIR = (
    WORKSTREAM_DIR
    / "history"
)

LATEST_JSON = (
    OUTPUT_DIR
    / "duplicate_verification_latest.json"
)

LATEST_TEXT = (
    OUTPUT_DIR
    / "duplicate_verification_latest.txt"
)

LATEST_CSV = (
    OUTPUT_DIR
    / "duplicate_verification_latest.csv"
)

LEDGER = (
    ROOT
    / "handoff"
    / "hardening"
    / "WORKSTREAM_1_LEDGER.md"
)


class DuplicateVerificationFailure(RuntimeError):
    pass


@dataclass(frozen=True)
class ModuleFingerprint:
    path: str
    module: str
    source_hash: str
    line_count: int
    normalized_ast: str
    normalized_ast_hash: str
    callable_fingerprints: dict[str, str]
    callable_ast: dict[str, str]
    statement_fingerprints: list[str]
    tokens: list[str]
    public_callables: list[str]


class NameNormalizer(ast.NodeTransformer):
    """
    Normalize local identifiers while preserving structural meaning.

    Attribute names and called function names are preserved because
    they often distinguish behavior.
    """

    def __init__(self) -> None:
        self.local_names: dict[str, str] = {}
        self.counter = 0

    def normalized_name(
        self,
        value: str,
    ) -> str:
        preserved = {
            "self",
            "cls",
            "True",
            "False",
            "None",
        }

        if value in preserved:
            return value

        if value not in self.local_names:
            self.counter += 1
            self.local_names[value] = (
                f"local_{self.counter}"
            )

        return self.local_names[value]

    def visit_arg(
        self,
        node: ast.arg,
    ) -> ast.AST:
        node.arg = self.normalized_name(
            node.arg
        )

        return self.generic_visit(node)

    def visit_Name(
        self,
        node: ast.Name,
    ) -> ast.AST:
        node.id = self.normalized_name(
            node.id
        )

        return node

    def visit_alias(
        self,
        node: ast.alias,
    ) -> ast.AST:
        if node.asname:
            node.asname = self.normalized_name(
                node.asname
            )

        return node


def load_pass4a() -> dict[str, Any]:
    if not PASS4A_REPORT.is_file():
        raise DuplicateVerificationFailure(
            "Pass 4A report is missing."
        )

    payload = json.loads(
        PASS4A_REPORT.read_text(
            encoding="utf-8"
        )
    )

    if payload.get("workstream") != 1:
        raise DuplicateVerificationFailure(
            "Pass 4A report belongs to another workstream."
        )

    if payload.get("pass") != "4A":
        raise DuplicateVerificationFailure(
            "Latest review report is not Pass 4A."
        )

    if payload.get("status") != "completed":
        raise DuplicateVerificationFailure(
            "Pass 4A did not complete successfully."
        )

    return payload


def sha256_text(
    value: str,
) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def normalized_ast_dump(
    node: ast.AST,
) -> str:
    copied = ast.fix_missing_locations(
        NameNormalizer().visit(
            ast.parse(
                ast.unparse(node)
            )
        )
    )

    return ast.dump(
        copied,
        annotate_fields=True,
        include_attributes=False,
    )


def source_tokens(
    source: str,
) -> list[str]:
    tokens = []

    ignored = {
        tokenize.ENCODING,
        tokenize.ENDMARKER,
        tokenize.NEWLINE,
        tokenize.NL,
        tokenize.INDENT,
        tokenize.DEDENT,
        tokenize.COMMENT,
    }

    try:
        stream = tokenize.generate_tokens(
            io.StringIO(source).readline
        )

        for token in stream:
            if token.type in ignored:
                continue

            value = token.string.strip()

            if not value:
                continue

            tokens.append(value)

    except tokenize.TokenError:
        pass

    return tokens


def callable_nodes(
    tree: ast.Module,
) -> dict[str, ast.AST]:
    nodes: dict[str, ast.AST] = {}

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
                nodes[node.name] = node

    return nodes


def statement_fingerprints(
    tree: ast.Module,
) -> list[str]:
    fingerprints = []

    for node in tree.body:
        if isinstance(
            node,
            (
                ast.Import,
                ast.ImportFrom,
            ),
        ):
            continue

        fingerprints.append(
            sha256_text(
                normalized_ast_dump(node)
            )
        )

    return sorted(fingerprints)


def build_fingerprint(
    *,
    path: Path,
    module: str,
) -> ModuleFingerprint:
    source = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    try:
        tree = ast.parse(
            source,
            filename=path.as_posix(),
        )

    except SyntaxError as exc:
        raise DuplicateVerificationFailure(
            f"Syntax error in {path}: "
            f"line={exc.lineno} message={exc.msg}"
        )

    callables = callable_nodes(tree)

    callable_ast = {
        name: normalized_ast_dump(node)
        for name, node in callables.items()
    }

    callable_fingerprints = {
        name: sha256_text(dump)
        for name, dump in callable_ast.items()
    }

    normalized_module = (
        normalized_ast_dump(tree)
    )

    return ModuleFingerprint(
        path=path.relative_to(
            ROOT
        ).as_posix(),
        module=module,
        source_hash=sha256_text(source),
        line_count=len(
            source.splitlines()
        ),
        normalized_ast=normalized_module,
        normalized_ast_hash=sha256_text(
            normalized_module
        ),
        callable_fingerprints=(
            callable_fingerprints
        ),
        callable_ast=callable_ast,
        statement_fingerprints=(
            statement_fingerprints(tree)
        ),
        tokens=source_tokens(source),
        public_callables=sorted(
            callables
        ),
    )


def sequence_similarity(
    left: str,
    right: str,
) -> float:
    return SequenceMatcher(
        None,
        left,
        right,
        autojunk=False,
    ).ratio()


def token_similarity(
    left: list[str],
    right: list[str],
) -> float:
    if not left and not right:
        return 1.0

    if not left or not right:
        return 0.0

    return SequenceMatcher(
        None,
        left,
        right,
        autojunk=False,
    ).ratio()


def multiset_jaccard(
    left: list[str],
    right: list[str],
) -> float:
    left_counter = Counter(left)
    right_counter = Counter(right)

    keys = (
        set(left_counter)
        | set(right_counter)
    )

    if not keys:
        return 1.0

    intersection = sum(
        min(
            left_counter[key],
            right_counter[key],
        )
        for key in keys
    )

    union = sum(
        max(
            left_counter[key],
            right_counter[key],
        )
        for key in keys
    )

    return (
        intersection / union
        if union
        else 0.0
    )


def line_count_similarity(
    left: int,
    right: int,
) -> float:
    maximum = max(
        left,
        right,
        1,
    )

    return 1.0 - (
        abs(left - right)
        / maximum
    )


def callable_similarity(
    left: ModuleFingerprint,
    right: ModuleFingerprint,
) -> tuple[
    float,
    list[dict[str, Any]],
]:
    comparisons = []

    left_names = set(
        left.callable_ast
    )

    right_names = set(
        right.callable_ast
    )

    exact_name_overlap = sorted(
        left_names
        & right_names
    )

    for name in exact_name_overlap:
        score = sequence_similarity(
            left.callable_ast[name],
            right.callable_ast[name],
        )

        comparisons.append(
            {
                "left_callable": name,
                "right_callable": name,
                "same_name": True,
                "similarity": round(
                    score,
                    6,
                ),
            }
        )

    unmatched_left = sorted(
        left_names
        - set(exact_name_overlap)
    )

    unmatched_right = sorted(
        right_names
        - set(exact_name_overlap)
    )

    for left_name in unmatched_left:
        best = None

        for right_name in unmatched_right:
            score = sequence_similarity(
                left.callable_ast[
                    left_name
                ],
                right.callable_ast[
                    right_name
                ],
            )

            candidate = {
                "left_callable": (
                    left_name
                ),
                "right_callable": (
                    right_name
                ),
                "same_name": False,
                "similarity": round(
                    score,
                    6,
                ),
            }

            if (
                best is None
                or candidate[
                    "similarity"
                ]
                > best["similarity"]
            ):
                best = candidate

        if best is not None:
            comparisons.append(best)

    if not comparisons:
        return (
            0.0,
            [],
        )

    top_scores = sorted(
        (
            item["similarity"]
            for item in comparisons
        ),
        reverse=True,
    )

    count = min(
        len(top_scores),
        max(
            len(left_names),
            len(right_names),
            1,
        ),
    )

    score = sum(
        top_scores[:count]
    ) / count

    return (
        score,
        comparisons,
    )


def verification_label(
    *,
    exact_source: bool,
    exact_ast: bool,
    module_ast_similarity: float,
    callable_score: float,
    statement_score: float,
    token_score: float,
    line_score: float,
    same_stack: bool,
) -> tuple[
    str,
    float,
    str,
]:
    if exact_source:
        return (
            "EXACT_SOURCE_DUPLICATE",
            1.0,
            "Files have identical source content.",
        )

    if exact_ast:
        return (
            "STRUCTURAL_DUPLICATE",
            0.995,
            "Normalized module AST is identical.",
        )

    weighted = (
        module_ast_similarity * 0.30
        + callable_score * 0.30
        + statement_score * 0.20
        + token_score * 0.15
        + line_score * 0.05
    )

    if same_stack:
        weighted += 0.02

    weighted = min(
        weighted,
        1.0,
    )

    if (
        weighted >= 0.90
        and callable_score >= 0.88
        and statement_score >= 0.80
    ):
        label = "PROBABLE_IMPLEMENTATION_DUPLICATE"
        reason = (
            "High structural, callable-body, and statement similarity."
        )

    elif (
        weighted >= 0.78
        and callable_score >= 0.72
    ):
        label = "POSSIBLE_IMPLEMENTATION_OVERLAP"
        reason = (
            "Meaningful implementation overlap exists, but "
            "the modules are not proven duplicates."
        )

    elif weighted >= 0.60:
        label = "SHARED_PATTERN_ONLY"
        reason = (
            "Modules share patterns or framework structure, "
            "not enough evidence for duplication."
        )

    else:
        label = "NOT_DUPLICATE"
        reason = (
            "Implementation similarity is too low to support "
            "a duplicate classification."
        )

    return (
        label,
        round(
            weighted,
            6,
        ),
        reason,
    )


def stack_from_path(
    path: str,
) -> str:
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

        if "api" in parts:
            return "api"

        if "analysis" in parts:
            return "analysis"

        return "unowned"


def csv_escape(
    value: object,
) -> str:
    text = str(value).replace(
        '"',
        '""',
    )

    return f'"{text}"'


def main() -> int:
    started_at = datetime.now(
        UTC
    )

    pass4a = load_pass4a()

    reported_duplicates = [
        item
        for item in pass4a.get(
            "modules",
            [],
        )
        if item.get(
            "review_result"
        )
        == "DUPLICATE_IMPLEMENTATION"
    ]

    if not reported_duplicates:
        raise DuplicateVerificationFailure(
            "Pass 4A reported no duplicate candidates."
        )

    fingerprint_cache: dict[
        str,
        ModuleFingerprint,
    ] = {}

    for item in reported_duplicates:
        path = ROOT / item["path"]

        if not path.is_file():
            raise DuplicateVerificationFailure(
                f"Candidate file missing: {item['path']}"
            )

        fingerprint_cache[
            item["path"]
        ] = build_fingerprint(
            path=path,
            module=item["module"],
        )

    pair_keys = set()

    for item in reported_duplicates:
        left_path = item["path"]

        for candidate in item.get(
            "duplicate_candidates",
            [],
        ):
            right_path = candidate[
                "path"
            ]

            if right_path not in (
                fingerprint_cache
            ):
                continue

            pair_keys.add(
                tuple(
                    sorted(
                        (
                            left_path,
                            right_path,
                        )
                    )
                )
            )

    if not pair_keys:
        all_paths = sorted(
            fingerprint_cache
        )

        for index, left_path in enumerate(
            all_paths
        ):
            for right_path in all_paths[
                index + 1:
            ]:
                pair_keys.add(
                    (
                        left_path,
                        right_path,
                    )
                )

    comparisons = []
    label_counts = Counter()

    for left_path, right_path in sorted(
        pair_keys
    ):
        left = fingerprint_cache[
            left_path
        ]

        right = fingerprint_cache[
            right_path
        ]

        callable_score, callable_details = (
            callable_similarity(
                left,
                right,
            )
        )

        module_ast_score = (
            sequence_similarity(
                left.normalized_ast,
                right.normalized_ast,
            )
        )

        statement_score = (
            multiset_jaccard(
                left.statement_fingerprints,
                right.statement_fingerprints,
            )
        )

        token_score = token_similarity(
            left.tokens,
            right.tokens,
        )

        line_score = (
            line_count_similarity(
                left.line_count,
                right.line_count,
            )
        )

        exact_source = (
            left.source_hash
            == right.source_hash
        )

        exact_ast = (
            left.normalized_ast_hash
            == right.normalized_ast_hash
        )

        left_stack = stack_from_path(
            left.path
        )

        right_stack = stack_from_path(
            right.path
        )

        label, confidence, reason = (
            verification_label(
                exact_source=exact_source,
                exact_ast=exact_ast,
                module_ast_similarity=(
                    module_ast_score
                ),
                callable_score=(
                    callable_score
                ),
                statement_score=(
                    statement_score
                ),
                token_score=token_score,
                line_score=line_score,
                same_stack=(
                    left_stack
                    == right_stack
                ),
            )
        )

        label_counts[label] += 1

        comparisons.append(
            {
                "left_path": left.path,
                "right_path": right.path,
                "left_module": left.module,
                "right_module": right.module,
                "left_stack": left_stack,
                "right_stack": right_stack,
                "same_stack": (
                    left_stack
                    == right_stack
                ),
                "label": label,
                "confidence": confidence,
                "reason": reason,
                "signals": {
                    "exact_source": (
                        exact_source
                    ),
                    "exact_normalized_ast": (
                        exact_ast
                    ),
                    "module_ast_similarity": round(
                        module_ast_score,
                        6,
                    ),
                    "callable_similarity": round(
                        callable_score,
                        6,
                    ),
                    "statement_similarity": round(
                        statement_score,
                        6,
                    ),
                    "token_similarity": round(
                        token_score,
                        6,
                    ),
                    "line_count_similarity": round(
                        line_score,
                        6,
                    ),
                },
                "left": {
                    "line_count": (
                        left.line_count
                    ),
                    "public_callables": (
                        left.public_callables
                    ),
                    "statement_count": len(
                        left.statement_fingerprints
                    ),
                },
                "right": {
                    "line_count": (
                        right.line_count
                    ),
                    "public_callables": (
                        right.public_callables
                    ),
                    "statement_count": len(
                        right.statement_fingerprints
                    ),
                },
                "callable_comparisons": (
                    callable_details
                ),
            }
        )

    comparisons.sort(
        key=lambda item: (
            -item["confidence"],
            item["left_path"],
            item["right_path"],
        )
    )

    confirmed = [
        item
        for item in comparisons
        if item["label"]
        in {
            "EXACT_SOURCE_DUPLICATE",
            "STRUCTURAL_DUPLICATE",
            "PROBABLE_IMPLEMENTATION_DUPLICATE",
        }
    ]

    possible_overlap = [
        item
        for item in comparisons
        if item["label"]
        == "POSSIBLE_IMPLEMENTATION_OVERLAP"
    ]

    rejected = [
        item
        for item in comparisons
        if item["label"]
        in {
            "SHARED_PATTERN_ONLY",
            "NOT_DUPLICATE",
        }
    ]

    module_results = []

    for path, fingerprint in sorted(
        fingerprint_cache.items()
    ):
        related = [
            item
            for item in comparisons
            if path in {
                item["left_path"],
                item["right_path"],
            }
        ]

        strongest = (
            related[0]
            if related
            else None
        )

        confirmed_relations = [
            item
            for item in related
            if item["label"]
            in {
                "EXACT_SOURCE_DUPLICATE",
                "STRUCTURAL_DUPLICATE",
                "PROBABLE_IMPLEMENTATION_DUPLICATE",
            }
        ]

        module_results.append(
            {
                "path": path,
                "module": (
                    fingerprint.module
                ),
                "stack": stack_from_path(
                    path
                ),
                "confirmed_duplicate": bool(
                    confirmed_relations
                ),
                "confirmed_relations": (
                    confirmed_relations
                ),
                "strongest_match": (
                    strongest
                ),
                "public_callables": (
                    fingerprint.public_callables
                ),
                "line_count": (
                    fingerprint.line_count
                ),
            }
        )

    completed_at = datetime.now(
        UTC
    )

    report = {
        "workstream": 1,
        "pass": "4B",
        "pass_name": (
            "Duplicate Verification Engine"
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
            "pass4a_duplicate_modules": len(
                reported_duplicates
            ),
            "unique_pairs_verified": len(
                comparisons
            ),
            "confirmed_duplicate_pairs": len(
                confirmed
            ),
            "possible_overlap_pairs": len(
                possible_overlap
            ),
            "rejected_duplicate_pairs": len(
                rejected
            ),
            "modules_with_confirmed_duplicate": sum(
                1
                for item in module_results
                if item[
                    "confirmed_duplicate"
                ]
            ),
        },
        "label_counts": dict(
            sorted(
                label_counts.items()
            )
        ),
        "confirmed_duplicates": confirmed,
        "possible_overlaps": (
            possible_overlap
        ),
        "rejected_false_positives": (
            rejected
        ),
        "module_results": (
            module_results
        ),
        "all_pair_comparisons": (
            comparisons
        ),
        "next_action": (
            "Only confirmed duplicate pairs may enter manual "
            "consolidation review. Rejected pairs must be restored "
            "to their original ownership review categories."
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
            "duplicate_verification_"
            f"{timestamp}.json"
        )
    ).write_text(
        serialized,
        encoding="utf-8",
    )

    csv_lines = [
        (
            "label,confidence,left_stack,right_stack,"
            "left_path,right_path,module_ast_similarity,"
            "callable_similarity,statement_similarity,"
            "token_similarity,line_count_similarity"
        )
    ]

    for item in comparisons:
        signals = item["signals"]

        csv_lines.append(
            ",".join(
                [
                    csv_escape(
                        item["label"]
                    ),
                    csv_escape(
                        item["confidence"]
                    ),
                    csv_escape(
                        item["left_stack"]
                    ),
                    csv_escape(
                        item["right_stack"]
                    ),
                    csv_escape(
                        item["left_path"]
                    ),
                    csv_escape(
                        item["right_path"]
                    ),
                    csv_escape(
                        signals[
                            "module_ast_similarity"
                        ]
                    ),
                    csv_escape(
                        signals[
                            "callable_similarity"
                        ]
                    ),
                    csv_escape(
                        signals[
                            "statement_similarity"
                        ]
                    ),
                    csv_escape(
                        signals[
                            "token_similarity"
                        ]
                    ),
                    csv_escape(
                        signals[
                            "line_count_similarity"
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
        "PASS 4B — DUPLICATE VERIFICATION ENGINE",
        "=" * 80,
        "",
        "MODE",
        "READ ONLY",
        "",
        "SUMMARY",
        (
            "Pass 4A duplicate modules:           "
            f"{report['summary']['pass4a_duplicate_modules']}"
        ),
        (
            "Unique pairs verified:              "
            f"{report['summary']['unique_pairs_verified']}"
        ),
        (
            "Confirmed duplicate pairs:          "
            f"{report['summary']['confirmed_duplicate_pairs']}"
        ),
        (
            "Possible overlap pairs:             "
            f"{report['summary']['possible_overlap_pairs']}"
        ),
        (
            "Rejected false-positive pairs:      "
            f"{report['summary']['rejected_duplicate_pairs']}"
        ),
        (
            "Modules with confirmed duplicate:   "
            f"{report['summary']['modules_with_confirmed_duplicate']}"
        ),
        "",
        "LABEL COUNTS",
    ]

    for label, count in sorted(
        label_counts.items()
    ):
        lines.append(
            f"- {label:<38} {count}"
        )

    lines.extend(
        [
            "",
            "CONFIRMED DUPLICATES",
        ]
    )

    if confirmed:
        for item in confirmed:
            lines.append(
                f"- [{item['label']}] "
                f"confidence={item['confidence']}"
            )
            lines.append(
                f"    {item['left_path']}"
            )
            lines.append(
                f"    {item['right_path']}"
            )
            lines.append(
                "    Signals: "
                f"AST={item['signals']['module_ast_similarity']} "
                f"callables={item['signals']['callable_similarity']} "
                f"statements={item['signals']['statement_similarity']} "
                f"tokens={item['signals']['token_similarity']}"
            )
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "POSSIBLE IMPLEMENTATION OVERLAPS",
        ]
    )

    if possible_overlap:
        for item in possible_overlap:
            lines.append(
                f"- confidence={item['confidence']} "
                f"{item['left_path']}"
            )
            lines.append(
                f"    vs {item['right_path']}"
            )
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "TOP REJECTED FALSE POSITIVES",
        ]
    )

    if rejected:
        for item in rejected[:30]:
            lines.append(
                f"- [{item['label']}] "
                f"confidence={item['confidence']}"
            )
            lines.append(
                f"    {item['left_path']}"
            )
            lines.append(
                f"    {item['right_path']}"
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
                "Restore rejected duplicate modules to their "
                "original helper, runtime, provider, or ownership "
                "review classifications. Only confirmed pairs may "
                "enter consolidation review."
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
            "duplicate_verification_"
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
            "## Pass 4B — Duplicate Verification Engine\n"
            "\n"
            f"Audit time: `{completed_at.isoformat()}`\n"
            "\n"
            f"- Pass 4A duplicate modules: "
            f"{len(reported_duplicates)}\n"
            f"- Unique pairs verified: "
            f"{len(comparisons)}\n"
            f"- Confirmed duplicate pairs: "
            f"{len(confirmed)}\n"
            f"- Possible overlap pairs: "
            f"{len(possible_overlap)}\n"
            f"- Rejected false-positive pairs: "
            f"{len(rejected)}\n"
            "- Source modified: **NO**\n"
            "- Runtime wiring changed: **NO**\n"
            "- Broker execution enabled: **NO**\n"
            "- Live trading enabled: **NO**\n"
            "\n"
            "### Evidence\n"
            "\n"
            "- `runtime/hardening/workstream1/"
            "duplicate_verification/"
            "duplicate_verification_latest.json`\n"
            "- `runtime/hardening/workstream1/"
            "duplicate_verification/"
            "duplicate_verification_latest.txt`\n"
            "- `runtime/hardening/workstream1/"
            "duplicate_verification/"
            "duplicate_verification_latest.csv`\n"
            "\n"
        )

    print(rendered)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(
            main()
        )

    except DuplicateVerificationFailure as exc:
        print("=" * 80)
        print("WORKSTREAM 1 PASS 4B BLOCKED")
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
