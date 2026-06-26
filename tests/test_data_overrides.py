from __future__ import annotations

import json
from pathlib import Path

import pytest

from foodmap.data_overrides import (
    apply_restaurant_overrides,
    load_food_group_overrides,
    validate_override_entry,
)
from foodmap.providers import MockRestaurantProvider


def test_validate_override_entry_rejects_unknown_group() -> None:
    with pytest.raises(ValueError, match="food_groups"):
        validate_override_entry({"food_groups": ["不存在類"]}, key="x")


def test_load_overrides_skips_comment_keys(tmp_path: Path) -> None:
    path = tmp_path / "food_group_overrides.json"
    path.write_text(
        json.dumps(
            {
                "_note": "comments",
                "place-1": {"food_groups": ["火鍋類"]},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    overrides = load_food_group_overrides(path)
    assert overrides == {"place-1": {"food_groups": ["火鍋類"]}}


def test_apply_restaurant_overrides_replaces_food_groups() -> None:
    record = {
        "id": "place-1",
        "name": "某店",
        "category": "restaurant",
        "food_groups": ["其他"],
    }
    merged = apply_restaurant_overrides(
        record,
        {"place-1": {"food_groups": ["滷味類"]}},
    )
    assert merged["food_groups"] == ["滷味類"]


def test_apply_restaurant_overrides_sets_avg_spend() -> None:
    record = {"id": "place-1", "name": "某店", "food_groups": ["便當類"]}
    merged = apply_restaurant_overrides(
        record,
        {"place-1": {"food_groups": ["便當類"], "avg_spend_ntd": 95}},
    )
    assert merged["avg_spend_ntd"] == 95


def test_mock_provider_applies_overlay(tmp_path: Path) -> None:
    cache = tmp_path / "places.json"
    cache.write_text(
        json.dumps(
            [
                {
                    "id": "p1",
                    "name": "宜大雞排",
                    "lat": 24.7464,
                    "lon": 121.7457,
                    "rating": 4.0,
                    "review_count": 10,
                    "category": "snack_bar",
                    "food_groups": ["炸物類"],
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    overrides = tmp_path / "food_group_overrides.json"
    overrides.write_text(
        json.dumps({"p1": {"food_groups": ["滷味類"]}}, ensure_ascii=False),
        encoding="utf-8",
    )

    rows = MockRestaurantProvider(cache).list_restaurants()
    assert rows[0].food_groups == ("滷味類",)
