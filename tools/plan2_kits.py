# 生成：python3 tools/plan2_kits.py → designs/kits.json（見せ場のキット）。第48回
# 第48回：見せ場のキット（ユーザーの「めっちゃいい」「いいね」の作例を、ゲームの目録の家具だけで組みなおしたもの）
# 座標はキットの左上 (0,0) から。北（y が小さい）が奥＝背の高い物、南が手前＝低い物（カメラは北を向く）
# items: [名前, dx, dy, 回転, 色, マイデザイン]  lines: 柵などの列（from〜to の長方形）  plants: 花と作物
import json
K = {}
def kit(id, name, size, ref, items, lines=(), plants=(), note=''):
    K[id] = {'name': name, 'size': size, 'ref': ref, 'items': [list(i) for i in items], 'lines': list(lines), 'plants': list(plants), 'note': note}
L = lambda item, a, b, **k: dict(item=item, **{'from': a, 'to': b}, **k)
P = lambda t, rect, colors=None, pattern='fill': dict(type=t, rect=rect, colors=colors or ['red'], pattern=pattern)

# ---- ロンドン ----
kit('lon_cafe', 'レンガの店先のカフェ（屋台・鉄のテーブル・花のワゴン）', [7, 4], ['X-0011', 'R-0878'], [
    ('stall', 0, 0, 0, 'White'), ('menu chalkboard', 2, 0), ('garden wagon', 4, 0, 0, 'Dark brown'), ('streetlamp', 6, 0, 0, 'Black'),
    ('iron garden chair', 0, 2, 0, 'Black'), ('iron garden table', 1, 2, 0, 'Black'), ('iron garden chair', 2, 2, 0, 'Black'),
    ('iron garden table', 4, 2, 0, 'Black'), ('iron garden chair', 5, 2, 0, 'Black'), ('cruiser bike', 5, 3, 0, 'Black'), ('stack of books', 3, 1, 0, 'Old')],
    note='作例の店の壁は、この後ろの崖のすそのパネル（レンガと窓のマイデザイン）')
kit('lon_square', '噴水の前庭（花のワゴン2台・鉄のいす・街灯）', [9, 7], ['R-1103'], [
    ('streetlamp', 0, 0, 0, 'Black'), ('garden wagon', 1, 0, 0, 'Dark brown'), ('fountain', 3, 1, 0, 'Gray'), ('garden wagon', 6, 0, 0, 'Dark brown'), ('streetlamp', 8, 0, 0, 'Black'),
    ('triangular topiary', 0, 2, 0, 'Green'), ('triangular topiary', 8, 2, 0, 'Green'),
    ('iron garden table', 1, 3, 0, 'Black'), ('iron garden chair', 1, 4, 0, 'Black'), ('iron garden table', 7, 3, 0, 'Black'), ('iron garden chair', 7, 4, 0, 'Black'),
    ('manhole cover', 4, 5, 0, 'Silver'), ('decorative pillar', 0, 6, 0, 'Whitestone marble'), ('decorative pillar', 8, 6, 0, 'Whitestone marble')],
    lines=[L('iron fence', [1, 6], [3, 6], var='Black'), L('iron fence', [5, 6], [7, 6], var='Black')])
kit('lon_benches', '八角の台のベンチ（花の台を囲むベンチ）', [5, 3], ['R-1225'], [
    ('streetlamp', 0, 0, 0, 'Black'), ('outdoor bench', 1, 0, 0, 'Black'), ('streetlamp', 4, 0, 0, 'Black'),
    ('flower stand', 1, 1, 0, 'Colorful'), ('iron garden bench', 3, 1, 1, 'Black'), ('iron garden bench', 0, 1, 1, 'Black')])
kit('lon_quay', '岸壁通り（鉄の柵・電話ボックス・スクーター・花壇）', [8, 3], ['R-1231', 'R-1148'], [
    ('phone box', 0, 0, 0, 'Red'), ('outdoor bench', 1, 0, 0, 'Black'), ('streetlamp', 3, 0, 0, 'Black'), ('flower bed', 4, 0, 0, 'Dark brown'), ('scooter', 6, 0, 0, 'Ivory'),
    ('manhole cover', 2, 1, 0, 'Silver'), ('cruiser bike', 5, 1, 0, 'Green')],
    lines=[L('iron fence', [0, 2], [7, 2], var='Black')], note='南のふち（y+2）は水ぎわの鉄の柵')
kit('lon_market', '屋台の路地（しまの屋台・木箱・たる・ランプの門）', [6, 4], ['R-1241', 'R-1130'], [
    ('stall', 0, 0, 0, 'Green'), ('stall', 2, 0, 0, 'Orange & silver'), ('barrel', 4, 0), ('stacked bottle crates', 5, 0),
    ('plain party-lights arch', 0, 2, 0, 'Dark wood'), ('wooden box', 4, 2, 0, 'Natural'), ('standing shop sign', 5, 2, 0, 'Black'),
    ('phone box', 5, 3, 0, 'Red'), ('tin bucket', 0, 3)], note='ランプの門（パーティーライト）は通り抜けられるアーチ')
kit('lon_records', 'レコードの屋台（DJブース・ギター・サックス）', [5, 3], ['R-1130'], [
    ('stall', 0, 0, 0, 'Black'), ('DJ\'s turntable', 2, 0, 0, 'Brown'), ('street organ', 4, 0, 0, 'Dark brown'),
    ('acoustic guitar', 0, 1, 0, 'Brown'), ('alto saxophone', 1, 1), ('cruiser bike', 3, 2, 0, 'Red')],
    lines=[L('rope fence', [0, 2], [2, 2])])
kit('lon_dock', '桟橋の船だまり（ヨット・たる・バケツ・浮き輪）', [7, 4], ['R-0187', 'R-1235'], [
    ('phone box', 0, 0, 0, 'Red'), ('barrel', 1, 0), ('stacked fish containers', 2, 0, 0, 'Gray'), ('streetlamp', 3, 0, 0, 'Black'), ('fish-drying rack', 4, 0, 0, 'Fish'), ('tire stack', 6, 0),
    ('yacht', 0, 1, 0, 'White'), ('tin bucket', 3, 1), ('wooden bucket', 3, 2), ('yacht', 4, 1, 0, 'Brown'), ('life ring', 6, 3, 0, 'Red'), ('anchor statue', 3, 3, 0, 'Black')])
kit('lon_books', '屋根のない本屋（本棚の壁・地球儀・机）', [6, 4], ['X-0006', 'R-0870'], [
    ('wooden bookshelf', 0, 0, 0), ('wooden bookshelf', 2, 0, 0), ('wooden bookshelf', 4, 0, 0),
    ('antique table', 1, 1, 0, 'Brown'), ('globe', 3, 1, 0, 'Sepia'), ('stack of books', 4, 1, 0, 'Old'), ('strapped books', 5, 1, 0, 'Brown'),
    ('book stands', 0, 2, 0, 'Navy blue'), ('vintage stool', 3, 2, 0, 'Brown'), ('streetlamp', 5, 3, 0, 'Black'), ('monstera', 0, 3, 0, 'Black')])
kit('lon_pub', '川沿いのパブ（カウンター・たる・ピアノ・黒板）', [6, 4], ['R-0877'], [
    ('upright piano', 0, 0, 0, 'Walnut'), ('barrel', 2, 0), ('barrel', 3, 0), ('menu chalkboard', 4, 0), ('streetlamp', 5, 0, 0, 'Black'),
    ('counter table', 1, 2, 0, 'Brick & natural wood'), ('counter table', 3, 2, 0, 'Brick & natural wood'),
    ('counter chair', 1, 3, 0, 'Dark wood'), ('counter chair', 2, 3, 0, 'Dark wood'), ('counter chair', 4, 3, 0, 'Dark wood'), ('barrel', 0, 3)])
kit('lon_station', '9¾番線（汽車・時計・電話・本のワゴン）', [8, 4], ['X-0010', 'R-1134', 'R-1118'], [
    ('park clock', 0, 0, 0, 'Black'), ('plaza train', 2, 0, 0, 'Classic'), ('phone box', 5, 0, 0, 'Red'), ('streetlamp', 7, 0, 0, 'Black'),
    ('handcart', 1, 2, 0, 'Brown'), ('stack of books', 2, 2, 0, 'Old'), ('strapped books', 3, 2, 0, 'Red'), ('public bench', 5, 2, 0, 'Monotone'), ('barrel', 7, 2),
    ('cruiser bike', 0, 3, 0, 'Black')], note='汽車は「ひろばのきしゃ」（Classic の色は黒い機関車）。9¾ の看板は後ろの崖のパネルに sign_934 のマイデザイン')
kit('lon_crossing', '交差点（信号・消火栓・ゴミ箱・自販機・バス停）', [6, 3], ['R-0849'], [
    ('crosswalk signal', 0, 0, 0, 'Black'), ('retro transportation stop', 1, 0, 0, 'Red'), ('drink machine', 3, 0, 0, 'Red'), ('round streetlight', 4, 0, 0, 'Black'), ('crosswalk signal', 5, 0, 0, 'Black'),
    ('fire hydrant', 0, 2, 0, 'Red'), ('steel trash can', 5, 2, 0, 'Black')])
kit('lon_garden', '駅前の生け垣の庭（噴水・バラ・ベンチ・電球の門）', [9, 6], ['R-1217'], [
    ('streetlamp', 0, 0, 0, 'Green'), ('plain party-lights arch', 3, 0, 0, 'Dark wood'), ('streetlamp', 8, 0, 0, 'Green'),
    ('fountain', 3, 2, 0, 'White'), ('round topiary', 1, 2, 0, 'Green'), ('round topiary', 7, 2, 0, 'Green'),
    ('outdoor bench', 0, 5, 0, 'Black'), ('outdoor bench', 7, 5, 0, 'Black')],
    lines=[L('hedge', [0, 1], [2, 1]), L('hedge', [6, 1], [8, 1])],
    plants=[P('roses', [0, 2, 0, 4], ['red', 'yellow']), P('roses', [8, 2, 8, 4], ['red', 'yellow']), P('roses', [1, 3, 2, 4], ['red', 'white']), P('roses', [6, 3, 7, 4], ['red', 'white'])])

# ---- 村・郊外 ----
kit('cot_garden', 'コテージの庭（井戸・花のワゴン・ベンチ・ノーム）', [6, 4], ['R-1283', 'R-1289'], [
    ('brick well', 0, 0, 0, 'Red'), ('garden wagon', 2, 0, 0, 'White'), ('garden bench', 4, 0, 0, 'White'),
    ('garden gnome', 4, 2, 0, 'Sleepy gnome'), ('wooden bucket', 2, 2), ('garden lantern', 5, 3, 0, 'White')],
    plants=[P('tulips', [0, 2, 1, 3], ['pink', 'white']), P('cosmos', [3, 2, 3, 3], ['pink', 'white']), P('tulips', [2, 3, 4, 3], ['yellow', 'white'])])
kit('cot_greenhouse', '温室と白い柵の庭（温室だな・苗・道具）', [6, 4], ['R-0915'], [
    ('greenhouse box', 1, 0), ('tool shelf', 3, 0, 0, 'White'), ('potted starter plants', 5, 0, 0, 'Green'),
    ('garden faucet', 1, 2, 0, 'Red brick'), ('wooden toolbox', 4, 2, 0, 'Natural'), ('handcart', 2, 2, 0, 'Green')],
    lines=[L('lattice fence', [0, 0], [0, 3], var='White'), L('lattice fence', [1, 3], [5, 3], var='White')])
kit('tea_picnic', '森のあき地のお茶会（ナチュラルなテーブル・電球のアーチ）', [6, 5], ['R-1151', 'R-1157', 'R-1161', 'R-1163'], [
    ('plain party-lights arch', 1, 0, 0, 'Light wood'), ('lantern', 0, 0, 0, 'Yellow'), ('lantern', 5, 0, 0, 'Yellow'),
    ('natural garden chair', 1, 2, 0, 'Natural'), ('natural garden table', 2, 2, 0, 'Natural'), ('natural garden chair', 4, 2, 0, 'Natural'),
    ('picnic basket', 0, 4, 0, 'Red'), ('log stool', 2, 4, 0, 'White birch'), ('log stool', 3, 4, 0, 'White birch')],
    plants=[P('lilies', [5, 3, 5, 4], ['white'])])
kit('bakery', 'パン屋の屋台とブランチの席', [6, 4], ['R-1164', 'R-1160'], [
    ('stall', 0, 0, 0, 'Natural'), ('wooden box', 2, 0, 0, 'Natural'), ('menu chalkboard', 3, 0), ('flower stand', 4, 0, 0, 'Yellow'),
    ('garden chair', 0, 2, 0, 'White'), ('garden table', 1, 2, 0, 'White'), ('garden chair', 2, 2, 0, 'White'), ('organic bread', 2, 1), ('firewood', 5, 3)])
kit('formal_garden', '生け垣の中庭と噴水（ベンチ・円すいの木・像）', [9, 6], ['R-0904', 'R-0898', 'R-0907'], [
    ('fountain', 3, 1, 0, 'White'), ('triangular topiary', 1, 1, 0, 'Green'), ('triangular topiary', 7, 1, 0, 'Green'),
    ('garden bench', 0, 4, 0, 'White'), ('garden bench', 7, 4, 0, 'White'), ('beautiful statue', 4, 5)],
    lines=[L('hedge', [0, 0], [8, 0]), L('hedge', [0, 1], [0, 3]), L('hedge', [8, 1], [8, 3])],
    plants=[P('roses', [1, 2, 2, 3], ['white', 'pink']), P('roses', [6, 2, 7, 3], ['white', 'pink'])])
kit('allotment', '市民農園（作物の列・かかし・道具だな）', [7, 5], ['R-1284', 'R-1288'], [
    ('wooden field sign', 0, 0, 0, 'Flower'), ('tool shelf', 2, 0, 0, 'Green'), ('potted starter plants', 4, 0, 0, 'Black'), ('water pump', 6, 0, 0, 'Green'),
    ('scarecrow', 3, 2), ('garden wagon', 5, 4, 0, 'Green')],
    plants=[P('tomatoes', [0, 2, 2, 2]), P('carrots', [4, 2, 6, 2], ['green']), P('pumpkins', [0, 4, 3, 4], ['orange', 'yellow', 'white'])])

# ---- 日本 ----
kit('jp_tea', '池のほとりの茶席（ししおどし・とうろう・たけのスクリーン）', [6, 3], ['R-1159'], [
    ('tall lantern', 0, 0, 0, 'Mossy'), ('bamboo partition', 1, 0, 0, 'Green bamboo'), ('bamboo partition', 3, 0, 0, 'Green bamboo'), ('deer scare', 5, 0, 0, 'Green bamboo'),
    ('zen cushion', 1, 1), ('tea table', 2, 1, 0, 'Dark wood'), ('zen cushion', 4, 1), ('mossy garden rock', 0, 2), ('tall garden rock', 5, 2)])

# ---- ハロウィン ----
kit('spooky_yard', 'お化け屋敷の前の墓場（ハロウィンの家具・せきひ・がいこつ）', [8, 4], [], [
    ('spooky tree', 0, 0, 0, 'Orange'), ('spooky tower', 2, 0, 0, 'Orange'), ('spooky lantern set', 3, 1, 0, 'Orange'), ('decayed tree', 6, 0, 0, 'Dark brown'),
    ('stone tablet', 2, 2, 0, 'Mossy'), ('stone tablet', 4, 2, 0, 'Mossy'), ('creepy skeleton', 5, 2, 0, 'Plain'), ('spooky scarecrow', 0, 3, 0, 'Orange'), ('candle', 7, 3, 0, 'Black')],
    lines=[L('spooky fence', [1, 3], [6, 3])])

# ---- 港 ----
kit('harbor_quay', '船着き場（干物・魚のコンテナ・浮き輪・いかり）', [8, 3], ['R-1235'], [
    ('fish-drying rack', 0, 0, 0, 'Fish'), ('fish-drying rack', 2, 0, 0, 'Squid'), ('stacked fish containers', 4, 0, 0, 'Light blue'), ('fish container', 5, 0, 0, 'Yellow'), ('barrel', 6, 0), ('streetlamp', 7, 0, 0, 'White'),
    ('life ring', 0, 2, 0, 'Red'), ('anchor statue', 3, 2, 0, 'Retro'), ('wooden box', 5, 2, 0, 'Natural'), ('tire stack', 7, 2)])

json.dump({'note': '見せ場のキット（第48回）。ユーザーのいいねの作例（ref）をゲームの目録の家具だけで組みなおした。build_plan2.json の groups で {"kit": id, "at": [x, y], "flip": true} として置く。北（y の小さい側）に背の高い物', 'kits': K},
          open('/home/user/Atsumori-ICE/designs/kits.json', 'w'), ensure_ascii=False, indent=1)
print(len(K), 'kits')
