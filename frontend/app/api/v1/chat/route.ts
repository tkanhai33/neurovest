import {
  NextRequest,
  NextResponse,
} from "next/server";

import { backendFetch } from "../../../../lib/backendAuth";

export const dynamic = "force-dynamic";

export async function POST(
  request: NextRequest
) {
  try {
    const payload =
      (await request.json()) as Record<
        string,
        unknown
      >;

    const response = await backendFetch(
      "/api/v1/chat",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Neurovest-Source": "frontend_chat",
        },
        body: JSON.stringify(payload),
      }
    );

    const body = await response.text();

    let parsed: unknown;

    try {
      parsed = JSON.parse(body);
    } catch {
      parsed = {
        status: "error",
        message:
          body ||
          "Backend returned a non-JSON response.",
      };
    }

    return NextResponse.json(parsed, {
      status: response.status,
    });
  } catch (error) {
    return NextResponse.json(
      {
        status: "error",
        message:
          "Unable to reach the NeuroVest chat backend.",
        error: String(error),
      },
      {
        status: 502,
      }
    );
  }
}
