repo: CxElegy/Atsumori-ICE
branch: main

## Last sync
date: 2026-10-11
- 第28回：作業ブランチの未統合分（ヨーロッパの石造りの街並みモジュール3種）を main に統合。全機能を github.md に一覧化
### Updated in this project
- 資料「更新の要件と仕組み」（2026-10-11）をもとに、main（11bba60）の上へ実装を追加
- 美的センスのSKILL・モジュールDB・地勢計画・見本の自動配置・完成イメージ・ゲーム画面・確認の道具

## Screen map
| screen | files |
|---|---|
| ブレスト | World Travel Island Brainstorm.dc.html |
| 計画書 v1〜v4 | World Travel Island Plan.dc.html, Plan v2/v3/v4.dc.html, island-grid*.json |
| 組み立て台 | Module Builder.dc.html, plan-terrain.json, modules-curated.json, samples.json |
| 完成イメージ（俯瞰） | London Render.dc.html |
| ロンドン 地形と川の再設計（審査の結果から） | London Redesign.dc.html, london-redesign.json |
| ゲーム画面 | Game View.dc.html |
| 組み方（旧・細部の1枚） | Module Guide.dc.html（ビルドガイドに統合ずみ） |
| **ビルドガイド（全部入り）** | tools/build_site.py + tools/site/template.html → ice-guide.html（作例の写真入りのため、リポジトリに入れず Artifact で公開） |

## ビルドガイドの機能（1枚の HTML）
- 地図とモジュール：島全体・地区ごとの立体図（London Render で描いた絵）と平面図をクリック → モジュールの草図（マイデザインの図を貼る）・家具の番号・確かめ（奥／通り道／左右対称／密度）
- 案の比較：飛行機ラウンジなどの枠ごとに複数の案（選んだ案はブラウザに保存）
- 作例：参考写真・修正点・断面図（モジュールごとの軸）・まわりの通り道 P1〜P7・組み方の手順①②③と「済み」
- 建てる準備：使うマイデザインの作者IDの一覧（コピー）・保存枠の数
- 作例の審査：地区を選び（ロンドンなど）、その地区で使うかを大きな画像で1枚ずつ評価：めっちゃいい（＝絶対に島に入れる）／いいね／ふつう／イマイチ／いいね（別の地区）（キー 1・2・3・4→Q〜Y・←→、画像クリックで拡大・ダブルクリックでいいね・左右のはしで前後・下の列で飛ぶ）。評価は Artifact のデータベース votes/all（r: {地区: {番号: 2／1／0／-1}}、a: {地区: {番号: 使いたい地区}}）に保存し Claude が読む
- マイデザイン図鑑（D-000）・集めた作例（R-0000、テーマ・用途（10分類）・検索語・MA の有無・採用だけ・キーワードで絞りこみ、採用を先頭）

## 一括で作り直す
`bash tools/build_all.sh [出力の置き場]`（作例の審査の大きな画像は build_site.py の `--big` で big/c000.jpg… を書き出し、Artifact に files として何回かに分けて載せる。1回64MBまで）：地勢 → 見本 → 確認 → ビルドガイド（ICE_CACHE に作例の写真の置き場、立体図は playwright）

## ロンドンの市街と郊外（第31回）
- テムズ川を境に、東岸・北岸が市街、西岸と南西の浜が郊外（村）。境は tools/gen_samples.py の LON_SUB。郊外は sub_lon_* のモジュールと旧石畳の小道

## GitHub Pages（第39回）
- docs/index.html が Pages 版のビルドガイド。`python3 tools/build_site.py --cache <写真の置き場> --out docs/index.html --views <views.json> --pages --votes <votes/all の写し.json>`
- 作者の画像はリポジトリに入れず、Pinterest（i.pinimg.com の 236x／736x）を直接読む。地面・家具の切り抜き（作者の図の一部）は Pages では出さず色で描く
- 作例の審査も Pages でできる：はじめは Claude のページ（Artifact）の votes/all の写し。つけた評価はそのブラウザ（localStorage）に保存し、「評価をファイルに保存」で votes-日付.json（Artifact と同じ形 {r, a, k, t}）に書き出す。Claude はそのファイル（チャットか db/votes/）を読む。「ファイルから読みこむ」で別のブラウザへ移せる
- 公開：Settings → Pages → Deploy from a branch → main / docs

## 小红书のノート（第40回）
- ノートを集めるのはブランチ claude/intelligent-bohr-avhvea（ローカルで xiaohongshu-mcp にログインして tools/xhs_fetch.py。画像もそのブランチの xhs/img/）
- main には清单だけ：`python3 tools/xhs_refs.py <notes.json>` → designs/xhs_refs.json（X-0001…、地区・用途。番号はノートの id で引きつぐ）
- ビルドガイドは `--xhs <そのブランチの xhs を git archive した置き場>`。1ノート＝1作例（画像はまとめて1グループ、評価は1つ）。Pages はブランチの raw を直接読む。集めた作例・審査に「出どころ」の絞りこみ
| tool | files |
|---|---|
| モジュール | tools/gen_popular_modules.py → modules-popular.json／tools/module_db.py → db/modules.sqlite, modules-curated.json |
| 地勢 | plan-design.json → tools/plan_terrain.py → plan-terrain.json |
| 見本 | tools/gen_samples.py → samples.json |
| 確認 | tools/test_logic.js, tools/snap.js, tools/edge_run.py, tools/road_preview.js |
| マイデザイン・作例 | designs/catalog.json（D-）・designs/refs.json（R-、tools/collect_refs.py で検索・分類・--dedupe で重複に dup）・designs/lon.json（ロンドンの細部モジュール・地面・断面）・designs/lon_paths.json（通り道）・tools/design_tiles.js |
| ビルドガイド | tools/build_site.py・tools/site/template.html・tools/site/render_views.js・tools/build_all.sh |

## ロンドンを二層の町に（第42回）
- めっちゃいいの作例（R-1233・X-0003・R-0088・R-1217）の道の重ね方にならい、高台の町（2段目）と川ぞいの町（1段目）を石段と橋で輪につなぐ
- 坂を3本に：切り通しの西の石段 (47,62)S のほかに、東の石段 (52,62)S（東の曳舟道を x52〜54 の3マスに広げた）と、ホワイトホールから時計台の前庭へ上がる大階段 (37〜40, 64〜65)W
- 坂は日本の霊峰の神社（3段目）とアメリカの峰の泉（3段目）への坂を1つずつ回した。どちらの地区も2段目への坂は残る。峰の2か所は、はしごで上がる眺めの所になる
- キングス・クロス駅の高架（2段目・x28〜36・y76〜77）：崖の面をレンガのアーチに見立て、上に客車をのせる
- 通り道 P8（東の石段）・P9（大階段）を追加。屋台の路地（S6）は東の曳舟道の東の1列、崖の上の市場（S7）は x55〜57 へ。確認 226項目すべてOK

## ロンドンの地形と川の再設計案（第41回）
- ロンドンの作例の審査がすべて終わったので（469件：めっちゃいい30・いいね285・ふつう117・イマイチ37、写しは db/votes/claude-page-2026-10-12-lon-done.json）、高評価の作例から地形と川の好みを読み取り、plan-terrain.json のロンドンを3通りに作り直した案
- めっちゃいい30件・いいね285件を1件ずつ見て判断：めっちゃいい24件といいね25件を20か所（S1〜S20）に置く。いいね10件は道ばたの小物と地面に使う。ロンドンらしくないもの・同じ型の重なり・室内の場面・滝や坂が足りないものは外し、理由を残す
- 地形：高台に切り通しの運河（坂をその中へ移す）・切り通しの口に橋（7/8）・テムズ川の西半分をまっすぐに・南岸に船だまり・キングス・クロス駅の平地・ハイドパークのあき地。坂8/8・河口へのつながり・2段目と砂浜の間隔は確認ずみ
- plan-design.json に反映（第41回）：テムズ川の道すじ・切り通し（level・set）・船だまり・林のあき地（set）・坂の位置（near [47,62]）・切り通しの口の橋・上の通りを付け替え。地下鉄の入口の坂の切りこみはやめた。釣り場は (38,70) へ
- 2段の河岸のモジュール（R-0088：lon_d_canal・lon_d_quay_up）は置ける所がなくなったので位置を外し、retired（作り直し待ち）に。ビルドガイドは retired を仮の場所にも置かない。地下鉄の入口は (42,62)。通り道 P5・P7、断面（軸 x47）、ゲーム画面の地点、確認（2段の運河）を新しい地形に合わせた。確認 225項目すべてOK
- 鳥瞰図で見直し：魔法の路地（S1）は案内所の陰に入るので、案内所の北西 (20〜26, 56〜59) へ移した。通り道 P4 は西の川で行き止まりになっていたので、西口からキングス・クロスの前庭のまん中を通る道 (37,79)→(29,79) に引き直した
