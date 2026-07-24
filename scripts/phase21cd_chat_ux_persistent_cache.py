#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()
PAGE = ROOT / "frontend/app/page.tsx"

text = PAGE.read_text()

# Add useRef import.
text = text.replace(
    'import { useCallback, useEffect, useState } from "react";',
    'import { useCallback, useEffect, useRef, useState } from "react";'
)

# Replace FloatingChatWidget with UX + localStorage cache version.
start = text.find("function FloatingChatWidget()")
end = text.find("\n\nexport default function Dashboard()", start)

if start == -1 or end == -1:
    raise RuntimeError("Could not locate FloatingChatWidget block")

component = r'''function FloatingChatWidget() {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    createChatMessage("assistant", "Neuro online. Standing guard."),
  ]);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const cached = window.localStorage.getItem("neuro_chat_history_v1");

    if (!cached) return;

    try {
      const parsed = JSON.parse(cached) as ChatMessage[];

      if (Array.isArray(parsed) && parsed.length > 0) {
        setMessages(parsed);
      }
    } catch {
      window.localStorage.removeItem("neuro_chat_history_v1");
    }
  }, []);

  useEffect(() => {
    window.localStorage.setItem("neuro_chat_history_v1", JSON.stringify(messages));
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, open, loading]);

  const clearHistory = useCallback(() => {
    const reset = [createChatMessage("assistant", "Neuro online. Standing guard.")];

    setMessages(reset);
    window.localStorage.setItem("neuro_chat_history_v1", JSON.stringify(reset));
  }, []);

  const send = useCallback(async () => {
    const cleanMessage = message.trim();

    if (!cleanMessage || loading) return;

    const userMessage = createChatMessage("user", cleanMessage);

    setMessages((current) => [...current, userMessage]);
    setMessage("");
    setLoading(true);

    try {
      const data = await sendChatMessage(cleanMessage);
      const assistantMessage = createChatMessage("assistant", normalizeChatReply(data));

      setMessages((current) => [...current, assistantMessage]);
    } catch (error) {
      const errorMessage = createChatMessage("assistant", String(error));

      setMessages((current) => [...current, errorMessage]);
    } finally {
      setLoading(false);
    }
  }, [loading, message]);

  return (
    <div
      style={{
        position: "fixed",
        right: 24,
        bottom: 24,
        zIndex: 999999,
      }}
    >
      {open && (
        <section
          style={{
            marginBottom: 16,
            width: 400,
            border: "1px solid rgba(34,211,238,0.45)",
            borderRadius: 24,
            background: "rgba(2,6,23,0.97)",
            padding: 16,
            boxShadow: "0 0 60px rgba(34,211,238,0.24)",
          }}
        >
          <div className="mb-3 flex items-center justify-between gap-2">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-cyan-300">Neuro Chat</p>
              <h2 className="text-lg font-bold text-white">Assistant Console</h2>
            </div>

            <div className="flex gap-2">
              <button
                type="button"
                onClick={clearHistory}
                className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300"
              >
                Clear
              </button>

              <button
                type="button"
                onClick={() => setOpen(false)}
                className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300"
              >
                Close
              </button>
            </div>
          </div>

          <div className="mb-3 max-h-80 space-y-2 overflow-auto rounded-2xl border border-slate-800 bg-slate-900/70 p-3">
            {messages.map((item) => (
              <div
                key={item.id}
                className={item.role === "user" ? "text-right" : "text-left"}
              >
                <div
                  className={
                    item.role === "user"
                      ? "inline-block max-w-[85%] rounded-2xl bg-cyan-400 px-3 py-2 text-sm font-semibold text-slate-950"
                      : "inline-block max-w-[85%] rounded-2xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-200"
                  }
                >
                  {item.content}

                  <div className="mt-1 text-[10px] opacity-60">
                    {new Date(item.createdAt).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}

            {loading && (
              <div className="text-left">
                <div className="inline-block rounded-2xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-400">
                  Neuro is thinking...
                </div>
              </div>
            )}

            <div ref={scrollRef} />
          </div>

          <textarea
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                void send();
              }
            }}
            className="h-24 w-full resize-none rounded-2xl border border-slate-700 bg-slate-900 p-3 text-sm text-white outline-none focus:border-cyan-400"
            placeholder="Ask Neuro..."
          />

          <button
            type="button"
            onClick={() => void send()}
            disabled={loading || !message.trim()}
            className="mt-3 w-full rounded-2xl bg-cyan-400 px-4 py-2 text-sm font-bold text-slate-950 disabled:opacity-60"
          >
            {loading ? "Sending" : "Send"}
          </button>
        </section>
      )}

      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        style={{
          background: "#22d3ee",
          color: "#020617",
          border: "2px solid white",
          borderRadius: 9999,
          padding: "16px 22px",
          fontWeight: 900,
          boxShadow: "0 0 40px rgba(34,211,238,0.55)",
          cursor: "pointer",
        }}
      >
        Neuro
      </button>
    </div>
  );
}'''

text = text[:start] + component + text[end:]
PAGE.write_text(text)

print("patched Phase 21C/D chat UX + persistent cache")
