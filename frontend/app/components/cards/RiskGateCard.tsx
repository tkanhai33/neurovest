"use client";

import { useCallback, useEffect, useState } from "react";

import {
  getRiskGate,
  type RiskGate,
} from "../../../services/riskService";

export default function RiskGateCard() {
  const [symbol, setSymbol] = useState("AAPL");
  const [riskGate, setRiskGate] = useState<RiskGate | null>(null);
  const [loading, setLoading] = useState(false);

  const loadRiskGate = useCallback(async (nextSymbol = symbol) => {
    const cleanSymbol = nextSymbol.trim().toUpperCase();

    if (!cleanSymbol) return;

    setLoading(true);

    try {
      const data = await getRiskGate(cleanSymbol);
      setRiskGate(data);
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  useEffect(() => {
    const firstLoad = setTimeout(() => {
      void loadRiskGate(symbol);
    }, 0);

    const timer = setInterval(() => {
      void loadRiskGate(symbol);
    }, 30000);

    return () => {
      clearTimeout(firstLoad);
      clearInterval(timer);
    };
  }, [loadRiskGate, symbol]);

  return (
    <section className="mt-6 rounded-2xl border border-emerald-400/30 bg-slate-950/80 p-5 shadow-[0_0_30px_rgba(52,211,153,0.12)]">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-emerald-300">Risk Gate</p>
          <h2 className="mt-1 text-2xl font-bold text-white">{riskGate?.symbol || symbol}</h2>
        </div>

        <div className="rounded-full border border-emerald-400/30 px-3 py-1 text-xs text-emerald-200">
          {riskGate?.status || "idle"}
        </div>
      </div>

      <div className="mb-4 text-4xl font-black text-white">
        {riskGate?.allowed ? "ALLOWED" : "BLOCKED"}
      </div>

      <div className="mb-4 grid grid-cols-2 gap-3 text-sm">
        <div className="rounded-xl bg-slate-900/80 p-3">
          <p className="text-slate-400">Gate</p>
          <p className="font-semibold text-emerald-200">{riskGate?.gate || "risk"}</p>
        </div>

        <div className="rounded-xl bg-slate-900/80 p-3">
          <p className="text-slate-400">Provider</p>
          <p className="font-semibold text-emerald-200">{riskGate?.provider || "—"}</p>
        </div>
      </div>

      {riskGate?.error && (
        <p className="mb-3 rounded-xl border border-red-400/30 bg-red-950/40 p-3 text-xs text-red-200">
          {riskGate.error}
        </p>
      )}

      <div className="flex gap-2">
        <input
          value={symbol}
          onChange={(event) => setSymbol(event.target.value.toUpperCase())}
          className="min-w-0 flex-1 rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white outline-none focus:border-emerald-400"
          placeholder="AAPL"
        />

        <button
          type="button"
          onClick={() => void loadRiskGate(symbol)}
          disabled={loading}
          className="rounded-xl bg-emerald-400 px-4 py-2 text-sm font-bold text-slate-950 disabled:opacity-60"
        >
          {loading ? "Loading" : "Update"}
        </button>
      </div>
    </section>
  );
}
