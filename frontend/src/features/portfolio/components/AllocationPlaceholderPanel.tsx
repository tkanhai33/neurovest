import { Card } from "../../../components/ui";

export function AllocationPlaceholderPanel() {
  return (
    <Card>
      <h2>Allocation Placeholder</h2>
      <div style={{ height: "180px", border: "1px dashed var(--panel-soft)", borderRadius: "14px", display: "grid", placeItems: "center", color: "var(--muted)" }}>
        Allocation chart locked during skeleton phase
      </div>
    </Card>
  );
}
