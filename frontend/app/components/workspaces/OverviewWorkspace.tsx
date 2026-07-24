"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import type { PortfolioPosition } from "../../../services/portfolioService";

import {
  getBackendHealth,
  type BackendHealth,
} from "../../../services/backendHealthService";

type LearningSymbol = {
  symbol: string;
  rows: number;
  reward_total: number;
  average_reward: number;
  average_confidence: number;
  decisions: Record<string, number>;
};

type LearningState = {
  created_at?: string;
  current_run?: {
    run_id?: string;
    rows?: number;
    reward_total?: number;
    decision_counts?: Record<string, number>;
    symbols?: LearningSymbol[];
  };
  lifetime?: {
    runs?: number;
    rows_processed?: number;
    reward_total?: number;
    decision_counts?: Record<string, number>;
  };
  certified?: boolean;
};

function StatusCard({
  label,
  value,
  detail,
  valueClass = "text-white",
}: {
  label: string;
  value: string;
  detail: string;
  valueClass?: string;
}) {
  return (
    <div className="rounded-3xl border border-cyan-400/10 bg-slate-950/80 p-5">
      <div className="flex items-center justify-between gap-3">
        <p className="text-xs uppercase tracking-[0.25em] text-slate-500">
          {label}
        </p>

        <span className="h-2 w-2 rounded-full bg-cyan-300 shadow-[0_0_12px_rgba(34,211,238,0.8)]" />
      </div>

      <p className={`mt-3 break-all text-3xl font-black ${valueClass}`}>
        {value}
      </p>

      <p className="mt-2 text-xs text-slate-500">{detail}</p>
    </div>
  );
}

export default function OverviewWorkspace({
  positions,
}: {
  positions: PortfolioPosition[];
}) {
  const [learning, setLearning] = useState<LearningState | null>(null);
  const [backend, setBackend] = useState<BackendHealth | null>(null);
  const [loading, setLoading] = useState(false);
  const [lastError, setLastError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);

    try {
      const [learningResponse, backendResult] = await Promise.all([
        fetch("/neurovest-training/learning_state.json", {
          cache: "no-store",
        }),
        getBackendHealth(),
      ]);

      if (!learningResponse.ok) {
        throw new Error(
          `Learning state request failed: ${learningResponse.status}`
        );
      }

      const learningResult =
        (await learningResponse.json()) as LearningState;

      setLearning(learningResult);
      setBackend(backendResult);
      setLastError(null);
    } catch (error) {
      setLastError(String(error));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const firstLoad = setTimeout(() => void refresh(), 0);
    const timer = setInterval(() => void refresh(), 30000);

    return () => {
      clearTimeout(firstLoad);
      clearInterval(timer);
    };
  }, [refresh]);

  const symbols = useMemo(
    () => learning?.current_run?.symbols || [],
    [learning]
  );

  const rankedSymbols = useMemo(
    () =>
      [...symbols].sort(
        (left, right) =>
          Number(right.reward_total || 0) -
          Number(left.reward_total || 0)
      ),
    [symbols]
  );

  const topSymbol = rankedSymbols[0];
  const weakestSymbol = rankedSymbols[rankedSymbols.length - 1];

  const decisionCounts =
    learning?.current_run?.decision_counts || {};

  const decisionTotal = Object.values(decisionCounts).reduce(
    (total, count) => total + Number(count || 0),
    0
  );

  const backendLabel =
    backend === null
      ? "unknown"
      : backend.apiOnline
        ? "online"
        : "offline";

  const rewardTotal = Number(
    learning?.lifetime?.reward_total || 0
  );

  return (
    <section className="mt-6 space-y-6">
      <section className="overflow-hidden rounded-3xl border border-cyan-400/30 bg-slate-950/80 shadow-[0_0_45px_rgba(34,211,238,0.12)]">
        <div className="border-b border-slate-800 bg-gradient-to-r from-cyan-500/10 via-fuchsia-500/10 to-transparent p-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-cyan-300">
                Executive Overview
              </p>

              <h2 className="mt-2 text-3xl font-black text-white">
                NeuroVest Command Summary
              </h2>

              <p className="mt-2 max-w-3xl text-sm text-slate-400">
                Current system health, replay learning, portfolio visibility,
                symbol performance, and safety state in one read-only view.
              </p>
            </div>

            <button
              type="button"
              onClick={() => void refresh()}
              disabled={loading}
              className="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-black text-slate-950 disabled:opacity-60"
            >
              {loading ? "Refreshing" : "Refresh"}
            </button>
          </div>
        </div>

        <div className="grid gap-4 p-6 md:grid-cols-2 xl:grid-cols-4">
          <StatusCard
            label="Backend"
            value={backendLabel}
            detail={`Graph latency: ${backend?.latencyMs ?? 0}ms`}
            valueClass={
              backend?.apiOnline
                ? "text-emerald-300"
                : backend === null
                  ? "text-slate-300"
                  : "text-red-300"
            }
          />

          <StatusCard
            label="Portfolio Positions"
            value={String(positions.length)}
            detail="Read-only portfolio service result"
            valueClass="text-cyan-300"
          />

          <StatusCard
            label="Lifetime Reward"
            value={rewardTotal.toFixed(4)}
            detail={`${learning?.lifetime?.runs ?? 0} weighted replay run(s)`}
            valueClass={
              rewardTotal >= 0
                ? "text-emerald-300"
                : "text-red-300"
            }
          />

          <StatusCard
            label="Rows Processed"
            value={String(
              learning?.lifetime?.rows_processed ?? 0
            )}
            detail="Historical replay observations"
            valueClass="text-fuchsia-300"
          />
        </div>
      </section>

      {lastError && (
        <section className="rounded-3xl border border-red-400/30 bg-red-950/20 p-5 text-sm text-red-200">
          {lastError}
        </section>
      )}

      <section className="grid gap-6 xl:grid-cols-[1.25fr_0.75fr]">
        <section className="rounded-3xl border border-cyan-400/20 bg-slate-950/80 p-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">
                Replay Intelligence
              </p>

              <h3 className="mt-1 text-xl font-black text-white">
                Current Symbol Performance
              </h3>
            </div>

            <span className="rounded-full border border-fuchsia-400/20 px-3 py-1 text-xs text-fuchsia-200">
              {learning?.current_run?.run_id || "no active run"}
            </span>
          </div>

          <div className="mt-5 grid gap-3">
            {rankedSymbols.length === 0 ? (
              <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 text-sm text-slate-400">
                No learning symbols available.
              </div>
            ) : (
              rankedSymbols.map((symbol, index) => {
                const reward = Number(
                  symbol.reward_total || 0
                );

                return (
                  <div
                    key={symbol.symbol}
                    className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <span className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-800 text-xs font-black text-cyan-200">
                          {index + 1}
                        </span>

                        <div>
                          <p className="font-black text-white">
                            {symbol.symbol}
                          </p>

                          <p className="text-xs text-slate-500">
                            {symbol.rows} rows · confidence{" "}
                            {Number(
                              symbol.average_confidence || 0
                            ).toFixed(4)}
                          </p>
                        </div>
                      </div>

                      <p
                        className={
                          reward >= 0
                            ? "text-lg font-black text-emerald-300"
                            : "text-lg font-black text-red-300"
                        }
                      >
                        {reward.toFixed(4)}
                      </p>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </section>

        <section className="space-y-6">
          <section className="rounded-3xl border border-cyan-400/20 bg-slate-950/80 p-5">
            <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">
              Decision Mix
            </p>

            <h3 className="mt-1 text-xl font-black text-white">
              Current Replay Actions
            </h3>

            <div className="mt-5 space-y-4">
              {Object.entries(decisionCounts).length === 0 ? (
                <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 text-sm text-slate-400">
                  No decision metrics available.
                </div>
              ) : (
                Object.entries(decisionCounts).map(
                  ([decision, count]) => {
                    const percentage = decisionTotal
                      ? (Number(count) / decisionTotal) * 100
                      : 0;

                    return (
                      <div key={decision}>
                        <div className="mb-2 flex items-center justify-between text-xs">
                          <span className="font-black text-white">
                            {decision}
                          </span>

                          <span className="text-slate-400">
                            {count} · {percentage.toFixed(1)}%
                          </span>
                        </div>

                        <div className="h-3 overflow-hidden rounded-full bg-slate-800">
                          <div
                            className="h-full rounded-full bg-cyan-400"
                            style={{
                              width: `${percentage}%`,
                            }}
                          />
                        </div>
                      </div>
                    );
                  }
                )
              )}
            </div>
          </section>

          <section className="rounded-3xl border border-cyan-400/20 bg-slate-950/80 p-5">
            <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">
              Symbol Summary
            </p>

            <div className="mt-4 grid gap-3">
              <div className="rounded-2xl border border-emerald-400/20 bg-emerald-950/20 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-emerald-300">
                  Strongest
                </p>

                <p className="mt-2 text-2xl font-black text-white">
                  {topSymbol?.symbol || "—"}
                </p>

                <p className="mt-1 text-xs text-slate-400">
                  Reward{" "}
                  {Number(
                    topSymbol?.reward_total || 0
                  ).toFixed(4)}
                </p>
              </div>

              <div className="rounded-2xl border border-red-400/20 bg-red-950/20 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-red-300">
                  Weakest
                </p>

                <p className="mt-2 text-2xl font-black text-white">
                  {weakestSymbol?.symbol || "—"}
                </p>

                <p className="mt-1 text-xs text-slate-400">
                  Reward{" "}
                  {Number(
                    weakestSymbol?.reward_total || 0
                  ).toFixed(4)}
                </p>
              </div>
            </div>
          </section>
        </section>
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <section className="rounded-3xl border border-cyan-400/20 bg-slate-950/80 p-5">
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">
            Safety Contract
          </p>

          <h3 className="mt-1 text-xl font-black text-white">
            Runtime Locks
          </h3>

          <div className="mt-5 grid gap-3">
            {[
              ["Replay mode", "ACTIVE"],
              ["Broker execution", "DISABLED"],
              ["Live execution", "DISABLED"],
              ["Portfolio mutation", "DISABLED"],
            ].map(([label, value]) => (
              <div
                key={label}
                className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-900/60 p-4"
              >
                <span className="text-sm text-slate-300">
                  {label}
                </span>

                <span className="rounded-full border border-emerald-400/20 px-3 py-1 text-xs font-black text-emerald-300">
                  {value}
                </span>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-3xl border border-fuchsia-400/20 bg-slate-950/80 p-5">
          <p className="text-xs uppercase tracking-[0.25em] text-fuchsia-300">
            Neuro Status
          </p>

          <h3 className="mt-1 text-xl font-black text-white">
            AI Runtime Summary
          </h3>

          <div className="mt-5 grid gap-3">
            {[
              ["Provider", "Ollama"],
              ["Conversation", "Floating button"],
              ["Learning feed", learning?.certified ? "CERTIFIED" : "UNKNOWN"],
              ["Graph", backend?.graphOnline ? "ONLINE" : "OFFLINE"],
            ].map(([label, value]) => (
              <div
                key={label}
                className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-900/60 p-4"
              >
                <span className="text-sm text-slate-300">
                  {label}
                </span>

                <span className="text-sm font-black text-fuchsia-200">
                  {value}
                </span>
              </div>
            ))}
          </div>
        </section>
      </section>
    </section>
  );
}
