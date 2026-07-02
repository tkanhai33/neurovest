import { Card } from "../../../components/ui";

export function EventLogPlaceholderPanel() {
  return (
    <Card>
      <h2>Event Log Placeholder</h2>
      <div style={{ height: "140px", border: "1px dashed var(--panel-soft)", borderRadius: "14px", display: "grid", placeItems: "center", color: "var(--muted)" }}>
        Runtime events unavailable until implementation phase
      </div>
    </Card>
  );
}
