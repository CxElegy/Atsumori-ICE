"""集めた作例（designs/refs.json）を広げて、用途で分類する。

  python tools/collect_refs.py              # 分類（cat）だけつけ直す
  python tools/collect_refs.py --search     # 下の検索語で Pinterest を探して、新しい画像を R- の続きの番号で足す
  python tools/collect_refs.py --cache DIR  # まだ置き場にない画像を DIR に落とす（index.json と 000.jpg…、build_site.py の --cache 用）
  python tools/collect_refs.py --cache DIR --dedupe  # 置き場の画像で重複を探し、重複に dup: 残す番号 をつける

  一度つけた番号は変えない。採用・不採用（verdict）・用途（use）・作者ID（ma）はそのまま残す。
"""
import argparse, json, os, sys, time, urllib.parse, urllib.request
ROOT = os.path.join(os.path.dirname(__file__), '..')
REFS = os.path.join(ROOT, 'designs', 'refs.json')

# 用途の分類（ビルドガイドの「集めた作例」の絞りこみ。並びはこの順）
CATS = {'road': '道・地面', 'street': '街並み・島全体', 'shop': 'お店・屋台', 'park': '公園・広場・庭', 'water': '水辺・橋・浜',
        'landmark': '名所・建造物', 'station': '駅・空港・旅', 'facility': '島の施設の前', 'small': '道ばたの小物', 'design': 'マイデザイン（いろいろ）'}

# これまでの検索語の分類
OLD = {
    'acnh london path code': 'road', 'acnh cobblestone path code': 'road', 'acnh brick path code': 'road', 'あつ森 石畳 マイデザイン': 'road',
    'acnh japanese stone path code': 'road', 'あつ森 和風 マイデザイン 道': 'road', 'acnh road asphalt design code': 'road', 'acnh desert island ideas sand path code': 'road',
    'acnh london street ideas': 'street', 'acnh european town ideas': 'street', 'acnh new york city build': 'street', 'acnh mediterranean island ideas': 'street',
    'acnh spooky forest graveyard ideas': 'street', 'あつ森 空港前 レンガ 街並み': 'street',
    'acnh british pub design code': 'shop', 'acnh american diner design code': 'shop', 'acnh bazaar market stall design code': 'shop', 'acnh tea house japanese': 'shop',
    'acnh paris cafe design code': 'shop', 'acnh afternoon tea outdoor ideas': 'shop',
    'acnh hyde park garden ideas': 'park', 'acnh japanese zen garden ideas': 'park', 'あつ森 枯山水': 'park', 'acnh windmill flower field ideas': 'park',
    'acnh flower field hybrid ideas': 'park', 'acnh orchard ideas': 'park', 'acnh farm vegetable garden ideas': 'park', 'acnh campsite national park ideas': 'park',
    'acnh canal bridge ideas': 'water', 'acnh fishing dock pier ideas': 'water', 'acnh beach club ideas': 'water', 'acnh waterfall cliff ideas': 'water',
    'acnh pyramid sphinx build': 'landmark', 'acnh shrine torii build': 'landmark', 'acnh eiffel tower build': 'landmark', 'acnh harry potter island ideas': 'landmark',
    'acnh platform 9 3/4 design code': 'landmark', 'acnh quarry ideas': 'landmark',
    'acnh victorian train station waiting room': 'station', 'acnh luggage suitcase travel display': 'station', 'acnh travel agency ideas': 'station',
    'acnh airport lounge design': 'station', 'acnh european airport entrance cobblestone': 'station', 'あつ森 空港前 ラウンジ レイアウト': 'station',
    'acnh departure board design code': 'station', 'acnh kings cross station': 'station', 'acnh vintage airport ideas': 'station', 'acnh airport entrance ideas': 'station',
    'acnh london airport entrance': 'station',
    "acnh nook's cranny entrance ideas": 'facility', 'acnh resident services plaza ideas': 'facility', 'acnh museum entrance ideas': 'facility', 'acnh able sisters entrance ideas': 'facility',
    'acnh red telephone box design code': 'small', 'acnh taxi bus stop ideas': 'small',
    'acnh london design code': 'design', 'acnh british design code': 'design', 'あつ森 ロンドン マイデザイン': 'design', 'acnh egyptian design code': 'design',
    'あつ森 エジプト マイデザイン': 'design', 'acnh halloween design code': 'design', 'acnh santorini white blue design code': 'design', 'acnh simple panel design code': 'design',
}

# 広げる検索語（地区, 分類, 検索語）。少なかった地区と分類を中心に
NEW = [
    ('lon', 'landmark', 'acnh big ben build'), ('lon', 'water', 'acnh london bridge build'), ('lon', 'park', 'acnh english cottage garden ideas'),
    ('lon', 'shop', 'acnh london market stall ideas'), ('lon', 'small', 'acnh victorian street lamp ideas'), ('lon', 'small', 'acnh double decker bus build'),
    ('lon', 'street', 'acnh victorian town ideas'),
    ('egy', 'landmark', 'acnh egyptian temple ideas'), ('egy', 'water', 'acnh oasis palm tree ideas'), ('egy', 'landmark', 'acnh desert ruins ideas'),
    ('egy', 'street', 'acnh desert village ideas'), ('egy', 'shop', 'acnh arabian market rug ideas'),
    ('jpn', 'street', 'acnh japanese street ideas'), ('jpn', 'shop', 'acnh japanese food stall yatai'), ('jpn', 'park', 'acnh bamboo forest ideas'),
    ('jpn', 'water', 'acnh japanese bridge pond ideas'), ('jpn', 'landmark', 'acnh onsen hot spring ideas'), ('jpn', 'road', 'acnh cherry blossom path ideas'),
    ('jpn', 'street', 'あつ森 和風 街並み'),
    ('usa', 'shop', 'acnh gas station route 66'), ('usa', 'landmark', 'acnh times square build'), ('usa', 'street', 'acnh suburban neighborhood ideas'),
    ('usa', 'small', 'acnh street sign design code'), ('usa', 'shop', 'acnh food truck ideas'),
    ('hal', 'landmark', 'acnh haunted house ideas'), ('hal', 'park', 'acnh pumpkin patch ideas'), ('hal', 'shop', 'acnh witch market ideas'),
    ('eur', 'park', 'acnh italian piazza fountain ideas'), ('eur', 'shop', 'acnh christmas market ideas'), ('eur', 'landmark', 'acnh castle build ideas'),
    ('eur', 'water', 'acnh dutch canal house ideas'), ('eur', 'shop', 'acnh flower shop stall ideas'), ('eur', 'road', 'acnh european stone path code'),
    ('port', 'street', 'acnh greek island ideas'), ('port', 'landmark', 'acnh lighthouse ideas'), ('port', 'water', 'acnh harbor boat dock ideas'),
    ('port', 'street', 'acnh italian riviera lemon ideas'), ('port', 'shop', 'acnh fish market stall ideas'), ('port', 'road', 'acnh mediterranean tile path code'),
    ('port', 'water', 'acnh beach umbrella sunbed ideas'),
    ('all', 'small', 'acnh bench seating area ideas'), ('all', 'small', 'acnh street lamp path ideas'), ('all', 'facility', 'acnh island entrance ideas'),
    ('all', 'park', 'acnh plaza layout ideas'), ('all', 'water', 'acnh river bridge ideas'), ('all', 'road', 'acnh incline slope ideas'),
    ('all', 'road', 'acnh cliff stairs ideas'), ('all', 'facility', 'acnh house front yard ideas'),
]

def search(q, n=25):
    data = json.dumps({'options': {'query': q, 'scope': 'pins', 'page_size': n}, 'context': {}})
    url = 'https://www.pinterest.com/resource/BaseSearchResource/get/?' + urllib.parse.urlencode({'source_url': '/search/pins/?q=' + q, 'data': data})
    req = urllib.request.Request(url, headers={'Accept': 'application/json', 'X-Pinterest-PWS-Handler': 'www/search/[scope].js', 'User-Agent': 'Mozilla/5.0'})
    res = json.load(urllib.request.urlopen(req, timeout=30))['resource_response']['data']['results']
    out = []
    for r in res:
        u = ((r.get('images') or {}).get('736x') or {}).get('url')
        if u: out.append((u, (r.get('grid_title') or r.get('title') or '').strip()))
    return out

def img_hashes(path):
    """pHash（全体・まん中）と dHash。あつ森のマイデザイン保存画面（上がピンクの帯）は枠が同じなので見分ける"""
    import numpy as np
    from PIL import Image
    def dct2(a):
        k = np.arange(a.shape[0]); c = np.cos(np.pi * (2 * k[None, :] + 1) * k[:, None] / (2 * a.shape[0])); return c @ a @ c.T
    def ph(im):
        d = dct2(np.asarray(im.resize((32, 32), Image.LANCZOS), dtype=float))[:8, :8].flatten(); return d > np.median(d[1:])
    rgb = Image.open(path).convert('RGB'); im = rgb.convert('L'); w, h = im.size
    b = np.asarray(im.resize((9, 8), Image.LANCZOS), dtype=float)
    t = np.asarray(rgb.resize((40, 40)), dtype=float)[:3].reshape(-1, 3).mean(0)
    return ph(im), (b[:, 1:] > b[:, :-1]).flatten(), ph(im.crop((w * .25, h * .25, w * .75, h * .75))), bool(t[0] > 215 and t[1] < 205 and t[2] > 165 and t[0] - t[1] > 25)

# 見て確かめて「重複ではない」とした組（同じ作者の別のページなど）
NOT_DUP = {('R-0358', 'R-0364')}

def orb_pairs(items, files):
    """2段目（第33回）：切り抜き・拡大・枠・字幕・インスタの画面・拼図に入った同じ画像を見つける。
    色と構図の近い25枚を候補にし、ORB の特徴点を RANSAC でそろえ、重ねて4×4の区画の明るさがそろうか確かめる。
    保存画面（ピンクの帯）や、それを貼りこんだ画像は、ほぼすべての区画がそろうときだけ。opencv が無ければ飛ばす"""
    try:
        import cv2, numpy as np
    except ImportError:
        print('opencv がないので2段目（特徴点）は飛ばします'); return []
    orb = cv2.ORB_create(nfeatures=800, fastThreshold=12); bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    G, K, D, SC, SZ, GR, UI = [], [], [], [], [], [], []
    for r in items:
        im = cv2.imread(files[r['url']]); h, w = im.shape[:2]
        top = im[: max(3, h // 13)].reshape(-1, 3).mean(0)
        screen = top[2] > 215 and top[1] < 205 and top[0] > 165 and top[2] - top[1] > 25
        if screen: im = im[int(h * .2):int(h * .85), int(w * .15):int(w * .85)]
        sc = 480 / max(im.shape[:2]); im = cv2.resize(im, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA); gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([cv2.cvtColor(im, cv2.COLOR_BGR2HSV)], [0, 1, 2], None, [12, 4, 4], [0, 180, 0, 256, 0, 256]).flatten(); hist /= hist.sum() + 1e-9
        g = cv2.resize(gray, (16, 16), interpolation=cv2.INTER_AREA).astype(float).flatten(); g = (g - g.mean()) / (g.std() + 1e-6)
        G.append(np.concatenate([np.sqrt(hist) * 4, g / 16]))
        f = im.reshape(-1, 3).astype(int); bb, gg, rr = f[:, 0], f[:, 1], f[:, 2]
        UI.append(bool(((rr > 235) & (gg > 225) & (bb > 195) & (bb < 235) & (rr - bb > 12)).mean() > .12 and ((rr > 220) & (gg < 200) & (bb > 160) & (rr - gg > 35)).mean() > .02))
        kp, des = orb.detectAndCompute(gray, None)
        K.append(np.float32([k.pt for k in kp]) if kp else np.zeros((0, 2), np.float32)); D.append(des); SC.append(bool(screen)); SZ.append(gray.shape); GR.append(gray)
    Gm = np.array(G); Gm /= np.linalg.norm(Gm, axis=1, keepdims=True); sim = Gm @ Gm.T; np.fill_diagonal(sim, -1)
    def same(i, j):
        if SC[i] or SC[j] or D[i] is None or D[j] is None or len(D[i]) < 30 or len(D[j]) < 30: return False
        good = [a for a, b in (x for x in bf.knnMatch(D[i], D[j], k=2) if len(x) == 2) if a.distance < .75 * b.distance]
        if len(good) < 20: return False
        p1 = K[i][[x.queryIdx for x in good]]; p2 = K[j][[x.trainIdx for x in good]]
        H, mask = cv2.findHomography(p1, p2, cv2.RANSAC, 6.0)
        if H is None or mask.sum() < 25: return False
        pts = p1[mask.ravel() == 1]
        if np.ptp(pts[:, 0]) * np.ptp(pts[:, 1]) / (SZ[i][0] * SZ[i][1]) <= .08: return False
        (hb, wb), (ha, wa) = GR[j].shape, GR[i].shape
        try: Hi = np.linalg.inv(H)
        except np.linalg.LinAlgError: return False
        m2 = cv2.warpPerspective(np.full((ha, wa), 255, np.uint8), H, (wb, hb)) > 0; m1 = cv2.warpPerspective(np.full((hb, wb), 255, np.uint8), Hi, (wa, ha)) > 0
        if min(m2.mean(), m1.mean()) < .4: return False      # 両方の4割以上が重なる
        A = cv2.GaussianBlur(cv2.warpPerspective(GR[i], H, (wb, hb)), (5, 5), 0).astype(float); B = cv2.GaussianBlur(GR[j], (5, 5), 0).astype(float)
        ys, xs = np.nonzero(m2); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1; oks = tot = 0
        for ty in range(4):
            for tx in range(4):
                sl = (slice(y0 + (y1 - y0) * ty // 4, y0 + (y1 - y0) * (ty + 1) // 4), slice(x0 + (x1 - x0) * tx // 4, x0 + (x1 - x0) * (tx + 1) // 4)); mm = m2[sl]
                if mm.sum() < 50: continue
                a, b = A[sl][mm], B[sl][mm]; tot += 1
                oks += (abs(a.mean() - b.mean()) < 20) if (a.std() < 6 and b.std() < 6) else (((a - a.mean()) * (b - b.mean())).mean() / (a.std() * b.std() + 1e-6) > .5)
        return tot >= 8 and oks / tot >= (.94 if (UI[i] or UI[j]) else .7)
    pairs, seen = [], set()
    for i in range(len(items)):
        for j in np.argsort(-sim[i])[:25]:
            a, b = min(i, int(j)), max(i, int(j))
            if (a, b) in seen: continue
            seen.add((a, b))
            if same(a, b): pairs.append((a, b))
    print('2段目（特徴点）：', len(seen), '組を確かめ、同じ画像', len(pairs), '組')
    return pairs

def dedupe(refs, cache):
    """同じ画像（貼り直し・字幕や枠の違い・少しの切り抜き）をまとめる。番号は変えず、重複に dup: 残す番号。
    残すのは 採用 があればそれ、なければいちばん小さい番号。保存画面どうしは、ほぼ同じものだけ重複にする"""
    import numpy as np
    idx = json.load(open(os.path.join(cache, 'index.json'))); files = {t[1]: os.path.join(cache, '%03d.jpg' % t[0]) for t in idx}
    items = [r for r in refs if r['url'] in files]; H = [img_hashes(files[r['url']]) for r in items]
    P, Dh, C, SC = (np.array([h[k] for h in H]) for k in range(4)); n = len(items); parent = list(range(n))
    def find(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    nd = lambda a, b: (items[a]['no'], items[b]['no']) in NOT_DUP or (items[b]['no'], items[a]['no']) in NOT_DUP
    for i in range(n):
        dp = (P[i] != P[i + 1:]).sum(1); dd = (Dh[i] != Dh[i + 1:]).sum(1); dc = (C[i] != C[i + 1:]).sum(1)
        ok = (~SC[i] & ~SC[i + 1:] & (dc <= 6) & ((dp <= 4) | ((dp <= 8) & (dd <= 8)))) | ((dp == 0) & (dd <= 2) & (dc <= 1))
        for j in np.nonzero(ok)[0]:
            if not nd(i, i + 1 + int(j)): parent[find(i + 1 + int(j))] = find(i)
    for a, b in orb_pairs(items, files):
        if not nd(a, b): parent[find(b)] = find(a)
    groups = {}
    for i in range(n): groups.setdefault(find(i), []).append(items[i])
    for r in refs: r.pop('dup', None)
    k = 0
    for g in groups.values():
        if len(g) < 2: continue
        keep = sorted(g, key=lambda r: (r.get('verdict') != '採用', r['no']))[0]
        for r in g:
            if r is not keep: r['dup'] = keep['no']; k += 1
    print('重複', k, '枚（', sum(len(g) > 1 for g in groups.values()), 'グループ）')

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--search', action='store_true'); ap.add_argument('--cache'); ap.add_argument('--dedupe', action='store_true'); a = ap.parse_args()
    refs = json.load(open(REFS, encoding='utf8'))
    qcat = {**OLD, **{q: c for _, c, q in NEW}}
    if a.search:
        have, n0 = {r['url'] for r in refs}, len(refs)
        nxt = max(int(r['no'][2:]) for r in refs) + 1
        for th, c, q in NEW:
            if any(r['q'] == q for r in refs): continue
            try: got = search(q)
            except Exception as e: print('とれず', q, e); continue
            for u, t in got:
                if u in have: continue
                have.add(u); r = {'url': u, 'q': q, 'th': th, 'no': 'R-%04d' % nxt}; nxt += 1
                if t: r['title'] = t
                refs.append(r)
            print(q, len(got)); time.sleep(1)
        print('足した', len(refs) - n0)
    miss = sorted({r['q'] for r in refs if r['q'] not in qcat})
    if miss: sys.exit('分類のない検索語：' + '、'.join(miss))
    for r in refs: r['cat'] = qcat[r['q']]
    if a.dedupe:
        if not a.cache: sys.exit('--dedupe には --cache（画像の置き場）が要る')
        dedupe(refs, a.cache)
    with open(REFS, 'w', encoding='utf8') as f: f.write(json.dumps(refs, ensure_ascii=False, indent=0))
    print('全', len(refs), '件', {CATS[k]: sum(r['cat'] == k for r in refs) for k in CATS})
    if a.cache:
        os.makedirs(a.cache, exist_ok=True); ip = os.path.join(a.cache, 'index.json')
        idx = json.load(open(ip)) if os.path.exists(ip) else []
        got = {t[1] for t in idx}
        for r in refs:
            if r['url'] in got: continue
            k = len(idx)
            try: urllib.request.urlretrieve(r['url'], os.path.join(a.cache, '%03d.jpg' % k))
            except Exception as e: print('落とせず', r['no'], e); continue
            idx.append([k, r['url'], r['q']]); got.add(r['url'])
        json.dump(idx, open(ip, 'w')); print('置き場', len(idx), '枚')

if __name__ == '__main__':
    main()
