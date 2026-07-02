import { Badge, Card } from "../../../components/ui";
import { dashboardPermissions, userRoles } from "../../../lib/auth";
import { frontendRoutes } from "../../../lib/routes/routeRegistry";

export function RoleVisibilityPreviewPanel() {
  return (
    <Card>
      <h2>Role Visibility Preview</h2>
      <p className="nv-muted">
        Static dashboard visibility preview. No auth enforcement, backend login, route hiding, or permission execution is active.
      </p>

      <div style={{ display: "grid", gap: "12px", marginTop: "14px" }}>
        {userRoles.map((role) => {
          const visibleRoutes = frontendRoutes.filter((route) =>
            dashboardPermissions[route.key].includes(role.role)
          );

          return (
            <div key={role.role} className="nv-panel">
              <strong>{role.label}</strong>
              <p className="nv-muted" style={{ margin: "6px 0 10px" }}>
                {role.description}
              </p>

              <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                {visibleRoutes.map((route) => (
                  <Badge key={route.key} label={route.label} />
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
