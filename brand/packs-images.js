/* Images des packs et valises (1000 × 1000, WebP) : vraies photos des articles du pack, posées comme un trousseau étalé,
   aux couleurs de la marque, avec le nom du pack. La valise maman, dont les articles ne sont pas au catalogue, est illustrée.
   Les prix ne sont pas écrits sur l'image (ils changent) : seulement le nom, la phrase d'accroche et le nombre d'articles.
   Usage : node brand/packs-images.js <dossier des polices @fontsource>   → images/pack-*.webp, images/valise-*.webp
   Les tuiles sont recadrées au centre (zoom 165 %, centré un peu en haut à gauche) : le filigrane des photos d'articles sort du cadre. */
const fs = require('fs'), path = require('path'), vm = require('vm');
const { chromium } = require('playwright');
const ROOT = path.join(__dirname, '..');
const FONTS = process.argv[2];
if (!FONTS) { console.error('dossier des polices manquant (node_modules/@fontsource)'); process.exit(1); }
const src = fs.readFileSync(path.join(ROOT, 'petit-baobab.html'), 'utf8');
const PRODUCTS = vm.runInNewContext('(' + src.match(/var PRODUCTS = ([\s\S]*?);\n\s*(?=var |\/\*)/)[1] + ')');
const byId = Object.fromEntries(PRODUCTS.map(p => [p.id, p]));
const MARK = JSON.parse(fs.readFileSync(path.join(__dirname, 'mark.json'), 'utf8')).mark;
const font = (fam, dir, w) => `@font-face{font-family:"${fam}";font-weight:${w};src:url("file://${path.join(FONTS, dir, 'files', `${dir}-latin-${w}-normal.woff2`)}")}`;
const FACES = [font('Fraunces', 'fraunces', 600), font('Fredoka', 'fredoka', 600), font('Nunito Sans', 'nunito-sans', 600), font('Nunito Sans', 'nunito-sans', 700)].join('');

const THEMES = {
  'pack-essentiel':  { bg: '#E1EFE5', ink: '#174F38', sub: '#3E5A4A', ribbon: '#F2A93B', title: 'Pack Essentiel', kicker: 'Pack naissance' },
  'pack-confort':    { bg: '#FBEBC8', ink: '#174F38', sub: '#5A4A2A', ribbon: '#1F6B4A', title: 'Pack Confort', kicker: 'Pack naissance', extra: '+ tout le pack Essentiel' },
  'pack-prestige':   { bg: '#174F38', ink: '#FFF3DC', sub: '#BFE0CC', ribbon: '#F2C14E', title: 'Pack Prestige', kicker: 'Pack naissance', extra: '+ tout le pack Confort', dark: true },
  'valise-bebe':     { bg: '#FFF3DC', ink: '#174F38', sub: '#5A4A2A', ribbon: '#2E8A5E', title: 'Valise bébé', kicker: 'Valise de maternité' },
  'valise-maman':    { bg: '#F7E7DC', ink: '#174F38', sub: '#5E4636', ribbon: '#F2A93B', title: 'Valise maman', kicker: 'Valise de maternité' },
  'valise-complete': { bg: '#E1EFE5', ink: '#174F38', sub: '#3E5A4A', ribbon: '#F2A93B', title: 'Valise complète', kicker: 'Valise de maternité', extra: 'maman + bébé' }
};

/* la valise illustrée (pour la valise maman, et en tuile dans la valise complète) */
const SUITCASE = `<svg viewBox="0 0 220 200" class="case"><rect x="78" y="14" width="64" height="30" rx="12" fill="none" stroke="#174F38" stroke-width="9"/>
<rect x="18" y="38" width="184" height="148" rx="24" fill="#2E8A5E"/><rect x="18" y="38" width="184" height="30" rx="14" fill="#1F6B4A"/>
<rect x="56" y="38" width="16" height="148" fill="#F2A93B"/><rect x="148" y="38" width="16" height="148" fill="#F2A93B"/>
<circle cx="110" cy="122" r="34" fill="#FFF3DC"/><g transform="translate(83 95) scale(.45)">${MARK.replace(/class="lg-sun"/g, 'fill="#F2A93B"').replace(/class="lg-fruit"/g, 'fill="#F2A93B"').replace(/class="lg-ground"/g, 'fill="#BFE3CB"').replace(/class="lg-trunk"/g, 'fill="#1F6B4A"').replace(/class="lg-tree"/g, 'fill="#1F6B4A"')}</g></svg>`;

function photos(p) {
  const ids = (p.items || []).map(i => i.id).filter(id => byId[id] && byId[id].image && !byId[id].items);
  return [...new Set(ids)].slice(0, 6).map(id => byId[id]);
}
function count(p) {
  if (p.contents) return p.contents.length;
  return (p.items || []).reduce((n, i) => n + (i.qty || 1), 0);
}

function page(p) {
  const t = THEMES[p.id];
  let tiles = [];
  if (p.id === 'valise-maman') tiles = null;
  else if (p.id === 'valise-complete') tiles = photos(byId['valise-bebe']).slice(0, 5).map(x => ({ img: x.image })).concat([{ svg: SUITCASE, label: 'maman' }]);
  else tiles = photos(p).map(x => ({ img: x.image }));
  const rot = [-4, 3, -2, 4, -3, 2];
  const mark = MARK.replace(/class="lg-sun"/g, `fill="${t.ribbon === '#F2C14E' ? '#F2C14E' : '#F2A93B'}"`).replace(/class="lg-fruit"/g, 'fill="#F2A93B"')
    .replace(/class="lg-ground"/g, `fill="${t.dark ? '#2E6B50' : '#BFE3CB'}"`).replace(/class="lg-trunk"/g, `fill="${t.dark ? '#FFF3DC' : '#1F6B4A'}"`).replace(/class="lg-tree"/g, `fill="${t.dark ? '#FFF3DC' : '#1F6B4A'}"`);
  const items = p.id === 'valise-maman' ? (p.contents || []).slice(0, 6) : [];
  const body = tiles ? `<div class="grid${tiles.length < 4 ? ' few' : ''}">${tiles.map((x, i) => `<div class="tile" style="--r:${rot[i % 6]}deg">${x.img ? `<div class="ph" style="background-image:url('file://${path.join(ROOT, x.img)}')"></div>` : `<div class="svgt">${x.svg}<span>${x.label}</span></div>`}</div>`).join('')}</div>`
    : `<div class="maman">${SUITCASE}<ul>${items.map(x => `<li>${x.replace(/^\d+\s*(paquet|lot|paire)?\s*(de|d')?\s*/i, '')}</li>`).join('')}</ul></div>`;
  return `<!doctype html><html><head><meta charset="utf-8"><style>${FACES}
*{box-sizing:border-box;margin:0}
body{width:1000px;height:1000px;background:${t.bg};font-family:"Nunito Sans",sans-serif;color:${t.ink};position:relative;overflow:hidden}
.blob{position:absolute;border-radius:50%;background:${t.dark ? 'rgba(255,243,220,.06)' : 'rgba(255,255,255,.55)'}}
.b1{width:620px;height:620px;right:-220px;top:-200px}.b2{width:420px;height:420px;left:-170px;bottom:-140px}
.brand{position:absolute;left:56px;top:46px;display:flex;align-items:center;gap:14px;font-family:Fredoka;font-weight:600;font-size:32px;color:${t.dark ? '#FFF3DC' : '#1F6B4A'}}
.brand svg{width:62px;height:62px}
.count{position:absolute;right:56px;top:52px;background:${t.ribbon};color:${t.dark || t.ribbon === '#1F6B4A' || t.ribbon === '#2E8A5E' ? (t.dark ? '#174F38' : '#FFF') : '#1E2B22'};font-weight:700;font-size:26px;padding:12px 22px;border-radius:999px}
.grid{position:absolute;left:70px;right:70px;top:150px;height:590px;display:grid;grid-template-columns:repeat(3,1fr);grid-auto-rows:1fr;gap:30px}
.grid.few{grid-template-columns:repeat(2,1fr);left:180px;right:180px}
.tile{background:#fff;border-radius:28px;box-shadow:0 18px 40px rgba(20,40,28,${t.dark ? '.45' : '.16'});transform:rotate(var(--r));padding:12px;overflow:hidden}
.ph{width:100%;height:100%;border-radius:18px;background-size:165%;background-position:42% 26%;background-repeat:no-repeat}
.svgt{height:100%;display:grid;place-items:center;background:#FFF3DC;border-radius:18px;position:relative}
.svgt svg{width:78%}
.svgt span{position:absolute;bottom:12px;font-family:Fredoka;font-weight:600;font-size:26px;color:#1F6B4A}
.maman{position:absolute;left:70px;right:70px;top:160px;height:570px;display:grid;grid-template-columns:1fr 1fr;align-items:center;gap:30px}
.maman svg{width:100%}
.maman ul{list-style:none;padding:0;display:grid;gap:14px}
.maman li{background:#fff;border-radius:999px;padding:14px 22px;font-weight:700;font-size:25px;box-shadow:0 8px 20px rgba(20,40,28,.1)}
.maman li::first-letter{text-transform:uppercase}
.foot{position:absolute;left:70px;right:70px;bottom:56px}
.kicker{font-weight:700;letter-spacing:.14em;text-transform:uppercase;font-size:22px;color:${t.dark ? '#F2C14E' : '#B66A10'}}
h1{font-family:Fraunces;font-weight:600;font-size:76px;line-height:1;margin-top:6px}
.sub{font-size:30px;color:${t.sub};margin-top:10px;font-weight:600}
.extra{display:inline-block;margin-left:14px;font-size:24px;font-weight:700;color:${t.dark ? '#174F38' : '#fff'};background:${t.dark ? '#F2C14E' : '#1F6B4A'};padding:6px 16px;border-radius:999px;vertical-align:middle}
</style></head><body><div class="blob b1"></div><div class="blob b2"></div>
<div class="brand"><svg viewBox="0 0 120 120">${mark}</svg>Petit Baobab</div><div class="count">${count(p)} ${p.id === 'valise-complete' ? 'valises' : 'articles'}</div>
${body}
<div class="foot"><div class="kicker">${t.kicker}</div><h1>${t.title}${t.extra ? `<span class="extra">${t.extra}</span>` : ''}</h1><div class="sub">${p.tagline || ''}</div></div>
</body></html>`;
}

(async () => {
  const b = await chromium.launch({ executablePath: process.env.PW_CHROMIUM || '/opt/pw-browsers/chromium' });
  const pg = await b.newPage({ viewport: { width: 1000, height: 1000 } });
  for (const id of Object.keys(THEMES)) {
    const p = byId[id]; if (!p) { console.log('absent :', id); continue; }
    const tmp = path.join(process.env.PACKS_TMP || require('os').tmpdir(), 'pack-' + id + '.html');
    fs.writeFileSync(tmp, page(p));
    await pg.goto('file://' + tmp); await pg.evaluate(() => document.fonts.ready); await pg.waitForTimeout(150);
    const png = await pg.screenshot({ type: 'png' });
    const out = path.join(ROOT, 'images', id + '.webp');
    await pg.setContent(`<canvas id=c width=1000 height=1000></canvas>`);
    const webp = await pg.evaluate(async b64 => { const im = new Image(); im.src = 'data:image/png;base64,' + b64; await im.decode(); const c = document.getElementById('c'); c.getContext('2d').drawImage(im, 0, 0); return c.toDataURL('image/webp', .86).split(',')[1]; }, png.toString('base64'));
    fs.writeFileSync(out, Buffer.from(webp, 'base64'));
    console.log(path.relative(ROOT, out), Math.round(fs.statSync(out).size / 1024) + ' Ko');
  }
  await b.close();
})();
