import Link from "next/link";

import PageHeader from "../../components/app-shell/PageHeader";

import {
  Panel,
  StatusBadge,
} from "../../components/ui";

type AdminWorkspaceCard = {
  title: string;
  description: string;
  href: string;
  status: string;
  tone:
    | "info"
    | "success"
    | "warning"
    | "violet";
  capability: string;
};

const workspaces:
  AdminWorkspaceCard[] = [
    {
      title: "User Management",
      description:
        "Inspect canonical identities, control account access, require password changes, issue temporary credentials, and close accounts.",
      href: "/admin/users",
      status: "Operational",
      tone: "success",
      capability: "Database-backed",
    },
    {
      title: "Session Administration",
      description:
        "Review authenticated session state, identify active access, and manage session revocation workflows.",
      href: "/admin/sessions",
      status: "Restricted",
      tone: "warning",
      capability: "Protected access",
    },
    {
      title: "Decision Audit",
      description:
        "Review immutable decision records, administrative events, and read-only system audit history.",
      href: "/admin/audit",
      status: "Read only",
      tone: "info",
      capability: "Ledger-backed",
    },
    {
      title: "Support Tickets",
      description:
        "Review user-reported problems and controlled support workflows without exposing internal developer systems.",
      href: "/admin/tickets",
      status: "Available",
      tone: "info",
      capability: "Support boundary",
    },
    {
      title: "User Statistics",
      description:
        "Inspect account-level platform statistics and aggregate user activity surfaces.",
      href: "/admin/user-stats",
      status: "Available",
      tone: "violet",
      capability: "Administrative view",
    },
    {
      title: "User Workspace Preview",
      description:
        "Inspect the customer-facing workspace presentation without changing the authenticated role boundary.",
      href: "/admin/user-dashboard",
      status: "Preview",
      tone: "violet",
      capability: "Read-only view",
    },
  ];

export default function AdminPage() {
  return (
    <main className="space-y-6">
      <PageHeader
        eyebrow="NeuroVest Administration"
        title="Platform operations."
        description="A controlled workspace for identity administration, session oversight, support, audit review, and user-platform visibility."
        badge={
          <StatusBadge tone="violet">
            Elevated access
          </StatusBadge>
        }
        actions={
          <Link
            href="/admin/users"
            className="nv-button nv-button-primary nv-button-lg"
          >
            Open user management
          </Link>
        }
      />

      <section className="grid gap-4 md:grid-cols-3">
        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Authorization boundary
          </p>

          <p className="mt-3 text-2xl font-black text-white">
            Server authoritative
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            Administrative access is resolved from the authenticated backend identity, not browser state or conversational claims.
          </p>
        </Panel>

        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Execution policy
          </p>

          <p className="mt-3 text-2xl font-black text-white">
            Live trading disabled
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            Administrative controls do not activate broker execution or bypass NeuroVest safety boundaries.
          </p>
        </Panel>

        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Environment
          </p>

          <p className="mt-3 text-2xl font-black text-white">
            Controlled development
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            Current administrative surfaces are operating inside the qualified development environment.
          </p>
        </Panel>
      </section>

      <section>
        <div className="mb-4 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="nv-eyebrow">
              Administrative workspaces
            </p>

            <h2 className="mt-2 text-2xl font-black tracking-[-0.03em] text-white sm:text-3xl">
              Operations directory
            </h2>
          </div>

          <StatusBadge tone="success">
            Identity database connected
          </StatusBadge>
        </div>

        <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
          {workspaces.map(
            (workspace) => (
              <Link
                key={workspace.href}
                href={workspace.href}
                className="group block"
              >
                <Panel
                  variant="default"
                  className="h-full p-6 transition duration-200 group-hover:-translate-y-1 group-hover:border-cyan-300/25 group-hover:shadow-[0_22px_70px_rgba(0,0,0,0.32)]"
                >
                  <div className="flex items-start justify-between gap-4">
                    <StatusBadge
                      tone={workspace.tone}
                    >
                      {workspace.status}
                    </StatusBadge>

                    <span
                      aria-hidden="true"
                      className="text-lg text-slate-600 transition group-hover:translate-x-1 group-hover:text-cyan-200"
                    >
                      →
                    </span>
                  </div>

                  <h3 className="mt-6 text-xl font-black text-white transition group-hover:text-cyan-100">
                    {workspace.title}
                  </h3>

                  <p className="mt-3 text-sm leading-7 text-slate-400">
                    {workspace.description}
                  </p>

                  <div className="mt-6 border-t border-white/[0.07] pt-4">
                    <p className="text-[10px] font-black uppercase tracking-[0.18em] text-slate-600">
                      {workspace.capability}
                    </p>
                  </div>
                </Panel>
              </Link>
            ),
          )}
        </div>
      </section>

      <Panel
        variant="muted"
        className="overflow-hidden"
      >
        <div className="grid gap-6 p-6 lg:grid-cols-[1fr_auto] lg:items-center">
          <div>
            <p className="nv-eyebrow">
              Operational policy
            </p>

            <h2 className="mt-3 text-xl font-black text-white">
              Administrative actions remain explicit and auditable.
            </h2>

            <p className="mt-3 max-w-4xl text-sm leading-7 text-slate-400">
              Sensitive mutations require authenticated permissions, same-origin request validation, CSRF protection, and explicit confirmation. Protected developer and owner identities remain guarded by backend policy.
            </p>
          </div>

          <div className="flex flex-wrap gap-2 lg:max-w-[300px] lg:justify-end">
            <StatusBadge tone="success">
              CSRF protected
            </StatusBadge>

            <StatusBadge tone="info">
              Role enforced
            </StatusBadge>

            <StatusBadge tone="warning">
              Confirmation required
            </StatusBadge>
          </div>
        </div>
      </Panel>
    </main>
  );
}
