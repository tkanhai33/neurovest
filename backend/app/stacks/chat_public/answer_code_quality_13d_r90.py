"""
NeuroVest R90: bounded Python-example validation.

Static validation only. Generated source is NEVER executed.
"""

from __future__ import annotations

import ast
import re
import textwrap


PYTHON_REQUEST = re.compile(
    r"\b(python|asyncio|threading|multiprocessing|"
    r"concurrent\.futures|python code|python example)\b",
    re.IGNORECASE,
)

FENCE = re.compile(
    r"(?m)^[ \t]{0,3}\\?```(?:python|py)[ \t]*\n"
    r"(.*?)"
    r"^[ \t]{0,3}\\?```[ \t]*$",
    re.DOTALL | re.MULTILINE | re.IGNORECASE,
)

CORE_CLAIM = re.compile(
    r"\b[Ee]ach task runs on a separate core\b"
)


def _python_syntax_error(code: str) -> str | None:
    if len(code) > 20000:
        return None

    try:
        ast.parse(textwrap.dedent(code))
        return None
    except SyntaxError as exc:
        line = exc.lineno or 0
        return f"Python syntax error at line {line}: {exc.msg}"


def _code_notice(error: str) -> str:
    return (
        "\n**Python example validation:** "
        "The generated example did not pass static "
        "syntax validation and should not be copied "
        "as working code. "
        + error
        + "\n"
    )


def inspect_python_answer(
    question: str,
    answer: str,
) -> tuple[str, dict]:
    result = {
        "scope": "not_applicable",
        "python_blocks": 0,
        "invalid_python_blocks": 0,
        "claim_corrections": 0,
        "executed_generated_code": False,
    }

    if not isinstance(question, str) or not isinstance(answer, str):
        return answer, result

    if not PYTHON_REQUEST.search(question):
        return answer, result

    if len(answer) > 50000:
        result["scope"] = "skipped_size"
        return answer, result

    result["scope"] = "python_programming"

    # Preserve developer-control, authentication,
    # finance, brokerage and trading answers.
    protected = re.search(
        r"\b(developer authorization|developer role|"
        r"brokerage|portfolio|trading orders|"
        r"financial results|sec filings|"
        r"account permissions)\b",
        question,
        re.IGNORECASE,
    )

    if protected:
        result["scope"] = "protected_request"
        return answer, result

    matches = list(FENCE.finditer(answer))
    result["python_blocks"] = len(matches)

    # Do not rewrite a response with malformed/unbalanced
    # fences. Such cases require a separate structural gate.
    opening_count = len(
        re.findall(
            r"(?m)^[ \t]{0,3}\\?```(?:python|py)[ \t]*$",
            answer,
            re.IGNORECASE,
        )
    )

    if opening_count != len(matches):
        result["scope"] = "unbalanced_fences"
        return answer, result

    changes = []

    for match in matches:
        code = match.group(1)
        error = _python_syntax_error(code)

        if error is None:
            continue

        result["invalid_python_blocks"] += 1

        # Retain the explanation, remove only the invalid
        # generated example. Do not attempt arbitrary fixes.
        changes.append(
            (match.start(), match.end(), _code_notice(error))
        )

    for start, end, replacement in reversed(changes):
        answer = answer[:start] + replacement + answer[end:]

    # Narrow, explicitly confirmed false guarantee.
    replacement = (
        "Separate processes can execute concurrently "
        "on available CPU cores, but a dedicated core "
        "per task and a speedup are not guaranteed"
    )

    answer, correction_count = CORE_CLAIM.subn(
        replacement,
        answer,
    )

    result["claim_corrections"] = correction_count
    return answer, result



# NEUROVEST_R92_R4_INTEGRATED_RELIABILITY
# Static code inspection only.
# Preserves R90 syntax validation and protected request scopes.

import ast as _r924_ast
import re as _r924_re
from urllib.parse import urlsplit as _r924_urlsplit

_r924_original = inspect_python_answer

_r924_scope = _r924_re.compile(
    r"\b(?:python|asyncio|threading|multiprocessing|"
    r"threadpoolexecutor|processpoolexecutor|"
    r"concurrent\.futures|python code|python example)\b",
    _r924_re.I,
)

_r924_protected = _r924_re.compile(
    r"\b(?:developer authorization|developer role|"
    r"brokerage|portfolio|trading orders|"
    r"financial results|sec filings|"
    r"account permissions)\b",
    _r924_re.I,
)

_r924_fence = _r924_re.compile(
    r"(?m)^[ \t]{0,3}\\?```"
)

_r924_python = _r924_re.compile(
    r"^[ \t]{0,3}\\?```(?:python|py)[ \t]*\n"
    r"(.*?)"
    r"^[ \t]{0,3}\\?```[ \t]*(?:\n|$)",
    _r924_re.I | _r924_re.M | _r924_re.S,
)

_r924_link = _r924_re.compile(
    r"\[([^\]\n]{1,250})\]"
    r"\((https?://[^\s)\n]{1,2000})\)"
)


def _r924_url_valid(value):
    try:
        parsed = _r924_urlsplit(value)
        return (
            parsed.scheme in ("http", "https")
            and bool(parsed.hostname)
            and not any(
                character in value
                for character in (
                    "`", "[", "]", " ", "\n", "\\"
                )
            )
        )
    except ValueError:
        return False


def _r924_links(text):
    count = 0

    def replace(match):
        nonlocal count
        label, url = match.groups()

        if not url.endswith("`"):
            return match.group(0)

        clean_url = url.rstrip("`")

        if not _r924_url_valid(clean_url):
            return match.group(0)

        clean_label = _r924_re.sub(
            r"`+[:\s]*$", "", label
        )

        if not clean_label.strip():
            return match.group(0)

        count += 1
        return f"[{clean_label}]({clean_url})"

    return _r924_link.sub(replace, text), count


def _r924_claims(text):
    rules = (
        (
            r"\bEach task runs on a separate core\b",
            "Separate processes can use available CPU "
            "cores, but a dedicated core per task "
            "is not guaranteed",
        ),
        (
            r"\bPython threads cannot run in parallel\b",
            "In conventional GIL-enabled CPython, "
            "CPU-bound Python threads generally cannot "
            "execute bytecode simultaneously; I/O can overlap",
        ),
        (
            r"\bmultiprocessing always run faster\b",
            "multiprocessing may improve CPU-bound "
            "performance, depending on workload, "
            "available cores and process overhead",
        ),
    )

    total = 0

    for pattern, replacement in rules:
        text, count = _r924_re.subn(
            pattern,
            replacement,
            text,
            flags=_r924_re.I,
        )
        total += count

    return text, total


def _r924_order_label(text, relevant):
    if not relevant:
        return text, 0

    return _r924_re.subn(
        r"(?m)^([ \t]*)(\*{0,2})"
        r"Expected Output:(\*{0,2})",
        r"\1\2Illustrative Output "
        r"(order may vary):\3",
        text,
    )


def _r924_outside_code(text, transform):
    boundaries = list(_r924_fence.finditer(text))

    if len(boundaries) % 2:
        return text, 0

    parts = []
    cursor = 0
    count = 0

    for index in range(0, len(boundaries), 2):
        start = boundaries[index].start()
        end = boundaries[index + 1].end()

        changed, amount = transform(text[cursor:start])
        parts.extend((changed, text[start:end]))
        count += amount
        cursor = end

    changed, amount = transform(text[cursor:])
    parts.append(changed)
    count += amount

    return "".join(parts), count


def _r924_code_facts(code):
    facts = {
        "http_calls": 0,
        "missing_timeouts": 0,
        "malformed_urls": 0,
        "handlers": 0,
        "completion_order": False,
    }

    if len(code) > 20000:
        return facts

    try:
        tree = _r924_ast.parse(code)
    except SyntaxError:
        return facts

    for node in _r924_ast.walk(tree):
        if isinstance(node, _r924_ast.ExceptHandler):
            facts["handlers"] += 1

        # Detect both imported symbols and actual calls.
        if isinstance(node, _r924_ast.ImportFrom):
            if (
                node.module == "concurrent.futures"
                and any(
                    item.name == "as_completed"
                    for item in node.names
                )
            ):
                facts["completion_order"] = True

        if isinstance(node, _r924_ast.Name):
            if node.id == "as_completed":
                facts["completion_order"] = True

        if not isinstance(node, _r924_ast.Call):
            continue

        func = node.func

        if isinstance(func, _r924_ast.Attribute):
            if func.attr == "as_completed":
                facts["completion_order"] = True

        if not (
            isinstance(func, _r924_ast.Attribute)
            and isinstance(func.value, _r924_ast.Name)
            and func.value.id in ("requests", "httpx")
            and func.attr in (
                "get", "post", "put", "patch",
                "delete", "head", "options",
            )
        ):
            continue

        facts["http_calls"] += 1

        if not any(
            keyword.arg == "timeout"
            for keyword in node.keywords
        ):
            facts["missing_timeouts"] += 1

        if node.args:
            first = node.args[0]
            if (
                isinstance(first, _r924_ast.Constant)
                and isinstance(first.value, str)
                and not _r924_url_valid(first.value)
            ):
                facts["malformed_urls"] += 1

    return facts


def inspect_python_answer(question, answer):
    response, info = _r924_original(question, answer)
    info = dict(info)

    info.update({
        "quality_engine": "R92-R4",
        "link_repairs": 0,
        "missing_timeouts": 0,
        "malformed_urls": 0,
        "output_label_repairs": 0,
        "network_calls": 0,
    })

    if not (
        isinstance(question, str)
        and isinstance(answer, str)
        and isinstance(response, str)
    ):
        return response, info

    if (
        not _r924_scope.search(question)
        or _r924_protected.search(question)
        or len(answer) > 50000
        or info.get("scope") in (
            "protected_request",
            "unbalanced_fences",
            "skipped_size",
        )
    ):
        return response, info

    if len(list(_r924_fence.finditer(answer))) % 2:
        return response, info

    notes = []
    completion_order = False

    for match in _r924_python.finditer(answer):
        facts = _r924_code_facts(match.group(1))

        info["network_calls"] += facts["http_calls"]
        info["missing_timeouts"] += facts["missing_timeouts"]
        info["malformed_urls"] += facts["malformed_urls"]

        completion_order |= facts["completion_order"]

        if facts["missing_timeouts"]:
            notes.append(
                "Some HTTP requests lack explicit timeouts."
            )

        if facts["malformed_urls"]:
            notes.append(
                "One or more literal HTTP URLs appear malformed."
            )

        if facts["http_calls"] and not facts["handlers"]:
            notes.append(
                "The example has HTTP requests without "
                "a visible exception handler."
            )

    response, count = _r924_outside_code(
        response, _r924_links
    )
    info["link_repairs"] = count

    response, count = _r924_outside_code(
        response, _r924_claims
    )
    info["claim_corrections"] = (
        info.get("claim_corrections", 0) + count
    )

    response, count = _r924_outside_code(
        response,
        lambda text: _r924_order_label(
            text, completion_order
        ),
    )
    info["output_label_repairs"] = count

    if notes:
        response += (
            "\n\n**Code reliability notes:**\n"
            + "".join(
                f"- {note}\n"
                for note in dict.fromkeys(notes)
            )
        )

    info["executed_generated_code"] = False
    return response, info

# NEUROVEST_R206_UNITTEST_STRUCTURE_GATE
# Static structure checks only. Generated code is never executed.
import ast as _nv206_ast
import re as _nv206_re

_nv206_previous_inspect = inspect_python_answer
_nv206_fences = _nv206_re.compile(
    r"(?m)^[ \t]{0,3}```(?:python|py)[ \t]*\n"
    r"(.*?)"
    r"^[ \t]{0,3}```[ \t]*$",
    _nv206_re.I | _nv206_re.S,
)

def inspect_python_answer(question, answer):
    response, info = _nv206_previous_inspect(question, answer)
    info = dict(info)

    requested = (
        isinstance(question, str)
        and PYTHON_REQUEST.search(question)
        and _nv206_re.search(
            r"\b(?:unittest|unit[ -]?tests?|unit[- ]testing)\b",
            question,
            _nv206_re.I,
        )
    )
    info["unittest_structure_issues"] = []

    if not requested or not isinstance(response, str):
        return response, info

    matches = list(_nv206_fences.finditer(response))
    needs_two_tests = bool(_nv206_re.search(
        r"\b(?:sequential|concurrent|parallel)\b",
        question,
        _nv206_re.I,
    ))

    invalid = []
    for index, match in enumerate(matches):
        try:
            tree = _nv206_ast.parse(match.group(1))
        except SyntaxError:
            continue  # R90 already handles syntax errors.

        issues = []

        # Catch executable self.assert... expressions outside a method.
        class TopLevelSelf(_nv206_ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                return
            def visit_AsyncFunctionDef(self, node):
                return
            def visit_ClassDef(self, node):
                return
            def visit_Lambda(self, node):
                return
            def visit_Name(self, node):
                if node.id == "self" and isinstance(node.ctx, _nv206_ast.Load):
                    issues.append("uses self at module level")

        visitor = TopLevelSelf()
        for statement in tree.body:
            if not isinstance(statement, (
                _nv206_ast.FunctionDef,
                _nv206_ast.AsyncFunctionDef,
                _nv206_ast.ClassDef,
            )):
                visitor.visit(statement)

        unittest_aliases = {"unittest"}
        testcase_aliases = {"TestCase"}
        for node in _nv206_ast.walk(tree):
            if isinstance(node, _nv206_ast.Import):
                for alias in node.names:
                    if alias.name == "unittest":
                        unittest_aliases.add(alias.asname or "unittest")
            elif isinstance(node, _nv206_ast.ImportFrom) and node.module == "unittest":
                for alias in node.names:
                    if alias.name == "TestCase":
                        testcase_aliases.add(alias.asname or "TestCase")

        test_methods = []
        for node in ast.walk(tree):
            if not isinstance(node, _nv206_ast.ClassDef):
                continue
            is_test_case = any(
                (
                    isinstance(base, _nv206_ast.Name)
                    and base.id in testcase_aliases
                )
                or (
                    isinstance(base, _nv206_ast.Attribute)
                    and base.attr == "TestCase"
                    and isinstance(base.value, _nv206_ast.Name)
                    and base.value.id in unittest_aliases
                )
                for base in node.bases
            )
            if is_test_case:
                test_methods.extend(
                    method for method in node.body
                    if isinstance(method, (
                        _nv206_ast.FunctionDef,
                        _nv206_ast.AsyncFunctionDef,
                    ))
                    and method.name.startswith("test_")
                )

        if not test_methods:
            issues.append("has no discoverable unittest.TestCase test methods")
        elif needs_two_tests and len(test_methods) < 2:
            issues.append("needs separate sequential and concurrent test methods")

        for method in test_methods:
            has_assertion = any(
                isinstance(node, _nv206_ast.Assert)
                or (
                    isinstance(node, _nv206_ast.Call)
                    and isinstance(node.func, _nv206_ast.Attribute)
                    and node.func.attr.startswith("assert")
                )
                for node in _nv206_ast.walk(method)
            )
            if not has_assertion:
                issues.append(f"{method.name} has no assertion")

        if issues:
            invalid.append((index, issues))

    if not invalid:
        return response, info

    info["invalid_unittest_structure_blocks"] = len(invalid)
    info["unittest_structure_issues"] = [
        issue for _, issues in invalid for issue in issues
    ]

    # Withhold only the flagged code blocks; preserve surrounding explanation.
    for index, issues in reversed(invalid):
        match = matches[index]
        notice = (
            "\n**Python example withheld:** it did not pass the static "
            "unittest structure check (" + "; ".join(issues) + "). "
            "No generated code was executed.\n"
        )
        response = response[:match.start()] + notice + response[match.end():]

    return response, info

# NEUROVEST_R210_PYTHON_FENCE_NORMALIZATION
# Normalize standalone Python examples and classify obvious non-Python fences.
import ast as _nv210_ast
import re as _nv210_re
import textwrap as _nv210_textwrap

_nv210_previous_inspect = inspect_python_answer
_nv210_fence_re = _nv210_re.compile(
    r"(?ms)^[ \t]{0,3}```(?P<lang>python|py)[ \t]*\n"
    r"(?P<code>.*?)"
    r"^[ \t]{0,3}```[ \t]*$",
    _nv210_re.I,
)
_nv210_sql_line = _nv210_re.compile(
    r"^(?:BEGIN|COMMIT|ROLLBACK|SELECT|INSERT|UPDATE|DELETE|"
    r"CREATE|ALTER|DROP)\b",
    _nv210_re.I,
)
_nv210_pseudo_markers = _nv210_re.compile(
    r"\b(?:exists in|process (?:payment|request)|save key|"
    r"if error|restore previous value)\b",
    _nv210_re.I,
)

def inspect_python_answer(question, answer):
    response, info = _nv210_previous_inspect(question, answer)
    info = dict(info)
    info["r210_python_fence_dedents"] = 0
    info["r210_sql_fence_relabels"] = 0
    info["r210_pseudocode_fence_relabels"] = 0
    info["r210_invalid_python_fence_blocks"] = 0
    info["r210_invalid_python_fence_issues"] = []

    if not isinstance(response, str):
        return response, info

    matches = list(_nv210_fence_re.finditer(response))
    question_text = question if isinstance(question, str) else ""
    debugging = bool(_nv210_re.search(
        r"\b(?:debug|debugging|troubleshoot|fix this|correct this)\b",
        question_text,
        _nv210_re.I,
    ))

    for index, match in reversed(list(enumerate(matches))):
        original_code = match.group("code")
        code = _nv210_textwrap.dedent(original_code)
        language = match.group("lang")
        nonblank = [line.strip() for line in code.splitlines() if line.strip()]

        is_sql = bool(nonblank) and all(
            line.startswith("--") or _nv210_sql_line.match(line)
            for line in nonblank
        )
        looks_pseudocode = (
            bool(_nv210_re.search(r"\bpseudocode\b", question_text, _nv210_re.I))
            or bool(_nv210_pseudo_markers.search(code))
        )

        new_language = language
        syntax_error = None

        if is_sql:
            new_language = "sql"
            info["r210_sql_fence_relabels"] += 1
        else:
            try:
                _nv210_ast.parse(code)
            except SyntaxError as exc:
                syntax_error = f"{exc.msg} at line {exc.lineno}"
                if looks_pseudocode:
                    new_language = "pseudocode"
                    info["r210_pseudocode_fence_relabels"] += 1

        # In a debugging answer, preserve an earlier intentionally broken
        # example when a later Python block provides the corrected version.
        preserve_original_debug_block = (
            debugging and index < len(matches) - 1
        )

        if (
            syntax_error
            and new_language.casefold() != "pseudocode"
            and not preserve_original_debug_block
        ):
            info["r210_invalid_python_fence_blocks"] += 1
            info["r210_invalid_python_fence_issues"].append(syntax_error)
            notice = (
                "\n**Python example withheld:** the fenced Python block "
                "did not parse as standalone Python. No generated code "
                "was executed.\n"
            )
            response = (
                response[:match.start()] + notice + response[match.end():]
            )
            continue

        if code != original_code:
            info["r210_python_fence_dedents"] += 1

        if code != original_code or new_language.casefold() != language.casefold():
            opening = response[match.start():match.start("lang")]
            separator = response[match.end("lang"):match.start("code")]
            closing = response[match.end("code"):match.end()]
            replacement = opening + new_language + separator + code + closing
            response = (
                response[:match.start()] + replacement + response[match.end():]
            )

    return response, info


# NEUROVEST_R215_KNOWN_TECHNICAL_ERROR_GUARD
import re as _r215_re

_r215_previous_inspect_python_answer = inspect_python_answer

_R215_WITHHELD_RESPONSE = (
    "I found a technical claim that failed a targeted correctness check, "
    "so I’m withholding this answer rather than risk misleading you. "
    "Please consult the relevant official documentation or ask for a "
    "narrower example."
)

def _r215_known_technical_issues(question, answer):
    question_text = str(question or "").casefold()
    answer_text = str(answer or "")
    answer_lower = answer_text.casefold()
    issues = []

    if "fastapi" in question_text:
        if _r215_re.search(
            r"from\s+fastapi\s+import[^\n]*\bRequestValidationError\b",
            answer_text,
            _r215_re.I,
        ):
            issues.append("RequestValidationError imported from the wrong FastAPI module")

        if _r215_re.search(
            r"\b(?:by default|default handler)\b.{0,180}"
            r"\b(?:do not|does not|never)\b.{0,80}\b(?:raw|input)\b",
            answer_text,
            _r215_re.I | _r215_re.S,
        ):
            issues.append("unqualified claim about default validation input disclosure")

    if "systemd" in question_text and "journalmaxuse" in answer_lower:
        issues.append("JournalMaxUse is not a documented journald storage-limit setting")

    if "typing" in question_text or "type checking" in question_text:
        if "cast" in answer_lower and (
            _r215_re.search(
                r"\b(?:runtime|crash|fail|error)\b.{0,100}\b(?:int|integer)\b",
                answer_lower,
                _r215_re.S,
            )
            or _r215_re.search(
                r"\b(?:int|integer)\b.{0,100}"
                r"\b(?:runtime|crash|fail|error)\b",
                answer_lower,
                _r215_re.S,
            )
        ):
            issues.append("claims typing.cast itself causes an integer runtime failure")


    normalized_answer = _r215_re.sub(r"[^a-z0-9]+", " ", answer_lower).strip()

    if "postgres" in question_text:
        if _r215_re.search(r"\brolls? back to the last begin\b", normalized_answer):
            issues.append(
                "incorrectly says PostgreSQL automatically rolls back to BEGIN"
            )

    if "systemd" in question_text:
        if any(
            directive in answer_lower
            for directive in ("journalmaxuse", "journalmaxfilesize")
        ):
            issues.append(
                "uses an unsupported journald setting name in the service example"
            )
        if (
            _r215_re.search(r"\b(?:indefinitely|without limit)\b", answer_lower)
            and not (
                "startlimitintervalsec" in answer_lower
                and "startlimitburst" in answer_lower
            )
        ):
            issues.append(
                "claims systemd restarts continue indefinitely without rate-limit qualification"
            )

    if "idempotency" in question_text:
        check_then_process = (
            _r215_re.search(
                r"if\s+idempotency_key\s+in\s+processed_requests",
                answer_lower,
            )
            and _r215_re.search(r"\bprocess\s*\(", answer_lower)
            and "processed_requests[" in answer_lower
        )
        concurrency_control = any(
            term in answer_lower
            for term in ("atomic", "transaction", "lock", "unique constraint")
        )
        if check_then_process and not concurrency_control:
            issues.append(
                "shows a non-atomic idempotency check-then-process example"
            )


    # NEUROVEST_R217_POSTGRES_IDEMPOTENCY_GUARDS
    if "postgres" in question_text:
        rollback_claims = (
            r"\btriggers?\s+an?\s+automatic\s+rollback\b",
            r"\bautomatically\s+(?:rolls?\s+back|undoes?)\b",
            r"\brolls?\s+back\s+(?:the\s+)?"
            r"(?:insert|prior|previous|earlier|preceding)\b",
        )
        for pattern in rollback_claims:
            match = _r215_re.search(pattern, answer_lower)
            if match:
                prefix = answer_lower[max(0, match.start() - 60):match.start()]
                if not _r215_re.search(
                    r"\b(?:not|never|does\s+not|doesn't|do\s+not)\b"
                    r"(?:\W+\w+){0,5}\W*$",
                    prefix,
                ):
                    issues.append(
                        "misstates PostgreSQL explicit-transaction rollback behavior"
                    )
                    break

    if "idempotency" in question_text:
        code_blocks = _r215_re.findall(
            r"```[^\n]*\n(.*?)```",
            answer_text,
            _r215_re.S,
        )
        for block in code_blocks:
            code = block.casefold()
            key_check = _r215_re.search(
                r"\bif\s+(?:key_exists\w*|"
                r"idempotency_key\s+in\s+\w+|"
                r"key\s+in\s+\w+)",
                code,
            )
            process = _r215_re.search(
                r"\bprocess(?:_request|_order)?\s*\(",
                code,
            )
            save_key = _r215_re.search(
                r"\b(?:store|save|cache|persist)\w*\s*\(",
                code,
            )
            concurrency_control = any(
                term in code
                for term in (
                    "atomic",
                    "transaction",
                    "lock",
                    "unique constraint",
                    "claim_idempotency_key",
                    "insert_if_absent",
                    "set nx",
                )
            )
            if (
                key_check
                and process
                and save_key
                and key_check.start() < process.start() < save_key.start()
                and not concurrency_control
            ):
                issues.append(
                    "shows a non-atomic idempotency check-process-store example"
                )
                break

    return issues

def inspect_python_answer(question, answer):
    candidate, report = _r215_previous_inspect_python_answer(question, answer)
    report = dict(report)
    issues = _r215_known_technical_issues(question, candidate)
    report["r215_known_technical_issues"] = issues
    report["r215_known_technical_blocks"] = int(bool(issues))
    if issues:
        candidate = _R215_WITHHELD_RESPONSE
    return candidate, report

