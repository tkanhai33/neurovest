import { Card, MetricTile } from "../../../components/ui";
import { lineagePreviewState } from "../contracts/strategyUiState";

export function VersionLineagePlaceholderPanel() {
  return (
    <Card>
      <h2>Version / Lineage Preview</h2>
      <p className="nv-muted">
        Strategy versions, parent lineage, and promotion review are visible but locked.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "12px", marginTop: "14px" }}>
        {lineagePreviewState.map((item) => (
          <MetricTile key={item.label} label={item.label} value={item.value} />
        ))}
      </div>
    </Card>
  );
}
