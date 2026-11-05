"use client";

import type {
  ReactNode,
} from "react";

import {
  usePathname,
} from "next/navigation";

import AppShell from "../../components/app-shell/AppShell";

type UserAppShellProps = {
  children: ReactNode;
};

export default function UserAppShell({
  children,
}: UserAppShellProps) {
  const pathname =
    usePathname();

  const showContextBar =
    pathname !==
    "/user/dashboard";

  return (
    <AppShell
      workspace="user"
      showContextBar={showContextBar}
    >
      {children}
    </AppShell>
  );
}
