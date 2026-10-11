// マイデザインの道を1マスごとにどのパーツ（全面・縁・角・ななめ・内角・段差）で敷くか決める
//   node でも（require）ブラウザでも（window.DesignTiles）使う。designs/<地区>.json の ground を渡す
//   モジュールの外は「同じ地面が続く」とみなす（となりのモジュールとつながるので、外周には縁を付けない）
//   家具のマスは下に同じ地面が続くとみなす。縁を付けるのは草地（.）と、ちがう地面との境だけ。join に書いた地面との境にも付けない
(function (root) {
  const GROUP = { '#': '_' };                       // 横断歩道は車道の一部
  const grp = ch => GROUP[ch] || ch;
  const DIRS = [[0, -1, '北'], [1, 0, '東'], [0, 1, '南'], [-1, 0, '西']];

  // 家具の下の地面：植物（木・花・竹・生け垣・岩）は草地に置くので道を敷かない。それ以外の家具は、まわりで一番多い地面を下に敷く
  const PLANT = 'tFeajyPol';
  const WATER = 'w';   // 水（地形で作る川・船だまり）。道を敷かず、となりの道には縁を付ける
  function underlay(rows, ground, force) {
    const g = rows.map(r => [...r]), H = g.length, W = g[0].length, todo = [];
    g.forEach((row, y) => row.forEach((ch, x) => { if (ch !== '.' && !WATER.includes(ch) && !(ch in ground) && !PLANT.includes(ch)) todo.push([x, y]); }));
    const fill = {};   // 横のとなりを重く見る（車道に止めたバス・線路の上の汽車は、その列の地面を敷く）。決まったマスを次の回に使う
    for (let pass = 0; pass < W + H; pass++) {
      const cand = [];   // はっきり決まるマスから先に決める（同点のマスは、ほかが決まってから）
      todo.forEach(([x, y]) => { if (fill[x + ',' + y]) return; const cnt = {};
        DIRS.forEach(([dx, dy]) => { const yy = y + dy, xx = x + dx; if (yy < 0 || yy >= H || xx < 0 || xx >= W) return; const c = fill[xx + ',' + yy] || g[yy][xx]; if (c in ground) cnt[c] = (cnt[c] || 0) + (dy === 0 ? 1.5 : 1); });
        const r = Object.entries(cnt).sort((p, q) => q[1] - p[1]); if (r.length) cand.push([x, y, r[0][0], !r[1] || r[0][1] > r[1][1]]); });
      const sure = cand.filter(c => c[3]), pick = sure.length ? sure : cand.slice(0, 1);
      if (!pick.length) break;
      pick.forEach(([x, y, c]) => { fill[x + ',' + y] = c; });
    }
    Object.entries(fill).forEach(([k, c]) => { const [x, y] = k.split(',').map(Number); g[y][x] = c; });
    if (force) g.forEach((row, y) => row.forEach((ch, x) => { if (force[rows[y][x]]) g[y][x] = force[rows[y][x]]; }));   // モジュールが決めた下の地面（汽車の下は線路など）
    return g.map(r => r.join(''));
  }

  function tilePieces(rows0, ground, force) {
    const rows = underlay(rows0, ground, force), H = rows.length, W = rows[0].length;
    const at = (x, y) => (x < 0 || y < 0 || x >= W || y >= H) ? null : rows[y][x];
    const same = (x, y, g, G) => { const c = at(x, y); if (c === null) return true; if (c === '.' || WATER.includes(c)) return false; if (!(c in ground)) return true; return grp(c) === g || (G.join || '').includes(c); };
    return rows.map((row, y) => [...row].map((ch, x) => {
      const G = ground[ch]; if (!G) return null;
      const g = grp(ch), miss = DIRS.map(([dx, dy]) => !same(x + dx, y + dy, g, G)), n = miss.filter(Boolean).length;
      const sides = DIRS.filter((d, i) => miss[i]).map(d => d[2]).join('');
      let piece = G.base, kind = 'base';
      if (ch === '#') piece = G.base;
      else if (n === 0) {
        const inner = [[1, -1, 0, 1], [1, 1, 1, 2], [-1, 1, 2, 3], [-1, -1, 3, 0]].filter(([dx, dy]) => !same(x + dx, y + dy, g, G));
        if (inner.length && G.inner) { piece = G.inner; kind = 'inner'; }
      } else if (n === 2 && ((miss[0] || miss[2]) && (miss[1] || miss[3]))) { piece = G.corner || G.edge || G.base; kind = G.corner === 'ななめ' ? 'diag' : 'corner'; }
      else { piece = G.edge || G.base; kind = G.edge ? 'edge' : 'base'; }
      return { ch, slot: G.slot, design: G.design, piece, kind, miss, sides };
    }));
  }

  // モジュールで使うマイデザインの一覧（地面はパーツごとのマス数、家具は個数）
  function designsUsed(rows, doc, force) {
    const out = {}, add = (design, slot, part, n) => { const k = design + '|' + slot; (out[k] = out[k] || { design, slot, parts: {} }).parts[part] = (out[k].parts[part] || 0) + n; };
    tilePieces(rows, doc.ground, force).forEach(r => r.forEach(t => { if (t) add(t.design, t.slot, t.piece, 1); }));
    rows.forEach(r => [...r].forEach(ch => { const it = doc.items[ch]; if (it) add(it.design, it.slot, '個', 1); }));
    if (rows.some(r => r.includes('#')) && doc.ground['#'] && doc.ground['#'].marks) add(doc.ground['#'].marks, '路面の表示', 'LOOK LEFT / RIGHT', 2);
    return Object.values(out);
  }

  const api = { tilePieces, designsUsed, underlay };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.DesignTiles = api;
})(typeof window !== 'undefined' ? window : globalThis);
