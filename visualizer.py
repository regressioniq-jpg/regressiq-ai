import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx


def risk_heatmap(risk_assessment: dict):
    module_risk = risk_assessment.get("module_risk", {})
    rows = []

    for module, details in module_risk.items():
        rows.append(
            {
                "module": module,
                "risk": details["risk"],
                "score": details["score"]
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame([{"module": "No modules", "risk": "Low", "score": 0}])

    fig = px.bar(
        df,
        x="module",
        y="score",
        color="risk",
        title="Regression Risk by Module",
        text="risk"
    )
    fig.update_layout(xaxis_title="Module", yaxis_title="Risk Score")
    return fig


def dependency_graph(graph, impacted_modules, risk_assessment):
    pos = nx.spring_layout(graph, seed=42)

    edge_x = []
    edge_y = []

    for edge in graph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line=dict(width=1),
            hoverinfo="none"
        )
    )

    node_x = []
    node_y = []
    node_text = []
    node_color = []

    module_risk = risk_assessment.get("module_risk", {})

    for node in graph.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

        risk = module_risk.get(node, {}).get("risk")
        if risk == "High":
            node_color.append("red")
        elif node in impacted_modules:
            node_color.append("orange")
        else:
            node_color.append("lightblue")

    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=node_text,
            textposition="top center",
            marker=dict(size=22, color=node_color, line=dict(width=1, color="black")),
            hoverinfo="text"
        )
    )

    fig.update_layout(
        title="Module Dependency Graph",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False)
    )

    return fig