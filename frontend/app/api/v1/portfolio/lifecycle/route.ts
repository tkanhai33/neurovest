import { NextResponse } from "next/server";

import { backendFetch } from "../../../../../lib/backendAuth";

export const dynamic = "force-dynamic";

export async function GET() {
  const response = await backendFetch(
    "/api/v1/portfolio/readonly/lifecycle",
    {
      method: "GET",
      cache: "no-store",
    },
  );

  const payload: unknown = await response.json().catch(
    () => ({
      status: "invalid_response",
    }),
  );

  return NextResponse.json(
    payload,
    {
      status: response.status,
      headers: {
        "Cache-Control": "no-store",
      },
    },
  );
}
