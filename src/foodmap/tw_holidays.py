from __future__ import annotations

from datetime import date

# 行政院人事行政總處公告之國定假日（含補假）；僅列查詢用年份。
_TW_PUBLIC_HOLIDAYS: frozenset[date] = frozenset(
    {
        # 2025
        date(2025, 1, 1),
        date(2025, 1, 27),
        date(2025, 1, 28),
        date(2025, 1, 29),
        date(2025, 1, 30),
        date(2025, 1, 31),
        date(2025, 2, 28),
        date(2025, 4, 4),
        date(2025, 5, 1),
        date(2025, 5, 31),
        date(2025, 6, 2),
        date(2025, 10, 6),
        date(2025, 10, 10),
        date(2025, 10, 24),
        date(2025, 12, 25),
        # 2026
        date(2026, 1, 1),
        date(2026, 2, 16),
        date(2026, 2, 17),
        date(2026, 2, 18),
        date(2026, 2, 19),
        date(2026, 2, 20),
        date(2026, 2, 28),
        date(2026, 4, 4),
        date(2026, 4, 5),
        date(2026, 5, 1),
        date(2026, 6, 19),
        date(2026, 9, 25),
        date(2026, 9, 28),
        date(2026, 10, 9),
        date(2026, 10, 10),
        date(2026, 10, 26),
        date(2026, 12, 25),
    }
)


def is_tw_public_holiday(day: date) -> bool:
    return day in _TW_PUBLIC_HOLIDAYS
