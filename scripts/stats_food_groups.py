from __future__ import annotations

"""統計快取內各 food_group 家數（含 overlay 後結果）。"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from foodmap.categories import FOOD_GROUPS, classify_food_groups  # noqa: E402
from foodmap.data_overrides import (  # noqa: E402
    apply_restaurant_overrides,
    default_override_path,
    load_food_group_overrides,
)


def _groups_for_record(record: dict, overrides: dict) -> list[str]:
    merged = apply_restaurant_overrides(record, overrides)
    raw_groups = merged.get("food_groups")
    if isinstance(raw_groups, list) and raw_groups:
        return [str(group) for group in raw_groups]
    return classify_food_groups(str(record.get("category", "")), str(record.get("name", "")))


def main() -> int:
    parser = argparse.ArgumentParser(description="Count restaurants per food_group.")
    parser.add_argument(
        "path",
        type=Path,
        nargs="?",
        default=ROOT / "data" / "places_cache.json",
        help="Restaurant JSON cache (default: data/places_cache.json)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON instead of a table",
    )
    args = parser.parse_args()

    raw = json.loads(args.path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise SystemExit("JSON root must be an array")

    overrides = load_food_group_overrides(default_override_path(args.path))
    counter: Counter[str] = Counter()
    other_examples: list[str] = []

    for record in raw:
        if not isinstance(record, dict):
            continue
        groups = _groups_for_record(record, overrides)
        for group in groups:
            counter[group] += 1
        if groups == ["其他"] and len(other_examples) < 15:
            other_examples.append(str(record.get("name", "")))

    ordered = {group: counter.get(group, 0) for group in FOOD_GROUPS}
    if args.json:
        print(
            json.dumps(
                {
                    "total_records": len(raw),
                    "override_count": len(overrides),
                    "counts": ordered,
                    "other_examples": other_examples,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    print(f"Cache: {args.path.resolve()}")
    print(f"Records: {len(raw)} | Overrides: {len(overrides)}")
    print()
    for group, count in ordered.items():
        print(f"  {group}: {count}")
    if other_examples:
        print()
        print("「其他」範例（前 15）：")
        for name in other_examples:
            print(f"  - {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
