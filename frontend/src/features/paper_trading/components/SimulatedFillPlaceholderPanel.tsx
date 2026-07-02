import { Card } from "../../../components/ui";

export function SimulatedFillPlaceholderPanel() {
  return (
    <Card>
      <h2>Simulated Fill Placeholder</h2>
      <div style={{ height: "140px", border: "1px dashed var(--panel-soft)", borderRadius: "14px", display: "grid", placeItems: "center", color: "var(--muted)" }}>
        Fill engine locked during skeleton phase
      </div>
    </Card>
  );
}
