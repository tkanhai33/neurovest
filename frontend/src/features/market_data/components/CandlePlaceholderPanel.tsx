import { Card } from "../../../components/ui";

export function CandlePlaceholderPanel() {
  return (
    <Card>
      <h2>Candle Chart Placeholder</h2>
      <div style={{ height: "180px", border: "1px dashed var(--panel-soft)", borderRadius: "14px", display: "grid", placeItems: "center", color: "var(--muted)" }}>
        Chart locked during skeleton phase
      </div>
    </Card>
  );
}
