import { Card, MetricTile } from "../../../components/ui";
import { screenerPreviewState } from "../contracts/researchUiState";

export function ScreenerPlaceholderPanel() {
  return (
    <Card>
      <h2>Screener Preview</h2>
      <p className="nv-muted">
        Screener buckets are visual only until research services are certified.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px", marginTop: "14px" }}>
        {screenerPreviewState.map((bucket) => (
          <MetricTile key={bucket.label} label={bucket.label} value={bucket.value} />
        ))}
      </div>

      <div style={{ height: "120px", border: "1px dashed var(--panel-soft)", borderRadius: "14px", display: "grid", placeItems: "center", color: "var(--muted)", marginTop: "14px" }}>
        Screener execution locked
      </div>
    </Card>
  );
}
