"""Geospatial utilities using India boundary GeoJSON datasets."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STATES_PATH = ROOT / "datasets" / "geo" / "india_states.geojson"
DISTRICTS_PATH = ROOT / "datasets" / "geo" / "india_districts.geojson"


@lru_cache
def _load_geojson(path: Path) -> dict:
    if not path.exists():
        return {"type": "FeatureCollection", "features": []}
    return json.loads(path.read_text(encoding="utf-8"))


def get_states_geojson() -> dict:
    """Return India state boundaries (geohacker/india)."""
    return _load_geojson(STATES_PATH)


def get_districts_geojson() -> dict:
    """Return India district boundaries (geohacker/india)."""
    return _load_geojson(DISTRICTS_PATH)


def list_state_names() -> list[str]:
    data = get_states_geojson()
    names = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        name = props.get("NAME_1") or props.get("ST_NM") or props.get("name")
        if name:
            names.append(str(name))
    return sorted(set(names))
