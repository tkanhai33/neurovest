export type GraphActivationStatus =
  | "idle"
  | "active"
  | "completed"
  | "blocked"
  | "failed"
  | "error"
  | string;

export type GraphRecordType =
  | "node_activation"
  | "edge_activation"
  | string;

export type LiveGraphNode = {
  id: string;
  name?: string;
  stack?: string;
  layer?: string;
  status?: GraphActivationStatus;
  event_count?: number;
  request_count?: number;
  success_count?: number;
  failure_count?: number;
  unauthorized_count?: number;
  forbidden_count?: number;
  http_error_count?: number;
  average_latency_ms?: number;
  minimum_latency_ms?: number;
  maximum_latency_ms?: number;
  p95_latency_ms?: number;
  last_latency_ms?: number;
  bytes_in?: number;
  bytes_out?: number;
  active_requests?: number;
  health?: string;
  declared?: boolean;
  observed?: boolean;
  materialized_from_edge?: boolean;
  materialization_state?: string;
  component_type?: string;
  source_file?: string | null;
  first_seen?: string;
  last_seen?: string;
  last_event_type?: string;
  last_trace_id?: string;
  symbol?: string | null;
  message?: string | null;
};

export type LiveGraphEdge = {
  id: string;
  from?: string;
  to?: string;
  type?: string;
  status?: GraphActivationStatus;
  count?: number;
  request_count?: number;
  success_count?: number;
  failure_count?: number;
  unauthorized_count?: number;
  forbidden_count?: number;
  http_error_count?: number;
  average_latency_ms?: number;
  p95_latency_ms?: number;
  bytes_in?: number;
  bytes_out?: number;
  health?: string;
  declared?: boolean;
  observed?: boolean;
  materialization_state?: string;
  relation?: string;
  last_seen?: string;
  last_trace_id?: string;
  source_layer?: string;
  destination_layer?: string;
  symbol?: string | null;
};

export type LiveGraphFlowStep = {
  sequence: number;
  record_type: GraphRecordType;
  trace_id: string;
  event_type?: string;
  status?: GraphActivationStatus;
  timestamp?: string;
  symbol?: string | null;

  node?: string;
  layer?: string;
  stack?: string;
  message?: string | null;

  edge_id?: string;
  from?: string;
  to?: string;
  source_layer?: string;
  destination_layer?: string;
};

export type LiveGraphTrace = {
  trace_id: string;
  symbol?: string | null;
  started_at?: string | null;
  last_seen?: string | null;
  step_count: number;
  steps: LiveGraphFlowStep[];
};

export type LiveGraphContract = {
  phase?: string;
  version?: number;
  event_driven?: boolean;
  synthetic_activations?: boolean;
  metric_aggregation?: boolean;
  supported_metrics?: string[];
  declared_topology?: boolean;
  edge_endpoint_materialization?: boolean;
  declared_edges_are_runtime_activity?: boolean;
  layers?: string[];
};

export type LiveGraphResponse = {
  status?: string;
  sequence: number;
  nodes: LiveGraphNode[];
  edges: LiveGraphEdge[];
  events: LiveGraphFlowStep[];
  recent_flows: LiveGraphFlowStep[];
  traces: LiveGraphTrace[];
  contract?: LiveGraphContract;
  topology?: {
    declared_node_count?: number;
    observed_node_count?: number;
    declared_edge_count?: number;
    observed_edge_count?: number;
    layers?: string[];
    generated_at?: string;
  };
  error?: string;
};

type RawGraph = {
  status?: string;
  sequence?: number;

  nodes?: Record<string, string> | LiveGraphNode[];
  node_meta?: Record<string, Partial<LiveGraphNode>>;

  edges?: Record<string, number> | LiveGraphEdge[];
  edge_meta?: Record<string, Partial<LiveGraphEdge>>;

  events?: LiveGraphFlowStep[];
  recent_flows?: LiveGraphFlowStep[];
  traces?: LiveGraphTrace[];
  contract?: LiveGraphContract;
  topology?: LiveGraphResponse["topology"];
  error?: string;
};

function normalizeLayer(layer?: string): string {
  const cleanLayer = String(layer || "UNASSIGNED").toUpperCase();

  if (/^L[0-7]$/.test(cleanLayer)) {
    return cleanLayer;
  }

  return "UNASSIGNED";
}

function normalizeStep(
  step: LiveGraphFlowStep,
  index: number
): LiveGraphFlowStep {
  return {
    ...step,
    sequence: Number(step.sequence ?? index),
    trace_id: String(step.trace_id || "unknown"),
    record_type: String(step.record_type || "unknown"),
    layer:
      step.record_type === "node_activation"
        ? normalizeLayer(step.layer)
        : step.layer,
    source_layer:
      step.record_type === "edge_activation"
        ? normalizeLayer(step.source_layer)
        : step.source_layer,
    destination_layer:
      step.record_type === "edge_activation"
        ? normalizeLayer(step.destination_layer)
        : step.destination_layer,
  };
}

export function normalizeLiveGraph(
  raw: RawGraph
): LiveGraphResponse {
  const nodeMeta = raw.node_meta || {};
  const edgeMeta = raw.edge_meta || {};

  const nodes: LiveGraphNode[] = Array.isArray(raw.nodes)
    ? raw.nodes.map((node, index) => ({
        ...node,
        id: node.id || node.name || `node-${index}`,
        layer: normalizeLayer(node.layer),
      }))
    : Object.entries(raw.nodes || {}).map(([id, status]) => ({
        id,
        status,
        ...nodeMeta[id],
        layer: normalizeLayer(nodeMeta[id]?.layer),
      }));

  const edges: LiveGraphEdge[] = Array.isArray(raw.edges)
    ? raw.edges.map((edge, index) => ({
        ...edge,
        id:
          edge.id ||
          `${edge.from || "unknown"}->${edge.to || index}`,
        source_layer: normalizeLayer(edge.source_layer),
        destination_layer: normalizeLayer(
          edge.destination_layer
        ),
      }))
    : Object.entries(raw.edges || {}).map(([id, count]) => {
        const meta = edgeMeta[id] || {};
        const [fallbackFrom, fallbackTo] = id.split("->", 2);

        return {
          id,
          count,
          from: meta.from || fallbackFrom,
          to: meta.to || fallbackTo,
          ...meta,
          source_layer: normalizeLayer(meta.source_layer),
          destination_layer: normalizeLayer(
            meta.destination_layer
          ),
        };
      });

  const recentFlows = (raw.recent_flows || [])
    .map(normalizeStep)
    .sort((left, right) => left.sequence - right.sequence);

  const traces = (raw.traces || []).map((trace) => ({
    ...trace,
    trace_id: String(trace.trace_id),
    step_count: Number(
      trace.step_count ?? trace.steps?.length ?? 0
    ),
    steps: (trace.steps || [])
      .map(normalizeStep)
      .sort((left, right) => left.sequence - right.sequence),
  }));

  return {
    status: raw.status || "ok",
    sequence: Number(raw.sequence || 0),
    nodes,
    edges,
    events: (raw.events || []).map(normalizeStep),
    recent_flows: recentFlows,
    traces,
    contract: raw.contract,
    topology: raw.topology,
    error: raw.error,
  };
}

export async function getLiveGraph(): Promise<LiveGraphResponse> {
  const response = await fetch("/api/v1/graph/live", {
    cache: "no-store",
  });

  const raw = (await response.json()) as RawGraph;

  if (!response.ok) {
    throw new Error(
      raw.error ||
        `Live graph request failed with status ${response.status}`
    );
  }

  return normalizeLiveGraph(raw);
}
