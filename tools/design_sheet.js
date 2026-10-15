// 地区のマイデザイン割り当てを1枚の絵にする（モジュールを1マスずつパーツで描き、使う作者IDを並べる）
//   node tools/design_sheet.js [lon] [--out figures/図11-1_ロンドンのマイデザイン.png]
//   @napi-rs/canvas が必要（npm i @napi-rs/canvas）
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
let lib;
try { lib = require('@napi-rs/canvas'); } catch (e) { console.error('@napi-rs/canvas が必要です（npm i @napi-rs/canvas）'); process.exit(2); }
const { createCanvas, GlobalFonts } = lib;
for (const p of ['C:/Windows/Fonts/YuGothB.ttc', 'C:/Windows/Fonts/meiryob.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', '/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf']) { try { if (fs.existsSync(p)) { GlobalFonts.registerFromPath(p, 'Zen Maru Gothic'); break; } } catch (e) {} }
const T = require('./design_tiles.js');
const J = f => JSON.parse(fs.readFileSync(path.join(ROOT, f), 'utf8'));
const th = process.argv[2] && !process.argv[2].startsWith('--') ? process.argv[2] : 'lon';
const DOC = J(`designs/${th}.json`), CAT = Object.fromEntries(J('designs/catalog.json').designs.map(d => [d.id, d]));
const outArg = process.argv.indexOf('--out'), out = outArg > 0 ? process.argv[outArg + 1] : path.join(ROOT, 'figures', `図11-1_${DOC.name}のマイデザイン.png`);

// 採用ずみのモジュールからも、割り当ての例として主役と脇役をいくつか描く
const EXTRA = { lon: ['pop0007', 'lon_934', 'pop0084', 'vig_lon_1'] }[th] || [];
let curated = [];
try { curated = J('modules-curated.json').modules; } catch (e) {}
const mods = DOC.modules.concat(EXTRA.map(id => curated.find(m => m.id === id)).filter(Boolean).map(m => ({ ...m, name: '採用ずみ：' + m.name, marks: [] })));

const ITEM = {   // 家具の描き方：[文字, 地の色, 字の色]
  L: ['灯', '#2f2f33', '#ffe7a3'], q: ['鉢', '#c98b5a', '#fff'], T: ['電', '#c8352b', '#fff'], $: ['〒', '#c8352b', '#fff'], b: ['ベ', '#6b4b35', '#fff'],
  K: ['時', '#2f2f33', '#fff'], t: ['木', '#3c843a', '#fff'], v: ['バ', '#d23a2f', '#fff'], W: ['壁', '#8a4b36', '#ffd9a0'], Q: ['塔', '#9b9488', '#fff'],
  A: ['門', '#9b9488', '#fff'], C: ['客', '#23306b', '#e8d48a'], N: ['停', '#c8352b', '#fff'], E: ['地', '#f4f1ea', '#c8352b'], f: ['柵', '#3a3a3a', '#fff'],
  i: ['看', '#3b5a3a', '#f3e2a9'], x: ['樽', '#8a5a33', '#fff'], h: ['椅', '#6b4b35', '#fff'], c: ['卓', '#6b4b35', '#fff'], Y: ['店', '#7a5130', '#fff'],
  '%': ['旗', '#23306b', '#fff'], F: ['花', '#f2a7c3', '#7a2b4b'], u: ['傘', '#e6e0d0', '#555'], e: ['垣', '#5a9a4a', '#fff'],
};
const C = 30, GRASS = '#7dbb5a';
const cv = createCanvas(1900, 100), ctx0 = cv.getContext('2d');

// ---- 1マスの地面をパーツで描く ----
function cell(ctx, x0, y0, t) {
  const G = DOC.ground[t.ch], col = G.color, s = C;
  ctx.fillStyle = col; ctx.fillRect(x0, y0, s, s);
  ctx.save(); ctx.beginPath(); ctx.rect(x0, y0, s, s); ctx.clip();
  if (G.pattern === 'brick') { ctx.strokeStyle = 'rgba(70,45,30,.45)'; ctx.lineWidth = 1; for (let r = 0; r < 4; r++) { const yy = y0 + r * s / 4; ctx.beginPath(); ctx.moveTo(x0, yy); ctx.lineTo(x0 + s, yy); ctx.stroke(); for (let k = 0; k < 3; k++) { const xx = x0 + ((k + (r % 2) * .5) * s / 2); ctx.beginPath(); ctx.moveTo(xx, yy); ctx.lineTo(xx, yy + s / 4); ctx.stroke(); } } }
  else if (G.pattern === 'cobble' || G.pattern === 'zebra' || G.pattern === 'stone') { ctx.fillStyle = G.pattern === 'stone' ? 'rgba(255,255,255,.18)' : 'rgba(255,255,255,.10)'; for (let r = 0; r < 4; r++) for (let k = 0; k < 4; k++) { ctx.beginPath(); ctx.ellipse(x0 + (k + .5 + (r % 2) * .25) * s / 4, y0 + (r + .5) * s / 4, s / 10, s / 12, 0, 0, 7); ctx.fill(); } }
  else if (G.pattern === 'lawn') { ctx.fillStyle = '#c9c2b0'; ctx.fillRect(x0 + 5, y0 + 5, s - 10, s - 10); }
  else if (G.pattern === 'rail') { ctx.fillStyle = '#6b5a48'; for (let k = 0; k < 4; k++) ctx.fillRect(x0 + k * s / 4 + 2, y0 + 4, 4, s - 8); ctx.fillStyle = '#c9ccd1'; ctx.fillRect(x0, y0 + 8, s, 3); ctx.fillRect(x0, y0 + s - 11, s, 3); }
  if (G.pattern === 'zebra') { ctx.fillStyle = '#f4f2ec'; for (let r = 0; r < 3; r++) ctx.fillRect(x0 + 2, y0 + r * s / 3 + 2, s - 4, s / 3 - 5); }
  ctx.restore();
  // 縁・段差・角（なくなっている辺に線を引く）
  const EC = t.kind === 'base' ? null : G.pattern === 'brick' ? '#6e4a37' : G.pattern === 'cobble' || G.pattern === 'zebra' ? '#d9d6cf' : '#ddd8cc';
  const lw = G.pattern === 'cobble' || G.pattern === 'zebra' ? 5 : 4;
  if (EC) { ctx.fillStyle = EC; const [n, e, so, w] = t.miss;
    if (n) ctx.fillRect(x0, y0, s, lw); if (so) ctx.fillRect(x0, y0 + s - lw, s, lw); if (w) ctx.fillRect(x0, y0, lw, s); if (e) ctx.fillRect(x0 + s - lw, y0, lw, s); }
  if (t.kind === 'diag') {   // ななめ：外の角を三角に切る
    const [n, e, so, w] = t.miss, cx = e ? x0 + s : x0, cy = so ? y0 + s : y0, dx = e ? -1 : 1, dy = so ? -1 : 1;
    ctx.fillStyle = GRASS; ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx + dx * s * .55, cy); ctx.lineTo(cx, cy + dy * s * .55); ctx.closePath(); ctx.fill();
    ctx.strokeStyle = '#6e4a37'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(cx + dx * s * .55, cy); ctx.lineTo(cx, cy + dy * s * .55); ctx.stroke();
  }
  if (t.kind === 'inner') { ctx.fillStyle = '#6e4a37'; ctx.fillRect(x0 + s / 2 - 2, y0 + s / 2 - 2, 4, 4); }
}

function drawModule(ctx, m, X, Y) {
  const rows = T.underlay(m.r, DOC.ground), tiles = T.tilePieces(m.r, DOC.ground), H = rows.length, W = rows[0].length;
  ctx.fillStyle = GRASS; ctx.fillRect(X, Y, W * C, H * C);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { const t = tiles[y][x]; if (t) cell(ctx, X + x * C, Y + y * C, t); }
  ctx.strokeStyle = 'rgba(0,0,0,.08)'; ctx.lineWidth = 1; for (let y = 0; y <= H; y++) { ctx.beginPath(); ctx.moveTo(X, Y + y * C); ctx.lineTo(X + W * C, Y + y * C); ctx.stroke(); } for (let x = 0; x <= W; x++) { ctx.beginPath(); ctx.moveTo(X + x * C, Y); ctx.lineTo(X + x * C, Y + H * C); ctx.stroke(); }
  m.r.forEach((row, y) => [...row].forEach((ch, x) => { const it = ITEM[ch]; if (!it) return; const px = X + x * C, py = Y + y * C;
    ctx.fillStyle = it[1]; ctx.beginPath(); ctx.roundRect(px + 3, py + 3, C - 6, C - 6, 6); ctx.fill(); ctx.fillStyle = it[2]; ctx.font = "700 15px 'Zen Maru Gothic', sans-serif"; ctx.textAlign = 'center'; ctx.fillText(it[0], px + C / 2, py + C / 2 + 5); ctx.textAlign = 'left'; }));
  (m.marks || []).forEach(([x, y, txt]) => { ctx.fillStyle = '#f4f2ec'; ctx.font = "700 10px 'Zen Maru Gothic', sans-serif"; ctx.textAlign = 'center'; ctx.fillText(txt, X + (x + .5) * C, Y + y * C + C / 2 + 4); ctx.textAlign = 'left'; });
  return [W * C, H * C];
}

// ---- 配置：カードを横に詰める ----
const PAD = 22, CW = 440;
const cards = mods.map(m => { const used = T.designsUsed(m.r, DOC); return { m, used, h: m.r.length * C + 64 + used.length * 19 }; });
let x = PAD, y = 120, rowH = 0; const pos = [];
cards.forEach(c => { if (x + CW > 1900 - PAD) { x = PAD; y += rowH + PAD; rowH = 0; } pos.push([x, y]); x += CW + PAD; rowH = Math.max(rowH, c.h); });
const legendY = y + rowH + 40, slots = [...Object.entries(DOC.ground), ...Object.entries(DOC.items)];
const H = legendY + 60 + Math.ceil(slots.length / 2) * 26 + 70;
const cv2 = createCanvas(1900, H), ctx = cv2.getContext('2d');
ctx.fillStyle = '#faf6ef'; ctx.fillRect(0, 0, 1900, H);
ctx.fillStyle = '#4a3b30'; ctx.font = "700 30px 'Zen Maru Gothic', sans-serif"; ctx.fillText(`${DOC.name}のマイデザイン：1マスごとのパーツと作者ID`, PAD, 50);
ctx.font = "16px 'Zen Maru Gothic', sans-serif"; ctx.fillStyle = '#6a5a4d';
ctx.fillText('地面は「全面・縁・角・ななめ・内角・段差」のパーツを自動で選ぶ（tools/design_tiles.js）。家具の下の地面は、まわりの地面を続けて敷く。木・花は草地のまま', PAD, 80);
ctx.fillText('作者IDは Pinterest の画像から読み取った。エイブルシスターズのマイデザインの端末で「作者IDで探す」から入手できる（Nintendo Switch Online が必要）', PAD, 102);
cards.forEach((c, i) => { const [X, Y] = pos[i];
  ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.roundRect(X, Y, CW, c.h, 14); ctx.fill();
  ctx.fillStyle = '#4a3b30'; ctx.font = "700 17px 'Zen Maru Gothic', sans-serif"; ctx.fillText(c.m.name.replace(/^細部：/, ''), X + 14, Y + 26);
  const [w, h] = drawModule(ctx, c.m, X + 14, Y + 38);
  ctx.font = "12.5px 'Zen Maru Gothic', sans-serif";
  c.used.forEach((u, k) => { const d = CAT[u.design] || {}, parts = Object.entries(u.parts).map(([p, n]) => p === '個' ? `${n}個` : `${p}${n}`).join('・');
    ctx.fillStyle = '#4a3b30'; ctx.fillText(`${u.slot}（${parts}）`, X + 14, Y + 38 + h + 22 + k * 19);
    ctx.fillStyle = d.checked === false ? '#b0563b' : '#2f6b8a'; ctx.fillText((d.ma || '') + (d.checked === false ? ' 要確認' : ''), X + CW - 150, Y + 38 + h + 22 + k * 19); });
});
ctx.fillStyle = '#4a3b30'; ctx.font = "700 20px 'Zen Maru Gothic', sans-serif"; ctx.fillText('割り当て（地面と家具 → マイデザイン）', PAD, legendY);
ctx.font = "13.5px 'Zen Maru Gothic', sans-serif";
slots.forEach(([ch, s], i) => { const d = CAT[s.design] || {}, X = PAD + (i % 2) * 930, Y = legendY + 30 + Math.floor(i / 2) * 26;
  if (DOC.ground[ch]) { ctx.fillStyle = s.color; ctx.fillRect(X, Y - 13, 18, 18); } else { const it = ITEM[ch] || ['?', '#999', '#fff']; ctx.fillStyle = it[1]; ctx.fillRect(X, Y - 13, 18, 18); ctx.fillStyle = it[2]; ctx.font = "700 11px 'Zen Maru Gothic', sans-serif"; ctx.fillText(it[0], X + 3, Y + 1); ctx.font = "13.5px 'Zen Maru Gothic', sans-serif"; }
  ctx.fillStyle = '#4a3b30'; ctx.fillText(`${s.slot}：${(d.name || '').replace(/（.*$/, '')}　${d.creator || ''}`, X + 26, Y + 1);
  ctx.fillStyle = '#2f6b8a'; ctx.fillText(d.ma || '', X + 760, Y + 1); });
fs.mkdirSync(path.dirname(out), { recursive: true });
fs.writeFileSync(out, cv2.toBuffer('image/png'));
console.log('保存:', path.relative(ROOT, out), `${mods.length}個のモジュール`);
