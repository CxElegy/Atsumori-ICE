"""アイス島ビルドガイド（1枚の HTML）を作る。地図・モジュール・草図・作例の写真・マイデザインをまとめる。

  python tools/build_site.py --cache <画像の置き場> --out <出力.html>

  作者の画像（Pinterest）は --cache の index.json（[番号, URL, 検索語] の一覧）と 000.jpg… から読み、
  縮小して HTML に埋めこむ。作者の画像なので、出力の HTML はリポジトリに入れない。
"""
import argparse, base64, io, json, os, re, sys
from PIL import Image, ImageOps
ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.dirname(__file__))
from collect_refs import CATS
J = lambda f: json.load(open(os.path.join(ROOT, f), encoding='utf8'))

def uri(im, fmt='JPEG', q=78):
    b = io.BytesIO(); im = im.convert('RGB') if fmt == 'JPEG' else im
    im.save(b, fmt, quality=q) if fmt == 'JPEG' else im.save(b, fmt, optimize=True)
    return 'data:image/%s;base64,%s' % ('jpeg' if fmt == 'JPEG' else 'png', base64.b64encode(b.getvalue()).decode())

def fit(im, w):
    return im if im.width <= w else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)

def rotate(rows, rot):
    r = [list(s) for s in rows]
    for _ in range(rot):
        h, w = len(r), len(r[0]); r = [[r[h - 1 - x][y] for x in range(h)] for y in range(w)]
    return [''.join(s) for s in r]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--cache', required=True, nargs='+'); ap.add_argument('--out', required=True); ap.add_argument('--board'); ap.add_argument('--views'); a = ap.parse_args()
    files = {}
    for c in a.cache:
        idx = json.load(open(os.path.join(c, 'index.json')))
        for k, u in (enumerate(idx) if isinstance(idx[0], str) else ((t[0], t[1]) for t in idx)):
            files[u] = os.path.join(c, '%03d.jpg' % k)
    opened = {}
    def open_url(u):
        if u not in opened: opened[u] = Image.open(files[u]).convert('RGB')
        return opened[u]
    T, S, LON, CATD, CUR = J('plan-terrain.json'), J('samples.json'), J('designs/lon.json'), J('designs/catalog.json'), J('modules-curated.json')
    leg_src = open(os.path.join(ROOT, 'Module Builder.dc.html'), encoding='utf8').read()
    leg_txt = leg_src[leg_src.index('  LEG = {'):leg_src.index('  genAll(')]
    LEG = {k.strip("'"): [n, c, g] for k, n, c, g in re.findall(r"('[^']+'|[\w$]+): \['([^']*)', '(#[0-9a-fA-F]{6})', '([^']*)'\]", leg_txt)}
    cat = {d['id']: d for d in CATD['designs']}
    for d in cat.values():
        d['thumb'] = uri(fit(open_url(d['images'][0]), 360), q=72) if d['images'][0] in files else ''
    ex = [{**x, 'thumb': uri(fit(open_url(x['image']), 640), q=74)} for x in CATD['examples'] if x['image'] in files]
    # 地面・家具のマイデザインの図（1マス分を切り出す）
    def crop(design, img_i, box, rot=0, size=72):
        im = open_url(cat[design]['images'][img_i]); x, y, w, h = box
        return uri(im.crop((x, y, x + w, y + h)).resize((size, round(size * h / w) if w != h else size), Image.LANCZOS), q=82)
    tex, tex_items = {}, {}
    for ch, g in LON['ground'].items():
        t = g.get('tex')
        if t: tex[ch] = {'pieces': {k: crop(t.get('design', g['design']), t['img'], b) for k, b in t['pieces'].items()}, 'rot': t.get('rot', 0)}
    for ch, g in LON['items'].items():
        t = g.get('tex')
        if t: tex_items[ch] = {'pieces': [crop(g['design'], t['img'], b) for b in t['pieces']], 'run': t.get('run', False)}
    lon = {k: LON[k] for k in ('ground', 'items', 'furniture', 'design_extra')}; lon['tex'] = tex; lon['texItems'] = tex_items
    # モジュール
    meta = {m['id']: m for m in CUR['modules']}
    NAMES = {'museum': '考古学博物館', 'able': 'エイブルシスターズ', 'nook': 'タヌキ商店', 'home': '自宅', 'camp': 'キャンプ場', 'lon_lounge': '飛行機ラウンジ', 'lon_park': 'ハイドパーク',
             'lon_corner': 'ロンドンの街角', 'lon_bus': 'バス停', 'egy_dig': '発掘現場', 'egy_mkt': 'バザール', 'egy_pyramid': 'ピラミッド', 'eur_cafe': 'パリのカフェ', 'eur_eiffel': 'エッフェル塔',
             'eur_mill': '風車の丘', 'jpn_tea': '茶屋', 'jpn_torii': '千本鳥居', 'port_beach': 'ビーチクラブ', 'port_fish': '漁港', 'usa_diner': 'ダイナー'}
    meta.update({m['id']: m for m in J('tools/base-modules.json')['modules'] if m['id'] not in meta})
    mods = {}
    for mid, rows in S['defs'].items():
        mm = meta.get(mid, {})
        mods[mid] = {'name': mm.get('name') or NAMES.get(mid, mid), 'role': mm.get('role', 'landmark' if mid in NAMES else ''), 'th': mm.get('th', ''), 'note': mm.get('note', ''), 'r': rows}
    for m in LON['modules']:
        mods[m['id']] = {k: v for k, v in m.items() if k != 'id'}; mods[m['id']]['name'] = m['name'].replace('細部：', '')
        for ch, g in (m.get('itemsOv') or {}).items():
            t = g.get('tex')
            if t: mods[m['id']].setdefault('texOv', {})[ch] = {'pieces': [crop(g['design'], t['img'], b) for b in t['pieces']], 'run': t.get('run', False)}
        for r in m.get('refs', []):
            r['img'] = uri(fit(Image.open(os.path.join(ROOT, r['img'])), 900), q=80)
    for mid in ('lon_934', 'pop0007', 'pop0084'):
        if mid in mods and mid in LON.get('design_extra', {}): mods[mid]['design'] = LON['design_extra'][mid]
    # 置き場所：見本の配置。9¾番線は作例どおりの細部モジュールに入れかえ、ほかの細部モジュールはロンドンの空き地に仮に置く
    places, occ = [], set()
    for z, lst in S['dists'].items():
        for e in lst:
            mid, x, y, rot = e[0], e[1], e[2], e[3] if len(e) > 3 else 0
            if mid == 'lon_934':   # 9¾番線は作例どおりの細部モジュールにして、地形で用意したレンガの浜（空港の入口の左・入り江に面する）へ
                if any(p['id'] == 'lon_d_platform' for p in places): continue
                mid, x, y, rot = 'lon_d_platform', 29, 84, 0
            rows = rotate(mods[mid]['r'], rot)
            places.append({'id': mid, 'x': x, 'y': y, 'rot': rot, 'zone': z, 'rows': rows})
            if sum(ch != '.' for row in rows for ch in row) >= 6:   # 道ばたの小物・すき間うめは、細部モジュールを置くときに場所をゆずる
                for dy, row in enumerate(rows):
                    for dx, ch in enumerate(row):
                        if ch != '.': occ.add((x + dx, y + dy))
    G, H = T['grid'], T['h']
    def fits(rows, x, y):
        lv = H[y][x]
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                X, Y = x + dx, y + dy
                if Y >= 96 or X >= 112 or G[Y][X] not in '13ptPK' or H[Y][X] != lv: return False
                if (X, Y) in occ: return False
        return True
    optonly = {c for o in LON.get('options', []) for c in o['choices']} - {'lon_d_platform'}   # 案としてだけ使うモジュールは、ほかの所に置かない
    for m in sorted(LON['modules'], key=lambda m: not m.get('at')):   # 場所を決めたモジュールを先に
        if any(p['id'] == m['id'] for p in places) or m['id'] in optonly: continue
        if m.get('at'):   # 場所を決めたモジュール：そこに置き、重なるほかのモジュール（細部以外）は外す
            x, y = m['at']; cs = {(x + dx, y + dy) for dy, row in enumerate(m['r']) for dx, ch in enumerate(row) if ch != '.'}
            places[:] = [p for p in places if mods[p['id']].get('detail') or not any((p['x'] + dx, p['y'] + dy) in cs for dy, row in enumerate(p['rows']) for dx, ch in enumerate(row) if ch != '.')]
            places.append({'id': m['id'], 'x': x, 'y': y, 'rot': 0, 'zone': 'lon', 'rows': m['r'], 'detail': True}); occ.update(cs); continue
        done = False
        px, py = m.get('prefer', [16, 54])   # 置きたい所（河岸は川のそば）に近い順に探す
        for x, y in sorted(((x, y) for y in range(54, 92) for x in range(16, 58)), key=lambda c: abs(c[0] - px) + abs(c[1] - py)):
            if True:
                if fits(m['r'], x, y):
                    places.append({'id': m['id'], 'x': x, 'y': y, 'rot': 0, 'zone': 'lon', 'rows': m['r'], 'detail': True, 'tentative': True})
                    cells = {(x + dx, y + dy) for dy, row in enumerate(m['r']) for dx, ch in enumerate(row)}
                    places[:] = [p for p in places if p.get('detail') or not any((p['x'] + dx, p['y'] + dy) in cells for dy, row in enumerate(p['rows']) for dx, ch in enumerate(row) if ch != '.')]
                    for dy, row in enumerate(m['r']):
                        for dx, ch in enumerate(row): occ.add((x + dx, y + dy))
                    done = True; break
        if not done: print('置けない:', m['id'])
    # 家具のマスが重なる配置を直す：大事な順（細部・主役・脇役…）に置き、重なるものは近くの空きへずらす。ずらせなければ外す
    GROUNDS = set('BpSgdwZDmlr_#^=')
    pri = lambda p: (0 if mods[p['id']].get('detail') else 1 if mods[p['id']].get('role') == 'landmark' else 2 if mods[p['id']].get('role') in ('support', 'facility') else 3)
    taken, kept, moved, dropped = set(), [], 0, []
    def cells(p, x, y): return [(x + dx, y + dy) for dy, row in enumerate(p['rows']) for dx, ch in enumerate(row) if ch not in GROUNDS and ch != '.']
    def ok_at(p, x, y):
        lv = None
        for dy, row in enumerate(p['rows']):
            for dx, ch in enumerate(row):
                if ch == '.': continue
                X, Y = x + dx, y + dy
                if not (0 <= X < 112 and 0 <= Y < 96) or G[Y][X] in 'Sw': return False
                if lv is None: lv = H[Y][X]
                elif H[Y][X] != lv: return False
        return not any(c in taken for c in cells(p, x, y))
    for p in sorted(places, key=pri):
        x0, y0, spot = p['x'], p['y'], None
        if not any(c in taken for c in cells(p, x0, y0)): spot = (x0, y0)
        else:
            for r in range(1, 7):
                cand = [(x0 + dx, y0 + dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1) if max(abs(dx), abs(dy)) == r]
                spot = next((c for c in cand if ok_at(p, *c)), None)
                if spot: break
        if not spot: dropped.append(p['id']); continue
        if spot != (x0, y0): moved += 1
        p['x'], p['y'] = spot; taken.update(cells(p, *spot)); kept.append(p)
    places = kept
    print('ずらした', moved, '外した', len(dropped), dropped[:8])
    opts = {o['at']: o for o in LON.get('options', [])}
    for p in places:
        if p['id'] in opts: p['slot'] = p['id']
        if mods[p['id']].get('detail'): p['detail'] = True
        if p['id'] == 'lon_d_platform': p['short'] = '9¾番線'
    # 集めた作例：検索で見つけた画像をすべて（使っていないものも）。目録は designs/refs.json
    lib = json.load(open(os.path.join(ROOT, 'designs', 'refs.json'), encoding='utf8'))
    used = {u: d['ma'] for d in cat.values() for u in d['images']}; usedEx = {x['image']: x['name'] for x in CATD['examples']}
    refs = [{'no': r['no'], 'verdict': r.get('verdict', ''), 'note': r.get('use', ''), 'url': r['url'], 'q': r['q'], 'th': r.get('th', 'all'), 'cat': r.get('cat', ''), 'title': r.get('title', ''), 'score': r.get('score', 0), 'ma': used.get(r['url'], r.get('ma', '')), 'ocr': r['url'] not in used and bool(r.get('ma_ocr')), 'use': usedEx.get(r['url'], ''), 'thumb': uri(ImageOps.fit(open_url(r['url']), (100, 100), Image.LANCZOS, centering=(.5, .35)), q=42)} for r in lib if r['url'] in files]
    data = {'options': opts, 'refs': refs, 'refCats': CATS, 'grid': G, 'h': H, 'inclines': T.get('inclines', []), 'paint': S['paint'], 'facs': S.get('facilities', []), 'places': places, 'mods': mods, 'leg': LEG, 'lon': lon, 'cat': cat, 'examples': ex,
            'th': {'lon': 'ロンドン', 'egy': 'エジプト', 'jpn': '日本', 'usa': 'アメリカ', 'eur': 'ヨーロッパ', 'port': '地中海'},
            'thColor': {'lon': '#b4503a', 'egy': '#d9a441', 'jpn': '#c45a7a', 'usa': '#3f6fb5', 'eur': '#4f9a8a', 'port': '#2f8fc9'},
            'role': {'landmark': '主役', 'support': '脇役', 'filler': 'すき間うめ', 'edge': '道ばた', 'step': '段差', 'facility': '施設'},
            'facGlyph': {'fishing': '釣', 'home': '家', 'farm': '畑', 'orchard': '果', 'quarry': '石', 'flowers': '花'}}
    # まわりの通り道（designs/lon_paths.json）：線を幅で太らせ、地面を敷く。通り道の上の小さなモジュール（すき間うめ・道ばた）は外す
    routes = json.load(open(os.path.join(ROOT, 'designs', 'lon_paths.json'), encoding='utf8'))['routes']
    for rt in routes:
        cells = []
        for (x1, y1), (x2, y2) in zip(rt['pts'], rt['pts'][1:]):
            n = max(abs(x2 - x1), abs(y2 - y1))
            for i in range(n + 1):
                x = x1 + (x2 - x1) * i // max(n, 1); y = y1 + (y2 - y1) * i // max(n, 1)
                for dx in range(rt['w'] if y1 != y2 else 1):
                    for dy in range(rt['w'] if x1 != x2 else 1):
                        cells.append((x + dx, y + dy))
        cells = sorted(set(c for c in cells if 0 <= c[0] < 112 and 0 <= c[1] < 96 and G[c[1]][c[0]] not in 'Swrb'))
        rt['cells'] = [list(c) for c in cells]
        cs = set(cells)
        def hits(p):
            return any((p['x'] + dx, p['y'] + dy) in cs for dy, row in enumerate(p['rows']) for dx, ch in enumerate(row) if ch != '.' and ch not in GROUNDS)
        places = [p for p in places if not (hits(p) and pri(p) >= 2)]   # 坂・橋の上の小物も外す（坂の上に木や花を置かない）
        if rt['mat'] in ('bridge', 'slope'): continue
        for x, y in cells: S['paint'].setdefault('lon', {})['%d,%d' % (x, y)] = rt['mat']
    data['routes'] = routes; data['levels'] = LON.get('levels')
    data['places'] = places
    if a.board:   # 立体図（London Render）に読ませる配置
        paint = {k: v for pa in S['paint'].values() for k, v in pa.items()}
        json.dump({'placed': [{'id': 'p%d' % i, 'm': (opts[p['slot']].get('default') if p.get('slot') else None) or p['id'], 'x': p['x'], 'y': p['y'], 'rot': p['rot']} for i, p in enumerate(places)], 'paint': paint, 'dist': 'lon',
                   'defs': {k: v['r'] for k, v in mods.items()}}, open(a.board, 'w'), ensure_ascii=False)
    data['views'] = json.load(open(a.views)) if a.views and os.path.exists(a.views) else {}
    html = open(os.path.join(ROOT, 'tools', 'site', 'template.html'), encoding='utf8').read()
    js = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    tiles = open(os.path.join(ROOT, 'tools', 'design_tiles.js'), encoding='utf8').read()
    html = html.replace('/*DATA*/', js).replace('/*TILES*/', tiles)
    open(a.out, 'w', encoding='utf8').write(html)
    print('保存:', a.out, '%.1f MB' % (len(html.encode()) / 1e6), 'モジュール', len(places))

if __name__ == '__main__':
    main()
