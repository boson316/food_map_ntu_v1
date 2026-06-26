from __future__ import annotations

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from foodmap.tw_holidays import is_tw_public_holiday

DEFAULT_TZ = "Asia/Taipei"


def parse_opening_hours_raw(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    periods = raw.get("periods")
    if not isinstance(periods, list):
        return None
    parsed: dict[str, Any] = {"periods": periods}
    special_days = raw.get("specialDays")
    if isinstance(special_days, list):
        parsed["specialDays"] = special_days
    return parsed


def _date_from_google_point(point: dict[str, Any]) -> tuple[int, int, int] | None:
    try:
        return int(point["year"]), int(point["month"]), int(point["day"])
    except (KeyError, TypeError, ValueError):
        return None


def _matches_local_date(point: dict[str, Any], local_now: datetime) -> bool:
    parts = _date_from_google_point(point)
    if parts is None:
        return False
    year, month, day = parts
    return local_now.year == year and local_now.month == month and local_now.day == day


def _special_day_entry(
    regular_hours: dict[str, Any],
    local_now: datetime,
) -> dict[str, Any] | None:
    special_days = regular_hours.get("specialDays")
    if not isinstance(special_days, list):
        return None
    for entry in special_days:
        if not isinstance(entry, dict):
            continue
        date_point = entry.get("date")
        if isinstance(date_point, dict) and _matches_local_date(date_point, local_now):
            return entry
    return None


def _is_open_for_periods(periods: list[Any], *, now_minutes: int) -> bool:
    for period in periods:
        if not isinstance(period, dict):
            continue
        open_pt = period.get("open")
        if not isinstance(open_pt, dict):
            continue
        open_m = _google_day_minutes(open_pt)
        close_pt = period.get("close")
        if not isinstance(close_pt, dict):
            if now_minutes >= open_m:
                return True
            continue
        close_m = _google_day_minutes(close_pt)
        if close_m <= open_m:
            if now_minutes >= open_m or now_minutes < close_m:
                return True
        elif open_m <= now_minutes < close_m:
            return True
    return False


def format_open_status(is_open_now: bool | None) -> str:
    if is_open_now is True:
        return "營業中"
    if is_open_now is False:
        return "休息中"
    return "未知"


def _google_day_minutes(point: dict[str, Any]) -> int:
    day = int(point.get("day", 0))
    hour = int(point.get("hour", 0))
    minute = int(point.get("minute", 0))
    return day * 24 * 60 + hour * 60 + minute


def _now_google_minutes(now: datetime) -> int:
    google_day = (now.weekday() + 1) % 7
    return google_day * 24 * 60 + now.hour * 60 + now.minute


def is_open_now(
    regular_hours: dict[str, Any] | None,
    *,
    now: datetime | None = None,
    tz: str = DEFAULT_TZ,
) -> bool | None:
    """依 Google regularOpeningHours 判斷當下是否營業；無資料回 None。"""
    if regular_hours is None:
        return None
    periods = regular_hours.get("periods")
    if periods is None:
        return None
    if not periods:
        return False

    local_now = (now or datetime.now(ZoneInfo(tz))).astimezone(ZoneInfo(tz))
    now_minutes = _now_google_minutes(local_now)

    special_entry = _special_day_entry(regular_hours, local_now)
    if special_entry is not None:
        if special_entry.get("closed") is True:
            return False
        exceptional = special_entry.get("exceptional_periods")
        if isinstance(exceptional, list):
            return _is_open_for_periods(exceptional, now_minutes=now_minutes)

    if is_tw_public_holiday(local_now.date()) and special_entry is None:
        # 國定假日且無 Google specialDays 覆寫 → 不臆測，沿用平日時段。
        pass

    return _is_open_for_periods(periods, now_minutes=now_minutes)


def resolve_is_open_now(
    *,
    regular_hours: dict[str, Any] | None,
    business_status: str | None,
    now: datetime | None = None,
    tz: str = DEFAULT_TZ,
) -> bool | None:
    if business_status == "CLOSED_PERMANENTLY":
        return False
    if business_status == "CLOSED_TEMPORARILY":
        return False
    return is_open_now(regular_hours, now=now, tz=tz)


def is_permanently_closed(business_status: str | None) -> bool:
    return business_status == "CLOSED_PERMANENTLY"
