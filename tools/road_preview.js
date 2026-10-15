// 国ごとの道路の舗装と道ばたの装飾の案を、地形つきで1枚にして見比べる絵（提案用）
//   node tools/road_preview.js [--out snaps/road-preview.png]      node が無い PC は python tools/edge_run.py tools/road_preview.js
// 上：舗装の見本（色と模様）と道ばたの装飾  下：地区の地形に、見本の道路と道ばたの装飾をのせた図（1マス＝5px）
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
let lib;
try { lib = require('@napi-rs/canvas'); } catch (e) { console.error('@napi-rs/canvas が必要です（npm i @napi-rs/canvas）'); process.exit(2); }
const { createCanvas, GlobalFonts } = lib;
for (const p of ['C:/Windows/Fonts/YuGothB.ttc', 'C:/Windows/Fonts/meiryob.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc']) { try { if (fs.existsSync(p)) { GlobalFonts.registerFromPath(p, 'Zen Maru Gothic'); break; } } catch (e) {} }
const J = f => JSON.parse(fs.readFileSync(path.join(ROOT, f), 'utf8'));
const T = J('plan-terrain.json'), S = J('samples.json');
const outArg = process.argv.indexOf('--out'), out = outArg > 0 ? process.argv[outArg + 1] : path.join(ROOT, 'snaps', 'road-preview.png');

const ZONES = [
  ['lon', 'ロンドン', '濃い灰色の石畳＋レンガの縁', '#605b58', 'cobble', 'ガス灯・ベンチ・電話ボックス', 'lon'],
  ['egy', 'エジプト', '砂岩の敷石', '#c99a5a', 'slab', 'ヤシ・石柱・壺', 'egy'],
  ['jpn', '日本', '板石の参道', '#b9b4aa', 'slab', '石灯籠・竹・生け垣', 'jpn'],
  ['usa', 'アメリカ', 'アスファルト＋中央線', '#4a4d52', 'line', '白い柵・街灯・看板', 'usa'],
  ['hal', 'ハロウィン', '暗い紫の石畳', '#4b4057', 'cobble', 'ランタン・かぼちゃ・墓石', 'usa'],
  ['eur', 'ヨーロッパ', '扇模様の石畳', '#bdb7ac', 'fan', '街灯・花・ベンチ', 'eur'],
  ['port', '地中海', '白い石畳＋青緑の縁石', '#f2efe6', 'curb', 'パラソル・ヤシ・樽', 'port']
];
const DB = { egy: [8, 12, 40, 62], jpn: [32, 12, 67, 61], usa: [65, 12, 101, 47], eur: [57, 39, 101, 85], port: [64, 70, 112, 94], lon: [16, 52, 65, 94] };
const C = { S: '#7fd6c3', s: '#f0e4a4', r: '#7c7f94', w: '#8ee0d0', '1': '#4c9f48', '3': '#72c752', t: '#3c843a', p: '#c8b487', b: '#8d8a92', P: '#cdb88c', K: '#b8694b' };
const PW = 340, PH = 440, G = 5;
const cv = createCanvas(PW * 4, PH * 2 + 60), ctx = cv.getContext('2d');
ctx.fillStyle = '#faf6ef'; ctx.fillRect(0, 0, cv.width, cv.height);
ctx.font = "700 22px 'Zen Maru Gothic', sans-serif"; ctx.fillStyle = '#4a3b30'; ctx.fillText('道路の舗装と道ばたの装飾（地区ごとの案）', 20, 36);
function swatch(x, y, z) {
  ctx.fillStyle = z[3]; ctx.fillRect(x, y, 120, 70); ctx.strokeStyle = 'rgba(0,0,0,.25)'; ctx.fillStyle = 'rgba(0,0,0,.18)';
  for (let i = 0; i < 6; i++) for (let j = 0; j < 4; j++) {
    const cx = x + 10 + i * 20, cy = y + 10 + j * 17;
    if (z[4] === 'cobble') { ctx.beginPath(); ctx.arc(cx, cy, 5, 0, 7); ctx.fill(); }
    else if (z[4] === 'slab') { ctx.strokeRect(cx - 9, cy - 7, 18, 14); }
    else if (z[4] === 'fan') { ctx.beginPath(); ctx.arc(cx, cy + 4, 8, Math.PI, 0); ctx.stroke(); }
  }
  if (z[4] === 'line') { ctx.fillStyle = '#f4d44a'; for (let i = 0; i < 4; i++) ctx.fillRect(x + 8 + i * 30, y + 33, 18, 4); }
  if (z[4] === 'curb') { ctx.fillStyle = '#5b9aa0'; ctx.fillRect(x, y + 58, 120, 12); }
}
ZONES.forEach((z, i) => {
  const ox = (i % 4) * PW + 10, oy = 50 + Math.floor(i / 4) * PH;
  ctx.fillStyle = '#fff'; ctx.fillRect(ox, oy, PW - 20, PH - 10);
  ctx.fillStyle = '#4a3b30'; ctx.font = "700 18px 'Zen Maru Gothic', sans-serif"; ctx.fillText(z[1], ox + 10, oy + 26);
  ctx.font = "13px 'Zen Maru Gothic', sans-serif"; ctx.fillStyle = '#6a5a4d'; ctx.fillText(z[2], ox + 10, oy + 46); ctx.fillText('道ばた：' + z[5], ox + 10, oy + 64);
  swatch(ox + 10, oy + 74, z);
  // 地形（地区の範囲）に、見本の道路と道ばたの装飾
  const b = DB[z[6]], gx = ox + 10, gy = oy + 160, w = Math.min(b[2] - b[0], 60);
  const cx0 = b[0], cy0 = b[1];
  for (let y = 0; y < 40; y++) for (let x = 0; x < w; x++) {
    const X = cx0 + x, Y = cy0 + y; if (Y >= 96) continue; ctx.fillStyle = C[T.grid[Y][X]] || '#4c9f48'; ctx.fillRect(gx + x * 5, gy + y * 5, 5, 5);
    const pv = (S.paint[z[6]] || {})[X + ',' + Y];
    if (pv) { ctx.fillStyle = pv === 'r:' + z[0] ? z[3] : 'rgba(0,0,0,0)'; ctx.fillRect(gx + x * 5, gy + y * 5, 5, 5); }
  }
  const decoRe = /^deco_/;
  (S.dists[z[6]] || []).forEach(([m, x, y]) => { if (decoRe.test(m) && x >= cx0 && x < cx0 + w && y >= cy0 && y < cy0 + 40) { ctx.fillStyle = '#ffd86b'; ctx.fillRect(gx + (x - cx0) * 5 + 1, gy + (y - cy0) * 5 + 1, 3, 3); } });
  ctx.fillStyle = '#6a5a4d'; ctx.font = "12px 'Zen Maru Gothic', sans-serif"; ctx.fillText('黄色の点＝道ばたの装飾（deco_*）', ox + 10, gy + 40 * 5 + 22);
});
fs.mkdirSync(path.dirname(out), { recursive: true });
fs.writeFileSync(out, cv.toBuffer('image/png'));
console.log('保存:', out.replace(ROOT, '').replace(/^[\\/]/, ''));
