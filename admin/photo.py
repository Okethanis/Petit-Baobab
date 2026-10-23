"""Prépare la photo d'un article pour le site : carré 1000 × 1000 sur fond blanc, filigrane Petit Baobab, WebP.
   Rogne d'abord les marges blanches unies (l'article remplit le cadre, avec une marge régulière) ;
   une photo d'ambiance (pièce, décor) n'est pas rognée puisque ses bords ne sont pas blancs.
   Usage :
     python3 -I admin/photo.py <image source> <id de l'article>              → remplace images/<id>.webp (+ original sans filigrane, vignette Catalogue)
     python3 -I admin/photo.py <image source> <id de l'article> --propose DIR → écrit seulement DIR/<id>.webp (proposition à valider, le site n'est pas touché)"""
import os, sys, io, json, base64
from PIL import Image, ImageOps, ImageFilter, ImageChops
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
args = sys.argv[1:]
propose = None
if '--propose' in args:
    k = args.index('--propose'); propose = args[k + 1]; del args[k:k + 2]
src, pid = args[0], args[1]

im = ImageOps.exif_transpose(Image.open(src))
if im.mode in ('RGBA', 'LA', 'P'):                       # transparence → fond blanc
    im = im.convert('RGBA'); bg = Image.new('RGBA', im.size, (255, 255, 255, 255)); bg.alpha_composite(im); im = bg
im = im.convert('RGB')

def trim_white(img, tol=18):
    """Rogne les bords blancs/presque blancs unis ; ne fait rien si le bord n'est pas blanc."""
    corners = [img.getpixel(p) for p in ((0, 0), (img.width - 1, 0), (0, img.height - 1), (img.width - 1, img.height - 1))]
    if min(min(c) for c in corners) < 235: return img      # fond pas blanc (photo d'ambiance) : on garde tel quel
    diff = ImageChops.difference(img, Image.new('RGB', img.size, (255, 255, 255))).convert('L')
    box = diff.point(lambda v: 255 if v > tol else 0).getbbox()
    return img.crop(box) if box else img

im = trim_white(im)
FILL = 0.90 if im.getpixel((0, 0))[0] >= 235 else 1.0     # marge blanche régulière autour d'un détourage
side = 1000; inner = int(side * FILL)
im.thumbnail((inner, inner), Image.LANCZOS) if max(im.size) > inner else None
if max(im.size) < inner:                                  # petite source : agrandir un peu, sans excès (×1,6 maxi)
    f = min(inner / max(im.size), 1.6); im = im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS)
sq = Image.new('RGB', (side, side), (255, 255, 255)); sq.paste(im, ((side - im.width) // 2, (side - im.height) // 2))

def watermark(img):
    WM = Image.open(os.path.join(HERE, 'wm', 'watermark.png')).convert('RGBA')
    base = img.convert('RGBA'); w, h = base.size
    tw = min(max(70, int(w * 0.34)), int(w * 0.8)); th = int(WM.height * tw / WM.width)
    wm = WM.resize((tw, th), Image.LANCZOS)
    shadow = Image.new('RGBA', wm.size, (0, 0, 0, 0)); shadow.putalpha(wm.split()[3]); shadow = shadow.filter(ImageFilter.GaussianBlur(max(1, tw // 90)))
    shadow.putalpha(shadow.split()[3].point(lambda a: int(a * 0.35))); wm.putalpha(wm.split()[3].point(lambda v: int(v * 0.66)))
    pad = max(4, int(w * 0.025)); x, y = w - tw - pad, h - th - pad
    base.alpha_composite(shadow, (x, y + max(1, tw // 120))); base.alpha_composite(wm, (x, y))
    return base.convert('RGB')

if propose:
    os.makedirs(propose, exist_ok=True)
    watermark(sq).save(os.path.join(propose, pid + '.webp'), 'WEBP', quality=84, method=6)
    print(os.path.join(propose, pid + '.webp')); sys.exit(0)

os.makedirs(os.path.join(ROOT, 'images-sans-filigrane'), exist_ok=True)
sq.save(os.path.join(ROOT, 'images-sans-filigrane', pid + '.webp'), 'WEBP', quality=86, method=6)
watermark(sq).save(os.path.join(ROOT, 'images', pid + '.webp'), 'WEBP', quality=84, method=6)
# vignette 80 px pour la page Catalogue
t = sq.copy(); t.thumbnail((80, 80), Image.LANCZOS); buf = io.BytesIO(); t.save(buf, 'WEBP', quality=70)
tp = os.path.join(HERE, 'thumbs.json'); thumbs = json.load(open(tp, encoding='utf-8'))
thumbs[pid] = 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()
json.dump(thumbs, open(tp, 'w', encoding='utf-8'), separators=(',', ':'))
print('images/' + pid + '.webp')
