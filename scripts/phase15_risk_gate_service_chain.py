#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()

# 15A backend risk service facade
service = ROOT / "backend/app/stacks/risk/risk_service.py"
service.write_text(r'''from backend.app.stacks.risk.drawdown_guard import healthcheck as drawdown_healthcheck


async def get_risk_gate_for_api(symbol: str):
    clean_symbol = symbol.strip().upper()

    if not clean_symbol:
        return {
            "status": "error",
            "symbol": clean_symbol,
            "allowed": False,
            "gate": "risk",
            "provider": "risk_service",
            "error": "missing_symbol",
        }

    try:
        drawdown = drawdown_healthcheck(100000)

        if hasattr(drawdown, "__await__"):
            drawdown = await drawdown

        return {
            "status": "ok",
            "symbol": clean_symbol,
            "allowed": True,
            "gate": "risk",
            "provider": "risk_service",
            "drawdown_guard": drawdown,
        }

    except Exception as e:
        return {
            "status": "error",
            "symbol": clean_symbol,
            "allowed": False,
            "gate": "risk",
            "provider": "risk_service",
            "error": f"{type(e).__name__}: {e}",
        }
''')

# 15B FastAPI route uses risk service
main = ROOT / "backend/app/main.py"
main_text = main.read_text()

import_line = "from backend.app.stacks.risk.risk_service import get_risk_gate_for_api\n"
if import_line not in main_text:
    main_text = import_line + main_text

route = r'''

@app.get("/api/v1/risk/gate/{symbol}")
async def api_risk_gate(symbol: str):
    return await get_risk_gate_for_api(symbol)
'''

if '"/api/v1/risk/gate/{symbol}"' not in main_text:
    main_text += route

main.write_text(main_text)

# 15C frontend riskService.ts
services_dir = ROOT / "frontend/services"
services_dir.mkdir(parents=True, exist_ok=True)

risk_service = services_dir / "riskService.ts"
risk_service.write_text(r'''export type RiskGate = {
  status?: string;
  symbol: string;
  allowed?: boolean;
  gate?: string;
  provider?: string;
  error?: string;
};

export async function getRiskGate(symbol: string): Promise<RiskGate> {
  const cleanSymbol = symbol.trim().toUpperCase();

  if (!cleanSymbol) {
    return {
      status: "error",
      symbol: cleanSymbol,
      allowed: false,
      gate: "risk",
      provider: "frontend_risk_service",
      error: "missing_symbol",
    };
  }

  const response = await fetch(`/api/v1/risk/gate/${cleanSymbol}`, {
    cache: "no-store",
  });

  return await response.json();
}
''')

# 15D Next proxy route
route_dir = ROOT / "frontend/app/api/v1/risk/gate/[symbol]"
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
        allowed: false,
        gate: "risk",
        provider: "next_proxy",
        error: "missing_symbol",
      },
      { status: 400 }
    );
  }

  try {
    const response = await fetch(
      `http://127.0.0.1:8000/api/v1/risk/gate/${encodeURIComponent(cleanSymbol)}`,
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
        allowed: false,
        gate: "risk",
        provider: "next_proxy",
        error: String(error),
      },
      { status: 502 }
    );
  }
}
''')

# 15E frontend risk gate card
page = ROOT / "frontend/app/page.tsx"
page_text = page.read_text()

if 'from "../services/riskService"' not in page_text:
    page_text = page_text.replace(
        'import { getStrategyDecision, type StrategyDecision } from "../services/strategyService";',
        'import { getStrategyDecision, type StrategyDecision } from "../services/strategyService";\nimport { getRiskGate, type RiskGate } from "../services/riskService";'
    )

component = r'''
function RiskGateCard() {
  const [symbol, setSymbol] = useState("AAPL");
  const [riskGate, setRiskGate] = useState<RiskGate | null>(null);
  const [loading, setLoading] = useState(false);

  const loadRiskGate = useCallback(async (nextSymbol = symbol) => {
    const cleanSymbol = nextSymbol.trim().toUpperCase();

    if (!cleanSymbol) return;

    setLoading(true);

    try {
      const data = await getRiskGate(cleanSymbol);
      setRiskGate(data);
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  useEffect(() => {
    const firstLoad = setTimeout(() => {
      void loadRiskGate(symbol);
    }, 0);

    const timer = setInterval(() => {
      void loadRiskGate(symbol);
    }, 30000);

    return () => {
      clearTimeout(firstLoad);
      clearInterval(timer);
    };
  }, [loadRiskGate, symbol]);

  return (
    <section className="mt-6 rounded-2xl border border-emerald-400/30 bg-slate-950/80 p-5 shadow-[0_0_30px_rgba(52,211,153,0.12)]">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-emerald-300">Risk Gate</p>
          <h2 className="mt-1 text-2xl font-bold text-white">{riskGate?.symbol || symbol}</h2>
        </div>

        <div className="rounded-full border border-emerald-400/30 px-3 py-1 text-xs text-emerald-200">
          {riskGate?.status || "idle"}
        </div>
      </div>

      <div className="mb-4 text-4xl font-black text-white">
        {riskGate?.allowed ? "ALLOWED" : "BLOCKED"}
      </div>

      <div className="mb-4 grid grid-cols-2 gap-3 text-sm">
        <div className="rounded-xl bg-slate-900/80 p-3">
          <p className="text-slate-400">Gate</p>
          <p className="font-semibold text-emerald-200">{riskGate?.gate || "risk"}</p>
        </div>

        <div className="rounded-xl bg-slate-900/80 p-3">
          <p className="text-slate-400">Provider</p>
          <p className="font-semibold text-emerald-200">{riskGate?.provider || "—"}</p>
        </div>
      </div>

      {riskGate?.error && (
        <p className="mb-3 rounded-xl border border-red-400/30 bg-red-950/40 p-3 text-xs text-red-200">
          {riskGate.error}
        </p>
      )}

      <div className="flex gap-2">
        <input
          value={symbol}
          onChange={(event) => setSymbol(event.target.value.toUpperCase())}
          className="min-w-0 flex-1 rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white outline-none focus:border-emerald-400"
          placeholder="AAPL"
        />

        <button
          onClick={() => void loadRiskGate(symbol)}
          disabled={loading}
          className="rounded-xl bg-emerald-400 px-4 py-2 text-sm font-bold text-slate-950 disabled:opacity-60"
        >
          {loading ? "Loading" : "Update"}
        </button>
      </div>
    </section>
  );
}
'''

if "function RiskGateCard()" not in page_text:
    page_text = page_text.replace("export default", component + "\n\nexport default")

if "<RiskGateCard />" not in page_text:
    page_text = page_text.replace("<StrategyDecisionCard />", "<StrategyDecisionCard />\n      <RiskGateCard />", 1)

page.write_text(page_text)

print("patched Phase 15 risk gate service chain")
