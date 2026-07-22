"""Inference wrapper for counterfeit currency detection."""
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[2] / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.ml.counterfeit import analyse_note
from app.schemas.counterfeit import Denomination


def predict(image_bytes: bytes, denomination: int = 500) -> dict:
    denom_map = {
        100: Denomination.INR_100,
        200: Denomination.INR_200,
        500: Denomination.INR_500,
        2000: Denomination.INR_2000,
    }
    result = analyse_note(image_bytes, denom_map[denomination])
    return result.model_dump()


if __name__ == "__main__":
    import cv2
    import numpy as np

    image = np.full((450, 1000, 3), 210, dtype=np.uint8)
    ok, encoded = cv2.imencode(".png", image)
    print(predict(encoded.tobytes()))
