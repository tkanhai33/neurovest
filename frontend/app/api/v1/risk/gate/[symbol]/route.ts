import {
  NextRequest,
  NextResponse,
} from "next/server";

import { backendFetch } from "../../../../../../lib/backendAuth";

export const dynamic = "force-dynamic";

export async function GET(
  _request: NextRequest,
  context: {
    params: Promise<{
      symbol: string;
    }>;
  }
) {
  const { symbol } = await context.params;

  const cleanSymbol = String(
    symbol || ""
  )
    .trim()
    .toUpperCase();

  if (!cleanSymbol) {
    return NextResponse.json(
      {
        status: "error",
        symbol: cleanSymbol,
        allowed: false,
        gate: "risk",
        provider: "next_proxy",
        error: "missing_symbol",
      },
      {
        status: 400,
      }
    );
  }

  try {
    const response = await backendFetch(
      `/api/v1/risk/gate/${encodeURIComponent(
        cleanSymbol
      )}`
    );

    const data = await response.json();

    return NextResponse.json(data, {
      status: response.status,
    });
  } catch (error) {
    return NextResponse.json(
      {
        status: "error",
        symbol: cleanSymbol,
        allowed: false,
        gate: "risk",
        provider: "next_proxy",
        error: String(error),
      },
      {
        status: 502,
      }
    );
  }
}
