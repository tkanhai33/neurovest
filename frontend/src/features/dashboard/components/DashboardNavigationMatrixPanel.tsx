import { Badge, Card } from "../../../components/ui";
import { dashboardPermissions, userRoles } from "../../../lib/auth";
import { frontendRoutes } from "../../../lib/routes/routeRegistry";

export function DashboardNavigationMatrixPanel() {
  return (
    <Card>
      <h2>Dashboard Navigation Matrix</h2>

      <p className="nv-muted">
        Static role-to-route matrix. This does not enforce permissions,
        hide routes, authenticate users, or call the backend.
      </p>

      <div
        style={{
          display: "grid",
          gap: "12px",
          marginTop: "14px"
        }}
      >
        {userRoles.map((role) => {
          const visibleRoutes = frontendRoutes.filter((route) =>
            dashboardPermissions[route.key].includes(role.role)
          );

          const hiddenRoutes = frontendRoutes.filter(
            (route) => !dashboardPermissions[route.key].includes(role.role)
          );

          return (
            <div key={role.role} className="nv-panel">
              <strong>{role.label} Navigation Matrix</strong>

              <p className="nv-muted" style={{ margin: "6px 0 10px" }}>
                Visibility preview only. Real role enforcement remains locked.
              </p>

              <div style={{ display: "grid", gap: "10px" }}>
                <div>
                  <strong>Visible Preview</strong>
                  <div
                    style={{
                      display: "flex",
                      flexWrap: "wrap",
                      gap: "6px",
                      marginTop: "8px"
                    }}
                  >
                    {visibleRoutes.map((route) => (
                      <Badge
                        key={`${role.role}-visible-${route.key}`}
                        label={route.label}
                      />
                    ))}
                  </div>
                </div>

                <div>
                  <strong>Hidden Later</strong>
                  <div
                    style={{
                      display: "flex",
                      flexWrap: "wrap",
                      gap: "6px",
                      marginTop: "8px"
                    }}
                  >
                    {hiddenRoutes.length === 0 ? (
                      <Badge label="None" />
                    ) : (
                      hiddenRoutes.map((route) => (
                        <Badge
                          key={`${role.role}-hidden-${route.key}`}
                          label={route.label}
                        />
                      ))
                    )}
                  </div>
                </div>

                <div>
                  <strong>Current Enforcement</strong>
                  <div
                    style={{
                      display: "flex",
                      flexWrap: "wrap",
                      gap: "6px",
                      marginTop: "8px"
                    }}
                  >
                    <Badge label="Preview only" />
                    <Badge label="No auth enforcement" />
                    <Badge label="No backend calls" />
                    <Badge label="No route hiding" />
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
