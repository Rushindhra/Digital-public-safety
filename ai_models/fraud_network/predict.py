"""Inference wrapper for fraud network graph analysis."""
import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[2] / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.graph import analyse_graph
from utils import load_edges, load_nodes


def predict(nodes: list[dict], edges: list[dict]) -> dict:
    return analyse_graph(nodes, edges)


if __name__ == "__main__":
    dataset = Path(__file__).resolve().parents[2] / "datasets" / "fraud_network.json"
    data = json.loads(dataset.read_text(encoding="utf-8"))
    print(json.dumps(predict(load_nodes(data), load_edges(data)), indent=2))
