#!/usr/bin/env python3
"""node が無い PC で、画面なしの Edge（Chromium でも可）で tools/*.js を動かす。標準ライブラリだけ。

  python tools/edge_run.py tools/test_logic.js                      ロジックの確認（「すべてOK」）
  python tools/edge_run.py tools/snap.js game lon sample night far  画面を PNG にする（snaps/ に保存）
  python tools/edge_run.py page "Game View.dc.html" --click 日本 --click 夜 [--out 画像.png]
                                                                    本物のページをボタンを押してから撮る。ページにエラーがあれば終了コード1

仕組み
  ・このフォルダの1つ上を配る小さなサーバーを立て、tools/edge_run.html を Edge で開く。ページは require('fs' | 'path' | 'os' | '@napi-rs/canvas' | './x.js')・process・__dirname を
    ブラウザの中で用意して JS を動かし、ログと書き出したファイルを POST で返す（結果はページから受け取る）。
  ・会社の Edge は新しいプロファイルだとサインイン画面が先に出るので、リモートデバッグ（CDP）で新しいタブを開く。
  ・Edge の場所は環境変数 EDGE_PATH で指定できる。Windows は PYTHONIONENCODING の代わりに PYTHONIOENCODING=utf-8 を付けると日本語が化けない。
"""
import base64, hashlib, http.server, json, os, shutil, socket, struct, subprocess, sys, tempfile, threading, time, urllib.parse, urllib.request, uuid, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SERVE = os.path.dirname(ROOT)                  # サーバーの / はリポジトリの1つ上
REPO = '/' + os.path.basename(ROOT) + '/'


def find_browser():
    cands = [os.environ.get('EDGE_PATH', ''),
             r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
             '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge', shutil.which('msedge') or '', shutil.which('microsoft-edge') or '',
             shutil.which('chromium') or '', shutil.which('google-chrome') or '', shutil.which('chrome') or ''] + glob.glob('/opt/pw-browsers/chromium-*/chrome-linux/chrome')
    for c in cands:
        if c and os.path.exists(c):
            return c
    sys.exit('Edge が見つかりません。環境変数 EDGE_PATH に msedge.exe の場所を入れてください')


class State:
    jobs = {}
    results = {}
    allowed = set()                            # サーバーの外で読んでよいファイル（引数で渡されたもの）


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=SERVE, **k)

    def log_message(self, *a):
        pass

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def do_GET(self):
        p = self.path.split('?')[0]
        if p.startswith('/__job/'):
            job = State.jobs.get(p[7:])
            body = json.dumps(job).encode() if job else b'{}'
            self.send_response(200 if job else 404); self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body); return
        if p.startswith('/__abs/'):
            f = urllib.parse.unquote(p[7:])
            if os.path.normcase(os.path.abspath(f)) in State.allowed and os.path.isfile(f):
                data = open(f, 'rb').read(); self.send_response(200); self.send_header('Content-Length', str(len(data))); self.end_headers(); self.wfile.write(data)
            else:
                self.send_response(403); self.end_headers()
            return
        return super().do_GET()

    def do_HEAD(self):
        return super().do_HEAD()

    def do_POST(self):
        p = self.path
        n = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(n)
        if p.startswith('/__result/'):
            State.results[p[10:]] = json.loads(body.decode('utf-8') or '{}')
            self.send_response(200); self.end_headers(); self.wfile.write(b'ok'); return
        self.send_response(404); self.end_headers()


def start_server():
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


# ---- 最小の WebSocket（CDP 用）-------------------------------------------------
class WS:
    def __init__(self, url):
        u = urllib.parse.urlparse(url)
        self.s = socket.create_connection((u.hostname, u.port), timeout=60)
        key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall(('GET %s HTTP/1.1\r\nHost: %s:%d\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\n\r\n' % (u.path, u.hostname, u.port, key)).encode())
        buf = b''
        while b'\r\n\r\n' not in buf:
            buf += self.s.recv(4096)
        self.buf = buf.split(b'\r\n\r\n', 1)[1]
        self.id = 0
        self.events = []

    def send(self, obj):
        data = json.dumps(obj).encode()
        hdr = bytearray([0x81]); n = len(data)
        if n < 126: hdr.append(0x80 | n)
        elif n < 65536: hdr.append(0x80 | 126); hdr += struct.pack('>H', n)
        else: hdr.append(0x80 | 127); hdr += struct.pack('>Q', n)
        mask = os.urandom(4); hdr += mask
        self.s.sendall(bytes(hdr) + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))

    def _read(self, n):
        while len(self.buf) < n:
            c = self.s.recv(65536)
            if not c: raise EOFError
            self.buf += c
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def recv(self):
        msg = b''
        while True:
            b1, b2 = self._read(2)
            n = b2 & 0x7f
            if n == 126: n = struct.unpack('>H', self._read(2))[0]
            elif n == 127: n = struct.unpack('>Q', self._read(8))[0]
            data = self._read(n)
            op = b1 & 0x0f
            if op == 8: raise EOFError
            if op in (1, 2, 0): msg += data
            if b1 & 0x80 and op != 9 and op != 10:
                return json.loads(msg.decode('utf-8'))

    def call(self, method, params=None):
        self.id += 1; mid = self.id
        self.send({'id': mid, 'method': method, 'params': params or {}})
        while True:
            m = self.recv()
            if m.get('id') == mid:
                if 'error' in m: raise RuntimeError(method + ': ' + json.dumps(m['error']))
                return m.get('result', {})
            self.events.append(m)

    def pump(self, secs):
        end = time.time() + secs
        self.s.settimeout(0.3)
        while time.time() < end:
            try: self.events.append(self.recv())
            except (socket.timeout, TimeoutError): pass
        self.s.settimeout(60)


def launch(url):
    exe = find_browser()
    tmp = tempfile.mkdtemp(prefix='edge_run_')
    s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
    args = [exe, '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--remote-debugging-port=%d' % port, '--user-data-dir=' + tmp, 'about:blank']
    if hasattr(os, 'geteuid') and os.geteuid() == 0:
        args.insert(1, '--no-sandbox')
    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(100):
        try:
            urllib.request.urlopen('http://127.0.0.1:%d/json/version' % port, timeout=1); break
        except Exception:
            time.sleep(0.2)
    # 新しいタブを開く（新しいプロファイルの初期画面ではなく）
    req = urllib.request.Request('http://127.0.0.1:%d/json/new?%s' % (port, urllib.parse.quote(url, safe=':/?=&')), method='PUT')
    tab = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())
    return proc, port, tab, tmp


def run_script(script, argv):
    srv = start_server(); port = srv.server_address[1]
    job = uuid.uuid4().hex[:8]
    sc = os.path.abspath(script)
    for a in argv:
        if os.path.exists(a):
            State.allowed.add(os.path.normcase(os.path.abspath(a)))
    State.jobs[job] = {'script': sc.replace('\\', '/'), 'argv': argv, 'env': {k: v for k, v in os.environ.items() if k in ('TMPDIR', 'TEMP', 'PYTHONIOENCODING')},
                       'root': REPO, 'serveAbs': SERVE.replace('\\', '/')}
    # スクリプトが相対パスで渡されたときは、リポジトリからの位置にそろえる
    if not os.path.isabs(script) or not sc.startswith(ROOT):
        State.jobs[job]['script'] = REPO + os.path.relpath(sc, ROOT).replace('\\', '/') if sc.startswith(ROOT) else sc.replace('\\', '/')
    else:
        State.jobs[job]['script'] = REPO + os.path.relpath(sc, ROOT).replace('\\', '/')
    url = 'http://127.0.0.1:%d%stools/edge_run.html?job=%s' % (port, REPO, job)
    proc, bport, tab, tmp = launch(url)
    t0 = time.time()
    try:
        while job not in State.results and time.time() - t0 < 600:
            time.sleep(0.2)
    finally:
        proc.terminate()
        try: proc.wait(10)
        except Exception: proc.kill()
        shutil.rmtree(tmp, ignore_errors=True)
    r = State.results.get(job)
    if not r:
        print('結果が返りませんでした（時間切れ）', file=sys.stderr); return 1
    for kind, text in r.get('logs', []):
        print(text, file=(sys.stderr if kind == 'err' else sys.stdout))
    for f in r.get('files', []):
        p = f['path'].replace('\\', '/')
        if p.startswith(REPO):
            p = p[len(REPO):]
        dest = os.path.normpath(os.path.join(ROOT, p))
        if not dest.startswith(ROOT):
            print('リポジトリの外へは書きません:', p, file=sys.stderr); continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if 'b64' in f: open(dest, 'wb').write(base64.b64decode(f['b64']))
        else: open(dest, 'w', encoding='utf-8', newline='').write(f['text'])
    if r.get('error'):
        print(r['error'], file=sys.stderr)
    return int(r.get('code') or 0)


def run_page(page, clicks, out):
    srv = start_server(); port = srv.server_address[1]
    rel = page.replace('\\', '/')
    url = 'http://127.0.0.1:%d%s%s' % (port, REPO, urllib.parse.quote(rel))
    proc, bport, tab, tmp = launch('about:blank')
    code = 0
    try:
        ws = WS(tab['webSocketDebuggerUrl'])
        ws.call('Page.enable'); ws.call('Runtime.enable'); ws.call('Log.enable')
        ws.call('Emulation.setDeviceMetricsOverride', {'width': 1400, 'height': 1000, 'deviceScaleFactor': 1, 'mobile': False})
        ws.call('Page.navigate', {'url': url})
        ws.pump(3.0)
        for c in clicks:
            js = '(()=>{const t=%s;const e=[...document.querySelectorAll("button,label,a,span")].find(x=>x.textContent.trim()===t);if(!e)return "NOTFOUND";e.click();return "ok"})()' % json.dumps(c, ensure_ascii=False)
            r = ws.call('Runtime.evaluate', {'expression': js, 'returnByValue': True})['result'].get('value')
            if r != 'ok':
                print('ボタンが見つかりません:', c, file=sys.stderr); code = 1
            ws.pump(1.5)
        ws.pump(0.5)
        shot = ws.call('Page.captureScreenshot', {'format': 'png'})['data']
        dest = os.path.join(ROOT, out)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, 'wb').write(base64.b64decode(shot))
        print('保存:', out)
        for e in ws.events:
            m = e.get('method')
            if m == 'Runtime.exceptionThrown':
                d = e['params']['exceptionDetails']; print('ページのエラー:', (d.get('exception') or {}).get('description') or d.get('text'), file=sys.stderr); code = 1
            elif m == 'Runtime.consoleAPICalled' and e['params']['type'] == 'error':
                txt = ' '.join(str(a.get('value', a.get('description', ''))) for a in e['params']['args'])
                if 'fonts.g' not in txt and 'unpkg' not in txt: print('console.error:', txt, file=sys.stderr); code = 1
    finally:
        proc.terminate()
        try: proc.wait(10)
        except Exception: proc.kill()
        shutil.rmtree(tmp, ignore_errors=True)
    return code


def main(a):
    if not a:
        print(__doc__); return 1
    if a[0] == 'page':
        clicks, out, page, i = [], 'snaps/page.png', None, 1
        while i < len(a):
            if a[i] == '--click': clicks.append(a[i + 1]); i += 2
            elif a[i] == '--out': out = a[i + 1]; i += 2
            else: page = a[i]; i += 1
        if not page: print(__doc__); return 1
        return run_page(page, clicks, out)
    return run_script(a[0], a[1:])


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
