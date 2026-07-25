import type {
  ReactNode,
} from "react";

import AppShell from "../../components/app-shell/AppShell";

export default function DeveloperDashboardLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <AppShell workspace="developer">
      {children}
    </AppShell>
  );
}
