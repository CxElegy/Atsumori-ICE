#!/usr/bin/env python3
"""第57回：案4の町の見せ場（キット）の案を、置く前に確かめる。地区ごとに見せ場を設計するときの道具。

  python3 tools/plan4_kitcheck.py --map D3                 # 地区 D3 の地形（段・道・水・建物・入口の前・坂・橋）を文字の地図で見る
  python3 tools/plan4_kitcheck.py --find lamp              # 目録から名前でさがす（大きさ・色・マイデザインの可否）
  python3 tools/plan4_kitcheck.py proposal.json            # 案を確かめる（NG があれば終了コード 1）
  python3 tools/plan4_kitcheck.py proposal.json --map      # 案を地図に重ねて見る
  python3 tools/plan4_kitcheck.py a.json b.json ...        # いくつかの案をまとめて（地区のあいだの重なりも）。--merge で designs/kits_plan4.json に書く
  python3 tools/plan4_kitcheck.py --built                  # 組み上がった島（自動の飾りもふくめた物すべて）で、道・入口・坂・橋に歩いて行けるか

案の形（JSON）
  {"district": "D3", "new_kits": {"p4_xxx": {kits.json と同じ形}}, "placements": [{"kit": "p4_xxx", "at": [x, y], "on_road": false, "flip": false, "name": "..."}]}
  キットの形：{"name", "size": [w, d], "ref": [...], "items": [[名前, dx, dy, rot, 色, マイデザイン?]], "lines": [{"item", "from", "to", "rot"?, "var"?}], "plants": [{"type", "rect": [x0, y0, x1, y1], "colors", "pattern"?, "fit"?}], "note"}

確かめること（あつ森の決まりは acnh_build.py、置き方は plan3_fill.py の place_kit と同じ）
  1. 目録：名前・外に置けるか・色・マイデザイン・大きさ（rot で向き）。キットの物はキットの四角の中。物どうし・花と物が重ならない
  2. 場所：キットの四角は地区の中・同じ段の平地（on_road なら道の上も可）。水・橋・坂・建物・入口の前・広場の上は不可。
     道の上に置かないキット（on_road=false）は、道でない平地で、建物のまわり1マスにかからず、同じ段の道に面する
  3. キットどうし：四角のあいだを1マスあける（地区のあいだも）
  4. 歩ける：飛行場の前の道から、道・橋・坂・広場・入口の前・キットの中のあいたマスを通って、置く前に行けた道（物がふさいだマスをのぞく）・
     家の入口の前・坂の上下・橋の両はしに、置いた後も行けること。キットごとに、行ける入口が1つはあること
  5. 混み具合：8×8 のかたまりで、見せ場の物が 30 マスまで（崖のパネル・柵などが後から入るので 45 よりきびしく）。同じ物（柵をのぞく）は 6 個まで
  6. 花：草地（道の上は不可。fit の花畑は道を飛ばす）
"""
import json, math, os, sys
from collections import Counter, deque

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding='utf-8'))
os.environ.setdefault('ICE_PLAN', '4')
PLAN = os.environ['ICE_PLAN']
CAT = J('designs/acnh_catalog.json')
ITEMS = CAT['items']
T = J(f'plan{PLAN}-terrain.json')
LAY = J(f'designs/plan{PLAN}_layout_out.json')
SPEC = J(f'designs/plan{PLAN}_spec.json')
BP = J(f'designs/build_plan{PLAN}.json')
DESIGN_ITEMS = BP['rules']['design_items']
DESIGNS = {d['id']: d for d in J('designs/catalog.json')['designs']}   # 本物のマイデザイン（MA コードつき）だけ
FLOWERS = BP['rules'].get('plants', {})
KITS = J('designs/kits.json')['kits']   # 前からあるキット（kits_plan4.json は案そのものから作るので読まない）
KITS_ALL = dict(KITS, **(J(f'designs/kits_plan{PLAN}.json')['kits'] if os.path.exists(os.path.join(ROOT, f'designs/kits_plan{PLAN}.json')) else {}))   # --built 用
G, HL = T['grid'], T['h']
W, H = len(G[0]), len(G)
inside = lambda x, y: 0 <= x < W and 0 <= y < H
g = lambda x, y: G[y][x] if inside(x, y) else 'S'
lv = lambda x, y: int(HL[y][x]) if inside(x, y) else 0
land = lambda x, y: g(x, y) in '13t'   # 木は見せ場の下ならぬく（植えるのは見せ場の後）
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))

DISTRICTS = {'D1': ([13, 38, 44, 58], 'ハイタウン（2段目・3段目の上の町、上の水路、広場、テラス）'),
             'D2': ([13, 59, 24, 82], '西の町（W1〜W3、エイブル、路地、浜への道）'),
             'D3': ([23, 59, 41, 82], '広場と市場（案内所の広場のまわり、市場の通り、東の小道、税関、飛行場の道）'),
             'D4': ([42, 38, 58, 67], '博物館の丘と川ぞい（運河、曳舟道、博物館のテラス、川ぞいの散歩道、倉庫）'),
             'D5': ([42, 68, 58, 82], 'バンクサイドと船だまり（2段目の町、下の通り、船だまり、波止場の道）'),
             'D6': ([62, 50, 80, 82], 'サザーク（2段目の町、ハイストリート、市場のホール、バラ・マーケット広場、路地、バンクサイド）'),
             'D7': ([81, 50, 98, 82], 'ドックランズ（灯台の丘、港の池と桟橋、倉庫、波止場）')}

if SPEC.get('districts'):   # 第59回：地区の四角は案の spec から（案5 など）。{"D1": {"box": [x0, y0, x1, y1], "name": "...", "zone": "C"}}
    DISTRICTS = {k: (v['box'], v.get('name', '')) for k, v in SPEC['districts'].items()}
DZONE = {k: v.get('zone', 'C') for k, v in SPEC.get('districts', {}).items()} or {'D7': 'P'}

SIZE = {'villager': (4, 4), 'player_house': (5, 4), 'museum': (7, 4), 'nook': (7, 4), 'able': (5, 4), 'campsite': (4, 4)}
bld, ring_b, front = {}, set(), set()
for b in LAY['buildings']:
    w, d = SIZE[b['kind']]; x0, y0 = b['at']
    for y in range(y0, y0 + d):
        for x in range(x0, x0 + w):
            bld[(x, y)] = b.get('villager') or b.get('name') or b['kind']
    ring_b.update((x, y) for y in range(y0 - 1, y0 + d + 1) for x in range(x0 - 1, x0 + w + 1))
    cols = range(x0, x0 + w) if w % 2 == 0 else range(x0 + w // 2 - 1, x0 + w // 2 + 2)
    front.update((x, y0 + d + k) for x in cols for k in range(2))
slope, inc_ends = {}, []
for i, (x, y, d) in enumerate(T['inclines']):
    cs = [(x + a, y + b) for a in range(2) for b in range(4)] if d in 'NS' else [(x + a, y + b) for a in range(4) for b in range(2)]
    for c in cs:
        slope[c] = i
    inc_ends.append(((x, y, d), [(x, y - 1), (x + 1, y - 1), (x, y + 4), (x + 1, y + 4)] if d in 'NS' else [(x - 1, y), (x - 1, y + 1), (x + 4, y), (x + 4, y + 1)]))
bridge = {(x, y) for y in range(H) for x in range(W) if g(x, y) == 'b'}
road = {(x, y) for y in range(H) for x in range(W) if g(x, y) == 'p'}
plaza = {(x, y) for y in range(H) for x in range(W) if g(x, y) == 'P'}
panels = {(p[0], p[1]): p[3] for p in SPEC.get('panels', {}).get('items', [])}
spec_kits = SPEC.get('kits', [])


def foot(size, rot):
    a, b = [max(1, math.ceil(float(v) - 1e-9)) for v in (size or '1x1').split('x')]
    return (b, a) if rot in (1, 3) else (a, b)


def kit_cells(k, ax, ay, flip):
    """キットの物（1つずつ、ゲームの大きさ）と花のマス。acnh_build.expand と同じ開き方"""
    KW = k['size'][0]; out, plants = [], []
    for it in k.get('items', []):
        name, dx, dy = it[0], it[1], it[2]
        rot = it[3] if len(it) > 3 else 0
        w, d = foot(ITEMS[name]['size'], rot) if name in ITEMS else (1, 1)
        if flip:
            dx = KW - dx - w
        out.append({'item': name, 'x': ax + dx, 'y': ay + dy, 'w': w, 'd': d, 'rot': rot, 'var': it[4] if len(it) > 4 else None, 'design': it[5] if len(it) > 5 else None, 'raw': it})
    for ln in k.get('lines', []):
        (x1, y1), (x2, y2) = ln['from'], ln['to']
        if flip:
            x1, x2 = KW - 1 - x1, KW - 1 - x2
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                w, d = foot(ITEMS[ln['item']]['size'], ln.get('rot', 0)) if ln['item'] in ITEMS else (1, 1)
                out.append({'item': ln['item'], 'x': ax + x, 'y': ay + y, 'w': w, 'd': d, 'rot': ln.get('rot', 0), 'var': ln.get('var'), 'design': ln.get('design'), 'raw': ln})
    for pl in k.get('plants', []):
        a, b, c, d = pl['rect']
        if flip:
            a, c = KW - 1 - c, KW - 1 - a
        pat = pl.get('pattern', 'fill')
        for y in range(b, d + 1):
            for x in range(a, c + 1):
                if pat == 'checker' and (x + y) % 2 or pat == 'rows' and (y - b) % 2 or pat == 'edge' and a < x < c and b < y < d:
                    continue
                plants.append((ax + x, ay + y, pl))
    return out, plants


FLAT = {'manhole cover'}   # 上を歩ける物
ARCH = {'castle gate'}     # 第60回：まん中のアーチをくぐれる物（3×1 のまん中の1マス。出どころ https://miketendo64.com/2021/11/16/guide-how-to-obtain-castle-items-in-animal-crossing-new-horizons/ ・1つだけなので U）


def arch_open(p):
    """アーチのまん中（くぐれるマス）"""
    if p['item'] not in ARCH:
        return set()
    return {(p['x'] + 1, p['y'])} if p['w'] >= 3 else {(p['x'], p['y'] + 1)}


def walk_set(blocked, extra):
    base = road | bridge | set(slope) | plaza | front
    if SPEC.get('beach_walk'):   # 第62回（案7）：浜も歩ける（v4 の地区どうしは浜でつながる所がある。道の A* も浜を歩く）
        base |= {(x, y) for y in range(H) for x in range(W) if g(x, y) == 's'}
    return (base | extra) - blocked


def reach(walk):
    """飛行場の前の道から、同じ段どうし・坂の上の1マスと下の3マスのあいだ・橋とその岸・浜と1段目を歩いて行けるマス"""
    st = min(road, key=lambda p: abs(p[0] - 34) + abs(p[1] - 83))   # 飛行場（浜の上）を出てすぐの道
    seen = {st}; q = deque([st])
    while q:
        x, y = q.popleft()
        for dx, dy in N4:
            n = (x + dx, y + dy)
            if n in seen or n not in walk:
                continue
            ok = lv(x, y) == lv(*n) or (x, y) in bridge or n in bridge or {g(x, y), g(*n)} & {'s'} and max(lv(x, y), lv(*n)) <= 1
            if not ok and (x, y) in slope and slope.get(n) == slope[(x, y)]:
                ok = True   # 坂の中（上の1マスと下の3マス）
            if ok:
                seen.add(n); q.append(n)
    return seen


def targets():
    out = {}
    for b in LAY['buildings']:
        w, d = SIZE[b['kind']]; x0, y0 = b['at']
        cols = range(x0, x0 + w) if w % 2 == 0 else range(x0 + w // 2 - 1, x0 + w // 2 + 2)
        out['入口の前 ' + (b.get('villager') or b['kind'])] = [(x, y0 + d) for x in cols]
    for (x, y, d), ends in inc_ends:
        out[f'坂 ({x},{y},{d}) の上'] = ends[:2]; out[f'坂 ({x},{y},{d}) の下'] = ends[2:]
    for x0, y0, x1, y1 in T['bridges']:
        if x1 - x0 == 4:   # 南北の橋
            out[f'橋 ({x0},{y0}) の北'] = [(x, y0 - 1) for x in range(x0, x1)]; out[f'橋 ({x0},{y0}) の南'] = [(x, y1) for x in range(x0, x1)]
        else:
            out[f'橋 ({x0},{y0}) の西'] = [(x0 - 1, y) for y in range(y0, y1)]; out[f'橋 ({x0},{y0}) の東'] = [(x1, y) for y in range(y0, y1)]
    return out


def check(props):
    errs, warns = [], []
    kits = dict(KITS)
    for pr in props:
        for kid, k in pr.get('new_kits', {}).items():
            if kid in KITS:
                errs.append(f'{pr["district"]}：キット {kid} はもうある（新しい名前にする）')
            if kid in kits and kid not in KITS:
                errs.append(f'キット {kid} が2つの案にある')
            kits[kid] = k
    # 1. キットの中身
    for kid, k in kits.items():
        if kid in KITS:
            continue
        KW, KD = k['size']
        for key in ('name', 'size', 'items'):
            if key not in k:
                errs.append(f'キット {kid}：{key} がない')
        out, plants = kit_cells(k, 0, 0, False)
        occ = {}
        for p in out:
            it = ITEMS.get(p['item'])
            if not it:
                near = [n for n in ITEMS if p['item'].split()[-1].lower() in n.lower()][:6]
                errs.append(f"キット {kid}：「{p['item']}」は目録にない（近い名前：{'・'.join(near)}）"); continue
            if not it.get('place', True):
                errs.append(f"キット {kid}：{p['item']}（{it['sheet']}）は外の地面に置けない")
            if p['rot'] not in (0, 1, 2, 3):
                errs.append(f"キット {kid}：{p['item']} の向き {p['rot']}（0〜3）")
            if p['var'] and p['var'] not in [v[0] for v in it['vars']]:
                errs.append(f"キット {kid}：{p['item']} に「{p['var']}」の色はない（{'・'.join(v[0] for v in it['vars']) or '色えらびなし'}）")
            if p['design'] and not (it['custom'] or p['item'] in DESIGN_ITEMS):
                errs.append(f"キット {kid}：{p['item']} にはマイデザインを貼れない")
            if p['design'] and p['design'] not in DESIGNS:
                errs.append(f"キット {kid}：マイデザイン「{p['design']}」は designs/catalog.json にない（MA コードのある本物だけ。{'・'.join(DESIGNS)}）")
            if p['x'] < 0 or p['y'] < 0 or p['x'] + p['w'] > KW or p['y'] + p['d'] > KD:
                errs.append(f"キット {kid}：{p['item']} ({p['x']},{p['y']}) 大きさ {p['w']}×{p['d']} がキットの {KW}×{KD} からはみ出す")
            for y in range(p['y'], p['y'] + p['d']):
                for x in range(p['x'], p['x'] + p['w']):
                    if (x, y) in occ:
                        errs.append(f"キット {kid}：{p['item']} ({p['x']},{p['y']}) と {occ[(x, y)]} が ({x},{y}) で重なる")
                    occ[(x, y)] = p['item']
        for x, y, pl in plants:
            if pl['type'] not in FLOWERS:
                errs.append(f"キット {kid}：花 {pl['type']} はゲームにない（{'・'.join(FLOWERS)}）"); break
            if (x, y) in occ:
                errs.append(f"キット {kid}：花 ({x},{y}) が {occ[(x, y)]} と重なる")
            if not (0 <= x < KW and 0 <= y < KD):
                errs.append(f"キット {kid}：花 ({x},{y}) がキットからはみ出す")
    # 2〜3. 置き場所
    placed, blocked, kitarea, kit_entry = [], set(), set(), []
    taken = {}   # キットの四角＋まわり1マス
    for k in spec_kits:   # すでに spec にある見せ場（地区の案から入れたものはのぞく）
        if k.get('at') and k['kit'] in KITS and not k.get('district'):
            KW, KD = kits[k['kit']]['size']; ax, ay = k['at']
            for y in range(ay - 1, ay + KD + 1):
                for x in range(ax - 1, ax + KW + 1):
                    taken[(x, y)] = 'spec ' + k['kit']
    cells8, same8 = Counter(), Counter()
    for pr in props:
        dname = pr.get('district', '?')
        bx0, by0, bx1, by1 = DISTRICTS[dname][0] if dname in DISTRICTS else (0, 0, W - 1, H - 1)
        for i, pl in enumerate(pr.get('placements', [])):
            kid = pl.get('kit'); tag = f"{dname} #{i} {kid} {pl.get('at')}"
            if kid not in kits:
                errs.append(f'{tag}：キットがない'); continue
            k = kits[kid]; KW, KD = k['size']; ax, ay = pl['at']; flip = bool(pl.get('flip')); onr = bool(pl.get('on_road'))
            L = lv(ax, ay)
            if not (bx0 <= ax and ax + KW - 1 <= bx1 and by0 <= ay and ay + KD - 1 <= by1):
                errs.append(f'{tag}：キットの四角 x{ax}〜{ax + KW - 1}・y{ay}〜{ay + KD - 1} が地区 {dname} の x{bx0}〜{bx1}・y{by0}〜{by1} からはみ出す')
            bad = []
            for y in range(ay, ay + KD):
                for x in range(ax, ax + KW):
                    c = g(x, y)
                    why = ('水' if c == 'w' else '橋' if c == 'b' else '海・浜・岩' if c in 'Ssr' else '広場' if c == 'P' else '飛行場' if c == 'K' else
                           '坂' if (x, y) in slope else '建物 ' + bld[(x, y)] if (x, y) in bld else '入口の前' if (x, y) in front else
                           f'段がちがう（{lv(x, y)}段・キットは{L}段）' if lv(x, y) != L else
                           '道（on_road=true なら置ける）' if c == 'p' and not onr else '建物のまわり1マス（on_road=false のとき）' if (x, y) in ring_b and not onr else
                           'ほかのキット ' + taken[(x, y)] + ' の四角かまわり1マス' if (x, y) in taken else '')
                    if why:
                        bad.append(f'({x},{y}) {why}')
            if bad:
                errs.append(f'{tag}：キットの四角が置けない所にかかる：' + '・'.join(bad[:6]) + (f' ほか{len(bad) - 6}' if len(bad) > 6 else ''))
            ring = [(x, y) for x in range(ax - 1, ax + KW + 1) for y in range(ay - 1, ay + KD + 1) if not (ax <= x < ax + KW and ay <= y < ay + KD)]
            if not onr and not any(p in road and lv(*p) == L for p in ring):
                errs.append(f'{tag}：on_road=false のキットは同じ段の道に面する（まわり1マスに{L}段の道がない）')
            for p in panels:
                if ax <= p[0] < ax + KW and ay <= p[1] < ay + KD:
                    warns.append(f'{tag}：spec の崖のパネル（{panels[p]}）({p[0]},{p[1]}) を消す')
            for y in range(ay - 1, ay + KD + 1):
                for x in range(ax - 1, ax + KW + 1):
                    taken.setdefault((x, y), f'{dname} #{i} {kid}')
            # 第60回：キットの四角とまわり1マス（同じ段）は plan3_fill で先にとられ、土台の目じるし・町の木がそこに置けなくなる
            lost_marks = [f"{m[0]} ({m[1]},{m[2]})" for m in SPEC.get('landmarks', []) for mx_ in range(m[1], m[1] + foot(ITEMS[m[0]]['size'], m[3])[0]) for my_ in range(m[2], m[2] + foot(ITEMS[m[0]]['size'], m[3])[1])
                          if ax - 1 <= mx_ <= ax + KW and ay - 1 <= my_ <= ay + KD and lv(mx_, my_) == L]
            lost_trees = [f"木 ({t[0]},{t[1]})" for t in SPEC.get('street_trees', []) if ax - 1 <= t[0] <= ax + KW and ay - 1 <= t[1] <= ay + KD and lv(t[0], t[1]) == L]
            if lost_marks or lost_trees:
                (errs if SPEC.get('camera_check') else warns).append(f"{tag}：キットの四角かまわり1マスに土台の目じるし・町の木があり、置けなくなる：{'・'.join(sorted(set(lost_marks)) + lost_trees)}")
            out, plants = kit_cells(k, ax, ay, flip)
            for p in out:   # 第60回：ゲームのカメラ（南から北を見る）から見えない物（南の1〜2列に高い段・家の真裏）
                if p['item'] == 'manhole cover':
                    continue
                L0, yb = lv(p['x'], p['y']), p['y'] + p['d'] - 1
                KS = (1, 2, 3) if SPEC.get('camera_check') else (1, 2)   # 2段高い崖は3列先でも・家の屋根は3列うしろまでかくす
                CR = {(a, b) for a0, b0, a1, b1 in SPEC.get('camera_roofs', []) for a in range(a0, a1 + 1) for b in range(b0, b1 + 1)}   # 案内所・飛行場の屋根
                if any(inside(x, yb + kk) and g(x, yb + kk) not in 'wSsb' and lv(x, yb + kk) - L0 >= min(kk, 2) or ((x, yb + kk) in bld or (x, yb + kk) in CR) and (kk < 3 or lv(x, yb + kk) >= L0) for x in range(p['x'], p['x'] + p['w']) for kk in KS):
                    (errs if SPEC.get('camera_check') else warns).append(f"{tag}：{p['item']} ({p['x']},{p['y']}) はカメラから見えない（南の1〜3列に高い段か家の真裏）")
            mine = set()
            for p in out:
                for y in range(p['y'], p['y'] + p['d']):
                    for x in range(p['x'], p['x'] + p['w']):
                        if p['item'] not in FLAT and (x, y) not in arch_open(p):
                            blocked.add((x, y))
                        mine.add((x, y))
                        cells8[(x // 8, y // 8)] += 1
                same8[(p['x'] // 8, p['y'] // 8, p['item'])] += 1
            for x, y, pdef in plants:
                if g(x, y) not in '13t' and not pdef.get('fit'):
                    errs.append(f'{tag}：花 ({x},{y}) が草地でない（{g(x, y)}）。道の上なら fit:true か場所を変える')
            area = {(x, y) for y in range(ay, ay + KD) for x in range(ax, ax + KW) if land(x, y) or (x, y) in road}
            kitarea |= area
            kit_entry.append((tag, area - mine, ring))
            placed.append((tag, ax, ay, KW, KD))
    for (bx, by), n in cells8.items():
        if n > 30:
            errs.append(f'8×8 のかたまり x{bx * 8}〜{bx * 8 + 7}・y{by * 8}〜{by * 8 + 7}：見せ場の物が {n} マス（30 まで。崖のパネルや柵が後から入る）')
        elif n > 24:
            warns.append(f'8×8 のかたまり x{bx * 8}〜・y{by * 8}〜：見せ場の物が {n} マス（多め）')
    for (bx, by, it), n in same8.items():
        if n > 6 and ITEMS.get(it, {}).get('sheet') != 'Fencing':
            errs.append(f'8×8 のかたまり x{bx * 8}〜{bx * 8 + 7}・y{by * 8}〜{by * 8 + 7}：{it} が {n} 個（6 個まで）')
    # 4. 歩ける
    before = reach(walk_set(set(), set()))
    after = reach(walk_set(blocked, kitarea))
    lost = sorted(p for p in before if p not in after and p not in blocked)
    if lost:
        errs.append(f'歩けなくなる道 {len(lost)} マス（例 {lost[:8]}）。見せ場の物が通りをふさいでいる')
    for name, cs in targets().items():
        if any(c in before for c in cs) and not any(c in after for c in cs):
            errs.append(f'{name} に行けなくなる')
    for tag, free_in, ring in kit_entry:
        if not any(c in after for c in free_in) and not any(c in after for c in ring):
            errs.append(f'{tag}：キットに入る所（中のあいたマスか、まわりの歩ける道）がない')
    pinch = 0
    for (x, y) in after & road:
        if (x, y) in before:
            nb = sum((x + dx, y + dy) in after and lv(x + dx, y + dy) == lv(x, y) for dx, dy in N4)   # 段のちがう道はとなりに数えない
            nb0 = sum((x + dx, y + dy) in before and lv(x + dx, y + dy) == lv(x, y) for dx, dy in N4)
            if nb0 >= 3 and nb <= 2 and any((x + dx, y + dy) in blocked for dx, dy in N4):
                pinch += 1
    if pinch > 6:
        warns.append(f'見せ場の物で、通りが1マス幅にせばまる所が {pinch} マス（通りの幅を2マス以上のこす）')
    return errs, warns, placed, blocked, kitarea


def draw_map(box, blocked=frozenset(), kitarea=frozenset(), mark=None):
    """文字の地図。1 2 3＝その段の草地／- + #＝1・2・3段の道／~ = ^＝1・2・3段の水／B 橋／/ 坂／H 建物／f 入口の前／o 建物のまわり1マス（on_road=false のキットは不可）／
    P 広場／K 飛行場／s 浜・S 海・r 岩／@ 見せ場の物／* 見せ場の四角の中のあいたマス／a 崖のパネル（spec）"""
    x0, y0, x1, y1 = box
    lines = ['     ' + ''.join(str(x // 10 % 10) if x % 10 == 0 else ' ' for x in range(x0, x1 + 1)), '     ' + ''.join(str(x % 10) for x in range(x0, x1 + 1))]
    for y in range(y0, y1 + 1):
        row = ''
        for x in range(x0, x1 + 1):
            c, L = g(x, y), lv(x, y)
            if (x, y) in blocked: ch = '@'
            elif mark and (x, y) in mark: ch = mark[(x, y)]
            elif (x, y) in kitarea: ch = '*'
            elif (x, y) in bld: ch = 'H'
            elif (x, y) in slope: ch = '/'
            elif c == 'b': ch = 'B'
            elif (x, y) in front: ch = 'f'
            elif (x, y) in panels: ch = 'a'
            elif c == 'p': ch = '-+#'[max(L, 1) - 1]
            elif c == 'w': ch = '~=^'[max(L, 1) - 1]
            elif c in 'PKsSr': ch = c
            elif (x, y) in ring_b: ch = 'o'
            else: ch = str(max(L, 1))
            row += ch
        lines.append(f'{y:3d}  ' + row)
    return '\n'.join(lines)


def find(word):
    w = word.lower()
    hits = [(n, it) for n, it in ITEMS.items() if w in n.lower() or w in (it.get('tag') or '').lower() or w in it.get('ja', '')]
    for n, it in hits[:60]:
        print(f"{n}｜{it['ja']}｜{it['size']}｜{it['sheet']}｜tag {it.get('tag')}｜外に置ける {it.get('place', True)}｜マイデザイン {bool(it['custom']) or n in DESIGN_ITEMS}｜色 {'・'.join(v[0] for v in it['vars'][:12])}")
    print(f'{len(hits)} 件' + ('（60 件まで表示）' if len(hits) > 60 else ''))


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit()
    if a[0] == '--built':   # 組み上がった島（designs/build_plan*.json の物すべて：見せ場・崖のパネル・柵・通りの小物）で歩けるか
        sys.path.insert(0, os.path.join(ROOT, 'tools'))
        from acnh_build import expand
        blocked = {(x, y) for p in expand() if p['item'] not in FLAT for x in range(p['x'], p['x'] + p['w']) for y in range(p['y'], p['y'] + p['d']) if (x, y) not in arch_open(p)}
        kitarea = set()
        for gp in BP['groups']:
            if gp.get('kit') and gp['kit'] in KITS_ALL:
                KW, KD = KITS_ALL[gp['kit']]['size']; ax, ay = gp['at']
                kitarea |= {(x, y) for y in range(ay, ay + KD) for x in range(ax, ax + KW) if land(x, y) or (x, y) in road}
        trees = {(x, y) for y in range(H) for x in range(W) if g(x, y) == 't'}
        # ゲームのとおり：草地・浜・道・橋・坂・広場は歩ける。物・木・建物・水・崖（段ちがい）は通れない
        open_ = {(x, y) for y in range(H) for x in range(W) if g(x, y) in '13psbPt'} | set(slope)
        g0 = reach(open_ - set(bld) - trees)
        g1 = reach(open_ - set(bld) - trees - blocked)
        lost = sorted(p for p in g0 if p not in g1 and p not in blocked and p in road)
        miss = [n for n, cs in targets().items() if any(c in g0 for c in cs) and not any(c in g1 for c in cs)]
        # 道だけで：通りが物で切れていないか（草地を回れば行けても、通りとしては切れている）
        r0, r1 = reach(walk_set(set(), set())), reach(walk_set(blocked, kitarea))
        cut = sorted(p for p in r0 if p not in r1 and p not in blocked and p in road)
        out = {'lost': lost, 'unreachable': miss, 'street_cut': cut}
        if '--json' in a:
            print(json.dumps(out, ensure_ascii=False)); sys.exit()
        print(f'歩いて行けなくなる道 {len(lost)} マス（例 {lost[:10]}）・行けなくなる入口や坂や橋 {len(miss)}：{"・".join(miss)}')
        print(f'（参考）通りが物で切れて、草地を回らないと行けない道 {len(cut)} マス（例 {cut[:10]}）')
        sys.exit(1 if lost or miss else 0)
    if a[0] == '--find':
        find(' '.join(a[1:])); sys.exit()
    if a[0] == '--map':
        d = a[1] if len(a) > 1 else 'D1'
        box = DISTRICTS[d][0] if d in DISTRICTS else [int(v) for v in d.split(',')]
        x0, y0, x1, y1 = box
        print(f'{d}：{DISTRICTS.get(d, ("", ""))[1]}')
        print(draw_map([max(0, x0 - 2), max(0, y0 - 2), min(W - 1, x1 + 2), min(H - 1, y1 + 2)]))
        print(draw_map.__doc__.strip())
        sys.exit()
    files = [f for f in a if not f.startswith('--')]
    props = [json.load(open(f, encoding='utf-8')) for f in files]
    errs, warns, placed, blocked, kitarea = check(props)
    if '--map' in a:
        for pr in props:
            if pr.get('district') in DISTRICTS:
                x0, y0, x1, y1 = DISTRICTS[pr['district']][0]
                print(draw_map([max(0, x0 - 2), max(0, y0 - 2), min(W - 1, x1 + 2), min(H - 1, y1 + 2)], blocked, kitarea))
    for w in warns:
        print('注意', w)
    for e in errs:
        print('NG', e)
    print(f'見せ場 {len(placed)} 個・物のマス {len(blocked)}・NG {len(errs)}・注意 {len(warns)}')
    if '--merge' in a and not errs:   # 地区の案をまとめて designs/kits_plan4.json に（plan4_design.py が spec の kits にする）
        out = {'note': '第57回：地区ごとに設計した町の見せ場（キットと置き場所）。tools/plan4_kitcheck.py --merge で書く', 'manual_zones': 'CP', 'kits': {}, 'placements': []}
        for pr in props:
            out['kits'].update(pr.get('new_kits', {}))
            for pl in pr.get('placements', []):
                out['placements'].append(dict({k: v for k, v in pl.items() if k in ('kit', 'at', 'on_road', 'flip', 'name', 'style')}, zone=DZONE.get(pr['district'], 'C'), district=pr['district']))
        json.dump(out, open(os.path.join(ROOT, f'designs/kits_plan{PLAN}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'designs/kits_plan{PLAN}.json')
    sys.exit(1 if errs else 0)
