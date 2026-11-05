import {
  NextRequest,
  NextResponse,
} from "next/server";

import { backendFetch } from "../../../../../lib/backendAuth";

export const dynamic = "force-dynamic";

async function readPayload(
  request: NextRequest
): Promise<Record<string, unknown>> {
  try {
    return (
      await request.json()
    ) as Record<string, unknown>;
  } catch {
    return {};
  }
}

export async function POST(
  request: NextRequest
) {
  try {
    const payload =
      await readPayload(request);

    const response = await backendFetch(
      "/api/v1/snaptrade/synchronize",
      {
        method: "POST",
        cache: "no-store",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          "X-Neurovest-Source":
            "frontend_snaptrade",
        },
        body: JSON.stringify(
          payload
        ),
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
          "Backend returned a non-JSON SnapTrade synchronization response.",
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
          "Unable to synchronize the read-only SnapTrade connection.",
        error: String(error),
      },
      {
        status: 502,
      }
    );
  }
}
