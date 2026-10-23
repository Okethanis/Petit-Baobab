/* Reporte dans petit-baobab.html les modifications faites sur la page Catalogue (base de données de l'artefact).
   Usage : node admin/apply-changes.js <dossier contenant articles/<id>.json>   [--dry]
   Chaque document : { price?, name?, badge?, hidden?, ref?, desc?, age?, plus?, specs?, updated } ; seul ce qui diffère du fichier est écrit.
   Les articles sont des objets JS sur une seule ligne : on remplace chaque champ en place, ou on l'insère à sa position habituelle. */
const fs = require('fs');
const path = require('path');
const dir = process.argv[2];
const dry = process.argv.includes('--dry');
if (!dir) { console.error('dossier manquant'); process.exit(1); }
const file = path.join(__dirname, '..', 'petit-baobab.html');
let src = fs.readFileSync(file, 'utf8');
const docsDir = path.join(dir, 'articles');
const docs = fs.existsSync(docsDir) ? fs.readdirSync(docsDir).filter(f => f.endsWith('.json')).map(f => ({ id: f.replace(/\.json$/, ''), ...JSON.parse(fs.readFileSync(path.join(docsDir, f), 'utf8')) })) : [];

const q = s => "'" + String(s).replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/\r?\n/g, ' ') + "'";
const ORDER = ['id', 'cat', 'name', 'price', 'badge', 'ref', 'desc', 'age', 'plus', 'specs', 'image'];   // ordre des champs dans une ligne d'article

/* Position du champ `key` dans la ligne : [début de "key:", fin de la valeur] ; null s'il n'existe pas. */
function findField(line, key) {
  const re = new RegExp('(?:\\{|, )' + key + ':');
  const m = re.exec(line); if (!m) return null;
  const start = m.index + (m[0][0] === '{' ? 1 : 2), vs = m.index + m[0].length;
  let i = vs;
  if (line[i] === "'") { i++; while (i < line.length) { if (line[i] === '\\') { i += 2; continue; } if (line[i] === "'") { i++; break; } i++; } }
  else if (line[i] === '[' || line[i] === '{') { let depth = 0, inStr = false; while (i < line.length) { const c = line[i]; if (inStr) { if (c === '\\') { i += 2; continue; } if (c === "'") inStr = false; i++; continue; } if (c === "'") inStr = true; else if (c === '[' || c === '{') depth++; else if (c === ']' || c === '}') { depth--; if (depth === 0) { i++; break; } } i++; } }
  else { while (i < line.length && line[i] !== ',' && line[i] !== '}') i++; }
  return [start, vs, i];
}
function readString(line, key) { const f = findField(line, key); if (!f) return undefined; const raw = line.slice(f[1], f[2]); if (raw[0] !== "'") return undefined; return raw.slice(1, -1).replace(/\\'/g, "'").replace(/\\\\/g, '\\'); }
function readValue(line, key) { const f = findField(line, key); if (!f) return undefined; try { return Function('"use strict"; return (' + line.slice(f[1], f[2]) + ')')(); } catch (e) { return undefined; } }
function setField(line, key, serialized) {
  const f = findField(line, key);
  if (f) return line.slice(0, f[1]) + serialized + line.slice(f[2]);
  if (serialized === null) return line;
  // insertion à la position habituelle : juste après le dernier champ qui précède `key` dans ORDER
  const idx = ORDER.indexOf(key);
  for (let k = idx - 1; k >= 0; k--) { const g = findField(line, ORDER[k]); if (g) return line.slice(0, g[2]) + ', ' + key + ':' + serialized + line.slice(g[2]); }
  return line.replace(/\}$/, ', ' + key + ':' + serialized + '}');
}
function removeField(line, key) { const f = findField(line, key); if (!f) return line; let s = f[0] - 2, e = f[2]; if (line.slice(f[0] - 2, f[0]) !== ', ') { s = f[0]; if (line.slice(e, e + 2) === ', ') e += 2; } return line.slice(0, s) + line.slice(e); }
const arr = a => '[' + a.map(x => Array.isArray(x) ? '[' + x.map(q).join(', ') + ']' : q(x)).join(', ') + ']';
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

const report = [];
for (const d of docs) {
  const data = d.data || d;   // export brut ({id, data, version}) ou document seul
  if (data.isNew) continue;   // nouveaux articles : traités par admin/import-new.js
  const re = new RegExp("^(\\s*\\{id:'" + d.id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + "',[^\\n]*\\}),?$", 'm');
  const m = src.match(re);
  if (!m) { report.push('? ' + d.id + ' : introuvable dans le fichier'); continue; }
  let line = m[1], orig = line, changes = [];
  if (typeof data.price === 'number' && data.price >= 0) {
    const cur = readValue(line, 'price');
    if (cur !== Math.round(data.price)) { line = setField(line, 'price', String(Math.round(data.price))); changes.push('prix ' + cur + ' → ' + Math.round(data.price)); }
  }
  for (const [key, label] of [['name', 'nom'], ['ref', 'référence'], ['desc', 'description'], ['age', 'âge conseillé']]) {
    if (typeof data[key] !== 'string') continue;
    const val = data[key].trim(); if (key === 'name' && !val) continue;
    const cur = readString(line, key) || '';
    if (cur !== val) {
      line = val ? setField(line, key, q(val)) : removeField(line, key);
      changes.push(label + (val.length > 60 || cur.length > 60 ? ' modifié' + (key === 'desc' ? 'e' : '') : ' « ' + cur + ' » → « ' + val + ' »'));
    }
  }
  if (typeof data.badge === 'string') {
    const cur = readString(line, 'badge') || '';
    if (cur !== data.badge) { line = data.badge ? setField(line, 'badge', q(data.badge)) : removeField(line, 'badge'); changes.push('badge « ' + cur + ' » → « ' + data.badge + ' »'); }
  }
  if (Array.isArray(data.plus)) {
    const val = data.plus.filter(x => typeof x === 'string' && x.trim()).map(x => x.trim()); const cur = readValue(line, 'plus') || [];
    if (!same(cur, val)) { line = val.length ? setField(line, 'plus', arr(val)) : removeField(line, 'plus'); changes.push('points forts (' + cur.length + ' → ' + val.length + ')'); }
  }
  if (Array.isArray(data.specs)) {
    const val = data.specs.filter(x => Array.isArray(x) && x.length === 2 && String(x[0]).trim()).map(x => [String(x[0]).trim(), String(x[1]).trim()]); const cur = readValue(line, 'specs') || [];
    if (!same(cur, val)) { line = val.length ? setField(line, 'specs', arr(val)) : removeField(line, 'specs'); changes.push('caractéristiques (' + cur.length + ' → ' + val.length + ')'); }
  }
  if (typeof data.hidden === 'boolean') {
    const cur = /hidden:true/.test(line);
    if (cur !== data.hidden) { line = removeField(line, 'hidden'); if (data.hidden) line = line.replace(/\}$/, ', hidden:true}'); changes.push(data.hidden ? 'masqué' : 'de nouveau visible'); }
  }
  if (changes.length) {
    try { Function('"use strict"; return (' + line.trim() + ')')(); } catch (e) { report.push('! ' + d.id + ' : ligne invalide après modification, ignorée (' + e.message + ')'); continue; }
    src = src.replace(orig, line); report.push('✔ ' + d.id + ' : ' + changes.join(' ; '));
  }
}
if (!dry) fs.writeFileSync(file, src);
console.log(report.length ? report.join('\n') : 'Aucune modification à reporter.');
console.log((dry ? '(simulation) ' : '') + report.filter(r => r[0] === '✔').length + ' article(s) modifié(s), ' + report.filter(r => r[0] === '?').length + ' introuvable(s), ' + report.filter(r => r[0] === '!').length + ' en erreur.');
