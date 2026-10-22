/* Reporte dans petit-baobab.html les modifications faites sur la page Catalogue (base de données de l'artefact).
   Usage : node admin/apply-changes.js <dossier contenant articles/<id>.json>   [--dry]
   Chaque document : { price?, name?, badge?, hidden?, updated } ; seul ce qui diffère du fichier est écrit. */
const fs = require('fs');
const path = require('path');
const dir = process.argv[2];
const dry = process.argv.includes('--dry');
if (!dir) { console.error('dossier manquant'); process.exit(1); }
const file = path.join(__dirname, '..', 'petit-baobab.html');
let src = fs.readFileSync(file, 'utf8');
const docsDir = path.join(dir, 'articles');
const docs = fs.existsSync(docsDir) ? fs.readdirSync(docsDir).filter(f => f.endsWith('.json')).map(f => ({ id: f.replace(/\.json$/, ''), ...JSON.parse(fs.readFileSync(path.join(docsDir, f), 'utf8')) })) : [];
const q = s => "'" + String(s).replace(/\\/g, '\\\\').replace(/'/g, "\\'") + "'";
const unq = s => s.replace(/\\'/g, "'").replace(/\\\\/g, '\\');
const report = [];
for (const d of docs) {
  const data = d.data || d;   // export brut ({id, data, version}) ou document seul
  const re = new RegExp("^(\\s*\\{id:'" + d.id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + "',[^\\n]*\\}),?$", 'm');
  const m = src.match(re);
  if (!m) { report.push('? ' + d.id + ' : introuvable dans le fichier'); continue; }
  let line = m[1], orig = line, changes = [];
  if (typeof data.price === 'number' && data.price >= 0) {
    const cur = parseInt((line.match(/price:(\d+)/) || [])[1], 10);
    if (cur !== data.price) { line = line.replace(/price:\d+/, 'price:' + Math.round(data.price)); changes.push('prix ' + cur + ' → ' + data.price); }
  }
  if (typeof data.name === 'string' && data.name.trim()) {
    const cur = unq((line.match(/name:'((?:\\'|[^'])*)'/) || [])[1] || '');
    if (cur !== data.name.trim()) { line = line.replace(/name:'(?:\\'|[^'])*'/, 'name:' + q(data.name.trim())); changes.push('nom « ' + cur + ' » → « ' + data.name.trim() + ' »'); }
  }
  if (typeof data.badge === 'string') {
    const cur = unq((line.match(/badge:'((?:\\'|[^'])*)'/) || [])[1] || '');
    if (cur !== data.badge) {
      line = line.replace(/,\s*badge:'(?:\\'|[^'])*'/, '');
      if (data.badge) line = line.replace(/(price:\d+)/, '$1, badge:' + q(data.badge));
      changes.push('badge « ' + cur + ' » → « ' + data.badge + ' »');
    }
  }
  if (typeof data.hidden === 'boolean') {
    const cur = /hidden:true/.test(line);
    if (cur !== data.hidden) {
      line = line.replace(/,\s*hidden:true/, '');
      if (data.hidden) line = line.replace(/\}$/, ', hidden:true}');
      changes.push(data.hidden ? 'masqué' : 'de nouveau visible');
    }
  }
  if (changes.length) { src = src.replace(orig, line); report.push('✔ ' + d.id + ' : ' + changes.join(' ; ')); }
}
if (!dry) fs.writeFileSync(file, src);
console.log(report.length ? report.join('\n') : 'Aucune modification à reporter.');
console.log((dry ? '(simulation) ' : '') + report.filter(r => r[0] === '✔').length + ' article(s) modifié(s), ' + report.filter(r => r[0] === '?').length + ' introuvable(s).');
