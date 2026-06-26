from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from foodmap.opening_hours import format_open_status, is_open_now, resolve_is_open_now


def _weekday_periods(*, open_hour: int, close_hour: int) -> dict:
    return {
        "periods": [
            {
                "open": {"day": day, "hour": open_hour, "minute": 0},
                "close": {"day": day, "hour": close_hour, "minute": 0},
            }
            for day in range(7)
        ]
    }


def test_is_open_now_inside_period() -> None:
    hours = _weekday_periods(open_hour=9, close_hour=21)
    monday_noon = datetime(2026, 6, 22, 12, 0, tzinfo=ZoneInfo("Asia/Taipei"))
    assert is_open_now(hours, now=monday_noon) is True


def test_is_open_now_outside_period() -> None:
    hours = _weekday_periods(open_hour=9, close_hour=21)
    monday_night = datetime(2026, 6, 22, 23, 0, tzinfo=ZoneInfo("Asia/Taipei"))
    assert is_open_now(hours, now=monday_night) is False


def test_is_open_now_missing_hours() -> None:
    assert is_open_now(None) is None


def test_resolve_closed_temporarily() -> None:
    assert (
        resolve_is_open_now(
            regular_hours=_weekday_periods(open_hour=0, close_hour=23),
            business_status="CLOSED_TEMPORARILY",
        )
        is False
    )


def test_format_open_status_labels() -> None:
    assert format_open_status(True) == "營業中"
    assert format_open_status(False) == "休息中"
    assert format_open_status(None) == "未知"


def test_special_day_closed_override() -> None:
    hours = {
        "periods": [
            {
                "open": {"day": 3, "hour": 9, "minute": 0},
                "close": {"day": 3, "hour": 21, "minute": 0},
            }
        ],
        "specialDays": [
            {
                "date": {"year": 2026, "month": 1, "day": 1},
                "closed": True,
            }
        ],
    }
    new_year = datetime(2026, 1, 1, 12, 0, tzinfo=ZoneInfo("Asia/Taipei"))
    assert is_open_now(hours, now=new_year) is False


def test_special_day_exceptional_periods() -> None:
    hours = {
        "periods": [
            {
                "open": {"day": 4, "hour": 9, "minute": 0},
                "close": {"day": 4, "hour": 17, "minute": 0},
            }
        ],
        "specialDays": [
            {
                "date": {"year": 2026, "month": 6, "day": 25},
                "exceptional_periods": [
                    {
                        "open": {"day": 4, "hour": 10, "minute": 0},
                        "close": {"day": 4, "hour": 14, "minute": 0},
                    }
                ],
            }
        ],
    }
    inside = datetime(2026, 6, 25, 11, 0, tzinfo=ZoneInfo("Asia/Taipei"))
    outside = datetime(2026, 6, 25, 16, 0, tzinfo=ZoneInfo("Asia/Taipei"))
    assert is_open_now(hours, now=inside) is True
    assert is_open_now(hours, now=outside) is False
