import { Card, MetricTile } from "../../../components/ui";
import { indicatorPreviewState } from "../contracts/researchUiState";

export function IndicatorPlaceholderPanel() {
  return (
    <Card>
      <h2>Indicator Preview</h2>
      <p className="nv-muted">
        Indicator layout is ready, but no calculations or market data calls are made.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px", marginTop: "14px" }}>
        {indicatorPreviewState.map((indicator) => (
          <MetricTile key={indicator.label} label={indicator.label} value={indicator.value} />
        ))}
      </div>
    </Card>
  );
}
