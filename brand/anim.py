"""Motion design du logo : « de la graine au baobab ».
   Séquence : l'horizon se trace, une graine tombe et s'enfonce, les racines poussent, une pousse sort de terre,
   elle devient le tronc, les feuillages s'ouvrent, le soleil se lève, un fruit tombe et donne le petit baobab,
   le nom s'écrit lettre par lettre, puis la signature. Ensuite les feuillages se balancent et le soleil pulse.
   Produit : brand/anim.css, brand/scene.html (le SVG), brand/out/logo-anime.html, la page de rendu locale,
   et remplace le bloc « Logo animé » de petit-baobab.html."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
mark = json.load(open(os.path.join(HERE, 'mark.json'), encoding='utf-8'))['mark']

# ---------- la scène SVG (400 × 400) ----------
M = 'translate(200 270) scale(2) translate(-60 -110)'   # repère du logo : base du tronc en (198,270)
def part(cls):
    m = re.search(r'<g class="%s">(.*?)</g>' % cls, mark)
    return m.group(1)
def nth(cls, n):   # n-ième groupe de cette classe (grand = 1, petit = 2)
    return re.findall(r'<g class="%s">(.*?)</g>' % cls, mark)[n - 1]
SCENE = f'''<svg viewBox="0 0 400 284" class="pb-scene" aria-hidden="true" focusable="false">
  <defs><clipPath id="pb-sky"><rect x="0" y="0" width="400" height="270"/></clipPath></defs>
  <line class="horizon" x1="48" y1="270" x2="352" y2="270"/>
  <g class="plx-sun" clip-path="url(#pb-sky)"><g transform="{M}"><g class="sun lg-sun"><circle class="halo" cx="104" cy="18" r="19"/>{part('lg-sun')}</g></g></g>
  <g class="plx-tree"><g transform="{M}" class="tree">
    <g class="trunk-big lg-trunk">{nth('lg-trunk', 1)}</g>
    <g class="canopy-big lg-tree">{nth('lg-tree', 1)}</g>
    <g class="fruit-big lg-fruit">{nth('lg-fruit', 1)}</g>
    <g class="fruit-fall lg-fruit"><circle cx="71" cy="40" r="3"/></g>
    <g class="trunk-small lg-trunk">{nth('lg-trunk', 2)}</g>
    <g class="canopy-small lg-tree">{nth('lg-tree', 2)}</g>
    <g class="fruit-small lg-fruit">{nth('lg-fruit', 2)}</g>
  </g></g>
  <g class="sprout" fill="none" stroke-linecap="round"><path class="stem" d="M198 270V230"/><ellipse class="leaf l1" cx="189" cy="234" rx="8" ry="4" transform="rotate(-28 189 234)"/><ellipse class="leaf l2" cx="207" cy="234" rx="8" ry="4" transform="rotate(28 207 234)"/></g>
  <ellipse class="seed" cx="198" cy="267" rx="5.5" ry="3.8"/>
</svg>'''
LETTERS = ''.join('<span style="--i:%d">%s</span>' % (i, '&nbsp;' if ch == ' ' else ch) for i, ch in enumerate('Petit Baobab'))

# ---------- le CSS (toutes les durées × --speed) ----------
def t(x): return 'calc(%ss * var(--speed))' % x
CSS = f'''/* ===== Logo animé « de la graine au baobab » : voir brand/anim.py ===== */
.pb-logo{{--speed:1;display:grid;justify-items:center;gap:10px;color:#F5F7F2}}
.pb-logo .pb-scene{{width:100%;height:auto;overflow:visible;display:block}}
.pb-logo .pb-scene .lg-sun,.pb-logo .pb-scene .lg-fruit{{fill:var(--accent)}}
.pb-logo .pb-scene .lg-trunk,.pb-logo .pb-scene .lg-tree{{fill:#F5F7F2}}
.pb-logo .horizon{{stroke:rgba(245,247,242,.55);stroke-width:2;stroke-linecap:round;transform-box:fill-box;transform-origin:50% 50%;animation:pb-hline {t(.7)} var(--ease) both}}
.pb-logo .seed{{fill:var(--accent);opacity:0;transform:scale(.6);transform-box:fill-box;transform-origin:50% 50%;animation:pb-seed {t(1)} var(--ease) {t(.3)} both,pb-seedrest {t(.5)} var(--ease) {t(1.9)} forwards}}
.pb-logo .sprout{{stroke:#F5F7F2}}
.pb-logo .stem{{stroke-width:3.2;opacity:0;transform-box:fill-box;transform-origin:50% 100%;animation:pb-stem {t(.5)} var(--ease) {t(1.5)} both,pb-vanish {t(.3)} ease {t(2.25)} forwards}}
.pb-logo .leaf{{fill:#F5F7F2;stroke:none;opacity:0;transform-box:fill-box;transform-origin:50% 50%;animation:pb-leaf {t(.4)} var(--spring) {t(1.95)} both,pb-vanish {t(.3)} ease {t(2.35)} forwards}}
.pb-logo .leaf.l2{{animation-delay:{t(2.02)},{t(2.35)}}}
.pb-logo .trunk-big{{transform-box:fill-box;transform-origin:50% 100%;animation:pb-grow {t(.9)} var(--spring) {t(2.1)} both}}
.pb-logo .canopy-big{{transform-box:fill-box;transform-origin:50% 76%;animation:pb-sway {t(7)} ease-in-out {t(6)} infinite}}
.pb-logo .canopy-big circle,.pb-logo .canopy-small circle,.pb-logo .fruit-big circle,.pb-logo .fruit-small circle{{transform-box:fill-box;transform-origin:50% 50%;animation:pb-pop {t(.5)} var(--spring) both}}
.pb-logo .canopy-big circle:nth-child(1){{animation-delay:{t(2.55)}}} .pb-logo .canopy-big circle:nth-child(2){{animation-delay:{t(2.63)}}}
.pb-logo .canopy-big circle:nth-child(3){{animation-delay:{t(2.7)}}} .pb-logo .canopy-big circle:nth-child(4){{animation-delay:{t(2.78)}}}
.pb-logo .canopy-big circle:nth-child(5){{animation-delay:{t(2.85)}}} .pb-logo .canopy-big circle:nth-child(6){{animation-delay:{t(2.93)}}}
.pb-logo .halo{{opacity:.16}}
.pb-logo .sun{{transform-box:fill-box;transform-origin:50% 50%;animation:pb-rise {t(.9)} var(--ease) {t(2.4)} both,pb-glow {t(4)} ease-in-out {t(4.5)} infinite}}
.pb-logo .fruit-big circle{{animation-delay:{t(3.15)}}}
.pb-logo .fruit-fall circle{{opacity:0;transform-box:fill-box;transform-origin:50% 50%;animation:pb-fall {t(1.1)} var(--ease) {t(3.4)} both}}
.pb-logo .trunk-small{{transform-box:fill-box;transform-origin:50% 100%;animation:pb-grow {t(.5)} var(--spring) {t(4.4)} both}}
.pb-logo .canopy-small{{transform-box:fill-box;transform-origin:50% 87%;animation:pb-sway {t(5)} ease-in-out {t(6.2)} infinite reverse}}
.pb-logo .canopy-small circle:nth-child(1){{animation-delay:{t(4.75)}}} .pb-logo .canopy-small circle:nth-child(2){{animation-delay:{t(4.83)}}} .pb-logo .canopy-small circle:nth-child(3){{animation-delay:{t(4.9)}}}
.pb-logo .fruit-small circle{{animation-delay:{t(5.05)}}}
.pb-logo .plx-sun{{transform:translate(calc(var(--px,0)*10px),calc(var(--py,0)*6px));transition:transform .35s var(--ease)}}
.pb-logo .plx-tree{{transform:translate(calc(var(--px,0)*4px),calc(var(--py,0)*2px));transition:transform .35s var(--ease)}}
.pb-logo .word{{font-family:var(--font-display);font-weight:600;line-height:1;letter-spacing:-.01em;display:flex}}
.pb-logo .word span{{display:inline-block;animation:pb-letter {t(.5)} var(--ease) both;animation-delay:calc((4.9s + var(--i) * .06s) * var(--speed))}}
.pb-logo .sign{{font-family:var(--font-body);font-weight:600;color:var(--accent);animation:pb-fade {t(.7)} var(--ease) {t(5.8)} both}}
@keyframes pb-fade{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes pb-hline{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
@keyframes pb-seed{{0%{{transform:translateY(-230px) scale(.9);opacity:0}}12%{{opacity:1}}68%{{transform:translateY(0) scale(1)}}78%{{transform:translateY(-9px) scale(1)}}88%{{transform:translateY(0) scale(1.2,.8)}}100%{{transform:none;opacity:1}}}}
@keyframes pb-seedrest{{from{{transform:none;opacity:1}}to{{transform:scale(.6);opacity:0}}}}
@keyframes pb-stem{{from{{transform:scaleY(0);opacity:1}}to{{transform:scaleY(1);opacity:1}}}}
@keyframes pb-leaf{{from{{transform:scale(0);opacity:1}}to{{transform:scale(1);opacity:1}}}}
@keyframes pb-vanish{{from{{opacity:1}}to{{opacity:0}}}}
@keyframes pb-grow{{from{{transform:scaleY(0)}}to{{transform:scaleY(1)}}}}
@keyframes pb-pop{{from{{transform:scale(0)}}to{{transform:scale(1)}}}}
@keyframes pb-rise{{from{{transform:translateY(118px)}}to{{transform:translateY(0)}}}}
@keyframes pb-glow{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.09)}}}}
@keyframes pb-fall{{0%{{transform:translate(0,0) scale(0);opacity:1}}14%{{transform:translate(0,0) scale(1);opacity:1}}58%{{transform:translate(28px,70px) scale(1);opacity:1}}70%{{transform:translate(28px,61px) scale(1);opacity:1}}82%{{transform:translate(28px,70px) scale(1.25,.75);opacity:1}}92%{{transform:translate(28px,70px) scale(1);opacity:1}}100%{{transform:translate(28px,70px) scale(1);opacity:0}}}}
@keyframes pb-sway{{0%,100%{{transform:rotate(-1.4deg)}}50%{{transform:rotate(1.4deg)}}}}
@keyframes pb-letter{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:none}}}}
@media (prefers-reduced-motion: reduce){{.pb-logo *{{animation:none !important}}}}
'''
open(os.path.join(HERE, 'anim.css'), 'w', encoding='utf-8').write(CSS)
open(os.path.join(HERE, 'scene.html'), 'w', encoding='utf-8').write(SCENE)

# ---------- page autonome (kit) ----------
def page(fonts_head):
    return f'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Petit Baobab · logo animé</title>
{fonts_head}
<style>
:root{{--accent:#F2A93B;--font-display:"Fredoka","Trebuchet MS",system-ui,sans-serif;--font-body:"Nunito Sans",system-ui,sans-serif;--ease:cubic-bezier(.2,.7,.2,1);--spring:cubic-bezier(.3,1.4,.4,1)}}
html,body{{margin:0;height:100%}}
body{{background:#174F38;display:grid;place-items:center}}
body.transparent{{background:transparent}}
body.clair{{background:#F5F7F2}}
body.clair .pb-logo{{color:#1F6B4A}} body.clair .pb-logo .pb-scene .lg-tree{{fill:#1F6B4A}} body.clair .pb-logo .pb-scene .lg-trunk{{fill:#174F38}}
body.clair .pb-logo .sprout,body.clair .pb-logo .leaf{{stroke:#1F6B4A;fill:#1F6B4A}} body.clair .pb-logo .soil{{fill:#E1EFE5}} body.clair .pb-logo .horizon{{stroke:#1F6B4A}} body.clair .pb-logo .roots path{{stroke:rgba(31,107,74,.45)}}
{CSS}
.pb-logo{{width:min(78vmin,900px);gap:min(1.6vmin,18px)}}
.pb-logo .pb-scene{{width:min(64vmin,740px)}}
.pb-logo .word{{font-size:min(10vmin,112px)}}
.pb-logo .sign{{font-size:min(3vmin,32px)}}
</style></head>
<body>
<div class="pb-logo" aria-label="Petit Baobab">{SCENE}<div class="word">{LETTERS}</div><div class="sign">Des racines solides dès le premier jour.</div></div>
<script>
/* ?fond=clair | transparent  ·  ?boucle=1 rejoue toutes les 9 s  ·  ?vitesse=1.3 pour aller plus vite */
var q = new URLSearchParams(location.search);
if (q.get('fond')) document.body.className = q.get('fond');
if (q.get('vitesse')) document.querySelector('.pb-logo').style.setProperty('--speed', 1 / parseFloat(q.get('vitesse')));
if (q.get('boucle')) setInterval(function(){{ var el = document.querySelector('.pb-logo'); el.replaceWith(el.cloneNode(true)); }}, 9000);
</script>
</body></html>
'''
GOOGLE = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fredoka:wght@600&family=Nunito+Sans:wght@600&display=swap">'
WM = '/tmp/claude-0/-home-claude/9f9cc82f-2878-57d7-9213-8fd04fffba95/scratchpad/wm'
LOCAL = ('<style>@font-face{font-family:"Fredoka";src:url("file://%s/package/files/fredoka-latin-600-normal.woff2") format("woff2");font-weight:600}'
         '@font-face{font-family:"Nunito Sans";src:url("file://%s/nunito/package/files/nunito-sans-latin-600-normal.woff2") format("woff2");font-weight:600}</style>') % (WM, WM)
open(os.path.join(HERE, 'out', 'logo-anime.html'), 'w', encoding='utf-8').write(page(GOOGLE))
open(os.path.join(WM, 'logo-anime-local.html'), 'w', encoding='utf-8').write(page(LOCAL))

# ---------- intégration au site ----------
p = os.path.join(HERE, '..', 'petit-baobab.html'); s = open(p, encoding='utf-8').read()
start = s.index('/* ===== Logo animé'); end = s.index('.hero-copy > *{animation:rise', start)
site_css = CSS + '''.hero-logo{display:grid;justify-items:center;gap:6px}
.hero-logo .pb-logo{--speed:.72;width:clamp(170px,30vw,250px);gap:6px}
.hero-logo .word{font-size:clamp(1.5rem,3.6vw,2.1rem)}
.hero-logo .sign{display:none}
'''
s = s[:start] + site_css + s[end:]
h0 = s.index('<div class="hero-logo" aria-hidden="true">'); h1 = s.index('<h1 class="plum-title hero-title">', h0)
s = s[:h0] + '<div class="hero-logo" aria-hidden="true"><div class="pb-logo">' + SCENE + '<div class="word">' + LETTERS + '</div></div></div>\n        ' + s[h1:]
# le texte du héros apparaît tout de suite, l'animation du logo joue au-dessus
s = s.replace(".hero-copy > :nth-child(2){animation-delay:2.05s}\n.hero-copy > :nth-child(3){animation-delay:2.15s}\n.hero-copy > :nth-child(4){animation-delay:2.25s}",
              ".hero-copy > :nth-child(2){animation-delay:.08s}\n.hero-copy > :nth-child(3){animation-delay:.18s}\n.hero-copy > :nth-child(4){animation-delay:.28s}")
open(p, 'w', encoding='utf-8').write(s)
print('anim.css, scene.html, logo-anime.html et petit-baobab.html mis à jour')
