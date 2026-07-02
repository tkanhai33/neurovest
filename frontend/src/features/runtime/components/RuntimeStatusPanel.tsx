import { Card, MetricTile } from "../../../components/ui";

export function RuntimeStatusPanel() {
  return (
    <Card>
      <h2>Runtime Status</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Runtime" value="Locked" />
        <MetricTile label="Scheduler" value="Disabled" />
        <MetricTile label="Loops" value="Disabled" />
      </div>
    </Card>
  );
}
