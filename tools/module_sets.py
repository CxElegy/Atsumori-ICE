"""モジュールDBに取り込む追加セット（DECO・TINY・VIGNETTE・SITE・STEP）。標準ライブラリだけ。

  DECO     道ばたの装飾（deco_*）  役 edge
  TINY     1〜2マスの小物と地面（tiny_*）  役 filler（細い道のすき間うめ）
  VIGNETTE 小さな飾りセット56個（vig_*）  役 filler（ちがう家具2〜4種の組み合わせ）
  SITE     主役の敷地（左右対称の前庭）  役 landmark
  STEP     段差のモジュール31個（stp_*）  役 step。rows と 段 lv（0=下・1/2=上）を持つ
"""
from gen_popular_modules import SOURCES, TH

# テーマで使う家具・地面（美的センス「テーマの一貫性」の判定に使う）
THEME_ITEMS = {
    'lon': 'LTbKWAQCxYRfNEVFtcughBpqedy',   # y：郊外の市民農園
    'egy': 'PORYxqfFtSgdsuXcNholi',
    'jpn': 'GnaefFtqgpdIcuhYXmolrU',
    'usa': 'LbFNiuqxckfeHDXhtpgdYfyjl',
    'hal': 'kJzXtsefLqcgpd',
    'eur': 'LbFcMUsKxefthuqNYBpgdl',
    'port': 'uPFqxYcosthLeSpd',
}
GROUND_CH = 'BpSgdwZD=mlr'      # m=砂紋（箒目）の白砂・l=空けておくマス（木や岩のまわり）
SMALL_CH = 'LbFNiuqxnJkfeaz'      # 道路の上に置いてよい小物（Module Builder の SMALL と同じ）

# ---- DECO：道ばたの装飾 -------------------------------------------------
DECO_SPEC = {
    'lon': [('ガス灯', ['L']), ('ガス灯とベンチ', ['Lb']), ('電話ボックス', ['T']), ('鉢植え', ['q']), ('花', ['F']), ('街灯と花', ['LF']), ('ベンチ', ['bb'])],
    'egy': [('ヤシ', ['P']), ('石柱', ['O']), ('壺', ['q']), ('樽', ['x']), ('ヤシと壺', ['Pq']), ('石柱の並び', ['OO'])],
    'jpn': [('石灯籠', ['n']), ('竹', ['a']), ('生け垣', ['e']), ('灯籠と竹', ['na']), ('花', ['F']), ('灯籠の並び', ['nn'])],
    'usa': [('白い柵', ['ff']), ('街灯', ['L']), ('看板', ['i']), ('ベンチ', ['bb']), ('花と柵', ['Ff']), ('鉢植え', ['q'])],
    'hal': [('ランタン', ['J']), ('かぼちゃ', ['k']), ('墓石', ['z']), ('かぼちゃとランタン', ['kJ']), ('生け垣', ['e'])],
    'eur': [('街灯', ['L']), ('花', ['F']), ('ベンチ', ['bb']), ('街灯と花', ['LF']), ('生け垣', ['ee']), ('鉢植え', ['q'])],
    'port': [('パラソル', ['u']), ('ヤシ', ['P']), ('鉢植え', ['q']), ('樽', ['x']), ('花', ['F']), ('ヤシとパラソル', ['Pu'])],
}

def deco():
    out = []
    for th, lst in DECO_SPEC.items():
        for i, (nm, rows) in enumerate(lst, 1):
            out.append({'id': 'deco_%s_%d' % (th, i), 'th': TH[th], 'name': '道ばた：%s' % nm, 'r': rows, 'note': '道路に面した地面に3マスおきに置く', 'mat': '', 'role': 'edge'})
    return out

# ---- TINY：1〜2マスの小物と地面 --------------------------------------------
TINY_ITEMS = {
    'lon': 'FtqxLbe', 'egy': 'PqxOFtf', 'jpn': 'Ftqnae', 'usa': 'FtqxefL', 'hal': 'ktzJeqx', 'eur': 'FtqLebx', 'port': 'FqPuxot',
}
TINY_GROUND = {'lon': 'Bpg', 'egy': 'Sgd', 'jpn': 'gpd', 'usa': 'pgd', 'hal': 'pgd', 'eur': 'pBd', 'port': 'pSd'}
NM = {'F': '花', 't': '木', 'q': '鉢植え', 'x': '樽', 'L': '街灯', 'b': 'ベンチ', 'e': '生け垣', 'P': 'ヤシ', 'O': '石柱', 'f': '柵', 'n': '灯籠', 'a': '竹',
      'k': 'かぼちゃ', 'z': '墓石', 'J': 'ランタン', 'u': 'パラソル', 'o': '岩',
      'B': 'レンガ', 'p': '石畳', 'S': '砂', 'g': '砂利', 'd': 'ウッドデッキ'}

def tiny():
    out = []
    for th in TH:
        for ch in TINY_ITEMS[th]:
            out.append({'id': 'tiny_%s_%s1' % (th, ch), 'th': TH[th], 'name': 'すき間うめ：%s' % NM[ch], 'r': [ch], 'note': '1マスのすき間に', 'mat': '', 'role': 'filler'})
        its = TINY_ITEMS[th]
        for a, b in zip(its, its[1:])[:3] if False else list(zip(its, its[1:]))[:3]:
            out.append({'id': 'tiny_%s_%s%s' % (th, a, b), 'th': TH[th], 'name': 'すき間うめ：%sと%s' % (NM[a], NM[b]), 'r': [a + b], 'note': '細い2マスに2種を並べる', 'mat': '', 'role': 'filler'})
        for ch in TINY_ITEMS[th]:
            out.append({'id': 'tiny_%s_%s2' % (th, ch), 'th': TH[th], 'name': 'すき間うめ：%sを2つ' % NM[ch], 'r': [ch * 2], 'note': '細い2マスに', 'mat': '', 'role': 'filler'})
        for g in TINY_GROUND[th]:
            out.append({'id': 'tiny_%s_g%s' % (th, g), 'th': TH[th], 'name': 'すき間うめ：%sの地面' % NM[g], 'r': [g * 2, g * 2], 'note': '細いすき間を地面で埋める（小物より先に選ぶ）', 'mat': g, 'role': 'filler'})
    return out

# ---- VIGNETTE：飾りセット（8個×7テーマ=56）-----------------------------------
VIG_ITEMS = {
    'lon': ['T', 'b', 'L', 'F', 'K', 'x'], 'egy': ['P', 'x', 'q', 'O', 'R', 'X'], 'jpn': ['n', 'a', 'F', 'q', 'h', 'e'],
    'usa': ['c', 'h', 'x', 'F', 'i', 'X'], 'hal': ['k', 'J', 'z', 'X', 's', 't'], 'eur': ['c', 'h', 'F', 'L', 'b', 'u'], 'port': ['u', 'h', 'x', 'P', 'q', 'F'],
}
VIG_LAYOUT = ['a.b|.#.|c.a', 'ab.|#c#|.ba', 'a#b|#c#|b#a', '.a.|bcb|.#.', 'ab|#c', 'a.a|#b#|c.c', 'abc|###', 'a#a|bcb|###']
VIG_NAMES = {'T': '電話ボックス', 'b': 'ベンチ', 'L': '街灯', 'F': '花', 'K': '時計', 'x': '樽', 'P': 'ヤシ', 'q': '鉢植え', 'O': '石柱', 'R': '絨毯', 'X': '焚き火',
             'n': '灯籠', 'a': '竹', 'h': '椅子', 'e': '生け垣', 'c': 'テーブル', 'i': '看板', 'k': 'かぼちゃ', 'J': 'ランタン', 'z': '墓石', 's': '像', 't': '木', 'u': 'パラソル'}
VIG_GROUND = {'lon': 'B', 'egy': 'S', 'jpn': 'g', 'usa': 'p', 'hal': 'p', 'eur': 'B', 'port': 'S'}

def vignette():
    out = []
    for th in TH:
        its = VIG_ITEMS[th]
        for i in range(8):
            trio = [its[(i + j * 2) % len(its)] for j in range(3)]
            if len(set(trio)) < 3:
                trio = [its[i % len(its)], its[(i + 1) % len(its)], its[(i + 2) % len(its)]]
            lay = VIG_LAYOUT[i]
            rows = []
            for row in lay.split('|'):
                rows.append(''.join(VIG_GROUND[th] if c == '#' else ('.' if c == '.' else trio['abc'.index(c)]) for c in row))
            w = max(len(r) for r in rows)
            rows = [r.ljust(w, '.') for r in rows]
            names = '・'.join(VIG_NAMES[c] for c in trio)
            out.append({'id': 'vig_%s_%d' % (th, i + 1), 'th': TH[th], 'name': '飾りセット：%s' % names, 'r': rows,
                        'note': 'ちがう家具3種の組み合わせ。色違いでなく、置き方で多様さを出す', 'mat': VIG_GROUND[th], 'role': 'filler'})
    return out

# ---- SITE：主役の敷地 -----------------------------------------------------
def site():
    return [
        {'id': 'egy_court', 'th': 'エジプト', 'name': 'エジプト考古学博物館の前庭（スフィンクスと蓮鉢）', 'r': ['P.O.s.O.P', '.SSSSSSS.', 'S.qqqqq.S', '.SSSSSSS.', 'P.O...O.P'],
         'note': '博物館（7×4）の前に置く左右対称の前庭。石柱・スフィンクス像・蓮を浮かべた鉢・ヤシ', 'mat': 'S', 'role': 'landmark'},
        {'id': 'jpn_court', 'th': '日本', 'name': '神社の前庭（石灯籠と手水）', 'r': ['n...n...n', '.ggggggg.', 'g.nngng.g'.replace('g.nngng.g', 'g.n.U.n.g'), '.ggggggg.', 'e.......e'],
         'note': '神社の前に置く左右対称の前庭。灯籠と手水（噴水）', 'mat': 'g', 'role': 'landmark'},
        {'id': 'usa_court', 'th': 'アメリカ', 'name': '町の広場（旗と花壇）', 'r': ['L.F...F.L', '.ppppppp.', 'p.b.K.b.p', '.ppppppp.', 'F...t...F'],
         'note': 'ダウンタウンの主役の前庭。街灯と花壇、中央に時計', 'mat': 'p', 'role': 'landmark'},
        {'id': 'lon_934', 'th': 'ロンドン', 'name': '9¾番線（城壁・城門・汽車）', 'r': ['QWWAWAWAWQ', 'BBBYBBBBLB', 'bBBCCCBBxB', 'bBBBBBBBBB', 'LBBBBBBBTB'],
         'note': '城壁・城門×3・城塔×2を奥に、汽車・樽・ベンチ・電話ボックス。浜の上に置く主役', 'mat': 'B', 'role': 'landmark'},
        {'id': 'lon_court', 'th': 'ロンドン', 'name': '博物館前の前庭（旧案）', 'r': ['L.F...F.L', '.BBBBBBB.', 'B.b.K.b.B', '.BBBBBBB.', 'f.f.f.f.f'],
         'note': '博物館をエジプトへ移したので保留', 'mat': 'B', 'role': 'landmark'},
    ]

# ---- STEP：段差のモジュール（rows と段 lv）-------------------------------------
# 各テーマ：上の段の飾り・下の段の飾り・地面。形は5種（坂つき3・坂なし2）を組み合わせる
STEP_THEME = {
    'lon': ('B', 'p', 'LbT', 'Fb', ['時計台の高台', 'テラスのベンチ', '二段の花壇', '坂の上の見晴らし']),
    'egy': ('S', 'g', 'OPs', 'xq', ['神殿の基壇（アブ・シンベル風）', '砂岩の階段テラス', '遺跡の二段広場', '台地の見晴らし']),
    'jpn': ('g', 'p', 'nGa', 'Fn', ['石段の参道', '二段の枯山水', '茶屋の高床', '石垣の庭']),
    'usa': ('p', 'g', 'Lbc', 'Fx', ['丘の上のベンチ', '二段の芝生', '展望テラス', '森の高台']),
    'hal': ('p', 'g', 'kJz', 'tJ', ['墓地の丘', 'かぼちゃの段々', '魔女の高台', '枯れ木の見晴らし']),
    'eur': ('B', 'p', 'LFb', 'Ft', ['噴水のテラス', '花の階段', '風車の丘', '運河ぞいの段']),
    'port': ('S', 'p', 'uPq', 'xF', ['白い崖町のテラス', '浜への階段', '見晴らしのカフェ', '桟橋の高台']),
}
# 保留にする3つ（坂を2本使う／余りがあるとき）
STEP_RESERVE = {'jpn_5': '段々の茶畑', 'eur_5': '城下町の大階段', 'port_5': '段々のぶどう畑'}


def _step_variant(th, k):
    up, lo, up_it, lo_it, names = STEP_THEME[th]
    W, H = 7, 7
    rows = [[lo] * W for _ in range(H)]
    lv = [[0] * W for _ in range(H)]
    # 上の段：上3行
    for y in range(3):
        for x in range(W):
            rows[y][x] = up; lv[y][x] = 1
    two_slopes = False
    kind = k % 4
    if kind in (0, 3):     # 坂つき：真ん中に2×4の坂（上1・下3）
        for y in range(2, 6):
            for x in (3, 4):
                rows[y][x] = 'Z'
        for x in (3, 4):
            lv[2][x] = 1
    if kind == 1:          # 坂なし：崖だけ。上に家具を並べる
        pass
    if kind == 2:          # 左右に坂2本
        for y in range(2, 6):
            for x in (1, 2, 4, 5):
                rows[y][x] = 'Z'
        for x in (1, 2, 4, 5):
            lv[2][x] = 1
        two_slopes = True
    # 飾り：上の段に上の家具、下の段に下の家具（坂・建物の前は空ける）
    items_up, items_lo = up_it, lo_it
    for i, x in enumerate((0, 2, 4, 6)):
        if rows[0][x] == up and (kind != 1 or True):
            rows[0][x] = items_up[i % len(items_up)]
    for i, x in enumerate((0, 6)):
        rows[6][x] = items_lo[i % len(items_lo)]
    rows[3][0] = items_lo[0] if kind in (0, 3) else rows[3][0]
    return [''.join(r) for r in rows], [''.join(str(v) for v in r) for r in lv], two_slopes, names[kind]


def step():
    out = []
    n = 0
    for th in TH:
        for k in range(4):
            rows, lv, two, nm = _step_variant(th, k)
            n += 1
            out.append({'id': 'stp_%s_%d' % (th, k + 1), 'th': TH[th], 'name': '段差：%s' % nm, 'r': rows, 'lv': lv, 'note': '上の段と下の段で見せる。坂は2×4（上1・下3）', 'mat': '', 'role': 'step'})
    # 余りの3つ（保留にする）：坂を2本使う大きな階段
    for key, nm in STEP_RESERVE.items():
        th = key.split('_')[0]
        rows, lv, _, _ = _step_variant(th, 2)
        out.append({'id': 'stp_%s' % key, 'th': TH[th], 'name': '段差：%s' % nm, 'r': rows, 'lv': lv, 'note': '坂を2本使うので、坂に余りがあるときだけ', 'mat': '', 'role': 'step'})
    return out

STEP_SRC = [{'key': k, 'label': l, 'url': u} for k, (l, u) in SOURCES.items()]   # 参考ページ13件

def check_step(m):
    """段差のモジュールの点検。問題があれば文字列のリストを返す（空なら合格）。"""
    errs = []
    r, lv = m['r'], m['lv']
    H, W = len(r), len(r[0])
    if any(len(x) != W for x in r) or len(lv) != H or any(len(x) != W for x in lv):
        return ['rows と lv の大きさが違う']
    L = [[int(c) for c in row] for row in lv]
    for y in range(H):
        for x in range(W):
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if (dx or dy) and 0 <= yy < H and 0 <= xx < W and r[y][x] != '.' and r[yy][xx] != '.' and abs(L[y][x] - L[yy][xx]) > 1:
                        errs.append('となりとの段の差が2以上 (%d,%d)' % (x, y))
    # 坂：2×4 の塊が1〜2つ。下を水に向けない
    zs = [(x, y) for y in range(H) for x in range(W) if r[y][x] == 'Z']
    if len(zs) % 8:
        errs.append('坂 Z が2×4でない（%d）' % len(zs))
    if len(zs) // 8 > 2:
        errs.append('1つのモジュールに坂は2本まで')
    for x, y in zs:
        if y + 1 < H and r[y + 1][x] == 'w':
            errs.append('坂の下が水')
    # 建物・屋台・風車・温泉・噴水は1つの段に収める
    for ch in 'HYMIU':
        ls = {L[y][x] for y in range(H) for x in range(W) if r[y][x] == ch}
        if len(ls) > 1:
            errs.append('%s が2つの段にまたがる' % ch)
    # 家の入口の前2マスは同じ段
    for y in range(H):
        for x in range(W):
            if r[y][x] == 'D':
                ds = {L[y + d][x] for d in (0, 1) if y + d < H}
                if len(ds) > 1:
                    errs.append('入口の前が2つの段')
    return sorted(set(errs))

# わざとまちがえた形8種類（check_step がすべて止めることの確認用）
BAD_STEPS = [
    {'r': ['ZZ', 'ZZ', 'ZZ'], 'lv': ['11', '00', '00']},                      # 坂が2×4でない
    {'r': ['pp', 'pp'], 'lv': ['22', '00']},                                  # 段の差が2
    {'r': ['ZZ', 'ZZ', 'ZZ', 'ZZ', 'ww'], 'lv': ['11', '00', '00', '00', '00']},   # 坂の下が水
    {'r': ['YYpp', 'pppp'], 'lv': ['1000', '0000']},                          # 屋台が2つの段
    {'r': ['HH', 'HH'], 'lv': ['10', '00']},                                  # 建物が2つの段
    {'r': ['HH', 'DD', 'pp'], 'lv': ['11', '11', '00']},                                  # 入口の前が違う段
    {'r': ['ZZZZ', 'ZZZZ', 'ZZZZ', 'ZZZZ', 'ZZZZ', 'ZZZZ', 'ZZZZ', 'ZZZZ', 'ZZZZ', 'ZZZZ', 'ZZZZ', 'ZZZZ'], 'lv': ['1111'] + ['0000'] * 11},   # 坂が3本以上
    {'r': ['pp', 'pp'], 'lv': ['1', '0']},                                    # lv の大きさが違う
]

# ---- 枯山水（日本）：水を使わず、白砂の砂紋（m）と石組み（o）で山水を表す ----------------------
def karesansui():
    K = [
        ('kare_ryoanji', 'landmark', '石庭（龍安寺の見立て）', ['ee.......ee', 'emmmmmmmmme', 'emommmmmome', 'emmmmommmme', 'emmommmmmme', 'emmmmmmmome', 'eeeeeeeeeee'],
         '白砂に石を5つ組んだ石庭。塀（生け垣）の内側に、砂紋を水面の波に見立てる'),
        ('kare_tsukubai', 'support', '縁側から見る石組み', ['nmmmmn', 'mmoomm', 'mmmmmm', 'h.mm.h'], '灯籠と腰掛けから、白砂の中の二石を眺める'),
        ('kare_sanzon', 'support', '三尊石', ['mmmmmmm', 'mmmommm', 'mmooomm', 'mmmmmmm'], '大きな石を中心に左右に石を添える（三尊石組）'),
        ('kare_island', 'support', '白砂の島（亀島）', ['.mmmmm.', 'mmeoemm', 'mmeeemm', '.mmmmm.'], '苔（生け垣）の島に石を置き、まわりを渦巻きの砂紋で囲む'),
        ('kare_bridge', 'support', '枯れ流れの石橋', ['mmmmm', 'ooooo', 'mmmmm'], '枯れ流れに板石を渡す'),
        ('kare_lantern', 'support', '灯籠と白砂', ['nmm', 'mmm', 'mmo'], '小さな坪庭'),
        ('kare_bamboo', 'support', '竹垣と白砂', ['aaaaa', 'mmmmm', 'mmomm'], '竹垣を背に白砂と石'),
        ('kare_moss', 'filler', '苔と飛び石', ['eme', 'mom', 'eme'], 'すき間を苔と白砂で埋める'),
        ('kare_sand', 'filler', '白砂（砂紋）', ['mm', 'mm'], '白砂に箒目を引いた地面'),
        # 第17回：白砂ばかりにしない。苔（r）・飛び石・延段・蹲踞・茶庭・竹垣・灯籠・紅葉と桜で変化をつける
        ('niwa_moss', 'support', '苔庭と飛び石', ['rrrrr', 'rgrrr', 'rrgrr', 'rrrgr', 'rrrrr'], '苔の中に飛び石を斜めに打つ'),
        ('niwa_nobedan', 'support', '延段と石灯籠', ['nggr', 'rggr', 'rggr', 'rggn'], '切り石を敷きつめた石の小道（延段）を灯籠ではさむ'),
        ('niwa_tsukubai', 'support', '蹲踞（つくばい）', ['erre', 'rUnr', 'rgrr'], '手水鉢と灯籠、前石。苔の中の小さな水場'),
        ('niwa_roji', 'support', '茶庭（露地）', ['aaaaa', 'rgrgr', 'hYYYh', 'rrgrr'], '竹垣の内側の茶室への小道。腰掛けと飛び石'),
        ('niwa_momiji', 'support', '紅葉と苔の築山', ['rtrrt', 'rrnrr', 'trrrr'], '苔の小山に木と灯籠。季節の色を見せる'),
        ('niwa_bamboo', 'filler', '竹垣と灯籠', ['aaaa', 'rnrr', 'rrgr'], '竹垣を背に灯籠と苔'),
        ('niwa_stones', 'filler', '飛び石', ['rgr', 'grg'], '苔に飛び石を2つ'),
        ('niwa_mossbed', 'filler', '苔', ['rr', 'rr'], '苔の地面（すき間を苔で埋める）'),
        ('niwa_lantern', 'filler', '雪見灯籠と苔', ['rn', 'rr'], '小さな灯籠'),
    ]
    return [{'id': k, 'th': '日本', 'name': ('枯山水：' if k.startswith('kare') else '庭：') + nm, 'r': r, 'note': nt, 'mat': 'm' if k.startswith('kare') else 'r', 'role': role} for k, role, nm, r, nt in K]

# ---- ロンドンの郊外（第31回）：川の西岸と南西の浜の村。旧石畳（p）・生け垣（e）・白い柵（f）・花・木・畑。
#      レンガ・電話ボックス・バス停は市街だけ。住民の家はまだ決めないので建物は置かない ------------------------
def london_suburb():
    K = [
        ('sub_lon_green', 'landmark', '村の緑地（ヴィレッジ・グリーン）', ['e.t.t.e', 'eFFpFFe', '.pbNbp.', '.ppppp.', 'eFFpFFe', 'e.....e'],
         '芝生の真ん中に道しるべとベンチ。まわりを生け垣と花で囲む村の顔'),
        ('sub_lon_manor', 'landmark', '屋敷の門と並木道', ['QWWAWWQ', 'e.ppp.e', 't.ppp.t', 'e.ppp.e', 't.ppp.t'],
         '門柱（城塔）と塀の門から、並木の石畳の道がまっすぐ続く'),
        ('sub_lon_allot', 'support', '市民農園（アロットメント）', ['ffffff', 'fyyyyf', 'fppppf', 'fyyyyf', 'fbxqpf'], '柵で囲んだ小さな畑。道具の樽とベンチ'),
        ('sub_lon_cottage', 'support', 'コテージガーデン', ['eFqFe', 'FFbFF', 'FpppF', 'ee.ee'], '花を盛りに植えた庭にベンチ。生け垣の切れ目から入る'),
        ('sub_lon_lane', 'support', '生け垣の小道', ['epe', 'epe', 'tpt', 'epe', 'epe'], '両側を生け垣で囲った田舎道。ところどころに木'),
        ('sub_lon_tea', 'support', '庭のティーテーブル', ['eFtFe', '.hch.', '.ppp.', 'FFpFF'], '木陰でお茶。花の小道から入る'),
        ('sub_lon_picnic', 'support', '芝生のピクニック', ['.u.u.', 'hcRch', 'F.F.F'], '敷物とパラソルのピクニック'),
        ('sub_lon_gate', 'support', '白い柵の木戸', ['fffpff', 'FFFpFF', '..tp..'], '白い柵の木戸から小道へ。柵の前に花'),
        ('sub_lon_hedge', 'filler', '生け垣と花', ['eee', 'FFF'], '生け垣の前に花を一列'),
        ('sub_lon_stone', 'filler', '石畳と鉢植え', ['pq', 'pp'], 'すき間を旧石畳と鉢植えで埋める'),
        ('sub_lon_post', 'filler', '道しるべと生け垣', ['eNe'], '分かれ道の道しるべ'),
        ('sub_lon_grove', 'filler', '木立と花', ['t.t', 'FFF'], '木を1マスあけて並べ、根元に花'),
        ('sub_lon_deco_1', 'edge', '生け垣', ['e'], '郊外の道ばた'),
        ('sub_lon_deco_2', 'edge', '白い柵と花', ['fF'], '郊外の道ばた'),
    ]
    return [{'id': k, 'th': 'ロンドン', 'name': '郊外：' + nm, 'r': r, 'note': nt, 'mat': 'p', 'role': role} for k, role, nm, r, nt in K]

# ---- 島の暮らしの施設：自宅のそばの畑・果樹園、採石場、釣り場、花の交配畑 ----------------------
def facility():
    F = [
        ('fac_farm', 'アメリカ', '畑（野菜）', ['ffff.fffff', 'fyyyyyyyyf', 'fppppppppf', 'fyyyyyyyyf', 'fppppppppf', 'fyyyyyyyyf', 'ffffffffff'],
         'カボチャ・トマト・小麦・サトウキビ・ジャガイモ・ニンジンを列に植え、間を歩けるようにする。北の入口から'),
        ('fac_orchard', 'アメリカ', '果樹園', ['jljljlj', 'lllllll', 'jljljlj', 'lllllll', 'jljljlj'], '果物の木は1マスずつあける（まわりに物を置かない）'),
        ('fac_quarry', 'エジプト', '採石場（石切り場）', ['fffffff', 'fololof', 'flllllf', 'fololof', 'fffifff'], '岩6つが毎日出る所。柵で囲み、岩と岩の間を1マスあけてたたけるようにする'),
        ('fac_fishing', 'ロンドン', '釣り場', ['dddd', 'bddx'], '水ぎわの板張り。ベンチと道具箱'),
        ('fac_flowers', 'ヨーロッパ', '花の交配畑', ['FlFlFlF', 'lllllll', 'FlFlFlF', 'lllllll', 'FlFlFlF'], '花を市松に植えて、間をあけて交配させる'),
    ]
    return [{'id': k, 'th': th, 'name': '施設：%s' % nm, 'r': r, 'note': nt, 'mat': '', 'role': 'facility'} for k, th, nm, r, nt in F]
