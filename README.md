# Campus Food Map NTU v1

**Languages:** [English](README.md) · [中文](README.zh-TW.md)

> **Status:** Phase 1 implemented · **Demo (planned):** https://food-map-ntu-v1.streamlit.app  
> **Repo:** https://github.com/boson316/food_map_ntu_v1 · **Fork from:** [food_map_niu_v2](https://github.com/boson316/food_map_niu_v2)

**Author:** Boson Huang · **License:** Proprietary — see [LICENSE](LICENSE)

Campus food map for **National Taiwan University (main campus / Gongguan)**. Offline Google Places cache + composite ranking + 15 food categories + **wheel Top 40** (open restaurants only).

| Item | Value |
|------|-------|
| Center | `25.0173, 121.5397` (Roosevelt Rd. main campus) |
| Default search | **1 km** |
| Fetch pool | **2 km** |
| Slider max | **5 km** |
| Wheel pool | **Top 40** |
| List limit | 300 |

Spec: [docs/v1-規格.md](docs/v1-規格.md) · Deploy: [docs/streamlit-cloud-deploy.md](docs/streamlit-cloud-deploy.md)

---

## Features

- **Food groups:** 15 categories + **其他**; multi-select sidebar; wheel auto-includes「其他」when filtering.
- **Budget:** `price_level 1` filter + optional include unknown price.
- **Hours:** map shows open/closed/unknown; **wheel excludes closed**.
- **Ranking:** `composite` (Huang score × distance decay, default), `huang`, `rating`, `distance`.
- **Offline cache:** `data/places_cache.public.json` for Streamlit Cloud (commit); full cache in `data/places_cache.json` (gitignored).

---

## Install & test

```powershell
cd food_map_ntu_v1
python -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
python -m pytest -q --cov=src --cov-fail-under=70
```

---

## CLI

```powershell
$env:PYTHONPATH = "src"
python -m foodmap search --lat 25.0173 --lon 121.5397 --sort composite --format table
python -m foodmap search --lat 25.0173 --lon 121.5397 --food-group 火鍋類 --max-price-level 1 --format json
```

Default `--radius` is **1.0 km**.

---

## Streamlit (local)

```powershell
$env:PYTHONPATH = "src"
streamlit run src/streamlit_app.py
# or (Cloud entrypoint)
streamlit run streamlit_app.py
```

Sidebar defaults: NTU center, **1 km** radius. Uses `data/places_cache.json` or `data/places_cache.public.json` when present.

---

## Fetch cache (one-time, needs API key)

```powershell
$env:PYTHONPATH = "src"
$env:GOOGLE_MAPS_API_KEY = "your-key"

python scripts/fetch_places_to_json.py `
  --lat 25.0173 --lon 121.5397 `
  --radius-m 2000 --grid 8 --max-pages 4 --target 800 `
  --out data/places_cache.json

python scripts/enrich_food_groups.py data/places_cache.json
python scripts/stats_food_groups.py data/places_cache.json
Copy-Item data/places_cache.json data/places_cache.public.json
```

Do **not** commit `GOOGLE_MAPS_API_KEY` or `data/places_cache.json`.

---

## Cloud deploy

See [docs/streamlit-cloud-deploy.md](docs/streamlit-cloud-deploy.md). Main file: `streamlit_app.py` (repo root).
