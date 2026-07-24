#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()
S = ROOT / "frontend/services"
PAGE = ROOT / "frontend/app/page.tsx"

(S / "observabilityTimelineService.ts").write_text(r'''import { getRequestMetrics } from "./requestObservability";
import { getLiveGraph } from "./graphService";

export type ObservabilityEvent = {
  id: string;
  source: "frontend" | "graph";
  label: string;
  detail: string;
  status: string;
  timestamp: string;
};

export async function getObservabilityTimeline(): Promise<ObservabilityEvent[]> {
  const requestEvents = getRequestMetrics().map((item) => ({
    id: `request-${item.key}-${item.lastSeen}`,
    source: "frontend" as const,
    label: item.key,
    detail: `${item.method} ${item.url} · ${item.lastLatencyMs}ms`,
    status: item.lastStatus,
    timestamp: item.lastSeen,
  }));

  const graph = await getLiveGraph();

  const graphEvents = graph.nodes.map((node) => ({
    id: `graph-${node.id}-${node.last_event_type || node.status || "active"}`,
    source: "graph" as const,
    label: node.id,
    detail: `${node.last_event_type || node.status || "active"} · ${node.symbol || "—"}`,
    status: node.status || "active",
    timestamp: new Date().toISOString(),
  }));

  return [...requestEvents, ...graphEvents]
    .sort((a, b) => b.timestamp.localeCompare(a.timestamp))
    .slice(0, 30);
}
''')

text = PAGE.read_text()

if 'from "../services/observabilityTimelineService"' not in text:
    text = text.replace(
        'import { getBackendHealth, type BackendHealth } from "../services/backendHealthService";',
        'import { getBackendHealth, type BackendHealth } from "../services/backendHealthService";\nimport { getObservabilityTimeline, type ObservabilityEvent } from "../services/observabilityTimelineService";'
    )

component = r'''
function ObservabilityEventTimeline() {
  const [events, setEvents] = useState<ObservabilityEvent[]>([]);

  const refreshTimeline = useCallback(async () => {
    setEvents(await getObservabilityTimeline());
  }, []);

  useEffect(() => {
    const firstLoad = setTimeout(() => {
      void refreshTimeline();
    }, 0);

    const timer = setInterval(() => {
      void refreshTimeline();
    }, 5000);

    return () => {
      clearTimeout(firstLoad);
      clearInterval(timer);
    };
  }, [refreshTimeline]);

  return (
    <section className="mt-6 rounded-2xl border border-fuchsia-400/30 bg-slate-950/80 p-5 shadow-[0_0_30px_rgba(217,70,239,0.10)]">
      <p className="text-xs uppercase tracking-[0.3em] text-fuchsia-300">
        Observability Timeline
      </p>

      <h2 className="mt-1 text-2xl font-bold text-white">
        Recent Frontend + Runtime Events
      </h2>

      <div className="mt-4 grid gap-2">
        {events.map((event) => (
          <div
            key={event.id}
            className="rounded-xl border border-slate-800 bg-slate-900/80 p-3 text-sm"
          >
            <div className="flex items-center justify-between gap-3">
              <p className="font-bold text-white">
                {event.label}
              </p>

              <span className="rounded-full border border-fuchsia-400/30 px-2 py-1 text-xs text-fuchsia-200">
                {event.source} · {event.status}
              </span>
            </div>

            <p className="mt-1 text-xs text-slate-400">
              {event.detail}
            </p>

            <p className="mt-1 text-xs text-slate-500">
              {event.timestamp}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}
'''

if "function ObservabilityEventTimeline()" not in text:
    text = text.replace("function FloatingChatWidget()", component + "\n\nfunction FloatingChatWidget()", 1)

if "<ObservabilityEventTimeline />" not in text:
    text = text.replace("<FrontendObservabilityPanel />", "<FrontendObservabilityPanel />\n      <ObservabilityEventTimeline />", 1)

PAGE.write_text(text)
print("patched Phase 24C observability event timeline")
