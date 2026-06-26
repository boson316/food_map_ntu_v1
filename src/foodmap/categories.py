from __future__ import annotations

from typing import Sequence

FOOD_GROUP_LUWEI = "滷味類"
FOOD_GROUP_CAFE = "下午茶咖啡廳類"
FOOD_GROUP_HOTPOT = "火鍋類"
FOOD_GROUP_STEAK = "牛排館類"
FOOD_GROUP_NOODLE = "麵食類"
FOOD_GROUP_JAPANESE = "日式料理類"
FOOD_GROUP_KOREAN = "韓式類"
FOOD_GROUP_VEGETARIAN = "素食蔬食類"
FOOD_GROUP_DIMSUM = "點心包子類"
FOOD_GROUP_ITALIAN = "義式披薩類"
FOOD_GROUP_BUFFET = "百匯自助餐類"
FOOD_GROUP_STIRFRY = "熱炒合菜類"
FOOD_GROUP_BBQ_ROAST = "燒腊港式類"
FOOD_GROUP_BENTO = "便當類"
FOOD_GROUP_FRIED = "炸物類"
FOOD_GROUP_OTHER = "其他"

FOOD_GROUPS: tuple[str, ...] = (
    FOOD_GROUP_LUWEI,
    FOOD_GROUP_CAFE,
    FOOD_GROUP_HOTPOT,
    FOOD_GROUP_STEAK,
    FOOD_GROUP_NOODLE,
    FOOD_GROUP_JAPANESE,
    FOOD_GROUP_KOREAN,
    FOOD_GROUP_VEGETARIAN,
    FOOD_GROUP_DIMSUM,
    FOOD_GROUP_ITALIAN,
    FOOD_GROUP_BUFFET,
    FOOD_GROUP_STIRFRY,
    FOOD_GROUP_BBQ_ROAST,
    FOOD_GROUP_BENTO,
    FOOD_GROUP_FRIED,
    FOOD_GROUP_OTHER,
)

_SELECTABLE_FOOD_GROUPS: tuple[str, ...] = FOOD_GROUPS[:-1]

_BENTO_FALLBACK_TYPES: frozenset[str] = frozenset(
    {
        "meal_takeaway",
        "breakfast_restaurant",
        "taiwanese_restaurant",
        "chinese_restaurant",
    }
)

_TYPE_TO_GROUPS: dict[str, tuple[str, ...]] = {
    "hot_pot_restaurant": (FOOD_GROUP_HOTPOT,),
    "cafe": (FOOD_GROUP_CAFE,),
    "coffee_shop": (FOOD_GROUP_CAFE,),
    "dessert_shop": (FOOD_GROUP_CAFE,),
    "dessert_restaurant": (FOOD_GROUP_CAFE,),
    "bakery": (FOOD_GROUP_CAFE,),
    "brunch_restaurant": (FOOD_GROUP_CAFE,),
    "pastry_shop": (FOOD_GROUP_CAFE,),
    "tea_house": (FOOD_GROUP_CAFE,),
    "steak_house": (FOOD_GROUP_STEAK,),
    "noodle_shop": (FOOD_GROUP_NOODLE,),
    "chinese_noodle_restaurant": (FOOD_GROUP_NOODLE,),
    "ramen_restaurant": (FOOD_GROUP_NOODLE,),
    "japanese_restaurant": (FOOD_GROUP_JAPANESE,),
    "japanese_curry_restaurant": (FOOD_GROUP_JAPANESE,),
    "japanese_izakaya_restaurant": (FOOD_GROUP_JAPANESE,),
    "sushi_restaurant": (FOOD_GROUP_JAPANESE,),
    "yakitori_restaurant": (FOOD_GROUP_JAPANESE,),
    "korean_restaurant": (FOOD_GROUP_KOREAN,),
    "vegetarian_restaurant": (FOOD_GROUP_VEGETARIAN,),
    "vegan_restaurant": (FOOD_GROUP_VEGETARIAN,),
    "dumpling_restaurant": (FOOD_GROUP_DIMSUM,),
    "italian_restaurant": (FOOD_GROUP_ITALIAN,),
    "pizza_restaurant": (FOOD_GROUP_ITALIAN,),
    "buffet_restaurant": (FOOD_GROUP_BUFFET,),
    "barbecue_restaurant": (FOOD_GROUP_STIRFRY,),
    "soup_restaurant": (FOOD_GROUP_BENTO,),
    "deli": (FOOD_GROUP_DIMSUM,),
    "salad_shop": (FOOD_GROUP_VEGETARIAN,),
    "vietnamese_restaurant": (FOOD_GROUP_NOODLE,),
    "meal_takeaway": (FOOD_GROUP_BENTO,),
    "breakfast_restaurant": (FOOD_GROUP_BENTO,),
    "taiwanese_restaurant": (FOOD_GROUP_BENTO,),
    "fast_food_restaurant": (FOOD_GROUP_FRIED,),
    "snack_bar": (FOOD_GROUP_FRIED,),
}

_KEYWORD_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("滷味", (FOOD_GROUP_LUWEI,)),
    ("火鍋", (FOOD_GROUP_HOTPOT,)),
    ("涮涮鍋", (FOOD_GROUP_HOTPOT,)),
    ("石頭鍋", (FOOD_GROUP_HOTPOT,)),
    ("鍋燒", (FOOD_GROUP_HOTPOT,)),
    ("壽喜", (FOOD_GROUP_HOTPOT,)),
    ("Syabu", (FOOD_GROUP_HOTPOT,)),
    ("shabu", (FOOD_GROUP_HOTPOT,)),
    ("咖啡", (FOOD_GROUP_CAFE,)),
    ("Coffee", (FOOD_GROUP_CAFE,)),
    ("茶坊", (FOOD_GROUP_CAFE,)),
    ("Café", (FOOD_GROUP_CAFE,)),
    ("Caf'e", (FOOD_GROUP_CAFE,)),
    ("下午茶", (FOOD_GROUP_CAFE,)),
    ("甜點", (FOOD_GROUP_CAFE,)),
    ("早午餐", (FOOD_GROUP_CAFE,)),
    ("brunch", (FOOD_GROUP_CAFE,)),
    ("Brunch", (FOOD_GROUP_CAFE,)),
    ("鬆餅", (FOOD_GROUP_CAFE,)),
    ("waffle", (FOOD_GROUP_CAFE,)),
    ("牛排", (FOOD_GROUP_STEAK,)),
    ("Steak", (FOOD_GROUP_STEAK,)),
    ("steak", (FOOD_GROUP_STEAK,)),
    ("紅豆餅", (FOOD_GROUP_CAFE,)),
    ("牛肉麵", (FOOD_GROUP_NOODLE,)),
    ("Beef Noodle", (FOOD_GROUP_NOODLE,)),
    ("Noodle", (FOOD_GROUP_NOODLE,)),
    ("拉麵", (FOOD_GROUP_NOODLE,)),
    ("Ramen", (FOOD_GROUP_NOODLE,)),
    ("ramen", (FOOD_GROUP_NOODLE,)),
    ("麵館", (FOOD_GROUP_NOODLE,)),
    ("麵店", (FOOD_GROUP_NOODLE,)),
    ("麵食", (FOOD_GROUP_NOODLE,)),
    ("米粉", (FOOD_GROUP_NOODLE,)),
    ("烏龍", (FOOD_GROUP_NOODLE,)),
    ("擔仔麵", (FOOD_GROUP_NOODLE,)),
    ("壽司", (FOOD_GROUP_JAPANESE,)),
    ("和食", (FOOD_GROUP_JAPANESE,)),
    ("鐵板", (FOOD_GROUP_JAPANESE,)),
    ("居酒", (FOOD_GROUP_JAPANESE,)),
    ("咖哩", (FOOD_GROUP_JAPANESE,)),
    ("丼", (FOOD_GROUP_JAPANESE,)),
    ("日式", (FOOD_GROUP_JAPANESE,)),
    ("韓式", (FOOD_GROUP_KOREAN,)),
    ("韓國", (FOOD_GROUP_KOREAN,)),
    ("素食", (FOOD_GROUP_VEGETARIAN,)),
    ("蔬食", (FOOD_GROUP_VEGETARIAN,)),
    ("包子", (FOOD_GROUP_DIMSUM,)),
    ("湯包", (FOOD_GROUP_DIMSUM,)),
    ("小籠", (FOOD_GROUP_DIMSUM,)),
    ("水餃", (FOOD_GROUP_DIMSUM,)),
    ("餛飩", (FOOD_GROUP_DIMSUM,)),
    ("點心", (FOOD_GROUP_DIMSUM,)),
    ("燒餅", (FOOD_GROUP_DIMSUM,)),
    ("披薩", (FOOD_GROUP_ITALIAN,)),
    ("Pizza", (FOOD_GROUP_ITALIAN,)),
    ("pizza", (FOOD_GROUP_ITALIAN,)),
    ("Pasta", (FOOD_GROUP_ITALIAN,)),
    ("pasta", (FOOD_GROUP_ITALIAN,)),
    ("義式", (FOOD_GROUP_ITALIAN,)),
    ("百匯", (FOOD_GROUP_BUFFET,)),
    ("自助餐", (FOOD_GROUP_BUFFET,)),
    ("熱炒", (FOOD_GROUP_STIRFRY,)),
    ("合菜", (FOOD_GROUP_STIRFRY,)),
    ("快炒", (FOOD_GROUP_STIRFRY,)),
    ("燒腊", (FOOD_GROUP_BBQ_ROAST,)),
    ("港式", (FOOD_GROUP_BBQ_ROAST,)),
    ("粵菜", (FOOD_GROUP_BBQ_ROAST,)),
    ("粵式", (FOOD_GROUP_BBQ_ROAST,)),
    ("便當", (FOOD_GROUP_BENTO,)),
    ("盒飯", (FOOD_GROUP_BENTO,)),
    ("定食", (FOOD_GROUP_BENTO,)),
    ("烤肉飯", (FOOD_GROUP_BENTO,)),
    ("排骨", (FOOD_GROUP_BENTO,)),
    ("簡餐", (FOOD_GROUP_BENTO,)),
    ("早餐", (FOOD_GROUP_BENTO,)),
    ("炸", (FOOD_GROUP_FRIED,)),
    ("雞排", (FOOD_GROUP_FRIED,)),
    ("雞肉串", (FOOD_GROUP_FRIED,)),
    ("鹽酥", (FOOD_GROUP_FRIED,)),
    ("鹹酥", (FOOD_GROUP_FRIED,)),
    ("香雞", (FOOD_GROUP_FRIED,)),
    ("蝦捲", (FOOD_GROUP_FRIED,)),
    ("羊肉湯", (FOOD_GROUP_NOODLE,)),
    ("五國真湯", (FOOD_GROUP_HOTPOT,)),
    ("真湯", (FOOD_GROUP_HOTPOT,)),
    ("仙草", (FOOD_GROUP_CAFE,)),
    ("清茶達人", (FOOD_GROUP_CAFE,)),
    ("春芳號", (FOOD_GROUP_CAFE,)),
    ("泰甜", (FOOD_GROUP_CAFE,)),
    ("Dumplings", (FOOD_GROUP_DIMSUM,)),
    ("水餃", (FOOD_GROUP_DIMSUM,)),
    ("粥品", (FOOD_GROUP_BENTO,)),
    ("粥", (FOOD_GROUP_BENTO,)),
    ("義饗", (FOOD_GROUP_ITALIAN,)),
    ("串燒", (FOOD_GROUP_STIRFRY,)),
    ("無麩質", (FOOD_GROUP_VEGETARIAN,)),
)


def classify_food_groups(category: str, name: str) -> list[str]:
    """Google primaryType + 店名關鍵字 → 使用者分類（可多標）。"""
    matched: set[str] = set()
    normalized_category = category.strip().lower()
    if normalized_category in _TYPE_TO_GROUPS:
        matched.update(_TYPE_TO_GROUPS[normalized_category])

    for keyword, groups in _KEYWORD_RULES:
        if keyword in name:
            matched.update(groups)

    if not matched and normalized_category in _BENTO_FALLBACK_TYPES:
        return [FOOD_GROUP_BENTO]

    if not matched:
        return [FOOD_GROUP_OTHER]
    return sorted(matched)


def matches_food_groups(restaurant_groups: Sequence[str], selected: Sequence[str]) -> bool:
    if not selected:
        return True
    selected_set = set(selected)
    return bool(selected_set.intersection(restaurant_groups))


def wheel_food_groups(selected: Sequence[str]) -> list[str] | None:
    """轉盤：有選分類時 = 所選 ∪ 其他。"""
    if not selected:
        return None
    expanded = set(selected)
    expanded.add(FOOD_GROUP_OTHER)
    return sorted(expanded)


FOOD_GROUP_SIDEBAR_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("台式小吃", (FOOD_GROUP_LUWEI, FOOD_GROUP_FRIED, FOOD_GROUP_BENTO, FOOD_GROUP_DIMSUM)),
    (
        "正餐料理",
        (
            FOOD_GROUP_HOTPOT,
            FOOD_GROUP_STEAK,
            FOOD_GROUP_NOODLE,
            FOOD_GROUP_JAPANESE,
            FOOD_GROUP_KOREAN,
            FOOD_GROUP_STIRFRY,
            FOOD_GROUP_BBQ_ROAST,
            FOOD_GROUP_ITALIAN,
            FOOD_GROUP_BUFFET,
        ),
    ),
    ("輕食飲品", (FOOD_GROUP_CAFE, FOOD_GROUP_VEGETARIAN)),
)

WHEEL_EXCLUDED_FOOD_GROUPS: frozenset[str] = frozenset(
    {
        FOOD_GROUP_CAFE,
        FOOD_GROUP_OTHER,
    }
)

_WHEEL_EXCLUDED_NAME_KEYWORDS: tuple[str, ...] = (
    "自助冰",
    "剉冰",
    "刨冰",
    "雪花冰",
    "燒仙草",
    "仙草冰",
    "豆花",
    "冰淇淋",
)


def is_wheel_eligible(food_groups: Sequence[str], name: str = "") -> bool:
    """轉盤候選：正餐為主，排除下午茶／冰品與非美食分類。"""
    for keyword in _WHEEL_EXCLUDED_NAME_KEYWORDS:
        if keyword in name:
            return False
    if not food_groups:
        return False
    group_set = set(food_groups)
    if group_set.intersection(WHEEL_EXCLUDED_FOOD_GROUPS):
        return False
    return True
