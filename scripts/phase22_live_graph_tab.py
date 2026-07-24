#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()

service = ROOT / "frontend/services/graphService.ts"
service.write_text('export type LiveGraphNode = {\n  id: string;\n  name?: string;\n  stack?: string;\n  layer?: string;\n  status?: string;\n  event_count?: number;\n  last_event_type?: string;\n  symbol?: string | null;\n};\n\nexport type LiveGraphEdge = {\n  id: string;\n  from?: string;\n  to?: string;\n  type?: string;\n  count?: number;\n  symbol?: string | null;\n};\n\nexport type LiveGraphResponse = {\n  status?: string;\n  nodes: LiveGraphNode[];\n  edges: LiveGraphEdge[];\n  error?: string;\n};\n\ntype RawGraph = {\n  status?: string;\n  nodes?: Record<string, string> | LiveGraphNode[];\n  node_meta?: Record<string, Partial<LiveGraphNode>>;\n  edges?: Record<string, number> | LiveGraphEdge[];\n  edge_meta?: Record<string, Partial<LiveGraphEdge>>;\n  error?: string;\n};\n\nexport function normalizeLiveGraph(raw: RawGraph): LiveGraphResponse {\n  const nodeMeta = raw.node_meta || {};\n  const edgeMeta = raw.edge_meta || {};\n\n  const nodes: LiveGraphNode[] = Array.isArray(raw.nodes)\n    ? raw.nodes.map((node, index) => ({\n        ...node,\n        id: node.id || node.name || `node-${index}`,\n      }))\n    : Object.entries(raw.nodes || {}).map(([id, status]) => ({\n        id,\n        status,\n        ...nodeMeta[id],\n      }));\n\n  const edges: LiveGraphEdge[] = Array.isArray(raw.edges)\n    ? raw.edges.map((edge, index) => ({\n        ...edge,\n        id: edge.id || `${edge.from || "unknown"}->${edge.to || index}`,\n      }))\n    : Object.entries(raw.edges || {}).map(([id, count]) => ({\n        id,\n        count,\n        ...edgeMeta[id],\n      }));\n\n  return {\n    status: raw.status || "ok",\n    nodes,\n    edges,\n    error: raw.error,\n  };\n}\n\nexport async function getLiveGraph(): Promise<LiveGraphResponse> {\n  const response = await fetch("/api/v1/graph/live", {\n    cache: "no-store",\n  });\n\n  const raw = await response.json();\n\n  return normalizeLiveGraph(raw);\n}\n')

route_dir = ROOT / "frontend/app/api/v1/graph/live"
route_dir.mkdir(parents=True, exist_ok=True)

(route_dir / "route.ts").write_text(r'''import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const response = await fetch("http://127.0.0.1:8000/api/v1/graph/live", {
      cache: "no-store",
    });

    const data = await response.json();

    return NextResponse.json(data, {
      status: response.status,
    });
  } catch (error) {
    return NextResponse.json(
      {
        status: "error",
        nodes: [],
        edges: [],
        error: String(error),
      },
      { status: 502 }
    );
  }
}
''')

page = ROOT / "frontend/app/page.tsx"
text = page.read_text()

if 'from "../services/graphService"' not in text:
    text = text.replace(
      'import { createChatMessage, normalizeChatReply, sendChatMessage, type ChatMessage } from "../services/chatService";',
      'import { createChatMessage, normalizeChatReply, sendChatMessage, type ChatMessage } from "../services/chatService";\nimport { getLiveGraph, type LiveGraphResponse } from "../services/graphService";'
    )

component = r'''
function LiveSystemGraphPanel() {
  const [graph, setGraph] = useState<LiveGraphResponse | null>(null);

  const loadGraph = useCallback(async () => {
    const data = await getLiveGraph();
    setGraph(data);
  }, []);

  useEffect(() => {
    const firstLoad = setTimeout(() => {
      void loadGraph();
    }, 0);

    const timer = setInterval(() => {
      void loadGraph();
    }, 5000);

    return () => {
      clearTimeout(firstLoad);
      clearInterval(timer);
    };
  }, [loadGraph]);

  const nodes = graph?.nodes || [];
  const edges = graph?.edges || [];

  return (
    <section className="mt-6 rounded-2xl border border-cyan-400/30 bg-slate-950/80 p-5 shadow-[0_0_30px_rgba(34,211,238,0.12)]">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-cyan-300">Live System Graph</p>
          <h2 className="mt-1 text-2xl font-bold text-white">Runtime Nodes</h2>
        </div>

        <button
          type="button"
          onClick={() => void loadGraph()}
          className="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-bold text-slate-950"
        >
          Refresh
        </button>
      </div>

      <div className="mb-4 grid gap-3 md:grid-cols-2">
        <div className="rounded-xl bg-slate-900/80 p-3">
          <p className="text-slate-400">Nodes</p>
          <p className="text-2xl font-black text-cyan-200">{nodes.length}</p>
        </div>

        <div className="rounded-xl bg-slate-900/80 p-3">
          <p className="text-slate-400">Edges</p>
          <p className="text-2xl font-black text-cyan-200">{edges.length}</p>
        </div>
      </div>

      {graph?.error && (
        <p className="mb-3 rounded-xl border border-red-400/30 bg-red-950/40 p-3 text-xs text-red-200">
          {graph.error}
        </p>
      )}

      <div className="grid gap-2 md:grid-cols-3">
        {nodes.map((node, index) => (
          <div
            key={node.id || node.name || index}
            className="rounded-xl border border-slate-800 bg-slate-900/80 p-3"
          >
            <p className="font-bold text-white">{node.id || node.name || `node-${index}`}</p>
            <p className="text-xs text-slate-400">{node.stack || "unknown stack"}</p>
            <p className="text-xs text-cyan-300">{node.layer || node.status || "active"}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
'''

if "function LiveSystemGraphPanel()" not in text:
    text = text.replace("function FloatingChatWidget()", component + "\n\nfunction FloatingChatWidget()", 1)

if "<LiveSystemGraphPanel />" not in text:
    text = text.replace("<LiveMarketWatchlist />", "<LiveMarketWatchlist />\n      <LiveSystemGraphPanel />", 1)

page.write_text(text)

print("patched Phase 22 live graph tab/panel")
