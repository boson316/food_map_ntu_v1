"""Streamlit Community Cloud entrypoint (repo root).

Set Main file path to ``streamlit_app.py`` (repo root) on share.streamlit.io.
Falls back to the same module when developing with ``streamlit run src/streamlit_app.py``.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

_APP_PATH = _SRC / "streamlit_app.py"
_spec = importlib.util.spec_from_file_location("ntu_foodmap_streamlit", _APP_PATH)
if _spec is None or _spec.loader is None:
    raise ImportError(f"cannot load Streamlit app from {_APP_PATH}")
_app = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_app)
run = _app.run

if __name__ == "__main__":
    run()
