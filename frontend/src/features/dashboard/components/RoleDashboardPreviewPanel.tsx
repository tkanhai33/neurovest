import { Badge, Card } from "../../../components/ui";
import { dashboardPermissions, userRoles } from "../../../lib/auth";
import { frontendRoutes } from "../../../lib/routes/routeRegistry";

export function RoleDashboardPreviewPanel() {
  return (
    <Card>
      <h2>Role Dashboard Layout Preview</h2>
      <p className="nv-muted">
        Static preview of future dashboard layouts. No auth enforcement, backend calls, route hiding, or runtime execution is active.
      </p>

      <div style={{ display: "grid", gap: "12px", marginTop: "14px" }}>
        {userRoles.map((role) => {
          const visibleRoutes = frontendRoutes.filter((route) =>
            dashboardPermissions[route.key].includes(role.role)
          );

          return (
            <div key={role.role} className="nv-panel">
              <strong>{role.label} Dashboard Preview</strong>
              <p className="nv-muted" style={{ margin: "6px 0 10px" }}>
                {role.description}
              </p>

              <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                {visibleRoutes.map((route) => (
                  <Badge key={`${role.role}-${route.key}`} label={route.label} />
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
