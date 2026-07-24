import { getRequestMetrics } from "./requestObservability";
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
