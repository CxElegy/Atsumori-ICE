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
if os.path.exists(os.path.join(ROOT, f'designs/kits_plan{PLAN}.json')):   # 第57回：地区ごとに設計した見せ場（案4 は kits_plan4.json、案5 は kits_plan5*.json）
    KITS.update(J(f'designs/kits_plan{PLAN}.json')['kits'])
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
ZM = SPEC.get('zone_meta', {})   # 第62回（案7・世界旅行の島）：spec で地区を足す（エジプト・アメリカ・ヨーロッパ など）。名前・坂・橋・柵・低木・見せ場の地面
for k_, m_ in ZM.items():
    CENT.setdefault(k_, [tuple(m_.get('center', (56, 48)))])
    if m_.get('name'):
        NAMES[k_] = m_['name']
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
for k_ in ZM:
    PLAN_KITS.setdefault(k_, [])
groups, ground, plants = [], [], []
def ring_skip(ax, ay, KW, KD):   # 囲みの1マスのうち、ちがう段・水・道などには地面を貼らない
    L = lv(ax, ay)
    return [[x, y] for y in range(ay - 1, ay + KD + 1) for x in range(ax - 1, ax + KW + 1)
            if not (inside(x, y) and g(x, y) in '13' and lv(x, y) == L)]
bld_cells = {(x, y) for b in LAY['buildings'] for x0, y0 in [b['at']] for x in range(x0, x0 + SIZE[b['kind']][0]) for y in range(y0, y0 + SIZE[b['kind']][1])}
CAMERA = bool(SPEC.get('camera_check'))   # 第60回：ゲームのカメラ（南から北を見る）から見えない所には自動の物を置かない
# 第60回：自動の物を置かない所（spec の keep_clear の四角・坂の上下の出入口）と、背の高い物（城の塔・門・城壁）の真うしろ
KEEP_CLEAR = {(x, y) for x0, y0, x1, y1 in SPEC.get('keep_clear', []) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
if CAMERA:
    for ix, iy, idir in T['inclines']:
        if idir in 'NS':
            KEEP_CLEAR |= {(ix + a, b) for a in range(2) for b in (iy - 2, iy - 1, iy + 4, iy + 5)}
        else:
            KEEP_CLEAR |= {(a, iy + b) for b in range(2) for a in (ix - 2, ix - 1, ix + 4, ix + 5)}
CAM_ROOF = {(x, y) for x0, y0, x1, y1 in SPEC.get('camera_roofs', []) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}   # 第60回：動かせない建物（案内所・飛行場）の屋根も物をかくす
TALL, LMK = set(), set()
for it in SPEC.get('landmarks', []):
    if CAMERA:   # 第60回：土台の目じるしの場所は、運河の岸の自動の物（柵など）にとらせない
        w_, d_ = foot(CAT[it[0]]['size'], it[3])
        LMK |= {(a, b) for a in range(it[1], it[1] + w_) for b in range(it[2], it[2] + d_)}
    if it[0] in ('castle tower', 'castle gate', 'castle wall', 'windmill', 'lighthouse', 'silo'):
        w_, d_ = foot(CAT[it[0]]['size'], it[3])
        TALL |= {(a, b) for a in range(it[1], it[1] + w_) for b in range(it[2], it[2] + d_)}
def cam_ok(x, y):
    if not CAMERA:
        return True
    if (x, y) in KEEP_CLEAR or (x, y + 1) in TALL or (x, y + 2) in TALL:
        return False
    if (x, y + 1) in globals().get('trees', ()):
        return False   # 木のかさの真うしろ（第60回）
    L = lv(x, y)
    for k in (1, 2, 3):   # 第60回の最終審査：2段高い崖は3列先でもかくす・家の屋根は3列うしろまでかくす
        if inside(x, y + k) and g(x, y + k) not in 'wSsb' and lv(x, y + k) - L >= min(k, 2):
            return False   # 南の高い段（崖の裏）にかくれる
        if ((x, y + k) in bld_cells or (x, y + k) in CAM_ROOF) and (k < 3 or lv(x, y + k) >= L):
            return False   # 家の真裏（案内所・飛行場の屋根も）。3列先の屋根がかくすのは同じ段の物だけ
    return True
def stand_ok(x, y, cells=()):   # 第60回：物のとなり（たて横）に、同じ段で立てるマス（木・低木・建物・坂・ほかの物でない）がある
    if not CAMERA:
        return True
    L = lv(x, y)
    for dx, dy in N4:
        c = (x + dx, y + dy)
        if c in cells or not inside(*c):
            continue
        if g(*c) in '13p' and lv(*c) == L and c not in globals().get('bush', ()) and c not in globals().get('trees', ()) and c not in bld_cells and c not in slope and (c not in occ or c in kitring):
            return True
    return False
def fits_designed(kid, ax, ay):   # 第57回：手で場所を決めた見せ場は通りの上にも置ける（歩ける幅は plan4_kitcheck.py で確かめる）
    k = KITS[kid]; KW, KD = k['size']; L = lv(ax, ay)
    return all(inside(x, y) and g(x, y) in '13p' and lv(x, y) == L and (x, y) not in bld_cells and (x, y) not in front and (x, y) not in slope and (x, y) not in occ
               for y in range(ay, ay + KD) for x in range(ax, ax + KW))
def place_kit(kid, tx, ty, r, z, style=None, flip=None, gid=None, name=None, on_road=False):
    k = KITS[kid]; KW, KD = k['size']; best = None
    for y in range(ty - r, ty + r + 1):
        for x in range(tx - r, tx + r + 1):
            if (fits_designed(kid, x, y) if on_road else fits(kid, x, y)):
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
    L = lv(ax, ay)
    for y in range(ay - 1, ay + KD + 1):
        for x in range(ax - 1, ax + KW + 1):
            inner = ax <= x < ax + KW and ay <= y < ay + KD
            if not inner and lv(x, y) != L:
                continue   # 第57回：段のちがうまわりのマス（屋根の城壁・崖の上の柵・崖のすそのパネル）は見せ場がとらない
            if not inner and (x, y) in LMK:
                continue   # 第60回：土台の目じるし（塔など）の場所は見せ場のまわりの1マスにとらせない
            occ.add((x, y))
            if not inner:
                kitring.add((x, y))
    if k.get('noground') or not (style or GSTYLE[z]):
        return True   # 第62回（案7）：地面のマイデザインを敷かない見せ場（歩いて上がらない丘の上・砂漠）
    st = style or GSTYLE[z][len(groups) % len(GSTYLE[z])]
    if SPEC.get('paving') and z in 'CP' and not style:
        st = SPEC['paving'][0]   # 第60回：見せ場のまわりの地面も町の敷石にそろえる
    ground.append({'id': gid, 'style': st, 'rect': [ax - 1, ay - 1, ax + KW, ay + KD], 'design': GDES[st], 'skip': ring_skip(ax, ay, KW, KD)})
    return True
GSTYLE = {'C': ['herring', 'brick', 'flag', 'cobble'], 'S': ['garden', 'flag'], 'P': ['plank', 'flag'], 'J': ['moss'], 'B': ['moss'], 'H': ['leaves'], 'F': ['leaves']}
GDES = {'herring': 'brick_arch', 'brick': 'brick_vintage_red', 'flag': 'brick_greige', 'cobble': 'road_chic_stone', 'garden': 'brick_city_old', 'plank': 'plank', 'moss': 'stone_natural', 'leaves': 'brick_autumn', 'stoneold': 'stone_old'}
for k_, m_ in ZM.items():
    GSTYLE.setdefault(k_, m_.get('gstyle', ['flag']))
for kd in SPEC.get('kits', []):   # 設計の見せ場（ねらいの場所のまわりに）。木より先に場所をとる
    tx, ty = kd.get('at') or kd['near']
    place_kit(kd['kit'], tx, ty, 0 if 'at' in kd else kd.get('r', 6), kd['zone'], kd.get('style'), kd.get('flip'), name=kd.get('name'), on_road=kd.get('on_road', False))

if SPEC.get('axis_paving'):   # 第60回：軸の背骨（軸の通りだけ別のマイデザイン）
    ap = SPEC['axis_paving']
    for r_ in ap['rects']:
        ground.append({'id': 'C-axis', 'style': ap['style'], 'rect': r_, 'design': GDES[ap['style']], 'skip': []})
# 地区の見せ場も木より先に（道に面した平地を林にとられないように）
n = 0
PLAN_KITS.update(SPEC.get('auto_kits', {}))   # 第60回：案ごとに野山の自動の見せ場を変える（同じお茶会を4つ並べない）
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
            ok = fits(kid, ax, ay, flip) and not any((x, y) in KEEP_CLEAR for x in range(ax, ax + KW) for y in range(ay, ay + KD))   # 第60回：自動の見せ場も keep_clear をよける（軸の北に墓地が来ないように）
            if ok and CAMERA and not all(cam_ok(x, y) for x in range(ax, ax + KW) for y in range(ay, ay + KD)):
                ok = False   # 第60回の最終審査：自動の見せ場も家の真裏・崖の裏に置かない（源氏の茶席が家のうしろだった）
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
    if CAMERA and diag_block(x, y):
        return False
    return True
def diag_block(x, y):   # 第60回の最終審査：ななめに崖・水・浜が接する木は、ゲームで植えられるか確かめていない（植えない）
    return any(not inside(x + dx, y + dy) or g(x + dx, y + dy) in 'wbsSrK' or (x + dx, y + dy) in bld_cells or (x + dx, y + dy) in slope or (g(x + dx, y + dy) != 'P' and lv(x + dx, y + dy) != lv(x, y))
               for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1)))
GROVES = {'F': (7, 9), 'J': (4, 7), 'H': (5, 6), 'B': (4, 6), 'S': (3, 5), 'C': (9, 2), 'P': (3, 3)}   # 林の数・1つの林の木の数
GROVES.update({k: tuple(v) for k, v in SPEC.get('groves', {}).items()})   # 第60回：案ごとに林の数を変える（町 C は {"C": [0, 0]} で、木は street_trees だけ）
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
# 第58回：町の木（作例の並木・広場の木・屋上の木）。spec の street_trees に場所を手で決め、ゲームの決まりで確かめる：
# 上下左右が水・橋・浜・海・岩・飛行場・坂・建物でなく同じ段（acnh_build.py と同じ）、建物のまわり1マス・入口の前・見せ場の上でない。道のマスなら草地にもどして植える
street = []
for x, y in SPEC.get('street_trees', []):
    L = lv(x, y)
    if g(x, y) not in '13p' or (x, y) in occ_b or (x, y) in slope or (x, y) in front or (x, y) in occ:
        print('町の木を植えられない', x, y, g(x, y)); continue
    if any(g(x + dx, y + dy) in 'wbsSrK' or (x + dx, y + dy) in bld_cells or (x + dx, y + dy) in slope or (g(x + dx, y + dy) != 'P' and lv(x + dx, y + dy) != L) for dx, dy in N4):
        print('町の木を植えられない（となり）', x, y); continue
    if CAMERA and diag_block(x, y):
        print('町の木を植えられない（ななめ）', x, y); continue
    if (x, y) in road and SPEC.get('trees_off_roads'):
        continue   # 第62回（案7）：v4 の林のマスに道が通ったら、その木は植えない（道を切らない）
    if (x, y) in road:
        G[y][x] = '3' if L >= 2 else '1'; road.discard((x, y))
    street.append((x, y)); occ.add((x, y))
trees -= set(street)
trees = set(sorted(trees, key=lambda p: (p[0] * 7 + p[1] * 13) % 97)[:185 - len(street)]) | set(street)   # 木は島ぜんたいで185本まで（森から町へ植えかえる）
bush = set()
NOBUSH = {(x, y) for x0, y0, x1, y1 in SPEC.get('bush_clear', []) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}   # 第60回：低木を置かない四角（主塔の真うしろの芝）
BUSH = {'F': .55, 'J': .35, 'H': .5, 'B': .3, 'S': .14, 'C': .02, 'P': .12}
BUSH.update({k_: m_['bush'] for k_, m_ in ZM.items() if 'bush' in m_})
if SPEC.get('base') == 'authored':
    BUSH['P'] = .02   # 案4：港も町（低木はほとんどなし）
for y in range(H):
    for x in range(W):
        z = Z[y][x]
        if g(x, y) in '13' and (x, y) not in trees and (x, y) not in occ_b and (x, y) not in slope and (x, y) not in front and (x, y) not in road and (x, y) not in occ and (x, y) not in NOBUSH:
            near = sum((x + dx, y + dy) in trees for dx in range(-2, 3) for dy in range(-2, 3))
            p = BUSH.get(z, 0) + .12 * near
            if lv(x, y) >= 1 and rng.random() < p * (.6 + .4 * (noise(x * 2, y * 2) + 1)):
                bush.add((x, y))
for x, y in SPEC.get('bushes', []):   # 第62回：低木を置くマスを手で（v4 の林のうち木にしないマス）
    if g(x, y) in '13' and (x, y) not in trees and (x, y) not in occ_b and (x, y) not in slope and (x, y) not in front and (x, y) not in road and (x, y) not in occ:
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
    zp = ZM.get(Z[y][x], {}).get('panel')   # 第62回（案7）：地区ごとの壁のマイデザイン（{"window": ..., "lamp": ...}）
    if zp:
        des = zp['lamp'] if piece in ('lamp', 'door', 'arch') else zp['window']
    panel_groups.append(['simple panel', x, y, rot, 'Brown', des, piece]); occ.add((x, y))
    cnt8[(x // 8, y // 8)] = cnt8.get((x // 8, y // 8), 0) + 1
for x, y, rot, piece in SPEC.get('panels', {}).get('items', []):
    if g(x, y) in '13' and (x, y) not in occ and (x, y) not in road and (x, y) not in slope and (x, y) not in front and (x, y) not in occ_b:
        panel(x, y, rot, piece)
    elif (x, y) in road and g(x, y) in '13' and (x, y) not in slope:   # 道のつきあたり：道の最後の1マスにアーチ
        panel(x, y, rot, piece)
CAP = {'C': 14, 'P': 6 if SPEC.get('base') != 'authored' else 12}
if SPEC.get('urban'):   # 第62回（案7）：町としてあつかう地区すべてに崖のすそのパネル
    CAP = {k: CAP.get(k, 12) for k in SPEC['urban']}
if SPEC.get('panel_cap'):   # 第60回：同じ物は 8×8 に6個まで（島の評価）。パネルを減らし、のこりの崖のすそは店先（storefront 2×1・マイデザイン）で
    CAP = {k: SPEC['panel_cap'] for k in CAP}
ALT = SPEC.get('panel_alt')
alt8 = {}
URBAN = 'CP' if SPEC.get('base') == 'authored' else 'C'   # 案4：港（ドックランズ）も町
URBAN = SPEC.get('urban', URBAN)   # 第62回：町としてあつかう地区を spec で（案7 はロンドンだけ）
k = 0
for y in range(1, H - 1):
    for x in range(1, W - 1):
        z = Z[y][x]
        if z not in CAP or g(x, y) not in '13p' or (x, y) in occ_b or (x, y) in slope or (x, y) in front or (x, y) in occ or (x, y) in trees:
            continue
        if SPEC.get('roof_visible') and (lv(x, y + 1) > lv(x, y) or lv(x, y + 2) > lv(x, y) and lv(x, y + 1) == lv(x, y) and (x, y + 1) not in road):
            continue   # 第62回（案7・規則の審査）：すぐ南が高い段のマス（崖にかこまれた穴など）のパネルはカメラから見えない
        for rot, (dx, dy) in enumerate(DIRS):
            a, b_ = x + dx, y + dy
            if rot == 2:
                continue   # 第58回：北を向くパネル（崖が南）はゲームのカメラ（南から北を見る）から見えない
            if rot in (1, 3) and SPEC.get('panels_face_south'):
                continue   # 第60回：東・西を向くパネルはカメラから横向き（ふちしか見えない）
            if (x, y) in road and SPEC.get('panels_off_road'):
                continue   # 第62回（案7）：通りの上にはパネルを貼らない（細い通りを切らない）
            if (x, y) in road and not (rot != 2 and all((x - i * dx, y - i * dy) in road and (x - i * dx, y - i * dy) not in occ and (x - i * dx, y - i * dy) not in slope and lv(x - i * dx, y - i * dy) == lv(x, y) for i in (1, 2))):
                continue   # 道の上には、通りが3マス幅以上で、反対がわの2マスがあいている所だけ貼る（第57回：2マス幅の路地の両がわに貼ってふさいでいた）。北を向くパネルはカメラから見えないので道には貼らない
            if lv(a, b_) == lv(x, y) + 1 and g(a, b_) != 'w' and (a, b_) not in slope and cnt8.get((x // 8, y // 8), 0) < CAP[z] and cam_ok(x, y) and stand_ok(x, y):
                panel(x, y, rot, PIECES[k % len(PIECES)]); k += 1
                break
            if ALT and rot == 0 and (x, y) not in road and lv(a, b_) == lv(x, y) + 1 and g(a, b_) != 'w' and (a, b_) not in slope and alt8.get((x // 8, y // 8), 0) < 6 and cam_ok(x, y):
                x2 = x + 1   # 店先は2マス：となりも崖のすそ・同じ段・あいている
                if g(x2, y) in '13' and lv(x2, y) == lv(x, y) and lv(x2, y - 1) == lv(x, y) + 1 and g(x2, y - 1) != 'w' and (x2, y - 1) not in slope and cam_ok(x2, y) \
                        and (x2, y) not in occ and (x2, y) not in road and (x2, y) not in occ_b and (x2, y) not in slope and (x2, y) not in front and (x2, y) not in trees and (x2 // 8) == (x // 8) \
                        and (stand_ok(x, y, {(x2, y)}) or stand_ok(x2, y, {(x, y)})):
                    panel_groups.append([ALT, x, y, 0, 'Brown', 'wall_brick_lamp']); occ |= {(x, y), (x2, y)}
                    alt8[(x // 8, y // 8)] = alt8.get((x // 8, y // 8), 0) + 1
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
    return (x, y) not in KEEP_CLEAR and (x, y) not in LMK and inside(x, y) and g(x, y) in '13p' and (x, y) not in slope and (x, y) not in bld and (x, y) not in front and ((x, y) not in occ or (x, y) in kitring) and (x, y) not in trees and not near_bridge(x, y) \
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
                if all(bank_ok(*c) and lv(*c) == lv(x, y) and not (CAMERA and c in road) for c in fp):   # 第60回：ヨットで運河通りをせばめない
                    ax, ay = min(c[0] for c in fp), min(c[1] for c in fp)
                    canal_items.append(['yacht', ax, ay, 0 if horiz else 1, 'White']); occ |= set(fp); boat = True; continue
            k = i % 6
            if CAMERA and (k in (1, 5) or (k == 4 and i % 12 != 4)):
                k = 2   # 第60回の最終審査：岸壁の柵は一続きに（街灯と自転車・花の荷車のほかは柵）
            if k == 0:
                canal_items.append(['streetlamp', x, y, 0, 'Black']); occ.add((x, y))
            elif k in (2, 3):
                canal_items.append(['iron-and-stone fence', x, y, 0, None]); occ.add((x, y))
            elif k == 4 and i % 12 == 4:
                nx, ny = (x + 1, y) if horiz else (x, y + 1)
                if (nx, ny) in cells and bank_ok(nx, ny):
                    wagon = i % 24 == 4 and not CAMERA   # 第60回：花の荷車は地区の見せ場に（岸壁で同じ荷車をくりかえさない）。自動は自転車だけ
                    canal_items.append(['garden wagon' if wagon else 'cruiser bike', x, y, 0 if horiz else 1, 'Dark brown' if wagon else 'Green']); occ |= {(x, y), (nx, ny)}
if canal_items:
    groups.append({'id': 'C-canals', 'zone': 'C', 'name': '運河の岸：城壁と岸壁（街灯・柵・花の荷車・自転車・ヨット）', 'at': [0, 0], 'items': canal_items, 'lines': [],
                   'note': '主水路の片がわは城壁（castle wall にレンガのマイデザイン）、もう片がわは岸壁。副水路の岸は草と花'})

# 案4：町の2段目・3段目のかたまりのうち、道のない（歩いて上がらない）かたまりは「建物」：ふちは城壁（銃眼のあるレンガの壁）、中は屋上の庭
# 第58回：町の目じるし（spec の landmarks）：段の上の塔（castle tower＝ビッグ・ベン、倉庫の荷上げの塔）など。屋根より先に場所をとる
marks = []
for it in SPEC.get('landmarks', []):
    name, x, y, rot = it[0], it[1], it[2], it[3]
    w, d = foot(CAT[name]['size'], rot); L = lv(x, y)
    cells = [(a, b) for a in range(x, x + w) for b in range(y, y + d)]
    okc = '13p' if name == 'castle gate' else '13'   # 第60回：城門（まん中のアーチをくぐれる）は道の上にも置ける
    if all(g(a, b) in okc and lv(a, b) == L and (a, b) not in occ and (a, b) not in slope and (a, b) not in occ_b and (a, b) not in front and (a, b) not in trees for a, b in cells):
        marks.append(list(it)); occ |= set(cells)
    else:
        print('目じるしを置けない', it)
if marks:
    groups.append({'id': 'C-landmarks', 'zone': 'C', 'name': '町の目じるし（段の上の塔）', 'at': [0, 0], 'items': marks, 'lines': []})
roofs, roofp = [], []
rground = set()
RV = SPEC.get('roof_visible')   # 第62回（案7）：屋根の上はカメラから見える物だけ・一本だけの柵なし・はしごで下りるマス
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
            if any((x + dx, y + dy) in slope for x, y in comp for dx, dy in N4):
                continue   # 坂で上がるかたまり（テラス）は鉄の柵のまま
            # 第57回：屋根を1種類にしない（「城壁ばかりで単調」）。かたまりごとに屋根の種類を変える：
            #   fort＝ふちに城壁（3段目の塔・大きな建物だけ）／slate・slate_dark・red＝屋根のマイデザイン（目録の本物：灰色のレンガ・濃い灰色の石畳・くすんだ茶色のレンガ）に、
            #   煙突の代わりのレンガのカベ1本と、室外機・給水タンク／garden＝ふちは生け垣、中は花の屋上庭園
            n_ = len(comp); mx, my = min(comp)
            kinds = ['slate', 'garden', 'slate', 'garden', 'slate'] if lv(x0, y0) == 2 else ['fort', 'red', 'fort', 'red']
            kinds = SPEC.get('roof_kinds', {}).get(str(lv(x0, y0)), kinds)
            kinds = ZM.get(Z[y0][x0], {}).get('roofs', {}).get(str(lv(x0, y0)), kinds)   # 第62回（案7）：地区ごとの屋根（エジプト＝砂岩の平屋根・港＝白・ヨーロッパ＝テラコッタ）   # 第60回：案ごとに屋根の種類のまぜ方を変える（灰色の平らな屋根ばかりにしない）   # 茶色のレンガの屋根は2段目だと通りのレンガとまぎれるので3段目だけ。第58回：通りの石畳（road_chic_stone）は屋根に使わない（屋根と通りが同じ柄になる）
            rk = 'fort' if n_ >= 40 and lv(x0, y0) == 2 and (mx * 7 + my) % 3 == 0 else kinds[(mx * 7 + my * 13) % len(kinds)]
            if n_ <= 3:
                rk = 'slate' if rk == 'garden' else rk
            for ox, oy, ok_ in SPEC.get('roof_overrides', []):   # 第60回：かたまりごとに屋根を手で決める（屋上の庭・城壁など）
                if (ox, oy) in cs:
                    rk = ok_
            interior = [(x, y) for x, y in sorted(comp) if not any(lv(x + dx, y + dy) < lv(x, y) for dx, dy in DIRS)]
            if rk == 'garden' and len(interior) < 4:
                rk = 'slate'   # 第58回：中のない細いかたまりを生け垣でふちどると、緑の箱になる
            stacks = set(interior[2::9]) if rk in ('slate', 'slate_dark', 'red') else set()   # 煙突（レンガのカベ1本）
            units = set(interior[6::13]) - stacks if rk in ('slate', 'slate_dark') else set()   # 室外機
            plain = set()
            if RV:   # 第62回（案7・規則の審査）：屋根のかたまりごとに、はしごで上り下りできるふちのマスを1つ残す（下のマスも空ける）
                cx_ = sum(x for x, _ in comp) / n_
                for x, y in sorted(comp, key=lambda p: (-p[1], abs(p[0] - cx_))):
                    nb = [(x + dx, y + dy) for dx, dy in DIRS if lv(x + dx, y + dy) == lv(x, y) - 1 and g(x + dx, y + dy) in '13p' and ((x + dx, y + dy) not in occ or (x + dx, y + dy) in rground) and (x + dx, y + dy) not in trees and (x + dx, y + dy) not in slope]
                    if nb and (x, y) not in occ and (x, y) not in trees:
                        plain.add((x, y)); occ.add(nb[0]); break
                else:   # 下のマスがみなうまっているときは、崖のすその1マスのパネルを1枚はずす
                    pan = {(it[1], it[2]): it for it in panel_groups if it[0] == 'simple panel'}
                    for x, y in sorted(comp, key=lambda p: (-p[1], abs(p[0] - cx_))):
                        nb = [(x + dx, y + dy) for dx, dy in DIRS if lv(x + dx, y + dy) == lv(x, y) - 1 and (x + dx, y + dy) in pan]
                        if nb and (x, y) not in occ and (x, y) not in trees:
                            panel_groups.remove(pan[nb[0]]); plain.add((x, y)); break
                    else:
                        print('屋根から下りるマスがない（このかたまりは草のまま）', min(comp))
                        continue
                walls_ = set()   # 城壁を先に決めて、そのすぐ北（2列）に花を植えない
                for x, y in sorted(comp):
                    if rk == 'fort' and (x, y) not in plain and (x, y) not in occ and lv(x, y + 1) < lv(x, y) and (x + 1, y) in cs and (x + 1, y) not in occ and lv(x + 1, y + 1) < lv(x + 1, y) and (x, y) not in walls_:
                        walls_ |= {(x, y), (x + 1, y)}
            for x, y in sorted(comp):
                if (x, y) in occ or (x, y) in trees or (x, y) in slope:
                    continue
                low = [(dx, dy) for dx, dy in DIRS if lv(x + dx, y + dy) < lv(x, y)]
                hid = RV and (any(lv(x, y + k) > lv(x, y) for k in (1, 2)) or any((x, y + k) in walls_ for k in (1, 2)))   # カメラから見えないマス
                if (x, y) in plain or RV and hid and (x, y) not in walls_:
                    pass
                elif rk == 'fort' and (0, 1) in low and not (CAMERA and any((a, y + k) in bld_cells for a in (x, x + 1) for k in (1, 2))):   # 第58回：城壁はカメラに向く南のふちだけ（背中あわせの2列にしない）。第60回：家の真うしろ（見えない）は庭に
                    x2, y2 = x + 1, y
                    if (x2, y2) in cs and (x2, y2) not in occ and (x2, y2) not in trees and lv(x2, y2 + 1) < lv(x2, y2):
                        roofs.append(['castle wall', x, y, 0, 'Brown', 'wall_windows_bricks']); occ |= {(x, y), (x2, y2)}
                        continue
                    elif not RV:   # 案7：一本だけの柵は置かない（屋根のマイデザインに）
                        roofs.append(['brick fence', x, y, 0, None]); occ.add((x, y))
                        continue
                elif low and rk == 'garden':
                    roofs.append(['hedge', x, y, 0, None]); occ.add((x, y))
                    continue
                elif rk == 'garden' or rk == 'fort' and (SPEC.get('fort_garden') or noise(x * .5 + 3, y * .5) <= -.1):   # 屋上の庭（第60回：fort_garden で城壁の屋根の中はぜんぶ庭）
                    roofp.append({'id': 'C-roofgarden', 'type': ['roses', 'tulips', 'roses', 'lilies'][(x * 3 + y) % 4], 'rect': [x, y, x, y], 'colors': ['red', 'white', 'pink'] if (mx + my) % 2 else ['white', 'yellow', 'orange'], 'fit': True}); occ.add((x, y))
                    continue
                elif (x, y) in stacks and not RV:
                    roofs.append(['brick fence', x, y, 0, None]); occ.add((x, y))
                    continue
                elif (x, y) in units:
                    roofs.append(['outdoor air conditioner', x, y, 0, None]); occ.add((x, y))
                    continue
                if True:   # 屋根のマイデザイン（はしごで上がって敷く）
                    rk_ = 'fort' if rk == 'garden' else rk
                    st = {'fort': ZM.get(Z[y0][x0], {}).get('fort_roof', 'roof'), 'slate': 'roof', 'slate_dark': 'roof_slate', 'red': 'roof_red', 'sand': 'roof_sand', 'white': 'roof_white', 'terra': 'roof_terra'}[rk_]
                    ground.append({'id': 'C-roof', 'style': st, 'rect': [x, y, x, y], 'design': {'roof': 'brick_grey', 'roof_slate': 'road_chic_stone', 'roof_red': 'brick_natural', 'roof_sand': 'brick_city_old', 'roof_white': 'brick_greige', 'roof_terra': 'brick_vintage_red'}[st], 'skip': []}); occ.add((x, y)); rground.add((x, y))
    if RV:   # 案7：屋根の上の一本だけの生け垣もやめる（屋根のマイデザインのまま）
        hc_ = {(r[1], r[2]) for r in roofs if r[0] == 'hedge'}
        for r in [r for r in roofs if r[0] == 'hedge' and not any((r[1] + dx, r[2] + dy) in hc_ for dx, dy in DIRS)]:
            roofs.remove(r)
    if roofs:
        groups.append({'id': 'C-roofs', 'zone': 'C', 'name': 'レンガのかたまりの上：ふちの城壁（castle wall）と屋上の庭', 'at': [0, 0], 'items': roofs, 'lines': []})
    plants.extend(roofp)
edge = []
for y in range(1, H - 1):
    for x in range(1, W - 1):
        if Z[y][x] not in URBAN or g(x, y) not in '13' or (x, y) in occ or (x, y) in occ_b or (x, y) in road or (x, y) in slope or (x, y) in front or (x, y) in trees:
            continue
        near_slope = any((x + dx, y + dy) in slope for dx in (-1, 0, 1) for dy in (-1, 0, 1))
        if not cam_ok(x, y):
            continue
        if lv(x, y) == 2 and not near_slope and any(lv(x + dx, y + dy) < lv(x, y) and g(x + dx, y + dy) not in 'w' for dx, dy in DIRS):
            edge.append([ZM.get(Z[y][x], {}).get('edge', 'iron fence'), x, y, 0, None]); occ.add((x, y))   # 上の町の崖のふち：鉄の柵（高架の手すりに見せる）。第62回：地区ごとの柵
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
FENCE.update({k_: m_['fence'] for k_, m_ in ZM.items() if m_.get('fence')})
fences = []
for b in LAY['buildings']:
    x0, y0 = b['at']; w, d = SIZE[b['kind']]; z = Z[y0][x0]
    if z == 'C' or z not in FENCE:
        continue
    ring = [(x0 - 1, y) for y in range(y0 - 1, y0 + d + 1)] + [(x0 + w, y) for y in range(y0 - 1, y0 + d + 1)] + [(x, y0 - 1) for x in range(x0, x0 + w)]
    for x, y in ring:
        if inside(x, y) and g(x, y) in '13' and (x, y) not in road and (x, y) not in slope and (x, y) not in front and (x, y) not in occ and (x, y) not in trees and lv(x, y) == lv(x0, y0) \
                and (not CAMERA or cam_ok(x, y)):   # 第60回：家の真うしろ（カメラから見えない）には柵・生け垣を立てない
            fences.append([FENCE[z], x, y, 0, 'White' if FENCE[z] == 'lattice fence' else None]); occ.add((x, y))
if RV:   # 案7：家のまわりの柵も、一本だけのものはやめる
    fc_ = {(f[1], f[2]) for f in fences}
    for f in [f for f in fences if not any((f[1] + dx, f[2] + dy) in fc_ for dx, dy in DIRS)]:
        fences.remove(f); occ.discard((f[1], f[2]))
if fences:
    groups.append({'id': 'S-fences', 'zone': 'S', 'name': '家のまわりの柵と生け垣（地区ごとの柵）', 'at': [0, 0], 'items': fences, 'lines': []})

# ---- ロンドンの通りの小物（街灯・電話ボックス・花の荷車・自転車・植木ばち…）：道に面したあいたマスに、間をあけて ----
STREET1 = [('streetlamp', 'Black'), ('round topiary', 'Green'), ('monstera', 'Black'), ('pot', 'Brown'), ('garbage bin', 'Black'), ('streetlamp', 'Black'), ('barrel', None),
           ('round topiary', 'Green'), ('standing shop sign', 'Black'), ('wooden box', 'Brown'), ('round streetlight', 'Black'), ('pot', 'White'), ('phone box', 'Red'), ('monstera', 'Black'),
           ('streetlamp', 'Black'), ('tin bucket', None), ('round topiary', 'Green'), ('plain wooden shop sign', 'Dark wood'), ('fire hydrant', 'Red'), ('barrel', None), ('pot', 'Brown'), ('park clock', 'Black')]
STREET1 = [tuple(v) for v in SPEC['street_props']] if SPEC.get('street_props') else STREET1   # 第60回：案ごとに通りの小物を変える（見せ場と同じ物をばらまかない）
STREET2 = [('garden wagon', 'Dark brown'), ('cruiser bike', 'Green'), ('flower bed', 'Dark brown'), ('iron garden bench', 'Black'), ('cruiser bike', 'Red'), ('medium cardboard boxes', None)]
STREET2 = [tuple(v) for v in SPEC['street_props2']] if 'street_props2' in SPEC else STREET2
props, street = set(), []
def cand(x, y):
    return Z[y][x] in URBAN and g(x, y) in '13' and (x, y) not in occ and (x, y) not in occ_b and (x, y) not in road and (x, y) not in slope and (x, y) not in front and (x, y) not in trees and cam_ok(x, y) \
        and not (RV and (lv(x, y + 1) > lv(x, y) or lv(x, y + 2) > lv(x, y) and lv(x, y + 1) == lv(x, y) and (x, y + 1) not in road))   # 案7：崖のすぐ北（見えない）には通りの小物を置かない
cells = [(x, y) for y in range(1, H - 1) for x in range(1, W - 1) if cand(x, y) and any((x + dx, y + dy) in road for dx, dy in N4)]
cells.sort(key=lambda p: (hash((p[0] * 31 + p[1] * 17) % 9973) % 1000))
k1 = k2 = 0
NAMED = {}   # 第60回：運河の岸や目じるしの物の名前（となりに同じ物を並べない）
if CAMERA:
    for gp in groups:
        for it in gp.get('items', []):
            if isinstance(it, list) and len(it) >= 3:
                NAMED[(it[1], it[2])] = it[0]
for x, y in cells:
    if not cand(x, y) or any((x + dx, y + dy) in props for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
        continue
    S1 = [tuple(v) for v in ZM.get(Z[y][x], {}).get('street_props', [])] or STREET1   # 第62回（案7）：地区ごとの通りの小物
    S2 = [tuple(v) for v in ZM.get(Z[y][x], {}).get('street_props2', [])] or STREET2
    if CAMERA and any(NAMED.get((x + dx, y + dy)) == S1[k1 % len(S1)][0] for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
        k1 += 1   # となりに同じ物（運河の岸の街灯など）があれば、次の小物にする
    if S2 and cand(x + 1, y) and (x + 1, y) not in props and (x + y) % 3 == 0 and lv(x + 1, y) == lv(x, y) and any((x + 1 + dx, y + dy) in props for dx in (-1, 0, 1) for dy in (-1, 0, 1)) is False:
        it, var = S2[k2 % len(S2)]; k2 += 1
        street.append([it, x, y, 0, var]); props |= {(x, y), (x + 1, y)}; occ |= {(x, y), (x + 1, y)}
    else:
        it, var = S1[k1 % len(S1)]; k1 += 1
        street.append([it, x, y, 0, var]); props.add((x, y)); occ.add((x, y))
if street:
    groups.append({'id': 'C-street', 'zone': 'C', 'name': 'ロンドンの通りの小物（街灯・電話ボックス・花の荷車・自転車・植木ばち）', 'at': [0, 0], 'items': street, 'lines': []})

# ---- 3段目のかたまりの屋上の庭（バラ）----
PAVE3 = bool(SPEC.get('pave_tier3'))   # 第60回：歩いて上がる3段目（城の前庭・上の町）は石畳を敷き、バラは上がれない3段目の屋根だけ
walk3 = set()
if PAVE3:
    q = [(x, y) for (x, y) in road if lv(x, y) == 3]
    walk3 = set(q)
    while q:
        x, y = q.pop()
        for dx, dy in N4:
            p_ = (x + dx, y + dy)
            if p_ not in walk3 and inside(*p_) and lv(*p_) == 3 and g(*p_) in '13p':
                walk3.add(p_); q.append(p_)
for y in range(H):
    for x in range(W):
        if Z[y][x] == 'C' and lv(x, y) == 3 and g(x, y) in '13' and (x, y) not in occ and (x, y) not in trees and (x, y) not in walk3:
            plants.append({'id': 'C-roof', 'type': 'roses', 'rect': [x, y, x, y], 'colors': ['red', 'white', 'pink'], 'fit': True}); occ.add((x, y))

# ---- ロンドンの地面はすべてマイデザインで敷く（家のまわりはレンガ、ほかは石畳。物の下も敷く）----
pave = {(x, y) for y in range(H) for x in range(W) if Z[y][x] in URBAN and g(x, y) in '13' and lv(x, y) <= (3 if PAVE3 else 2) and (x, y) not in slope and (x, y) not in trees and ((x, y) not in occ or (x, y) in props) and (x, y) not in road}
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
                if SPEC.get('paving'):   # 第60回：通りの外の地面を1種類に（作例はひとつの敷石。4種類の市松はうるさい）
                    st, des = SPEC['paving']
                if ZM.get(Z[y][x], {}).get('paving'):   # 第62回（案7）：地区ごとの敷石
                    st, des = ZM[Z[y][x]]['paving']
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
FIELDZ = 'S' + ''.join(k_ for k_, m_ in ZM.items() if m_.get('fields'))   # 第62回：花畑の地区（ヨーロッパの村など）
fields = [(rng.choice(['cosmos', 'tulips', 'lilies', 'hyacinths', 'windflowers']), rng.choice([['red', 'yellow', 'white'], ['pink', 'white'], ['purple', 'blue', 'white'], ['orange', 'yellow']])) for _ in range(6)]
k = 0
for y in range(H):
    for x in range(W):
        if Z[y][x] in FIELDZ and free(x, y, lv(x, y)) and (x, y) not in trees and (x, y) not in bush and noise(x * .8 + 50, y * .8) > .18 and not (RV and any(lv(x, y + k_) > lv(x, y) for k_ in (1, 2))):   # 案7：高いかたまりのすぐ北の畑は見えない
            t, cs = fields[(x // 9 + y // 7) % len(fields)]
            if CAMERA:   # 第60回の最終審査：ゲームにない色（青・紫のユリなど）を植えない
                cs = [c for c in cs if c in P2['rules'].get('plants', {}).get(t, {}).get('colors', cs)] or ['white']
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
INC.update({k_: m_['inc'] for k_, m_ in ZM.items() if m_.get('inc')}); BRI.update({k_: m_['bri'] for k_, m_ in ZM.items() if m_.get('bri')})
B3 = {'note': '案3（第49回）：乱れ（たね %d）で作りなおした島。地形 tools/plan3_gen.py・配置 tools/plan3_layout.py・中身 tools/plan3_fill.py' % T['seed'],
      'season': SPEC.get('season', P2['season']), 'rules': P2['rules'], 'buildings': B_ALL,
      'inclines': {'%d,%d' % (x, y): SPEC.get('incline_kinds', {}).get('%d,%d' % (x, y), INC[Z[y][x]]) for x, y, d in T['inclines']},   # 第58回：場所ごとに種類を変えられる（石の階段など）
      'bridges': {'%d,%d' % (r[0], r[1]): SPEC.get('bridge_kinds', {}).get('%d,%d' % (r[0], r[1]), BRI[Z[r[1]][r[0]]]) for r in T.get('bridges', [])},
      'paths': dict(P2['paths'], **SPEC.get('paths', {})), 'groups': groups, 'ground': ground, 'plants': plants, 'orchards': [], 'ground_styles': dict(P2.get('ground_styles', {}), roof='屋根（灰色のレンガ）', roof_slate='屋根（濃い灰色の石畳）', roof_red='屋根（茶色のレンガ）', **({'roof_sand': '屋根（砂岩色の明るい石畳：エジプトの平屋根）', 'roof_white': '屋根（グレージュのレンガ：港の白い家）', 'roof_terra': '屋根（赤いレンガ：ヨーロッパのテラコッタ）'} if any('roofs' in m for m in ZM.values()) else {}), **({'stoneold': '石畳（old stone road：町の通りと同じ）'} if SPEC.get('paving') or any('paving' in m for m in ZM.values()) else {}))}
json.dump(B3, open(os.path.join(ROOT, f'designs/build_plan{PLAN}.json'), 'w'), ensure_ascii=False, indent=1)
print('木', len(trees), '低木', len(bush), 'キット', len([g_ for g_ in groups if g_.get('kit')]), 'パネル', len(panel_groups), '地面', len(ground), '花', len(plants))
