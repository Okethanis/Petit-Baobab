"""23 oct. 2026 — branche les images de packs (brand/packs-images.js) sur le site : champ image des 6 packs/valises,
   et une grande image en tête de chaque carte de pack. Idempotent."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, '..', 'petit-baobab.html')
s = open(P, encoding='utf-8').read()
for pid in ['pack-essentiel', 'pack-confort', 'pack-prestige', 'valise-bebe', 'valise-maman', 'valise-complete']:
    m = re.search(r"^(\s*\{id:'" + pid + r"',[^\n]*?)(\}),?$", s, re.M)
    assert m, pid
    line = m.group(0)
    if "image:'images/" + pid + ".webp'" in line: continue
    new = re.sub(r"\}(,?)$", ", image:'images/" + pid + ".webp'}\\1", line)
    s = s.replace(line, new, 1)
old = "  return '<article class=\"pack' + (p.featured ? ' featured' : '') + '\" style=\"--i:' + (i||0) + '\">' +\n"
new = old + "    (p.image ? '<button type=\"button\" class=\"pack-img\" data-action=\"open\" data-id=\"' + p.id + '\" aria-label=\"Voir le détail : ' + esc(p.name) + '\"><img src=\"' + esc(img(p)) + '\" alt=\"' + esc(p.name) + ' : les articles du pack\" loading=\"lazy\" width=\"1000\" height=\"1000\"></button>' : '') +\n"
if 'class="pack-img"' not in s:
    assert s.count(old) == 1; s = s.replace(old, new)
CSS = '/* Images des packs (brand/packs-site.py) */\n.pack-img{display:block;width:calc(100% + 2*var(--sp-4,24px));margin:calc(-1*var(--sp-4,24px)) calc(-1*var(--sp-4,24px)) 14px;padding:0;border:0;background:none;cursor:zoom-in;overflow:hidden;border-radius:var(--radius-lg,20px) var(--radius-lg,20px) 0 0}\n.pack-img img{display:block;width:100%;height:auto;aspect-ratio:1;object-fit:cover;transition:transform .5s var(--ease)}\n.pack-img:hover img{transform:scale(1.03)}\n'
if '/* Images des packs (brand/packs-site.py) */' not in s:
    i = s.index('</style>'); s = s[:i] + CSS + s[i:]
open(P, 'w', encoding='utf-8').write(s)
print('images des packs branchées')
