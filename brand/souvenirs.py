"""Souvenirs pour la carte « Myris » : photos recadrées en 4:5 avec un rendu peint, et la vidéo des mains en boucle muette.
   Sortie : static/souvenirs/ (publié tel quel à la racine du site ; les métadonnées EXIF disparaissent au passage).
   Usage : python3 -I brand/souvenirs.py <dossier des sources>   (ombre.jpg, ascenseur.jpg, rouge.jpg, mains.mov)"""
import sys, os, subprocess, numpy as np, cv2
from PIL import Image, ImageEnhance

SRC = sys.argv[1]; OUT = 'static/souvenirs'; os.makedirs(OUT, exist_ok=True)

def painted(im):
    bgr = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    smooth = cv2.edgePreservingFilter(bgr, flags=cv2.RECURS_FILTER, sigma_s=50, sigma_r=0.4)
    smooth = cv2.bilateralFilter(smooth, 11, 70, 70); smooth = cv2.bilateralFilter(smooth, 7, 50, 50)
    gray = cv2.cvtColor(smooth, cv2.COLOR_BGR2GRAY)
    lines = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 70, 160)
    lines = cv2.GaussianBlur(cv2.dilate(lines, np.ones((2, 2), np.uint8)), (3, 3), 0)
    ink = 1.0 - cv2.cvtColor(lines, cv2.COLOR_GRAY2BGR).astype(np.float32) / 255.0
    out = Image.fromarray(cv2.cvtColor((smooth.astype(np.float32) * (0.72 + 0.28 * ink)).clip(0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB))
    out = ImageEnhance.Color(out).enhance(1.22); out = ImageEnhance.Contrast(out).enhance(1.06)
    r, g, b = out.split(); r = r.point(lambda v: min(255, int(v * 1.06 + 6))); b = b.point(lambda v: int(v * 0.94)); out = Image.merge('RGB', (r, g, b))
    cx, cy = out.size[0] / 2, out.size[1] / 2; yy, xx = np.mgrid[0:out.size[1], 0:out.size[0]]
    d = np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2); mask = (np.clip((d - 0.75) / 0.6, 0, 1) * 100).astype(np.uint8)
    return Image.composite(Image.new('RGB', out.size, (40, 60, 45)), out, Image.fromarray(mask))

def photo(name, box):
    """box = (gauche, haut, droite, bas) en fractions de l'image ; le cadre est ramené au format 4:5 autour de cette zone."""
    im = Image.open(os.path.join(SRC, name)).convert('RGB'); W, H = im.size
    l, t, r, b = [int(v * s) for v, s in zip(box, (W, H, W, H))]
    w, h = r - l, b - t
    if h / w > 1.25: nh = int(w * 1.25); t = t + (h - nh) // 2; b = t + nh
    else: nw = int(h / 1.25); cx = (l + r) // 2; l = max(0, cx - nw // 2); r = min(W, l + nw); l = r - nw
    crop = im.crop((l, t, r, b)).resize((640, 800), Image.LANCZOS)
    painted(crop).save(os.path.join(OUT, os.path.splitext(name)[0] + '.jpg'), quality=82, optimize=True)
    print(name, '→', os.path.splitext(name)[0] + '.jpg')

photo('ombre.jpg', (0.18, 0.44, 1.0, 1.0))        # les deux ombres sur le sable
photo('ascenseur.jpg', (0.0, 0.30, 0.62, 0.99))   # miroir d'ascenseur
photo('rouge.jpg', (0.25, 0.33, 0.95, 1.0))       # robe rouge

# vidéo des mains : 4:5, muette, en boucle, légère et compatible partout (H.264), avec une image d'attente
src = os.path.join(SRC, 'mains.mov')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-an', '-vf', 'crop=iw:min(ih\\,iw*1.25),scale=448:560,eq=saturation=1.15:contrast=1.04,colorbalance=rs=.04:bs=-.04',
                '-c:v', 'libx264', '-profile:v', 'baseline', '-level', '3.0', '-pix_fmt', 'yuv420p', '-crf', '27', '-preset', 'slow', '-movflags', '+faststart', os.path.join(OUT, 'mains.mp4')], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(OUT, 'mains.mp4'), '-frames:v', '1', '-q:v', '4', os.path.join(OUT, 'mains.jpg')], check=True)
print('mains.mp4', os.path.getsize(os.path.join(OUT, 'mains.mp4')) // 1024, 'Ko')
