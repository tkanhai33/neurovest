"use client";

import type { PortfolioPosition } from "../../../services/portfolioService";

export default function PositionsPanel({
  positions,
}: {
  positions: PortfolioPosition[];
}) {
  return (
    <section className="mt-6 rounded-2xl border border-cyan-400/30 bg-slate-950/80 p-5 shadow-[0_0_30px_rgba(34,211,238,0.12)]">
      <div className="mb-4">
        <p className="text-xs uppercase tracking-[0.3em] text-cyan-300">
          Portfolio Positions
        </p>

        <h2 className="mt-1 text-2xl font-bold text-white">
          Positions ({positions.length})
        </h2>
      </div>

      {positions.length === 0 ? (
        <div className="rounded-xl bg-slate-900/80 p-4 text-sm text-slate-400">
          No positions available.
        </div>
      ) : (
        <div className="space-y-2">
          {positions.map((position) => (
            <div
              key={String(position.id ?? position.symbol)}
              className="rounded-xl border border-slate-800 bg-slate-900/80 p-4"
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-bold text-white">
                    {position.symbol}
                  </div>

                  <div className="text-sm text-slate-400">
                    Shares: {position.shares_quantity ?? 0}
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-xs text-slate-400">
                    Realized PnL
                  </div>

                  <div className="font-semibold text-cyan-200">
                    {position.realized_pnl ?? 0}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
