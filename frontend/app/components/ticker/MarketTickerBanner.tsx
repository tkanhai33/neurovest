"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  getLivePrices,
  type LiveQuote,
} from "../../../services/marketService";

const CAD_TICKER_SYMBOLS = [
  "CNR.TO",
  "ENB.TO",
  "VFV.TO",
  "VUN.TO",
  "RY.TO",
  "TD.TO",
  "BNS.TO",
  "BAM.TO",
  "SHOP.TO",
  "ATZ.TO",
];

const US_TICKER_SYMBOLS = [
  "AAPL",
  "MSFT",
  "NVDA",
  "TSLA",
  "AMD",
  "META",
  "GOOGL",
  "AMZN",
];

const CRYPTO_TICKER_SYMBOLS = [
  "BTC-CAD",
  "ETH-CAD",
  "SOL-CAD",
  "XRP-CAD",
];

type TickerItem = {
  group: "CAD" | "US" | "CRYPTO";
  symbol: string;
};

function finiteNumber(
  value: unknown,
): number | null {
  if (
    typeof value !== "number" ||
    !Number.isFinite(value)
  ) {
    return null;
  }

  return value;
}

function referenceOpen(
  quote: LiveQuote | undefined,
): number | null {
  if (!quote) {
    return null;
  }

  return (
    finiteNumber(quote.open_price) ??
    finiteNumber(quote.open) ??
    finiteNumber(
      quote.regularMarketOpen,
    ) ??
    finiteNumber(
      quote.previous_close,
    )
  );
}

function priceChange(
  quote: LiveQuote | undefined,
): {
  absolute: number;
  percentage: number;
} | null {
  const price =
    finiteNumber(quote?.price);

  const open =
    referenceOpen(quote);

  if (
    price === null ||
    open === null ||
    open <= 0
  ) {
    return null;
  }

  const absolute =
    price - open;

  return {
    absolute,
    percentage:
      (absolute / open) * 100,
  };
}

function displayPrice(
  quote: LiveQuote | undefined,
): string {
  const price =
    finiteNumber(quote?.price);

  if (price === null) {
    return "—";
  }

  if (price >= 10000) {
    return `$${price.toLocaleString(
      undefined,
      {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      },
    )}`;
  }

  return `$${price.toFixed(2)}`;
}

function MarketTickerBanner() {
  const [quotes, setQuotes] =
    useState<
      Record<string, LiveQuote>
    >({});

  const loadTicker =
    useCallback(async () => {
      try {
        const loaded =
          await getLivePrices([
            ...CAD_TICKER_SYMBOLS,
            ...US_TICKER_SYMBOLS,
            ...CRYPTO_TICKER_SYMBOLS,
          ]);

        setQuotes(loaded);
      } catch {
        // Read-only market ribbon.
        // Existing values remain visible.
      }
    }, []);

  useEffect(() => {
    const firstLoad =
      window.setTimeout(
        () => {
          void loadTicker();
        },
        0,
      );

    const timer =
      window.setInterval(
        () => {
          void loadTicker();
        },
        30000,
      );

    return () => {
      window.clearTimeout(
        firstLoad,
      );

      window.clearInterval(timer);
    };
  }, [loadTicker]);

  const tickerItems =
    useMemo<TickerItem[]>(
      () => [
        ...CAD_TICKER_SYMBOLS.map(
          (symbol) => ({
            group: "CAD" as const,
            symbol,
          }),
        ),
        ...US_TICKER_SYMBOLS.map(
          (symbol) => ({
            group: "US" as const,
            symbol,
          }),
        ),
        ...CRYPTO_TICKER_SYMBOLS.map(
          (symbol) => ({
            group:
              "CRYPTO" as const,
            symbol,
          }),
        ),
      ],
      [],
    );

  const renderItems = [
    ...tickerItems,
    ...tickerItems,
  ];

  return (
    <section
      aria-label="Live market prices"
      className="nv-market-ribbon overflow-hidden rounded-3xl border border-cyan-300/20 bg-slate-950/80 px-3 py-3 shadow-[0_0_40px_rgba(34,211,238,0.10)]"
    >
      <div className="neurovest-ticker-track nv-market-ribbon-track flex w-max items-center gap-3 whitespace-nowrap">
        {renderItems.map(
          (item, index) => {
            const quote =
              quotes[item.symbol];

            const change =
              priceChange(quote);

            const positive =
              change !== null &&
              change.absolute > 0;

            const negative =
              change !== null &&
              change.absolute < 0;

            const changeClass =
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
              positive ? "+" : "";

            return (
              <span
                key={`${item.group}-${item.symbol}-${index}`}
                className="inline-flex shrink-0 items-center gap-2 rounded-full border border-cyan-300/15 bg-slate-900/90 px-3 py-1.5 text-xs shadow-[0_0_18px_rgba(15,23,42,0.35)]"
              >
                <span className="font-black uppercase tracking-[0.2em] text-cyan-300">
                  {item.group}
                </span>

                <span className="font-black text-white">
                  {item.symbol}
                </span>

                <span className="font-black text-slate-200">
                  {displayPrice(
                    quote,
                  )}
                </span>

                <span
                  className={`font-black ${changeClass}`}
                >
                  {change
                    ? `${arrow} ${sign}${change.absolute.toFixed(
                        2,
                      )} (${sign}${change.percentage.toFixed(
                        2,
                      )}%)`
                    : "—"}
                </span>
              </span>
            );
          },
        )}
      </div>
    </section>
  );
}

export default MarketTickerBanner;
