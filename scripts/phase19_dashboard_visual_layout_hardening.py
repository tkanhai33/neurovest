#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()
PAGE = ROOT / "frontend/app/page.tsx"

text = PAGE.read_text()

text = text.replace(
'''  return (
    <main style={{
      background: "#050816",
      color: "white",
      minHeight: "100vh",
      padding: 24,
      fontFamily: "monospace"
    }}>

      <h1>Neurovest Dashboard</h1>

      <section style={{
        display: "grid",
        gridTemplateColumns: "repeat(4, 1fr)",
        gap: 12,
        marginTop: 20
      }}>
        <div>Trades: {analytics?.total_trades_logged ?? 0}</div>
        <div>Buys: {analytics?.buy_signals_count ?? 0}</div>
        <div>Sells: {analytics?.sell_signals_count ?? 0}</div>
        <div>Success: {analytics?.execution_success_percentage ?? 0}%</div>
      </section>

      <PositionsPanel positions={positions} />
          <LivePriceCard />
      <LiveMarketWatchlist />
      <StrategyDecisionCard />
      <RiskGateCard />
    </main>
  );''',
'''  return (
    <main className="min-h-screen bg-[#050816] px-6 py-6 font-mono text-white">
      <section className="mb-8 rounded-3xl border border-cyan-400/20 bg-slate-950/80 p-6 shadow-[0_0_60px_rgba(34,211,238,0.10)]">
        <p className="text-xs uppercase tracking-[0.4em] text-cyan-300">
          Neurovest V3
        </p>

        <h1 className="mt-2 text-4xl font-black tracking-tight text-white">
          Trading Control Dashboard
        </h1>

        <p className="mt-3 max-w-3xl text-sm text-slate-400">
          Live market data, portfolio state, strategy decisions, and risk gates are separated through certified service chains.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-4">
        <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-4">
          <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Trades</p>
          <div className="mt-2 text-3xl font-black text-white">{analytics?.total_trades_logged ?? 0}</div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-4">
          <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Buys</p>
          <div className="mt-2 text-3xl font-black text-emerald-300">{analytics?.buy_signals_count ?? 0}</div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-4">
          <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Sells</p>
          <div className="mt-2 text-3xl font-black text-red-300">{analytics?.sell_signals_count ?? 0}</div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-4">
          <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Success</p>
          <div className="mt-2 text-3xl font-black text-cyan-300">{analytics?.execution_success_percentage ?? 0}%</div>
        </div>
      </section>

      <section className="mt-8 grid gap-6 xl:grid-cols-2">
        <LivePriceCard />
        <StrategyDecisionCard />
      </section>

      <section className="mt-6 grid gap-6 xl:grid-cols-2">
        <RiskGateCard />
        <PositionsPanel positions={positions} />
      </section>

      <LiveMarketWatchlist />
    </main>
  );'''
)

PAGE.write_text(text)
print("patched Phase 19 dashboard visual/layout hardening")
