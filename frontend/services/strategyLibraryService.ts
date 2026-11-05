/**
 * Canonical browser-side Strategy Library authority.
 *
 * Browser components call NeuroVest frontend API routes only.
 * Authentication/session propagation remains owned by the Next.js proxy layer.
 *
 * This service intentionally preserves Response semantics for existing consumers
 * while also providing one normalized enabled-strategy reader for Neuro Briefing.
 */

export type StrategyLibraryRecord = {
  strategy_name?: unknown;
  name?: unknown;
  enabled?: unknown;
  description?: unknown;
  [key: string]: unknown;
};


export function fetchStrategyLibrary(
  params = "",
  init?: RequestInit,
): Promise<Response> {
  return fetch(
    `/api/v1/strategy-library${params}`,
    init,
  );
}


export function fetchAllocationPaperEvaluations(
  init?: RequestInit,
): Promise<Response> {
  return fetch(
    "/api/v1/strategy-library/allocation-proposals/paper-evaluations",
    init,
  );
}


export function fetchEnabledStrategies(
  init?: RequestInit,
): Promise<Response> {
  return fetch(
    "/api/v1/strategy-library/enabled",
    init,
  );
}


function asRecord(
  value: unknown,
): Record<string, unknown> | null {
  if (
    typeof value !== "object" ||
    value === null ||
    Array.isArray(value)
  ) {
    return null;
  }

  return value as Record<string, unknown>;
}


function extractArray(
  payload: unknown,
): unknown[] {
  if (Array.isArray(payload)) {
    return payload;
  }

  const record = asRecord(payload);

  if (!record) {
    return [];
  }

  for (const key of [
    "strategies",
    "items",
    "data",
  ]) {
    const value = record[key];

    if (Array.isArray(value)) {
      return value;
    }
  }

  return [];
}


export async function getEnabledStrategyNames(): Promise<string[]> {
  const response = await fetchEnabledStrategies({
    method: "GET",
    credentials: "include",
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(
      `Strategy library request failed with ${response.status}`,
    );
  }

  const payload: unknown = await response.json();

  const values = extractArray(payload);

  const names = values
    .map((value) => {
      if (typeof value === "string") {
        return value.trim();
      }

      const record = asRecord(value);

      if (!record) {
        return "";
      }

      const raw =
        record.strategy_name ??
        record.name;

      return typeof raw === "string"
        ? raw.trim()
        : "";
    })
    .filter(
      (value): value is string =>
        Boolean(value),
    );

  return Array.from(
    new Set(names),
  );
}
