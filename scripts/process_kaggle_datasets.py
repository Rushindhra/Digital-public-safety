#!/usr/bin/env python3
"""Process downloaded Kaggle datasets into platform-ready formats."""
from __future__ import annotations

import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("process_kaggle")

ROOT = Path(__file__).resolve().parents[1]
KAGGLE_RAW = ROOT / "datasets" / "raw" / "kaggle"
PROCESSED = ROOT / "datasets" / "processed" / "kaggle"


def index_fake_currency() -> None:
    """Index fake/genuine currency images for training manifests."""
    base = KAGGLE_RAW / "fake_currency"
    if not base.exists():
        logger.warning("fake_currency not found — run scripts/download_kaggle.ps1 first")
        return

    manifest: list[dict] = []
    for path in base.rglob("*"):
        if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            continue
        label = "counterfeit" if "fake" in path.parts or "counterfeit" in path.name.lower() else "genuine"
        manifest.append({"path": str(path.relative_to(ROOT)), "label": label})

    PROCESSED.mkdir(parents=True, exist_ok=True)
    out = PROCESSED / "currency_manifest.json"
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    logger.info("Indexed %d currency images → %s", len(manifest), out)


def index_inr_2000() -> None:
    base = KAGGLE_RAW / "inr_2000_notes"
    if not base.exists():
        logger.warning("inr_2000_notes not found")
        return
    images = [str(p.relative_to(ROOT)) for p in base.rglob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png"}]
    out = PROCESSED / "inr_2000_manifest.json"
    out.write_text(json.dumps(images, indent=2), encoding="utf-8")
    logger.info("Indexed %d INR 2000 note images", len(images))


def main() -> None:
    index_fake_currency()
    index_inr_2000()
    logger.info("Kaggle processing complete.")


if __name__ == "__main__":
    main()
