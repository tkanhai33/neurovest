"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import {
  getLivePrices,
  type LiveQuote,
} from "../../../services/marketService";

import type {
  PortfolioPosition,
} from "../../../services/portfolioService";


const WATCHLIST_SYMBOLS = [
  "AAPL",
  "MSFT",
  "NVDA",
  "TSLA",
  "RY.TO",
  "TD.TO",
];


import {
  CAD_TICKER_SYMBOLS,
  CRYPTO_TICKER_SYMBOLS,
  US_TICKER_SYMBOLS,
} from "../../../lib/marketUniverse";


type QuoteMovement = {
  absolute: number;
  percentage: number;
  referenceLabel: string;
};


function finiteNumber(
  value: unknown,
): number | null {

  if (
    typeof value !== "number"
    ||
    !Number.isFinite(value)
  ) {
    return null;
  }

  return value;
}


function quoteCurrency(
  quote: LiveQuote | undefined,
): string | null {

  const currency =
    String(
      quote?.currency
      ??
      "",
    )
    .trim()
    .toUpperCase();

  return currency || null;
}


function referenceValue(
  quote: LiveQuote | undefined,
): {
  value: number;
  label: string;
} | null {

  if (!quote) {
    return null;
  }

  const openPrice =
    finiteNumber(
      quote.open_price,
    );

  if (openPrice !== null) {
    return {
      value: openPrice,
      label: "vs open",
    };
  }

  const open =
    finiteNumber(
      quote.open,
    );

  if (open !== null) {
    return {
      value: open,
      label: "vs open",
    };
  }

  const regularOpen =
    finiteNumber(
      quote.regularMarketOpen,
    );

  if (regularOpen !== null) {
    return {
      value: regularOpen,
      label: "vs open",
    };
  }

  const previousClose =
    finiteNumber(
      quote.previous_close,
    );

  if (previousClose !== null) {
    return {
      value: previousClose,
      label: "vs previous close",
    };
  }

  return null;
}


function quoteMovement(
  quote: LiveQuote | undefined,
): QuoteMovement | null {

  const price =
    finiteNumber(
      quote?.price,
    );

  const reference =
    referenceValue(
      quote,
    );

  if (
    price === null
    ||
    reference === null
    ||
    reference.value <= 0
  ) {
    return null;
  }

  const absolute =
    price
    -
    reference.value;

  return {
    absolute,

    percentage:
      (
        absolute
        /
        reference.value
      )
      *
      100,

    referenceLabel:
      reference.label,
  };
}


function displayPrice(
  quote: LiveQuote | undefined,
): string {

  const price =
    finiteNumber(
      quote?.price,
    );

  if (price === null) {
    return "—";
  }

  const currency =
    quoteCurrency(
      quote,
    );

  if (currency) {
    try {
      return new Intl.NumberFormat(
        "en-CA",
        {
          style: "currency",
          currency,
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        },
      ).format(price);
    } catch {
      // Fall through to an honest symbol-only value.
    }
  }

  return `$${price.toLocaleString(
    "en-CA",
    {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    },
  )}`;
}


function statusClasses(
  status: string | undefined,
): string {

  const normalized =
    String(
      status
      ??
      "idle",
    ).toLowerCase();

  if (
    normalized === "ok"
    ||
    normalized === "success"
  ) {
    return (
      "border-emerald-400/30 "
      +
      "bg-emerald-400/[0.04] "
      +
      "text-emerald-300"
    );
  }

  if (
    normalized === "error"
    ||
    normalized === "failed"
  ) {
    return (
      "border-red-400/30 "
      +
      "bg-red-400/[0.04] "
      +
      "text-red-300"
    );
  }

  return (
    "border-slate-600/40 "
    +
    "bg-slate-700/10 "
    +
    "text-slate-400"
  );
}


function LiveMarketWatchlist() {

  const [
    quotes,
    setQuotes,
  ] = useState<
    Record<string, LiveQuote>
  >({});

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [search, setSearch] = useState("");
  const [refreshError, setRefreshError] =
    useState<string | null>(null);
  const [lastRetrievedAt, setLastRetrievedAt] =
    useState<Date | null>(null);

  const requestInFlight = useRef(false);

  const visibleSymbols = WATCHLIST_SYMBOLS.filter(
    symbol =>
      symbol.toLowerCase().includes(
        search.trim().toLowerCase(),
      ),
  );


  const loadWatchlist =
    useCallback(
      async () => {
        if (requestInFlight.current) {
          return;
        }

        requestInFlight.current = true;
        setLoading(true);

        try {
          const loaded = await getLivePrices(
            WATCHLIST_SYMBOLS,
          );

          if (
            !loaded ||
            Object.keys(loaded).length === 0
          ) {
            throw new Error(
              "No quote records were returned.",
            );
          }

          setQuotes(loaded);
          setLastRetrievedAt(new Date());
          setRefreshError(null);
        } catch {
          // Preserve previously retrieved quotes.
          // Never silently present them as freshly retrieved.
          setRefreshError(
            "Quote refresh failed. Previously retrieved " +
            "values are retained where available; " +
            "they may be outdated.",
          );
        } finally {
          requestInFlight.current = false;
          setLoading(false);
        }
      },
      [],
    );


  useEffect(
    () => {

      const firstLoad =
        window.setTimeout(
          () => {
            void loadWatchlist();
          },
          0,
        );

      const timer =
        window.setInterval(
          () => {
            void loadWatchlist();
          },
          30_000,
        );

      return () => {
        window.clearTimeout(
          firstLoad,
        );

        window.clearInterval(
          timer,
        );
      };
    },
    [
      loadWatchlist,
    ],
  );


  return (
    <section
      className="
        nv-surface-section
        min-w-0 p-5
      "
    >
      <div
        className="
          mb-4 flex
          items-center justify-between
          gap-4
        "
      >
        <div>
          <p
            className="
              text-xs uppercase
              tracking-[0.3em]
              text-cyan-300
            "
          >
            Live Watchlist
          </p>

          <h2
            className="
              mt-1 text-2xl
              font-black text-white
            "
          >
            Market Pulse
          </h2>

          <p
            className="
              mt-1 text-xs
              text-slate-500
            "
          >
            Read-only quotes · automatic 30-second refresh
          </p>
        </div>

        <button
          type="button"
          onClick={() => {
            void loadWatchlist();
          }}
          disabled={loading}
          className="
            rounded-xl
            bg-cyan-400
            px-4 py-2
            text-sm font-bold
            text-slate-950
            disabled:opacity-60
          "
        >
          {loading
            ? "Refreshing"
            : "Refresh"}
        </button>
      </div>

      <div
        data-testid="f9-market-refresh-status"
        aria-live="polite"
        className="mb-4 rounded-xl border border-white/[0.08] bg-white/[0.025] px-4 py-3"
      >
        <p className="text-xs leading-5 text-slate-300">
          {loading
            ? "Retrieving watchlist quotes..."
            : lastRetrievedAt
              ? `Last successful retrieval: ${lastRetrievedAt.toLocaleTimeString("en-CA")}`
              : "No quotes successfully retrieved yet."}
        </p>
        <p className="mt-1 text-xs leading-5 text-slate-500">
          Retrieval time is not exchange quote time.
          Prices may be delayed or stale depending on the provider.
        </p>
        {refreshError && (
          <p
            role="alert"
            data-testid="f9-market-refresh-error"
            className="mt-2 text-xs leading-5 text-amber-200"
          >
            {refreshError}
          </p>
        )}
      </div>

      <label className="mb-4 block min-w-0">
        <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.15em] text-cyan-200">
          Find a watchlist symbol
        </span>
        <input
          type="search"
          data-testid="f9-market-symbol-search"
          value={search}
          onChange={event => setSearch(event.target.value)}
          placeholder="Filter AAPL, MSFT, NVDA..."
          className="nv-input w-full"
        />
      </label>

      <p
        data-testid="f9-market-visible-count"
        aria-live="polite"
        className="mb-3 text-xs text-slate-400"
      >
        Showing {visibleSymbols.length} of{" "}
        {WATCHLIST_SYMBOLS.length} watchlist symbols
      </p>

      {visibleSymbols.length === 0 && (
        <p
          className="mb-4 rounded-xl border border-white/[0.08] p-4 text-sm text-slate-400"
          data-testid="f9-market-no-match"
        >
          No symbols in this watchlist match your search.
        </p>
      )}

      <div
        className="
          grid gap-3
          md:grid-cols-2
          xl:grid-cols-3
        "
      >
        {visibleSymbols.map(
          symbol => {

            const quote =
              quotes[symbol];

            const movement =
              quoteMovement(
                quote,
              );

            const currency =
              quoteCurrency(
                quote,
              );

            const positive =
              movement !== null
              &&
              movement.absolute > 0;

            const negative =
              movement !== null
              &&
              movement.absolute < 0;

            const movementClass =
              positive
                ? "text-emerald-300"
                : negative
                  ? "text-red-300"
                  : "text-slate-400";

            const arrow =
              positive
                ? "▲"
                : negative
                  ? "▼"
                  : "—";

            const sign =
              positive
                ? "+"
                : "";

            const status =
              refreshError && quote
                ? "Previously retrieved"
                : String(
                    quote?.status
                    ??
                    "unavailable",
                  );

            return (
              <article
                key={symbol}
                className="
                  nv-developer-inset-card
                  min-w-0
                "
              >
                <div
                  className="
                    flex items-center
                    justify-between gap-3
                  "
                >
                  <p
                    className="
                      font-bold text-white
                    "
                  >
                    {symbol}
                  </p>

                  <span
                    className={`
                      rounded-full border
                      px-2 py-1
                      text-[10px]
                      font-semibold uppercase
                      tracking-[0.12em]
                      ${statusClasses(
                        status,
                      )}
                    `}
                  >
                    {status}
                  </span>
                </div>

                <p
                  className="
                    nv-section-title
                    mt-3
                  "
                >
                  {displayPrice(
                    quote,
                  )}
                </p>

                <div
                  className="
                    mt-2 flex
                    flex-wrap items-center
                    gap-x-2 gap-y-1
                    text-xs
                  "
                >
                  <span
                    className="
                      rounded-md
                      border border-white/[0.07]
                      bg-white/[0.025]
                      px-2 py-0.5
                      font-semibold
                      text-slate-300
                    "
                  >
                    {currency
                      ??
                      "Currency unavailable"}
                  </span>

                  {movement ? (
                    <span
                      className={
                        movementClass
                      }
                    >
                      {arrow}
                      {" "}
                      {sign}
                      {movement.absolute.toFixed(
                        2,
                      )}
                      {" · "}
                      {sign}
                      {movement.percentage.toFixed(
                        2,
                      )}
                      %
                    </span>
                  ) : (
                    <span
                      className="
                        text-slate-500
                      "
                    >
                      Movement unavailable
                    </span>
                  )}
                </div>

                <p
                  className="
                    mt-1 text-[10px]
                    uppercase
                    tracking-[0.12em]
                    text-slate-600
                  "
                >
                  {movement
                    ? movement.referenceLabel
                    : "No reference value returned"}
                </p>

                <div
                  className="
                    mt-3 flex
                    items-center justify-between
                    gap-3 border-t
                    border-white/[0.05]
                    pt-3 text-[10px]
                    text-slate-500
                  "
                >
                  <span>
                    Provider:{" "}
                    {quote?.provider
                      ||
                      "—"}
                  </span>

                  <span>
                    Refresh: 30s
                  </span>
                </div>

                {quote?.error && (
                  <p
                    className="
                      mt-3 rounded-lg
                      border border-red-400/20
                      bg-red-950/20
                      px-2 py-1.5
                      text-[10px]
                      text-red-200
                    "
                  >
                    {quote.error}
                  </p>
                )}
              </article>
            );
          },
        )}
      </div>
    </section>
  );
}



function MarketSymbolLookup() {
  const [symbolInput, setSymbolInput] = useState("");
  const [resultSymbol, setResultSymbol] = useState("");
  const [resultQuote, setResultQuote] =
    useState<LiveQuote | null>(null);
  const [resultError, setResultError] =
    useState<string | null>(null);
  const [retrievedAt, setRetrievedAt] =
    useState<Date | null>(null);
  const [lookingUp, setLookingUp] = useState(false);

  const inFlight = useRef(false);

  async function lookupSymbol() {
    if (inFlight.current) {
      return;
    }

    const requested = symbolInput.trim().toUpperCase();

    if (!/^[A-Z0-9][A-Z0-9.\\^-]{0,19}$/.test(requested)) {
      setResultSymbol("");
      setResultQuote(null);
      setRetrievedAt(null);
      setResultError(
        "Enter a valid market symbol, such as ENB.TO, AAPL, or RY.TO.",
      );
      return;
    }

    inFlight.current = true;
    setLookingUp(true);
    setResultError(null);
    setResultQuote(null);
    setRetrievedAt(null);
    setResultSymbol(requested);

    try {
      const response = await getLivePrices([requested]);

      const quote =
        response?.[requested] ??
        Object.entries(response ?? {}).find(
          ([key]) => key.toUpperCase() === requested,
        )?.[1];

      if (!quote) {
        throw new Error(
          "No quote was returned for this symbol. Check the ticker " +
          "or whether the market-data provider supports it.",
        );
      }

      if (finiteNumber(quote.price) === null) {
        throw new Error(
          typeof quote.error === "string" && quote.error.trim()
            ? quote.error
            : "The provider did not return a usable price for this symbol.",
        );
      }

      setResultQuote(quote);
      setRetrievedAt(new Date());
    } catch (caught) {
      setResultError(
        caught instanceof Error
          ? caught.message
          : "Market symbol lookup failed.",
      );
    } finally {
      inFlight.current = false;
      setLookingUp(false);
    }
  }

  const movement = quoteMovement(resultQuote ?? undefined);
  const positive = movement !== null && movement.absolute > 0;
  const negative = movement !== null && movement.absolute < 0;

  return (
    <section
      className="nv-surface-section min-w-0 p-5"
      data-testid="f9-r2-market-lookup"
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-cyan-300">
            Market research
          </p>
          <h3 className="mt-2 text-xl font-black text-white">
            Look up a market symbol
          </h3>
          <p className="mt-2 text-sm leading-6 text-slate-400">
            Research symbols beyond the six-stock watchlist.
            Quotes are read-only and provider availability varies.
          </p>
        </div>
        <span className="rounded-full border border-cyan-300/20 px-3 py-1 text-xs font-semibold text-cyan-200">
          Read only
        </span>
      </div>

      <form
        className="mt-5 flex flex-col gap-3 sm:flex-row"
        onSubmit={event => {
          event.preventDefault();
          void lookupSymbol();
        }}
      >
        <label className="min-w-0 flex-1">
          <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.15em] text-slate-400">
            Ticker symbol
          </span>
          <input
            type="text"
            name="market-symbol"
            data-testid="f9-r2-symbol-input"
            value={symbolInput}
            onChange={event => setSymbolInput(event.target.value)}
            autoComplete="off"
            maxLength={20}
            placeholder="ENB.TO"
            className="nv-input w-full"
            aria-describedby="f9-r2-symbol-help"
          />
        </label>
        <button
          type="submit"
          data-testid="f9-r2-symbol-submit"
          disabled={lookingUp}
          className="min-h-11 self-end rounded-xl bg-cyan-400 px-6 py-3 text-sm font-bold text-slate-950 disabled:opacity-60"
        >
          {lookingUp ? "Looking up..." : "Get quote"}
        </button>
      </form>

      <p
        id="f9-r2-symbol-help"
        className="mt-2 text-xs leading-5 text-slate-500"
      >
        Examples: ENB.TO, RY.TO, MSFT. Lookup runs when you submit;
        it does not add symbols to the automatic watchlist.
      </p>

      <div aria-live="polite" className="mt-4">
        {resultError && (
          <p
            role="alert"
            data-testid="f9-r2-symbol-error"
            className="rounded-xl border border-amber-300/20 bg-amber-300/[0.04] p-4 text-sm text-amber-200"
          >
            {resultError}
          </p>
        )}

        {resultQuote && (
          <article
            data-testid="f9-r2-symbol-result"
            className="rounded-2xl border border-cyan-300/20 bg-cyan-300/[0.03] p-5"
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h4 className="text-xl font-black text-white">
                {resultSymbol}
              </h4>
              <span className="text-xs font-semibold uppercase tracking-[0.12em] text-cyan-200">
                Retrieved quote
              </span>
            </div>

            <p className="mt-3 text-3xl font-black text-white">
              {displayPrice(resultQuote)}
            </p>

            <p className="mt-2 text-sm text-slate-300">
              Currency: {quoteCurrency(resultQuote) ?? "Not provided"}
            </p>

            {movement ? (
              <p className={
                "mt-2 text-sm font-semibold " +
                (positive
                  ? "text-emerald-300"
                  : negative
                    ? "text-red-300"
                    : "text-slate-300")
              }>
                {positive ? "+" : ""}
                {movement.absolute.toFixed(2)}
                {" · "}
                {positive ? "+" : ""}
                {movement.percentage.toFixed(2)}
                % {movement.referenceLabel}
              </p>
            ) : (
              <p className="mt-2 text-xs text-slate-400">
                Reference movement unavailable
              </p>
            )}

            <div className="mt-4 flex flex-wrap justify-between gap-2 border-t border-white/[0.07] pt-3 text-xs text-slate-400">
              <span>
                Provider: {resultQuote.provider || "Not provided"}
              </span>
              <span>
                Retrieved: {retrievedAt?.toLocaleTimeString("en-CA") ?? "—"}
              </span>
            </div>
            <p className="mt-2 text-xs leading-5 text-slate-500">
              Retrieval time is not exchange time. Prices may be
              delayed or stale. No brokerage order is placed.
            </p>
          </article>
        )}
      </div>
    </section>
  );
}


export default function MarketWorkspace({
  positions,
}: {
  positions: PortfolioPosition[];
}) {

  return (
    <section
      className="
        mt-6 min-w-0
        space-y-6
      "
    >
      <section
        className="
          overflow-hidden
          rounded-3xl
          border border-cyan-400/30
          bg-slate-950/80
          shadow-[0_0_40px_rgba(34,211,238,0.12)]
        "
      >
        <div
          className="
            border-b border-slate-800
            bg-gradient-to-r
            from-cyan-500/10
            via-blue-500/10
            to-transparent
            p-5
          "
        >
          <p
            className="
              text-xs uppercase
              tracking-[0.3em]
              text-cyan-300
            "
          >
            Market
          </p>

          <h2
            className="
              mt-1 text-3xl
              font-black text-white
            "
          >
            Market Intelligence
          </h2>

          <p
            className="
              mt-2 max-w-3xl
              text-sm text-slate-400
            "
          >
            Read-only watchlist, quote refresh, active universe,
            and replay-focused CAD symbols.
          </p>
        </div>

        <div
          className="
            grid gap-3 p-5
            md:grid-cols-4
          "
        >
          {[
            [
              "CAD Symbols",
              String(
                CAD_TICKER_SYMBOLS.length,
              ),
              "text-cyan-300",
            ],
            [
              "US Symbols",
              String(
                US_TICKER_SYMBOLS.length,
              ),
              "text-fuchsia-300",
            ],
            [
              "Crypto",
              String(
                CRYPTO_TICKER_SYMBOLS.length,
              ),
              "text-emerald-300",
            ],
            [
              "Positions",
              String(
                positions.length,
              ),
              "text-white",
            ],
          ].map(
            (
              [
                label,
                value,
                color,
              ],
            ) => (
              <div
                key={label}
                className="
                  rounded-2xl
                  border border-slate-800
                  bg-slate-900/70
                  p-4
                "
              >
                <p
                  className="
                    text-xs uppercase
                    tracking-[0.2em]
                    text-slate-500
                  "
                >
                  {label}
                </p>

                <p
                  className={`
                    mt-2 text-3xl
                    font-black
                    ${color}
                  `}
                >
                  {value}
                </p>
              </div>
            ),
          )}
        </div>
      </section>

      <MarketSymbolLookup />

      <section
        className="
          grid min-w-0 gap-6
          xl:grid-cols-[1.2fr_0.8fr]
          xl:items-start
        "
      >
        <LiveMarketWatchlist />

        <section
          className="
            nv-surface-section
            min-w-0 p-5
          "
        >
          <p
            className="
              text-xs uppercase
              tracking-[0.25em]
              text-cyan-300
            "
          >
            Training Universe
          </p>

          <h3
            className="
              mt-1 text-xl
              font-black text-white
            "
          >
            Replay Symbol Examples
          </h3>

          <p
            data-testid="f9-static-replay-disclosure"
            className="mt-3 text-xs leading-5 text-amber-200/90"
          >
            Static illustrative symbol groups.
            Not a live training result, current strategy decision,
            or investment recommendation.
          </p>

          <div
            className="
              mt-5 space-y-4
            "
          >
            <div
              className="
                rounded-2xl
                border border-emerald-400/20
                bg-emerald-950/20
                p-4
              "
            >
              <p
                className="
                  text-xs uppercase
                  tracking-[0.2em]
                  text-emerald-300
                "
              >
                Train More
              </p>

              <p
                className="
                  mt-2 text-2xl
                  font-black text-white
                "
              >
                CNR.TO
              </p>

              <p
                className="
                  mt-1 text-xs
                  text-slate-400
                "
              >
                Illustrative replay category; not a verified current reward.
              </p>
            </div>

            <div
              className="
                rounded-2xl
                border border-cyan-400/20
                bg-cyan-950/20
                p-4
              "
            >
              <p
                className="
                  text-xs uppercase
                  tracking-[0.2em]
                  text-cyan-300
                "
              >
                Watchlist
              </p>

              <p
                className="
                  mt-2 text-lg
                  font-black text-white
                "
              >
                ENB.TO · VFV.TO · VUN.TO
              </p>

              <p
                className="
                  mt-1 text-xs
                  text-slate-400
                "
              >
                Illustrative symbol group; current inclusion is not verified here.
              </p>
            </div>

            <div
              className="
                rounded-2xl
                border border-red-400/20
                bg-red-950/20
                p-4
              "
            >
              <p
                className="
                  text-xs uppercase
                  tracking-[0.2em]
                  text-red-300
                "
              >
                Excluded From Replay
              </p>

              <p
                className="
                  mt-2 text-lg
                  font-black text-white
                "
              >
                SHOP.TO · ATZ.TO · BNS.TO
              </p>

              <p
                className="
                  mt-1 text-xs
                  text-slate-400
                "
              >
                Illustrative excluded group; no current underperformance is verified here.
              </p>
            </div>
          </div>
        </section>
      </section>
    </section>
  );
}
