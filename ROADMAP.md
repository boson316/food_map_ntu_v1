# ROADMAP — 校園美食地圖 NTU v1

**Languages:** [English](ROADMAP.en.md) · [中文](ROADMAP.md)

> **時間預算：** 4–5 h · **策略：** Fork 宜大 v2  
> **對齊：** [PRD.md](PRD.md) · [docs/v1-規格.md](docs/v1-規格.md)

---

## 總覽

| 階段 | 時間 | 重點 | 交付 |
|------|------|------|------|
| Phase 0 | 完成 | 規劃 + bootstrap | 規格文件 |
| Phase 1 | 0.5 h | Fork + 常數 | pytest 綠 |
| Phase 2 | 2–3 h | Fetch 2 km + overrides | 快取 JSON |
| Phase 3 | 0.5 h | 部署 | Streamlit URL |
| Phase 4 | 0.5 h | 作品集 | portfolio |

---

## 目前進度

| 指標 | 進度 |
|------|------|
| code_complete | **5%** |
| go_to_market | **0%** |

---

## Phase 1 — Fork + 常數

- 中心 `25.0173, 121.5397`
- 預設半徑 **1 km**；fetch **2 km**；slider max **5 km**

## Phase 2 — 資料

```powershell
--radius-m 2000 --grid 8 --target 800
```

## v1.1（Out of Scope）

- 公館次中心、轉盤 pin

---

[SUMMARY.md](SUMMARY.md) · [TASKS.md](TASKS.md)
