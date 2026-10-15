// 案2（第45回）の全島の地勢計画 plan2-terrain.json を、あつ森の決まりと island-planning の点検で確かめる
//   python3 tools/plan_terrain.py --design plan2-design.json --out plan2-terrain.json --quiet && node tools/test_plan2.js
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const ROOT = path.join(__dirname, '..');
const J = f => JSON.parse(fs.readFileSync(path.join(ROOT, f), 'utf8'));
let n = 0, bad = 0;
const ok = (name, c, info) => { n++; if (!c) { bad++; console.log('NG ' + name + (info !== undefined ? '：' + info : '')); } };

const T = J('plan2-terrain.json'), G = T.grid, HL = T.h, D = J('plan2-design.json');
const cells = f => { const out = []; for (let y = 0; y < 96; y++) for (let x = 0; x < 112; x++) if (f(G[y][x], +HL[y][x], x, y)) out.push([x, y]); return out; };
ok('案2 地形：96行×112文字', G.length === 96 && G.every(r => r.length === 112) && HL.length === 96 && HL.every(r => /^[0-3]{112}$/.test(r)));
ok('案2 地形：海と岩は高さ0', cells((c, h) => 'Sr'.includes(c) && h !== 0).length === 0);
ok('案2 地形：砂浜・広場・レンガ・橋は高さ1', cells((c, h) => 'sPKb'.includes(c) && h !== 1).length === 0);
ok('案2 地形：案内所前の広場（P）は12×10（動かせない）', cells(c => c === 'P').length === 120);
ok('案2 地形：飛行場（K）はそのまま', cells(c => c === 'K').length === J('plan-terrain.json').grid.join('').split('K').length - 1);
ok('案2 地形：崖が砂浜・海・岩のとなりにない', cells((c, h, x, y) => h >= 2 && [[1, 0], [-1, 0], [0, 1], [0, -1]].some(([dx, dy]) => 'Ssr'.includes((G[y + dy] || '')[x + dx] || 'S'))).length === 0);
ok('案2 地形：3段目は2段目の1マス内側', cells((c, h, x, y) => h === 3 && [-1, 0, 1].some(dx => [-1, 0, 1].some(dy => +((HL[y + dy] || '')[x + dx] || 0) < 2))).length === 0);
ok('案2 地形：草地の見た目は段と合う', cells((c, h) => (c === '1' && h >= 2) || (c === '3' && h < 2)).length === 0);
const slopeCells = ([x, y, d]) => { const out = []; for (let i = 0; i < 4; i++) for (let k = 0; k < 2; k++) out.push(d === 'E' || d === 'W' ? [x + i, y + k, d === 'E' ? i : 3 - i] : [x + k, y + i, d === 'S' ? i : 3 - i]); return out; };
ok('案2 地形：坂は8個まで', T.inclines.length <= 8, T.inclines.length);
ok('案2 地形：坂は上の1マス＋下の3マス', T.inclines.every(inc => { const sc = slopeCells(inc), top = sc.find(c => c[2] === 0), hi = +HL[top[1]][top[0]]; return sc.every(([x, y, i]) => +HL[y][x] === (i === 0 ? hi : hi - 1)); }));
ok('案2 地形：坂は水・海・広場の上にない', T.inclines.every(inc => slopeCells(inc).every(([x, y]) => !'wSsrPKb'.includes(G[y][x]))));
ok('案2 地形：坂どうしは1マスあける', T.inclines.every((a, i) => T.inclines.every((b, j) => i >= j || !slopeCells(a).some(([x, y]) => slopeCells(b).some(([x2, y2]) => Math.abs(x - x2) <= 1 && Math.abs(y - y2) <= 1)))));
const comps = f => { const seen = new Set(); let k = 0; for (let y = 0; y < 96; y++) for (let x = 0; x < 112; x++) if (f(G[y][x]) && !seen.has(x + ',' + y)) { k++; const st = [[x, y]]; seen.add(x + ',' + y); while (st.length) { const [a, b] = st.pop(); [[1, 0], [-1, 0], [0, 1], [0, -1]].forEach(([dx, dy]) => { const p = (a + dx) + ',' + (b + dy); if (G[b + dy] && f(G[b + dy][a + dx]) && !seen.has(p)) { seen.add(p); st.push([a + dx, b + dy]); } }); } } return k; };
ok('案2 地形：橋は8個まで', comps(c => c === 'b') <= 8, comps(c => c === 'b'));
ok('案2 地形：水は600マス以下・幅1の水がほとんどない', T.stats.water <= 600 && T.stats.water_width1 <= 10, T.stats.water + '・' + T.stats.water_width1);
ok('案2 地形：滝は2〜3か所（霊峰の泉 → 池泉 → 川）', T.stats.waterfalls >= 2 && T.stats.waterfalls <= 3, T.stats.waterfalls);
ok('案2 地形：3段目からの滝がある', cells((c, h, x, y) => c === 'w' && h === 3 && [[1, 0], [-1, 0], [0, 1], [0, -1]].some(([dx, dy]) => (G[y + dy] || '')[x + dx] === 'w' && +HL[y + dy][x + dx] === 2)).length > 0);
ok('案2 地形：枯れ流れ（白砂の砂紋）が日本にある', Object.entries(T.ground || {}).filter(([k, v]) => v === 'm' && +k.split(',')[0] <= 41 && +k.split(',')[1] <= 37).length >= 30);
const fish = T.facilities.filter(f => f.kind === 'fishing');
ok('案2 地形：釣り場は1段目と2段目の両方・2段目は2段目の水のそば', fish.some(f => f.level === 1) && fish.filter(f => f.level === 2).length >= 2 && fish.filter(f => f.level === 2).every(f => [-2, -1, 0, 1, 2].some(dx => [-2, -1, 0, 1, 2].some(dy => (G[f.y + dy] || '')[f.x + dx] === 'w' && +HL[f.y + dy][f.x + dx] === 2))));
ok('案2 地形：自宅・畑・果樹園・採石場・花の交配畑', ['home', 'farm', 'orchard', 'quarry', 'flowers'].every(k => T.facilities.some(f => f.kind === k)));
ok('案2 設計：すべての op に理由（why）', D.ops.every(o => o.why && o.why.length > 5));
// island-planning の点検（tools/island_check.py）
const C = JSON.parse(execFileSync('python3', [path.join(ROOT, 'tools/island_check.py'), '--json'], { encoding: 'utf8' }));
ok('案2 点検：何もない草地が全地区で上限以内', Object.entries(C.open_grass_pct).every(([k, v]) => v <= C.open_grass_limit_pct[k]), JSON.stringify(C.open_grass_pct));
ok('案2 点検：浮いた物（入口の道がない・囲み4割未満）が0', C.floating.length === 0, C.floating.map(f => f.name).join('・'));
ok('案2 点検：地区のさかいの8割以上が地形（崖・水・道・林）の上', C.zone_border_on_terrain_pct >= 80, C.zone_border_on_terrain_pct);
ok('案2 点検：飛行場から道が切れずにつながる・道に着かない目じるし0', C.road_islands === 0 && C.landmarks_off_network.length === 0, C.road_islands + '・' + C.landmarks_off_network.map(l => l.name).join('・'));
// 第47回：あつ森で作れるか（tools/acnh_build.py：本物の建物・目録の家具・マイデザインの貼り方・花と作物・木の植え方）
const A = JSON.parse(execFileSync('python3', [path.join(ROOT, 'tools/acnh_build.py'), '--json'], { encoding: 'utf8', maxBuffer: 1 << 26 }));
ok('案2 あつ森：作れない所が0（建物・家具・花・木・坂と橋の種類）', A.errors.length === 0, A.errors.slice(0, 3).join(' / '));
const BP = J('designs/build_plan2.json'), kinds = BP.buildings.map(b => b.kind);
ok('案2 あつ森：住民の家は10軒まで・博物館・タヌキ商店・エイブル・キャンプ場は1つずつ', kinds.filter(k => k === 'villager').length <= 10 && ['museum', 'nook', 'able', 'campsite'].every(k => kinds.filter(x => x === k).length === 1));
ok('案2 あつ森：置く家具は200個以上（島ぜんぶに家具のまとまりがある）', A.items >= 200, A.items);
console.log(`案2：${n}項目 中 ${n - bad} 項目OK` + (bad ? `・NG ${bad}` : '　→ すべてOK'));
process.exitCode = bad ? 1 : 0;
