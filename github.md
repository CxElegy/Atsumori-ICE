repo: CxElegy/Atsumori-ICE
branch: main

## Last sync
date: 2026-10-11
### Updated in this project
- 資料「更新の要件と仕組み」（2026-10-11）をもとに、main（11bba60）の上へ実装を追加
- 美的センスのSKILL・モジュールDB・地勢計画・見本の自動配置・完成イメージ・ゲーム画面・確認の道具

## Screen map
| screen | files |
|---|---|
| ブレスト | World Travel Island Brainstorm.dc.html |
| 計画書 v1〜v4 | World Travel Island Plan.dc.html, Plan v2/v3/v4.dc.html, island-grid*.json |
| 組み立て台 | Module Builder.dc.html, plan-terrain.json, modules-curated.json, samples.json |
| 完成イメージ（俯瞰） | London Render.dc.html |
| ゲーム画面 | Game View.dc.html |

## Tools
| tool | files |
|---|---|
| モジュール | tools/gen_popular_modules.py → modules-popular.json／tools/module_db.py → db/modules.sqlite, modules-curated.json |
| 地勢 | plan-design.json → tools/plan_terrain.py → plan-terrain.json |
| 見本 | tools/gen_samples.py → samples.json |
| 確認 | tools/test_logic.js, tools/snap.js, tools/edge_run.py, tools/road_preview.js |
