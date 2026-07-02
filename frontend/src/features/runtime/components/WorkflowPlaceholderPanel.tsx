import { Badge, Card } from "../../../components/ui";
import { workflowPreviewState } from "../contracts/runtimeUiState";

export function WorkflowPlaceholderPanel() {
  return (
    <Card>
      <h2>Workflow Preview</h2>
      <p className="nv-muted">
        Workflow chain is shown only as a static visual path. Nothing executes.
      </p>

      <div style={{ display: "grid", gap: "10px", marginTop: "14px" }}>
        {workflowPreviewState.map((item) => (
          <div key={item.step} className="nv-panel">
            <strong>{item.step}</strong>
            <div style={{ marginTop: "8px" }}>
              <Badge label={item.status} />
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
