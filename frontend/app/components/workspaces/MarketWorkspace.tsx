"use client";

import { useCallback, useEffect, useState } from "react";

import {
  getLivePrices,
  type LiveQuote,
} from "../../../services/marketService";

import type { PortfolioPosition } from "../../../services/portfolioService";

const WATCHLIST_SYMBOLS = ["AAPL", "MSFT", "NVDA", "TSLA", "RY.TO", "TD.TO"];

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

function LiveMarketWatchlist() {
  const [quotes, setQuotes] = useState<Record<string, LiveQuote>>({});
  const [loading, setLoading] = useState(false);

  const loadWatchlist = useCallback(async () => {
    setLoading(true);

    try {
      setQuotes(await getLivePrices(WATCHLIST_SYMBOLS));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const firstLoad = setTimeout(() => void loadWatchlist(), 0);
    const timer = setInterval(() => void loadWatchlist(), 30000);

    return () => {
      clearTimeout(firstLoad);
      clearInterval(timer);
    };
  }, [loadWatchlist]);

  return (
    <section className="nv-surface-section p-5">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-cyan-300">Live Watchlist</p>
          <h2 className="mt-1 text-2xl font-black text-white">Market Pulse</h2>
        </div>

        <button
          type="button"
          onClick={() => void loadWatchlist()}
          disabled={loading}
          className="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-bold text-slate-950 disabled:opacity-60"
        >
          {loading ? "Refreshing" : "Refresh"}
        </button>
      </div>

      <div className="grid gap-3 md:grid-cols-3">
        {WATCHLIST_SYMBOLS.map((symbol) => {
          const quote = quotes[symbol];

          return (
            <div key={symbol} className="nv-developer-inset-card">
              <div className="flex items-center justify-between">
                <p className="font-bold text-white">{symbol}</p>
                <span className="rounded-full border border-emerald-400/30 px-2 py-1 text-xs text-emerald-300">
                  {quote?.status || "idle"}
                </span>
              </div>

              <p className="nv-section-title">
                {quote?.price ? `$${Number(quote.price).toFixed(2)}` : "—"}
              </p>

              <p className="mt-2 text-xs text-slate-400">
                Provider: {quote?.provider || "—"}
              </p>
            </div>
          );
        })}
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
    <section className="mt-6 space-y-6">
      <section className="overflow-hidden rounded-3xl border border-cyan-400/30 bg-slate-950/80 shadow-[0_0_40px_rgba(34,211,238,0.12)]">
        <div className="border-b border-slate-800 bg-gradient-to-r from-cyan-500/10 via-blue-500/10 to-transparent p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-cyan-300">Market</p>
          <h2 className="mt-1 text-3xl font-black text-white">Market Intelligence</h2>
          <p className="mt-2 max-w-3xl text-sm text-slate-400">
            Read-only watchlist, live quote refresh, active universe, and replay-focused CAD symbols.
          </p>
        </div>

        <div className="grid gap-3 p-5 md:grid-cols-4">
          {[
            ["CAD Symbols", String(CAD_TICKER_SYMBOLS.length), "text-cyan-300"],
            ["US Symbols", String(US_TICKER_SYMBOLS.length), "text-fuchsia-300"],
            ["Crypto", String(CRYPTO_TICKER_SYMBOLS.length), "text-emerald-300"],
            ["Positions", String(positions.length), "text-white"],
          ].map(([label, value, color]) => (
            <div key={label} className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">{label}</p>
              <p className={`mt-2 text-3xl font-black ${color}`}>{value}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <LiveMarketWatchlist />

        <section className="nv-surface-section p-5">
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">Training Universe</p>
          <h3 className="mt-1 text-xl font-black text-white">Replay Symbol Groups</h3>

          <div className="mt-5 space-y-4">
            <div className="rounded-2xl border border-emerald-400/20 bg-emerald-950/20 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-emerald-300">Train More</p>
              <p className="mt-2 text-2xl font-black text-white">CNR.TO</p>
              <p className="mt-1 text-xs text-slate-400">Positive weighted replay reward.</p>
            </div>

            <div className="rounded-2xl border border-cyan-400/20 bg-cyan-950/20 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-cyan-300">Watchlist</p>
              <p className="mt-2 text-lg font-black text-white">ENB.TO · VFV.TO · VUN.TO</p>
              <p className="mt-1 text-xs text-slate-400">Included in filtered replay universe.</p>
            </div>

            <div className="rounded-2xl border border-red-400/20 bg-red-950/20 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-red-300">Excluded From Replay</p>
              <p className="mt-2 text-lg font-black text-white">SHOP.TO · ATZ.TO · BNS.TO</p>
              <p className="mt-1 text-xs text-slate-400">Excluded due to current strategy underperformance.</p>
            </div>
          </div>
        </section>
      </section>
    </section>
  );
}
