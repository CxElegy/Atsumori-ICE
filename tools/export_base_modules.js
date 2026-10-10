// 組み立て台の基本モジュール（手書き＋自動生成）を取り出して tools/base-modules.json に書く（見本の自動配置が読む）。
// 使い方: node tools/export_base_modules.js
const fs = require('fs'), path = require('path');
const root = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'Module Builder.dc.html'), 'utf8');
const m = /<script type="text\/x-dc" data-dc-script>([\s\S]*?)<\/script>/.exec(html);
class DCLogic { constructor() { this.props = {}; } }
const React = { createRef: () => ({ current: null }) };
const Component = new Function('DCLogic', 'React', m[1] + '\nreturn Component;')(DCLogic, React);
const c = new Component();
const mods = c.MODS.map(x => ({ id: x.id, th: x.th, name: x.name, r: x.r, note: x.note, mat: x.mat || '' }));
fs.writeFileSync(path.join(__dirname, 'base-modules.json'), JSON.stringify({ count: mods.length, modules: mods }));
console.log('base-modules.json:', mods.length, '個');
