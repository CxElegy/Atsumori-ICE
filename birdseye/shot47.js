const { chromium } = require(process.env.PW);
const fs = require('fs');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  const errs = [];
  const TAG = process.env.TAG || 'main', PAGE = process.env.PAGE || 'london-birdseye.html', ODIR = process.env.ODIR || '.';   // 第59回：候補ごとに別のページと出力先
  fs.writeFileSync(`_page_${TAG}.html`, '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>[hidden]{display:none!important}</style></head><body style="margin:0">' + fs.readFileSync(PAGE, 'utf8') + '</body></html>');
  const p = await b.newPage({ viewport: { width: 1360, height: 1000 } });
  p.on('pageerror', e => errs.push(String(e))); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.emulateMedia({ reducedMotion: 'reduce' });
  await p.goto(`http://127.0.0.1:8765/_page_${TAG}.html`, { waitUntil: 'networkidle' });
  await p.waitForTimeout(3000);
  if (process.env.CLEAN) await p.addStyleTag({ content: '#bubble,#pins,.hint{display:none!important}' });   // 点検用：説明の吹き出しとピンを消す
  const bb = await p.locator('#stage').boundingBox();
  for (const [v, t, n] of JSON.parse(process.argv[2])) {
    await p.click(`#time button[data-v="${t}"]`); await p.waitForTimeout(300);
    if (v.startsWith('g:')) await p.click(`.gitem[data-g="${v.slice(2)}"]`);
    else if (v.startsWith('cam:')) { const [x, y, z, pol, dist] = v.slice(4).split(',').map(Number); await p.evaluate(a => window.__cam && window.__cam(...a), [x, y, z, pol, dist]); }
    else await p.click(`#view button[data-v="${v}"]`);
    await p.waitForTimeout(2200); await p.screenshot({ path: `${ODIR}/m_${n}.png`, clip: bb, timeout: 120000 });
  }
  if (process.argv[3]) await p.screenshot({ path: `${ODIR}/m_full.png`, fullPage: true, timeout: 120000 });
  console.log('errors:', errs); await b.close();
})();
