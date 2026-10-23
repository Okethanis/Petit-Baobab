/* Ambiance Petit Baobab : de petites choses de bébé et des feuilles de baobab tombent doucement sur la page,
   des bulles de bain montent et éclatent. Dessins maison, couleurs de la marque, jamais d'emoji.
   - Le jour : feuilles et fleurs de baobab, tétine, biberon, hochet, chausson, body, canard de bain, petits pieds, soleil.
   - Le soir (19 h – 6 h, heure du visiteur) : lunes et étoiles, comme au-dessus d'un berceau.
   - Quand on fait défiler la page, tout s'envole un peu, comme sous un souffle.
   Rien pour qui a demandé « moins d'animations », ni en mode économie de données, ni à l'impression. */
(function(){
  'use strict';
  try {
    if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var cn = navigator.connection; if (cn && cn.saveData) return;
  } catch (e) {}
  if (document.querySelector('.amb')) return;

  /* ---------- les dessins (même langage que le logo : formes rondes, aplats, vert / soleil / crème) ---------- */
  var S = {
    leaf: '<path class="abk-g1" stroke-width="2.4" d="M24 30q1.5 8-1 15"/>' +
      [-64, -32, 0, 32, 64].map(function(a, i){ return '<g transform="rotate(' + a + ' 24 30)"><path class="' + (i % 4 ? 'ab-g2' : 'ab-g1') + '" d="M24 30C18.5 24 18.5 14.5 24 7.5 29.5 14.5 29.5 24 24 30z"/><path class="abk-g3" stroke-width="1.1" d="M24 28V12"/></g>'; }).join(''),
    flower: '<path class="abk-g1" stroke-width="2" d="M24 1v12"/>' +
      [-78, -40, 40, 78].map(function(a){ return '<ellipse class="ab-c abk-s2" stroke-width=".8" transform="rotate(' + a + ' 24 16)" cx="24" cy="9.5" rx="4.4" ry="7.4"/>'; }).join('') +
      '<path class="ab-g1" d="M17.5 13.5Q24 23 30.5 13.5z"/><circle class="ab-w abk-c" stroke-width="1.4" cx="24" cy="29" r="8.5"/>' +
      [[20, 25], [24, 23.4], [28, 25], [29.6, 29], [28, 33], [24, 34.6], [20, 33], [18.4, 29], [24, 29]].map(function(p){ return '<circle class="ab-s1" cx="' + p[0] + '" cy="' + p[1] + '" r="1.25"/>'; }).join(''),
    fruit: '<path class="abk-g1" stroke-width="1.8" d="M24 2q1.5 6 0 11"/><ellipse class="ab-s1" cx="24" cy="28" rx="9" ry="15"/><path class="abk-c" stroke-width="1.6" d="M19.5 20q-2 8 0 15" opacity=".7"/><circle class="ab-c" cx="27" cy="24" r="1"/><circle class="ab-c" cx="28.5" cy="31" r="1"/><circle class="ab-c" cx="25" cy="36" r="1"/>',
    pacifier: '<ellipse class="ab-c abk-s1" stroke-width="1.2" cx="24" cy="38.5" rx="5.6" ry="6.6"/><circle class="abk-g1" stroke-width="3.2" cx="24" cy="12.5" r="6.5"/><path class="ab-s1" d="M7.5 26c0-5.2 7.3-8.4 16.5-8.4s16.5 3.2 16.5 8.4-7.3 8.4-16.5 8.4S7.5 31.2 7.5 26z"/><circle class="ab-c" cx="14.5" cy="26" r="2"/><circle class="ab-c" cx="33.5" cy="26" r="2"/><circle class="ab-g1" cx="24" cy="26" r="4.6"/>',
    bottle: '<path class="ab-s2" d="M19 13.5c0-4.5 2.2-9 5-9s5 4.5 5 9z"/><rect class="ab-c abk-g3" stroke-width="1.2" x="15.5" y="17" width="17" height="27" rx="5.5"/><path class="ab-w" d="M16.1 30.5h15.8v8a5 5 0 0 1-5 5h-5.8a5 5 0 0 1-5-5z"/><rect class="ab-g2" x="14.5" y="12" width="19" height="6.5" rx="2.4"/><path class="abk-g2" stroke-width="1.5" d="M26.5 23h3.5M26.5 27h3.5M26.5 31h3.5"/>',
    rattle: '<path class="abk-g2" stroke-width="5" d="M27 27l10.5 12"/><circle class="abk-g1" stroke-width="2.6" cx="39.5" cy="41.5" r="3.6"/><circle class="ab-g1" cx="27.5" cy="27.5" r="3.3"/><circle class="ab-s1" cx="19.5" cy="19.5" r="12.5"/><circle class="ab-c" cx="14" cy="16" r="2.2"/><circle class="ab-c" cx="22" cy="12.5" r="2.2"/><circle class="ab-c" cx="18" cy="24" r="2.2"/><circle class="ab-c" cx="25.5" cy="21" r="2.2"/>',
    bootie: '<path class="ab-g3" d="M12.5 13.5h15v12.5c0 2.2 1.6 3.4 4.4 4.3l5.2 1.8c3.3 1.1 4.6 3.3 4.6 5.6v.8c0 2.4-2 3.5-4.4 3.5H17.5c-3 0-5-2.1-5-5z"/><path class="abk-g1" stroke-width="1.6" d="M12.8 40.5h28.6"/><rect class="ab-c" x="11" y="7.5" width="18" height="8" rx="3.4"/><path class="abk-c" stroke-width="2" d="M19 28.5q6-3.4 11 1.8"/><circle class="ab-s1" cx="31.5" cy="28" r="3.2"/>',
    onesie: '<path class="ab-c abk-g3" stroke-width="1.2" d="M17 6q7 6.5 14 0l9.5 5.2-3.3 8.3-4.2-2V36c0 4.2-2.8 6.5-6.5 7.2h-5c-3.7-.7-6.5-3-6.5-7.2V17.5l-4.2 2-3.3-8.3z"/><path class="abk-g2" stroke-width="2" d="M17 6q7 6.5 14 0"/><path class="ab-s1" d="M24 27.5c-3.4-2.3-5-4.2-5-6.2a2.6 2.6 0 0 1 5-1 2.6 2.6 0 0 1 5 1c0 2-1.6 3.9-5 6.2z"/><circle class="ab-g2" cx="21" cy="40" r="1.2"/><circle class="ab-g2" cx="24" cy="40.8" r="1.2"/><circle class="ab-g2" cx="27" cy="40" r="1.2"/>',
    duck: '<path class="ab-s2" d="M7.5 29.5Q5.5 23 11 24.8 15 22 22 23l8.5 1.2Q38.5 26 38.5 32.5 38.5 41.5 24 41.5 9.5 41.5 7.5 29.5z"/><circle class="ab-s2" cx="31" cy="16.5" r="8.2"/><path class="ab-s1" d="M38.3 16.5q6.2-.4 7.2 2.2-3.2 3.2-8.3 1.8z"/><circle class="ab-ink" cx="33" cy="14.6" r="1.6"/><circle class="ab-w" cx="33.6" cy="14" r=".5"/><path class="abk-s1" stroke-width="2" d="M15.5 31.5q6.5 5.2 13 0"/>',
    foot: '<path class="ab-g3" d="M17.5 21.5c4-3.5 12.8-2 14.2 6.8 1.1 7-1.2 13.8-6.7 15.2-4.6 1.2-8.5-1.4-8.5-6.4 0-3.6 2.4-5.3 1.6-9-.4-2.6-3.6-4.4-.6-6.6z"/><circle class="ab-g3" cx="16.5" cy="15.5" r="3.4"/><circle class="ab-g3" cx="22" cy="11.2" r="3"/><circle class="ab-g3" cx="27.3" cy="10.3" r="2.6"/><circle class="ab-g3" cx="31.6" cy="12.4" r="2.3"/><circle class="ab-g3" cx="34.8" cy="16" r="2"/>',
    star: '<path class="ab-s2 abk-s2" stroke-width="3.4" d="M24 6.5l5.3 10.8 11.9 1.7-8.6 8.4 2 11.8L24 33.6l-10.6 5.6 2-11.8-8.6-8.4 11.9-1.7z"/>',
    moon: '<path class="ab-c abk-s2" stroke-width="1.6" d="M30.5 6.5A17.5 17.5 0 1 0 42 36.2 14 14 0 1 1 30.5 6.5z"/><path class="abk-g1" stroke-width="1.7" d="M15.5 27.5q3 2.8 6 0"/><circle class="ab-s1" cx="14.6" cy="32.4" r="1.6" opacity=".55"/>',
    heart: '<path class="ab-s1" d="M24 41C12.2 33.2 6.5 26.2 6.5 18.6a8.8 8.8 0 0 1 17.5-2.4 8.8 8.8 0 0 1 17.5 2.4c0 7.6-5.7 14.6-17.5 22.4z"/><path class="abk-c" stroke-width="2.2" d="M12 17.5a4.5 4.5 0 0 1 4-4" opacity=".8"/>',
    sun: [0, 45, 90, 135, 180, 225, 270, 315].map(function(a){ return '<path class="abk-s2" stroke-width="2.8" transform="rotate(' + a + ' 24 24)" d="M24 6.5v4.5"/>'; }).join('') + '<circle class="ab-s1" cx="24" cy="24" r="9.5"/>',
    bubble: '<circle class="ab-bub" stroke-width="1.7" cx="24" cy="24" r="16.5"/><path class="abk-w" stroke-width="2.6" d="M14.5 19.5a11 11 0 0 1 7-7.4"/><circle class="ab-w" cx="31.5" cy="31" r="1.6" opacity=".9"/>'
  };

  /* ---------- qui tombe, quand ---------- */
  var h = new Date().getHours(), night = h >= 19 || h < 6;
  var small = (window.innerWidth || 1024) < 760;
  var FAM = {
    leaf:   { pool: night ? ['leaf', 'leaf', 'flower', 'star'] : ['leaf', 'leaf', 'leaf', 'flower', 'fruit'], sz: [20, 31], d: [17, 27], fl: [2.6, 4.4] },
    item:   { pool: night ? ['moon', 'moon', 'pacifier', 'bottle', 'bootie', 'onesie', 'star', 'duck'] : ['pacifier', 'bottle', 'rattle', 'bootie', 'onesie', 'duck', 'foot', 'foot'], sz: [22, 33], d: [23, 35], fl: [2.8, 4.2] },
    spark:  { pool: night ? ['star', 'star', 'moon', 'heart'] : ['star', 'heart', 'sun', 'heart'], sz: [14, 22], d: [19, 30], fl: [2.4, 4] },
    bubble: { pool: ['bubble'], sz: [16, 34], d: [13, 21], fl: [1.6, 2.6] }
  };
  var PLAN = small ? { leaf: 4, item: 4, spark: night ? 2 : 1, bubble: 2 } : { leaf: 6, item: 6, spark: night ? 4 : 3, bubble: 3 };
  if (small) { FAM.leaf.sz = [17, 25]; FAM.item.sz = [19, 27]; FAM.spark.sz = [12, 18]; FAM.bubble.sz = [14, 27]; }

  function rnd(a, b){ return a + Math.random() * (b - a); }
  function pick(a){ return a[Math.floor(Math.random() * a.length)]; }

  var root = document.createElement('div');
  root.className = 'amb'; root.setAttribute('aria-hidden', 'true');
  root.innerHTML = '<svg class="amb-defs" width="0" height="0" focusable="false"><defs>' +
    Object.keys(S).map(function(k){ return '<symbol id="a-' + k + '" viewBox="0 0 48 48">' + S[k] + '</symbol>'; }).join('') + '</defs></svg><div class="amb-wind"></div>';
  var wind = root.lastChild;

  // positions réparties sur la largeur (pas de paquets), puis mélangées entre familles
  var slots = [];
  Object.keys(PLAN).forEach(function(f){ for (var i = 0; i < PLAN[f]; i++) slots.push(f); });
  var N = slots.length;
  slots.sort(function(){ return Math.random() - .5; });
  slots.forEach(function(f, i){
    var F = FAM[f], d = rnd(F.d[0], F.d[1]);
    var el = document.createElement('span');
    el.className = 'amb-i amb-' + f;
    var st = el.style;
    st.setProperty('--x', ((i + rnd(.15, .85)) / N * 96 + 1).toFixed(2) + 'vw');
    st.setProperty('--d', d.toFixed(2) + 's');
    st.setProperty('--dl', (-rnd(0, d)).toFixed(2) + 's');
    st.setProperty('--sw', rnd(4.5, 8).toFixed(2) + 's');
    st.setProperty('--amp', rnd(10, f === 'leaf' ? 38 : 26).toFixed(0) + 'px');
    st.setProperty('--fl', rnd(F.fl[0], F.fl[1]).toFixed(2) + 's');
    st.setProperty('--r', Math.random() < .5 ? '-1' : '1');
    st.setProperty('--ph', rnd(48, 92).toFixed(0) + 'vh');
    dress(el, f);
    el.innerHTML = '<span class="amb-sw"><svg class="amb-in" viewBox="0 0 48 48" focusable="false"><use href="#a-' + el.dataset.k + '"/></svg></span>';
    // à chaque passage, l'élément revient sous une autre forme, ailleurs
    el.addEventListener('animationiteration', function(e){
      if (e.target !== el) return;
      dress(el, f);
      el.style.setProperty('--x', rnd(2, 96).toFixed(2) + 'vw');
      var u = el.querySelector('use'); if (u) u.setAttribute('href', '#a-' + el.dataset.k);
    });
    wind.appendChild(el);
  });
  function dress(el, f){
    var F = FAM[f], k = pick(F.pool);
    el.dataset.k = k;
    el.style.setProperty('--s', rnd(F.sz[0], F.sz[1]).toFixed(1) + 'px');
    el.style.setProperty('--o', (k === 'bubble' ? rnd(.75, .95) : rnd(.82, 1)).toFixed(2));
  }

  function mount(){
    document.body.appendChild(root);
    setTimeout(function(){ root.classList.add('on'); }, 900);
  }
  if (document.body) mount(); else document.addEventListener('DOMContentLoaded', mount);

  /* ---------- un souffle quand on fait défiler ---------- */
  var lastY = window.scrollY || 0, lastT = 0, lift = 0, target = 0, running = false;
  window.addEventListener('scroll', function(){
    var now = performance.now(), y = window.scrollY || 0;
    if (lastT) { var v = (y - lastY) / Math.max(16, now - lastT); target = Math.max(-70, Math.min(70, target - v * 22)); }
    lastY = y; lastT = now;
    if (!running) { running = true; requestAnimationFrame(step); }
  }, { passive: true });
  function step(){
    target *= .9; lift += (target - lift) * .12;
    wind.style.transform = 'translate3d(' + (lift * -.25).toFixed(1) + 'px,' + lift.toFixed(1) + 'px,0)';
    if (Math.abs(lift) > .3 || Math.abs(target) > .3) requestAnimationFrame(step);
    else { running = false; lift = target = 0; wind.style.transform = ''; }
  }
})();
