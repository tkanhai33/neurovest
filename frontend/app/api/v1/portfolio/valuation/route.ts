import {
  NextResponse,
} from "next/server";

import {
  backendFetch,
} from "../../../../../lib/backendAuth";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const response = await backendFetch(
      "/api/v1/portfolio/valuation",
    );

    const payload =
      await response.json();

    return NextResponse.json(
      payload,
      {
        status: response.status,
      },
    );
  } catch (error) {
    return NextResponse.json(
      {
        starting_capital: 0,
        current_cash_balance: 0,
        total_fees_paid: 0,
        net_liquidation_value: 0,
        valuation_basis:
          "unavailable",
        live_market_marking:
          false,
        error:
          error instanceof Error
            ? error.message
            : "Portfolio valuation could not be loaded.",
      },
      {
        status: 502,
      },
    );
  }
}
