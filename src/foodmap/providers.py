from __future__ import annotations

import json
import math
import os
import time
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Sequence

from foodmap.categories import classify_food_groups
from foodmap.data_overrides import (
    apply_restaurant_overrides,
    default_override_path,
    load_food_group_overrides,
)
from foodmap.models import Restaurant
from foodmap.opening_hours import parse_opening_hours_raw
from foodmap.validation import load_restaurant_array

_NEARBY_TYPES = (
    "restaurant",
    "cafe",
    "coffee_shop",
    "fast_food_restaurant",
    "meal_takeaway",
    "chinese_restaurant",
    "japanese_restaurant",
    "korean_restaurant",
    "breakfast_restaurant",
    "bakery",
    "dessert_shop",
    "dessert_restaurant",
    "barbecue_restaurant",
    "tea_house",
    "snack_bar",
    "hot_pot_restaurant",
    "taiwanese_restaurant",
    "chinese_noodle_restaurant",
    "noodle_shop",
    "brunch_restaurant",
    "steak_house",
    "vegetarian_restaurant",
    "yakiniku_restaurant",
    "soup_restaurant",
    "japanese_curry_restaurant",
    "buffet_restaurant",
    "bistro",
    "seafood_restaurant",
    "hamburger_restaurant",
    "pizza_restaurant",
    "ramen_restaurant",
    "sushi_restaurant",
    "food_court",
    "cafeteria",
    "ice_cream_shop",
    "sandwich_shop",
)

_DEFAULT_TEXT_QUERIES = (
    "餐廳 國立臺灣大學",
    "美食 台大 公館",
    "小吃 羅斯福路 台大",
    "咖啡廳 台大",
    "火鍋 公館",
    "便當 台大",
    "炸物 公館",
    "滷味 公館",
)


def offset_center_meters(lat: float, lon: float, north_m: float, east_m: float) -> tuple[float, float]:
    dlat = north_m / 111_320.0
    dlon = east_m / (111_320.0 * math.cos(math.radians(lat)))
    return lat + dlat, lon + dlon


def grid_offsets_meters(grid: int, spacing_m: float) -> list[tuple[float, float]]:
    if grid <= 1:
        return [(0.0, 0.0)]
    half = (grid - 1) / 2.0
    return [
        ((half - row) * spacing_m, (col - half) * spacing_m)
        for row in range(grid)
        for col in range(grid)
    ]


def merge_restaurants_unique(existing: dict[str, Restaurant], rows: Sequence[Restaurant]) -> None:
    for row in rows:
        if row.id:
            existing[row.id] = row


class RestaurantProvider(ABC):
    @abstractmethod
    def list_restaurants(self) -> Sequence[Restaurant]:
        raise NotImplementedError


class MockRestaurantProvider(RestaurantProvider):
    """從套件內建 JSON 載入餐廳（離線 demo／期末報告用）。"""

    def __init__(self, json_path: Path | None = None) -> None:
        if json_path is None:
            json_path = Path(__file__).resolve().parent / "data" / "sample_restaurants.json"
        self._path = json_path
        self._cache: list[Restaurant] | None = None

    def list_restaurants(self) -> Sequence[Restaurant]:
        if self._cache is not None:
            return self._cache
        raw = load_restaurant_array(self._path)
        overrides = load_food_group_overrides(default_override_path(self._path))
        self._cache = [
            Restaurant.from_dict(apply_restaurant_overrides(item, overrides)) for item in raw
        ]
        return self._cache


class GooglePlacesProvider(RestaurantProvider):
    """Google Places API (New) — 建議先抓成 JSON 快取，查詢時用 MockRestaurantProvider。

    環境變數：GOOGLE_MAPS_API_KEY（必填）
    一次性匯出：python scripts/fetch_places_to_json.py --out data/places_cache.json
    """

    _SEARCH_URL = "https://places.googleapis.com/v1/places:searchNearby"
    _TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
    _FIELD_MASK = (
        "places.id,places.displayName,places.location,places.rating,places.userRatingCount,"
        "places.primaryType,places.priceLevel,places.regularOpeningHours,places.businessStatus"
    )

    def __init__(
        self,
        *,
        center_lat: float,
        center_lon: float,
        radius_m: float = 1000.0,
        api_key: str | None = None,
        max_pages: int = 3,
    ) -> None:
        self._center_lat = center_lat
        self._center_lon = center_lon
        self._radius_m = radius_m
        self._api_key = api_key or os.environ.get("GOOGLE_MAPS_API_KEY", "")
        self._max_pages = max_pages
        self._cache: list[Restaurant] | None = None

    def list_restaurants(self) -> Sequence[Restaurant]:
        if self._cache is not None:
            return self._cache
        if not self._api_key:
            raise ValueError(
                "GOOGLE_MAPS_API_KEY is required for GooglePlacesProvider; "
                "or fetch once via scripts/fetch_places_to_json.py and use --data"
            )
        self._cache = self._fetch_all_pages()
        return self._cache

    def list_restaurants_dense(
        self,
        *,
        target: int = 300,
        grid: int = 5,
        page_delay_s: float = 2.0,
    ) -> list[Restaurant]:
        """多中心格網搜尋 + 去重，突破單次 Nearby 約 20 筆上限。"""
        if target <= 0:
            raise ValueError("target must be positive")
        if grid <= 0:
            raise ValueError("grid must be positive")

        spacing_m = self._radius_m / grid
        sub_radius_m = max(self._radius_m / max(grid - 1, 1), 400.0)
        seen: dict[str, Restaurant] = {}

        for north_m, east_m in grid_offsets_meters(grid, spacing_m):
            center_lat, center_lon = offset_center_meters(
                self._center_lat,
                self._center_lon,
                north_m,
                east_m,
            )
            sub = GooglePlacesProvider(
                center_lat=center_lat,
                center_lon=center_lon,
                radius_m=sub_radius_m,
                api_key=self._api_key,
                max_pages=self._max_pages,
            )
            merge_restaurants_unique(seen, sub.list_restaurants())
            if page_delay_s > 0:
                time.sleep(page_delay_s)

        return list(seen.values())[:target]

    def list_restaurants_maximum(
        self,
        *,
        target: int = 300,
        grid: int = 6,
        page_delay_s: float = 1.5,
        text_queries: Sequence[str] | None = None,
    ) -> list[Restaurant]:
        """格網 Nearby + 逐類型 Nearby + Text Search，盡量拉高 1 km 內去重筆數。"""
        if target <= 0:
            raise ValueError("target must be positive")

        seen: dict[str, Restaurant] = {}
        merge_restaurants_unique(seen, self.list_restaurants_dense(target=target, grid=grid, page_delay_s=page_delay_s))

        for place_type in _NEARBY_TYPES:
            if len(seen) >= target:
                break
            merge_restaurants_unique(seen, self._fetch_all_pages([place_type]))
            if page_delay_s > 0:
                time.sleep(page_delay_s)

        queries = text_queries if text_queries is not None else _DEFAULT_TEXT_QUERIES
        for query in queries:
            if len(seen) >= target:
                break
            merge_restaurants_unique(seen, self._fetch_text_search(query))
            if page_delay_s > 0:
                time.sleep(page_delay_s)

        return list(seen.values())[:target]

    def _fetch_all_pages(self, included_types: Sequence[str] | None = None) -> list[Restaurant]:
        types = list(included_types) if included_types else list(_NEARBY_TYPES)
        body: dict[str, Any] = {
            "includedTypes": types,
            "maxResultCount": 20,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": self._center_lat, "longitude": self._center_lon},
                    "radius": min(self._radius_m, 50_000.0),
                }
            },
        }
        rows: list[Restaurant] = []
        page_token: str | None = None
        for page_idx in range(self._max_pages):
            request_body = dict(body)
            if page_token:
                if page_idx > 0:
                    time.sleep(2.0)
                request_body["pageToken"] = page_token
            payload = self._post_json(request_body)
            rows.extend(self._parse_places(payload.get("places", [])))
            page_token = payload.get("nextPageToken")
            if not page_token:
                break
        return rows

    def _fetch_text_search(self, text_query: str) -> list[Restaurant]:
        body: dict[str, Any] = {
            "textQuery": text_query,
            "pageSize": 20,
            "languageCode": "zh-TW",
            "regionCode": "TW",
            "locationBias": {
                "circle": {
                    "center": {"latitude": self._center_lat, "longitude": self._center_lon},
                    "radius": min(self._radius_m, 50_000.0),
                }
            },
        }
        rows: list[Restaurant] = []
        page_token: str | None = None
        for page_idx in range(self._max_pages):
            request_body = dict(body)
            if page_token:
                if page_idx > 0:
                    time.sleep(2.0)
                request_body["pageToken"] = page_token
            payload = self._post_json(request_body, url=self._TEXT_SEARCH_URL)
            rows.extend(self._parse_places(payload.get("places", [])))
            page_token = payload.get("nextPageToken")
            if not page_token:
                break
        return rows

    def _post_json(self, body: dict[str, Any], *, url: str | None = None) -> dict[str, Any]:
        timeout_s = float(os.environ.get("GOOGLE_PLACES_TIMEOUT_S", "30"))
        max_retries = int(os.environ.get("GOOGLE_PLACES_MAX_RETRIES", "3"))
        endpoint = url or self._SEARCH_URL
        data = json.dumps(body).encode("utf-8")
        last_error: Exception | None = None

        for attempt in range(max_retries):
            req = urllib.request.Request(
                endpoint,
                data=data,
                method="POST",
                headers={
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": self._api_key,
                    "X-Goog-FieldMask": self._FIELD_MASK,
                },
            )
            try:
                with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                    raw = json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                if exc.code in {429, 500, 502, 503, 504} and attempt + 1 < max_retries:
                    time.sleep(min(2**attempt, 8))
                    last_error = exc
                    continue
                raise RuntimeError(
                    f"Google Places API HTTP {exc.code}: {detail}"
                ) from exc
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_error = exc
                if attempt + 1 >= max_retries:
                    break
                time.sleep(min(2**attempt, 8))
                continue
            else:
                if not isinstance(raw, dict):
                    raise ValueError("Google Places API returned non-object JSON")
                return raw

        raise RuntimeError(
            "Google Places API 連線失敗 "
            f"（{max_retries} 次重試，timeout={timeout_s}s）：{last_error}\n"
            "請檢查：\n"
            "  1) 網路 / VPN / 防火牆是否擋 places.googleapis.com:443\n"
            "  2) $env:GOOGLE_MAPS_API_KEY 是否已設定\n"
            "  3) Google Cloud 是否啟用「Places API (New)」\n"
            "  4) 拉長逾時：$env:GOOGLE_PLACES_TIMEOUT_S = \"60\""
        ) from last_error

    @staticmethod
    def _parse_price_level(raw: Any) -> int | None:
        if raw is None:
            return None
        if isinstance(raw, int):
            return raw if 1 <= raw <= 4 else None
        if isinstance(raw, str):
            mapping = {
                "PRICE_LEVEL_INEXPENSIVE": 1,
                "PRICE_LEVEL_MODERATE": 2,
                "PRICE_LEVEL_EXPENSIVE": 3,
                "PRICE_LEVEL_VERY_EXPENSIVE": 4,
            }
            if raw in mapping:
                return mapping[raw]
            if raw.isdigit():
                level = int(raw)
                return level if 1 <= level <= 4 else None
        return None

    @staticmethod
    def _parse_places(places: list[dict[str, Any]]) -> list[Restaurant]:
        out: list[Restaurant] = []
        for p in places:
            loc = p.get("location") or {}
            name_obj = p.get("displayName") or {}
            name = str(name_obj.get("text", "unknown"))
            category = str(p.get("primaryType", ""))
            out.append(
                Restaurant(
                    id=str(p.get("id", "")),
                    name=name,
                    lat=float(loc.get("latitude", 0.0)),
                    lon=float(loc.get("longitude", 0.0)),
                    rating=float(p.get("rating", 0.0)),
                    review_count=int(p.get("userRatingCount", 0)),
                    category=category,
                    price_level=GooglePlacesProvider._parse_price_level(p.get("priceLevel")),
                    regular_opening_hours=parse_opening_hours_raw(p.get("regularOpeningHours")),
                    business_status=(
                        str(p["businessStatus"]) if p.get("businessStatus") is not None else None
                    ),
                    food_groups=tuple(classify_food_groups(category, name)),
                )
            )
        return out
