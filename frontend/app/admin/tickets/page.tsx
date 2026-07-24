import PageHeader from "../../../components/app-shell/PageHeader";

import {
  Panel,
  StatusBadge,
  StatusMessage,
} from "../../../components/ui";

const supportStates = [
  {
    label: "Open",
    description:
      "A newly submitted issue awaiting administrative review.",
    tone: "info" as const,
  },
  {
    label: "Waiting for user",
    description:
      "Administrative review requires additional user information.",
    tone: "warning" as const,
  },
  {
    label: "Waiting for administrator",
    description:
      "The user has responded and administrative action is required.",
    tone: "violet" as const,
  },
  {
    label: "Resolved",
    description:
      "The reported issue has been addressed and documented.",
    tone: "success" as const,
  },
  {
    label: "Closed",
    description:
      "The support conversation has reached its final state.",
    tone: "success" as const,
  },
];

export default function AdminTicketsPage() {
  return (
    <main className="space-y-6">
      <PageHeader
        eyebrow="NeuroVest Administration"
        title="Support tickets."
        description="Review controlled support workflows while preserving user privacy, role boundaries, and administrative attribution."
        badge={
          <StatusBadge tone="info">
            Support boundary
          </StatusBadge>
        }
      />

      <section className="grid gap-4 md:grid-cols-3">
        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Identity policy
          </p>

          <p className="mt-3 text-xl font-black text-white">
            No impersonation
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            Reviewing a ticket does not change the authenticated
            administrator identity.
          </p>
        </Panel>

        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Access policy
          </p>

          <p className="mt-3 text-xl font-black text-white">
            Explicit selection
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            User-specific support information must originate from an
            authorized server record.
          </p>
        </Panel>

        <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Developer boundary
          </p>

          <p className="mt-3 text-xl font-black text-white">
            Internal systems hidden
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            Support access does not expose developer diagnostics or
            repository context.
          </p>
        </Panel>
      </section>

      <section className="grid gap-6 lg:grid-cols-[0.82fr_1.18fr]">
        <Panel
          variant="elevated"
          className="p-6"
        >
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="nv-eyebrow">
                Workflow states
              </p>

              <h2 className="mt-3 text-2xl font-black text-white">
                Support lifecycle
              </h2>

              <p className="mt-3 text-sm leading-7 text-slate-400">
                These states define the controlled support workflow. They
                are not ticket counts or fabricated account records.
              </p>
            </div>

            <StatusBadge tone="violet">
              Administrative
            </StatusBadge>
          </div>

          <div className="mt-6 space-y-3">
            {supportStates.map(
              (state) => (
                <div
                  key={state.label}
                  className="border-b border-white/[0.07] px-1 py-4 last:border-b-0"
                >
                  <div className="flex flex-wrap items-center gap-3">
                    <StatusBadge tone={state.tone}>
                      {state.label}
                    </StatusBadge>
                  </div>

                  <p className="mt-3 text-sm leading-6 text-slate-400">
                    {state.description}
                  </p>
                </div>
              ),
            )}
          </div>
        </Panel>

        <Panel
          variant="default"
          className="p-6"
        >
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="nv-eyebrow">
                Ticket workspace
              </p>

              <h2 className="mt-3 text-2xl font-black text-white">
                Support conversation
              </h2>

              <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-400">
                Ticket details and messages are displayed only after an
                authorized server record has been selected.
              </p>
            </div>

            <StatusBadge tone="warning">
              Selection required
            </StatusBadge>
          </div>

          <div className="mt-6">
            <StatusMessage tone="info">
              No support ticket is selected.
            </StatusMessage>
          </div>

          <div className="mt-6 grid gap-4 border-t border-white/[0.07] pt-6 sm:grid-cols-2">
            <Panel
              variant="muted"
              className="p-5"
            >
              <p className="nv-stat-label">
                Administrator identity
              </p>

              <p className="mt-3 font-black text-white">
                Preserved
              </p>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                Actions remain attributable to the authenticated
                administrator.
              </p>
            </Panel>

            <Panel
              variant="muted"
              className="p-5"
            >
              <p className="nv-stat-label">
                User privacy
              </p>

              <p className="mt-3 font-black text-white">
                Protected
              </p>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                Unselected users and unrelated account information remain
                outside this view.
              </p>
            </Panel>
          </div>
        </Panel>
      </section>
    </main>
  );
}
