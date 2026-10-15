# 案6 設計の手引き（第60回：審美の skill で0から作りなおす）

## ユーザーが言ったこと（第60回）
- 「案5（5c 運河と市場の町）は8分、保留」。plan5c の物（tools/plan5c_design.py・designs/plan5c_spec.json・birdseye/plan5c-8pt.html）と案4 はさわらない。
- 新しい案は **案6**（tools/plan6_design.py → designs/plan6_spec.json、`ICE_PLAN=6`）。新しい artifact に出す（古いのは上書きしない）。
- 「完全用审美skill重新帮我从0开始造」：0から作る。審美の skill（island-aesthetics・island-planning・acnh-basics の ref/stunning.md）を設計の物差しにする。
- 先に直す案5の土台の弱い所（数は `tools/town_check.py`。案5c の値 → 案6 のねらい）：
  1. 北の列の家の真南に高いかたまりがあり、入口（門脸）がかくれる（5c：6軒 → **0軒**）
  2. 坂が4つだけ、2段目にほとんど上がれない（5c：坂4・町2・2段目以上の36%・3段目0 → **坂9〜10・町7以上・70%以上・3段目にも上がれる**）
  3. 市場が三方を水にかこまれた「堀」（5c：8.2% → **3%まで**）
  4. 灰色の平らな屋根が多すぎ（5c：屋根の64% → **30%まで**。屋根を減らし、テラスとして歩けるようにする。残る屋根は城壁の胸壁・屋上の庭・茶色のレンガ・3段目の芯）
  5. 軸のつきあたりが小さな塔1つ（→ **城門＋主塔＋石段の双塔**）
  6. 広場が大きなベージュのかたまり（広場12×10 は物も道も置けない → **まわりで額縁にする**：並木・建物の正面・石段・見下ろすテラス。広場のまわり3マスに木8本以上）
- 借りる物：
  - 案5a から **滝**（上の町の2段目・3段目の水路から1段目へ落ちる。南を向く＝カメラから見える）・**通りにそった運河**（片がわは通り＋岸壁、片がわは水から立つ壁。運河から2マス以内の通り20マス以上）・**井戸の石段**（上の段を切りこんだ「井戸」に坂を下ろし、通りを横切らない。2つ以上）
  - 案5b から **双塔**（大石段の両わきの3段目の台に castle tower）・**城門**（castle gate 3×1）・**主塔**（天守：3段目の castle tower）
- そのあと：地区ごとに見せ場（plan4_kitcheck.py）・木を植える・3人（作例に近いか／ゲームの決まり／構図）で点をつける。
- 説明の吹き出しは鳥瞰の下（島をかくさない）。

## いつも守る決まり（skill acnh-basics・acnh-buildable・island-planning・island-aesthetics）
- あつ森に本当にある物だけ：家具は目録（designs/acnh_catalog.json）の名前、マイデザインは designs/catalog.json の MA コードのある物。坂と橋はそれぞれ10まで。
- 建物：住民の家10（4×4）・自宅 5×4・博物館 7×4・タヌキ商店 7×4・エイブル 5×4・キャンプ場 4×4。入口は南。まわり1マスは同じ段の平地、入口の前（3×2）はあける、建物どうし1マス。
- 崖：2マス幅から。3段目は2段目の1マス内側。浜のとなりに崖を作らない（海岸から2マス）。
- 坂：2×4（上の段1マス＋下の段3マス）、まっすぐな崖、まわり1マスに別の坂なし、水に向けない。橋：幅4・水3〜5マス・岸が平行・まわり1マスに段ちがいの陸なし。
- 木は島で185本まで（森から町へ植えかえる）。崖・水・浜・建物・坂・橋のとなりに植えない（spec の street_trees はゲームの決まりで確かめて植える）。
- 8×8 マスで物は45マス未満、同じ物は6個まで。
- **カメラは南から北を見る**：見せ場・パネル・小物は南を向く所に。家の真裏・高い段の北どなり（崖の裏）・北向きのパネルに物を置かない（spec に `camera_check: true` で自動の物もよける）。
- **屋根に通りの柄を敷かない**：歩いて上がれないかたまり（屋根）の上に、spec の通り（- + #）を描かない（`town_check.py` の「上がれない段の上の道」＝0）。
- 町の水は町の陸の約1割（test は 7〜13%）。複雑さは水ではなく、台地（1・2・3段）・石段・路地（2マス）・中庭で出す。

## 作例（ユーザーのめっちゃいい。SCRATCH/img_top/*.jpg、URL は designs/refs.json の no）
R-1233・R-1148・R-0088（城壁の上の通り・運河の岸壁・石畳の通り・花の荷車）、R-1231・X-0003（レンガの擁壁・胸壁・石段・カフェ・中庭）、R-1235（港）、R-0849・R-0862〜R-0871（ハリー・ポッターの町の路地）、R-0877・R-0878（パブ）、R-1103・R-1148・R-1150（空港前の石畳と噴水）、R-1217・R-1225（キングス・クロス）、R-1266・R-1267（ビッグ・ベン）、R-1271・R-1274（ロンドン橋）、X-0006・X-0010・X-0011。
読みとり：レンガの擁壁（崖のすそのパネル）と上の胸壁（castle wall）・せまくまっすぐな石畳の通り（板石の縁）・壁ぞいの街灯と花の荷車・運河の岸壁とヨット・石段の左右の壁・中庭のカフェ・木の植えます。**密・層・額縁**。

## 道具（そろっている）
- 設計書：`tools/plan6X_design.py` → `designs/plan6X_spec.json`（形式は tools/plan5c_design.py と同じ：canvas の1マスずつの図・draw・water・inclines・bridges・buildings・streets・routes・zones・landmarks・panels・street_trees・districts・page）。
  記号（canvas）：`1 2 3`＝段の地面、`- + #`＝その段の通り、`~ = ^`＝1・2・3段目の水、空白＝さわらない。
- 案6 で足した spec の項目：
  - `axis: {"x0","x1","y0","y1","term_rows"}`：飛行場 → 広場 → 石段 → 塔の帯（x0〜x1、北のはし y0 から term_rows 列がつきあたり）。
  - `town_targets`：test_plan3.js の案6 の点検の目標（下の表）。
  - `camera_check: true`（自動の物をカメラから見えない所に置かない）・`paths: {"C": {"kind": "custom", "design": "stone_old"}}`（町の通りを old stone road：灰色の丸い石畳と白い板石の縁、R-1233 に近い）・`roof_kinds: {"2": [...], "3": [...]}`（屋根の種類：slate＝灰色のレンガ・garden＝屋上の庭・red＝茶色のレンガ・fort＝城壁の胸壁）。
- 組み立てと点検（すべて OK にする）：
  ```
  python3 tools/plan6X_design.py && ICE_PLAN=6X SEED=6 bash tools/plan3_build.sh
  ICE_PLAN=6X node tools/test_plan3.js          # すべて OK
  ICE_PLAN=6X python3 tools/plan4_kitcheck.py --built   # 歩けなくなる道 0
  ICE_PLAN=6X python3 tools/town_check.py       # 町の土台の数（案5の弱い所）
  ICE_PLAN=6X python3 tools/plan4_kitcheck.py --map 12,36,76,84   # 文字の地図
  ```
- 鳥瞰図：`bash SCRATCH/render.sh 6X SCRATCH/r60/6X '[["bird","day","bird"],["cam:34,2,58,0.8,42","day","axis"]]'`（cam の X,Y は寄るマス、0.8 は見下ろす角度、42 は距離。画像は Read で見る）。

## town_targets（案6 のねらい）
```
{"inclines": 9, "inclines_town": 7, "upper_walkable_pct": 70, "tier3_walkable": 20, "moat_pct": 3, "water_pct": [7, 13],
 "roof_grey_pct": 30, "town_trees": 45, "plaza_trees": 8, "hidden_items": 6, "well_stairs": 2, "canal_street": 20}
```

## 動かせない物
- 島 112×96。海・浜・岩・案内所の広場（x25〜36・y62〜71、物も道も置けない。案内所の建物はその奥のまん中）・飛行場（x29〜39・y84〜89、出口の道は (34,82)）・河口（西 (11,37)(12,37)(13,38〜40)、南 (70〜73,83)）。
- 住民：町に6人（Raymond・Maelle・Truffles・Deena・Ed・Pecan）、ほか Genji（J 霊峰）・Muffy（H ハロウィン）・Bea・Scoot（S 村）。自宅・博物館・タヌキ商店・エイブル・キャンプ場。

## 審美の物差し（skill から）
- 骨組み → さかい → 区画（囲まれた部屋）→ 目じるし → 家具の順（island-planning）。北に背景、左右の片がわを囲み、南（手前）を開けて入口。
- 町は「彫った町」：2段目・3段目のレンガのかたまりのあいだを、1段目の通り（2〜4マス）と路地（2マス）で彫る。かたまりの崖の面は建物の正面（パネル）。
- **円形劇場の断面**：北ほど高く（1段 → 2段 → 3段）。家の列は自分より低い列の北に置く＝どの家も南から正面が見える。背の高い物は北、低い物は南。
- 目じるし：島の目じるし1つ（軸のつきあたりの主塔と城門）、地区ごとに1つ、曲がり角ごとに小さな目じるし。主役の正面への道（軸）には背の高い物を置かない。
- リズム：にぎやか → ひと休み → にぎやか。せまい路地の先でぱっと開ける。どの地区も同じ密度にしない。
- つまらなく見える理由（ref/stunning.md）：広すぎる道・まっすぐな線と整列だけ・平らな地面・同じ物のくり返し・高い物の詰めこみ・どこも同じ密度。
- 見せ場の採用は island-aesthetics の110点（テーマ25・役15・密度20・重ねすぎない15・地形15・作れる10・段差+10）で70点以上。

## 付録：作例の場面 → 目録の本物の家具（見せ場の設計の手がかり。名前は designs/acnh_catalog.json で確かめた）
| 作例 | 場面 | 使える家具（英語名・大きさ） |
|---|---|---|
| R-1233 | 城壁の上の石畳の通り・木箱の上のランタン・花の荷車・石段 | castle wall(2×1)・streetlamp・fire hydrant・manhole cover・wooden box＋lantern・garden wagon(2×1)・iron garden bench(2×1)・坂は stone staircase |
| R-1148・R-0088 | 運河の岸壁・ヨット・自転車・カフェ | yacht(3×2・陸の上)・log stakes（係留のくい）・cruiser bike(2×1)・iron-and-stone fence・outdoor table(2×1)＋iron garden chair・Festivale parasol(1.5×1.5)・garden wagon |
| R-1231 | 博物館前の広場・電話ボックス・スクーター・木の植えます | phone box・garden bench・scooter(2×1)・fountain(3×3)・imperial fence・round topiary・streetlamp |
| X-0003 | 中庭のカフェ・石段の左右の胸壁・植えますの木 | iron garden table＋iron garden chair・menu chalkboard・phone box（Brown）・fire hydrant・manhole cover・brick fence（植えますのふち）・stone staircase |
| R-1217 | キングス・クロスの門・左右の塔・トピアリー | castle gate(3×1・まん中をくぐれる)・castle tower(2×2)・castle wall・triangular topiary・round topiary・public bench(2×1)・streetlamp |
| R-0877・R-0878 | パブの店先 | barrel・menu chalkboard・standing shop sign・outdoor table・lantern・stacked bottle crates・signboard のマイデザイン（PUB） |
| R-1103・R-1150 | 空港前の噴水の前庭・時計・待合 | fountain / park fountain(3×3)・plaza clock・park clock・public bench・retro transportation stop(2×1)・street lamp with banners(2×1)・arrive_depart のマイデザイン |
| R-1235 | 港のカフェと船だまり | yacht・barrel・wooden box・fish container・rope fence・cruiser bike・scooter・outdoor table |
| R-0849・R-0862〜0871 | 本屋と路地の店先 | wooden bookshelf(2×0.5)・stack of books・display stand・stall(2×1)・flower display case(2×1)・flower stand(1.5×1.5)・window_hp のマイデザイン（パネル） |
- 1つの場面は関係のある3つ（ベンチ＋新聞＋コーヒー）。高い物は奥（北）、低い物は手前（南）。同じ組み方（テーブル＋いす＋街灯）を地区ごとにくり返さない。
- 傘（かさ）は手に持つ物で地面に置けない。パラソルは家具の Festivale parasol・mush parasol・beach chairs with parasol だけ。

## 第60回の最終審査で足した決まりと道具
- カメラの決まりを深く：2段高い崖は3列先・家の屋根は2列（3列目は同じ段の物だけ）うしろまで物をかくす。案内所と飛行場の屋根も（spec の `camera_roofs`）（plan3_fill の cam_ok・plan4_kitcheck・town_check でそろえる）。立てるマス（木・低木・建物・坂でない同じ段のマス）がとなりにない物は置かない（terrain_rules §6）。
- 花はゲームにある色だけ（acnh_build で確かめる）。ななめに崖・水・浜が接する木は植えない（植えられるか確かめていない）。
- spec の項目：`axis_paving`（軸の通りの別のマイデザイン）・`camera_roofs`・`no_route`（道を通さない四角）・`auto_kits`（野山の自動の見せ場）・`bush_clear`（低木を置かない四角）・`street_tree_kind`/`street_tree_tones`（町の木の種類と鳥瞰の色）。
- 鳥瞰図：縁の板石は壁のすそと水ぎわだけ・看板（PUB）・吊り看板・ドアのパネルを描く。
