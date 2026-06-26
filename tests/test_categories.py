from __future__ import annotations

import json
from pathlib import Path

import pytest

from foodmap.categories import (
    FOOD_GROUP_BENTO,
    FOOD_GROUP_CAFE,
    FOOD_GROUP_DIMSUM,
    FOOD_GROUP_FRIED,
    FOOD_GROUP_HOTPOT,
    FOOD_GROUP_ITALIAN,
    FOOD_GROUP_NOODLE,
    FOOD_GROUP_OTHER,
    FOOD_GROUP_STEAK,
    FOOD_GROUP_STIRFRY,
    FOOD_GROUP_VEGETARIAN,
    classify_food_groups,
    matches_food_groups,
    wheel_food_groups,
)


def test_classify_hot_pot_by_type() -> None:
    groups = classify_food_groups("hot_pot_restaurant", "某火鍋店")
    assert FOOD_GROUP_HOTPOT in groups


def test_classify_steak_by_type_and_name() -> None:
    assert classify_food_groups("steak_house", "MIO米歐牛排館") == [FOOD_GROUP_STEAK]
    assert FOOD_GROUP_STEAK in classify_food_groups("restaurant", "獅子座牛排（宜大店）")


def test_classify_noodle_by_type() -> None:
    groups = classify_food_groups("chinese_noodle_restaurant", "某牛肉麵")
    assert groups == [FOOD_GROUP_NOODLE]


def test_classify_luwei_by_keyword() -> None:
    groups = classify_food_groups("restaurant", "神農路滷味攤")
    assert "滷味類" in groups


def test_classify_fried_by_keyword() -> None:
    groups = classify_food_groups("snack_bar", "宜大雞排")
    assert FOOD_GROUP_FRIED in groups
    assert FOOD_GROUP_FRIED in classify_food_groups("restaurant", "好事達鹹酥雞")


def test_classify_dimsum_by_keyword() -> None:
    assert FOOD_GROUP_DIMSUM in classify_food_groups("restaurant", "宜蘭神農包子")


def test_classify_cafe_by_type() -> None:
    groups = classify_food_groups("coffee_shop", "某店")
    assert FOOD_GROUP_CAFE in groups
    assert FOOD_GROUP_CAFE in classify_food_groups("restaurant", "一藍茶坊")


def test_classify_bento_fallback_for_taiwanese() -> None:
    assert classify_food_groups("taiwanese_restaurant", "某店") == [FOOD_GROUP_BENTO]


def test_classify_fallback_other() -> None:
    groups = classify_food_groups("hotel", "某某飯店")
    assert groups == [FOOD_GROUP_OTHER]


def test_classify_vegetarian_by_type() -> None:
    assert classify_food_groups("vegetarian_restaurant", "全民素食") == [FOOD_GROUP_VEGETARIAN]


def test_matches_food_groups_empty_selection() -> None:
    assert matches_food_groups(["火鍋類"], [])


def test_wheel_food_groups_unions_other() -> None:
    assert wheel_food_groups(["牛排館類"]) == ["其他", "牛排館類"]


@pytest.mark.parametrize(
    ("name", "groups", "expected"),
    [
        ("六扇門", ["火鍋類"], True),
        ("麥當勞-宜蘭神農餐廳", ["炸物類"], True),
        ("非凡豆漿", ["便當類"], True),
        ("哈哈自助冰、燒仙草", ["下午茶咖啡廳類", "百匯自助餐類"], False),
        ("某咖啡廳", ["下午茶咖啡廳類"], False),
        ("新買醉餐酒館", ["其他"], False),
    ],
)
def test_is_wheel_eligible_main_meals(name: str, groups: list[str], expected: bool) -> None:
    from foodmap.categories import is_wheel_eligible

    assert is_wheel_eligible(groups, name) is expected


def test_mio_steak_from_cache() -> None:
    cache = Path(__file__).resolve().parents[1] / "data" / "places_cache.json"
    if not cache.is_file():
        pytest.skip("places_cache.json not present")
    raw = json.loads(cache.read_text(encoding="utf-8"))
    mio = next(item for item in raw if "MIO米歐牛排館" in item["name"])
    assert mio["food_groups"] == [FOOD_GROUP_STEAK]


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("正隆羊肉湯", FOOD_GROUP_NOODLE),
        ("❤️五國真湯宜蘭店", FOOD_GROUP_HOTPOT),
        ("T4清茶達人-宜蘭宜大店", FOOD_GROUP_CAFE),
        ("喝泰甜（今天有開）", FOOD_GROUP_CAFE),
        ("義饗家", FOOD_GROUP_ITALIAN),
        ("Just Fresh Meat Dumplings", FOOD_GROUP_DIMSUM),
        ("碳休今呷串燒酒場", FOOD_GROUP_STIRFRY),
    ],
)
def test_classify_other_edge_cases_by_keyword(name: str, expected: str) -> None:
    assert expected in classify_food_groups("restaurant", name)
