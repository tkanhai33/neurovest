from __future__ import annotations

import json
import os
import re
import urllib.request
from datetime import date
from decimal import Decimal, localcontext
from urllib.parse import quote

# NEUROVEST_13D_R57_SEC_RESEARCH
# Public SEC filings only: no private credentials,
# broker actions, database writes, or shell execution.

VERSION = "NEUROVEST_13D_R57_SEC_RESEARCH"

# Supported company names are explicit to avoid accidentally
# interpreting ordinary English words as ticker symbols.
COMPANIES = {
    "NVIDIA": ("NVDA", "0001045810"),
    "APPLE": ("AAPL", "0000320193"),
    "MICROSOFT": ("MSFT", "0000789019"),
    "AMAZON": ("AMZN", "0001018724"),
    "ALPHABET": ("GOOGL", "0001652044"),
    "GOOGLE": ("GOOGL", "0001652044"),
    "META": ("META", "0001326801"),
    "TESLA": ("TSLA", "0001318605"),
    "AMD": ("AMD", "0000002488"),
    "INTEL": ("INTC", "0000050863"),
}

TICKERS = {
    value[0]: (name, value[1])
    for name, value in COMPANIES.items()
}

RESEARCH_INTENT = re.compile(
    r"\b(?:revenue|gross profit|gross margin|"
    r"net income|financial results|financial performance|"
    r"annual results|earnings|10-k|"
    r"financial statements|revenue growth)\b",
    re.I,
)

# We deliberately require an explicit company reference.
def identify_company(message):
    if not isinstance(message, str):
        return None
    for name in sorted(COMPANIES, key=len, reverse=True):
        if re.search(r"\b" + re.escape(name) + r"\b", message, re.I):
            ticker, cik = COMPANIES[name]
            return name, ticker, cik
    match = re.search(
        r"(?:\bticker\s*[:=]?\s*|\$)([A-Za-z]{1,5})\b",
        message,
        re.I,
    )
    if match:
        ticker = match.group(1).upper()
        if ticker in TICKERS:
            name, cik = TICKERS[ticker]
            return name, ticker, cik
    return None

# SEC XBRL taxonomy may use different revenue tags.
TAGS = {
    "revenue": (
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
    ),
    "cost": (
        "CostOfRevenue",
        "CostOfGoodsAndServicesSold",
        "CostOfGoodsSold",
    ),
    "gross_profit": ("GrossProfit",),
    "net_income": ("NetIncomeLoss",),
}

def _get_json(url, *, opener=None, user_agent=None):
    agent = user_agent or os.environ.get(
        "NEUROVEST_SEC_USER_AGENT", ""
    ).strip()

    if (
        len(agent) < 12
        or len(agent) > 180
        or not re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", agent)
        or "\n" in agent
        or "\r" in agent
    ):
        raise ValueError("sec_user_agent_contact_required")

    if not re.fullmatch(
        r"https://data\.sec\.gov/api/xbrl/companyfacts/"
        r"CIK[0-9]{10}\.json",
        url,
    ):
        raise ValueError("unapproved_sec_url")

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": agent,
            "Accept": "application/json",
            "Accept-Encoding": "identity",
        },
    )
    transport = opener or urllib.request.urlopen
    with transport(request, timeout=12) as response:
        raw = response.read(5_000_001)

    if len(raw) > 5_000_000:
        raise ValueError("sec_response_too_large")

    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("invalid_sec_response")
    return data

def _latest_annual(facts, tags):
    us_gaap = facts.get("facts", {}).get("us-gaap", {})
    candidates = []

    for tag in tags:
        section = us_gaap.get(tag, {})
        rows = section.get("units", {}).get("USD", [])
        if not isinstance(rows, list):
            continue

        for row in rows:
            if not isinstance(row, dict):
                continue

            if row.get("form") not in ("10-K", "10-K/A"):
                continue

            if row.get("fp") != "FY":
                continue

            start = row.get("start")
            end = row.get("end")
            filed = row.get("filed")
            accession = row.get("accn")
            value = row.get("val")

            if not all(isinstance(x, str) for x in (
                start, end, filed, accession
            )):
                continue

            if isinstance(value, bool) or not isinstance(
                value, (int, float)
            ):
                continue

            try:
                duration = (
                    date.fromisoformat(end)
                    - date.fromisoformat(start)
                ).days
                date.fromisoformat(filed)
            except ValueError:
                continue

            # Prefer full-year figures rather than quarterly
            # comparative values in annual filings.
            if not 330 <= duration <= 380:
                continue

            number = Decimal(str(value))
            if not number.is_finite():
                continue

            candidates.append({
                "end": end,
                "filed": filed,
                "accn": accession,
                "value": number,
                "tag": tag,
                "start": start,
            })

    # Prefer the most recent fiscal period and the latest
    # filing for that period; preserve tag priority.
    if not candidates:
        return []

    dates = sorted(
        {item["end"] for item in candidates},
        reverse=True,
    )[:4]

    chosen = []
    for end in dates:
        group = [x for x in candidates if x["end"] == end]
        latest_filed = max(x["filed"] for x in group)
        group = [x for x in group if x["filed"] == latest_filed]
        group.sort(key=lambda x: tags.index(x["tag"]))
        chosen.append(group[0])

    return chosen

def extract_financials(facts, ticker, cik):
    if not isinstance(facts, dict):
        raise ValueError("invalid_facts")

    returned_cik = facts.get("cik")
    if returned_cik is None or int(returned_cik) != int(cik):
        raise ValueError("sec_cik_mismatch")

    series = {
        key: _latest_annual(facts, tags)
        for key, tags in TAGS.items()
    }
    revenues = series["revenue"]

    if not revenues:
        raise ValueError("annual_revenue_unavailable")

    latest = revenues[0]
    period = latest["end"]

    def same_period(name):
        return next(
            (item for item in series[name]
             if item["end"] == period),
            None,
        )

    gross = same_period("gross_profit")
    cost = same_period("cost")
    net = same_period("net_income")

    def dec(value):
        return str(value.normalize()) if value is not None else None

    revenue = latest["value"]
    gross_value = gross["value"] if gross else None

    # Calculated gross profit is only used when a comparable
    # cost-of-revenue record exists.
    gross_origin = "reported" if gross else None
    if gross_value is None and cost is not None:
        gross_value = revenue - cost["value"]
        gross_origin = "calculated_from_reported_values"

    with localcontext() as ctx:
        ctx.prec = 28
        gross_margin = (
            gross_value / revenue * Decimal(100)
            if gross_value is not None and revenue != 0
            else None
        )
        prior = revenues[1] if len(revenues) > 1 else None
        growth = (
            (revenue / prior["value"] - 1) * Decimal(100)
            if prior is not None and prior["value"] != 0
            else None
        )

    accession = latest["accn"]
    accession_flat = accession.replace("-", "")
    filing_link = (
        "https://www.sec.gov/Archives/edgar/data/"
        + str(int(cik))
        + "/"
        + accession_flat
        + "/"
    )

    return {
        "ticker": ticker,
        "source": "SEC EDGAR XBRL companyfacts",
        "source_endpoint": (
            "https://data.sec.gov/api/xbrl/companyfacts/"
            f"CIK{cik}.json"
        ),
        "filing_reference": filing_link,
        "form": "10-K",
        "fiscal_period_end": period,
        "revenue_filing_date": latest["filed"],
        "currency": "USD",
        "units": "dollars",
        "annual_revenue": dec(revenue),
        "prior_annual_revenue": (
            dec(prior["value"]) if prior else None
        ),
        "prior_period_end": prior["end"] if prior else None,
        "annual_revenue_growth_percent": dec(growth),
        "gross_profit": dec(gross_value),
        "gross_profit_origin": gross_origin,
        "gross_margin_percent": dec(gross_margin),
        "net_income": dec(net["value"]) if net else None,
        "net_income_filing_date": net["filed"] if net else None,
        "evidence_class": "public_sec_reported_or_derived",
        "notes": (
            "Annual 10-K XBRL figures only; not a live quote "
            "or necessarily the latest quarterly results. "
            "Different metric concepts or amended filings "
            "may affect comparability."
        ),
    }

def research_financials(message, *, opener=None, user_agent=None):
    if not isinstance(message, str) or len(message) > 500:
        return None
    if not RESEARCH_INTENT.search(message):
        return None

    match = identify_company(message)
    if match is None:
        return None

    name, ticker, cik = match
    url = (
        "https://data.sec.gov/api/xbrl/companyfacts/"
        f"CIK{cik}.json"
    )
    raw = _get_json(
        url,
        opener=opener,
        user_agent=user_agent,
    )
    result = extract_financials(raw, ticker, cik)
    result["company_reference"] = name
    return result

def attach_sec_research(context, message):
    # NEUROVEST_13D_R61_CANONICAL_MARKET_QUOTES
    from backend.app.stacks.chat_public.financial_research_13d_r58 import (
        attach_financial_research,
    )
    from backend.app.stacks.chat_public.market_quote_evidence_13d_r61 import (
        attach_market_quote_evidence,
    )
    research_context = attach_financial_research(
        context, message
    )
    return attach_market_quote_evidence(
        research_context, message
    )
