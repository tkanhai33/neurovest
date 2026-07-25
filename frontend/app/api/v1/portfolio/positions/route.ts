import { NextResponse } from "next/server";

import { backendFetch } from "../../../../../lib/backendAuth";

export const dynamic = "force-dynamic";

type UnknownRecord = Record<string, unknown>;

type OwnedPositionRecord = {
  account_id_hash?: unknown;
  position?: unknown;
};

function isRecord(value: unknown): value is UnknownRecord {
  return (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value)
  );
}

function asFiniteNumber(
  value: unknown,
  fallback = 0,
): number {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }

  if (typeof value === "string" && value.trim()) {
    const parsed = Number(value);

    if (Number.isFinite(parsed)) {
      return parsed;
    }
  }

  return fallback;
}

function asOptionalFiniteNumber(
  value: unknown,
): number | null {
  if (value === null || value === undefined || value === "") {
    return null;
  }

  const parsed = asFiniteNumber(value, Number.NaN);

  return Number.isFinite(parsed)
    ? parsed
    : null;
}

function asString(
  value: unknown,
  fallback = "",
): string {
  return typeof value === "string"
    ? value
    : fallback;
}

function normalizeOwnedPosition(
  item: OwnedPositionRecord,
  index: number,
): UnknownRecord | null {
  if (!isRecord(item.position)) {
    return null;
  }

  const position = item.position;

  const symbol = asString(
    position.symbol,
  ).trim().toUpperCase();

  if (!symbol) {
    return null;
  }

  const quantity = asFiniteNumber(
    position.quantity ??
      position.shares_quantity,
  );

  const averagePrice = asFiniteNumber(
    position.average_price ??
      position.average_entry_price,
  );

  const marketPrice = asOptionalFiniteNumber(
    position.market_price ??
      position.price,
  );

  const marketValue = asOptionalFiniteNumber(
    position.market_value,
  );

  const costBasis = asOptionalFiniteNumber(
    position.cost_basis ??
      position.total_cost_basis,
  );

  const unrealizedGain = asOptionalFiniteNumber(
    position.unrealized_gain ??
      position.unrealized_pnl,
  );

  return {
    id:
      asString(
        position.position_id_hash,
        `${symbol}-${index}`,
      ),
    symbol,
    shares_quantity:
      quantity,
    quantity,
    average_entry_price:
      averagePrice,
    average_price:
      averagePrice,
    total_cost_basis:
      costBasis ?? quantity * averagePrice,
    cost_basis:
      costBasis,
    market_price:
      marketPrice,
    market_value:
      marketValue,
    unrealized_gain:
      unrealizedGain,
    unrealized_pnl:
      unrealizedGain,
    realized_pnl:
      asFiniteNumber(
        position.realized_pnl,
      ),
    currency:
      asString(
        position.currency,
      ),
    instrument_kind:
      asString(
        position.instrument_kind,
      ),
    account_id_hash:
      asString(
        item.account_id_hash,
      ),
    read_only:
      true,
    paper_only:
      true,
    trading_enabled:
      false,
    order_operations_enabled:
      false,
  };
}

function controlledEmpty(
  detail: string,
  status: number,
) {
  return NextResponse.json(
    {
      status:
        status === 403
          ? "portfolio_not_bound"
          : "portfolio_unavailable",
      detail,
      read_only: true,
      paper_only: true,
      trading_enabled: false,
      order_operations_enabled: false,
      positions: [],
    },
    {
      status: 200,
      headers: {
        "Cache-Control": "no-store",
        "X-NeuroVest-Source":
          "owner-scoped-readonly-portfolio",
        "X-NeuroVest-Upstream-Status":
          String(status),
      },
    },
  );
}

export async function GET() {
  try {
    const response = await backendFetch(
      "/api/v1/portfolio/readonly/positions",
      {
        method: "GET",
        cache: "no-store",
      },
    );

    if (response.status === 401) {
      return NextResponse.json(
        {
          status: "unauthorized",
          detail: "Authentication required",
          positions: [],
        },
        {
          status: 401,
          headers: {
            "Cache-Control": "no-store",
          },
        },
      );
    }

    if (response.status === 403) {
      return controlledEmpty(
        "No read-only brokerage portfolio is bound to this user.",
        403,
      );
    }

    if (response.status === 503) {
      return controlledEmpty(
        "The read-only portfolio snapshot is temporarily unavailable.",
        503,
      );
    }

    const payload: unknown = await response.json().catch(
      () => null,
    );

    if (!response.ok) {
      const detail =
        isRecord(payload) &&
        typeof payload.detail === "string"
          ? payload.detail
          : "Portfolio positions could not be loaded.";

      return NextResponse.json(
        {
          status: "upstream_error",
          detail,
          read_only: true,
          paper_only: true,
          trading_enabled: false,
          order_operations_enabled: false,
          positions: [],
        },
        {
          status: response.status,
          headers: {
            "Cache-Control": "no-store",
          },
        },
      );
    }

    const rawPositions =
      isRecord(payload) &&
      Array.isArray(payload.positions)
        ? payload.positions
        : [];

    const positions = rawPositions
      .map((item, index) =>
        isRecord(item)
          ? normalizeOwnedPosition(
              item as OwnedPositionRecord,
              index,
            )
          : null,
      )
      .filter(
        (item): item is UnknownRecord =>
          item !== null,
      );

    return NextResponse.json(
      {
        status: "ok",
        read_only: true,
        paper_only: true,
        trading_enabled: false,
        order_operations_enabled: false,
        owner_scoped: true,
        positions,
      },
      {
        status: 200,
        headers: {
          "Cache-Control": "no-store",
          "X-NeuroVest-Source":
            "owner-scoped-readonly-portfolio",
        },
      },
    );
  } catch {
    return NextResponse.json(
      {
        status: "portfolio_proxy_unavailable",
        detail:
          "The read-only portfolio service is unavailable.",
        read_only: true,
        paper_only: true,
        trading_enabled: false,
        order_operations_enabled: false,
        positions: [],
      },
      {
        status: 503,
        headers: {
          "Cache-Control": "no-store",
        },
      },
    );
  }
}
