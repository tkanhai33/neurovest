import { Card, MetricTile } from "../../../components/ui";

export function IndicatorPlaceholderPanel() {
  return (
    <Card>
      <h2>Indicator Placeholder</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px" }}>
        <MetricTile label="RSI" value="Locked" />
        <MetricTile label="MACD" value="Locked" />
        <MetricTile label="EMA" value="Locked" />
        <MetricTile label="ATR" value="Locked" />
      </div>
    </Card>
  );
}
