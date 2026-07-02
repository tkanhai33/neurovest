import { Card, MetricTile } from "../../../components/ui";
import { exposurePreviewState } from "../contracts/riskUiState";

export function ExposurePlaceholderPanel() {
  return (
    <Card>
      <h2>Exposure Preview</h2>
      <p className="nv-muted">
        Exposure layout is ready, but no portfolio, broker, or risk calculations are performed.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px", marginTop: "14px" }}>
        {exposurePreviewState.map((item) => (
          <MetricTile key={item.label} label={item.label} value={item.value} />
        ))}
      </div>
    </Card>
  );
}
