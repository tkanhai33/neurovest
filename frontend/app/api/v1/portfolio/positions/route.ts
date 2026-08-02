import {
  NextResponse,
} from "next/server";

import {
  backendFetch,
} from "../../../../../lib/backendAuth";

export const dynamic = "force-dynamic";

type BackendPosition = {
  id: number;
  symbol: string;
  shares_quantity: number;
  average_entry_price: number;
  total_cost_basis: number;
  realized_pnl: number;
  last_updated: string | null;
};

type BackendPositionsResponse = {
  active_exposure_count: number;
  positions: BackendPosition[];
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

function isBackendPositionsResponse(
  value: unknown,
): value is BackendPositionsResponse {
  if (!isRecord(value)) {
    return false;
  }

  return (
    typeof value.active_exposure_count === "number" &&
    Array.isArray(value.positions)
  );
}

export async function GET() {
  try {
    const response = await backendFetch(
      "/api/v1/positions",
      {
        method: "GET",
        cache: "no-store",
      },
    );

    const payload: unknown = await response
      .json()
      .catch(() => null);

    if (response.status === 401) {
      return NextResponse.json(
        {
          detail: "Authentication required",
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
      return NextResponse.json(
        {
          detail: "Portfolio access denied",
        },
        {
          status: 403,
          headers: {
            "Cache-Control": "no-store",
          },
        },
      );
    }

    if (!response.ok) {
      return NextResponse.json(
        isRecord(payload)
          ? payload
          : {
              detail:
                "Portfolio positions request failed",
            },
        {
          status: response.status,
          headers: {
            "Cache-Control": "no-store",
            "X-NeuroVest-Source":
              "owner-scoped-paper-inventory",
            "X-NeuroVest-Upstream-Status":
              String(response.status),
          },
        },
      );
    }

    if (!isBackendPositionsResponse(payload)) {
      return NextResponse.json(
        {
          detail:
            "Invalid owner-scoped portfolio response",
        },
        {
          status: 502,
          headers: {
            "Cache-Control": "no-store",
            "X-NeuroVest-Source":
              "owner-scoped-paper-inventory",
          },
        },
      );
    }

    /*
     * Preserve the backend response exactly.
     *
     * The backend already:
     * - authenticates the principal;
     * - filters PortfolioInventory by principal.subject;
     * - returns only that user's paper positions.
     *
     * Rewrapping this response previously caused valid positions to
     * be discarded and replaced by an empty brokerage snapshot.
     */
    return NextResponse.json(
      payload,
      {
        status: 200,
        headers: {
          "Cache-Control": "no-store",
          "X-NeuroVest-Source":
            "owner-scoped-paper-inventory",
          "X-NeuroVest-Upstream-Status":
            String(response.status),
        },
      },
    );
  } catch (error) {
    return NextResponse.json(
      {
        detail:
          "Portfolio positions proxy unavailable",
        error:
          error instanceof Error
            ? error.message
            : String(error),
      },
      {
        status: 502,
        headers: {
          "Cache-Control": "no-store",
        },
      },
    );
  }
}
