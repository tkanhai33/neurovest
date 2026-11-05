import {
  NextResponse,
} from "next/server";

import {
  backendFetch,
} from "../../../../../lib/backendAuth";

export const dynamic = "force-dynamic";

function errorResponse(
  detail: string,
  status: number
) {
  return NextResponse.json(
    {
      status: "error",
      detail,
    },
    {
      status,
      headers: {
        "Cache-Control":
          "no-store, no-cache, must-revalidate",
      },
    }
  );
}

export async function GET() {
  try {
    const response = await backendFetch(
      "/api/v1/admin/execution-control",
      {
        method: "GET",
        cache: "no-store",
        headers: {
          Accept: "application/json",
          "X-Neurovest-Source":
            "frontend_execution_control",
        },
      }
    );

    const rawBody = await response.text();

    let payload: unknown;

    try {
      payload = JSON.parse(rawBody);
    } catch {
      return errorResponse(
        rawBody ||
          "Backend returned a non-JSON execution-control response.",
        response.status || 502
      );
    }

    return NextResponse.json(
      payload,
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
          "Unable to reach the NeuroVest execution-control backend.",
        error:
          error instanceof Error
            ? error.message
            : String(error),
      },
      {
        status: 502,
        headers: {
          "Cache-Control":
            "no-store, no-cache, must-revalidate",
        },
      }
    );
  }
}
