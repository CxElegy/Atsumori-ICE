#!/usr/bin/env python3
"""第60回：町の底層（土台）を数で確かめる。案5（5c）でユーザーに言われた弱い所を、案ごとにくらべられるように。

  ICE_PLAN=6 python3 tools/town_check.py            # 表で見る
  ICE_PLAN=6 python3 tools/town_check.py --json     # test_plan3.js が読む
  ICE_PLAN=6 python3 tools/town_check.py --detail   # NG の場所を全部

数えること（町＝地区 C と P）
  1. 門脸（ファサード）：町の建物の南（入口の前から6列・建物の幅＋左右1マス）に、建物より高い地面がない
     （カメラは南から北を見るので、南の高い段が入口と壁をかくす。5c の北の家の列は南の2段目・3段目にかくれた）
  2. 坂と橋の数、町の坂の数
  3. 二層に上がれるか：町の2段目以上の陸のうち、飛行場から歩いて（坂を使って）行けるマスの割合（テラス）と、行けないマス（屋根）
  4. 護城河：町の陸のマスから東西南北に10マス見て、3方向以上に水（川・運河・橋）がある所の割合（5c の市場は三方が水）
  5. 町の水：町の陸に対する水と橋の割合（1割前後。test は15%まで）
  6. 屋根：歩いて上がれないかたまりの上の屋根の種類（灰色の平らなレンガ屋根 brick_grey の割合）
  7. 軸：spec の axis（{"x0","x1","y0","y1"}：飛行場 → 広場 → 石段 → 塔の帯）の中の坂の数、上る段、つきあたりの目じるし、軸をふさぐ物
  8. 町の木の数・広場のまわり（3マス以内）の木
  9. 見えない物：物の南どなり（1〜2列）に高い段がある（崖の裏）・家の真裏（建物の北1〜2列）・北向きのパネル
 10. 複雑さ：町の2段目以上のかたまりの数・町の崖のふちの長さ・町の滝
"""
import json, os, sys
from collections import deque, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding='utf-8'))
PLAN = os.environ.get('ICE_PLAN', '6')
T = J(f'plan{PLAN}-terrain.json')
LAY = J(f'designs/plan{PLAN}_layout_out.json')
SPEC = J(f'designs/plan{PLAN}_spec.json')
BP = J(f'designs/build_plan{PLAN}.json')
CAT = J('designs/acnh_catalog.json')['items']
G, HL = T['grid'], T['h']
Z = T.get('zones') or ['S' * 112] * 96
W, H = len(G[0]), len(G)
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
inside = lambda x, y: 0 <= x < W and 0 <= y < H
g = lambda x, y: G[y][x] if inside(x, y) else 'S'
lv = lambda x, y: int(HL[y][x]) if inside(x, y) else 0
town = lambda x, y: inside(x, y) and Z[y][x] in 'CP'
SIZE = {'villager': (4, 4), 'player_house': (5, 4), 'museum': (7, 4), 'nook': (7, 4), 'able': (5, 4), 'campsite': (4, 4)}

sys.path.insert(0, os.path.join(ROOT, 'tools'))
os.environ['ICE_PLAN'] = PLAN
from acnh_build import expand  # noqa: E402
ITEMS = expand()

bld = {}
for b in LAY['buildings']:
    w, d = SIZE[b['kind']]; x0, y0 = b['at']
    for y in range(y0, y0 + d):
        for x in range(x0, x0 + w):
            bld[(x, y)] = b
slope = {}
for i, (x, y, d) in enumerate(T['inclines']):
    for c in ([(x + a, y + b) for a in range(2) for b in range(4)] if d in 'NS' else [(x + a, y + b) for a in range(4) for b in range(2)]):
        slope[c] = i
TALL = {'castle tower', 'castle gate', 'lighthouse', 'windmill', 'plaza ferris wheel', 'tall lantern', 'castle wall'}
res, bad = {}, {}
MOAT_R = int(os.environ.get('MOAT_R', 14))   # 護城河：4方向に何マスまで見るか

# 1. ファサード
fac = []
for b in LAY['buildings']:
    x0, y0 = b['at']; w, d = SIZE[b['kind']]; L = lv(x0, y0)
    if not town(x0, y0):
        continue
    worst = None
    for k in range(6):
        y = y0 + d + k
        for x in range(x0 - 1, x0 + w + 1):
            if inside(x, y) and g(x, y) not in 'wSs' and lv(x, y) > L:
                worst = worst or (x, y, lv(x, y) - L, k)
    tall = [(p['item'], p['x'], p['y']) for p in ITEMS if p['item'] in TALL and x0 - 1 <= p['x'] <= x0 + w and y0 + d <= p['y'] <= y0 + d + 3]
    if worst or tall:
        fac.append({'b': b.get('villager') or b['kind'], 'at': [x0, y0], 'level': L, 'higher_south': worst, 'tall_south': tall})
res['facade_blocked'] = fac

# 2. 坂と橋
res['inclines'] = len(T['inclines']); res['bridges'] = len(T.get('bridges', []))
res['inclines_town'] = sum(1 for x, y, d in T['inclines'] if town(x, y))

# 2b. 井戸の石段（5a）：坂の下の3マスが、上の段を切りこんだ「井戸」の中にある（坂の左右2マス目が上の段の崖）。通りを横切らない
wells = []
for (x, y, d) in T['inclines']:
    cs = [(x + a, y + b) for a in range(2) for b in range(4)] if d in 'NS' else [(x + a, y + b) for a in range(4) for b in range(2)]
    hi = max(lv(*c) for c in cs)
    if d in 'NS':
        rows = range(y + 1, y + 4) if d == 'S' else range(y, y + 3)
        side = [(x - 2, r) for r in rows] + [(x + 3, r) for r in rows]
    else:
        cols = range(x + 1, x + 4) if d == 'E' else range(x, x + 3)
        side = [(c, y - 2) for c in cols] + [(c, y + 3) for c in cols]
    if sum(lv(*c) >= hi and g(*c) not in 'wb' for c in side) >= len(side) - 1:
        wells.append([x, y, d])
res['well_stairs'] = wells

# 2c. 通りにそった運河（5a）：町の道のマスで、東西南北の2マス以内に水（運河）がある所
cs_ = 0
for y in range(H):
    for x in range(W):
        if town(x, y) and g(x, y) == 'p' and any(g(x + dx * k, y + dy * k) == 'w' and lv(x + dx * k, y + dy * k) <= lv(x, y) for dx, dy in N4 for k in (1, 2)):
            cs_ += 1
res['canal_street_cells'] = cs_

# 3. 二層に上がれるか（物を置く前の地形で、草地も歩ける）
start = tuple(SPEC['start'])
open_ = {(x, y) for y in range(H) for x in range(W) if g(x, y) in '13psbPt' and (x, y) not in bld} | set(slope)
seen = {start}; q = deque([start])
while q:
    x, y = q.popleft()
    for dx, dy in N4:
        n = (x + dx, y + dy)
        if n in seen or n not in open_:
            continue
        ok = lv(x, y) == lv(*n) or g(x, y) == 'b' or g(*n) == 'b' or ({g(x, y), g(*n)} & {'s'} and max(lv(x, y), lv(*n)) <= 1)
        if not ok and (x, y) in slope and slope.get(n) == slope[(x, y)]:
            ok = True
        if ok:
            seen.add(n); q.append(n)
up = [(x, y) for y in range(H) for x in range(W) if town(x, y) and lv(x, y) >= 2 and g(x, y) not in 'wb']
up_r = [c for c in up if c in seen or c in bld and any(n in seen for n in [(c[0] + dx, c[1] + dy) for dx, dy in N4])]
upb = set(up) - {c for c in up if c in seen}
res['upper_cells'] = len(up); res['upper_walkable'] = len([c for c in up if c in seen or c in bld])
res['upper_walkable_pct'] = round(100 * res['upper_walkable'] / max(1, len(up)))
res['upper_tier3_walkable'] = sum(1 for c in up if lv(*c) == 3 and (c in seen or c in bld))
res['upper_tier3'] = sum(1 for c in up if lv(*c) == 3)
road_up = [(x, y) for y in range(H) for x in range(W) if g(x, y) == 'p' and lv(x, y) >= 2 and (x, y) not in seen]
res['roads_on_unreachable_upper'] = len(road_up)
bad['roads_on_unreachable_upper'] = road_up[:20]

# 4. 護城河（4方向に10マス：水か橋に当たるまで。町の外・海・浜・段ちがいの陸は止まらない）
tl = [(x, y) for y in range(H) for x in range(W) if town(x, y) and g(x, y) in '13pt']
enc = []
for x, y in tl:
    n = 0
    for dx, dy in N4:
        for k in range(1, MOAT_R + 1):
            a, b_ = x + dx * k, y + dy * k
            c = g(a, b_)
            if c in 'Ss':
                break
            if c in 'wb':
                n += 1; break
    if n >= 3:
        enc.append((x, y))
res['moat_cells'] = len(enc); res['moat_pct'] = round(100 * len(enc) / max(1, len(tl)), 1)
bad['moat'] = enc[:40]

# 5. 町の水
tw = [(x, y) for y in range(H) for x in range(W) if town(x, y) and g(x, y) not in 'Ssr']
wat = sum(1 for c in tw if g(*c) in 'wb')
res['town_water_pct'] = round(100 * wat / max(1, len(tw)), 1)
zr = [z['rect'] for z in SPEC.get('zones', []) if z.get('zone') in 'CP' and z.get('rect')]
land = wat2 = 0
for y in range(H):
    for x in range(W):
        if g(x, y) in 'Ssr' or not any(a <= x <= c and b <= y <= d for a, b, c, d in zr):
            continue
        land += 1; wat2 += g(x, y) in 'wb'
res['town_water_pct_test'] = round(100 * wat2 / max(1, land), 1)

# 6. 屋根
rc = Counter()
for gd in BP.get('ground', []):
    if gd['id'] == 'C-roof':
        rc[gd['design']] += 1
roofp = sum(1 for p in BP.get('plants', []) if p['id'] == 'C-roofgarden')
fort = sum(1 for gp in BP['groups'] if gp['id'] == 'C-roofs' for it in gp['items'] if it[0] == 'castle wall')
res['roof_tiles'] = dict(rc); res['roof_garden_cells'] = roofp; res['roof_castle_walls'] = fort
tot = sum(rc.values()) + roofp
res['roof_grey_pct'] = round(100 * rc.get('brick_grey', 0) / max(1, tot))
res['roof_cells_total'] = tot

# 7. 軸
ax = SPEC.get('axis')
if ax:
    x0, x1, y0, y1 = ax['x0'], ax['x1'], ax['y0'], ax['y1']
    band = lambda x, y: x0 <= x <= x1 and y0 <= y <= y1
    incs = [i for i in T['inclines'] if any(band(*c) for c, k in slope.items() if k == T['inclines'].index(i))]
    tiers = sorted({lv(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1) if g(x, y) not in 'wSs'})
    term = [(p['item'], p['x'], p['y'], lv(p['x'], p['y'])) for p in ITEMS if p['item'] in TALL and x0 - 4 <= p['x'] <= x1 + 4 and y0 - 2 <= p['y'] <= y0 + ax.get('term_rows', 8)]
    block = [(p['item'], p['x'], p['y']) for p in ITEMS if p['item'] in TALL and band(p['x'], p['y']) and p['y'] > y0 + ax.get('term_rows', 8)]
    trees = [(x, y) for y in range(y0 + ax.get('term_rows', 8) + 1, y1 + 1) for x in range(x0, x1 + 1) if g(x, y) == 't']
    bl = [(b.get('villager') or b['kind']) for b in LAY['buildings'] if any(band(*c) for c, bb in bld.items() if bb is b)]
    towers = [(p['x'], p['y'], lv(p['x'], p['y'])) for p in ITEMS if p['item'] == 'castle tower' and x0 - 6 <= p['x'] <= x1 + 6 and y0 - 2 <= p['y'] <= y1]
    res['axis'] = {'stairs': len(incs), 'tiers': tiers, 'terminus': term, 'blocking_tall': block, 'trees_in_band': trees, 'buildings_in_band': bl, 'towers': towers}

# 8. 木
tt = [(x, y) for y in range(H) for x in range(W) if town(x, y) and g(x, y) == 't']
res['town_trees'] = len(tt); res['island_trees'] = sum(r.count('t') for r in G)
P = [(x, y) for y in range(H) for x in range(W) if g(x, y) == 'P']
px0, py0 = min(p[0] for p in P), min(p[1] for p in P); px1, py1 = max(p[0] for p in P), max(p[1] for p in P)
res['plaza_trees'] = sum(1 for x, y in tt if px0 - 3 <= x <= px1 + 3 and py0 - 3 <= y <= py1 + 3)
res['plaza_box'] = [px0, py0, px1, py1]

# 9. 見えない物
hid = []
tallc = {(x, y) for q in ITEMS if q['item'] in TALL for x in range(q['x'], q['x'] + q['w']) for y in range(q['y'], q['y'] + q['d'])}
for p in ITEMS:
    if p['item'] in ('manhole cover',) or not town(p['x'], p['y']):
        continue
    L = lv(p['x'], p['y']); yb = p['y'] + p['d'] - 1
    for x in range(p['x'], p['x'] + p['w']):
        if any(inside(x, yb + k) and g(x, yb + k) not in 'wSs' and lv(x, yb + k) - L >= k for k in (1, 2)):
            hid.append((p['item'], p['x'], p['y'], 'cliff')); break
        if (x, yb + 1) in bld or (x, yb + 2) in bld:
            hid.append((p['item'], p['x'], p['y'], 'house')); break
        if p['item'] not in TALL and ((x, yb + 1) in tallc or (x, yb + 2) in tallc):
            hid.append((p['item'], p['x'], p['y'], 'tall')); break   # 第60回：城の塔・門・城壁の真うしろ
npan = sum(1 for p in ITEMS if 'panel' in p['item'] and p.get('rot') == 2)
res['hidden_items'] = len(hid); res['north_panels'] = npan
res['side_panels'] = sum(1 for p in ITEMS if 'panel' in p['item'] and p.get('rot') in (1, 3) and town(p['x'], p['y']))   # 東・西を向く（カメラから横向き）
bad['hidden'] = hid[:40]

# 10. 複雑さ
comps, sn = 0, set()
for c in up:
    if c in sn:
        continue
    q = [c]; sn.add(c); n = 0
    while q:
        x, y = q.pop(); n += 1
        for dx, dy in N4:
            m = (x + dx, y + dy)
            if m in sn or not town(*m) or g(*m) in 'wb' or lv(*m) < 2:
                continue
            sn.add(m); q.append(m)
    comps += n >= 4
edges = sum(1 for x, y in tw for dx, dy in ((1, 0), (0, 1)) if town(x + dx, y + dy) and g(x, y) not in 'w' and g(x + dx, y + dy) not in 'w' and lv(x, y) != lv(x + dx, y + dy))
falls = sum(1 for x, y in tw if g(x, y) == 'w' and any(g(x + dx, y + dy) == 'w' and lv(x + dx, y + dy) < lv(x, y) for dx, dy in N4))
res['upper_blocks'] = comps; res['cliff_edge_len'] = edges; res['town_waterfall_cells'] = falls
# 第60回：複雑さ（「城镇越复杂越好」）：広すぎる道（3×3 がまるごと道）・南北の断面で段が変わる回数（層の重なり）
road = {(x, y) for y in range(H) for x in range(W) if g(x, y) == 'p'}
res['wide_road_cells'] = sum(1 for (x, y) in road if town(x, y) and all((x + dx, y + dy) in road for dx in (-1, 0, 1) for dy in (-1, 0, 1)))
cols = [x for x in range(W) if sum(town(x, y) and g(x, y) not in 'Ssr' for y in range(H)) >= 20]
ch = []
for x in cols:
    ys = [y for y in range(H) if town(x, y) and g(x, y) not in 'Ssrw']
    ch.append(sum(1 for a, b in zip(ys, ys[1:]) if b == a + 1 and lv(x, a) != lv(x, b)))
res['section_changes_avg'] = round(sum(ch) / max(1, len(ch)), 1)
tc = Counter(lv(*c) for c in tw if g(*c) not in 'wb')
res['town_tiers'] = {str(k): v for k, v in sorted(tc.items())}

if '--json' in sys.argv:
    print(json.dumps(res, ensure_ascii=False)); sys.exit()
print(f'案{PLAN} の町の土台')
print(f' 1. 門脸：南の高い段・高い物に入口がかくれる町の建物 {len(fac)} 軒')
for f in fac:
    print(f"      {f['b']} {f['at']} {f['level']}段　南の高い段 {f['higher_south']}　南の高い物 {f['tall_south']}")
print(f" 2. 坂 {res['inclines']}（町 {res['inclines_town']}）・橋 {res['bridges']}")
print(f" 2b. 井戸の石段 {len(wells)}：{wells}　2c. 運河にそった通り {cs_} マス")
print(f" 3. 町の2段目以上 {res['upper_cells']} マスのうち歩いて上がれる {res['upper_walkable']}（{res['upper_walkable_pct']}%）・3段目 {res['upper_tier3_walkable']}/{res['upper_tier3']}・上がれない段の上の道 {res['roads_on_unreachable_upper']}")
print(f" 4. 護城河：3方向以上が水の町の陸 {res['moat_cells']} マス（{res['moat_pct']}%）")
print(f" 5. 町の水 {res['town_water_pct']}%（test の数え方 {res['town_water_pct_test']}%）")
print(f" 6. 屋根 {res['roof_cells_total']} マス：{res['roof_tiles']}・屋上の庭 {res['roof_garden_cells']}・城壁 {res['roof_castle_walls']}・灰色の平らな屋根 {res['roof_grey_pct']}%")
if ax:
    a = res['axis']
    print(f" 7. 軸：石段 {a['stairs']}・段 {a['tiers']}・つきあたり {a['terminus']}・軸をふさぐ高い物 {a['blocking_tall']}・軸の木 {len(a['trees_in_band'])}・軸の建物 {a['buildings_in_band']}・軸のまわりの塔 {a['towers']}")
else:
    print(' 7. 軸：spec に axis がない')
print(f" 8. 町の木 {res['town_trees']}（島 {res['island_trees']}）・広場のまわりの木 {res['plaza_trees']}")
print(f" 9. 見えない物 {res['hidden_items']}・北向きのパネル {res['north_panels']}・東西を向くパネル {res['side_panels']}")
print(f" 11. 広すぎる道（3×3 がまるごと道）{res['wide_road_cells']} マス・南北の断面で段が変わる回数（平均）{res['section_changes_avg']}")
print(f" 10. 2段目以上のかたまり {res['upper_blocks']}・崖のふち {res['cliff_edge_len']}・町の滝 {res['town_waterfall_cells']}・段の割合 {res['town_tiers']}")
if '--detail' in sys.argv:
    print('見えない物', bad['hidden']); print('護城河', bad['moat']); print('上がれない段の道', bad['roads_on_unreachable_upper'])
