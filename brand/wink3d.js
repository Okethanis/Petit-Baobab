/* ===== wink3d : la carte « Myris » en 3D (three.js chargé à la demande, seulement quand la carte apparaît) =====
   Le grand baobab pousse, le soleil se lève, un fruit tombe du grand arbre et fait naître le petit baobab : Myris.
   Puis le nom se redresse en 3D. La scène vit ensuite (feuillages, caméra, parallaxe) ; toucher = coup de vent et un fruit tombe ; toucher le soleil = tout repousse.
   Sans WebGL, avec « réduire les animations » ou en économie de données, la carte garde son illustration vectorielle animée. */
(function(){
  if (!window.matchMedia || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (navigator.connection && navigator.connection.saveData) return;
  var pathMode = /^https?:$/.test(location.protocol) && !/\.html$/.test(location.pathname);
  var SRC = (pathMode ? '/' : '') + 'vendor/three.min.js';
  var BASE = (pathMode ? '/' : '') + 'souvenirs/';
  var SLIDES = [{ img: 'ombre.jpg' }, { img: 'ascenseur.jpg' }, { img: 'rouge.jpg' }, { video: 'mains.mp4', img: 'mains.jpg' }];   // ordre d'apparition ; la vidéo joue en boucle, sans son
  var loading = null, current = null;
  function load(){
    if (window.THREE) return Promise.resolve();
    if (!loading) loading = new Promise(function(res, rej){ var s = document.createElement('script'); s.src = SRC; s.async = true; s.onload = res; s.onerror = rej; document.head.appendChild(s); });
    return loading;
  }
  function mountAll(){ var el = document.querySelector('.wink-scene:not(.is3d):not(.pending)'); if (!el) return; el.classList.add('pending'); load().then(function(){ try { mount(el); } catch (e) { el.classList.remove('pending'); } }).catch(function(){ el.classList.remove('pending'); }); }
  new MutationObserver(mountAll).observe(document.body, { childList: true, subtree: true });
  mountAll();

  var ease = {
    out: function(t){ return 1 - Math.pow(1 - t, 3); },
    inout: function(t){ return t < .5 ? 4*t*t*t : 1 - Math.pow(-2*t + 2, 3) / 2; },
    spring: function(t){ return 1 - Math.pow(2, -8*t) * Math.cos(t * 7.5); },
    bounce: function(t){ var n = 7.5625, d = 2.75; if (t < 1/d) return n*t*t; if (t < 2/d) return n*(t -= 1.5/d)*t + .75; if (t < 2.5/d) return n*(t -= 2.25/d)*t + .9375; return n*(t -= 2.625/d)*t + .984375; }
  };
  function seg(t, a, b, fn){ if (t <= a) return 0; if (t >= b) return 1; var k = (t - a) / (b - a); return fn ? fn(k) : k; }
  function L(x, y){ return [(x - 60) / 15, (110 - y) / 15]; }

  function mount(holder){
    if (!document.body.contains(holder)) return;
    var THREE = window.THREE; if (!THREE) return;
    if (current) { cancelAnimationFrame(current.raf); try { current.renderer.forceContextLoss(); current.renderer.dispose(); } catch (e) {} current = null; }
    var touch = window.matchMedia('(hover:none)').matches;
    var renderer;
    try { renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'low-power' }); } catch (e) { return; }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 3));   // pleine résolution de l'écran : la scène est légère, autant qu'elle soit nette
    var aniso = renderer.capabilities.getMaxAnisotropy ? renderer.capabilities.getMaxAnisotropy() : 1;
    renderer.setClearColor(0x000000, 0);
    renderer.outputEncoding = THREE.sRGBEncoding;
    if (!touch) { renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap; }
    var canvas = renderer.domElement; canvas.setAttribute('aria-hidden', 'true');
    holder.appendChild(canvas); holder.classList.add('is3d'); holder.classList.remove('pending');
    var card = holder.closest('.wink'); if (card) card.classList.add('is3d');

    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(32, 400 / 284, 0.1, 100);
    var target = new THREE.Vector3(0.6, 3.0, 0);
    var grad = new THREE.DataTexture(new Uint8Array([110, 180, 255]), 3, 1, THREE.LuminanceFormat);
    grad.minFilter = THREE.NearestFilter; grad.magFilter = THREE.NearestFilter; grad.needsUpdate = true;
    function toon(hex){ return new THREE.MeshToonMaterial({ color: hex, gradientMap: grad }); }
    var mLeaf = toon(0x1F6B4A), mTrunk = toon(0x174F38), mFruit = toon(0xF2A93B);
    var mShadow = new THREE.MeshBasicMaterial({ color: 0x174F38, transparent: true, opacity: touch ? .22 : .12, depthWrite: false });
    scene.add(new THREE.HemisphereLight(0xFFFFFF, 0x9FC9B3, 0.55));
    var sunLight = new THREE.DirectionalLight(0xFFE2B0, 0.7); sunLight.position.set(5, 8, 6);
    if (!touch) { sunLight.castShadow = true; sunLight.shadow.mapSize.set(1024, 1024); sunLight.shadow.camera.left = -6; sunLight.shadow.camera.right = 6; sunLight.shadow.camera.top = 9; sunLight.shadow.camera.bottom = -1; sunLight.shadow.radius = 4; }
    scene.add(sunLight);

    var ground = new THREE.Mesh(new THREE.CircleGeometry(3.9, 48), new THREE.MeshBasicMaterial({ color: 0x1F6B4A, transparent: true, opacity: .14, depthWrite: false }));
    ground.rotation.x = -Math.PI / 2; ground.position.y = 0.001; ground.scale.set(1, .42, 1); scene.add(ground);
    var floor = new THREE.Mesh(new THREE.PlaneGeometry(14, 10), new THREE.ShadowMaterial({ opacity: .18 })); floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);

    var big = new THREE.Group(); scene.add(big);
    var trunkPts = [[0.98, 0], [0.92, 0.5], [0.74, 1.2], [0.6, 2.0], [0.6, 2.7], [0.76, 3.25], [1.02, 3.65], [0.7, 3.85], [0, 3.9]].map(function(p){ return new THREE.Vector2(p[0], p[1]); });
    var trunk = new THREE.Mesh(new THREE.LatheGeometry(trunkPts, 28), mTrunk); trunk.castShadow = !touch; big.add(trunk);
    var canopy = new THREE.Group(); canopy.position.y = 3.9; big.add(canopy);
    var leaves = [[59, 44, 26, 0], [33, 54, 17, .55], [85, 54, 17, -.55], [43, 30, 15, -.5], [75, 30, 15, .5], [59, 22, 13, .15]].map(function(c){
      var p = L(c[0], c[1]); var m = new THREE.Mesh(new THREE.SphereGeometry(c[2] / 15, 28, 20), mLeaf);
      m.position.set(p[0], p[1] - 3.9, c[3]); m.castShadow = !touch; m.scale.setScalar(.0001); canopy.add(m); return m;
    });
    var fp = L(71, 40); var fruit = new THREE.Mesh(new THREE.SphereGeometry(.2, 16, 12), mFruit); fruit.position.set(fp[0], fp[1] - 3.9, 1.72); fruit.scale.setScalar(.0001); canopy.add(fruit);
    var shadowBig = new THREE.Mesh(new THREE.CircleGeometry(1.1, 32), mShadow); shadowBig.rotation.x = -Math.PI / 2; shadowBig.position.y = .002; shadowBig.scale.set(1.4, .5, 1); scene.add(shadowBig);

    var small = new THREE.Group(); small.position.x = L(99, 0)[0]; scene.add(small);
    var sPts = [[0.3, 0], [0.26, 0.4], [0.2, 0.8], [0.26, 1.15], [0.34, 1.3], [0, 1.35]].map(function(p){ return new THREE.Vector2(p[0], p[1]); });
    var sTrunk = new THREE.Mesh(new THREE.LatheGeometry(sPts, 20), mTrunk); sTrunk.castShadow = !touch; small.add(sTrunk);
    var sCanopy = new THREE.Group(); sCanopy.position.y = 1.35; small.add(sCanopy);
    var sLeaves = [[99, 82, 9.5, 0], [91, 87, 5.5, .3], [107, 87, 5.5, -.3]].map(function(c){
      var p = L(c[0], c[1]); var m = new THREE.Mesh(new THREE.SphereGeometry(c[2] / 15, 24, 16), mLeaf);
      m.position.set(p[0] - small.position.x, p[1] - 1.35, c[3]); m.castShadow = !touch; m.scale.setScalar(.0001); sCanopy.add(m); return m;
    });
    var sfp = L(103, 80); var sFruit = new THREE.Mesh(new THREE.SphereGeometry(.13, 14, 10), mFruit); sFruit.position.set(sfp[0] - small.position.x, sfp[1] - 1.35, .66); sFruit.scale.setScalar(.0001); sCanopy.add(sFruit);
    var shadowSmall = new THREE.Mesh(new THREE.CircleGeometry(.5, 24), mShadow); shadowSmall.rotation.x = -Math.PI / 2; shadowSmall.position.set(small.position.x, .002, 0); shadowSmall.scale.set(1.3, .5, 1); scene.add(shadowSmall);

    var sunPos = L(104, 18); var sunHome = new THREE.Vector3(sunPos[0] + .3, sunPos[1], -2.6);
    var sun = new THREE.Mesh(new THREE.SphereGeometry(.68, 32, 24), new THREE.MeshBasicMaterial({ color: 0xF2A93B })); scene.add(sun);
    var gc = document.createElement('canvas'); gc.width = gc.height = 128; var g = gc.getContext('2d');
    var rg = g.createRadialGradient(64, 64, 10, 64, 64, 64); rg.addColorStop(0, 'rgba(242,169,59,.45)'); rg.addColorStop(.5, 'rgba(242,169,59,.14)'); rg.addColorStop(1, 'rgba(242,169,59,0)'); g.fillStyle = rg; g.fillRect(0, 0, 128, 128);
    var glow = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(gc), transparent: true, depthWrite: false })); glow.scale.set(3.4, 3.4, 1); scene.add(glow);

    // la photo de nous deux : un polaroid suspendu à une branche du grand baobab
    var PW = 2.3, PH = 2.75, STRING = 0.5;
    var polaroid = new THREE.Group(); polaroid.position.set(-2.75, 3.4, 1.35); polaroid.visible = false; scene.add(polaroid);
    var cardMesh = new THREE.Mesh(new THREE.BoxGeometry(PW, PH, .05), new THREE.MeshToonMaterial({ color: 0xFFFFFF, gradientMap: grad })); cardMesh.position.y = -(STRING + PH / 2); cardMesh.castShadow = !touch; polaroid.add(cardMesh);
    var photoW = PW - .2, photoH = PH - .1 - .34;
    var photoMat = new THREE.MeshBasicMaterial({ color: 0xE1EFE5 });
    var photoMesh = new THREE.Mesh(new THREE.PlaneGeometry(photoW, photoH), photoMat); photoMesh.position.set(0, -(STRING + .1 + photoH / 2), .03); polaroid.add(photoMesh);
    var string = new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, -STRING, 0)]), new THREE.LineBasicMaterial({ color: 0x174F38 })); polaroid.add(string);
    function fit(tex, w, h){ var ia = w / h, pa = photoW / photoH; if (ia < pa) { tex.repeat.set(1, ia / pa); tex.offset.set(0, (1 - ia / pa) / 2); } else { tex.repeat.set(pa / ia, 1); tex.offset.set((1 - pa / ia) / 2, 0); } }
    var loader = new THREE.TextureLoader(), slides = SLIDES.map(function(d){ return { def: d, tex: null, video: null }; });
    slides.forEach(function(sl){
      loader.load(BASE + sl.def.img, function(tex){ tex.encoding = THREE.sRGBEncoding; tex.minFilter = THREE.LinearMipmapLinearFilter; tex.anisotropy = aniso; fit(tex, tex.image.width, tex.image.height); sl.tex = tex; if (sl === slides[slide] && !photoMat.map) show(sl); });
      if (sl.def.video) {
        var v = document.createElement('video'); v.muted = true; v.loop = true; v.playsInline = true; v.setAttribute('playsinline', ''); v.setAttribute('muted', ''); v.preload = 'auto'; v.src = BASE + sl.def.video; v.crossOrigin = 'anonymous';
        var vt = new THREE.VideoTexture(v); vt.encoding = THREE.sRGBEncoding; vt.minFilter = THREE.LinearFilter; vt.anisotropy = aniso;
        v.addEventListener('loadedmetadata', function(){ fit(vt, v.videoWidth, v.videoHeight); });
        sl.video = v; sl.videoTex = vt;
      }
    });
    var slide = 0, flip = 0, flipping = false, swapped = false, lastSwitch = 0;
    function show(sl){
      slides.forEach(function(o){ if (o.video && o !== sl) o.video.pause(); });
      if (sl.video && sl.video.readyState >= 2) { photoMat.map = sl.videoTex; sl.video.currentTime = 0; sl.video.play().catch(function(){ photoMat.map = sl.tex; }); }
      else photoMat.map = sl.tex;
      photoMat.color.set(0xFFFFFF); photoMat.needsUpdate = true;
    }
    function next(){ if (flipping) return; flipping = true; swapped = false; flip = 0; }
    var sw = 0, swV = 0;
    var falling = [];
    function dropFruit(from, to){ var f = new THREE.Mesh(new THREE.SphereGeometry(.17, 14, 10), mFruit); f.position.copy(from); scene.add(f); falling.push({ m: f, from: from.clone(), to: to.clone(), t: 0 }); }

    var T0 = performance.now(), gust = 0, gustV = 0, px = 0, py = 0, tpx = 0, tpy = 0, frame = 0, seeded = false;
    function replay(){ T0 = performance.now(); seeded = false; sw = 0; swV = 0; lastSwitch = 0; flipping = false; flip = 0; slide = 0; show(slides[0]); falling.forEach(function(f){ scene.remove(f.m); }); falling = []; if (card) { card.classList.remove('is3d'); void card.offsetWidth; card.classList.add('is3d'); } }
    function layout(){ var w = holder.clientWidth || 280, h = Math.round(w * 284 / 400); renderer.setSize(w, h, false); canvas.style.width = w + 'px'; canvas.style.height = h + 'px'; camera.aspect = w / h; camera.updateProjectionMatrix(); }
    layout();
    if ('ResizeObserver' in window) new ResizeObserver(layout).observe(holder);
    if (!touch) { canvas.addEventListener('mousemove', function(e){ var r = canvas.getBoundingClientRect(); tpx = (e.clientX - r.left) / r.width * 2 - 1; tpy = (e.clientY - r.top) / r.height * 2 - 1; }); canvas.addEventListener('mouseleave', function(){ tpx = 0; tpy = 0; }); }
    else if (window.DeviceOrientationEvent && typeof DeviceOrientationEvent.requestPermission !== 'function') window.addEventListener('deviceorientation', function(e){ if (e.gamma == null) return; tpx = Math.max(-1, Math.min(1, e.gamma / 30)); }, { passive: true });
    var ray = new THREE.Raycaster(), ndc = new THREE.Vector2();
    canvas.addEventListener('click', function(e){
      var r = canvas.getBoundingClientRect(); ndc.set((e.clientX - r.left) / r.width * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1); ray.setFromCamera(ndc, camera);
      if (ray.intersectObject(sun).length) { replay(); return; }
      if (polaroid.visible && ray.intersectObject(cardMesh).length) { swV += .8; next(); lastSwitch = performance.now(); return; }
      gustV += 0.9;
      if ((performance.now() - T0) / 1000 > 1.6) { var src = leaves[Math.floor(Math.random() * leaves.length)]; var wp = new THREE.Vector3(); src.getWorldPosition(wp); wp.y -= src.geometry.parameters.radius * .6; wp.z += .4; dropFruit(wp, new THREE.Vector3(wp.x + (Math.random() - .5) * 1.4, .17, 1.2 + Math.random())); }
    });

    function tick(now){
      current.raf = requestAnimationFrame(tick);
      if (document.hidden || !document.body.contains(canvas)) { if (!document.body.contains(canvas)) { cancelAnimationFrame(current.raf); slides.forEach(function(o){ if (o.video) { o.video.pause(); o.video.removeAttribute('src'); o.video.load(); } }); try { renderer.forceContextLoss(); renderer.dispose(); } catch (e) {} current = null; } return; }
      frame++; if (touch && frame % 2) return;
      var t = (now - T0) / 1000;
      ground.scale.set(seg(t, 0, .4, ease.out), .42 * seg(t, 0, .4, ease.out), 1);
      var tg = seg(t, .1, .95, ease.spring); trunk.scale.set(1, Math.max(.0001, tg), 1); trunk.visible = t > .1;
      canopy.visible = t > .65;
      leaves.forEach(function(m, i){ m.scale.setScalar(Math.max(.0001, seg(t, .7 + i * .07, 1.15 + i * .07, ease.spring))); });
      fruit.scale.setScalar(Math.max(.0001, seg(t, 1.3, 1.7, ease.spring)));
      shadowBig.scale.set(1.4 * tg, .5 * tg, 1);
      var sr = seg(t, .9, 1.8, ease.inout), breathe = 1 + Math.sin(t * 1.6) * .035;
      sun.position.set(sunHome.x - 1.2 + 1.2 * sr, 2.4 + (sunHome.y - 2.4) * sr, sunHome.z); sun.scale.setScalar(breathe); sun.visible = t > .9;
      glow.position.copy(sun.position); glow.visible = sun.visible; glow.material.opacity = sr * (.85 + Math.sin(t * 1.6) * .15); glow.scale.setScalar(3.4 * breathe);
      sunLight.position.set(sun.position.x + 2, sun.position.y + 2.5, 6);
      if (!seeded && t > 1.85) { seeded = true; var wp = new THREE.Vector3(); fruit.getWorldPosition(wp); dropFruit(wp, new THREE.Vector3(small.position.x, .17, 0)); }
      var sg = seg(t, 2.95, 3.5, ease.spring); sTrunk.scale.set(1, Math.max(.0001, sg), 1); sTrunk.visible = t > 2.95;
      sCanopy.visible = t > 3.35;
      sLeaves.forEach(function(m, i){ m.scale.setScalar(Math.max(.0001, seg(t, 3.4 + i * .07, 3.85 + i * .07, ease.spring))); });
      sFruit.scale.setScalar(Math.max(.0001, seg(t, 3.9, 4.25, ease.spring)));
      shadowSmall.scale.set(1.3 * sg, .5 * sg, 1);
      for (var i = falling.length - 1; i >= 0; i--) {
        var f = falling[i]; f.t += touch ? 1 / 30 : 1 / 60; var k = f.t / 1.1;
        if (k >= 1.9) { scene.remove(f.m); falling.splice(i, 1); continue; }
        var kk = Math.min(1, k), b = ease.bounce(kk);
        f.m.position.set(f.from.x + (f.to.x - f.from.x) * ease.out(kk), f.from.y + (f.to.y - f.from.y) * b, f.from.z + (f.to.z - f.from.z) * ease.out(kk));
        f.m.scale.setScalar(k > 1.3 ? Math.max(.0001, 1 - (k - 1.3) / .6) : 1);
      }
      var pg = seg(t, 4.4, 5.1, ease.spring); polaroid.visible = t > 4.4; polaroid.scale.setScalar(Math.max(.0001, pg));
      swV -= sw * 7 / 60; swV *= .97; sw += swV / 60;
      if (polaroid.visible && pg > .99) {
        if (!lastSwitch) lastSwitch = now;
        if (!flipping && now - lastSwitch > 5000) { next(); lastSwitch = now; }
      }
      var flipAngle = 0;
      if (flipping) {
        flip += (touch ? 2 : 1) / 60 / .7;
        if (flip >= .5 && !swapped) { swapped = true; slide = (slide + 1) % slides.length; show(slides[slide]); }
        if (flip >= 1) { flipping = false; flip = 0; } else flipAngle = Math.sin(flip * Math.PI) * Math.PI / 2;
      }
      polaroid.rotation.z = Math.sin(t * 1.1) * .05 + sw * .5; polaroid.rotation.y = Math.sin(t * .45) * .16 + px * .2 + flipAngle;
      gustV -= gust * 9 / 60; gustV *= .94; gust += gustV / 60;
      canopy.rotation.z = Math.sin(t * .9) * .028 + gust * .35; canopy.rotation.x = Math.sin(t * .7 + 1) * .012;
      sCanopy.rotation.z = Math.sin(t * 1.3 + 2) * .035 - gust * .25;
      px += (tpx - px) * .06; py += (tpy - py) * .06;
      var yaw = Math.sin(t * .22) * .14 + px * .32, pitch = .1 - py * .08;
      camera.position.set(target.x + Math.sin(yaw) * 14.5 * Math.cos(pitch), target.y + Math.sin(pitch) * 14.5 + .6, target.z + Math.cos(yaw) * 14.5 * Math.cos(pitch));
      camera.lookAt(target);
      renderer.render(scene, camera);
    }
    current = { renderer: renderer, raf: requestAnimationFrame(tick), canvas: canvas };
  }
})();
