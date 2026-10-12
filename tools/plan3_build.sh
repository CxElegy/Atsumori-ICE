#!/usr/bin/env bash
# 案3（第49回）：地形 → 配置 → 中身 → 点検 を1回で
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/plan3_layout.py --seed "${SEED:-6}"
python3 tools/plan3_fill.py
python3 tools/plan3_trim.py
ICE_PLAN=3 python3 tools/acnh_build.py | tail -3
ICE_PLAN=3 python3 tools/island_check.py | sed -n '9,30p'
