import { Card, MetricTile } from "../../../components/ui";
import { allocationPreviewState } from "../contracts/portfolioUiState";

export function AllocationPlaceholderPanel() {
  return (
    <Card>
      <h2>Allocation Preview</h2>
      <p className="nv-muted">
        Allocation buckets are visual only until holdings data is connected.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px", marginTop: "14px" }}>
        {allocationPreviewState.map((bucket) => (
          <MetricTile key={bucket.label} label={bucket.label} value={bucket.value} />
        ))}
      </div>

      <div style={{ height: "140px", border: "1px dashed var(--panel-soft)", borderRadius: "14px", display: "grid", placeItems: "center", color: "var(--muted)", marginTop: "14px" }}>
        Allocation chart locked during UI composition phase
      </div>
    </Card>
  );
}
