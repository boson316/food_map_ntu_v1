# Streamlit Cloud × GitHub 部署步驟（台大美食地圖）

**Languages:** [English](streamlit-cloud-deploy.md) · [中文](streamlit-cloud-部署步驟.md)

> 目標：免費 Streamlit Community Cloud 上線，網址可貼系上／社團／LINE。

---

## 0. 部署前檢查（本機）

```powershell
cd c:\Users\User\Documents\code\food_map_ntu_v1
python -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
python -m pytest -q --cov=src --cov-fail-under=70
streamlit run streamlit_app.py
```

瀏覽器開 `http://localhost:8501`，確認列表與轉盤正常；預設半徑 **1 km**、中心 **台大校本部**。

---

## 1. 資料策略

| 檔案 | Git | 雲端效果 |
|------|-----|----------|
| `data/places_cache.json` | ❌ `.gitignore` | 不會上傳 |
| `data/places_cache.public.json` | ✅ 建議 commit | 約 300–800 家 |
| 兩者都沒有 | — | 僅 15 筆宜大範例（NTU 座標下幾乎無結果） |

**部署前：**

```powershell
Copy-Item data/places_cache.json data/places_cache.public.json
```

確認 JSON 內**沒有** API Key。

---

## 2. GitHub repo

| 項目 | 值 |
|------|-----|
| 帳號 | `boson316` |
| Repo | `food_map_ntu_v1` |
| 公開／私人 | 公開較方便 QR 分享 |

**應 commit：** `src/`、`tests/`、`scripts/`、`requirements.txt`、`streamlit_app.py`、`README.md`、`README.zh-TW.md`、`PRD.md`、`data/places_cache.public.json`、`.github/workflows/`。

**勿 commit：** `.env`、`GOOGLE_MAPS_API_KEY`、`data/places_cache.json`、內部檔（`AGENTS.md`、`AI_HANDOFF.md`、`TASKS.md` 等）。

```powershell
git status --short --ignored
```

---

## 3. Streamlit Community Cloud

1. https://share.streamlit.io → New app
2. Repo：`boson316/food_map_ntu_v1`，分支 `main`
3. **Main file path：** `streamlit_app.py`（repo 根目錄）
4. Deploy

**規劃網址：** `https://food-map-ntu-v1.streamlit.app`

**Secrets：** 日常讀 JSON 快取，**不必**設 `GOOGLE_MAPS_API_KEY`；僅伺服器端重抓 Places 時才需要。

---

## 4. 上線後驗收

- [ ] 標題：國立臺灣大學 校園美食地圖
- [ ] 側欄半徑預設 **1 km**
- [ ] 1 km 內有店家列表
- [ ] 轉盤 ≤ 40、排除休息中
- [ ] 地圖 pin：台大校本部
