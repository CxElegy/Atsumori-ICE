#!/usr/bin/env python3
"""案7（第62回）：「世界旅行の島」。改造プラン v4（World Travel Island Plan v4.dc.html・island-grid-v4.json）の島を 3D の鳥瞰図に起こす。
designs/plan7_spec.json を書く。

  python3 tools/plan7_design.py && ICE_PLAN=7 SEED=6 bash tools/plan3_build.sh && ICE_PLAN=7 node tools/test_plan3.js
  ICE_PLAN=7 python3 tools/plan4_kitcheck.py --built      # 物を置いた後も歩けるか
  ICE_PLAN=7 python3 tools/terrain_rules.py               # 滝・水・河口・坂の決まり（島ぜんたい）
  python3 tools/plan7_design.py --show                    # 段の図を文字で見る

v4 の図（1マス単位）をそのまま土台にする：
  ・記号：1＝1段目・3＝上の段・t＝林・p＝道・w＝川と池・b＝橋。上の段は2段目にし、林・道・水の段はとなりの陸から決める。
  ・地区は v4 の9つ（エジプト・日本・日本庭園（中島）・アメリカの都市・ハロウィン・森林・ヨーロッパ・地中海の港・ロンドン）。さかいは v4 の多角形。
  ・施設と家は v4 の場所：役場（動かせない）・飛行場（動かせない）・博物館＝エジプト考古学博物館（台地の南東のふもと）・タヌキ商店＝バザール・
    キャンプ場（森林の南の入口）・エイブル（ヨーロッパの運河ぞい）・自宅（森の手前）・住民の家10軒（エジプト2・日本3・アメリカ1・ヨーロッパ2・港1・ロンドン1）。
  ・水は v4 の1つの水系（西の河口から南の河口まで）。
3D にするために足したこと・ゲームの決まりに合わせて直したこと（v4 は2段の平面図）：
  ・3段目は4か所だけ：ピラミッド（エジプトの台地の西）・神社の山（日本の北の奥）・森林の高台の芯・時計台の高台（ロンドンの北）。
  ・神社の下の池は2段目の池にして、南向きの滝で1段目の川へ落とす（島の滝）。
  ・飛行場は動かせない所（x29〜39・y84〜89）なので、v4 で「レンガ（9¾）」だった所は飛行場。9¾番線は v4 の説明どおり「飛行場の左の浜」に置く。
  ・橋は幅3〜5の水にしかかけられない、住民は坂と橋でしか歩かない。v4 の1マス幅の水路で切れていた所は、地続きの道か橋でつなぐ。
  ・木は島で185本まで。v4 の林のマスは、木（植えかえた大人の木）と低木の林にする。
"""
import json, os, sys
from collections import deque

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
PID = '7'
_kp = os.path.join(ROOT, f'designs/kits_plan{PID}.json')
KP = json.load(open(_kp, encoding='utf-8')) if os.path.exists(_kp) and not os.environ.get('NOKITS') else {}
V = json.load(open(os.path.join(ROOT, 'island-grid-v4.json')))
W, H = 112, 96
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
inside = lambda x, y: 0 <= x < W and 0 <= y < H


# ---------------- v4 の図を段に直す ----------------
def convert():
    T = [[0] * W for _ in range(H)]
    q = deque()
    for y in range(H):
        for x in range(W):
            if V[y][x] == '1':
                T[y][x] = 1; q.append((x, y))
            elif V[y][x] == '3':
                T[y][x] = 2; q.append((x, y))
    while q:   # 林と道の段：いちばん近い陸（1・3）の段
        x, y = q.popleft()
        for dx, dy in N4:
            a, b = x + dx, y + dy
            if inside(a, b) and V[b][a] in 'tp' and T[b][a] == 0:
                T[b][a] = T[y][x]; q.append((a, b))
    for y in range(H):
        for x in range(W):
            if V[y][x] in 'tp' and T[y][x] == 0:
                T[y][x] = 1
    # 小さな上の段（10マス未満のかたまり）は1段目にする（v4 の点のような上の段）
    seen = set()
    for y in range(H):
        for x in range(W):
            if T[y][x] == 2 and (x, y) not in seen and V[y][x] not in 'wb':
                comp, st = [], [(x, y)]; seen.add((x, y))
                while st:
                    a, b = st.pop(); comp.append((a, b))
                    for dx, dy in N4:
                        p = (a + dx, b + dy)
                        if inside(*p) and p not in seen and T[p[1]][p[0]] == 2 and V[p[1]][p[0]] not in 'wb':
                            seen.add(p); st.append(p)
                if len(comp) < 10:
                    for a, b in comp:
                        T[b][a] = 1
    C = {}
    for y in range(H):
        for x in range(W):
            c = V[y][x]
            if c in 'SsrPK':
                continue
            if c in 'wb':
                C[(x, y)] = '~'
            elif c == 'p':
                C[(x, y)] = '-' if T[y][x] == 1 else '+'
            else:
                C[(x, y)] = str(T[y][x])
    # 広すぎる道：まわり8マスがみな道のマスは地面にもどす（道の固まりを通りと街区に）
    road = {p for p, ch in C.items() if ch in '-+#'}
    for (x, y) in list(road):
        if all((x + dx, y + dy) in road or (inside(x + dx, y + dy) and V[y + dy][x + dx] == 'P') for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
            C[(x, y)] = '1' if C[(x, y)] == '-' else '2'
    return C


C = convert()


def causeways():
    """v4 の道が1〜2マスの水路で切れている所を、地続きの道（渡り道）にする（橋は幅3〜5の水にしかかけられない）"""
    made = []
    for (x, y), ch in list(C.items()):
        if ch not in '~=^':
            continue
        for dx, dy in ((1, 0), (0, 1)):
            run = [(x, y)]
            while C.get((run[-1][0] + dx, run[-1][1] + dy), '') in '~=^' and len(run) <= 2:
                run.append((run[-1][0] + dx, run[-1][1] + dy))
            a = (x - dx, y - dy); b = (run[-1][0] + dx, run[-1][1] + dy)
            if len(run) <= 2 and C.get(a, '') in '-+' and C.get(b, '') == C.get(a) and C.get((x - 2 * dx, y - 2 * dy), '') == C.get(a) and C.get((b[0] + dx, b[1] + dy), '') == C.get(a):
                if C.get((x + dy, y + dx), '') not in '~=^' or C.get((x - dy, y - dx), '') not in '~=^' or True:
                    for c in run:
                        C[c] = C[a]
                    made.append(run)
    return made


MOUTH = {(11, 37), (12, 37), (13, 38), (13, 39), (13, 40), (70, 83), (71, 83), (72, 83), (73, 83)}
MOUTH_NEAR = {(x + dx, y + dy) for x, y in MOUTH for dx in (-1, 0, 1) for dy in (-1, 0, 1)}


def land_of(x, y):   # 水をうめるときの段：となりの陸の段（いちばん多いもの）
    hs = [C[(x + dx, y + dy)] for dx, dy in N4 if C.get((x + dx, y + dy), '~') not in '~=^']
    hs = ['123'['123-+#'.index(h) % 3] for h in hs]
    return max(set(hs), key=hs.count) if hs else '1'


def tidy_water():
    """v4 の水のうち、ゲームの決まりに合わない所を直す：
    ・浜・海・岩にふれる水（河口のほか）は陸にする（水が海へ出るのは決まった河口だけ）
    ・行き止まりの1マス幅の水路（ひげ）はうめる（川のゆれの点のような水。滝・橋・道のじゃまになる）"""
    n = 0
    for _ in range(40):
        ch = 0
        for (x, y), c in list(C.items()):
            if c not in '~=^' or (x, y) in MOUTH_NEAR:
                continue
            coast = any(V[y + dy][x + dx] in 'sSr' for dx, dy in N4 if inside(x + dx, y + dy))
            wn = sum(C.get((x + dx, y + dy), '') in '~=^' or (x + dx, y + dy) in MOUTH for dx, dy in N4)
            if coast or wn <= 1:
                C[(x, y)] = land_of(x, y); ch += 1
        n += ch
        if not ch:
            break
    return n


TIDY = tidy_water()
CAUSE = causeways()
FOREST = [(x, y) for y in range(H) for x in range(W) if V[y][x] == 't']


def F(x0, y0, x1, y1, ch, only=None):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if (x, y) in C and (only is None or C[(x, y)] in only):
                C[(x, y)] = ch


def lift(x0, y0, x1, y1, h):   # 段だけ変える（道は道のまま、その段の通りに）
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            ch = C.get((x, y))
            if ch is None or ch in '~=^':
                continue
            C[(x, y)] = ('-+#' if ch in '-+#' else '123')[h - 1]


# ---------------- 水と橋（v4 の水路を、橋をかけられる幅・地続きの道に）----------------
F(25, 73, 39, 75, '~')                        # テムズ川（役場の南）：幅3にして鉄の橋（アイアンブリッジ）をかける
F(34, 76, 35, 82, '-')                        # ロンドン街道（飛行場の出口 → テムズ川の鉄の橋 → 役場前広場）
F(39, 66, 39, 67, '-')                        # 広場の東の運河（1マス幅）を地続きの道でわたる（広場 → ロンドンの町）
F(18, 44, 20, 49, '~')                        # ナイル川：エジプトの北と南をつなぐ橋の所は幅3
for y in range(74, 83):                       # 南の運河（ロンドンと地中海の港のさかい → 南の河口）を、橋をかけられる幅3のまっすぐな運河に描きなおす
    for x in range(52, 77):
        if C.get((x, y)) == '~':
            C[(x, y)] = '1'
F(52, 77, 76, 79, '~'); F(70, 80, 73, 82, '~')

# ---------------- 3D にするための段 ----------------
# v4 の上の段はふちがぎざぎざで、坂（まっすぐな崖が要る）をかけられない。v4 の形にそって、まっすぐな崖のかたまりに描きなおす。
for (x, y), ch in list(C.items()):
    if ch in '23':
        C[(x, y)] = '1'
    elif ch in '+#':
        C[(x, y)] = '-'
# エジプト：北西の台地（2段目）と、その西のピラミッド（3段目・崖を3段重ねる）
lift(13, 14, 34, 21, 2); lift(13, 22, 27, 27, 2); lift(13, 28, 25, 34, 2)
F(15, 17, 23, 25, '#')                        # 頂は砂の道（砂漠の石の台）。南の面に大きな石段
F(13, 15, 24, 28, '+', only='2')              # 第62回の審査：ピラミッドのまわりの2段目も砂の道（段々の砂のかたまりに見せる。台地のほかは乾いた草）
# 日本：北の上の段（2段目）と神社の山（3段目）。神社の下の池（2段目）から南向きの滝で1段目の川へ
for y in range(13, 26):
    for x in range(60, 71):
        if C.get((x, y)) in ('~',):
            C[(x, y)] = '1'
lift(44, 15, 65, 22, 2)
F(51, 16, 60, 18, '3')
F(62, 16, 64, 22, '=')                        # 神社の下の池（2段目）
F(62, 23, 64, 26, '~')                        # 滝の下の流れ（1段目）→ 中央の池へ
# アメリカ：都市（1段目）の南の住宅地の上の段（2段目）
lift(66, 22, 86, 28, 2)
# 森林：森の入口の川の南の高台（2段目）と芯（3段目）
lift(79, 30, 96, 37, 2)
F(88, 31, 94, 35, '3')
# ヨーロッパ：運河の南の風車の丘（2段目）
lift(67, 57, 72, 65, 2)

# ロンドン：広場の北の時計台の高台（2段目）
lift(19, 56, 29, 60, 2)
F(82, 29, 82, 29, '~')
F(63, 42, 63, 42, '1')                        # 太鼓橋（中島の北 → 神社の側）の南の岸                        # 森の入口の川（2段目の台地のあいだの谷）の1マスの渡り道はやめる（段がちがう）

# ---------------- 木と低木（v4 の林のマス）----------------
# 木は島で185本まで。v4 の林のマスから、ゲームの決まり（たて横が同じ段の陸・水や浜や崖のとなりでない）に合うマスを、
# 林ごとに市松に近い間で選ぶ。のこりの林のマスは低木（生け垣・やぶ）にする。
def tree_spots():
    lvl = lambda c: {'1': 1, '2': 2, '3': 3}.get(c, 0)
    ok = []
    for (x, y) in FOREST:
        ch = C.get((x, y))
        if ch not in ('1', '2', '3'):
            continue
        L = lvl(ch)
        if any(C.get((x + dx, y + dy)) is None or C.get((x + dx, y + dy)) in '~=^' or lvl(C.get((x + dx, y + dy), '')) not in (L, 0) or
               ((C.get((x + dx, y + dy), '') in '-+#') and False) for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
            continue
        if any(C.get((x + dx, y + dy), '') in '123' and lvl(C[(x + dx, y + dy)]) != L for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
            continue
        ok.append((x, y))
    return ok


SPOTS = tree_spots()
PRI = {'F': 0, 'H': 1, 'C': 2, 'B': 2, 'J': 3, 'A': 4, 'U': 4, 'E': 5, 'P': 5}   # 森林・ハロウィン・公園の森を先に


def zone_at(x, y):
    z = None
    for k, P_ in ZPOLY:
        ins_ = False; j = len(P_) - 1
        for i in range(len(P_)):
            (xi, yi), (xj, yj) = P_[i], P_[j]
            if (yi > y + .5) != (yj > y + .5) and x + .5 < (xj - xi) * (y + .5 - yi) / (yj - yi) + xi:
                ins_ = not ins_
            j = i
        if ins_:
            z = k
    return z


rows = None


def dump():
    return [''.join(C.get((x, y), ' ') for x in range(W)) for y in range(H)]


rows = dump()

ZPOLY = [   # v4 の地区のさかい（ふちの地区は島のふちまでのばす）
    ('C', [[0, 52], [30, 56], [34, 52], [34, 60], [58, 60], [58, 84], [54, 84], [54, 96], [0, 96]]),
    ('E', [[0, 0], [38, 0], [38, 30], [34, 34], [34, 52], [30, 56], [18, 56], [18, 84], [0, 84]]),
    ('J', [[38, 0], [66, 0], [66, 40], [62, 48], [62, 60], [34, 60], [34, 34], [38, 30]]),
    ('A', [[66, 0], [112, 0], [112, 46], [76, 46], [66, 40]]),
    ('H', [[86, 0], [112, 0], [112, 25], [86, 25]]),
    ('F', [[82, 25], [112, 25], [112, 46], [82, 46]]),
    ('U', [[66, 40], [76, 46], [112, 46], [112, 72], [76, 72], [76, 84], [58, 84], [58, 60], [62, 60], [62, 48]]),
    ('P', [[76, 72], [112, 72], [112, 96], [54, 96], [54, 84], [76, 84]]),
    ('B', [[36, 47], [45, 47], [45, 59], [36, 59]]),   # 日本庭園の竹林（中島の西の林を竹に：v4 日本 6）
    ('C', [[18, 56], [30, 56], [34, 52], [34, 60], [58, 60], [58, 84], [54, 84], [54, 96], [18, 96], [18, 84]]),
]
_cand = sorted((p for p in SPOTS if (p[0] + p[1]) % 2 == 0), key=lambda p: (PRI.get(zone_at(*p), 6), (p[0] * 7 + p[1] * 13) % 11))
TREES = [list(p) for p in _cand[:178]]
# 第62回の審査（参考図還原度）：v4 の「森林の高台（針葉樹を密に）」。高台の2段目と3段目の芯に杉を（spec の cedar_belts で鳥瞰も杉に）
def plateau_spots(x0, y0, x1, y1):
    out = []
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            ch = C.get((x, y))
            if ch not in ('2', '3') or (x + y) % 2:
                continue
            if all(C.get((x + dx, y + dy)) == ch for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                out.append([x, y])
    return out


HILL = plateau_spots(80, 30, 98, 37)
TREES = HILL + TREES
_tset = {tuple(p) for p in TREES}
BUSHES = [[x, y] for (x, y) in FOREST if (x, y) not in _tset and C.get((x, y)) in ('1', '2', '3') and (x * 3 + y) % 2 == 0]   # 第62回の審査：低木は半分に（島じゅう同じ点々にしない）
ZONE_META = {
    'E': {'name': 'エジプト', 'col': '#c79a2e', 'grass': '#b4b06a', 'pathc': '#e3cf98', 'road': 'dirt', 'inc': 'stone staircase', 'bri': 'stone bridge', 'fence': 'stone fence', 'bush': .03, 'gstyle': ['garden']},
    'J': {'name': '日本', 'col': '#c2406f', 'bush': .04},
    'A': {'name': 'アメリカの都市', 'col': '#3f7a2a', 'grass': '#9db463', 'pathc': '#8a8986', 'road': 'stone', 'inc': 'red steel staircase', 'bri': 'iron bridge', 'fence': 'country fence', 'bush': .03, 'gstyle': ['flag']},
    'H': {'name': 'ハロウィン', 'col': '#6b3fa0', 'bush': .08},
    'F': {'name': '森林', 'col': '#2d5e1e', 'bush': .1},
    'U': {'name': 'ヨーロッパ', 'col': '#2f66b3', 'grass': '#a3b968', 'pathc': '#c98f6a', 'road': 'stone', 'inc': 'stone staircase', 'bri': 'stone bridge', 'fence': 'iron-and-stone fence', 'bush': .04, 'gstyle': ['flag'], 'fields': True},
    'P': {'name': '地中海の港', 'col': '#1f86a8', 'pathc': '#d7c7ae', 'road': 'stone', 'bush': .02},
    'C': {'name': 'ロンドン', 'col': '#a8402a', 'bush': 0},
    'B': {'name': '竹林', 'col': '#7aa04a', 'bush': .05},
}

BUILD = [   # v4 の家と施設の場所（アイコンの中心 → 4×4 の家の左上）
    {'id': 'museum', 'kind': 'museum', 'near': [31, 25], 'r': 6, 'name': 'エジプト考古学博物館（台地の南東のふもと）'},
    {'id': 'nook', 'kind': 'nook', 'near': [17, 33], 'r': 6, 'name': 'タヌキ商店（エジプトのバザール）'},
    {'id': 'camp', 'kind': 'campsite', 'near': [88, 39], 'r': 6, 'name': '国立公園キャンプ場（森林の南の入口）'},
    {'id': 'able', 'kind': 'able', 'near': [73, 62], 'r': 6, 'name': 'エイブルシスターズ（ヨーロッパの運河ぞい）'},
    {'id': 'home', 'kind': 'player_house', 'near': [78, 40], 'r': 6, 'name': '自宅（森の手前）'},
    {'id': 'v1', 'kind': 'villager', 'villager': 'Ed', 'near': [22, 14], 'r': 5, 'zone': 'E'},
    {'id': 'v2', 'kind': 'villager', 'villager': 'Pecan', 'near': [24, 43], 'r': 5, 'zone': 'E'},
    {'id': 'v3', 'kind': 'villager', 'villager': 'Genji', 'near': [39, 34], 'r': 5, 'zone': 'J'},
    {'id': 'v4', 'kind': 'villager', 'villager': 'Truffles', 'near': [47, 46], 'r': 5, 'zone': 'J'},
    {'id': 'v5', 'kind': 'villager', 'villager': 'Maelle', 'near': [54, 44], 'r': 5, 'zone': 'J'},
    {'id': 'v6', 'kind': 'villager', 'villager': 'Muffy', 'near': [72, 15], 'r': 5, 'zone': 'A'},
    {'id': 'v7', 'kind': 'villager', 'villager': 'Raymond', 'near': [86, 50], 'r': 5, 'zone': 'U'},
    {'id': 'v8', 'kind': 'villager', 'villager': 'Bea', 'near': [81, 60], 'r': 5, 'zone': 'U'},
    {'id': 'v9', 'kind': 'villager', 'villager': 'Scoot', 'near': [78, 74], 'r': 5, 'zone': 'P'},
    {'id': 'v10', 'kind': 'villager', 'villager': 'Deena', 'near': [38, 64], 'r': 5, 'zone': 'C'},
]
INCL = [
    [25, 30, 'E'],    # エジプトの台地の東の石段（博物館の通り → イッテツの家・ピラミッド）
    [18, 25, 'S'],    # ピラミッドの南の面の大石段（台地 → ピラミッドの頂）
    [41, 17, 'W'],    # 日本：千本鳥居の参道の石段（西の細い道 → 北の上の段）
    [53, 18, 'S'],    # 神社の山の石段（上の段 → 神社）
    [78, 19, 'N'],    # アメリカ：都市 → 南の住宅地の上の段
    [84, 37, 'S'],    # 森林の高台（キャンプ場の北）
    [21, 60, 'S'],    # ロンドン：時計台の高台の石段（広場の北）
]
BRIDGES = [[33, 73, 37, 76],   # テムズ川の鉄の橋（ロンドン街道：飛行場 → 役場前広場）
           [18, 45, 21, 49],   # ナイルの橋（エジプトの北と南）
           [60, 77, 64, 80],   # 南の運河の橋（ロンドン → 地中海の港）
           [60, 39, 64, 42]]   # 太鼓橋（日本庭園の中島の北 → 神社の側。朱色の和風の橋）
LANDMARKS = []

DISTRICTS = {   # 見せ場を設計する地区（v4 の地区の見どころの番号どおり）。tools/plan4_kitcheck.py --map D1 で文字の地図
    'D1': {'box': [10, 13, 37, 35], 'name': 'エジプト北：ピラミッド（3段目・南の大石段）・台地・遺跡の小道・エジプト考古学博物館の前庭', 'zone': 'E'},
    'D2': {'box': [8, 36, 33, 55], 'name': 'エジプト南：バザール通り（タヌキ商店）・ナイルの船着き場（西の河口）・ナイルの橋・オアシス', 'zone': 'E'},
    'D3': {'box': [38, 13, 66, 30], 'name': '日本北：神社（3段目）・千本鳥居の参道・神社の下の池と滝・茶屋', 'zone': 'J'},
    'D4': {'box': [34, 31, 66, 60], 'name': '日本庭園（中島）：回遊の散策路と東屋・竹林・太鼓橋・住民3軒', 'zone': 'J'},
    'D5': {'box': [66, 13, 86, 21], 'name': 'アメリカの都市（ダウンタウン）：ダイナー・信号・消火栓', 'zone': 'A'},
    'D6': {'box': [66, 22, 88, 29], 'name': 'アメリカの郊外の住宅地（上の段）：白い柵の家並み', 'zone': 'A'},
    'D7': {'box': [86, 13, 101, 25], 'name': 'ハロウィン：お化けの森・かぼちゃ畑の小道', 'zone': 'H'},
    'D8': {'box': [76, 26, 101, 46], 'name': '森林：森の入口の川・針葉樹の高台・国立公園キャンプ場・自宅', 'zone': 'F'},
    'D9': {'box': [62, 40, 101, 57], 'name': 'ヨーロッパ北：パリの広場（カフェテラス・花のアーチ）・ヴェネツィアの運河', 'zone': 'U'},
    'D10': {'box': [58, 56, 90, 76], 'name': 'ヨーロッパ南：風車の丘（チューリップ）・エイブル・南の運河の石畳の散歩道', 'zone': 'U'},
    'D11': {'box': [74, 72, 110, 92], 'name': '地中海の港：白い家並み・南の河口の船着き場と魚市場・ビーチクラブ・桟橋', 'zone': 'P'},
    'D12': {'box': [8, 52, 40, 83], 'name': 'ロンドン西：役場前広場（トラファルガー広場風）・時計台の高台・公園の森', 'zone': 'C'},
    'D13': {'box': [38, 60, 60, 84], 'name': 'ロンドン東：ロンドン街道・テムズ川の鉄の橋・町', 'zone': 'C'},
    'D14': {'box': [14, 82, 28, 92], 'name': '9¾番線（飛行場の左の浜）：城壁・城門・汽車', 'zone': 'C'},
}

spec = {
    'note': '案7（第62回）：世界旅行の島（改造プラン v4 の島を 3D に）。tools/plan7_design.py が書く',
    'base': 'authored', 'seed': 6, 'start': [34, 82],
    'draw': [{'canvas': {'x0': 0, 'y0': 0, 'rows': rows}, 'why': 'v4 の島を1マスずつ（上の段は2段目、3段目は4か所）'}],
    'water': [], 'edits': [], 'bridge_sites': [], 'incline_sites': [],
    'inclines': INCL, 'buildings': BUILD, 'streets': [],
    'routes': [{'name': b['id'], 'to': b['id']} for b in BUILD],
    'bridges': BRIDGES,
    'zones': [{'zone': z, 'poly': p} for z, p in ZPOLY],
    'zone_meta': ZONE_META,
    'urban': 'C',
    'prune_streets': True, 'trees_off_roads': True, 'beach_walk': True,
    'axis_paving': {'style': 'brick', 'rects': [[34, 76, 35, 82]]},   # ロンドン街道はレンガの道（v4：レンガ道・街灯・電話ボックス）
    'manual_zones': '',
    'kits': [{k: v for k, v in p.items() if k in ('kit', 'at', 'zone', 'on_road', 'flip', 'name', 'style', 'district')} for p in KP.get('placements', [])],
    'groves': {k: [0, 0] for k in 'CEJAHFUPBS'},
    'auto_kits': {k: [] for k in 'CEJAHFUPBS'},
    'camera_check': True,
    'camera_roofs': [[28, 62, 33, 65], [29, 84, 39, 89]],
    'street_trees': TREES, 'bushes': BUSHES,
    'cedar_belts': [[80, 30, 98, 37]],   # 森林の高台は杉（針葉樹）
    'landmarks': LANDMARKS,
    'districts': DISTRICTS,
    'bridge_kinds': {'33,73': 'iron bridge', '18,45': 'stone bridge', '60,77': 'brick bridge', '60,39': 'red zen bridge', '33,38': 'zen bridge'},
    'incline_kinds': {'25,30': 'stone staircase', '18,25': 'stone staircase', '41,17': 'stone staircase', '53,18': 'stone staircase',
                      '78,19': 'red steel staircase', '84,37': 'log staircase', '21,60': 'brick staircase'},
    'paths': {'C': {'kind': 'custom', 'design': 'stone_old'}, 'E': {'kind': 'game', 'name': 'sand path'}, 'A': {'kind': 'custom', 'design': 'road_suburban'},
              'U': {'kind': 'game', 'name': 'terra-cotta path'}, 'P': {'kind': 'game', 'name': 'arched tile path'}, 'J': {'kind': 'game', 'name': 'stone path'},
              'B': {'kind': 'game', 'name': 'stone path'}, 'F': {'kind': 'game', 'name': 'dark dirt path'}, 'H': {'kind': 'game', 'name': 'dark dirt path'}},
    'street_tree_tones': ['#7d9152', '#6f8c4c', '#86994f', '#768f4e'],   # 夏の緑（広葉樹は島じゅう同じ緑）
    'season': '夏。広葉樹は緑（ハロウィンの家具は10月に集めておく）',
    'page': {'title': 'アイス島 案7', 'ribbon': 'アイス島　案7', 'small': '世界旅行の島：改造プラン v4 の島を 3D に',
             'who': 'アイス島　全島（案7・第62回）', 'intro': '改造プラン v4 の「世界旅行ができる島」を、あつ森で作れる 3D の島に起こした。'},
}
json.dump(spec, open(os.path.join(ROOT, f'designs/plan{PID}_spec.json'), 'w'), ensure_ascii=False, indent=1)
_bp = os.path.join(ROOT, f'designs/build_plan{PID}.json')
if not os.path.exists(_bp):
    json.dump({'buildings': [], 'groups': [], 'inclines': {}, 'bridges': {}}, open(_bp, 'w'))
print(f'designs/plan{PID}_spec.json')
if __name__ == '__main__' and '--show' in sys.argv:
    print('    ' + ''.join(str(x // 10 % 10) if x % 10 == 0 else ' ' for x in range(W)))
    print('    ' + ''.join(str(x % 10) for x in range(W)))
    for j, r in enumerate(rows):
        if 6 <= j <= 91:
            print('%2d  %s' % (j, r))
