#!/usr/bin/env python3
"""地勢計画から計画の地形を作る（標準ライブラリだけ）。

入力  island-grid-v4.json（今の島・変えない）と plan-design.json（{note, measure, ops}）
出力  plan-terrain.json（{note, grid, h, inclines, stats}）
        grid  表面の記号（96行×112文字）  h  高さ 0〜3（96行×112文字）  inclines  坂 [x, y, 向き]

ops は書いた順に、3つの段階で使う。
  1 土地の形   level（四角 rect か多角形 poly の範囲を段 h に）・flatten（小さな切れ端をならす）・river（直線の川）・
               stream（自然な川。点ごとに幅 [x,y,w]）・fillwater（川・池を埋める。keep の四角は残す）・unroad / set
  2 決まりで直す（自動）  浜・海・岩のとなりに崖を作らない／3段目は2段目の1マス内側から／水面はその台地の段
  3 坂と道   incline（近くの置ける所に坂 2×4 を探して置く）・road（道。段をまたぐと注意）・bridge（橋。川幅3〜5・幅4・両岸が平ら）
坂と橋は8個まで。案内所前の広場（P）と9¾番線のレンガ（K）は変えない。

  使い方: python tools/plan_terrain.py [--quiet]
"""
import json, os, sys, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 112, 96
LIMIT = 8
KEEP = 'PK'          # 変えない記号
NOCLIFF = 'Ssr'      # 海・砂浜・岩（となりに崖を作らない）


def load():
    grid = [list(r) for r in json.load(open(os.path.join(ROOT, 'island-grid-v4.json'), encoding='utf-8'))]
    h = [[0 if c in 'Sr' else (2 if c == '3' else 1) for c in row] for row in grid]
    return grid, h


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


def in_rect(x, y, r):
    return r[0] <= x < r[2] and r[1] <= y < r[3]


def region(op):
    if 'rect' in op:
        r = op['rect']
        return [(x, y) for y in range(max(r[1], 0), min(r[3], H)) for x in range(max(r[0], 0), min(r[2], W))]
    return [(x, y) for y in range(H) for x in range(W) if in_poly(x, y, op['poly'])]


def brush(cx, cy, w):
    """幅 w の丸い筆：偶数は角を中心に、奇数はマスの中心を中心に"""
    off = .5 if w % 2 == 0 else 0
    cx += .5 + off; cy += .5 + off
    r = w / 2 + .01
    n = int(w // 2 + 2)
    out = []
    for y in range(int(cy) - n, int(cy) + n + 1):
        for x in range(int(cx) - n, int(cx) + n + 1):
            if math.hypot(x + .5 - cx, y + .5 - cy) <= r:
                out.append((x, y))
    return out


def stroke(path):
    """点 [x, y, w] を結んだ線を、幅を変えながら丸い筆でなぞったマス"""
    cells = set()
    for a, b in zip(path, path[1:]) if len(path) > 1 else [(path[0], path[0])]:
        n = max(abs(b[0] - a[0]), abs(b[1] - a[1]), 1) * 2
        for i in range(n + 1):
            t = i / n
            x = a[0] + (b[0] - a[0]) * t; y = a[1] + (b[1] - a[1]) * t
            w = a[2] + (b[2] - a[2]) * t
            cells.update(brush(round(x), round(y), max(1, round(w))))
    return [(x, y) for x, y in cells if 0 <= x < W and 0 <= y < H]


def line_cells(path, w):
    return stroke([[p[0], p[1], w] for p in path])


class Terrain:
    def __init__(self):
        self.grid, self.h = load()
        self.inclines = []
        self.bridges = []
        self.warn = []
        self.ground = {}
        self.cnt = {}

    # -- 1 土地の形 --------------------------------------------------------
    def level(self, op):
        hv = op['h']
        for x, y in region(op):
            c = self.grid[y][x]
            if c in 'Srs' or c in KEEP or c == 'b':
                continue
            self.h[y][x] = hv

    def flatten(self, op):
        mn = op.get('min', 8)
        seen = set()
        for y in range(H):
            for x in range(W):
                if self.h[y][x] >= 2 and (x, y) not in seen:
                    comp, st = [], [(x, y)]
                    seen.add((x, y))
                    while st:
                        cx, cy = st.pop(); comp.append((cx, cy))
                        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in seen and self.h[ny][nx] == self.h[cy][cx]:
                                seen.add((nx, ny)); st.append((nx, ny))
                    if len(comp) < mn:
                        for cx, cy in comp:
                            self.h[cy][cx] -= 1

    def water(self, cells):
        for x, y in cells:
            if self.grid[y][x] in 'Sr' or self.grid[y][x] in KEEP:
                continue
            self.grid[y][x] = 'w'
            self.h[y][x] = max(self.h[y][x], 1)

    def river(self, op):
        self.water(line_cells(op['path'], op.get('w', 1)))

    def stream(self, op):
        self.water(stroke(op['path']))

    def fillwater(self, op):
        keep = op.get('keep', [])
        for x, y in region(op):
            if self.grid[y][x] == 'w' and not any(in_rect(x, y, k) for k in keep):
                self.grid[y][x] = '1'
                self.h[y][x] = max(self.h[y][x], 1)

    def dry(self, op):
        """枯れ流れ：水を使わず白砂に砂紋（箒目）を引いた川。地形は変えず、地面の模様（m）として残す"""
        for x, y in stroke([[p[0], p[1], op.get('w', 3)] for p in op['path']]):
            if self.grid[y][x] in '13tp':
                self.ground['%d,%d' % (x, y)] = 'm'

    def unroad(self, op):
        for x, y in region(op):
            if self.grid[y][x] == 'p':
                self.grid[y][x] = '1'

    def set(self, op):
        for x, y in region(op):
            if self.grid[y][x] in KEEP:
                continue
            self.grid[y][x] = op['v']

    # -- 2 決まりで直す ------------------------------------------------------
    def fix(self):
        g, h = self.grid, self.h
        lowered = 0
        for y in range(H):
            for x in range(W):
                if g[y][x] in 'Sr':
                    h[y][x] = 0
                elif g[y][x] == 's':
                    h[y][x] = 1
                elif g[y][x] in KEEP or g[y][x] == 'b':
                    h[y][x] = 1
        # 浜・海・岩のとなりに崖を作らない
        for y in range(H):
            for x in range(W):
                if h[y][x] >= 2 and any(0 <= x + dx < W and 0 <= y + dy < H and g[y + dy][x + dx] in NOCLIFF
                                        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    h[y][x] = 1; lowered += 1
        # 3段目は2段目の1マス内側から
        for y in range(H):
            for x in range(W):
                if h[y][x] == 3 and any(not (0 <= x + dx < W and 0 <= y + dy < H) or h[y + dy][x + dx] < 2
                                        for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                    h[y][x] = 2; lowered += 1
        # 表面：草地は段で見た目を変える（1=下の段・3=上の段）
        for y in range(H):
            for x in range(W):
                if g[y][x] in '13':
                    g[y][x] = '3' if h[y][x] >= 2 else '1'
        self.cnt['lowered'] = lowered

    # -- 3 坂と道 ---------------------------------------------------------------
    def slope_rect(self, x, y, d):
        if d == 'S': return (x, y, x + 2, y + 4)
        if d == 'N': return (x, y, x + 2, y + 4)
        return (x, y, x + 4, y + 2)

    def slope_cells(self, x, y, d, hi):
        """(マス, 段) の並び：上の1マス（高い段）と下の3マス"""
        out = []
        if d == 'S':
            for i in range(4):
                for dx in range(2): out.append(((x + dx, y + i), hi if i == 0 else hi - 1))
        elif d == 'N':
            for i in range(4):
                for dx in range(2): out.append(((x + dx, y + i), hi if i == 3 else hi - 1))
        elif d == 'E':
            for i in range(4):
                for dy in range(2): out.append(((x + i, y + dy), hi if i == 0 else hi - 1))
        else:
            for i in range(4):
                for dy in range(2): out.append(((x + i, y + dy), hi if i == 3 else hi - 1))
        return out

    def slope_ok(self, x, y, d, hi, strict):
        g, h = self.grid, self.h
        cells = self.slope_cells(x, y, d, hi)
        for (cx, cy), lv in cells:
            if not (0 <= cx < W and 0 <= cy < H) or g[cy][cx] in 'wSsrPKb' or h[cy][cx] != lv:
                return False
        ax, ay = {'S': (0, 1), 'N': (0, -1), 'E': (1, 0), 'W': (-1, 0)}[d]      # 下る向き
        ups = [c for c, lv in cells if lv == hi]
        lows = [c for c, lv in cells if lv == hi - 1]
        # 下を水に向けない：坂の先（下の端のすぐ先）が水でない
        far = max(c[0] * ax + c[1] * ay for c in lows)
        for c in lows:
            if c[0] * ax + c[1] * ay == far:
                ex, ey = c[0] + ax, c[1] + ay
                if not (0 <= ex < W and 0 <= ey < H) or g[ey][ex] == 'w':
                    return False
        # ほかの坂・橋と1マスあける
        mine = {c for c, _ in cells}
        others = []
        for o in self.inclines:
            others += [c for c, _ in self.slope_cells(o[0], o[1], o[2], 9)]
        for b in self.bridges:
            others += b
        if any(abs(a[0] - b[0]) <= 1 and abs(a[1] - b[1]) <= 1 for a in mine for b in others):
            return False
        if strict:   # まっすぐな崖：坂の両どなりも、上の段のふち（上＝高い段・その先＝1段下）がつづく
            px, py = abs(ay), abs(ax)
            u0 = min(ups, key=lambda c: c[0] * px + c[1] * py)
            u1 = max(ups, key=lambda c: c[0] * px + c[1] * py)
            for base, k in ((u0, -1), (u1, 1)):
                a = (base[0] + px * k, base[1] + py * k)
                b = (a[0] + ax, a[1] + ay)
                if not (0 <= a[0] < W and 0 <= a[1] < H and 0 <= b[0] < W and 0 <= b[1] < H):
                    return False
                if h[a[1]][a[0]] != hi or h[b[1]][b[0]] != hi - 1:
                    return False
        return True

    def incline(self, op):
        nx, ny = op['near']; hi = op['from']; d = op['dir']
        if len(self.inclines) >= LIMIT:
            raise SystemExit('坂が%d個を超えます' % LIMIT)
        cand = [(x, y) for y in range(max(ny - 14, 0), min(ny + 15, H)) for x in range(max(nx - 14, 0), min(nx + 15, W))]
        cand.sort(key=lambda c: (max(abs(c[0] - nx), abs(c[1] - ny)), abs(c[0] - nx) + abs(c[1] - ny)))
        for strict in (True, False):
            for x, y in cand:
                if self.slope_ok(x, y, d, hi, strict):
                    self.inclines.append([x, y, d])
                    return
        raise SystemExit('坂を置ける所が見つかりません near=%s from=%s dir=%s' % (op['near'], hi, d))

    def road_cells(self, path, w):
        """道のマス：まっすぐな区間は両端をそろえ（先をまるくしない）、幅は組み立て台の stamp と同じ並べ方"""
        o = (w - 1) // 2
        cells = set()
        for a, b in zip(path, path[1:]):
            n = max(abs(b[0] - a[0]), abs(b[1] - a[1]), 1)
            for i in range(n + 1):
                x = a[0] + round((b[0] - a[0]) * i / n); y = a[1] + round((b[1] - a[1]) * i / n)
                if a[0] == b[0]:
                    cells.update((x - o + k, y) for k in range(w))
                elif a[1] == b[1]:
                    cells.update((x, y - o + k) for k in range(w))
                else:
                    cells.update((x - o + i2, y - o + j2) for i2 in range(w) for j2 in range(w))
        return [(x, y) for x, y in cells if 0 <= x < W and 0 <= y < H]

    def road(self, op):
        cells = self.road_cells(op['path'], op.get('w', 1))
        for x, y in cells:
            if self.grid[y][x] in 'wSsrPKb':
                continue
            self.grid[y][x] = 'p'
        hs = {self.h[y][x] for x, y in cells if self.grid[y][x] == 'p'}
        if len(hs) > 1:
            self.warn.append('道が段をまたぐ：%s（%s）' % (op['path'], op.get('why', '')[:20]))

    def bridge(self, op):
        if len(self.bridges) + sum(1 for r in self.grid for c in r if False) >= LIMIT:
            raise SystemExit('橋が%d個を超えます' % LIMIT)
        x0, y0, x1, y1 = op['rect']
        wx, wy = x1 - x0, y1 - y0
        if wx == 4 and 3 <= wy <= 5:
            banks = [[(x, y0 - 1) for x in range(x0, x1)], [(x, y1) for x in range(x0, x1)]]
        elif wy == 4 and 3 <= wx <= 5:
            banks = [[(x0 - 1, y) for y in range(y0, y1)], [(x1, y) for y in range(y0, y1)]]
        else:
            raise SystemExit('橋は川幅3〜5・幅4：%s' % op['rect'])
        for y in range(y0, y1):
            for x in range(x0, x1):
                if self.grid[y][x] != 'w':
                    raise SystemExit('橋の下が水でない (%d,%d)：%s' % (x, y, op['rect']))
        lv = set()
        for bank in banks:
            for x, y in bank:
                if self.grid[y][x] in 'wSsr':
                    raise SystemExit('橋の両岸が陸でない (%d,%d)：%s' % (x, y, op['rect']))
                lv.add(self.h[y][x])
        if len(lv) != 1:
            raise SystemExit('橋の両岸が平らでない（段 %s）：%s' % (sorted(lv), op['rect']))
        for y in range(y0, y1):
            for x in range(x0, x1):
                self.grid[y][x] = 'b'; self.h[y][x] = lv.copy().pop()
        self.bridges.append([(x, y) for y in range(y0, y1) for x in range(x0, x1)])

    def forest(self, op):
        """林：1マスおき（x・y とも偶数のマス、行ごとに少しずらす）に木（竹林も t）を植える。草地だけ。
        道・水・橋・坂・広場のとなりと、clear の四角（目じるし・畑など）はあける。dens は植える割合（0〜1）"""
        dens = op.get('dens', .6); clear = op.get('clear', [])
        slope = {c for o in self.inclines for c, _ in self.slope_cells(o[0], o[1], o[2], 9)}
        g = self.grid
        n = 0
        for x, y in region(op):
            if (y % 2) or ((x + (y // 2) % 2) % 2):
                continue
            if g[y][x] not in '13' or (x, y) in slope or any(in_rect(x, y, [r[0], r[1], r[2] + 1, r[3] + 1]) for r in clear):
                continue
            if any(0 <= x + dx < W and 0 <= y + dy < H and (g[y + dy][x + dx] in 'pPbwKSr' or (x + dx, y + dy) in slope)
                   for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                continue
            if ((x * 73856093) ^ (y * 19349663)) % 1000 / 1000 < dens:
                g[y][x] = 't'; n += 1
        bush = op.get('bush', 0)   # 低木（記号 u・地面の模様として残す）：木の間をうめて林を濃くする。低木はとなり合ってよい
        if bush:
            for x, y in region(op):
                if g[y][x] not in '13' or (x, y) in slope or '%d,%d' % (x, y) in self.ground or any(in_rect(x, y, [r[0], r[1], r[2] + 1, r[3] + 1]) for r in clear):
                    continue
                if any(0 <= x + dx < W and 0 <= y + dy < H and (g[y + dy][x + dx] in 'pPbwKSr' or (x + dx, y + dy) in slope) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    continue
                if ((x * 19349663) ^ (y * 83492791)) % 1000 / 1000 < bush:
                    self.ground['%d,%d' % (x, y)] = 'u'
        self.cnt['forest'] = self.cnt.get('forest', 0) + n

    def untree(self, op):
        """置く所（目じるし・田舎の作例・家並み）の木をぬいて草地にする（林を植えたあとに働く）"""
        for x, y in region(op):
            if self.grid[y][x] == 't':
                self.grid[y][x] = '3' if self.h[y][x] >= 2 else '1'
            self.ground.pop('%d,%d' % (x, y), None) if self.ground.get('%d,%d' % (x, y)) == 'u' else None

    def thin(self, op):
        """第47回：あつ森では木は縦横にとなり合って植えられない（ななめは植えられる）。左か上に木がある木をぬき、市松にする"""
        n = 0
        for x, y in region(op):
            if self.grid[y][x] == 't' and ((x > 0 and self.grid[y][x - 1] == 't') or (y > 0 and self.grid[y - 1][x] == 't')):
                self.grid[y][x] = '3' if self.h[y][x] >= 2 else '1'; n += 1
        self.cnt['thin'] = self.cnt.get('thin', 0) + n

    def treecap(self, op):
        """第48回：あつ森の木の決まり。①崖・水・浜・橋・坂のとなりの木はぬく（植えられない）②地区ごとの本数まで（島ぜんぶで190本くらい。
        木の点が220をこえると5つ星にならない）。木の多い所（林のかたまり）を残し、ぬいた林の木は低木（u）にかえて林のかさを保つ"""
        import sys as _s; _s.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from zones import zone_cells
        g, h = self.grid, self.h
        slope = {c for o in self.inclines for c, _ in self.slope_cells(o[0], o[1], o[2], 9)}
        bad = lambda x, y, x2, y2: not (0 <= x2 < W and 0 <= y2 < H) or g[y2][x2] in 'wbsSrKP' or (x2, y2) in slope or (g[y2][x2] != 'P' and h[y2][x2] != h[y][x])
        Z = zone_cells([''.join(str(v) for v in r) for r in h])
        trees = [(x, y) for y in range(H) for x in range(W) if g[y][x] == 't']
        cut = 0
        for x, y in trees:
            if any(bad(x, y, x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                g[y][x] = '3' if h[y][x] >= 2 else '1'; cut += 1
        trees = [(x, y) for x, y in trees if g[y][x] == 't']
        tset = set(trees)
        dens = {(x, y): sum((x + dx, y + dy) in tset for dx in range(-2, 3) for dy in range(-2, 3)) for x, y in trees}
        quota = op['quota']; keep = {}
        for x, y in sorted(trees, key=lambda q: (-dens[q], ((q[0] * 73856093) ^ (q[1] * 19349663)) % 1000)):
            z = Z[y][x]
            if keep.get(z, 0) < quota.get(z, 0):
                keep[z] = keep.get(z, 0) + 1; continue
            g[y][x] = '3' if h[y][x] >= 2 else '1'
            if z in op.get('bush_zones', '') and ((x * 19349663) ^ (y * 83492791)) % 1000 / 1000 < op.get('bush', .7):
                self.ground['%d,%d' % (x, y)] = 'u'
        self.cnt['treecap'] = (cut, sum(keep.values()))

    # -- 全体 -------------------------------------------------------------------
    def run(self, design):
        ops = design['ops']
        land = ('level', 'flatten', 'river', 'stream', 'fillwater', 'unroad', 'set', 'dry')
        for op in ops:
            if op['op'] in land:
                getattr(self, op['op'])(op)
        self.fix()
        for op in ops:
            if op['op'] in ('incline', 'road', 'bridge', 'forest', 'untree', 'thin', 'treecap'):
                getattr(self, op['op'])(op)
        self.ground = {k: v for k, v in self.ground.items() if self.grid[int(k.split(',')[1])][int(k.split(',')[0])] in '13t'}
        # 坂は上の1マスの段を変えず、下の3マスはもともと1段低い所。橋の下の段をそろえる
        existing_bridges = sum(1 for y in range(H) for x in range(W) if self.grid[y][x] == 'b')
        return existing_bridges


def components(mask):
    seen, n = set(), 0
    for y in range(H):
        for x in range(W):
            if mask(x, y) and (x, y) not in seen:
                n += 1; st = [(x, y)]; seen.add((x, y))
                while st:
                    cx, cy = st.pop()
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in seen and mask(nx, ny):
                            seen.add((nx, ny)); st.append((nx, ny))
    return n


def irregularity(grid, rect):
    """道の不規則さ：外周の角の数 ÷ 道のマス数×100"""
    x0, y0, x1, y1 = rect
    road = lambda x, y: x0 <= x < x1 and y0 <= y < y1 and grid[y][x] == 'p'
    n = sum(1 for y in range(y0, y1) for x in range(x0, x1) if road(x, y))
    if not n:
        return 0.0
    corners = 0
    for y in range(y0 - 1, y1):
        for x in range(x0 - 1, x1):
            q = [road(x, y), road(x + 1, y), road(x, y + 1), road(x + 1, y + 1)]
            s = sum(q)
            if s in (1, 3):
                corners += 1
            elif s == 2 and q[0] == q[3]:
                corners += 2
    return round(corners / n * 100, 1)


def main():
    quiet = '--quiet' in sys.argv
    arg = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
    src, dst = arg('--design', 'plan-design.json'), arg('--out', 'plan-terrain.json')   # 第45回：案2 は plan2-design.json → plan2-terrain.json
    design = json.load(open(os.path.join(ROOT, src), encoding='utf-8'))
    t = Terrain()
    existing = t.run(design)
    grid = [''.join(r) for r in t.grid]
    hh = [''.join(str(v) for v in r) for r in t.h]
    water = lambda x, y: t.grid[y][x] == 'w'
    wcount = sum(1 for y in range(H) for x in range(W) if water(x, y))
    wat = lambda x, y: 0 <= x < W and 0 <= y < H and t.grid[y][x] in 'wb'
    thin = sum(1 for y in range(H) for x in range(W) if water(x, y) and ((not wat(x - 1, y) and not wat(x + 1, y)) or (not wat(x, y - 1) and not wat(x, y + 1))))
    falls = sum(1 for y in range(H) for x in range(W) if water(x, y) and any(0 <= x + dx < W and 0 <= y + dy < H and water(x + dx, y + dy) and t.h[y + dy][x + dx] < t.h[y][x] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))))
    nb = len(t.bridges) + existing_old_bridges(design, t)
    fe = [(x, y) for y in range(H) for x in range(W) if water(x, y) and any(0 <= x + dx < W and 0 <= y + dy < H and water(x + dx, y + dy) and t.h[y + dy][x + dx] < t.h[y][x] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    nfalls, seenf = 0, set()
    for c in fe:
        if c in seenf:
            continue
        nfalls += 1; st = [c]; seenf.add(c)
        while st:
            a = st.pop()
            for b in fe:
                if b not in seenf and abs(a[0] - b[0]) <= 1 and abs(a[1] - b[1]) <= 1:
                    seenf.add(b); st.append(b)
    facs = []
    for f in design.get('facilities', []):
        f = dict(f)
        if f['kind'] == 'fishing':
            # 釣り場：陸のマスで、となり（2マス以内）に同じ段の水がある
            lv = f.get('level', 1)
            okw = any(0 <= f['x'] + dx < W and 0 <= f['y'] + dy < H and water(f['x'] + dx, f['y'] + dy) and t.h[f['y'] + dy][f['x'] + dx] == lv for dx in range(-2, 3) for dy in range(-2, 3))
            if t.grid[f['y']][f['x']] in 'wSr' or (not okw and t.grid[f['y']][f['x']] != 's'):
                t.warn.append('釣り場のそばに%d段目の水がない：%s (%d,%d)' % (lv, f['name'], f['x'], f['y']))
        f['h'] = t.h[f['y']][f['x']]
        facs.append(f)
    lv = [sum(1 for y in range(H) for x in range(W) if t.h[y][x] == k and t.grid[y][x] not in 'Sr') for k in (1, 2, 3)]
    stats = {'water': wcount, 'water_bodies': components(water), 'water_width1': thin, 'inclines': len(t.inclines), 'bridges': nb,
             'fall_edges': falls, 'waterfalls': nfalls, 'dry_cells': len(t.ground), 'level_cells': {'1': lv[0], '2': lv[1], '3': lv[2]},
             'irregularity': {k: irregularity(t.grid, v) for k, v in design.get('measure', {}).items()}}
    out = {'note': design.get('note', ''), 'grid': grid, 'h': hh, 'inclines': t.inclines, 'ground': t.ground, 'facilities': facs, 'stats': stats}
    with open(os.path.join(ROOT, dst), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    if not quiet:
        ops = {}
        for o in design['ops']:
            ops[o['op']] = ops.get(o['op'], 0) + 1
        print('ops:', ' '.join('%s %d' % kv for kv in ops.items()))
        print('水 %d マス・%d のかたまり・幅1の水のマス %d・坂 %d/%d・橋 %d/%d・滝 %d か所（落ち口 %d マス）・枯れ流れ %d マス' % (wcount, stats['water_bodies'], thin, len(t.inclines), LIMIT, nb, LIMIT, nfalls, falls, len(t.ground)))
        print('段：1段目 %d・2段目 %d・3段目 %d' % tuple(lv))
        for k, v in stats['irregularity'].items():
            print('道の不規則さ', k, v)
        for w in t.warn:
            print('注意:', w)
    if len(t.inclines) > LIMIT or nb > LIMIT:
        sys.exit(1)


def existing_old_bridges(design, t):
    """今の島に残っている橋（b）のうち、新しく架けたもの以外のマス数から本数を数える（幅2×長さのかたまり）"""
    mine = {c for b in t.bridges for c in b}
    seen, n = set(), 0
    for y in range(H):
        for x in range(W):
            if t.grid[y][x] == 'b' and (x, y) not in mine and (x, y) not in seen:
                n += 1; st = [(x, y)]; seen.add((x, y))
                while st:
                    cx, cy = st.pop()
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in seen and (nx, ny) not in mine and t.grid[ny][nx] == 'b':
                            seen.add((nx, ny)); st.append((nx, ny))
    return n


if __name__ == '__main__':
    main()
