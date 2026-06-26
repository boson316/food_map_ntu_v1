from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from foodmap.providers import MockRestaurantProvider
from foodmap.service import FoodMapService


def _weekday_periods(*, open_hour: int, close_hour: int) -> dict:
    return {
        "periods": [
            {
                "open": {"day": day, "hour": open_hour, "minute": 0},
                "close": {"day": day, "hour": close_hour, "minute": 0},
            }
            for day in range(7)
        ]
    }


def _write_v2_json(path: Path) -> None:
    base_lat, base_lon = 24.7464, 121.7457
    payload = [
        {
            "id": "open1",
            "name": "宜大火鍋店",
            "lat": base_lat + 0.0002,
            "lon": base_lon,
            "rating": 4.5,
            "review_count": 120,
            "category": "hot_pot_restaurant",
            "price_level": 1,
            "regular_opening_hours": _weekday_periods(open_hour=9, close_hour=22),
        },
        {
            "id": "closed1",
            "name": "休息中便當",
            "lat": base_lat + 0.0001,
            "lon": base_lon,
            "rating": 4.0,
            "review_count": 80,
            "category": "meal_takeaway",
            "price_level": 1,
            "regular_opening_hours": _weekday_periods(open_hour=9, close_hour=17),
        },
        {
            "id": "perm",
            "name": "已歇業店",
            "lat": base_lat,
            "lon": base_lon,
            "rating": 3.0,
            "review_count": 10,
            "category": "restaurant",
            "business_status": "CLOSED_PERMANENTLY",
        },
        {
            "id": "expensive",
            "name": "高價餐廳",
            "lat": base_lat + 0.0003,
            "lon": base_lon,
            "rating": 4.8,
            "review_count": 200,
            "category": "steak_house",
            "price_level": 4,
        },
    ]
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_max_price_level_filters_expensive(tmp_path: Path) -> None:
    p = tmp_path / "v2.json"
    _write_v2_json(p)
    svc = FoodMapService(MockRestaurantProvider(json_path=p))
    rows = svc.rank_nearby(
        center_lat=24.7464,
        center_lon=121.7457,
        radius_km=1.0,
        max_price_level=1,
        include_unknown_price=False,
        limit=10,
    )
    names = {r.restaurant.name for r in rows}
    assert "高價餐廳" not in names
    assert "宜大火鍋店" in names


def test_permanently_closed_excluded(tmp_path: Path) -> None:
    p = tmp_path / "v2.json"
    _write_v2_json(p)
    svc = FoodMapService(MockRestaurantProvider(json_path=p))
    rows = svc.rank_nearby(
        center_lat=24.7464,
        center_lon=121.7457,
        radius_km=1.0,
        limit=10,
    )
    assert all(r.restaurant.name != "已歇業店" for r in rows)


def test_food_group_filter(tmp_path: Path) -> None:
    p = tmp_path / "v2.json"
    _write_v2_json(p)
    svc = FoodMapService(MockRestaurantProvider(json_path=p))
    rows = svc.rank_nearby(
        center_lat=24.7464,
        center_lon=121.7457,
        radius_km=1.0,
        food_groups=["火鍋類"],
        limit=10,
    )
    assert len(rows) == 1
    assert rows[0].restaurant.name == "宜大火鍋店"


def test_open_only_excludes_closed_hours(tmp_path: Path) -> None:
    p = tmp_path / "v2.json"
    _write_v2_json(p)
    svc = FoodMapService(MockRestaurantProvider(json_path=p))
    evening = datetime(2026, 6, 22, 20, 0, tzinfo=ZoneInfo("Asia/Taipei"))
    rows = svc.rank_nearby(
        center_lat=24.7464,
        center_lon=121.7457,
        radius_km=1.0,
        open_only=True,
        now=evening,
        limit=10,
    )
    names = {r.restaurant.name for r in rows}
    assert "休息中便當" not in names
    assert "宜大火鍋店" in names


def test_to_public_dict_v2_fields(tmp_path: Path) -> None:
    p = tmp_path / "v2.json"
    _write_v2_json(p)
    svc = FoodMapService(MockRestaurantProvider(json_path=p))
    rows = svc.rank_nearby(
        center_lat=24.7464,
        center_lon=121.7457,
        radius_km=1.0,
        limit=5,
    )
    out = FoodMapService.to_public_dict(rows)
    assert out[0]["open_status_display"] in {"營業中", "休息中", "未知"}
    assert "food_group_display" in out[0]


def test_max_avg_spend_ntd_filters_by_overlay(tmp_path: Path) -> None:
    p = tmp_path / "spend.json"
    p.write_text(
        json.dumps(
            [
                {
                    "id": "cheap",
                    "name": "平價店",
                    "lat": 24.7466,
                    "lon": 121.7457,
                    "rating": 4.0,
                    "review_count": 50,
                    "category": "restaurant",
                    "avg_spend_ntd": 90,
                },
                {
                    "id": "dear",
                    "name": "貴店",
                    "lat": 24.7466,
                    "lon": 121.7457,
                    "rating": 4.5,
                    "review_count": 50,
                    "category": "restaurant",
                    "avg_spend_ntd": 250,
                },
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    svc = FoodMapService(MockRestaurantProvider(json_path=p))
    rows = svc.rank_nearby(
        center_lat=24.7464,
        center_lon=121.7457,
        radius_km=1.0,
        max_avg_spend_ntd=100,
        include_unknown_price=False,
        limit=10,
    )
    names = {r.restaurant.name for r in rows}
    assert "平價店" in names
    assert "貴店" not in names


def test_avg_spend_display_prefers_ntd(tmp_path: Path) -> None:
    p = tmp_path / "one.json"
    p.write_text(
        json.dumps(
            [
                {
                    "id": "x",
                    "name": "測試店",
                    "lat": 24.7466,
                    "lon": 121.7457,
                    "rating": 4.0,
                    "review_count": 10,
                    "price_level": 2,
                    "avg_spend_ntd": 85,
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    svc = FoodMapService(MockRestaurantProvider(json_path=p))
    out = FoodMapService.to_public_dict(
        svc.rank_nearby(
            center_lat=24.7464,
            center_lon=121.7457,
            radius_km=1.0,
            limit=1,
        )
    )
    assert out[0]["avg_spend_display"] == "約 $85"
