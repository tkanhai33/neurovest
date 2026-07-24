#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()

route_dir = ROOT / "frontend/app/api/v1/market/live-price/[symbol]"
route_dir.mkdir(parents=True, exist_ok=True)

route_file = route_dir / "route.ts"

route_file.write_text(r'''import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(
  _request: NextRequest,
  context: { params: Promise<{ symbol: string }> }
) {
  const { symbol } = await context.params;
  const cleanSymbol = String(symbol || "").trim().toUpperCase();

  if (!cleanSymbol) {
    return NextResponse.json(
      {
        status: "error",
        symbol: cleanSymbol,
        price: null,
        provider: "next_proxy",
        error: "missing_symbol",
      },
      { status: 400 }
    );
  }

  try {
    const backendUrl = `http://127.0.0.1:8000/api/v1/market/live-price/${encodeURIComponent(cleanSymbol)}`;

    const response = await fetch(backendUrl, {
      cache: "no-store",
    });

    const data = await response.json();

    return NextResponse.json(data, {
      status: response.status,
    });
  } catch (error) {
    return NextResponse.json(
      {
        status: "error",
        symbol: cleanSymbol,
        price: null,
        provider: "next_proxy",
        error: String(error),
      },
      { status: 502 }
    );
  }
}
''')

print(f"patched Phase 11D Next API proxy: {route_file}")
