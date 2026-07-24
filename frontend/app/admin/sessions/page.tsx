import PageHeader from "../../../components/app-shell/PageHeader";

import {
  Panel,
  StatusBadge,
  StatusMessage,
} from "../../../components/ui";

export default function AdminSessionsPage() {
  return (
    <main className="space-y-6">
      <PageHeader
        eyebrow="NeuroVest Administration"
        title="Session administration."
        description="Review authenticated session boundaries, access policy, and controlled revocation responsibilities."
        badge={
          <StatusBadge tone="warning">
            Restricted access
          </StatusBadge>
        }
      />

      <section className="grid gap-4 md:grid-cols-3">
        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Session authority
          </p>

          <p className="mt-3 text-xl font-black text-white">
            Backend enforced
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            Browser state cannot grant, renew, or extend an authenticated
            session.
          </p>
        </Panel>

        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Revocation policy
          </p>

          <p className="mt-3 text-xl font-black text-white">
            Explicit action
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            Session revocation remains permission-controlled, attributable,
            and auditable.
          </p>
        </Panel>

        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Credential exposure
          </p>

          <p className="mt-3 text-xl font-black text-white">
            Protected
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            Raw access and refresh credentials are never displayed in this
            workspace.
          </p>
        </Panel>
      </section>

      <Panel
        variant="default"
        className="p-6"
      >
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="nv-eyebrow">
              Session inventory
            </p>

            <h2 className="mt-3 text-2xl font-black text-white">
              Authenticated access records
            </h2>

            <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-400">
              Session records appear only when returned through a qualified
              server-authoritative administrative source.
            </p>
          </div>

          <StatusBadge tone="info">
            Server records only
          </StatusBadge>
        </div>

        <div className="mt-6">
          <StatusMessage tone="info">
            No qualified session records are currently available to this view.
          </StatusMessage>
        </div>
      </Panel>

      <Panel
        variant="muted"
        className="p-6"
      >
        <div className="grid gap-4 md:grid-cols-3">
          <div>
            <p className="nv-stat-label">
              Identity source
            </p>

            <p className="mt-2 font-black text-white">
              Canonical authentication service
            </p>
          </div>

          <div>
            <p className="nv-stat-label">
              Administrative scope
            </p>

            <p className="mt-2 font-black text-white">
              Permission controlled
            </p>
          </div>

          <div>
            <p className="nv-stat-label">
              Secret visibility
            </p>

            <p className="mt-2 font-black text-white">
              None
            </p>
          </div>
        </div>
      </Panel>
    </main>
  );
}
