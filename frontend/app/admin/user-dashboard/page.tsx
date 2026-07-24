import Link from "next/link";

import PageHeader from "../../../components/app-shell/PageHeader";

import {
  Panel,
  StatusBadge,
  StatusMessage,
} from "../../../components/ui";

export default function AdminUserDashboardPage() {
  return (
    <main className="space-y-6">
      <PageHeader
        eyebrow="NeuroVest Administration"
        title="User workspace access."
        description="Open the genuine lower-level User dashboard while retaining the authenticated Administrator role and audit identity."
        badge={
          <StatusBadge tone="violet">
            Downward view access
          </StatusBadge>
        }
        actions={
          <Link
            href="/user/dashboard"
            className="nv-button nv-button-primary nv-button-lg"
          >
            Open User dashboard
          </Link>
        }
      />

      <section className="grid gap-4 md:grid-cols-3">
        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Authenticated role
          </p>

          <p className="mt-3 text-xl font-black text-white">
            Administrator
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            Opening the User workspace does not change the active
            administrative identity.
          </p>
        </Panel>

        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Accessible view
          </p>

          <p className="mt-3 text-xl font-black text-white">
            User dashboard
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            Administrators may inspect lower-level product views for support
            and issue confirmation.
          </p>
        </Panel>

        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Impersonation
          </p>

          <p className="mt-3 text-xl font-black text-white">
            Disabled
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            No user identity, chat role, account ownership, or audit
            attribution is assumed.
          </p>
        </Panel>
      </section>

      <Panel
        variant="default"
        className="p-6"
      >
        <div className="grid gap-6 lg:grid-cols-[1fr_auto] lg:items-center">
          <div>
            <p className="nv-eyebrow">
              Hierarchical workspace access
            </p>

            <h2 className="mt-3 text-2xl font-black text-white">
              Inspect the customer-facing experience
            </h2>

            <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-400">
              The linked dashboard is the real User workspace, not a copied
              Developer console and not an impersonated account.
              Engineering-only systems and privileged internal controls
              remain outside the User workspace.
            </p>
          </div>

          <Link
            href="/user/dashboard"
            className="nv-button nv-button-primary nv-button-lg"
          >
            Continue to User view
          </Link>
        </div>
      </Panel>

      <section className="grid gap-4 md:grid-cols-2">
        <Panel
          variant="muted"
          className="p-6"
        >
          <p className="nv-eyebrow">
            Preserved permissions
          </p>

          <h2 className="mt-3 text-xl font-black text-white">
            Administrator authority remains active
          </h2>

          <p className="mt-3 text-sm leading-7 text-slate-400">
            Route access and backend authorization continue to resolve from
            the authenticated Administrator principal.
          </p>
        </Panel>

        <Panel
          variant="muted"
          className="p-6"
        >
          <p className="nv-eyebrow">
            Preserved role truth
          </p>

          <h2 className="mt-3 text-xl font-black text-white">
            Chat and context remain administrative
          </h2>

          <p className="mt-3 text-sm leading-7 text-slate-400">
            Viewing a lower-level page does not cause Neuro to identify the
            Administrator as a standard User account.
          </p>
        </Panel>
      </section>

      <StatusMessage tone="info">
        Downward view access is observational and support-oriented. It does not
        grant user impersonation or expose Developer-only systems.
      </StatusMessage>
    </main>
  );
}
