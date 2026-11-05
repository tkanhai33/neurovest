import {
  NextResponse,
} from "next/server";

import {
  backendFetch,
} from "../../../../../lib/backendAuth";

export const dynamic = "force-dynamic";


export async function GET(
  request: Request,
) {
  const symbols = new URL(request.url)
    .searchParams
    .get("symbols")
    ?.trim() ?? "";

  if (!symbols) {
    return NextResponse.json(
      {
        status: "error",
        quotes: {},
        error: "missing_symbols",
      },
      {
        status: 400,
      },
    );
  }

  try {
    const response = await backendFetch(
      `/api/v1/market/live-prices?symbols=${encodeURIComponent(
        symbols,
      )}`,
    );

    return NextResponse.json(
      await response.json(),
      {
        status: response.status,
      },
    );
  } catch (error) {
    return NextResponse.json(
      {
        status: "error",
        quotes: {},
        error: (
          error instanceof Error
            ? error.message
            : "bulk_market_proxy_failed"
        ),
      },
      {
        status: 502,
      },
    );
  }
}
