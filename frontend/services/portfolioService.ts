export type PortfolioPosition = {
  id?: number | string;
  symbol: string;
  shares_quantity?: number;
  quantity?: number;
  average_entry_price?: number;
  average_price?: number;
  total_cost_basis?: number | null;
  cost_basis?: number | null;
  market_price?: number | null;
  market_value?: number | null;
  unrealized_gain?: number | null;
  unrealized_pnl?: number | null;
  realized_pnl?: number;
  currency?: string;
  instrument_kind?: string;
  account_id_hash?: string;
  read_only?: boolean;
  paper_only?: boolean;
  trading_enabled?: boolean;
  order_operations_enabled?: boolean;
};

export type PortfolioPositionsResponse = {
  status?: string;
  detail?: string;
  read_only?: boolean;
  paper_only?: boolean;
  trading_enabled?: boolean;
  order_operations_enabled?: boolean;
  owner_scoped?: boolean;
  positions: PortfolioPosition[];
};

function isRecord(
  value: unknown,
): value is Record<string, unknown> {
  return (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value)
  );
}

export async function getPortfolioPositions(): Promise<PortfolioPositionsResponse> {
  const response = await fetch(
    "/api/v1/portfolio/positions",
    {
      method: "GET",
      credentials: "include",
      cache: "no-store",
      headers: {
        Accept: "application/json",
      },
    },
  );

  const payload: unknown = await response.json().catch(
    () => null,
  );

  if (response.status === 401) {
    throw new Error(
      "Authentication required",
    );
  }

  if (!response.ok) {
    const detail =
      isRecord(payload) &&
      typeof payload.detail === "string"
        ? payload.detail
        : "Portfolio positions could not be loaded.";

    throw new Error(detail);
  }

  if (!isRecord(payload)) {
    return {
      status: "invalid_response",
      read_only: true,
      paper_only: true,
      trading_enabled: false,
      order_operations_enabled: false,
      owner_scoped: true,
      positions: [],
    };
  }

  const positions = Array.isArray(
    payload.positions,
  )
    ? payload.positions.filter(
        (item): item is PortfolioPosition =>
          isRecord(item) &&
          typeof item.symbol === "string",
      )
    : [];

  return {
    status:
      typeof payload.status === "string"
        ? payload.status
        : "ok",
    detail:
      typeof payload.detail === "string"
        ? payload.detail
        : undefined,
    read_only:
      payload.read_only === true,
    paper_only:
      payload.paper_only === true,
    trading_enabled:
      payload.trading_enabled === true,
    order_operations_enabled:
      payload.order_operations_enabled === true,
    owner_scoped:
      payload.owner_scoped === true,
    positions,
  };
}

// BEGIN NEUROVEST PORTFOLIO SNAPSHOT LIFECYCLE CLIENT

export type PortfolioSnapshotLifecycle = {
  status?: string;
  owner_scoped?: boolean;
  read_only?: boolean;
  paper_only?: boolean;
  trading_enabled?: boolean;
  order_operations_enabled?: boolean;
  external_refresh_enabled?: boolean;
  refresh_source?: string;
  snapshot_state?: "missing" | "fresh" | "stale" | string;
  active_snapshot_present?: boolean;
  active_snapshot_sha256?: string | null;
  snapshot_age_seconds?: number | null;
  stale_after_seconds?: number;
  stale_at?: string | null;
  last_refresh_started_at?: string | null;
  last_successful_refresh_at?: string | null;
  last_failed_refresh_at?: string | null;
  last_refresh_status?: string;
  last_failure_type?: string | null;
  last_failure_message?: string | null;
  refresh_count?: number;
  failed_refresh_count?: number;
  retained_snapshot_count?: number;
  retention_limit?: number;
  network_request_count?: number;
  database_write_count?: number;
  refresh_result?: string;
};

export async function getPortfolioSnapshotLifecycle(): Promise<PortfolioSnapshotLifecycle> {
  const response = await fetch(
    "/api/v1/portfolio/lifecycle",
    {
      method: "GET",
      credentials: "include",
      cache: "no-store",
      headers: {
        Accept: "application/json",
      },
    },
  );

  const payload =
    (await response.json()) as PortfolioSnapshotLifecycle;

  if (!response.ok) {
    throw new Error(
      typeof payload === "object" &&
      payload !== null &&
      "detail" in payload
        ? String(
            (payload as {
              detail?: unknown;
            }).detail,
          )
        : "Portfolio lifecycle could not be loaded.",
    );
  }

  return payload;
}

export async function refreshPortfolioSnapshot(): Promise<PortfolioSnapshotLifecycle> {
  const response = await fetch(
    "/api/v1/portfolio/refresh",
    {
      method: "POST",
      credentials: "include",
      cache: "no-store",
      headers: {
        Accept: "application/json",
      },
    },
  );

  const payload =
    (await response.json()) as PortfolioSnapshotLifecycle;

  if (!response.ok) {
    throw new Error(
      typeof payload === "object" &&
      payload !== null &&
      "detail" in payload
        ? String(
            (payload as {
              detail?: unknown;
            }).detail,
          )
        : "Portfolio snapshot refresh failed.",
    );
  }

  return payload;
}

// END NEUROVEST PORTFOLIO SNAPSHOT LIFECYCLE CLIENT

