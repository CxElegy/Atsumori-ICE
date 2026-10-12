// ロジックの確認（node tools/test_logic.js ／ node が無い PC は python tools/edge_run.py tools/test_logic.js）
// 画面の HTML から Component のコードを取り出し、canvas・localStorage・fetch の代用品で動かす。
//  データ：計画の地形・採用したモジュール・見本   組み立て台   完成イメージ   ゲーム画面
// 描画は「最後まで例外なく走るか」と「数に NaN や Infinity が入らないか」を見る。
const fs = require('fs'), path = require('path');
const { loadComponent, ROOT } = require('./dc_harness.js');
const J = f => JSON.parse(fs.readFileSync(path.join(ROOT, f), 'utf8'));

let n = 0, bad = 0;
const fails = [];
function ok(name, cond, detail) { n++; if (!cond) { bad++; fails.push(name + (detail !== undefined ? '：' + detail : '')); } }
const eq = (name, a, b) => ok(name, JSON.stringify(a) === JSON.stringify(b), JSON.stringify(a) + ' ≠ ' + JSON.stringify(b));
const DISTS = { egy: [8, 12, 40, 62], jpn: [32, 12, 67, 61], usa: [65, 12, 101, 47], eur: [57, 39, 101, 85], port: [64, 70, 112, 94], lon: [16, 52, 65, 94] };

(async () => {
  // ================= データ =================
  const T = J('plan-terrain.json'), G = T.grid, HL = T.h;
  ok('地形：grid は96行', G.length === 96); ok('地形：grid は各112文字', G.every(r => r.length === 112));
  ok('地形：h は96行×112文字', HL.length === 96 && HL.every(r => r.length === 112));
  ok('地形：h は0〜3', HL.every(r => /^[0-3]+$/.test(r)));
  const cells = (f) => { const out = []; for (let y = 0; y < 96; y++) for (let x = 0; x < 112; x++) if (f(G[y][x], +HL[y][x], x, y)) out.push([x, y]); return out; };
  ok('地形：海と岩は高さ0', cells((c, h) => 'Sr'.includes(c) && h !== 0).length === 0);
  ok('地形：砂浜・案内所前の広場・レンガ・橋は高さ1', cells((c, h) => 'sPKb'.includes(c) && h !== 1).length === 0);
  const P = cells(c => c === 'P'); ok('地形：案内所前の広場（P）は12×10', P.length === 120, P.length);
  ok('地形：崖が砂浜・海・岩のとなりにない', cells((c, h, x, y) => h >= 2 && [[1, 0], [-1, 0], [0, 1], [0, -1]].some(([dx, dy]) => 'Ssr'.includes((G[y + dy] || '')[x + dx] || 'S'))).length === 0);
  ok('地形：3段目は2段目の1マス内側', cells((c, h, x, y) => h === 3 && [-1, 0, 1].some(dx => [-1, 0, 1].some(dy => +((HL[y + dy] || '')[x + dx] || 0) < 2))).length === 0);
  ok('地形：草地の見た目は段と合う（1=下・3=上）', cells((c, h) => (c === '1' && h >= 2) || (c === '3' && h < 2)).length === 0);
  ok('地形：水面は1段目以上', cells((c, h) => c === 'w' && h < 1).length === 0);
  ok('地形：坂は8個まで', T.inclines.length <= 8, T.inclines.length);
  const slopeCells = ([x, y, d]) => { const out = []; for (let i = 0; i < 4; i++) for (let k = 0; k < 2; k++) out.push(d === 'E' || d === 'W' ? [x + i, y + k, d === 'E' ? i : 3 - i] : [x + k, y + i, d === 'S' ? i : 3 - i]); return out; };
  ok('地形：坂は上の1マス＋下の3マス（段が1違う）', T.inclines.every(inc => { const sc = slopeCells(inc), hi = +HL[sc.find(c => c[2] === 0)[1]][sc.find(c => c[2] === 0)[0]]; return sc.every(([x, y, i]) => +HL[y][x] === (i === 0 ? hi : hi - 1)); }));
  ok('地形：坂は水・海・広場の上にない', T.inclines.every(inc => slopeCells(inc).every(([x, y]) => !'wSsrPKb'.includes(G[y][x]))));
  ok('地形：坂どうしは1マスあける', T.inclines.every((a, i) => T.inclines.every((b, j) => i >= j || !slopeCells(a).some(([x, y]) => slopeCells(b).some(([x2, y2]) => Math.abs(x - x2) <= 1 && Math.abs(y - y2) <= 1)))));
  const comps = (f) => { const seen = new Set(); let k = 0; for (let y = 0; y < 96; y++) for (let x = 0; x < 112; x++) if (f(G[y][x]) && !seen.has(x + ',' + y)) { k++; const st = [[x, y]]; seen.add(x + ',' + y); while (st.length) { const [cx, cy] = st.pop(); for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { const nx = cx + dx, ny = cy + dy, kk = nx + ',' + ny; if (nx >= 0 && nx < 112 && ny >= 0 && ny < 96 && !seen.has(kk) && f(G[ny][nx])) { seen.add(kk); st.push([nx, ny]); } } } } return k; };
  ok('地形：橋は8個まで', comps(c => c === 'b') <= 8, comps(c => c === 'b'));
  ok('地形：ロンドンの尾根は3段目の林（x41〜52・y56〜60）', cells((c, h, x, y) => x >= 41 && x <= 52 && y >= 56 && y <= 60 && ((c !== 't' && c !== 'w') || h !== 3)).length === 0 && cells((c, h, x, y) => x >= 41 && x <= 52 && y >= 56 && y <= 60 && c === 'w').length <= 20);
  ok('地形：統計に水・坂・橋がある', T.stats && T.stats.water > 0 && T.stats.inclines === T.inclines.length);
  ok('地形：滝は3か所まで（高台の釣り場2つ＋3段目の二段の滝）', T.stats.waterfalls >= 2 && T.stats.waterfalls <= 3, T.stats.waterfalls);
  ok('地形：3段目からの滝がある（3段目→2段目→1段目）', cells((c, h, x, y) => c === 'w' && h === 3 && [[1, 0], [-1, 0], [0, 1], [0, -1]].some(([dx, dy]) => (G[y + dy] || '')[x + dx] === 'w' && +HL[y + dy][x + dx] === 2)).length > 0 && cells((c, h, x, y) => c === 'w' && h === 2 && [[0, 1], [0, -1]].some(([dx, dy]) => (G[y + dy] || '')[x + dx] === 'w' && +HL[y + dy][x + dx] === 1)).length > 0);
  ok('地形：水路は幅3（幅1の水のマスがほとんどない）', T.stats.water_width1 <= 10, T.stats.water_width1);
  ok('地形：水は少なめ（600マス以下）', T.stats.water <= 600, T.stats.water);
  const ZJ = [[38, 0], [66, 0], [66, 40], [62, 48], [62, 60], [34, 60], [34, 34], [38, 30]], inJ = (x, y) => { let c = false; for (let i = 0, j = ZJ.length - 1; i < ZJ.length; j = i++) { const [xi, yi] = ZJ[i], [xj, yj] = ZJ[j]; if ((yi > y + .5) !== (yj > y + .5) && x + .5 < (xj - xi) * (y + .5 - yi) / (yj - yi) + xi) c = !c; } return c; };
  const jw = cells((c, h, x, y) => c === 'w' && inJ(x, y));
  ok('地形：日本の水は庭の池（池泉）と滝の流れだけ（120マス以下）', jw.length > 10 && jw.length <= 120 && jw.every(([x, y]) => x >= 44 && x <= 58 && y >= 40 && y <= 59), jw.length);
  ok('地形：枯れ流れ（白砂の砂紋）がある', Object.values(T.ground || {}).filter(v => v === 'm').length >= 50);
  const fish = (T.facilities || []).filter(f => f.kind === 'fishing');
  ok('地形：釣り場は1段目と2段目の両方', fish.some(f => f.level === 1) && fish.filter(f => f.level === 2).length >= 1);
  ok('地形：2段目の釣り場は2段目の水のそば', fish.filter(f => f.level === 2).every(f => [-2, -1, 0, 1, 2].some(dx => [-2, -1, 0, 1, 2].some(dy => (G[f.y + dy] || '')[f.x + dx] === 'w' && +HL[f.y + dy][f.x + dx] === 2))));
  ok('地形：自宅・畑・果樹園・採石場・花の交配畑の場所が決まっている', ['home', 'farm', 'orchard', 'quarry', 'flowers'].every(k => (T.facilities || []).some(f => f.kind === k)));
  const D = J('plan-design.json'); ok('設計：ops がある（書いた順に使う）', D.ops.length >= 30, D.ops.length);
  ok('設計：ロンドンとヨーロッパの水路はまっすぐ（river・直角と45度）', D.ops.filter(o => o.op === 'river').length >= 3 && D.ops.filter(o => o.op === 'river').every(o => o.path.every((p, i) => !i || p[0] === o.path[i - 1][0] || p[1] === o.path[i - 1][1] || Math.abs(p[0] - o.path[i - 1][0]) === Math.abs(p[1] - o.path[i - 1][1]))));
  ok('設計：自然の所（エジプト・北東の山・日本の池）は少し不規則な形（stream）', D.ops.filter(o => o.op === 'stream').length >= 5);
  ok('設計：すべての op に理由（why）', D.ops.every(o => o.why && o.why.length > 5));
  const base = J('island-grid-v4.json'); ok('今の島（island-grid-v4.json）は96行×112文字', base.length === 96 && base.every(r => r.length === 112));

  const C = J('modules-curated.json');
  ok('採用：316個（293＋日本の庭の脇役4＋島の暮らしの施設5＋ロンドン郊外14）', C.count === 316 && C.modules.length === 316, C.modules.length);
  const by = (k) => C.modules.reduce((a, m) => (a[m[k]] = (a[m[k]] || 0) + 1, a), {});
  eq('採用：役別（主役19・脇役66・すき間うめ162・道ばた36・段差28・施設5）', by('role'), { landmark: 19, support: 66, filler: 162, edge: 36, step: 28, facility: 5 });
  eq('採用：テーマ別', by('th'), { 'ロンドン': 63, 'エジプト': 46, '日本': 50, 'アメリカ': 45, 'ハロウィン': 33, 'ヨーロッパ': 46, '地中海': 33 });
  ok('採用：id が重ならない', new Set(C.modules.map(m => m.id)).size === C.modules.length);
  ok('採用：枯山水の石庭（白砂の砂紋 m と石 o）がある', C.modules.filter(m => m.th === '日本' && m.r.join('').includes('m') && m.r.join('').includes('o')).length >= 1);
  ok('採用：形（rows）は長方形', C.modules.every(m => m.r.every(r => r.length === m.r[0].length)));
  ok('採用：理由（why）と点（score）が70点以上', C.modules.every(m => m.why && m.score >= 70));
  ok('採用：段差のモジュール28個に段 lv', C.modules.filter(m => m.role === 'step').every(m => m.lv && m.lv.length === m.r.length));
  const Pop = J('modules-popular.json'); ok('人気の作例：1000個', Pop.count === 1000 && Pop.modules.length === 1000);
  ok('人気の作例：id は pop0001〜pop1000', Pop.modules[0].id === 'pop0001' && Pop.modules[999].id === 'pop1000');
  ok('人気の作例：形が重ならない', new Set(Pop.modules.map(m => m.r.join('|'))).size === 1000);
  const S = J('samples.json');
  ok('見本：全地区に配置がある', Object.keys(DISTS).every(d => (S.dists[d] || []).length > 50));
  ok('見本：全地区とも空き地0（6×6以上の空きなし）', Object.keys(DISTS).every(d => S.stats[d].biggest_empty < 6 && S.stats[d].empty === 0), JSON.stringify(Object.keys(DISTS).map(d => S.stats[d].biggest_empty)));
  ok('見本：配置のモジュールはすべて形がある', Object.values(S.dists).every(l => l.every(p => S.defs[p[0]])));
  ok('見本：配置は地区の範囲の中', Object.entries(S.dists).every(([d, l]) => l.every(p => p[1] >= DISTS[d][0] - 1 && p[1] < DISTS[d][2] && p[2] >= DISTS[d][1] - 1 && p[2] < DISTS[d][3])));
  ok('見本：建物（H）のモジュールは回さない', Object.values(S.dists).every(l => l.every(p => p[3] === 0 || !S.defs[p[0]].join('').includes('H'))));
  // 第31回：ロンドンの郊外（テムズ川の西岸と南西の浜。gen_samples.py の LON_SUB と同じ）は車道にせず旧石畳の小道 p
  const LON_SUB = [[18, 56], [25, 56], [25, 71], [28, 71], [28, 74], [25, 84], [29, 84], [29, 96], [0, 96], [0, 84], [18, 84]];
  const inPoly = (x, y, poly) => { const px = x + .5, py = y + .5; let ins = false; for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) { const [xi, yi] = poly[i], [xj, yj] = poly[j]; if ((yi > py) !== (yj > py) && px < (xj - xi) * (py - yi) / (yj - yi) + xi) ins = !ins; } return ins; };
  ok('見本：道路は地形 p のマスで、値は r:地区（ロンドンの郊外は旧石畳 p）', Object.entries(S.paint).every(([d, pt]) => Object.entries(pt).every(([k, v]) => { const [x, y] = k.split(',').map(Number); return v === 'm' || (G[y][x] === 'p' && (/^r:(lon|egy|jpn|usa|hal|eur|port)$/.test(v) || (d === 'lon' && v === 'p' && inPoly(x, y, LON_SUB)))); })));
  const lonPl = (S.dists.lon || []), defs = S.defs || {};
  ok('見本：ロンドン郊外のモジュール（sub_lon_*）は郊外だけに置く', lonPl.filter(p => p[0].startsWith('sub_lon_')).length >= 5 && lonPl.filter(p => p[0].startsWith('sub_lon_')).every(p => inPoly(p[1], p[2], LON_SUB)));
  ok('見本：ロンドン郊外にレンガ・電話ボックス・バス停・ガス灯・時計を置かない（ハイドパークの小道は別）', lonPl.filter(p => inPoly(p[1], p[2], LON_SUB) && p[0] !== 'lon_park' && defs[p[0]]).every(p => !/[BTKLE]/.test(defs[p[0]].join(''))));
  ok('見本：枯れ流れは白砂の砂紋（m）で塗る', Object.values(S.paint.jpn || {}).filter(v => v === 'm').length >= 30);
  const jc = {}; S.dists.jpn.forEach(([id]) => S.defs[id].join('').split('').forEach(c => { if (c !== '.') jc[c] = (jc[c] || 0) + 1; })); Object.values(S.paint.jpn).forEach(v => { const c = v === 'm' ? 'm' : 'road'; jc[c] = (jc[c] || 0) + 1; });
  const jt = Object.values(jc).reduce((a, b) => a + b, 0);
  ok('見本：日本の白砂（砂紋）は2割まで（白砂ばかりにしない）', (jc.m || 0) / jt <= .2, ((jc.m || 0) / jt).toFixed(2));
  ok('見本：日本に苔・延段・蹲踞・茶庭・紅葉の庭がある', (jc.r || 0) / jt >= .05 && ['niwa_moss', 'niwa_nobedan', 'niwa_tsukubai', 'niwa_roji', 'niwa_momiji'].filter(id => S.dists.jpn.some(p => p[0] === id)).length >= 4);
  ok('見本：日本の主役の石庭（龍安寺の見立て）を置く', S.dists.jpn.some(p => p[0] === 'kare_ryoanji'));
  ok('見本：住民の家はまだ置かない', Object.values(S.dists).every(l => l.every(p => p[0] !== 'house')));
  const FP = k => S.facilities.filter(f => f[1] === k);
  ok('見本：自宅を1つ置く', FP('home').length === 1);
  const hm = FP('home')[0] || [0, 0, -99, -99];
  ok('見本：自宅のそばに畑と果樹園（12マス以内）', ['farm', 'orchard'].every(k => FP(k).some(f => Math.abs(f[2] - hm[2]) <= 12 && Math.abs(f[3] - hm[3]) <= 12)));
  ok('見本：採石場・花の交配畑がある', FP('quarry').length === 1 && FP('flowers').length === 1);
  ok('見本：釣り場は5か所（1段目・2段目・海）', FP('fishing').length === 5);
  ok('見本：ハロウィンの道路は r:hal', Object.values(S.paint.usa || {}).some(v => v === 'r:hal'));

  // ================= 組み立て台 =================
  const MB = loadComponent('Module Builder.dc.html'); const mb = await MB.start();
  ok('組み立て台：地形を読む', !!mb.grid && !!mb.lvl);
  ok('採用：記号はすべて凡例にある', C.modules.every(m => m.r.every(r => [...r].every(c => c === '.' || c in mb.LEG))));
  ok('人気の作例：記号はすべて凡例にある', Pop.modules.every(m => m.r.every(r => [...r].every(c => c === '.' || c in mb.LEG))));
  ok('組み立て台：採用分を足す（基本＋293）', mb.MODS.length > 293 + 900, mb.MODS.length);
  ok('組み立て台：見本を読む', !!mb.SAMPLES);
  eq('組み立て台：地区の判定 ロンドン', mb.zoneAt(30, 70), 'lon'); eq('組み立て台：地区の判定 エジプト', mb.zoneAt(20, 30), 'egy'); eq('組み立て台：地区の判定 日本', mb.zoneAt(50, 30), 'jpn');
  eq('組み立て台：地区の判定 ハロウィン', mb.zoneAt(90, 15), 'hal'); eq('組み立て台：地区の判定 アメリカ', mb.zoneAt(75, 20), 'usa'); eq('組み立て台：地区の判定 ヨーロッパ', mb.zoneAt(80, 55), 'eur'); eq('組み立て台：地区の判定 地中海', mb.zoneAt(90, 85), 'port');
  mb.state.tool = 'road'; eq('組み立て台：道路は地区の舗装 r:lon', mb.paintVal(30, 70), 'r:lon');
  mb.state.paint = { '5,5': 'm', '6,6': 'r:lon' }; ok('組み立て台：白砂（砂紋）は道路ではない', !mb.isRoad(5, 5) && mb.isRoad(6, 6));
  ok('組み立て台：凡例に白砂・畑・果物の木', ['m', 'y', 'j', 'l'].every(c => c in mb.LEG));
  mb.state.tool = 'B'; eq('組み立て台：レンガ道はそのまま B', mb.paintVal(30, 70), 'B');
  eq('組み立て台：stamp 幅3は9マス', mb.stamp(10, 10, 3).length, 9); eq('組み立て台：stamp 幅2は4マス', mb.stamp(10, 10, 2).length, 4);
  // ---- マイデザインの細部（第18回：ロンドン） ----
  const CAT = J('designs/catalog.json'), DZL = J('designs/lon.json'), DT = require('./design_tiles.js');
  ok('マイデザイン：作者IDは MA-0000-0000-0000 の形', CAT.designs.every(d => /^MA-\d{4}-\d{4}-\d{4}$/.test(d.ma)), CAT.designs.filter(d => !/^MA-\d{4}-\d{4}-\d{4}$/.test(d.ma)).map(d => d.id).join(','));
  ok('マイデザイン：目録のidは重ならない', new Set(CAT.designs.map(d => d.id)).size === CAT.designs.length);
  ok('マイデザイン：ロンドンの割り当ては目録にある', [...Object.values(DZL.ground), ...Object.values(DZL.items)].every(g => CAT.designs.some(d => d.id === g.design)));
  ok('マイデザイン：ロンドンのデザインはすべてロンドン向け', [...Object.values(DZL.ground), ...Object.values(DZL.items)].every(g => CAT.designs.find(d => d.id === g.design).themes.includes('lon')));
  ok('マイデザイン：細部モジュールは長方形で、記号は凡例にある', DZL.modules.length >= 8 && DZL.modules.every(m => new Set(m.r.map(r => r.length)).size === 1 && m.r.every(r => [...r].every(c => c === '.' || c in mb.LEG))));
  const tpc = DT.tilePieces(DZL.modules.find(m => m.id === 'lon_d_crossing').r, DZL.ground);
  eq('マイデザイン：車道と歩道の境は段差のパーツ', tpc[2][0].piece, '段差（縁石）'); eq('マイデザイン：横断歩道のパーツ', tpc[3][4].piece, '横断歩道'); eq('マイデザイン：歩道の中はレンガの全面', tpc[5][4].piece, '全面');
  ok('マイデザイン：レンガの外の角は「ななめ」', DT.tilePieces(['..BB', '.BBB', 'BBBB'], DZL.ground).flat().some(t => t && t.kind === 'diag'));
  eq('マイデザイン：車道に止めたバスの下は車道', DT.underlay(DZL.modules.find(m => m.id === 'lon_d_bus').r, DZL.ground)[2], '_______');
  { const mp = DZL.modules.find(m => m.id === 'lon_d_platform'); eq('マイデザイン：汽車の下は線路（モジュールが決める）', DT.underlay(mp.r, DZL.ground, mp.under)[1][5], '^'); ok('マイデザイン：9¾番線に作例の写真と直し方', mp.refs.length >= 1 && mp.fix.length >= 3); }
  ok('マイデザイン：木の下には道を敷かない', DT.underlay(['tB', 'BB'], DZL.ground)[0][0] === 't');
  await new Promise(r => setTimeout(r, 30));
  ok('組み立て台：細部モジュールを一覧に足す', mb.MODS.some(m => m.id === 'lon_d_crossing'));
  const dzc = mb.dzOf(mb.modById('lon_d_crossing'));
  ok('組み立て台：モジュールのマイデザイン（レンガ・車道・LOOK RIGHT）', ['MA-7705-5897-7581', 'MA-3533-6629-1009', 'MA-4969-7472-0919'].every(c => dzc.some(d => d.ma === c)), dzc.map(d => d.ma).join(','));
  ok('組み立て台：エジプトにはまだ割り当てがない', mb.dzOf({ th: 'エジプト', r: ['SS'] }).length === 0);
  mb.state.placed = [{ id: 'p1', m: 'lon_d_bus', x: 30, y: 70, rot: 0 }]; mb.state.paint = { '31,74': 'r:lon' }; mb.state.dist = 'lon';
  ok('組み立て台：買い物リストにマイデザイン', mb.shopping('dist').designs.some(d => d.ma === 'MA-2644-7906-9909'));
  mb.state.placed = []; mb.state.paint = {};
  ok('立体図：車道と線路の色', /_: '#5c5856'/.test(fs.readFileSync(path.join(ROOT, 'London Render.dc.html'), 'utf8')));
  // ---- モジュールの組み方（Module Guide） ----
  ok('マイデザイン：目録の全件に作者の画像のリンク', CAT.designs.every(d => d.images.length && d.images.every(u => /^https:\/\/i\.pinimg\.com\//.test(u)) && /^https:\/\/www\.pinterest\.com\/search/.test(d.search)));
  ok('マイデザイン：参考の写真はあるモジュールに付く', CAT.examples.every(x => x.for.every(id => DZL.modules.some(m => m.id === id) || id in S.defs)));
  ok('マイデザイン：案の選択肢はすべてあるモジュール', DZL.options.every(o => o.choices.every(id => DZL.modules.some(m => m.id === id) || id in S.defs)));
  ok('番号：作例 R-0000・マイデザイン D-000 は重ならない', (() => { const r = J('designs/refs.json').map(x => x.no), d = CAT.designs.map(x => x.no); return r.every(x => /^R-\d{4}$/.test(x)) && d.every(x => /^D-\d{3}$/.test(x)) && new Set(r).size === r.length && new Set(d).size === d.length; })());
  { const R = J('designs/refs.json'), by = Object.fromEntries(R.map(r => [r.no, r])); ok('判定：R-0045 不採用・R-0033 はヨーロッパ', by['R-0045'].verdict === '不採用' && /ヨーロッパ/.test(by['R-0033'].use)); }
  ok('通り道：P1〜P9（坂3本と橋で立体交差）', J('designs/lon_paths.json').routes.map(r => r.id).sort().join() === 'P1,P2,P3,P4,P5,P6,P7,P8,P9');
  ok('2段の運河：切り通しの運河の両岸は1段目の曳舟道、その外は2段目の高台で、坂は切り通しの中', (() => { const inc = T.inclines.find(([x, y]) => x >= 46 && x <= 53 && y >= 60 && y <= 70); if (!inc) return false; return [63, 64, 65, 66].every(y => G[y][50] === 'w' && T.h[y][48] === '1' && T.h[y][53] === '1' && T.h[y][45] === '2' && T.h[y][55] === '2'); })());
  ok('二層の町（第42回）：切り通しの両岸に坂が1本ずつ、主軸（橋のたもと→時計台）の大階段、キングス・クロスの高架（2段目）', T.inclines.some(([x, y, d]) => x === 52 && y === 62 && d === 'S') && T.inclines.some(([x, y, d]) => x === 47 && y === 62 && d === 'S') && T.inclines.some(([x, y, d]) => x === 43 && y === 66 && d === 'S') && T.h[67][41] === '1' && T.h[66][41] === '2' && T.h[76][32] === '2' && T.h[77][32] === '2' && T.h[78][32] === '1');
  ok('作り直し待ちのモジュール（retired）は場所を持たない', DZL.modules.filter(m => m.retired).every(m => !m.at));
  ok('判定：駅が作れるマイデザは採用・飛行機ラウンジ', CAT.designs.find(x => x.ma === 'MA-2715-7913-6849').verdict === '採用' && DZL.options[0].default === 'lon_d_station');
  ok('作例の目録：URLと検索語', J('designs/refs.json').length >= 200 && J('designs/refs.json').every(r => /^https:\/\/i\.pinimg\.com\//.test(r.url) && r.q));
  const MG = loadComponent('Module Guide.dc.html', { w: 400, h: 300 }); const mg = await MG.start(); await new Promise(r => setTimeout(r, 30)); mg.setState({});
  ok('組み方：読み込んで描く', !!mg.DT && !!mg.DOC && MG.stats.calls > 100 && MG.stats.bad.length === 0, MG.stats.bad.slice(0, 2).join(','));
  const gr = mg.renderVals();
  ok('組み方：横断歩道の角の地面（レンガ・車道・横断歩道・LOOK RIGHT）', gr.grounds.length === 4 && gr.grounds.every(g => /^MA-/.test(g.ma) && g.img), gr.grounds.map(g => g.slot).join(','));
  ok('組み方：マイデザインを貼る家具（花かご・円柱ポスト）と、ほかの家具', gr.dzItems.map(d => d.ma).join() === 'MA-1944-3607-0570,MA-4037-0735-3722' && gr.plain.length === 3);
  eq('組み方：置く所の言い方', mg.posText(mg.cur(), 'L'), '奥の左端・奥の右端・手前の右端');
  mg.setState({ group: 'adopt', sel: 'lon_934' }); const g934 = mg.renderVals();
  ok('組み方：採用ずみのモジュール（9¾番線）も組める', g934.mName.startsWith('9¾') && g934.dzItems.some(d => d.ma === 'MA-5454-6202-3841') && /見本での場所/.test(g934.mPlace), g934.mPlace);
  eq('組み方：横に続く家具はまとめて言う', mg.posText(mg.cur(), 'C'), '奥から3列目の4〜6番目');
  mg.setState({ tab: 'book', bookTh: 'lon' }); const gb = mg.renderVals(); ok('図鑑：ロンドンのデザインを画像つきで並べる', gb.book.length >= 25 && gb.book.every(d => d.img && d.ma));
  ok('組み立て台：モジュールの組み方へのリンク', fs.readFileSync(path.join(ROOT, 'Module Builder.dc.html'), 'utf8').includes('Module Guide.dc.html'));
  const lc = mb.lineCells([10, 10], [20, 10], 1); ok('組み立て台：直線は横にまっすぐ', lc.length === 11 && lc.every(c => c[1] === 10));
  const lc2 = mb.lineCells([10, 10], [20, 20], 1); ok('組み立て台：斜め45度', lc2.length === 11 && lc2.every(c => c[0] - 10 === c[1] - 10));
  eq('組み立て台：回転 R で4回もとに戻る', mb.rows({ r: ['ab', 'cd', 'ef'] }, 4).map(r => r.join('')), ['ab', 'cd', 'ef']);
  eq('組み立て台：90度回転', mb.rows({ r: ['ab', 'cd'] }, 1).map(r => r.join('')), ['ca', 'db']);
  // 置く・消す・元に戻す
  mb.state.placed = []; mb.state.paint = {}; mb.hist = []; mb.fut = [];
  mb.state.tool = 'place'; mb.state.mod = 'lon_corner';
  mb.remember(); mb.setState(s => ({ placed: [{ id: 1, m: 'lon_corner', x: 30, y: 74, rot: 0 }] }));
  ok('組み立て台：置くと配置が増える', mb.state.placed.length === 1); mb.undo(); ok('組み立て台：元に戻す', mb.state.placed.length === 0); mb.redo(); ok('組み立て台：やり直す', mb.state.placed.length === 1);
  mb.state.tool = 'road'; mb.remember(); mb.applyCells([[40, 70], [41, 70]]); ok('組み立て台：道路を塗る', Object.values(mb.state.paint).includes('r:lon'));
  mb.state.tool = 'erase'; mb.remember(); mb.applyCells([[40, 70]]); ok('組み立て台：消しゴムで道を消す', !mb.state.paint['40,70'] && !!mb.state.paint['41,70']);
  // 置けるかの確認
  mb.state.placed = [{ id: 1, m: 'house', x: 20, y: 56, rot: 0 }]; mb._issFor = null;
  mb.state.placed = [{ id: 2, m: 'lon_corner', x: 30, y: 62, rot: 0 }]; mb._issFor = null; ok('置けるか：案内所前の広場（P）の上は赤', Object.keys(mb.issuesOf()).length === 1);
  const wy = G.findIndex(r => r.includes('w')), wx = G[wy].indexOf('w');
  mb.state.placed = [{ id: 3, m: 'lon_corner', x: wx, y: wy, rot: 0 }]; mb._issFor = null; ok('置けるか：水の上は赤', Object.keys(mb.issuesOf()).length === 1);
  mb.state.placed = [{ id: 4, m: 'lon_corner', x: 30, y: 78, rot: 0 }, { id: 5, m: 'lon_corner', x: 31, y: 78, rot: 0 }]; mb._issFor = null; ok('置けるか：家具どうしの重なりは赤', Object.keys(mb.issuesOf()).length >= 1);
  const st = [...Array(96).keys()].map(y => [...Array(112).keys()].map(x => [x, y])).flat().find(([x, y]) => G[y][x] === '3' && G[y][x + 1] === '3' && HL[y][x] === '2' && G[y + 1][x] === '1');
  // 見本を置いて確認：全地区で赤い枠がない
  for (const d of Object.keys(DISTS)) { mb.state.placed = []; mb.state.paint = {}; mb._issFor = null; mb.placeSample(d); mb._issFor = null; const iss = Object.keys(mb.issuesOf()); ok(`見本を置く（${d}）：置けない所が0`, iss.length === 0, iss.length + '件'); }
  mb.state.placed = []; mb.state.paint = {}; mb._issFor = null; mb.placeSample('all'); mb._issFor = null; ok('見本を置く（島全体）：置けない所が0', Object.keys(mb.issuesOf()).length === 0);
  ok('見本を置く：道路の塗りも一緒に置く', Object.keys(mb.state.paint).length > 500, Object.keys(mb.state.paint).length);
  const sh = mb.shopping('all'); ok('買い物リスト：道・地面と家具を数える', sh.ground.length > 3 && sh.items.length > 5);
  ok('買い物リスト：道路は地区ごとの舗装名', sh.ground.some(g => /道路・/.test(g.name)));
  const snap = mb.snapshot(); ok('保存：placed・paint・dist・defs', snap.placed.length > 100 && snap.defs && snap.dist);
  ok('書き出した配置を読み込める', mb.importText(JSON.stringify(snap)) === true);
  ok('読み込み：JSON でないものは止める', mb.importText('{x') === false && MB.alerts.length >= 1);
  ok('読み込み：配置ファイルでないものは止める', mb.importText('{"a":1}') === false);
  mb.state.dist = 'lon'; mb.setState({ dist: 'lon' }); const before = mb.state.placed.length; mb.hist = []; mb.remember(); mb.setState(s => ({ placed: s.placed.filter(p => p.x < 16) })); ok('地区を全消去（配置が減る）', mb.state.placed.length < before);
  mb.draw(); ok('組み立て台：描画が最後まで走る', MB.stats.calls > 100 && MB.stats.bad.length === 0, MB.stats.bad.slice(0, 2).join(' '));
  const rv = mb.renderVals(); ok('組み立て台：画面の値（地区・道具・一覧）', rv.dists.length === 7 && rv.tools.length >= 8 && rv.mods.length > 0 && rv.total > 900);
  ok('組み立て台：配置を localStorage に自動保存', !!MB.store['wti-module-board']);
  MB.listeners.keydown && MB.listeners.keydown.forEach(f => f({ key: 'r', target: { tagName: 'BODY' } })); ok('組み立て台：R キーで回転', mb.state.rot === 1);
  MB.listeners.keydown && MB.listeners.keydown.forEach(f => f({ key: 'Escape', target: { tagName: 'BODY' } })); eq('組み立て台：Esc で選ぶ道具', mb.state.tool, 'select');
  ok('組み立て台：ゲーム画面へのリンクがある', fs.readFileSync(path.join(ROOT, 'Module Builder.dc.html'), 'utf8').includes('Game View.dc.html'));

  // ================= 完成イメージ =================
  const store = { 'wti-module-board': JSON.stringify(snap) };
  const LR = loadComponent('London Render.dc.html', { store, w: 1200, h: 800 }); const lr = await LR.start();
  ok('完成イメージ：地形と見本を読む', !!lr.T && !!lr.SM);
  for (const v of Object.keys(lr.VIEWS)) { lr.dk = null; LR.stats.calls = 0; lr.setState({ view: v }); ok(`完成イメージ：範囲「${lr.VIEWS[v][0]}」を描く`, LR.stats.calls > 200 && LR.stats.bad.length === 0, LR.stats.bad.slice(0, 2).join(' ')); }
  for (const t of ['dusk', 'night']) { lr.dk = null; LR.stats.calls = 0; lr.setState({ view: 'lon', time: t }); ok(`完成イメージ：${t} を描く`, LR.stats.calls > 200); }
  for (const nm of ['dist', 'none']) { lr.dk = null; lr.setState({ names: nm }); ok(`完成イメージ：名前「${nm}」`, LR.stats.bad.length === 0); }
  ok('完成イメージ：組み立て台の配置で描く', lr.state.source === '組み立て台の配置で描画中', lr.state.source);
  const LR2 = loadComponent('London Render.dc.html', { w: 1200, h: 800 }); const lr2 = await LR2.start(); ok('完成イメージ：配置がなければ見本で描く', lr2.state.source === '見本の配置で描画中', lr2.state.source);
  ok('完成イメージ：PNG で保存できる', (() => { const r = lr.renderVals(); r.savePng(); return true; })());
  ok('完成イメージ：8以上の見る範囲', Object.keys(lr.VIEWS).length >= 8);
  ok('完成イメージ：地区の境目は組み立て台と同じ', ['lon', 'egy', 'jpn', 'usa', 'hal', 'eur', 'port'].every((z, i) => true) && lr.zoneAt(90, 15) === 'hal' && lr.zoneAt(30, 70) === 'lon');

  // ================= ゲーム画面 =================
  const GV = loadComponent('Game View.dc.html', { store: {}, canvas_cv: undefined, w: 1280, h: 720 }); const gv = await GV.start();
  ok('ゲーム画面：地形と見本を読む', !!gv.T && !!gv.SM);
  ok('ゲーム画面：配置は見本', gv.state.source === '見本の配置で描画中', gv.state.source);
  for (const [d, v] of Object.entries(gv.SPOTS)) for (const [nm, x, y] of v[1]) { gv.dk = null; GV.stats.calls = 0; GV.stats.bad = []; gv.setState({ dist: d, tx: x, ty: y }); ok(`ゲーム画面：${v[0]}・${nm}（${x},${y}）を描く`, GV.stats.calls > 200 && GV.stats.bad.length === 0, GV.stats.bad.slice(0, 2).join(' ')); }
  for (const cam of ['near', 'far', 'normal']) { gv.dk = null; GV.stats.calls = 0; gv.setState({ cam }); ok(`ゲーム画面：カメラ「${gv.CAMS[cam][0]}」`, GV.stats.calls > 200 && GV.stats.bad.length === 0); }
  for (const t of ['dusk', 'night', 'day']) { gv.dk = null; GV.stats.calls = 0; gv.setState({ time: t }); ok(`ゲーム画面：時間 ${t}`, GV.stats.calls > 200 && GV.stats.bad.length === 0); }
  gv.dk = null; gv.setState({ names: 'none' }); ok('ゲーム画面：名前「なし（写真）」で描く', GV.stats.bad.length === 0);
  gv.setState({ names: 'all', tx: 0, ty: 0 }); gv.move(-5, -5); ok('ゲーム画面：地図の外へは出ない（左上）', gv.state.tx === 0 && gv.state.ty === 0);
  gv.setState({ tx: 111, ty: 95 }); gv.move(5, 5); ok('ゲーム画面：地図の外へは出ない（右下）', gv.state.tx === 111 && gv.state.ty === 95);
  gv.setState({ tx: 50, ty: 50 }); GV.listeners.keydown.forEach(f => f({ key: 'ArrowRight', shiftKey: false, preventDefault() {}, target: { tagName: 'BODY' } })); eq('ゲーム画面：矢印キーで1マス', gv.state.tx, 51);
  GV.listeners.keydown.forEach(f => f({ key: 'ArrowRight', shiftKey: true, preventDefault() {}, target: { tagName: 'BODY' } })); eq('ゲーム画面：Shift で4マス', gv.state.tx, 55);
  GV.listeners.keydown.forEach(f => f({ key: 'w', shiftKey: false, preventDefault() {}, target: { tagName: 'BODY' } })); eq('ゲーム画面：W で北へ1マス', gv.state.ty, 49);
  gv.mp.current.getBoundingClientRect = () => ({ left: 0, top: 0, width: 336, height: 288 }); gv.renderVals().onMap({ clientX: 30, clientY: 30 }); ok('ゲーム画面：小地図のクリックでそこへ立つ', gv.state.tx === 10 && gv.state.ty === 10, gv.state.tx + ',' + gv.state.ty);
  const rv2 = gv.renderVals(); ok('ゲーム画面：立っている所の表示（区画・座標・地区・段・地形）', /^いま立っている所：[A-F][1-7]（x\d+, y\d+）・.+・\d段目・/.test(rv2.where), rv2.where);
  ok('ゲーム画面：PNG で保存できる', (() => { rv2.savePng(); return true; })());
  const GV2 = loadComponent('Game View.dc.html', { store: { 'wti-module-board': JSON.stringify(snap) }, w: 1280, h: 720 }); const gv2 = await GV2.start(); ok('ゲーム画面：組み立て台の配置で描く', gv2.state.source === '組み立て台の配置で描画中', gv2.state.source);
  ok('ゲーム画面：地点はすべて陸（水・海・岩の上に立たない）', Object.values(gv.SPOTS).every(v => v[1].every(([nm, x, y]) => '13tpsPKb'.includes(G[y][x]))), '')
  ok('ゲーム画面：カメラは3種（50°/38°/20°）', gv.CAMS.normal[1] === 50 && gv.CAMS.near[1] === 38 && gv.CAMS.far[1] === 20);
  ok('ゲーム画面：高さは1段＝1.1マス', /\* 1\.1/.test(fs.readFileSync(path.join(ROOT, 'Game View.dc.html'), 'utf8')));

  console.log(fails.length ? fails.map(f => 'NG ' + f).join('\n') : '');
  console.log(`${n}項目 中 ${n - bad} 項目OK` + (bad ? `・NG ${bad}` : '　→ すべてOK'));
  process.exitCode = bad ? 1 : 0;
})().catch(e => { console.error(e); process.exitCode = 1; });
