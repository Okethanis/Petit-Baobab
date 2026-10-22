"""Motion design sur téléphone et tablette : le doigt remplace la souris.
   - toucher un élément déclenche la même micro-animation que le survol (classe .tapped pendant 1 s, annulée si le doigt fait défiler),
   - toucher le baobab du haut de page le fait repousser (toutes plateformes),
   - le soleil du haut de page se couche quand on fait défiler la page (téléphone),
   - toucher le soleil du pied de page fait jaillir les rayons avant de passer en mode nuit,
   - un peu de vie permanente : l'illustration de « Notre histoire » respire, le bouton WhatsApp s'agite toutes les 7 s.
   Idempotent : relancer ne double rien."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, '..', 'petit-baobab.html'); s = open(p, encoding='utf-8').read()
if 'touch-motion' in s:
    print('déjà en place'); raise SystemExit

CSS = '''
/* ===== touch-motion : sur téléphone et tablette, toucher = animer, plus un peu de vie permanente ===== */
.pb-logo.still,.pb-logo.still *{animation:none !important}
.hero-logo .pb-logo{cursor:pointer;-webkit-tap-highlight-color:transparent}
@media (hover:none) and (prefers-reduced-motion: no-preference){
  .logo .mark > g:nth-of-type(1){transform-origin:104px 18px}
  .logo.tapped .mark > g:nth-of-type(1){animation:lg-hop .7s var(--spring)}
  .logo .mark > g:nth-of-type(4){transform-origin:59px 58px}
  .logo.tapped .mark > g:nth-of-type(4){animation:lg-shake .8s var(--ease)}
  .logo .mark > g:nth-of-type(6),.logo .mark > g:nth-of-type(7),.logo .mark > g:nth-of-type(8){transform-origin:99px 110px}
  .logo.tapped .mark > g:nth-of-type(6),.logo.tapped .mark > g:nth-of-type(7),.logo.tapped .mark > g:nth-of-type(8){animation:lg-jump .6s var(--spring) .15s}
  .baobab-illus > g:nth-of-type(4){transform-origin:59px 58px;animation:lg-sway 6s ease-in-out infinite}
  .baobab-illus > g:nth-of-type(7){transform-origin:99px 88px;animation:lg-sway 4.5s ease-in-out 1s infinite reverse}
  .baobab-illus > g:nth-of-type(1){transform-origin:104px 18px;animation:pb-glow 5s ease-in-out infinite}
  .baobab-illus.tapped > g:nth-of-type(1){animation:lg-hop .8s var(--spring)}
  .baobab-illus.tapped > g:nth-of-type(6),.baobab-illus.tapped > g:nth-of-type(7),.baobab-illus.tapped > g:nth-of-type(8){transform-origin:99px 110px;animation:lg-jump .7s var(--spring)}
  .card.tapped .add{animation:lg-quarter .5s var(--spring)}
  .univ-card.tapped .num{animation:lg-spin .7s var(--spring)}
  .univ-card.tapped .icon{animation:lg-up .5s var(--ease)}
  .who-card.tapped .go svg{animation:lg-nudge .5s var(--spring)}
  .who-card.tapped h3{letter-spacing:.07em;transition:letter-spacing .3s var(--ease)}
  .chip.tapped,.value.tapped,.gift-box.tapped,.stage.tapped,.btn.tapped{animation:lg-press .45s var(--spring)}
  .tstep.tapped .num{animation:lg-hop .6s var(--spring)}
  .value.tapped h3 i{animation:lg-dot .5s var(--spring)}
  .btn-primary{overflow:hidden}
  .btn-primary::after{content:"";position:absolute;inset:0;background:linear-gradient(105deg,transparent 35%,rgba(255,255,255,.55) 50%,transparent 65%);transform:translateX(-130%);pointer-events:none}
  .btn-primary.tapped::after{animation:btn-shine .8s var(--ease)}
  .fab-wa .icon{animation:lg-ring-idle 7s ease-in-out 4s infinite}
  .fab-wa.tapped .icon{animation:lg-ring .6s var(--ease)}
  .fab-top.tapped .icon{animation:lg-up .6s var(--ease)}
  .footer-scene.tapped .mark > g:nth-of-type(4){animation:lg-shake .8s var(--ease)}
  .footer-scene.tapped .mark > g:nth-of-type(7){animation:lg-jump .6s var(--spring)}
  .footer-brand.sun-tap .rays{opacity:1;transform:scale(1)}
  .footer-brand.sun-tap .lg-sun > circle:first-of-type{transform:translateY(-4px) scale(1.15)}
  .pb-logo .plx-sun,.pb-logo .plx-tree{transition:transform .6s var(--ease)}
}
@keyframes lg-spin{from{transform:rotate(0) scale(1)}60%{transform:rotate(360deg) scale(1.12)}to{transform:rotate(360deg) scale(1)}}
@keyframes lg-quarter{0%{transform:none}50%{transform:rotate(90deg) scale(1.1)}100%{transform:none}}
@keyframes lg-nudge{0%,100%{transform:none}50%{transform:translateX(6px)}}
@keyframes lg-press{0%{transform:none}40%{transform:scale(.96)}100%{transform:none}}
@keyframes lg-dot{0%,100%{transform:none}50%{transform:scale(1.6)}}
@keyframes lg-ring-idle{0%,12%,100%{transform:rotate(0)}2%{transform:rotate(-14deg)}5%{transform:rotate(12deg)}8%{transform:rotate(-8deg)}10%{transform:rotate(5deg)}}
'''
anchor_css = "@media (prefers-reduced-motion: reduce){.footer .mark > g,.footer .stars circle{animation:none !important}}\n"
assert s.count(anchor_css) == 1
s = s.replace(anchor_css, anchor_css + CSS)

JS = '''/* ===== touch-motion : toucher = animer, le baobab repousse, le soleil suit le défilement ===== */
(function(){
  if (!window.matchMedia || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var logo = $('.hero-logo .pb-logo');
  if (logo) logo.addEventListener('click', function(){ if (logo.classList.contains('is3d')) return; logo.classList.add('still'); void logo.offsetWidth; logo.classList.remove('still'); });
  if (!window.matchMedia('(hover:none)').matches) return;
  var SEL = '.logo,.baobab-illus,.card,.univ-card,.who-card,.chip,.btn,.value,.gift-box,.stage,.tstep,.fab-wa,.fab-top,.footer-scene';
  var pend = null;
  function fire(el){ el.classList.remove('tapped'); void el.offsetWidth; el.classList.add('tapped'); clearTimeout(el._tapT); el._tapT = setTimeout(function(){ el.classList.remove('tapped'); }, 1000); }
  document.addEventListener('pointerdown', function(e){
    if (e.pointerType === 'mouse') return;
    var el = e.target.closest(SEL); if (!el) return;
    pend = { el: el, x: e.clientX, y: e.clientY, t: setTimeout(function(){ if (pend) { fire(pend.el); pend = null; } }, 90) };
  }, {passive:true});
  document.addEventListener('pointermove', function(e){ if (pend && Math.hypot(e.clientX - pend.x, e.clientY - pend.y) > 8) { clearTimeout(pend.t); pend = null; } }, {passive:true});
  document.addEventListener('pointerup', function(){ if (pend) { clearTimeout(pend.t); fire(pend.el); pend = null; } }, {passive:true});
  document.addEventListener('pointercancel', function(){ if (pend) { clearTimeout(pend.t); pend = null; } }, {passive:true});
  var sun = $('.sun-toggle'), fb = $('.footer-brand');
  if (sun && fb) sun.addEventListener('pointerdown', function(){ fb.classList.add('sun-tap'); setTimeout(function(){ fb.classList.remove('sun-tap'); }, 900); }, {passive:true});
  var hero = $('#v-accueil .plum');
  if (hero && logo){
    var raf = null;
    var onS = function(){ if (raf) return; raf = requestAnimationFrame(function(){ raf = null; var y = Math.max(0, Math.min(1, window.scrollY / Math.max(1, hero.offsetHeight))); logo.style.setProperty('--py', (y * 3).toFixed(3)); logo.style.setProperty('--px', (y * 1.2).toFixed(3)); }); };
    window.addEventListener('scroll', onS, {passive:true}); onS();
  }
})();
'''
anchor_js = "  });\n})();\n})();\n</script>"
assert s.count(anchor_js) == 1
s = s.replace(anchor_js, "  });\n})();\n" + JS + "})();\n</script>")
open(p, 'w', encoding='utf-8').write(s)
print('touch-motion en place')
