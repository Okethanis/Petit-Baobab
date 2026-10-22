"""Photo du couple pour la carte « Myris » : recadrage sur eux deux, rendu peint (lissage des aplats + contours doux),
   lumière chaude. Sort static/nous.jpg (publié à la racine du site, sans métadonnées EXIF).
   Usage : python3 -I brand/nous.py <photo source>"""
import sys, numpy as np, cv2
from PIL import Image, ImageEnhance, ImageFilter

src = sys.argv[1]
im = Image.open(src).convert('RGB')
W, H = im.size
# recadrage portrait 4:5 sur les deux personnes (partie gauche de la photo, du haut des têtes au bas)
left, top, right, bottom = int(W * 0.0), int(H * 0.30), int(W * 0.62), int(H * 0.99)
box_w = right - left; box_h = int(box_w * 1.25)
top = min(top, bottom - box_h); bottom = top + box_h
crop = im.crop((left, top, right, bottom)).resize((640, 800), Image.LANCZOS)

# rendu peint : lissage préservant les contours (deux passes), puis contours légers
bgr = cv2.cvtColor(np.array(crop), cv2.COLOR_RGB2BGR)
smooth = cv2.edgePreservingFilter(bgr, flags=cv2.RECURS_FILTER, sigma_s=50, sigma_r=0.4)
smooth = cv2.bilateralFilter(smooth, 11, 70, 70)
smooth = cv2.bilateralFilter(smooth, 7, 50, 50)
gray = cv2.cvtColor(smooth, cv2.COLOR_BGR2GRAY)
lines = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 70, 160)
lines = cv2.dilate(lines, np.ones((2, 2), np.uint8))
lines = cv2.GaussianBlur(lines, (3, 3), 0)
ink = 1.0 - cv2.cvtColor(lines, cv2.COLOR_GRAY2BGR).astype(np.float32) / 255.0   # 1 = pas de trait
painted = (smooth.astype(np.float32) * (0.72 + 0.28 * ink)).clip(0, 255).astype(np.uint8)
out = Image.fromarray(cv2.cvtColor(painted, cv2.COLOR_BGR2RGB))

# lumière chaude, un peu plus de couleur, vignette douce
out = ImageEnhance.Color(out).enhance(1.25)
out = ImageEnhance.Contrast(out).enhance(1.06)
r, g, b = out.split()
r = r.point(lambda v: min(255, int(v * 1.06 + 6))); b = b.point(lambda v: int(v * 0.94))
out = Image.merge('RGB', (r, g, b))
vign = Image.new('L', out.size, 0)
cx, cy = out.size[0] / 2, out.size[1] / 2
yy, xx = np.mgrid[0:out.size[1], 0:out.size[0]]
d = np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2)
mask = (np.clip((d - 0.75) / 0.6, 0, 1) * 110).astype(np.uint8)
out = Image.composite(Image.new('RGB', out.size, (40, 60, 45)), out, Image.fromarray(mask))
out.save('static/nous.jpg', quality=82, optimize=True)
print('static/nous.jpg', out.size)
