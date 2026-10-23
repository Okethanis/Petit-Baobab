"""23 oct. 2026 — versions par couleur d'un même article.
   Un article peut porter `colors:[['Rose','images/x.webp'], ['Blanc','images/x-blanc.webp', 'note facultative'], …]`.
   La première couleur est celle de la vignette ; sur la fiche, des boutons de couleur changent la photo.
   La couleur choisie part dans le panier, le récapitulatif et le message WhatsApp : la clé du panier devient
   « id~Couleur » et byId() renvoie alors une copie de l'article nommée « Nom (Couleur) » avec la bonne photo.
   Idempotent : se relance sans rien dupliquer."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, '..', 'petit-baobab.html')
s = open(P, encoding='utf-8').read()

def rep(old, new, marker=None):
    """Remplace `old` (présent une seule fois) par `new`, sauf si `marker` (ou `new`) est déjà dans le fichier."""
    global s
    if (marker or new) in s: return
    assert s.count(old) == 1, ('introuvable ou multiple', old[:90])
    s = s.replace(old, new)

# 1) byId comprend « id~Couleur »
rep("function byId(id){ for (var i=0;i<PRODUCTS.length;i++){ if (PRODUCTS[i].id===id) return PRODUCTS[i]; } return null; }",
    "function byId(id){\n"
    "  var k = String(id), cut = k.indexOf('~'), base = cut > 0 ? k.slice(0, cut) : k, col = cut > 0 ? k.slice(cut + 1) : '';\n"
    "  for (var i=0;i<PRODUCTS.length;i++){ if (PRODUCTS[i].id===base){ var p = PRODUCTS[i]; if (!col) return p; var c = colorOf(p, col); if (!c) return p;\n"
    "    var v = Object.create(p); v.id = k; v.baseId = base; v.color = c[0]; v.name = p.name + ' (' + c[0] + ')'; if (c[1]) v.image = c[1]; return v; } }\n"
    "  return null;\n"
    "}\n"
    "/* Couleurs d'un article (brand/couleurs.py) */\n"
    "function colorOf(p, name){ var cs = (p && p.colors) || []; for (var j=0;j<cs.length;j++){ if (cs[j][0]===name) return cs[j]; } return null; }\n"
    "function colorKey(p){ return p.colors && p.colors.length && !p.baseId ? p.id + '~' + p.colors[0][0] : p.id; }\n"
    "function colorPicker(p, cur){\n"
    "  if (!cur) return '';\n"
    "  return '<div class=\"colors\"><div class=\"col-lab\">Couleur : <strong id=\"col-name\">' + esc(cur[0]) + '</strong></div><div class=\"col-chips\" role=\"group\" aria-label=\"Couleur\">' +\n"
    "    p.colors.map(function(c){ var on = c===cur; return '<button type=\"button\" class=\"col-chip' + (on ? ' on' : '') + '\" data-action=\"color\" data-id=\"' + p.id + '\" data-color=\"' + esc(c[0]) + '\" aria-pressed=\"' + (on ? 'true' : 'false') + '\"><img src=\"' + esc(img({image:c[1]})) + '\" alt=\"\" width=\"34\" height=\"34\"><span>' + esc(c[0]) + '</span></button>'; }).join('') +\n"
    "    '</div><p class=\"col-note\" id=\"col-note\"' + (cur[2] ? '' : ' hidden') + '>' + esc(cur[2]||'') + '</p></div>';\n"
    "}\n"
    "function pickColor(t){\n"
    "  var p = byId(t.getAttribute('data-id')), c = colorOf(p, t.getAttribute('data-color')); if (!c) return;\n"
    "  var im = $('#sheet .product .tile img'); if (im){ im.src = img({image:c[1]}); im.alt = p.name + ' (' + c[0] + ')'; }\n"
    "  $$('#sheet .col-chip').forEach(function(b){ var on = b===t; b.classList.toggle('on', on); b.setAttribute('aria-pressed', on ? 'true' : 'false'); });\n"
    "  var n = $('#col-name'); if (n) n.textContent = c[0];\n"
    "  var note = $('#col-note'); if (note){ note.textContent = c[2] || ''; note.hidden = !c[2]; }\n"
    "  var add = $('#sheet [data-action=\"add-sheet\"]'); if (add) add.setAttribute('data-id', p.id + '~' + c[0]);\n"
    "}",
    marker="function colorOf(p, name)")

# 2) ajout depuis une vignette : la couleur affichée (la première)
rep("function addToCart(id, qty, fromEl){ state.cart[id] =",
    "function addToCart(id, qty, fromEl){ var p0 = byId(id); if (p0 && !p0.baseId) id = colorKey(p0); state.cart[id] =",
    marker="var p0 = byId(id); if (p0 && !p0.baseId) id = colorKey(p0);")

# 3) fiche article : couleur choisie, photo de cette couleur, boutons
rep("function openProduct(id){\n  var p = byId(id); if (!p) return;\n",
    "function openProduct(id){\n  var p = byId(id); if (!p) return;\n"
    "  var pick = p.baseId ? p.color : null; if (p.baseId) p = byId(p.baseId);\n"
    "  var cur = p.colors && p.colors.length ? (colorOf(p, pick) || p.colors[0]) : null;\n",
    marker="var cur = p.colors && p.colors.length ?")
rep("openSheet('<div class=\"product\"><div class=\"tile\">' + (p.image ? '<img src=\"' + esc(img(p)) + '\"",
    "openSheet('<div class=\"product\"><div class=\"tile\">' + (p.image ? '<img src=\"' + esc(cur ? img({image:cur[1]}) : img(p)) + '\"",
    marker="esc(cur ? img({image:cur[1]}) : img(p))")
rep("(p.ref ? '<div class=\"ref\" style=\"margin-top:4px\">Référence ' + esc(p.ref) + '</div>' : '') +",
    "(p.ref ? '<div class=\"ref\" style=\"margin-top:4px\">Référence ' + esc(p.ref) + '</div>' : '') + colorPicker(p, cur) +")
rep("'<button type=\"button\" class=\"btn btn-primary\" data-action=\"add-sheet\" data-id=\"' + p.id + '\">'",
    "'<button type=\"button\" class=\"btn btn-primary\" data-action=\"add-sheet\" data-id=\"' + (cur ? p.id + '~' + cur[0] : p.id) + '\">'")

# 4) vignette : « 2 coloris »
rep("(p.ref ? '<span class=\"ref\">Réf. ' + esc(p.ref) + '</span>' : '') +\n    '<div class=\"card-foot\">",
    "(p.ref ? '<span class=\"ref\">Réf. ' + esc(p.ref) + '</span>' : '') + (p.colors && p.colors.length > 1 ? '<span class=\"ncol\">' + p.colors.length + ' coloris</span>' : '') +\n    '<div class=\"card-foot\">")

# 5) clic sur une couleur
rep("    case 'add-sheet':", "    case 'color': pickColor(t); break;\n    case 'add-sheet':", marker="case 'color': pickColor(t); break;")

# 6) styles
CSS = """
/* Couleurs d'un article (brand/couleurs.py) */
.colors{margin-top:14px}
.col-lab{font-size:.92rem;color:var(--muted)}
.col-lab strong{color:var(--ink)}
.col-chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
.col-chip{display:inline-flex;align-items:center;gap:8px;padding:3px 14px 3px 3px;border:1.5px solid var(--line);border-radius:999px;background:var(--surface);color:var(--ink);font:inherit;font-size:.92rem;cursor:pointer;transition:border-color .2s var(--ease),box-shadow .2s var(--ease)}
.col-chip img{width:34px;height:34px;border-radius:50%;object-fit:cover;background:#fff;display:block}
.col-chip:hover{border-color:var(--brand)}
.col-chip.on{border-color:var(--brand);box-shadow:0 0 0 2px var(--brand-soft);font-weight:700}
.col-note{margin:8px 0 0;font-size:.85rem;color:var(--muted);font-style:italic}
.ncol{display:block;font-size:.78rem;color:var(--brand);font-weight:600;margin-top:2px}
"""
if '/* Couleurs d\'un article (brand/couleurs.py) */\n.colors' not in s:
    i = s.index('</style>'); s = s[:i] + CSS + s[i:]

# 7) les articles et leurs couleurs (première = vignette)
COLORS = {
    'kdd185': [['Rose', 'images/kdd185.webp'], ['Blanc', 'images/kdd185-blanc.webp']],
    'c316a':  [['Bleu', 'images/c316a.webp'], ['Gris', 'images/c316a-gris.webp']],
    '608':    [['Rose', 'images/608.webp', 'Photo du fabricant : modèle très proche, montants légèrement différents.'], ['Gris', 'images/608-gris.webp']],
    '271':    [['Blanc', 'images/271.webp'], ['Gris', 'images/271-gris.webp']],
    'p3501':  [['Vert', 'images/p3501.webp'], ['Camel', 'images/p3501-camel.webp']],
    '2261':   [['Rayures bleues', 'images/2261.webp'], ['Rayures beiges', 'images/2261-beige.webp']],
    # doublons « même modèle, autre couleur » regroupés (brand/doublons.py, 23 oct. 2026)
    'p270': [['Blanc', 'images/p270.webp'], ['Bois naturel', 'images/270.webp']],
    'bjj-008p': [['Kaki', 'images/bjj-008p.webp'], ['Blanc', 'images/bjj008p.webp']],
    '08303': [['Gris', 'images/08303.webp'], ['Mauve', 'images/08305.webp']],
    '8207': [['Lamas', 'images/8207.webp'], ['Pingouins', 'images/8208.webp'], ['Gris rayé', 'images/8209.webp']],
    '8104': [['Gris clair', 'images/8104.webp'], ['Gris foncé', 'images/8105.webp'], ['Mauve', 'images/8106.webp']],
    '08112': [['Gris foncé', 'images/08112.webp'], ['Gris clair', 'images/08114.webp']],
    '8085': [['Gris', 'images/8085.webp'], ['Gris foncé', 'images/8087.webp'], ['Beige', 'images/08081.webp']],
    'f7025': [['Bleu', 'images/f7025.webp'], ['Rose', 'images/g7025.webp']],
    '668-34': [['Multicolore', 'images/668-34.webp'], ['Rose', 'images/668-35.webp']],
    '6037': [['Vert', 'images/6037.webp'], ['Rose', 'images/6033.webp']],
    'np-002': [['Bleu', 'images/np-002.webp'], ['Blanc', 'images/np-003.webp']],
}
def js(v):
    return '[' + ', '.join('[' + ', '.join("'" + x.replace("\\", "\\\\").replace("'", "\\'") + "'" for x in c) + ']' for c in v) + ']'
i0 = s.index('var PRODUCTS'); i1 = s.index('\n];', i0)
block = s[i0:i1]
for pid, cols in COLORS.items():
    m = re.search(r"^  \{id:'" + re.escape(pid) + r"',[^\n]*?\}(?=,?\n)", block, re.M)   # début de ligne : pas un {id:…, qty:…} de pack
    assert m, pid
    row = m.group(0)
    new = re.sub(r", colors:\[\[.*?\]\]", '', row)             # remplace une ancienne valeur
    new = new.replace("image:'images/" + pid + ".webp'", "image:'images/" + pid + ".webp', colors:" + js(cols), 1)
    assert 'colors:' in new, pid
    block = block.replace(row, new, 1)
s = s[:i0] + block + s[i1:]

open(P, 'w', encoding='utf-8').write(s)
print('couleurs : ' + ', '.join(COLORS))
