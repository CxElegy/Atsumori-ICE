#!/usr/bin/env python3
"""小红书に QR コードでログインし、xiaohongshu-mcp 用の cookies.json を書き出す。

xiaohongshu-mcp 標準の QR ログインは、海外のサーバー等から入ると出る
「手机短信验证」（471 → SMS コード入力）に対応していないので、その代わり。

  pip install playwright pillow
  python3 tools/xhs_login.py --cookies /path/to/xiaohongshu-mcp/cookies.json
  # → xhs-login-qr.png をアプリで読み取り「确认登录」
  # → SMS 認証が出たら、届いた6桁をターミナルに入力（--code-file を指定すると、そのファイルに書いても可）

xiaohongshu-mcp は COOKIES_PATH の cookies をリクエストごとに読むので、再起動は不要。
cookies.json はログイン情報そのもの。リポジトリに入れないこと。
"""
import argparse, asyncio, base64, json, os, sys, threading, time

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
LOGGED_IN = '.main-container .user .link-wrapper .channel'


def ask_code(box, code_file):
    """SMS コードを標準入力か code_file から受け取る"""
    def stdin():
        try:
            box.setdefault('code', input('SMS の6桁コード: ').strip())
        except EOFError:
            pass
    threading.Thread(target=stdin, daemon=True).start()
    while 'code' not in box:
        if code_file and os.path.exists(code_file):
            box['code'] = open(code_file).read().strip()
            os.remove(code_file)
        time.sleep(0.5)


async def main(a):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        kw = {'executable_path': a.chrome} if a.chrome else {}
        b = await p.chromium.launch(headless=not a.show, args=['--disable-blink-features=AutomationControlled'], **kw)
        ctx = await b.new_context(user_agent=UA, locale='zh-CN', viewport={'width': 1280, 'height': 800})
        pg = await ctx.new_page()
        state = {}

        def on_resp(r):
            if '/login/qrcode/status' in r.url and r.status == 471:
                state['sms'] = True  # 異常環境 → SMS 認証へ
        pg.on('response', on_resp)

        await pg.goto('https://www.xiaohongshu.com/explore', wait_until='networkidle', timeout=60000)
        if await pg.query_selector(LOGGED_IN):
            print('すでにログイン済みです')
        else:
            el = await pg.wait_for_selector('.login-container .qrcode-img', timeout=30000)
            src = await el.get_attribute('src')
            with open(a.qr, 'wb') as f:
                f.write(base64.b64decode(src.split(',', 1)[1]))
            print(f'QR コードを保存しました: {a.qr}（4分以内に小红书アプリで読み取り →「确认登录」）')
            deadline = time.time() + 240
            typed = False
            while time.time() < deadline:
                await pg.wait_for_timeout(1500)
                if await pg.query_selector(LOGGED_IN):
                    break
                if state.get('sms') and not typed:
                    print('SMS 認証が求められました。登録の電話番号に届いたコードを入力してください（約60秒で失効）')
                    box = {}
                    await asyncio.get_running_loop().run_in_executor(None, ask_code, box, a.code_file)
                    inp = await pg.wait_for_selector('input[placeholder="请输入验证码"]', timeout=15000)
                    await inp.click()
                    await pg.keyboard.type(box['code'], delay=120)
                    typed = True
                    deadline = max(deadline, time.time() + 60)
            else:
                await pg.screenshot(path=a.qr.replace('.png', '-timeout.png'))
                raise SystemExit('ログインできませんでした（時間切れ）')
            await pg.wait_for_timeout(2000)

        cookies = await ctx.cookies()
        if not any(c['name'] == 'web_session' for c in cookies):
            raise SystemExit('web_session cookie がありません')
        out = {'version': 2, 'saved_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'cookies': cookies}
        if os.path.exists(a.cookies):  # 既存ファイルの指紋 seed は引き継ぐ
            try:
                old = json.load(open(a.cookies))
                if isinstance(old, dict) and old.get('seed'):
                    out['seed'] = old['seed']
            except Exception:
                pass
        fd = os.open(a.cookies, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, 'w') as f:
            json.dump(out, f)
        print(f'ログイン成功。cookies を保存しました: {a.cookies}（{len(cookies)}件）')
        await b.close()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--cookies', default='cookies.json', help='xiaohongshu-mcp の COOKIES_PATH')
    ap.add_argument('--qr', default='xhs-login-qr.png')
    ap.add_argument('--code-file', help='SMS コードをこのファイルに書いても受け付ける')
    ap.add_argument('--chrome', help='Chromium の実行ファイル（省略時は Playwright 同梱のもの）')
    ap.add_argument('--show', action='store_true', help='ブラウザ画面を表示する')
    asyncio.run(main(ap.parse_args()))
