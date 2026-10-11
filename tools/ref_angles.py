"""角度ちがいの同じ作例の「候補」を出す（第34回）。同じ画像ではないが、同じ島の同じ所を別の位置・角度から撮ったもの。
候補（色と構図の近い30枚）→ ORB（多め）→ 基礎行列 F の RANSAC（視点が変わってもよい）で、そろう点が多く広く散らばるか。
まとめ記事の表紙（同じ帯と番号）は多くの画像とそろうので、3枚以上とそろった画像は外す。
角度ちがいは自動では決めきれないので、出た候補を見て designs/ref_angles.json の same / not に書く。

  python tools/ref_angles.py designs/refs.json <画像の置き場> <候補.json>     （約13分）
"""
import json, os, sys, time
import numpy as np, cv2
refs = json.load(open(sys.argv[1], encoding='utf8')); cache = sys.argv[2]; out = sys.argv[3]
idx = json.load(open(os.path.join(cache, 'index.json'))); files = {t[1]: os.path.join(cache, '%03d.jpg' % t[0]) for t in idx}
items = [r for r in refs if r['url'] in files and not r.get('dup')]
orb = cv2.ORB_create(nfeatures=1500, fastThreshold=10)
G, K, D, BAD, SZ = [], [], [], [], []
for r in items:
    im = cv2.imread(files[r['url']]); h, w = im.shape[:2]
    top = im[: max(3, h // 13)].reshape(-1, 3).mean(0)
    f = im.reshape(-1, 3).astype(int); bb, gg, rr = f[:, 0], f[:, 1], f[:, 2]
    ui = ((rr > 235) & (gg > 225) & (bb > 195) & (bb < 235) & (rr - bb > 12)).mean() > .12 and ((rr > 220) & (gg < 200) & (bb > 160) & (rr - gg > 35)).mean() > .02
    screen = top[2] > 215 and top[1] < 205 and top[0] > 165 and top[2] - top[1] > 25
    s = 560 / max(h, w); im = cv2.resize(im, None, fx=s, fy=s, interpolation=cv2.INTER_AREA); gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([cv2.cvtColor(im, cv2.COLOR_BGR2HSV)], [0, 1, 2], None, [12, 4, 4], [0, 180, 0, 256, 0, 256]).flatten(); hist /= hist.sum() + 1e-9
    G.append(np.sqrt(hist))
    kp, des = orb.detectAndCompute(gray, None)
    K.append(np.float32([k.pt for k in kp]) if kp else np.zeros((0, 2), np.float32)); D.append(des); BAD.append(bool(ui or screen)); SZ.append(gray.shape)
Gm = np.array(G); Gm /= np.linalg.norm(Gm, axis=1, keepdims=True); sim = Gm @ Gm.T; np.fill_diagonal(sim, -1)
bf = cv2.BFMatcher(cv2.NORM_HAMMING)
def check(i, j):
    if BAD[i] or BAD[j] or D[i] is None or D[j] is None or len(D[i]) < 80 or len(D[j]) < 80: return None
    m1 = bf.knnMatch(D[i], D[j], k=2); m2 = bf.knnMatch(D[j], D[i], k=2)
    f1 = {a.queryIdx: a.trainIdx for a, b in (x for x in m1 if len(x) == 2) if a.distance < .8 * b.distance}
    f2 = {a.queryIdx: a.trainIdx for a, b in (x for x in m2 if len(x) == 2) if a.distance < .8 * b.distance}
    cross = [(q, t) for q, t in f1.items() if f2.get(t) == q]      # 両方向で一致したものだけ
    if len(cross) < 30: return None
    p1 = K[i][[q for q, t in cross]]; p2 = K[j][[t for q, t in cross]]
    F, mask = cv2.findFundamentalMat(p1, p2, cv2.FM_RANSAC, 2.0, .99)
    if F is None or mask is None: return None
    inl = int(mask.sum()); ratio = inl / len(cross)
    a = p1[mask.ravel() == 1]; b = p2[mask.ravel() == 1]
    spa = np.ptp(a[:, 0]) * np.ptp(a[:, 1]) / (SZ[i][0] * SZ[i][1]); spb = np.ptp(b[:, 0]) * np.ptp(b[:, 1]) / (SZ[j][0] * SZ[j][1])
    # 同じ所を撮った写真なら、そろう点が多く、両方の画像の広い範囲に散らばる。小さな文字やロゴだけの一致は落とす
    if inl >= 40 and ratio >= .45 and min(spa, spb) >= .18:
        return inl, round(ratio, 2), round(float(min(spa, spb)), 2)
    return None
res = []; seen = set(); t0 = time.time()
for i in range(len(items)):
    for j in np.argsort(-sim[i])[:30]:
        a, b = min(i, int(j)), max(i, int(j))
        if (a, b) in seen: continue
        seen.add((a, b)); c = check(a, b)
        if c: res.append([items[a]['no'], items[b]['no'], *c])
import collections
deg = collections.Counter([p[0] for p in res] + [p[1] for p in res])
done = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'designs', 'ref_angles.json'), encoding='utf8'))
known = {tuple(sorted(p)) for p in done['same'] + done['not']}
res = [p for p in res if deg[p[0]] < 3 and deg[p[1]] < 3 and tuple(sorted(p[:2])) not in known]
print('組', len(seen), 'まだ見ていない角度ちがいの候補', len(res), '%.0fs' % (time.time() - t0))
json.dump(res, open(out, 'w'))
