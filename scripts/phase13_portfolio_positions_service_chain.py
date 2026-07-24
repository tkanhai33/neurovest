#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()

# 13A backend portfolio service facade
service = ROOT / "backend/app/stacks/portfolio/portfolio_service.py"
service.write_text(r'''from backend.app.stacks.execution.paper_broker import get_positions_snapshot


async def get_portfolio_positions_for_api():
    return await get_positions_snapshot()
''')

# Add safe helper if missing
paper = ROOT / "backend/app/stacks/execution/paper_broker.py"
paper_text = paper.read_text()

if "async def get_positions_snapshot" not in paper_text:
    paper_text += r'''


async def get_positions_snapshot():
    return {
        "status": "ok",
        "positions": [],
        "count": 0,
        "provider": "paper_broker",
    }
'''
paper.write_text(paper_text)

# 13B FastAPI route uses portfolio service
main = ROOT / "backend/app/main.py"
main_text = main.read_text()

import_line = "from backend.app.stacks.portfolio.portfolio_service import get_portfolio_positions_for_api\n"
if import_line not in main_text:
    main_text = import_line + main_text

route = r'''

@app.get("/api/v1/portfolio/positions")
async def api_portfolio_positions():
    return await get_portfolio_positions_for_api()
'''

if '"/api/v1/portfolio/positions"' not in main_text:
    main_text += route

main.write_text(main_text)

# 13C frontend portfolioService.ts
services_dir = ROOT / "frontend/services"
services_dir.mkdir(parents=True, exist_ok=True)

portfolio_service = services_dir / "portfolioService.ts"
portfolio_service.write_text(r'''export type PortfolioPosition = {
  id?: string | number;
  symbol: string;
  shares_quantity?: number;
  realized_pnl?: number;
};

export type PortfolioPositionsResponse = {
  status?: string;
  positions: PortfolioPosition[];
  count?: number;
  provider?: string;
  error?: string;
};

export async function getPortfolioPositions(): Promise<PortfolioPositionsResponse> {
  const response = await fetch("/api/v1/portfolio/positions", {
    cache: "no-store",
  });

  return await response.json();
}
''')

# 13D Next proxy route
route_dir = ROOT / "frontend/app/api/v1/portfolio/positions"
route_dir.mkdir(parents=True, exist_ok=True)
(route_dir / "route.ts").write_text(r'''import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const response = await fetch("http://127.0.0.1:8000/api/v1/portfolio/positions", {
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
        positions: [],
        count: 0,
        provider: "next_proxy",
        error: String(error),
      },
      { status: 502 }
    );
  }
}
''')

# 13E page imports frontend service
page = ROOT / "frontend/app/page.tsx"
page_text = page.read_text()

if 'from "../services/portfolioService"' not in page_text:
    page_text = page_text.replace(
        'import { getLivePrice, getLivePrices, type LiveQuote } from "../services/marketService";',
        'import { getLivePrice, getLivePrices, type LiveQuote } from "../services/marketService";\nimport { getPortfolioPositions, type PortfolioPosition } from "../services/portfolioService";'
    )

page_text = page_text.replace(
    "type Position = {\n  id: number | string;\n  symbol: string;\n  shares_quantity: number;\n  realized_pnl?: number;\n};\n\n",
    ""
)

page_text = page_text.replace("useState<Position[]>([])", "useState<PortfolioPosition[]>([])")
page_text = page_text.replace("(p: Position)", "(p: PortfolioPosition)")

# Replace direct positions fetch if present
page_text = page_text.replace(
    '''      const positionsResponse = await fetch("/api/v1/positions");
      const positionsData = await positionsResponse.json();
      setPositions(positionsData.positions || []);''',
    '''      const positionsData = await getPortfolioPositions();
      setPositions(positionsData.positions || []);'''
)

page.write_text(page_text)

print("patched Phase 13 portfolio positions service chain")
