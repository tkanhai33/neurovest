#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()
PAGE = ROOT / "frontend/app/page.tsx"

text = PAGE.read_text()

# Deduplicate DashboardTabNavigation if older certs duplicated it.
name = "function DashboardTabNavigation("
first = text.find(name)
second = text.find(name, first + 1)

if first != -1 and second != -1:
    next_func = text.find("\n\nfunction ", second + 1)
    if next_func != -1:
        text = text[:second] + text[next_func + 2:]

if 'function ChatTabPanel()' not in text:
    component = r'''
function ChatTabPanel() {
  return (
    <section className="mt-6 rounded-2xl border border-cyan-400/30 bg-slate-950/80 p-5 shadow-[0_0_30px_rgba(34,211,238,0.12)]">
      <p className="text-xs uppercase tracking-[0.3em] text-cyan-300">
        Chat Workspace
      </p>

      <h2 className="mt-1 text-2xl font-bold text-white">
        Neuro Assistant Console
      </h2>

      <p className="mt-3 max-w-3xl text-sm text-slate-400">
        The floating Neuro button remains protected and active. This workspace reserves the full chat console surface for the next expansion.
      </p>

      <div className="mt-4 grid gap-3 md:grid-cols-3">
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-4">
          <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Mode</p>
          <p className="mt-2 text-lg font-bold text-cyan-200">Assistant</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-4">
          <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Widget</p>
          <p className="mt-2 text-lg font-bold text-emerald-200">Protected</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-4">
          <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Runtime</p>
          <p className="mt-2 text-lg font-bold text-fuchsia-200">Connected</p>
        </div>
      </div>
    </section>
  );
}
'''
    text = text.replace(
        "function FloatingChatWidget()",
        component + "\n\nfunction FloatingChatWidget()",
        1,
    )

# Replace empty chat tab placeholder with real panel.
text = text.replace(
'''      {(activeTab === "overview" || activeTab === "chat") && (
        <></>
      )}''',
'''      {activeTab === "chat" && (
        <ChatTabPanel />
      )}'''
)

# If previous replacement left a pure empty chat block, repair it too.
text = text.replace(
'''      {activeTab === "chat" && (
        <></>
      )}''',
'''      {activeTab === "chat" && (
        <ChatTabPanel />
      )}'''
)

PAGE.write_text(text)
print("patched Phase 25B tab layout polish + chat tab panel")
