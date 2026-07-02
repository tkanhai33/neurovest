import { Card } from "../../../components/ui";

export function BacktestPlaceholderPanel() {
  return (
    <Card>
      <h2>Backtest Placeholder</h2>
      <div style={{ height: "140px", border: "1px dashed var(--panel-soft)", borderRadius: "14px", display: "grid", placeItems: "center", color: "var(--muted)" }}>
        Backtest execution locked
      </div>
    </Card>
  );
}
