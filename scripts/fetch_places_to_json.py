from __future__ import annotations

"""一次性從 Google Places API (New) 抓資料，存成 JSON 快取。

用法（PowerShell）— v2 預設 1 km、盡量抓滿：
  $env:PYTHONPATH = "src"
  $env:GOOGLE_MAPS_API_KEY = "你的金鑰"
  python scripts/fetch_places_to_json.py

之後查詢走快取（不燒 API 額度）：
  python -m foodmap search --lat 24.7464 --lon 121.7457 --radius 1.0 --data data/places_cache.json
"""

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from foodmap.distance import HaversineCenter, haversine_km_from_center  # noqa: E402
from foodmap.providers import GooglePlacesProvider  # noqa: E402


def _restaurant_to_json_dict(restaurant) -> dict:
    payload = {
        "id": restaurant.id,
        "name": restaurant.name,
        "lat": restaurant.lat,
        "lon": restaurant.lon,
        "rating": restaurant.rating,
        "review_count": restaurant.review_count,
        "category": restaurant.category,
        "price_level": restaurant.price_level,
        "food_groups": list(restaurant.food_groups),
    }
    if restaurant.regular_opening_hours is not None:
        payload["regular_opening_hours"] = restaurant.regular_opening_hours
    if restaurant.business_status is not None:
        payload["business_status"] = restaurant.business_status
    return payload


def _filter_within_radius_km(rows, *, center_lat: float, center_lon: float, radius_km: float):
    center = HaversineCenter.from_degrees(center_lat, center_lon)
    kept = []
    for row in rows:
        dist = haversine_km_from_center(center, row.lat, row.lon)
        if dist <= radius_km:
            kept.append(row)
    return kept


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Google Places nearby restaurants to JSON cache.")
    parser.add_argument("--lat", type=float, default=25.0173, help="Center latitude")
    parser.add_argument("--lon", type=float, default=121.5397, help="Center longitude")
    parser.add_argument("--radius-m", type=float, default=2000.0, help="Search radius in meters")
    parser.add_argument("--max-pages", type=int, default=3, help="Max API pages per grid cell (20/page)")
    parser.add_argument(
        "--target",
        type=int,
        default=300,
        help="腳本提前停止上限（非產品 KPI；宜大 1 km 實測約 120 家）",
    )
    parser.add_argument("--grid", type=int, default=6, help="Grid size (6 = 6x6 centers)")
    parser.add_argument(
        "--no-text-search",
        action="store_true",
        help="Skip Text Search supplement (fewer API calls)",
    )
    parser.add_argument("--out", type=Path, default=Path("data/places_cache.json"), help="Output JSON path")
    args = parser.parse_args()

    if not os.environ.get("GOOGLE_MAPS_API_KEY"):
        print(
            "[ERROR] GOOGLE_MAPS_API_KEY is not set.\n"
            "  PowerShell: $env:GOOGLE_MAPS_API_KEY = \"你的金鑰\"\n"
            "  Then re-run this script.",
            file=sys.stderr,
        )
        return 1

    radius_km = args.radius_m / 1000.0
    provider = GooglePlacesProvider(
        center_lat=args.lat,
        center_lon=args.lon,
        radius_m=args.radius_m,
        max_pages=args.max_pages,
    )
    if args.target > 20:
        text_queries = () if args.no_text_search else None
        rows = provider.list_restaurants_maximum(
            target=args.target,
            grid=args.grid,
            text_queries=text_queries,
        )
    else:
        rows = provider.list_restaurants()[: args.target]

    rows = _filter_within_radius_km(
        rows,
        center_lat=args.lat,
        center_lon=args.lon,
        radius_km=radius_km,
    )

    payload = [_restaurant_to_json_dict(r) for r in rows]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Wrote {len(payload)} restaurants (≤{radius_km:.1f} km) -> {args.out.resolve()}")

    with_price = sum(1 for item in payload if item.get("price_level") is not None)
    with_hours = sum(1 for item in payload if item.get("regular_opening_hours"))
    print(
        f"[STATS] price_level 覆蓋 {with_price}/{len(payload)} · "
        f"營業時間覆蓋 {with_hours}/{len(payload)}"
    )
    if len(payload) < args.target:
        print(
            f"[WARN] Only {len(payload)} unique places within {radius_km:.1f} km (target {args.target}). "
            "宜大周邊 1 km 實際 POI 可能約 120–180；已用格網+逐類型+Text Search。"
            "若仍不足，代表 Google 索引已飽和，非程式漏抓。",
            file=sys.stderr,
        )
        print(
            "[TIP] 複製到雲端 demo：Copy-Item data/places_cache.json data/places_cache.public.json",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
