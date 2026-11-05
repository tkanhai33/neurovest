"""Owner-scoped historical portfolio research; read-only."""
import asyncio
import math
import re
from concurrent.futures import ThreadPoolExecutor

PREFIX = "R117_PORTFOLIO_OPPORTUNITY_VERIFIED\n"
PERIODS = (("3m", 63), ("6m", 126), ("12m", 252))

REQUEST = re.compile(
    r"\b(?:my\s+portfolio|portfolio|my\s+holdings|holdings)\b", re.I
)
SYMBOL_REQUEST = re.compile(
    r"\b(?:symbols?|stocks?|tickers?|equities)\b", re.I
)
BETTER_REQUEST = re.compile(
    r"\b(?:better|outperform|do\s+better|higher\s+return|"
    r"best\s+performing)\b",
    re.I,
)
EXECUTION = re.compile(
    r"\b(?:buy|sell|execute|place|submit|cancel|liquidate)\b"
    r".{0,80}\b(?:shares?|orders?|trades?|positions?)\b",
    re.I | re.S,
)


def _is_execution_request(message):
    for match in EXECUTION.finditer(message):
        prior = message[:match.start()]
        clause = re.split(
            r"[.!?;,\n]|\b(?:but|however|instead)\b",
            prior,
            flags=re.I,
        )[-1]
        if re.search(
            r"\b(?:don't|don’t|do not|never|not|won't|won’t|"
            r"will not|wouldn't|wouldn’t|would not)\b",
            clause,
            re.I,
        ):
            continue
        return True
    return False


def _quotes(response):
    if not isinstance(response, dict):
        return []
    rows = response.get("quotes")
    if isinstance(rows, list):
        return rows
    try:
        rows = response["finance"]["result"][0]["quotes"]
        return rows if isinstance(rows, list) else []
    except (KeyError, IndexError, TypeError):
        return []


def _screen(region):
    import yfinance as yf
    from yfinance import EquityQuery

    query = EquityQuery("and", [
        EquityQuery("eq", ["region", region]),
        EquityQuery("gte", ["intradaymarketcap", 1_000_000_000]),
        EquityQuery("gte", ["intradayprice", 5]),
        EquityQuery("gt", ["dayvolume", 50_000]),
    ])
    response = yf.screen(
        query, size=8, sortField="intradaymarketcap", sortAsc=False
    )

    result = []
    for row in _quotes(response):
        if not isinstance(row, dict):
            continue
        symbol = row.get("symbol")
        currency = str(row.get("currency") or "").strip().upper()
        if (
            isinstance(symbol, str)
            and re.fullmatch(r"[A-Za-z0-9.^-]{1,16}", symbol)
            and currency in {"CAD", "USD"}
        ):
            result.append({
                "symbol": symbol.upper(),
                "currency": currency,
                "region": region,
                "name": str(row.get("longName") or row.get("shortName") or ""),
            })
    return result


def _date_key(value):
    try:
        return value.date().isoformat()
    except Exception:
        return str(value)[:10]


def _completed_daily_bars(symbol):
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from backend.app.stacks.market_data.bars import get_bars

    rows = get_bars(symbol, limit=254, include_adjusted_close=True)
    today = datetime.now(
        ZoneInfo("America/Toronto")
    ).date()
    completed = []
    for row in rows:
        stamp = str(row.get("timestamp") or "")
        try:
            bar_date = datetime.fromisoformat(
                stamp.replace("Z", "+00:00")
            ).astimezone(
                ZoneInfo("America/Toronto")
            ).date()
        except (TypeError, ValueError):
            continue
        # Exclude today's bar so an in-progress daily candle cannot enter returns.
        if bar_date < today:
            completed.append(row)
    return completed


def _load_fx():
    rates = {}
    for row in _completed_daily_bars("USDCAD=X"):
        day = _date_key(row.get("timestamp"))
        try:
            value = float(row.get("close"))
        except (TypeError, ValueError, OverflowError):
            continue
        if math.isfinite(value) and value > 0:
            rates[day] = value

    if not rates:
        raise ValueError("USD/CAD history unavailable")
    latest_date = max(rates)
    return rates, rates[latest_date], latest_date


def _symbol_root(symbol):
    return re.sub(r"\.(?:TO|V|NE|CN)$", "", symbol.strip().upper())


def _issuer_key(name, symbol):
    clean = re.sub(r"[^a-z0-9]+", " ", str(name).lower()).strip()
    ignored = {
        "inc", "incorporated", "corp", "corporation", "ltd", "limited",
        "plc", "company", "co", "class", "cdr", "depositary", "receipt",
    }
    tokens = [part for part in clean.split() if part not in ignored]
    if tokens:
        return " ".join(tokens)
    return re.sub(r"\.(?:TO|V|NE|CN)$", "", symbol.upper())


def _history(symbol, currency, fx_rates):
    try:
        bars = _completed_daily_bars(symbol)
        closes = {}

        for row in bars:
            day = _date_key(row.get("timestamp"))
            raw_price = (
                row.get("close")
                if symbol == "USDCAD=X"
                else row.get("adjusted_close")
            )
            try:
                price = float(raw_price)
            except (TypeError, ValueError, OverflowError):
                continue
            if math.isfinite(price) and price > 0:
                closes[day] = price

        if symbol == "USDCAD=X":
            return closes or None

        if currency == "USD":
            values = {
                day: price * fx_rates[day]
                for day, price in closes.items()
                if day in fx_rates
            }
        elif currency == "CAD":
            values = closes
        else:
            return None

        days = sorted(values)
        prices = {day: values[day] for day in days}
        daily = {}
        for index in range(1, len(days)):
            previous = prices[days[index - 1]]
            if previous > 0:
                daily[days[index]] = prices[days[index]] / previous - 1

        if len(daily) < 22:
            return None
        return {
            "prices": prices,
            "daily": daily,
            "quote_date": days[-1],
            "sessions": len(daily),
        }
    except Exception:
        return None


def _compound(values):
    result = 1.0
    for value in values:
        result *= 1.0 + value
    return (result - 1.0) * 100.0


def _period_return(history, sessions):
    days = sorted(history["prices"])
    if len(days) <= sessions:
        return None
    start = history["prices"][days[-sessions - 1]]
    end = history["prices"][days[-1]]
    if start <= 0:
        return None
    return (end / start - 1.0) * 100.0


def _period_text(history):
    parts = []
    for label, sessions in PERIODS:
        result = _period_return(history, sessions)
        if result is None:
            parts.append(f"{label} unavailable ({history['sessions']} sessions)")
        else:
            parts.append(f"{label} {result:+.2f}%")
    return "; ".join(parts)


def _annualized_volatility(daily_values, sessions=252):
    values = list(daily_values)[-sessions:]
    if len(values) < 22:
        return None
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    return math.sqrt(variance * 252) * 100.0


def _max_drawdown(history, sessions=252):
    days = sorted(history["prices"])[-(sessions + 1):]
    if len(days) < 22:
        return None
    peak = 0.0
    worst = 0.0
    for day in days:
        value = history["prices"][day]
        peak = max(peak, value)
        if peak > 0:
            worst = min(worst, value / peak - 1.0)
    return worst * 100.0


def _correlation(left_prices, right_prices, minimum=60, maximum=252):
    common = sorted(set(left_prices) & set(right_prices))
    common = common[-(maximum + 1):]
    if len(common) < minimum + 1:
        return None, max(0, len(common) - 1)

    xs = []
    ys = []
    for index in range(1, len(common)):
        previous_day = common[index - 1]
        day = common[index]
        left_previous = left_prices[previous_day]
        right_previous = right_prices[previous_day]
        left_current = left_prices[day]
        right_current = right_prices[day]
        if (
            left_previous <= 0
            or right_previous <= 0
            or left_current <= 0
            or right_current <= 0
        ):
            continue
        xs.append(left_current / left_previous - 1.0)
        ys.append(right_current / right_previous - 1.0)

    if len(xs) < minimum:
        return None, len(xs)

    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    var_x = sum((value - mean_x) ** 2 for value in xs)
    var_y = sum((value - mean_y) ** 2 for value in ys)
    if var_x <= 0 or var_y <= 0:
        return None, len(xs)

    covariance = sum(
        (xs[index] - mean_x) * (ys[index] - mean_y)
        for index in range(len(xs))
    )
    return covariance / math.sqrt(var_x * var_y), len(xs)


# R117_SNAPTRADE_CASH_SCENARIO_V1
def _cash_scenario_lines(
    *,
    balance_snapshot,
    balance_error,
    candidates,
    start_day,
    end_day,
    fx_rates,
):
    lines = [
        "",
        "Hypothetical cash scenarios (historical, not a recommendation):",
        "The latest stored SnapTrade cash is treated as if it had been available "
        "at the historical start date. This is not the account's actual past cash.",
        "Only positive cash_amount rows are used, grouped by currency. "
        "Buying power is ignored; no cross-currency conversion is assumed.",
        "Each candidate is a separate alternative. Cash left uninvested is shown "
        "with a 0% return assumption; fees, taxes, and interest are excluded.",
        "The stored balance reader does not expose a separate cash as-of timestamp.",
    ]

    if balance_error:
        lines.append(
            "Cash scenario unavailable: stored SnapTrade balances could not be read "
            f"({balance_error})."
        )
        return lines

    if not isinstance(balance_snapshot, dict):
        lines.append("Cash scenario unavailable: no stored SnapTrade balance snapshot.")
        return lines

    rows = balance_snapshot.get("balances")
    if not isinstance(rows, list) or not rows:
        lines.append("Cash scenario unavailable: no stored balance rows were returned.")
        return lines

    cash_by_currency = {}
    ignored_rows = 0
    for row in rows:
        if not isinstance(row, dict):
            ignored_rows += 1
            continue
        currency = str(row.get("currency") or "").strip().upper()
        try:
            amount = float(row.get("cash_amount"))
        except (TypeError, ValueError, OverflowError):
            ignored_rows += 1
            continue
        if (
            currency not in {"CAD", "USD"}
            or not math.isfinite(amount)
            or amount <= 0
        ):
            ignored_rows += 1
            continue
        cash_by_currency[currency] = cash_by_currency.get(currency, 0.0) + amount

    if not cash_by_currency:
        lines.append(
            "Cash scenario unavailable: no positive CAD or USD SnapTrade "
            "cash_amount rows were available."
        )
        return lines

    for currency, amount in sorted(cash_by_currency.items()):
        lines.append(
            f"Stored positive {currency} cash used for scenarios: "
            f"{amount:,.2f} {currency}."
        )
    if ignored_rows:
        lines.append(
            f"Ignored {ignored_rows} balance row(s) with missing, unsupported, "
            "negative, or non-finite cash."
        )

    if not start_day or not end_day:
        lines.append(
            "Cash scenarios unavailable because the portfolio benchmark "
            "date window could not be established."
        )
        return lines

    scenario_count = 0
    for candidate in candidates:
        chosen = candidate.get("chosen", {})
        symbol = chosen.get("symbol")
        currency = str(chosen.get("currency") or "").upper()
        amount = cash_by_currency.get(currency)
        history = candidate.get("history")

        if not symbol or currency not in {"CAD", "USD"} or not amount:
            continue
        if not isinstance(history, dict):
            continue

        prices = history.get("prices")
        if not isinstance(prices, dict):
            continue
        start_price = prices.get(start_day)
        end_price = prices.get(end_day)
        if start_price is None or end_price is None:
            lines.append(
                f"- {symbol}: same-currency {currency} cash scenario unavailable; "
                f"a price is missing on {start_day} or {end_day}."
            )
            continue

        try:
            start_price = float(start_price)
            end_price = float(end_price)
            if currency == "USD":
                start_fx = float(fx_rates[start_day])
                end_fx = float(fx_rates[end_day])
                start_price /= start_fx
                end_price /= end_fx
        except (KeyError, TypeError, ValueError, OverflowError):
            lines.append(
                f"- {symbol}: same-currency {currency} cash scenario unavailable; "
                "price or FX data is missing."
            )
            continue

        if (
            not math.isfinite(start_price)
            or not math.isfinite(end_price)
            or start_price <= 0
            or end_price <= 0
        ):
            continue

        end_value = amount * end_price / start_price
        change = end_value - amount
        pct_change = (end_price / start_price - 1.0) * 100.0
        lines.append(
            f"- {symbol}: hypothetical {amount:,.2f} {currency} at the "
            f"{start_day} adjusted close becomes {end_value:,.2f} {currency} "
            f"at the {end_day} adjusted close "
            f"({change:+,.2f} {currency}; {pct_change:+.2f}%), "
            f"versus {amount:,.2f} {currency} left as cash."
        )
        scenario_count += 1

    if scenario_count == 0:
        lines.append(
            "No candidate had both positive same-currency SnapTrade cash and "
            "complete prices for the benchmark window."
        )

    lines.append(
        "These are independent hindsight scenarios using today's stored cash "
        "amount and the current screen's candidates; they do not establish that "
        "the cash was available on the historical start date."
    )
    return lines


def _build_report(positions, balance_snapshot=None, balance_error=None):
    errors = []
    screened = {"ca": [], "us": []}
    for region in ("ca", "us"):
        try:
            screened[region] = _screen(region)
        except Exception as exc:
            errors.append(f"{region.upper()} screen unavailable ({type(exc).__name__})")

    try:
        fx_rates, latest_fx, fx_date = _load_fx()
    except Exception as exc:
        fx_rates, latest_fx, fx_date = {}, None, None
        errors.append(f"USD/CAD history unavailable ({type(exc).__name__})")

    holdings = []
    for row in positions if isinstance(positions, (list, tuple)) else []:
        if not isinstance(row, dict):
            continue
        symbol = str(row.get("symbol") or "").strip().upper()
        currency = str(row.get("currency") or "").strip().upper()
        if not symbol:
            continue
        try:
            value = float(row.get("market_value"))
            if not math.isfinite(value):
                value = None
        except (TypeError, ValueError, OverflowError):
            value = None
        holdings.append({
            "symbol": symbol,
            "currency": currency,
            "market_value": value,
            "last_synced_at": row.get("last_synced_at"),
        })

    if not holdings:
        return "No stored position rows were available for this owner."

    symbols = {row["symbol"] for row in holdings}
    currencies = {row["symbol"]: row["currency"] for row in holdings}
    for rows in screened.values():
        for row in rows:
            symbols.add(row["symbol"])
            currencies.setdefault(row["symbol"], row["currency"])

    ordered = sorted(symbols)
    with ThreadPoolExecutor(max_workers=6) as pool:
        histories = dict(zip(
            ordered,
            pool.map(
                lambda symbol: _history(
                    symbol, currencies.get(symbol), fx_rates
                ),
                ordered,
            ),
        ))

    # Approximate a daily-rebalanced benchmark using current position values.
    # Suppress it if any holding with value cannot be represented.
    weighted_positions = []
    skipped_weights = 0
    for row in holdings:
        value = row["market_value"]
        currency = row["currency"]
        if value is None or value < 0 or currency not in {"CAD", "USD"}:
            skipped_weights += 1
            continue
        if value == 0:
            continue
        history = histories.get(row["symbol"])
        if not isinstance(history, dict):
            skipped_weights += 1
            continue
        if currency == "USD":
            if latest_fx is None:
                skipped_weights += 1
                continue
            value *= latest_fx
        weighted_positions.append((row["symbol"], value))

    total_value = sum(value for _, value in weighted_positions)
    portfolio_prices = {}
    benchmark_eligible = (
        skipped_weights == 0
        and bool(weighted_positions)
        and total_value > 0
    )
    if benchmark_eligible:
        weights = [
            (symbol, value / total_value)
            for symbol, value in weighted_positions
        ]
        common_days = sorted(set.intersection(*[
            set(histories[symbol]["prices"])
            for symbol, _ in weights
        ]))
        if len(common_days) >= 2:
            portfolio_prices[common_days[0]] = 100.0
            for previous_day, day in zip(common_days, common_days[1:]):
                interval_return = sum(
                    weight * (
                        histories[symbol]["prices"][day]
                        / histories[symbol]["prices"][previous_day]
                        - 1.0
                    )
                    for symbol, weight in weights
                )
                portfolio_prices[day] = (
                    portfolio_prices[previous_day] * (1.0 + interval_return)
                )
        else:
            benchmark_eligible = False

    held_roots = {
        _symbol_root(row["symbol"])
        for row in holdings
    }

    # Group issuer listings across regions when normalized Yahoo names match.
    groups = {}
    for region in ("ca", "us"):
        for row in screened[region]:
            key = _issuer_key(row["name"], row["symbol"])
            group = groups.setdefault(key, {
                "key": key, "listings": [], "regions": set()
            })
            if row["symbol"] not in {
                item["symbol"] for item in group["listings"]
            }:
                group["listings"].append(row)
            group["regions"].add(region)

    candidates = []
    for key, group in groups.items():
        candidate_roots = {
            _symbol_root(item["symbol"])
            for item in group["listings"]
        }
        if candidate_roots & held_roots:
            continue
        available = [
            row for row in group["listings"]
            if isinstance(histories.get(row["symbol"]), dict)
        ]
        if not available:
            continue
        # Prefer a CAD listing; otherwise use the FX-converted USD listing.
        available.sort(
            key=lambda row: (row["currency"] != "CAD", row["region"] != "ca")
        )
        chosen = available[0]
        candidates.append({
            **group,
            "chosen": chosen,
            "history": histories[chosen["symbol"]],
        })

    # Keep ranking transparent: sort on 3-month return and show longer windows,
    # risk, drawdown, and correlation beside it. Short-history names stay visible.
    candidates.sort(
        key=lambda row: (
            _period_return(row["history"], 63) is not None,
            _period_return(row["history"], 63) or -float("inf"),
        ),
        reverse=True,
    )

    lines = [
        "Owner-scoped portfolio comparison — historical research, not a prediction.",
        "Returns use adjusted daily closes.",
        "Candidate sample: up to 8 liquid, large-cap listings per region, "
        "screened by market capitalization.",
    ]
    if fx_rates:
        lines.append("USD listings are converted to CAD using date-aligned USD/CAD closes.")
    else:
        lines.append(
            "USD/CAD conversion is unavailable; USD-denominated comparisons "
            "are excluded where conversion is required."
        )
    if fx_date:
        lines.append(f"USD/CAD source: Yahoo Finance USDCAD=X; latest rate date {fx_date}.")
    lines.extend(errors)

    sync_times = sorted({
        str(row["last_synced_at"])
        for row in holdings
        if row.get("last_synced_at")
    })
    if sync_times:
        lines.append("Stored position sync time(s): " + ", ".join(sync_times))

    common_benchmark_days = sorted(portfolio_prices)
    lines.append("")
    if benchmark_eligible and len(common_benchmark_days) > 63:
        benchmark_3m = (
            portfolio_prices[common_benchmark_days[-1]]
            / portfolio_prices[common_benchmark_days[-64]]
            - 1.0
        ) * 100.0
        lines.append(
            f"Rough daily-rebalanced current-weight portfolio 3-month return: "
            f"{benchmark_3m:+.2f}% CAD."
        )
        lines.append(
            "Benchmark price window: "
            f"{common_benchmark_days[-64]} through "
            f"{common_benchmark_days[-1]} "
            "(64 daily closes, 63 return intervals)."
        )
    else:
        benchmark_3m = None
        if skipped_weights:
            lines.append(
                "Whole-portfolio benchmark unavailable: "
                f"{skipped_weights} holding row(s) could not be included."
            )
        else:
            lines.append(
                "Portfolio benchmark unavailable: fewer than 64 common daily price dates."
            )

    lines.append(
        "Portfolio correlation uses returns over the same common price-date "
        "intervals; it is a historical diversification clue, not a guarantee."
    )

    lines.append("")

    lines.append("Candidate screen results (sorted by 3-month return when available):")
    comparison_results = []
    for row in candidates[:8]:
        chosen = row["chosen"]
        history = row["history"]
        aliases = sorted({
            item["symbol"] for item in row["listings"]
            if item["symbol"] != chosen["symbol"]
        })
        alias_text = f"; also listed as {', '.join(aliases)}" if aliases else ""
        region_text = (
            "Canadian and U.S. screens"
            if len(row["regions"]) == 2
            else "Canadian screen" if "ca" in row["regions"]
            else "U.S. screen"
        )

        details = _period_text(history)
        volatility = _annualized_volatility(history["daily"].values())
        drawdown = _max_drawdown(history)
        if volatility is None:
            details += "; volatility unavailable"
        else:
            details += f"; recent annualized volatility {volatility:.1f}%"
        if drawdown is None:
            details += "; 12m drawdown unavailable"
        else:
            details += f"; max drawdown over available 12m window {drawdown:.1f}%"

        correlation, corr_sessions = _correlation(
            history["prices"], portfolio_prices
        )
        if correlation is None:
            details += f"; portfolio correlation unavailable ({corr_sessions} common sessions)"
        else:
            details += (
                f"; correlation to current-weight portfolio {correlation:+.2f} "
                f"({corr_sessions} common sessions)"
            )

        if benchmark_3m is not None:
            # Compare every candidate on the benchmark's exact endpoint dates.
            start_day = common_benchmark_days[-64]
            end_day = common_benchmark_days[-1]
            if (
                start_day in history["prices"]
                and end_day in history["prices"]
            ):
                candidate_3m = (
                    history["prices"][end_day]
                    / history["prices"][start_day]
                    - 1.0
                ) * 100.0
                difference = candidate_3m - benchmark_3m
                comparison_results.append(
                    (chosen["symbol"], difference, start_day, end_day)
                )
                details += (
                    f"; {difference:+.2f} percentage points vs. benchmark "
                    f"over the same dates {start_day} to {end_day}"
                )
            else:
                details += (
                    "; same-window comparison unavailable "
                    f"(benchmark dates {start_day} to {end_day}; "
                    "candidate close missing at an endpoint)"
                )

        lines.append(
            f"- {chosen['symbol']} ({chosen['currency']}; {region_text})"
            f"{alias_text}: {details}; quote date {history['quote_date']}."
        )

    if benchmark_3m is not None:
        outperformers = [
            item for item in comparison_results if item[1] > 0
        ]
        if outperformers:
            lines.append(
                "Screened symbols above the portfolio benchmark over their "
                "matching date windows: "
                + ", ".join(
                    f"{symbol} ({difference:+.2f} percentage points; "
                    f"{start} to {end})"
                    for symbol, difference, start, end in outperformers
                )
                + "."
            )
        elif comparison_results:
            lines.append(
                "None of the evaluated symbols in this limited screen sample "
                "outperformed the portfolio benchmark over matching dates."
            )
        else:
            lines.append(
                "No candidate had enough matching daily price dates for an "
                "outperformance comparison."
            )

    lines.extend(_cash_scenario_lines(
        balance_snapshot=balance_snapshot,
        balance_error=balance_error,
        candidates=candidates[:8],
        start_day=(
            common_benchmark_days[-64]
            if benchmark_3m is not None
            else None
        ),
        end_day=(
            common_benchmark_days[-1]
            if benchmark_3m is not None
            else None
        ),
        fx_rates=fx_rates,
    ))

    lines.extend([
        "",
        "Returns are historical and do not predict future performance.",
        "The benchmark applies current position weights across the historical "
        "window; it is a synthetic daily-rebalanced comparison, not the "
        "account's actual historical return.",
        "Canadian and U.S. listings are grouped only where Yahoo issuer names match.",
        "This limited screen is not exhaustive. Sector labels were not used.",
        "Positive stored cash_amount rows were used only in the separate "
        "hypothetical scenarios above; the balance reader provides no separate "
        "cash as-of timestamp.",
        "Buying power, share quantities, fractional-share eligibility, fees, "
        "taxes, and account-specific orderability were not evaluated.",
        "For a suitability-based shortlist, specify your time horizon and whether "
        "you prioritize growth, lower volatility, income, or diversification.",
        "No orders or account changes were made.",
    ])
    return "\n".join(lines)


async def portfolio_opportunity_evidence(*, message, principal):
    if (
        not isinstance(message, str)
        or not REQUEST.search(message)
        or not SYMBOL_REQUEST.search(message)
        or not BETTER_REQUEST.search(message)
        or _is_execution_request(message)
    ):
        return None

    owner = str(getattr(principal, "subject", "") or "").strip()
    if not owner:
        return PREFIX + "An authenticated owner is required for portfolio research."

    try:
        from backend.app.stacks.db_runtime import async_session
        from backend.app.stacks.snaptrade.application.external_portfolio_inventory import (
            get_external_snaptrade_portfolio,
        )
        from backend.app.stacks.snaptrade.application.external_balance_inventory import (
            get_external_snaptrade_balances,
        )

        async with async_session() as session:
            snapshot = await get_external_snaptrade_portfolio(
                session=session,
                neurovest_user_id=owner,
            )
            balance_error = None
            try:
                balance_snapshot = await get_external_snaptrade_balances(
                    session=session,
                    neurovest_user_id=owner,
                )
            except Exception as balance_exc:
                balance_snapshot = None
                balance_error = type(balance_exc).__name__

        report = await asyncio.to_thread(
            _build_report,
            snapshot.get("positions", []),
            balance_snapshot,
            balance_error,
        )
        return PREFIX + report
    except Exception as exc:
        return (
            PREFIX
            + "Owner-scoped portfolio research is unavailable "
            + f"({type(exc).__name__}). No holdings or cash were inferred."
        )
