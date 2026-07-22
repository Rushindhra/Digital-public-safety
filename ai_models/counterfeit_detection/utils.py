"""Utilities for counterfeit_detection model package."""
from pathlib import Path


def ensure_artifact_dir(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
