import { Badge, Card } from "../../../components/ui";

const brainLockStates = [
  {
    node: "Market Data",
    lockState: "Provider locked",
    reason: "No yfinance, Finnhub, backend, or live quote calls are active"
  },
  {
    node: "Research",
    lockState: "Research locked",
    reason: "No indicators, screeners, news calls, backtests, or AI summaries execute"
  },
  {
    node: "Strategy",
    lockState: "Strategy locked",
    reason: "No signal generation, scoring, candidate promotion, or lineage mutation runs"
  },
  {
    node: "Risk",
    lockState: "Risk locked",
    reason: "No exposure math, drawdown math, approvals, or position sizing executes"
  },
  {
    node: "Runtime",
    lockState: "Runtime locked",
    reason: "No scheduler, workflows, background loops, or mutation systems execute"
  },
  {
    node: "Broker",
    lockState: "Broker locked",
    reason: "No SnapTrade auth, account sync, broker reads, orders, or live trading paths run"
  },
  {
    node: "Paper Trading",
    lockState: "Paper engine locked",
    reason: "No simulated orders, fills, positions, or PnL calculations execute"
  },
  {
    node: "Portfolio",
    lockState: "Backend reads locked",
    reason: "No holdings, balances, allocations, or account reads are requested"
  },
  {
    node: "AI Chat",
    lockState: "AI calls locked",
    reason: "No model calls are required by the dashboard brain visualization"
  },
  {
    node: "Role Navigation",
    lockState: "Preview only",
    reason: "No backend auth, route protection, hidden-route enforcement, or permission writes are active"
  }
] as const;

export function BrainLockStateOverlayPanel() {
  return (
    <Card>
      <h2>Brain Lock State Overlay</h2>

      <p className="nv-muted">
        Static lock overlay for the NeuroVest brain. This shows why each system node remains safe before backend,
        runtime, broker, AI, or trading integration is enabled.
      </p>

      <div style={{ display: "grid", gap: "10px", marginTop: "14px" }}>
        {brainLockStates.map((item) => (
          <div key={item.node} className="nv-panel">
            <strong>{item.node}</strong>

            <p className="nv-muted" style={{ margin: "6px 0 10px" }}>
              {item.reason}
            </p>

            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
              <Badge label={item.lockState} />
              <Badge label="Static safety overlay" />
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
