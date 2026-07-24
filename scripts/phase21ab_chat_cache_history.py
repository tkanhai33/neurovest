#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()

chat_service = ROOT / "frontend/services/chatService.ts"
chat_service.write_text(r'''export type ChatRole = "user" | "assistant" | "system";

export type ChatMessage = {
  id: string;
  role: ChatRole;
  content: string;
  createdAt: string;
};

export type ChatResponse = {
  status?: string;
  response?: unknown;
  message?: string;
  error?: string;
};

export function createChatMessage(role: ChatRole, content: string): ChatMessage {
  return {
    id: `${role}-${Date.now()}-${Math.random().toString(16).slice(2)}`,
    role,
    content,
    createdAt: new Date().toISOString(),
  };
}

export function normalizeChatReply(data: ChatResponse): string {
  if (typeof data.message === "string" && data.message.trim()) {
    return data.message;
  }

  if (typeof data.error === "string" && data.error.trim()) {
    return data.error;
  }

  if (
    typeof data.response === "object" &&
    data.response !== null &&
    "message" in data.response
  ) {
    const response = data.response as { message?: unknown };

    if (typeof response.message === "string" && response.message.trim()) {
      return response.message;
    }
  }

  return JSON.stringify(data.response ?? data, null, 2);
}

export async function sendChatMessage(message: string): Promise<ChatResponse> {
  const cleanMessage = message.trim();

  if (!cleanMessage) {
    return {
      status: "error",
      message: "",
      error: "missing_message",
    };
  }

  const response = await fetch("/api/v1/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    cache: "no-store",
    body: JSON.stringify({
      message: cleanMessage,
    }),
  });

  return await response.json();
}
''')

page = ROOT / "frontend/app/page.tsx"
text = page.read_text()

text = text.replace(
  'import { sendChatMessage, type ChatResponse } from "../services/chatService";',
  'import { createChatMessage, normalizeChatReply, sendChatMessage, type ChatMessage } from "../services/chatService";'
)

start = text.find("function FloatingChatWidget()")
end = text.find("\n\nexport default function Dashboard()", start)

component = r'''function FloatingChatWidget() {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    createChatMessage("assistant", "Neuro online. Standing guard."),
  ]);
  const [loading, setLoading] = useState(false);

  const send = useCallback(async () => {
    const cleanMessage = message.trim();

    if (!cleanMessage) return;

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
  }, [message]);

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
            width: 380,
            border: "1px solid rgba(34,211,238,0.45)",
            borderRadius: 24,
            background: "rgba(2,6,23,0.97)",
            padding: 16,
            boxShadow: "0 0 60px rgba(34,211,238,0.24)",
          }}
        >
          <div className="mb-3 flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-cyan-300">Neuro Chat</p>
              <h2 className="text-lg font-bold text-white">Assistant Console</h2>
            </div>

            <button
              type="button"
              onClick={() => setOpen(false)}
              className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300"
            >
              Close
            </button>
          </div>

          <div className="mb-3 max-h-72 space-y-2 overflow-auto rounded-2xl border border-slate-800 bg-slate-900/70 p-3">
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
          </div>

          <textarea
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            className="h-24 w-full resize-none rounded-2xl border border-slate-700 bg-slate-900 p-3 text-sm text-white outline-none focus:border-cyan-400"
            placeholder="Ask Neuro..."
          />

          <button
            type="button"
            onClick={() => void send()}
            disabled={loading}
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

if start == -1 or end == -1:
    raise RuntimeError("Could not locate FloatingChatWidget block")

text = text[:start] + component + text[end:]

page.write_text(text)

print("patched Phase 21A/B chat cache + message history")
