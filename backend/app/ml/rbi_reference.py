"""Load RBI banknote reference specifications for denomination-aware screening."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SPECS_PATH = ROOT / "datasets" / "reference" / "rbi_banknote_specs.json"


@lru_cache
def load_rbi_specs() -> dict:
    if not SPECS_PATH.exists():
        return {"denominations": {}}
    return json.loads(SPECS_PATH.read_text(encoding="utf-8"))


def get_denomination_spec(denomination: int) -> dict:
    specs = load_rbi_specs()
    return specs.get("denominations", {}).get(str(denomination), {})


def expected_aspect_ratio(denomination: int) -> float | None:
    spec = get_denomination_spec(denomination)
    dims = spec.get("dimensions_mm")
    if not dims or len(dims) != 2:
        return None
    return dims[0] / dims[1]
