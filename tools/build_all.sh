#!/usr/bin/env bash
# アイス島：計画データから確認・ビルドガイドまでを1回で作り直す
#   bash tools/build_all.sh [出力の置き場]
#   1 地勢（plan-design.json → plan-terrain.json）  2 見本の配置（samples.json）  3 確認（tools/test_logic.js）
#   4 ビルドガイド（1枚の HTML：地図・立体図・モジュール・草図・断面・作例・マイデザイン図鑑・準備）
#   作例の写真の置き場は ICE_CACHE（index.json と 000.jpg… のフォルダをスペース区切り）。写真は作者のものなので、出力はリポジトリに入れない
#   立体図には playwright（PW）と Chromium（CHROME）が要る。なければ立体図なしで作る
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; OUT="${1:-$ROOT/../ice-build}"; mkdir -p "$OUT"; cd "$ROOT"
python3 tools/plan_terrain.py --quiet
python3 tools/gen_samples.py | tail -1
node tools/test_logic.js | tail -1
if [ -z "${ICE_CACHE:-}" ]; then echo "ICE_CACHE がないので、ビルドガイドは作りません（確認まで）"; exit 0; fi
python3 tools/build_site.py --cache $ICE_CACHE --out "$OUT/ice-guide.html" --board "$OUT/board.json" | tail -1
if node -e "require(process.env.PW || 'playwright')" 2>/dev/null; then
  node tools/site/render_views.js "$OUT/board.json" "$OUT/views.json" "${UNPKG_CACHE:-}" | tail -1
  python3 tools/build_site.py --cache $ICE_CACHE --out "$OUT/ice-guide.html" --board "$OUT/board.json" --views "$OUT/views.json" | tail -1
fi
