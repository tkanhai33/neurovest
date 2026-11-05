"""
NeuroVest R82: conservative assistant-response presentation cleanup.

Only repairs narrow, mechanically recognizable presentation defects.
Does not fetch evidence, invent citations, authorize tools, or trade.
"""

from __future__ import annotations

import re


def _unescape_markdown(line: str) -> str:
    # Only structural Markdown at the start of a line.
    # Do not alter arbitrary prose, URLs, financial values,
    # inline code, escaped expressions or citation contents.

    match = re.match(r"^([ \t]{0,3})\\(#{1,6})(?=\s)", line)
    if match:
        start = match.group(0)
        line = line.replace(
            start,
            match.group(1) + match.group(2),
            1,
        )

    match = re.match(
        r"^([ \t]{0,8})\\([-*+])(?=\s)",
        line,
    )
    if match:
        start = match.group(0)
        line = line.replace(
            start,
            match.group(1) + match.group(2),
            1,
        )

    match = re.match(r"^([ \t]{0,3})\\(>)(?=\s)", line)
    if match:
        start = match.group(0)
        line = line.replace(
            start,
            match.group(1) + match.group(2),
            1,
        )

    # Only unescape pipes on rows that are clearly intended
    # to be Markdown tables.
    if re.match(r"^\s*\\\|", line):
        if line.count(r"\|") >= 2:
            line = line.replace(r"\|", "|")

    return line


def _is_plain_prose(line: str) -> bool:
    value = line.strip()
    if not value:
        return False

    if value.startswith((
        "#", "-", "*", "+", ">", "|",
        "```", "~~~", "[", "http://", "https://",
    )):
        return False

    if re.match(r"^\d+[.)]\s", value):
        return False

    if "```" in value or "<" in value or ">" in value:
        return False

    if "http://" in value or "https://" in value:
        return False

    return True


def _deduplicate_truncated_prefix(lines: list[str]) -> list[str]:
    # Example:
    # Long complete-looking prefix ending "over 10"
    # Immediately followed by the same paragraph extended
    # to "...over 105%, while AMD...".
    #
    # Only delete a line if its entire substantive text
    # is the prefix of the *next* longer line.
    #
    # Avoid changing sections, quotations, citations, code,
    # financial values, lists, and intentionally short lines.

    result: list[str] = []
    i = 0

    while i < len(lines):
        if i + 1 < len(lines):
            current = lines[i]
            following = lines[i + 1]

            left = current.strip()
            right = following.strip()

            if (
                len(left) >= 100
                and len(right) >= len(left) + 12
                and _is_plain_prose(left)
                and _is_plain_prose(right)
                and right.startswith(left)
                and not left.endswith((".", "!", "?"))
            ):
                i += 1
                continue

        result.append(lines[i])
        i += 1

    return result


def clean_assistant_presentation(content: str) -> str:
    if not isinstance(content, str) or not content:
        return content

    # Never rewrite a full response containing Markdown
    # fenced code. A backslash might be meaningful code.
    if "```" in content or "~~~" in content:
        return content

    if len(content) > 50000:
        return content

    lines = content.split("\n")

    repaired = [
        _unescape_markdown(line)
        for line in lines
    ]

    repaired = _deduplicate_truncated_prefix(repaired)

    result = "\n".join(repaired)

    # Do not convert nonempty text to empty text.
    if content.strip() and not result.strip():
        return content

    return result
