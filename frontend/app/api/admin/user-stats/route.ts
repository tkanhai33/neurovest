import {
  NextResponse,
} from "next/server";

import {
  backendFetch,
} from "../../../../lib/backendAuth";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const response = await backendFetch(
      "/api/v1/admin/user-stats",
      {
        method: "GET",
        cache: "no-store",
      },
    );

    const payload: unknown = await response
      .json()
      .catch(() => null);

    if (!response.ok) {
      return NextResponse.json(
        payload &&
          typeof payload === "object"
          ? payload
          : {
              detail:
                "Administrative statistics request failed",
            },
        {
          status: response.status,
          headers: {
            "Cache-Control": "no-store",
            "X-NeuroVest-Upstream-Status":
              String(response.status),
          },
        },
      );
    }

    return NextResponse.json(
      payload,
      {
        status: 200,
        headers: {
          "Cache-Control": "no-store",
          "X-NeuroVest-Source":
            "server-authoritative-postgresql",
          "X-NeuroVest-Upstream-Status":
            String(response.status),
        },
      },
    );
  } catch (error) {
    return NextResponse.json(
      {
        detail:
          "Administrative statistics proxy unavailable",
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
