import { Sidebar } from "../components/Sidebar";
import { TopStatusBar } from "../components/TopStatusBar";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <main style={{ display: "grid", gridTemplateColumns: "260px 1fr", minHeight: "100vh" }}>
      <Sidebar />
      <section>
        <TopStatusBar />
        <div style={{ padding: "24px" }}>{children}</div>
      </section>
    </main>
  );
}
