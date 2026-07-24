#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()

# 14A backend strategy service facade
service = ROOT / "backend/app/stacks/strategy/strategy_service.py"
service.write_text(r'''from backend.app.stacks.strategy.engine import generate_strategy_decision


async def get_strategy_decision_for_api(symbol: str):
    clean_symbol = symbol.strip().upper()

    if not clean_symbol:
        return {
            "status": "error",
            "symbol": clean_symbol,
            "decision": "hold",
            "confidence": 0,
            "provider": "strategy_service",
            "error": "missing_symbol",
        }

    try:
        result = generate_strategy_decision(clean_symbol)

        if hasattr(result, "__await__"):
            result = await result

        if isinstance(result, dict):
            result.setdefault("status", "ok")
            result.setdefault("symbol", clean_symbol)
            result.setdefault("provider", "strategy_engine")
            return result

        return {
            "status": "ok",
            "symbol": clean_symbol,
            "decision": str(result),
            "confidence": 0,
            "provider": "strategy_engine",
        }

    except Exception as e:
        return {
            "status": "error",
            "symbol": clean_symbol,
            "decision": "hold",
            "confidence": 0,
            "provider": "strategy_service",
            "error": f"{type(e).__name__}: {e}",
        }
''')

# 14B FastAPI route uses strategy service
main = ROOT / "backend/app/main.py"
main_text = main.read_text()

import_line = "from backend.app.stacks.strategy.strategy_service import get_strategy_decision_for_api\n"
if import_line not in main_text:
    main_text = import_line + main_text

route = r'''

@app.get("/api/v1/strategy/decision/{symbol}")
async def api_strategy_decision(symbol: str):
    return await get_strategy_decision_for_api(symbol)
'''

if '"/api/v1/strategy/decision/{symbol}"' not in main_text:
    main_text += route

main.write_text(main_text)

# 14C frontend strategyService.ts
services_dir = ROOT / "frontend/services"
services_dir.mkdir(parents=True, exist_ok=True)

strategy_service = services_dir / "strategyService.ts"
strategy_service.write_text(r'''export type StrategyDecision = {
  status?: string;
  symbol: string;
  decision?: string;
  signal?: string;
  confidence?: number;
  provider?: string;
  error?: string;
};

export async function getStrategyDecision(symbol: string): Promise<StrategyDecision> {
  const cleanSymbol = symbol.trim().toUpperCase();

  if (!cleanSymbol) {
    return {
      status: "error",
      symbol: cleanSymbol,
      decision: "hold",
      confidence: 0,
      provider: "frontend_strategy_service",
      error: "missing_symbol",
    };
  }

  const response = await fetch(`/api/v1/strategy/decision/${cleanSymbol}`, {
    cache: "no-store",
  });

  return await response.json();
}
''')

# 14D Next proxy route
route_dir = ROOT / "frontend/app/api/v1/strategy/decision/[symbol]"
route_dir.mkdir(parents=True, exist_ok=True)

(route_dir / "route.ts").write_text(r'''import { NextRequest, NextResponse } from "next/server";

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
        decision: "hold",
        confidence: 0,
        provider: "next_proxy",
        error: "missing_symbol",
      },
      { status: 400 }
    );
  }

  try {
    const response = await fetch(
      `http://127.0.0.1:8000/api/v1/strategy/decision/${encodeURIComponent(cleanSymbol)}`,
      {
        cache: "no-store",
      }
    );

    const data = await response.json();

    return NextResponse.json(data, {
      status: response.status,
    });
  } catch (error) {
    return NextResponse.json(
      {
        status: "error",
        symbol: cleanSymbol,
        decision: "hold",
        confidence: 0,
        provider: "next_proxy",
        error: String(error),
      },
      { status: 502 }
    );
  }
}
''')

# 14E frontend decision card
page = ROOT / "frontend/app/page.tsx"
page_text = page.read_text()

if 'from "../services/strategyService"' not in page_text:
    page_text = page_text.replace(
        'import { getPortfolioPositions, type PortfolioPosition } from "../services/portfolioService";',
        'import { getPortfolioPositions, type PortfolioPosition } from "../services/portfolioService";\nimport { getStrategyDecision, type StrategyDecision } from "../services/strategyService";'
    )

component = r'''
function StrategyDecisionCard() {
  const [symbol, setSymbol] = useState("AAPL");
  const [decision, setDecision] = useState<StrategyDecision | null>(null);
  const [loading, setLoading] = useState(false);

  const loadDecision = useCallback(async (nextSymbol = symbol) => {
    const cleanSymbol = nextSymbol.trim().toUpperCase();

    if (!cleanSymbol) return;

    setLoading(true);

    try {
      const data = await getStrategyDecision(cleanSymbol);
      setDecision(data);
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  useEffect(() => {
    const firstLoad = setTimeout(() => {
      void loadDecision(symbol);
    }, 0);

    const timer = setInterval(() => {
      void loadDecision(symbol);
    }, 30000);

    return () => {
      clearTimeout(firstLoad);
      clearInterval(timer);
    };
  }, [loadDecision, symbol]);

  const visibleDecision = decision?.decision || decision?.signal || "hold";

  return (
    <section className="mt-6 rounded-2xl border border-violet-400/30 bg-slate-950/80 p-5 shadow-[0_0_30px_rgba(167,139,250,0.12)]">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-violet-300">Strategy Decision</p>
          <h2 className="mt-1 text-2xl font-bold text-white">{decision?.symbol || symbol}</h2>
        </div>

        <div className="rounded-full border border-violet-400/30 px-3 py-1 text-xs text-violet-200">
          {decision?.status || "idle"}
        </div>
      </div>

      <div className="mb-4 text-4xl font-black text-white">
        {visibleDecision.toUpperCase()}
      </div>

      <div className="mb-4 grid grid-cols-2 gap-3 text-sm">
        <div className="rounded-xl bg-slate-900/80 p-3">
          <p className="text-slate-400">Confidence</p>
          <p className="font-semibold text-violet-200">{decision?.confidence ?? 0}</p>
        </div>

        <div className="rounded-xl bg-slate-900/80 p-3">
          <p className="text-slate-400">Provider</p>
          <p className="font-semibold text-violet-200">{decision?.provider || "—"}</p>
        </div>
      </div>

      {decision?.error && (
        <p className="mb-3 rounded-xl border border-red-400/30 bg-red-950/40 p-3 text-xs text-red-200">
          {decision.error}
        </p>
      )}

      <div className="flex gap-2">
        <input
          value={symbol}
          onChange={(event) => setSymbol(event.target.value.toUpperCase())}
          className="min-w-0 flex-1 rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white outline-none focus:border-violet-400"
          placeholder="AAPL"
        />

        <button
          onClick={() => void loadDecision(symbol)}
          disabled={loading}
          className="rounded-xl bg-violet-400 px-4 py-2 text-sm font-bold text-slate-950 disabled:opacity-60"
        >
          {loading ? "Loading" : "Update"}
        </button>
      </div>
    </section>
  );
}
'''

if "function StrategyDecisionCard()" not in page_text:
    page_text = page_text.replace("export default", component + "\n\nexport default")

if "<StrategyDecisionCard />" not in page_text:
    page_text = page_text.replace("<LiveMarketWatchlist />", "<LiveMarketWatchlist />\n      <StrategyDecisionCard />", 1)

page.write_text(page_text)

print("patched Phase 14 strategy decision service chain")
