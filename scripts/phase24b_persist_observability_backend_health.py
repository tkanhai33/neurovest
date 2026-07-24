#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()
S = ROOT / "frontend/services"
PAGE = ROOT / "frontend/app/page.tsx"

# Persist observability metrics in browser localStorage.
(S / "requestObservability.ts").write_text(r'''export type RequestMetric = {
  key: string;
  url: string;
  method: string;
  count: number;
  cacheHits: number;
  inflightHits: number;
  failures: number;
  lastStatus: "idle" | "ok" | "error" | "cache" | "inflight";
  lastLatencyMs: number;
  lastSeen: string;
};

const STORAGE_KEY = "neurovest_request_metrics_v1";
const metrics = new Map<string, RequestMetric>();

function canUseStorage() {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

export function hydrateRequestMetrics() {
  if (!canUseStorage()) return;

  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return;

    const items = JSON.parse(raw) as RequestMetric[];
    metrics.clear();

    for (const item of items) {
      metrics.set(item.key, item);
    }
  } catch {
    metrics.clear();
  }
}

function persistRequestMetrics() {
  if (!canUseStorage()) return;

  window.localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify(Array.from(metrics.values()))
  );
}

export function clearRequestMetrics() {
  metrics.clear();

  if (canUseStorage()) {
    window.localStorage.removeItem(STORAGE_KEY);
  }
}

export function recordRequestMetric(key: string, url: string, method: string, patch: Partial<RequestMetric>) {
  const current = metrics.get(key) || {
    key, url, method, count: 0, cacheHits: 0, inflightHits: 0,
    failures: 0, lastStatus: "idle", lastLatencyMs: 0,
    lastSeen: new Date().toISOString(),
  };

  metrics.set(key, {
    ...current,
    count: current.count + (patch.count ?? 0),
    cacheHits: current.cacheHits + (patch.cacheHits ?? 0),
    inflightHits: current.inflightHits + (patch.inflightHits ?? 0),
    failures: current.failures + (patch.failures ?? 0),
    lastStatus: patch.lastStatus ?? current.lastStatus,
    lastLatencyMs: patch.lastLatencyMs ?? current.lastLatencyMs,
    lastSeen: new Date().toISOString(),
  });

  persistRequestMetrics();
}

export function getRequestMetrics(): RequestMetric[] {
  return Array.from(metrics.values()).sort((a, b) => a.key.localeCompare(b.key));
}
''')

# Backend health service.
(S / "backendHealthService.ts").write_text(r'''export type BackendHealth = {
  apiOnline: boolean;
  frontendOnline: boolean;
  graphOnline: boolean;
  lastChecked: string;
  latencyMs: number;
  error?: string;
};

export async function getBackendHealth(): Promise<BackendHealth> {
  const startedAt = Date.now();

  try {
    const response = await fetch("/api/v1/graph/live", {
      cache: "no-store",
    });

    return {
      apiOnline: response.ok,
      frontendOnline: true,
      graphOnline: response.ok,
      lastChecked: new Date().toISOString(),
      latencyMs: Date.now() - startedAt,
      error: response.ok ? undefined : `status_${response.status}`,
    };
  } catch (error) {
    return {
      apiOnline: false,
      frontendOnline: true,
      graphOnline: false,
      lastChecked: new Date().toISOString(),
      latencyMs: Date.now() - startedAt,
      error: String(error),
    };
  }
}
''')

text = PAGE.read_text()

if 'from "../services/backendHealthService"' not in text:
    text = text.replace(
        'import { getRequestMetrics, type RequestMetric } from "../services/requestObservability";',
        'import { clearRequestMetrics, getRequestMetrics, hydrateRequestMetrics, type RequestMetric } from "../services/requestObservability";\nimport { getBackendHealth, type BackendHealth } from "../services/backendHealthService";'
    )

# Upgrade existing observability panel.
start = text.find("function FrontendObservabilityPanel()")
end = text.find("\n\nfunction FloatingChatWidget()", start)

if start == -1 or end == -1:
    raise RuntimeError("FrontendObservabilityPanel block not found")

component = r'''function FrontendObservabilityPanel() {
  const [metrics, setMetrics] = useState<RequestMetric[]>([]);
  const [health, setHealth] = useState<BackendHealth | null>(null);

  const refreshMetrics = useCallback(() => {
    setMetrics(getRequestMetrics());
  }, []);

  const refreshHealth = useCallback(async () => {
    setHealth(await getBackendHealth());
  }, []);

  useEffect(() => {
    hydrateRequestMetrics();

    const firstLoad = setTimeout(() => {
      refreshMetrics();
      void refreshHealth();
    }, 0);

    const timer = setInterval(() => {
      refreshMetrics();
      void refreshHealth();
    }, 5000);

    return () => {
      clearTimeout(firstLoad);
      clearInterval(timer);
    };
  }, [refreshHealth, refreshMetrics]);

  const totalRequests = metrics.reduce((sum, item) => sum + item.count, 0);
  const totalCacheHits = metrics.reduce((sum, item) => sum + item.cacheHits, 0);
  const totalInflightHits = metrics.reduce((sum, item) => sum + item.inflightHits, 0);
  const totalFailures = metrics.reduce((sum, item) => sum + item.failures, 0);

  return (
    <section className="mt-6 rounded-2xl border border-amber-400/30 bg-slate-950/80 p-5 shadow-[0_0_30px_rgba(251,191,36,0.10)]">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-amber-300">Frontend Observability</p>
          <h2 className="mt-1 text-2xl font-bold text-white">Request Governor Metrics</h2>
        </div>

        <button
          type="button"
          onClick={() => {
            clearRequestMetrics();
            refreshMetrics();
          }}
          className="rounded-xl border border-amber-300/40 px-3 py-2 text-xs text-amber-200"
        >
          Clear Metrics
        </button>
      </div>

      <div className="mb-4 grid gap-3 md:grid-cols-4">
        <div className="rounded-xl bg-slate-900/80 p-3">Backend: {health?.apiOnline ? "ONLINE" : "OFFLINE"}</div>
        <div className="rounded-xl bg-slate-900/80 p-3">Graph: {health?.graphOnline ? "ONLINE" : "OFFLINE"}</div>
        <div className="rounded-xl bg-slate-900/80 p-3">Latency: {health?.latencyMs ?? 0}ms</div>
        <div className="rounded-xl bg-slate-900/80 p-3">Last Check: {health?.lastChecked || "—"}</div>
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-4">
        <div className="rounded-xl bg-slate-900/80 p-3">Requests: {totalRequests}</div>
        <div className="rounded-xl bg-slate-900/80 p-3">Cache Hits: {totalCacheHits}</div>
        <div className="rounded-xl bg-slate-900/80 p-3">Inflight Dedupes: {totalInflightHits}</div>
        <div className="rounded-xl bg-slate-900/80 p-3">Failures: {totalFailures}</div>
      </div>

      {health?.error && (
        <p className="mt-3 rounded-xl border border-red-400/30 bg-red-950/40 p-3 text-xs text-red-200">
          {health.error}
        </p>
      )}

      <div className="mt-4 grid gap-2">
        {metrics.map((item) => (
          <div key={item.key} className="rounded-xl border border-slate-800 bg-slate-900/80 p-3 text-sm">
            <p className="font-bold text-white">{item.key}</p>
            <p className="truncate text-xs text-slate-400">{item.url}</p>
            <p className="text-xs text-amber-200">
              {item.lastStatus} · {item.lastLatencyMs}ms · cache {item.cacheHits} · inflight {item.inflightHits}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}'''

text = text[:start] + component + text[end:]
PAGE.write_text(text)

print("patched Phase 24B persistent observability + backend health")
