#!/usr/bin/env python3
"""案3（第49回）：plan3_layout.py の島に、地区・木と低木・見せ場（キット）・地面のマイデザイン・崖のパネルの壁・花を置く。

  python3 tools/plan3_fill.py       # plan3-terrain.json に zones と木・低木を書き、designs/build_plan3.json を作る

決まりは skill acnh-basics：木は190本くらいまで・崖や水や浜や建物や坂や橋のとなりには植えない・低木はどこでも（浜以外）・
家具は目録の名前・8×8 のかたまりで45マス未満・同じ家具は6個まで・花は草地だけ。乱れはたね（seed）で決まる。
"""
import json, math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plan3_gen as gen
from acnh_build import foot

ROOT = gen.ROOT
W, H = gen.W, gen.H
N4, N8 = gen.N4, gen.N8
inside = gen.inside
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding='utf-8'))
PLAN = os.environ.get('ICE_PLAN', '3')   # 第54回：ICE_PLAN=4 で案4
T = J(f'plan{PLAN}-terrain.json')
if 'zones' in T:
    sys.exit(f'plan{PLAN}-terrain.json はもう中身が入っている。先に python3 tools/plan3_layout.py を流す')
SPEC = J(f'designs/plan{PLAN}_spec.json')
LAY = J(f'designs/plan{PLAN}_layout_out.json')
CAT = J('designs/acnh_catalog.json')['items']
KITS = J('designs/kits.json')['kits']
P2 = J('designs/build_plan2.json')
G = [list(r) for r in T['grid']]
Hh = [[int(c) for c in r] for r in T['h']]
rng = random.Random(T['seed'] * 101 + 3)
noise = gen.Noise(T['seed'] * 13 + 7, 7)
SIZE = {'villager': (4, 4), 'player_house': (5, 4), 'museum': (7, 4), 'nook': (7, 4), 'able': (5, 4), 'campsite': (4, 4)}
lv = lambda x, y: Hh[y][x] if inside(x, y) else 0
g = lambda x, y: G[y][x] if inside(x, y) else 'S'

# ---- 地区（中心からの近さ＋ノイズ。さかいは崖・川・道で自然に切れる）----
CENT = {'C': [(30, 64), (22, 58), (36, 56), (46, 60), (44, 74), (22, 49), (38, 49)], 'S': [(80, 50), (76, 70), (66, 44)], 'F': [(52, 26), (44, 34)], 'J': [(27, 22)], 'B': [(15, 32), (34, 36)],
        'H': [(88, 26)], 'P': [(93, 66), (86, 80)]}
NAMES = {'C': 'ロンドン市内', 'S': '郊外と村', 'F': '森', 'B': '竹林', 'J': '日本（霊峰）', 'H': 'ハロウィン', 'P': '海辺の港町'}
Z = [['S'] * W for _ in range(H)]
for y in range(H):
    for x in range(W):
        best = None
        for k, cs in CENT.items():
            for cx, cy in cs:
                d = math.hypot(x - cx, y - cy) + noise(x, y) * 7
                if best is None or d < best[0]:
                    best = (d, k)
        Z[y][x] = best[1]
# 高い所は地区をよせる：霊峰の2・3段目は日本、北東の尾根はハロウィン
for y in range(H):
    for x in range(W):
        if lv(x, y) >= 2 and x < 42 and y < 36: Z[y][x] = 'J'
        if lv(x, y) >= 2 and x > 74 and y < 40: Z[y][x] = 'H'
if LAY.get('zones'):   # 案4：地区は手で塗ったもの（見せ場を置く芯は地区の重心）
    Z = [list(r) for r in LAY['zones']]
    for k in list(CENT):
        cs = [(x, y) for y in range(H) for x in range(W) if Z[y][x] == k]
        CENT[k] = [(sum(p[0] for p in cs) / len(cs), sum(p[1] for p in cs) / len(cs))] if cs else CENT[k]

# ---- 建物 ----
B_ALL = [{'id': 'rs', 'kind': 'resident_services', 'fixed': True, 'rect': [28, 62, 6, 4], 'name': '案内所', 'note': '広場（12×10）ごと動かせない'},
         {'id': 'airport', 'kind': 'airport', 'fixed': True, 'rect': [29, 84, 11, 6], 'name': '飛行場', 'note': '南の浜。動かせない'}]
occ_b, front = set(), set()
for b in LAY['buildings']:
    nb = {k: v for k, v in b.items() if k != 'door'}
    w, d = SIZE[b['kind']]; x0, y0 = b['at']
    nb['zone'] = Z[y0][x0]
    B_ALL.append(nb)
    for y in range(y0 - 1, y0 + d + 1):
        for x in range(x0 - 1, x0 + w + 1):
            occ_b.add((x, y))
    cols = range(x0, x0 + w) if w % 2 == 0 else range(x0 + w // 2 - 1, x0 + w // 2 + 2)
    for k in range(2):
        for x in cols:
            front.add((x, y0 + d + k))
slope = set()
for x, y, d in T['inclines']:
    slope.update([(x + i, y + j) for i in range(2) for j in range(4)] if d in 'NS' else [(x + i, y + j) for i in range(4) for j in range(2)])
road = {(x, y) for y in range(H) for x in range(W) if g(x, y) in 'pb'}

# ---- 見せ場（キット）を地区ごとに置く：道のとなり・平ら・あいている所 ----
occ = set()   # 家具・花・地面の予約
kitring = set()   # 見せ場のまわり1マス（城壁や岸の小物は置いてよい）
def free(x, y, L):
    return inside(x, y) and g(x, y) in '13' and lv(x, y) == L and (x, y) not in occ_b and (x, y) not in slope and (x, y) not in front and (x, y) not in road and (x, y) not in occ
def fits(kid, ax, ay, flip=False):
    k = KITS[kid]; KW, KD = k['size']; L = lv(ax, ay)
    for y in range(ay, ay + KD):
        for x in range(ax, ax + KW):
            if not free(x, y, L):
                return False
    ring = [(x, y) for x in range(ax - 1, ax + KW + 1) for y in range(ay - 1, ay + KD + 1) if not (ax <= x < ax + KW and ay <= y < ay + KD)]
    return any(p in road and lv(*p) == L for p in ring)   # 同じ段の道に面する（崖の下の道では入れない）
PLAN_KITS = {'C': ['lon_square', 'lon_cafe', 'lon_market', 'lon_books', 'lon_pub', 'lon_records', 'lon_crossing', 'lon_benches', 'lon_quay', 'lon_garden', 'lon_station', 'lon_dock', 'lon_cafe', 'lon_market'],
             'S': ['cot_garden', 'cot_greenhouse', 'bakery', 'allotment', 'formal_garden', 'cot_garden', 'tea_picnic', 'allotment', 'cot_greenhouse', 'bakery', 'cot_garden', 'tea_picnic'],
             'F': ['tea_picnic', 'tea_picnic', 'tea_picnic'], 'J': ['jp_tea'], 'B': ['tea_picnic'], 'H': ['spooky_yard'], 'P': ['harbor_quay', 'lon_dock', 'bakery']}
groups, ground, plants = [], [], []
def ring_skip(ax, ay, KW, KD):   # 囲みの1マスのうち、ちがう段・水・道などには地面を貼らない
    L = lv(ax, ay)
    return [[x, y] for y in range(ay - 1, ay + KD + 1) for x in range(ax - 1, ax + KW + 1)
            if not (inside(x, y) and g(x, y) in '13' and lv(x, y) == L)]
def place_kit(kid, tx, ty, r, z, style=None, flip=None, gid=None, name=None):
    k = KITS[kid]; KW, KD = k['size']; best = None
    for y in range(ty - r, ty + r + 1):
        for x in range(tx - r, tx + r + 1):
            if fits(kid, x, y):
                d = math.hypot(x - tx, y - ty)
                if best is None or d < best[0]:
                    best = (d, x, y)
    if not best:
        print('キットを置けない', kid, tx, ty); return False
    _, ax, ay = best
    gid = gid or f'{z}-{kid}-{ax}-{ay}'
    g_ = {'id': gid, 'zone': z, 'kit': kid, 'at': [ax, ay], 'flip': rng.random() < .5 if flip is None else flip, 'items': [], 'lines': []}
    if name: g_['name'] = name
    groups.append(g_)
    for y in range(ay - 1, ay + KD + 1):
        for x in range(ax - 1, ax + KW + 1):
            occ.add((x, y))
            if not (ax <= x < ax + KW and ay <= y < ay + KD):
                kitring.add((x, y))
    st = style or GSTYLE[z][len(groups) % len(GSTYLE[z])]
    ground.append({'id': gid, 'style': st, 'rect': [ax - 1, ay - 1, ax + KW, ay + KD], 'design': GDES[st], 'skip': ring_skip(ax, ay, KW, KD)})
    return True
GSTYLE = {'C': ['herring', 'brick', 'flag', 'cobble'], 'S': ['garden', 'flag'], 'P': ['plank', 'flag'], 'J': ['moss'], 'B': ['moss'], 'H': ['leaves'], 'F': ['leaves']}
GDES = {'herring': 'brick_arch', 'brick': 'brick_vintage_red', 'flag': 'brick_greige', 'cobble': 'road_chic_stone', 'garden': 'brick_city_old', 'plank': 'plank', 'moss': 'stone_natural', 'leaves': 'brick_autumn'}
for kd in SPEC.get('kits', []):   # 設計の見せ場（ねらいの場所のまわりに）。木より先に場所をとる
    tx, ty = kd.get('at') or kd['near']
    place_kit(kd['kit'], tx, ty, 0 if 'at' in kd else kd.get('r', 6), kd['zone'], kd.get('style'), kd.get('flip'), name=kd.get('name'))

# 地区の見せ場も木より先に（道に面した平地を林にとられないように）
n = 0
for z, kl in PLAN_KITS.items():
    if z in SPEC.get('manual_zones', ''):
        continue
    anchors = [(x, y) for y in range(H) for x in range(W) if Z[y][x] == z]
    rng.shuffle(anchors)
    # 地区の中心に近い順に試す（見せ場を地区の芯に）
    cs = CENT[z]
    anchors.sort(key=lambda p: min(math.hypot(p[0] - cx, p[1] - cy) for cx, cy in cs) + rng.random() * 6)
    for kid in kl:
        k = KITS[kid]; KW, KD = k['size']
        spur = None
        for ax, ay in anchors:
            flip = rng.random() < .5
            ok = fits(kid, ax, ay, flip)
            if not ok and z in 'FJBHP':   # 野山の地区：道から11マスまでなら、小道（土の道）を1本引いてつなぐ
                L = lv(ax, ay)
                if all(free(x, y, L) for y in range(ay, ay + KD) for x in range(ax, ax + KW)):
                    for rx, ry, dx, dy in [(x, ay - 1, 0, -1) for x in range(ax, ax + KW)] + [(x, ay + KD, 0, 1) for x in range(ax, ax + KW)] + [(ax - 1, y, -1, 0) for y in range(ay, ay + KD)] + [(ax + KW, y, 1, 0) for y in range(ay, ay + KD)]:
                        cells = []
                        for i in range(12):
                            c = (rx + dx * i, ry + dy * i)
                            if c in road and lv(*c) == L:
                                spur = cells; break
                            if not free(c[0], c[1], L):
                                break
                            cells.append(c)
                        if spur:
                            break
                    ok = bool(spur)
            if ok:
                for c in (spur or []):
                    G[c[1]][c[0]] = 'p'; road.add(c)
                n += 1; gid = f'{z}-{n:02d}'
                groups.append({'id': gid, 'zone': z, 'kit': kid, 'at': [ax, ay], 'flip': flip, 'items': [], 'lines': []})
                for y in range(ay - 1, ay + KD + 1):
                    for x in range(ax - 1, ax + KW + 1):
                        occ.add((x, y))
                        if not (ax <= x < ax + KW and ay <= y < ay + KD):
                            kitring.add((x, y))
                st = GSTYLE[z][n % len(GSTYLE[z])]
                ground.append({'id': gid, 'style': st, 'rect': [ax - 1, ay - 1, ax + KW, ay + KD], 'design': GDES[st], 'skip': ring_skip(ax, ay, KW, KD)})
                break
        else:
            print('地区のキットを置けない', z, kid, len(anchors))

# ---- 木（190本まで。林のかたまり＝植えかえた大人の木はとなり合ってよい）と低木 ----
def tree_ok(x, y):
    if g(x, y) not in '13' or (x, y) in occ_b or (x, y) in slope or (x, y) in front or (x, y) in occ:
        return False
    for dx, dy in N4:
        a, b = x + dx, y + dy
        if not inside(a, b) or g(a, b) in 'wbsSrKPp' or (a, b) in slope or lv(a, b) != lv(x, y) or (a, b) in occ_b:
            return False
    return True
GROVES = {'F': (7, 9), 'J': (4, 7), 'H': (5, 6), 'B': (4, 6), 'S': (3, 5), 'C': (9, 2), 'P': (3, 3)}   # 林の数・1つの林の木の数
trees = set()
for z, (ng, nt) in GROVES.items():
    cells = [(x, y) for y in range(H) for x in range(W) if Z[y][x] == z and tree_ok(x, y)]
    rng.shuffle(cells)
    for c in cells[:ng]:
        grove = [c]; q = [c]
        while q and len(grove) < nt + rng.randint(-2, 2):
            x, y = q.pop(0)
            for dx, dy in rng.sample(N8, 8):
                p = (x + dx, y + dy)
                if p not in grove and p not in trees and tree_ok(*p) and Z[p[1]][p[0]] == z and rng.random() < .55:
                    grove.append(p); q.append(p)
        trees |= set(grove)
trees = set(sorted(trees, key=lambda p: (p[0] * 7 + p[1] * 13) % 97)[:185])
bush = set()
BUSH = {'F': .55, 'J': .35, 'H': .5, 'B': .3, 'S': .14, 'C': .02, 'P': .12}
if SPEC.get('base') == 'authored':
    BUSH['P'] = .02   # 案4：港も町（低木はほとんどなし）
for y in range(H):
    for x in range(W):
        z = Z[y][x]
        if g(x, y) in '13' and (x, y) not in trees and (x, y) not in occ_b and (x, y) not in slope and (x, y) not in front and (x, y) not in road and (x, y) not in occ:
            near = sum((x + dx, y + dy) in trees for dx in range(-2, 3) for dy in range(-2, 3))
            p = BUSH.get(z, 0) + .12 * near
            if lv(x, y) >= 1 and rng.random() < p * (.6 + .4 * (noise(x * 2, y * 2) + 1)):
                bush.add((x, y))
for x, y in trees:
    G[y][x] = 't'


# ---- 町の崖のすそのパネルの壁（ロンドン・港）と、崖の上のふちの柵・運河の岸の柵 ----
# パネルは崖のある向き rot（0北 1東 2南 3西）に背を当て、マイデザイン（窓・あかり・ドア・アーチ）を表に向ける。
# 設計のアーチ（spec の panels）は、道のつきあたりの崖に貼る「トンネルの入口」：下の道が上の町の下をくぐるように見せる
DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
PIECES = ['window', 'window', 'lamp', 'window', 'door', 'window', 'lamp']
panel_groups = []
cnt8 = {}
def panel(x, y, rot, piece):
    des = 'wall_brick_lamp' if piece in ('lamp', 'door', 'arch') else 'wall_windows_bricks'
    panel_groups.append(['simple panel', x, y, rot, 'Brown', des, piece]); occ.add((x, y))
    cnt8[(x // 8, y // 8)] = cnt8.get((x // 8, y // 8), 0) + 1
for x, y, rot, piece in SPEC.get('panels', {}).get('items', []):
    if g(x, y) in '13' and (x, y) not in occ and (x, y) not in road and (x, y) not in slope and (x, y) not in front and (x, y) not in occ_b:
        panel(x, y, rot, piece)
    elif (x, y) in road and g(x, y) in '13' and (x, y) not in slope:   # 道のつきあたり：道の最後の1マスにアーチ
        panel(x, y, rot, piece)
CAP = {'C': 14, 'P': 6 if SPEC.get('base') != 'authored' else 12}
URBAN = 'CP' if SPEC.get('base') == 'authored' else 'C'   # 案4：港（ドックランズ）も町
k = 0
for y in range(1, H - 1):
    for x in range(1, W - 1):
        z = Z[y][x]
        if z not in CAP or g(x, y) not in '13p' or (x, y) in occ_b or (x, y) in slope or (x, y) in front or (x, y) in occ or (x, y) in trees:
            continue
        for rot, (dx, dy) in enumerate(DIRS):
            a, b_ = x + dx, y + dy
            if (x, y) in road and not ((x - dx, y - dy) in road and (x - 2 * dx, y - 2 * dy) not in slope and any((x - dx + sx, y - dy + sy) in road for sx, sy in ((dy, dx), (-dy, -dx)))):
                continue   # 道の上には、崖と反対がわにも道が続く（2マス幅の）所だけ貼る
            if lv(a, b_) == lv(x, y) + 1 and g(a, b_) != 'w' and (a, b_) not in slope and cnt8.get((x // 8, y // 8), 0) < CAP[z]:
                panel(x, y, rot, PIECES[k % len(PIECES)]); k += 1
                break
if panel_groups:
    groups.append({'id': 'C-walls', 'zone': 'C', 'name': '崖のすそのレンガの壁（シンプルなパネル＋マイデザイン）', 'at': [0, 0], 'items': panel_groups, 'lines': [],
                   'note': '町の崖のすそにレンガ・窓・あかり・ドアのマイデザインのパネルを崖に背を当てて並べ、崖を建物の壁・擁壁に見せる。道のつきあたりの崖にはアーチ（上の町の下をくぐるトンネルに見せる）'})
# ---- 町の運河の岸（spec の water の wall・quay・bank）：片がわは城壁（castle wall・レンガのマイデザイン）、
#      もう片がわは岸壁（街灯・花の荷車・自転車・石と鉄の柵・ヨット）。副水路の岸は草と花（R-0088・R-1148 にならう）----
SIDE = {'N': (0, -1), 'S': (0, 1), 'W': (-1, 0), 'E': (1, 0)}
bld = {(x, y) for b in LAY['buildings'] for x0, y0 in [b['at']] for x in range(x0, x0 + SIZE[b['kind']][0]) for y in range(y0, y0 + SIZE[b['kind']][1])}
def near_bridge(x, y):
    return any(g(x + dx, y + dy) == 'b' for dx in range(-1, 2) for dy in range(-1, 2))
def bank_ok(x, y):
    return inside(x, y) and g(x, y) in '13p' and (x, y) not in slope and (x, y) not in bld and (x, y) not in front and ((x, y) not in occ or (x, y) in kitring) and (x, y) not in trees and not near_bridge(x, y) \
        and not any((x + dx, y + dy) in slope for dx, dy in N4)
canal_items = []
for op in SPEC.get('water', []):
    if 'canal' in op:
        w = op.get('w', 3); wc = set()
        for (xa, ya), (xb, yb) in zip(op['canal'], op['canal'][1:]):
            wc |= {(x, y) for x in range(min(xa, xb), max(xa, xb) + w) for y in range(min(ya, yb), max(ya, yb) + w)}
    elif 'pool' in op:
        x0, y0, x1, y1 = op['pool']; wc = {(x, y) for y in range(y0, y1) for x in range(x0, x1)}
    else:
        continue
    wc = {c for c in wc if g(*c) == 'w'}
    def banks(side):
        dx, dy = SIDE[side]
        out = sorted({(x + dx, y + dy) for x, y in wc if (x + dx, y + dy) not in wc and inside(x + dx, y + dy) and g(x + dx, y + dy) != 'w'})
        return out
    if op.get('bank') == 'flowers':
        for side in SIDE:
            for x, y in banks(side):
                if bank_ok(x, y) and (x, y) not in road:
                    plants.append({'id': 'C-bank-flowers', 'type': 'cosmos' if (x + y) % 3 else 'tulips', 'rect': [x, y, x, y], 'colors': ['white', 'pink', 'red'], 'fit': True}); occ.add((x, y))
    if op.get('wall'):
        horiz = op['wall'] in 'NS'
        cells = banks(op['wall']); used = set()
        for x, y in cells:
            x2, y2 = (x + 1, y) if horiz else (x, y + 1)
            if (x, y) in used or (x2, y2) not in cells or not bank_ok(x, y) or not bank_ok(x2, y2) or lv(x, y) != lv(x2, y2):
                continue
            canal_items.append(['castle wall', x, y, 0 if horiz else 1, 'Brown', 'wall_windows_bricks']); used |= {(x, y), (x2, y2)}; occ |= {(x, y), (x2, y2)}; kitring -= {(x, y), (x2, y2)}
    if op.get('quay'):
        cells = [c for c in banks(op['quay']) if bank_ok(*c)]
        dx, dy = SIDE[op['quay']]; horiz = op['quay'] in 'NS'
        boat = False
        for i, (x, y) in enumerate(cells):
            if not bank_ok(x, y):
                continue
            if not boat and i > 3:   # 岸壁に1そうのヨット（3×2）
                fp = [(x + (k if horiz else j * dx), y + (j * dy if horiz else k)) for k in range(3) for j in range(2)]
                if all(bank_ok(*c) and lv(*c) == lv(x, y) for c in fp):
                    ax, ay = min(c[0] for c in fp), min(c[1] for c in fp)
                    canal_items.append(['yacht', ax, ay, 0 if horiz else 1, 'White']); occ |= set(fp); boat = True; continue
            k = i % 6
            if k == 0:
                canal_items.append(['streetlamp', x, y, 0, 'Black']); occ.add((x, y))
            elif k in (2, 3):
                canal_items.append(['iron-and-stone fence', x, y, 0, None]); occ.add((x, y))
            elif k == 4 and i % 12 == 4:
                nx, ny = (x + 1, y) if horiz else (x, y + 1)
                if (nx, ny) in cells and bank_ok(nx, ny):
                    canal_items.append(['garden wagon' if i % 24 == 4 else 'cruiser bike', x, y, 0 if horiz else 1, 'Dark brown' if i % 24 == 4 else 'Green']); occ |= {(x, y), (nx, ny)}
if canal_items:
    groups.append({'id': 'C-canals', 'zone': 'C', 'name': '運河の岸：城壁と岸壁（街灯・柵・花の荷車・自転車・ヨット）', 'at': [0, 0], 'items': canal_items, 'lines': [],
                   'note': '主水路の片がわは城壁（castle wall にレンガのマイデザイン）、もう片がわは岸壁。副水路の岸は草と花'})

# 案4：町の2段目・3段目のかたまりのうち、道のない（歩いて上がらない）かたまりは「建物」：ふちは城壁（銃眼のあるレンガの壁）、中は屋上の庭
roofs, roofp = [], []
if SPEC.get('base') == 'authored':
    seen = set()
    for y0 in range(H):
        for x0 in range(W):
            if (x0, y0) in seen or Z[y0][x0] not in URBAN or lv(x0, y0) < 2 or g(x0, y0) not in '13':
                continue
            comp, q = [], [(x0, y0)]; seen.add((x0, y0))
            while q:
                x, y = q.pop(); comp.append((x, y))
                for dx, dy in N4:
                    p_ = (x + dx, y + dy)
                    if inside(*p_) and p_ not in seen and lv(*p_) == lv(x0, y0) and g(*p_) in '13p':
                        seen.add(p_); q.append(p_)
            if any(c in road for c in comp):
                continue   # 歩いて上がるかたまり（テラス）は鉄の柵のまま
            cs = set(comp)
            for x, y in sorted(comp):
                if (x, y) in occ or (x, y) in trees:
                    continue
                low = [(dx, dy) for dx, dy in DIRS if lv(x + dx, y + dy) < lv(x, y)]
                if low:
                    dx, dy = low[0]; x2, y2 = (x + 1, y) if dy else (x, y + 1)
                    if (x2, y2) in cs and (x2, y2) not in occ and (x2, y2) not in trees and any(lv(x2 + a, y2 + b) < lv(x2, y2) for a, b in DIRS):
                        roofs.append(['castle wall', x, y, 0 if dy else 1, 'Brown', 'wall_windows_bricks']); occ |= {(x, y), (x2, y2)}
                    else:
                        roofs.append(['brick fence', x, y, 0, None]); occ.add((x, y))
                elif noise(x * .5 + 3, y * .5) > -.1:   # 屋根：灰色のレンガのマイデザイン（はしごで上がって敷く）
                    ground.append({'id': 'C-roof', 'style': 'roof', 'rect': [x, y, x, y], 'design': 'brick_grey', 'skip': []}); occ.add((x, y))
                else:   # 屋上の庭
                    roofp.append({'id': 'C-roofgarden', 'type': 'roses' if (x * 3 + y) % 4 else 'lilies', 'rect': [x, y, x, y], 'colors': ['red', 'white', 'pink'], 'fit': True}); occ.add((x, y))
    if roofs:
        groups.append({'id': 'C-roofs', 'zone': 'C', 'name': 'レンガのかたまりの上：ふちの城壁（castle wall）と屋上の庭', 'at': [0, 0], 'items': roofs, 'lines': []})
    plants.extend(roofp)
edge = []
for y in range(1, H - 1):
    for x in range(1, W - 1):
        if Z[y][x] not in URBAN or g(x, y) not in '13' or (x, y) in occ or (x, y) in occ_b or (x, y) in road or (x, y) in slope or (x, y) in front or (x, y) in trees:
            continue
        near_slope = any((x + dx, y + dy) in slope for dx in (-1, 0, 1) for dy in (-1, 0, 1))
        if lv(x, y) == 2 and not near_slope and any(lv(x + dx, y + dy) < lv(x, y) and g(x + dx, y + dy) not in 'w' for dx, dy in DIRS):
            edge.append(['iron fence', x, y, 0, None]); occ.add((x, y))   # 上の町の崖のふち：鉄の柵（高架の手すりに見せる）
        elif lv(x, y) == 1 and not near_slope and sum(g(x + dx, y + dy) == 'w' and lv(x + dx, y + dy) == 1 for dx, dy in DIRS) == 1 and sum(g(x + dx, y + dy) == 'w' for dx in (-1, 0, 1) for dy in (-1, 0, 1)) <= 3 and (x + y) % 5 != 0:
            edge.append(['iron-and-stone fence', x, y, 0, None]); occ.add((x, y))   # 運河の岸：石と鉄の柵（5マスに1つあけて岸に下りられる）
ec = {(e[1], e[2]): e[0] for e in edge}
lone = [e for e in edge if not any(ec.get((e[1] + dx, e[2] + dy)) == e[0] for dx, dy in DIRS)]   # 1本だけの柵はやめる
for e in lone:
    edge.remove(e); occ.discard((e[1], e[2]))
if edge:
    groups.append({'id': 'C-edges', 'zone': 'C', 'name': '上の町の崖のふちの鉄の柵・運河の岸の石と鉄の柵', 'at': [0, 0], 'items': edge, 'lines': []})

# ---- 家のまわりの柵・生け垣（入口の前と道はあける。地区ごとの柵）----
FENCE = {'S': 'hedge', 'J': 'bamboo lattice fence', 'H': 'spooky fence', 'P': 'lattice fence', 'F': 'log fence', 'B': 'green bamboo fence', 'C': 'iron fence'}
fences = []
for b in LAY['buildings']:
    x0, y0 = b['at']; w, d = SIZE[b['kind']]; z = Z[y0][x0]
    if z == 'C':
        continue
    ring = [(x0 - 1, y) for y in range(y0 - 1, y0 + d + 1)] + [(x0 + w, y) for y in range(y0 - 1, y0 + d + 1)] + [(x, y0 - 1) for x in range(x0, x0 + w)]
    for x, y in ring:
        if inside(x, y) and g(x, y) in '13' and (x, y) not in road and (x, y) not in slope and (x, y) not in front and (x, y) not in occ and (x, y) not in trees and lv(x, y) == lv(x0, y0):
            fences.append([FENCE[z], x, y, 0, 'White' if FENCE[z] == 'lattice fence' else None]); occ.add((x, y))
if fences:
    groups.append({'id': 'S-fences', 'zone': 'S', 'name': '家のまわりの柵と生け垣（地区ごとの柵）', 'at': [0, 0], 'items': fences, 'lines': []})

# ---- ロンドンの通りの小物（街灯・電話ボックス・花の荷車・自転車・植木ばち…）：道に面したあいたマスに、間をあけて ----
STREET1 = [('streetlamp', 'Black'), ('round topiary', 'Green'), ('monstera', 'Black'), ('pot', 'Brown'), ('garbage bin', 'Black'), ('streetlamp', 'Black'), ('barrel', None),
           ('round topiary', 'Green'), ('standing shop sign', 'Black'), ('wooden box', 'Brown'), ('round streetlight', 'Black'), ('pot', 'White'), ('phone box', 'Red'), ('monstera', 'Black'),
           ('streetlamp', 'Black'), ('tin bucket', None), ('round topiary', 'Green'), ('plain wooden shop sign', 'Dark wood'), ('fire hydrant', 'Red'), ('barrel', None), ('pot', 'Brown'), ('park clock', 'Black')]
STREET2 = [('garden wagon', 'Dark brown'), ('cruiser bike', 'Green'), ('flower bed', 'Dark brown'), ('iron garden bench', 'Black'), ('cruiser bike', 'Red'), ('medium cardboard boxes', None)]
props, street = set(), []
def cand(x, y):
    return Z[y][x] in URBAN and g(x, y) in '13' and (x, y) not in occ and (x, y) not in occ_b and (x, y) not in road and (x, y) not in slope and (x, y) not in front and (x, y) not in trees
cells = [(x, y) for y in range(1, H - 1) for x in range(1, W - 1) if cand(x, y) and any((x + dx, y + dy) in road for dx, dy in N4)]
cells.sort(key=lambda p: (hash((p[0] * 31 + p[1] * 17) % 9973) % 1000))
k1 = k2 = 0
for x, y in cells:
    if not cand(x, y) or any((x + dx, y + dy) in props for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
        continue
    if cand(x + 1, y) and (x + 1, y) not in props and (x + y) % 3 == 0 and lv(x + 1, y) == lv(x, y) and any((x + 1 + dx, y + dy) in props for dx in (-1, 0, 1) for dy in (-1, 0, 1)) is False:
        it, var = STREET2[k2 % len(STREET2)]; k2 += 1
        street.append([it, x, y, 0, var]); props |= {(x, y), (x + 1, y)}; occ |= {(x, y), (x + 1, y)}
    else:
        it, var = STREET1[k1 % len(STREET1)]; k1 += 1
        street.append([it, x, y, 0, var]); props.add((x, y)); occ.add((x, y))
if street:
    groups.append({'id': 'C-street', 'zone': 'C', 'name': 'ロンドンの通りの小物（街灯・電話ボックス・花の荷車・自転車・植木ばち）', 'at': [0, 0], 'items': street, 'lines': []})

# ---- 3段目のかたまりの屋上の庭（バラ）----
for y in range(H):
    for x in range(W):
        if Z[y][x] == 'C' and lv(x, y) == 3 and g(x, y) in '13' and (x, y) not in occ and (x, y) not in trees:
            plants.append({'id': 'C-roof', 'type': 'roses', 'rect': [x, y, x, y], 'colors': ['red', 'white', 'pink'], 'fit': True}); occ.add((x, y))

# ---- ロンドンの地面はすべてマイデザインで敷く（家のまわりはレンガ、ほかは石畳。物の下も敷く）----
pave = {(x, y) for y in range(H) for x in range(W) if Z[y][x] in URBAN and g(x, y) in '13' and lv(x, y) <= 2 and (x, y) not in slope and (x, y) not in trees and ((x, y) not in occ or (x, y) in props) and (x, y) not in road}
q = [p for p in pave if any((p[0] + dx, p[1] + dy) in road and lv(p[0] + dx, p[1] + dy) == lv(*p) for dx, dy in N4)]
reach = set(q)
while q:   # 道から歩いて行ける所だけ敷く
    x, y = q.pop()
    for dx, dy in N4:
        p_ = (x + dx, y + dy)
        if p_ in pave and p_ not in reach and lv(*p_) == lv(x, y):
            reach.add(p_); q.append(p_)
for y in range(H):
    for x in range(W):
        if (x, y) in reach:
            if (x, y) in occ_b and not any(x0 <= x < x0 + SIZE[b['kind']][0] and y0 <= y < y0 + SIZE[b['kind']][1] for b in LAY['buildings'] for x0, y0 in [b['at']]):
                st, des = 'brick', 'brick_vintage_red'   # 家のまわり1マス：赤いレンガ
            elif (x, y) in occ_b:
                continue
            else:
                st, des = ('herring', 'brick_arch') if noise(x * .35 + 9, y * .35) > .25 else ('cobble', 'road_chic_stone')
            ground.append({'id': 'C-paving', 'style': st, 'rect': [x, y, x, y], 'design': des, 'skip': []}); occ.add((x, y))

# ---- 花（村の家の庭・郊外の花畑・森のふち）----
for b in LAY['buildings']:
    z = Z[b['at'][1]][b['at'][0]]
    if z in 'SJ' and b['kind'] in ('villager', 'player_house'):
        x0, y0 = b['at']; w, d = SIZE[b['kind']]
        for x in range(x0 - 2, x0 + w + 2):
            for y in range(y0 - 1, y0 + d + 1):
                if (x in (x0 - 2, x0 - 1, x0 + w, x0 + w + 1)) and free(x, y, lv(x0, y0)) and (x, y) not in trees:
                    plants.append({'id': b['id'] + '-garden', 'type': 'roses' if z == 'S' else 'mums', 'rect': [x, y, x, y], 'colors': ['red', 'white', 'pink', 'yellow'] if z == 'S' else ['white', 'yellow'], 'fit': True}); occ.add((x, y))
fields = [(rng.choice(['cosmos', 'tulips', 'lilies', 'hyacinths', 'windflowers']), rng.choice([['red', 'yellow', 'white'], ['pink', 'white'], ['purple', 'blue', 'white'], ['orange', 'yellow']])) for _ in range(6)]
k = 0
for y in range(H):
    for x in range(W):
        if Z[y][x] == 'S' and free(x, y, lv(x, y)) and (x, y) not in trees and (x, y) not in bush and noise(x * .8 + 50, y * .8) > .18:
            t, cs = fields[(x // 9 + y // 7) % len(fields)]
            plants.append({'id': 'S-fields', 'type': t, 'rect': [x, y, x, y], 'colors': cs, 'fit': True}); occ.add((x, y))
for x, y in list(bush):
    if (x, y) in occ:
        bush.discard((x, y))

# ---- 書き出し ----
for y in range(H):
    for x in range(W):
        if G[y][x] == '1' and Hh[y][x] >= 2:
            G[y][x] = '3'
T['grid'] = [''.join(r) for r in G]
T['zones'] = [''.join(r) for r in Z]
T['zone_names'] = NAMES
gr = {k: v for k, v in T.get('ground', {}).items() if v == 'm'}
for x, y in bush:
    gr['%d,%d' % (x, y)] = 'u'
T['ground'] = gr
T['facilities'] = []
json.dump(T, open(os.path.join(ROOT, f'plan{PLAN}-terrain.json'), 'w'))
INC = {'C': 'brick staircase', 'S': 'natural ramp', 'F': 'log staircase', 'J': 'stone staircase', 'B': 'stone staircase', 'H': 'log staircase', 'P': 'white-plank ramp'}
BRI = {'C': 'brick bridge', 'S': 'stone bridge', 'F': 'log bridge', 'J': 'red zen bridge', 'B': 'zen bridge', 'H': 'log bridge', 'P': 'wooden bridge'}
B3 = {'note': '案3（第49回）：乱れ（たね %d）で作りなおした島。地形 tools/plan3_gen.py・配置 tools/plan3_layout.py・中身 tools/plan3_fill.py' % T['seed'],
      'season': P2['season'], 'rules': P2['rules'], 'buildings': B_ALL,
      'inclines': {'%d,%d' % (x, y): INC[Z[y][x]] for x, y, d in T['inclines']},
      'bridges': {'%d,%d' % (r[0], r[1]): BRI[Z[r[1]][r[0]]] for r in T.get('bridges', [])},
      'paths': P2['paths'], 'groups': groups, 'ground': ground, 'plants': plants, 'orchards': [], 'ground_styles': P2.get('ground_styles', {})}
json.dump(B3, open(os.path.join(ROOT, f'designs/build_plan{PLAN}.json'), 'w'), ensure_ascii=False, indent=1)
print('木', len(trees), '低木', len(bush), 'キット', len([g_ for g_ in groups if g_.get('kit')]), 'パネル', len(panel_groups), '地面', len(ground), '花', len(plants))
