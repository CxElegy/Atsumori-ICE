# 鳥瞰図（3D）の道具と、保留した版

- `archive/`：アイス島 アーカイブ（10の島を同じカメラで並べて・重ねて比べ、評価をつける・作例のめっちゃいい・これまでのページ）。artifact https://claude.ai/artifact/E4M1Q4XH6Df5KpCg8agxoB 。`index.tpl.html` の `/*DATA*/null` に `data.json` を入れたものが index.html。島の3Dページは build47.py（昔の候補は `ALLOW_NG=1`）、写真は shot47.js の `bird・dusk・game・cam:34,2,60,0.8,44` で撮る。島の評価はそのページのデータベース `ratings/designs`（r: 2 めっちゃいい〜-1 イマイチ、s: 10点、n: ひとこと）。

- `plan7.html`：案7（世界旅行の島＝改造プラン v4 を 3D に・第62回 v2「彫った町」）。artifact https://claude.ai/artifact/VdTLkDc9sy3G5umGiwkyw5 。データ：`tools/plan7_design.py` → `designs/plan7_spec.json`・見せ場 `designs/kits_plan7.json`。手引き `plan7_BRIEF.md`。点検 `python3 tools/plan7_design.py && ICE_PLAN=7 SEED=6 bash tools/plan3_build.sh && ICE_PLAN=7 node tools/test_plan3.js && ICE_PLAN=7 python3 tools/plan4_kitcheck.py --built && ICE_PLAN=7 python3 tools/terrain_rules.py`。画像は figures/plan7/（v1_* は4分だった v1）。
- `plan6.html`：案6（城壁の旧市街・第60回）。artifact https://claude.ai/artifact/APrzKovN5fgc37CGnzFY89 。データ：`tools/plan6_design.py` → `designs/plan6_spec.json`・見せ場 `designs/kits_plan6.json`。手引き `plan6_BRIEF.md`。点検 `ICE_PLAN=6 SEED=6 bash tools/plan3_build.sh && ICE_PLAN=6 node tools/test_plan3.js && ICE_PLAN=6 python3 tools/plan4_kitcheck.py --built && ICE_PLAN=6 python3 tools/terrain_rules.py && ICE_PLAN=6 python3 tools/town_check.py`。画像は figures/plan6/。
- `plan5c-8pt.html`：案5（5c 運河と市場の町）。ユーザー評価 8分・保留。artifact https://claude.ai/artifact/K8B3SKRiZVEa1rYzrmXzWR 第2版と同じ。
- `plan4-v23.html`：案4 第58回（v23）。artifact https://claude.ai/artifact/7Lge8tytQovrKAUpcEoY75 。
- `acnh3d_tpl.html`（three r128 のテンプレート）・`build47.py`（データを埋めこんでページを作る）・`shot47.js`（playwright で写真を撮る）。
  `ICE_ROOT=<repo>/ ICE_PLAN=5c OUT=birdseye-plan5c.html python3 birdseye/build47.py`（物の絵は acnhcdn.com から birdseye/icons/ に取る）
  `python3 -m http.server 8765 --bind 127.0.0.1` を birdseye/ で動かし、`TAG=x PAGE=... ODIR=. PW=<playwright> node shot47.js '[["bird","day","bird"]]'`
- `plan5_BRIEF.md`：案5 の設計の手引き（ユーザーの言葉・決まり・学んだこと）。
- データ：`tools/plan5c_design.py` → `designs/plan5c_spec.json`、`ICE_PLAN=5c SEED=6 bash tools/plan3_build.sh && ICE_PLAN=5c node tools/test_plan3.js`。
