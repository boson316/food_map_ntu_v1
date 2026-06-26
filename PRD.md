# PRD — 校園美食地圖 NTU v1（國立臺灣大學）

> **v1 完整規劃：** [docs/v1-規格.md](docs/v1-規格.md)  
> **程式碼來源（Fork）：** `校園美食地圖_v2` / https://github.com/boson316/food_map_niu_v2  
> **目標 repo：** https://github.com/boson316/food_map_ntu_v1

## 1. 問題與目標

- **問題陳述**：台大學生在公館／羅斯福路校本部步行圈內覓食時，選擇極多，難以依評價、距離、預算與營業狀態快速篩選與隨機抽店。
- **目標使用者**：國立臺灣大學學生（步行／YouBike 可達範圍為主）。
- **校園中心**：校本部（羅斯福路四段1號）約 `25.0173°N, 121.5397°E`。
- **成功條件**：同 CCU v1 架構；預設搜尋 **1 km**；資料池 **2 km**。

## 2. 功能邊界（In Scope）

- **FR-1～FR-5**：同 [CCU PRD](https://github.com/boson316/food_map_ccu_v1) 架構（Fork 自宜大 v2）。
- **FR-v1-1**：預設搜尋半徑 **1 km**；Slider 上限 **5 km**。
- **FR-v1-2**：資料池 fetch **2 km** 內盡量抓滿。
- **FR-v1-3**：平價篩選、營業狀態、轉盤排除休息中。
- **FR-v1-4**：轉盤候選 **Top 40**。

## 3. 非目標（Out of Scope）

- **NFR-1～NFR-3**：同 CCU v1。
- **NFR-4**：公館商圈獨立次中心（v1.1）。

## 4. KPI

- `pytest -q` 全綠；coverage ≥ 70%。
- 快取 ≤2 km 內 unique POI ≥ 300。
- Streamlit 公開 demo。

## 5. NO-GO 條件

- 同 CCU v1。

## 6. 風險與假設

- **風險**：都市區 2 km 店數可能 >800，需 `--target` 與 top-k 控制；分類 overrides 工作量大。
- **假設**：1 km 預設涵蓋大部分上課動線；2 km fetch 已含公館部分店家。
- **緩解**：`--target 800`；分批 enrich + overrides。

## 7. 交付雙指標

| 指標 | 目標 |
|------|------|
| code_complete | 0% → 80% |
| go_to_market | 0% → 40% |

## 8. Phase 與 Scope 鎖

- **Phase 1 MVP：** Fork、常數、fetch 2 km、部署。
- **v1.1：** 轉盤 pin、公館次中心。
