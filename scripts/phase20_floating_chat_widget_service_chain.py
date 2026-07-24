#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()

# 20A frontend chat service
services = ROOT / "frontend/services"
services.mkdir(parents=True, exist_ok=True)

(services / "chatService.ts").write_text('export type ChatRole = "user" | "assistant" | "system";\n\nexport type ChatMessage = {\n  id: string;\n  role: ChatRole;\n  content: string;\n  createdAt: string;\n};\n\nexport type ChatResponse = {\n  status?: string;\n  response?: unknown;\n  message?: string;\n  error?: string;\n};\n\nexport function createChatMessage(role: ChatRole, content: string): ChatMessage {\n  return {\n    id: `${role}-${Date.now()}-${Math.random().toString(16).slice(2)}`,\n    role,\n    content,\n    createdAt: new Date().toISOString(),\n  };\n}\n\nexport function normalizeChatReply(data: ChatResponse): string {\n  if (typeof data.message === "string" && data.message.trim()) return data.message;\n  if (typeof data.error === "string" && data.error.trim()) return data.error;\n\n  if (typeof data.response === "object" && data.response !== null && "message" in data.response) {\n    const response = data.response as { message?: unknown };\n    if (typeof response.message === "string" && response.message.trim()) return response.message;\n  }\n\n  return JSON.stringify(data.response ?? data, null, 2);\n}\n\nexport async function sendChatMessage(message: string): Promise<ChatResponse> {\n  const cleanMessage = message.trim();\n\n  if (!cleanMessage) return { status: "error", error: "missing_message" };\n\n  const response = await fetch("/api/v1/chat", {\n    method: "POST",\n    headers: { "Content-Type": "application/json" },\n    cache: "no-store",\n    body: JSON.stringify({ message: cleanMessage }),\n  });\n\n  return await response.json();\n}\n')

# 20B Next chat proxy
route_dir = ROOT / "frontend/app/api/v1/chat"
route_dir.mkdir(parents=True, exist_ok=True)

(route_dir / "route.ts").write_text(r'''import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const response = await fetch("http://127.0.0.1:8000/api/v1/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      cache: "no-store",
      body: JSON.stringify(body),
    });

    const data = await response.json();

    return NextResponse.json(data, {
      status: response.status,
    });
  } catch (error) {
    return NextResponse.json(
      {
        status: "error",
        response: {
          type: "text",
          message: "Chat proxy unavailable.",
        },
        error: String(error),
      },
      { status: 502 }
    );
  }
}
''')

# 20C Floating Chat Widget
page = ROOT / "frontend/app/page.tsx"
text = page.read_text()

if 'from "../services/chatService"' not in text:
    text = text.replace(
        'import { getRiskGate, type RiskGate } from "../services/riskService";',
        'import { getRiskGate, type RiskGate } from "../services/riskService";\nimport { sendChatMessage, type ChatResponse } from "../services/chatService";'
    )

component = r'''
function FloatingChatWidget() {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState<ChatResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const send = useCallback(async () => {
    const cleanMessage = message.trim();

    if (!cleanMessage) return;

    setLoading(true);

    try {
      const data = await sendChatMessage(cleanMessage);
      setReply(data);
      setMessage("");
    } finally {
      setLoading(false);
    }
  }, [message]);

  const visibleReply =
    typeof reply?.response === "object" && reply?.response !== null && "message" in reply.response
      ? String((reply.response as { message?: string }).message || "")
      : String(reply?.message || reply?.error || "");

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {open && (
        <section className="mb-4 w-[360px] rounded-3xl border border-cyan-400/30 bg-slate-950/95 p-4 shadow-[0_0_60px_rgba(34,211,238,0.18)]">
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

          {visibleReply && (
            <div className="mt-3 max-h-56 overflow-auto rounded-2xl border border-slate-800 bg-slate-900/80 p-3 text-sm text-slate-200">
              {visibleReply}
            </div>
          )}
        </section>
      )}

      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="rounded-full border border-cyan-300/40 bg-cyan-400 px-5 py-4 text-sm font-black text-slate-950 shadow-[0_0_40px_rgba(34,211,238,0.35)]"
      >
        Neuro
      </button>
    </div>
  );
}
'''

if "function FloatingChatWidget()" not in text:
    text = text.replace("export default function Dashboard()", component + "\n\nexport default function Dashboard()", 1)

if "<FloatingChatWidget />" not in text:
    text = text.replace("</main>", "      <FloatingChatWidget />\n    </main>", 1)

page.write_text(text)

print("patched Phase 20 floating chat widget service chain")
