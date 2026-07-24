"use client";

import { useCallback, useEffect, useState } from "react";

import {
  getBackendHealth,
  type BackendHealth,
} from "../../../services/backendHealthService";

import {
  getRequestMetrics,
  type RequestMetric,
} from "../../../services/requestObservability";

function MetricCard({
  title,
  value,
  color = "text-white",
}: {
  title: string;
  value: string;
  color?: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
      <p className="text-xs uppercase tracking-[0.2em] text-slate-500">{title}</p>
      <p className={`mt-2 break-all text-2xl font-black ${color}`}>{value}</p>
    </div>
  );
}

export default function NeuroWorkspace() {
  const [backend, setBackend] = useState<BackendHealth | null>(null);
  const [metrics, setMetrics] = useState<RequestMetric[]>([]);

  const refresh = useCallback(async () => {
    try {
      setBackend(await getBackendHealth());
      setMetrics(getRequestMetrics());
    } catch {
      // read-only dev overview
    }
  }, []);

  useEffect(() => {
    const first = setTimeout(() => void refresh(), 0);
    const timer = setInterval(() => void refresh(), 5000);

    return () => {
      clearTimeout(first);
      clearInterval(timer);
    };
  }, [refresh]);

  const ok = metrics.reduce(
    (total, metric) =>
      total + Math.max(0, metric.count - metric.failures),
    0
  );

  const failed = metrics.reduce(
    (total, metric) => total + metric.failures,
    0
  );

  return (
    <section className="mt-6 space-y-6">
      <section className="overflow-hidden rounded-3xl border border-cyan-400/20 bg-slate-950/80">
        <div className="border-b border-slate-800 bg-gradient-to-r from-cyan-500/10 via-fuchsia-500/10 to-transparent p-6">
          <p className="text-xs uppercase tracking-[0.3em] text-cyan-300">Neuro Workspace</p>
          <h2 className="mt-2 text-3xl font-black text-white">Neuro System Overview</h2>
          <p className="mt-2 max-w-3xl text-sm text-slate-400">
            Runtime telemetry and diagnostics. The floating Neuro button remains the only conversational interface.
          </p>
        </div>

        <div className="grid gap-4 p-6 md:grid-cols-5">
          <MetricCard
            title="Backend"
            value={
              backend === null
                ? "unknown"
                : backend.apiOnline
                  ? "online"
                  : "offline"
            }
            color={
              backend?.apiOnline
                ? "text-emerald-300"
                : "text-red-300"
            }
          />
          <MetricCard title="Requests" value={String(ok)} color="text-emerald-300" />
          <MetricCard title="Failures" value={String(failed)} color="text-red-300" />
          <MetricCard title="Provider" value="Ollama" color="text-fuchsia-300" />
          <MetricCard title="Broker" value="Locked" color="text-amber-300" />
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <section className="rounded-3xl border border-cyan-400/20 bg-slate-950/80 p-5">
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">Runtime</p>
          <h3 className="mt-2 text-xl font-black text-white">Current Status</h3>

          <div className="mt-5 space-y-3">
            {[
              ["Replay Engine", "ACTIVE"],
              ["Learning Engine", "ACTIVE"],
              ["Broker Execution", "LOCKED"],
              ["Portfolio Mutation", "LOCKED"],
              ["Chat Interface", "FLOATING BUTTON"],
            ].map(([label, value]) => (
              <div key={label} className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
                <span>{label}</span>
                <span className="rounded-full border border-emerald-400/20 px-3 py-1 text-xs font-bold text-emerald-300">
                  {value}
                </span>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-3xl border border-cyan-400/20 bg-slate-950/80 p-5">
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">Upcoming Metrics</p>
          <h3 className="mt-2 text-xl font-black text-white">Planned Telemetry</h3>

          <div className="mt-5 grid gap-3">
            {[
              "Current model",
              "Fallback reason",
              "Reasoning latency",
              "Prompt tokens",
              "Completion tokens",
              "Memory recall hits",
              "Context size",
              "Provider routing",
            ].map((item) => (
              <div key={item} className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 text-slate-300">
                {item}
              </div>
            ))}
          </div>
        </section>
      </section>
    </section>
  );
}
