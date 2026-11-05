import {
  NextResponse,
} from "next/server";

import {
  backendFetch,
} from "../../../../../../lib/backendAuth";


export async function GET() {
  try {
    const response =
      await backendFetch(
        "/api/v1/developer/chat/statistics",
        {
          method:
            "GET",

          headers: {
            Accept:
              "application/json",

            "X-NeuroVest-Source":
              "frontend_developer_chat_statistics",
          },
        }
      );

    const payload =
      await response
        .json()
        .catch(
          () => null
        );

    if (!response.ok) {
      return NextResponse.json(
        payload ?? {
          status:
            "error",

          detail:
            "Developer Chat statistics request failed.",
        },
        {
          status:
            response.status,
        }
      );
    }

    return NextResponse.json(
      payload,
      {
        status:
          200,

        headers: {
          "Cache-Control":
            "no-store, max-age=0",
        },
      }
    );

  } catch {
    return NextResponse.json(
      {
        status:
          "unavailable",

        detail:
          "Developer Chat statistics are temporarily unavailable.",
      },
      {
        status:
          502,
      }
    );
  }
}
