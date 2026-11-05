"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import {
  getLivePrices,
  type LiveQuote,
} from "../../../services/marketService";

import {
  CAD_TICKER_SYMBOLS,
  CRYPTO_TICKER_SYMBOLS,
  MARKET_TICKER_SYMBOLS,
  TICKER_REFRESH_BATCH_SIZE,
  US_TICKER_SYMBOLS,
} from "../../../lib/marketUniverse";

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
  const [
    initialQuotes,
    setInitialQuotes,
  ] = useState<Record<string, LiveQuote>>({});

  const [tickerReady, setTickerReady] =
    useState(false);

  const tickerTrackRef =
    useRef<HTMLDivElement | null>(null);

  const pendingQuotesRef =
    useRef<Record<string, LiveQuote>>({});

  const applyQuotesToTicker =
    useCallback(
      (loaded: Record<string, LiveQuote>) => {
        const track = tickerTrackRef.current;

        if (!track) {
          return;
        }

        for (
          const [symbol, quote]
          of Object.entries(loaded)
        ) {
          const change = priceChange(quote);
          const positive = Boolean(
            change && change.absolute > 0,
          );
          const negative = Boolean(
            change && change.absolute < 0,
          );
          const changeClass = positive
            ? "text-emerald-300"
            : negative
              ? "text-red-300"
              : "text-slate-400";
          const arrow = positive
            ? "▲"
            : negative
              ? "▼"
              : "—";
          const sign = positive ? "+" : "";
          const changeText = change
            ? `${arrow} ${sign}${change.absolute.toFixed(
                2,
              )} (${sign}${change.percentage.toFixed(
                2,
              )}%)`
            : "—";

          for (
            const node
            of track.querySelectorAll<HTMLElement>(
              "[data-price-symbol]",
            )
          ) {
            if (node.dataset.priceSymbol === symbol) {
              node.textContent = displayPrice(quote);
            }
          }

          for (
            const node
            of track.querySelectorAll<HTMLElement>(
              "[data-change-symbol]",
            )
          ) {
            if (node.dataset.changeSymbol === symbol) {
              node.textContent = changeText;
              node.className =
                `font-black ${changeClass}`;
            }
          }
        }
      },
      [],
    );

  const tickerCursor = useRef(0);

  const loadTicker =
    useCallback(async () => {
      const symbolCount =
        MARKET_TICKER_SYMBOLS.length;

      const batchSize = Math.min(
        TICKER_REFRESH_BATCH_SIZE,
        symbolCount,
      );

      const symbols = Array.from(
        { length: batchSize },
        (_, offset) =>
          MARKET_TICKER_SYMBOLS[
            (tickerCursor.current + offset) %
              symbolCount
          ],
      );

      tickerCursor.current =
        (tickerCursor.current + batchSize) %
        symbolCount;

      try {
        const loaded =
          await getLivePrices([...symbols]);

        pendingQuotesRef.current = {
          ...pendingQuotesRef.current,
          ...loaded,
        };
      } catch {
        // Read-only market ribbon.
        // Existing values remain visible.
      }
    }, [applyQuotesToTicker]);

  const bootstrapTicker =
    useCallback(async () => {
      const loadedQuotes: Record<
        string,
        LiveQuote
      > = {};

      for (
        let start = 0;
        start < MARKET_TICKER_SYMBOLS.length;
        start += TICKER_REFRESH_BATCH_SIZE
      ) {
        const batch = MARKET_TICKER_SYMBOLS.slice(
          start,
          start + TICKER_REFRESH_BATCH_SIZE,
        );

        try {
          const loaded =
            await getLivePrices([...batch]);

          Object.assign(loadedQuotes, loaded);
        } catch {
          // Continue loading the remaining read-only batches.
        }
      }

      setInitialQuotes(loadedQuotes);

      window.requestAnimationFrame(() => {
        applyQuotesToTicker(loadedQuotes);
        setTickerReady(true);
      });
    }, [applyQuotesToTicker]);

  useEffect(() => {
    let active = true;
    let timer: number | undefined;

    queueMicrotask(() => {
      if (!active) {
        return;
      }

      void bootstrapTicker().finally(() => {
        if (!active) {
          return;
        }

        timer = window.setInterval(
          () => {
            void loadTicker();
          },
          15000,
        );
      });
    });

    return () => {
      active = false;

      if (timer !== undefined) {
        window.clearInterval(timer);
      }
    };
  }, [bootstrapTicker, loadTicker]);

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
      <div
        ref={tickerTrackRef}
        onAnimationIteration={() => {
          const pending =
            pendingQuotesRef.current;

          if (Object.keys(pending).length === 0) {
            return;
          }

          pendingQuotesRef.current = {};
          applyQuotesToTicker(pending);
        }}
        className="neurovest-ticker-track nv-market-ribbon-track flex w-max items-center gap-3 whitespace-nowrap"
        style={{
          animationPlayState: tickerReady
            ? "running"
            : "paused",
          opacity: tickerReady ? 1 : 0,
        }}
      >
        {renderItems.map(
          (item, index) => {
            const quote =
              initialQuotes[item.symbol];

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

                <span
                  data-price-symbol={item.symbol}
                  className="font-black text-slate-200"
                >
                  {displayPrice(quote)}
                </span>

                <span
                  data-change-symbol={item.symbol}
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
