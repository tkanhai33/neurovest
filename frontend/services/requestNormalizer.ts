import { recordRequestMetric } from "./requestObservability";

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
