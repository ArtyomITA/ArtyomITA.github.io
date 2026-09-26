/* artyomita.github.io · figure calcolate nella pagina (canvas 2D e SVG scritti a mano, nessuna libreria).
   Un solo gestore di scroll passivo, un solo requestAnimationFrame per fotogramma, figure attive solo
   quando un IntersectionObserver le vede. prefers-reduced-motion: un fotogramma finale per figura. */
(function () {
'use strict';
var D = document, root = D.documentElement, lang = root.lang === 'en' ? 'en' : 'it', loc = lang === 'it' ? 'it-IT' : 'en-GB';
var RMq = matchMedia('(prefers-reduced-motion: reduce)'), rm = RMq.matches, DARKq = matchMedia('(prefers-color-scheme: dark)');
function $(s, c) { return (c || D).querySelector(s); }
function $$(s, c) { return [].slice.call((c || D).querySelectorAll(s)); }
function clamp(x, a, b) { return x < a ? a : x > b ? b : x; }
function lerp(a, b, t) { return a + (b - a) * t; }
function sst(x) { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); }
function rng(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; var t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function nf(x, d) { return x.toLocaleString(loc, { minimumFractionDigits: d, maximumFractionDigits: d }); }
function cv(n) { return getComputedStyle(root).getPropertyValue(n).trim(); }
function f1(x) { return (Math.round(x * 10) / 10).toString(); }
function T(x, y, s, cls, anc, extra) { return '<text x="' + f1(x) + '" y="' + f1(y) + '"' + (cls ? ' class="' + cls + '"' : '') + (anc ? ' text-anchor="' + anc + '"' : '') + (extra || '') + '>' + s + '</text>'; }
function ln(x1, y1, x2, y2, cls) { return '<line x1="' + f1(x1) + '" y1="' + f1(y1) + '" x2="' + f1(x2) + '" y2="' + f1(y2) + '" class="' + cls + '"/>'; }
function wOf(el) { return Math.round(el.getBoundingClientRect().width); }

var L = {
  it: { sens: 'sensoriali', cen: 'centrali', desc: 'discendenti', rate: 'tasso', ro: ['t', 'ingresso ×', 'spike/ms'],
    tok: 'token · BPE 4096', in1: 'ingresso: 17.937', in2: 'neuroni sensoriali', core: 'nucleo ricorrente LIF', c2: '166.700 neuroni · 2,75 M sinapsi (≥ 10)', c3: '4+4 sottopassi per token',
    o1: 'lettura: 2.241 neuroni', o2: 'discendenti e motori', o3: '→ logit del prossimo token', att: 'attention causale esterna · 4 teste · cache 128 · rientra dalle stesse porte', attS: 'attention esterna · 4 teste · cache 128',
    les1: 'lesione in silico:', les2: 'lobo ottico rimosso,', les3: 'cross-entropy invariata', hop: 'salti dalle porte', pin: 'ingresso', pout: 'uscita',
    k: ['MoE · un lancio per kernel', 'MoE · CUDA graph', 'denso · un lancio per kernel', 'denso · CUDA graph'], kax: 'tempo per token, relativo',
    pad: 'padding: 0,76', fix: 'fix', cosax: '1 − coseno', ts: 'tok/s su GTX 1080', dec: 'decodifica', dr: 'con drafter', turns: 'turni con cifre non supportate', fence: 'GTX 1080 · nessuna chiamata esterna',
    grid: ['mostra la griglia', 'nascondi la griglia'] },
  en: { sens: 'sensory', cen: 'central', desc: 'descending', rate: 'rate', ro: ['t', 'input ×', 'spikes/ms'],
    tok: 'token · BPE 4096', in1: 'input: 17,937', in2: 'sensory neurons', core: 'recurrent LIF core', c2: '166,700 neurons · 2.75 M synapses (≥ 10)', c3: '4+4 substeps per token',
    o1: 'readout: 2,241 descending', o2: 'and motor neurons', o3: '→ next-token logits', att: 'external causal attention · 4 heads · cache 128 · re-enters through the same ports', attS: 'external attention · 4 heads · cache 128',
    les1: 'in-silico lesion:', les2: 'optic lobe removed,', les3: 'cross-entropy unchanged', hop: 'hops from the ports', pin: 'input', pout: 'output',
    k: ['MoE · one launch per kernel', 'MoE · CUDA graph', 'dense · one launch per kernel', 'dense · CUDA graph'], kax: 'time per token, relative',
    pad: 'padding: 0.76', fix: 'fix', cosax: '1 − cosine', ts: 'tok/s on GTX 1080', dec: 'decoding', dr: 'with drafter', turns: 'turns with unsupported figures', fence: 'GTX 1080 · no external calls',
    grid: ['show the grid', 'hide the grid'] }
}[lang];

/* ---------- pianificatore: scroll passivo, un rAF per fotogramma ---------- */
var scr = [], dirty = 0, raf = 0;
function need() { if (!raf) raf = requestAnimationFrame(tick); }
function tick(now) {
  raf = 0;
  if (dirty) {
    dirty = 0;
    var vh = innerHeight, on = scr.filter(function (s) { return s.on; }), rs = on.map(function (s) { return s.el.getBoundingClientRect(); });
    on.forEach(function (s, i) { s.set(rm ? 1 : clamp(s.p(rs[i], vh), 0, 1)); });
  }
  Ras.frame(now);
  if (Ras.live()) need();
}
var ioNear = new IntersectionObserver(function (es) {
  es.forEach(function (e) { scr.forEach(function (s) { if (s.el === e.target) s.on = e.isIntersecting; }); });
  dirty = 1; need();
}, { rootMargin: '50% 0px' });
function scrubber(el, p, set) { var s = { el: el, p: p, set: set, on: false }; scr.push(s); ioNear.observe(el); return s; }
function scrubNow(s) { s.set(rm ? 1 : clamp(s.p(s.el.getBoundingClientRect(), innerHeight), 0, 1)); }

/* ---------- Fig. 1: raster LIF guidato dallo scroll (canvas) ---------- */
var Ras = (function () {
  var c = $('#raster');
  if (!c || !c.getContext) return { kick: function () {}, frame: function () {}, live: function () { return false; }, redraw: function () {}, motion: function () {} };
  var ctx = c.getContext('2d'), box = c.parentNode, ro = $('#readout'), WIN = 720;
  var N, S, C, Dn, v, inp, nxt, rf, typ, tgt, wt, hist, rate, t, nextTok, lastTok = -1, rnd, drive = 0;
  var W = 0, H = 0, dpr = 1, vis = false, run = false, last = 0, lastRo = 0, col, lab = 80, forced = false, samp = [], idle = performance.now(), settle = -1, settleTok = -1;
  function build() {
    var r = rng(27721); rnd = rng(61); drive = rm ? 0 : drive;
    N = (forced || W < 560) ? 72 : 128; S = Math.round(N * 0.18); Dn = Math.round(N * 0.14); C = N - S - Dn;
    v = new Float32Array(N); inp = new Float32Array(N); nxt = new Float32Array(N); rf = new Uint8Array(N); typ = new Uint8Array(N); tgt = []; wt = [];
    for (var i = 0; i < N; i++) {
      var g = i < S ? 0 : i < S + C ? 1 : 2, Tg = [], X = [];
      typ[i] = g === 0 ? 0 : g === 2 ? 3 : (r() < 0.2 ? 2 : 1);
      for (var n = 0; n < (g === 2 ? 0 : 8); n++) {
        var j;
        if (g === 0) j = S + Math.floor(Math.pow(r(), 1.7) * C * 0.4);
        else { j = i + 1 + Math.floor(r() * Math.max(4, C * 0.25)); if (j >= S + C) j = S + C + Math.floor(r() * Dn); if (r() < 0.05) j = S + Math.floor(r() * C); }
        if (j !== i) { Tg.push(j); X.push(typ[i] === 2 ? -1.1 : (g === 0 ? 0.75 : 0.5)); }
      }
      tgt.push(Tg); wt.push(X);
    }
    hist = new Array(WIN); rate = new Float32Array(WIN); t = 0; nextTok = 12; lastTok = -1;
    $$('.nn').forEach(function (e) { e.textContent = N; });
  }
  function step() {
    var i, s, Tg, X, spk = [], sp = 0.003 + Math.min(0.03, drive * 0.012);
    if (t >= nextTok) {
      var a = Math.floor(rnd() * (S - 7)), len = 4 + Math.floor(rnd() * 4);
      for (i = a; i < a + len; i++) inp[i] += 1.05 + rnd() * 0.3;
      nextTok = t + Math.round((95 + rnd() * 50) / (1 + Math.min(2.5, drive))); lastTok = t;
    }
    for (i = 0; i < N; i++) {
      if (typ[i] === 0) { if (rnd() < sp) inp[i] += 1.1; } else if (rnd() < 0.0022) inp[i] += 0.75;
      if (rf[i]) { rf[i]--; v[i] = 0; continue; }
      v[i] = Math.max(-0.6, v[i] * 0.92 + inp[i]);
      if (v[i] >= 1) { spk.push(i); v[i] = 0; rf[i] = 3; Tg = tgt[i]; X = wt[i]; for (s = 0; s < Tg.length; s++) nxt[Tg[s]] += X[s]; }
    }
    var tmp = inp; inp = nxt; nxt = tmp; nxt.fill(0);
    hist[t % WIN] = spk; rate[t % WIN] = spk.length; t++; drive *= 0.994;
  }
  function warm() { var n = rm ? 960 : WIN; for (var i = 0; i < n; i++) step(); }
  function yOf(i, rh, top, gp) { return top + i * rh + (i < S ? 0 : i < S + C ? gp : 2 * gp); }
  function fontSz() { return W < 560 ? 12 : 13; }
  function measure() {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.font = fontSz() + 'px ' + col.font;
    lab = Math.ceil(Math.max(ctx.measureText(L.sens).width, ctx.measureText(L.cen).width, ctx.measureText(L.desc).width, ctx.measureText(L.rate).width)) + 14;
  }
  function draw() {
    if (!W || !hist) return;
    var rH = Math.round(H * 0.15), top = 4, gp = 8, sb = 18, rh = (H - rH - top - 2 * gp - sb - 10) / N, pw = W - lab;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, W, H);
    var px = pw / WIN, tw = Math.max(1, px * 0.85), th = Math.max(1.4, rh * 0.7), P = [new Path2D(), new Path2D(), new Path2D(), new Path2D()], n = Math.min(t, WIN), k, q, Ls;
    for (k = 0; k < n; k++) { Ls = hist[(t - n + k) % WIN]; var x = lab + (WIN - n + k) * px; for (q = 0; q < Ls.length; q++) { var i = Ls[q]; P[typ[i]].rect(x, yOf(i, rh, top, gp) + (rh - th) / 2, tw, th); } }
    ctx.fillStyle = col.fig; ctx.fill(P[0]); ctx.fill(P[3]); ctx.fillStyle = col.ink; ctx.fill(P[1]); ctx.fillStyle = col.inh; ctx.fill(P[2]);
    var y0 = H - sb - rH, yb = H - sb - 4;
    ctx.strokeStyle = col.rule; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(lab, yb + 0.5); ctx.lineTo(W, yb + 0.5); ctx.stroke();
    ctx.strokeStyle = col.fig; ctx.lineWidth = 1.3; ctx.beginPath();
    for (k = 0; k < n; k++) {
      var a = 0, m = 0; for (q = Math.max(0, k - 6); q <= Math.min(n - 1, k + 6); q++) { a += rate[(t - n + q) % WIN]; m++; }
      var yy = yb - Math.min(1, a / m / (N * 0.09)) * (rH - 6); if (k) ctx.lineTo(lab + (WIN - n + k) * px, yy); else ctx.moveTo(lab + (WIN - n + k) * px, yy);
    }
    ctx.stroke();
    ctx.fillStyle = col.ink2; ctx.strokeStyle = col.ink3; ctx.lineWidth = 1; ctx.font = fontSz() + 'px ' + col.font; ctx.textBaseline = 'middle';
    [[0, S, L.sens], [S, S + C, L.cen], [S + C, N, L.desc]].forEach(function (g) {
      var a = yOf(g[0], rh, top, gp), b = yOf(g[1] - 1, rh, top, gp) + rh, bx = Math.round(lab - 9) + 0.5;
      ctx.beginPath(); ctx.moveTo(bx + 3, a + 1); ctx.lineTo(bx, a + 1); ctx.lineTo(bx, b - 1); ctx.lineTo(bx + 3, b - 1); ctx.stroke(); ctx.fillText(g[2], 0, (a + b) / 2);
    });
    ctx.fillText(L.rate, 0, y0 + rH / 2);
    var L100 = 100 * px; ctx.strokeStyle = col.ink; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(W - L100, H - 5); ctx.lineTo(W, H - 5); ctx.stroke();
    ctx.font = '11px ' + col.mono; ctx.textAlign = 'right'; ctx.textBaseline = 'alphabetic'; ctx.fillStyle = col.ink2; ctx.fillText('100 ms', W - L100 - 8, H - 2); ctx.textAlign = 'left';
  }
  function readout(now, force) {
    if (!ro || (!force && now - lastRo < 250)) return; lastRo = now;
    var s = 0, n = Math.min(t, 32); for (var k = 0; k < n; k++) s += rate[(t - 1 - k) % WIN];
    ro.textContent = L.ro[0] + ' = ' + nf(t, 0) + ' ms · ' + L.ro[1] + nf(1 + Math.min(2.5, drive), 1) + ' · ' + nf(s / Math.max(1, n), 1) + ' ' + L.ro[2];
  }
  function colors() { var bs = getComputedStyle(D.body); col = { fig: cv('--fig'), ink: cv('--ink'), ink2: cv('--ink-2'), ink3: cv('--ink-3'), inh: cv('--inh'), rule: cv('--rule'), font: bs.fontFamily, mono: cv('--mono') }; }
  function size() {
    var b = box.getBoundingClientRect(), nw = Math.round(b.width), old = W; W = nw; H = Math.round(b.height); dpr = Math.min(2, devicePixelRatio || 1);
    c.width = Math.round(W * dpr); c.height = Math.round(H * dpr);
    measure();
    if (!old || (old < 560) !== (W < 560) || !hist) { build(); warm(); }
    draw(); readout(0, true);
  }
  function ok() { return vis && !rm && D.visibilityState === 'visible'; }
  function start() { if (!run && ok()) { run = true; last = 0; settle = -1; need(); } }
  function stop() { run = false; draw(); readout(0, true); }
  function frame(now) {
    if (!run) return;
    if (!ok()) { stop(); return; }
    var dt = Math.min(50, now - (last || now)); last = now;
    var t0 = performance.now(), st = Math.max(1, Math.round(dt * 0.2));
    for (var i = 0; i < st; i++) step();
    draw();
    samp.push(performance.now() - t0); if (samp.length > 30) samp.shift();
    if (!forced && N > 72 && samp.length === 30 && samp.reduce(function (a, b) { return a + b; }, 0) / 30 > 9) { forced = true; build(); warm(); samp = []; }
    readout(now);
    /* pagina ferma da 7 s: si aspetta il prossimo token e 360 ms simulati (raffica a meta' finestra), poi stop */
    if (performance.now() - idle > 7000) {
      if (settle < 0) { settle = t; settleTok = -1; }
      if (settleTok < 0 && lastTok >= settle) settleTok = lastTok;
      if (settleTok >= 0 && t - settleTok >= 360) stop();
    }
  }
  colors(); c.setAttribute('width', 1);
  new ResizeObserver(size).observe(box);
  new IntersectionObserver(function (e) { vis = e[0].isIntersecting; if (vis) start(); }).observe(box);
  box.addEventListener('pointerenter', function () { idle = performance.now(); start(); });
  D.addEventListener('visibilitychange', function () { if (D.visibilityState === 'visible') { idle = performance.now(); start(); } });
  return {
    kick: function (vel) { if (rm) return; drive = Math.min(6, drive + vel * 0.08); idle = performance.now(); settle = -1; start(); },
    frame: frame, live: function () { return run; },
    redraw: function () { colors(); if (W) { measure(); draw(); } },
    motion: function () { run = false; drive = 0; build(); warm(); draw(); readout(0, true); if (!rm) { idle = performance.now(); start(); } }
  };
})();

/* ---------- Fig. 2: connettoma schematico, raggiungibilita' per salti (SVG) ----------
   I salti si calcolano su un grafo di vicinato che non si disegna: si vedono solo i punti,
   tinti per salto su una rampa sequenziale, e pochi fasci fra le regioni. */
(function () {
  var svg = $('#cns'); if (!svg) return;
  var fig = svg.parentNode, G = 6, groups = [], leads = [], ann = null, loop = null, arw = null, portrait = null, P = null, A = null, hop = null, lastP = -1;
  var E = [[200, 130, 92, 66, 'cb'], [64, 128, 58, 92, 'ol'], [336, 128, 58, 92, 'ol'], [200, 220, 20, 26, 'nk'], [200, 288, 62, 50, 'v'], [200, 372, 66, 44, 'v'], [200, 446, 56, 40, 'v'], [200, 514, 30, 46, 'v']];
  function inE(x, y) { for (var k = 0; k < E.length; k++) { var e = E[k], a = (x - e[0]) / e[2], b = (y - e[1]) / e[3]; if (a * a + b * b <= 1) return k; } return -1; }
  function ed(p) { var e = E[p.k], a = (p.x - e[0]) / e[2], b = (p.y - e[1]) / e[3]; return 1 - Math.sqrt(a * a + b * b); }
  function gen() {
    var r = rng(166700), md = 9.6, cs = md / Math.SQRT2, gw = Math.ceil(400 / cs) + 1, gh = Math.ceil(570 / cs) + 1, grid = new Int32Array(gw * gh).fill(-1), tries = 0; P = [];
    while (tries++ < 26000) {
      var x = r() * 400, y = r() * 570, k = inE(x, y); if (k < 0) continue;
      var gx = x / cs | 0, gy = y / cs | 0, okp = true;
      for (var a = -2; a <= 2 && okp; a++) for (var b = -2; b <= 2; b++) { var X = gx + a, Y = gy + b; if (X < 0 || Y < 0 || X >= gw || Y >= gh) continue; var id = grid[Y * gw + X]; if (id >= 0) { var q = P[id], dx = q.x - x, dy = q.y - y; if (dx * dx + dy * dy < md * md) { okp = false; break; } } }
      if (okp) { grid[gy * gw + gx] = P.length; P.push({ x: x, y: y, k: k, rg: E[k][4] }); }
    }
    P.forEach(function (p) {
      var d = ed(p); p.role = 1;
      if (p.rg === 'ol' && r() < 0.26) p.role = 0; else if (p.rg === 'v' && d < 0.22 && r() < 0.3) p.role = 0; else if (p.rg === 'cb' && d < 0.18 && r() < 0.14) p.role = 0;
      else if (p.rg === 'nk' || (p.rg === 'v' && d > 0.5 && r() < 0.2)) p.role = 2;
    });
    A = P.map(function () { return []; }); var i, j;
    for (i = 0; i < P.length; i++) {
      var best = [];
      for (j = 0; j < P.length; j++) { if (i === j) continue; var dx = P[i].x - P[j].x, dy = P[i].y - P[j].y, d2 = dx * dx + dy * dy; if (best.length < 3 || d2 < best[2][0]) { best.push([d2, j]); best.sort(function (a, b) { return a[0] - b[0]; }); if (best.length > 3) best.pop(); } }
      best.forEach(function (b) { if (A[i].indexOf(b[1]) < 0) { A[i].push(b[1]); A[b[1]].push(i); } });
    }
    for (i = 0; i < P.length; i++) if (r() < 0.1) { j = Math.floor(r() * P.length); var dd = Math.hypot(P[i].x - P[j].x, P[i].y - P[j].y); if (dd > 70 && dd < 240) { A[i].push(j); A[j].push(i); } }
    hop = new Int16Array(P.length).fill(-1); var Q = []; for (i = 0; i < P.length; i++) if (P[i].role === 0) { hop[i] = 0; Q.push(i); }
    for (var h = 0; h < Q.length; h++) { var u = Q[h]; A[u].forEach(function (w) { if (hop[w] < 0) { hop[w] = hop[u] + 1; Q.push(w); } }); }
    for (i = 0; i < P.length; i++) if (hop[i] < 0) hop[i] = G - 1;
  }
  function build() {
    if (!P) gen();
    var w = fig.getBoundingClientRect().width; portrait = w < 1100; fig.classList.toggle('portrait', portrait);
    var sc = portrait ? 1 : 1.25, VW = portrait ? 440 : 1200, VH = portrait ? 880 : 808, ox = portrait ? 10 : 350, oy = portrait ? 206 : 18;
    svg.setAttribute('viewBox', '0 0 ' + VW + ' ' + VH); svg.setAttribute('preserveAspectRatio', portrait ? 'xMidYMid meet' : 'xMinYMid meet');
    var ng = [], g, i, s = '', X = function (x) { return f1(x * sc + ox); }, Y = function (y) { return f1(y * sc + oy); };
    for (g = 0; g < G; g++) ng.push('');
    for (i = 0; i < P.length; i++) {
      var p = P[i], hi = Math.min(G - 1, hop[i]);
      ng[hi] += p.role === 2 ? '<rect class="d" x="' + f1(p.x * sc + ox - 2.3) + '" y="' + f1(p.y * sc + oy - 2.3) + '" width="4.6" height="4.6"/>'
        : '<circle class="' + (p.role ? 'c' : 's') + '" cx="' + X(p.x) + '" cy="' + Y(p.y) + '" r="' + (p.role ? (1.35 + sc * 0.45) * (1.12 - 0.07 * hi) : 1.7 + sc * 0.5).toFixed(2) + '"/>';
    }
    /* fasci fra regioni: lobi ottici -> cervello, cervello -> collo -> cordone ventrale */
    var fx = '';
    function bundle(a, b, bend, fl) {
      var dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy), nx = -dy / l, ny = dx / l, mx = (a[0] + b[0]) / 2 + nx * bend, my = (a[1] + b[1]) / 2 + ny * bend;
      for (var k = -2; k <= 2; k++) fx += 'M' + X(a[0] + nx * k * 1.6) + ' ' + Y(a[1] + ny * k * 1.6) + 'Q' + X(mx + nx * k * fl) + ' ' + Y(my + ny * k * fl) + ' ' + X(b[0] + nx * k * 1.6) + ' ' + Y(b[1] + ny * k * 1.6);
    }
    bundle([92, 112], [168, 120], -14, 4); bundle([308, 112], [232, 120], 14, 4); bundle([92, 160], [170, 156], 10, 4); bundle([308, 160], [230, 156], -10, 4);
    bundle([200, 176], [200, 258], 0, 1.6);
    s += '<path class="fx" d="' + fx + '"/>';
    s += '<ellipse class="les" cx="' + X(64) + '" cy="' + Y(128) + '" rx="' + 63 * sc + '" ry="' + 97 * sc + '"/><ellipse class="les" cx="' + X(336) + '" cy="' + Y(128) + '" rx="' + 63 * sc + '" ry="' + 97 * sc + '"/>';
    for (g = 0; g < G; g++) s += '<g class="hg h' + g + '">' + ng[g] + '</g>';
    /* legenda accanto alla sagoma, a sinistra del cordone ventrale (in verticale dove il cordone si stringe) */
    var lx = portrait ? 12 : 150, ly = portrait ? 694 : 574, st = portrait ? 22 : 30, lg = '<g class="lgd">' + T(lx, ly, L.hop, 't-m');
    for (g = 0; g < G; g++) lg += '<circle class="lg' + g + '" cx="' + (lx + 6 + g * st) + '" cy="' + (ly + 18) + '" r="' + (g ? 3.6 * (1.12 - 0.07 * g) : 3.4).toFixed(2) + '"/>' + T(lx + 12 + g * st, ly + 22, g > 4 ? '5+' : g, 't-m');
    if (portrait) lg += '<circle class="s" cx="' + (lx + 6) + '" cy="' + (ly + 44) + '" r="3"/>' + T(lx + 16, ly + 48, L.pin, 't-m') + '<rect class="d" x="' + (lx + 3) + '" y="' + (ly + 61) + '" width="6" height="6"/>' + T(lx + 16, ly + 68, L.pout, 't-m') + '</g>';
    else lg += '<circle class="s" cx="' + (lx + 6) + '" cy="' + (ly + 44) + '" r="3"/>' + T(lx + 16, ly + 48, L.pin, 't-m') + '<rect class="d" x="' + (lx + 97) + '" y="' + (ly + 41) + '" width="6" height="6"/>' + T(lx + 109, ly + 48, L.pout, 't-m') + '</g>';
    var an = '', ld = '', lp, ah;
    function lead(d) { ld += '<path class="ld" pathLength="1" stroke-dasharray="1 1" d="' + d + '"/>'; }
    if (!portrait) {
      an += T(330, 168, L.tok, 't-m', 'end') + T(330, 192, L.in1, '', 'end') + T(330, 212, L.in2, '', 'end'); lead('M336 188H352L' + X(22) + ' ' + Y(126));
      an += T(330, 360, L.les1, 't-r', 'end') + T(330, 380, L.les2, 't-r', 'end') + T(330, 400, L.les3, 't-r', 'end'); lead('M336 376H352L' + X(40) + ' ' + Y(205));
      an += T(880, 40, L.core, 't-i') + T(880, 64, L.c2, 't-m') + T(880, 84, L.c3, 't-m'); lead('M872 35.5H' + X(216) + 'V' + Y(100));
      an += '<circle class="ldo" cx="' + X(216) + '" cy="' + Y(100) + '" r="3"/>';
      an += T(880, 480, L.o1) + T(880, 500, L.o2) + T(880, 526, L.o3, 't-m'); lead('M874 492H852L' + X(226) + ' ' + Y(384));
      lp = '<path class="loop" pathLength="1" stroke-dasharray="1 1" d="M900 544V728Q900 764 864 764H156Q120 764 120 728V224Q120 188 156 188H196"/>'; ah = 'M189 183.5L199 188L189 192.5z'; an += T(510, 794, L.att, 't-a', 'middle');
    } else {
      an += T(12, 104, L.tok, 't-m') + T(12, 126, L.in1 + ' ' + L.in2); lead('M40 134V' + Y(60));
      an += T(428, 150, L.core, 't-i', 'end') + T(428, 170, L.c2, 't-m', 'end') + T(428, 188, L.c3, 't-m', 'end'); lead('M300 196L' + X(200) + ' ' + Y(100));
      an += '<circle class="ldo" cx="' + X(200) + '" cy="' + Y(100) + '" r="3"/>';
      an += T(12, 826, L.o1 + ' ' + L.o2) + T(12, 848, L.o3, 't-m'); lead('M200 810L' + X(200) + ' ' + Y(548));
      an += T(428, 478, L.les1, 't-r', 'end') + T(428, 496, L.les2, 't-r', 'end') + T(428, 514, L.les3, 't-r', 'end'); lead('M404 462L' + X(336) + ' ' + Y(200));
      lp = '<path class="loop" pathLength="1" stroke-dasharray="1 1" d="M320 842Q436 842 436 740V150Q436 116 400 116H338"/>'; ah = 'M345 111.5L335 116L345 120.5z'; an += T(0, 0, L.attS, 't-a', 'middle', ' transform="translate(428 660) rotate(-90)"');
    }
    /* punta di freccia separata dal tracciato: compare solo a curva completa (un marker-end sarebbe visibile da subito) */
    svg.innerHTML = s + '<g>' + ld + lp + '<path class="arw" opacity="0" d="' + ah + '"/></g>' + lg + '<g class="ann">' + an + '</g>';
    groups = $$('.hg', svg); leads = $$('.ld', svg); loop = $('.loop', svg); arw = $('.arw', svg); ann = $('.ann', svg);
    var pd = nf(Math.round(166700 / P.length), 0); $$('.pd').forEach(function (e) { e.textContent = pd; });
    lastP = -1;
  }
  function set(p) {
    if (p === lastP) return; lastP = p;
    groups.forEach(function (g, k) { g.style.opacity = clamp(p * 7.2 - k, 0.06, 1); });
    var lp = clamp(p * 2.4 - 0.35, 0, 1); leads.forEach(function (l) { l.setAttribute('stroke-dashoffset', f1(1 - lp)); });
    ann.style.opacity = portrait ? 1 : clamp(p * 3 - 0.5, 0, 1);
    var q = clamp(p * 2 - 1, 0, 1); loop.setAttribute('stroke-dashoffset', (1 - q).toFixed(3)); loop.style.opacity = q ? 1 : 0;
    arw.setAttribute('opacity', q >= 0.97 ? '1' : '0');
  }
  var sc = scrubber(svg, function (r, vh) { return (vh * 0.95 - r.top) / (r.height * 0.75 + vh * 0.2); }, set);
  var lastW = 0;
  new ResizeObserver(function () { var w = fig.getBoundingClientRect().width; if (!lastW || (w < 1100) !== (lastW < 1100)) { lastW = w; build(); scrubNow(sc); } lastW = w; }).observe(fig);
})();

/* ---------- Fig. 3: linea del tempo dei kernel CUDA ---------- */
(function () {
  var svg = $('#kt'); if (!svg) return;
  var box = svg, rows = [], lastP = -1, W0 = 0;
  var pairs = [[27721, 1.40, 0.60], [27722, 1.07, 0.90]], n = 18;
  function kpath(x, y, ws, g) { var d = ''; for (var i = 0; i < n; i++) { x += g; d += 'M' + f1(x) + ' ' + y + 'h' + f1(ws[i]) + 'v16h' + f1(-ws[i]) + 'z'; x += ws[i]; } return [d, x]; }
  function build() {
    var w = wOf(box); if (!w) return; W0 = w;
    var narrow = w < 700, labW = narrow ? 0 : 204, ro = 58, x0 = labW, W = w - labW - ro, y = narrow ? 16 : 6, s = '', li = 0;
    rows = [];
    pairs.forEach(function (pr, pi) {
      var r = rng(pr[0]), k = pr[2], ws = [], sum = 0, i;
      for (i = 0; i < n; i++) { ws.push(0.6 + 1.4 * r()); sum += ws[i]; }
      ws = ws.map(function (x) { return x / sum * k * W; });
      var g0 = (1 - k) * W / n - 2, g1 = (W / pr[1] - k * W - 2) / n;
      for (var rr = 0; rr < 2; rr++) {
        if (narrow) s += T(x0, y - 5, L.k[li], 'fl'); else s += T(0, y + 12, L.k[li], 'fl');
        if (rr === 0) {
          var x = x0, d = '', tk = '';
          for (i = 0; i < n; i++) { tk += 'M' + f1(x) + ' ' + (y - 3) + 'h2v22h-2z'; x += 2 + g0; d += 'M' + f1(x) + ' ' + y + 'h' + f1(ws[i]) + 'v16h' + f1(-ws[i]) + 'z'; x += ws[i]; }
          s += '<path class="tk" d="' + tk + '"/><path class="kn" d="' + d + '"/>';
        } else {
          s += '<path class="tk" d="M' + f1(x0) + ' ' + (y - 3) + 'h2v22h-2z"/><path class="kn" data-r="' + rows.length + '"/>' + '<line class="endl" data-r="' + rows.length + '" y1="' + (y - 6) + '" y2="' + (y + 22) + '"/>' + T(w, y + 12, '', 'fv', 'end', ' data-r="' + rows.length + '"');
          rows.push({ x0: x0, y: y, ws: ws, g0: g0, g1: g1, R: pr[1] });
        }
        li++; y += narrow ? 44 : 30;
      }
      y += narrow ? 12 : 14;
    });
    y += 4;
    var ticks = narrow ? [0, 0.5, 1] : [0, 0.25, 0.5, 0.75, 1];
    s += ln(x0, y, x0 + W, y, 'ax');
    ticks.forEach(function (tv) { var x = x0 + tv * W; s += ln(x, y, x, y + 5, 'ax') + T(x, y + 18, tv === 0 || tv === 1 ? nf(tv, 0) : nf(tv, tv === 0.5 ? 1 : 2), 'fm', tv === 1 ? 'end' : tv === 0 ? 'start' : 'middle'); });
    s += T(x0, y + 38, L.kax, 'fl');
    var H = y + 46;
    svg.setAttribute('viewBox', '0 0 ' + w + ' ' + H); svg.setAttribute('width', w); svg.setAttribute('height', H);
    svg.innerHTML = s;
    rows.forEach(function (rw, i) { rw.path = $('.kn[data-r="' + i + '"]', svg); rw.line = $('.endl[data-r="' + i + '"]', svg); rw.txt = $('text[data-r="' + i + '"]', svg); });
    lastP = -1;
  }
  function set(p) {
    if (p === lastP) return; lastP = p;
    rows.forEach(function (rw) {
      var o = kpath(rw.x0 + 2, rw.y, rw.ws, lerp(rw.g0, rw.g1, p));
      rw.path.setAttribute('d', o[0]); rw.line.setAttribute('x1', f1(o[1])); rw.line.setAttribute('x2', f1(o[1]));
      rw.txt.textContent = nf(1 - p * (1 - 1 / rw.R), 2) + '×';
    });
  }
  var sc = scrubber(svg, function (r, vh) { return sst((vh * 0.9 - r.top) / (vh * 0.5)); }, set);
  new ResizeObserver(function () { if (wOf(box) !== W0) { build(); scrubNow(sc); } }).observe(box);
})();

/* ---------- Fig. 4: asse logaritmico dell'errore ---------- */
(function () {
  var svg = $('#err'); if (!svg) return;
  var box = svg, W0 = 0, lastP = -1, X, ya, pt, lk, rd;
  function build() {
    var w = wOf(box); if (!w) return; W0 = w;
    var narrow = w < 600, H = narrow ? 150 : 124, x0 = narrow ? 8 : 12, x1 = w - (narrow ? 22 : 40), s = '';
    ya = H - (narrow ? 58 : 46);
    X = function (l) { return x0 + (-l) / 5 * (x1 - x0); };
    s += ln(x0, ya, x1, ya, 'ax');
    for (var d = 0; d <= 5; d++) {
      var x = X(-d); s += ln(x, ya, x, ya + 6, 'ax');
      s += d === 0 ? T(x, ya + 22, '1', 'fm', 'start') : '<text x="' + f1(x) + '" y="' + (ya + 22) + '" class="fm" text-anchor="middle">10<tspan dy="-5" class="ex">−' + d + '</tspan></text>';
    }
    var xf = X(-4.36);
    s += ln(xf, ya - 10, xf, ya + 10, 'tgt') + T(xf, ya + (narrow ? 44 : 40), L.fix, 'fl', 'middle');
    s += T(x0, ya + (narrow ? 44 : 40), L.cosax, 'fl', 'start');
    var xp = X(-0.62);
    s += T(xp - 7, ya - 30, L.pad, 'fl', 'start');
    s += '<line class="lk" x1="' + f1(xp) + '" y1="' + ya + '" x2="' + f1(xp) + '" y2="' + ya + '"/>';
    s += '<circle class="p0" cx="' + f1(xp) + '" cy="' + ya + '" r="4.5"/><circle class="p1" cx="' + f1(xp) + '" cy="' + ya + '" r="5"/>';
    s += T(xp, ya - 12, '', 'fv', 'middle', ' id="err-v"');
    svg.setAttribute('viewBox', '0 0 ' + w + ' ' + H); svg.setAttribute('width', w); svg.setAttribute('height', H);
    svg.innerHTML = s; pt = $('.p1', svg); lk = $('.lk', svg); rd = $('#err-v', svg); lastP = -1;
  }
  function set(p) {
    if (p === lastP) return; lastP = p;
    /* si muove solo il punto; l'etichetta mostra solo i due valori misurati, e scatta a meta' corsa */
    var x = X(lerp(-0.62, -4.36, p));
    pt.setAttribute('cx', f1(x)); lk.setAttribute('x2', f1(x)); rd.setAttribute('x', f1(x));
    rd.textContent = p >= 0.5 ? nf(0.999956, 6) : nf(0.76, 2);
  }
  var sc = scrubber(svg, function (r, vh) { return (vh * 0.85 - r.top) / (vh * 0.5); }, set);
  new ResizeObserver(function () { if (wOf(box) !== W0) { build(); scrubNow(sc); } }).observe(box);
})();

/* ---------- Fig. 5: il recinto di Vergilius ---------- */
(function () {
  var svg = $('#fence'); if (!svg) return;
  var box = svg, W0 = 0, lastP = -1, path, cells = [], stamped = rm, closed = false;
  var A = { cols: 7, n: 35, red: [9, 20, 31] }, B = { cols: 6, n: 36, red: [22] };
  var pt = 21, cz = 17;
  function waffle(x, y, cfg, out) {
    var s = '', m = cz * 0.28;
    for (var i = 0; i < cfg.n; i++) {
      var cx = x + (i % cfg.cols) * pt, cy = y + Math.floor(i / cfg.cols) * pt, red = cfg.red.indexOf(i) >= 0;
      s += '<g class="cell' + (red ? ' r' : '') + (stamped ? ' in' : '') + '"><rect x="' + f1(cx + 0.5) + '" y="' + f1(cy + 0.5) + '" width="' + (cz - 1) + '" height="' + (cz - 1) + '"/>' + (red ? '<path class="x" d="M' + f1(cx + m) + ' ' + f1(cy + m) + 'L' + f1(cx + cz - m) + ' ' + f1(cy + cz - m) + 'M' + f1(cx + cz - m) + ' ' + f1(cy + m) + 'L' + f1(cx + m) + ' ' + f1(cy + cz - m) + '"/>' : '') + '</g>';
      out.push(red);
    }
    return s;
  }
  function build() {
    var w = wOf(box); if (!w) return; W0 = w;
    var st = w < 560, top = 10, pad = 22, s = '', H, reds = [];
    pt = st ? 17 : 21; cz = st ? 14 : 17;
    /* il blocco dei turni ha larghezza fissa; l'asse della velocita' prende tutto il resto: niente vuoto nel recinto */
    var wA = A.cols * pt - (pt - cz), wB = B.cols * pt - (pt - cz), gap = st ? 40 : 52, RB = wA + gap + wB;
    var lx0 = pad, lx1 = st ? w - pad : w - RB - 3 * pad, ly = 44;
    var X = function (v) { return lx0 + v / 110 * (lx1 - lx0); }, ry = ly + 78;
    s += T(lx0, ly, L.ts, 'fl');
    s += ln(lx0, ry, lx1, ry, 'ax');
    var step = (lx1 - lx0) / 11 < 30 ? 20 : 10;
    for (var v = 0; v <= 110; v += 10) { var big = v % 50 === 0; s += ln(X(v), ry, X(v), ry + (big ? 8 : 5), 'ax'); if (v % step === 0) s += T(X(v), ry + 22, nf(v, 0), 'fm', 'middle'); }
    s += '<path class="brk" d="M' + f1(X(78)) + ' ' + (ry - 22) + 'v-6H' + f1(X(100)) + 'v6"/>' + T(X(100), ry - 36, L.dr + ' · ' + nf(78, 0) + '-' + nf(100, 0), 'fl2', 'end');
    s += '<circle class="p1" cx="' + f1(X(64)) + '" cy="' + ry + '" r="5"/>' + T(X(64) + 3, ry - 12, L.dec + ' · ' + nf(64, 0), 'fl2', 'end');
    var rx0 = st ? pad : w - RB - pad, rtop = st ? ry + 62 : ly;
    s += T(rx0, rtop, L.turns, 'fl');
    var wy = rtop + 18;
    s += waffle(rx0, wy, A, reds);
    var bx = rx0 + wA + gap;
    s += T(rx0 + wA + gap / 2, wy + 3 * pt, '→', 'fm', 'middle');
    s += waffle(bx, wy, B, reds);
    s += T(rx0, wy + 6 * pt + 20, '3/35', 'fv') + T(bx, wy + 6 * pt + 20, '1/36', 'fv');
    H = wy + 6 * pt + 38;
    if (!st) H = Math.max(H, ry + 44);
    s += '<rect class="lbx" x="12" y="' + (top - 9) + '" width="10" height="18"/>' + T(20, top + 4.5, L.fence, 'fl lbt');
    svg.setAttribute('viewBox', '0 0 ' + w + ' ' + H); svg.setAttribute('width', w); svg.setAttribute('height', H);
    svg.innerHTML = '<path class="fen" pathLength="1"/>' + s;
    var lt = $('.lbt', svg), tw = 200; try { tw = lt.getComputedTextLength(); } catch (e) {}
    var sx = 20 + tw + 8; $('.lbx', svg).setAttribute('width', f1(tw + 16));
    path = $('.fen', svg);
    path.setAttribute('d', 'M' + f1(sx) + ' ' + top + 'H' + (w - 0.5) + 'V' + (H - 0.5) + 'H0.5V' + top + 'H' + f1(sx));
    var g = $$('.cell', svg), order = [];
    g.forEach(function (c, i) { if (!reds[i]) order.push(c); }); g.forEach(function (c, i) { if (reds[i]) order.push(c); });
    cells = order; lastP = -1; svg.classList.toggle('chiuso', closed);
  }
  function set(p) {
    if (p === lastP) return; lastP = p;
    var f = lerp(40 / 360, 1, sst(p / 0.6));
    path.setAttribute('stroke-dasharray', f.toFixed(4) + ' 1');
    if (f >= 1 && !closed) { closed = true; svg.classList.add('chiuso'); }
  }
  function stamp() { if (stamped) return; stamped = true; cells.forEach(function (c, i) { c.style.transitionDelay = rm ? '0ms' : (i * 10) + 'ms'; c.classList.add('in'); }); }
  var sc = scrubber(svg, function (r, vh) { return (vh * 0.9 - r.top) / (vh * 0.6); }, set);
  new IntersectionObserver(function (es, o) { if (es[0].isIntersecting) { stamp(); o.disconnect(); } }, { threshold: 0.4 }).observe(svg);
  new ResizeObserver(function () { if (wOf(box) !== W0) { build(); scrubNow(sc); } }).observe(box);
  if (D.fonts && D.fonts.ready) D.fonts.ready.then(function () { build(); scrubNow(sc); });
  RMq.addEventListener('change', function () { if (rm) { stamp(); closed = true; svg.classList.add('chiuso'); } });
})();

/* ---------- note a margine: evidenziatore quando il testo entra ---------- */
var noteIO = new IntersectionObserver(function (es) {
  es.forEach(function (e) {
    if (!e.isIntersecting) return;
    e.target.classList.add('on');
    (e.target.getAttribute('data-notes') || '').split(' ').forEach(function (id) { var n = id && D.getElementById(id); if (n) n.classList.add('on'); });
    noteIO.unobserve(e.target);
  });
}, { rootMargin: '0px 0px -35% 0px' });
$$('[data-notes]').forEach(function (e) { if (rm) { e.classList.add('on'); e.getAttribute('data-notes').split(' ').forEach(function (id) { var n = D.getElementById(id); if (n) n.classList.add('on'); }); } else noteIO.observe(e); });

/* ---------- scroll ---------- */
var ly = scrollY, lt = performance.now();
addEventListener('scroll', function () {
  var nw = performance.now(), y = scrollY;
  Ras.kick(Math.abs(y - ly) / Math.max(8, nw - lt)); ly = y; lt = nw;
  dirty = 1; need();
}, { passive: true });
addEventListener('resize', function () { dirty = 1; need(); });
RMq.addEventListener('change', function () {
  rm = RMq.matches; Ras.motion();
  scr.forEach(scrubNow);
  if (rm) $$('[data-notes]').forEach(function (e) { e.classList.add('on'); });
});

/* ---------- testata: barra fissa dopo l'hero, testatina corrente ---------- */
(function () {
  var mast = $('#mast'), slot = $('#mast-slot'), h1 = $('h1'), cur = $('#cur'); if (!mast || !h1) return;
  var links = $$('.nav a, .toc a');
  new IntersectionObserver(function (es) {
    var e = es[0], on = !e.isIntersecting && e.boundingClientRect.top < 0;
    if (on === mast.classList.contains('stuck')) return;
    if (on) { slot.style.height = mast.offsetHeight + 'px'; mast.classList.add('stuck'); }
    else { mast.classList.remove('stuck'); slot.style.height = ''; }
  }).observe(h1);
  var secIO = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (!e.isIntersecting) return;
      cur.textContent = e.target.getAttribute('data-k');
      var id = '#' + e.target.id;
      links.forEach(function (a) { if (a.getAttribute('href') === id) a.setAttribute('aria-current', 'location'); else a.removeAttribute('aria-current'); });
    });
  }, { rootMargin: '-45% 0px -54% 0px' });
  $$('[data-k]').forEach(function (s) { secIO.observe(s); });
})();

/* ---------- indice a comparsa (details) ---------- */
$$('details.toc').forEach(function (d) {
  $$('a', d).forEach(function (a) { a.addEventListener('click', function () { d.open = false; }); });
});
D.addEventListener('keydown', function (e) { if (e.key === 'Escape') $$('details.toc[open]').forEach(function (d) { d.open = false; $('summary', d).focus(); }); });
D.addEventListener('click', function (e) { $$('details.toc[open]').forEach(function (d) { if (!d.contains(e.target)) d.open = false; }); });

/* ---------- tema ---------- */
/* tre stati: chiaro, scuro, auto (segue il sistema e cancella la scelta salvata) */
function pref() { var t = root.getAttribute('data-theme'); return t === 'dark' || t === 'light' ? t : 'auto'; }
function syncTheme() { var t = pref(); $$('[data-set]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-set') === t)); }); }
$$('[data-set]').forEach(function (b) {
  b.addEventListener('click', function () {
    var t = b.getAttribute('data-set');
    if (t === 'auto') { root.removeAttribute('data-theme'); try { localStorage.removeItem('ai-theme'); } catch (e) {} }
    else { root.setAttribute('data-theme', t); try { localStorage.setItem('ai-theme', t); } catch (e) {} }
    syncTheme(); setTimeout(Ras.redraw, 20);
  });
});
DARKq.addEventListener('change', function () { syncTheme(); Ras.redraw(); });
syncTheme();

/* ---------- lingua: conserva l'ancora ---------- */
$$('.lang a').forEach(function (a) { a.addEventListener('click', function () { if (location.hash) a.href = a.getAttribute('href').split('#')[0] + location.hash; }); });

/* ---------- mostra la griglia ---------- */
var gb = $('#gridbtn');
if (gb) gb.addEventListener('click', function () { var on = root.classList.toggle('show-grid'); gb.setAttribute('aria-pressed', String(on)); gb.textContent = L.grid[on ? 1 : 0]; });

if (D.fonts && D.fonts.ready) D.fonts.ready.then(function () { Ras.redraw(); });
dirty = 1; need();
})();
