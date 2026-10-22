"""Carte « Myris » en 3D : met en place la mise en page de la carte, l'emplacement de la scène et le script (brand/wink3d.js, three.js servi depuis vendor/).
   Idempotent : relancer remplace le bloc existant."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, '..', 'petit-baobab.html'); s = open(p, encoding='utf-8').read()

# ---- 1. CSS de la carte (remplace l'ancien bloc .wink) ----
CSS = """/* Clin d'œil : chercher « Myris » dans la boutique ou la recherche du menu */
.wink{display:grid;grid-template-columns:minmax(220px,300px) 1fr;gap:22px;align-items:center;background:var(--brand-soft);border-radius:var(--radius);padding:20px 22px;color:var(--ink)}
.wink .wink-scene{position:relative;width:100%;aspect-ratio:400/284}
.wink .wink-scene svg.wink-mark{position:absolute;inset:8%;width:84%;height:84%;overflow:visible}
.wink .wink-scene canvas{display:block;width:100%;height:100%;touch-action:pan-y;cursor:pointer;-webkit-tap-highlight-color:transparent}
.wink .wink-scene.is3d svg{display:none}
.wink .wink-mark > g:nth-of-type(6),.wink .wink-mark > g:nth-of-type(7),.wink .wink-mark > g:nth-of-type(8){transform-origin:99px 110px;animation:wink-grow .9s var(--spring) .4s both}
.wink .wink-mark > g:nth-of-type(1){transform-origin:104px 18px;animation:lg-hop 1s var(--spring) 1.3s}
.wink .wink-mark > g:nth-of-type(4){transform-origin:59px 58px;animation:lg-sway 5s ease-in-out 1.4s infinite}
.wink h3{font-family:var(--font-display);font-size:2rem;color:var(--brand);margin:0 0 6px;line-height:1.1}
.wink p{margin:0;color:var(--muted);max-width:52ch}
.wink .wink-sign{margin-top:8px;font-weight:700;color:var(--brand)}
.wink.is3d h3{animation:wink-title 1s var(--spring) 3.3s both;transform-origin:50% 100%}
.wink.is3d p{animation:pb-fade .7s var(--ease) 3.9s both}
.wink.is3d .wink-sign{animation-delay:4.3s}
@keyframes wink-grow{from{transform:scale(0)}to{transform:scale(1)}}
@keyframes wink-title{from{opacity:0;transform:perspective(500px) rotateX(85deg) translateY(14px)}to{opacity:1;transform:none}}
@media (max-width:620px){.wink{grid-template-columns:1fr;text-align:center;justify-items:center}.wink p{max-width:none}.wink .wink-scene{max-width:360px}}
@media (prefers-reduced-motion: reduce){.wink .wink-mark > g,.wink h3,.wink p{animation:none !important}}
"""
s = re.sub(r"/\* Clin d'œil : chercher « Myris »[^\n]*\n(?:\.wink[^\n]*\n|@keyframes wink[^\n]*\n|@media \([^\n]*\{\.wink[^\n]*\n)+", lambda m: CSS, s, count=1)
assert s.count('.wink .wink-scene{position') == 1

# ---- 2. la carte : la scène a son emplacement ----
s = s.replace('<div class="wink" style="grid-column:1/-1"><svg class="mark wink-mark"', '<div class="wink" style="grid-column:1/-1"><div class="wink-scene"><svg class="mark wink-mark"', 1)
s = re.sub(r'(<svg class="mark wink-mark"[\s\S]*?</svg>)(?!</div>)', r'\1</div>', s, count=1)
assert s.count('<div class="wink-scene">') == 1 and s.count('</svg></div><div><h3>Myris</h3>') == 1

# ---- 3. le script, à la fin ----
js = open(os.path.join(HERE, 'wink3d.js'), encoding='utf-8').read().strip()
s = re.sub(r'<script id="pb-wink3d">[\s\S]*?</script>\n?', '', s)
assert s.rstrip().endswith('</script>')
s = s.rstrip() + '\n<script id="pb-wink3d">\n' + js + '\n</script>\n'
open(p, 'w', encoding='utf-8').write(s)

# ---- 4. build.js : copie de vendor/ et cache long ----
b = os.path.join(HERE, '..', 'build.js'); t = open(b, encoding='utf-8').read()
if 'VENDOR' not in t:
    old = "let written = [];"
    t = t.replace(old, "// Bibliothèques servies par le site lui-même (three.js pour la carte Myris) : dossier vendor/\nconst VENDOR = path.join(__dirname, 'vendor');\nif (fs.existsSync(VENDOR)) { fs.mkdirSync(path.join(OUT, 'vendor'), { recursive: true }); for (const f of fs.readdirSync(VENDOR)) fs.copyFileSync(path.join(VENDOR, f), path.join(OUT, 'vendor', f)); }\n" + old, 1)
    t = t.replace("/images/*\n  Cache-Control: public, max-age=31536000, immutable\n", "/images/*\n  Cache-Control: public, max-age=31536000, immutable\n\n/vendor/*\n  Cache-Control: public, max-age=31536000, immutable\n", 1)
    open(b, 'w', encoding='utf-8').write(t)
print('carte Myris en 3D en place')
