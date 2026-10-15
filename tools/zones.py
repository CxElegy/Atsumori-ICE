#!/usr/bin/env python3
"""全島の地区（案2）を1マスずつ塗る。designs/zones_plan2.json の paint を上から順に塗る（第44回）。

  from zones import zone_cells      # → 96 行 × 112 字（C S F B J H P）
  python3 tools/zones.py            # 地区ごとのマス数
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def zone_cells(h=None):
    Z = json.load(open(os.path.join(ROOT, 'designs/zones_plan2.json'), encoding='utf-8'))
    if h is None:
        h = json.load(open(os.path.join(ROOT, 'plan2-terrain.json'), encoding='utf-8'))['h']
    H, W = len(h), len(h[0])
    z = [['S'] * W for _ in range(H)]
    for code, r, *_ in Z['paint']:
        x0, y0, x1, y1 = r[:4]; minh = r[4] if len(r) > 4 else 0
        for y in range(max(y0, 0), min(y1, H - 1) + 1):
            for x in range(max(x0, 0), min(x1, W - 1) + 1):
                if int(h[y][x]) >= minh:
                    z[y][x] = code
    return [''.join(r) for r in z]


if __name__ == '__main__':
    from collections import Counter
    c = Counter(''.join(zone_cells()))
    print(' '.join('%s %d' % kv for kv in sorted(c.items())))
