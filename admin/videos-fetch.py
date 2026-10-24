"""Vidéos des articles, préparées pendant la construction Netlify (après admin/photos-fetch.js et photos-ocr.py).
   Demande de Hanis (24 oct. 2026) : « au moins 5 images et une vidéo des produits » ; logo du fournisseur accepté,
   mais tout texte chinois doit être effacé.

   Source : photos/sources.json → "video": "https://…mp4" (vidéo du fournisseur ; même statut que les photos).

   Aperçus (tout sauf la production) :
     - télécharge la vidéo, lit le texte de 2 images par seconde (RapidOCR) ;
     - efface chaque texte chinois (idéogrammes) : filtre ffmpeg « delogo » sur sa zone (avec marge), pendant tout le
       temps où il apparaît (± 1 s) ; la vidéo préparée est relue : s'il en reste, on élargit et on recommence (3 fois au plus) ;
     - sans le son, 960 px au plus (grand côté), 45 s au plus, H.264 « faststart » (lecture immédiate) ;
     - site/videos/<id>.mp4 + <id>.jpg (affiche) + site/videos/videos.json {id: {w, h, d}} ;
     - page /verification-videos/ : vidéo du fournisseur et vidéo préparée côte à côte, textes effacés.
     Cache : .photos-cache/videos/ (gardé d'une construction à l'autre), une vidéo n'est préparée qu'une fois.
   En ligne (production) : reprend les vidéos déjà préparées sur l'aperçu n° 4 (PHOTOS_FROM), sans les « à vérifier ».
   Limite de temps : PB_BUILD_START (heure de début écrite par netlify.toml) ; on s'arrête à 15 min de construction,
   la suite est préparée à la construction suivante.
   Ne casse jamais la construction. Usage local : python3 admin/videos-fetch.py (ffmpeg et rapidocr nécessaires)."""
import hashlib, html, json, os, re, shutil, subprocess, sys, tempfile, time, urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'site', 'videos')
SRC = os.environ.get('VIDEOS_SRC') or os.path.join(ROOT, 'photos', 'sources.json')   # VIDEOS_SRC : essais
CACHE = os.path.join(ROOT, '.photos-cache', 'videos')
PROD = os.environ.get('CONTEXT') == 'production'
FROM = os.environ.get('PHOTOS_FROM') or ('https://deploy-preview-4--petit-baobab.netlify.app' if PROD else '')   # aperçu validé (PR n° 4)
VERSION = 'v1'
ALGO = 2   # 2 : lecture à 2 images/s, marges plus larges, nouvelle passe tant qu'il reste du chinois
MAXSIDE, MAXD = 960, 45   # grand côté 960 px au plus (540 × 960 en portrait) : léger sur un téléphone
CJK = re.compile('[㐀-鿿豈-﫿]')
START = float(os.environ.get('PB_BUILD_START') or time.time())
STOP = START + float(os.environ.get('VIDEOS_STOP_S') or 900)   # 15 min après le début (Netlify coupe à 18 min, envoi du site compris)

def log(*a): print('videos-fetch :', *a, flush=True)

def get(url, timeout=60):
    if not re.match(r'https?:', url): return open(os.path.join(ROOT, url), 'rb').read(), 'video/mp4'   # fichier local (essais)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh) PetitBaobab-build', 'Referer': 'https://www.alibaba.com/'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.headers.get('content-type', '')

def ffmpeg_exe():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return shutil.which('ffmpeg')

def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode: raise RuntimeError(p.stderr[-600:])
    return p.stderr

def probe(ff, path):
    err = subprocess.run([ff, '-hide_banner', '-i', path], stderr=subprocess.PIPE, text=True).stderr
    m = re.search(r'Video:.*?(\d{2,5})x(\d{2,5})', err); d = re.search(r'Duration: (\d+):(\d+):([\d.]+)', err)
    rot = re.search(r'rotate\s*:\s*(-?\d+)|displaymatrix: rotation of (-?[\d.]+)', err)
    w, h = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    if rot and abs(round(float(rot.group(1) or rot.group(2)))) in (90, 270): w, h = h, w
    dur = int(d.group(1)) * 3600 + int(d.group(2)) * 60 + float(d.group(3)) if d else 0
    return w, h, dur

def out_size(w, h):
    k = min(1.0, MAXSIDE / float(max(w, h)))
    return int(round(w * k / 2.0)) * 2, int(round(h * k / 2.0)) * 2

def ocr_frames(ff, eng, src, W, H, dur, fps, tmp):
    """Images à `fps` par seconde, réduites (OCR plus rapide), lues par RapidOCR → [(t, x0, y0, x1, y1, texte)] en pixels de sortie."""
    k = min(1.0, 960.0 / max(W, H)); w2, h2 = int(W * k) // 2 * 2, int(H * k) // 2 * 2
    d = os.path.join(tmp, 'f%s' % fps); os.makedirs(d, exist_ok=True)
    run([ff, '-hide_banner', '-loglevel', 'error', '-y', '-t', str(min(dur, MAXD)), '-i', src,
         '-vf', 'fps=%s,scale=%d:%d' % (fps, w2, h2), '-q:v', '3', os.path.join(d, '%04d.jpg')])
    found = []
    for name in sorted(os.listdir(d)):
        t = (int(name[:4]) - 1) / float(fps) + 0.5 / fps
        r, _ = eng(os.path.join(d, name))
        for box, text, score in (r or []):
            if float(score) < 0.5 or not CJK.search(text): continue
            if len(CJK.findall(text)) <= 1 and len(re.findall('[A-Za-z]', text)) >= 4: continue   # logo latin lu de travers
            xs = [p[0] / k for p in box]; ys = [p[1] / k for p in box]
            found.append((t, min(xs), min(ys), max(xs), max(ys), text))
    return found

def regions(found, W, H, fps, grow=1.0):
    """Regroupe les détections proches (même ligne de texte, temps qui se suivent) → zones à effacer avec leur période.
       Marges larges : les sous-titres des fournisseurs apparaissent souvent en glissant ou lettre par lettre."""
    span = 1.0 / fps + 0.75 * grow
    regs = []
    for t, x0, y0, x1, y1, text in sorted(found):
        h = y1 - y0
        px, py = max(10, 0.6 * h) * grow, max(8, 0.35 * h) * grow
        x0, y0, x1, y1 = x0 - px, y0 - py, x1 + px, y1 + py
        for g in regs:
            ix = min(x1, g['x1']) - max(x0, g['x0']); iy = min(y1, g['y1']) - max(y0, g['y0'])
            if ix > -h and iy > 0.3 * min(y1 - y0, g['y1'] - g['y0']) and t - span <= g['t1'] + 1.0:
                g.update(x0=min(x0, g['x0']), y0=min(y0, g['y0']), x1=max(x1, g['x1']), y1=max(y1, g['y1']), t1=max(g['t1'], t + span))
                g['txt'].add(text); break
        else:
            regs.append(dict(x0=x0, y0=y0, x1=x1, y1=y1, t0=max(0, t - span), t1=t + span, txt={text}))
    out = []
    for g in regs:
        x0 = int(max(1, g['x0'])); y0 = int(max(1, g['y0'])); x1 = int(min(W - 2, g['x1'])); y1 = int(min(H - 2, g['y1']))
        if x1 - x0 >= 4 and y1 - y0 >= 4: out.append(dict(x=x0, y=y0, w=x1 - x0, h=y1 - y0, t0=round(g['t0'], 2), t1=round(g['t1'], 2), txt=sorted(g['txt'])))
    return out

def encode(ff, src, dst, W, H, dur, regs):
    vf = ['scale=%d:%d' % (W, H)]
    for r in regs[:90]:
        vf.append("delogo=x=%d:y=%d:w=%d:h=%d:enable='between(t,%s,%s)'" % (r['x'], r['y'], r['w'], r['h'], r['t0'], r['t1']))
    vf.append('format=yuv420p')
    run([ff, '-hide_banner', '-loglevel', 'error', '-y', '-i', src, '-t', str(min(dur, MAXD)), '-an', '-vf', ','.join(vf),
         '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '28', '-profile:v', 'high', '-movflags', '+faststart', dst])

def prepare(ff, eng, vid, url):
    key = hashlib.sha1((url + '|' + VERSION).encode()).hexdigest()
    base = os.path.join(CACHE, key)
    if os.path.exists(base + '.json') and os.path.exists(base + '.mp4'):
        info = json.load(open(base + '.json', encoding='utf-8'))
        # vidéo déjà préparée ; on ne refait que celles qui avaient du chinois avec l'ancienne méthode (algo 1)
        if info.get('algo', 1) >= ALGO or not (info.get('efface') or info.get('reste')): return base, info
    if time.time() > STOP - 90: return None, None
    tmp = tempfile.mkdtemp(prefix='pbv-')
    try:
        data, ctype = get(url)
        if len(data) < 20000: raise RuntimeError('fichier trop petit (%s)' % ctype)
        src = os.path.join(tmp, 'src.mp4'); open(src, 'wb').write(data)
        w, h, dur = probe(ff, src)
        if not w or not dur: raise RuntimeError('vidéo illisible')
        W, H = out_size(w, h)
        found = ocr_frames(ff, eng, src, W, H, dur, 2, tmp)
        regs = regions(found, W, H, 2)
        # on efface, puis on relit la vidéo préparée (1 image par seconde) ; s'il reste du chinois, on élargit et on recommence
        for tour in range(3):
            encode(ff, src, base + '.mp4', W, H, dur, regs)
            if not regs and tour == 0 and not found: reste = []; break
            left = ocr_frames(ff, eng, base + '.mp4', W, H, dur, 1, tmp)
            reste = sorted({round(f[0], 1) for f in left})
            if not left or time.time() > STOP - 60: break
            regs = regs + regions(left, W, H, 1, grow=1.6 + tour)
        run([ff, '-hide_banner', '-loglevel', 'error', '-y', '-ss', '1', '-i', base + '.mp4', '-frames:v', '1', '-q:v', '4', base + '.jpg'])
        info = dict(id=vid, url=url, algo=ALGO, w=W, h=H, d=round(min(dur, MAXD), 1), efface=regs, reste=reste,
                    ko=os.path.getsize(base + '.mp4') // 1024)
        json.dump(info, open(base + '.json', 'w', encoding='utf-8'), ensure_ascii=False)
        return base, info
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def page(rows, names):
    def card(vid, info, s):
        lbl = {'trouve': ('Même article', '#1F6B4A'), 'couleur': ('Autre couleur', '#C9711C')}.get(s.get('statut'), ('À vérifier', '#B4423B'))
        eff = ''.join('<li>%s–%s s : %s</li>' % (r['t0'], r['t1'], html.escape(' / '.join(r['txt']))) for r in info['efface'])
        warn = ('<p class="warn">Il reste peut-être du chinois vers %s s</p>' % ', '.join('%g' % t for t in info['reste'][:6])) if info['reste'] else ''
        return ('<article class="row"><div class="head"><b>%s</b> <span class="ref">%s · %s s · %s Ko</span><span class="tag" style="background:%s">%s</span></div>'
                '<div class="vids"><figure><video src="%s" controls muted playsinline preload="metadata"></video><figcaption>Vidéo du fournisseur</figcaption></figure>'
                '<figure><video src="/videos/%s.mp4" poster="/videos/%s.jpg" controls muted playsinline preload="metadata"></video><figcaption>Sur le site</figcaption></figure></div>%s%s</article>') % (
            html.escape(names.get(vid, vid)), html.escape(vid), info['d'], info['ko'], lbl[1], lbl[0], html.escape(info['url']), vid, vid,
            ('<details><summary>%d texte(s) chinois effacé(s)</summary><ul>%s</ul></details>' % (len(info['efface']), eff)) if info['efface'] else '<p class="ok">Aucun texte chinois</p>', warn)
    body = '\n'.join(card(*r) for r in rows)
    return ('<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Vérification des vidéos · Petit Baobab</title>'
            '<style>body{margin:0;font:15px/1.45 system-ui,-apple-system,sans-serif;background:#F5F7F2;color:#1E2B22}header{position:sticky;top:0;z-index:2;background:#1F6B4A;color:#fff;padding:12px 16px}header h1{margin:0;font-size:18px}header p{margin:4px 0 0;font-size:13px}'
            'main{max-width:1100px;margin:0 auto;padding:12px 16px 60px}.row{background:#fff;border:1px solid #D9E1D8;border-radius:14px;padding:12px;margin:12px 0}.head{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.ref{color:#55615A;font-size:13px;flex:1}'
            '.tag{color:#fff;border-radius:999px;padding:2px 10px;font-size:12px;font-weight:700}.vids{display:flex;gap:10px;margin-top:10px;flex-wrap:wrap}figure{margin:0;flex:1 1 260px}video{width:100%%;max-height:60vh;background:#000;border-radius:10px;display:block}'
            'figcaption{font-size:12px;color:#55615A;text-align:center;margin-top:3px}details,.ok,.warn{margin:8px 0 0;font-size:13px}.ok{color:#2E7D5B}.warn{color:#B4423B;font-weight:700}</style></head>'
            '<body><header><h1>Vérification des vidéos (%d articles)</h1><p>À gauche la vidéo du fournisseur, à droite celle du site (sans le son, texte chinois effacé).</p></header><main>%s</main></body></html>') % (len(rows), body)

def names_from_html():
    s = open(os.path.join(ROOT, 'petit-baobab.html'), encoding='utf-8').read()
    return {m.group(1): m.group(2).replace("\\'", "'") for m in re.finditer(r"^  \{id:'([^']+)', cat:'[^']*', name:'((?:[^'\\]|\\.)*)'", s, re.M)}

def main():
    if not os.path.exists(SRC): return log('pas de photos/sources.json')
    S = json.load(open(SRC, encoding='utf-8'))
    todo = {k: v for k, v in S.items() if v.get('video') and not (PROD and v.get('statut') == 'doute')}
    if not todo: return log('aucune vidéo')
    os.makedirs(OUT, exist_ok=True)
    index = {}
    if PROD:   # reprise des vidéos préparées sur l'aperçu
        if not FROM: return log('pas d\'aperçu d\'où reprendre les vidéos')
        try: prev = json.loads(get(FROM.rstrip('/') + '/videos/videos.json', 30)[0])
        except Exception as e: return log('videos.json de l\'aperçu illisible (%s)' % e)
        for vid in todo:
            if vid not in prev: continue
            try:
                mp4, ct = get(FROM.rstrip('/') + '/videos/%s.mp4' % vid)
                jpg, ct2 = get(FROM.rstrip('/') + '/videos/%s.jpg' % vid, 30)
                if 'video/mp4' not in ct or len(mp4) < 20000: continue
                open(os.path.join(OUT, vid + '.mp4'), 'wb').write(mp4); open(os.path.join(OUT, vid + '.jpg'), 'wb').write(jpg)
                index[vid] = prev[vid]
            except Exception as e: log('échec reprise', vid, e)
        json.dump(index, open(os.path.join(OUT, 'videos.json'), 'w'))
        return log('%d vidéos reprises de l\'aperçu' % len(index))
    ff = ffmpeg_exe()
    try:
        from rapidocr_onnxruntime import RapidOCR
        eng = RapidOCR()
    except Exception as e:
        return log('RapidOCR absent (%s) : pas de vidéo sans contrôle du chinois' % e)
    if not ff: return log('ffmpeg absent')
    os.makedirs(CACHE, exist_ok=True)
    rows, later, names = [], 0, names_from_html()
    for vid, s in todo.items():
        try:
            base, info = prepare(ff, eng, vid, s['video'])
        except Exception as e:
            log('échec', vid, str(e)[:300]); continue
        if not base: later += 1; continue
        shutil.copyfile(base + '.mp4', os.path.join(OUT, vid + '.mp4')); shutil.copyfile(base + '.jpg', os.path.join(OUT, vid + '.jpg'))
        index[vid] = dict(w=info['w'], h=info['h'], d=info['d'])
        rows.append((vid, info, s))
    json.dump(index, open(os.path.join(OUT, 'videos.json'), 'w'))
    os.makedirs(os.path.join(ROOT, 'site', 'verification-videos'), exist_ok=True)
    open(os.path.join(ROOT, 'site', 'verification-videos', 'index.html'), 'w', encoding='utf-8').write(page(rows, names))
    log('%d vidéos prêtes%s, %d avec du chinois effacé' % (len(index), (', %d reportées (limite de temps)' % later) if later else '', sum(1 for r in rows if r[1]['efface'])))

try:
    main()
except Exception as e:
    log('erreur', e)
sys.exit(0)
