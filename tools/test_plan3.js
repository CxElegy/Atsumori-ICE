// 案3（第49回）：地形から作り直した島 plan3-terrain.json と designs/build_plan3.json を、あつ森の決まりと island-planning の点検で確かめる
//   bash tools/plan3_build.sh && node tools/test_plan3.js（案4は ICE_PLAN=4 をつける）
const PL = process.env.ICE_PLAN || '3';
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const ROOT = path.join(__dirname, '..');
const J = f => JSON.parse(fs.readFileSync(path.join(ROOT, f), 'utf8'));
let n = 0, bad = 0;
const ok = (name, c, info) => { n++; if (!c) { bad++; console.log('NG ' + name + (info !== undefined ? '：' + info : '')); } };

const T = J(`plan${PL}-terrain.json`), G = T.grid, HL = T.h, SPEC = J(`designs/plan${PL}_spec.json`);
const N4 = [[1, 0], [-1, 0], [0, 1], [0, -1]];
const at = (x, y) => (G[y] || '')[x] || 'S', lv = (x, y) => +((HL[y] || '')[x] || 0);
const cells = f => { const out = []; for (let y = 0; y < 96; y++) for (let x = 0; x < 112; x++) if (f(G[y][x], +HL[y][x], x, y)) out.push([x, y]); return out; };
ok('案3 地形：96行×112文字', G.length === 96 && G.every(r => r.length === 112) && HL.length === 96 && HL.every(r => /^[0-3]{112}$/.test(r)));
ok('案3 地形：海と岩は高さ0', cells((c, h) => 'Sr'.includes(c) && h !== 0).length === 0);
ok('案3 地形：案内所前の広場（P）は12×10', cells(c => c === 'P').length === 120);
ok('案3 地形：飛行場（K）は動かさない', cells(c => c === 'K').length === J('plan-terrain.json').grid.join('').split('K').length - 1);
ok('案3 地形：崖が砂浜・海・岩のとなりにない', cells((c, h, x, y) => h >= 2 && N4.some(([dx, dy]) => 'Ssr'.includes(at(x + dx, y + dy)))).length === 0);
ok('案3 地形：3段目は2段目の1マス内側', cells((c, h, x, y) => h === 3 && [-1, 0, 1].some(dx => [-1, 0, 1].some(dy => lv(x + dx, y + dy) < 2))).length === 0);
ok('案3 地形：崖の段は2マス幅以上（縦か横に同じ段が続く）', cells((c, h, x, y) => h >= 2 && c !== 'w' && !((lv(x - 1, y) >= h || lv(x + 1, y) >= h) && (lv(x, y - 1) >= h || lv(x, y + 1) >= h))).length === 0);
ok('案3 地形：川は西と南の河口から海へ出る', at(13, 38) === 'w' && [70, 71, 72, 73].some(x => at(x, 83) === 'w'));
ok('案3 地形：滝がある（上の段の水が下の段の水へ）', cells((c, h, x, y) => c === 'w' && N4.some(([dx, dy]) => at(x + dx, y + dy) === 'w' && lv(x + dx, y + dy) === h - 1)).length > 0);
const islets = (() => { const seen = new Set(); let k = 0; for (let y = 0; y < 96; y++) for (let x = 0; x < 112; x++) { if ('wSb'.includes(G[y][x]) || seen.has(x + ',' + y)) continue; const st = [[x, y]], part = []; seen.add(x + ',' + y); let open = false; while (st.length) { const [a, b] = st.pop(); part.push([a, b]); for (const [dx, dy] of N4) { const c = at(a + dx, b + dy); if (c === 'S' || c === 'b') { open = true; continue; } if (c === 'w') continue; const q = (a + dx) + ',' + (b + dy); if (!seen.has(q)) { seen.add(q); st.push([a + dx, b + dy]); } } } if (!open && part.length >= 2) k++; } return k; })();
ok('案3 地形：水に囲まれた中島がある', islets >= 1, islets);
const slopeCells = ([x, y, d]) => { const out = []; for (let i = 0; i < 4; i++) for (let k = 0; k < 2; k++) out.push(d === 'E' || d === 'W' ? [x + i, y + k, d === 'E' ? i : 3 - i] : [x + k, y + i, d === 'S' ? i : 3 - i]); return out; };
ok('案3 地形：坂は10個まで（2.0 のプロの工事の許可）', T.inclines.length <= 10, T.inclines.length);
ok('案3 地形：坂は上の1マス＋下の3マス', T.inclines.every(inc => { const sc = slopeCells(inc), top = sc.find(c => c[2] === 0), hi = lv(top[0], top[1]); return sc.every(([x, y, i]) => lv(x, y) === (i === 0 ? hi : hi - 1)); }));
ok('案3 地形：坂は水・海・広場の上にない', T.inclines.every(inc => slopeCells(inc).every(([x, y]) => !'wSsrPKb'.includes(at(x, y)))));
ok('案3 地形：橋は10個まで（2.0 のプロの工事の許可）・幅4で水3〜5マス', T.bridges.length <= 10 && T.bridges.every(([x0, y0, x1, y1]) => { const w = x1 - x0, h = y1 - y0; return (w === 4 && h >= 3 && h <= 5) || (h === 4 && w >= 3 && w <= 5); }), JSON.stringify(T.bridges));
ok('案3 地形：同じ種（seed）から作り直せる', T.seed === SPEC.seed);
// island-planning の点検（tools/island_check.py）
const env = Object.assign({}, process.env, { ICE_PLAN: PL });
const C = JSON.parse(execFileSync('python3', [path.join(ROOT, 'tools/island_check.py'), '--json'], { encoding: 'utf8', env }));
ok('案3 点検：浮いた物（入口の道がない・囲み4割未満）が0', C.floating.length === 0, C.floating.map(f => f.name).join('・'));
ok('案3 点検：地区のさかいの8割以上が地形（崖・水・道・林）の上', C.zone_border_on_terrain_pct >= 80, C.zone_border_on_terrain_pct);
ok('案3 点検：飛行場から道が切れずにつながる・道に着かない目じるし0', C.road_islands === 0 && C.landmarks_off_network.length === 0, C.road_islands + '・' + C.landmarks_off_network.map(l => l.name).join('・'));
// あつ森で作れるか（tools/acnh_build.py）
const A = JSON.parse(execFileSync('python3', [path.join(ROOT, 'tools/acnh_build.py'), '--json'], { encoding: 'utf8', maxBuffer: 1 << 26, env }));
ok('案3 あつ森：作れない所が0（建物・家具・花・木・坂と橋の種類）', A.errors.length === 0, A.errors.slice(0, 3).join(' / '));
const BP = J(`designs/build_plan${PL}.json`), kinds = BP.buildings.map(b => b.kind);
ok('案3 あつ森：住民の家は10軒・博物館・タヌキ商店・エイブル・キャンプ場は1つずつ', kinds.filter(k => k === 'villager').length === 10 && ['museum', 'nook', 'able', 'campsite'].every(k => kinds.filter(x => x === k).length === 1));
ok('案3 あつ森：置く家具は250個以上', A.items >= 250, A.items);
const placed = new Set(BP.groups.filter(g => g.kit).map(g => g.kit));
ok('案3 設計：ロンドンの見せ場（spec の kits）がすべて置けた', SPEC.kits.every(k => BP.groups.some(g => g.kit === k.kit && g.zone === k.zone && (!k.at || (g.at[0] === k.at[0] && g.at[1] === k.at[1])))), SPEC.kits.filter(k => !placed.has(k.kit)).map(k => k.kit).join('・'));
console.log(`案${PL}：${n}項目 中 ${n - bad} 項目OK` + (bad ? `・NG ${bad}` : '　→ すべてOK'));
process.exitCode = bad ? 1 : 0;
