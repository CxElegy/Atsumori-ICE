#!/usr/bin/env bash
# アイス島：計画データから確認・ビルドガイドまでを1回で作り直す
#   bash tools/build_all.sh [出力の置き場]
#   1 地勢（plan-design.json → plan-terrain.json。案2 は plan2-design.json → plan2-terrain.json と tools/test_plan2.js）  2 見本の配置（samples.json）  3 確認（tools/test_logic.js）
#   4 ビルドガイド（1枚の HTML：地図・立体図・モジュール・草図・断面・作例・マイデザイン図鑑・準備）
#   作例の写真の置き場は ICE_CACHE（index.json と 000.jpg… のフォルダをスペース区切り）。写真は作者のものなので、出力はリポジトリに入れない
#   立体図には playwright（PW）と Chromium（CHROME）が要る。なければ立体図なしで作る
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; OUT="${1:-$ROOT/../ice-build}"; mkdir -p "$OUT"; cd "$ROOT"
python3 tools/plan_terrain.py --quiet
python3 tools/gen_samples.py | tail -1
node tools/test_logic.js | tail -1
python3 tools/plan_terrain.py --design plan2-design.json --out plan2-terrain.json --quiet   # 案2（第45回）
python3 tools/acnh_build.py   # 第47回：あつ森で作れるか（建物・家具・花・木）
node tools/test_plan2.js | tail -3
bash tools/plan3_build.sh >/dev/null   # 案3（第49回）：地形から作り直した島（種 seed から作る）
node tools/test_plan3.js | tail -3
python3 tools/plan4_design.py >/dev/null && ICE_PLAN=4 bash tools/plan3_build.sh >/dev/null   # 案4（第54回）：手で描いた島
ICE_PLAN=4 node tools/test_plan3.js | tail -3
if [ -z "${ICE_CACHE:-}" ]; then echo "ICE_CACHE がないので、ビルドガイドは作りません（確認まで）"; exit 0; fi
python3 tools/build_site.py --cache $ICE_CACHE --out "$OUT/ice-guide.html" --board "$OUT/board.json" | tail -1
if node -e "require(process.env.PW || 'playwright')" 2>/dev/null; then
  node tools/site/render_views.js "$OUT/board.json" "$OUT/views.json" "${UNPKG_CACHE:-}" | tail -1
  python3 tools/build_site.py --cache $ICE_CACHE --out "$OUT/ice-guide.html" --board "$OUT/board.json" --views "$OUT/views.json" | tail -1
fi
