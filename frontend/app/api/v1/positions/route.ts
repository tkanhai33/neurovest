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
      "/api/v1/positions",
    );

    const data = await response.json();

    return NextResponse.json(
      data,
      {
        status: response.status,
      },
    );
  } catch (error) {
    return NextResponse.json(
      {
        active_exposure_count: 0,
        positions: [],
        error: String(error),
      },
      {
        status: 502,
      },
    );
  }
}
