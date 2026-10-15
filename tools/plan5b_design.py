#!/usr/bin/env python3
"""案5b（第59回・候補B「段々の丘の町」）：島を0から描く設計書 designs/plan5b_spec.json と、地区の見せ場 designs/kits_plan5b.json を書く。

  python3 tools/plan5b_design.py && ICE_PLAN=5b SEED=6 bash tools/plan3_build.sh && ICE_PLAN=5b node tools/test_plan3.js
  ICE_PLAN=5b python3 tools/plan4_kitcheck.py --built      # 物を置いた後も歩けるか
  ICE_PLAN=5b python3 tools/plan4_kitcheck.py --map D3     # 地区の文字の地図（D1〜D8）
  python3 tools/plan5b_design.py --show                    # 町の図を文字で見る

考え：町は飛行場と案内所の広場から北へ、円形劇場のように3段で上る。
  1段目＝広場と下町（飛行場の前庭・並木の大通り・タヌキ商店とエイブル）、広場の北の「路地の町」
         （2段目のレンガのかたまり W1 W2 を1段目の路地 C1 C2 とパブの小広場で彫る。路地 C2 のつきあたりはテラスの下をくぐる城の門）
  2段目＝軸のテラス（広場の真北の大石段の上・両わきに塔の台）と上のテラス（レイモンドとメルの家が城の崖を背に南向き）、
         運河の東の倉庫のテラス（水から立つ城壁・トリュフの家・市場のホール）。路地 C1 の頭の石段でつづら折りに上がる
  3段目＝城の丘（城門と天守の塔・正面の城壁と角の塔・自宅・天守の庭）。
         飛行場 → 前庭 → 大通り → 広場 → 大石段 → 軸のテラス → 城への石段 → 城門 → 天守の塔 が1本の軸（x30〜31）
  東＝博物館の通りと東の公園、港（運河の曲がり・船だまり・魚市場・倉庫のあいだのディーナとスクートの家）
  町のかたまりの多くは3段目の芯（茶色のレンガの屋根・窓のパネル）をもつ＝2階建てのレンガの建物に見せる（灰色の屋根ばかりにしない）
  川向こうの村（S）は手で見せ場を置く（落ち葉と苔の地面・風車）。自動の見せ場は町の東のふちに白い石の床を並べていた
水は少なく（町の陸の約8%）：城の貯水池（3段目）から2段の滝で落ち、運河1本（3マス）が倉庫のテラスの城壁と岸の道のあいだを南へ、東へ曲がって船だまりへ。
自然の川は町の外：霊峰の池 → 滝 → 西の河口、森の泉 → 滝 → 東の谷 → 南の河口。北は霊峰・竹林・森の2段目の台地（北の街道で町とつながる）。
記号（canvas）：1 2 3＝段の地面、- + #＝その段の通り、~ = ^＝1・2・3段目の水、空白＝さわらない。
"""
import json, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
PLAN = '5b'

# ---- 町の図（x13〜66・y26〜82）----
X0, Y0, X1, Y1 = 13, 26, 66, 82
C = {}


def F(x0, y0, x1, y1, ch):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if X0 <= x <= X1 and Y0 <= y <= Y1:
                C[(x, y)] = ch


F(X0, Y0, X1, Y1, '1')
# ===== 北：町と野山のさかいの「北の街道」（2段目。北の台地とつながる）=====
F(18, 26, 46, 27, '+')
# ===== 丘（2段目）：城の丘のふもと・上のテラス（y39〜45）=====
F(18, 28, 46, 45, '2')
F(14, 41, 17, 45, '2')
F(15, 42, 16, 44, '3')                 # 西のはしの見張りの塔（3段目のかたまり）
F(18, 28, 19, 43, '+')                 # 西のテラスの小道（北の街道 → テラス）
# ===== 城の丘（3段目）y29〜38：城門と天守の塔（軸）・自宅（西）・天守の庭（東）・正面の城壁、東に貯水池と稜堡 =====
F(21, 29, 44, 38, '3')
F(30, 33, 31, 37, '#')                 # 軸：城への石段の上 → 城門
F(23, 34, 29, 35, '#')                 # 自宅の前へ
F(32, 33, 34, 34, '#')                 # 天守の庭へ
# ===== 上のテラス（2段目）：家は城の崖を背に南向き（y44〜45 がテラス通り）=====
F(14, 44, 38, 45, '+')                 # テラス通り
F(30, 42, 31, 43, '+')                 # 城への石段の下
# ===== 軸のテラス（2段目）：広場の真北の大石段（2本を1マスあけて並べる）の上の石畳の広場。両わきに塔の台（3段目）=====
F(25, 46, 36, 57, '2')
F(26, 51, 27, 55, '3'); F(34, 51, 35, 55, '3')     # 塔の台（castle tower をのせる）
F(30, 46, 31, 55, '+')                 # 軸の道
F(28, 56, 32, 56, '+')                 # 大石段の上の踊り場
# ===== 路地の町（y46〜59）：1段目の路地と小広場を、2段目のレンガのかたまりのあいだに彫る =====
F(14, 49, 17, 58, '2'); F(15, 50, 16, 57, '3')     # かたまり W1（3段目の芯のある高いレンガの建物。石段のとなりは1マスあける）
F(18, 49, 19, 59, '-')                 # 路地 C1（頭に石段：テラスへつづら折り）
F(20, 49, 22, 53, '2')                 # かたまり W2
F(23, 47, 24, 53, '-')                 # 路地 C2（つきあたり y46 はテラスの下をくぐる城の門）
# パブの小広場（x20〜24・y54〜59）は1段目の石畳（道にしない）
F(37, 46, 38, 59, '-')                 # 運河の西の岸（広場の東の通りの北）
# ===== 東：博物館の通り（1段目）と、運河から立つ倉庫のテラス（2段目）=====
F(42, 39, 43, 43, '2')                 # 2段目の水路の東の岸
F(44, 44, 62, 45, '-')                 # 博物館の前の通り
F(47, 28, 48, 43, '-')                 # 東の公園の小道
F(42, 48, 55, 56, '2')                 # 倉庫のテラス（西のふちは運河から立つ城壁）
F(52, 49, 54, 54, '3')                 # 市場のホール（3段目のかたまり）
F(44, 55, 51, 55, '+')                 # テラスの道（トリュフの家の前 → 石段）
F(56, 46, 57, 59, '-')                 # 路地 C5
F(58, 48, 61, 55, '2'); F(59, 50, 60, 54, '3')     # 倉庫 E3（3段目の芯）
F(42, 57, 43, 59, '-')                 # 運河の東の岸（南）
# 広場の北の通り（大石段の足もと x27〜33 は y61 だけ道）
F(14, 60, 26, 61, '-'); F(34, 60, 63, 61, '-'); F(27, 61, 33, 61, '-')
# ===== 広場のまわりと西 =====
F(23, 62, 24, 74, '-')                 # 広場の西の通り
F(37, 62, 38, 74, '-')                 # 広場の東の通り
F(15, 62, 21, 65, '2'); F(16, 63, 20, 64, '3')     # 西のかたまり（2段目・3段目の芯のレンガの建物）
F(14, 69, 15, 74, '2')                 # 南西のかたまり
# ===== 下町：広場の南の通り・大通り・前庭・海岸通り =====
F(25, 73, 42, 74, '-')
F(30, 75, 33, 80, '-')                 # 大通り（飛行場 → 広場）
F(22, 76, 27, 80, '2'); F(24, 77, 26, 79, '3')     # 市場のかたまり（2段目・3段目の芯）
F(30, 81, 34, 82, '-')                 # 飛行場の前庭（x26〜38 は石畳）
F(14, 82, 25, 82, '-'); F(39, 82, 63, 82, '-')     # 海岸の小道
# ===== 運河の東：運河の角・港の船だまり・倉庫のあいだの家 =====
F(44, 62, 46, 63, '2')                 # 運河の角のかたまり
F(42, 67, 54, 68, '-')                 # 南の岸の通り
F(42, 69, 43, 81, '-')                 # 東の路地
F(50, 73, 53, 80, '2'); F(51, 75, 52, 79, '3')     # 港の倉庫（ディーナとスクートの家のあいだ・3段目の芯は南のふちに銃眼の城壁）
F(57, 71, 63, 72, '-')                 # 港の岸
F(62, 44, 63, 82, '-')                 # 川ぞいの道（町の東のさかい）
# ===== 水（最後に描く：通りに上書きされないように）=====
F(39, 30, 41, 38, '^')                 # 城の貯水池 → 2段の滝
F(39, 39, 41, 43, '=')                 # 2段目の水路（貯水池の滝の下）
F(39, 44, 41, 66, '~')                 # 運河（滝の下から南へ）
F(42, 64, 56, 66, '~')                 # 運河（東へ）
F(55, 62, 60, 70, '~')                 # 港の船だまり
rows = [''.join(C.get((x, y), ' ') for x in range(X0, X1 + 1)) for y in range(Y0, Y1 + 1)]

draw = [
    # ---- 北の台地（2段目）：霊峰・竹林・森がひとつづきの高い野山。町の2段目（北の街道）とつながる ----
    {'blob': [25, 21, 12, 8.5], 'h': 2, 'amp': .16, 'why': '霊峰のすそ（2段目）'},
    {'blob': [40, 22, 7, 8], 'h': 2, 'amp': .16, 'why': '竹林の台地'},
    {'blob': [52, 21, 11.5, 8], 'h': 2, 'amp': .18, 'why': '森の台地'},
    {'rect': [19, 22, 46, 25], 'h': 2, 'why': '台地と北の街道をつなぐ'},
    {'blob': [24, 18.5, 5.5, 3.6], 'h': 3, 'amp': .14, 'why': '霊峰の頂（3段目）'},
    {'blob': [56, 18, 4.2, 3], 'h': 3, 'amp': .15, 'why': '森の泉の丘（3段目）'},
    # ---- ハロウィン（北東）：南西に口のあいた尾根の輪 ----
    {'blob': [89, 24, 10.5, 9.5], 'h': 2, 'amp': .16, 'why': '尾根'},
    {'blob': [87, 26, 6, 5.5], 'h': 1, 'amp': .1, 'why': 'くぼ地'},
    {'poly': [[78, 30], [84, 26], [88, 30], [84, 36], [78, 36]], 'h': 1, 'why': '尾根の南西の口'},
    # ---- 村（東）：平らな村（風車は村の通りの東に）----
    # ---- 町（最後に描く。北の台地の南のふちを町の図で切りそろえる）----
    {'canvas': {'x0': X0, 'y0': Y0, 'rows': rows}, 'why': '段々の丘の町（3段）を1マスずつ'},
]

water = [
    {'river': [[16, 24.5], [15, 28], [14.5, 32], [14, 35], [13, 37]], 'wmin': 2, 'wmax': 2.5, 'name': 'A（霊峰の池 → 滝 → 西の河口）'},
    {'pond': [18, 22, 3.2, 2.5], 'why': '霊峰の池（川Aの源）'},
    {'pond': [88, 45, 4, 3.2], 'islet': True, 'why': '村の池と中島'},
    {'river': [[57, 18], [62, 21], [66, 26], [69, 32], [71, 40], [72, 48], [70, 57], [72, 66], [71, 75], [72, 83]], 'wmin': 2.2, 'wmax': 3.4, 'name': 'B（森の泉 → 滝 → 東の谷 → 南の河口）'},
    {'pond': [87, 24, 2.2, 1.8], 'why': 'くぼ地の黒い池'},
    {'settle': True},
]

BUILD = [
    {'id': 'home', 'kind': 'player_house', 'near': [22, 30], 'r': 0, 'name': '自宅（城の丘の西）'},
    {'id': 'museum', 'kind': 'museum', 'near': [49, 40], 'r': 0, 'name': '博物館（東の通り・貯水池の滝のとなり）'},
    {'id': 'v1', 'kind': 'villager', 'villager': 'Raymond', 'near': [22, 40], 'r': 0, 'zone': 'C'},
    {'id': 'v2', 'kind': 'villager', 'villager': 'Maelle', 'near': [33, 40], 'r': 0, 'zone': 'C'},
    {'id': 'v3', 'kind': 'villager', 'villager': 'Truffles', 'near': [46, 49], 'r': 0, 'zone': 'C'},
    {'id': 'v4', 'kind': 'villager', 'villager': 'Deena', 'near': [45, 73], 'r': 0, 'zone': 'C'},
    {'id': 'v6', 'kind': 'villager', 'villager': 'Bea', 'near': [18, 69], 'r': 0, 'zone': 'C'},
    {'id': 'nook', 'kind': 'nook', 'near': [14, 77], 'r': 0, 'name': 'タヌキ商店（海岸通りの西）'},
    {'id': 'able', 'kind': 'able', 'near': [37, 76], 'r': 0, 'name': 'エイブルシスターズ（飛行場の前庭の東）'},
    {'id': 'v9', 'kind': 'villager', 'villager': 'Scoot', 'near': [55, 74], 'r': 0, 'zone': 'P'},
    {'id': 'v7', 'kind': 'villager', 'villager': 'Genji', 'near': [30, 22], 'r': 5, 'zone': 'J'},
    {'id': 'camp', 'kind': 'campsite', 'near': [48, 21], 'r': 5, 'name': 'キャンプ場（森の台地）'},
    {'id': 'v8', 'kind': 'villager', 'villager': 'Muffy', 'near': [86, 26], 'r': 4, 'zone': 'H'},
    {'id': 'v5', 'kind': 'villager', 'villager': 'Pecan', 'near': [82, 48], 'r': 5, 'zone': 'S'},
    {'id': 'v10', 'kind': 'villager', 'villager': 'Ed', 'near': [84, 68], 'r': 5, 'zone': 'S'},
]


# ---- 地区の見せ場（キット）：designs/kits_plan5b.json に書く。どれも目録の本物の家具・マイデザイン ----
KITS5B = {
    'p5b_citadel': {'name': '城門と天守の塔（軸のつきあたり：レンガの城門・天守の塔・左右の城壁）', 'size': [6, 3], 'ref': ['R-1266', 'R-1231', 'X-0010_1'],
                    'items': [['castle wall', 0, 1, 0, 'Brown', 'wall_windows_bricks'], ['castle tower', 2, 0, 0, 'Brown'], ['castle wall', 4, 1, 0, 'Brown', 'wall_windows_bricks'],
                              ['castle gate', 1, 2, 0, 'Brown']],
                    'note': '飛行場 → 広場 → 大石段 → 軸のテラス → 城への石段 → 城門 → 天守の塔。軸のつきあたりの目じるし。城門の前（y33）が軸の道のおわり'},
    'p5b_gatecourt': {'name': '城門の前の石畳の前庭（城のマンホール）', 'size': [5, 2], 'ref': ['R-1233', 'R-1231'],
                      'items': [['manhole cover', 2, 1, 0, 'Castle']],
                      'note': '城への石段を上がった所から城門までの前庭。レンガのヘリンボーンのマイデザインを敷く（灰色の道の十字にしない）'},
    'p5b_windmill': {'name': '村の風車（風車・ベンチ・チューリップの畑）', 'size': [5, 3], 'ref': ['X-0006_1'],
                     'items': [['windmill', 1, 0, 0, 'White'], ['garden bench', 3, 2, 0, 'White']],
                     'plants': [{'type': 'tulips', 'rect': [0, 0, 0, 2], 'colors': ['red', 'yellow', 'white']}, {'type': 'tulips', 'rect': [3, 0, 4, 1], 'colors': ['red', 'yellow', 'white']}],
                     'note': '村の目じるし。村の通りの東、池と市民農園のあいだ'},
    'p5b_closegate': {'name': '路地 C2 のつきあたりの城の門（テラスの下をくぐるレンガのアーチ）', 'size': [3, 1], 'ref': ['R-1233', 'R-1148', 'X-0010_1'],
                      'items': [['castle gate', 0, 0, 0, 'Brown']],
                      'note': '上のテラスの崖のすそ。路地 C2 が城の門をくぐってテラスの下へ入っていくように見せる（見た目の立体交差）'},
    'p5b_bastion': {'name': '貯水池の東の稜堡の塔（濃い灰色の石）', 'size': [2, 2], 'ref': ['R-1231'], 'items': [['castle tower', 0, 0, 0, 'Dark gray']],
                    'note': '堀（貯水池）の東の3段目の稜堡。滝の上の見張りの塔'},
    'p5b_castlefront_w': {'name': '城の正面・西（角の塔と銃眼のある城壁）', 'size': [8, 2], 'ref': ['R-1231', 'X-0003_1'],
                          'items': [['castle tower', 0, 0, 0, 'Brown'], ['castle wall', 2, 1, 0, 'Brown', 'wall_windows_bricks'], ['castle wall', 4, 1, 0, 'Brown', 'wall_windows_bricks'],
                                    ['castle wall', 6, 1, 0, 'Brown', 'wall_windows_bricks']],
                          'note': '城の丘（3段目）の南のふち。上のテラスと広場から見上げる城の正面'},
    'p5b_castlefront_e': {'name': '城の正面・東（銃眼のある城壁と角の塔）', 'size': [6, 2], 'ref': ['R-1231', 'X-0003_1'],
                          'items': [['castle wall', 0, 1, 0, 'Brown', 'wall_windows_bricks'], ['castle wall', 2, 1, 0, 'Brown', 'wall_windows_bricks'], ['castle tower', 4, 0, 0, 'Brown']],
                          'note': '城への石段の東。貯水池の西の角の塔'},
    'p5b_castlegarden': {'name': '天守の庭のあずまや（白いガゼボ・ガーデンライト・鉄のベンチ・バラ）', 'size': [4, 4], 'ref': ['R-1231', 'R-1217'],
                         'items': [['gazebo', 0, 0, 0, 'White'], ['garden lantern', 3, 0, 0, 'Black'], ['iron garden bench', 2, 3, 0, 'Black']],
                         'plants': [{'type': 'roses', 'rect': [3, 1, 3, 2], 'colors': ['red', 'white']}, {'type': 'roses', 'rect': [0, 3, 1, 3], 'colors': ['red', 'white']}],
                         'note': '城の丘（3段目）の天守の東。丘の小道（西）から入る'},
    'p5b_belvedere_w': {'name': '大石段の上の見晴らし台・西（観光ぼうえんきょう・鉄のベンチ）', 'size': [3, 1], 'ref': ['X-0003_1'],
                        'items': [['tourist telescope', 0, 0, 0, 'Black'], ['iron garden bench', 1, 0, 0, 'Black']],
                        'note': '軸のテラスの南のふち（2段目）。広場と案内所と飛行場の軸を見下ろす'},
    'p5b_belvedere_e': {'name': '大石段の上の見晴らし台・東（鉄のベンチ・ガーデンライト）', 'size': [3, 1], 'ref': ['X-0003_1'],
                        'items': [['iron garden bench', 0, 0, 0, 'Black'], ['garden lantern', 2, 0, 0, 'Black']],
                        'note': '軸のテラスの南のふち（2段目）'},
    'p5b_stairfoot': {'name': '大石段の足もとのアーケードのカフェ（緑の屋台・黒板・鉄のテーブル）', 'size': [4, 2], 'ref': ['X-0003_1', 'X-0011_1', 'R-1233'],
                      'items': [['menu chalkboard', 0, 0, 0, 'Dark brown'], ['stall', 1, 0, 0, 'Green'], ['streetlamp', 3, 0, 0, 'Black'],
                                ['iron garden chair', 0, 1, 0, 'Black'], ['iron garden table', 1, 1, 0, 'Black'], ['iron garden chair', 2, 1, 0, 'Black']],
                      'note': '軸のテラスの崖（アーチと戸のパネル）の足もと。大石段の西。南の通りに面する'},
    'p5b_flowerstall': {'name': '大石段の足もとの花屋（花のショーケース・花の荷車・街灯）', 'size': [3, 2], 'ref': ['X-0011_1', 'R-1233'],
                        'items': [['streetlamp', 0, 0, 0, 'Black'], ['flower display case', 1, 0, 0, 'Green'], ['garden wagon', 1, 1, 0, 'Dark brown']],
                        'note': '軸のテラスの崖の足もと。大石段の東'},
    'p5b_pub': {'name': 'パブの小広場（パブの軒先：たる・木箱・鉄のテーブル・黒板）', 'size': [4, 2], 'ref': ['R-0877', 'R-0878', 'X-0011_1'],
                'items': [['barrel', 0, 0], ['standing shop sign', 1, 0, 0, 'Black'], ['iron garden table', 2, 0, 0, 'Brown'], ['iron garden chair', 3, 0, 0, 'Brown'],
                          ['wooden box', 0, 1, 0, 'Dark brown'], ['iron garden chair', 2, 1, 0, 'Brown']],
                'note': 'かたまり W2 の南の崖（窓と戸のパネル）の足もと。路地 C1 と C2 のあいだの小広場'},
    'p5b_arrivals': {'name': '飛行場の前庭・西（広場の時計・待合いのベンチ・赤い電話ボックス）', 'size': [4, 1], 'ref': ['R-1103', 'R-1150', 'R-1130'],
                     'items': [['park clock', 0, 0, 0, 'Black'], ['public bench', 1, 0, 0, 'Monotone'], ['phone box', 3, 0, 0, 'Red']],
                     'note': '飛行場を出てすぐ左。時計の下で待ち合わせ。南の1列（y82）は海岸の小道のためにあける'},
    'p5b_departures': {'name': '飛行場の前庭・東（到着と出発の掲示板・青い運航表・街灯）', 'size': [3, 1], 'ref': ['R-1134', 'R-1118'],
                       'items': [['simple panel', 0, 0, 0, 'Brown', 'arrive_depart'], ['simple panel', 1, 0, 0, 'Brown', 'flight_board_blue'], ['streetlamp', 2, 0, 0, 'Black']],
                       'note': '飛行場を出てすぐ右。エイブルの入口の前（x38〜40）と南の1列（y82）はあける'},
    'p5b_plazabench': {'name': '広場の南の並木のベンチ', 'size': [2, 1], 'ref': ['R-1231'], 'items': [['iron garden bench', 0, 0, 0, 'Black']],
                       'note': '広場の南のふち。並木のあいだから広場と案内所を向く'},
    'p5b_nookstalls': {'name': 'タヌキ商店の西の八百屋の軒先（屋台・野菜かご）', 'size': [3, 1], 'ref': ['R-1241', 'X-0011_1'],
                       'items': [['stall', 0, 0, 0, 'Natural'], ['veggie basket', 2, 0]],
                       'note': '海岸ぞい。タヌキ商店の入口（x16〜18）はあける'},
    'p5b_museumyard': {'name': '博物館の前庭（白い大理石の柱・いだいなちょうこく・展示台）', 'size': [5, 2], 'ref': ['R-1231'],
                       'items': [['decorative pillar', 0, 0, 0, 'Whitestone marble'], ['great statue', 1, 0], ['decorative pillar', 3, 0, 0, 'Whitestone marble'],
                                 ['display stand', 4, 0, 0, 'White'], ['garden lantern', 0, 1, 0, 'White'], ['garden lantern', 3, 1, 0, 'White'], ['stack of books', 4, 1, 0, 'Old']],
                       'note': '博物館の入口の真向かい、通りの南。うしろは倉庫のテラスの崖'},
    'p5b_bookmarket': {'name': '倉庫のテラスの足もとの古本市（こげ茶の屋台・本の山・鉄のベンチ）', 'size': [5, 2], 'ref': ['X-0006_1', 'X-0011_1'],
                       'items': [['stall', 0, 0, 0, 'Dark brown'], ['stack of books', 2, 0, 0, 'Literature'], ['strapped books', 3, 0, 0, 'Red'], ['streetlamp', 4, 0, 0, 'Black'],
                                 ['menu chalkboard', 0, 1, 0, 'Dark brown'], ['stack of books', 1, 1, 0, 'Old'], ['iron garden bench', 3, 1, 0, 'Black']],
                       'note': '倉庫のテラスの南の崖（アーチのパネル）の足もと。石段の東'},
    'p5b_bandstand': {'name': '東の公園の音楽堂（緑のガゼボ・ふめんだい・鉄のベンチ）', 'size': [5, 5], 'ref': ['R-1217'],
                      'items': [['garden lantern', 0, 0, 0, 'Black'], ['gazebo', 1, 1, 0, 'Green'], ['garden lantern', 4, 0, 0, 'Black'], ['music stand', 4, 2, 0, 'Black'],
                                ['iron garden bench', 0, 4, 0, 'Green'], ['iron garden bench', 3, 4, 0, 'Green']],
                      'note': '城の東の公園（1段目）の木立の中。北に貯水池と稜堡、南に博物館'},
    'p5b_slipway': {'name': '運河の曲がり角の船台（白いヨット）', 'size': [3, 2], 'ref': ['R-1148', 'R-1235'],
                    'items': [['yacht', 0, 0, 0, 'White']],
                    'note': '運河の東への曲がり角と船だまりのあいだの岸。ヨットを陸にあげて手入れする船台'},
    'p5b_fishmarket': {'name': '港の魚市場（白い屋台・魚の干物・クーラーボックス・うきわ・いかり）', 'size': [5, 2], 'ref': ['R-1235'],
                       'items': [['stall', 0, 0, 0, 'White'], ['fish-drying rack', 2, 0, 0, 'Fish'], ['barrel', 4, 0], ['cooler box', 0, 1, 0, 'Blue'], ['wooden box', 1, 1, 0, 'Natural'],
                                 ['life ring', 2, 1, 0, 'Red'], ['anchor statue', 3, 1, 0, 'Black'], ['menu chalkboard', 4, 1, 0, 'White']],
                       'note': '運河の南の岸の通りの南。ディーナの家の北'},
}
KIT_AT = [   # [キット, 場所, 地区, 道の上に置くか, 名前, 地面のデザイン（herring＝レンガのヘリンボーン・brick＝赤いレンガ・flag＝石の板・plank＝板・leaves＝落ち葉・moss＝苔の石）]
    ['p5b_citadel', [28, 30], 'D1', True, '城門と天守の塔', 'herring'],
    ['p5b_gatecourt', [29, 34], 'D1', True, '城門の前の前庭', 'herring'],
    ['p5b_bastion', [42, 30], 'D1', True, '稜堡の塔', 'flag'],
    ['p5b_closegate', [22, 46], 'D3', True, '路地 C2 の城の門', 'brick'],
    ['p5b_castlefront_w', [21, 37], 'D1', True, '城の正面・西', 'herring'],
    ['p5b_castlefront_e', [33, 37], 'D1', True, '城の正面・東', 'herring'],
    ['p5b_castlegarden', [35, 30], 'D1', True, '天守の庭のあずまや', 'flag'],
    ['p5b_belvedere_w', [25, 57], 'D3', True, '大石段の上の見晴らし台・西', 'herring'],
    ['p5b_belvedere_e', [34, 57], 'D3', True, '大石段の上の見晴らし台・東', 'herring'],
    ['p5b_stairfoot', [23, 58], 'D3', True, '大石段の足もとのカフェ', 'herring'],
    ['p5b_flowerstall', [34, 58], 'D3', True, '大石段の足もとの花屋', 'herring'],
    ['p5b_pub', [20, 54], 'D3', True, 'パブの小広場', 'brick'],
    ['p5b_plazabench', [28, 72], 'D4', True, '広場の南のベンチ・西', 'herring'],
    ['p5b_plazabench', [32, 72], 'D4', True, '広場の南のベンチ・東', 'herring'],
    ['p5b_arrivals', [26, 81], 'D4', True, '飛行場の前庭・西', 'flag'],
    ['p5b_departures', [35, 81], 'D4', True, '飛行場の前庭・東', 'flag'],
    ['p5b_nookstalls', [13, 81], 'D4', True, 'タヌキ商店の八百屋の軒先', 'brick'],
    ['p5b_museumyard', [49, 46], 'D5', True, '博物館の前庭', 'flag'],
    ['p5b_bookmarket', [50, 57], 'D5', True, '倉庫のテラスの足もとの古本市', 'herring'],
    ['p5b_bandstand', [52, 31], 'D6', True, '東の公園の音楽堂', 'herring'],
    ['p5b_fishmarket', [49, 69], 'D7', True, '港の魚市場', 'plank'],
    ['p5b_slipway', [52, 62], 'D7', False, '運河の船台', 'plank'],
    ['p5b_windmill', [87, 57], 'D8', True, '村の風車', 'leaves'],
]
# 村（S）の見せ場は手で置く（自動で置くと町の東のふちに白い石の床が並ぶ）。kits.json の見せ場を、落ち葉と苔の地面で
VILLAGE = [['cot_garden', [87, 49], 'ピーカンの家の東のコテージの庭', 'leaves'], ['tea_picnic', [94, 42], '池のほとりのお茶会', 'moss'],
           ['bakery', [77, 56], '村の通りのパン屋', 'leaves'], ['formal_garden', [74, 61], '村の広場（生け垣と噴水）', 'moss'],
           ['cot_greenhouse', [77, 68], 'エドの家の西の温室', 'leaves'], ['allotment', [92, 66], '風車の丘の南の市民農園', 'leaves']]
DISTRICTS = {
    'D1': {'box': [18, 26, 46, 38], 'name': '城の丘（3段目の城門と天守の塔・正面の城壁と角の塔・自宅・天守の庭・貯水池と稜堡・北の街道）', 'zone': 'C'},
    'D2': {'box': [13, 39, 38, 45], 'name': '上のテラス（2段目：レイモンドとメルの家・テラス通り・西の小道・城への石段の下）', 'zone': 'C'},
    'D3': {'box': [13, 46, 38, 61], 'name': '路地の町と大石段（路地 C1 の石段・C2 の城の門・パブの小広場・軸のテラスと塔の台・大石段の足もとのカフェと花屋）', 'zone': 'C'},
    'D4': {'box': [13, 62, 41, 82], 'name': '広場と下町（案内所の広場・西のかたまり・ベア・タヌキ商店・大通り・飛行場の前庭・エイブル）', 'zone': 'C'},
    'D5': {'box': [39, 39, 63, 61], 'name': '博物館と倉庫のテラス（滝の下の運河・博物館と前庭・水から立つ倉庫のテラスとトリュフの家・市場のホール・古本市・路地 C5）', 'zone': 'C'},
    'D6': {'box': [47, 26, 63, 38], 'name': '東の公園（城の東の木立・音楽堂）', 'zone': 'C'},
    'D7': {'box': [42, 62, 63, 82], 'name': '港（運河の東の曲がり・船だまり・魚市場・倉庫のあいだのディーナとスクートの家・川ぞいの道）', 'zone': 'P'},
    'D8': {'box': [64, 34, 100, 82], 'name': '川向こうの村（村の風車・村の広場・パン屋・コテージの庭・温室・市民農園・池のほとりのお茶会）', 'zone': 'S'},
}
json.dump({'note': '案5b（第59回）の地区の見せ場。tools/plan5b_design.py が書く', 'manual_zones': 'CPS', 'kits': KITS5B,
           'placements': [{'kit': k, 'at': at, 'on_road': onr, 'flip': False, 'name': nm, 'zone': DISTRICTS[d]['zone'], 'district': d, 'style': st} for k, at, d, onr, nm, st in KIT_AT]},
          open(os.path.join(ROOT, f'designs/kits_plan{PLAN}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---- 町の木（森から植えかえる）----
TREES = [[25, 72], [26, 72], [35, 72], [36, 72],                                  # 広場の南の並木
         [29, 75], [29, 77], [29, 79], [34, 75], [34, 77], [34, 79],              # 大通りの並木
         [29, 48], [29, 51], [29, 54], [32, 48], [32, 51], [32, 54],              # 軸のテラスの並木（軸の道の両がわ）
         [20, 40], [20, 42], [28, 40], [27, 43],                                  # 上のテラス（家のあいだ）
         [22, 35], [36, 35], [37, 35],                                           # 城の丘
         [20, 57], [44, 50], [44, 53],                                           # パブの小広場・倉庫のテラスの西のふち
         [50, 29], [50, 32], [50, 35], [50, 38], [53, 37], [56, 37], [58, 35], [61, 33], [61, 36], [59, 38], [55, 29],   # 東の公園の木立
         [45, 59], [59, 58], [44, 71], [55, 72], [17, 74]]
# ---- 崖のすそのアーチ・戸・窓（下の路地が上のテラスの下をくぐるように見せる）rot 0＝崖が北 ----
PANELS = [[16, 46, 0, 'window'], [17, 46, 0, 'door'], [14, 46, 0, 'window'], [15, 46, 0, 'arch'],
          [25, 58, 0, 'window'], [26, 58, 0, 'door'], [27, 58, 0, 'arch'], [33, 58, 0, 'arch'],
          [44, 57, 0, 'arch'], [45, 57, 0, 'window'], [47, 57, 0, 'arch']]

spec = {
    'note': '案5b（第59回・候補B「段々の丘の町」）：0から描いた島（tools/plan5b_design.py が書く）',
    'base': 'authored', 'seed': 6, 'start': [33, 82],
    'draw': draw, 'water': water, 'edits': [],
    'bridge_sites': [], 'incline_sites': [],
    # 設計の坂（S＝北が上の段）：広場の真北の大石段（2本を1マスあけて並べる）・城への石段（軸）・路地 C1 の頭の石段（つづら折り）・倉庫のテラスの石段
    'inclines': [[28, 57, 'S'], [31, 57, 'S'], [30, 38, 'S'], [18, 45, 'S'], [48, 56, 'S']],
    'buildings': BUILD,
    'streets': [],
    # 道を引く順：町 → 野山 → 自宅（城の丘）。城の丘の裏に勝手な坂ができないように、北の街道へは西のテラスの小道から
    'routes': [{'name': '飛行場 → 広場', 'to': [[31, 73], [32, 73]], 'w': 2}] + [{'name': i, 'to': i} for i in
               ['nook', 'able', 'v6', 'v4', 'v9', 'v1', 'v2', 'museum', 'v3', 'v7', 'camp', 'v8', 'v5', 'v10', 'home']],
    # 設計の橋：広場の北の通り×運河、港の路地×運河
    'bridges': [[39, 58, 42, 62], [48, 64, 52, 67]],
    'zones': [
        {'zone': 'S', 'rect': [0, 0, 111, 95]},
        {'zone': 'J', 'blob': [24, 20, 13, 9.5]},
        {'zone': 'B', 'rect': [35, 12, 43, 28]},
        {'zone': 'F', 'rect': [44, 12, 66, 28]},
        {'zone': 'H', 'rect': [76, 12, 104, 37]},
        {'zone': 'C', 'rect': [13, 29, 63, 82]},
        {'zone': 'P', 'rect': [52, 61, 63, 82]},
    ],
    'manual_zones': 'CPS',
    'kits': [{'kit': k, 'at': at, 'zone': DISTRICTS[d]['zone'], 'on_road': onr, 'flip': False, 'name': nm, 'district': d, 'style': st} for k, at, d, onr, nm, st in KIT_AT] +
            [{'kit': k, 'at': at, 'zone': 'S', 'on_road': True, 'flip': False, 'name': nm, 'style': st} for k, at, nm, st in VILLAGE],
    'street_trees': TREES,
    # 目じるし：大石段の両わきの塔の台（3段目）の上の castle tower（タワーブリッジの塔のように軸をはさむ）、
    # 運河から立つ倉庫のテラスの水ぎわの城壁（R-1233：水からじかに立つ壁の上の銃眼）、路地 C2 のつきあたりの城の門（テラスの下をくぐる）
    'landmarks': [['castle tower', 26, 52, 0, 'Brown'], ['castle tower', 34, 52, 0, 'Brown'],
                  ['castle wall', 42, 49, 1, 'Brown', 'wall_windows_bricks'], ['castle wall', 42, 51, 1, 'Brown', 'wall_windows_bricks'],
                  ['castle wall', 42, 53, 1, 'Brown', 'wall_windows_bricks']],
    'incline_kinds': {'30,38': 'stone staircase', '18,45': 'stone staircase', '28,57': 'stone staircase', '31,57': 'stone staircase'},
    'bridge_kinds': {'39,58': 'stone bridge'},
    'panels': {'items': PANELS},
    'districts': DISTRICTS,
    'page': {'ribbon': 'アイス島　案5b', 'small': '段々の丘の町：広場から大石段と城の石段で城門と天守へ3段で上る町', 'who': 'アイス島　全島（案5b・第59回）',
             'intro': '案5b「段々の丘の町」。町は飛行場と案内所の広場から北へ、円形劇場のように3段で上る。1段目は広場と下町（飛行場の前庭・並木の大通り・タヌキ商店とエイブル）。'
                      '広場の真北は2本並べた石の大石段で、両わきの塔の台に城の塔が立ち、上は並木の軸のテラス。そこから城への石段が3段目の城の丘（城門と天守の塔・正面の城壁と角の塔・自宅・天守の庭）へ続く。'
                      '飛行場 → 前庭 → 大通り → 広場 → 大石段 → 軸のテラス → 城への石段 → 城門 → 天守の塔 が1本の軸。'
                      '大石段の西は、2段目のレンガのかたまりを1段目の路地とパブの小広場で彫った「路地の町」で、路地のつきあたりはテラスの下をくぐる城の門、路地の頭の石段でつづら折りに上のテラスへ。'
                      '水は少なく、城の貯水池から2段の滝で落ちる運河1本（3マス）が、片がわは水から立つ倉庫のテラスの城壁、片がわは岸の道で、港の船だまりへ（町の水は陸の約8%）。'
                      '北は霊峰・竹林・森の台地（2段目）で、西のテラスの小道と北の街道で町とつながる。自然の川は2本：霊峰の池から滝で西の河口へ、森の泉から滝で東の谷を通って南の河口へ。'
                      '川向こうの東は村（風車の丘・中島のある池）、北東はハロウィンの尾根のくぼ地。'},
}
json.dump(spec, open(os.path.join(ROOT, f'designs/plan{PLAN}_spec.json'), 'w'), ensure_ascii=False, indent=1)
_bp = os.path.join(ROOT, f'designs/build_plan{PLAN}.json')
if not os.path.exists(_bp):   # plan3_fill.py が acnh_build.py を読むときに要る（中身は fill が書く）
    json.dump({'buildings': [], 'groups': [], 'inclines': {}, 'bridges': {}}, open(_bp, 'w'))
print(f'designs/plan{PLAN}_spec.json')
if __name__ == '__main__':
    if '--show' in sys.argv:
        print('    ' + ''.join(str(x // 10 % 10) if x % 10 == 0 else ' ' for x in range(X0, X1 + 1)))
        print('    ' + ''.join(str(x % 10) for x in range(X0, X1 + 1)))
        for j, r in enumerate(rows):
            print('%3d %s' % (Y0 + j, r))
