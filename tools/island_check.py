#!/usr/bin/env python3
"""全島の計画を .claude/skills/island-planning の決まりで数える（第44回）。

  python3 tools/island_check.py          # 表で出す
  python3 tools/island_check.py --json   # 数を JSON で出す

読むもの：plan2-terrain.json（地形）・designs/lon_paths2.json（道）・designs/zones_plan2.json（地区）・
designs/build_plan2.json（第47回：あつ森で作れる建物と家具のまとまり。tools/acnh_build.py）。地形の記号は plan_terrain.py と同じ
（数字＝草地・t 木・p 道・P 案内所の広場・w 水・b 橋・s 砂・r 岩・S 海）。
"""
import json, os, sys
from collections import deque

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding='utf-8'))

T = J('plan2-terrain.json')
G, H = T['grid'], T['h']
GR = T.get('ground', {})
MH, MW = len(G), len(G[0])
Z = J('designs/zones_plan2.json')
NAMES = Z['names']
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zones import zone_cells
ZC = zone_cells(H)
ROUTES = J('designs/lon_paths2.json')['routes']
INC = T['inclines']   # [x, y, 向き]。2×4 の足もとは (x, y) から（plan_terrain.py の slope_cells と同じ）

inside = lambda x, y: 0 <= x < MW and 0 <= y < MH
g = lambda x, y: G[y][x] if inside(x, y) else 'S'
lv = lambda x, y: int(H[y][x]) if inside(x, y) else 0
zone = lambda x, y: ZC[y][x]
grass = lambda c: c in '123'

# 道（地形の p・広場 P・橋 b・lon_paths の道・坂の足もと）
road = set()
for y in range(MH):
    for x in range(MW):
        if g(x, y) in 'pPb':
            road.add((x, y))
for rt in ROUTES:
    pts = rt['pts']
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        n = max(abs(x2 - x1), abs(y2 - y1), 1)
        for i in range(n + 1):
            x, y = x1 + int((x2 - x1) * i / n), y1 + int((y2 - y1) * i / n)
            for dx in range(rt['w'] if y1 != y2 else 1):
                for dy in range(rt['w'] if x1 != x2 else 1):
                    if inside(x + dx, y + dy) and g(x + dx, y + dy) not in 'Swr':
                        road.add((x + dx, y + dy))
slope = set()
for x, y, d in INC:
    cells = [(x + i, y + j) for i in range(2) for j in range(4)] if d in 'NS' else [(x + i, y + j) for i in range(4) for j in range(2)]
    slope.update(cells)
road |= slope

# 物（第47回：あつ森で作れる物だけ。designs/build_plan2.json の本物の建物と、家具のまとまり）
from acnh_build import expand, SIZE, B as BUILD
things = []
for b in BUILD['buildings']:
    if b.get('fixed'):
        continue
    w, d = SIZE[b['kind']]; x, y = b['at']
    things.append((b['id'] + ' ' + (b.get('villager') or b.get('name', b['kind'])), zone(x, y), [x, y, x + w - 1, y + d - 1]))
bb = {}
for p in expand():
    r = bb.setdefault(p['group'], [999, 999, -1, -1])
    r[0], r[1] = min(r[0], p['x']), min(r[1], p['y']); r[2], r[3] = max(r[2], p['x'] + p['w'] - 1), max(r[3], p['y'] + p['d'] - 1)
names = {g['id']: g['name'] for g in BUILD['groups']}
from acnh_build import expand_plants
PLANTED = {(q['x'], q['y']) for q in expand_plants()}   # 花・作物の植わったマスも「物」（あき地ではない）
things += [(k + ' ' + names[k], zone(r[0], r[1]), r) for k, r in bb.items()]
occ = set(PLANTED)
for _, _, (a, b, c, d) in things:
    occ.update((x, y) for x in range(a, c + 1) for y in range(b, d + 1))

# 1. 何もない草地：草地で、木・道・水・物から2マス以上はなれている所（地区ごとの割合）
def busy(x, y):
    c = g(x, y)
    return c in 'tpPbwsrS' or GR.get('%d,%d' % (x, y)) == 'u' or (x, y) in road or (x, y) in occ
open_cells = set()
for y in range(MH):
    for x in range(MW):
        if grass(g(x, y)) and (x, y) not in road and (x, y) not in occ:
            if not any(busy(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)):
                open_cells.add((x, y))
area, opn = {}, {}
for y in range(MH):
    for x in range(MW):
        if g(x, y) in 'S':
            continue
        k = zone(x, y); area[k] = area.get(k, 0) + 1
        if (x, y) in open_cells: opn[k] = opn.get(k, 0) + 1
LIMIT = {'C': 10, 'S': 30, 'F': 15, 'B': 15, 'J': 25, 'H': 15, 'P': 25}
open_rate = {k: round(100 * opn.get(k, 0) / area[k]) for k in area}

# 2. 浮いた物：まわり1マスのうち、道が1マスもない（入口がない）か、囲み（崖・木・水・ほかの物・道）が4割未満
floating = []
for name, z, (a, b, c, d) in things:
    ring = [(x, y) for x in range(a - 1, c + 2) for y in range(b - 1, d + 2) if not (a <= x <= c and b <= y <= d)]
    ringset = set(ring)
    entry = any(p in road for p in ring) or (sum(g(x, y) == 's' for x in range(a, c + 1) for y in range(b, d + 1)) * 2 > (c - a + 1) * (d - b + 1) and any(g(*p) == 's' for p in ring))   # 浜の物は浜から入れる
    def bound(x, y):
        if (x, y) in road or (x, y) in occ or g(x, y) in 'twbrsS' or GR.get('%d,%d' % (x, y)) == 'u':
            return True
        if any((x + dx, y + dy) in ringset and g(x + dx, y + dy) == 't' for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            return True   # 木は1マスおきにしか植えられないので、木と木のあいだも並木の囲みに数える
        return inside(x, y) and lv(x, y) != lv(min(max(x, a), c), min(max(y, b), d))   # 崖
    rate = round(100 * sum(bound(*p) for p in ring) / len(ring))
    if not entry or rate < 40:
        floating.append((name, z, rate, entry))

# 3. 地区のさかいが地形（崖・水・砂・岩・林・道）に乗っているか
edge = on = 0
for y in range(MH):
    for x in range(MW):
        for dx, dy in ((1, 0), (0, 1)):
            x2, y2 = x + dx, y + dy
            if not inside(x2, y2) or g(x, y) == 'S' or g(x2, y2) == 'S' or zone(x, y) == zone(x2, y2):
                continue
            edge += 1
            if lv(x, y) != lv(x2, y2) or set(g(x, y) + g(x2, y2)) & set('wbrst') or (x, y) in road or (x2, y2) in road:
                on += 1
border_rate = round(100 * on / max(edge, 1))

# 4. 道のつながり：飛行場（いちばん下の道）からつながる道と、行き止まり・道に着かない目じるし
walk = road | {p for p in occ if inside(*p) and g(*p) not in 'wSr'} | {(x, y) for y in range(MH) for x in range(MW) if g(x, y) == 's'}   # 物の中（広場・庭・店先）と浜も歩いて通れる
def nb(x, y):
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        p = (x + dx, y + dy)
        if p in walk and (lv(*p) == lv(x, y) or p in slope or (x, y) in slope or g(*p) == 'b' or g(x, y) == 'b'):
            yield p
start = (44, 84)   # 飛行場の出口（lon_paths の P1）
seen, q = {start}, deque([start])
while q:
    for p in nb(*q.popleft()):
        if p not in seen:
            seen.add(p); q.append(p)
comps = 0; rest = set(walk) - seen
while rest:
    s = rest.pop(); qq = deque([s]); hasroad = s in road
    while qq:
        for p in nb(*qq.popleft()):
            if p in rest:
                rest.discard(p); qq.append(p); hasroad = hasroad or p in road
    comps += hasroad   # 道をふくむ切れはしだけ数える（浜や物の中だけの所は数えない）
unreached = []
for name, z, (a, b, c, d) in things:
    ring = [(x, y) for x in range(a - 1, c + 2) for y in range(b - 1, d + 2)]
    if not any(p in seen for p in ring):
        unreached.append((name, z))
blobs = 0   # 道の固まり：3×3 がまるごと道（広場 P・橋はのぞく）＝道ではなく空き地になっている所
for (x, y) in road:
    if g(x, y) in 'Pb' or (x, y) in slope:
        continue
    if all((x + dx, y + dy) in road and g(x + dx, y + dy) != 'P' for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
        blobs += 1

res = {
    'open_grass_pct': open_rate, 'open_grass_limit_pct': LIMIT,
    'floating': [{'name': n, 'zone': z, 'enclosed_pct': r, 'entry': e} for n, z, r, e in floating],
    'zone_border_on_terrain_pct': border_rate,
    'road_cells': len(road), 'road_reached_from_airport': len(seen), 'road_islands': comps,
    'landmarks_off_network': [{'name': n, 'zone': z} for n, z in unreached],
    'road_blob_cells': blobs,
}
if '--json' in sys.argv:
    print(json.dumps(res, ensure_ascii=False, indent=1)); sys.exit()
print('1. 何もない草地（木・道・水・物から2マス以上）。地区の面積に対する割合　［上限］')
for k in 'CSFBJHP':
    if k in open_rate:
        print(f'   {NAMES[k]:<8} {open_rate[k]:>3}%  ［{LIMIT[k]}%］ {"OK" if open_rate[k] <= LIMIT[k] else "多すぎ"}')
print(f'2. 浮いた物（入口の道がない・まわりの囲みが4割未満）：{len(things)} か所のうち {len(floating)} か所')
for n, z, r, e in floating:
    print(f'   {NAMES[z]}　{n}　囲み {r}%　{"" if e else "入口の道なし"}')
print(f'3. 地区のさかいが地形の上にある割合：{border_rate}%　［8割以上］')
print(f'4. 道：{len(road)} マス。飛行場からつながる {len(seen)} マス・切れた道の島 {comps} 個・道の固まり（3×3 がまるごと道）{blobs} マス')
print(f'   道に着かない目じるし：{len(unreached)}　' + '・'.join(n for n, _ in unreached))
