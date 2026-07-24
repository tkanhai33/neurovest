import type {
  ReactNode,
} from "react";

import AppShell from "../../components/app-shell/AppShell";

export default function UserLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <AppShell workspace="user">
      {children}
    </AppShell>
  );
}
