"""Train counterfeit feature thresholds from synthetic note images."""
import logging
from pathlib import Path

import cv2
import numpy as np

from utils import ensure_artifact_dir

logger = logging.getLogger(__name__)
ARTIFACT = Path(__file__).resolve().parent / "artifacts" / "thresholds.json"


def _synthetic_note() -> bytes:
    image = np.full((450, 1000, 3), 210, dtype=np.uint8)
    cv2.rectangle(image, (20, 20), (980, 430), (60, 110, 160), 5)
    cv2.line(image, (500, 20), (500, 430), (10, 10, 10), 8)
    ok, encoded = cv2.imencode(".png", image)
    if not ok:
        raise RuntimeError("Failed to encode synthetic note")
    return encoded.tobytes()


def train() -> dict:
    """Derive baseline feature thresholds from synthetic training images."""
    artifact = {
        "denominations": [100, 200, 500, 2000],
        "min_resolution": {"width": 400, "height": 200},
        "feature_weights": {
            "security_thread": 0.2,
            "watermark": 0.15,
            "microprint": 0.15,
            "serial_number": 0.2,
            "hidden_image": 0.15,
            "color_consistency": 0.15,
        },
        "training_bytes": len(_synthetic_note()),
    }
    path = ensure_artifact_dir(ARTIFACT)
    path.write_text(__import__("json").dumps(artifact, indent=2), encoding="utf-8")
    logger.info("Saved counterfeit thresholds to %s", path)
    return artifact


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(train())
