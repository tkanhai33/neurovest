import {
  NextResponse,
} from "next/server";

import { backendFetch } from "../../../../../lib/backendAuth";

export const dynamic = "force-dynamic";

async function proxyResponse(
  response: Response
) {
  const body = await response.text();

  let parsed: unknown;

  try {
    parsed = JSON.parse(body);
  } catch {
    parsed = {
      status: "error",
      detail:
        body ||
        "Backend returned a non-JSON SnapTrade status response.",
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
}

export async function GET() {
  try {
    const response = await backendFetch(
      "/api/v1/snaptrade/status",
      {
        method: "GET",
        cache: "no-store",
        headers: {
          Accept: "application/json",
          "X-Neurovest-Source":
            "frontend_snaptrade",
        },
      }
    );

    return await proxyResponse(
      response
    );
  } catch (error) {
    return NextResponse.json(
      {
        status: "error",
        detail:
          "Unable to reach the NeuroVest SnapTrade status backend.",
        error: String(error),
      },
      {
        status: 502,
      }
    );
  }
}
