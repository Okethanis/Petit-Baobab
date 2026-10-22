"""Micro-animations du site : pied de page interactif (soleil = nuit/jour, rayons, lune, étoiles), survols, parallaxe, carte qui se penche.
   Idempotent : relancer ne double rien."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, '..', 'petit-baobab.html'); s = open(p, encoding='utf-8').read()
if 'footer-brand' in s:
    print('déjà en place'); raise SystemExit
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:70]); s = s.replace(old, new)

# ---------- 1. Pied de page : paysage interactif ----------
foot_start = s.index('<footer class="footer">')
a = s.index('<a href="#accueil" class="logo" data-action="nav" data-view="accueil">', foot_start)
b = s.index('</a>', a) + 4
mark = json.load(open(os.path.join(HERE, 'mark.json'), encoding='utf-8'))['mark']
rays = ''.join('<line x1="104" y1="18" x2="104" y2="1" transform="rotate(%d 104 18)"/>' % d for d in range(0, 360, 45))
stars = ''.join('<circle cx="%d" cy="%d" r="%.1f" style="--d:%d"/>' % (x, y, r, i) for i, (x, y, r) in enumerate([(14, 10, 1.4), (30, 26, 1), (62, 8, 1.2), (118, 40, 1), (90, 4, .9), (46, 18, .8), (112, 60, .9)]))
scene = ('<span class="footer-scene"><svg viewBox="0 0 120 120" class="mark" aria-hidden="true" focusable="false"><g class="stars">' + stars + '</g>'
         + mark.replace('<g class="lg-sun"><circle cx="104" cy="18" r="10"/></g>',
                        '<g class="lg-sun"><g class="rays" stroke-linecap="round">' + rays + '</g><circle cx="104" cy="18" r="10"/><circle class="moonbite" cx="108" cy="14" r="8.5"/></g>')
         + '</svg></span>')
s = s[:a] + '<div class="footer-brand">' + scene + '<a href="#accueil" class="logo" data-action="nav" data-view="accueil"><span>Petit Baobab</span></a><button type="button" class="sun-toggle" data-action="theme" aria-label="Passer en mode nuit ou jour" title="Mode nuit / jour"></button></div>' + s[b:]

# ---------- 2. CSS ----------
CSS = '''
/* ===== Micro-animations : la souris fait vivre le site (souris seulement, jamais si la personne préfère moins de mouvement) ===== */
.mark > g{transform-box:view-box}
@media (hover:hover) and (prefers-reduced-motion: no-preference){
  .logo .mark > g:nth-of-type(1){transform-origin:104px 18px}
  .logo:hover .mark > g:nth-of-type(1){animation:lg-hop .7s var(--spring)}
  .logo .mark > g:nth-of-type(4){transform-origin:59px 58px}
  .logo:hover .mark > g:nth-of-type(4){animation:lg-shake .8s var(--ease)}
  .logo .mark > g:nth-of-type(6),.logo .mark > g:nth-of-type(7),.logo .mark > g:nth-of-type(8){transform-origin:99px 110px}
  .logo:hover .mark > g:nth-of-type(6),.logo:hover .mark > g:nth-of-type(7),.logo:hover .mark > g:nth-of-type(8){animation:lg-jump .6s var(--spring) .15s}
  .baobab-illus > g:nth-of-type(6),.baobab-illus > g:nth-of-type(7),.baobab-illus > g:nth-of-type(8){transform-origin:99px 110px;transition:transform .9s var(--spring)}
  .baobab-illus:hover > g:nth-of-type(6),.baobab-illus:hover > g:nth-of-type(7),.baobab-illus:hover > g:nth-of-type(8){transform:scale(1.35)}
  .baobab-illus > g:nth-of-type(1){transform-origin:104px 18px;transition:transform .7s var(--ease)}
  .baobab-illus:hover > g:nth-of-type(1){transform:scale(1.25) translateY(-3px)}
  .baobab-illus > g:nth-of-type(4){transform-origin:59px 58px}
  .baobab-illus:hover > g:nth-of-type(4){animation:lg-sway 3s ease-in-out infinite}
  .baobab-illus > g:nth-of-type(2){transform-origin:60px 110px;transition:transform .9s var(--spring)}
  .baobab-illus:hover > g:nth-of-type(2){transform:scaleX(1.08)}
  .card .add{transition:transform .35s var(--spring),background .25s,color .25s}
  .card:hover .add{transform:rotate(90deg) scale(1.08)}
  .univ-card .num{transition:transform .5s var(--spring)}
  .univ-card:hover .num{transform:rotate(360deg) scale(1.12)}
  .univ-card .icon{transition:transform .4s var(--spring)}
  .univ-card:hover .icon{transform:translateY(-3px) rotate(-6deg)}
  .who-card h3{transition:letter-spacing .3s var(--ease)}
  .who-card:hover h3{letter-spacing:.07em}
  .who-card .go svg{transition:transform .3s var(--spring)}
  .who-card:hover .go svg{transform:translateX(6px)}
  .chip{transition:transform .2s var(--spring),background .25s var(--ease),color .2s,border-color .2s}
  .chip:hover{transform:translateY(-2px)}
  .tstep .num{transition:transform .5s var(--spring)}
  .tstep:hover .num{transform:scale(1.15) rotate(-8deg)}
  .btn-primary{overflow:hidden}
  .btn-primary::after{content:"";position:absolute;inset:0;background:linear-gradient(105deg,transparent 35%,rgba(255,255,255,.55) 50%,transparent 65%);transform:translateX(-130%);pointer-events:none}
  .btn-primary:hover::after{animation:btn-shine .8s var(--ease)}
  .btn:hover{transform:translateY(-2px)}
  .fab-wa:hover .icon{animation:lg-ring .6s var(--ease)}
  .fab-top:hover .icon{animation:lg-up .6s var(--ease)}
  .value{transition:transform .35s var(--spring)}
  .value:hover{transform:translateY(-3px)}
  .value h3 i{transition:transform .4s var(--spring)}
  .value:hover h3 i{transform:scale(1.6)}
  .gift-box,.stage{transition:transform .35s var(--spring),box-shadow .35s var(--ease)}
  .gift-box:hover,.stage:hover{transform:translateY(-3px);box-shadow:var(--shadow)}
  .footer-scene:hover .mark > g:nth-of-type(4){animation:lg-shake .8s var(--ease)}
  .footer-scene:hover .mark > g:nth-of-type(7){animation:lg-jump .6s var(--spring)}
  .footer-brand:has(.sun-toggle:hover) .rays{opacity:1;transform:scale(1)}
  .footer-brand:has(.sun-toggle:hover) .lg-sun > circle:first-of-type{transform:translateY(-4px) scale(1.15)}
  .footer-brand:has(.sun-toggle:hover) .moonbite{transform:translate(2px,-2px)}
}
.gift-card{transition:transform .25s var(--ease),box-shadow .25s var(--ease);transform:rotate(-2deg) perspective(900px) rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg))}
.gift-card.tilting{box-shadow:0 26px 60px rgba(30,43,34,.22)}
.footer-brand{display:grid;gap:4px;justify-items:start;position:relative}
.footer-scene{display:block;width:150px;position:relative}
.footer-scene .mark{width:100%;height:auto;overflow:visible}
.footer .mark .lg-tree,.footer .mark .lg-trunk{fill:var(--footer-ink)}
.footer .mark .lg-ground{fill:rgba(255,255,255,.2)}
.footer .mark > g:nth-of-type(4){transform-origin:59px 58px;animation:lg-sway 8s ease-in-out infinite}
.footer .mark > g:nth-of-type(7){transform-origin:99px 88px;animation:lg-sway 6s ease-in-out 1s infinite reverse}
.footer .lg-sun > circle:first-of-type{transform-box:view-box;transform-origin:104px 18px;transition:transform .5s var(--spring),fill .5s}
.footer .rays{stroke:var(--accent);stroke-width:2.2;opacity:0;transform-box:view-box;transform-origin:104px 18px;transform:scale(.4);transition:opacity .35s,transform .5s var(--spring)}
.footer .moonbite{fill:var(--footer-bg);transform-box:view-box;transform-origin:108px 14px;transform:translate(16px,-12px) scale(.2);opacity:0;transition:transform .6s var(--spring),opacity .4s}
.footer .stars circle{fill:#FFF1CF;opacity:0;transform-box:fill-box;transform-origin:center;transition:opacity .6s}
.sun-toggle{position:absolute;left:calc(150px * 104 / 120 - 16px);top:calc(150px * 18 / 120 - 16px);width:32px;height:32px;border-radius:50%;border:0;background:transparent;cursor:pointer;padding:0}
.sun-toggle:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
html[data-theme="dark"] .footer .moonbite{transform:none;opacity:1}
html[data-theme="dark"] .footer .lg-sun > circle:first-of-type{fill:#F5F7F2}
html[data-theme="dark"] .footer .rays{display:none}
html[data-theme="dark"] .footer .stars circle{opacity:.9;animation:lg-twinkle 2.6s ease-in-out infinite;animation-delay:calc(var(--d) * .37s)}
@media (prefers-color-scheme: dark){
  html:not([data-theme="light"]) .footer .moonbite{transform:none;opacity:1}
  html:not([data-theme="light"]) .footer .lg-sun > circle:first-of-type{fill:#F5F7F2}
  html:not([data-theme="light"]) .footer .rays{display:none}
  html:not([data-theme="light"]) .footer .stars circle{opacity:.9;animation:lg-twinkle 2.6s ease-in-out infinite;animation-delay:calc(var(--d) * .37s)}
}
@keyframes lg-hop{0%{transform:none}35%{transform:translateY(-6px) scale(1.15)}70%{transform:translateY(1px) scale(.95)}100%{transform:none}}
@keyframes lg-shake{0%,100%{transform:rotate(0)}20%{transform:rotate(-4deg)}45%{transform:rotate(3.5deg)}70%{transform:rotate(-2deg)}}
@keyframes lg-jump{0%,100%{transform:none}40%{transform:translateY(-5px) scaleY(1.08)}70%{transform:translateY(0) scaleY(.94)}}
@keyframes lg-sway{0%,100%{transform:rotate(-1.4deg)}50%{transform:rotate(1.4deg)}}
@keyframes lg-ring{0%,100%{transform:rotate(0)}20%{transform:rotate(-14deg)}40%{transform:rotate(12deg)}60%{transform:rotate(-8deg)}80%{transform:rotate(5deg)}}
@keyframes lg-up{0%,100%{transform:none}50%{transform:translateY(-5px)}}
@keyframes lg-twinkle{0%,100%{opacity:.25;transform:scale(.8)}50%{opacity:1;transform:scale(1.15)}}
@keyframes btn-shine{from{transform:translateX(-130%)}to{transform:translateX(130%)}}
@media (prefers-reduced-motion: reduce){.footer .mark > g,.footer .stars circle{animation:none !important}}
'''
rep(".footer .mark .lg-tree,.footer .mark .lg-trunk{fill:var(--footer-ink)}\n.footer .mark .lg-ground{fill:rgba(255,255,255,.2)}\n", "")
rep(".footer .logo{color:var(--footer-ink);margin:0}", ".footer .logo{color:var(--footer-ink);margin:0}" + CSS)

# ---------- 3. JS ----------
JS = '''
/* ===== La souris fait vivre la page : parallaxe du logo animé, carte cadeau qui se penche ===== */
(function(){
  if (!window.matchMedia || !window.matchMedia('(hover:hover)').matches || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var hero = $('#v-accueil .plum'), logo = $('.hero-logo .pb-logo');
  if (hero && logo){
    var raf = null, px = 0, py = 0;
    hero.addEventListener('mousemove', function(e){
      var r = hero.getBoundingClientRect(); px = (e.clientX - r.left) / r.width * 2 - 1; py = (e.clientY - r.top) / r.height * 2 - 1;
      if (!raf) raf = requestAnimationFrame(function(){ raf = null; logo.style.setProperty('--px', px.toFixed(3)); logo.style.setProperty('--py', py.toFixed(3)); });
    });
    hero.addEventListener('mouseleave', function(){ logo.style.setProperty('--px', '0'); logo.style.setProperty('--py', '0'); });
  }
  $$('.gift-card').forEach(function(card){
    var box = card.parentElement;
    box.addEventListener('mousemove', function(e){
      var r = card.getBoundingClientRect(); var x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
      card.classList.add('tilting'); card.style.setProperty('--ry', (x * 14).toFixed(2) + 'deg'); card.style.setProperty('--rx', (-y * 12).toFixed(2) + 'deg');
    });
    box.addEventListener('mouseleave', function(){ card.classList.remove('tilting'); card.style.setProperty('--rx', '0deg'); card.style.setProperty('--ry', '0deg'); });
  });
})();
'''
anchor = "if (document.fonts && document.fonts.ready) document.fonts.ready.then(measureHeader);\n})();"
assert s.count(anchor) == 1
s = s.replace(anchor, anchor.replace('\n})();', '') + JS + '})();')
open(p, 'w', encoding='utf-8').write(s)
print('micro-animations en place')
