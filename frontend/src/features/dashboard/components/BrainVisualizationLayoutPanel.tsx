import { Badge, Card } from "../../../components/ui";

const brainFlowNodes = [
  { name: "Market Data", role: "Quotes, providers, symbols, candles", state: "Visual only" },
  { name: "Research", role: "Indicators, screeners, news, comparisons", state: "Visual only" },
  { name: "Strategy", role: "Signals, candidates, scoring, lineage", state: "Visual only" },
  { name: "Risk", role: "Exposure, drawdown, limits, approvals", state: "Visual only" },
  { name: "Runtime", role: "Scheduler, workflows, event log, mutation locks", state: "Locked" },
  { name: "Broker", role: "SnapTrade boundary and order locks", state: "Locked" },
  { name: "Paper Trading", role: "Simulated orders, fills, positions, PnL", state: "Locked" },
  { name: "Portfolio", role: "Holdings, cash, allocation, account summary", state: "Visual only" }
] as const;

export function BrainVisualizationLayoutPanel() {
  return (
    <Card>
      <h2>Brain Visualization Layout</h2>

      <p className="nv-muted">
        Top-down NeuroVest brain visualization foundation. This is a static layout only:
        no backend calls, runtime execution, broker calls, AI calls, or trading paths are active.
      </p>

      <div
        style={{
          display: "grid",
          gap: "10px",
          marginTop: "14px"
        }}
      >
        {brainFlowNodes.map((node, index) => (
          <div key={node.name} className="nv-panel">
            <strong>
              {index + 1}. {node.name}
            </strong>

            <p className="nv-muted" style={{ margin: "6px 0 10px" }}>
              {node.role}
            </p>

            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
              <Badge label={node.state} />
              <Badge label={index === 0 ? "Input layer" : "Downstream layer"} />
              {index < brainFlowNodes.length - 1 ? (
                <Badge label={`Feeds ${brainFlowNodes[index + 1].name}`} />
              ) : (
                <Badge label="Terminal view" />
              )}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
