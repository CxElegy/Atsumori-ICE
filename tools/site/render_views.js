// 立体図（London Render.dc.html）を、ビルドガイドの配置で描いて JPEG にする
//   node tools/site/render_views.js <board.json> <views.json> [unpkg のキャッシュ置き場]
//   playwright（Chromium）が要る。React などは unpkg から読む（キャッシュ置き場があればそこから）
const { chromium } = require(process.env.PW || 'playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..', '..'), [board, out, cache] = process.argv.slice(2);
const VIEWS = { all: '島全体', lon: 'ロンドン', egy: 'エジプト', jpn: '日本', usa: 'アメリカ', eur: 'ヨーロッパ', port: '地中海の港' };
const mime = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json' };
const srv = http.createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); if (!fs.existsSync(p) || fs.statSync(p).isDirectory()) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'content-type': mime[path.extname(p)] || 'application/octet-stream' }); fs.createReadStream(p).pipe(r); });
srv.listen(0, async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME || undefined, args: ['--no-sandbox'] });
  const pg = await b.newPage({ viewport: { width: 1500, height: 1000 } });
  if (cache) await pg.route('**/*', rt => { const u = rt.request().url(); const m = /unpkg\.com\/(.*)/.exec(u); if (m) { const f = path.join(cache, path.basename(m[1])); if (fs.existsSync(f)) return rt.fulfill({ status: 200, contentType: 'text/javascript', body: fs.readFileSync(f) }); } return u.startsWith('http://127.0.0.1') ? rt.continue() : rt.abort(); });
  const url = `http://127.0.0.1:${srv.address().port}/`;
  await pg.goto(url + 'support.js'); await pg.evaluate(s => localStorage.setItem('wti-module-board', s), fs.readFileSync(board, 'utf8'));
  await pg.goto(url + encodeURIComponent('London Render.dc.html')); await pg.waitForTimeout(3000);
  const res = {};
  for (const [k, name] of Object.entries(VIEWS)) {
    await pg.getByText(name, { exact: true }).first().click(); await pg.waitForTimeout(1500);
    res[k] = await pg.evaluate(() => { const c = document.querySelector('canvas'), o = document.createElement('canvas'); o.width = c.width; o.height = c.height; const x = o.getContext('2d');
      x.fillStyle = '#86d3c4'; x.fillRect(0, 0, o.width, o.height); x.drawImage(c, 0, 0); return { img: o.toDataURL('image/jpeg', .82), w: c.width, h: c.height }; });   // 透明の所は海の色
    console.log(k, res[k].w, res[k].h, Math.round(res[k].img.length / 1024) + 'KB');
  }
  fs.writeFileSync(out, JSON.stringify(res)); await b.close(); srv.close();
});
