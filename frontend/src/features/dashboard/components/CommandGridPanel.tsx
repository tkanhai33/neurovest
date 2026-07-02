import { Card, MetricTile } from "../../../components/ui";

export function CommandGridPanel() {
  return (
    <Card>
      <h2>Command Grid</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "12px" }}>
        <MetricTile label="Frontend Phases" value="13-30" />
        <MetricTile label="Backend Tests" value="85 Passing" />
        <MetricTile label="UI Surfaces" value="12" />
        <MetricTile label="Execution" value="Locked" />
      </div>
    </Card>
  );
}
