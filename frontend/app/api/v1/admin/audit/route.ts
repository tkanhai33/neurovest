import {
  NextRequest,
  NextResponse,
} from "next/server";

import { backendFetch } from "../../../../../lib/backendAuth";

export const dynamic = "force-dynamic";

export async function GET(
  request: NextRequest
) {
  try {
    const requestedLimit =
      request.nextUrl.searchParams.get("limit") || "100";

    const numericLimit = Number.parseInt(
      requestedLimit,
      10
    );

    const limit = Number.isFinite(numericLimit)
      ? Math.min(
          1000,
          Math.max(1, numericLimit)
        )
      : 100;

    const response = await backendFetch(
      `/api/v1/admin/audit?limit=${limit}`,
      {
        method: "GET",
        headers: {
          Accept: "application/json",
          "X-Neurovest-Source":
            "frontend_admin_audit",
        },
        cache: "no-store",
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
          "Backend returned a non-JSON audit response.",
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
          "Unable to reach the NeuroVest audit backend.",
        error: String(error),
      },
      {
        status: 502,
      }
    );
  }
}
