import { Card, MetricTile } from "../../../components/ui";

export function PaperAccountPlaceholderPanel() {
  return (
    <Card>
      <h2>Paper Account</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Account" value="Placeholder" />
        <MetricTile label="Currency" value="CAD" />
        <MetricTile label="Starting Cash" value="Locked" />
      </div>
    </Card>
  );
}
