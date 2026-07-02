import { Card, MetricTile } from "../../../components/ui";

export function SignalPlaceholderPanel() {
  return (
    <Card>
      <h2>Signal Placeholder</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Direction" value="Locked" />
        <MetricTile label="Confidence" value="Disabled" />
        <MetricTile label="Symbol" value="Placeholder" />
      </div>
    </Card>
  );
}
