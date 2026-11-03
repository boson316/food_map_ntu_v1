from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from foodmap.providers import MockRestaurantProvider
from foodmap.scoring import huang_weighted_rating
from foodmap.service import FoodMapService

_ROOT = Path(__file__).resolve().parents[1]
_SCRIPT = _ROOT / "scripts" / "export_static.py"


@pytest.fixture(scope="module")
def export_mod():
    spec = importlib.util.spec_from_file_location("export_static", _SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_export_writes_places_and_config(export_mod, tmp_path: Path) -> None:
    data = _ROOT / "data" / "places_cache.public.json"
    args = export_mod.parse_args(["--data", str(data), "--out", str(tmp_path)])
    places_path, config_path, count = export_mod.export(args)

    places = json.loads(places_path.read_text(encoding="utf-8"))
    config = json.loads(config_path.read_text(encoding="utf-8"))
    assert len(places) == count > 0

    all_items = MockRestaurantProvider(json_path=data).list_restaurants()
    by_id = {r.id: r for r in all_items}
    for rec in places:
        r = by_id[rec["id"]]
        assert rec.get("status") != "CLOSED_PERMANENTLY"
        assert rec["groups"] == list(r.food_groups)
        assert rec["huang"] == pytest.approx(huang_weighted_rating(r.rating, r.review_count), abs=1e-4)

    assert config["center"] == [export_mod.SCHOOL["lat"], export_mod.SCHOOL["lon"]]
    assert config["tiles"]["url"].startswith("https://")
    assert config["decay_km"] == 0.6
    assert config["food_group_sidebar"]
    assert set(config["wheel_pinned_ids"]) <= set(by_id)


def test_export_matches_service_ranking(export_mod, tmp_path: Path) -> None:
    """Static export + JS composite formula reproduces FoodMapService ordering."""
    import math

    from foodmap.distance import haversine_km

    data = _ROOT / "data" / "places_cache.public.json"
    args = export_mod.parse_args(["--data", str(data), "--out", str(tmp_path)])
    places_path, _, _ = export_mod.export(args)
    places = json.loads(places_path.read_text(encoding="utf-8"))

    lat, lon, radius = export_mod.SCHOOL["lat"], export_mod.SCHOOL["lon"], export_mod.SCHOOL["radius"]
    ranked = []
    for p in places:
        d = haversine_km(lat, lon, p["lat"], p["lon"])
        if d <= radius:
            ranked.append((p["huang"] * math.exp(-d / 0.6), p["id"]))
    ranked.sort(reverse=True)

    service = FoodMapService(MockRestaurantProvider(json_path=data))
    expected = service.rank_nearby(center_lat=lat, center_lon=lon, radius_km=radius)
    assert [pid for _, pid in ranked[:20]] == [row.restaurant.id for row in expected[:20]]
    assert min(len(ranked), 300) == len(expected)  # rank_nearby default limit=300
