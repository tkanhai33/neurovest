"use client";

import { useCallback, useEffect, useState } from "react";

type LearningState = {
  current_run?: {
    run_id?: string;
    rows?: number;
    reward_total?: number;
    decision_counts?: Record<string, number>;
    symbols?: Array<{
      symbol: string;
      rows: number;
      reward_total: number;
      average_reward: number;
      average_confidence: number;
      decisions: Record<string, number>;
    }>;
  };
  lifetime?: {
    runs?: number;
    rows_processed?: number;
    reward_total?: number;
    decision_counts?: Record<string, number>;
  };
};

export default function LearningWorkspacePanel() {
  const [data, setData] = useState<LearningState | null>(null);

  const loadLearning = useCallback(async () => {
    const response = await fetch("/neurovest-training/learning_state.json", {
      cache: "no-store",
    });
    setData(await response.json());
  }, []);

  useEffect(() => {
    const firstLoad = setTimeout(() => void loadLearning(), 0);
    const timer = setInterval(() => void loadLearning(), 30000);

    return () => {
      clearTimeout(firstLoad);
      clearInterval(timer);
    };
  }, [loadLearning]);

  const symbols = data?.current_run?.symbols || [];
  const decisions = data?.current_run?.decision_counts || {};
  const rewardTotal = Number(data?.lifetime?.reward_total || 0);
  const maxReward = Math.max(
    1,
    ...symbols.map((s) => Math.abs(Number(s.reward_total || 0)))
  );
  const maxConfidence = Math.max(
    1,
    ...symbols.map((s) => Number(s.average_confidence || 0))
  );
  const decisionTotal = Object.values(decisions).reduce(
    (sum, value) => sum + Number(value || 0),
    0
  );

  return (
    <section className="mt-6 space-y-6">
      <section className="overflow-hidden rounded-3xl border border-fuchsia-400/30 bg-slate-950/80 shadow-[0_0_40px_rgba(217,70,239,0.12)]">
        <div className="border-b border-slate-800 bg-gradient-to-r from-fuchsia-500/10 via-cyan-500/10 to-transparent p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-fuchsia-300">Learning</p>
          <h2 className="mt-1 text-3xl font-black text-white">Training Intelligence</h2>
          <p className="mt-2 max-w-3xl text-sm text-slate-400">
            Weighted replay metrics, symbol reward quality, confidence, and decision distribution.
          </p>
        </div>

        <div className="grid gap-3 p-5 md:grid-cols-4">
          {[
            ["Active Run", data?.current_run?.run_id || "—", "text-cyan-200"],
            ["Rows", String(data?.lifetime?.rows_processed ?? 0), "text-white"],
            ["Reward", rewardTotal.toFixed(4), rewardTotal >= 0 ? "text-emerald-300" : "text-red-300"],
            ["Runs", String(data?.lifetime?.runs ?? 0), "text-fuchsia-300"],
          ].map(([label, value, color]) => (
            <div key={label} className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">{label}</p>
              <p className={`mt-2 break-all text-2xl font-black ${color}`}>{value}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.4fr_0.8fr]">
        <div className="nv-surface-section p-5">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">Performance</p>
              <h3 className="text-xl font-black text-white">Reward by Symbol</h3>
            </div>
            <span className="rounded-full border border-emerald-400/20 px-3 py-1 text-xs text-emerald-300">
              weighted replay
            </span>
          </div>

          <div className="space-y-4">
            {symbols.map((s, index) => {
              const value = Number(s.reward_total || 0);
              const width = Math.max(4, Math.min(100, Math.abs(value) / maxReward * 100));

              return (
                <div key={s.symbol} className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
                  <div className="mb-2 flex items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <span className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-800 text-xs font-black text-cyan-200">
                        {index + 1}
                      </span>
                      <div>
                        <p className="font-black text-white">{s.symbol}</p>
                        <p className="text-xs text-slate-500">{s.rows} replay rows</p>
                      </div>
                    </div>

                    <p className={value >= 0 ? "font-black text-emerald-300" : "font-black text-red-300"}>
                      {value.toFixed(4)}
                    </p>
                  </div>

                  <div className="h-4 overflow-hidden rounded-full bg-slate-800">
                    <div
                      className={value >= 0 ? "h-full rounded-full bg-emerald-400" : "h-full rounded-full bg-red-400"}
                      style={{ width: `${width}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="space-y-6">
          <div className="nv-surface-section p-5">
            <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">Decision Mix</p>
            <h3 className="mt-1 text-xl font-black text-white">Action Distribution</h3>

            <div className="mt-5 space-y-4">
              {Object.entries(decisions).map(([decision, count]) => {
                const pct = decisionTotal ? (Number(count) / decisionTotal) * 100 : 0;

                return (
                  <div key={decision}>
                    <div className="mb-1 flex justify-between text-xs">
                      <span className="font-bold text-white">{decision}</span>
                      <span className="text-slate-400">{Number(count)} · {pct.toFixed(1)}%</span>
                    </div>
                    <div className="h-3 rounded-full bg-slate-800">
                      <div className="h-full rounded-full bg-cyan-400" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="nv-surface-section p-5">
            <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">Confidence</p>
            <h3 className="mt-1 text-xl font-black text-white">Symbol Confidence</h3>

            <div className="mt-5 space-y-3">
              {symbols.map((s) => {
                const confidence = Number(s.average_confidence || 0);
                const pct = Math.min(100, (confidence / maxConfidence) * 100);

                return (
                  <div key={s.symbol}>
                    <div className="mb-1 flex justify-between text-xs">
                      <span className="font-bold text-white">{s.symbol}</span>
                      <span className="text-cyan-200">{confidence.toFixed(4)}</span>
                    </div>
                    <div className="h-3 rounded-full bg-slate-800">
                      <div className="h-full rounded-full bg-fuchsia-400" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {symbols.map((s) => {
          const reward = Number(s.reward_total || 0);

          return (
            <div key={s.symbol} className="rounded-3xl border border-slate-800 bg-slate-950/80 p-5">
              <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Symbol</p>
              <h3 className="mt-1 text-2xl font-black text-white">{s.symbol}</h3>
              <p className={reward >= 0 ? "mt-3 text-2xl font-black text-emerald-300" : "mt-3 text-2xl font-black text-red-300"}>
                {reward.toFixed(4)}
              </p>
              <p className="mt-2 text-xs text-slate-500">Avg reward {Number(s.average_reward).toFixed(8)}</p>
              <p className="mt-1 text-xs text-slate-500">Confidence {Number(s.average_confidence).toFixed(4)}</p>
            </div>
          );
        })}
      </section>
    </section>
  );
}
