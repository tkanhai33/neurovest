import { Card, MetricTile } from "../../../components/ui";

export function PaperPnLPlaceholderPanel() {
  return (
    <Card>
      <h2>Paper PnL Placeholder</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Realized PnL" value="Locked" />
        <MetricTile label="Unrealized PnL" value="Locked" />
        <MetricTile label="Currency" value="CAD" />
      </div>
    </Card>
  );
}
