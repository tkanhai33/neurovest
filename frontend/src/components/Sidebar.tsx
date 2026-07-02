import { frontendRoutes } from "../lib/routes/routeRegistry";
import { currentRolePreviewState, getVisibleFrontendRoutesForRole } from "../lib/auth";

export function Sidebar() {
  return (
    <aside className="nv-sidebar">
      <h1 className="nv-brand">NeuroVest</h1>
      <p className="nv-subtitle">Certified skeleton UI</p>
      <nav className="nv-nav nv-nav-section" aria-label="Primary navigation">
        {getVisibleFrontendRoutesForRole(currentRolePreviewState.currentRole, frontendRoutes).map((route) => (
          <div key={route.key} className="nv-nav-item">
            {route.label} {route.locked ? "🔒" : ""}
          </div>
        ))}
      </nav>
    </aside>
  );
}
