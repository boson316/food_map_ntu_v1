from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from foodmap.categories import classify_food_groups
from foodmap.opening_hours import parse_opening_hours_raw


@dataclass(frozen=True, slots=True)
class Restaurant:
    """單一餐廳（評分為聚合後的平均星等）。"""

    id: str
    name: str
    lat: float
    lon: float
    rating: float
    review_count: int
    category: str = ""
    price_level: int | None = None
    avg_spend_ntd: int | None = None
    regular_opening_hours: dict[str, Any] | None = None
    business_status: str | None = None
    food_groups: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Restaurant:
        category = str(raw.get("category", ""))
        name = str(raw["name"])
        raw_groups = raw.get("food_groups")
        if isinstance(raw_groups, list) and raw_groups:
            food_groups = tuple(str(g) for g in raw_groups)
        else:
            food_groups = tuple(classify_food_groups(category, name))

        return cls(
            id=str(raw["id"]),
            name=name,
            lat=float(raw["lat"]),
            lon=float(raw["lon"]),
            rating=float(raw["rating"]),
            review_count=int(raw["review_count"]),
            category=category,
            price_level=int(raw["price_level"]) if raw.get("price_level") is not None else None,
            avg_spend_ntd=int(raw["avg_spend_ntd"]) if raw.get("avg_spend_ntd") is not None else None,
            regular_opening_hours=parse_opening_hours_raw(raw.get("regular_opening_hours")),
            business_status=(
                str(raw["business_status"]) if raw.get("business_status") is not None else None
            ),
            food_groups=food_groups,
        )
