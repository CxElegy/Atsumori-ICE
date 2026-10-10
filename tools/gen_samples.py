#!/usr/bin/env python3
"""見本の自動配置（標準ライブラリだけ）。地形に合わせて、全地区に見本を置く。

  使うのは組み立て台の基本モジュール（tools/base-modules.json）と、採用したもの（modules-curated.json）だけ。
  1 主役を置く     地区ごとの表 SPEC（モジュール・目標 x,y・探す半径）。半径0はその場所に、それ以外は近くで置ける所を半径×1〜3で探す
  2 道路を塗る     地形 p のマスの、草地からの距離が2以下なら道路（値 "r:地区"。ハロウィンは r:hal）。内側の広い所は広場としてモジュールで埋める
  3 道ばたの装飾   deco_* を道路に面した地面に、3マスおきに順番に置く
  4 ぎっしり埋める 左から1マスずつ、置ける候補（脇役・すき間うめ・道ばた）すべてと4つの向きを試し、点数のいちばん高いものを置く。
                   点数 = 面積（脇役は1.2倍）− 使った回数×6 + 小さいすき間うめの加点 − 同じ小物が2マス以内にある数×2.5（RHYTHM）、同じ大きさなら地面を優先
  5 上限（CAP）    1地区で同じモジュールは脇役3・すき間うめ6・道ばた8まで。1〜2マスの小物は上限なし
  6 出力           samples.json と、地区ごとの埋まり具合（埋めた・余白・空き・いちばん大きい空き地）。「map 地区」で文字の地図も出せる

ルール（tools/test_logic.js と組み立て台の「置けるか」と同じ）：水・海・岩の上、上の段と下の段にまたがる所、案内所前の広場（P）には置かない。
道路の上は小物だけ。建物（H・玄関 D のあるモジュール）は回さない（入口は南）。アメリカの森林とハイドパークの木は残す。

  使い方: python tools/gen_samples.py          samples.json を作る
          python tools/gen_samples.py map lon  文字の地図を出す
"""
import json, os, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 112, 96
GROUND = 'BpSgdwZD'
SMALL = 'LbFNiuqxnJkfeaz'
CAP = {'support': 3, 'filler': 6, 'edge': 8}

# 地区の表示範囲（組み立て台の DISTS と同じ）
DISTS = {'egy': [8, 12, 40, 62], 'jpn': [32, 12, 67, 61], 'usa': [65, 12, 101, 47], 'eur': [57, 39, 101, 85], 'port': [64, 70, 112, 94], 'lon': [16, 52, 65, 94]}
DIST_ZONES = {'egy': ['egy'], 'jpn': ['jpn'], 'usa': ['usa', 'hal'], 'eur': ['eur'], 'port': ['port'], 'lon': ['lon']}
TH = {'lon': 'ロンドン', 'egy': 'エジプト', 'jpn': '日本', 'usa': 'アメリカ', 'hal': 'ハロウィン', 'eur': 'ヨーロッパ', 'port': '地中海'}
# 地区の境目（組み立て台の ZONES と同じ。上から順に判定）
ZONES = [['hal', [[86, 0], [112, 0], [112, 25], [86, 25]]], ['usa', [[82, 25], [112, 25], [112, 46], [82, 46]]],
         ['usa', [[66, 0], [86, 0], [86, 25], [82, 25], [82, 46], [76, 46], [66, 40]]],
         ['egy', [[0, 0], [38, 0], [38, 30], [34, 34], [34, 52], [30, 56], [18, 56], [18, 84], [0, 84]]],
         ['jpn', [[38, 0], [66, 0], [66, 40], [62, 48], [62, 60], [34, 60], [34, 34], [38, 30]]],
         ['port', [[76, 72], [112, 72], [112, 96], [58, 96], [58, 84], [76, 84]]],
         ['eur', [[66, 40], [76, 46], [112, 46], [112, 72], [76, 72], [76, 84], [58, 84], [58, 60], [62, 60], [62, 48]]],
         ['lon', [[0, 84], [18, 84], [18, 56], [30, 56], [34, 52], [34, 60], [58, 60], [58, 96], [0, 96]]]]
# 木を残す所（アメリカの森林・ハイドパーク）
KEEP_TREES = [[82, 25, 112, 46], [16, 66, 32, 82]]

# 主役の表：(モジュールの id か 'LM:地区:k'=その地区の採用した主役のk番目 / 'SUP:地区:k'、目標 x, y、探す半径)
SPEC = {
    'lon': [('lon_lounge', 38, 77, 0), ('lon_934', 29, 84, 3), ('lon_park', 22, 74, 3), ('LM:lon:0', 41, 62, 3), ('house', 40, 66, 5),
            ('lon_corner', 36, 72, 6), ('lon_bus', 52, 72, 6), ('SUP:lon:0', 33, 78, 6), ('SUP:lon:1', 54, 66, 6)],
    'egy': [('museum', 27, 25, 0), ('egy_court', 27, 28, 2), ('egy_pyramid', 20, 18, 6), ('house', 24, 16, 6), ('house', 24, 46, 6), ('nook', 20, 33, 6),
            ('egy_dig', 14, 24, 6), ('egy_mkt', 22, 38, 6), ('SUP:egy:0', 12, 30, 8)],
    'jpn': [('able', 55, 15, 4), ('LM:jpn:0', 41, 15, 4), ('jpn_court', 53, 21, 4), ('jpn_tea', 48, 26, 6), ('house', 41, 36, 6),
            ('house', 49, 48, 6), ('house', 58, 45, 6), ('jpn_torii', 41, 30, 6), ('SUP:jpn:0', 44, 40, 8)],
    'usa': [('usa_diner', 80, 15, 4), ('usa_yard', 78, 24, 6), ('house', 74, 17, 6), ('camp', 90, 41, 5), ('home', 80, 42, 5), ('LM:usa:0', 93, 20, 6), ('SUP:usa:0', 70, 30, 8)],
    'eur': [('eur_cafe', 73, 45, 4), ('eur_mill', 73, 59, 6), ('able', 75, 64, 5), ('eur_eiffel', 84, 57, 8), ('house', 88, 52, 6), ('house', 83, 62, 6), ('eur_canal', 79, 53, 6), ('SUP:eur:0', 66, 74, 8)],
    'port': [('port_beach', 80, 78, 5), ('port_fish', 90, 87, 6), ('house', 80, 76, 5), ('LM:port:0', 100, 80, 8), ('SUP:port:0', 71, 82, 8)],
}
# 自分で足す大きな像のモジュール（s が6マス以上かたまると大きな建造物1つ）
LOCAL = [
    {'id': 'egy_pyramid', 'th': 'エジプト', 'r': ['sssss', 'sssss', 'sssss', 'sssss'], 'role': 'landmark'},
    {'id': 'eur_eiffel', 'th': 'ヨーロッパ', 'r': ['.ss.', 'ssss', 'ssss', 'ssss'], 'role': 'landmark'},
]


def in_poly(x, y, poly):
    px, py = x + .5, y + .5
    ins = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
            ins = not ins
        j = i
    return ins


def zone_of(x, y):
    for k, p in ZONES:
        if in_poly(x, y, p):
            return k
    return 'lon'


def rotate(rows, rot):
    r = [list(s) for s in rows]
    for _ in range(rot):
        h, w = len(r), len(r[0])
        r = [[r[h - 1 - x][y] for x in range(h)] for y in range(w)]
    return [''.join(s) for s in r]


class Mod:
    def __init__(self, d, role):
        self.id = d['id']; self.th = d['th']; self.name = d.get('name', d['id']); self.role = role
        self.rows = d['r']
        self.fixed = any(c in ''.join(self.rows) for c in 'HD')       # 建物は回さない（入口は南）
        self.rots = []
        seen = set()
        for rot in ([0] if self.fixed else range(4)):
            rr = rotate(self.rows, rot)
            k = '|'.join(rr)
            if k in seen:
                continue
            seen.add(k)
            cells = [(x, y, c) for y, row in enumerate(rr) for x, c in enumerate(row) if c != '.']
            self.rots.append((rot, cells, len(rr[0]), len(rr)))
        self.area = sum(1 for c in ''.join(self.rows) if c != '.')
        self.pure_ground = all(c in GROUND for c in ''.join(self.rows).replace('.', ''))
        self.needs_water = any(c in 'w=Z' for c in ''.join(self.rows))
        self.items = set(c for c in ''.join(self.rows) if c not in GROUND and c != '.')


class World:
    def __init__(self):
        t = json.load(open(os.path.join(ROOT, 'plan-terrain.json'), encoding='utf-8'))
        self.g = t['grid']; self.h = [[int(c) for c in row] for row in t['h']]
        self.zone = [[zone_of(x, y) for x in range(W)] for y in range(H)]
        self.placed = []              # [id, x, y, rot, zone]
        self.paint = {}               # "x,y" -> "r:地区"
        self.fur = [[None] * W for _ in range(H)]     # 家具があるマス
        self.cov = [[False] * W for _ in range(H)]    # 埋まったマス（地面・家具・道路・余白・残す木）
        self.margin = [[False] * W for _ in range(H)]
        self.road = [[False] * W for _ in range(H)]
        self.use = collections.Counter()
        self.defs = {}

    def mask_for(self, dist):
        x0, y0, x1, y1 = DISTS[dist]
        zs = set(DIST_ZONES[dist])
        return [[(x0 <= x < x1 and y0 <= y < y1 and self.zone[y][x] in zs) for x in range(W)] for y in range(H)]

    def locked(self, x, y):
        return self.g[y][x] == 't' and any(a <= x < c and b <= y < d for a, b, c, d in KEEP_TREES)

    def land(self, x, y):
        return self.g[y][x] in '13tps'

    # -- 置けるか ------------------------------------------------------------
    def ok(self, mask, cells, x, y, m, ignore_margin=False):
        lv = set()
        for dx, dy, c in cells:
            cx, cy = x + dx, y + dy
            if not (0 <= cx < W and 0 <= cy < H) or not mask[cy][cx]:
                return False
            v = self.g[cy][cx]
            if c == 'w' or c == '=' or c == 'Z':
                if c != 'Z' and v != 'w':
                    return False
                continue
            if v not in '13tps' or self.locked(cx, cy):
                return False
            lv.add(self.h[cy][cx])
            if c in GROUND:
                continue
            if self.fur[cy][cx] or (self.margin[cy][cx] and not ignore_margin):
                return False
            if self.road[cy][cx] and c not in SMALL:
                return False
        return len(lv) <= 1

    def put(self, m, rot, x, y, zone, margin=False):
        for r in m.rots:
            if r[0] == rot:
                cells, w, h = r[1], r[2], r[3]
                break
        else:
            return
        self.placed.append([m.id, x, y, rot, zone])
        self.defs[m.id] = m.rows
        if m.area > 2:
            self.use[(zone, m.id)] += 1
        hasH = False
        for dx, dy, c in cells:
            cx, cy = x + dx, y + dy
            self.cov[cy][cx] = True
            if c not in GROUND or c == 'D':
                self.fur[cy][cx] = c
            if c == 'H':
                hasH = True
        if margin or hasH:
            for dx, dy, c in cells:
                if c in 'HD':
                    for ny in (-1, 0, 1):
                        for nx in (-1, 0, 1):
                            px, py = x + dx + nx, y + dy + ny
                            if 0 <= px < W and 0 <= py < H and not self.fur[py][px]:
                                self.margin[py][px] = True
                                self.cov[py][px] = True


def load_modules():
    base = json.load(open(os.path.join(ROOT, 'tools', 'base-modules.json'), encoding='utf-8'))['modules']
    cur = json.load(open(os.path.join(ROOT, 'modules-curated.json'), encoding='utf-8'))['modules']
    mods = {}
    for d in base:
        mods[d['id']] = Mod(d, 'base')
    for d in cur:
        mods[d['id']] = Mod(d, d['role'])
    for d in LOCAL:
        mods[d['id']] = Mod(d, d['role'])
    return mods, cur


def resolve(sel, mods, cur):
    if sel in mods:
        return mods[sel]
    if ':' in sel:
        kind, th, k = sel.split(':')
        role = {'LM': 'landmark', 'SUP': 'support'}[kind]
        lst = [d for d in cur if d['role'] == role and d['th'] == TH[th] and not d['id'].startswith(('tiny', 'vig'))]
        lst.sort(key=lambda d: (-d['score'], d['id']))
        if int(k) < len(lst):
            return mods[lst[int(k)]['id']]
    return None


def search(w, mask, m, x, y, r, zone):
    """目標 (x,y) の近くで置ける所を探す。r=0 はその場所だけ。それ以外は半径 r の1〜3倍まで広げる"""
    if r == 0:
        spans = [0]
    else:
        spans = [r, r * 2, r * 3]
    best = None
    for span in spans:
        cands = []
        for yy in range(y - span, y + span + 1):
            for xx in range(x - span, x + span + 1):
                for rot, cells, mw, mh in m.rots:
                    cands.append((abs(xx - x) + abs(yy - y), xx, yy, rot, cells))
        cands.sort(key=lambda c: (c[0], c[3]))
        for _, xx, yy, rot, cells in cands:
            if w.ok(mask, cells, xx, yy, m, True):
                return xx, yy, rot
        if r == 0:
            break
    return None


def paint_roads(w, dist, mask):
    """地形 p のマスのうち、草地（1・3・t）からの距離が2以下を道路にする"""
    INF = 99
    d = [[INF] * W for _ in range(H)]
    q = collections.deque()
    for y in range(H):
        for x in range(W):
            if w.g[y][x] in '13t':
                d[y][x] = 0; q.append((x, y))
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and w.g[ny][nx] == 'p' and d[ny][nx] > d[y][x] + 1:
                d[ny][nx] = d[y][x] + 1; q.append((nx, ny))
    n = 0
    for y in range(H):
        for x in range(W):
            if mask[y][x] and w.g[y][x] == 'p' and d[y][x] <= 2 and not w.cov[y][x]:
                z = w.zone[y][x]
                w.paint['%d,%d' % (x, y)] = 'r:' + ('hal' if z == 'hal' else ('usa' if z == 'usa' else z))
                w.road[y][x] = True; w.cov[y][x] = True; n += 1
    return n


def roadside(w, dist, mask, mods, cur, zone_th):
    """道ばたの装飾（deco_*）を道路に面した地面に、3マスおきに順番に置く"""
    decos = {}
    for d in cur:
        if d['role'] == 'edge':
            decos.setdefault(d['th'], []).append(mods[d['id']])
    n = 0
    k = collections.Counter()
    last = []
    for y in range(H):
        for x in range(W):
            if not mask[y][x] or w.cov[y][x] or w.fur[y][x] or not w.land(x, y) or w.locked(x, y):
                continue
            if not any(0 <= x + dx < W and 0 <= y + dy < H and w.road[y + dy][x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                continue
            if any(abs(x - a) <= 2 and abs(y - b) <= 2 for a, b in last[-40:]):
                continue
            th = TH[w.zone[y][x]]
            lst = decos.get(th) or []
            if not lst:
                continue
            for _ in range(len(lst)):
                m = lst[k[th] % len(lst)]; k[th] += 1
                for rot, cells, mw, mh in m.rots:
                    if w.ok(mask, cells, x, y, m):
                        w.put(m, rot, x, y, w.zone[y][x]); last.append((x, y)); n += 1
                        break
                else:
                    continue
                break
    return n


def pool_for(zone, mods, cur):
    """その地区のぎっしり埋める候補：採用した脇役・すき間うめ・道ばた＋基本の広場・休憩・花壇"""
    th = TH[zone]
    out = []
    for d in cur:
        if d['th'] == th and d['role'] in ('support', 'filler') and 'Z' not in ''.join(d['r']) and 'w' not in ''.join(d['r']):
            out.append(mods[d['id']])
    for d in cur:
        if d['th'] == th and d['role'] == 'edge':
            out.append(mods[d['id']])
    from module_sets import THEME_ITEMS
    from gen_popular_modules import GROUNDS
    zk = zone
    allowed = set(THEME_ITEMS[zk])
    grounds = set(GROUNDS[zk])
    seen = {m.id for m in out}
    for mid, m in mods.items():
        if m.role == 'base' and m.th in ('広場', '休憩', '花壇') and mid not in seen and m.items <= allowed | set('F') and not m.needs_water and not m.fixed and set(c for c in ''.join(m.rows) if c in 'BpSgd') <= grounds:
            out.append(m); seen.add(mid)
    return out


def fill(w, dist, mask, zone_pools):
    """左から1マスずつ、置ける候補と4つの向きを試して、点数のいちばん高いものを置く"""
    def near(cells, x, y, m):
        n = 0
        for dx, dy, c in cells:
            if c in GROUND:
                continue
            cx, cy = x + dx, y + dy
            for yy in range(cy - 2, cy + 3):
                for xx in range(cx - 2, cx + 3):
                    if 0 <= xx < W and 0 <= yy < H and w.fur[yy][xx] == c:
                        n += 1
        return n
    x0, y0, x1, y1 = DISTS[dist]
    for y in range(y0, y1):
        for x in range(x0, x1):
            if not mask[y][x] or w.cov[y][x] or not w.land(x, y) or w.locked(x, y):
                continue
            zone = w.zone[y][x]
            best = None
            for m in zone_pools[zone]:
                if m.area > 2 and w.use[(zone, m.id)] >= CAP.get(m.role, 6):
                    continue
                for rot, cells, mw, mh in m.rots:
                    new = sum(1 for dx, dy, c in cells if 0 <= y + dy < H and 0 <= x + dx < W and not w.cov[y + dy][x + dx])
                    if not new or not w.ok(mask, cells, x, y, m):
                        continue
                    pts = new * (1.2 if m.role == 'support' else 1) - w.use[(zone, m.id)] * 6 + (3 if m.area <= 2 else 0) - near(cells, x, y, m) * 2.5 + (0.5 if m.pure_ground else 0)
                    if best is None or pts > best[0]:
                        best = (pts, m, rot)
            if best:
                w.put(best[1], best[2], x, y, zone)
    # 残った穴（最後の手段）：1マスの地面
    for y in range(y0, y1):
        for x in range(x0, x1):
            if mask[y][x] and not w.cov[y][x] and w.land(x, y) and not w.locked(x, y):
                z = w.zone[y][x]
                m = zone_pools[z][0] if False else None
                for cand in zone_pools[z]:
                    if cand.area <= 2:
                        for rot, cells, mw, mh in cand.rots:
                            if w.ok(mask, cells, x, y, cand):
                                w.put(cand, rot, x, y, z); m = cand; break
                    if m:
                        break


def stats_for(w, dist, mask):
    """埋めた・余白・空き・いちばん大きい空き地"""
    x0, y0, x1, y1 = DISTS[dist]
    total = filled = margin = empty = 0
    free = [[False] * W for _ in range(H)]
    for y in range(y0, y1):
        for x in range(x0, x1):
            if not mask[y][x] or not w.land(x, y) or w.g[y][x] in 'PKb':
                continue
            total += 1
            if w.margin[y][x] and not w.fur[y][x]:
                margin += 1
            elif w.cov[y][x] or w.locked(x, y):
                filled += 1
            else:
                empty += 1; free[y][x] = True
    big = 0
    for y in range(y0, y1):
        for x in range(x0, x1):
            n = 0
            while n < 12 and all(0 <= y + j < H and 0 <= x + n < W and free[y + j][x + n] for j in range(n + 1)) and all(free[y + n][x + i] for i in range(n + 1)):
                n += 1
            big = max(big, n)
    return {'total': total, 'filled': filled, 'margin': margin, 'empty': empty, 'biggest_empty': big}


def build():
    mods, cur = load_modules()
    w = World()
    out = {'dists': {}, 'paint': {}, 'stats': {}}
    pools = {z: pool_for(z, mods, cur) for z in TH}
    for dist in DISTS:
        mask = w.mask_for(dist)
        n0 = len(w.placed)
        # 1 主役
        for sel, x, y, r in SPEC.get(dist, []):
            m = resolve(sel, mods, cur)
            if not m:
                print('警告: 主役が見つかりません', dist, sel, file=sys.stderr); continue
            pos = search(w, mask, m, x, y, r, dist)
            if not pos:
                print('警告: 主役を置けません', dist, sel, (x, y), 'r=%d' % r, file=sys.stderr); continue
            zone = w.zone[pos[1]][pos[0]]
            w.put(m, pos[2], pos[0], pos[1], zone, margin=(m.role == 'landmark' or m.id in ('house', 'home', 'museum', 'nook', 'able', 'camp')))
        # 2 道路
        nr = paint_roads(w, dist, mask)
        # 3 道ばた
        ne = roadside(w, dist, mask, mods, cur, None)
        # 4〜5 ぎっしり埋める
        fill(w, dist, mask, pools)
        out['dists'][dist] = [[p[0], p[1], p[2], p[3]] for p in w.placed[n0:]]
        out['paint'][dist] = {k: v for k, v in w.paint.items() if mask[int(k.split(',')[1])][int(k.split(',')[0])]}
        s = stats_for(w, dist, mask)
        s.update({'items': len(out['dists'][dist]), 'road': len(out['paint'][dist]), 'roadside': ne})
        out['stats'][dist] = s
    out['defs'] = w.defs
    out['stats']['all'] = {'items': sum(s['items'] for s in out['stats'].values()), 'modules': len(w.defs),
                           'road': sum(s['road'] for k, s in out['stats'].items() if k != 'all' and 'road' in s)}
    return out, w


def show_map(w, dist):
    mask = w.mask_for(dist)
    x0, y0, x1, y1 = DISTS[dist]
    cell = {}
    for mid, x, y, rot, z in w.placed:
        pass
    grid = [[' '] * W for _ in range(H)]
    for y in range(y0, y1):
        for x in range(x0, x1):
            if mask[y][x]:
                grid[y][x] = '#' if w.road[y][x] else ('m' if (w.margin[y][x] and not w.fur[y][x]) else ('·' if w.cov[y][x] else '_'))
                if w.fur[y][x]:
                    grid[y][x] = w.fur[y][x]
    for y in range(y0, y1):
        print(''.join(grid[y][x0:x1]))


def main():
    out, w = build()
    with open(os.path.join(ROOT, 'samples.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    if len(sys.argv) > 2 and sys.argv[1] == 'map':
        show_map(w, sys.argv[2]); return
    print('%-5s %6s %6s %6s %6s %8s' % ('地区', '置く地面', '埋めた', '余白', '空き', '最大空き'))
    for d in DISTS:
        s = out['stats'][d]
        print('%-5s %6d %6d %6d %6d %8d   置いた%d・道路%d' % (d, s['total'], s['filled'], s['margin'], s['empty'], s['biggest_empty'], s['items'], s['road']))
    a = out['stats']['all']
    print('見本：%d か所・モジュール %d 種・道路 %d マス' % (a['items'], a['modules'], a['road']))


if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
