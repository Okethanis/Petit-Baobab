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

/* Mise en scène « coffret » : les articles sortent d'une boîte cadeau (packs) ou d'une valise ouverte (valises).
   Les photos sont des médaillons ronds en éventail ; la boîte porte le nom, la phrase d'accroche et le nombre d'articles. */
const SCENES = {
  'pack-essentiel':  { bg: '#E7F2EA', panel: '#2E8A5E', inner: '#1F6B4A', lid: '#3E9A6E', ribbon: '#F2A93B', ink: '#FFFFFF', sub: '#DDF1E5', kind: 'box' },
  'pack-confort':    { bg: '#FFF4DE', panel: '#F2A93B', inner: '#D98E22', lid: '#F6BC5E', ribbon: '#1F6B4A', ink: '#1E2B22', sub: '#4A3A1C', kind: 'box' },
  'pack-prestige':   { bg: '#DCEBE1', panel: '#174F38', inner: '#0F3826', lid: '#22654A', ribbon: '#E9B949', ink: '#FFF3DC', sub: '#CFE6D8', kind: 'box' },
  'valise-bebe':     { bg: '#FFF4DE', panel: '#2E8A5E', inner: '#1F6B4A', lid: '#3E9A6E', ribbon: '#F2A93B', ink: '#FFFFFF', sub: '#DDF1E5', kind: 'case' },
  'valise-maman':    { bg: '#F8EAE0', panel: '#C9734A', inner: '#A85A36', lid: '#D88A62', ribbon: '#FFF3DC', ink: '#FFFFFF', sub: '#FBE3D6', kind: 'case' },
  'valise-complete': { bg: '#E7F2EA', panel: '#1F6B4A', inner: '#174F38', lid: '#2E8A5E', ribbon: '#F2A93B', ink: '#FFFFFF', sub: '#DDF1E5', kind: 'case' }
};
function page(p) {
  const t = THEMES[p.id], c = SCENES[p.id];
  let pics;
  if (p.id === 'valise-complete') pics = photos(byId['valise-bebe']).slice(0, 4).map(x => x.image);
  else pics = photos(p).slice(0, 5).map(x => x.image);
  // éventail de médaillons : du centre vers les bords, les plus grands au milieu
  const SLOTS = [[500, 300, 270], [292, 352, 222], [708, 352, 222], [128, 452, 172], [872, 452, 172]];
  const order = pics.length >= 5 ? [3, 1, 0, 2, 4] : pics.length === 4 ? [1, 0, 2, 4] : [1, 0, 2];
  const medals = pics.map((src, i) => { const [x, y, d] = SLOTS[order[i] === undefined ? i : order[i]]; return `<div class="medal" style="left:${x - d / 2}px;top:${y - d / 2}px;width:${d}px;height:${d}px;--r:${[-6, 4, -3, 5, -4][i]}deg"><div class="ph" style="background-image:url('file://${path.join(ROOT, src)}')"></div></div>`; }).join('');
  const chips = p.id === 'valise-maman' ? (p.contents || []).slice(0, 6).map((x, i) => { const pos = [[70, 170], [520, 150], [100, 262], [540, 242], [80, 354], [520, 334]][i]; return `<span class="chip" style="left:${pos[0]}px;top:${pos[1]}px;--r:${[-4, 3, 2, -3, 4, -2][i]}deg">${x.replace(/^\d+\s*(paquet|lot|paire)?\s*(de|d')?\s*/i, '')}</span>`; }).join('') : '';
  const maman = p.id === 'valise-complete' ? `<div class="medal mam" style="left:${872 - 86}px;top:${452 - 86}px;width:172px;height:172px;--r:5deg"><div class="mm">${SUITCASE}<span>maman</span></div></div>` : '';
  const mark = (fill, trunk) => MARK.replace(/class="lg-sun"/g, 'fill="#F2A93B"').replace(/class="lg-fruit"/g, 'fill="#F2A93B"').replace(/class="lg-ground"/g, `fill="${fill}"`).replace(/class="lg-trunk"/g, `fill="${trunk}"`).replace(/class="lg-tree"/g, `fill="${trunk}"`);
  const bow = `<div class="bow"><svg viewBox="0 0 160 90"><path d="M80 45C55 10 18 6 12 24s30 34 68 21z" fill="${c.ribbon}"/><path d="M80 45c25-35 62-39 68-21S118 58 80 45z" fill="${c.ribbon}"/><path d="M80 45 62 88h14l4-12 4 12h14z" fill="${c.ribbon}" opacity=".9"/><circle cx="80" cy="45" r="13" fill="${c.ribbon}" stroke="rgba(0,0,0,.12)" stroke-width="3"/></svg></div>`;
  const deco = c.kind === 'box' ? '<div class="ribbon-v"></div>' : '<div class="strap s1"></div><div class="strap s2"></div><div class="handle"></div><div class="corner c1"></div><div class="corner c2"></div>';
  return `<!doctype html><html><head><meta charset="utf-8"><style>${FACES}
*{box-sizing:border-box;margin:0}
body{width:1000px;height:1000px;background:${c.bg};font-family:"Nunito Sans",sans-serif;position:relative;overflow:hidden}
.dots{position:absolute;inset:0;background-image:radial-gradient(rgba(31,107,74,.10) 2px,transparent 2.5px);background-size:34px 34px}
.halo{position:absolute;left:150px;top:90px;width:700px;height:560px;border-radius:50%;background:radial-gradient(closest-side,rgba(255,255,255,.95),rgba(255,255,255,0))}
.brand{position:absolute;left:0;right:0;top:40px;display:flex;justify-content:center;align-items:center;gap:12px;font-family:Fredoka;font-weight:600;font-size:30px;color:#1F6B4A}
.brand svg{width:54px;height:54px}
.inner{position:absolute;left:96px;right:96px;top:505px;height:110px;background:${c.inner};border-radius:26px 26px 0 0}
.lid{position:absolute;left:560px;top:420px;width:360px;height:110px;background:${c.lid};border-radius:22px;transform:rotate(14deg);transform-origin:left bottom;box-shadow:0 10px 24px rgba(0,0,0,.12)}
.case .lid{left:96px;width:808px;top:430px;height:90px;transform:none;border-radius:30px 30px 8px 8px}
.medal{position:absolute;border-radius:50%;background:#fff;padding:10px;box-shadow:0 18px 36px rgba(20,40,28,.22);transform:rotate(var(--r))}
.medal .ph{width:100%;height:100%;border-radius:50%;background-size:165%;background-position:42% 26%;background-repeat:no-repeat}
.mm{width:100%;height:100%;border-radius:50%;background:#FFF3DC;display:grid;place-items:center;position:relative;overflow:hidden}
.mm svg{width:62%;margin-top:-14px}.mm span{position:absolute;bottom:18px;font-family:Fredoka;font-weight:600;font-size:22px;color:#1F6B4A}
.chip{position:absolute;background:#fff;border-radius:999px;padding:13px 22px;font-weight:700;font-size:26px;color:#3A2A20;box-shadow:0 10px 24px rgba(20,40,28,.14);transform:rotate(var(--r));white-space:nowrap}
.chip::first-letter{text-transform:uppercase}
.front{position:absolute;left:80px;right:80px;top:560px;bottom:70px;background:${c.panel};border-radius:30px;box-shadow:0 26px 50px rgba(20,40,28,.25), inset 0 6px 0 rgba(255,255,255,.12);overflow:hidden;padding:92px 70px 0;color:${c.ink}}
.front::after{content:"";position:absolute;left:0;right:0;top:0;height:18px;background:rgba(0,0,0,.08)}
.ribbon-v{position:absolute;left:auto;right:150px;top:0;bottom:0;width:58px;background:${c.ribbon};opacity:.95}
.bow{position:absolute;left:${1000 - 80 - 150 - 29 - 95}px;top:508px;width:190px;z-index:3}
.strap{position:absolute;top:0;bottom:0;width:28px;background:${c.ribbon};opacity:.9}.s1{right:150px}.s2{right:96px}
.handle{position:absolute;left:50%;top:-6px;width:170px;height:26px;margin-left:-85px;border-radius:0 0 18px 18px;background:rgba(0,0,0,.18)}
.corner{position:absolute;bottom:0;width:70px;height:70px;background:rgba(0,0,0,.14)}.c1{left:0;border-radius:0 40px 0 0}.c2{right:0;border-radius:40px 0 0 0}
.tag{position:relative;z-index:2;display:inline-block}
.kicker{font-weight:700;letter-spacing:.16em;text-transform:uppercase;font-size:22px;opacity:.9}
h1{font-family:Fraunces;font-weight:600;font-size:78px;line-height:1;margin-top:8px}
.sub{font-size:28px;font-weight:600;color:${c.sub};margin-top:10px;max-width:560px}
.count{position:absolute;left:70px;top:34px;z-index:2;background:#fff;color:#1E2B22;font-weight:700;font-size:24px;padding:10px 20px;border-radius:999px}
</style></head><body class="${c.kind}"><div class="dots"></div><div class="halo"></div>
<div class="brand"><svg viewBox="0 0 120 120">${mark('#BFE3CB', '#1F6B4A')}</svg>Petit Baobab</div>
<div class="lid"></div><div class="inner"></div>
${medals}${maman}${chips}
<div class="front">${deco}<span class="count">${count(p)} ${p.id === 'valise-complete' ? 'valises' : 'articles'}</span><div class="tag"><div class="kicker">${t.kicker}</div><h1>${t.title}</h1><div class="sub">${t.extra ? t.extra.replace(/^\+ /, 'Avec ') + ' · ' : ''}${p.tagline || ''}</div></div></div>
${c.kind === 'box' ? bow : ''}
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
