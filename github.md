repo: CxElegy/Atsumori-ICE
branch: main

## Last sync
date: 2026-10-07
### Updated in this project
- リポジトリは空（取得時409）。このプロジェクトからの書き込みは未実施

## Screen map
| screen | files |
|---|---|
| ブレスト | World Travel Island Brainstorm.dc.html |
| 計画書 v1〜v4 | World Travel Island Plan.dc.html, Plan v2/v3/v4.dc.html, island-grid*.json |
| 組み立て台 | Module Builder.dc.html, island-grid-v4.json, xhs/notes.json, xhs/modules.json, xhs/img/ |
| ロンドン イメージ図 | London Render.dc.html |

## 小红书から作る（組み立て台の下）
- 地区ごとに人気（いいね順）の島づくりノートを `xhs/notes.json` と `xhs/img/` に保存。写真を見ながらマス目に描くと「小红书」テーマのモジュールになる
- 作ったモジュールはブラウザに保存。「書き出し」で modules.json をダウンロード → `xhs/modules.json` に置いてコミットすると全員の組み立て台に出る
- ノートの追加（xiaohongshu-mcp をローカルで起動・ログインしておく）
  1. `go build` した xiaohongshu-mcp を `COOKIES_PATH=…/cookies.json ./xiaohongshu-mcp` で起動
  2. `python3 tools/xhs_login.py --cookies …/cookies.json` → QR を読み取り「确认登录」、SMS が来たら6桁を入力
  3. `python3 tools/xhs_fetch.py themes`（6地区まとめて）／ `search 动森岛建 xxx --theme 日本` ／ `url <共有リンク> --theme 地中海`
- cookies.json はログイン情報。コミットしない（.gitignore 済み）
