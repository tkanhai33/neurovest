export type RequestMetric = {
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
