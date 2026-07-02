import { Card, MetricTile } from "../../../components/ui";
import { runtimeStatusPreviewState } from "../contracts/runtimeUiState";

export function RuntimeStatusPanel() {
  return (
    <Card>
      <h2>Runtime Status</h2>
      <p className="nv-muted">
        Runtime readiness is displayed as static contract state only.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px", marginTop: "14px" }}>
        {runtimeStatusPreviewState.map((item) => (
          <MetricTile key={item.label} label={item.label} value={item.value} />
        ))}
      </div>
    </Card>
  );
}
