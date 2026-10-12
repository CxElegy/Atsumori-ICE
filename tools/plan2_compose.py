# 生成：python3 tools/plan2_compose.py → designs/build_plan2.json の groups・ground・plants を書きかえる（第48回）。そのあと python3 tools/acnh_build.py
# 第48回：島の見せ場を組みなおす（キット・崖のすそのパネルの壁・地面のマイデザイン・花）。build_plan2.json の groups・ground・plants を書きかえる
import json
R = '/home/user/Atsumori-ICE/'
B = json.load(open(R + 'designs/build_plan2.json'))
G, GROUND, PL = [], [], []
def kit(id, kitid, at, flip=False, name=None, ref=None, note='', lines=()):
    g = {'id': id, 'zone': id.split('-')[0], 'kit': kitid, 'at': at, 'flip': flip, 'items': [], 'lines': list(lines)}
    if name: g['name'] = name
    if ref: g['ref'] = ref
    if note: g['note'] = note
    G.append(g)
def grp(id, name, items=(), lines=(), ref=None, note=''):
    g = {'id': id, 'zone': id.split('-')[0], 'name': name, 'at': [0, 0], 'items': [list(i) for i in items], 'lines': list(lines)}
    if ref: g['ref'] = ref
    if note: g['note'] = note
    G.append(g)
L = lambda item, a, b, **k: dict(item=item, **{'from': a, 'to': b}, **k)
def ground(id, style, rect, design, skip=()):
    GROUND.append({'id': id, 'style': style, 'rect': rect, 'design': design, 'skip': [list(s) for s in skip]})
def plant(id, t, rect, colors, pattern='fill', skip=()):
    PL.append({'id': id, 'type': t, 'rect': rect, 'colors': colors, 'pattern': pattern, 'skip': [list(s) for s in skip]})
WALL = dict(var='Brown', design='wall_windows_bricks')   # 崖のすそのレンガの壁（シンプルなパネル＋マイデザイン）
WALL2 = dict(var='Brown', design='wall_brick_lamp')

# ======== ロンドン市内 ========
# 地面：町の広場・河岸・市場をマイデザインで敷きつめる（道は地形の道＝シックないしだたみ）
ground('C', 'herring', [18, 55, 30, 59], 'brick_arch')            # 博物館の前の通りの南（本屋とカフェの前）
ground('C', 'flag', [40, 61, 42, 66], 'stone_old')                # 高台の西のはし（大階段の上の見晴らし台）
ground('C', 'flag', [45, 61, 45, 66], 'stone_old')
ground('C', 'cobble', [38, 67, 42, 69], 'road_chic_stone')        # 岸壁通り
ground('C', 'brick', [57, 61, 68, 66], 'brick_vintage_red')       # 東の河岸の市場
ground('C', 'brick', [55, 69, 60, 70], 'brick_vintage_red')
ground('C', 'brick', [63, 69, 67, 70], 'brick_vintage_red')
ground('C', 'flag', [27, 74, 35, 80], 'brick_greige')             # 南岸の駅前の庭
ground('C', 'herring', [47, 75, 52, 80], 'brick_arch')            # 南岸のパン屋
ground('C', 'plank', [52, 78, 58, 80], 'plank')                   # 船だまりの板の桟橋
ground('C', 'flag', [59, 74, 68, 80], 'stone_curved')             # ドックランズの広場
ground('C', 'herring', [44, 48, 54, 53], 'versailles')
ground('C', 'herring', [18, 52, 30, 52], 'brick_arch')            # 博物館の前の敷石            # リージェンツ・パーク（幾何学の庭）
ground('C', 'leaves', [17, 72, 23, 82], 'brick_autumn')           # ハイドパークの落ち葉の小道
ground('C', 'flag', [13, 61, 23, 66], 'brick_greige')             # スピーカーズ・コーナー
ground('C', 'garden', [40, 54, 67, 58], 'brick_greige')            # 高台の住民の家の前庭（建物の土地はよける）
ground('C', 'garden', [33, 59, 39, 60], 'brick_greige')
kit('C-cross', 'lon_crossing', [33, 58], name='北の大通りの交差点（信号・バス停・自販機）', ref=['R-0849'])
# 崖のすその壁（パネル）と見せ場
grp('C-terrace', '高台の通り（住民の家4軒とエイブル・2段目）',
    [('streetlamp', 45, 58, 0, 'Black'), ('streetlamp', 50, 58, 0, 'Black'), ('streetlamp', 55, 58, 0, 'Black'), ('streetlamp', 61, 58, 0, 'Black'),
     ('phone box', 40, 57, 0, 'Red'), ('fire hydrant', 40, 58, 0, 'Red'), ('steel trash can', 66, 58, 0, 'Black'),
     ('tourist telescope', 67, 59, 0, 'Black'), ('plaza bench', 66, 55, 0, 'Classic'), ('round streetlight', 67, 57, 0, 'Black')],
    [L('iron fence', [46, 61], [55, 61], var='Black', skip=[[47, 61], [48, 61], [52, 61], [53, 61]])],
    ref=['R-0849'], note='本物の住民の家（ジャック・アンヌ・トンコ・まりも）とエイブルの前の通り。切り通しの頭に鉄の柵')
grp('C-view', '大階段の上の見晴らし台（2段目の西のはし）',
    [('crosswalk signal', 42, 61, 0, 'Black'), ('crosswalk signal', 45, 61, 0, 'Black'), ('flower stand', 40, 61, 0, 'Colorful'), ('iron garden bench', 40, 64, 1, 'Black'),
     ('street lamp with banners', 41, 65, 0, 'Black'), ('round topiary', 45, 63, 0, 'Green'), ('streetlamp', 45, 65, 0, 'Black')],
    [L('brick fence', [40, 66], [42, 66]), L('brick fence', [45, 66], [45, 66])],
    note='2段目のふちにレンガの柵（胸壁）。下の岸壁通りから見ると、崖のパネルの壁の上に柵が乗って城壁に見える')
grp('C-quay', '岸壁通り（崖のすそのレンガの壁・アーチ窓）',
    [('phone box', 38, 67, 0, 'Red'), ('streetlamp', 39, 67, 0, 'Black'), ('scooter', 38, 68, 0, 'Ivory'), ('flower bed', 40, 68, 0, 'Dark brown'), ('streetlamp', 42, 68, 0, 'Black'), ('outdoor bench', 39, 69, 0, 'Black'), ('manhole cover', 42, 69, 0, 'Silver')],
    [L('simple panel', [40, 67], [42, 67], **WALL), L('simple panel', [45, 67], [45, 67], **WALL)],
    ref=['R-1231', 'R-1233'], note='2段目の崖のすそ（y67）にレンガと窓のマイデザインのパネルを並べ、崖をレンガの擁壁に見せる')
grp('C-cut', '切り通しの運河と曳舟道（1段目）',
    [('stall', 54, 65, 1, 'Green'), ('barrel', 54, 67), ('stacked bottle crates', 46, 62), ('barrel', 46, 63), ('streetlamp', 46, 65, 0, 'Black'), ('garden wagon', 46, 66, 1, 'Green'), ('streetlamp', 54, 63, 0, 'Black'), ('wooden box', 54, 62, 0, 'Natural')],
    ref=['R-1233', 'R-1241'])
kit('C-market', 'lon_market', [57, 63], name='東の河岸の市場（屋台の路地）', ref=['R-1241'])
kit('C-records', 'lon_records', [63, 63], name='東の河岸のレコードの屋台', ref=['R-1130'])
grp('C-marketwall', '東の河岸の市場の奥（崖のすそのレンガの店先）', [],
    [L('simple panel', [57, 61], [61, 61], **WALL), L('simple panel', [62, 61], [67, 61], **WALL2)],
    note='高台の東の崖（2段目）のすそにパネルの店先を並べ、市場の背景の「建物の壁」にする')
grp('C-eastst', '東の河岸通り（花壇・自転車・街灯）',
    [('flower bed', 55, 69, 0, 'Dark brown'), ('cruiser bike', 57, 69, 0, 'Green'), ('streetlamp', 59, 69, 0, 'Black'), ('streetlamp', 63, 69, 0, 'Black'), ('iron garden bench', 64, 69, 0, 'Black'), ('fire hydrant', 66, 69, 0, 'Red')])
grp('C-tower', 'タワーブリッジ（レンガの橋と城の塔）',
    [('castle tower', 41, 75, 0, 'Gray'), ('castle tower', 47, 74, 0, 'Gray'), ('street lamp with banners', 46, 69, 0, 'Black')],
    ref=['R-1274'], note='あつ森の橋は平ら。レンガの橋の南のたもとに「おしろのとう」（ver 2.0）を立てる')
grp('C-plaza', '案内所の広場のまわり（トラファルガー広場）',
    [('valiant statue', 38, 62), ('gallant statue', 38, 65), ('round streetlight', 38, 61, 0, 'Black'),
     ('street lamp with banners', 22, 62, 0, 'Black'), ('round streetlight', 23, 68, 0, 'Black'), ('park clock', 23, 61, 0, 'Black')],
    note='広場（P）には物を置けない。広場をかこむ道の外に像と街灯')
kit('C-books', 'lon_books', [18, 56], name='屋根のない本屋（博物館通り）', ref=['X-0006', 'R-0870'])
kit('C-cafe', 'lon_cafe', [24, 56], name='レンガの店先のカフェ（博物館通り）', ref=['X-0011', 'R-0878'])
grp('C-shopwall', '博物館通りの店の壁（パネル）', [],
    [L('simple panel', [18, 55], [23, 55], **WALL), L('simple panel', [24, 55], [30, 55], **WALL2)],
    note='北の背景にパネルの店の壁（2階建ての店は作れないので、パネルの1列）')
grp('C-museum', 'ブルームズベリー（博物館の前）',
    [('sphinx', 27, 49, 0), ('decorative pillar', 18, 49, 0, 'Whitestone marble'), ('decorative pillar', 27, 51, 0, 'Whitestone marble'), ('streetlamp', 18, 51, 0, 'Black'), ('streetlamp', 29, 51, 0, 'Black')])
kit('C-regent', 'formal_garden', [44, 48], name='リージェンツ・パーク（生け垣の中庭と噴水）', ref=['R-0904', 'R-0913'])
grp('C-speak', 'スピーカーズ・コーナー（広場の西）',
    [('outdoor bench', 14, 62, 0, 'Green'), ('outdoor bench', 18, 62, 0, 'Green'), ('park clock', 16, 64, 0, 'Black'), ('streetlamp', 13, 64, 0, 'Black'), ('streetlamp', 21, 64, 0, 'Black'), ('flower stand', 19, 64, 0, 'Red')],
    [L('hedge', [13, 61], [21, 61])])
plant('C-speak', 'tulips', [14, 66, 22, 66], ['red', 'white'])
kit('C-kx', 'lon_garden', [27, 75], name='キングス・クロスの庭（南岸の西）', ref=['R-1217'])
grp('C-south', '南岸の駅前（タヌキ商店・バス停）',
    [('retro transportation stop', 47, 80, 0, 'Red'),  ('streetlamp', 42, 81, 0, 'Black')])
kit('C-bakery', 'bakery', [47, 76], name='南岸のパン屋とブランチの席', ref=['X-0011', 'R-1164'])
grp('C-docks', '船だまり（板の桟橋・ヨット）',
    [('yacht', 53, 78, 0, 'White'), ('anchor statue', 52, 78, 0, 'Black'), ('tin bucket', 52, 80), ('barrel', 56, 78), ('stacked fish containers', 57, 78, 0, 'Gray'), ('life ring', 56, 79, 0, 'Red'), ('phone box', 58, 79, 0, 'Red'), ('wooden box', 57, 79, 0, 'Natural')],
    ref=['R-0187', 'R-1235'])
grp('C-plaza2', 'ドックランズの広場（観覧車とメリーゴーランド）',
    [('plaza ferris wheel', 63, 75, 0, 'Classic'), ('plaza merry-go-round', 63, 78, 0, 'Classic'), ('plaza bench', 66, 77, 1, 'Classic'), ('plaza clock', 62, 77, 0, 'Classic'),
     ('plaza balloon wagon', 66, 79, 0, 'Classic'), ('plaza arch', 62, 74, 0, 'Classic')],
    note='ロンドン・アイは作れない。ゲームの「ひろばのかんらんしゃ」（3×2）と「ひろばのメリーゴーランド」')
kit('C-hyde', 'tea_picnic', [17, 73], name='ハイドパークの林のお茶会', ref=['R-1157', 'R-1161'])
kit('C-station', 'lon_station', [14, 78], name='林の小さな駅（9¾番線）', ref=['X-0010', 'R-1134'])

# ======== 村（川の南）========
grp('S-pecan', 'レベッカの家の庭（花の小道のコテージ）', [('brick well', 13, 42, 0, 'Red'), ('garden wagon', 13, 44, 0, 'White'), ('garden gnome', 15, 42, 0, 'Sleepy gnome'), ('wooden bucket', 15, 43)], ref=['R-1283'])
plant('S-pecan', 'tulips', [15, 44, 15, 44], ['pink', 'white'])
ground('S', 'garden', [13, 45, 16, 45], 'brick_city_old')
grp('S-hedge', 'レベッカの家のうらの生け垣', [], [L('hedge', [16, 41], [21, 41])])
kit('S-bea', 'cot_greenhouse', [30, 42], name='ベーグルの家のとなりの温室', ref=['R-0915', 'R-1289'])
ground('S', 'garden', [35, 42, 44, 45], 'brick_city_old')
kit('S-square', 'bakery', [38, 42], name='村の広場（橋のたもと・パン屋の屋台）', ref=['R-1164', 'R-1160'])
grp('S-green', '村の緑地（ブランコのベンチ）', [('swinging bench', 36, 42, 0, 'White wood'), ('garden lantern', 37, 44, 0, 'White'), ('signpost', 44, 45, 0, 'Shop')])
plant('S-green', 'cosmos', [36, 45, 37, 45], ['pink', 'white'])
grp('S-mill', '村の東のはずれの農家（風車とサイロ）',
    [('windmill', 53, 42, 0, 'White'), ('silo', 55, 42, 0, 'Red & brown'), ('hay bed', 53, 45, 0, 'Brown'), ('wooden box', 56, 45, 0, 'Natural'), ('firewood', 52, 45)],
    note='水車は家具にない。ゲームの「ふうしゃ」（牧場の風車 2×2）とサイロ')
PL.append({'id': 'S-river', 'type': 'hyacinths', 'rect': [13, 40, 34, 41], 'colors': ['blue', 'white', 'purple', 'pink'], 'pattern': 'fill', 'fit': True})   # 村の家の裏、川ぞいの花
grp('S-river', '村の家の裏の川ぞいの花とベンチ', [('garden bench', 28, 38, 0, 'White'), ('fishing-rod stand', 31, 38, 0, 'Natural')])
ground('S', 'leaves', [26, 39, 33, 39], 'stone_natural')   # 川ぞいの小道（竹林の道から）
# ======== 東の郊外 ========
kit('S-allot', 'allotment', [62, 30], name='村の畑（市民農園）', ref=['R-1284', 'R-1288'])
plant('S-field', 'cosmos', [62, 36, 71, 38], ['yellow', 'orange', 'pink', 'white'], 'rows')
grp('S-home', '自宅の前（菜園）', [('scarecrow', 71, 45), ('water pump', 70, 45, 0, 'Green')],
    [L('hedge', [64, 40], [70, 40]), L('hedge', [64, 41], [64, 44])])
plant('S-home', 'wheat', [70, 41, 71, 44], ['gold'])
grp('S-orchard', 'ガゼボの庭（桃の木のそば）', [('gazebo', 61, 43, 0, 'White')], ref=['R-1291'])
grp('S-ranch', '牧場（横板の柵・干し草・トラクター）',
    [('hay bed', 73, 50, 0, 'Brown'), ('hay bed', 73, 52, 0, 'Pale green'), ('tractor', 81, 50, 0, 'Red'), ('silo', 84, 52, 0, 'Red & brown'), ('water pump', 76, 51, 0, 'Rust')],
    [L('corral fence', [71, 48], [78, 48]), L('corral fence', [73, 54], [78, 54]), L('corral fence', [80, 48], [85, 48]), L('corral fence', [80, 54], [85, 54])],
    ref=['R-1292'], note='動物は置けない。柵で囲んだ牧草地と干し草のベッド・トラクター')
kit('S-garden', 'formal_garden', [88, 42], name='東の丘の庭園（生け垣の中庭と噴水）', ref=['R-0904', 'R-0898'])
grp('S-lake', '東の丘の湖のガゼボと風車', [('gazebo', 86, 48, 0, 'White'), ('windmill', 89, 51, 0, 'White'), ('garden bench', 96, 47, 1, 'White')], ref=['R-0897'])
# ======== 日本・竹林 ========
grp('J-shrine', '霊峰の頂（あずまやの社・五重塔・どら）',
    [('azumaya gazebo', 21, 16, 0, 'Natural'), ('pagoda', 18, 17, 0, 'Red'), ('gong', 25, 17, 0, 'Red'), ('stone lion-dog', 21, 20, 0, 'Natural'), ('stone lion-dog', 24, 20, 0, 'Natural'),
     ('tall lantern', 20, 22, 0, 'Natural'), ('tall lantern', 25, 22, 0, 'Natural'), ('torii', 21, 24, 0, 'Vermilion'), ('paper lantern', 19, 20, 0, 'Natural wood'), ('mossy garden rock', 26, 20)],
    note='社は作れないので、あずまや（3×3）を社に見立てる。鳥居は通り抜けられるアーチ')
ground('J', 'moss', [19, 19, 26, 23], 'stone_natural')
grp('J-torii', '千本鳥居（2段目の参道）とあんどん', [('torii', 21, 29, 0, 'Vermilion'), ('torii', 21, 31, 0, 'Vermilion'), ('torii', 21, 33, 0, 'Vermilion'), ('paper lantern', 21, 30, 0, 'Natural wood'), ('paper lantern', 21, 32, 0, 'Natural wood'), ('paper lantern', 21, 34, 0, 'Natural wood'), ('tall lantern', 24, 34, 0, 'Mossy')])
grp('J-genji', 'ゲンジの家と池泉の茶席', [('zen bench', 29, 32, 0), ('tall lantern', 32, 32, 0, 'Mossy'), ('deer scare', 32, 33, 0, 'Green bamboo'), ('tea table', 29, 34, 0, 'Dark wood'), ('zen cushion', 31, 34), ('zen cushion', 31, 35), ('mossy garden rock', 32, 35), ('bamboo partition', 29, 33, 0, 'Green bamboo')], ref=['R-1159'], note='ゲンジ（瓦屋根の和風の住民の家）を池のほとりの茶室に。茶席は家の入口の前（3×2）をよけて東の岸に')
grp('B-fence', '竹林の道の竹垣', [('bamboo candleholder', 21, 39, 0, 'Green bamboo'), ('bamboo candleholder', 24, 39, 0, 'Green bamboo')], [L('green bamboo fence', [21, 42], [21, 45]), L('green bamboo fence', [24, 42], [24, 45])])
grp('B-gate', '竹林の門と川のはじまりのピクニック',
    [('torii', 21, 40, 0, 'Gray'), ('outdoor picnic set', 29, 39), ('picnic basket', 31, 39, 0, 'Red'), ('log bench', 29, 41, 0, 'Orange wood')], ref=['R-1172'])
ground('J', 'moss', [24, 32, 32, 33], 'stone_natural')            # ゲンジの家の前の苔の飛び石
grp('J-fence', 'ゲンジの家のたけがき', [], [L('bamboo lattice fence', [24, 27], [29, 27]), L('bamboo lattice fence', [24, 28], [24, 31])])
# ======== 森 ========
grp('F-camp', 'キャンプ場の前（たき火とまるたの柵）', [('campfire', 56, 22), ('log bench', 54, 21, 0, 'Dark wood'), ('log stakes', 57, 23), ('firewood', 55, 23)],
    [L('log fence', [56, 16], [61, 16]), L('log fence', [56, 17], [56, 20]), L('log fence', [61, 17], [61, 20])])
kit('F-tea1', 'tea_picnic', [63, 23], name='森のふちのお茶会（まるたの柵）', ref=['R-1163', 'R-1168'], lines=[L('log fence', [-1, -1], [6, -1])])   # キットの組の lines はキットの左上からの座標
grp('F-tea2', '森の長いテーブルのピクニック', [('log dining table', 51, 32, 0, 'Orange wood'), ('log stool', 50, 32, 0, 'Orange wood'), ('log stool', 53, 32, 0, 'Orange wood'), ('picnic basket', 51, 34, 0, 'Red'), ('lantern', 50, 34, 0, 'Yellow')], ref=['R-1151'])
grp('F-tea3', '森の小さなお茶の席（キノコ）', [('mush table', 47, 31, 0, 'Red mushroom'), ('mush low stool', 49, 31, 0, 'Red mushroom'), ('mush lamp', 47, 33)], ref=['R-1152'])
grp('F-tea4', '湖のほとりのお茶', [('cute tea table', 54, 36, 0, 'White'), ('fishing-rod stand', 56, 36, 0, 'Natural'), ('log stool', 55, 36, 0, 'White birch')], ref=['R-1159'])
# ======== ハロウィン ========
grp('H-gate', '尾根の切り通しの門', [('spooky arch', 77, 28, 0, 'Orange'), ('spooky lantern', 76, 27, 0, 'Orange'), ('spooky lantern', 80, 27, 0, 'Orange')])
plant('H-gate', 'pumpkins', [75, 30, 80, 30], ['orange', 'orange', 'white', 'yellow'])
grp('H-yard', 'フリルの家（お化け屋敷に見立てる）と墓場', [('spooky tree', 83, 20, 0, 'Orange'), ('spooky scarecrow', 83, 23, 0, 'Orange'), ('spooky tower', 84, 23, 0, 'Orange'), ('decayed tree', 91, 20, 0, 'Dark brown'), ('spooky lantern set', 90, 24, 0, 'Orange'), ('stone tablet', 91, 23, 0, 'Mossy'), ('stone tablet', 93, 23, 0, 'Mossy'), ('stone tablet', 92, 25, 0, 'Mossy'), ('creepy skeleton', 94, 25, 0, 'Plain'), ('candle', 93, 24, 0, 'Black'), ('spooky lantern', 85, 26, 0, 'Orange'), ('spooky lantern', 88, 26, 0, 'Orange')], [dict(item='spooky fence', **{'from': [91, 22], 'to': [94, 22]})], note='墓石は家具にないので「せきひ」。家はフリル（紫の屋根・黒い石の壁の住民の家）。入口の前（3×2）はあける')
grp('H-pond', '窪地の黒い池のほとり（馬車）', [('spooky carriage', 83, 31, 0, 'Monochrome'), ('decayed tree', 88, 32, 0, 'White')])
ground('H', 'leaves', [82, 24, 93, 33], 'brick_autumn')
# ======== 港町 ========
grp('P-cliff', '崖の上の町（マモルとキザノホマレの家・灯台）',
    [('lighthouse', 96, 58, 0, 'Red'), ('garden bench', 94, 61, 0, 'White'), ('streetlamp', 89, 66, 0, 'White'), ('anchor statue', 97, 65, 0, 'White')],
    [L('lattice fence', [97, 60], [97, 64], var='White'), L('hedge', [89, 57], [95, 57])])
plant('P-cliff', 'windflowers', [88, 69, 91, 72], ['blue', 'white'], 'checker')
plant('P-cliff', 'windflowers', [94, 69, 97, 72], ['blue', 'white'], 'checker')
kit('P-quay', 'harbor_quay', [80, 80], name='船着き場（干物・魚のコンテナ）', ref=['R-1235'])
ground('P', 'plank', [79, 79, 90, 83], 'plank')
grp('P-beach', '浜（ビーチベッドと監視台）', [('beach chairs with parasol', 90, 85, 0, 'Blue'), ('beach chairs with parasol', 93, 85, 0, 'Orange'), ('lifeguard chair', 96, 84, 0, 'Red'), ('surfboard', 98, 85), ('yacht', 82, 85, 0, 'Blue')])
grp('P-meadow', '港の道の東の花畑とリンゴ園', [('wooden field sign', 80, 62, 0, 'Flower'), ('picnic basket', 82, 63, 0, 'Red'), ('outdoor picnic set', 83, 62)])
grp('P-hedge', '花畑の南の生け垣', [], [L('hedge', [80, 64], [86, 64])])
PL.append({'id': 'P-meadow', 'type': 'cosmos', 'rect': [80, 56, 87, 61], 'colors': ['pink', 'white', 'red', 'pink'], 'pattern': 'fill', 'fit': True})
# 港の道の両がわの畑（作物と花の畑のつぎはぎ。作物・花は数の決まりがない）
grp('P-farm', '港の道の畑（サトウキビ・カボチャ・小麦・チューリップ）',
    [('scarecrow', 75, 66), ('scarecrow', 83, 67), ('wooden field sign', 73, 61, 0, 'Light green'), ('hay bed', 80, 70, 0, 'Brown'), ('garden wagon', 85, 70, 0, 'Brown'), ('water pump', 87, 74, 0, 'Rust'), ('tractor', 74, 78 - 4, 0, 'Green')],
    [L('hedge', [73, 71], [77, 71]), L('hedge', [80, 74], [84, 74])], note='作物と花の畑。生け垣で区切る（イギリスの田舎のつぎはぎの畑）')
PL.append({'id': 'P-farm', 'type': 'sugarcane', 'rect': [73, 53, 77, 60], 'colors': ['green'], 'pattern': 'rows', 'fit': True})
PL.append({'id': 'P-farm', 'type': 'pumpkins', 'rect': [73, 64, 77, 70], 'colors': ['orange', 'orange', 'yellow', 'white'], 'pattern': 'fill', 'fit': True})
PL.append({'id': 'P-farm', 'type': 'wheat', 'rect': [76, 72, 77, 77], 'colors': ['gold'], 'pattern': 'fill', 'fit': True})
PL.append({'id': 'P-farm', 'type': 'wheat', 'rect': [80, 65, 87, 69], 'colors': ['gold'], 'pattern': 'fill', 'fit': True})
PL.append({'id': 'P-farm', 'type': 'tulips', 'rect': [80, 75, 87, 77], 'colors': ['red', 'yellow', 'white', 'pink'], 'pattern': 'rows', 'fit': True})

B['groups'], B['ground'], B['plants'] = G, GROUND, PL
B['ground_styles'] = {'cobble': '石畳', 'herring': 'ヘリンボーンのレンガ', 'brick': '赤いレンガ', 'flag': '敷石', 'plank': '板の桟橋', 'leaves': '落ち葉の土', 'garden': '明るい石畳', 'moss': '苔むした石'}
json.dump(B, open(R + 'designs/build_plan2.json', 'w'), ensure_ascii=False, indent=1)
print(len(G), 'groups', len(GROUND), 'ground', len(PL), 'plants')
