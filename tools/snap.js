// 画面の canvas を PNG にする（node tools/snap.js ... ／ node が無い PC は python tools/edge_run.py tools/snap.js ...）
//   render  完成イメージ   node tools/snap.js render <範囲> [sample|board] [day|dusk|night] [none|dist|all]
//             範囲：lon egy jpn usa eur port museum wide all
//   builder 組み立て台の地図 node tools/snap.js builder <地区> [sample]
//   game    ゲーム画面     node tools/snap.js game <地区 か x,y> [sample|board] [day|dusk|night] [near|normal|far] [none|dist|all]
//   --out ファイル で保存先を決める（初めは snaps/ の中）。--board 配置.json で組み立て台の保存した配置を使う。描画にかかった時間も出す。
const fs = require('fs'), path = require('path');
const { loadComponent, ROOT } = require('./dc_harness.js');
let canvasLib;
try { canvasLib = require('@napi-rs/canvas'); } catch (e) { console.error('@napi-rs/canvas が必要です（npm i @napi-rs/canvas）。node が無い PC は tools/edge_run.py で動かします'); process.exit(2); }
const { createCanvas, GlobalFonts } = canvasLib;
// 日本語の字：游ゴシック Bold など（'Zen Maru Gothic' の名前で登録。無ければ Noto などを探す）
for (const p of ['C:/Windows/Fonts/YuGothB.ttc', 'C:/Windows/Fonts/meiryob.ttc', 'C:/Windows/Fonts/meiryo.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', '/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc', '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc']) {
  try { if (fs.existsSync(p)) { GlobalFonts.registerFromPath(p, 'Zen Maru Gothic'); break; } } catch (e) {}
}
const args = process.argv.slice(2);
const opt = {}; const pos = [];
for (let i = 0; i < args.length; i++) { if (args[i] === '--out') opt.out = args[++i]; else if (args[i] === '--board') opt.board = args[++i]; else pos.push(args[i]); }
const [mode, target, ...rest] = pos;
if (!mode || !target) { console.log(fs.readFileSync(__filename, 'utf8').split('\n').slice(0, 7).join('\n')); process.exit(1); }
const has = (list, d) => rest.find(r => list.includes(r)) || d;
const src = has(['sample', 'board'], opt.board ? 'board' : 'sample'), time = has(['day', 'dusk', 'night'], 'day'), names = has(['none', 'dist', 'all'], 'all'), cam = has(['near', 'normal', 'far'], 'normal');
const store = {};
if (src === 'board' && opt.board) store['wti-module-board'] = fs.readFileSync(opt.board, 'utf8');

(async () => {
  const file = { render: 'London Render.dc.html', builder: 'Module Builder.dc.html', game: 'Game View.dc.html' }[mode];
  if (!file) { console.error('mode は render / builder / game'); process.exit(1); }
  const cv = createCanvas(mode === 'game' ? 1280 : 1200, mode === 'game' ? 720 : 800);
  const mp = mode === 'game' ? createCanvas(336, 288) : undefined;
  const h = loadComponent(file, { store, createCanvas, canvas_cv: cv, canvas_mp: mp });
  const comp = await h.start();
  const t0 = Date.now();
  if (mode === 'render') { comp.dk = null; comp.setState({ view: target, time, names }); }
  else if (mode === 'builder') { if (comp.DISTS[target]) { comp.setState({ dist: target, theme: comp.DIST_TH[target] || 'すべて' }); } if (src === 'sample') comp.placeSample(target); comp.draw(); }
  else {
    let tx, ty;
    if (/^\d+,\d+$/.test(target)) [tx, ty] = target.split(',').map(Number);
    else { const sp = comp.SPOTS[target]; if (!sp) { console.error('地区は ' + Object.keys(comp.SPOTS).join(' ') + ' か x,y'); process.exit(1); } tx = sp[1][0][1]; ty = sp[1][0][2]; }
    comp.dk = null; comp.setState({ tx, ty, cam, time, names });
  }
  const ms = Date.now() - t0;
  const out = opt.out || path.join(ROOT, 'snaps', `${mode}-${target.replace(',', '_')}-${src}-${time}${mode === 'game' ? '-' + cam : ''}.png`);
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, cv.toBuffer('image/png'));
  console.log(`${out.replace(ROOT, '').replace(/^[\\/]/, '')}（${cv.width}×${cv.height}・描画${ms}ミリ秒）`);
  if (h.stats.bad.length) { console.error('数が不正な描画:', h.stats.bad.slice(0, 3).join(' ')); process.exitCode = 1; }
})().catch(e => { console.error(e); process.exit(1); });
