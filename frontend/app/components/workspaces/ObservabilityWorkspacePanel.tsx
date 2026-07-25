"use client";

import { useCallback, useEffect, useState } from "react";

import {
  clearRequestMetrics,
  getRequestMetrics,
  hydrateRequestMetrics,
  type RequestMetric,
} from "../../../services/requestObservability";

import {
  getObservabilityTimeline,
  type ObservabilityEvent,
} from "../../../services/observabilityTimelineService";

import {
  getBackendHealth,
  type BackendHealth,
} from "../../../services/backendHealthService";

function FrontendObservabilityPanel({
  metrics,
  onClear,
}: {
  metrics: RequestMetric[];
  onClear: () => void;
}) {
  return (
    <section className="nv-surface-section p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">
            Request Telemetry
          </p>
          <h3 className="mt-1 text-xl font-black text-white">
            Frontend Requests
          </h3>
        </div>

        <button
          type="button"
          onClick={onClear}
          className="rounded-xl border border-red-400/30 px-4 py-2 text-sm font-bold text-red-200"
        >
          Clear Metrics
        </button>
      </div>

      <div className="mt-5 grid gap-3">
        {metrics.length === 0 ? (
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 text-sm text-slate-400">
            No frontend request metrics recorded.
          </div>
        ) : (
          metrics.map((metric) => (
            <div
              key={metric.key}
              className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4"
            >
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="font-black text-white">{metric.key}</p>
                  <p className="mt-1 text-xs text-slate-400">
                    {metric.method} {metric.url}
                  </p>
                </div>

                <span
                  className={
                    metric.lastStatus === "error"
                      ? "rounded-full border border-red-400/30 px-3 py-1 text-xs text-red-300"
                      : "rounded-full border border-emerald-400/30 px-3 py-1 text-xs text-emerald-300"
                  }
                >
                  {metric.lastStatus}
                </span>
              </div>

              <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-slate-400 md:grid-cols-5">
                <p>Count: {metric.count}</p>
                <p>Cache: {metric.cacheHits}</p>
                <p>Inflight: {metric.inflightHits}</p>
                <p>Failures: {metric.failures}</p>
                <p>Latency: {metric.lastLatencyMs}ms</p>
              </div>
            </div>
          ))
        )}
      </div>
    </section>
  );
}

function ObservabilityEventTimeline({
  events,
}: {
  events: ObservabilityEvent[];
}) {
  return (
    <section className="rounded-3xl border border-fuchsia-400/20 bg-slate-950/80 p-5">
      <p className="text-xs uppercase tracking-[0.25em] text-fuchsia-300">
        Timeline
      </p>

      <h3 className="mt-1 text-xl font-black text-white">
        Recent Frontend + Runtime Events
      </h3>

      <div className="mt-5 grid gap-3">
        {events.length === 0 ? (
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 text-sm text-slate-400">
            No observability events available.
          </div>
        ) : (
          events.map((event) => (
            <div
              key={event.id}
              className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4"
            >
              <div className="flex flex-wrap items-center justify-between gap-3">
                <p className="font-black text-white">{event.label}</p>

                <span className="rounded-full border border-fuchsia-400/30 px-3 py-1 text-xs text-fuchsia-200">
                  {event.source} · {event.status}
                </span>
              </div>

              <p className="mt-2 text-xs text-slate-400">{event.detail}</p>
              <p className="mt-1 text-xs text-slate-500">{event.timestamp}</p>
            </div>
          ))
        )}
      </div>
    </section>
  );
}

export default function ObservabilityWorkspacePanel() {
  const [backendHealth, setBackendHealth] =
    useState<BackendHealth | null>(null);

  const [metrics, setMetrics] = useState<RequestMetric[]>([]);
  const [events, setEvents] = useState<ObservabilityEvent[]>([]);

  const loadDevOverview = useCallback(async () => {
    try {
      hydrateRequestMetrics();

      const [health, timeline] = await Promise.all([
        getBackendHealth(),
        getObservabilityTimeline(),
      ]);

      setBackendHealth(health);
      setMetrics(getRequestMetrics());
      setEvents(timeline);
    } catch {
      setMetrics(getRequestMetrics());
    }
  }, []);

  useEffect(() => {
    const firstLoad = setTimeout(() => void loadDevOverview(), 0);
    const timer = setInterval(() => void loadDevOverview(), 5000);

    return () => {
      clearTimeout(firstLoad);
      clearInterval(timer);
    };
  }, [loadDevOverview]);

  const failedRequests = metrics.reduce(
    (total, item) => total + item.failures,
    0
  );

  const successfulRequests = metrics.reduce(
    (total, item) => total + Math.max(0, item.count - item.failures),
    0
  );

  const backendStatus = backendHealth?.apiOnline ? "online" : "offline";

  function clearMetrics() {
    clearRequestMetrics();
    setMetrics([]);
  }

  return (
    <section className="mt-6 space-y-6">
      <section className="overflow-hidden rounded-3xl border border-fuchsia-400/30 bg-slate-950/80 shadow-[0_0_40px_rgba(217,70,239,0.12)]">
        <div className="border-b border-slate-800 bg-gradient-to-r from-fuchsia-500/10 via-cyan-500/10 to-transparent p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-fuchsia-300">
            Observability
          </p>

          <h2 className="mt-1 text-3xl font-black text-white">
            Dev Runtime Overview
          </h2>

          <p className="mt-2 max-w-3xl text-sm text-slate-400">
            Backend health, request telemetry, chat route visibility,
            Ollama fallback monitoring, and runtime safety locks.
          </p>
        </div>

        <div className="grid gap-3 p-5 md:grid-cols-4">
          {[
            ["Backend", backendStatus, "text-cyan-300"],
            ["Requests OK", String(successfulRequests), "text-emerald-300"],
            ["Failed", String(failedRequests), "text-red-300"],
            ["Ollama Fallback", "watching", "text-fuchsia-300"],
          ].map(([label, value, color]) => (
            <div
              key={label}
              className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4"
            >
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                {label}
              </p>

              <p className={`mt-2 break-all text-2xl font-black ${color}`}>
                {value}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <section className="nv-surface-section p-5">
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">
            Runtime Locks
          </p>

          <h3 className="mt-1 text-xl font-black text-white">
            Safety Status
          </h3>

          <div className="mt-5 grid gap-3">
            {[
              ["Replay mode", "ACTIVE"],
              ["Broker execution", "DISABLED"],
              ["Live execution", "DISABLED"],
              ["Portfolio mutation", "DISABLED"],
              ["Chat button", "UNCHANGED"],
            ].map(([label, value]) => (
              <div
                key={label}
                className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-900/60 p-4"
              >
                <span className="text-sm text-slate-300">{label}</span>

                <span className="rounded-full border border-emerald-400/20 px-3 py-1 text-xs font-bold text-emerald-300">
                  {value}
                </span>
              </div>
            ))}
          </div>
        </section>

        <section className="nv-surface-section p-5">
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">
            Backend Health
          </p>

          <h3 className="mt-1 text-xl font-black text-white">
            API / Graph Status
          </h3>

          <div className="mt-5 grid gap-3">
            {[
              ["API", backendHealth?.apiOnline ? "ONLINE" : "OFFLINE"],
              ["Frontend", backendHealth?.frontendOnline ? "ONLINE" : "OFFLINE"],
              ["Graph", backendHealth?.graphOnline ? "ONLINE" : "OFFLINE"],
              ["Latency", `${backendHealth?.latencyMs ?? 0}ms`],
            ].map(([label, value]) => (
              <div
                key={label}
                className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-900/60 p-4"
              >
                <span className="text-sm text-slate-300">{label}</span>
                <span className="text-sm font-black text-cyan-200">{value}</span>
              </div>
            ))}

            {backendHealth?.error && (
              <div className="rounded-2xl border border-red-400/30 bg-red-950/20 p-4 text-xs text-red-200">
                {backendHealth.error}
              </div>
            )}
          </div>
        </section>
      </section>

      <FrontendObservabilityPanel
        metrics={metrics}
        onClear={clearMetrics}
      />

      <ObservabilityEventTimeline events={events} />
    </section>
  );
}
