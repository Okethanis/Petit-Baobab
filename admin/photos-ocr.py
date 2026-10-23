"""Aperçus Netlify seulement : lit le texte des photos du site et repère le chinois et les prix en yuans.
   Lancé après admin/photos-fetch.js (voir netlify.toml). Demande de Hanis (23 oct. 2026) : aucune photo avec du chinois.
   - Lit chaque nouvelle photo HD (liste site/images/galerie.json), avec RapidOCR (chinois + latin).
   - Résultats gardés dans .photos-cache/ocr.json (clé = empreinte du fichier) : seules les nouvelles photos sont relues.
   - Écrit site/verification-photos/ocr.json  {"<fichier>.webp": ["texte chinois lu", …]}  (seulement les photos signalées)
     et ajoute une étiquette rouge « Texte chinois » sur la page /verification-photos/.
   Ne casse jamais la construction : en cas d'erreur, il le dit et s'arrête."""
import hashlib, json, os, re, sys, time

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
IMG = os.path.join(ROOT, 'site', 'images')
VERIF = os.path.join(ROOT, 'site', 'verification-photos')
CACHE = os.path.join(ROOT, '.photos-cache', 'ocr.json')
CJK = re.compile(r'[　-〿㐀-鿿＀-￯]')
MONEY = re.compile(r'[¥￥]|RMB|元')

def flagged(lines):
    out = []
    for t, score in lines:
        if score < 0.6: continue
        n = len(CJK.findall(t))
        # « 中Petit Baobab » : notre filigrane lu de travers, pas du chinois
        if 'etit' in t and n <= 1: continue
        if n or MONEY.search(t): out.append(t)
    return out

def main():
    try:
        from rapidocr_onnxruntime import RapidOCR
        from PIL import Image
    except Exception as e:
        print('photos-ocr : RapidOCR absent (' + str(e) + '), rien à faire'); return
    eng = RapidOCR()
    cache = {}
    if os.path.exists(CACHE):
        try: cache = json.load(open(CACHE, encoding='utf-8'))
        except Exception: cache = {}
    # seulement les nouvelles photos HD (les anciennes photos du dépôt sont relues à part, sans Netlify)
    gal = json.load(open(os.path.join(IMG, 'galerie.json'), encoding='utf-8'))
    files = sorted({f for k, v in gal.items() if ':' not in k for f in v if os.path.exists(os.path.join(IMG, f))})
    t0, done = time.time(), 0
    res = {}
    for f in files:
        p = os.path.join(IMG, f)
        h = hashlib.sha1(open(p, 'rb').read()).hexdigest()
        if h not in cache:
            if time.time() - t0 > 600:  # garde de la marge sur la limite de temps de Netlify ; la suite au prochain aperçu
                continue
            im = Image.open(p).convert('RGB')
            if max(im.size) > 1000: im.thumbnail((1000, 1000))
            tmp = '/tmp/pb-ocr.png'; im.save(tmp)
            r, _ = eng(tmp)
            cache[h] = [[t, round(float(s), 2)] for _, t, s in (r or [])]
            done += 1
        bad = flagged(cache[h])
        if bad: res[f] = bad
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump(cache, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False)
    os.makedirs(VERIF, exist_ok=True)
    left = sum(1 for f in files if hashlib.sha1(open(os.path.join(IMG, f), 'rb').read()).hexdigest() not in cache)
    json.dump({'photos': res, 'relues': done, 'restantes': left, 'total': len(files)},
              open(os.path.join(VERIF, 'ocr.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    page = os.path.join(VERIF, 'index.html')
    if os.path.exists(page) and res:
        html = open(page, encoding='utf-8').read()
        for f in res:
            html = html.replace('<img src="/images/' + f + '" alt="" loading="lazy">',
                                '<img src="/images/' + f + '" alt="" loading="lazy" class="cn"><span class="cnb">Texte chinois</span>')
        html = html.replace('</style>', 'figure{position:relative}.cn{outline:3px solid #B4423B}.cnb{position:absolute;top:6px;left:6px;background:#B4423B;color:#fff;font-size:11px;font-weight:700;border-radius:999px;padding:2px 8px}</style>', 1)
        open(page, 'w', encoding='utf-8').write(html)
    print('photos-ocr : %d photos relues, %d avec du chinois, %d restantes' % (done, len(res), left))

try:
    main()
except Exception as e:
    print('photos-ocr : erreur', e)
sys.exit(0)
