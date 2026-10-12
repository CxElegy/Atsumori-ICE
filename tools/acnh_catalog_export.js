// animal-crossing@8.2.0（あつ森のデータ表）から、島の外に置ける物・工事（坂・橋）・住民の目録を書き出す
const ac = require('animal-crossing'), fs = require('fs');
const SHEETS = ['Housewares', 'Miscellaneous', 'Wall-mounted', 'Fencing', 'Umbrellas', 'Artwork'];   // かさ（地面に開いて置ける）・美術品（像）も外に置ける
const icon = i => { const v = (i.variations || [])[0] || i; const u = v.image || v.storageImage || v.closetImage || i.image || i.storageImage || i.highResTexture || ''; return u.replace('https://acnhcdn.com/latest/FtrIcon/', '').replace('https://acnhcdn.com/latest/', ''); };
const uniq = i => { const seen = {}, out = []; (i.variations || []).forEach(v => { if (v.variation && !seen[v.variation]) { seen[v.variation] = 1; out.push([v.variation, (v.variantTranslations || {}).jPja || '', (v.image || '').replace('https://acnhcdn.com/latest/FtrIcon/', '')]); } }); return out; };
const items = {};
ac.items.filter(i => SHEETS.includes(i.sourceSheet)).forEach(i => {
  const t = i.translations || {};
  items[i.name] = { ja: t.jPja || '', zh: t.cNzh || '', sheet: i.sourceSheet, size: i.size || (i.sourceSheet === 'Fencing' ? '1x1' : ''), tag: i.tag || '',
    src: (i.source || []).join('/'), diy: !!i.diy, ver: i.versionAdded, custom: !!(i.patternCustomize), outdoorOnly: !!i.outdoor,
    vars: uniq(i), icon: icon(i) };
});
const cons = {};
ac.construction.filter(c => ['Incline', 'Bridge', 'Roofing', 'Siding', 'Door', 'Mailbox'].includes(c.category)).forEach(c => { (cons[c.category] = cons[c.category] || {})[c.name] = { ja: (c.translations || {}).jPja || '', img: (c.image || '').replace('https://acnhcdn.com/', '') }; });
const vill = {};
ac.villagers.forEach(v => { vill[v.name] = { ja: (v.translations || {}).jPja || '', sp: v.species, pers: v.personality, house: (v.houseImage || '').replace('https://acnhcdn.com/', ''), ver: v.versionAdded }; });
const out = { note: 'あつ森（ver 2.0）の目録。npm の animal-crossing@8.2.0（コミュニティのデータ表 ACNH Spreadsheet を元にしたもの）から tools/acnh_catalog_export.js で書き出した。物の名前は英語版のゲーム内の名前、ja は日本語版の名前。size は「横x奥行き」のマス。画像は acnhcdn.com（任天堂の画像なのでリポジトリには入れない）', source: 'https://www.npmjs.com/package/animal-crossing (v8.2.0) / https://tinyurl.com/acnh-sheet', items, construction: cons, villagers: vill };
fs.writeFileSync(process.argv[2], JSON.stringify(out));
console.log(Object.keys(items).length, 'items', Object.keys(vill).length, 'villagers');
