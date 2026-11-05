import { NextRequest, NextResponse } from "next/server";

import {
  backendFetch,
} from "../../../../lib/backendAuth";


export async function GET(
  request: NextRequest,
) {
  const market =
    request.nextUrl.searchParams.get("market");

  const query = market
    ? `?market=${encodeURIComponent(market)}`
    : "";

  try {
    const response = await backendFetch(
      `/api/v1/strategy-library${query}`,
      {
        method: "GET",
        headers: {
          Accept: "application/json",
          "X-NeuroVest-Source":
            "frontend_strategy_library",
        },
      },
    );

    const payload = await response
      .json()
      .catch(() => null);

    return NextResponse.json(
      payload ?? {
        status: "unavailable",
      },
      {
        status: response.status,
        headers: {
          "Cache-Control":
            "no-store, max-age=0",
        },
      },
    );
  } catch {
    return NextResponse.json(
      {
        status: "unavailable",
      },
      {
        status: 502,
      },
    );
  }
}
