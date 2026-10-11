// 画面の HTML（DC 形式）から Component のコードを取り出し、canvas・localStorage・fetch の代用品で動かす道具。
// test_logic.js（ロジックの確認）と snap.js（画面を PNG にする）が使う。node が無い PC では tools/edge_run.py が Edge で動かす。
const fs = require('fs'), path = require('path');
// ブラウザ（tools/edge_run.py）では setImmediate・Buffer が無い
const tick = typeof setImmediate === 'function' ? setImmediate : f => setTimeout(f, 0);
const ROOT = path.join(__dirname, '..');

// 何でも受ける描画の代用品。数に NaN や Infinity が入っていたら記録する（投影の間違いを見つける）
function stubCtx(stats) {
  const grad = { addColorStop() {} };
  const t = { canvas: null };
  return new Proxy(t, {
    get(o, k) {
      if (k in o) return o[k];
      if (k === 'measureText') return s => ({ width: String(s).length * 9 });
      if (/^create/.test(k)) return () => grad;
      if (k === 'getTransform') return () => ({});
      return (...a) => { stats.calls++; for (const v of a) if (typeof v === 'number' && !Number.isFinite(v)) stats.bad.push(k + '(' + a.join(',') + ')'); };
    },
    set(o, k, v) { o[k] = v; return true; }
  });
}
function stubCanvas(stats) {
  const c = { width: 300, height: 150, style: {}, getBoundingClientRect: () => ({ left: 0, top: 0, width: c.width, height: c.height }), toBlob: cb => cb({ size: 1 }), toDataURL: () => 'data:image/png;base64,', toBuffer: () => (typeof Buffer !== 'undefined' ? Buffer.alloc(0) : '') };
  let ctx = null;
  c.getContext = () => ctx || (ctx = Object.assign(stubCtx(stats), {}));
  return c;
}

function loadComponent(file, opt = {}) {
  const stats = { calls: 0, bad: [] };
  const html = fs.readFileSync(path.join(ROOT, file), 'utf8');
  const m = /<script type="text\/x-dc" data-dc-script[^>]*>([\s\S]*?)<\/script>/.exec(html);
  if (!m) throw new Error('DC のスクリプトが見つかりません: ' + file);
  const store = opt.store || {};
  const localStorage = { getItem: k => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); }, removeItem: k => { delete store[k]; } };
  const listeners = {};
  const win = { addEventListener: (n, f) => { (listeners[n] = listeners[n] || []).push(f); }, removeEventListener: (n, f) => { listeners[n] = (listeners[n] || []).filter(x => x !== f); } };
  const made = [];
  const mk = opt.createCanvas || (() => stubCanvas(stats));
  const clicks = [];
  const document = {
    createElement: tag => { if (tag === 'canvas') { const c = mk(300, 150); made.push(c); return c; } const el = { click() { clicks.push(el); }, href: '', download: '' }; return el; },
    fonts: undefined
  };
  const logs = [];
  const fetch = u => { const p = path.join(ROOT, decodeURIComponent(u)); return fs.existsSync(p) ? Promise.resolve({ json: () => Promise.resolve(JSON.parse(fs.readFileSync(p, 'utf8'))), text: () => Promise.resolve(fs.readFileSync(p, 'utf8')) }) : Promise.reject(new Error('404 ' + u)); };
  class DCLogic {
    constructor() { this.props = {}; }
    setState(p) { const n = typeof p === 'function' ? p(this.state) : p; this.state = Object.assign({}, this.state, n); if (this.__up && this.componentDidUpdate) this.componentDidUpdate(); }
  }
  const React = { createRef: () => ({ current: null }) };
  const alerts = [];
  const Comp = new Function('DCLogic', 'React', 'window', 'document', 'localStorage', 'fetch', 'performance', 'setTimeout', 'URL', 'Blob', 'alert', 'confirm', 'console', m[1] + '\nreturn Component;')(
    DCLogic, React, win, document, localStorage, fetch, { now: () => Date.now() }, f => { Promise.resolve().then(f); return 0; }, { createObjectURL: () => 'blob:x' }, class { constructor(p) { this.parts = p; } },
    s => { alerts.push(s); }, () => true, { log: (...a) => logs.push(a.join(' ')), error: (...a) => logs.push('ERR ' + a.join(' ')) });
  const comp = new Comp();
  // 画面の canvas の代わり
  for (const k of ['cv', 'mp', 'cv3']) if (comp[k] && 'current' in comp[k]) comp[k].current = opt['canvas_' + k] || mk(opt.w || 300, opt.h || 150);
  return { comp, stats, store, listeners, clicks, alerts, logs, made, win,
    async start() { if (comp.componentDidMount) comp.componentDidMount(); comp.__up = true; for (let i = 0; i < 20; i++) await new Promise(r => tick(r)); if (comp.componentDidUpdate) { try { comp.componentDidUpdate(); } catch (e) { throw e; } } return comp; },
    async settle() { for (let i = 0; i < 10; i++) await new Promise(r => tick(r)); } };
}
module.exports = { loadComponent, stubCanvas, ROOT };
