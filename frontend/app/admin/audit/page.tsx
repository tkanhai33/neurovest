import PageHeader from "../../../components/app-shell/PageHeader";

import {
  Panel,
  StatusBadge,
  StatusMessage,
} from "../../../components/ui";

export default function AdminAuditPage() {
  return (
    <main className="space-y-6">
      <PageHeader
        eyebrow="NeuroVest Administration"
        title="Decision audit."
        description="Review server-authoritative decision records, administrative events, and immutable audit history."
        badge={
          <StatusBadge tone="info">
            Read only
          </StatusBadge>
        }
      />

      <section className="grid gap-4 md:grid-cols-3">
        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Access mode
          </p>

          <p className="mt-3 text-xl font-black text-white">
            Read only
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            Audit records cannot be changed from this workspace.
          </p>
        </Panel>

        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Evidence source
          </p>

          <p className="mt-3 text-xl font-black text-white">
            Server authoritative
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            Local estimates and fabricated audit events are never displayed.
          </p>
        </Panel>

        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Mutation policy
          </p>

          <p className="mt-3 text-xl font-black text-white">
            Prohibited
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            Administrative review cannot modify immutable decision evidence.
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
              Audit record inventory
            </p>

            <h2 className="mt-3 text-2xl font-black text-white">
              Decision and administrative history
            </h2>

            <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-400">
              Records appear here only when returned through a qualified
              read-only audit source.
            </p>
          </div>

          <StatusBadge tone="success">
            Immutable boundary
          </StatusBadge>
        </div>

        <div className="mt-6">
          <StatusMessage tone="info">
            No qualified audit records are currently available to this view.
          </StatusMessage>
        </div>
      </Panel>
    </main>
  );
}
