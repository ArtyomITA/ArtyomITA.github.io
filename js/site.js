/* artyomita.github.io · tema, comparsa allo scroll, contatori, luce sulle schede, figura FlyToLLM e caricamento della scena 3D.
   Nessuna libreria; la scena three.js sta in hero.js e si carica solo se serve (WebGL presente, movimento ammesso). */
(function () {
'use strict';
var D = document, root = D.documentElement, lang = root.lang === 'en' ? 'en' : 'it';
var rm = matchMedia('(prefers-reduced-motion: reduce)').matches;
var fine = matchMedia('(hover:hover) and (pointer:fine)').matches;
function $(s, c) { return (c || D).querySelector(s); }
function $$(s, c) { return [].slice.call((c || D).querySelectorAll(s)); }
function clamp(x, a, b) { return x < a ? a : x > b ? b : x; }
function rng(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; var t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function idle(fn) { if (window.requestIdleCallback) requestIdleCallback(fn, { timeout: 2500 }); else setTimeout(fn, 400); }
function onSee(els, fn, opt) {
  if (!('IntersectionObserver' in window)) { els.forEach(function (e) { fn(e); }); return; }
  var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { io.unobserve(e.target); fn(e.target); } }); }, opt || { rootMargin: '0px 0px -8% 0px' });
  els.forEach(function (e) { io.observe(e); });
}

/* tema: chiaro, scuro (predefinito) o auto. Lo script nel head applica la scelta salvata prima del primo disegno. */
var K = 'ai-theme';
function saved() { try { var t = localStorage.getItem(K); return t === 'light' || t === 'auto' ? t : 'dark'; } catch (e) { return 'dark'; } }
function apply(p) {
  var light = p === 'light' || (p === 'auto' && matchMedia('(prefers-color-scheme: light)').matches);
  if (light) root.setAttribute('data-theme', 'light'); else root.removeAttribute('data-theme');
  $$('.theme button').forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-set') === p ? 'true' : 'false'); });
}
var pref = saved(); apply(pref);
$$('.theme button').forEach(function (b) {
  b.addEventListener('click', function () { pref = b.getAttribute('data-set'); try { localStorage.setItem(K, pref); } catch (e) { } apply(pref); });
});
matchMedia('(prefers-color-scheme: light)').addEventListener('change', function () { if (pref === 'auto') apply('auto'); });

/* lingua: l'ancora resta. Indice a comparsa: si chiude da solo. */
$$('.lang a').forEach(function (a) { a.addEventListener('click', function () { if (location.hash) a.href = a.getAttribute('href').split('#')[0] + location.hash; }); });
var toc = $('.toc');
if (toc) {
  $$('a', toc).forEach(function (a) { if (a.closest('ol')) a.addEventListener('click', function () { toc.removeAttribute('open'); }); });
  D.addEventListener('click', function (e) { if (!toc.contains(e.target)) toc.removeAttribute('open'); });
  addEventListener('keydown', function (e) { if (e.key === 'Escape') toc.removeAttribute('open'); });
}

/* comparsa allo scroll */
if ('IntersectionObserver' in window && !rm) {
  root.classList.add('rv-on');
  onSee($$('.rv'), function (e) { e.classList.add('in'); setTimeout(function () { e.classList.add('done'); }, 1400); }, { rootMargin: '0px 0px -6% 0px', threshold: 0.06 });
}
addEventListener('beforeprint', function () { root.classList.remove('rv-on'); });

/* contatori: cifre nello stile della lingua, il testo finale e' gia' nell'HTML */
function nf(x, d) { var p = x.toFixed(d).split('.'), th = lang === 'it' ? '.' : ',', i = p[0].replace(/\B(?=(\d{3})+(?!\d))/g, th); return i + (d ? (lang === 'it' ? ',' : '.') + p[1] : ''); }
function count(el) {
  var t = el.textContent, m = t.match(/^([^\d]*)([\d.,]+)(.*)$/); if (!m) return;
  var th = lang === 'it' ? '.' : ',', dc = lang === 'it' ? ',' : '.', raw = m[2].split(th).join(''), di = raw.indexOf(dc), dec = di < 0 ? 0 : raw.length - di - 1;
  var to = parseFloat(raw.replace(dc, '.')); if (isNaN(to)) return;
  var t0 = performance.now(), dur = 1300;
  (function step(now) {
    var p = clamp((now - t0) / dur, 0, 1), e = 1 - Math.pow(1 - p, 4);
    el.textContent = p < 1 ? m[1] + nf(to * e, dec) + m[3] : t;
    if (p < 1) requestAnimationFrame(step);
  })(t0);
}
if (!rm) onSee($$('.cn'), count, { threshold: 0.6 });

/* luce che segue il mouse sulle schede, e un leggero tilt (solo con mouse vero) */
if (fine && !rm) {
  D.addEventListener('pointermove', function (e) {
    var c = e.target.closest ? e.target.closest('.card,.stat') : null; if (!c) return;
    var b = c.getBoundingClientRect(), x = e.clientX - b.left, y = e.clientY - b.top;
    c.style.setProperty('--mx', x + 'px'); c.style.setProperty('--my', y + 'px');
    if (c.classList.contains('tilt')) c.style.transform = 'perspective(900px) rotateX(' + ((0.5 - y / b.height) * 4).toFixed(2) + 'deg) rotateY(' + ((x / b.width - 0.5) * 5).toFixed(2) + 'deg) translateY(-3px)';
  }, { passive: true });
  D.addEventListener('pointerout', function (e) { var c = e.target.closest ? e.target.closest('.tilt') : null; if (c && !c.contains(e.relatedTarget)) c.style.transform = ''; });
}

/* voce di menu della sezione in vista; ml e rl contano come "sperimentali" */
var links = $$('.nav a, .toc ol a');
if ('IntersectionObserver' in window) {
  var so = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (!e.isIntersecting) return;
      var h = e.target.getAttribute('data-nav') || '#' + e.target.id;
      links.forEach(function (a) { if (a.getAttribute('href') === h) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current'); });
    });
  }, { rootMargin: '-45% 0px -50% 0px' });
  $$('main section[id]').forEach(function (s) { if (s.id !== 'top') so.observe(s); });
  var hero = $('#top');
  if (hero) new IntersectionObserver(function (es) { if (es[0].isIntersecting) links.forEach(function (a) { a.removeAttribute('aria-current'); }); }, { threshold: 0.5 }).observe(hero);
}

/* FlyToLLM: il sistema nervoso centrale come nuvola di punti. Un'onda parte dalle porte d'ingresso e avanza un salto alla volta.
   Sagoma: un solo contorno chiuso (Catmull-Rom). Punti a disco di Poisson dentro il contorno (seme 166700, il numero dei neuroni),
   grafo dei 3 vicini, salti contati dalle porte: bordo esterno dei lobi ottici e fascia dorsale del cervello. */
(function () {
  var cv = $('#cns'); if (!cv) return;
  var box = cv.parentNode, ctx = cv.getContext('2d'), G = 6, P = null, A = null, hop = null, OUT = null, bg = null, W = 0, s = 1, dpr = 1, vis = false, raf = 0, mouse = null;
  var R = [[200, 74], [226, 72], [252, 66], [276, 56], [300, 40], [330, 30], [362, 38], [384, 62], [394, 98], [396, 140], [388, 182], [368, 210], [340, 224], [312, 218], [290, 202],
    [268, 192], [246, 196], [226, 206], [216, 222], [218, 240], [244, 250], [262, 270], [266, 298], [256, 322], [244, 334], [262, 352], [268, 380], [258, 406], [244, 416],
    [254, 432], [256, 458], [246, 478], [234, 496], [228, 522], [218, 548], [200, 562]];
  function cr(q, k, u) { var a = q[0][k], b = q[1][k], c = q[2][k], d = q[3][k]; return 0.5 * (2 * b + (c - a) * u + (2 * a - 5 * b + 4 * c - d) * u * u + (3 * b - a - 3 * c + d) * u * u * u); }
  function outline() {
    var Kp = R.slice(0, -1).concat(R.slice(1).reverse().map(function (p) { return [400 - p[0], p[1]]; })), n = Kp.length, pts = [];
    for (var i = 0; i < n; i++) { var q = [Kp[(i - 1 + n) % n], Kp[i], Kp[(i + 1) % n], Kp[(i + 2) % n]]; for (var k = 0; k < 6; k++) pts.push([cr(q, 0, k / 6), cr(q, 1, k / 6)]); }
    return pts;
  }
  function region(x, y) { var a = (Math.abs(x - 200) - 145) / 55, b = (y - 127) / 99; if (a * a + b * b <= 1) return 'ol'; return y < 214 ? 'cb' : y < 246 ? 'nk' : 'v'; }
  function gen() {
    OUT = outline();
    var mc = D.createElement('canvas'), mx = mc.getContext('2d'); mc.width = 400; mc.height = 570;
    mx.beginPath(); OUT.forEach(function (p, i) { if (i) mx.lineTo(p[0], p[1]); else mx.moveTo(p[0], p[1]); }); mx.closePath(); mx.fill();
    var M = mx.getImageData(0, 0, 400, 570).data;
    var r = rng(166700), md = 9.6, cs = md / Math.SQRT2, gw = Math.ceil(400 / cs) + 1, gh = Math.ceil(570 / cs) + 1, grid = new Int32Array(gw * gh).fill(-1), tries = 0, i, j; P = [];
    while (tries++ < 26000) {
      var x = r() * 400, y = r() * 570; if (M[((y | 0) * 400 + (x | 0)) * 4 + 3] < 128) continue;
      var gx = x / cs | 0, gy = y / cs | 0, ok = true;
      for (var a = -2; a <= 2 && ok; a++) for (var b = -2; b <= 2; b++) { var X = gx + a, Y = gy + b; if (X < 0 || Y < 0 || X >= gw || Y >= gh) continue; var id = grid[Y * gw + X]; if (id >= 0) { var q = P[id], dx = q.x - x, dy = q.y - y; if (dx * dx + dy * dy < md * md) { ok = false; break; } } }
      if (ok) { grid[gy * gw + gx] = P.length; P.push({ x: x, y: y, rg: region(x, y), role: 1 }); }
    }
    P.forEach(function (p) { if ((p.rg === 'ol' && Math.abs(p.x - 200) > 158 && r() < 0.6) || (p.rg === 'cb' && p.y < 92 && r() < 0.5)) p.role = 0; });
    A = P.map(function () { return []; });
    for (i = 0; i < P.length; i++) {
      var best = [], px = P[i].x / cs | 0, py = P[i].y / cs | 0;
      for (var gy2 = Math.max(0, py - 3); gy2 <= Math.min(gh - 1, py + 3); gy2++) for (var gx2 = Math.max(0, px - 3); gx2 <= Math.min(gw - 1, px + 3); gx2++) {
        j = grid[gy2 * gw + gx2]; if (j < 0 || j === i) continue;
        var ex = P[i].x - P[j].x, ey = P[i].y - P[j].y, d2 = ex * ex + ey * ey;
        if (best.length < 3 || d2 < best[2][0]) { best.push([d2, j]); best.sort(function (u, w) { return u[0] - w[0]; }); if (best.length > 3) best.pop(); }
      }
      best.forEach(function (bb) { if (A[i].indexOf(bb[1]) < 0) { A[i].push(bb[1]); A[bb[1]].push(i); } });
    }
    var d = new Int16Array(P.length).fill(-1), Q = []; for (i = 0; i < P.length; i++) if (P[i].role === 0) { d[i] = 0; Q.push(i); }
    for (var h = 0; h < Q.length; h++) { var u = Q[h]; A[u].forEach(function (w) { if (d[w] < 0) { d[w] = d[u] + 1; Q.push(w); } }); }
    /* un "salto" della figura = meta' della distanza mediana del collo, cosi' il collo cade a 2 salti */
    var nk = []; for (i = 0; i < P.length; i++) if (P[i].rg === 'nk' && d[i] >= 0) nk.push(d[i]);
    nk.sort(function (u, w) { return u - w; }); var k = Math.max(1, (nk[nk.length >> 1] || 16) / 2);
    hop = new Int8Array(P.length);
    for (i = 0; i < P.length; i++) { hop[i] = d[i] < 0 ? G - 1 : Math.min(G - 1, Math.round(d[i] / k)); if (P[i].role === 0) hop[i] = 0; }
    for (i = 0; i < P.length; i++) if (hop[i] === 2 && P[i].role && (P[i].rg === 'nk' || (P[i].rg === 'cb' && P[i].y > 176 && Math.abs(P[i].x - 200) < 44)) && r() < 0.7) P[i].role = 2;
    var pd = nf(Math.round(166700 / P.length), 0); $$('.pd').forEach(function (e) { e.textContent = pd; });
  }
  function layer() {
    bg = D.createElement('canvas'); bg.width = cv.width; bg.height = cv.height;
    var b = bg.getContext('2d'); b.scale(dpr * s, dpr * s);
    b.beginPath(); OUT.forEach(function (p, i) { if (i) b.lineTo(p[0], p[1]); else b.moveTo(p[0], p[1]); }); b.closePath();
    b.fillStyle = 'rgba(46,242,176,.04)'; b.fill(); b.strokeStyle = 'rgba(46,242,176,.2)'; b.lineWidth = 1 / s; b.stroke();
    b.strokeStyle = 'rgba(46,242,176,.1)'; b.lineWidth = 0.7 / s; b.beginPath();
    for (var i = 0; i < P.length; i++) A[i].forEach(function (j) { if (j > i) { b.moveTo(P[i].x, P[i].y); b.lineTo(P[j].x, P[j].y); } });
    b.stroke();
  }
  function size() {
    var w = box.clientWidth; if (!w || !P) return;
    dpr = Math.min(window.devicePixelRatio || 1, 2); W = w; s = w / 400;
    cv.width = Math.round(w * dpr); cv.height = Math.round(w * 570 / 400 * dpr); layer(); paint(performance.now());
  }
  function paint(now) {
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, cv.width, cv.height); ctx.drawImage(bg, 0, 0);
    ctx.setTransform(dpr * s, 0, 0, dpr * s, 0, 0); ctx.globalCompositeOperation = 'lighter';
    var f = (now / 1000 * 1.1) % (G + 3.5);
    for (var i = 0; i < P.length; i++) {
      var p = P[i], h = hop[i], act;
      if (rm) act = 0.3 + 0.7 * Math.max(0, 1 - h / 5); else { var d = f - h; act = d >= 0 ? Math.exp(-d * 0.95) : Math.exp(d * 3.2); }
      if (mouse) { var mx = p.x - mouse.x, my = p.y - mouse.y; act = Math.max(act, Math.exp(-(mx * mx + my * my) / 900)); }
      var a = 0.22 + 0.78 * act;
      if (p.role === 0) { ctx.fillStyle = 'rgba(255,106,87,' + (0.5 + 0.5 * a).toFixed(2) + ')'; ctx.beginPath(); ctx.arc(p.x, p.y, 3.1 + act * 1.2, 0, 6.2832); ctx.fill(); if (act > 0.5) { ctx.fillStyle = 'rgba(255,106,87,.14)'; ctx.beginPath(); ctx.arc(p.x, p.y, 9, 0, 6.2832); ctx.fill(); } }
      else if (p.role === 2) { ctx.fillStyle = 'rgba(217,255,241,' + (0.45 + 0.55 * a).toFixed(2) + ')'; var z = 2.3 + act * 1.1; ctx.fillRect(p.x - z, p.y - z, 2 * z, 2 * z); }
      else {
        ctx.fillStyle = 'rgba(46,242,176,' + a.toFixed(2) + ')'; ctx.beginPath(); ctx.arc(p.x, p.y, 1.6 + act * 1.1, 0, 6.2832); ctx.fill();
        if (act > 0.6) { ctx.fillStyle = 'rgba(46,242,176,.1)'; ctx.beginPath(); ctx.arc(p.x, p.y, 6, 0, 6.2832); ctx.fill(); }
      }
    }
    ctx.globalCompositeOperation = 'source-over';
  }
  function loop(now) { raf = 0; if (!vis || D.visibilityState !== 'visible') return; paint(now); raf = requestAnimationFrame(loop); }
  function kick() { if (!rm && vis && !raf) raf = requestAnimationFrame(loop); }
  onSee([box], function () { gen(); size(); }, { rootMargin: '100% 0px' });
  new IntersectionObserver(function (es) { vis = es[0].isIntersecting; if (vis && !P) { gen(); size(); } kick(); }).observe(box);
  D.addEventListener('visibilitychange', kick);
  if ('ResizeObserver' in window) new ResizeObserver(function () { if (P && box.clientWidth !== W) size(); }).observe(box);
  cv.addEventListener('pointermove', function (e) { var b = cv.getBoundingClientRect(); mouse = { x: (e.clientX - b.left) / b.width * 400, y: (e.clientY - b.top) / b.height * 570 }; if (rm) paint(0); }, { passive: true });
  cv.addEventListener('pointerleave', function () { mouse = null; if (rm) paint(0); });
})();

/* scena 3D della hero: carica hero.js (three.js incluso) a pagina finita, solo se c'e' WebGL e il movimento e' ammesso */
(function () {
  var cv = $('#hero-cv'), hero = $('#top');
  if (!cv || !hero || rm || (navigator.connection && navigator.connection.saveData)) return;
  function webgl() {
    try {
      var c = D.createElement('canvas'), g = c.getContext('webgl2');
      if (g) { var x = g.getExtension('WEBGL_lose_context'); if (x) x.loseContext(); return true; }
    } catch (e) { }
    return false;
  }
  function go() { if (!webgl()) return; import('./hero.js').then(function (m) { m.start(cv, hero); }).catch(function () { }); }
  if (D.readyState === 'complete') idle(go); else addEventListener('load', function () { idle(go); });
})();
})();
