#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()
PAGE = ROOT / "frontend/app/page.tsx"

text = PAGE.read_text()

start = text.find("function LiveSystemGraphPanel()")
end = text.find("\n\nfunction FloatingChatWidget()", start)

if start == -1 or end == -1:
    raise RuntimeError("Could not locate LiveSystemGraphPanel block")

component = r'''function LiveSystemGraphPanel() {
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
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-cyan-300">
            Live System Graph
          </p>

          <h2 className="mt-1 text-2xl font-bold text-white">
            Runtime Flow
          </h2>
        </div>

        <button
          type="button"
          onClick={() => void loadGraph()}
          className="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-bold text-slate-950"
        >
          Refresh
        </button>
      </div>

      <div className="mb-5 grid gap-3 md:grid-cols-3">
        <div className="rounded-xl bg-slate-900/80 p-3">
          <p className="text-slate-400">Nodes</p>
          <p className="text-2xl font-black text-cyan-200">{nodes.length}</p>
        </div>

        <div className="rounded-xl bg-slate-900/80 p-3">
          <p className="text-slate-400">Edges</p>
          <p className="text-2xl font-black text-cyan-200">{edges.length}</p>
        </div>

        <div className="rounded-xl bg-slate-900/80 p-3">
          <p className="text-slate-400">Status</p>
          <p className="text-2xl font-black text-emerald-300">
            {graph?.status || "ok"}
          </p>
        </div>
      </div>

      <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-950/80 p-4">
        <div className="flex min-w-max items-center gap-3">
          {nodes.map((node, index) => (
            <div key={node.id} className="flex items-center gap-3">
              <div className="relative w-52 rounded-2xl border border-cyan-400/30 bg-slate-900/90 p-4 shadow-[0_0_24px_rgba(34,211,238,0.10)]">
                <div className="absolute -right-1 -top-1 h-3 w-3 rounded-full bg-emerald-300 shadow-[0_0_18px_rgba(110,231,183,0.9)]" />

                <p className="truncate text-sm font-black text-white">
                  {node.id}
                </p>

                <p className="mt-1 text-xs text-cyan-300">
                  {node.last_event_type || "active"}
                </p>

                <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                  <div className="rounded-lg bg-slate-950/80 p-2">
                    <p className="text-slate-500">Events</p>
                    <p className="font-bold text-white">{node.event_count ?? 0}</p>
                  </div>

                  <div className="rounded-lg bg-slate-950/80 p-2">
                    <p className="text-slate-500">Symbol</p>
                    <p className="font-bold text-white">{node.symbol || "—"}</p>
                  </div>
                </div>
              </div>

              {index < nodes.length - 1 && (
                <div className="flex items-center gap-1">
                  <div className="h-1 w-10 rounded-full bg-cyan-400 shadow-[0_0_14px_rgba(34,211,238,0.8)]" />
                  <div className="h-2 w-2 rotate-45 border-r-2 border-t-2 border-cyan-300" />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="mt-4 rounded-2xl border border-slate-800 bg-slate-950/80 p-4">
        <p className="mb-3 text-xs uppercase tracking-[0.3em] text-slate-400">
          Active Edges
        </p>

        <div className="grid gap-2 md:grid-cols-2 xl:grid-cols-3">
          {edges.map((edge) => (
            <div
              key={edge.id}
              className="rounded-xl border border-slate-800 bg-slate-900/80 p-3 text-sm"
            >
              <p className="font-bold text-white">
                {edge.from || edge.id.split("->")[0]} → {edge.to || edge.id.split("->")[1] || "unknown"}
              </p>

              <p className="mt-1 text-xs text-cyan-300">
                count: {edge.count ?? 0}
              </p>

              <p className="text-xs text-slate-400">
                symbol: {edge.symbol || "—"}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}'''

text = text[:start] + component + text[end:]
PAGE.write_text(text)

print("patched Phase 22B live graph visualization")
