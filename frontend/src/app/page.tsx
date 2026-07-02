import { FeatureCard } from "../components/FeatureCard";
import { AppShell } from "../layouts/AppShell";

const features = [
  "Market Data",
  "Portfolio",
  "Research",
  "Strategy",
  "Risk",
  "Paper Trading",
  "Broker Integration",
  "Runtime",
  "Neuro Chat"
];

export default function HomePage() {
  return (
    <AppShell>
      <h1>NeuroVest Dashboard</h1>
      <p style={{ color: "var(--muted)" }}>
        Phase 13 frontend skeleton. All business logic, broker calls, AI calls, and runtime execution are locked.
      </p>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px" }}>
        {features.map((feature) => (
          <FeatureCard key={feature} title={feature} status="Skeleton only — locked" />
        ))}
      </div>
    </AppShell>
  );
}
