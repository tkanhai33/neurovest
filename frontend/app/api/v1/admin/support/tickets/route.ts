import {
  NextResponse,
} from "next/server";

import {
  backendFetch,
} from "../../../../../../lib/backendAuth";


export const dynamic = "force-dynamic";


export async function GET(
  request: Request,
) {
  const url = new URL(
    request.url,
  );

  const query =
    url.search.length > 0
      ? url.search
      : "";

  try {
    const response = await backendFetch(
      `/api/v1/admin/support/tickets${query}`,
      {
        method: "GET",
        headers: {
          Accept: "application/json",
          "X-NeuroVest-Source":
            "frontend_admin_support_tickets",
        },
      },
    );

    let body: unknown;

    try {
      body = await response.json();
    } catch {
      body = {
        detail:
          "Administrative support service returned an invalid response.",
      };
    }

    return NextResponse.json(
      body,
      {
        status: response.status,
        headers: {
          "Cache-Control":
            "no-store, no-cache, must-revalidate",
        },
      },
    );
  } catch {
    return NextResponse.json(
      {
        status: "unavailable",
        detail:
          "Administrative support tickets are temporarily unavailable.",
      },
      {
        status: 502,
        headers: {
          "Cache-Control":
            "no-store, no-cache, must-revalidate",
        },
      },
    );
  }
}
