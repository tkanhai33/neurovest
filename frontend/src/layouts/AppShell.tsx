import { Sidebar } from "../components/Sidebar";
import { TopStatusBar } from "../components/TopStatusBar";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <main className="nv-shell">
      <Sidebar />
      <section className="nv-main">
        <TopStatusBar />
        <div className="nv-content">{children}</div>
      </section>
    </main>
  );
}
