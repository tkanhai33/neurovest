"""
NeuroVest R106-FIX2: final response presentation cleanup.

Pure text cleanup. Does not retrieve data, call models,
alter permissions, or authorize financial execution.
"""

from __future__ import annotations

import re

# NEUROVEST_R106_FIX2_RESPONSE_CLEANUP

EMPTY_SOURCE = re.compile(
    r"(?:\n[ \t]*)*Approved local research source:"
    r"[ \t\r\n]*\Z",
    re.IGNORECASE,
)

INTERNAL_MARKER = re.compile(
    r"^[ \t]*\[NEUROVEST_R105\][ \t]*$",
    re.MULTILINE,
)

# Match the column anywhere in a Markdown table row,
# including the second column after **Metric**.
DATE_HEADING = re.compile(
    r"(?i)(\|[ \t]*)"
    r"\*\*Fiscal Period End\*\*"
    r"([ \t]*\|)",
)

def cleanup_response(value):
    if not isinstance(value, str):
        return value

    if not value or len(value) > 100000:
        return value

    original = value

    value = INTERNAL_MARKER.sub("", value)

    if (
        "Yahoo Finance" in value
        and "yfinance" in value.lower()
    ):
        value = DATE_HEADING.sub(
            lambda m: (
                m.group(1)
                + "**Yahoo Finance Statement Date**"
                + m.group(2)
            ),
            value,
        )

    value = EMPTY_SOURCE.sub("", value)

    value = value.rstrip()

    return value if value.strip() else original
