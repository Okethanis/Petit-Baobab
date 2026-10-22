"""Logo Petit Baobab : une seule définition vectorielle, toutes les déclinaisons en sortent.
   Marque = grand baobab + petit baobab + soleil + sol. Mot-symbole = « Petit Baobab » en Fredoka 600 converti en tracés.
   Usage : python3 brand/logo.py  → brand/out/*.svg (+ brand/mark.json pour le site)"""
import os, json
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
FONT = '/tmp/claude-0/-home-claude/9f9cc82f-2878-57d7-9213-8fd04fffba95/scratchpad/wm/fredoka-600.ttf'

# Couleurs de la marque
C = {'brand': '#1F6B4A', 'deep': '#174F38', 'accent': '#F2A93B', 'soft': '#E1EFE5', 'cream': '#F5F7F2', 'ink': '#1E2B22'}

# ---- la marque (viewBox 0 0 120 120) : chaque élément porte une classe pour être recoloré en CSS ----
MARK_PARTS = [
  ('sun',    '<circle cx="104" cy="18" r="10"/>'),
  ('ground', '<ellipse cx="60" cy="110" rx="56" ry="5"/>'),
  ('trunk',  '<path d="M43 110c4-18 5-34 1-54h30c-4 20-3 36 1 54z"/>'),
  ('tree',   '<circle cx="59" cy="44" r="26"/><circle cx="33" cy="54" r="17"/><circle cx="85" cy="54" r="17"/><circle cx="43" cy="30" r="15"/><circle cx="75" cy="30" r="15"/><circle cx="59" cy="22" r="13"/>'),
  ('fruit',  '<circle cx="71" cy="40" r="3"/>'),
  ('trunk',  '<path d="M94 110c1.5-7 1.8-13 .7-20h8.6c-1.1 7-.8 13 .7 20z"/>'),
  ('tree',   '<circle cx="99" cy="82" r="9.5"/><circle cx="91" cy="87" r="5.5"/><circle cx="107" cy="87" r="5.5"/>'),
  ('fruit',  '<circle cx="103" cy="80" r="2"/>'),
]
PALETTES = {
  'color': {'sun': C['accent'], 'ground': C['soft'], 'trunk': C['deep'], 'tree': C['brand'], 'fruit': C['accent']},
  'white': {'sun': C['accent'], 'ground': 'rgba(255,255,255,.22)', 'trunk': C['cream'], 'tree': C['cream'], 'fruit': C['accent']},
  'mono-white': {'sun': C['cream'], 'ground': 'rgba(255,255,255,.22)', 'trunk': C['cream'], 'tree': C['cream'], 'fruit': C['cream']},
  'green': {'sun': C['brand'], 'ground': C['soft'], 'trunk': C['brand'], 'tree': C['brand'], 'fruit': C['cream']},
  'black': {'sun': C['ink'], 'ground': 'rgba(0,0,0,.12)', 'trunk': C['ink'], 'tree': C['ink'], 'fruit': '#FFFFFF'},
}
def mark_inner(pal, ground=True):
  return ''.join('<g fill="%s">%s</g>' % (pal[k], svg) for k, svg in MARK_PARTS if ground or k != 'ground')
def mark_svg(pal, ground=True, size=None):
  attrs = ' width="%d" height="%d"' % (size, size) if size else ''
  return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"%s>%s</svg>' % (attrs, mark_inner(pal, ground))
def mark_classed():
  """Version pour le site : classes CSS au lieu de couleurs (lg-sun, lg-ground, lg-trunk, lg-tree, lg-fruit)."""
  return ''.join('<g class="lg-%s">%s</g>' % (k, svg) for k, svg in MARK_PARTS)

# ---- le mot-symbole en tracés ----
font = TTFont(FONT)
glyph_set = font.getGlyphSet(); cmap = font.getBestCmap(); upem = font['head'].unitsPerEm
cap = font['OS/2'].sCapHeight or 700
def word_paths(text, scale, x0=0.0, y0=0.0):
  """Tracés SVG du texte, ligne de base en y0, hauteur de capitale = cap*scale."""
  out, x = [], x0
  for ch in text:
    gname = cmap.get(ord(ch)); g = glyph_set[gname]
    pen = SVGPathPen(glyph_set)
    g.draw(TransformPen(pen, (scale, 0, 0, -scale, x, y0)))
    d = pen.getCommands()
    if d: out.append('<path d="%s"/>' % d)
    x += g.width * scale
  return ''.join(out), x - x0
def wordmark(color, cap_h):
  scale = cap_h / cap
  d, w = word_paths('Petit Baobab', scale, 0, cap_h)
  return '<g fill="%s">%s</g>' % (color, d), w, cap_h * (1 + 0.22)   # descente des lettres (p, b) ≈ 22 % de la capitale

# ---- compositions ----
def horizontal(pal, text_color, pad=0):
  cap_h = 52.0; gap = 16.0
  wm, w, h_txt = wordmark(text_color, cap_h)
  W = 120 + gap + w + 2 * pad; H = 120 + 2 * pad
  y_text = pad + 60 - cap_h / 2 + 4          # centre optique sur la marque
  return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.1f %.1f"><g transform="translate(%d %d)">%s</g><g transform="translate(%.1f %.1f)">%s</g></svg>' % (W, H, pad, pad, mark_inner(pal), pad + 120 + gap, y_text, wm), W, H
def stacked(pal, text_color, pad=0):
  cap_h = 34.0; gap = 14.0
  wm, w, h_txt = wordmark(text_color, cap_h)
  W = max(120, w) + 2 * pad; H = 120 + gap + h_txt + 2 * pad
  return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.1f %.1f"><g transform="translate(%.1f %d)">%s</g><g transform="translate(%.1f %.1f)">%s</g></svg>' % (W, H, (W - 120) / 2, pad, mark_inner(pal), (W - w) / 2, pad + 120 + gap, wm), W, H
def app_icon(bg=C['brand'], pal=None):
  pal = pal or PALETTES['white']
  return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><rect width="120" height="120" rx="27" fill="%s"/><g transform="translate(8 8) scale(.87)">%s</g></svg>' % (bg, mark_inner(pal, ground=False))
def favicon():
  pal = PALETTES['white']
  return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><rect width="120" height="120" rx="24" fill="%s"/><g transform="translate(6 10) scale(.9)">%s</g></svg>' % (C['brand'], mark_inner(pal, ground=False))

files = {}
for name, pal in PALETTES.items():
  files['marque-%s.svg' % name] = mark_svg(pal)
  files['marque-%s-sans-sol.svg' % name] = mark_svg(pal, ground=False)
text_colors = {'color': C['brand'], 'white': C['cream'], 'mono-white': C['cream'], 'green': C['brand'], 'black': C['ink']}
dims = {}
for name in PALETTES:
  svg, W, H = horizontal(PALETTES[name], text_colors[name]); files['logo-horizontal-%s.svg' % name] = svg; dims['horizontal'] = (W, H)
  svg, W, H = stacked(PALETTES[name], text_colors[name]); files['logo-empile-%s.svg' % name] = svg; dims['empile'] = (W, H)
files['icone-app.svg'] = app_icon()
files['icone-app-creme.svg'] = app_icon(bg=C['cream'], pal=PALETTES['color'])
files['favicon.svg'] = favicon()
for n, s in files.items():
  open(os.path.join(OUT, n), 'w', encoding='utf-8').write(s)
# pour le site : marque avec classes, mot-symbole en tracés (couleur via CSS), favicon et icône
wm_site, w_site, _ = wordmark('currentColor', 52.0)
json.dump({'mark': mark_classed(), 'wordmark': wm_site, 'wordmark_width': w_site, 'favicon': files['favicon.svg'], 'icon': files['icone-app.svg'], 'dims': dims},
          open(os.path.join(HERE, 'mark.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print(len(files), 'fichiers SVG ;', 'horizontal %.0f×%.0f, empilé %.0f×%.0f' % (dims['horizontal'] + dims['empile']))
