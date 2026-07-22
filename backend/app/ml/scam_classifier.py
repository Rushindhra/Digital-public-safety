"""Hybrid scam classifier: rule engine + TF-IDF logistic regression."""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[3]
DATASET_PATH = ROOT / "datasets" / "scam_transcripts.json"
MODEL_PATH = ROOT / "ai_models" / "scam_detection" / "artifacts" / "scam_classifier.joblib"
PHISHING_PATH = ROOT / "datasets" / "reference" / "phishing_patterns.json"

_pipeline: Pipeline | None = None


def _load_phishing_patterns() -> list[str]:
    if not PHISHING_PATH.exists():
        return []
    data = json.loads(PHISHING_PATH.read_text(encoding="utf-8"))
    return data.get("text_indicators", []) + data.get("url_indicators", [])


def train_classifier(dataset_path: Path | None = None) -> Pipeline:
    """Train TF-IDF + LogisticRegression on the unified scam dataset."""
    path = dataset_path or DATASET_PATH
    samples = json.loads(path.read_text(encoding="utf-8"))
    texts = [s["content"] for s in samples]
    labels = [1 if s["label"] == "scam" else 0 for s in samples]

    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=8000, min_df=1)),
            ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )
    pipeline.fit(texts, labels)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    logger.info("Saved scam classifier to %s (%d samples)", MODEL_PATH, len(samples))
    return pipeline


def load_classifier() -> Pipeline | None:
    """Load persisted classifier or train from dataset if missing."""
    global _pipeline
    if _pipeline is not None:
        return _pipeline
    if MODEL_PATH.exists():
        _pipeline = joblib.load(MODEL_PATH)
        return _pipeline
    if DATASET_PATH.exists():
        try:
            _pipeline = train_classifier()
            return _pipeline
        except Exception as exc:
            logger.warning("Could not train scam classifier: %s", exc)
    return None


def ml_scam_probability(text: str) -> tuple[float, float]:
    """
    Return (scam_probability, confidence) from ML model.
    Falls back to (0.0, 0.0) if model unavailable.
    """
    pipeline = load_classifier()
    if pipeline is None:
        return 0.0, 0.0

    proba = pipeline.predict_proba([text])[0]
    scam_idx = list(pipeline.classes_).index(1)
    scam_p = float(proba[scam_idx])
    confidence = float(max(proba))
    return scam_p, confidence


def phishing_pattern_hits(text: str) -> list[str]:
    """Return matched phishing indicator patterns."""
    hits = []
    for pattern in _load_phishing_patterns():
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            hits.append(match.group(0)[:80])
    return hits
