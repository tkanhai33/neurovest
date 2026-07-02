import { Card, StatusPill } from "../../../components/ui";

export function DashboardHeroPanel() {
  return (
    <Card>
      <div style={{ display: "grid", gap: "14px" }}>
        <div>
          <h1 style={{ margin: 0 }}>NeuroVest Command Center</h1>
          <p className="nv-muted">
            Certified static frontend shell. Backend, provider, AI, runtime, broker, and trading paths remain locked.
          </p>
        </div>
        <div>
          <StatusPill label="Frontend Certified" />
          <StatusPill label="Runtime Locked" />
          <StatusPill label="Broker Locked" />
          <StatusPill label="Trading Locked" />
        </div>
      </div>
    </Card>
  );
}
