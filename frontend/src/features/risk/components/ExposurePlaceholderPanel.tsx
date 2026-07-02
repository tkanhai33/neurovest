import { Card, MetricTile } from "../../../components/ui";

export function ExposurePlaceholderPanel() {
  return (
    <Card>
      <h2>Exposure Placeholder</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Portfolio Exposure" value="Locked" />
        <MetricTile label="Sector Exposure" value="Locked" />
        <MetricTile label="Symbol Exposure" value="Locked" />
      </div>
    </Card>
  );
}
