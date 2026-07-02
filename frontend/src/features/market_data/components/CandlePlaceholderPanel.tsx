import { Card, MetricTile } from "../../../components/ui";
import { candlePreviewState } from "../contracts/marketDataUiState";

export function CandlePlaceholderPanel() {
  return (
    <Card>
      <h2>Candle Chart Preview</h2>
      <p className="nv-muted">
        Visual shell for future candle data. Chart data remains locked.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px", marginTop: "14px" }}>
        <MetricTile label="Symbol" value={candlePreviewState.selectedSymbol} />
        <MetricTile label="Interval" value={candlePreviewState.interval} />
        <MetricTile label="Range" value={candlePreviewState.range} />
        <MetricTile label="Data Status" value={candlePreviewState.dataStatus} />
      </div>

      <div style={{ height: "180px", border: "1px dashed var(--panel-soft)", borderRadius: "14px", display: "grid", placeItems: "center", color: "var(--muted)", marginTop: "14px" }}>
        {candlePreviewState.chartStatus}
      </div>
    </Card>
  );
}
