import { Card } from "../../../components/ui";

export function WorkflowPlaceholderPanel() {
  return (
    <Card>
      <h2>Workflow Placeholder</h2>
      <div style={{ height: "140px", border: "1px dashed var(--panel-soft)", borderRadius: "14px", display: "grid", placeItems: "center", color: "var(--muted)" }}>
        Workflow execution locked during skeleton phase
      </div>
    </Card>
  );
}
