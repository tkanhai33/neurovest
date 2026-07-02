import { frontendRoutes } from "../lib/routes/routeRegistry";

export function Sidebar() {
  return (
    <aside style={{ background: "var(--panel)", padding: "24px", borderRight: "1px solid var(--panel-soft)" }}>
      <h1 style={{ marginTop: 0 }}>NeuroVest</h1>
      <p style={{ color: "var(--muted)" }}>Skeleton UI</p>
      <nav style={{ display: "grid", gap: "10px" }}>
        {frontendRoutes.map((route) => (
          <div key={route.key} style={{ color: "var(--text)" }}>
            {route.label} {route.locked ? "🔒" : ""}
          </div>
        ))}
      </nav>
    </aside>
  );
}
