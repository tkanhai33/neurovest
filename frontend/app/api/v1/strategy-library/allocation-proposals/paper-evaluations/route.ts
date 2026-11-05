import { NextResponse } from "next/server";

import { backendFetch } from "../../../../../../lib/backendAuth";

export const dynamic = "force-dynamic";

const BACKEND_PATH =
  "/api/v1/strategy-library/allocation-proposals/paper-evaluations";

export async function GET() {
  try {
    const response = await backendFetch(
      BACKEND_PATH,
      {
        method: "GET",
        headers: {
          Accept: "application/json",
          "X-NeuroVest-Source":
            "frontend-allocation-paper-evaluations-proxy",
        },
        cache: "no-store",
      },
    );

    const payload = await response.text();

    return new NextResponse(
      payload,
      {
        status: response.status,
        headers: {
          "Content-Type":
            response.headers.get("content-type") ??
            "application/json; charset=utf-8",
          "Cache-Control": "no-store",
        },
      },
    );
  } catch {
    return NextResponse.json(
      {
        detail:
          "Allocation paper evaluations are temporarily unavailable.",
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
