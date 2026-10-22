/* ===== hero3d : le logo en 3D (three.js), en haut de l'accueil =====
   Un petit baobab pousse à partir d'une graine, le soleil se lève, un fruit tombe et fait naître le second baobab.
   Ensuite la scène vit : feuillages qui ondulent, caméra qui tourne doucement, parallaxe à la souris ou au défilement.
   Toucher la scène = coup de vent et un fruit tombe. Toucher le soleil = tout repousse.
   Sans WebGL, avec « réduire les animations » ou en mode économie de données, l'animation vectorielle reste en place. */
(function(){
  if (!window.matchMedia || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (navigator.connection && navigator.connection.saveData) return;
  var logo = document.querySelector('.hero-logo .pb-logo'); if (!logo) return;
  var scene2d = logo.querySelector('.pb-scene'); if (!scene2d) return;
  var pathMode = /^https?:$/.test(location.protocol) && !/\.html$/.test(location.pathname);
  var SRC = (pathMode ? '/' : '') + 'vendor/three.min.js';
  var started = false;

  function boot(){
    if (started) return; started = true;
    var s = document.createElement('script'); s.src = SRC; s.async = true;
    s.onload = function(){ try { init(); } catch (e) { /* on garde l'animation vectorielle */ } };
    document.head.appendChild(s);
  }
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function(es){ es.forEach(function(en){ if (en.isIntersecting) { io.disconnect(); boot(); } }); }, { rootMargin: '200px' });
    io.observe(logo);
  } else boot();

  // ---------- outils ----------
  var ease = {
    out: function(t){ return 1 - Math.pow(1 - t, 3); },
    inout: function(t){ return t < .5 ? 4*t*t*t : 1 - Math.pow(-2*t + 2, 3) / 2; },
    spring: function(t){ return 1 - Math.pow(2, -8*t) * Math.cos(t * 7.5); },   // dépasse un peu puis se pose
    bounce: function(t){ var n = 7.5625, d = 2.75; if (t < 1/d) return n*t*t; if (t < 2/d) return n*(t -= 1.5/d)*t + .75; if (t < 2.5/d) return n*(t -= 2.25/d)*t + .9375; return n*(t -= 2.625/d)*t + .984375; }
  };
  function seg(t, a, b, fn){ if (t <= a) return 0; if (t >= b) return 1; var k = (t - a) / (b - a); return fn ? fn(k) : k; }
  function L(x, y){ return [(x - 60) / 15, (110 - y) / 15]; }   // repère du logo (viewBox 120) → unités 3D (sol en y=0)

  function init(){
    var THREE = window.THREE; if (!THREE) return;
    var touch = window.matchMedia('(hover:none)').matches;
    var renderer;
    try { renderer = new THREE.WebGLRenderer({ alpha: true, antialias: !touch, powerPreference: 'low-power' }); } catch (e) { return; }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, touch ? 1.5 : 2));
    renderer.setClearColor(0x000000, 0);
    renderer.outputEncoding = THREE.sRGBEncoding;
    if (!touch) { renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap; }
    var canvas = renderer.domElement; canvas.className = 'pb-3d'; canvas.setAttribute('aria-hidden', 'true');
    scene2d.insertAdjacentElement('afterend', canvas);
    logo.classList.add('is3d');
    // les lettres repartent en même temps que la pousse 3D
    logo.classList.add('still'); void logo.offsetWidth; logo.classList.remove('still');

    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(32, 400 / 284, 0.1, 100);
    var target = new THREE.Vector3(0.5, 3.1, 0);

    // dégradé « toon » en trois paliers : des aplats comme sur le logo, mais avec du volume
    var grad = new THREE.DataTexture(new Uint8Array([90, 170, 255]), 3, 1, THREE.LuminanceFormat);
    grad.minFilter = THREE.NearestFilter; grad.magFilter = THREE.NearestFilter; grad.needsUpdate = true;
    function toon(hex){ return new THREE.MeshToonMaterial({ color: hex, gradientMap: grad }); }
    var mLeaf = toon(0xE1EFE5), mTrunk = toon(0xF5F7F2), mFruit = toon(0xF2A93B);
    var mShadow = new THREE.MeshBasicMaterial({ color: 0x08261A, transparent: true, opacity: touch ? .3 : .16, depthWrite: false });

    scene.add(new THREE.HemisphereLight(0xFFF6E6, 0x174F38, 1.0));
    var sunLight = new THREE.DirectionalLight(0xFFE2B0, 0.95); sunLight.position.set(5, 8, 6);
    if (!touch) { sunLight.castShadow = true; sunLight.shadow.mapSize.set(1024, 1024); sunLight.shadow.camera.left = -6; sunLight.shadow.camera.right = 6; sunLight.shadow.camera.top = 9; sunLight.shadow.camera.bottom = -1; sunLight.shadow.radius = 4; }
    scene.add(sunLight);

    // ---------- sol ----------
    var ground = new THREE.Mesh(new THREE.CircleGeometry(3.9, 48), new THREE.MeshBasicMaterial({ color: 0xF5F7F2, transparent: true, opacity: .2, depthWrite: false }));
    ground.rotation.x = -Math.PI / 2; ground.position.y = 0.001; ground.scale.set(1, 0.42, 1); scene.add(ground);
    var floor = new THREE.Mesh(new THREE.PlaneGeometry(14, 10), new THREE.ShadowMaterial({ opacity: .22 }));
    floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);

    // ---------- grand baobab ----------
    var big = new THREE.Group(); scene.add(big);
    var trunkPts = [[0.98, 0], [0.92, 0.5], [0.74, 1.2], [0.6, 2.0], [0.6, 2.7], [0.76, 3.25], [1.02, 3.65], [0.7, 3.85], [0, 3.9]].map(function(p){ return new THREE.Vector2(p[0], p[1]); });
    var trunk = new THREE.Mesh(new THREE.LatheGeometry(trunkPts, 28), mTrunk); trunk.castShadow = !touch; big.add(trunk);
    var canopy = new THREE.Group(); canopy.position.y = 3.9; big.add(canopy);   // pivot au sommet du tronc pour l'ondulation
    var leaves = [[59, 44, 26, 0], [33, 54, 17, .55], [85, 54, 17, -.55], [43, 30, 15, -.5], [75, 30, 15, .5], [59, 22, 13, .15]].map(function(c){
      var p = L(c[0], c[1]); var m = new THREE.Mesh(new THREE.SphereGeometry(c[2] / 15, 28, 20), mLeaf);
      m.position.set(p[0], p[1] - 3.9, c[3]); m.castShadow = !touch; m.scale.setScalar(0.0001); canopy.add(m); return m;
    });
    var fp = L(71, 40); var fruit = new THREE.Mesh(new THREE.SphereGeometry(.2, 16, 12), mFruit); fruit.position.set(fp[0], fp[1] - 3.9, 1.72); fruit.scale.setScalar(0.0001); canopy.add(fruit);
    var shadowBig = new THREE.Mesh(new THREE.CircleGeometry(1.1, 32), mShadow); shadowBig.rotation.x = -Math.PI / 2; shadowBig.position.y = 0.002; shadowBig.scale.set(1.4, .5, 1); scene.add(shadowBig);

    // ---------- petit baobab ----------
    var small = new THREE.Group(); small.position.x = L(99, 0)[0]; scene.add(small);
    var sPts = [[0.3, 0], [0.26, 0.4], [0.2, 0.8], [0.26, 1.15], [0.34, 1.3], [0, 1.35]].map(function(p){ return new THREE.Vector2(p[0], p[1]); });
    var sTrunk = new THREE.Mesh(new THREE.LatheGeometry(sPts, 20), mTrunk); sTrunk.castShadow = !touch; small.add(sTrunk);
    var sCanopy = new THREE.Group(); sCanopy.position.y = 1.35; small.add(sCanopy);
    var sLeaves = [[99, 82, 9.5, 0], [91, 87, 5.5, .3], [107, 87, 5.5, -.3]].map(function(c){
      var p = L(c[0], c[1]); var m = new THREE.Mesh(new THREE.SphereGeometry(c[2] / 15, 24, 16), mLeaf);
      m.position.set(p[0] - small.position.x, p[1] - 1.35, c[3]); m.castShadow = !touch; m.scale.setScalar(0.0001); sCanopy.add(m); return m;
    });
    var sfp = L(103, 80); var sFruit = new THREE.Mesh(new THREE.SphereGeometry(.13, 14, 10), mFruit); sFruit.position.set(sfp[0] - small.position.x, sfp[1] - 1.35, .66); sFruit.scale.setScalar(0.0001); sCanopy.add(sFruit);
    var shadowSmall = new THREE.Mesh(new THREE.CircleGeometry(.5, 24), mShadow); shadowSmall.rotation.x = -Math.PI / 2; shadowSmall.position.set(small.position.x, 0.002, 0); shadowSmall.scale.set(1.3, .5, 1); scene.add(shadowSmall);

    // ---------- soleil ----------
    var sunPos = L(104, 18); var sunHome = new THREE.Vector3(sunPos[0] + .3, sunPos[1], -2.6);
    var sun = new THREE.Mesh(new THREE.SphereGeometry(.68, 32, 24), new THREE.MeshBasicMaterial({ color: 0xF2A93B })); scene.add(sun);
    var glowCanvas = document.createElement('canvas'); glowCanvas.width = glowCanvas.height = 128;
    var g = glowCanvas.getContext('2d'); var rg = g.createRadialGradient(64, 64, 10, 64, 64, 64); rg.addColorStop(0, 'rgba(242,169,59,.55)'); rg.addColorStop(.5, 'rgba(242,169,59,.18)'); rg.addColorStop(1, 'rgba(242,169,59,0)'); g.fillStyle = rg; g.fillRect(0, 0, 128, 128);
    var glowTex = new THREE.CanvasTexture(glowCanvas);
    var glow = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending })); glow.scale.set(3.6, 3.6, 1); scene.add(glow);

    // ---------- graine et fruits qui tombent ----------
    var seed = new THREE.Mesh(new THREE.SphereGeometry(.17, 14, 10), mFruit); seed.visible = false; scene.add(seed);
    var falling = [];
    function dropFruit(from, to){ var f = new THREE.Mesh(new THREE.SphereGeometry(.17, 14, 10), mFruit); f.position.copy(from); scene.add(f); falling.push({ m: f, from: from.clone(), to: to.clone(), t: 0 }); }

    // ---------- état ----------
    var T0 = performance.now(), paused = false, visible = true, gust = 0, gustV = 0, px = 0, py = 0, tpx = 0, tpy = 0, frame = 0;
    var seedDropped = false;
    function replay(){ T0 = performance.now(); seedDropped = false; falling.forEach(function(f){ scene.remove(f.m); }); falling = []; logo.classList.add('still'); void logo.offsetWidth; logo.classList.remove('still'); }

    function layout(){
      var w = logo.clientWidth || 250, h = Math.round(w * 284 / 400);
      renderer.setSize(w, h, false); canvas.style.width = w + 'px'; canvas.style.height = h + 'px';
      camera.aspect = w / h; camera.updateProjectionMatrix();
    }
    layout();
    if ('ResizeObserver' in window) new ResizeObserver(layout).observe(logo); else window.addEventListener('resize', layout);
    if ('IntersectionObserver' in window) new IntersectionObserver(function(es){ es.forEach(function(en){ visible = en.isIntersecting; }); }).observe(canvas);
    document.addEventListener('visibilitychange', function(){ paused = document.hidden; });

    // parallaxe : souris sur l'accueil, défilement sur téléphone
    var hero = logo.closest('.plum') || logo.parentElement;
    if (!touch) {
      hero.addEventListener('mousemove', function(e){ var r = hero.getBoundingClientRect(); tpx = (e.clientX - r.left) / r.width * 2 - 1; tpy = (e.clientY - r.top) / r.height * 2 - 1; });
      hero.addEventListener('mouseleave', function(){ tpx = 0; tpy = 0; });
    } else {
      var onS = function(){ var y = Math.max(0, Math.min(1, window.scrollY / Math.max(1, hero.offsetHeight))); tpx = y * 1.4; tpy = -y * .8; };
      window.addEventListener('scroll', onS, { passive: true }); onS();
      if (window.DeviceOrientationEvent && typeof DeviceOrientationEvent.requestPermission !== 'function') {
        window.addEventListener('deviceorientation', function(e){ if (e.gamma == null) return; tpx = Math.max(-1, Math.min(1, e.gamma / 30)); }, { passive: true });
      }
    }
    // toucher : coup de vent + un fruit tombe ; sur le soleil : tout repousse
    var ray = new THREE.Raycaster(), ndc = new THREE.Vector2();
    canvas.addEventListener('click', function(e){
      var r = canvas.getBoundingClientRect(); ndc.set((e.clientX - r.left) / r.width * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
      ray.setFromCamera(ndc, camera);
      if (ray.intersectObject(sun).length) { replay(); return; }
      gustV += 0.9;
      var t = (performance.now() - T0) / 1000;
      if (t > 3.2) { var src = leaves[Math.floor(Math.random() * leaves.length)]; var wp = new THREE.Vector3(); src.getWorldPosition(wp); wp.y -= src.geometry.parameters.radius * .6; wp.z += .4; dropFruit(wp, new THREE.Vector3(wp.x + (Math.random() - .5) * 1.4, 0.17, 1.2 + Math.random())); }
    });

    function tick(now){
      requestAnimationFrame(tick);
      if (paused || !visible) return;
      frame++; if (touch && frame % 2) return;   // 30 images/s sur téléphone : assez fluide, deux fois moins de batterie
      var t = (now - T0) / 1000;
      // --- chronologie de la pousse ---
      ground.scale.set(seg(t, 0, .6, ease.out), .42 * seg(t, 0, .6, ease.out), 1);
      var sd = seg(t, .25, 1.15, ease.bounce);
      if (t < 1.75) { seed.visible = true; seed.position.set(0, 6.5 - 6.33 * sd, 0.9); var sk = 1 - seg(t, 1.35, 1.75, ease.inout); seed.scale.setScalar(Math.max(.0001, sk)); seed.position.y = Math.min(seed.position.y, .17 * sk); } else seed.visible = false;
      var tg = seg(t, 1.5, 2.45, ease.spring); trunk.scale.set(1, Math.max(.0001, tg), 1); trunk.visible = t > 1.5;
      canopy.visible = t > 2.35;
      leaves.forEach(function(m, i){ m.scale.setScalar(Math.max(.0001, seg(t, 2.4 + i * .09, 2.9 + i * .09, ease.spring))); });
      fruit.scale.setScalar(Math.max(.0001, seg(t, 3.15, 3.55, ease.spring)));
      shadowBig.scale.set(1.4 * tg, .5 * tg, 1);
      // soleil : se lève derrière le sol, puis respire
      var sr = seg(t, 2.6, 3.6, ease.inout); var breathe = 1 + Math.sin(t * 1.6) * .035;
      sun.position.set(sunHome.x - 1.2 + 1.2 * sr, 2.4 + (sunHome.y - 2.4) * sr, sunHome.z); sun.scale.setScalar(breathe); sun.visible = t > 2.6;   // se lève derrière le feuillage
      glow.position.copy(sun.position); glow.visible = sun.visible; glow.material.opacity = sr * (0.85 + Math.sin(t * 1.6) * .15); glow.scale.setScalar(3.6 * breathe);
      sunLight.position.set(sun.position.x + 2, sun.position.y + 2.5, 6);
      // le fruit qui tombe et fait naître le petit baobab
      if (!seedDropped && t > 3.5) { seedDropped = true; var wp = new THREE.Vector3(); fruit.getWorldPosition(wp); dropFruit(wp, new THREE.Vector3(small.position.x, .17, 0)); }
      var sg = seg(t, 4.6, 5.2, ease.spring); sTrunk.scale.set(1, Math.max(.0001, sg), 1); sTrunk.visible = t > 4.6;
      sCanopy.visible = t > 5.05;
      sLeaves.forEach(function(m, i){ m.scale.setScalar(Math.max(.0001, seg(t, 5.1 + i * .08, 5.55 + i * .08, ease.spring))); });
      sFruit.scale.setScalar(Math.max(.0001, seg(t, 5.6, 5.95, ease.spring)));
      shadowSmall.scale.set(1.3 * sg, .5 * sg, 1);
      // fruits en chute : parabole, rebond, puis disparition
      for (var i = falling.length - 1; i >= 0; i--) {
        var f = falling[i]; f.t += touch ? 1 / 30 : 1 / 60; var k = f.t / 1.1;
        if (k >= 1.9) { scene.remove(f.m); falling.splice(i, 1); continue; }
        var kk = Math.min(1, k); var b = ease.bounce(kk);
        f.m.position.set(f.from.x + (f.to.x - f.from.x) * ease.out(kk), f.from.y + (f.to.y - f.from.y) * b, f.from.z + (f.to.z - f.from.z) * ease.out(kk));
        f.m.scale.setScalar(k > 1.3 ? Math.max(.0001, 1 - (k - 1.3) / .6) : 1);
      }
      // --- vie : vent, ondulation, caméra ---
      gustV -= gust * 9 * (1 / 60); gustV *= .94; gust += gustV * (1 / 60);
      canopy.rotation.z = Math.sin(t * .9) * .028 + gust * .35; canopy.rotation.x = Math.sin(t * .7 + 1) * .012;
      sCanopy.rotation.z = Math.sin(t * 1.3 + 2) * .035 - gust * .25;
      px += (tpx - px) * .06; py += (tpy - py) * .06;
      var yaw = Math.sin(t * .22) * .14 + px * .32, pitch = .1 - py * .08;
      camera.position.set(target.x + Math.sin(yaw) * 14.5 * Math.cos(pitch), target.y + Math.sin(pitch) * 14.5 + .6, target.z + Math.cos(yaw) * 14.5 * Math.cos(pitch));
      camera.lookAt(target);
      renderer.render(scene, camera);
    }
    requestAnimationFrame(tick);
  }
})();
