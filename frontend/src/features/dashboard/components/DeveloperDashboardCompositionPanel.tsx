import { Badge, Card } from "../../../components/ui";
import { frontendRoutes } from "../../../lib/routes/routeRegistry";
import { featureIntegrationState } from "../../../lib/integration/featureIntegrationRegistry";
import { roleAwareNavigationState } from "../../../lib/routes/navigationState";
import { currentRolePreviewState } from "../../../lib/auth";

const developerSurfaces = [
  "Architecture Map",
  "Certification Verifiers",
  "Runtime Visibility",
  "Stack Diagnostics",
  "Role Navigation Preview",
  "System Lock State"
] as const;

export function DeveloperDashboardCompositionPanel() {
  return (
    <Card>
      <h2>Developer Dashboard Composition</h2>

      <p className="nv-muted">
        Developer cockpit preview only. No backend diagnostics, runtime execution,
        mutation, broker calls, or privileged enforcement is active.
      </p>

      <div style={{ display: "grid", gap: "12px", marginTop: "14px" }}>
        <div className="nv-panel">
          <strong>Developer Role Preview</strong>
          <p className="nv-muted" style={{ margin: "6px 0 10px" }}>
            Current preview role: {currentRolePreviewState.currentRole}
          </p>

          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
            <Badge label="Preview only" />
            <Badge label="No auth enforcement" />
            <Badge label="No backend auth" />
            <Badge label="No route protection" />
          </div>
        </div>

        <div className="nv-panel">
          <strong>Developer Surfaces</strong>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginTop: "10px" }}>
            {developerSurfaces.map((surface) => (
              <Badge key={surface} label={surface} />
            ))}
          </div>
        </div>

        <div className="nv-panel">
          <strong>Visible Developer Routes</strong>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginTop: "10px" }}>
            {frontendRoutes.map((route) => (
              <Badge key={route.key} label={route.label} />
            ))}
          </div>
        </div>

        <div className="nv-panel">
          <strong>Lock State</strong>
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
