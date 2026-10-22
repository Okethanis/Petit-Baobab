/* Recalcule les packs et valises à partir de leur composition (items = articles + quantités) et des prix actuels des articles :
   valeur = somme des articles (+ valeur du pack de base), prix = valeur × (1 − remise) − rabais, arrondi aux 500 FCFA,
   économie = valeur − prix, liste « contents » régénérée avec les noms et prix du moment.
   Usage : node admin/packs.js   (à lancer après chaque changement de prix, avant node build.js) */
const fs = require('fs');
const path = require('path');
const file = path.join(__dirname, '..', 'petit-baobab.html');
let src = fs.readFileSync(file, 'utf8');
const start = src.indexOf('var PRODUCTS = [\n') + 'var PRODUCTS = [\n'.length;
const end = src.indexOf('\n];\n', start);
const lines = src.slice(start, end).split('\n');
const vm = require('vm');
const products = lines.map(l => vm.runInNewContext('(' + l.trim().replace(/,$/, '') + ')'));
const byId = {}; products.forEach(p => { byId[p.id] = p; });
const fmt = n => Math.round(n).toLocaleString('fr-FR') + ' FCFA';
const round500 = n => Math.round(n / 500) * 500;
const done = {};
function compute(p) {
  if (done[p.id] || !p.items) return;
  let value = 0;
  if (p.base) { compute(byId[p.base]); value += byId[p.base].value; }
  const contents = [];
  for (const it of p.items) {
    const a = byId[it.id]; if (!a) throw new Error(p.id + ' : article ' + it.id + ' introuvable');
    if (a.items) compute(a);
    value += a.price * it.qty;
    if (!a.items && a.cat !== 'packs' && a.cat !== 'valise') contents.push(it.qty + ' × ' + a.name + ' (' + fmt(a.price * it.qty) + ')');
  }
  (p.extras || []).forEach(x => contents.push(x));
  const price = round500(value * (1 - (p.discount || 0)) - (p.rebate || 0));
  const before = p.price;
  p.value = value; p.price = price; p.saving = value - price; p.contents = contents;
  done[p.id] = true;
  console.log(p.id + ' : valeur ' + fmt(value) + ', prix ' + fmt(price) + (before !== price ? ' (avant : ' + fmt(before) + ')' : '') + ', économie ' + fmt(p.saving));
}
products.forEach(compute);
const ORDER = ['id', 'cat', 'name', 'price', 'ref', 'badge', 'featured', 'tagline', 'desc', 'age', 'plus', 'specs', 'includes', 'base', 'items', 'discount', 'rebate', 'extras', 'contents', 'value', 'saving', 'image', 'hidden'];
const js = v => typeof v === 'boolean' ? String(v) : typeof v === 'number' ? String(v) : typeof v === 'string' ? "'" + v.replace(/\\/g, '\\\\').replace(/'/g, "\\'") + "'"
  : Array.isArray(v) ? '[' + v.map(js).join(', ') + ']' : '{' + ORDER.filter(k => k in v).concat(Object.keys(v).filter(k => !ORDER.includes(k))).map(k => k + ':' + js(v[k])).join(', ') + '}';
const newLines = lines.map((l, i) => products[i].items ? '  ' + js(products[i]) + (/,\s*$/.test(l) ? ',' : '') : l);
fs.writeFileSync(file, src.slice(0, start) + newLines.join('\n') + src.slice(end));
