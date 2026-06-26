# Senior 規劃能力 — 開案與交付 SOP

**Languages:** [English](PLANNING.en.md) · [中文](PLANNING.md)

> **用途：** 新專案 scaffold 後先讀本檔；Agent 遵守 `rules/senior-planning.mdc`。  
> **互補：** `PRD.md`（做什麼）· `ROADMAP.md`（何時）· `SUMMARY.md`（現況）· `TECH_DEBT.md`（欠什麼）

---

## 1. 核心原則（Senior 與 Junior 差在哪）

| Junior 本能 | Senior 做法 |
|-------------|-------------|
| 功能做完 = 完成 | **雙指標**：code 與 go-to-market 分開追 |
| 一次把 roadmap 全做 | **Scope 鎖死**；加購項等有客戶付錢 |
| 測試綠燈就 ship | **真實依賴煙測**（外部 API、部署 URL） |
| 繼續加功能逃避推銷 | code 超前時 **80% GTM / 20% bug** |
| 「我 X 分鐘做完」 | 區分 **人時 / Agent 算力 / 等效人工** |

---

## 2. 雙指標（必建）

在 `SUMMARY.md` 與 `ROADMAP.md` 維護，**禁止**混成一個百分比。

| 指標 | 定義 | 典型訊號 |
|------|------|----------|
| **code_complete** | repo 內功能 + 測試 + 文件 scaffold | pytest 綠、檔案齊 |
| **go_to_market** | 可對外 demo、真實整合、推銷、詢價 | 公開 URL、DM、詢價 |

```
code_complete    [████████░░░░░░░░░░░░]  ?%
go_to_market     [████░░░░░░░░░░░░░░░░]  ?%
```

**規則：** `code_complete ≥ 70%` 且 `go_to_market < 40%` → **停止加功能**，跑 [docs/go-to-market-checklist.md](templates/go-to-market-checklist.md)。

---

## 3. 開案順序（Plan → Spec → Test → Ship → Sell）

```
1. 問題 + 使用者 + 不做什么（PRD §1–3）
2. Phase 切分 + 時間預算（ROADMAP）
3. slo.config.json + slo_sync（工程 KPI）
4. TDD 最小閉環（tests → src）
5. 第一個可公開 demo（部署 URL）
6. 真實依賴煙測（寫入 TECH_DEBT 關閉項）
7. 推銷 / 接案（GTM checklist）
8. 加購項（決策 artifact 後才做）
```

**AI 編排：** 一次 Agent session = **一個可 merge 單元** + 驗收命令；禁止「順便做 Phase B」。

---

## 4. Scope 鎖（Scope Lock）

### 預設 In Scope

- PRD §2 列出的 FR
- 驗收命令可測的 MVP

### 預設 Out of Scope（直到有付費或 decision artifact）

- v1.1 錦上添花
- 第二資料源 / 第二市場
- PDF / 報表 / 進階分析
- 會員、後端 auth（除非 PRD 明定）

**加 Scope 必須：** `python scripts/record_decision.py ...` → `artifacts/decision_*.md`

---

## 5. 技術債登記（TECH_DEBT.md）

任何以下情況 **必須** 寫入 `TECH_DEBT.md`，不可假裝完成：

- 測試只用 fixture/mock，未打真實外部 API
- `NotImplementedError` / stub
- 作品集或 DM 模板仍為本機路徑
- CI workflow 存在但未啟用部署
- 已知會因上游 HTML/API 改版而壞的 crawler

**上線前：** 至少關閉 **P0** 項（公開 URL + 核心真實煙測）。

---

## 6. 時間誠實（AI 時代）

記錄時分三欄（寫在 `weekly_review.md` 或 decision artifact）：

| 欄位 |  meaning |
|------|----------|
| **人時** | 你下指令、審 spec、驗收的小時/分鐘 |
| **Agent 算力** | 模型實際生成與工具呼叫（估即可） |
| **等效人工** | 若無 AI，同等 scaffold 約幾人時（供 portfolio 不誇大） |

**禁止對外說：**「20 分鐘 = Senior 一週」  
**可以說：**「spec 驅動 + AI，X 人時內交付含 N tests 的可 demo scaffold」

---

## 7. 第一週 GTM Checklist（模板）

複製到 `docs/go-to-market-checklist.md`，按序勾：

1. 部署 → 取得 **公開 demo URL**
2. 更新 portfolio / outreach 模板中的 URL
3. **真實依賴煙測**（記錄 pass/fail）
4. 冷 DM / 詢問 ≥ N（寫進 tracker）
5. 目標 ≥1 **詢價**（非必成交）
6. 更新 `SUMMARY.md` 雙指標

---

## 8. 每週節奏（5h/週也適用）

| 比例 | code 超前 | code 與 GTM 同步 |
|------|-----------|------------------|
| 建議 | **20% 修 bug / 80% GTM** | 50% build / 50% GTM |
| 週末 15min | `weekly_review.md` + `risk_register.md` + `next_actions.md` |

---

## 9. Agent 使用規則（摘要）

見 `.cursor/rules/senior-planning.mdc`。要點：

- 先讀 `PLANNING.md` + `PRD.md` + `TECH_DEBT.md`
- 動手前列 **預計改動檔案** 與 **驗收命令**
- `go_to_market < 40%` 時拒絕加 FR，除非使用者明確 override 並寫 decision
- 完成後更新 `SUMMARY.md` 雙指標，不過度宣稱「完成」

---

## 10. 文件對照表

| 檔案 | 誰維護 | 更新時機 |
|------|--------|----------|
| `PRD.md` | 人 + Agent | 功能邊界變更 |
| `ROADMAP.md` | 人 | Phase / 里程碑調整 |
| `SUMMARY.md` | Agent + 人審 | 每 sprint 末 |
| `TECH_DEBT.md` | Agent | 每次 stub/mock/未部署 |
| `TASKS.md` | 人 | 勾選進度 |
| `docs/go-to-market-checklist.md` | 人 | 上線週 |

---

## 11. Prompt 模板

見 [prompt-patterns.md](prompt-patterns.md)：

- `plan-before-ship`
- `scope-gate`
- `dual-metrics-review`
- `gtm-week1`
- `tech-debt-triage`
