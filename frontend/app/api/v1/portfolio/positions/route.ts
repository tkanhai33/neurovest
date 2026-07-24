import { NextResponse } from "next/server";

import { backendFetch } from "../../../../../lib/backendAuth";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const response = await backendFetch(
      "/api/v1/portfolio/positions"
    );

    const data = await response.json();

    return NextResponse.json(data, {
      status: response.status,
    });
  } catch (error) {
    return NextResponse.json(
      {
        status: "error",
        positions: [],
        count: 0,
        provider: "next_proxy",
        error: String(error),
      },
      {
        status: 502,
      }
    );
  }
}
