import { Card, MetricTile } from "../../../components/ui";

export function DailyLimitPlaceholderPanel() {
  return (
    <Card>
      <h2>Daily Trade Limits</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="Max Trades" value="10" />
        <MetricTile label="Used Today" value="Locked" />
        <MetricTile label="Remaining" value="Disabled" />
      </div>
    </Card>
  );
}
