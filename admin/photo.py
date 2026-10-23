"""Prépare la photo d'un article pour le site : carré 1000 × 1000 sur fond blanc, filigrane Petit Baobab, WebP.
   Garde aussi l'original sans filigrane et met à jour la vignette de la page Catalogue.
   Usage : python3 -I admin/photo.py <image source> <id de l'article>"""
import os, sys, io, json, base64
from PIL import Image, ImageOps, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
src, pid = sys.argv[1], sys.argv[2]
im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
im.thumbnail((1000, 1000), Image.LANCZOS)
sq = Image.new('RGB', (1000, 1000), (255, 255, 255)); sq.paste(im, ((1000 - im.width) // 2, (1000 - im.height) // 2))
os.makedirs(os.path.join(ROOT, 'images-sans-filigrane'), exist_ok=True)
sq.save(os.path.join(ROOT, 'images-sans-filigrane', pid + '.webp'), 'WEBP', quality=86, method=6)
# filigrane (mêmes réglages que le reste du catalogue)
WM = Image.open(os.path.join(HERE, 'wm', 'watermark.png')).convert('RGBA')
base = sq.convert('RGBA'); w, h = base.size
tw = min(max(70, int(w * 0.34)), int(w * 0.8)); th = int(WM.height * tw / WM.width)
wm = WM.resize((tw, th), Image.LANCZOS)
shadow = Image.new('RGBA', wm.size, (0, 0, 0, 0)); shadow.putalpha(wm.split()[3]); shadow = shadow.filter(ImageFilter.GaussianBlur(max(1, tw // 90)))
shadow.putalpha(shadow.split()[3].point(lambda a: int(a * 0.35))); wm.putalpha(wm.split()[3].point(lambda v: int(v * 0.66)))
pad = max(4, int(w * 0.025)); x, y = w - tw - pad, h - th - pad
base.alpha_composite(shadow, (x, y + max(1, tw // 120))); base.alpha_composite(wm, (x, y))
base.convert('RGB').save(os.path.join(ROOT, 'images', pid + '.webp'), 'WEBP', quality=84, method=6)
# vignette 80 px pour la page Catalogue
t = sq.copy(); t.thumbnail((80, 80), Image.LANCZOS); buf = io.BytesIO(); t.save(buf, 'WEBP', quality=70)
tp = os.path.join(HERE, 'thumbs.json'); thumbs = json.load(open(tp, encoding='utf-8'))
thumbs[pid] = 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()
json.dump(thumbs, open(tp, 'w', encoding='utf-8'), separators=(',', ':'))
print('images/' + pid + '.webp')
