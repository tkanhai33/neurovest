import type {
  ReactNode,
} from "react";

import UserAppShell from "./UserAppShell";

export default function UserLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <UserAppShell>
      {children}
    </UserAppShell>
  );
}
