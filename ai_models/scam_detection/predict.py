"""Inference wrapper for digital-arrest scam detection."""
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[2] / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.ml.scam import analyse_scam
from app.schemas.platform import ScamRequest


def predict(content: str, channel: str = "chat", language: str = "en") -> dict:
    """Run scam analysis and return a serializable result dict."""
    result = analyse_scam(ScamRequest(content=content, channel=channel, language=language))
    return result.model_dump()


if __name__ == "__main__":
    demo = predict("CBI officer digital arrest transfer money immediately")
    print(demo)
