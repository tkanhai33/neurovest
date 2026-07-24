"use client";

import { useCallback, useEffect, useState } from "react";

import {
  getStrategyDecision,
  type StrategyDecision,
} from "../../../services/strategyService";

export default function StrategyDecisionCard() {
  const [symbol, setSymbol] = useState("AAPL");
  const [decision, setDecision] = useState<StrategyDecision | null>(null);
  const [loading, setLoading] = useState(false);

  const loadDecision = useCallback(async (nextSymbol = symbol) => {
    const cleanSymbol = nextSymbol.trim().toUpperCase();

    if (!cleanSymbol) return;

    setLoading(true);

    try {
      const data = await getStrategyDecision(cleanSymbol);
      setDecision(data);
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  useEffect(() => {
    const firstLoad = setTimeout(() => {
      void loadDecision(symbol);
    }, 0);

    const timer = setInterval(() => {
      void loadDecision(symbol);
    }, 30000);

    return () => {
      clearTimeout(firstLoad);
      clearInterval(timer);
    };
  }, [loadDecision, symbol]);

  const visibleDecision = String(
  decision?.decision ||
  (typeof decision?.signal === "string"
    ? decision.signal
    : "hold")
);

  return (
    <section className="mt-6 rounded-2xl border border-violet-400/30 bg-slate-950/80 p-5 shadow-[0_0_30px_rgba(167,139,250,0.12)]">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-violet-300">Strategy Decision</p>
          <h2 className="mt-1 text-2xl font-bold text-white">{decision?.symbol || symbol}</h2>
        </div>

        <div className="rounded-full border border-violet-400/30 px-3 py-1 text-xs text-violet-200">
          {decision?.status || "idle"}
        </div>
      </div>

      <div className="mb-4 text-4xl font-black text-white">
        {visibleDecision.toUpperCase()}
      </div>

      <div className="mb-4 grid grid-cols-2 gap-3 text-sm">
        <div className="rounded-xl bg-slate-900/80 p-3">
          <p className="text-slate-400">Confidence</p>
          <p className="font-semibold text-violet-200">{decision?.confidence ?? 0}</p>
        </div>

        <div className="rounded-xl bg-slate-900/80 p-3">
          <p className="text-slate-400">Provider</p>
          <p className="font-semibold text-violet-200">{decision?.provider || "—"}</p>
        </div>
      </div>

      {decision?.error && (
        <p className="mb-3 rounded-xl border border-red-400/30 bg-red-950/40 p-3 text-xs text-red-200">
          {decision.error}
        </p>
      )}

      <div className="flex gap-2">
        <input
          value={symbol}
          onChange={(event) => setSymbol(event.target.value.toUpperCase())}
          className="min-w-0 flex-1 rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white outline-none focus:border-violet-400"
          placeholder="AAPL"
        />

        <button
          type="button"
          onClick={() => void loadDecision(symbol)}
          disabled={loading}
          className="rounded-xl bg-violet-400 px-4 py-2 text-sm font-bold text-slate-950 disabled:opacity-60"
        >
          {loading ? "Loading" : "Update"}
        </button>
      </div>
    </section>
  );
}
