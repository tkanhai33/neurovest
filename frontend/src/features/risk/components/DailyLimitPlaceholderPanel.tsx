import { Card, MetricTile } from "../../../components/ui";
import { dailyLimitPreviewState } from "../contracts/riskUiState";

export function DailyLimitPlaceholderPanel() {
  return (
    <Card>
      <h2>Daily Trade Limits</h2>
      <p className="nv-muted">
        Trade limits are visual only. Enforcement remains locked until certified risk logic exists.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px", marginTop: "14px" }}>
        <MetricTile label="Max Trades" value={dailyLimitPreviewState.maxTrades} />
        <MetricTile label="Used Today" value={dailyLimitPreviewState.usedToday} />
        <MetricTile label="Remaining" value={dailyLimitPreviewState.remaining} />
        <MetricTile label="Reset Window" value={dailyLimitPreviewState.resetWindow} />
        <MetricTile label="Enforcement" value={dailyLimitPreviewState.enforcement} />
      </div>
    </Card>
  );
}
