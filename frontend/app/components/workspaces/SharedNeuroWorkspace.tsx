"use client";

import FloatingChatWidget from "../chat/FloatingChatWidget";
import NeuroWorkspace from "./NeuroWorkspace";

export type NeuroWorkspaceAudience =
  | "dev"
  | "admin"
  | "user";

type SharedNeuroWorkspaceProps = {
  audience: NeuroWorkspaceAudience;
  showGlobals?: boolean;
  title?: string;
  description?: string;
  children?: React.ReactNode;
};

const audienceLabels: Record<
  NeuroWorkspaceAudience,
  string
> = {
  dev: "Development Workspace",
  admin: "Administrative Workspace",
  user: "User Workspace",
};

export default function SharedNeuroWorkspace({
  audience,
  showGlobals = false,
  title = "Neuro",
  description = (
    "Shared Neuro intelligence, chat, and runtime workspace."
  ),
  children,
}: SharedNeuroWorkspaceProps) {
  return (
    <main className="mx-auto min-h-[calc(100vh-68px)] max-w-[1600px] px-6 py-8">
      <header className="rounded-3xl border border-cyan-300/10 bg-slate-900/60 p-7 shadow-2xl">
        <p className="text-xs font-black uppercase tracking-[0.3em] text-cyan-300">
          {audienceLabels[audience]}
        </p>

        <h1 className="mt-3 text-3xl font-black tracking-tight text-white">
          {title}
        </h1>

        <p className="mt-3 max-w-3xl leading-7 text-slate-400">
          {description}
        </p>
      </header>

      {children ? (
        <section className="mt-6">
          {children}
        </section>
      ) : null}

      {showGlobals ? (
        <section className="mt-6">
          <NeuroWorkspace />
        </section>
      ) : null}

      <FloatingChatWidget />
    </main>
  );
}
