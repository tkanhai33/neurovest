#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()
S = ROOT / "frontend/services"
PAGE = ROOT / "frontend/app/page.tsx"

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

const metrics = new Map<string, RequestMetric>();

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
}

export function getRequestMetrics(): RequestMetric[] {
  return Array.from(metrics.values()).sort((a, b) => a.key.localeCompare(b.key));
}
''')

(S / "requestNormalizer.ts").write_text(r'''import { recordRequestMetric } from "./requestObservability";

type CacheEntry<T> = { expiresAt: number; value: T };

const responseCache = new Map<string, CacheEntry<unknown>>();
const inflight = new Map<string, Promise<unknown>>();

export type RequestOptions = {
  ttlMs?: number;
  method?: "GET" | "POST";
  headers?: Record<string, string>;
  body?: BodyInit | null;
};

export async function normalizedJsonRequest<T>(key: string, url: string, options: RequestOptions = {}): Promise<T> {
  const method = options.method || "GET";
  const ttlMs = options.ttlMs ?? 3000;
  const cacheKey = `${method}:${key}`;
  const now = Date.now();

  if (method === "GET") {
    const cached = responseCache.get(cacheKey);
    if (cached && cached.expiresAt > now) {
      recordRequestMetric(cacheKey, url, method, { cacheHits: 1, lastStatus: "cache" });
      return cached.value as T;
    }

    const existing = inflight.get(cacheKey);
    if (existing) {
      recordRequestMetric(cacheKey, url, method, { inflightHits: 1, lastStatus: "inflight" });
      return existing as Promise<T>;
    }
  }

  const startedAt = Date.now();

  const request = fetch(url, {
    method,
    headers: options.headers,
    body: options.body,
    cache: "no-store",
  })
    .then(async (response) => {
      const data = await response.json();
      recordRequestMetric(cacheKey, url, method, {
        count: 1,
        lastStatus: "ok",
        lastLatencyMs: Date.now() - startedAt,
      });

      if (method === "GET") {
        responseCache.set(cacheKey, { expiresAt: Date.now() + ttlMs, value: data });
      }

      return data as T;
    })
    .catch((error) => {
      recordRequestMetric(cacheKey, url, method, {
        failures: 1,
        lastStatus: "error",
        lastLatencyMs: Date.now() - startedAt,
      });
      throw error;
    })
    .finally(() => inflight.delete(cacheKey));

  if (method === "GET") inflight.set(cacheKey, request);
  return request;
}
''')

text = PAGE.read_text()

if 'from "../services/requestObservability"' not in text:
    text = text.replace(
        'import { getLiveGraph, type LiveGraphResponse } from "../services/graphService";',
        'import { getLiveGraph, type LiveGraphResponse } from "../services/graphService";\nimport { getRequestMetrics, type RequestMetric } from "../services/requestObservability";'
    )

component = r'''
function FrontendObservabilityPanel() {
  const [metrics, setMetrics] = useState<RequestMetric[]>([]);

  const refreshMetrics = useCallback(() => {
    setMetrics(getRequestMetrics());
  }, []);

  useEffect(() => {
    const firstLoad = setTimeout(refreshMetrics, 0);
    const timer = setInterval(refreshMetrics, 5000);

    return () => {
      clearTimeout(firstLoad);
      clearInterval(timer);
    };
  }, [refreshMetrics]);

  const totalRequests = metrics.reduce((sum, item) => sum + item.count, 0);
  const totalCacheHits = metrics.reduce((sum, item) => sum + item.cacheHits, 0);
  const totalInflightHits = metrics.reduce((sum, item) => sum + item.inflightHits, 0);
  const totalFailures = metrics.reduce((sum, item) => sum + item.failures, 0);

  return (
    <section className="mt-6 rounded-2xl border border-amber-400/30 bg-slate-950/80 p-5 shadow-[0_0_30px_rgba(251,191,36,0.10)]">
      <p className="text-xs uppercase tracking-[0.3em] text-amber-300">Frontend Observability</p>
      <h2 className="mt-1 text-2xl font-bold text-white">Request Governor Metrics</h2>

      <div className="mt-4 grid gap-3 md:grid-cols-4">
        <div className="rounded-xl bg-slate-900/80 p-3">Requests: {totalRequests}</div>
        <div className="rounded-xl bg-slate-900/80 p-3">Cache Hits: {totalCacheHits}</div>
        <div className="rounded-xl bg-slate-900/80 p-3">Inflight Dedupes: {totalInflightHits}</div>
        <div className="rounded-xl bg-slate-900/80 p-3">Failures: {totalFailures}</div>
      </div>

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
}
'''

if "function FrontendObservabilityPanel()" not in text:
    text = text.replace("function FloatingChatWidget()", component + "\n\nfunction FloatingChatWidget()", 1)

if "<FrontendObservabilityPanel />" not in text:
    text = text.replace("<LiveSystemGraphPanel />", "<LiveSystemGraphPanel />\n      <FrontendObservabilityPanel />", 1)

PAGE.write_text(text)
print("hard patched Phase 24A frontend observability dashboard")
