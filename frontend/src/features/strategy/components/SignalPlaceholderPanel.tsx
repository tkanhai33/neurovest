import { Card, MetricTile } from "../../../components/ui";
import { signalPreviewState } from "../contracts/strategyUiState";

export function SignalPlaceholderPanel() {
  return (
    <Card>
      <h2>Signal Preview</h2>
      <p className="nv-muted">
        Signal layout is ready, but no scoring or strategy generation is performed.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px", marginTop: "14px" }}>
        <MetricTile label="Symbol" value={signalPreviewState.symbol} />
        <MetricTile label="Direction" value={signalPreviewState.direction} />
        <MetricTile label="Confidence" value={signalPreviewState.confidence} />
        <MetricTile label="Strategy Family" value={signalPreviewState.strategyFamily} />
        <MetricTile label="Risk Linked" value={signalPreviewState.riskLinked} />
      </div>
    </Card>
  );
}
