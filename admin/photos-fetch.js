/* Récupère et prépare les photos HD des articles pendant la construction Netlify (après build.js).
   Source : photos/sources.json  →  { "<id>": { "urls": ["https://…jpg", …], "statut": "trouve|couleur|doute", "note": "…", "fiche": "…" }, … }
   Pour chaque article : 1re photo → site/images/<id>.webp (remplace l'ancienne), suivantes → site/images/<id>-2.webp, -3, -4 (galerie).
   Traitement (comme admin/photo.py) : marges blanches rognées, carré 1000 × 1000 sur fond blanc, filigrane Petit Baobab, WebP.
   Cache : .photos-cache/ (gardé d'une construction à l'autre par netlify/plugins/photos-cache) ; si une photo n'est plus
   disponible chez le fournisseur, on garde la version déjà préparée, sinon l'ancienne photo reste en place.
   Sur les aperçus seulement : page /verification-photos/ (avant / après) pour que Hanis valide.
   Usage local : node admin/photos-fetch.js   (sans sharp ou sans réseau, il ne fait rien et le dit). */
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ROOT = path.join(__dirname, '..');
const OUT = path.join(ROOT, 'site');
const SRC = path.join(ROOT, 'photos', 'sources.json');
const CACHE = path.join(ROOT, '.photos-cache');
const WM = path.join(__dirname, 'wm', 'watermark.png');
const PREVIEW = process.env.CONTEXT === 'deploy-preview' || process.env.PHOTOS_VERIF === '1';

let sharp;
try { sharp = require('sharp'); } catch (e) { console.log('photos-fetch : sharp absent, rien à faire ici (c\'est Netlify qui prépare les photos).'); process.exit(0); }
if (!fs.existsSync(SRC)) { console.log('photos-fetch : pas de photos/sources.json'); process.exit(0); }
const SOURCES = JSON.parse(fs.readFileSync(SRC, 'utf8'));
fs.mkdirSync(CACHE, { recursive: true });

const sleep = ms => new Promise(r => setTimeout(r, ms));
async function download(url) {
  if (!/^https?:/.test(url)) return fs.readFileSync(path.resolve(ROOT, url));          // chemin local (tests)
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const ctl = new AbortController(); const t = setTimeout(() => ctl.abort(), 25000);
      const r = await fetch(url, { signal: ctl.signal, headers: { 'User-Agent': 'Mozilla/5.0 (Macintosh) PetitBaobab-build', 'Accept': 'image/avif,image/webp,image/png,image/jpeg,*/*' } });
      clearTimeout(t);
      if (!r.ok) throw new Error('HTTP ' + r.status);
      const buf = Buffer.from(await r.arrayBuffer());
      if (buf.length < 2000) throw new Error('fichier trop petit');
      return buf;
    } catch (e) { if (attempt === 2) throw e; await sleep(1500 * (attempt + 1)); }
  }
}

let WMBUF = null;
async function watermark(size) {
  if (!WMBUF) WMBUF = fs.readFileSync(WM);
  const tw = Math.round(size * 0.34);
  // filigrane à 66 % d'opacité
  const { data, info } = await sharp(WMBUF).resize({ width: tw }).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
  for (let i = 3; i < data.length; i += 4) data[i] = Math.round(data[i] * 0.66);
  return { buf: await sharp(data, { raw: info }).png().toBuffer(), w: info.width, h: info.height };
}

async function prepare(buf) {
  const SIDE = 1000;
  let img = sharp(buf, { failOn: 'none' }).rotate().flatten({ background: '#ffffff' });
  const meta = await img.metadata();
  // fond blanc ? (les 4 coins presque blancs) → on rogne les marges et on laisse une marge régulière de 5 %
  const { data, info } = await img.clone().resize(64, 64, { fit: 'fill' }).raw().toBuffer({ resolveWithObject: true });
  const px = (x, y) => { const i = (y * info.width + x) * info.channels; return Math.min(data[i], data[i + 1], data[i + 2]); };
  const white = [px(0, 0), px(63, 0), px(0, 63), px(63, 63)].every(v => v >= 235);
  let base = await img.toBuffer();
  if (white) { try { base = await sharp(base).trim({ background: '#ffffff', threshold: 18 }).toBuffer(); } catch (e) {} }
  const inner = white ? Math.round(SIDE * 0.9) : SIDE;
  const fitted = await sharp(base).resize(inner, inner, { fit: 'inside', withoutEnlargement: false, kernel: 'lanczos3' }).toBuffer({ resolveWithObject: true });
  const wm = await watermark(SIDE), pad = Math.round(SIDE * 0.025);
  return sharp({ create: { width: SIDE, height: SIDE, channels: 3, background: '#ffffff' } })
    .composite([
      { input: fitted.data, left: Math.round((SIDE - fitted.info.width) / 2), top: Math.round((SIDE - fitted.info.height) / 2) },
      { input: wm.buf, left: SIDE - wm.w - pad, top: SIDE - wm.h - pad },
    ])
    .webp({ quality: 84, effort: 5 }).toBuffer();
}

(async () => {
  // En ligne (production) : seulement les photos sûres (« même article » ou « autre couleur ») ;
  // les « à vérifier » attendent la validation de Hanis sur l'aperçu. Partout : on saute les fiches masquées
  // dont la photo ne sert nulle part (doublons effacés) ; les couleurs regroupées gardent leur photo.
  const HTML = fs.readFileSync(path.join(ROOT, 'petit-baobab.html'), 'utf8');
  const hidden = new Set([...HTML.matchAll(/^  \{id:'([^']+)',[^\n]*hidden:true/gm)].map(m => m[1]));
  const used = id => HTML.split('images/' + id + '.webp').length - 1 > 1;
  const PROD = process.env.CONTEXT === 'production';
  const ids = Object.keys(SOURCES).filter(id => !(hidden.has(id) && !used(id)) && !(PROD && SOURCES[id].statut === 'doute'));
  const result = {};
  let ok = 0, ko = 0;
  fs.mkdirSync(path.join(OUT, 'images', '_avant'), { recursive: true });
  // téléchargements en parallèle limité (6 à la fois)
  const jobs = [];
  for (const id of ids) (SOURCES[id].urls || []).slice(0, 4).forEach((url, k) => jobs.push({ id, url, k }));
  let next = 0, reportees = 0;
  // Limite de temps (Netlify coupe une construction à 18 min, avec la lecture des photos ensuite) :
  // au-delà, les photos pas encore en cache restent celles du dépôt et seront préparées à la construction suivante.
  const DEADLINE = Date.now() + (+process.env.PHOTOS_MAX_S || (process.env.CONTEXT === 'production' ? 840 : 480)) * 1000;   // en ligne, pas de lecture des photos ensuite
  async function worker() {
    while (next < jobs.length) {
      const j = jobs[next++];
      const name = j.k === 0 ? j.id + '.webp' : j.id + '-' + (j.k + 1) + '.webp';
      const key = crypto.createHash('sha1').update(j.url + '|v1').digest('hex') + '.webp';
      const cached = path.join(CACHE, key);
      try {
        let out;
        if (fs.existsSync(cached)) out = fs.readFileSync(cached);
        else if (Date.now() > DEADLINE) { reportees++; continue; }
        else { out = await prepare(await download(j.url)); fs.writeFileSync(cached, out); }
        const dest = path.join(OUT, 'images', name);
        if (j.k === 0 && fs.existsSync(dest) && !fs.existsSync(path.join(OUT, 'images', '_avant', name))) fs.copyFileSync(dest, path.join(OUT, 'images', '_avant', name));
        fs.writeFileSync(dest, out);
        (result[j.id] = result[j.id] || []).push(name); ok++;
      } catch (e) {
        ko++; console.log('photos-fetch : échec ' + j.id + ' #' + (j.k + 1) + ' (' + e.message + ') ' + j.url);
        (result[j.id + ':echecs'] = result[j.id + ':echecs'] || []).push(j.k + 1);
      }
    }
  }
  await Promise.all(Array.from({ length: 6 }, worker));
  const rank = f => { const m = f.match(/-(\d)\.webp$/); return m && !/^\d+$/.test(f.replace(/\.webp$/, '')) ? +m[1] : 1; };
  for (const id of Object.keys(result)) if (!id.includes(':')) result[id].sort((a, b) => (a === id + '.webp' ? 0 : rank(a)) - (b === id + '.webp' ? 0 : rank(b)));
  fs.writeFileSync(path.join(OUT, 'images', 'galerie.json'), JSON.stringify(result));
  console.log('photos-fetch : ' + ok + ' photos prêtes, ' + ko + ' échecs, ' + ids.length + ' articles' + (reportees ? ', ' + reportees + ' reportées à la prochaine construction (limite de temps)' : ''));

  if (!PREVIEW) return;
  /* ---- Page de vérification (aperçus seulement, jamais en ligne) ---- */
  const html = fs.readFileSync(path.join(ROOT, 'petit-baobab.html'), 'utf8');
  const nameOf = id => { const m = html.match(new RegExp("\\{id:'" + id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + "', cat:'[^']*', name:'((?:[^'\\\\]|\\\\.)*)', price:(\\d+)(?:, ref:'((?:[^'\\\\]|\\\\.)*)')?")); return m ? { name: m[1].replace(/\\'/g, "'"), price: +m[2], ref: m[3] || '' } : { name: id, ref: '' }; };
  const esc = s => String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
  const LBL = { trouve: ['Même article', '#1F6B4A'], couleur: ['Autre couleur', '#C9711C'], doute: ['À vérifier', '#B4423B'] };
  let n = 0;
  const rows = ids.filter(id => result[id]).map(id => {
    n++; const p = nameOf(id), s = SOURCES[id], l = LBL[s.statut] || LBL.doute, files = result[id];
    const avant = fs.existsSync(path.join(OUT, 'images', '_avant', id + '.webp')) ? '/images/_avant/' + id + '.webp' : '';
    return `<article class="row" data-n="${n}"><div class="head"><label><input type="checkbox" checked data-n="${n}" data-id="${esc(id)}"> <b>${n}.</b> ${esc(p.name)}${p.ref ? ' <span class="ref">réf. ' + esc(p.ref) + '</span>' : ''}</label><span class="tag" style="background:${l[1]}">${l[0]}</span></div>
<div class="imgs"><figure class="avant">${avant ? `<img src="${avant}" alt="" loading="lazy">` : ''}<figcaption>Avant</figcaption></figure>${files.map((f, k) => `<figure><img src="/images/${f}" alt="" loading="lazy"><figcaption>${k ? 'Photo ' + (k + 1) : 'Après'}</figcaption></figure>`).join('')}</div>${s.note ? `<p class="note">${esc(s.note)}</p>` : ''}</article>`;
  }).join('\n');
  fs.mkdirSync(path.join(OUT, 'verification-photos'), { recursive: true });
  fs.writeFileSync(path.join(OUT, 'verification-photos', 'index.html'), `<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Vérification des photos · Petit Baobab</title>
<style>body{margin:0;font:15px/1.45 system-ui,-apple-system,sans-serif;background:#F5F7F2;color:#1E2B22}header{position:sticky;top:0;z-index:2;background:#1F6B4A;color:#fff;padding:12px 16px}header h1{margin:0;font-size:18px}header p{margin:4px 0 0;font-size:13px;opacity:.9}
main{max-width:1100px;margin:0 auto;padding:12px 16px 120px}.row{background:#fff;border:1px solid #D9E1D8;border-radius:14px;padding:12px;margin:12px 0}.row.off{opacity:.45}.head{display:flex;justify-content:space-between;gap:8px;align-items:center;flex-wrap:wrap}.head label{cursor:pointer}.head input{transform:scale(1.4);margin-right:6px}
.ref{color:#55615A;font-size:13px}.tag{color:#fff;border-radius:999px;padding:2px 10px;font-size:12px;font-weight:700}.imgs{display:flex;gap:8px;overflow-x:auto;margin-top:10px}figure{margin:0;flex:0 0 auto;width:min(42vw,220px)}figure img{width:100%;aspect-ratio:1;object-fit:contain;background:#fff;border:1px solid #ECF1EA;border-radius:10px;display:block}
figcaption{font-size:12px;color:#55615A;text-align:center;margin-top:3px}.avant img{border:2px dashed #B4423B}.note{margin:8px 0 0;font-size:13px;color:#55615A;font-style:italic}
footer{position:fixed;left:0;right:0;bottom:0;background:#fff;border-top:1px solid #D9E1D8;padding:10px 16px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}footer output{flex:1;min-width:200px;font-size:13px}footer button{background:#1F6B4A;color:#fff;border:0;border-radius:999px;padding:10px 16px;font-weight:700;font-size:14px}</style></head>
<body><header><h1>Vérification des nouvelles photos (${n} articles)</h1><p>Décochez les articles dont la nouvelle photo ne convient pas, puis envoyez-moi la liste des numéros refusés.</p></header>
<main>${rows}</main>
<footer><output id="res"></output><button type="button" id="copy">Copier les numéros refusés</button></footer>
<script>(function(){var K='pb-verif',st={};try{st=JSON.parse(localStorage.getItem(K)||'{}')}catch(e){}
var boxes=[].slice.call(document.querySelectorAll('input[type=checkbox]'));
function up(){var off=[];boxes.forEach(function(b){var r=b.closest('.row');r.classList.toggle('off',!b.checked);if(!b.checked)off.push(b.dataset.n)});document.getElementById('res').textContent=off.length?('Refusés : '+off.join(', ')):'Tout est validé';try{localStorage.setItem(K,JSON.stringify(st))}catch(e){}return off}
boxes.forEach(function(b){if(st[b.dataset.id]===false)b.checked=false;b.addEventListener('change',function(){st[b.dataset.id]=b.checked;up()})});
document.getElementById('copy').addEventListener('click',function(){var off=up(),t=off.length?('Photos refusées : '+off.join(', ')):'Toutes les photos sont validées';try{navigator.clipboard.writeText(t);this.textContent='Copié !'}catch(e){prompt('Copiez ce texte :',t)}});up()})();</script></body></html>`);
  console.log('photos-fetch : page /verification-photos/ créée (' + n + ' articles)');
})().catch(e => { console.error('photos-fetch : erreur', e); process.exit(0); });   // ne jamais casser la mise en ligne
