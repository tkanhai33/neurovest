import { Badge, Card } from "../../../components/ui";
import { dashboardPermissions, currentRolePreviewState } from "../../../lib/auth";
import { frontendRoutes } from "../../../lib/routes/routeRegistry";
import { featureIntegrationState } from "../../../lib/integration/featureIntegrationRegistry";
import { roleAwareNavigationState } from "../../../lib/routes/navigationState";

const userSurfaces = [
  "Portfolio View",
  "Market Data View",
  "Research View",
  "Paper Trading Preview",
  "Neuro Chat",
  "Settings"
] as const;

export function UserDashboardCompositionPanel() {
  const userRoutes = frontendRoutes.filter((route) =>
    dashboardPermissions[route.key].includes("user")
  );

  return (
    <Card>
      <h2>User Dashboard Composition</h2>

      <p className="nv-muted">
        User cockpit preview only. No backend portfolio reads, broker actions,
        auth enforcement, runtime execution, or trading paths are active.
      </p>

      <div style={{ display: "grid", gap: "12px", marginTop: "14px" }}>
        <div className="nv-panel">
          <strong>User Role Preview</strong>
          <p className="nv-muted" style={{ margin: "6px 0 10px" }}>
            Current shell preview role remains {currentRolePreviewState.currentRole}.
            User visibility is represented as static composition only.
          </p>

          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
            <Badge label="Preview only" />
            <Badge label="No user auth enforcement" />
            <Badge label="No account reads" />
            <Badge label="No trading" />
          </div>
        </div>

        <div className="nv-panel">
          <strong>User Surfaces</strong>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginTop: "10px" }}>
            {userSurfaces.map((surface) => (
              <Badge key={surface} label={surface} />
            ))}
          </div>
        </div>

        <div className="nv-panel">
          <strong>Visible User Routes</strong>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginTop: "10px" }}>
            {userRoutes.map((route) => (
              <Badge key={route.key} label={route.label} />
            ))}
          </div>
        </div>

        <div className="nv-panel">
          <strong>User Lock State</strong>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginTop: "10px" }}>
            <Badge label={`Integration only: ${featureIntegrationState.integrationOnly ? "true" : "false"}`} />
            <Badge label={`Role preview: ${roleAwareNavigationState.previewOnly ? "true" : "false"}`} />
            <Badge label={`Route hiding: ${roleAwareNavigationState.routeHidingEnabled ? "enabled" : "locked"}`} />
            <Badge label={`Backend auth: ${roleAwareNavigationState.backendAuthEnabled ? "enabled" : "locked"}`} />
            <Badge label={`Enforcement: ${roleAwareNavigationState.enforcementEnabled ? "enabled" : "locked"}`} />
          </div>
        </div>
      </div>
    </Card>
  );
}
