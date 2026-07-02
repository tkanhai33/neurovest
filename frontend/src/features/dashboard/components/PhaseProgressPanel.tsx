import { Card, MetricTile } from "../../../components/ui";

export function PhaseProgressPanel() {
  return (
    <Card>
      <h2>Phase Progress</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Backend Topology" value="Certified" />
        <MetricTile label="Frontend Shell" value="Certified" />
        <MetricTile label="Visual Polish" value="Active" />
        <MetricTile label="API Wiring" value="Forbidden" />
      </div>
    </Card>
  );
}
