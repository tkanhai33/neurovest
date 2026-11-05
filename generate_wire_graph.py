#!/usr/bin/env python3
"""DOMAIN_LOGIC_V1 unified backend/frontend system network visualization graph builder."""

import json
import urllib.request

import matplotlib.pyplot as plt
import networkx as nx


LIVE_GRAPH_URL = "http://127.0.0.1:8000/api/v1/graph/live"




def fetch_dependency_graph():
    path = "runtime/repo_memory/dependency_graph_v1.json"
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return {"nodes": []}


def fetch_dependency_overlay():
    path = "runtime/repo_memory/dependency_topology_overlay_v1.json"
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return {"topology_overlay_edges": []}


def fetch_live_graph_state():
    try:
        with urllib.request.urlopen(LIVE_GRAPH_URL, timeout=2) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        return {"nodes": {}, "edges": {}, "events": []}


def build_neurovest_topology_graph():
    G = nx.DiGraph()
    live_state = fetch_live_graph_state()
    dependency_overlay = fetch_dependency_overlay()
    dependency_graph = fetch_dependency_graph()

    frontend_nodes = {
        "UI Gateway\n(Next.js React)": "http://localhost:3001",
        "Pillar 1: WS Log\n(Telemetry Receiver)": "ws://stream/orders",
        "Pillar 2: Analytics\n(Stats Display)": "GET /api/v1/analytics",
        "Pillar 3: Table\n(Warehouse View)": "GET /api/v1/positions",
        "Pillar 4: Console\n(Sandbox Control)": "POST /sandbox/override",
    }

    backend_nodes = {
        "FastAPI Gateway\n(app.main)": "Port 8000 / 0.0.0.0",
        "Chat Runtime\n(chat_public)": "POST /api/v1/chat",
        "Intent Engine\n(Ollama Router)": "LLM command parsing",
        "Execution Engine\n(execution.paper_broker)": "Trade Parameter Sizing",
        "Event Bus Broker\n(events.broker)": "SystemEventBus Stream",
        "Audit Daemon\n(portfolio.reconciliation)": "Background Drift Audit",
        "Equity Calculator\n(portfolio.accounting)": "Live Capital Tracker",
        "Drawdown Guard\n(risk.drawdown_guard)": "Trailing Risk Supervisor",
        "Repo Memory\n(repo_memory)": "Repository awareness index",
        "Research Database\n(research_db)": "Training corpus",
        "Market Data\n(market_data)": "Historical/live pricing",
        "Strategy Engine\n(strategy.engine)": "Signal generation",
        "Risk Engine\n(risk)": "Trade approval",
    }

    storage_nodes = {
        "PostgreSQL Container\n(journal_ledger.ledger)": "Relational Row Persistence\nOrderHistory & PortfolioInventory"
    }

    live_nodes = {
        "Live Graph State\n(/api/v1/graph/live)": "Runtime node/edge overlay"
    }

    for node, desc in frontend_nodes.items():
        G.add_node(node, layer="frontend", desc=desc, live_key=None)

    for node, desc in backend_nodes.items():
        live_key = None
        if "Chat Runtime" in node:
            live_key = "chat_public"
        elif "Intent Engine" in node:
            live_key = "intent_engine"
        elif "Execution Engine" in node:
            live_key = "execution"

        G.add_node(node, layer="backend", desc=desc, live_key=live_key)

    for node, desc in storage_nodes.items():
        G.add_node(node, layer="storage", desc=desc, live_key="ledger")

    for node, desc in live_nodes.items():
        G.add_node(node, layer="observability", desc=desc, live_key=None)

    G.add_edge("UI Gateway\n(Next.js React)", "Pillar 1: WS Log\n(Telemetry Receiver)")
    G.add_edge("UI Gateway\n(Next.js React)", "Pillar 2: Analytics\n(Stats Display)")
    G.add_edge("UI Gateway\n(Next.js React)", "Pillar 3: Table\n(Warehouse View)")
    G.add_edge("UI Gateway\n(Next.js React)", "Pillar 4: Console\n(Sandbox Control)")

    G.add_edge("Pillar 1: WS Log\n(Telemetry Receiver)", "FastAPI Gateway\n(app.main)", type="WebSocket")
    G.add_edge("Pillar 2: Analytics\n(Stats Display)", "FastAPI Gateway\n(app.main)", type="REST")
    G.add_edge("Pillar 3: Table\n(Warehouse View)", "FastAPI Gateway\n(app.main)", type="REST")
    G.add_edge("Pillar 4: Console\n(Sandbox Control)", "FastAPI Gateway\n(app.main)", type="REST")

    G.add_edge("FastAPI Gateway\n(app.main)", "Chat Runtime\n(chat_public)")
    G.add_edge("Chat Runtime\n(chat_public)", "Intent Engine\n(Ollama Router)")
    G.add_edge("Intent Engine\n(Ollama Router)", "Execution Engine\n(execution.paper_broker)")

    G.add_edge("Intent Engine\n(Ollama Router)", "Repo Memory\n(repo_memory)")
    G.add_edge("Repo Memory\n(repo_memory)", "Research Database\n(research_db)")
    G.add_edge("Research Database\n(research_db)", "Market Data\n(market_data)")
    G.add_edge("Market Data\n(market_data)", "Strategy Engine\n(strategy.engine)")
    G.add_edge("Strategy Engine\n(strategy.engine)", "Risk Engine\n(risk)")
    G.add_edge("Risk Engine\n(risk)", "Execution Engine\n(execution.paper_broker)")

    G.add_edge("FastAPI Gateway\n(app.main)", "Execution Engine\n(execution.paper_broker)")
    G.add_edge("Execution Engine\n(execution.paper_broker)", "Drawdown Guard\n(risk.drawdown_guard)")
    G.add_edge("Execution Engine\n(execution.paper_broker)", "Event Bus Broker\n(events.broker)")
    G.add_edge("FastAPI Gateway\n(app.main)", "Event Bus Broker\n(events.broker)")

    G.add_edge("Event Bus Broker\n(events.broker)", "Live Graph State\n(/api/v1/graph/live)")
    G.add_edge("Live Graph State\n(/api/v1/graph/live)", "FastAPI Gateway\n(app.main)")

    G.add_edge("Execution Engine\n(execution.paper_broker)", "PostgreSQL Container\n(journal_ledger.ledger)")
    G.add_edge("Audit Daemon\n(portfolio.reconciliation)", "PostgreSQL Container\n(journal_ledger.ledger)")
    G.add_edge("Equity Calculator\n(portfolio.accounting)", "PostgreSQL Container\n(journal_ledger.ledger)")
    G.add_edge("Drawdown Guard\n(risk.drawdown_guard)", "PostgreSQL Container\n(journal_ledger.ledger)")
    G.add_edge("PostgreSQL Container\n(journal_ledger.ledger)", "FastAPI Gateway\n(app.main)")

    # Live runtime propagation path
    G.add_edge("Event Bus Broker\n(events.broker)", "PostgreSQL Container\n(journal_ledger.ledger)")
    G.add_edge("PostgreSQL Container\n(journal_ledger.ledger)", "Equity Calculator\n(portfolio.accounting)")
    G.add_edge("Equity Calculator\n(portfolio.accounting)", "Audit Daemon\n(portfolio.reconciliation)")
    G.add_edge("Audit Daemon\n(portfolio.reconciliation)", "Live Graph State\n(/api/v1/graph/live)")


    # ============================================================
    # PHASE 7E2 FIXED TOPOLOGY ANCHORS
    # ============================================================

    pos = {
        "UI Gateway\n(Next.js React)": (-7.0, 0.0),

        "Pillar 3: Table\n(Warehouse View)": (-6.0, 2.7),
        "Pillar 1: WS Log\n(Telemetry Receiver)": (-6.0, 1.4),
        "Pillar 2: Analytics\n(Stats Display)": (-6.0, 0.1),
        "Pillar 4: Console\n(Sandbox Control)": (-6.0, -1.4),

        "FastAPI Gateway\n(app.main)": (-3.4, 0.0),

        "Chat Runtime\n(chat_public)": (-0.8, 3.5),
        "Intent Engine\n(Ollama Router)": (-0.8, 2.2),
        "Repo Memory\n(repo_memory)": (-0.8, 1.2),
        "Research Database\n(research_db)": (-0.8, 0.2),
        "Market Data\n(market_data)": (-0.8, -0.8),
        "Strategy Engine\n(strategy.engine)": (-0.8, -1.8),
        "Risk Engine\n(risk)": (-0.8, -2.8),
        "Execution Engine\n(execution.paper_broker)": (-0.8, -4.3),

        "Audit Daemon\n(portfolio.reconciliation)": (2.0, 1.4),
        "Equity Calculator\n(portfolio.accounting)": (2.4, -0.8),
        "Event Bus Broker\n(events.broker)": (2.0, -3.2),
        "Drawdown Guard\n(risk.drawdown_guard)": (2.0, -5.6),

        "PostgreSQL Container\n(journal_ledger.ledger)": (5.0, -2.0),
        "Live Graph State\n(/api/v1/graph/live)": (8.2, -2.0),
    }


    plt.figure(figsize=(22, 13), facecolor="#020617")
    ax = plt.gca()
    ax.set_facecolor("#020617")

    active_live_keys = set(live_state.get("nodes", {}).keys())
    live_edges = live_state.get("edges", {})

    colors = []
    node_sizes = []

    for node in G.nodes():
        layer = G.nodes[node]["layer"]
        live_key = G.nodes[node].get("live_key")

        if live_key in active_live_keys:
            colors.append("#facc15")
            node_sizes.append(4200)
        elif layer == "frontend":
            colors.append("#38bdf8")
            node_sizes.append(3200)
        elif layer == "backend":
            colors.append("#34d399")
            node_sizes.append(3200)
        elif layer == "storage":
            colors.append("#a78bfa")
            node_sizes.append(3400)
        else:
            colors.append("#fb7185")
            node_sizes.append(3400)

    nx.draw_networkx_nodes(
        G, pos, node_size=node_sizes, node_color=colors,
        alpha=0.96, edgecolors="#1e293b", linewidths=2
    )

    live_edge_map = {
        "user->chat_public": ("FastAPI Gateway\n(app.main)", "Chat Runtime\n(chat_public)"),
        "chat_public->intent_engine": ("Chat Runtime\n(chat_public)", "Intent Engine\n(Ollama Router)"),
        "intent_engine->execution": ("Intent Engine\n(Ollama Router)", "Execution Engine\n(execution.paper_broker)"),
        "execution->ledger": ("Execution Engine\n(execution.paper_broker)", "PostgreSQL Container\n(journal_ledger.ledger)"),

        "intent_engine->repo_memory":
            ("Intent Engine\n(Ollama Router)",
             "Repo Memory\n(repo_memory)"),

        "repo_memory->research":
            ("Repo Memory\n(repo_memory)",
             "Research Database\n(research_db)"),

        "research->market":
            ("Research Database\n(research_db)",
             "Market Data\n(market_data)"),

        "market->strategy":
            ("Market Data\n(market_data)",
             "Strategy Engine\n(strategy.engine)"),

        "strategy->risk":
            ("Strategy Engine\n(strategy.engine)",
             "Risk Engine\n(risk)"),

        "risk->execution":
            ("Risk Engine\n(risk)",
             "Execution Engine\n(execution.paper_broker)"),

        "execution->events_broker":
            ("Execution Engine\n(execution.paper_broker)",
             "Event Bus Broker\n(events.broker)"),

        "events_broker->journal_ledger":
            ("Event Bus Broker\n(events.broker)",
             "PostgreSQL Container\n(journal_ledger.ledger)"),

        "journal_ledger->portfolio_accounting":
            ("PostgreSQL Container\n(journal_ledger.ledger)",
             "Equity Calculator\n(portfolio.accounting)"),

        "portfolio_accounting->portfolio_reconciliation":
            ("Equity Calculator\n(portfolio.accounting)",
             "Audit Daemon\n(portfolio.reconciliation)"),

        "portfolio_reconciliation->graph_live":
            ("Audit Daemon\n(portfolio.reconciliation)",
             "Live Graph State\n(/api/v1/graph/live)"),
    }

    active_edge_pairs = {
        pair for live_edge, pair in live_edge_map.items()
        if live_edge in live_edges
    }

    default_edges = []
    active_edges = []

    reverse_live_edge_map = {
        pair: live_edge
        for live_edge, pair in live_edge_map.items()
    }

    for edge in G.edges():
        if edge in active_edge_pairs:
            active_edges.append(edge)
        else:
            default_edges.append(edge)

    nx.draw_networkx_edges(
        G, pos, edgelist=default_edges, arrowstyle="-|>",
        arrowsize=18, edge_color="#475569", width=1.6,
        connectionstyle="arc3,rad=0.08"
    )

    dependency_edges = []
    dependency_widths = []

    for dep in dependency_overlay.get("topology_overlay_edges", []):
        src = dep.get("from_topology_node")
        dst = dep.get("to_topology_node")

        if src in G.nodes and dst in G.nodes:
            edge = (src, dst)
            if edge not in dependency_edges:
                dependency_edges.append(edge)
                dependency_widths.append(
                    max(1.0, min(float(dep.get("dependency_count", 1)), 6.0))
                )

    if dependency_edges:
        nx.draw_networkx_edges(
            G, pos, edgelist=dependency_edges, arrowstyle="-|>",
            arrowsize=14, edge_color="#a78bfa", width=dependency_widths,
            style="dashed",
            alpha=0.55,
            connectionstyle="arc3,rad=-0.18"
        )

    if active_edges:
        for edge in active_edges:
            live_key = reverse_live_edge_map.get(edge)
            count = live_edges.get(live_key, 1)

            heat_width = min(12, 3 + count)
            heat_arrow = min(38, 20 + count)

            if count <= 5:
                heat_color = "#facc15"   # yellow
            elif count <= 20:
                heat_color = "#fb923c"   # orange
            elif count <= 50:
                heat_color = "#f97316"   # deep orange
            else:
                heat_color = "#ef4444"   # red

            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=[edge],
                arrowstyle="-|>",
                arrowsize=heat_arrow,
                edge_color=heat_color,
                width=heat_width,
                connectionstyle="arc3,rad=0.08",
            )

    labels = {}

    node_meta = live_state.get("node_meta", {})

    for node in G.nodes():
        base = node
        live_key = G.nodes[node].get("live_key")

        if live_key and live_key in node_meta:
            meta = node_meta[live_key]
            count = meta.get("event_count", 0)
            symbol = meta.get("symbol") or "-"
            event_type = meta.get("last_event_type") or "-"

            labels[node] = f"{base}\ncount: {count}\nsymbol: {symbol}\nevent: {event_type}"
        else:
            labels[node] = base

    nx.draw_networkx_labels(
        G, pos, labels=labels, font_size=7, font_color="#f1f5f9",
        font_weight="bold", font_family="monospace"
    )


    edge_labels = {}

    reverse_live_edge_map = {
        pair: live_edge
        for live_edge, pair in live_edge_map.items()
    }

    for edge in active_edges:
        live_key = reverse_live_edge_map.get(edge)

        if live_key:
            count = live_edges.get(live_key, 0)
            edge_labels[edge] = str(count)

    if edge_labels:
        nx.draw_networkx_edge_labels(
            G,
            pos,
            edge_labels=edge_labels,
            font_size=7,
            font_color="#facc15",
            font_family="monospace",
            bbox=dict(
                facecolor="#020617",
                edgecolor="none",
                alpha=0.7,
            ),
        )


    live_event_count = len(live_state.get("events", []))
    active_node_count = len(active_live_keys)

    plt.title(
        f"NEUROVEST AI-AWARE TOPOLOGY WIRE GRAPH | LIVE NODES: {active_node_count} | LIVE EVENTS: {live_event_count} | DEP HEATMAP ON",
        color="#34d399",
        fontsize=12,
        fontweight="bold",
        pad=20,
        fontfamily="monospace",
    )

    plt.text(
        -6.8,
        -6.15,
        "Yellow = active runtime path | Purple dashed = dependency overlay | Larger nodes = dependency heat",
        color="#facc15",
        fontsize=8,
        fontfamily="monospace",
    )

    plt.axis("off")
    plt.tight_layout()

    output_png = "topology_wire_graph.png"
    plt.savefig(output_png, facecolor=plt.gcf().get_facecolor(), dpi=300, edgecolor="none")
    plt.close()

    print(f"Updated AI-aware topology wire graph generated successfully as '{output_png}'")


if __name__ == "__main__":
    build_neurovest_topology_graph()
