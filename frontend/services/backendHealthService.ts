export type BackendHealth = {
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
