# Streamlit Cloud × GitHub Deployment (NTU Food Map)

**Languages:** [English](streamlit-cloud-deploy.md) · [中文](streamlit-cloud-部署步驟.md)

> **Goal:** Free Streamlit Community Cloud hosting; share URL / QR with NTU students.

---

## 0. Pre-flight (local)

```powershell
cd c:\Users\User\Documents\code\food_map_ntu_v1
python -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
python -m pytest -q --cov=src --cov-fail-under=70
streamlit run streamlit_app.py
```

Open `http://localhost:8501` — verify list + wheel tabs; default radius **1 km**, center **NTU main campus**.

---

## 1. Data strategy

| File | In Git? | On cloud |
|------|---------|----------|
| `data/places_cache.json` | No (`.gitignore`) | Not uploaded |
| `data/places_cache.public.json` | **Yes** (recommended) | ~300–800 restaurants |
| Neither | — | 15 sample restaurants (Yilan demo coords; poor NTU UX) |

**Before deploy:**

```powershell
Copy-Item data/places_cache.json data/places_cache.public.json
```

Ensure no API keys in JSON.

---

## 2. GitHub repo

| Item | Value |
|------|-------|
| Account | `boson316` |
| Repo | `food_map_ntu_v1` |
| Visibility | Public (recommended for QR sharing) |

**Commit (public hygiene):**

- `src/`, `tests/`, `scripts/`, `requirements.txt`, `streamlit_app.py`
- `README.md`, `README.zh-TW.md`, `PRD.md`, `LICENSE`
- `data/places_cache.public.json`, `data/food_group_overrides.json`, `data/user_favorites.json`
- `.github/workflows/`

**Do not commit:** `.env`, `GOOGLE_MAPS_API_KEY`, `data/places_cache.json`, internal docs (`AGENTS.md`, `AI_HANDOFF.md`, `TASKS.md`, etc.).

```powershell
git status --short --ignored
```

---

## 3. Streamlit Community Cloud

1. https://share.streamlit.io → New app
2. Repo: `boson316/food_map_ntu_v1`, branch `main`
3. **Main file path:** `streamlit_app.py` (repo root)
4. Deploy

**Planned URL:** `https://food-map-ntu-v1.streamlit.app`

**Secrets:** Not required for normal operation (JSON cache). Add `GOOGLE_MAPS_API_KEY` only if re-fetching Places on the server.

---

## 4. Post-deploy smoke

- [ ] Title: 國立臺灣大學 校園美食地圖
- [ ] Default radius slider: **1 km**
- [ ] Restaurants visible within 1 km of campus
- [ ] Wheel ≤ 40 segments; no closed-only picks
- [ ] Map pin: 台大校本部
