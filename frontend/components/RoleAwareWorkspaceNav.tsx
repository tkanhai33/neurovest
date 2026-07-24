"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

type WorkspaceRole = "dev" | "owner" | "admin" | "user";

type SessionPayload = {
  role?: string;
  user?: {
    role?: string;
  };
  principal?: {
    role?: string;
  };
};

type NavigationItem = {
  href: string;
  label: string;
  description: string;
  minimumRole: "dev" | "admin" | "user";
};

const navigationItems: NavigationItem[] = [
  {
    href: "/dashboard",
    label: "Dev",
    description: "Development dashboard and system tools",
    minimumRole: "dev",
  },
  {
    href: "/admin",
    label: "Admin",
    description: "Users, sessions, access, and support",
    minimumRole: "admin",
  },
  {
    href: "/admin/user-stats",
    label: "User Stats",
    description: "Plans, activity, and account distribution",
    minimumRole: "admin",
  },
  {
    href: "/admin/tickets",
    label: "Tickets",
    description: "Neuro support and user conversations",
    minimumRole: "admin",
  },
  {
    href: "/user/dashboard",
    label: "User",
    description: "Normal customer dashboard experience",
    minimumRole: "user",
  },
  {
    href: "/user/settings",
    label: "Settings",
    description: "Account, security, billing, notifications, and support",
    minimumRole: "user",
  },
];

function normalizeRole(value: unknown): WorkspaceRole {
  const role = String(value ?? "")
    .trim()
    .toLowerCase();

  if (
    role === "dev" ||
    role === "developer" ||
    role === "owner"
  ) {
    return role === "owner" ? "owner" : "dev";
  }

  if (
    role === "admin" ||
    role === "administrator"
  ) {
    return "admin";
  }

  return "user";
}

function canSee(
  role: WorkspaceRole,
  minimumRole: NavigationItem["minimumRole"],
): boolean {
  if (role === "dev" || role === "owner") {
    return true;
  }

  if (role === "admin") {
    return minimumRole !== "dev";
  }

  return minimumRole === "user";
}

export default function RoleAwareWorkspaceNav() {
  const pathname = usePathname();
  const [role, setRole] = useState<WorkspaceRole>("user");
  const [resolved, setResolved] = useState(false);

  useEffect(() => {
    let active = true;

    async function loadSession(): Promise<void> {
      try {
        const response = await fetch("/api/auth/session", {
          method: "GET",
          credentials: "include",
          cache: "no-store",
        });

        if (!response.ok) {
          return;
        }

        const payload = (await response.json()) as SessionPayload;

        const resolvedRole = normalizeRole(
          payload.role ??
            payload.user?.role ??
            payload.principal?.role,
        );

        if (active) {
          setRole(resolvedRole);
        }
      } catch {
        // The current route remains server-authoritative.
        // Navigation failure never grants additional access.
      } finally {
        if (active) {
          setResolved(true);
        }
      }
    }

    void loadSession();

    return () => {
      active = false;
    };
  }, []);

  const visibleItems = useMemo(
    () =>
      navigationItems.filter((item) =>
        canSee(role, item.minimumRole),
      ),
    [role],
  );

  return (
    <nav
      aria-label="NeuroVest workspace navigation"
      className="border-b border-white/10 bg-slate-950/85 px-4 py-3 backdrop-blur-xl"
    >
      <div className="mx-auto flex max-w-[1600px] items-center gap-2 overflow-x-auto">
        <div className="mr-3 shrink-0">
          <p className="text-[10px] font-black uppercase tracking-[0.28em] text-cyan-300">
            Workspace
          </p>
          <p className="text-xs text-slate-500">
            {resolved ? role.toUpperCase() : "LOADING"}
          </p>
        </div>

        {visibleItems.map((item) => {
          const active =
            pathname === item.href ||
            pathname.startsWith(`${item.href}/`);

          return (
            <Link
              key={item.href}
              href={item.href}
              title={item.description}
              className={[
                "shrink-0 rounded-xl border px-4 py-2 text-xs font-black uppercase tracking-[0.12em] transition",
                active
                  ? "border-cyan-300/50 bg-cyan-300/10 text-cyan-200"
                  : "border-white/5 bg-white/[0.025] text-slate-400 hover:border-white/15 hover:text-white",
              ].join(" ")}
            >
              {item.label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
