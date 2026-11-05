import {
  NextResponse,
} from "next/server";

import { backendFetch } from "../../../../../lib/backendAuth";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const response = await backendFetch(
      "/api/v1/snaptrade/portfolio",
      {
        method: "GET",
        cache: "no-store",
        headers: {
          Accept: "application/json",
          "X-Neurovest-Source":
            "frontend_snaptrade_portfolio",
        },
      }
    );

    const body = await response.text();

    let parsed: unknown;

    try {
      parsed = JSON.parse(body);
    } catch {
      parsed = {
        status: "error",
        detail:
          body ||
          "Backend returned a non-JSON SnapTrade portfolio response.",
      };
    }

    return NextResponse.json(
      parsed,
      {
        status: response.status,
        headers: {
          "Cache-Control":
            "no-store, no-cache, must-revalidate",
        },
      }
    );
  } catch (error) {
    return NextResponse.json(
      {
        status: "error",
        detail:
          "Unable to load the read-only SnapTrade portfolio.",
        error: String(error),
      },
      {
        status: 502,
      }
    );
  }
}
