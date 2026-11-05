"use client";

import { useCallback, useEffect, useState } from "react";

import type { PortfolioPosition } from "../../../services/portfolioService";

import {
  getBackendHealth,
  type BackendHealth,
} from "../../../services/backendHealthService";

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

      <p className={`mt-3 break-words text-2xl font-black sm:text-3xl ${valueClass}`}>
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
  const [backend, setBackend] = useState<BackendHealth | null>(null);
  const [loading, setLoading] = useState(false);
  const [lastError, setLastError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);

    try {
      const backendResult =
        await getBackendHealth();

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

  const backendLabel =
    backend === null
      ? "unknown"
      : backend.apiOnline
        ? "online"
        : "offline";

  return (
    <section className="mt-4 space-y-4">
      <section className="overflow-hidden rounded-3xl border border-cyan-400/30 bg-slate-950/80 shadow-[0_0_45px_rgba(34,211,238,0.12)]">
        <div className="border-b border-slate-800 bg-gradient-to-r from-cyan-500/10 via-fuchsia-500/10 to-transparent p-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-cyan-300">
                Platform overview
              </p>

              <h2 className="mt-2 text-2xl font-black text-white sm:text-3xl">
                Platform and portfolio status
              </h2>

              <p className="mt-2 max-w-3xl text-sm text-slate-400">
                System health, portfolio visibility, and trading safeguards
                in one read-only overview.
              </p>
            </div>

            <button
              type="button"
              onClick={() => void refresh()}
              disabled={loading}
              className="inline-flex min-h-11 items-center justify-center rounded-xl bg-cyan-400 px-4 py-2 text-sm font-black text-slate-950 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300 disabled:opacity-60"
            >
              {loading ? "Refreshing" : "Refresh"}
            </button>
          </div>
        </div>

        <div className="grid gap-3 p-4 sm:p-5 md:grid-cols-2 xl:grid-cols-4">
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

        </div>
      </section>

      {lastError && (
        <section className="rounded-3xl border border-red-400/30 bg-red-950/20 p-5 text-sm text-red-200">
          {lastError}
        </section>
      )}

      <section className="grid gap-6 xl:grid-cols-2">
        <section className="nv-surface-section p-5">
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">
            Trading safeguards
          </p>

          <h3 className="mt-1 text-xl font-black text-white">
            Execution protections
          </h3>
          <p className="mt-3 text-xs leading-5 text-slate-400">
            These labels describe the safety model rather than a live backend verification. Live broker execution is not enabled for the public beta.
          </p>

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
            Neuro status
          </h3>

          <div className="mt-5 grid gap-3">
            {[
              ["Provider", "Ollama"],
              ["Conversation", "Floating button"],
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
