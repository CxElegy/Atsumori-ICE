#!/usr/bin/env python3
"""人気の作例をもとにしたモジュール1000個を作る（標準ライブラリだけ）。

作例ごとのテンプレート（形）に、3つの差し替えを組み合わせて色違いを作る。
  '#' 地面（レンガ B・石畳 p・砂 S・砂利 g・ウッドデッキ d に差し替え）
  '~' 縁の飾り（なし・街灯・花・柵・ベンチ・生け垣・木・ヤシ・鉢植え・石柱・樽・灯籠・ランタン・かぼちゃ・墓石…）
  '*' アクセント小物（電話ボックス・時計・像・噴水・焚き火・鳥居・温泉・風車など）
出力: modules-popular.json（count・sources・modules）と modules-popular.md（一覧）。
  使い方: python tools/gen_popular_modules.py
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N = 1000

# 出典（作例のページ）。Module Builder の「参考にしたページ」と同じ
SOURCES = {
    'note_lon': ('ロンドンを再現した島（アズーリ島）訪問記', 'https://note.com/view_cream/n/n1908c2ceff0d'),
    'myme_lon': ('飛行場前とアンティークな時計台（マイミーボックス）', 'https://www.mymeblog.com/entry/2020/09/29/142621'),
    'eur_all': ('ヨーロッパ風の街並み・レイアウトまとめ', 'https://atsumori-mydesign.com/european-style-cityscape/'),
    'altema_eur': ('島のレイアウト一覧：ヨーロッパ風（アルテマ）', 'https://altema.jp/atsumori/osyarenashima'),
    'jpn_40': ('和風のレイアウト40選（庭園・枯山水・旅館）', 'https://annamy.com/atumori-japanese-style-layout/'),
    'jpn_shrine': ('神社風レイアウトの作り方', 'https://hibinomatome.com/entry/2021/01/06/004216'),
    'jpn_gw': ('和風の島の作り方（GameWith）', 'https://gamewith.jp/atsumori/article/show/201839'),
    'egy_mtmmo': ('砂漠の島の作例と夢番地', 'https://www.mtmmo.com/news/474--acnh-desert-island-dream-code--design-ideas--animal-crossing-desert-island-tour'),
    'egy_faqs': ('エジプト風に使える家具（GameFAQs）', 'https://gamefaqs.gamespot.com/boards/248082-animal-crossing-new-horizons/78702159'),
    'coast': ('海辺の街のアイデア15選', 'https://madfandom.com/acnh-coastal-town/'),
    'camp1': ('キャンプサイトの作例15選', 'https://madfandom.com/acnh-campsite-designs/'),
    'camp2': ('キャンプサイトのアイデア20選', 'https://www.fandomspot.com/acnh-campsite-ideas/'),
    'hal': ('ハロウィンの島のアイデア20選', 'https://www.fandomspot.com/acnh-halloween-ideas/'),
}

TH = {'lon': 'ロンドン', 'egy': 'エジプト', 'jpn': '日本', 'usa': 'アメリカ', 'hal': 'ハロウィン', 'eur': 'ヨーロッパ', 'port': '地中海'}
MAT = {'B': 'レンガ', 'p': '石畳', 'S': '砂', 'g': '砂利', 'd': 'ウッドデッキ'}
GROUNDS = {'lon': 'Bpg', 'egy': 'Sgdp', 'jpn': 'gpd', 'usa': 'pgd', 'hal': 'pgd', 'eur': 'pBgd', 'port': 'pSd'}
EDGE_NAME = {'.': 'なし', 'L': '街灯', 'F': '花', 'f': '柵', 'b': 'ベンチ', 'e': '生け垣', 't': '木', 'P': 'ヤシ', 'q': '鉢植え', 'O': '石柱',
             'x': '樽', 'n': '灯籠', 'J': 'ランタン', 'k': 'かぼちゃ', 'a': '竹', 'z': '墓石', 'u': 'パラソル'}
ACC_NAME = {'T': '電話ボックス', 'K': '時計', 's': '像', 'U': '噴水', 'X': '焚き火', 'G': '鳥居', 'I': '温泉', 'N': '道しるべ', 'E': '案内板', 'i': '看板',
            'c': 'テーブル', 'h': '椅子', 'b': 'ベンチ', 'u': 'パラソル', 'F': '花', 'q': '鉢植え', 'x': '樽', 'n': '灯籠', 'O': '石柱', 'P': 'ヤシ',
            'R': '絨毯', 'k': 'かぼちゃ', 'J': 'ランタン', 'z': '墓石', 'L': '街灯', 't': '木', 'M': '風車', 'o': '岩'}

# (base, テーマ, 役, 名前, rows, 縁の候補, アクセント候補, 説明, 出典キー)
T = [
    ('lon_clock', 'lon', 'landmark', '時計台の広場', ['~#####~', '#######', '###*###', '#######', '~#####~'], '.LFfbt', 'KsUT', '中央に主役の置物。四隅に縁の飾り', 'note_lon'),
    ('lon_corner', 'lon', 'support', '電話ボックスの角', ['*bb~', '####', '####'], '.LFt', 'TKNi', '角や建物の脇に。電話ボックス＋ベンチ', 'myme_lon'),
    ('lon_tea', 'lon', 'support', 'アフタヌーンティー', ['~hch~', '..*..', '#####'], '.LFbt', 'uFqN', '博物館前や公園の脇に1卓', 'note_lon'),
    ('lon_bus', 'lon', 'filler', 'バス停風', ['~b*b~', '#####'], '.LFT', 'NEiK', '道しるべを停留所の標識に見立てる', 'myme_lon'),
    ('egy_obelisk', 'egy', 'landmark', '石柱の広場', ['~#####~', '#######', '###*###', '#######', '~#####~'], '.POxqf', 'OsUP', '遺跡の広場。中央に石柱や像', 'egy_mtmmo'),
    ('egy_bazaar', 'egy', 'support', 'バザールの屋台', ['YYRYY*', '######', '~#####'], '.xPqFf', 'xqFR', '屋台＋絨毯。縦に並べるとバザール通り', 'egy_faqs'),
    ('egy_oasis', 'egy', 'support', 'オアシス', ['~.*.~', '.www.', '#www#', '.www.', '~.#.~'], 'PtFOqe', 'PqFX', '3×3の池をヤシで囲む', 'egy_mtmmo'),
    ('egy_camp', 'egy', 'filler', '隊商の焚き火', ['h#h', '#X#', '~*~'], '.PxqOf', 'xqFO', '焚き火を椅子で囲む', 'egy_faqs'),
    ('jpn_torii', 'jpn', 'landmark', '鳥居の参道', ['~#~', '#G#', '~#~', '#G#', '~#~', '#*#'], 'nate.F', 'nFtI', '1マスおきに鳥居。坂の前後に', 'jpn_shrine'),
    ('jpn_pond', 'jpn', 'support', '池泉の庭', ['~....~', '.#ww#.', '#wwww#', '.#ww#.', '~.*..~'], 'natFe.', 'nFqt', '池の縁に飛び石と灯籠', 'jpn_40'),
    ('jpn_tea', 'jpn', 'support', '茶屋', ['~YYY~', '.YYY.', 'h#*#h', '..#..'], 'natF.e', 'ucnF', '屋台を茶屋に見立てて縁台を左右に', 'jpn_gw'),
    ('jpn_bamboo', 'jpn', 'filler', '竹林の小道', ['a#a', 'a#a', '~#~', 'a#a', 'a#*'], 'nteF.L', 'nFqO', '細い道の両側に竹', 'jpn_40'),
    ('usa_diner', 'usa', 'landmark', 'ダイナー前', ['~YYYY~', '.chch.', '######'], 'LFtbxe', 'Tuxq', 'カウンターと外の席', 'camp1'),
    ('usa_yard', 'usa', 'support', '白い柵の前庭', ['ffffff', 'fHHHHf', 'fHHHHf', 'fHHHHf', 'fHHHHf', 'f~D#*f'], 'FteLq.', 'bqucx', '住民の家を柵で囲む。6×6', 'camp2'),
    ('usa_camp', 'usa', 'support', 'キャンプの焚き火', ['t~#~t', '#hXh#', '~#*#~', '..#..'], 'tFLexq', 'xqFc', '丸太椅子と焚き火', 'camp1'),
    ('usa_bench', 'usa', 'filler', 'ベンチと街灯', ['L*b~', '####'], '.FtLe', 'FqxT', '道ばたの小さな休憩', 'camp2'),
    ('hal_pumpkin', 'hal', 'landmark', 'かぼちゃ畑', ['kkkkk', 'k#*#k', 'kkkkk', '~###~'], 'JktzeL', 'XJszk', '畑の中の小道', 'hal'),
    ('hal_lantern', 'hal', 'support', 'ランタンの小道', ['J#J', '.#.', '~#~', 'J#J', '.#.', '~#*'], 'ktzeJ.', 'XszF', '3マスおきにランタン', 'hal'),
    ('hal_grave', 'hal', 'filler', '墓地', ['z~z~', '#*##', 'z~z~'], 'teJkL.', 'sXzJ', '墓石と枯れ木', 'hal'),
    ('hal_fire', 'hal', 'filler', '焚き火の輪', ['h~h', '#X#', 'h*h'], 'JktzeF', 'xqsk', '焚き火を囲む', 'hal'),
    ('eur_cafe', 'eur', 'landmark', 'カフェテラス', ['~YYYY*', '#####.', 'hchhch', '######'], 'LFxeut', 'uFxq', 'カウンターの前に2卓', 'eur_all'),
    ('eur_mill', 'eur', 'support', '風車と花', ['~~~~~', '~MMM~', '~MMM~', '~MMM~', '~#*#~'], 'FteLfq', 'FbxU', '風車の周りを花で一周', 'altema_eur'),
    ('eur_plaza', 'eur', 'filler', '小さな広場', ['~#~#~', '#####', '~#*#~', '#####', '~#~#~'], 'FLtbeq', 'sUKN', '中央に噴水や像', 'eur_all'),
    ('eur_street', 'eur', 'filler', '並木通り', ['~#~', '~#~', '~#~', '~#~', '~#~', '~#*'], 'tLFbef', 'LFbN', '縦につなげて伸ばす', 'eur_all'),
    ('port_dome', 'port', 'landmark', '青いドームの広場', ['~#####~', '#######', '###*###', '#######', '~#####~'], 'uPFqxt', 'UsKP', '白い石畳の広場', 'coast'),
    ('port_beach', 'port', 'support', 'ビーチクラブ', ['~u*u~', 'hxhxh', '#####'], 'PqFo.t', 'PqFx', '浜にパラソルとデッキチェア', 'coast'),
    ('port_fish', 'port', 'support', '魚市場', ['YYxYY', 'YY*YY', '#####'], 'xqFPLe', 'xqFR', '河口や桟橋の近くに', 'coast'),
    ('port_house', 'port', 'filler', '白い家並みの小道', ['~q*q~', '#####'], 'FtLeuP', 'bUKN', '鉢植えで飾った細い道', 'coast'),
    ('lon_pub', 'lon', 'support', 'パブの前', ['~YYY~', 'h#*#h', '#####'], '.LFtb', 'xcqT', 'カウンターと立ち飲みの席', 'note_lon'),
    ('lon_benchrow', 'lon', 'support', 'ベンチ並び', ['~bbb*', '#####'], '.LFt', 'TKNF', '並木道の休憩所', 'myme_lon'),
    ('lon_phone', 'lon', 'support', '電話ボックスの並び', ['T~T', '###', '~*~'], '.LFb', 'bNKi', '赤い電話ボックスを並べる', 'myme_lon'),
    ('egy_dig', 'egy', 'support', '発掘現場', ['ffff', 'fO*f', 'fOOf', 'ff~f'], 'xPqt.O', 'xqOs', '柵で囲って石柱と木箱', 'egy_mtmmo'),
    ('egy_market2', 'egy', 'support', 'ラグ市場', ['YY~YY', 'RR#RR', '#####'], 'xqPFfL', 'xqFR', '屋台と絨毯を2つ並べる', 'egy_faqs'),
    ('egy_well', 'egy', 'support', '井戸の広場', ['~#~', '#U#', '~*~'], 'PqxOtF', 'xqFP', '中央に井戸', 'egy_mtmmo'),
    ('jpn_stone', 'jpn', 'support', '石灯籠の庭', ['n#n', '#*#', 'n#n'], 'natF.e', 'FqtO', '灯籠で四隅をしめる', 'jpn_40'),
    ('jpn_onsen', 'jpn', 'support', '温泉の湯屋', ['~I#I~', '#####'], 'natFe.', 'nFqs', '温泉を2つ並べる', 'jpn_gw'),
    ('jpn_karesansui', 'jpn', 'support', '枯山水', ['~ggggg~', 'ggg*ggg', '~ggggg~'], 'nOtFe.', 'nOqs', '砂利に石を置く', 'jpn_40'),
    ('usa_porch', 'usa', 'support', 'ポーチの席', ['~#hh#~', '######'], 'FtLeqb', 'cqxu', '家の前のくつろぎ', 'camp2'),
    ('usa_bbq', 'usa', 'support', 'バーベキュー', ['~cX*c~', '######'], 'FtLexq', 'xqcb', '焚き火とテーブル', 'camp1'),
    ('usa_mail', 'usa', 'support', '郵便受けの角', ['~#*#~', '#####'], 'FtLexq', 'iNbT', '看板と花', 'camp2'),
    ('hal_pump2', 'hal', 'support', 'かぼちゃの広場', ['k#k', '#*#', 'k#k'], 'JtzeLk', 'XszJ', '四隅にかぼちゃ', 'hal'),
    ('hal_haunted', 'hal', 'support', '不気味な庭', ['z~z', '~*~', 'z~z'], 'tJkeLX', 'sXzJ', '墓石と枯れ木', 'hal'),
    ('hal_cauldron', 'hal', 'support', '魔女の焚き火', ['~X~', '#*#', 'h#h'], 'JkzteL', 'xqsk', '焚き火を椅子で囲む', 'hal'),
    ('eur_fountain', 'eur', 'support', '噴水広場', ['~#~#~', '#U*U#', '~#~#~'], 'FLtbeq', 'sKNF', '噴水を2つ並べる', 'altema_eur'),
    ('eur_flower', 'eur', 'support', '花壇', ['FFF', 'F*F', 'FFF'], '.', 'sUKNtqb', '花の中央に主役', 'eur_all'),
    ('eur_stall', 'eur', 'support', '市場の屋台', ['~YY~', '#*##'], 'FLtbeq', 'xqFu', '屋台を並べる', 'eur_all'),
    ('port_pier', 'port', 'support', '桟橋の小物', ['~#~#~', '#*#*#'], 'xqPuFo', 'xqFP', '桟橋の端に樽', 'coast'),
    ('port_boat', 'port', 'support', '船着き場', ['~x#x~', '#####', '~*~~~'], 'qPFoeL', 'xqFu', '樽と船具', 'coast'),
    ('port_cafe', 'port', 'support', '浜のカフェ', ['~u*u~', '#chc#'], 'PqFt.L', 'xqFR', '浜のテラス席', 'coast'),
]
ROLES = {t[0]: t[2] for t in T}
BASE_TH = {t[0]: TH[t[1]] for t in T}


def build():
    per = {}
    for base, th, role, nm, rows, edges, accs, note, src in T:
        out, seen = [], set()
        for g in GROUNDS[th]:
            for e in edges:
                for a in accs:
                    r = [''.join(g if c == '#' else (e if c == '~' else (a if c == '*' else c)) for c in row) for row in rows]
                    key = '|'.join(r)
                    if key in seen:
                        continue
                    seen.add(key)
                    mt = g if any('#' in row for row in rows) else ''
                    ed = '' if '~' not in ''.join(rows) else '・縁：' + EDGE_NAME.get(e, e)
                    ac = '' if '*' not in ''.join(rows) else '・' + ACC_NAME.get(a, a)
                    label = f"{nm}（{MAT[g] if mt else TH[th]}{ac}{ed}）"
                    out.append({'th': TH[th], 'name': label, 'r': r, 'note': note, 'mat': mt, 'src': SOURCES[src][1], 'base': base})
        per.setdefault(th, []).append(out)
    # テーマごとに同じ数（1000÷7）、型ごとに同じ数ずつ、等間隔に選ぶ
    quota = {th: N // 7 + (1 if i < N % 7 else 0) for i, th in enumerate(TH)}
    mods = []
    for th in TH:
        lists = per[th]
        need = quota[th]
        share = [need // len(lists) + (1 if i < need % len(lists) else 0) for i in range(len(lists))]
        for lst, k in zip(lists, share):
            k = min(k, len(lst))
            step = len(lst) / k
            mods += [lst[int(i * step)] for i in range(k)]
    # 足りない分は残りから足す
    if len(mods) < N:
        have = {'|'.join(m['r']) for m in mods}
        rest = {th: [m for lst in per[th] for m in lst if '|'.join(m['r']) not in have] for th in TH}
        while len(mods) < N and any(rest.values()):
            for th in TH:
                if rest[th] and len(mods) < N:
                    mods.append(rest[th].pop(0))
    # 形が同じものは1つだけ（別の型どうしでも）。足りない分は残りから足す
    uniq, seen2 = [], set()
    for m in mods:
        k = '|'.join(m['r'])
        if k not in seen2:
            seen2.add(k); uniq.append(m)
    if len(uniq) < N:
        rest = {th: [m for lst in per[th] for m in lst if '|'.join(m['r']) not in seen2] for th in TH}
        while len(uniq) < N and any(rest.values()):
            for th in TH:
                while rest[th] and '|'.join(rest[th][0]['r']) in seen2:
                    rest[th].pop(0)
                if rest[th] and len(uniq) < N:
                    m = rest[th].pop(0); seen2.add('|'.join(m['r'])); uniq.append(m)
    mods = uniq[:N]
    for i, m in enumerate(mods, 1):
        m['id'] = 'pop%04d' % i
    return mods


def main():
    mods = build()
    used = {m['src'] for m in mods}
    sources = [{'key': k, 'label': l, 'url': u} for k, (l, u) in SOURCES.items() if u in used]
    keys = ['id', 'th', 'name', 'r', 'note', 'mat', 'src', 'base']
    data = {'count': len(mods), 'sources': sources, 'modules': [{k: m[k] for k in keys} for m in mods]}
    with open(os.path.join(ROOT, 'modules-popular.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    lines = ['# 人気の作例のモジュール（%d個）' % len(mods), '', 'tools/gen_popular_modules.py が作った一覧です（生成物）。', '',
             '| id | テーマ | 名前 | 大きさ | 型 |', '|---|---|---|---|---|']
    for m in mods:
        lines.append('| %s | %s | %s | %d×%d | %s |' % (m['id'], m['th'], m['name'], len(m['r'][0]), len(m['r']), m['base']))
    with open(os.path.join(ROOT, 'modules-popular.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    th_count = {}
    for m in mods:
        th_count[m['th']] = th_count.get(m['th'], 0) + 1
    print('modules-popular.json:', len(mods), th_count)


if __name__ == '__main__':
    main()
