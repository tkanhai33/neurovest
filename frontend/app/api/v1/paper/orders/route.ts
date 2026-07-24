import {
  NextRequest,
  NextResponse,
} from "next/server";

import {
  backendFetch,
} from "../../../../../lib/backendAuth";

export const dynamic = "force-dynamic";

export async function POST(
  request: NextRequest,
) {
  try {
    const body = await request.text();

    const response = await backendFetch(
      "/api/v1/paper/orders",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body,
      },
    );

    const contentType =
      response.headers.get(
        "content-type",
      ) ?? "";

    if (
      contentType.includes(
        "application/json",
      )
    ) {
      return NextResponse.json(
        await response.json(),
        {
          status: response.status,
        },
      );
    }

    return NextResponse.json(
      {
        status: "error",
        detail:
          await response.text(),
      },
      {
        status: response.status,
      },
    );
  } catch (error) {
    return NextResponse.json(
      {
        status: "error",
        detail:
          error instanceof Error
            ? error.message
            : "Paper order could not be submitted.",
      },
      {
        status: 502,
      },
    );
  }
}
