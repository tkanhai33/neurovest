const navItems = [
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
];

export function Sidebar() {
  return (
    <aside style={{ background: "var(--panel)", padding: "24px", borderRight: "1px solid var(--panel-soft)" }}>
      <h1 style={{ marginTop: 0 }}>NeuroVest</h1>
      <p style={{ color: "var(--muted)" }}>Skeleton UI</p>
      <nav style={{ display: "grid", gap: "10px" }}>
        {navItems.map((item) => (
          <div key={item} style={{ color: "var(--text)" }}>{item}</div>
        ))}
      </nav>
    </aside>
  );
}
