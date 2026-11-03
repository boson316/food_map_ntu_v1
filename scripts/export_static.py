"""Export restaurant data + site config for the static Leaflet frontend (``web/``).

The static site has no server: every filter, distance, composite score and
open-now check runs in the browser. This script precomputes everything that
does *not* depend on the user's center point or the current time:

- food groups (overrides + keyword classification, same as the Streamlit app)
- Huang rating, Bayesian rating (dataset prior), rating tier
- Google Maps URL

Usage::

    PYTHONPATH=src python scripts/export_static.py            # writes web/data/
    PYTHONPATH=src python scripts/export_static.py --out dist/data

School-specific values (title, center, counter namespace) can be overridden
with flags or env vars so the same ``web/`` frontend serves every campus.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from foodmap.categories import (  # noqa: E402
    FOOD_GROUP_OTHER,
    FOOD_GROUP_SIDEBAR_GROUPS,
    WHEEL_EXCLUDED_FOOD_GROUPS,
    _WHEEL_EXCLUDED_NAME_KEYWORDS,
)
from foodmap.integrity import author_notice  # noqa: E402
from foodmap.models import Restaurant  # noqa: E402
from foodmap.opening_hours import is_permanently_closed  # noqa: E402
from foodmap.providers import MockRestaurantProvider  # noqa: E402
from foodmap.scoring import (  # noqa: E402
    bayesian_average_rating,
    dataset_prior_mean,
    huang_weighted_rating,
    rating_tier,
)
from foodmap.service import build_maps_url, format_avg_spend  # noqa: E402

# School-specific defaults (the only part that differs between campus repos).
SCHOOL = {
    "school": "台大",
    "title": "國立臺灣大學 校園美食地圖",
    "campus_name": "台大校本部",
    "lat": 25.0173,
    "lon": 121.5397,
    "radius": 1.0,
    "max_radius": 5.0,
    "tiles": "carto",
    "counter_namespace": "food-map-ntu-v1",
    "repo_url": "https://github.com/boson316/food_map_ntu_v1",
}

TILES = {
    "carto": {
        "url": "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
        "subdomains": "abcd",
        "max_zoom": 20,
        "attribution": '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> '
        '&copy; <a href="https://carto.com/attributions">CARTO</a>',
    },
    # 國土測繪 EMAP5：台灣地名為中文（Carto 在鄉鎮多為拼音）
    "nlsc": {
        "url": "https://wmts.nlsc.gov.tw/wmts/EMAP5/default/GoogleMapsCompatible/{z}/{y}/{x}",
        "subdomains": "",
        "max_zoom": 19,
        "attribution": '&copy; <a href="https://maps.nlsc.gov.tw/">內政部國土測繪中心</a>',
    },
}

PRIOR_STRENGTH = 8.0  # FoodMapService default
DECAY_KM = 0.6  # FoodMapService default
WHEEL_TOP_N = 40  # streamlit_app._WHEEL_TOP_N


def default_data_path() -> Path | None:
    data_dir = _ROOT / "data"
    for filename in ("places_cache.json", "places_cache.public.json"):
        path = data_dir / filename
        if path.is_file():
            return path
    return None


def load_pinned_ids(path: Path) -> list[str]:
    if not path.is_file():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    ids = raw.get("place_ids") if isinstance(raw, dict) else None
    if not isinstance(ids, list):
        return []
    return [str(i) for i in ids if str(i).strip()]


def place_record(r: Restaurant, *, prior_mean: float) -> dict[str, Any]:
    rec: dict[str, Any] = {
        "id": r.id,
        "name": r.name,
        "lat": round(r.lat, 7),
        "lon": round(r.lon, 7),
        "rating": r.rating,
        "reviews": r.review_count,
        "category": r.category,
        "groups": list(r.food_groups),
        "spend": format_avg_spend(r.price_level, avg_spend_ntd=r.avg_spend_ntd),
        "huang": round(huang_weighted_rating(r.rating, r.review_count), 4),
        "bayes": round(
            bayesian_average_rating(
                r.rating,
                r.review_count,
                prior_mean=prior_mean,
                prior_strength=PRIOR_STRENGTH,
            ),
            4,
        ),
        "tier": rating_tier(r.rating),
        "url": build_maps_url(r.name, r.lat, r.lon, place_id=r.id),
    }
    if r.price_level is not None:
        rec["price_level"] = r.price_level
    if r.avg_spend_ntd is not None:
        rec["avg_spend_ntd"] = r.avg_spend_ntd
    if r.business_status and r.business_status != "OPERATIONAL":
        rec["status"] = r.business_status
    if r.regular_opening_hours is not None:
        rec["hours"] = r.regular_opening_hours
    return rec


def build_config(args: argparse.Namespace, *, pinned_ids: list[str]) -> dict[str, Any]:
    return {
        "school": args.school,
        "title": args.title,
        "campus_name": args.campus_name,
        "center": [args.lat, args.lon],
        "default_radius_km": args.radius,
        "max_radius_km": args.max_radius,
        "tiles": TILES[args.tiles],
        "decay_km": DECAY_KM,
        "wheel_top_n": WHEEL_TOP_N,
        "food_group_sidebar": [[label, list(groups)] for label, groups in FOOD_GROUP_SIDEBAR_GROUPS],
        "food_group_other": FOOD_GROUP_OTHER,
        "wheel_excluded_groups": sorted(WHEEL_EXCLUDED_FOOD_GROUPS),
        "wheel_excluded_name_keywords": list(_WHEEL_EXCLUDED_NAME_KEYWORDS),
        "wheel_pinned_ids": pinned_ids,
        "counter_namespace": args.counter_namespace,
        "author_notice": author_notice(),
        "repo_url": args.repo_url,
    }


def export(args: argparse.Namespace) -> tuple[Path, Path, int]:
    data_path = Path(args.data) if args.data else default_data_path()
    provider = MockRestaurantProvider(json_path=data_path) if data_path else MockRestaurantProvider()
    all_items = list(provider.list_restaurants())
    prior_mean = dataset_prior_mean(all_items)  # same prior as FoodMapService.rank_nearby
    places = [
        place_record(r, prior_mean=prior_mean)
        for r in all_items
        if not is_permanently_closed(r.business_status)
    ]

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    places_path = out_dir / "places.json"
    config_path = out_dir / "config.json"
    places_path.write_text(
        json.dumps(places, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    config = build_config(args, pinned_ids=load_pinned_ids(_ROOT / "data" / "user_favorites.json"))
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return places_path, config_path, len(places)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    env = os.environ.get
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", default=None, help="restaurant JSON (default: data/places_cache*.json)")
    p.add_argument("--out", default=str(_ROOT / "web" / "data"))
    p.add_argument("--school", default=env("FOODMAP_SCHOOL", SCHOOL["school"]))
    p.add_argument("--title", default=env("FOODMAP_TITLE", SCHOOL["title"]))
    p.add_argument("--campus-name", default=env("FOODMAP_CAMPUS_NAME", SCHOOL["campus_name"]))
    p.add_argument("--lat", type=float, default=float(env("CAMPUS_LAT", SCHOOL["lat"])))
    p.add_argument("--lon", type=float, default=float(env("CAMPUS_LON", SCHOOL["lon"])))
    p.add_argument("--radius", type=float, default=SCHOOL["radius"], help="default search radius (km)")
    p.add_argument("--max-radius", type=float, default=SCHOOL["max_radius"], help="radius slider max (km)")
    p.add_argument("--tiles", choices=sorted(TILES), default=SCHOOL["tiles"], help="basemap")
    p.add_argument(
        "--counter-namespace",
        default=env("VISIT_COUNTER_NAMESPACE", SCHOOL["counter_namespace"]),
        help="counterapi.dev namespace for the footer visit counter ('' disables)",
    )
    p.add_argument("--repo-url", default=env("FOODMAP_REPO_URL", SCHOOL["repo_url"]))
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    places_path, config_path, count = export(parse_args(argv))
    print(f"wrote {count} places → {places_path}")
    print(f"wrote config → {config_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
