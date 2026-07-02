import { Card, MetricTile } from "../../../components/ui";

export function QuotePlaceholderPanel() {
  return (
    <Card>
      <h2>Quote Placeholder</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Last Price" value="Locked" />
        <MetricTile label="Currency" value="CAD" />
        <MetricTile label="Provider" value="Disabled" />
        <MetricTile label="Freshness" value="No Calls" />
      </div>
    </Card>
  );
}
