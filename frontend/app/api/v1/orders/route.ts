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
      "/api/v1/orders",
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
        total_records: 0,
        orders: [],
        error: String(error),
      },
      {
        status: 502,
      },
    );
  }
}
