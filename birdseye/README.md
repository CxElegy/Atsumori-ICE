# 鳥瞰図（3D）の道具と、保留した版

- `plan5c-8pt.html`：案5（5c 運河と市場の町）。ユーザー評価 8分・保留。artifact https://claude.ai/artifact/K8B3SKRiZVEa1rYzrmXzWR 第2版と同じ。
- `plan4-v23.html`：案4 第58回（v23）。artifact https://claude.ai/artifact/7Lge8tytQovrKAUpcEoY75 。
- `acnh3d_tpl.html`（three r128 のテンプレート）・`build47.py`（データを埋めこんでページを作る）・`shot47.js`（playwright で写真を撮る）。
  `ICE_ROOT=<repo>/ ICE_PLAN=5c OUT=birdseye-plan5c.html python3 birdseye/build47.py`（物の絵は acnhcdn.com から birdseye/icons/ に取る）
  `python3 -m http.server 8765 --bind 127.0.0.1` を birdseye/ で動かし、`TAG=x PAGE=... ODIR=. PW=<playwright> node shot47.js '[["bird","day","bird"]]'`
- `plan5_BRIEF.md`：案5 の設計の手引き（ユーザーの言葉・決まり・学んだこと）。
- データ：`tools/plan5c_design.py` → `designs/plan5c_spec.json`、`ICE_PLAN=5c SEED=6 bash tools/plan3_build.sh && ICE_PLAN=5c node tools/test_plan3.js`。
