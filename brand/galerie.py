"""23 oct. 2026 — galerie de photos sur la fiche article (jusqu'à 8 depuis le 24 oct.).
   Les photos supplémentaires sont préparées par Netlify (admin/photos-fetch.js) : images/<id>-2.webp … -8,
   et listées dans images/galerie.json ({ "<id>": ["<id>.webp", "<id>-2.webp", …] }), lu par la page au chargement.
   Sous la grande photo : des vignettes ; un clic change la grande photo. Compatible avec les couleurs (brand/couleurs.py).
   Idempotent."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, '..', 'petit-baobab.html')
s = open(P, encoding='utf-8').read()

def rep(old, new, marker=None):
    global s
    if (marker or new) in s: return
    assert s.count(old) == 1, ('introuvable ou multiple', old[:90])
    s = s.replace(old, new)

# 1) chargement de la liste des photos + vignettes
rep("function colorKey(p){",
    "/* Galerie de photos d'un article (brand/galerie.py) */\n"
    "var GALERIE = {};\n"
    "setTimeout(function(){ try { fetch(img({image:'images/galerie.json'}), {cache:'no-cache'}).then(function(r){ return r.ok ? r.json() : {}; }).then(function(j){ GALERIE = j || {}; }).catch(function(){}); } catch(e){} }, 0);\n"
    "function galleryStrip(p, cur){\n"
    "  var extra = (GALERIE[p.id] || []).filter(function(f){ return f !== p.id + '.webp'; });\n"
    "  if (!extra.length) return '';\n"
    "  var list = [cur ? cur[1] : p.image].concat(extra.map(function(f){ return 'images/' + f; }));\n"
    "  return '<div class=\"gal\" role=\"group\" aria-label=\"Photos de l\\'article\">' + list.map(function(src, i){ return '<button type=\"button\" class=\"gal-t' + (i ? '' : ' on') + '\" data-action=\"gal\" data-src=\"' + esc(img({image:src})) + '\" aria-label=\"Photo ' + (i+1) + '\"><img src=\"' + esc(img({image:src})) + '\" alt=\"\" loading=\"lazy\" onerror=\"this.parentNode.remove()\"></button>'; }).join('') + '</div>';\n"
    "}\n"
    "function pickPhoto(t){\n"
    "  var im = $('#sheet .product .tile img'); if (im) im.src = t.getAttribute('data-src');\n"
    "  $$('#sheet .gal-t').forEach(function(b){ b.classList.toggle('on', b===t); });\n"
    "}\n"
    "function colorKey(p){",
    marker="function galleryStrip(p, cur)")

# 2) la fiche : la grande photo + les vignettes dans la même colonne
rep("openSheet('<div class=\"product\"><div class=\"tile\">' + (p.image ?",
    "openSheet('<div class=\"product\"><div class=\"pgal\"><div class=\"tile\">' + (p.image ?")
rep("'>' : icon(c.icon)) + '</div>' +\n    '<div><div class=\"crumbs\">'",
    "'>' : icon(c.icon)) + '</div>' + galleryStrip(p, cur) + '</div>' +\n    '<div><div class=\"crumbs\">'",
    marker="galleryStrip(p, cur) + '</div>' +")

# 3) changer de couleur remet la 1re vignette sur la photo de cette couleur
rep("  var im = $('#sheet .product .tile img'); if (im){ im.src = img({image:c[1]}); im.alt = p.name + ' (' + c[0] + ')'; }\n",
    "  var im = $('#sheet .product .tile img'); if (im){ im.src = img({image:c[1]}); im.alt = p.name + ' (' + c[0] + ')'; }\n"
    "  var g0 = $('#sheet .gal-t'); if (g0){ g0.setAttribute('data-src', img({image:c[1]})); $('img', g0).src = img({image:c[1]}); $$('#sheet .gal-t').forEach(function(b){ b.classList.toggle('on', b===g0); }); }\n",
    marker="var g0 = $('#sheet .gal-t');")

# 4) clic sur une vignette
rep("    case 'color': pickColor(t); break;\n", "    case 'color': pickColor(t); break;\n    case 'gal': pickPhoto(t); break;\n", marker="case 'gal': pickPhoto(t); break;")

# 5) styles
CSS = """
/* Galerie de photos d'un article (brand/galerie.py) */
.pgal{min-width:0}
.gal{display:flex;gap:8px;margin-top:10px;overflow-x:auto;padding-bottom:2px}
.gal-t{flex:0 0 auto;width:62px;height:62px;padding:0;border:1.5px solid var(--line);border-radius:10px;background:#fff;cursor:pointer;overflow:hidden;transition:border-color .2s var(--ease)}
.gal-t img{width:100%;height:100%;object-fit:contain;display:block}
.gal-t.on{border-color:var(--brand);box-shadow:0 0 0 2px var(--brand-soft)}
"""
if "/* Galerie de photos d'un article (brand/galerie.py) */\n.pgal" not in s:
    i = s.index('</style>'); s = s[:i] + CSS + s[i:]

open(P, 'w', encoding='utf-8').write(s)
print('galerie ok')
