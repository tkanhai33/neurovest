import { Card } from "../../../components/ui";

export function ScreenerPlaceholderPanel() {
  return (
    <Card>
      <h2>Screener Placeholder</h2>
      <div style={{ height: "140px", border: "1px dashed var(--panel-soft)", borderRadius: "14px", display: "grid", placeItems: "center", color: "var(--muted)" }}>
        Screener locked during skeleton phase
      </div>
    </Card>
  );
}
