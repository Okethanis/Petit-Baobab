/* Ambiance Petit Baobab : de petites choses de bébé tombent doucement sur la page, une cigogne traverse avec son baluchon,
   des bulles de bain montent et éclatent. Dessins maison, couleurs de la marque, jamais d'emoji.
   - Le jour : tétine, biberon, hochet, chausson, body, petits pieds, étoiles, cœurs, soleil.
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
    pacifier: '<ellipse class="ab-c abk-s1" stroke-width="1.2" cx="24" cy="38.5" rx="5.6" ry="6.6"/><circle class="abk-g1" stroke-width="3.2" cx="24" cy="12.5" r="6.5"/><path class="ab-s1" d="M7.5 26c0-5.2 7.3-8.4 16.5-8.4s16.5 3.2 16.5 8.4-7.3 8.4-16.5 8.4S7.5 31.2 7.5 26z"/><circle class="ab-c" cx="14.5" cy="26" r="2"/><circle class="ab-c" cx="33.5" cy="26" r="2"/><circle class="ab-g1" cx="24" cy="26" r="4.6"/>',
    bottle: '<path class="ab-s2" d="M19 13.5c0-4.5 2.2-9 5-9s5 4.5 5 9z"/><rect class="ab-c abk-g3" stroke-width="1.2" x="15.5" y="17" width="17" height="27" rx="5.5"/><path class="ab-w" d="M16.1 30.5h15.8v8a5 5 0 0 1-5 5h-5.8a5 5 0 0 1-5-5z"/><rect class="ab-g2" x="14.5" y="12" width="19" height="6.5" rx="2.4"/><path class="abk-g2" stroke-width="1.5" d="M26.5 23h3.5M26.5 27h3.5M26.5 31h3.5"/>',
    rattle: '<path class="abk-g2" stroke-width="5" d="M27 27l10.5 12"/><circle class="abk-g1" stroke-width="2.6" cx="39.5" cy="41.5" r="3.6"/><circle class="ab-g1" cx="27.5" cy="27.5" r="3.3"/><circle class="ab-s1" cx="19.5" cy="19.5" r="12.5"/><circle class="ab-c" cx="14" cy="16" r="2.2"/><circle class="ab-c" cx="22" cy="12.5" r="2.2"/><circle class="ab-c" cx="18" cy="24" r="2.2"/><circle class="ab-c" cx="25.5" cy="21" r="2.2"/>',
    bootie: '<path class="ab-g3" d="M12.5 13.5h15v12.5c0 2.2 1.6 3.4 4.4 4.3l5.2 1.8c3.3 1.1 4.6 3.3 4.6 5.6v.8c0 2.4-2 3.5-4.4 3.5H17.5c-3 0-5-2.1-5-5z"/><path class="abk-g1" stroke-width="1.6" d="M12.8 40.5h28.6"/><rect class="ab-c" x="11" y="7.5" width="18" height="8" rx="3.4"/><path class="abk-c" stroke-width="2" d="M19 28.5q6-3.4 11 1.8"/><circle class="ab-s1" cx="31.5" cy="28" r="3.2"/>',
    onesie: '<path class="ab-c abk-g3" stroke-width="1.2" d="M17 6q7 6.5 14 0l9.5 5.2-3.3 8.3-4.2-2V36c0 4.2-2.8 6.5-6.5 7.2h-5c-3.7-.7-6.5-3-6.5-7.2V17.5l-4.2 2-3.3-8.3z"/><path class="abk-g2" stroke-width="2" d="M17 6q7 6.5 14 0"/><path class="ab-s1" d="M24 27.5c-3.4-2.3-5-4.2-5-6.2a2.6 2.6 0 0 1 5-1 2.6 2.6 0 0 1 5 1c0 2-1.6 3.9-5 6.2z"/><circle class="ab-g2" cx="21" cy="40" r="1.2"/><circle class="ab-g2" cx="24" cy="40.8" r="1.2"/><circle class="ab-g2" cx="27" cy="40" r="1.2"/>',
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
    item:   { pool: night ? ['moon', 'moon', 'pacifier', 'bottle', 'bootie', 'onesie', 'star'] : ['pacifier', 'bottle', 'rattle', 'bootie', 'onesie', 'foot', 'foot'], sz: [22, 33], d: [23, 35], fl: [2.8, 4.2] },
    spark:  { pool: night ? ['star', 'star', 'moon', 'heart'] : ['star', 'heart', 'sun', 'heart'], sz: [14, 22], d: [19, 30], fl: [2.4, 4] },
    bubble: { pool: ['bubble'], sz: [16, 34], d: [13, 21], fl: [1.6, 2.6] }
  };
  var PLAN = small ? { item: 3, spark: 1, bubble: 1 } : { item: 5, spark: 2, bubble: 2 };
  if (small) { FAM.item.sz = [19, 27]; FAM.spark.sz = [12, 18]; FAM.bubble.sz = [14, 27]; }

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
    st.setProperty('--amp', rnd(10, 26).toFixed(0) + 'px');
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

  /* ---------- la cigogne : elle traverse la page (et le texte) avec un bébé dans son baluchon ---------- */
  var stork = document.createElement('div');
  stork.className = 'amb-stork';
  stork.innerHTML = '<div class="amb-stork-bob"><svg viewBox="0 0 130 92" focusable="false">' +
    '<path class="sk-leg" d="M44 47 18 58M47 48 22 62"/>' +
    '<path class="sk-wing sk-far" d="M57 35C50 22 44 12 30 6c10 9 13 19 18 30z"/>' +
    '<path class="sk-tail" d="M33 37l-11-3 9 8z"/>' +
    '<ellipse class="sk-body" cx="55" cy="41" rx="24" ry="10.5"/>' +
    '<path class="sk-body" d="M73 37c6-3 9-8 11-13l6 2c-2 7-6 13-13 17z"/>' +
    '<circle class="sk-body" cx="89" cy="23" r="6.5"/>' +
    '<path class="sk-beak" d="M94 21.5 117 26.5 94 26z"/>' +
    '<circle class="sk-eye" cx="90.5" cy="21.5" r="1.3"/>' +
    '<g class="sk-wing sk-near"><path class="sk-body" d="M62 36C56 22 46 9 28 2c9 10 12 24 20 36z"/><path class="sk-tip" d="M28 2c9 10 12 24 20 36l-6-1C37 26 33 14 28 2z"/></g>' +
    '<g class="sk-bundle"><path class="sk-knot" d="M114 27.5 107 44M114 27.5l5 17"/>' +
    '<path class="sk-cloth" d="M100 46c0-4 6-6 13-6s13 2 13 6c0 12-5 22-13 22s-13-10-13-22z"/>' +
    '<circle class="sk-face" cx="113" cy="52" r="6.2"/><path class="sk-eyes" d="M109.8 51.6q1.2 1 2.2 0M114 51.6q1.2 1 2.2 0"/>' +
    '<path class="sk-fold" d="M101 58q12 5 24 0"/><circle class="sk-dot" cx="106" cy="63" r="1.3"/><circle class="sk-dot" cx="120" cy="62" r="1.3"/>' +
    '<circle class="sk-tie" cx="113" cy="41" r="2.6"/></g>' +
    '</svg></div>';
  wind.appendChild(stork);
  function flyStork(){
    var ltr = Math.random() < .7;   // le plus souvent de gauche à droite, parfois dans l'autre sens
    stork.classList.remove('fly', 'rtl'); void stork.offsetWidth;
    stork.style.setProperty('--y', rnd(18, 62).toFixed(0) + 'vh');
    stork.style.setProperty('--fd', (small ? rnd(9, 11) : rnd(13, 16)).toFixed(1) + 's');
    if (!ltr) stork.classList.add('rtl');
    stork.classList.add('fly');
  }
  stork.addEventListener('animationend', function(e){
    if (e.target !== stork) return;
    stork.classList.remove('fly');
    setTimeout(flyStork, rnd(20, 34) * 1000);
  });
  setTimeout(flyStork, 5000);

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
