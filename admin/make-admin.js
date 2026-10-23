/* Génère la page d'administration du catalogue à partir de petit-baobab.html (même source de vérité que le site).
   Usage : node admin/make-admin.js  → admin/catalogue-admin.html */
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const src = fs.readFileSync(path.join(__dirname, '..', 'petit-baobab.html'), 'utf8');
function extract(name) {
  const m = src.match(new RegExp('var ' + name + ' = ([\\s\\S]*?);\\n\\s*(?=var |/\\*)'));
  if (!m) throw new Error('bloc ' + name + ' introuvable');
  return vm.runInNewContext('(' + m[1] + ')');
}
const UNIVERS = extract('UNIVERS'), CATS = extract('CATS'), PRODUCTS = extract('PRODUCTS');
const thumbs = JSON.parse(fs.readFileSync(path.join(__dirname, 'thumbs.json'), 'utf8'));
const base = PRODUCTS.map(p => ({ id: p.id, ref: p.ref || '', name: p.name, cat: p.cat, price: p.price, badge: p.badge || '', hidden: !!p.hidden, computed: !!p.items, img: p.image ? path.basename(p.image, '.webp') : '',
  desc: p.desc || '', age: p.age || '', plus: Array.isArray(p.plus) ? p.plus : [], specs: Array.isArray(p.specs) ? p.specs : [] }));
const used = {}; base.forEach(p => { if (p.img && thumbs[p.img]) used[p.img] = thumbs[p.img]; });
const data = 'var BASE = ' + JSON.stringify(base) + ';\nvar CATS = ' + JSON.stringify(CATS.map(c => ({ id: c.id, label: c.label, univers: c.univers }))) +
  ';\nvar UNIV = ' + JSON.stringify(UNIVERS.map(u => ({ id: u.id, n: u.n, title: u.title }))) + ';\nvar THUMBS = ' + JSON.stringify(used) + ';';
const tpl = fs.readFileSync(path.join(__dirname, 'template.html'), 'utf8');
const out = tpl.replace('/*__DATA__*/', data);
fs.writeFileSync(path.join(__dirname, 'catalogue-admin.html'), out);
console.log('catalogue-admin.html : ' + base.length + ' articles, ' + Object.keys(used).length + ' vignettes, ' + Math.round(out.length / 1024) + ' Ko');
