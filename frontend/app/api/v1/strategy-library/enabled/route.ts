import { NextRequest, NextResponse } from "next/server";

import {
  backendFetch,
} from "../../../../../lib/backendAuth";


async function proxyJson(
  method: "GET" | "PUT" | "DELETE",
  body?: unknown,
) {
  try {
    const response = await backendFetch(
      "/api/v1/strategy-library/enabled",
      {
        method,
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          "X-NeuroVest-Source":
            "frontend_strategy_library_enabled",
        },
        body:
          body === undefined
            ? undefined
            : JSON.stringify(body),
      },
    );

    const payload = await response
      .json()
      .catch(() => null);

    return NextResponse.json(
      payload ?? {
        status: "unavailable",
      },
      {
        status: response.status,
        headers: {
          "Cache-Control":
            "no-store, max-age=0",
        },
      },
    );
  } catch {
    return NextResponse.json(
      {
        status: "unavailable",
      },
      {
        status: 502,
      },
    );
  }
}


export async function GET() {
  return proxyJson(
    "GET",
  );
}


export async function PUT(
  request: NextRequest,
) {
  const body = await request
    .json()
    .catch(() => ({
      strategy_names: [],
    }));

  return proxyJson(
    "PUT",
    body,
  );
}


export async function DELETE() {
  return proxyJson(
    "DELETE",
  );
}
