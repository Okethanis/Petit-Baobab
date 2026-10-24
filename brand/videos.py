"""Vidéo de l'article sur sa fiche (demande de Hanis, 24 oct. 2026 : « au moins 5 images et une vidéo des produits »).
   Les vidéos sont préparées par Netlify (admin/videos-fetch.py) : videos/<id>.mp4 (sans le son, chinois effacé),
   videos/<id>.jpg (affiche), listées dans videos/videos.json, lu par la page au chargement.
   Sur la fiche : une vignette « Vidéo » (affiche + triangle) dans la rangée des photos ; un clic remplace la grande photo
   par la vidéo (lecture sur place, muette, avec les commandes) ; un clic sur une photo revient à la photo.
   Rien n'est chargé tant que le client ne clique pas (preload="none"). Idempotent ; à lancer après brand/galerie.py."""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'petit-baobab.html')
s = open(P, encoding='utf-8').read()

def rep(old, new, marker):
    global s
    if marker in s: return
    assert s.count(old) == 1, ('introuvable ou multiple', old[:90])
    s = s.replace(old, new)

# 1) liste des vidéos + vignette dans la galerie
rep("function galleryStrip(p, cur){\n  var extra = (GALERIE[p.id] || []).filter(function(f){ return f !== p.id + '.webp'; });\n  if (!extra.length) return '';\n",
    "var VIDEOS = {};\n"
    "setTimeout(function(){ try { fetch(img({image:'videos/videos.json'}), {cache:'no-cache'}).then(function(r){ return r.ok ? r.json() : {}; }).then(function(j){ VIDEOS = j || {}; }).catch(function(){}); } catch(e){} }, 0);\n"
    "function videoThumb(p){\n"
    "  if (!VIDEOS[p.id]) return '';\n"
    "  return '<button type=\"button\" class=\"gal-t gal-v\" data-action=\"gal-video\" data-id=\"' + esc(p.id) + '\" aria-label=\"Voir la vidéo\"><img src=\"' + esc(img({image:'videos/' + p.id + '.jpg'})) + '\" alt=\"\" loading=\"lazy\"><span>Vidéo</span></button>';\n"
    "}\n"
    "function galleryStrip(p, cur){\n  var extra = (GALERIE[p.id] || []).filter(function(f){ return f !== p.id + '.webp'; });\n  if (!extra.length && !VIDEOS[p.id]) return '';\n",
    "function videoThumb(p)")
rep("}).join('') + '</div>';\n}\nfunction pickPhoto(t){\n  var im = $('#sheet .product .tile img'); if (im) im.src = t.getAttribute('data-src');\n",
    "}).join('') + videoThumb(p) + '</div>';\n}\n"
    "function pickVideo(t){\n"
    "  var tile = $('#sheet .product .tile'), id = t.getAttribute('data-id'), v = VIDEOS[id]; if (!tile || !v) return;\n"
    "  var old = $('.pvid', tile); if (old) old.remove();\n"
    "  var im = $('img', tile); if (im) im.hidden = true;\n"
    "  var el = document.createElement('video');\n"
    "  el.className = 'pvid'; el.controls = true; el.muted = true; el.playsInline = true; el.setAttribute('playsinline', ''); el.preload = 'none';\n"
    "  el.poster = img({image:'videos/' + id + '.jpg'}); el.src = img({image:'videos/' + id + '.mp4'});\n"
    "  el.setAttribute('aria-label', 'Vidéo de l\\'article');\n"
    "  tile.appendChild(el); try { var pr = el.play(); if (pr && pr.catch) pr.catch(function(){}); } catch(e){}\n"
    "  $$('#sheet .gal-t').forEach(function(b){ b.classList.toggle('on', b===t); });\n"
    "}\n"
    "function pickPhoto(t){\n  var pv = $('#sheet .product .tile .pvid'); if (pv){ try { pv.pause(); } catch(e){} pv.remove(); }\n  var im = $('#sheet .product .tile img'); if (im){ im.hidden = false; im.src = t.getAttribute('data-src'); }\n",
    "function pickVideo(t)")

# 2) changer de couleur revient aussi à la photo
rep("  var im = $('#sheet .product .tile img'); if (im){ im.src = img({image:c[1]}); im.alt = p.name + ' (' + c[0] + ')'; }\n",
    "  var pv = $('#sheet .product .tile .pvid'); if (pv){ try { pv.pause(); } catch(e){} pv.remove(); }\n"
    "  var im = $('#sheet .product .tile img'); if (im){ im.hidden = false; im.src = img({image:c[1]}); im.alt = p.name + ' (' + c[0] + ')'; }\n",
    "if (pv){ try { pv.pause(); } catch(e){} pv.remove(); }\n  var im = $('#sheet .product .tile img'); if (im){ im.hidden = false; im.src = img({image:c[1]})")

# 3) clic sur la vignette vidéo
rep("    case 'gal': pickPhoto(t); break;\n", "    case 'gal': pickPhoto(t); break;\n    case 'gal-video': pickVideo(t); break;\n", "case 'gal-video'")

# 4) styles
CSS = """
/* Vidéo de l'article (brand/videos.py) */
.gal-v{position:relative}
.gal-v img{object-fit:cover}
.gal-v::before{content:"";position:absolute;left:50%;top:42%;transform:translate(-50%,-50%);width:26px;height:26px;border-radius:50%;background:rgba(30,43,34,.72)}
.gal-v::after{content:"";position:absolute;left:50%;top:42%;transform:translate(-35%,-50%);border-style:solid;border-width:6px 0 6px 10px;border-color:transparent transparent transparent #fff}
.gal-v span{position:absolute;left:0;right:0;bottom:0;background:rgba(30,43,34,.72);color:#fff;font-size:.68rem;font-weight:700;line-height:1.5;text-align:center}
.product .tile .pvid{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;background:#000;display:block;border-radius:inherit}
"""
if "/* Vidéo de l'article (brand/videos.py) */" not in s:
    i = s.index('</style>'); s = s[:i] + CSS + s[i:]

open(P, 'w', encoding='utf-8').write(s)
print('vidéos sur la fiche : ok')
