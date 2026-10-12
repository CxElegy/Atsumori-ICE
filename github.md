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
- 見るだけ：評価ボタンは出さず、Claude のページ（Artifact）の votes/all の写しを地区ごとのラベルで出す。「作例の審査」タブは Claude のページへのリンク
- 公開：Settings → Pages → Deploy from a branch → main / docs

## Tools
| tool | files |
|---|---|
| モジュール | tools/gen_popular_modules.py → modules-popular.json／tools/module_db.py → db/modules.sqlite, modules-curated.json |
| 地勢 | plan-design.json → tools/plan_terrain.py → plan-terrain.json |
| 見本 | tools/gen_samples.py → samples.json |
| 確認 | tools/test_logic.js, tools/snap.js, tools/edge_run.py, tools/road_preview.js |
| マイデザイン・作例 | designs/catalog.json（D-）・designs/refs.json（R-、tools/collect_refs.py で検索・分類・--dedupe で重複に dup）・designs/lon.json（ロンドンの細部モジュール・地面・断面）・designs/lon_paths.json（通り道）・tools/design_tiles.js |
| ビルドガイド | tools/build_site.py・tools/site/template.html・tools/site/render_views.js・tools/build_all.sh |
