import type {
  ReactNode,
} from "react";

import AppShell from "../../components/app-shell/AppShell";

export default function AdminLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <AppShell workspace="admin">
      {children}
    </AppShell>
  );
}
