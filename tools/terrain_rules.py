#!/usr/bin/env python3
"""第60回：地形があつ森で本当に作れるか（test_plan3.js の他の点検で見ていない所）。第60回の「ゲームの決まり」の審査で見つかった穴をふさぐ。

  ICE_PLAN=6 python3 tools/terrain_rules.py          # NG を一覧
  ICE_PLAN=6 python3 tools/terrain_rules.py --json   # test_plan3.js が読む

1. 滝：同じ水のマスが2方向に落ちない（角の滝）・一度に1段だけ落ちる・幅3マスまで・両わきに崖のマス（崖のふちがまっすぐ続く）
2. 水がこぼれない：上の段の水のとなり（たて横）に、それより低い陸がない（水は同じ段の陸か、滝で下の段の水にしか接しない）
3. 河口：水が海・浜・岩にふれるのは、決まった河口（西 (11,37)(12,37)(13,38〜40)、南 (70〜73,83)）とそのとなりだけ
4. 坂：上の1マス＋下の3マス、坂の上のマスの左右は上の段で崖がまっすぐ、坂の下の3マスの左右は下の段の平地（崖の壁にくっつかない）、
   上と下の出入口（2マス）は水・橋でない、まわり1マスに別の坂・橋・木がない
5. 橋と坂：橋（と両岸の 4×1）と坂のあいだを1マスあける
6. 物を置ける：物のとなりに同じ段で立てるマスがある（台をちょうどうめる塔は置けない。木・低木のマスには立てない）
"""
import json, os, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = os.environ.get('ICE_PLAN', '6')
T = json.load(open(os.path.join(ROOT, f'plan{PLAN}-terrain.json')))
G, HL = T['grid'], T['h']
W, H = len(G[0]), len(G)
g = lambda x, y: G[y][x] if 0 <= x < W and 0 <= y < H else 'S'
lv = lambda x, y: int(HL[y][x]) if 0 <= x < W and 0 <= y < H else 0
N4 = ((1, 0, 'E'), (-1, 0, 'W'), (0, 1, 'S'), (0, -1, 'N'))
MOUTH = {(11, 37), (12, 37), (13, 38), (13, 39), (13, 40), (70, 83), (71, 83), (72, 83), (73, 83)}
MOUTH_NEAR = {(x + dx, y + dy) for x, y in MOUTH for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
errs = []


def slope(inc):
    x, y, d = inc
    return [((x + i, y + k) if d in 'EW' else (x + k, y + i), i if d in 'ES' else 3 - i) for i in range(4) for k in range(2)]


SL = {c: tuple(inc) for inc in T['inclines'] for c, _ in slope(inc)}
BR = set()
BANK = set()
for x0, y0, x1, y1 in T.get('bridges', []):
    BR |= {(x, y) for y in range(y0, y1) for x in range(x0, x1)}
    if x1 - x0 == 4:   # 南北にかかる橋
        BANK |= {(x, y0 - 1) for x in range(x0, x1)} | {(x, y1) for x in range(x0, x1)}
    else:
        BANK |= {(x0 - 1, y) for y in range(y0, y1)} | {(x1, y) for y in range(y0, y1)}
water = lambda x, y: g(x, y) in 'wb'

# 1. 滝
falls = [(x, y, dn, lv(x, y), lv(x + dx, y + dy)) for y in range(H) for x in range(W) if g(x, y) == 'w'
         for dx, dy, dn in N4 if g(x + dx, y + dy) == 'w' and lv(x + dx, y + dy) < lv(x, y)]
fc = Counter((f[0], f[1]) for f in falls)
seen, groups = set(), []
for f in falls:
    if f in seen:
        continue
    x, y, dn, a, b = f
    grp = [f]; seen.add(f)
    px, py = (1, 0) if dn in 'NS' else (0, 1)
    for s in (1, -1):
        k = 1
        while (x + px * s * k, y + py * s * k, dn, a, b) in falls and (x + px * s * k, y + py * s * k, dn, a, b) not in seen:
            q = (x + px * s * k, y + py * s * k, dn, a, b); grp.append(q); seen.add(q); k += 1
    groups.append(grp)
for grp in groups:
    x, y, dn, a, b = grp[0]
    tag = f'滝 ({x},{y}) {dn}向き {a}→{b}段 幅{len(grp)}'
    if a - b >= 2:
        errs.append(f'{tag}：一度に{a - b}段落ちる（1段ずつ）')
    if len(grp) > 3:
        errs.append(f'{tag}：幅が3マスより広い')
    if any(fc[(c[0], c[1])] > 1 for c in grp):
        errs.append(f'{tag}：同じ水のマスが2方向に落ちる（角の滝）')
    if dn in 'NS':
        xs = sorted(c[0] for c in grp); ly = y + (1 if dn == 'S' else -1)
        flank = [(xs[0] - 1, y, xs[0] - 1, ly), (xs[-1] + 1, y, xs[-1] + 1, ly)]
    else:
        ys = sorted(c[1] for c in grp); lx = x + (1 if dn == 'E' else -1)
        flank = [(x, ys[0] - 1, lx, ys[0] - 1), (x, ys[-1] + 1, lx, ys[-1] + 1)]
    for ux, uy, dx_, dy_ in flank:
        if not (lv(ux, uy) == a and not water(ux, uy) and lv(dx_, dy_) < a):
            errs.append(f'{tag}：わきの ({ux},{uy}) が崖でない（{g(ux, uy)}・{lv(ux, uy)}段、下は {g(dx_, dy_)}・{lv(dx_, dy_)}段）')

# 2. 水がこぼれない
for y in range(H):
    for x in range(W):
        if g(x, y) != 'w':
            continue
        for dx, dy, _ in N4:
            a, b = x + dx, y + dy
            if g(a, b) not in 'wbSsr' and lv(a, b) < lv(x, y):
                errs.append(f'水 ({x},{y}) {lv(x, y)}段 のとなり ({a},{b}) が {lv(a, b)}段の陸（水がこぼれる）')

# 3. 河口
for y in range(H):
    for x in range(W):
        if g(x, y) == 'w' and (x, y) not in MOUTH_NEAR and any(g(x + dx, y + dy) in 'Ssr' for dx, dy, _ in N4):
            errs.append(f'水 ({x},{y}) が海・浜・岩にふれる（決まった河口のほかに河口はつくれない）')

# 4・5. 坂
for inc in T['inclines']:
    x, y, d = inc
    sc = slope(inc)
    hi = lv(*[c for c, i in sc if i == 0][0]); lo = hi - 1
    tag = f'坂 {list(inc)}'
    if d in 'NS':
        st = 1 if d == 'S' else -1; ty = y if d == 'S' else y + 3
        lows = [ty + st * k for k in (1, 2, 3)]
        for sx in (x - 1, x + 2):
            if lv(sx, ty) != hi or water(sx, ty) or lv(sx, ty + st) != lo:
                errs.append(f'{tag}：坂の上のわき ({sx},{ty}) で崖がまっすぐ続かない')
            for ry in lows:
                if lv(sx, ry) != lo or water(sx, ry):
                    errs.append(f'{tag}：坂の下のわき ({sx},{ry}) が下の段の平地でない（{g(sx, ry)}・{lv(sx, ry)}段）')
        ends = [((sx, ty - st), hi) for sx in (x, x + 1)] + [((sx, ty + 4 * st), lo) for sx in (x, x + 1)]
        ring = [(a, b) for a in range(x - 1, x + 3) for b in range(min(ty, *lows) - 1, max(ty, *lows) + 2)]
    else:
        st = 1 if d == 'E' else -1; tx = x if d == 'E' else x + 3
        lows = [tx + st * k for k in (1, 2, 3)]
        for sy in (y - 1, y + 2):
            if lv(tx, sy) != hi or water(tx, sy) or lv(tx + st, sy) != lo:
                errs.append(f'{tag}：坂の上のわき ({tx},{sy}) で崖がまっすぐ続かない')
            for rx in lows:
                if lv(rx, sy) != lo or water(rx, sy):
                    errs.append(f'{tag}：坂の下のわき ({rx},{sy}) が下の段の平地でない（{g(rx, sy)}・{lv(rx, sy)}段）')
        ends = [((tx - st, sy), hi) for sy in (y, y + 1)] + [((tx + 4 * st, sy), lo) for sy in (y, y + 1)]
        ring = [(a, b) for a in range(min(tx, *lows) - 1, max(tx, *lows) + 2) for b in range(y - 1, y + 3)]
    for (a, b), L in ends:
        if lv(a, b) != L or water(a, b) or g(a, b) in 'Ss':
            errs.append(f'{tag}：出入口 ({a},{b}) が {L}段の陸でない')
    other = {SL[c] for c in ring if c in SL and SL[c] != tuple(inc)}
    if other:
        errs.append(f'{tag}：まわり1マスに別の坂 {sorted(other)}')
    if any(c in BR or c in BANK for c in ring):
        errs.append(f'{tag}：まわり1マスに橋か橋の岸（4×1）')
    if any(g(*c) == 't' for c in ring):
        errs.append(f'{tag}：まわり1マスに木')

# 6. 物を置ける：物のとなり（たて横）に、同じ段で立てる陸のマスがある（2×2 の台をちょうどうめる塔は、立つ所がなく置けない）
sys.path.insert(0, os.path.join(ROOT, 'tools'))
os.environ['ICE_PLAN'] = PLAN
try:
    from acnh_build import expand
    LAY = json.load(open(os.path.join(ROOT, f'designs/plan{PLAN}_layout_out.json')))
    SZ = {'villager': (4, 4), 'player_house': (5, 4), 'museum': (7, 4), 'nook': (7, 4), 'able': (5, 4), 'campsite': (4, 4)}
    GRD = T.get('ground', {})
    BLD = {(x, y) for b in LAY['buildings'] for x in range(b['at'][0], b['at'][0] + SZ[b['kind']][0]) for y in range(b['at'][1], b['at'][1] + SZ[b['kind']][1])}
    for q in expand():
        cells = {(x, y) for x in range(q['x'], q['x'] + q['w']) for y in range(q['y'], q['y'] + q['d'])}
        L = lv(q['x'], q['y'])
        ring = {(x + dx, y + dy) for x, y in cells for dx, dy, _ in N4} - cells
        if not any(g(*c) in '13psb' and lv(*c) == L and c not in BLD and c not in SL and GRD.get('%d,%d' % c) != 'u' for c in ring):   # 第60回：木・低木のマスには立てない
            errs.append(f"物 {q['item']} ({q['x']},{q['y']}) {L}段：となりに同じ段の立てるマスがなく、置けない")
except FileNotFoundError:
    pass

if '--json' in sys.argv:
    print(json.dumps({'errors': errs}, ensure_ascii=False)); sys.exit()
for e in errs:
    print('NG', e)
print(f'案{PLAN}：地形の決まりの NG {len(errs)}')
sys.exit(1 if errs else 0)
