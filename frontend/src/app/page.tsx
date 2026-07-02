import { DashboardShell } from "../features/dashboard/components";
import { AppShell } from "../layouts/AppShell";

export default function HomePage() {
  return (
    <AppShell>
      <DashboardShell />
    </AppShell>
  );
}
