import { Card } from "../../../components/ui";

export function PaperPositionPlaceholderPanel() {
  return (
    <Card>
      <h2>Paper Position Placeholder</h2>
      <div style={{ height: "140px", border: "1px dashed var(--panel-soft)", borderRadius: "14px", display: "grid", placeItems: "center", color: "var(--muted)" }}>
        Position mutation locked
      </div>
    </Card>
  );
}
