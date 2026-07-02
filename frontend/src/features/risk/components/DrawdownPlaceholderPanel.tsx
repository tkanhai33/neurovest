import { Card, MetricTile } from "../../../components/ui";

export function DrawdownPlaceholderPanel() {
  return (
    <Card>
      <h2>Drawdown Placeholder</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Daily Drawdown" value="Locked" />
        <MetricTile label="Soft Limit" value="Disabled" />
        <MetricTile label="Hard Limit" value="Disabled" />
      </div>
    </Card>
  );
}
