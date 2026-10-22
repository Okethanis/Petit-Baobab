"""Intègre le logo 3D (brand/hero3d.js + three.js servi depuis vendor/) dans petit-baobab.html. Idempotent : remplace le bloc s'il existe déjà."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, '..', 'petit-baobab.html'); s = open(p, encoding='utf-8').read()
js = open(os.path.join(HERE, 'hero3d.js'), encoding='utf-8').read().strip()
CSS = ".pb-logo.is3d .pb-scene{display:none}\n.pb-logo canvas.pb-3d{display:block;width:100%;max-width:100%;touch-action:pan-y;cursor:pointer;-webkit-tap-highlight-color:transparent}\n.hero-logo .pb-logo.is3d{--speed:1.1;width:min(80vw,300px)}\n"
block = '<script id="pb-hero3d">\n' + js + '\n</script>'
s = re.sub(r'<script id="pb-hero3d">[\s\S]*?</script>\n?', '', s)
s = re.sub(r'\.pb-logo\.is3d \.pb-scene\{display:none\}\n\.pb-logo canvas\.pb-3d\{[^\n]*\}\n\.hero-logo \.pb-logo\.is3d\{[^\n]*\}\n', '', s)
anchor = ".hero-logo .sign{display:none}\n"
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + CSS)
assert s.rstrip().endswith('</script>')
s = s.rstrip() + '\n' + block + '\n'
open(p, 'w', encoding='utf-8').write(s)
print('logo 3D en place (%d Ko de script)' % (len(js) // 1024))
