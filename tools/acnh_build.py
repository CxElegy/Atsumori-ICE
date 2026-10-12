#!/usr/bin/env python3
"""第47回：案2の島を「あつ森の中で本当に作れるもの」だけで組み立て、作れるかを確かめる。

  python3 tools/acnh_build.py           # 点検（作れない所があれば NG と理由）
  python3 tools/acnh_build.py --json    # 点検の結果と、置く物の一覧（3D の鳥瞰図が読む）

読むもの
  designs/build_plan2.json  建物（数と大きさの決まった本物の建物）・坂と橋の種類・道・置く物（家具の名前で）
  designs/acnh_catalog.json あつ森の目録（物 1919 件・坂と橋の種類・住民 413 人。tools/acnh_catalog_export.js）
  plan2-terrain.json        地形（plan_terrain.py が作る）

あつ森の決まり（出どころは build_plan2.json の rules）
  建物：住民は10人まで。大きさ 住民の家 4×4・自宅 5×4・博物館 7×4・タヌキ商店 7×4・エイブル 5×4・キャンプ場 4×4。
        建物のまわり1マスは同じ段の平らな地面（水・崖・砂浜・坂・橋にかからない）。建物どうしは1マス以上あける。入口の前1マスは物を置かない。
  物　：目録にある名前だけ。大きさは目録のとおり（0.5 は1マスに切り上げ）。水・海・岩・橋・坂・案内所の広場・飛行場・木・建物の上には置けない。
        物どうしは重ならない。1つの物は同じ段の上だけ（崖をまたがない）。
  木　：縦横にとなり合わない（ななめはよい）。ヤシの木は砂浜だけ。
  花　：ゲームの花8種類と作物6種類（rules.plants）。草地だけ（道・家具・木・建物の上は不可）。
  坂・橋：それぞれ8本まで（ver 2.0 の建設ライセンスの追加で10本）。種類は目録の8種類から。
  マイデザイン：地面（道）と、模様を変えられる家具（シンプルなパネル・顔出し看板・かさ など）だけ。崖の面・水の面には貼れない。
"""
import json, math, os, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding='utf-8'))
CAT = J('designs/acnh_catalog.json')
ITEMS, CONS, VILL = CAT['items'], CAT['construction'], CAT['villagers']
T = J('plan2-terrain.json')
G, H = T['grid'], T['h']
GR = T.get('ground', {})
B = J('designs/build_plan2.json')
MW, MH = len(G[0]), len(G)
inside = lambda x, y: 0 <= x < MW and 0 <= y < MH
g = lambda x, y: G[y][x] if inside(x, y) else 'S'
lv = lambda x, y: int(H[y][x]) if inside(x, y) else 0

SIZE = {'villager': (4, 4), 'player_house': (5, 4), 'museum': (7, 4), 'nook': (7, 4), 'able': (5, 4), 'campsite': (4, 4)}
COUNT = {'villager': 10, 'player_house': 8, 'museum': 1, 'nook': 1, 'able': 1, 'campsite': 1}

slope = set()
for x, y, d in T['inclines']:
    slope.update([(x + i, y + j) for i in range(2) for j in range(4)] if d in 'NS' else [(x + i, y + j) for i in range(4) for j in range(2)])


def foot(size, rot):
    a, b = [max(1, math.ceil(float(v) - 1e-9)) for v in size.split('x')]
    return (b, a) if rot in (1, 3) else (a, b)


def expand():
    """build_plan2.json の groups（物の組）と lines（柵や街灯の列）を、1つずつの物に開く"""
    out = []
    for gp in B['groups']:
        ax, ay = gp.get('at', [0, 0])
        for it in gp.get('items', []):
            name, dx, dy = it[0], it[1], it[2]
            rot = it[3] if len(it) > 3 else 0
            var = it[4] if len(it) > 4 else None
            des = it[5] if len(it) > 5 else None
            out.append({'item': name, 'x': ax + dx, 'y': ay + dy, 'rot': rot, 'var': var, 'design': des, 'group': gp['id']})
        for ln in gp.get('lines', []):
            (x1, y1), (x2, y2) = ln['from'], ln['to']
            step = ln.get('step', 1)
            n = max(abs(x2 - x1), abs(y2 - y1))
            sx, sy = (x2 > x1) - (x2 < x1), (y2 > y1) - (y2 < y1)
            skip = {tuple(p) for p in ln.get('skip', [])}
            for i in range(0, n + 1, step):
                x, y = ax + x1 + sx * i, ay + y1 + sy * i
                if (x - ax, y - ay) in skip:
                    continue
                out.append({'item': ln['item'], 'x': x, 'y': y, 'rot': ln.get('rot', 0), 'var': ln.get('var'), 'design': ln.get('design'), 'group': gp['id']})
    for p in out:
        it = ITEMS.get(p['item'])
        p['w'], p['d'] = foot(it['size'] or '1x1', p['rot']) if it else (1, 1)
    return out


def expand_plants():
    """plants（花畑・作物）を1マスずつに開く。pattern：fill（全部）・checker（市松）・rows（1列おき）・edge（ふちだけ）"""
    out = []
    for pl in B.get('plants', []):
        x0, y0, x1, y1 = pl['rect']
        skip = {tuple(p) for p in pl.get('skip', [])}
        pat = pl.get('pattern', 'fill')
        cs = pl.get('colors', ['red'])
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if (x, y) in skip:
                    continue
                if pat == 'checker' and (x + y) % 2:
                    continue
                if pat == 'rows' and (y - y0) % 2:
                    continue
                if pat == 'edge' and x0 < x < x1 and y0 < y < y1:
                    continue
                out.append({'id': pl['id'], 'type': pl['type'], 'x': x, 'y': y, 'color': cs[(x * 3 + y * 5) % len(cs)] if pat != 'rows' else cs[((y - y0) // 2) % len(cs)]})
    return out


def check():
    errs, warn = [], []
    bad = lambda m: errs.append(m)
    # 1. 建物
    bl = B['buildings']
    cnt = Counter(b['kind'] for b in bl)
    for k, n in COUNT.items():
        if cnt[k] > n:
            bad(f'建物：{k} が {cnt[k]} 軒（{n} まで）')
    for k in ('museum', 'nook', 'able', 'campsite'):
        if cnt[k] != 1:
            warn.append(f'建物：{k} がない')
    occ_b, front = {}, set()
    for b in bl:
        if b.get('fixed'):
            continue
        w, d = SIZE[b['kind']]
        x0, y0 = b['at']
        if b['kind'] == 'villager' and b.get('villager') not in VILL:
            bad(f"建物 {b['id']}：住民 {b.get('villager')} は目録にない")
        L = lv(x0, y0)
        for y in range(y0 - 1, y0 + d + 1):
            for x in range(x0 - 1, x0 + w + 1):
                inner = x0 <= x < x0 + w and y0 <= y < y0 + d
                c = g(x, y)
                if lv(x, y) != L or c in 'wSsrbPK' or (x, y) in slope:
                    bad(f"建物 {b['id']}（{b.get('villager') or b['kind']}）：まわり ({x},{y}) が {c}・{lv(x, y)}段（同じ段の平地が要る）"); break
                if inner and c in 'tp':
                    bad(f"建物 {b['id']}：({x},{y}) に {'木' if c == 't' else '道'}がある（ぬく）")
                if inner and (x, y) in occ_b:
                    bad(f"建物 {b['id']} と {occ_b[(x, y)]} が重なる")
        for y in range(y0, y0 + d):
            for x in range(x0, x0 + w):
                occ_b[(x, y)] = b['id']
        door = x0 + w // 2 - (1 if w % 2 == 0 else 0)
        front.update({(door, y0 + d), (door + 1, y0 + d)} if w % 2 == 0 else {(door, y0 + d)})
    ids = [b for b in bl if not b.get('fixed')]
    for i, a in enumerate(ids):   # 建物どうしは1マスあける
        for c in ids[i + 1:]:
            (ax, ay), (cx, cy) = a['at'], c['at']
            aw, ad = SIZE[a['kind']]; cw, cd = SIZE[c['kind']]
            if ax - 1 < cx + cw and cx - 1 < ax + aw and ay - 1 < cy + cd and cy - 1 < ay + ad:
                bad(f"建物 {a['id']} と {c['id']} のあいだが1マスない")
    # 2. 坂と橋
    inc = B['inclines']
    if len(T['inclines']) > 10:
        bad(f"坂が {len(T['inclines'])} 本（10本まで）")
    for k, s in inc.items():
        if s not in CONS['Incline']:
            bad(f'坂 {k}：{s} という種類はない')
    have = {'%d,%d' % (x, y) for x, y, d in T['inclines']}
    if set(inc) != have:
        bad(f'坂の種類の表と地形の坂がちがう：{sorted(have ^ set(inc))}')
    for k, s in B['bridges'].items():
        if s not in CONS['Bridge']:
            bad(f'橋 {k}：{s} という種類はない')
    # 3. 物
    P = expand()
    occ, cut = {}, set()
    for p in P:
        it = ITEMS.get(p['item'])
        if not it:
            near = [n for n in ITEMS if p['item'].split()[-1] in n][:5]
            bad(f"物 {p['group']}：「{p['item']}」は目録にない（近い名前：{'・'.join(near)}）"); continue
        if p['var'] and p['var'] not in [v[0] for v in it['vars']]:
            bad(f"物 {p['group']}：{p['item']} に「{p['var']}」の色はない（{'・'.join(v[0] for v in it['vars'])}）")
        if p['design'] and not (it['custom'] or p['item'] in B['rules']['design_items']):
            bad(f"物 {p['group']}：{p['item']} にはマイデザインを貼れない")
        L = lv(p['x'], p['y'])
        for y in range(p['y'], p['y'] + p['d']):
            for x in range(p['x'], p['x'] + p['w']):
                c = g(x, y)
                if c == 't' or GR.get('%d,%d' % (x, y)) == 'u':
                    cut.add((x, y))   # 物の下の木・低木はぬく（掘って別の所へ植えかえる）
                why = ('水' if c == 'w' else '海' if c == 'S' else '岩' if c == 'r' else '橋' if c == 'b' else '案内所の広場' if c == 'P' else '飛行場' if c == 'K' else
                       '坂' if (x, y) in slope else '建物' if (x, y) in occ_b else '入口の前' if (x, y) in front else
                       '崖をまたぐ' if lv(x, y) != L else '')
                if why:
                    bad(f"物 {p['group']}：{p['item']} ({p['x']},{p['y']}) が{why}にかかる ({x},{y})")
                elif (x, y) in occ:
                    bad(f"物 {p['group']}：{p['item']} ({p['x']},{p['y']}) と {occ[(x, y)]} が重なる ({x},{y})")
                occ[(x, y)] = p['item'] + ' ' + p['group']
    # 4. 花と作物（ゲームの花8種類・作物6種類。草地だけに植えられる：道・家具・木・建物の上は不可）
    FLOWERS = B['rules'].get('plants', {})
    plants = expand_plants()
    for q in plants:
        if q['type'] not in FLOWERS:
            bad(f"花 {q['id']}：{q['type']} はゲームにない"); continue
        x, y = q['x'], q['y']; c = g(x, y)
        if c not in '123' or (x, y) in occ or (x, y) in occ_b or (x, y) in slope or (x, y) in front or GR.get('%d,%d' % (x, y)) in ('u', 'm'):
            bad(f"花 {q['id']}：({x},{y}) は草地ではない（{c}）{'・家具' if (x, y) in occ else ''}{'・建物' if (x, y) in occ_b else ''}")
        occ[(x, y)] = '花 ' + q['id']
    # 5. 木
    tt = [(x, y) for y in range(MH) for x in range(MW) if g(x, y) == 't' and (x, y) not in cut]
    adj = [(x, y) for x, y in tt if g(x + 1, y) == 't' or g(x, y + 1) == 't']
    if adj:
        bad(f'木：縦横にとなり合う木が {len(adj)} か所（例 {adj[:4]}）')
    return errs, warn, P, sorted(cut), plants


if __name__ == '__main__':
    errs, warn, P, cut, plants = check()
    if '--json' in sys.argv:
        print(json.dumps({'errors': errs, 'warnings': warn, 'placements': P, 'untree': cut, 'plants': plants, 'items': len(P), 'kinds': len({p['item'] for p in P})}, ensure_ascii=False))
        sys.exit()
    for w in warn:
        print('注意', w)
    for e in errs[:80]:
        print('NG', e)
    vc = Counter(b['kind'] for b in B['buildings'])
    print(f"建物 {len(B['buildings'])}（住民の家 {vc['villager']}/10）・坂 {len(T['inclines'])}・置く物 {len(P)} 個（{len({p['item'] for p in P})} 種類）・花と作物 {len(plants)} 株・物の下でぬく木と低木 {len(cut)}・NG {len(errs)}")
    sys.exit(1 if errs else 0)
