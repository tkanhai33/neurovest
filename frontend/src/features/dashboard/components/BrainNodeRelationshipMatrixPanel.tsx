import { Badge, Card } from "../../../components/ui";

const brainNodeRelationships = [
  {
    source: "Market Data",
    target: "Research",
    relationship: "Feeds symbols, quotes, candles, and provider context",
    lockState: "Provider calls locked"
  },
  {
    source: "Research",
    target: "Strategy",
    relationship: "Feeds indicators, screeners, news context, and comparisons",
    lockState: "Research execution locked"
  },
  {
    source: "Strategy",
    target: "Risk",
    relationship: "Feeds signals, candidates, scoring, and lineage",
    lockState: "Signal generation locked"
  },
  {
    source: "Risk",
    target: "Runtime",
    relationship: "Feeds approvals, exposure limits, drawdown state, and trade limits",
    lockState: "Risk math locked"
  },
  {
    source: "Runtime",
    target: "Broker",
    relationship: "Feeds allowed workflow state only after all gates are certified",
    lockState: "Runtime execution locked"
  },
  {
    source: "Broker",
    target: "Paper Trading",
    relationship: "Feeds broker boundary visibility without broker writes",
    lockState: "Broker calls locked"
  },
  {
    source: "Paper Trading",
    target: "Portfolio",
    relationship: "Feeds simulated positions, fills, and PnL after paper engine exists",
    lockState: "Paper engine locked"
  },
  {
    source: "Portfolio",
    target: "Dashboard",
    relationship: "Feeds holdings, allocation, cash, and summary state for user visibility",
    lockState: "Backend reads locked"
  }
] as const;

export function BrainNodeRelationshipMatrixPanel() {
  return (
    <Card>
      <h2>Brain Node Relationship Matrix</h2>

      <p className="nv-muted">
        Static connection matrix for the NeuroVest brain. Relationships are visual only:
        no backend calls, runtime execution, broker calls, AI calls, or trading paths are active.
      </p>

      <div style={{ display: "grid", gap: "10px", marginTop: "14px" }}>
        {brainNodeRelationships.map((edge) => (
          <div key={`${edge.source}-${edge.target}`} className="nv-panel">
            <strong>
              {edge.source} → {edge.target}
            </strong>

            <p className="nv-muted" style={{ margin: "6px 0 10px" }}>
              {edge.relationship}
            </p>

            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
              <Badge label="Visual relationship" />
              <Badge label={edge.lockState} />
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
