"use client";

import SharedNeuroWorkspace from "../../components/workspaces/SharedNeuroWorkspace";
import PageHeader from "../../components/app-shell/PageHeader";
import { Panel, StatusMessage } from "../../components/ui";

export default function UserChatPage() {
  return (
    <SharedNeuroWorkspace
      audience="user"
      title="Talk with Neuro"
      description="Ask Neuro questions, review your simulated activity, and work inside your personal AI workspace."
    >
      <main className="space-y-6">
        <PageHeader
          eyebrow="NeuroVest Personal Workspace"
          title="Neuro chat."
          description="Ask Neuro questions, review your simulated activity, and work inside your personal AI workspace."
          badge={
            <StatusMessage tone="success">
              Authenticated
            </StatusMessage>
          }
        />

        <Panel variant="default" className="p-6">
          <section className="rounded-3xl border border-white/10 bg-slate-900/60 p-6">
            <p className="text-xs font-black uppercase tracking-[0.22em] text-fuchsia-300">
              User Access
            </p>

            <h2 className="mt-3 text-xl font-black text-white">
              Personal Neuro Session
            </h2>

            <p className="mt-3 max-w-3xl leading-7 text-slate-400">
              Your Neuro chat is available from the floating chat control.
              Paper trading, simulation, plan capabilities, and account data
              remain enforced by qualified server-authoritative APIs.
            </p>
          </section>
        </Panel>
      </main>
    </SharedNeuroWorkspace>
  );
}
