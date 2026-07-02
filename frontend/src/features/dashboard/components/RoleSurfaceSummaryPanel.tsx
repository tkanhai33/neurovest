import { Badge, Card } from "../../../components/ui";

const roleSurfaces = [
  {
    role: "User",
    description:
      "Portfolio, market data, research, paper trading, and Neuro chat experience.",
    features: [
      "Market Data",
      "Portfolio",
      "Research",
      "Paper Trading",
      "Neuro Chat"
    ]
  },
  {
    role: "Admin",
    description:
      "Operational oversight including risk, broker visibility, and system monitoring.",
    features: [
      "Market Data",
      "Portfolio",
      "Research",
      "Strategy",
      "Risk",
      "Broker Integration",
      "Admin"
    ]
  },
  {
    role: "Developer",
    description:
      "Complete architecture visibility including runtime, diagnostics, and certification tools.",
    features: [
      "Dashboard",
      "Market Data",
      "Portfolio",
      "Research",
      "Strategy",
      "Risk",
      "Paper Trading",
      "Broker Integration",
      "Runtime",
      "Neuro Chat",
      "Admin",
      "Settings"
    ]
  }
] as const;

export function RoleSurfaceSummaryPanel() {
  return (
    <Card>
      <h2>Dashboard Role Surface Summary</h2>

      <p className="nv-muted">
        Shared dashboard architecture preview only. No authentication,
        authorization, role enforcement, or route filtering is active.
      </p>

      <div
        style={{
          display: "grid",
          gap: "12px",
          marginTop: "14px"
        }}
      >
        {roleSurfaces.map((surface) => (
          <div key={surface.role} className="nv-panel">
            <strong>{surface.role}</strong>

            <p
              className="nv-muted"
              style={{ margin: "6px 0 10px" }}
            >
              {surface.description}
            </p>

            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: "6px"
              }}
            >
              {surface.features.map((feature) => (
                <Badge
                  key={`${surface.role}-${feature}`}
                  label={feature}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
