"""Train or refresh scam-detection pattern weights from labelled transcripts."""
import json
import logging
from pathlib import Path

from utils import load_dataset, save_model_artifact

logger = logging.getLogger(__name__)
DATASET = Path(__file__).resolve().parents[2] / "datasets" / "scam_transcripts.json"
ARTIFACT = Path(__file__).resolve().parent / "artifacts" / "pattern_weights.json"


def train(output_path: Path | None = None) -> dict:
    """Build pattern-weight artifact from the synthetic scam dataset."""
    samples = load_dataset(DATASET)
    weights: dict[str, float] = {}
    for sample in samples:
        label = sample.get("label", "benign")
        weight = 1.0 if label == "scam" else 0.2
        for tag in sample.get("tags", []):
            weights[tag] = max(weights.get(tag, 0), weight)
    artifact = {"weights": weights, "samples": len(samples)}
    save_model_artifact(output_path or ARTIFACT, artifact)
    logger.info("Saved scam pattern weights to %s", output_path or ARTIFACT)
    return artifact


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(json.dumps(train(), indent=2))
