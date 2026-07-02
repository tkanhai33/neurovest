import { Card, StatusPill } from "../../../components/ui";

export function SimulatedOrderPlaceholderPanel() {
  return (
    <Card>
      <h2>Simulated Order Shell</h2>
      <StatusPill label="Orders Rejected By Skeleton" />
      <p style={{ color: "var(--muted)" }}>
        Simulated order creation is locked until the paper trading engine is explicitly implemented.
      </p>
    </Card>
  );
}
