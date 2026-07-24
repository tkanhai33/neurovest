"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  getLiveGraph,
  type GraphActivationStatus,
  type LiveGraphEdge,
  type LiveGraphNode,
  type LiveGraphResponse,
  type LiveGraphTrace,
} from "../../../services/graphService";

const GRAPH_LAYERS = [
  "L7",
  "L6",
  "L5",
  "L4",
  "L3",
  "L2",
  "L1",
  "L0",
  "UNASSIGNED",
] as const;

const LAYER_LABELS: Record<string, string> = {
  L7: "Tests / Certification",
  L6: "Frontend",
  L5: "API",
  L4: "Runtime",
  L3: "Facade / Routing",
  L2: "Domain",
  L1: "Security",
  L0: "Adapters",
  UNASSIGNED: "Historical / Unassigned",
};

const EMPTY_GRAPH: LiveGraphResponse = {
  status: "idle",
  sequence: 0,
  nodes: [],
  edges: [],
  events: [],
  recent_flows: [],
  traces: [],
};

function statusClasses(
  status?: GraphActivationStatus,
  highlighted = false
): string {
  if (highlighted) {
    return "border-cyan-300 bg-cyan-400/15 text-cyan-100 shadow-[0_0_28px_rgba(34,211,238,0.40)] neurovest-graph-node-pulse";
  }

  switch (status) {
    case "declared":
      return "border-slate-700 border-dashed bg-slate-950/45 text-slate-400";
    case "qualified":
      return "border-violet-400/40 bg-violet-950/25 text-violet-100";
    case "completed":
      return "border-emerald-400/40 bg-emerald-950/25 text-emerald-100";
    case "blocked":
      return "border-amber-400/45 bg-amber-950/25 text-amber-100";
    case "failed":
    case "error":
      return "border-red-400/45 bg-red-950/25 text-red-100";
    case "active":
      return "border-fuchsia-400/40 bg-fuchsia-950/25 text-fuchsia-100";
    default:
      return "border-slate-800 bg-slate-900/65 text-slate-200";
  }
}

function statusDotClass(
  status?: GraphActivationStatus,
  highlighted = false
): string {
  if (highlighted) {
    return "bg-cyan-300 shadow-[0_0_14px_rgba(34,211,238,1)]";
  }

  switch (status) {
    case "declared":
      return "bg-slate-700";
    case "qualified":
      return "bg-violet-400";
    case "completed":
      return "bg-emerald-400";
    case "blocked":
      return "bg-amber-400";
    case "failed":
    case "error":
      return "bg-red-400";
    case "active":
      return "bg-fuchsia-400";
    default:
      return "bg-slate-600";
  }
}

function formatTimestamp(value?: string | null): string {
  if (!value) {
    return "—";
  }

  const parsed = new Date(value);

  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return parsed.toLocaleString();
}

function GraphNodeCard({
  node,
  highlighted,
}: {
  node: LiveGraphNode;
  highlighted: boolean;
}) {
  return (
    <div
      className={`min-w-[220px] rounded-2xl border p-4 transition-all duration-300 ${statusClasses(
        node.status,
        highlighted
      )}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="font-black">{node.name || node.id}</p>
          <p className="mt-1 text-xs opacity-65">
            {node.stack || "UNASSIGNED"}
          </p>
        </div>

        <span
          className={`mt-1 h-2.5 w-2.5 shrink-0 rounded-full ${statusDotClass(
            node.status,
            highlighted
          )}`}
        />
      </div>

      <div className="mt-3 grid gap-1 text-xs opacity-75">
        <p>State: {node.status || "idle"}</p>
        <p>
          Materialization:{" "}
          {node.observed ? "OBSERVED" : "DECLARED"}
        </p>
        <p>
          Type: {node.component_type || "component"}
        </p>
        <p>Requests: {node.request_count ?? node.event_count ?? 0}</p>
        <p>
          Success / Failure: {node.success_count ?? 0} /{" "}
          {node.failure_count ?? 0}
        </p>
        <p>
          Latency avg / p95:{" "}
          {node.average_latency_ms?.toFixed(1) || "0.0"}ms /{" "}
          {node.p95_latency_ms?.toFixed(1) || "0.0"}ms
        </p>
        <p>
          Auth 401 / 403: {node.unauthorized_count ?? 0} /{" "}
          {node.forbidden_count ?? 0}
        </p>
        <p>Health: {node.health || "unknown"}</p>
        <p>Last: {node.last_event_type || "—"}</p>
        <p>Symbol: {node.symbol || "—"}</p>
      </div>
    </div>
  );
}

function LayerLane({
  layer,
  nodes,
  activeNode,
}: {
  layer: string;
  nodes: LiveGraphNode[];
  activeNode?: string;
}) {
  return (
    <section className="grid gap-4 rounded-3xl border border-slate-800/90 bg-slate-950/65 p-4 lg:grid-cols-[190px_1fr]">
      <div className="rounded-2xl border border-cyan-400/15 bg-slate-900/70 p-4">
        <p className="text-2xl font-black text-cyan-200">
          {layer}
        </p>
        <p className="mt-1 text-xs uppercase tracking-[0.16em] text-slate-500">
          {LAYER_LABELS[layer]}
        </p>
        <p className="mt-3 text-xs text-slate-500">
          {nodes.length} node{nodes.length === 1 ? "" : "s"}
        </p>
      </div>

      <div className="flex min-w-0 gap-3 overflow-x-auto pb-1">
        {nodes.length === 0 ? (
          <div className="flex min-h-[132px] min-w-[220px] items-center rounded-2xl border border-dashed border-slate-800 px-4 text-sm text-slate-600">
            No recorded nodes in this layer.
          </div>
        ) : (
          nodes.map((node) => (
            <GraphNodeCard
              key={node.id}
              node={node}
              highlighted={activeNode === node.id}
            />
          ))
        )}
      </div>
    </section>
  );
}

function TraceSelector({
  traces,
  selectedTraceId,
  setSelectedTraceId,
}: {
  traces: LiveGraphTrace[];
  selectedTraceId: string;
  setSelectedTraceId: (traceId: string) => void;
}) {
  return (
    <section className="rounded-3xl border border-fuchsia-400/20 bg-slate-950/80 p-5">
      <p className="text-xs uppercase tracking-[0.25em] text-fuchsia-300">
        Recorded Traces
      </p>

      <h3 className="mt-1 text-xl font-black text-white">
        Runtime Flow Selection
      </h3>

      <div className="mt-5 grid max-h-[430px] gap-3 overflow-y-auto pr-1">
        {traces.length === 0 ? (
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 text-sm text-slate-400">
            No trace-correlated runtime flows recorded yet.
          </div>
        ) : (
          traces.map((trace) => {
            const selected =
              trace.trace_id === selectedTraceId;

            return (
              <button
                key={trace.trace_id}
                type="button"
                onClick={() =>
                  setSelectedTraceId(trace.trace_id)
                }
                className={
                  selected
                    ? "rounded-2xl border border-fuchsia-300 bg-fuchsia-500/15 p-4 text-left shadow-[0_0_24px_rgba(217,70,239,0.18)]"
                    : "rounded-2xl border border-slate-800 bg-slate-900/60 p-4 text-left hover:border-slate-700"
                }
              >
                <div className="flex items-center justify-between gap-3">
                  <span className="truncate text-sm font-black text-white">
                    {trace.trace_id}
                  </span>

                  <span className="rounded-full border border-slate-700 px-2 py-1 text-xs text-slate-300">
                    {trace.step_count} steps
                  </span>
                </div>

                <div className="mt-2 grid gap-1 text-xs text-slate-500">
                  <p>Symbol: {trace.symbol || "—"}</p>
                  <p>{formatTimestamp(trace.last_seen)}</p>
                </div>
              </button>
            );
          })
        )}
      </div>
    </section>
  );
}

function EdgeFlowCard({
  edge,
  highlighted,
}: {
  edge: LiveGraphEdge;
  highlighted: boolean;
}) {
  return (
    <div
      className={
        highlighted
          ? "rounded-2xl border border-cyan-300 bg-cyan-500/15 p-4 shadow-[0_0_24px_rgba(34,211,238,0.28)] neurovest-graph-edge-pulse"
          : "rounded-2xl border border-slate-800 bg-slate-900/60 p-4"
      }
    >
      <div className="flex flex-wrap items-center gap-2">
        <span className="font-black text-white">
          {edge.from || "unknown"}
        </span>

        <span className="text-cyan-300">→</span>

        <span className="font-black text-white">
          {edge.to || "unknown"}
        </span>
      </div>

      <div className="mt-2 grid gap-1 text-xs text-slate-500">
        <p>
          {edge.source_layer || "UNASSIGNED"} →{" "}
          {edge.destination_layer || "UNASSIGNED"}
        </p>
        <p>
          Materialization:{" "}
          {edge.observed ? "OBSERVED" : "DECLARED"}
        </p>
        <p>Relation: {edge.relation || edge.type || "dependency"}</p>
        <p>Requests: {edge.request_count ?? edge.count ?? 0}</p>
        <p>
          Success / Failure: {edge.success_count ?? 0} /{" "}
          {edge.failure_count ?? 0}
        </p>
        <p>
          Latency avg / p95:{" "}
          {edge.average_latency_ms?.toFixed(1) || "0.0"}ms /{" "}
          {edge.p95_latency_ms?.toFixed(1) || "0.0"}ms
        </p>
        <p>Status: {edge.status || "historical"}</p>
        <p>Health: {edge.health || "unknown"}</p>
        <p>Symbol: {edge.symbol || "—"}</p>
      </div>
    </div>
  );
}

function PlaybackTimeline({
  trace,
  playbackIndex,
}: {
  trace?: LiveGraphTrace;
  playbackIndex: number;
}) {
  const steps = trace?.steps || [];

  return (
    <section className="rounded-3xl border border-cyan-400/20 bg-slate-950/80 p-5">
      <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">
        Ordered Activation Log
      </p>

      <h3 className="mt-1 text-xl font-black text-white">
        Trace Playback
      </h3>

      <div className="mt-5 grid max-h-[540px] gap-3 overflow-y-auto pr-1">
        {steps.length === 0 ? (
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 text-sm text-slate-400">
            Select a trace to inspect its ordered activation
            records.
          </div>
        ) : (
          steps.map((step, index) => {
            const active = index === playbackIndex;
            const passed = index < playbackIndex;

            return (
              <div
                key={`${step.trace_id}-${step.sequence}-${index}`}
                className={
                  active
                    ? "rounded-2xl border border-cyan-300 bg-cyan-500/15 p-4 shadow-[0_0_24px_rgba(34,211,238,0.24)]"
                    : passed
                      ? "rounded-2xl border border-emerald-400/20 bg-emerald-950/15 p-4"
                      : "rounded-2xl border border-slate-800 bg-slate-900/60 p-4"
                }
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
                      Step {index + 1} · {step.record_type}
                    </p>

                    <p className="mt-1 font-black text-white">
                      {step.record_type === "edge_activation"
                        ? `${step.from || "unknown"} → ${
                            step.to || "unknown"
                          }`
                        : step.node || "unknown"}
                    </p>
                  </div>

                  <span className="rounded-full border border-slate-700 px-2 py-1 text-xs text-slate-300">
                    #{step.sequence}
                  </span>
                </div>

                <div className="mt-3 grid gap-1 text-xs text-slate-500">
                  <p>Event: {step.event_type || "—"}</p>
                  <p>Status: {step.status || "—"}</p>
                  <p>Symbol: {step.symbol || "—"}</p>
                  <p>{formatTimestamp(step.timestamp)}</p>
                </div>
              </div>
            );
          })
        )}
      </div>
    </section>
  );
}

export default function GraphWorkspacePanel() {
  const [graph, setGraph] =
    useState<LiveGraphResponse>(EMPTY_GRAPH);

  const [loading, setLoading] = useState(false);
  const [selectedTraceId, setSelectedTraceId] =
    useState("");

  const [playbackIndex, setPlaybackIndex] = useState(0);
  const [playing, setPlaying] = useState(true);

  const loadGraph = useCallback(async () => {
    setLoading(true);

    try {
      const nextGraph = await getLiveGraph();

      setGraph(nextGraph);

      setSelectedTraceId((current) => {
        if (
          current &&
          nextGraph.traces.some(
            (trace) => trace.trace_id === current
          )
        ) {
          return current;
        }

        return nextGraph.traces[0]?.trace_id || "";
      });
    } catch (error) {
      setGraph({
        ...EMPTY_GRAPH,
        status: "error",
        error: String(error),
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const firstLoad = setTimeout(
      () => void loadGraph(),
      0
    );

    const timer = setInterval(
      () => void loadGraph(),
      2000
    );

    return () => {
      clearTimeout(firstLoad);
      clearInterval(timer);
    };
  }, [loadGraph]);

  const selectedTrace = useMemo(
    () =>
      graph.traces.find(
        (trace) => trace.trace_id === selectedTraceId
      ),
    [graph.traces, selectedTraceId]
  );

  useEffect(() => {
    const stepCount = selectedTrace?.steps.length || 0;

    if (!playing || stepCount <= 1) {
      return;
    }

    const timer = setInterval(() => {
      setPlaybackIndex((current) => {
        if (current >= stepCount - 1) {
          return 0;
        }

        return current + 1;
      });
    }, 900);

    return () => clearInterval(timer);
  }, [playing, selectedTrace]);

  const activeStep =
    selectedTrace?.steps[playbackIndex];

  const activeNode =
    activeStep?.record_type === "node_activation"
      ? activeStep.node
      : undefined;

  const activeEdgeId =
    activeStep?.record_type === "edge_activation"
      ? activeStep.edge_id ||
        `${activeStep.from}->${activeStep.to}`
      : undefined;

  const nodesByLayer = useMemo(() => {
    const grouped = new Map<string, LiveGraphNode[]>();

    for (const layer of GRAPH_LAYERS) {
      grouped.set(layer, []);
    }

    for (const node of graph.nodes) {
      const layer = GRAPH_LAYERS.includes(
        node.layer as (typeof GRAPH_LAYERS)[number]
      )
        ? String(node.layer)
        : "UNASSIGNED";

      grouped.get(layer)?.push(node);
    }

    for (const nodes of grouped.values()) {
      nodes.sort((left, right) =>
        left.id.localeCompare(right.id)
      );
    }

    return grouped;
  }, [graph.nodes]);

  const visibleEdges = useMemo(() => {
    const traceEdgeIds = new Set(
      (selectedTrace?.steps || [])
        .filter(
          (step) =>
            step.record_type === "edge_activation"
        )
        .map(
          (step) =>
            step.edge_id ||
            `${step.from || "unknown"}->${
              step.to || "unknown"
            }`
        )
    );

    if (traceEdgeIds.size === 0) {
      return graph.edges;
    }

    return graph.edges.filter((edge) =>
      traceEdgeIds.has(edge.id)
    );
  }, [graph.edges, selectedTrace]);

  const contractVerified =
    graph.contract?.event_driven === true &&
    graph.contract?.synthetic_activations === false &&
    graph.contract?.declared_topology === true &&
    graph.contract?.edge_endpoint_materialization === true;

  return (
    <section className="mt-6 space-y-6">
      <section className="overflow-hidden rounded-3xl border border-cyan-400/30 bg-slate-950/80 shadow-[0_0_42px_rgba(34,211,238,0.10)]">
        <div className="border-b border-slate-800 bg-gradient-to-r from-cyan-500/10 via-fuchsia-500/10 to-transparent p-5">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-cyan-300">
                Active Node Flow Graph
              </p>

              <h2 className="mt-1 text-3xl font-black text-white">
                Layered Runtime Activation
              </h2>

              <p className="mt-2 max-w-4xl text-sm text-slate-400">
                Declared architecture and observed runtime activity
                grouped by L0–L7. Dashed nodes are approved but idle.
                Playback highlights only timestamped real trace records.
              </p>
            </div>

            <button
              type="button"
              onClick={() => void loadGraph()}
              disabled={loading}
              className="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-black text-slate-950 disabled:opacity-60"
            >
              {loading ? "Refreshing" : "Refresh"}
            </button>
          </div>
        </div>

        <div className="grid gap-3 p-5 md:grid-cols-2 xl:grid-cols-5">
          {[
            [
              "Graph",
              graph.status || "unknown",
              "text-cyan-300",
            ],
            [
              "Sequence",
              String(graph.sequence),
              "text-white",
            ],
            [
              "Nodes",
              String(graph.nodes.length),
              "text-emerald-300",
            ],
            [
              "Edges",
              String(graph.edges.length),
              "text-fuchsia-300",
            ],
            [
              "Contract",
              contractVerified ? "VERIFIED" : "UNVERIFIED",
              contractVerified
                ? "text-emerald-300"
                : "text-amber-300",
            ],
          ].map(([label, value, color]) => (
            <div
              key={label}
              className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4"
            >
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                {label}
              </p>
              <p
                className={`mt-2 break-all text-2xl font-black ${color}`}
              >
                {value}
              </p>
            </div>
          ))}
        </div>
      </section>

      {graph.error && (
        <section className="rounded-3xl border border-red-400/30 bg-red-950/20 p-5 text-sm text-red-200">
          {graph.error}
        </section>
      )}

      <section className="grid gap-6 xl:grid-cols-[0.72fr_1.28fr]">
        <TraceSelector
          traces={graph.traces}
          selectedTraceId={selectedTraceId}
          setSelectedTraceId={(traceId) => {
            setSelectedTraceId(traceId);
            setPlaybackIndex(0);
            setPlaying(true);
          }}
        />

        <section className="rounded-3xl border border-cyan-400/20 bg-slate-950/80 p-5">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">
                Playback Control
              </p>
              <h3 className="mt-1 text-xl font-black text-white">
                {selectedTrace?.trace_id ||
                  "No trace selected"}
              </h3>
            </div>

            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() =>
                  setPlaybackIndex((current) =>
                    Math.max(0, current - 1)
                  )
                }
                disabled={!selectedTrace}
                className="rounded-xl border border-slate-700 px-3 py-2 text-xs font-bold text-slate-300 disabled:opacity-40"
              >
                Previous
              </button>

              <button
                type="button"
                onClick={() =>
                  setPlaying((current) => !current)
                }
                disabled={!selectedTrace}
                className="rounded-xl border border-cyan-400/30 px-3 py-2 text-xs font-bold text-cyan-200 disabled:opacity-40"
              >
                {playing ? "Pause" : "Play"}
              </button>

              <button
                type="button"
                onClick={() =>
                  setPlaybackIndex((current) =>
                    Math.min(
                      (selectedTrace?.steps.length || 1) -
                        1,
                      current + 1
                    )
                  )
                }
                disabled={!selectedTrace}
                className="rounded-xl border border-slate-700 px-3 py-2 text-xs font-bold text-slate-300 disabled:opacity-40"
              >
                Next
              </button>
            </div>
          </div>

          <div className="mt-5 grid gap-3 md:grid-cols-4">
            {[
              [
                "Symbol",
                selectedTrace?.symbol || "—",
              ],
              [
                "Step",
                selectedTrace
                  ? `${playbackIndex + 1}/${
                      selectedTrace.steps.length
                    }`
                  : "—",
              ],
              [
                "Node / Edge",
                activeStep?.record_type ===
                "edge_activation"
                  ? `${activeStep.from} → ${activeStep.to}`
                  : activeStep?.node || "—",
              ],
              [
                "Status",
                activeStep?.status || "—",
              ],
            ].map(([label, value]) => (
              <div
                key={label}
                className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4"
              >
                <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
                  {label}
                </p>
                <p className="mt-2 break-all text-sm font-black text-white">
                  {value}
                </p>
              </div>
            ))}
          </div>
        </section>
      </section>

      <section className="space-y-4">
        {GRAPH_LAYERS.map((layer) => (
          <LayerLane
            key={layer}
            layer={layer}
            nodes={nodesByLayer.get(layer) || []}
            activeNode={activeNode}
          />
        ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-[1fr_0.9fr]">
        <section className="rounded-3xl border border-cyan-400/20 bg-slate-950/80 p-5">
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">
            Dependency Activations
          </p>

          <h3 className="mt-1 text-xl font-black text-white">
            Recorded Edges
          </h3>

          <div className="mt-5 grid gap-3 md:grid-cols-2">
            {visibleEdges.length === 0 ? (
              <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 text-sm text-slate-400">
                No dependency edges are recorded for this
                trace.
              </div>
            ) : (
              visibleEdges.map((edge) => (
                <EdgeFlowCard
                  key={edge.id}
                  edge={edge}
                  highlighted={edge.id === activeEdgeId}
                />
              ))
            )}
          </div>
        </section>

        <PlaybackTimeline
          trace={selectedTrace}
          playbackIndex={playbackIndex}
        />
      </section>

      <section className="rounded-3xl border border-amber-400/20 bg-amber-950/10 p-5">
        <p className="text-xs uppercase tracking-[0.25em] text-amber-300">
          Graph Truth Boundary
        </p>

        <p className="mt-3 text-sm leading-6 text-slate-300">
          Declared nodes and edges describe approved repository
          architecture and remain visible while idle. They carry zero
          runtime traffic until observed. A node or edge pulses only
          when the selected trace contains its real activation record.
          Declared topology is never presented as current activity.
        </p>
      </section>
    </section>
  );
}
