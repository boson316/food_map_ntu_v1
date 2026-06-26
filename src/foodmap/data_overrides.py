from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from foodmap.categories import FOOD_GROUPS

FOOD_GROUP_OVERRIDE_FILENAME = "food_group_overrides.json"
MAX_OVERRIDE_FILE_BYTES = 512 * 1024


def default_override_path(cache_path: Path) -> Path:
    return cache_path.parent / FOOD_GROUP_OVERRIDE_FILENAME


def validate_override_entry(raw: Any, *, key: str) -> None:
    if not isinstance(raw, dict):
        raise ValueError(f"override[{key!r}] must be a JSON object")

    food_groups = raw.get("food_groups")
    if food_groups is None:
        raise ValueError(f"override[{key!r}] missing food_groups")
    if not isinstance(food_groups, list) or not food_groups:
        raise ValueError(f"override[{key!r}].food_groups must be a non-empty list")
    if not all(isinstance(group, str) and group in FOOD_GROUPS for group in food_groups):
        raise ValueError(
            f"override[{key!r}].food_groups must contain only: {', '.join(FOOD_GROUPS)}"
        )

    avg_spend_ntd = raw.get("avg_spend_ntd")
    if avg_spend_ntd is not None:
        spend = int(avg_spend_ntd)
        if spend <= 0:
            raise ValueError(f"override[{key!r}].avg_spend_ntd must be positive")


def load_food_group_overrides(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None or not path.is_file():
        return {}

    size = path.stat().st_size
    if size > MAX_OVERRIDE_FILE_BYTES:
        raise ValueError(f"override file too large: {size} bytes (max {MAX_OVERRIDE_FILE_BYTES})")

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path.name}: {exc.msg}") from exc

    if not isinstance(raw, dict):
        raise ValueError(f"{path.name} must be a JSON object keyed by restaurant id")

    overrides: dict[str, dict[str, Any]] = {}
    for key, entry in raw.items():
        if str(key).startswith("_"):
            continue
        restaurant_id = str(key).strip()
        if not restaurant_id:
            raise ValueError("override keys must be non-empty restaurant ids")
        validate_override_entry(entry, key=restaurant_id)
        overrides[restaurant_id] = dict(entry)

    return overrides


def apply_restaurant_overrides(
    record: dict[str, Any],
    overrides: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    restaurant_id = str(record.get("id", "")).strip()
    if not restaurant_id:
        return record

    entry = overrides.get(restaurant_id)
    if entry is None:
        return record

    merged = dict(record)
    merged["food_groups"] = list(entry["food_groups"])
    if entry.get("avg_spend_ntd") is not None:
        merged["avg_spend_ntd"] = int(entry["avg_spend_ntd"])
    return merged
