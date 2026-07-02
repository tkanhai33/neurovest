import { Badge, Card } from "../../../components/ui";
import { dashboardPermissions, currentRolePreviewState } from "../../../lib/auth";
import { frontendRoutes } from "../../../lib/routes/routeRegistry";
import { featureIntegrationState } from "../../../lib/integration/featureIntegrationRegistry";
import { roleAwareNavigationState } from "../../../lib/routes/navigationState";

const adminSurfaces = [
  "Risk Oversight",
  "Broker Visibility",
  "System Lock State",
  "Strategy Review",
  "Admin Controls",
  "Operational Monitoring"
] as const;

export function AdminDashboardCompositionPanel() {
  const adminRoutes = frontendRoutes.filter((route) =>
    dashboardPermissions[route.key].includes("admin")
  );

  return (
    <Card>
      <h2>Admin Dashboard Composition</h2>

      <p className="nv-muted">
        Admin cockpit preview only. No backend operations, broker actions,
        runtime controls, auth enforcement, or privileged writes are active.
      </p>

      <div style={{ display: "grid", gap: "12px", marginTop: "14px" }}>
        <div className="nv-panel">
          <strong>Admin Role Preview</strong>
          <p className="nv-muted" style={{ margin: "6px 0 10px" }}>
            Current shell preview role remains {currentRolePreviewState.currentRole}.
            Admin visibility is represented as static composition only.
          </p>

          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
            <Badge label="Preview only" />
            <Badge label="No admin enforcement" />
            <Badge label="No backend auth" />
            <Badge label="No privileged writes" />
          </div>
        </div>

        <div className="nv-panel">
          <strong>Admin Surfaces</strong>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginTop: "10px" }}>
            {adminSurfaces.map((surface) => (
              <Badge key={surface} label={surface} />
            ))}
          </div>
        </div>

        <div className="nv-panel">
          <strong>Visible Admin Routes</strong>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginTop: "10px" }}>
            {adminRoutes.map((route) => (
              <Badge key={route.key} label={route.label} />
            ))}
          </div>
        </div>

        <div className="nv-panel">
          <strong>Admin Lock State</strong>
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
