/* Ajoute au site les nouveaux articles créés dans la page Catalogue, et remplace les photos changées.
   Usage : node admin/import-new.js <dossier de l'export (articles/*.json)> <dossier des photos téléchargées (<asset>.*)> [--dry]
   Un nouvel article (isNew:true) devient une ligne de PRODUCTS (id tiré de la référence ou du nom) ; sa photo passe par admin/photo.py.
   Affiche à la fin la correspondance « document → id du site » : ces documents sont à supprimer de la base après publication. */
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const [dir, photos] = process.argv.slice(2); const dry = process.argv.includes('--dry');
const ROOT = path.join(__dirname, '..'), file = path.join(ROOT, 'petit-baobab.html');
let src = fs.readFileSync(file, 'utf8');
const docs = fs.readdirSync(path.join(dir, 'articles')).filter(f => f.endsWith('.json')).map(f => ({ docId: f.replace(/\.json$/, ''), ...JSON.parse(fs.readFileSync(path.join(dir, 'articles', f), 'utf8')) })).map(d => ({ docId: d.docId, ...(d.data || d) }));
const q = s => "'" + String(s).replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/\r?\n/g, ' ') + "'";
const slug = s => String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 40) || 'article';
const exists = id => new RegExp("\\{id:'" + id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + "',").test(src);
const photoFile = asset => { if (!asset || !photos || !fs.existsSync(photos)) return null; const f = fs.readdirSync(photos).find(x => x.startsWith(asset)); return f ? path.join(photos, f) : null; };
const report = [], mapping = {};
// 1. nouveaux articles
const newLines = [];
for (const d of docs.filter(d => d.isNew)) {
  if (!d.name || !d.cat || !(d.price > 0)) { report.push('? ' + d.docId + ' : fiche incomplète (nom, catégorie ou prix manquant), ignorée'); continue; }
  let id = slug(d.ref || d.name), k = 2; while (exists(id) || newLines.some(l => l.id === id)) id = slug(d.ref || d.name) + '-' + k++;
  const pf = photoFile(d.photo);
  if (pf && !dry) execFileSync('python3', ['-I', path.join(__dirname, 'photo.py'), pf, id]);
  const parts = ["id:" + q(id), "cat:" + q(d.cat), "name:" + q(d.name.trim()), "price:" + Math.round(d.price)];
  if (d.badge) parts.push("badge:" + q(d.badge));
  if (d.ref) parts.push("ref:" + q(d.ref.trim()));
  parts.push("desc:" + q((d.desc || '').trim()));
  if (d.age) parts.push("age:" + q(d.age.trim()));
  const plus = (d.plus || []).filter(x => x && x.trim()); parts.push("plus:[" + plus.map(q).join(', ') + "]");
  const specs = (d.specs || []).filter(x => Array.isArray(x) && x[0] && x[1]); if (specs.length) parts.push("specs:[" + specs.map(x => '[' + q(x[0]) + ', ' + q(x[1]) + ']').join(', ') + "]");
  if (pf) parts.push("image:" + q('images/' + id + '.webp'));
  if (d.hidden) parts.push('hidden:true');
  const line = '  {' + parts.join(', ') + '}';
  Function('"use strict"; return (' + line.trim() + ')')();
  newLines.push({ id, line }); mapping[d.docId] = id;
  report.push('+ ' + id + ' : « ' + d.name + ' » ' + Math.round(d.price) + ' F' + (pf ? ', avec photo' : ', sans photo' + (d.photo ? ' (photo non trouvée dans ' + photos + ')' : '')));
}
if (newLines.length) {
  const end = src.indexOf('\n];\n', src.indexOf('var PRODUCTS = ['));
  if (end < 0) throw new Error('fin de PRODUCTS introuvable');
  const lastLineStart = src.lastIndexOf('\n', end - 1) + 1; let last = src.slice(lastLineStart, end);
  const fixed = /,\s*$/.test(last) ? last : last + ',';
  src = src.slice(0, lastLineStart) + fixed + '\n' + newLines.map(l => l.line).join(',\n') + src.slice(end);
}
// 2. photos changées sur des articles existants
for (const d of docs.filter(d => !d.isNew && d.photo)) {
  const pf = photoFile(d.photo); if (!pf) { report.push('? ' + d.docId + ' : photo à télécharger (' + d.photo + ')'); continue; }
  if (!dry) execFileSync('python3', ['-I', path.join(__dirname, 'photo.py'), pf, d.docId]);
  const re = new RegExp("(\\{id:'" + d.docId.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + "',[^\\n]*?)(, image:'[^']*')?(\\})(,?)$", 'm');
  src = src.replace(re, (m, a, img, b, c) => a + ", image:'images/" + d.docId + ".webp'" + b + c);
  report.push('📷 ' + d.docId + ' : nouvelle photo');
}
if (!dry) fs.writeFileSync(file, src);
console.log(report.join('\n') || 'Aucun nouvel article ni photo.');
console.log('Correspondance (documents à supprimer de la base après publication) : ' + JSON.stringify(mapping));
