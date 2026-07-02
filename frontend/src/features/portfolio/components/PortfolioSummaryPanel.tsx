import { Card, MetricTile } from "../../../components/ui";

export function PortfolioSummaryPanel() {
  return (
    <Card>
      <h2>Portfolio Summary</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Total Value" value="Locked" />
        <MetricTile label="Cash" value="Locked" />
        <MetricTile label="Holdings" value="Placeholder" />
        <MetricTile label="PnL" value="Locked" />
      </div>
    </Card>
  );
}
