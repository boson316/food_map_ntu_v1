# 校園美食地圖 NTU v1

**Languages:** [English](README.md) · [中文](README.zh-TW.md)

> **狀態：** 已上線 · **Demo：** https://food-ntu-v1.streamlit.app/  
> **Repo：** https://github.com/boson316/food_map_ntu_v1 · **Fork 自：** [food_map_niu_v2](https://github.com/boson316/food_map_niu_v2)

**作者：** Boson Huang · **授權：** 專有軟體 — 見 [LICENSE](LICENSE)

國立臺灣大學**校本部／公館**步行圈美食地圖：離線 Google Places 快取 + 綜合分排序 + 15 類篩選 + **轉盤 Top 40**（排除休息中）。

| 項目 | 值 |
|------|-----|
| 中心點 | `25.0173, 121.5397`（羅斯福路校本部） |
| 預設搜尋 | **1 km** |
| 資料池 fetch | **2 km** |
| Slider 上限 | **5 km** |
| 轉盤候選 | **Top 40** |
| 列表上限 | 300 |

規格：[docs/v1-規格.md](docs/v1-規格.md) · 部署：[docs/streamlit-cloud-部署步驟.md](docs/streamlit-cloud-部署步驟.md)

---

## 功能摘要

- **美食分類**：十五類 + **其他**（側欄多選；轉盤有選時自動併入「其他」）。
- **預算**：平價篩選（`price_level 1`）+ 可含未標價位。
- **營業狀態**：地圖顯示營業中／休息中／未知；**轉盤排除休息中**。
- **排序**：`composite`（黃氏星等 × 距離衰減，預設）、`huang`、`rating`、`distance`。
- **離線快取**：雲端用 `data/places_cache.public.json`（可 commit）；本機完整快取 `data/places_cache.json`（gitignore）。

---

## 安裝與測試

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

`--radius` 預設 **1.0 km**。

---

## Streamlit（本機）

```powershell
$env:PYTHONPATH = "src"
streamlit run src/streamlit_app.py
# 或（Cloud 入口）
streamlit run streamlit_app.py
```

側欄預設台大中心、半徑 **1 km**。有快取檔時自動載入 `data/places_cache.json` 或 `data/places_cache.public.json`。

---

## 抓取快取（一次性，需 API Key）

```powershell
$env:PYTHONPATH = "src"
$env:GOOGLE_MAPS_API_KEY = "你的金鑰"

python scripts/fetch_places_to_json.py `
  --lat 25.0173 --lon 121.5397 `
  --radius-m 2000 --grid 8 --max-pages 4 --target 800 `
  --out data/places_cache.json

python scripts/enrich_food_groups.py data/places_cache.json
python scripts/stats_food_groups.py data/places_cache.json
Copy-Item data/places_cache.json data/places_cache.public.json
```

勿 commit 金鑰或 `data/places_cache.json`。

---

## 雲端部署

見 [docs/streamlit-cloud-部署步驟.md](docs/streamlit-cloud-部署步驟.md)。Main file：`streamlit_app.py`（repo 根目錄）。
