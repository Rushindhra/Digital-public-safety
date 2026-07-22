"""Fraud-network analytics using NetworkX."""
from typing import Any
import networkx as nx


def analyse_graph(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
    graph = nx.Graph()
    for node in nodes:
        node_id = str(node.get("id", "")).strip()
        if not node_id:
            raise ValueError("Every node requires a non-empty id")
        graph.add_node(node_id, **{k: v for k, v in node.items() if k != "id"})
    for edge in edges:
        source, target = str(edge.get("source", "")), str(edge.get("target", ""))
        if source not in graph or target not in graph:
            raise ValueError(f"Unknown edge endpoint: {source} -> {target}")
        graph.add_edge(source, target, **{k: v for k, v in edge.items() if k not in {"source", "target"}})
    communities = [sorted(c) for c in nx.community.greedy_modularity_communities(graph)] if graph.number_of_edges() else [[n] for n in graph.nodes]
    centrality = nx.betweenness_centrality(graph)
    masterminds = sorted(({"id": k, "centrality": round(v, 4), "degree": graph.degree(k)} for k, v in centrality.items()), key=lambda x: (x["centrality"], x["degree"]), reverse=True)[:10]
    return {"node_count": graph.number_of_nodes(), "edge_count": graph.number_of_edges(),
        "components": nx.number_connected_components(graph), "communities": communities,
        "mastermind_candidates": masterminds, "density": round(nx.density(graph), 4)}

