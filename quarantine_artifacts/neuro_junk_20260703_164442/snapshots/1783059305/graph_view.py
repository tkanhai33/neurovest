def render_ascii_graph(graph):

    output = []

    for file, imports in graph.items():
        short = file.split("/")[-1]
        for imp in imports[:3]:
            output.append(f"{short} → {imp}")

    return "\n".join(output)
