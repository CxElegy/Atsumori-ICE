#!/usr/bin/env python3
"""案3（第49回）：plan3_gen.py の地形に、建物・坂・橋・道を置く。

  python3 tools/plan3_layout.py --seed 6     # plan3-terrain.json と designs/build_plan3.json を作る

1. 地形の手直し（設計の意図）：designs/plan3_spec.json の edits（段をならす所など）
2. 建物：spec の buildings を、ねらいの場所のいちばん近い「建てられる所」に置く（建物の大きさ・まわり1マスの同じ段の平地・入口の前 3×2・建物どうし1マス）
3. 道：飛行場の出口から、案内所の広場・建物の入口・目じるしへ、A* で引く（ななめも可・ノイズで少しまがる）。
   水は橋の候補（水3〜5マス・幅4・両岸が同じ段）でだけ、段ちがいは坂の候補（2×4・まっすぐな崖）でだけ越える。坂と橋は8本まで
"""
import heapq, json, math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plan3_gen as gen

ROOT = gen.ROOT
W, H = gen.W, gen.H
N4, N8 = gen.N4, gen.N8
inside = gen.inside
SIZE = {'villager': (4, 4), 'player_house': (5, 4), 'museum': (7, 4), 'nook': (7, 4), 'able': (5, 4), 'campsite': (4, 4)}


def front_cells(kind, x0, y0):
    w, d = SIZE[kind]
    cols = range(x0, x0 + w) if w % 2 == 0 else range(x0 + w // 2 - 1, x0 + w // 2 + 2)
    rows = 1 if kind in ('museum', 'campsite') else 2
    if kind == 'campsite':
        cols = range(x0 + 1, x0 + 3)
    return [(x, y0 + d + k) for x in cols for k in range(rows)]


class Layout:
    def __init__(self, isl, spec):
        self.isl, self.g, self.h, self.spec = isl, isl.g, isl.h, spec
        self.rng = random.Random(isl.seed * 31 + 5)
        self.noise = gen.Noise(isl.seed * 11 + 9, 6)
        self.reserved = set()     # 設計で場所を決めた見せ場（道を通さない）
        self.blocked = set()      # 建物の土地・入口の前・坂
        self.buildings, self.inclines, self.bridges, self.roads = [], [], [], set()
        self.log = []

    lv = lambda self, x, y: self.h[y][x] if inside(x, y) else 0
    def flat(self, x, y):
        return inside(x, y) and self.g[y][x] in '13tp' and (x, y) not in self.blocked

    # ---- 建物 ----
    def can_build(self, kind, x0, y0):
        w, d = SIZE[kind]
        L = self.lv(x0, y0)
        for y in range(y0 - 1, y0 + d + 1):
            for x in range(x0 - 1, x0 + w + 1):
                if not inside(x, y) or self.g[y][x] not in '13tp' or self.lv(x, y) != L:
                    return False
                if (x, y) in self.blocked or any((x + dx, y + dy) in self.house for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                    return False
        for x, y in front_cells(kind, x0, y0):
            if not inside(x, y) or self.g[y][x] not in '13tp' or self.lv(x, y) != L or (x, y) in self.blocked:
                return False
        return True

    def place(self, b):
        self.house = getattr(self, 'house', set())
        kind, (tx, ty), rad = b['kind'], b['near'], b.get('r', 10)
        best = None
        for y in range(ty - rad, ty + rad + 1):
            for x in range(tx - rad, tx + rad + 1):
                if self.can_build(kind, x, y):
                    dd = math.hypot(x - tx, y - ty)
                    if best is None or dd < best[0]:
                        best = (dd, x, y)
        if not best:
            self.log.append(f"建物 {b['id']} を置けない（{b['near']} のまわり {rad}）"); return
        _, x0, y0 = best; w, d = SIZE[kind]
        for y in range(y0, y0 + d):
            for x in range(x0, x0 + w):
                self.blocked.add((x, y)); self.house.add((x, y))
                if self.g[y][x] in 'tp':
                    self.g[y][x] = '1' if self.h[y][x] < 2 else '3'
        for p in front_cells(kind, x0, y0):
            self.blocked.add(p)
        self.ring = getattr(self, 'ring', set()) | {(x, y) for x in range(x0 - 1, x0 + w + 1) for y in range(y0 - 1, y0 + d + 1)}   # 建物のまわり1マス（坂・橋はあける）
        nb = dict(b); nb.pop('near'); nb.pop('r', None); nb['at'] = [x0, y0]
        nb['door'] = [x0 + w // 2, y0 + d]
        self.buildings.append(nb)

    # ---- 坂と橋の候補 ----
    def incline_ok(self, x, y, d):
        cells = gen_slope(x, y, d)
        top = [c for c, i in cells if i == 0]
        hi = self.lv(*top[0])
        if hi < 2:
            return False
        for (cx, cy), i in cells:
            if not inside(cx, cy) or self.g[cy][cx] not in '13t' or (cx, cy) in self.blocked or (cx, cy) in getattr(self, 'ring', ()) or self.lv(cx, cy) != (hi if i == 0 else hi - 1):
                return False
        # 上と下の出口（2マス）・崖がまっすぐ（坂の左右の崖のふちが続く）・まわり1マスに別の坂がない
        dx, dy = {'S': (0, 1), 'N': (0, -1), 'E': (1, 0), 'W': (-1, 0)}[d]
        tops = [c for c, i in cells if i == 0]; bots = [c for c, i in cells if i == 3]
        for (cx, cy) in tops:
            a, b = cx - dx, cy - dy
            if not inside(a, b) or self.g[b][a] not in '13tp' or self.lv(a, b) != hi:
                return False
        for (cx, cy) in bots:
            a, b = cx + dx, cy + dy
            if not inside(a, b) or self.g[b][a] not in '13tp' or self.lv(a, b) != hi - 1:
                return False
        side = [(-dy, dx), (dy, -dx)]
        for (sx, sy) in side:
            for (cx, cy) in tops:
                a, b = cx + sx, cy + sy
                if (a, b) in [c for c, _ in cells]:
                    continue
                if not inside(a, b) or self.lv(a, b) != hi or not inside(a + dx, b + dy) or self.lv(a + dx, b + dy) != hi - 1:
                    return False
        for (cx, cy), _ in cells:
            for ex, ey in N8:
                if (cx + ex, cy + ey) in self.slopecells:
                    return False
        return True

    def bridge_spans(self):
        out = []
        for y in range(H):
            for x in range(W):
                for vert in (True, False):
                    for L in (3, 4, 5):
                        if vert:
                            span = [(x + i, y + j) for i in range(4) for j in range(L)]
                            b1 = [(x + i, y - 1) for i in range(4)]; b2 = [(x + i, y + L) for i in range(4)]
                        else:
                            span = [(x + j, y + i) for i in range(4) for j in range(L)]
                            b1 = [(x - 1, y + i) for i in range(4)]; b2 = [(x + L, y + i) for i in range(4)]
                        if not all(inside(*c) and self.g[c[1]][c[0]] == 'w' for c in span):
                            continue
                        if not all(inside(*c) and self.g[c[1]][c[0]] in '13tp' and (c not in self.blocked) and c not in getattr(self, 'ring', ()) for c in b1 + b2):
                            continue
                        lvls = {self.lv(*c) for c in b1 + b2} | {self.lv(*c) for c in span}
                        if len(lvls) != 1:
                            continue
                        out.append({'span': span, 'banks': (b1, b2), 'vert': vert, 'L': L, 'rect': [x, y, x + (4 if vert else L), y + (L if vert else 4)]})
        return out

    # ---- 道（A*）----
    def build_graph(self):
        self.slopecells = set(c for inc in self.inclines for c, _ in gen_slope(*inc))
        self.inc_cand = []
        for y in range(H):
            for x in range(W):
                for d in 'NSEW':
                    if self.incline_ok(x, y, d):
                        self.inc_cand.append((x, y, d))
        self.br_cand = self.bridge_spans()
        self.edges = {}
        for k, (x, y, d) in enumerate(self.inc_cand):
            cells = gen_slope(x, y, d); dx, dy = {'S': (0, 1), 'N': (0, -1), 'E': (1, 0), 'W': (-1, 0)}[d]
            top = [c for c, i in cells if i == 0][0]; bot = [c for c, i in cells if i == 3][0]
            a = (top[0] - dx, top[1] - dy); b = (bot[0] + dx, bot[1] + dy)
            self.edges.setdefault(a, []).append((b, ('inc', k))); self.edges.setdefault(b, []).append((a, ('inc', k)))
        sites = self.spec.get('bridge_sites', [])
        self.br_pref = set()   # 設計で橋をかけたい所（bridge_sites）の近くの橋は安くする
        for k, br in enumerate(self.br_cand):
            x0, y0, x1, y1 = br['rect']
            if any(math.hypot((x0 + x1) / 2 - px, (y0 + y1) / 2 - py) <= 5 for px, py, _ in sites):
                self.br_pref.add(k)
        for k, br in enumerate(self.br_cand):
            a, b = br['banks'][0][1], br['banks'][1][1]
            self.edges.setdefault(a, []).append((b, ('br', k))); self.edges.setdefault(b, []).append((a, ('br', k)))

    def astar(self, starts, goal_set):
        built_inc = {tuple(i) for i in self.inclines}; built_br = {tuple(b['rect']) for b in self.bridges}
        def walk(x, y):
            return inside(x, y) and self.g[y][x] in '13tpKPs' and (x, y) not in self.house and (x, y) not in self.reserved
        pq, best, prev = [], {}, {}
        for s in starts:
            best[s] = 0; heapq.heappush(pq, (0, 0, s))
        gx = sum(p[0] for p in goal_set) / len(goal_set); gy = sum(p[1] for p in goal_set) / len(goal_set)
        while pq:
            _, c, (x, y) = heapq.heappop(pq)
            if (x, y) in goal_set:
                path, cur = [], (x, y)
                while cur in prev:
                    path.append((cur, prev[cur][1])); cur = prev[cur][0]
                path.append((cur, None)); return path[::-1]
            if c > best.get((x, y), 1e9):
                continue
            for dx, dy in N8:
                a, b = x + dx, y + dy
                if not walk(a, b) or self.lv(a, b) != self.lv(x, y):
                    continue
                if dx and dy and (not walk(x + dx, y) or not walk(x, y + dy) or self.lv(x + dx, y) != self.lv(x, y) or self.lv(x, y + dy) != self.lv(x, y)):
                    continue
                step = (1.42 if dx and dy else 1) * (1.15 + .5 * self.noise(a, b))
                if (a, b) in self.roads:
                    step *= .35
                if any(inside(a + ex, b + ey) and self.g[b + ey][a + ex] == 'w' for ex, ey in N4):
                    step += .6   # 水ぎわは少しさける
                nc = c + step
                if nc < best.get((a, b), 1e9):
                    best[(a, b)] = nc; prev[(a, b)] = ((x, y), None); heapq.heappush(pq, (nc + .9 * math.hypot(a - gx, b - gy), nc, (a, b)))
            for (a, b), e in self.edges.get((x, y), []):
                kind, k = e
                key = tuple(self.inc_cand[k]) if kind == 'inc' else tuple(self.br_cand[k]['rect'])
                built = key in (built_inc if kind == 'inc' else built_br)
                if not built and len(self.inclines if kind == 'inc' else self.bridges) >= 8:
                    continue
                nc = c + (6 if built else (3 if kind == "br" and k in self.br_pref else 14 if kind == "br" else 18))   # 橋・坂を新しくかけるのは少し高い（遠回りよりは安い）
                if nc < best.get((a, b), 1e9):
                    best[(a, b)] = nc; prev[(a, b)] = ((x, y), e); heapq.heappush(pq, (nc + .9 * math.hypot(a - gx, b - gy), nc, (a, b)))
        return None

    def connect(self, targets, w=2, name=''):
        if not self.roads:
            self.roads |= set(targets); return True
        path = self.astar(list(self.roads), set(targets))
        if not path:
            self.log.append(f'道 {name}：つながらない'); return False
        for (x, y), e in path:
            if e:
                kind, k = e
                if kind == 'inc':
                    inc = tuple(self.inc_cand[k])
                    if inc not in {tuple(i) for i in self.inclines}:
                        self.inclines.append(list(inc)); self.blocked |= {c for c, _ in gen_slope(*inc)}; self.slopecells |= {c for c, _ in gen_slope(*inc)}
                else:
                    br = self.br_cand[k]
                    if tuple(br['rect']) not in {tuple(b['rect']) for b in self.bridges}:
                        self.bridges.append(br)
                        for cx, cy in br['span']:
                            self.g[cy][cx] = 'b'
                        for side in br['banks']:
                            self.roads |= set(side); self.blocked |= set(side)
        cells = [p for p, _ in path]
        self.paths = getattr(self, 'paths', []) + [(name, cells, [e for _, e in path if e])]
        for i, (x, y) in enumerate(cells):
            for dx in range(w):
                for dy in range(w):
                    a, b = x + dx - (w - 1) // 2, y + dy - (w - 1) // 2
                    if inside(a, b) and self.g[b][a] in '13t' and (a, b) not in self.blocked and self.lv(a, b) == self.lv(x, y):
                        self.roads.add((a, b))
            self.roads.add((x, y))
        return True

    def paint_roads(self):
        for x, y in self.roads:
            if self.g[y][x] in '13t':
                self.g[y][x] = 'p'


def gen_slope(x, y, d):
    """坂の 2×4 のマス（plan_terrain.py の slope_cells と同じ。S・E は (x,y) が上の段、N・W は下のはしが (x,y)）と、上からの順番 i"""
    out = []
    for i in range(4):
        for k in range(2):
            if d in 'NS':
                out.append(((x + k, y + i), i if d == 'S' else 3 - i))
            else:
                out.append(((x + i, y + k), i if d == 'E' else 3 - i))
    return out


def force_bridge(isl, px, py, orient):
    """橋をかけられる川の形にととのえる：幅4の帯で、水を3〜5マスのまっすぐな流れにし、両岸を同じ段の陸にする（あつ森の橋の決まり）"""
    g, h = isl.g, isl.h
    if orient == 'NS':   # 橋は南北にのびる（東西に流れる川をまたぐ）
        cols = range(px, px + 4); runs = []
        for x in cols:
            ys = [y for y in range(py - 6, py + 7) if inside(x, y) and g[y][x] == 'w']
            runs += ys
        if not runs:
            return False
        y0, y1 = min(runs), max(runs); L = y1 - y0 + 1
        if L > 5:
            c = (y0 + y1) // 2; y0, y1 = c - 1, c + 2
        elif L < 3:
            y1 = y0 + 2
        lvl = min(h[y][x] for x in cols for y in range(y0, y1 + 1) if g[y][x] == 'w') if any(g[y][x] == 'w' for x in cols for y in range(y0, y1 + 1)) else 1
        for x in cols:
            for y in range(py - 6, py + 7):
                if not inside(x, y) or g[y][x] in 'SsrKP':
                    continue
                if y0 <= y <= y1:
                    g[y][x] = 'w'; h[y][x] = lvl
                elif g[y][x] == 'w' and (y in (y0 - 1, y1 + 1) or abs(y - (y0 + y1) / 2) < 5):
                    g[y][x] = '1'; h[y][x] = lvl
            for y in (y0 - 1, y1 + 1, y0 - 2, y1 + 2):
                if inside(x, y) and g[y][x] not in 'SsrKP':
                    g[y][x] = '1' if g[y][x] == 'w' else g[y][x]; h[y][x] = lvl
    else:
        rows = range(py, py + 4); runs = []
        for y in rows:
            runs += [x for x in range(px - 6, px + 7) if inside(x, y) and g[y][x] == 'w']
        if not runs:
            return False
        x0, x1 = min(runs), max(runs); L = x1 - x0 + 1
        if L > 5:
            c = (x0 + x1) // 2; x0, x1 = c - 1, c + 2
        elif L < 3:
            x1 = x0 + 2
        lvl = min(h[y][x] for y in rows for x in range(x0, x1 + 1) if g[y][x] == 'w') if any(g[y][x] == 'w' for y in rows for x in range(x0, x1 + 1)) else 1
        for y in rows:
            for x in range(px - 6, px + 7):
                if not inside(x, y) or g[y][x] in 'SsrKP':
                    continue
                if x0 <= x <= x1:
                    g[y][x] = 'w'; h[y][x] = lvl
                elif g[y][x] == 'w' and (x in (x0 - 1, x1 + 1) or abs(x - (x0 + x1) / 2) < 5):
                    g[y][x] = '1'; h[y][x] = lvl
            for x in (x0 - 1, x1 + 1, x0 - 2, x1 + 2):
                if inside(x, y) and g[y][x] not in 'SsrKP':
                    g[y][x] = '1' if g[y][x] == 'w' else g[y][x]; h[y][x] = lvl
    return True


def force_incline(isl, px, py, d):
    """坂を置ける形にととのえる：(px,py) の近くの崖のふちを探し、坂の 2×4 とその左右・出入口を、上の段と下の段にまっすぐそろえる"""
    g, h = isl.g, isl.h
    dx, dy = {'S': (0, 1), 'N': (0, -1), 'E': (1, 0), 'W': (-1, 0)}[d]   # 下りる向き
    best = None
    for y in range(py - 6, py + 7):
        for x in range(px - 6, px + 7):
            if inside(x, y) and inside(x + dx, y + dy) and h[y][x] >= 2 and h[y + dy][x + dx] == h[y][x] - 1 and g[y][x] in '13' and g[y + dy][x + dx] in '13':
                dd = math.hypot(x - px, y - py)
                if best is None or dd < best[0]:
                    best = (dd, x, y)
    if not best:
        return None
    _, tx, ty = best; hi = h[ty][tx]
    sx, sy = -dy, dx   # 崖にそった向き
    # 上の段：坂の上（2マス幅）とその左右1マス、奥へ2マス。下の段：坂の3マスとその左右1マス、出口へ1マス
    for k in range(-1, 3):
        for back in range(0, 3):
            x, y = tx + sx * k - dx * back, ty + sy * k - dy * back
            if inside(x, y) and g[y][x] in '13':
                h[y][x] = hi
        for fwd in range(1, 5):
            x, y = tx + sx * k + dx * fwd, ty + sy * k + dy * fwd
            if inside(x, y) and g[y][x] in '13':
                h[y][x] = hi - 1
    # 坂の基点（gen_slope の決まり：S・E は上の段の角、N・W は下のはし）
    if d == 'S': return (tx, ty, 'S')
    if d == 'E': return (tx, ty, 'E')
    if d == 'N': return (tx, ty - 3, 'N')
    return (tx - 3, ty, 'W')


def run(seed):
    spec = json.load(open(os.path.join(ROOT, 'designs/plan3_spec.json')))
    isl = gen.build(seed)
    for e in spec.get('edits', []):
        x0, y0, x1, y1 = e['rect']
        for y in range(y0, y1):
            for x in range(x0, x1):
                if isl.land(x, y) and isl.g[y][x] != 'w':
                    isl.h[y][x] = e['h']
    for px, py, o in spec.get('bridge_sites', []):
        force_bridge(isl, px, py, o)
    for px, py, o in spec.get('incline_sites', []):
        r = force_incline(isl, px, py, o)
        if r is None:
            print('坂の場所が見つからない', px, py, o)
    isl.fix_tiers()
    lay = Layout(isl, spec)
    for b in spec['buildings']:
        lay.place(b)
    # 設計で場所を決めた見せ場（spec の kits の at）は、道を通さないように先にとっておく
    KS = json.load(open(os.path.join(ROOT, 'designs/kits.json')))['kits']
    for kd in spec.get('kits', []):
        if 'at' in kd:
            (ax, ay), (kw, kh) = kd['at'], KS[kd['kit']]['size']
            lay.reserved |= {(x, y) for x in range(ax, ax + kw) for y in range(ay, ay + kh)}
    lay.blocked |= lay.reserved
    lay.build_graph()
    # 飛行場の出口から（飛行場のすぐ北の浜の上を始まりに）
    start = tuple(spec['start'])
    lay.roads.add(start)
    for r in spec['routes']:
        if 'bridge' in r:   # 設計の橋：いちばん近い橋の候補の両岸へ道を引く（片方は橋を渡る）
            px, py = r['bridge']
            k = min(range(len(lay.br_cand)), key=lambda k: math.hypot((lay.br_cand[k]['rect'][0] + lay.br_cand[k]['rect'][2]) / 2 - px, (lay.br_cand[k]['rect'][1] + lay.br_cand[k]['rect'][3]) / 2 - py))
            for bank in lay.br_cand[k]['banks']:
                lay.connect(bank, r.get('w', 2), r.get('name', 'bridge'))
            continue
        tgt = r['to']
        if isinstance(tgt, str):
            b = next((b for b in lay.buildings if b['id'] == tgt), None)
            if not b:
                continue
            x0, y0 = b['at']; w, d = SIZE[b['kind']]
            targets = [(x, y0 + d) for x in range(x0, x0 + w)]   # 入口の前の1列目（建物のまわり1マスに道が触れる）
        else:
            targets = [tuple(t) for t in tgt]
        lay.connect(targets, r.get('w', 2), r.get('name', str(tgt)))
    # 設計の通り（spec の streets）：折れ線で引く通り（同じ段だけ。水・建物・坂の上はとばす）
    for st in spec.get('streets', []):
        pts = st['path']; w = st.get('w', 2)
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            n = max(abs(x2 - x1), abs(y2 - y1), 1)
            for i in range(n + 1):
                x, y = round(x1 + (x2 - x1) * i / n), round(y1 + (y2 - y1) * i / n)
                for dx in range(w):
                    for dy in range(w):
                        a, b = x + dx - (w - 1) // 2, y + dy - (w - 1) // 2
                        if inside(a, b) and isl.g[b][a] in '13t' and (a, b) not in lay.blocked:
                            lay.roads.add((a, b))
    lay.paint_roads()
    return isl, lay


if __name__ == '__main__':
    arg = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
    seed = int(arg('--seed', 6))
    isl, lay = run(seed)
    for l in lay.log:
        print(l)
    print('建物', len(lay.buildings), '坂', len(lay.inclines), '橋', len(lay.bridges), '道', len(lay.roads), '坂の候補', len(lay.inc_cand), '橋の候補', len(lay.br_cand))
    T = isl.dump(); T['inclines'] = lay.inclines; T['bridges'] = [b['rect'] for b in lay.bridges]
    json.dump(T, open(os.path.join(ROOT, 'plan3-terrain.json'), 'w'))
    json.dump({'buildings': lay.buildings}, open(os.path.join(ROOT, 'designs/plan3_layout_out.json'), 'w'), ensure_ascii=False, indent=1)
