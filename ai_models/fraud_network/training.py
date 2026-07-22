"""Train fraud-network graph statistics from synthetic transaction data."""
import json
import logging
from pathlib import Path

from utils import load_edges, load_nodes

logger = logging.getLogger(__name__)
DATASET = Path(__file__).resolve().parents[2] / "datasets" / "fraud_network.json"
ARTIFACT = Path(__file__).resolve().parent / "artifacts" / "graph_stats.json"


def train() -> dict:
    data = json.loads(DATASET.read_text(encoding="utf-8"))
    nodes = load_nodes(data)
    edges = load_edges(data)
    artifact = {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "node_types": sorted({n.get("type", "unknown") for n in nodes}),
    }
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    logger.info("Saved graph stats to %s", ARTIFACT)
    return artifact


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(json.dumps(train(), indent=2))
