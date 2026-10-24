"""Univers : couleurs plus douces et accordées au vert de la marque (demande de Hanis, 24 oct. 2026 :
   « dans l'univers les couleurs sont trop fortes et il y a un décalage de couleur »).
   - Palette des 8 univers moins saturée (clair et sombre), contrastes texte ≥ 4,5:1.
   - Bandeau des pages univers : fond pastel (teinte légère de l'univers) et texte foncé, au lieu d'un aplat vif
     sous texte blanc ; encadrés blancs ; la couleur de l'univers ne sert plus qu'aux petits titres et au filet.
   - Cartes d'articles : filet du haut en teinte moyenne (fini l'arc-en-ciel vif dans la boutique).
   - Accueil : pastille du numéro en teinte légère.
   Aucune modification du JavaScript ni de build.js : la teinte est retrouvée à partir du style « --u-xxx » déjà posé.
   Idempotent."""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'petit-baobab.html')
s = open(P, encoding='utf-8').read()

OLD_L = '--u-dort:#2F4E8C; --u-balade:#1F6B4A; --u-voiture:#B5483A; --u-eveil:#C9711C; --u-mange:#8A5A2B; --u-soigne:#1F8A9C; --u-habille:#9A3B6E; --u-maison:#4B6355;'
OLD_D = '--u-dort:#5F7FC2; --u-balade:#4FA37F; --u-voiture:#D96F60; --u-eveil:#E6914A; --u-mange:#B98558; --u-soigne:#3EA7B8; --u-habille:#C45E95; --u-maison:#7D9A88;'

# couleur de l'univers (texte, filets) — clair puis sombre
LIGHT = {'dort': '#4A6488', 'balade': '#456F54', 'voiture': '#9A5245', 'eveil': '#8E5B22',
         'mange': '#85623F', 'soigne': '#356F75', 'habille': '#92566D', 'maison': '#5A6C60'}
DARK = {'dort': '#9AB0D0', 'balade': '#93BFA1', 'voiture': '#D99C8F', 'eveil': '#DDB070',
        'mange': '#C9A687', 'soigne': '#87BFC4', 'habille': '#CFA1B4', 'maison': '#A9BBAF'}

def h2r(h): h = h.lstrip('#'); return [int(h[i:i + 2], 16) for i in (0, 2, 4)]
def r2h(r): return '#%02X%02X%02X' % tuple(round(x) for x in r)
def mix(a, b, t): A, B = h2r(a), h2r(b); return r2h([A[i] * t + B[i] * (1 - t) for i in range(3)])
def lum(h):
    c = [x / 255 for x in h2r(h)]; c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
def contrast(a, b): la, lb = sorted([lum(a), lum(b)], reverse=True); return (la + 0.05) / (lb + 0.05)

def line(pal, base, soft, mid, glow):
    out = []
    for k, c in pal.items():
        so, mi = mix(c, base, soft), mix(c, base, mid)
        assert contrast(c, so) >= 4.5, (k, c, so, contrast(c, so))
        out.append('--u-%s:%s; --u-%s-soft:%s; --u-%s-mid:%s;' % (k, c, k, so, k, mi))
    return ' '.join(out) + ' --u-glow:%s;' % glow

NEW_L = line(LIGHT, '#FFFFFF', .11, .38, 'rgba(255,255,255,.5)')
NEW_D = line(DARK, '#1A2420', .14, .45, 'rgba(255,255,255,.03)')

if '--u-dort-soft' not in s:
    assert s.count(OLD_L) == 1 and s.count(OLD_D) == 2, 'variables des univers introuvables'
    s = s.replace(OLD_L, NEW_L).replace(OLD_D, NEW_D)

MARK = '/* Univers : couleurs douces (brand/univers-doux.py) */'
if MARK not in s:
    per = '\n'.join('[style*="--u-%s)"]{--ucs:var(--u-%s-soft);--ucm:var(--u-%s-mid)}' % (k, k, k) for k in LIGHT)
    CSS = '\n' + MARK + '\n' + per + """
.univ-hero{background:var(--ucs,var(--brand-soft));color:var(--ink);border-bottom:1px solid var(--line)}
.univ-hero::before{background:var(--u-glow)}
.univ-hero .kicker{color:var(--uc,var(--brand));border-bottom-color:currentColor}
.univ-hero h1,.univ-hero .view-title{color:var(--ink)}
.univ-hero .lead{color:var(--muted)}
.univ-hero .bignum{color:var(--uc,var(--brand));opacity:.1}
.univ-hero .crumbs a{color:var(--muted)}
.univ-hero .crumbs [aria-current]{color:var(--ink)}
.univ-hero .tip{background:var(--surface);border:1px solid var(--line)}
.univ-hero .tip .kicker{color:var(--uc,var(--brand))}
.univ-hero .tip p{color:var(--ink)}
.univ-hero .univ-cats .chip{border-color:var(--line);background:var(--surface);color:var(--ink)}
.univ-hero .univ-cats .chip:hover{border-color:var(--uc,var(--brand))}
.univ-hero .univ-cats .chip.active{background:var(--uc,var(--brand));border-color:var(--uc,var(--brand));color:var(--bg)}
.card{border-top:3px solid var(--ucm,var(--line))}
.univ-card .num{background:var(--ucs,var(--brand-soft));color:var(--uc,var(--brand))}
@media print{.univ-hero{background:#fff;color:#000}}
"""
    i = s.index('</style>'); s = s[:i] + CSS + s[i:]

open(P, 'w', encoding='utf-8').write(s)
print('univers doux : ok')
