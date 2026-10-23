/* Construit le site pour Netlify à partir de petit-baobab.html :
   une vraie adresse par page (titre, description, canonique, partage réseaux, données structurées),
   page 404, sitemap.xml, robots.txt, llms.txt, favicon, image de partage, manifest, en-têtes de sécurité.
   Usage : node build.js            → dossier site/ + petit-baobab-site.zip
           SITE_URL=https://www.monsite.ci node build.js   (à faire dès que le nom de domaine est connu)
   Sur Netlify (dépôt GitHub relié) : le build tourne tout seul avec l'adresse du site (variable URL fournie par Netlify) ;
   sans Playwright, les PNG (favicons, image de partage) sont repris du dossier static/. */
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const { execSync } = require('child_process');

const SITE_URL = (process.env.SITE_URL || process.env.URL || 'https://petit-baobab.netlify.app').replace(/\/$/, '');  // Netlify fournit URL (adresse du site, puis le nom de domaine une fois branché)
const SRC = path.join(__dirname, 'petit-baobab.html');
const OUT = path.join(__dirname, 'site');
const TODAY = new Date().toISOString().slice(0, 10);

const src = fs.readFileSync(SRC, 'utf8');

/* ---- Données du site, lues dans le code de la page (une seule source de vérité) ---- */
function extract(name) {
  const m = src.match(new RegExp('var ' + name + ' = ([\\s\\S]*?);\\n\\s*(?=var |/\\*)'));
  if (!m) throw new Error('bloc ' + name + ' introuvable');
  return vm.runInNewContext('(' + m[1] + ')');
}
const CONFIG = extract('CONFIG');
const ROUTES = extract('ROUTES');
const PRODUCTS = extract('PRODUCTS').filter(p => !p.hidden);   // les articles masqués depuis la page Catalogue ne sont pas publiés
const CATS = extract('CATS');
const UNIVERS = extract('UNIVERS');
const FAQ = [...src.matchAll(/<details><summary>([\s\S]*?)<svg[\s\S]*?<\/summary><p>([\s\S]*?)<\/p><\/details>/g)].map(m => ({ q: m[1].trim(), a: m[2].trim() }));

/* ---- Morceaux de la page ---- */
const fonts = (src.match(/<link rel="preconnect"[\s\S]*?display=swap">/) || [''])[0];
const style = (src.match(/<style>([\s\S]*?)<\/style>/) || ['', ''])[1];
const bodyStart = src.indexOf('</style>') + '</style>'.length;
let body = src.slice(bodyStart).trim();
// Les liens internes pointent vers les vraies adresses
body = body.replace(/href="#([a-z]+)"/g, (all, key) => ROUTES[key] ? 'href="' + ROUTES[key].path + '"' : all);

const BASE_CSS = `:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}html,body{margin:0}[hidden]{display:none!important}`;
const tel = '+' + CONFIG.whatsapp;
const phoneDisplay = CONFIG.whatsappDisplay;

function jsonld(view) {
  const r = ROUTES[view];
  const org = {
    '@type': 'OnlineStore', '@id': SITE_URL + '/#organisation',
    name: CONFIG.brand, url: SITE_URL + '/', logo: SITE_URL + '/icon-512.png', image: SITE_URL + '/og-image.png',
    description: ROUTES.accueil.description, slogan: 'Des racines solides dès le premier jour.',
    telephone: tel,
    contactPoint: { '@type': 'ContactPoint', contactType: 'customer service', telephone: tel, availableLanguage: 'fr' },
    areaServed: { '@type': 'Country', name: 'Côte d\'Ivoire' },
    priceRange: '600 – 550 000 FCFA', currenciesAccepted: 'XOF', paymentAccepted: 'Espèces, Wave, Mobile Money (Orange Money, MTN MoMo, Moov Money)',
    sameAs: [CONFIG.social && CONFIG.social.instagram, CONFIG.social && CONFIG.social.tiktok].filter(Boolean)
  };
  const website = {
    '@type': 'WebSite', '@id': SITE_URL + '/#site', url: SITE_URL + '/', name: CONFIG.brand, inLanguage: 'fr',
    publisher: { '@id': SITE_URL + '/#organisation' },
    potentialAction: { '@type': 'SearchAction', target: { '@type': 'EntryPoint', urlTemplate: SITE_URL + '/boutique/?q={search_term_string}' }, 'query-input': 'required name=search_term_string' }
  };
  const page = { '@type': view === 'histoire' ? 'AboutPage' : 'WebPage', '@id': SITE_URL + r.path + '#page', url: SITE_URL + r.path, name: r.title, description: r.description, inLanguage: 'fr', isPartOf: { '@id': SITE_URL + '/#site' }, dateModified: TODAY };
  const crumbs = { '@type': 'BreadcrumbList', itemListElement: [{ '@type': 'ListItem', position: 1, name: 'Accueil', item: SITE_URL + '/' }] };
  if (view !== 'accueil') crumbs.itemListElement.push({ '@type': 'ListItem', position: 2, name: r.nav, item: SITE_URL + r.path });
  const graph = [org, website, page, crumbs];
  const product = p => ({
    '@type': 'Product', name: p.name, description: p.desc || p.tagline || '', sku: p.id,
    ...(p.image ? { image: SITE_URL + '/' + p.image } : {}),
    brand: { '@type': 'Brand', name: CONFIG.brand },
    offers: { '@type': 'Offer', price: p.price, priceCurrency: 'XOF', availability: 'https://schema.org/InStock', url: SITE_URL + r.path, seller: { '@id': SITE_URL + '/#organisation' } }
  });
  const list = (name, items) => ({ '@type': 'ItemList', name, numberOfItems: items.length, itemListElement: items.map((p, i) => ({ '@type': 'ListItem', position: i + 1, item: product(p) })) });
  if (r.univers) graph.push(list(r.nav, PRODUCTS.filter(p => { const c = CATS.find(x => x.id === p.cat); return c && c.univers === r.univers; })));
  if (view === 'packs') graph.push(list('Packs naissance', PRODUCTS.filter(p => p.cat === 'packs')));
  if (view === 'valise') graph.push(list('Valises de maternité', PRODUCTS.filter(p => p.cat === 'valise')));
  if (view === 'boutique') graph.push(list('Boutique', PRODUCTS));
  if (view === 'livraison') graph.push({ '@type': 'FAQPage', mainEntity: FAQ.map(f => ({ '@type': 'Question', name: f.q, acceptedAnswer: { '@type': 'Answer', text: f.a } })) });
  return JSON.stringify({ '@context': 'https://schema.org', '@graph': graph });
}

function pageFor(view) {
  const r = ROUTES[view];
  let b = body;
  // Un seul titre principal par page : le titre de la vue servie devient le h1, le h1 du héros redevient h2 ailleurs
  if (view !== 'accueil') {
    b = b.replace(/<h1 class="([^"]*hero-title[^"]*)">/, '<h2 class="$1">').replace('</h1>', '</h2>');
    const secId = r.univers ? 'v-univers' : 'v-' + view;
    const start = b.indexOf('id="' + secId + '"');
    const end = b.indexOf('</section>', start);
    let sec = b.slice(start, end);
    const m = sec.match(/<h2 class="([^"]*view-title[^"]*)"([^>]*)>/);
    if (m) { const at = sec.indexOf(m[0]); const close = sec.indexOf('</h2>', at); sec = sec.slice(0, at) + '<h1 class="' + m[1] + '"' + m[2] + '>' + sec.slice(at + m[0].length, close) + '</h1>' + sec.slice(close + 5); }
    b = b.slice(0, start) + sec + b.slice(end);
  }
  if (r.univers) {
    const u = UNIVERS.find(x => x.id === r.univers);
    const pad = n => (n < 10 ? '0' : '') + n;
    const hero = `<div class="univ-hero" id="univ-hero" style="--uc:var(--u-${u.id})"><div class="wrap"><span class="kicker">Univers ${pad(u.n)}</span><h1 class="view-title">${esc(u.title)}</h1><p class="lead">${esc(u.tagline)}</p><div class="tips"><div class="tip"><span class="kicker">Quand en avoir besoin ?</span><p>${esc(u.quand)}</p></div><div class="tip"><span class="kicker">Notre conseil</span><p>${esc(u.conseil)}</p></div><div class="tip gift"><span class="kicker">Idée cadeau</span><p>${esc(u.cadeau)}</p></div></div></div><div class="bignum" aria-hidden="true">${pad(u.n)}</div></div>`;
    b = b.replace('<div class="univ-hero" id="univ-hero"></div>', hero);
  }
  // La page servie est visible avant même l'exécution du script
  const visId = r.univers ? 'v-univers' : 'v-' + view;
  b = b.replace('class="view" id="' + visId + '" hidden', 'class="view" id="' + visId + '"');
  const url = SITE_URL + r.path;
  return `<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>${esc(r.title)}</title>
<meta name="description" content="${esc(r.description)}">
<link rel="canonical" href="${url}" data-site="${SITE_URL}">
${r.noindex ? '<meta name="robots" content="noindex, follow">\n' : ''}<meta property="og:type" content="website">
<meta property="og:site_name" content="${esc(CONFIG.brand)}">
<meta property="og:locale" content="fr_FR">
<meta property="og:title" content="${esc(r.title)}">
<meta property="og:description" content="${esc(r.description)}">
<meta property="og:url" content="${url}">
<meta property="og:image" content="${SITE_URL}/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="${esc(CONFIG.brand)} : des racines solides dès le premier jour. Packs naissance et équipement bébé livrés à Abidjan">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${esc(r.title)}">
<meta name="twitter:description" content="${esc(r.description)}">
<meta name="twitter:image" content="${SITE_URL}/og-image.png">
<meta name="theme-color" content="#1F6B4A" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#121915" media="(prefers-color-scheme: dark)">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
${fonts}
<script type="application/ld+json">${jsonld(view)}</script>
<script>window.__ROUTE__='${view}';</script>
<style>
${BASE_CSS}
${style.trim()}
</style>
</head>
<body>
${b}
</body>
</html>
`;
}
function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;'); }

/* ---- Écriture ---- */
fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(path.join(OUT, 'images'), { recursive: true });
// Photos des produits (dossier images/ à côté de ce script)
const IMG_SRC = path.join(__dirname, 'images');
if (fs.existsSync(IMG_SRC)) for (const f of fs.readdirSync(IMG_SRC)) fs.copyFileSync(path.join(IMG_SRC, f), path.join(OUT, 'images', f));
// Sur les aperçus Netlify seulement (jamais en ligne) : un sélecteur pour comparer des polices de titres.
const PREVIEW_TOOLS = process.env.CONTEXT === 'deploy-preview' ? `<div id="pv-fonts" style="position:fixed;left:12px;bottom:12px;z-index:60;background:#fff;color:#1E2B22;border:1px solid #D9E1D8;border-radius:14px;box-shadow:0 10px 30px rgba(30,43,34,.18);padding:10px 12px;font:600 13px/1.3 system-ui,sans-serif;max-width:calc(100vw - 100px)">
<div style="margin-bottom:6px">Aperçu · police des titres</div><div id="pv-btns" style="display:flex;flex-wrap:wrap;gap:6px"></div></div>
<script>(function(){var F=[['Fraunces','"Fraunces",Georgia,serif',''],['Young Serif','"Young Serif",Georgia,serif','Young+Serif'],['DM Serif Display','"DM Serif Display",Georgia,serif','DM+Serif+Display']];
var cur=localStorage.getItem('pv-font')||'Fraunces',box=document.getElementById('pv-btns');
function load(q){if(!q||document.querySelector('link[data-pv="'+q+'"]'))return;var l=document.createElement('link');l.rel='stylesheet';l.dataset.pv=q;l.href='https://fonts.googleapis.com/css2?family='+q+'&display=swap';document.head.appendChild(l);}
function set(n){var f=F.filter(function(x){return x[0]===n})[0]||F[0];load(f[2]);document.documentElement.style.setProperty('--font-display',f[1]);var w=document.getElementById('pv-w')||document.head.appendChild(Object.assign(document.createElement('style'),{id:'pv-w'}));w.textContent=f[2]?'h1,h2,h3,h4{font-weight:400}':'';try{localStorage.setItem('pv-font',f[0])}catch(e){}
[].forEach.call(box.children,function(b){var on=b.textContent===f[0];b.style.background=on?'#1F6B4A':'#fff';b.style.color=on?'#fff':'#1E2B22'})}
F.forEach(function(f){var b=document.createElement('button');b.type='button';b.textContent=f[0];b.style.cssText='border:1px solid #1F6B4A;border-radius:999px;padding:6px 10px;font:600 13px system-ui,sans-serif;cursor:pointer';b.onclick=function(){set(f[0])};box.appendChild(b)});set(cur);})();</script>` : '';
let written = [];
for (const view of Object.keys(ROUTES)) {
  const r = ROUTES[view];
  const file = view === 'notfound' ? path.join(OUT, '404.html') : path.join(OUT, r.path.replace(/^\//, ''), 'index.html');
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, PREVIEW_TOOLS ? pageFor(view).replace('\n</body>', '\n' + PREVIEW_TOOLS + '\n</body>') : pageFor(view));
  written.push(path.relative(OUT, file));
}

/* ---- Aménageur de chambre 3D : page à part (/amenageur/), chargée seulement quand on l'ouvre ----
   amenageur/page.html (l'outil) + amenageur/meubles.json (dimensions, modèle 3D, couleurs du modèle).
   Nom, référence, prix et photo viennent de PRODUCTS : toujours ceux du site. three.js, vidéo et affiche : static/amenageur/. */
const AM_DIR = path.join(__dirname, 'amenageur');
const AM_PATH = '/amenageur/';
if (fs.existsSync(path.join(AM_DIR, 'page.html'))) {
  const byIdP = Object.fromEntries(PRODUCTS.map(p => [p.id, p]));
  const catalog = JSON.parse(fs.readFileSync(path.join(AM_DIR, 'meubles.json'), 'utf8')).map(m => {
    const p = byIdP[m.id];
    if (!p) throw new Error('aménageur : l\'article ' + m.id + ' est absent ou masqué');
    const col = m.couleur ? (p.colors || []).find(c => c[0] === m.couleur) : null;
    if (m.couleur && !col) throw new Error('aménageur : couleur « ' + m.couleur + ' » absente de ' + m.id);
    const o = Object.assign({}, m, { name: p.name + (col ? ' (' + col[0] + ')' : ''), ref: p.ref || p.id.toUpperCase(), price: p.price, img: '/' + (col && col[1] ? col[1] : p.image) });
    delete o.couleur;
    return o;
  });
  const t = fs.readFileSync(path.join(AM_DIR, 'page.html'), 'utf8');
  const amTitle = 'Aménager la chambre de bébé en 3D · ' + CONFIG.brand;
  const amDesc = 'Entrez les mesures de la chambre, placez les lits, armoires et commodes de la boutique sur un plan et en 3D, vérifiez que tout rentre, puis commandez sur WhatsApp.';
  const amFonts = (t.match(/<link rel="preconnect"[\s\S]*?display=swap">/) || [''])[0];
  const amStyle = t.slice(t.indexOf('<style>'), t.indexOf('</style>') + 8);
  const amBody = t.slice(t.indexOf('</style>') + 8).trim()
    .replace('/*CATALOG*/', JSON.stringify(catalog))
    .replace("'/*WA*/'", JSON.stringify(String(CONFIG.whatsapp).replace(/\D/g, '')))
    .replace('/*WA_DISPLAY*/', esc(CONFIG.whatsappDisplay));
  const amUrl = SITE_URL + AM_PATH;
  fs.mkdirSync(path.join(OUT, 'amenageur'), { recursive: true });
  fs.writeFileSync(path.join(OUT, 'amenageur', 'index.html'), `<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>${esc(amTitle)}</title>
<meta name="description" content="${esc(amDesc)}">
<link rel="canonical" href="${amUrl}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="${esc(CONFIG.brand)}">
<meta property="og:locale" content="fr_FR">
<meta property="og:title" content="${esc(amTitle)}">
<meta property="og:description" content="${esc(amDesc)}">
<meta property="og:url" content="${amUrl}">
<meta property="og:image" content="${SITE_URL}/amenageur/demo-poster.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#1F6B4A">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
${amFonts}
<style>[hidden]{display:none!important}</style>
${amStyle}
</head>
<body>
${amBody}
</body>
</html>
`);
  written.push('amenageur/index.html');
}

const indexable = Object.keys(ROUTES).filter(v => !ROUTES[v].noindex);
fs.writeFileSync(path.join(OUT, 'sitemap.xml'), `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${indexable.map(v => `  <url><loc>${SITE_URL}${ROUTES[v].path}</loc><lastmod>${TODAY}</lastmod><changefreq>${v === 'accueil' || v === 'boutique' ? 'weekly' : 'monthly'}</changefreq><priority>${v === 'accueil' ? '1.0' : v === 'packs' || v === 'boutique' ? '0.9' : '0.6'}</priority></url>`).join('\n')}
${written.includes('amenageur/index.html') ? `  <url><loc>${SITE_URL}${AM_PATH}</loc><lastmod>${TODAY}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>\n` : ''}</urlset>
`);
fs.writeFileSync(path.join(OUT, 'robots.txt'), `User-agent: *
Allow: /
Disallow: /commande/

Sitemap: ${SITE_URL}/sitemap.xml
`);
const packs = PRODUCTS.filter(p => p.cat === 'packs');
fs.writeFileSync(path.join(OUT, 'llms.txt'), `# ${CONFIG.brand}

> ${ROUTES.accueil.description}

Boutique de puériculture en ligne à Abidjan (Côte d'Ivoire) : packs naissance par budget, valise de maternité et équipement de bébé classé en 8 univers. Commande sur le site, envoi du récapitulatif sur WhatsApp (${phoneDisplay}) avec une référence de commande, paiement à la livraison (espèces, Wave ou Mobile Money), par Wave ou Mobile Money avant livraison, ou acompte de 50 % et solde à la livraison. Livraison à Abidjan en moins de 24 h, offerte dès ${CONFIG.freeDeliveryFrom.toLocaleString('fr-FR')} FCFA ; envoi par compagnie de transport dans le reste du pays. Échange sous 48 h en cas de défaut. Horaires WhatsApp : tous les jours de 8 h à 21 h.

## La marque

Le baobab est l'arbre emblématique de l'Afrique de l'Ouest : solide, protecteur, il traverse les générations. Un petit baobab, c'est un enfant qui va grandir fort. Promesse en trois mots : solide (articles neufs sous emballage d'origine, choisis pour durer), protecteur (prix affichés, conseil sur WhatsApp, échange sous 48 h), qui dure (8 univers et un guide mois par mois, du premier jour aux premiers pas). Signature : « Des racines solides dès le premier jour. »

## Pages

${indexable.map(v => `- [${ROUTES[v].nav}](${SITE_URL}${ROUTES[v].path}) : ${ROUTES[v].description}`).join('\n')}

## Univers

${UNIVERS.map(u => `- ${u.title} : ${u.tagline}`).join('\n')}

## Packs naissance (prix en FCFA)

${packs.map(p => `- ${p.name} : ${p.price.toLocaleString('fr-FR')} FCFA. ${p.tagline}. ${p.desc}`).join('\n')}

## Questions fréquentes

${FAQ.map(f => `- ${f.q} ${f.a}`).join('\n')}
`);
fs.writeFileSync(path.join(OUT, '_headers'), `/*
  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://plausible.io; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self' https://plausible.io; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; object-src 'none'; upgrade-insecure-requests

/images/*
  Cache-Control: public, max-age=31536000, immutable


/*.png
  Cache-Control: public, max-age=604800

/favicon.svg
  Cache-Control: public, max-age=604800
`);
fs.writeFileSync(path.join(OUT, 'site.webmanifest'), JSON.stringify({
  name: CONFIG.brand, short_name: CONFIG.brand, description: ROUTES.accueil.description, lang: 'fr', start_url: '/', display: 'minimal-ui',
  background_color: '#F5F7F2', theme_color: '#1F6B4A',
  icons: [{ src: '/icon-192.png', sizes: '192x192', type: 'image/png' }, { src: '/icon-512.png', sizes: '512x512', type: 'image/png' }]
}, null, 2));
fs.writeFileSync(path.join(OUT, 'images', 'LISEZMOI.txt'), `Déposez ici les photos des produits (format WebP ou JPEG, 1200 px de large maximum, moins de 200 Ko chacune),
puis indiquez dans petit-baobab.html, pour chaque produit : image:'images/nom-du-fichier.webp', alt:'description de la photo'.
`);

/* Favicon et image de partage */
const LOGO_WHITE = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 572.0 120.0"><g transform="translate(0 0)"><g fill="#F2A93B"><circle cx="104" cy="18" r="10"/></g><g fill="rgba(255,255,255,.22)"><ellipse cx="60" cy="110" rx="56" ry="5"/></g><g fill="#F5F7F2"><path d="M43 110c4-18 5-34 1-54h30c-4 20-3 36 1 54z"/></g><g fill="#F5F7F2"><circle cx="59" cy="44" r="26"/><circle cx="33" cy="54" r="17"/><circle cx="85" cy="54" r="17"/><circle cx="43" cy="30" r="15"/><circle cx="75" cy="30" r="15"/><circle cx="59" cy="22" r="13"/></g><g fill="#F2A93B"><circle cx="71" cy="40" r="3"/></g><g fill="#F5F7F2"><path d="M94 110c1.5-7 1.8-13 .7-20h8.6c-1.1 7-.8 13 .7 20z"/></g><g fill="#F5F7F2"><circle cx="99" cy="82" r="9.5"/><circle cx="91" cy="87" r="5.5"/><circle cx="107" cy="87" r="5.5"/></g><g fill="#F2A93B"><circle cx="103" cy="80" r="2"/></g></g><g transform="translate(136.0 38.0)"><g fill="#F5F7F2"><path d="M9.062857142857144 52.668571428571425Q6.314285714285715 52.668571428571425 5.162857142857144 51.85142857142857Q4.011428571428572 51.034285714285716 3.7142857142857144 49.69714285714286Q3.4171428571428573 48.36 3.4171428571428573 46.94857142857143V6.388571428571424Q3.4171428571428573 4.977142857142859 3.7142857142857144 3.677142857142858Q4.011428571428572 2.3771428571428572 5.2 1.5599999999999987Q6.388571428571429 0.7428571428571402 9.137142857142857 0.7428571428571402H24.365714285714287Q27.485714285714288 0.7428571428571402 30.642857142857146 1.857142857142854Q33.800000000000004 2.971428571428568 36.511428571428574 5.311428571428568Q39.222857142857144 7.651428571428568 40.894285714285715 11.068571428571428Q42.565714285714286 14.485714285714288 42.565714285714286 19.091428571428573Q42.565714285714286 23.622857142857143 40.894285714285715 27.04Q39.222857142857144 30.457142857142856 36.511428571428574 32.722857142857144Q33.800000000000004 34.98857142857143 30.60571428571429 36.14Q27.411428571428573 37.29142857142857 24.291428571428572 37.29142857142857H14.782857142857143V47.02285714285714Q14.782857142857143 48.434285714285714 14.485714285714286 49.73428571428572Q14.188571428571429 51.034285714285716 13.0 51.85142857142857Q11.811428571428571 52.668571428571425 9.062857142857144 52.668571428571425ZM14.782857142857143 26.0H24.365714285714287Q26.0 26.0 27.597142857142856 25.294285714285714Q29.194285714285716 24.588571428571427 30.271428571428572 23.028571428571425Q31.34857142857143 21.468571428571426 31.34857142857143 19.017142857142858Q31.34857142857143 16.93714285714286 30.457142857142856 15.377142857142857Q29.565714285714286 13.817142857142855 27.96857142857143 12.925714285714285Q26.371428571428574 12.034285714285716 24.291428571428572 12.034285714285716H14.782857142857143Z"/><path d="M65.81714285714287 53.33714285714286Q60.617142857142866 53.33714285714286 56.86571428571429 51.62857142857143Q53.114285714285714 49.92 50.73714285714286 47.13428571428572Q48.36000000000001 44.34857142857143 47.20857142857143 40.93142857142857Q46.057142857142864 37.51428571428571 46.057142857142864 34.097142857142856Q46.057142857142864 28.525714285714287 48.58285714285715 24.217142857142857Q51.10857142857143 19.908571428571427 55.56571428571429 17.419999999999998Q60.02285714285715 14.931428571428569 65.81714285714287 14.931428571428569Q70.1257142857143 14.931428571428569 73.28285714285715 16.305714285714284Q76.44 17.68 78.48285714285714 19.87142857142857Q80.52571428571429 22.06285714285714 81.52857142857144 24.588571428571427Q82.53142857142858 27.114285714285714 82.53142857142858 29.417142857142856Q82.53142857142858 33.50285714285714 80.56285714285715 35.47142857142857Q78.59428571428572 37.44 75.54857142857144 37.44H57.86857142857143Q58.01714285714286 39.37142857142857 59.24285714285715 40.708571428571425Q60.46857142857144 42.04571428571428 62.32571428571429 42.78857142857143Q64.18285714285715 43.53142857142857 66.26285714285714 43.53142857142857Q68.0457142857143 43.53142857142857 69.38285714285715 43.34571428571428Q70.72 43.16 71.68571428571428 42.825714285714284Q72.65142857142857 42.49142857142857 73.46857142857144 42.15714285714286Q74.28571428571429 41.822857142857146 74.91714285714286 41.6Q75.54857142857144 41.37714285714286 76.14285714285714 41.30285714285714Q77.25714285714287 41.22857142857143 78.1857142857143 41.934285714285714Q79.11428571428573 42.64 79.85714285714286 44.05142857142857Q80.37714285714287 44.86857142857143 80.56285714285715 45.611428571428576Q80.74857142857144 46.354285714285716 80.74857142857144 47.097142857142856Q80.74857142857144 48.88 78.92857142857143 50.29142857142857Q77.10857142857142 51.70285714285714 73.80285714285714 52.519999999999996Q70.49714285714286 53.33714285714286 65.81714285714287 53.33714285714286ZM57.86857142857143 31.34857142857143H69.6057142857143Q70.79428571428572 31.34857142857143 71.35142857142858 30.939999999999998Q71.90857142857143 30.53142857142857 71.90857142857143 29.34285714285714Q71.90857142857143 28.005714285714284 71.09142857142858 27.002857142857142Q70.27428571428572 26.0 68.9 25.442857142857143Q67.52571428571429 24.885714285714286 65.74285714285715 24.885714285714286Q63.440000000000005 24.885714285714286 61.65714285714286 25.777142857142856Q59.87428571428572 26.66857142857143 58.871428571428574 28.154285714285713Q57.86857142857143 29.64 57.86857142857143 31.34857142857143Z"/><path d="M106.37714285714287 52.668571428571425Q102.58857142857144 52.668571428571425 99.87714285714287 51.85142857142857Q97.1657142857143 51.034285714285716 95.38285714285715 49.325714285714284Q93.60000000000001 47.61714285714286 92.74571428571429 44.980000000000004Q91.89142857142858 42.34285714285714 91.89142857142858 38.70285714285714V8.542857142857144Q91.89142857142858 7.057142857142857 92.15142857142858 5.868571428571428Q92.41142857142859 4.68 93.60000000000001 3.8999999999999986Q94.78857142857143 3.1199999999999974 97.46285714285716 3.1199999999999974Q100.13714285714286 3.1199999999999974 101.3257142857143 3.937142857142856Q102.51428571428572 4.7542857142857144 102.77428571428572 6.017142857142858Q103.03428571428572 7.280000000000001 103.03428571428572 8.765714285714282V38.25714285714285Q103.03428571428572 39.44571428571429 103.22 40.22571428571429Q103.4057142857143 41.005714285714284 103.77714285714288 41.37714285714286Q104.14857142857144 41.748571428571424 104.81714285714287 41.89714285714285Q105.4857142857143 42.04571428571428 106.45142857142858 42.04571428571428Q108.08571428571429 42.04571428571428 109.34857142857143 42.34285714285714Q110.61142857142858 42.64 111.31714285714287 43.68Q112.02285714285715 44.72 112.02285714285715 47.17142857142857Q112.02285714285715 49.84571428571429 111.2057142857143 51.034285714285716Q110.38857142857144 52.222857142857144 109.08857142857144 52.44571428571429Q107.78857142857143 52.668571428571425 106.37714285714287 52.668571428571425ZM89.58857142857144 16.119999999999997H97.76L108.01142857142858 15.822857142857139Q109.42285714285715 15.822857142857139 110.6857142857143 16.08285714285714Q111.94857142857144 16.34285714285714 112.7657142857143 17.53142857142857Q113.58285714285715 18.72 113.58285714285715 21.468571428571426Q113.58285714285715 23.994285714285713 112.80285714285715 25.18285714285714Q112.02285714285715 26.37142857142857 110.76000000000002 26.705714285714286Q109.49714285714288 27.04 108.01142857142858 27.04L98.28000000000002 26.817142857142855H89.29142857142858Q87.13714285714286 26.74285714285714 86.28285714285715 25.517142857142858Q85.42857142857144 24.291428571428572 85.42857142857144 21.394285714285715Q85.42857142857144 18.72 86.46857142857144 17.419999999999998Q87.50857142857144 16.119999999999997 89.58857142857144 16.119999999999997Z"/><path d="M123.76000000000002 52.668571428571425Q121.01142857142858 52.668571428571425 119.86000000000001 51.888571428571424Q118.70857142857145 51.10857142857143 118.44857142857146 49.808571428571426Q118.18857142857145 48.50857142857143 118.18857142857145 47.097142857142856V21.17142857142857Q118.18857142857145 19.685714285714283 118.44857142857146 18.42285714285714Q118.70857142857145 17.159999999999997 119.89714285714288 16.38Q121.0857142857143 15.600000000000001 123.83428571428573 15.600000000000001Q126.50857142857144 15.600000000000001 127.66000000000003 16.417142857142856Q128.8114285714286 17.23428571428571 129.07142857142858 18.497142857142855Q129.33142857142857 19.759999999999998 129.33142857142857 21.32V47.17142857142857Q129.33142857142857 48.582857142857144 129.07142857142858 49.88285714285715Q128.8114285714286 51.182857142857145 127.66000000000003 51.925714285714285Q126.50857142857144 52.668571428571425 123.76000000000002 52.668571428571425ZM123.76000000000002 10.177142857142854Q120.93714285714287 10.177142857142854 119.74857142857144 9.36Q118.56000000000002 8.542857142857144 118.30000000000001 7.205714285714286Q118.04000000000002 5.868571428571428 118.04000000000002 4.382857142857141Q118.04000000000002 2.8228571428571385 118.33714285714288 1.5228571428571414Q118.63428571428572 0.2228571428571442 119.82285714285715 -0.5571428571428569Q121.01142857142858 -1.337142857142858 123.83428571428573 -1.337142857142858Q126.58285714285716 -1.337142857142858 127.77142857142859 -0.5199999999999996Q128.96 0.29714285714285893 129.22000000000003 1.6342857142857135Q129.48000000000002 2.971428571428568 129.48000000000002 4.4571428571428555Q129.48000000000002 5.942857142857143 129.22000000000003 7.279999999999998Q128.96 8.617142857142852 127.77142857142859 9.397142857142853Q126.58285714285716 10.177142857142854 123.76000000000002 10.177142857142854Z"/><path d="M154.8857142857143 52.668571428571425Q151.09714285714287 52.668571428571425 148.3857142857143 51.85142857142857Q145.67428571428573 51.034285714285716 143.8914285714286 49.325714285714284Q142.10857142857145 47.61714285714286 141.25428571428574 44.980000000000004Q140.4 42.34285714285714 140.4 38.70285714285714V8.542857142857144Q140.4 7.057142857142857 140.66000000000003 5.868571428571428Q140.92000000000002 4.68 142.10857142857145 3.8999999999999986Q143.29714285714286 3.1199999999999974 145.9714285714286 3.1199999999999974Q148.6457142857143 3.1199999999999974 149.83428571428573 3.937142857142856Q151.02285714285716 4.7542857142857144 151.28285714285715 6.017142857142858Q151.54285714285714 7.280000000000001 151.54285714285714 8.765714285714282V38.25714285714285Q151.54285714285714 39.44571428571429 151.72857142857143 40.22571428571429Q151.9142857142857 41.005714285714284 152.28571428571428 41.37714285714286Q152.65714285714287 41.748571428571424 153.3257142857143 41.89714285714285Q153.99428571428572 42.04571428571428 154.96 42.04571428571428Q156.59428571428572 42.04571428571428 157.85714285714286 42.34285714285714Q159.12 42.64 159.8257142857143 43.68Q160.5314285714286 44.72 160.5314285714286 47.17142857142857Q160.5314285714286 49.84571428571429 159.71428571428572 51.034285714285716Q158.89714285714285 52.222857142857144 157.59714285714284 52.44571428571429Q156.29714285714286 52.668571428571425 154.8857142857143 52.668571428571425ZM138.09714285714287 16.119999999999997H146.26857142857145L156.52 15.822857142857139Q157.93142857142857 15.822857142857139 159.1942857142857 16.08285714285714Q160.45714285714286 16.34285714285714 161.27428571428572 17.53142857142857Q162.0914285714286 18.72 162.0914285714286 21.468571428571426Q162.0914285714286 23.994285714285713 161.3114285714286 25.18285714285714Q160.5314285714286 26.37142857142857 159.26857142857145 26.705714285714286Q158.0057142857143 27.04 156.52 27.04L146.78857142857143 26.817142857142855H137.8Q135.6457142857143 26.74285714285714 134.79142857142858 25.517142857142858Q133.93714285714287 24.291428571428572 133.93714285714287 21.394285714285715Q133.93714285714287 18.72 134.97714285714287 17.419999999999998Q136.01714285714286 16.119999999999997 138.09714285714287 16.119999999999997Z"/><path d="M189.65142857142857 52.668571428571425Q186.97714285714284 52.668571428571425 185.7885714285714 51.81428571428572Q184.6 50.96 184.33999999999997 49.58571428571429Q184.07999999999998 48.21142857142857 184.07999999999998 46.72571428571429V6.462857142857139Q184.07999999999998 4.977142857142859 184.33999999999997 3.677142857142858Q184.6 2.3771428571428572 185.7885714285714 1.5228571428571414Q186.97714285714284 0.6685714285714255 189.72571428571428 0.6685714285714255H208.22285714285712Q212.60571428571427 0.6685714285714255 216.02285714285713 2.7485714285714273Q219.44 4.828571428571429 221.44571428571427 8.32Q223.45142857142855 11.811428571428571 223.37714285714284 15.897142857142853Q223.45142857142855 17.53142857142857 223.07999999999998 19.091428571428573Q222.70857142857142 20.65142857142857 222.00285714285712 22.1Q221.29714285714283 23.548571428571428 220.25714285714284 24.737142857142857Q221.81714285714284 26.22285714285714 222.85714285714283 28.117142857142856Q223.89714285714285 30.01142857142857 224.4542857142857 32.09142857142857Q225.01142857142855 34.17142857142857 225.01142857142855 36.325714285714284Q224.93714285714285 39.74285714285714 223.71142857142854 42.75142857142857Q222.48571428571427 45.76 220.25714285714284 47.95142857142857Q218.0285714285714 50.142857142857146 215.13142857142856 51.40571428571428Q212.2342857142857 52.668571428571425 208.96571428571428 52.668571428571425ZM195.37142857142857 41.45142857142857H208.22285714285712Q209.48571428571427 41.45142857142857 210.78571428571428 40.96857142857143Q212.0857142857143 40.48571428571429 212.94 39.18571428571428Q213.7942857142857 37.885714285714286 213.7942857142857 35.50857142857143Q213.7942857142857 33.94857142857143 213.42285714285714 32.90857142857143Q213.05142857142857 31.86857142857143 212.38285714285712 31.31142857142857Q211.7142857142857 30.754285714285714 210.89714285714285 30.53142857142857Q210.07999999999998 30.308571428571426 209.1885714285714 30.23428571428571Q208.29714285714283 30.16 207.48 30.16H205.32571428571427Q202.79999999999998 30.16 201.76 29.082857142857144Q200.72 28.005714285714284 200.72 25.33142857142857Q200.72 22.73142857142857 201.87142857142857 21.69142857142857Q203.02285714285713 20.65142857142857 205.54857142857142 20.65142857142857H207.70285714285714Q208.44571428571427 20.65142857142857 209.26285714285711 20.577142857142857Q210.07999999999998 20.502857142857142 210.71142857142854 20.13142857142857Q211.34285714285713 19.759999999999998 211.75142857142856 18.905714285714286Q212.16 18.051428571428573 212.16 16.565714285714286Q212.16 14.04 210.89714285714285 12.962857142857143Q209.6342857142857 11.885714285714286 206.44 11.885714285714286H195.37142857142857Z"/><path d="M260.52 52.59428571428572Q257.77142857142854 52.59428571428572 256.47142857142853 51.62857142857143Q255.17142857142855 50.66285714285714 255.17142857142855 49.25142857142857L255.9142857142857 47.988571428571426Q255.4685714285714 48.73142857142857 254.20571428571427 49.808571428571426Q252.94285714285712 50.885714285714286 250.93714285714285 51.74Q248.93142857142857 52.59428571428572 245.95999999999998 52.59428571428572Q242.54285714285714 52.59428571428572 239.45999999999998 51.10857142857143Q236.37714285714284 49.62285714285714 234.0 46.98571428571429Q231.62285714285713 44.34857142857143 230.2485714285714 41.00571428571429Q228.8742857142857 37.66285714285714 228.8742857142857 33.94857142857143Q228.8742857142857 30.308571428571426 230.2485714285714 27.002857142857142Q231.62285714285713 23.697142857142858 234.03714285714284 21.134285714285713Q236.45142857142855 18.57142857142857 239.49714285714285 17.085714285714285Q242.54285714285714 15.600000000000001 245.95999999999998 15.600000000000001Q248.70857142857142 15.600000000000001 250.64 16.38Q252.57142857142856 17.159999999999997 253.87142857142857 18.2Q255.17142857142855 19.240000000000002 255.83999999999997 20.205714285714286L255.24571428571429 19.165714285714287Q255.17142857142855 17.38285714285714 256.47142857142853 16.454285714285714Q257.77142857142854 15.525714285714287 260.5942857142857 15.525714285714287Q263.2685714285714 15.525714285714287 264.41999999999996 16.34285714285714Q265.57142857142856 17.159999999999997 265.83142857142855 18.497142857142855Q266.09142857142854 19.834285714285713 266.09142857142854 21.32V46.94857142857143Q266.09142857142854 48.36 265.83142857142855 49.69714285714286Q265.57142857142856 51.034285714285716 264.41999999999996 51.81428571428572Q263.2685714285714 52.59428571428572 260.52 52.59428571428572ZM247.59428571428572 41.52571428571429Q249.5257142857143 41.52571428571429 251.12285714285713 40.52285714285714Q252.72 39.519999999999996 253.64857142857142 37.81142857142857Q254.57714285714286 36.10285714285715 254.57714285714286 34.02285714285714Q254.57714285714286 31.86857142857143 253.61142857142858 30.197142857142858Q252.64571428571426 28.525714285714287 251.01142857142855 27.52285714285714Q249.37714285714284 26.52 247.44571428571427 26.52Q245.29142857142855 26.52 243.62 27.56Q241.94857142857143 28.599999999999998 240.94571428571427 30.308571428571426Q239.94285714285712 32.01714285714286 239.94285714285712 34.17142857142857Q239.94285714285712 36.177142857142854 240.94571428571427 37.848571428571425Q241.94857142857143 39.519999999999996 243.6942857142857 40.52285714285714Q245.44 41.52571428571429 247.59428571428572 41.52571428571429Z"/><path d="M289.8628571428571 53.26285714285714Q286.3714285714285 53.26285714285714 282.91714285714284 51.888571428571424Q279.4628571428571 50.51428571428571 276.64 47.98857142857143Q273.8171428571428 45.462857142857146 272.1828571428571 41.934285714285714Q270.5485714285714 38.40571428571428 270.5485714285714 34.097142857142856Q270.5485714285714 30.085714285714285 272.0342857142857 26.63142857142857Q273.52 23.177142857142854 276.1942857142857 20.502857142857142Q278.8685714285714 17.82857142857143 282.3228571428571 16.305714285714284Q285.77714285714285 14.78285714285714 289.71428571428567 14.78285714285714Q295.0628571428571 14.78285714285714 299.4085714285714 17.345714285714283Q303.7542857142857 19.908571428571427 306.35428571428565 24.29142857142857Q308.9542857142857 28.674285714285713 308.9542857142857 34.02285714285714Q308.9542857142857 38.55428571428571 307.2828571428571 42.08285714285714Q305.6114285714285 45.61142857142857 302.82571428571424 48.137142857142855Q300.03999999999996 50.66285714285714 296.65999999999997 51.962857142857146Q293.28 53.26285714285714 289.8628571428571 53.26285714285714ZM289.71428571428567 42.04571428571428Q291.4971428571428 42.04571428571428 293.35428571428565 41.15428571428571Q295.21142857142854 40.26285714285714 296.47428571428566 38.480000000000004Q297.7371428571428 36.69714285714286 297.7371428571428 33.94857142857143Q297.7371428571428 31.57142857142857 296.6971428571428 29.788571428571426Q295.65714285714284 28.005714285714284 293.8371428571428 27.002857142857142Q292.0171428571428 26.0 289.64 26.0Q287.41142857142853 26.0 285.6657142857142 27.04Q283.91999999999996 28.08 282.8428571428571 29.9Q281.76571428571424 31.72 281.76571428571424 34.02285714285714Q281.76571428571424 36.69714285714286 282.9914285714285 38.51714285714286Q284.21714285714285 40.33714285714286 286.0742857142857 41.191428571428574Q287.9314285714285 42.04571428571428 289.71428571428567 42.04571428571428Z"/><path d="M333.4685714285714 52.59428571428572Q329.8285714285714 52.59428571428572 327.0428571428571 51.07142857142857Q324.2571428571428 49.54857142857143 322.4371428571428 46.94857142857143Q320.6171428571428 44.34857142857143 319.68857142857144 41.00571428571429Q318.76 37.66285714285714 318.83428571428567 33.87428571428571Q318.83428571428567 30.234285714285715 319.79999999999995 26.89142857142857Q320.76571428571424 23.548571428571428 322.58571428571423 21.02285714285714Q324.4057142857142 18.497142857142855 327.1171428571428 17.048571428571428Q329.8285714285714 15.600000000000001 333.4685714285714 15.600000000000001Q336.7371428571428 15.600000000000001 339.81999999999994 17.085714285714285Q342.9028571428571 18.57142857142857 345.28 21.134285714285713Q347.65714285714284 23.697142857142858 349.03142857142853 27.002857142857142Q350.4057142857142 30.308571428571426 350.4057142857142 33.94857142857143Q350.4057142857142 37.73714285714286 349.03142857142853 41.11714285714285Q347.65714285714284 44.497142857142855 345.28 47.097142857142856Q342.9028571428571 49.69714285714286 339.85714285714283 51.14571428571429Q336.81142857142856 52.59428571428572 333.4685714285714 52.59428571428572ZM331.9085714285714 41.6Q333.9885714285714 41.6 335.62285714285713 40.597142857142856Q337.2571428571428 39.59428571428572 338.26 37.885714285714286Q339.2628571428571 36.177142857142854 339.2628571428571 34.097142857142856Q339.2628571428571 31.942857142857143 338.29714285714283 30.271428571428572Q337.33142857142855 28.599999999999998 335.6971428571428 27.634285714285713Q334.0628571428571 26.66857142857143 331.9828571428571 26.66857142857143Q329.97714285714284 26.66857142857143 328.30571428571426 27.634285714285713Q326.6342857142857 28.599999999999998 325.7057142857143 30.271428571428572Q324.77714285714285 31.942857142857143 324.77714285714285 34.097142857142856Q324.77714285714285 36.177142857142854 325.74285714285713 37.885714285714286Q326.7085714285714 39.59428571428572 328.34285714285716 40.597142857142856Q329.97714285714284 41.6 331.9085714285714 41.6ZM318.9828571428571 52.668571428571425Q316.3085714285714 52.668571428571425 315.11999999999995 51.85142857142857Q313.9314285714285 51.034285714285716 313.6714285714285 49.73428571428572Q313.41142857142853 48.434285714285714 313.41142857142853 47.02285714285714V4.308571428571426Q313.41142857142853 2.748571428571424 313.7085714285714 1.485714285714284Q314.00571428571425 0.2228571428571442 315.15714285714284 -0.5571428571428569Q316.3085714285714 -1.337142857142858 319.0571428571428 -1.337142857142858Q321.7314285714285 -1.337142857142858 322.8457142857143 -0.5199999999999996Q323.96 0.29714285714285893 324.1828571428571 1.597142857142856Q324.4057142857142 2.8971428571428532 324.33142857142855 4.308571428571426V49.325714285714284Q323.96 51.034285714285716 322.77142857142854 51.85142857142857Q321.5828571428571 52.668571428571425 318.9828571428571 52.668571428571425Z"/><path d="M385.6914285714285 52.59428571428572Q382.94285714285706 52.59428571428572 381.6428571428571 51.62857142857143Q380.3428571428571 50.66285714285714 380.3428571428571 49.25142857142857L381.08571428571423 47.988571428571426Q380.63999999999993 48.73142857142857 379.37714285714276 49.808571428571426Q378.11428571428564 50.885714285714286 376.1085714285714 51.74Q374.1028571428571 52.59428571428572 371.1314285714285 52.59428571428572Q367.71428571428567 52.59428571428572 364.6314285714285 51.10857142857143Q361.5485714285714 49.62285714285714 359.1714285714285 46.98571428571429Q356.79428571428565 44.34857142857143 355.41999999999996 41.00571428571429Q354.0457142857142 37.66285714285714 354.0457142857142 33.94857142857143Q354.0457142857142 30.308571428571426 355.41999999999996 27.002857142857142Q356.79428571428565 23.697142857142858 359.20857142857136 21.134285714285713Q361.6228571428571 18.57142857142857 364.66857142857134 17.085714285714285Q367.71428571428567 15.600000000000001 371.1314285714285 15.600000000000001Q373.87999999999994 15.600000000000001 375.8114285714285 16.38Q377.7428571428571 17.159999999999997 379.0428571428571 18.2Q380.3428571428571 19.240000000000002 381.0114285714285 20.205714285714286L380.4171428571428 19.165714285714287Q380.3428571428571 17.38285714285714 381.6428571428571 16.454285714285714Q382.94285714285706 15.525714285714287 385.76571428571424 15.525714285714287Q388.43999999999994 15.525714285714287 389.59142857142854 16.34285714285714Q390.7428571428571 17.159999999999997 391.00285714285707 18.497142857142855Q391.26285714285706 19.834285714285713 391.26285714285706 21.32V46.94857142857143Q391.26285714285706 48.36 391.00285714285707 49.69714285714286Q390.7428571428571 51.034285714285716 389.59142857142854 51.81428571428572Q388.43999999999994 52.59428571428572 385.6914285714285 52.59428571428572ZM372.76571428571424 41.52571428571429Q374.6971428571428 41.52571428571429 376.29428571428565 40.52285714285714Q377.8914285714285 39.519999999999996 378.81999999999994 37.81142857142857Q379.7485714285714 36.10285714285715 379.7485714285714 34.02285714285714Q379.7485714285714 31.86857142857143 378.7828571428571 30.197142857142858Q377.8171428571428 28.525714285714287 376.1828571428571 27.52285714285714Q374.5485714285714 26.52 372.61714285714277 26.52Q370.4628571428571 26.52 368.7914285714285 27.56Q367.11999999999995 28.599999999999998 366.11714285714277 30.308571428571426Q365.11428571428564 32.01714285714286 365.11428571428564 34.17142857142857Q365.11428571428564 36.177142857142854 366.11714285714277 37.848571428571425Q367.11999999999995 39.519999999999996 368.86571428571426 40.52285714285714Q370.6114285714285 41.52571428571429 372.76571428571424 41.52571428571429Z"/><path d="M417.1142857142857 52.59428571428572Q413.47428571428566 52.59428571428572 410.6885714285714 51.07142857142857Q407.9028571428571 49.54857142857143 406.0828571428571 46.94857142857143Q404.2628571428571 44.34857142857143 403.33428571428567 41.00571428571429Q402.4057142857142 37.66285714285714 402.47999999999996 33.87428571428571Q402.47999999999996 30.234285714285715 403.44571428571425 26.89142857142857Q404.41142857142853 23.548571428571428 406.2314285714285 21.02285714285714Q408.0514285714285 18.497142857142855 410.7628571428571 17.048571428571428Q413.47428571428566 15.600000000000001 417.1142857142857 15.600000000000001Q420.3828571428571 15.600000000000001 423.4657142857143 17.085714285714285Q426.5485714285714 18.57142857142857 428.92571428571426 21.134285714285713Q431.30285714285714 23.697142857142858 432.6771428571428 27.002857142857142Q434.0514285714285 30.308571428571426 434.0514285714285 33.94857142857143Q434.0514285714285 37.73714285714286 432.6771428571428 41.11714285714285Q431.30285714285714 44.497142857142855 428.92571428571426 47.097142857142856Q426.5485714285714 49.69714285714286 423.5028571428571 51.14571428571429Q420.4571428571428 52.59428571428572 417.1142857142857 52.59428571428572ZM415.5542857142857 41.6Q417.6342857142857 41.6 419.26857142857136 40.597142857142856Q420.9028571428571 39.59428571428572 421.9057142857142 37.885714285714286Q422.9085714285714 36.177142857142854 422.9085714285714 34.097142857142856Q422.9085714285714 31.942857142857143 421.9428571428571 30.271428571428572Q420.97714285714284 28.599999999999998 419.34285714285716 27.634285714285713Q417.7085714285714 26.66857142857143 415.6285714285714 26.66857142857143Q413.62285714285713 26.66857142857143 411.95142857142855 27.634285714285713Q410.28 28.599999999999998 409.3514285714285 30.271428571428572Q408.4228571428571 31.942857142857143 408.4228571428571 34.097142857142856Q408.4228571428571 36.177142857142854 409.38857142857137 37.885714285714286Q410.3542857142857 39.59428571428572 411.9885714285714 40.597142857142856Q413.62285714285713 41.6 415.5542857142857 41.6ZM402.6285714285714 52.668571428571425Q399.9542857142857 52.668571428571425 398.76571428571424 51.85142857142857Q397.5771428571428 51.034285714285716 397.3171428571428 49.73428571428572Q397.0571428571428 48.434285714285714 397.0571428571428 47.02285714285714V4.308571428571426Q397.0571428571428 2.748571428571424 397.35428571428565 1.485714285714284Q397.65142857142854 0.2228571428571442 398.8028571428571 -0.5571428571428569Q399.9542857142857 -1.337142857142858 402.7028571428571 -1.337142857142858Q405.3771428571428 -1.337142857142858 406.4914285714285 -0.5199999999999996Q407.60571428571427 0.29714285714285893 407.8285714285714 1.597142857142856Q408.0514285714285 2.8971428571428532 407.97714285714284 4.308571428571426V49.325714285714284Q407.60571428571427 51.034285714285716 406.41714285714284 51.85142857142857Q405.2285714285714 52.668571428571425 402.6285714285714 52.668571428571425Z"/></g></g></svg>`;
const faviconSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><rect width="120" height="120" rx="24" fill="#1F6B4A"/><g transform="translate(6 10) scale(.9)"><g fill="#F2A93B"><circle cx="104" cy="18" r="10"/></g><g fill="#F5F7F2"><path d="M43 110c4-18 5-34 1-54h30c-4 20-3 36 1 54z"/></g><g fill="#F5F7F2"><circle cx="59" cy="44" r="26"/><circle cx="33" cy="54" r="17"/><circle cx="85" cy="54" r="17"/><circle cx="43" cy="30" r="15"/><circle cx="75" cy="30" r="15"/><circle cx="59" cy="22" r="13"/></g><g fill="#F2A93B"><circle cx="71" cy="40" r="3"/></g><g fill="#F5F7F2"><path d="M94 110c1.5-7 1.8-13 .7-20h8.6c-1.1 7-.8 13 .7 20z"/></g><g fill="#F5F7F2"><circle cx="99" cy="82" r="9.5"/><circle cx="91" cy="87" r="5.5"/><circle cx="107" cy="87" r="5.5"/></g><g fill="#F2A93B"><circle cx="103" cy="80" r="2"/></g></g></svg>`;
fs.writeFileSync(path.join(OUT, 'favicon.svg'), faviconSvg);

async function renderImages() {
  let chromium;
  try { chromium = require('playwright').chromium; } catch (e) { console.log('Playwright absent : favicons PNG et image de partage non générés (npm install playwright).'); return; }
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium', args: ['--no-sandbox'] });
  const page = await browser.newPage();
  for (const [name, size] of [['favicon-32.png', 32], ['apple-touch-icon.png', 180], ['icon-192.png', 192], ['icon-512.png', 512]]) {
    await page.setViewportSize({ width: size, height: size });
    await page.setContent(`<html><body style="margin:0;background:transparent">${faviconSvg.replace('<svg ', `<svg width="${size}" height="${size}" `)}</body></html>`);
    await page.screenshot({ path: path.join(OUT, name), omitBackground: true });
  }
  await page.setViewportSize({ width: 1200, height: 630 });
  await page.setContent(`<html><head><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fredoka:wght@600&family=Nunito+Sans:wght@600&display=swap"></head>
<body style="margin:0;width:1200px;height:630px;background:#1F6B4A;color:#fff;font-family:Fredoka,Arial,sans-serif;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 90px;box-sizing:border-box;position:relative;overflow:hidden">
  <div style="position:absolute;width:520px;height:520px;border-radius:50%;background:rgba(255,255,255,.06);right:-180px;top:-240px"></div>
  <div style="width:760px">${LOGO_WHITE}</div>
  <div style="font-size:34px;font-weight:500;color:#F2A93B;margin-top:8px">Des racines solides dès le premier jour.</div>
  <div style="width:260px;height:3px;background:#F2A93B;margin:26px auto"></div>
  <div style="font-size:44px;font-weight:600;line-height:1.1">Le trousseau de naissance sans stress,<br>livré chez vous.</div>
  <div style="font-family:'Nunito Sans',Arial,sans-serif;font-size:24px;font-weight:600;opacity:.85;margin-top:30px">Packs naissance · Valise de maternité · Livraison Abidjan en moins de 24 h</div>
</body></html>`);
  await page.waitForTimeout(800);
  await page.screenshot({ path: path.join(OUT, 'og-image.png') });
  await browser.close();
}

(async () => {
  const STATIC = path.join(__dirname, 'static');   // fichiers publiés tels quels à la racine : PNG déjà rendus (favicons, image de partage)
  if (fs.existsSync(STATIC)) fs.cpSync(STATIC, OUT, { recursive: true });
  await renderImages();
  try { fs.rmSync(path.join(__dirname, 'petit-baobab-site.zip'), { force: true }); execSync('zip -qr ../petit-baobab-site.zip .', { cwd: OUT }); } catch (e) { console.log('zip non créé :', e.message); }
  console.log('Pages : ' + written.join(', '));
  console.log('Fichiers : ' + fs.readdirSync(OUT).join(', '));
  console.log('Adresse du site utilisée : ' + SITE_URL);
})();
