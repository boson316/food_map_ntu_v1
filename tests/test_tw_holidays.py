from __future__ import annotations

from datetime import date

from foodmap.tw_holidays import is_tw_public_holiday


def test_tw_public_holiday_2026_new_year() -> None:
    assert is_tw_public_holiday(date(2026, 1, 1)) is True


def test_tw_public_holiday_regular_weekday() -> None:
    assert is_tw_public_holiday(date(2026, 6, 23)) is False
