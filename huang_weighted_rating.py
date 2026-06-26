"""黃氏星等（Huang weighted rating）— 獨立示範版。

與 src/foodmap/scoring.py 中 huang_weighted_rating 邏輯一致，可單檔執行示範。
"""

from __future__ import annotations

import math
from typing import Literal

RatingTier = Literal["low", "medium", "high"]

TIER: dict[RatingTier, float] = {
    "low": 0.65,      # 1～2 星（rating < 2.5）
    "medium": 1.0,    # 3 星
    "high": 1.25,     # 4～5 星
}
REVIEW_SATURATION = 500
def rating_tier(rating: float) -> RatingTier:
    if rating < 2.5:
        return "low"
    if rating < 4.0:
        return "medium"
    return "high"
def tier_weight(rating: float) -> float:
    return TIER[rating_tier(rating)]
def star_weight(rating: float) -> float:
    return max(0.0, min(1.0, rating / 5.0))
def review_weight(review_count: int, *, saturation: int = REVIEW_SATURATION) -> float:
    if review_count < 0:
        raise ValueError("review_count must be non-negative")
    if saturation <= 0:
        raise ValueError("saturation must be positive")
    if review_count == 0:
        return 0.1
    return min(1.0, math.log1p(review_count) / math.log1p(saturation))
def huang_weighted_rating(
    rating: float,
    review_count: int,
    *,
    review_saturation: int = REVIEW_SATURATION,
) -> float:
    """黃氏星等：rating × tier × w_star × w_review。"""
    tier = tier_weight(rating)
    w_star = 0.5 + 0.5 * star_weight(rating)
    w_review = 0.4 + 0.6 * review_weight(review_count, saturation=review_saturation)
    return rating * tier * w_star * w_review


if __name__ == "__main__":
    examples = [
        (4.5, 200, "高星、評論多"),
        (2.0, 200, "低星、評論多"),
        (4.5, 5, "高星、評論少"),
        (3.0, 0, "無評論"),
    ]
    print("黃氏星等 huang_weighted_rating 示範")
    print("-" * 48)
    for rating, n, label in examples:
        score = huang_weighted_rating(rating, n)
        print(f"rating={rating}, n={n:>3}  ({label})  →  huang = {score:.4f}")
