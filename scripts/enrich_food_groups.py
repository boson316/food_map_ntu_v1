from __future__ import annotations

"""為既有 JSON 快取補上 food_groups（不需 Google API）。"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from foodmap.categories import classify_food_groups  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich restaurant JSON with food_groups.")
    parser.add_argument("path", type=Path, help="JSON cache path")
    args = parser.parse_args()

    raw = json.loads(args.path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise SystemExit("JSON root must be an array")

    for item in raw:
        if not isinstance(item, dict):
            continue
        category = str(item.get("category", ""))
        name = str(item.get("name", ""))
        item["food_groups"] = classify_food_groups(category, name)

    args.path.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Enriched {len(raw)} records -> {args.path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
