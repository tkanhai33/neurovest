import { Card, MetricTile } from "../../../components/ui";

export function PhaseProgressPanel() {
  return (
    <Card>
      <h2>Phase Progress</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Backend" value="Certified" />
        <MetricTile label="Frontend" value="Skeleton" />
        <MetricTile label="Tests" value="85 Passing" />
        <MetricTile label="Trading" value="Locked" />
      </div>
    </Card>
  );
}
