from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd
import pytest

pytest.importorskip("streamlit")
pytest.importorskip("pandas")

_SRC_APP = Path(__file__).resolve().parents[1] / "src" / "streamlit_app.py"
_spec = importlib.util.spec_from_file_location("streamlit_app_module", _SRC_APP)
assert _spec is not None and _spec.loader is not None
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
_wheel_candidate_df = _mod._wheel_candidate_df


def test_wheel_candidate_pins_low_score_restaurants_first() -> None:
    df = pd.DataFrame(
        {
            "id": ["pinned-low", "popular"],
            "name": ["巧食坊宜大店", "高人氣店"],
            "is_open_now": [True, True],
            "food_groups": [["麵食類"], ["便當類"]],
            "composite_score": [1.0, 9.0],
        }
    )
    result = _wheel_candidate_df(df, [], pinned_ids={"pinned-low"})
    assert list(result["id"]) == ["pinned-low", "popular"]


def test_wheel_candidate_skips_closed_pinned_restaurant() -> None:
    df = pd.DataFrame(
        {
            "id": ["pinned-closed", "open-shop"],
            "name": ["鴨米港式燒臘便當", "營業中店"],
            "is_open_now": [False, True],
            "food_groups": [["燒腊港式類"], ["便當類"]],
            "composite_score": [8.0, 2.0],
        }
    )
    result = _wheel_candidate_df(df, [], pinned_ids={"pinned-closed"})
    assert list(result["id"]) == ["open-shop"]
