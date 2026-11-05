
"""G43-R63: deterministic calculations from explicit input.

Educational calculations only.
No network, database, broker or order execution.
"""

from __future__ import annotations

import re
from decimal import Decimal, ROUND_HALF_UP, localcontext

D = Decimal
CENT = D("0.01")

NUM = r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"

VERSION = "NEUROVEST_G43_R63_NUMERICAL_VERIFICATION"


def value(text):
    return D(str(text).replace(",", ""))


def money(number):
    amount = number.quantize(
        CENT, rounding=ROUND_HALF_UP
    )
    return f"${amount:,.2f}"


def verified_answer(
    question,
    *,
    intent="general_conversation",
    context=None,
):
    """Return verified educational answer or None.

    Only unambiguous supported expressions are handled.
    Everything else continues through the original model.
    """
    if intent != "general_conversation":
        return None

    if not isinstance(question, str):
        return None

    if not 15 <= len(question) <= 1200:
        return None

    q = " ".join(question.split())

    if re.search(
        r"\b(?:neurovest|developer|broker|execute|"
        r"place order|submit order|live price|"
        r"current price|script|code|api)\b",
        q,
        re.I,
    ):
        return None

    with localcontext() as ctx:
        ctx.prec = 42

        # Sequential compound investment returns.
        pattern = (
            rf"(?:CAD\s*)?\$?({NUM})\s+earns\s+"
            r"(.+?)\s+in consecutive periods\.\s*"
            r"What is its final compounded value\?\s*"
            r"Give two decimals\."
        )

        m = re.fullmatch(pattern, q, re.I)

        if m:
            rates = re.fullmatch(
                r"\s*([+-]?\d+(?:\.\d+)?)%\s*,"
                r"\s*then\s*([+-]?\d+(?:\.\d+)?)%"
                r"\s*,\s*then\s*"
                r"([+-]?\d+(?:\.\d+)?)%\s*",
                m.group(2),
                re.I,
            )

            if rates:
                principal = value(m.group(1))
                percentages = [
                    D(x) for x in rates.groups()
                ]

                if principal > 0 and all(
                    D("-100") <= x <= D("1000")
                    for x in percentages
                ):
                    result = principal

                    for rate in percentages:
                        result *= 1 + rate / D(100)

                    return (
                        "**Compounded final value: "
                        f"CAD {money(result)}**. "
                        "Each percentage change applies "
                        "to the preceding period's balance."
                    )

        # Signed portfolio rebalancing arithmetic.
        pattern = (
            rf"A portfolio contains \$({NUM}) in equities "
            rf"and \$({NUM}) in bonds\. "
            rf"For a ({NUM})% equity target, "
            r"what is the signed CAD equity trade "
            r"\(positive means buy, negative means sell\)\?"
        )

        m = re.fullmatch(pattern, q, re.I)

        if m:
            equities, bonds, target = map(
                value, m.groups()
            )

            total = equities + bonds

            if (
                equities >= 0
                and bonds >= 0
                and total > 0
                and 0 <= target <= 100
            ):
                desired = total * target / D(100)
                change = desired - equities

                direction = (
                    "buy" if change > 0 else
                    "sell" if change < 0 else
                    "no trade"
                )

                return (
                    "**Signed equity adjustment: "
                    f"CAD {change:+,.2f}** "
                    f"({direction} {money(abs(change))}). "
                    f"Target equity value: {money(desired)}; "
                    f"current value: {money(equities)}. "
                    "Calculation only; no order submitted."
                )

        # Net stock-trading profit.
        pattern = (
            rf"Buy ({NUM}) shares at \$({NUM}) "
            rf"and sell at \$({NUM}); "
            rf"total commissions and fees are \$({NUM})\. "
            r"What is net profit before taxes\?"
        )

        m = re.fullmatch(pattern, q, re.I)

        if m:
            shares, buy, sell, fees = map(
                value, m.groups()
            )

            if min(shares, buy, sell, fees) >= 0:
                profit = shares * (sell - buy) - fees

                return (
                    "**Net profit before taxes: "
                    f"CAD {money(profit)}**. "
                    f"Calculation: {shares:g} shares × "
                    f"({money(sell)} − {money(buy)}) "
                    f"− {money(fees)} in total fees."
                )

        # Simple interest with a month duration.
        pattern = (
            rf"What is simple interest in CAD on "
            rf"\$({NUM}) at ({NUM})% annually "
            rf"for ({NUM}) months?, "
            r"ignoring compounding\?"
        )

        m = re.fullmatch(pattern, q, re.I)

        if m:
            principal, rate, months = map(
                value, m.groups()
            )

            if (
                principal >= 0
                and 0 <= rate <= 100
                and 0 <= months <= 1200
            ):
                interest = (
                    principal
                    * rate / D(100)
                    * months / D(12)
                )

                return (
                    "**Simple interest: "
                    f"CAD {money(interest)}**. "
                    f"Using principal × {rate}% × "
                    f"{months:g}/12 years."
                )

        # Distribution multiplied by share count.
        pattern = (
            rf"You own ({NUM}) shares and receive "
            rf"a CAD \$({NUM}) quarterly cash "
            r"distribution per share\. "
            r"What is the total quarterly "
            r"cash distribution\?"
        )

        m = re.fullmatch(pattern, q, re.I)

        if m:
            shares, distribution = map(
                value, m.groups()
            )

            if shares >= 0 and distribution >= 0:
                total = shares * distribution

                return (
                    "**Quarterly cash distribution: "
                    f"CAD {money(total)}**. "
                    f"{shares:g} shares × "
                    f"{money(distribution)} per share."
                )

        # Compound annual growth rate.
        pattern = (
            rf"An asset grows from \$({NUM}) "
            rf"to \$({NUM}) over exactly "
            r"(\d+|one|two|three|four|five) years?\. "
            r"What is its CAGR in percent\? "
            r"Give (two|three|four) decimals?\."
        )

        m = re.fullmatch(pattern, q, re.I)

        if m:
            start = value(m.group(1))
            end = value(m.group(2))

            names = {
                "one": 1,
                "two": 2,
                "three": 3,
                "four": 4,
                "five": 5,
            }

            raw_years = m.group(3).lower()
            years = D(
                names.get(raw_years, raw_years)
            )

            digits = {
                "two": 2,
                "three": 3,
                "four": 4,
            }[m.group(4).lower()]

            if (
                start > 0
                and end > 0
                and 0 < years <= 100
            ):
                growth = (
                    (end / start) ** (D(1) / years)
                    - D(1)
                ) * D(100)

                rounded = growth.quantize(
                    D(1).scaleb(-digits),
                    rounding=ROUND_HALF_UP,
                )

                return (
                    f"**CAGR: {rounded:.{digits}f}%**. "
                    "Calculated from the start value, "
                    "end value and exact holding period."
                )

    return None
