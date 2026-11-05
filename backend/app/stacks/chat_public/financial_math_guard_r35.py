
"""Read-only, deterministic ordinary-annuity projections."""
from __future__ import annotations

import re
from decimal import Decimal, ROUND_HALF_UP, localcontext

AMOUNT = re.compile(r"\$\s*([\d,]+(?:\.\d{1,2})?)")
YEARS = re.compile(r"\b(\d{1,2})\s+years?\b", re.I)
RATE = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*%\s*"
    r"(?:annual|annually|per year|yearly)\b", re.I
)
END = re.compile(
    r"(?:at the end of (?:every|each|the) month|"
    r"end[- ]of[- ]month)", re.I
)
COMPOUND = re.compile(r"compound(?:ed|ing)? monthly", re.I)
EXCLUDE = re.compile(
    r"\b(?:initial investment|initial lump sum|starting balance|"
    r"withdrawals?|fees?|taxes|inflation|variable rates?|"
    r"weekly|daily|beginning of (?:each|every|the) month|"
    r"additional contributions|increase(?:d|s|ing)? deposits|"
    r"decrease(?:d|s|ing)? deposits)\b", re.I
)
CENT = Decimal("0.01")

def calculate(payment, annual_rate_percent, years):
    payment = Decimal(str(payment))
    rate = Decimal(str(annual_rate_percent))
    years = int(years)
    if not payment.is_finite() or not rate.is_finite():
        raise ValueError("nonfinite input")
    if not (0 < payment <= 100000000):
        raise ValueError("invalid payment")
    if not (0 <= rate <= 100):
        raise ValueError("invalid rate")
    if not (1 <= years <= 80):
        raise ValueError("invalid years")
    n = 12 * years
    with localcontext() as ctx:
        ctx.prec = 40
        r = rate / Decimal(1200)
        total = (
            payment * n if r == 0
            else payment * (((1 + r) ** n - 1) / r)
        )
        deposits = payment * n
        total = total.quantize(CENT, rounding=ROUND_HALF_UP)
        deposits = deposits.quantize(CENT, rounding=ROUND_HALF_UP)
        growth = total - deposits
    return total, deposits, growth

def answer_explicit_monthly_projection(
    message, *, intent="general_conversation", context=None
):
    if not isinstance(message, str):
        return None
    if intent not in ("general_conversation", "trading_conversation"):
        return None
    if context and str(context).strip():
        return None
    if EXCLUDE.search(message):
        return None
    if not END.search(message) or not COMPOUND.search(message):
        return None
    if not re.search(r"\b(?:invest|deposit|contribut|sav)\w*\b", message, re.I):
        return None

    amounts = AMOUNT.findall(message)
    years = YEARS.findall(message)
    rates = RATE.findall(message)
    if (len(amounts), len(years), len(rates)) != (1, 1, 1):
        return None

    # Only route explicit end-of-month, single-rate projections.
    try:
        payment = Decimal(amounts[0].replace(",", ""))
        annual_rate = Decimal(rates[0])
        duration = int(years[0])
        total, deposits, growth = calculate(
            payment, annual_rate, duration
        )
    except (ValueError, ArithmeticError):
        return None

    return (
        f"With ${payment:,.2f} invested at the end of each month "
        f"for {duration} years, assuming a hypothetical "
        f"{annual_rate}% nominal annual return compounded monthly:\n\n"
        f"- **Projected total value:** ${total:,.2f}\n"
        f"- **Your contributions:** ${deposits:,.2f}\n"
        f"- **Projected growth:** ${growth:,.2f}\n\n"
        "The total already includes your contributions; "
        "don't add them again. This illustration assumes a "
        "constant return, with no fees, taxes, or inflation "
        "adjustments. Actual investment returns vary and "
        "are not guaranteed."
    )
