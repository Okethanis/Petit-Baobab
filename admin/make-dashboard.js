/* Génère le tableau de bord à partir de petit-baobab.html (même source de vérité que le site et que la page Catalogue).
   Usage : node admin/make-dashboard.js  → admin/tableau-de-bord.html (page à publier) + admin/tableau-de-bord.local.html (même page avec squelette, pour l'ouvrir en local) */
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const src = fs.readFileSync(path.join(__dirname, '..', 'petit-baobab.html'), 'utf8');
function extract(name) {
  const m = src.match(new RegExp('var ' + name + ' = ([\\s\\S]*?);\\n\\s*(?=var |/\\*)'));
  if (!m) throw new Error('bloc ' + name + ' introuvable');
  return vm.runInNewContext('(' + m[1] + ')');
}
const CONFIG = extract('CONFIG'), UNIVERS = extract('UNIVERS'), CATS = extract('CATS'), PRODUCTS = extract('PRODUCTS');
const catUniv = {}; CATS.forEach(c => { catUniv[c.id] = c.univers; });
const items = PRODUCTS.map(p => {
  const o = { i: p.id, n: p.name, p: p.price, c: p.cat, u: (p.cat === 'packs' || p.cat === 'valise') ? p.cat : (catUniv[p.cat] || p.cat) };
  if (p.items) o.k = 1;                 // pack ou valise (prix calculé)
  if (p.stock === 'commande') o.s = 1;  // sur commande, arrive par conteneur
  return o;
});
const univ = {}; UNIVERS.forEach(u => { univ[u.id] = u.title; });
univ.packs = univ.packs || 'Packs naissance'; univ.valise = univ.valise || 'Valise de maternité';
const mark = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'brand', 'mark.json'), 'utf8')).mark;
const data = [
  'var ITEMS = ' + JSON.stringify(items) + ';',
  'var UNIV = ' + JSON.stringify(univ) + ';',
  'var ZONES = ' + JSON.stringify(CONFIG.zones) + ';',
  'var DEPOSIT = ' + JSON.stringify(CONFIG.deposit) + ';',
  'var FREE_FROM = ' + JSON.stringify(CONFIG.freeDeliveryFrom) + ';',
  'var SITE = ' + JSON.stringify(process.env.SITE_URL || 'https://petit-baobab.netlify.app') + ';'
].join('\n');
const tpl = fs.readFileSync(path.join(__dirname, 'dashboard-template.html'), 'utf8');
const out = tpl.replace('/*__DATA__*/', () => data).replace('<!--__MARK__-->', () => mark);
fs.writeFileSync(path.join(__dirname, 'tableau-de-bord.html'), out);
const skeleton = '<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light}body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style></head><body>';
fs.writeFileSync(path.join(__dirname, 'tableau-de-bord.local.html'), skeleton + out + '</body></html>');
console.log('tableau-de-bord.html : ' + items.length + ' articles, ' + Object.keys(univ).length + ' univers, ' + Math.round(out.length / 1024) + ' Ko');
