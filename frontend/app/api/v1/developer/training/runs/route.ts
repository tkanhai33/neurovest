import { NextResponse } from "next/server";

import {
  backendFetch,
} from "../../../../../../lib/backendAuth";


export async function GET() {
  try {
    const response = await backendFetch(
      "/api/v1/developer/training/runs",
      {
        method: "GET",
        headers: {
          Accept: "application/json",
          "X-NeuroVest-Source":
            "frontend_developer_learning_workspace",
        },
      }
    );

    const payload =
      await response.json().catch(
        () => null
      );

    if (!response.ok) {
      return NextResponse.json(
        payload ?? {
          status: "error",
          detail:
            "Developer training runtime request failed.",
        },
        {
          status: response.status,
        }
      );
    }

    return NextResponse.json(
      payload,
      {
        status: 200,
        headers: {
          "Cache-Control":
            "no-store, max-age=0",
          "X-NeuroVest-Truth-Source":
            "bounded-training-runtime",
        },
      }
    );

  } catch {
    return NextResponse.json(
      {
        status: "unavailable",
        detail:
          "Developer training runtime is temporarily unavailable.",
      },
      {
        status: 502,
      }
    );
  }
}
