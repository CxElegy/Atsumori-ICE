#!/usr/bin/env python3
"""案3（第49回）：島の地形を一から作りなおす。設計の意図（どこを高く・川をどこに）に、たね（seed）つきの乱れ（ノイズ）を足して、
まっすぐな線のない、あつ森の決まりどおりの地形を作る。

  python3 tools/plan3_gen.py --seed 7 --out plan3-terrain.json [--png 地図.png]

動かせない物（今の島 island-grid.json から）：海・浜・浜の岩・飛行場（K）・案内所の広場（P）・河口2つ（西と南）。
あつ森の決まり（skill acnh-basics）：崖は3段・2マス幅から・上の段は下の段のふちから1マス内側・浜のとなりに崖は作れない・
滝は崖の上から・坂 2×4・橋は水3〜5マスを幅4で。
記号は plan_terrain.py と同じ（S 海・s 浜・r 岩・K 飛行場・P 広場・w 水・p 道・b 橋・t 木・1/3 草地）。h は段（0〜3）。
"""
import json, math, os, random, sys
from collections import deque

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 112, 96
ORIG = json.load(open(os.path.join(ROOT, 'island-grid.json')))
FIXED = 'SsrKP'
MOUTHS = {'west': [(11, 37), (12, 37), (13, 38), (13, 39), (13, 40)], 'south': [(70, 83), (71, 83), (72, 83), (73, 83)]}
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
N8 = N4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))
inside = lambda x, y: 0 <= x < W and 0 <= y < H


class Noise:
    """たねつきの値ノイズ（なめらかな乱れ）"""
    def __init__(self, seed, cell):
        self.r = random.Random(seed); self.cell = cell; self.v = {}
    def lat(self, i, j):
        if (i, j) not in self.v:
            self.v[(i, j)] = self.r.random() * 2 - 1
        return self.v[(i, j)]
    def __call__(self, x, y):
        fx, fy = x / self.cell, y / self.cell; i, j = math.floor(fx), math.floor(fy); u, v = fx - i, fy - j
        s = lambda t: t * t * (3 - 2 * t); u, v = s(u), s(v)
        a, b, c, d = self.lat(i, j), self.lat(i + 1, j), self.lat(i, j + 1), self.lat(i + 1, j + 1)
        return (a * (1 - u) + b * u) * (1 - v) + (c * (1 - u) + d * u) * v


class Island:
    def __init__(self, seed):
        self.seed = seed; self.rng = random.Random(seed)
        self.n1, self.n2, self.n3 = Noise(seed * 7 + 1, 9), Noise(seed * 7 + 2, 4.5), Noise(seed * 7 + 3, 2.6)
        self.g = [[ORIG[y][x] if ORIG[y][x] in FIXED else '1' for x in range(W)] for y in range(H)]
        self.h = [[0 if self.g[y][x] in 'Sr' else 1 for x in range(W)] for y in range(H)]
        for side in MOUTHS.values():
            for x, y in side:
                self.g[y][x] = 'w'
        self.land = lambda x, y: inside(x, y) and self.g[y][x] not in FIXED
        # 浜・海・広場・飛行場・河口からの距離（崖は浜にくっつけられない・広場と飛行場のまわりは平らに）
        self.dcoast = self.dist(lambda x, y: self.g[y][x] in 'Ssr')
        self.dfixed = self.dist(lambda x, y: self.g[y][x] in 'KP')
        self.notes = []

    def dist(self, src):
        d = [[999] * W for _ in range(H)]; q = deque()
        for y in range(H):
            for x in range(W):
                if src(x, y):
                    d[y][x] = 0; q.append((x, y))
        while q:
            x, y = q.popleft()
            for dx, dy in N8:
                a, b = x + dx, y + dy
                if inside(a, b) and d[b][a] > d[y][x] + 1:
                    d[b][a] = d[y][x] + 1; q.append((a, b))
        return d

    def wobble(self, x, y, amp):
        return amp * (self.n1(x, y) * .65 + self.n2(x, y) * .35)

    # ---- 1 段（設計の意図の形 × ノイズのふち）----
    def blob(self, cx, cy, rx, ry, amp=.22):
        out = set()
        for y in range(H):
            for x in range(W):
                d = math.hypot((x + .5 - cx) / rx, (y + .5 - cy) / ry)
                if d < 1 + self.wobble(x, y, amp):
                    out.add((x, y))
        return out

    def lobes(self, cx, cy, rx, ry, amp):
        """楕円を2〜3つの、ずれた小さな楕円のあつまりにする（形がまるくそろわないように）"""
        r = self.rng; out = self.blob(cx, cy, rx * .85, ry * .85, amp)
        for _ in range(r.randint(1, 3)):
            a = r.uniform(0, 6.28); k = r.uniform(.35, .65)
            out |= self.blob(cx + math.cos(a) * rx * .45, cy + math.sin(a) * ry * .45, rx * k, ry * k, amp)
        return out

    def raise_tiers(self, plan):
        L2, L3 = set(), set()
        for kind, cx, cy, rx, ry, *rest in plan:
            cells = self.lobes(cx, cy, rx, ry, rest[0] if rest else .3) if kind != -2 else self.blob(cx, cy, rx, ry, .2)
            if kind == 2: L2 |= cells
            elif kind == 3: L3 |= cells
            elif kind == -2: L2 -= cells   # くぼ地（2段目をぬく）
        for x, y in L2:
            if self.land(x, y) and self.dcoast[y][x] >= 3 and self.dfixed[y][x] >= 3:
                self.h[y][x] = 2
        for x, y in L3:
            if self.h[y][x] == 2:
                self.h[y][x] = 3
        self.fix_tiers()

    def fix_tiers(self):
        """あつ森の決まり：段は2マス幅から（2×2 がおさまらない所は下げる）。3段目は2段目のふちから1マス内側。浜のとなりは1段目"""
        for _ in range(6):
            changed = 0
            for L in (3, 2):
                for y in range(H):
                    for x in range(W):
                        if self.h[y][x] < L:
                            continue
                        ok2 = any(all(inside(x + i, y + j) and self.h[y + j][x + i] >= L for i in (a, a + 1) for j in (b, b + 1)) for a in (-1, 0) for b in (-1, 0))
                        if not ok2:
                            self.h[y][x] = L - 1; changed += 1; continue
                        if L == 3 and any(not inside(x + dx, y + dy) or self.h[y + dy][x + dx] < 2 for dx, dy in N8):
                            self.h[y][x] = 2; changed += 1
            # 1マスの穴・1マスの出っぱりもなくす（崖のふちをなめらかに）
            for y in range(1, H - 1):
                for x in range(1, W - 1):
                    if not self.land(x, y):
                        continue
                    hs = [self.h[y + dy][x + dx] for dx, dy in N4]
                    up = sum(v > self.h[y][x] for v in hs)
                    if up >= 3 and self.h[y][x] >= 1:
                        self.h[y][x] = max(v for v in hs); changed += 1
            if not changed:
                break

    # ---- 2 川（源から河口へ、ノイズでまがる）----
    def river(self, pts, wmin=2, wmax=4, name=''):
        """制御点をなめらかにつないだ線（Catmull-Rom）をノイズで横にゆらし、幅をかえながら掘る。段を下るところが滝"""
        path = []
        P = [pts[0]] + pts + [pts[-1]]
        for i in range(1, len(P) - 2):
            p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
            n = max(2, int(math.hypot(p2[0] - p1[0], p2[1] - p1[1]) * 2))
            for k in range(n):
                t = k / n; t2, t3 = t * t, t * t * t
                x = .5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
                y = .5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
                path.append((x, y))
        path.append(pts[-1])
        cells = []
        for i, (x, y) in enumerate(path):
            # 進む向きの直角にノイズでゆらす
            if 0 < i < len(path) - 1:
                dx, dy = path[i + 1][0] - path[i - 1][0], path[i + 1][1] - path[i - 1][1]; l = math.hypot(dx, dy) or 1
                off = self.n3(x * 1.3, y * 1.3) * 1.2
                x, y = x - dy / l * off, y + dx / l * off
            w = wmin + (wmax - wmin) * (self.n2(x * 2, y * 2) * .5 + .5)
            r = w / 2
            for yy in range(int(y - r - 1), int(y + r + 2)):
                for xx in range(int(x - r - 1), int(x + r + 2)):
                    if inside(xx, yy) and math.hypot(xx + .5 - x, yy + .5 - y) <= r and self.g[yy][xx] not in 'SsrKP':
                        cells.append((xx, yy))
        for x, y in cells:
            self.g[y][x] = 'w'
        self.notes.append(f'川 {name}：{len(set(cells))} マス')
        return path

    def pond(self, cx, cy, rx, ry, islet=False):
        cells = [(x, y) for x, y in self.blob(cx, cy, rx, ry, .25) if self.land(x, y)]
        for x, y in cells:
            self.g[y][x] = 'w'
        if islet:   # 池の中の小島（2×2 以上）
            ix, iy = int(cx + self.rng.uniform(-1, 1)), int(cy + self.rng.uniform(-1, 1))
            for x in range(ix, ix + 2):
                for y in range(iy, iy + 2):
                    if self.g[y][x] == 'w':
                        self.g[y][x] = '1'

    def settle_water(self):
        """水の段：水は流れの上から下へ。水のマスの段は、まわりの陸の段のいちばん低いものにそろえる（崖をまたぐ所が滝）。1マス幅の水の切れはしは埋める"""
        for _ in range(3):
            for y in range(H):
                for x in range(W):
                    if self.g[y][x] == 'w':
                        nb = [self.h[y + dy][x + dx] for dx, dy in N4 if inside(x + dx, y + dy) and self.g[y + dy][x + dx] not in 'wSs']
                        if nb:
                            self.h[y][x] = min(nb) if min(nb) >= 1 else 1
        # 水は浜につけない（河口だけ）
        mouth = {p for v in MOUTHS.values() for p in v}
        for y in range(H):
            for x in range(W):
                if self.g[y][x] == 'w' and (x, y) not in mouth and any(inside(x + dx, y + dy) and self.g[y + dy][x + dx] in 's' for dx, dy in N4):
                    self.g[y][x] = '1'

    def waterfalls(self):
        out = []
        for y in range(H):
            for x in range(W):
                if self.g[y][x] == 'w':
                    for dx, dy in N4:
                        a, b = x + dx, y + dy
                        if inside(a, b) and self.g[b][a] == 'w' and self.h[b][a] < self.h[y][x]:
                            out.append((x, y, a, b))
        return out

    def summary(self):
        from collections import Counter
        c = Counter(self.h[y][x] for y in range(H) for x in range(W) if self.g[y][x] not in 'Ssr')
        return {'tiers': dict(c), 'water': sum(r.count('w') for r in self.g), 'falls': len(self.waterfalls()), 'notes': self.notes}

    def dump(self):
        return {'grid': [''.join(r) for r in self.g], 'h': [''.join(str(v) for v in r) for r in self.h], 'seed': self.seed}


def render(isl, path, S=7):
    from PIL import Image, ImageDraw
    im = Image.new('RGB', (W * S, H * S)); d = ImageDraw.Draw(im)
    LV = {0: (236, 224, 180), 1: (160, 196, 112), 2: (118, 160, 86), 3: (80, 124, 64)}
    for y in range(H):
        for x in range(W):
            c = isl.g[y][x]
            col = {'S': (110, 190, 200), 'w': (80, 150, 205), 'r': (140, 140, 140), 's': (236, 224, 180), 'P': (240, 220, 200), 'K': (200, 200, 200), 'p': (205, 185, 150), 'b': (180, 140, 90), 't': None}.get(c) or LV.get(isl.h[y][x], (0, 0, 0))
            if c == 'w':
                col = (80 + 25 * isl.h[y][x], 150 + 10 * isl.h[y][x], 205)
            d.rectangle([x * S, y * S, x * S + S - 1, y * S + S - 1], fill=col)
            for dx, dy in ((1, 0), (0, 1)):
                a, b = x + dx, y + dy
                if inside(a, b) and isl.h[b][a] != isl.h[y][x] and isl.g[y][x] not in 'Sw' and isl.g[b][a] not in 'Sw':
                    d.line([a * S, y * S, a * S, y * S + S] if dx else [x * S, b * S, x * S + S, b * S], fill=(60, 40, 20), width=2)
    for x, y, a, b in isl.waterfalls():
        d.ellipse([x * S + 1, y * S + 1, x * S + S - 2, y * S + S - 2], fill=(255, 255, 255))
    im.save(path)


# 設計の意図（案3）：北ほど高い（町 → 村 → 森 → 霊峰）。北西に霊峰（3段目の頂）、北のまん中に森の台地、北東に尾根に囲まれたくぼ地、
# 東に丘と港の崖、南のまん中は町（ロンドン）の低地に2段目の高台。川は2本：霊峰の頂の泉 → 池 → 西の河口、森の台地の泉 → 町の運河 → 南の河口
PLAN = [
    (2, 27, 25, 15, 12), (3, 25, 21, 8, 6.5),          # 霊峰
    (2, 56, 22, 14, 8),                                 # 森の台地
    (2, 88, 26, 12, 11), (-2, 89, 26, 6.5, 5.5), (-2, 86, 35, 2.6, 3.5),   # 北東の尾根とくぼ地（南に切り通し）
    (2, 92, 49, 6.5, 5.5),                              # 東の丘
    (2, 93, 66, 5, 7.5),                                # 港の崖
    (2, 53, 58, 10, 4.5),                               # 町の高台
]
EXTRA = [(2, 40, 47, 4, 3), (2, 76, 40, 4.5, 3.5), (2, 20, 52, 4, 3.5), (2, 80, 72, 4, 3), (3, 56, 21, 4, 3)]   # 乱れ：小さな台地（このうちいくつかを、たねで選んで、ずらして足す）


def build(seed):
    isl = Island(seed)
    r = isl.rng
    extra = [(k, cx + r.uniform(-4, 4), cy + r.uniform(-3, 3), rx * r.uniform(.8, 1.3), ry * r.uniform(.8, 1.3)) for k, cx, cy, rx, ry in EXTRA if r.random() < .6]
    isl.notes.append('乱れの台地：%d' % len(extra))
    isl.raise_tiers(PLAN + extra)
    j = lambda v, a: v + r.uniform(-a, a)
    # 川A：霊峰の頂の泉 → 2段目の池（小島）→ 1段目へ滝 → 村の北をまがって西の河口
    isl.river([(j(27, 2), 19), (j(30, 2), 24), (j(33, 2), 30), (j(30, 3), 36), (j(22, 3), j(39, 1)), (15, 39), (12, 38)], 2, 3.4, 'A')
    isl.pond(j(31, 1.5), j(28, 1), 4.2, 3.2, islet=True)
    # 川B：森の台地の泉 → 森を南へ → 村と町のあいだを東へまがる → 町の東を運河で南へ → 南の河口
    isl.river([(j(58, 3), 18), (j(56, 3), 27), (j(60, 5), 35), (j(50, 5), 42), (j(58, 5), j(48, 2)), (j(66, 4), j(54, 2)), (j(60, 5), j(62, 2)), (j(70, 4), 68), (j(64, 4), 75), (72, 80), (72, 83)], 2, 4, 'B')
    isl.pond(j(62, 2), j(45, 1), 4.5, 3, islet=r.random() < .6)
    # 町の運河：川Bから西へ分かれ、案内所の広場の南東の船だまり（池）でおわる（ロンドンの河岸）
    if r.random() < .8:
        isl.river([(j(66, 2), j(70, 2)), (j(58, 2), j(74, 1)), (j(48, 2), j(75, 1)), (j(42, 1), j(76, 1))], 2, 3, 'C（町の運河）')
        isl.pond(j(41, 1), j(77, .5), 3, 2.2)
    # 支流：くぼ地の黒い池 → 尾根の切れ目 → 川B
    isl.pond(j(92, 1), j(28, 1), 3, 2.4)
    isl.settle_water()
    isl.fix_tiers()
    isl.settle_water()
    return isl


if __name__ == '__main__':
    arg = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
    seed = int(arg('--seed', 7))
    isl = build(seed)
    print(json.dumps(isl.summary(), ensure_ascii=False))
    if '--png' in sys.argv:
        render(isl, arg('--png', 'plan3.png'))
    if '--out' in sys.argv:
        json.dump(isl.dump(), open(os.path.join(ROOT, arg('--out', 'plan3-terrain.json')), 'w'))
