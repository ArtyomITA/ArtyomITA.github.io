/* artyomita.github.io · figure calcolate nella pagina (canvas 2D e SVG scritti a mano, nessuna libreria).
   Un solo gestore di scroll passivo, un solo requestAnimationFrame per fotogramma, figure attive solo
   quando un IntersectionObserver le vede. prefers-reduced-motion: un fotogramma finale per figura. */
(function () {
'use strict';
var D = document, root = D.documentElement, lang = root.lang === 'en' ? 'en' : 'it';
var RMq = matchMedia('(prefers-reduced-motion: reduce)'), rm = RMq.matches, DARKq = matchMedia('(prefers-color-scheme: dark)');
function $(s, c) { return (c || D).querySelector(s); }
function $$(s, c) { return [].slice.call((c || D).querySelectorAll(s)); }
function clamp(x, a, b) { return x < a ? a : x > b ? b : x; }
function lerp(a, b, t) { return a + (b - a) * t; }
function sst(x) { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); }
function rng(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; var t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
/* numeri alla maniera della lingua della pagina, senza Intl (costruirlo costa decine di ms su CPU lente) */
function nf(x, d) { var p = Math.abs(x).toFixed(d).split('.'), th = lang === 'it' ? '.' : ',', i = p[0].replace(/\B(?=(\d{3})+(?!\d))/g, th); return (x < 0 ? '−' : '') + i + (d ? (lang === 'it' ? ',' : '.') + p[1] : ''); }
function f1(x) { return (Math.round(x * 10) / 10).toString(); }
function T(x, y, s, cls, anc, extra) { return '<text x="' + f1(x) + '" y="' + f1(y) + '"' + (cls ? ' class="' + cls + '"' : '') + (anc ? ' text-anchor="' + anc + '"' : '') + (extra || '') + '>' + s + '</text>'; }
function ln(x1, y1, x2, y2, cls) { return '<line x1="' + f1(x1) + '" y1="' + f1(y1) + '" x2="' + f1(x2) + '" y2="' + f1(y2) + '" class="' + cls + '"/>'; }
/* righe di testo in colonna */
function T3(x, y, dy, a, cls, anc) { return a.map(function (s, i) { return T(x, y + i * dy, s, cls[i], anc); }).join(''); }
function wOf(el) { return Math.round(el.getBoundingClientRect().width); }
/* cella quadrata di Fig. 5 e 6; rossa con la croce se sbagliata */
function cell(x, y, z, red, cls) { var m = z * 0.28, a = f1(x + m), b = f1(y + m), c = f1(x + z - m), d = f1(y + z - m); return '<g class="cell' + (red ? ' r' : '') + (cls || '') + '"><rect x="' + f1(x + 0.5) + '" y="' + f1(y + 0.5) + '" width="' + (z - 1) + '" height="' + (z - 1) + '"/>' + (red ? '<path class="x" d="M' + a + ' ' + b + 'L' + c + ' ' + d + 'M' + c + ' ' + b + 'L' + a + ' ' + d + '"/>' : '') + '</g>'; }

var L = {
  it: { sens: 'sensoriali', cen: 'centrali', desc: 'discendenti', rate: 'tasso', ro: ['t', 'ingresso ×', 'spike/ms'],
    tok: 'token · BPE 4096', in1: 'ingresso: 17.937', in2: 'neuroni sensoriali', core: 'nucleo ricorrente LIF', c2: '166.700 neuroni · 2,75 M sinapsi (≥ 10)', c3: '4+4 sottopassi per token',
    o1: 'lettura: 2.241 neuroni', o2: 'discendenti e motori', o3: '→ logit del prossimo token', att: 'attention causale esterna · 4 teste · cache 128 · rientra dalle stesse porte', attS: 'attention esterna · 4 teste · cache 128',
    les1: 'lesione in silico:', les2: 'lobo ottico rimosso,', les3: 'cross-entropy invariata', hop: 'salti dalle porte', hop2: ['salti dalle', 'porte'], pin: 'ingresso', pout: 'uscita',
    k: ['MoE · un lancio per kernel', 'MoE · CUDA graph', 'denso · un lancio per kernel', 'denso · CUDA graph'], kax: 'tempo per token, relativo',
    pad: 'padding · cos 0,76', padv: '1 − cos = 0,24', fix: 'fix · cos 0,999956', fixv: '1 − cos = 4,4·10', ratio: '≈ 5.500 volte più vicino', cosax: '1 − coseno', ts: 'tok/s su GTX 1080', dec: 'decodifica', dr: 'con drafter', turns: 'turni con cifre non supportate', fence: 'GTX 1080 · nessuna chiamata esterna',
    two: '2 salti', sp: 'massimo spendibile', tet: 'tetto del bot', pag: 'prezzo pagato', hit: 'tetto ≥ prezzo', cr: 'crediti', lots: "28 lotti simulati, in ordine d'asta", bridge: 'ponte FantaAsta Live · assegnazioni identiche',
    grid: ['mostra la griglia', 'nascondi la griglia'] },
  en: { sens: 'sensory', cen: 'central', desc: 'descending', rate: 'rate', ro: ['t', 'input ×', 'spikes/ms'],
    tok: 'token · BPE 4096', in1: 'input: 17,937', in2: 'sensory neurons', core: 'recurrent LIF core', c2: '166,700 neurons · 2.75 M synapses (≥ 10)', c3: '4+4 substeps per token',
    o1: 'readout: 2,241 descending', o2: 'and motor neurons', o3: '→ next-token logits', att: 'external causal attention · 4 heads · cache 128 · re-enters through the same ports', attS: 'external attention · 4 heads · cache 128',
    les1: 'in-silico lesion:', les2: 'optic lobe removed,', les3: 'cross-entropy unchanged', hop: 'hops from the ports', hop2: ['hops from', 'the ports'], pin: 'input', pout: 'output',
    k: ['MoE · one launch per kernel', 'MoE · CUDA graph', 'dense · one launch per kernel', 'dense · CUDA graph'], kax: 'time per token, relative',
    pad: 'padding · cos 0.76', padv: '1 − cos = 0.24', fix: 'fix · cos 0.999956', fixv: '1 − cos = 4.4·10', ratio: '≈ 5,500 times closer', cosax: '1 − cosine', ts: 'tok/s on GTX 1080', dec: 'decoding', dr: 'with drafter', turns: 'turns with unsupported numbers', fence: 'GTX 1080 · no external calls',
    two: '2 hops', sp: 'maximum spendable', tet: 'bot cap', pag: 'price paid', hit: 'cap ≥ price', cr: 'credits', lots: '28 simulated lots, in auction order', bridge: 'FantaAsta Live bridge · identical assignments',
    grid: ['show the grid', 'hide the grid'] }
}[lang];

/* pianificatore: scroll passivo, un rAF per fotogramma */
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
/* le figure 3-6 hanno nell'HTML una copia statica al fotogramma finale: si ricostruiscono solo quando si avvicinano */
function near(el, fn) { new IntersectionObserver(function (es, o) { if (es[0].isIntersecting) { o.disconnect(); fn(); } }, { rootMargin: '100% 0px' }).observe(el); }
function scrubNow(s) { s.set(rm ? 1 : clamp(s.p(s.el.getBoundingClientRect(), innerHeight), 0, 1)); }
/* ricostruzione: la prima quando la figura si avvicina, poi a ogni cambio di larghezza; gate() puo' rimandarla */
function live(box, build, sc, gate) {
  var on = false, w0 = -1;
  function go() { if (on && (!gate || gate())) { w0 = wOf(box); build(); scrubNow(sc); } }
  near(box, function () { on = true; go(); });
  new ResizeObserver(function () { if (on && wOf(box) !== w0) go(); }).observe(box);
  return go;
}
function vb(svg, w, h) { svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h); svg.setAttribute('width', w); svg.setAttribute('height', h); }

/* Fig. 1: raster LIF guidato dallo scroll (canvas)
   Il raster vive in un buffer circolare fuori schermo, una colonna di pixel per ms simulato: ogni fotogramma
   dipinge solo le colonne nuove e copia il buffer sul canvas in due pezzi. Al massimo 30 fotogrammi al secondo;
   il ciclo parte solo dopo il load e un momento libero del thread. */
var Ras = (function () {
  var c = $('#raster');
  if (!c || !c.getContext) return { kick: function () {}, frame: function () {}, live: function () { return false; }, redraw: function () {}, motion: function () {} };
  var ctx = c.getContext('2d'), box = c.parentNode, ro = $('#readout'), WIN = 720, off = D.createElement('canvas'), oc = off.getContext('2d');
  var N, S, C, Dn, v, inp, nxt, rf, typ, tgt, wt, hist, rate, sm, rs, t, nextTok, lastTok = -1, rnd, drive = 0;
  var cap = 1, W = 0, H = 0, dpr = 1, vis = false, run = false, armed = false, last = 0, lastRo = 0, col, lab = 80, forced = false, idle = performance.now(), settle = -1, settleTok = -1;
  var rH, top = 4, gp = 8, sb = 18, rh, th, px, painted = 0, FILL, CI = [0, 1, 2, 0];
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
    hist = new Array(WIN); rate = new Float32Array(WIN); sm = new Float32Array(WIN); rs = 0; t = 0; cap = N * 0.04; nextTok = 12; lastTok = -1; painted = 0;
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
    /* tasso: media mobile su 13 ms tenuta a parte, cosi' il disegno non la ricalcola */
    rs += spk.length; if (t >= 13) rs -= rate[(t - 13) % WIN];
    /* scala del tasso: sale del 10% oltre ogni nuovo massimo, cosi' la curva non viene mai tagliata in un plateau */
    var r = rs / Math.min(t + 1, 13); if (r > cap) cap = r * 1.1;
    hist[t % WIN] = spk; rate[t % WIN] = spk.length; sm[t % WIN] = r; t++; drive *= 0.994;
  }
  /* il declassamento a 72 neuroni si decide qui, prima del primo fotogramma, mai a meta' animazione */
  function warm() {
    var n = rm ? 960 : WIN, t0 = performance.now(), i;
    for (i = 0; i < n; i++) step();
    if (!forced && N > 72 && (performance.now() - t0) / n > 0.05) { forced = true; build(); geo(); for (i = 0; i < n; i++) step(); }
  }
  function yOf(i) { return top + i * rh + (i < S ? 0 : i < S + C ? gp : 2 * gp); }
  function fontSz() { return W < 560 ? 12 : 13; }
  function measure() {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.font = fontSz() + 'px ' + col.font;
    lab = Math.ceil(Math.max(ctx.measureText(L.sens).width, ctx.measureText(L.cen).width, ctx.measureText(L.desc).width, ctx.measureText(L.rate).width)) + 14;
  }
  function geo() {
    rH = Math.round(H * 0.15); rh = (H - rH - top - 2 * gp - sb - 10) / N; th = Math.max(1.4, rh * 0.7); px = (W - lab) / WIN;
    off.width = WIN; off.height = Math.max(1, Math.ceil((yOf(N - 1) + rh - top) * dpr)); painted = 0;
  }
  /* dipinge nel buffer le colonne non ancora dipinte, una per ms */
  function paint() {
    var from = Math.max(painted, t - WIN), k, q, x, Ls, h = Math.max(1, th * dpr);
    if (t - from >= WIN) oc.clearRect(0, 0, WIN, off.height); else for (k = from; k < t; k++) oc.clearRect(k % WIN, 0, 1, off.height);
    /* un fillStyle per colore, non per tratto */
    for (var cI = 0; cI < 3; cI++) {
      oc.fillStyle = FILL[cI];
      for (k = from; k < t; k++) { x = k % WIN; Ls = hist[x]; for (q = 0; q < Ls.length; q++) { var i = Ls[q]; if (CI[typ[i]] === cI) oc.fillRect(x, (yOf(i) - top + (rh - th) / 2) * dpr, 1, h); } }
    }
    painted = t;
  }
  function draw() {
    if (!W || !hist) return;
    paint();
    var n = Math.min(t, WIN), k, pos = t % WIN, dx = lab * dpr, dw = px * dpr;
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, c.width, c.height); ctx.imageSmoothingEnabled = false;
    if (t >= WIN) {
      ctx.drawImage(off, pos, 0, WIN - pos, off.height, dx, top * dpr, (WIN - pos) * dw, off.height);
      if (pos) ctx.drawImage(off, 0, 0, pos, off.height, dx + (WIN - pos) * dw, top * dpr, pos * dw, off.height);
    } else if (t) ctx.drawImage(off, 0, 0, t, off.height, dx + (WIN - t) * dw, top * dpr, t * dw, off.height);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    var y0 = H - sb - rH, yb = H - sb - 4;
    ctx.strokeStyle = col.rule; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(lab, yb + 0.5); ctx.lineTo(W, yb + 0.5); ctx.stroke();
    ctx.strokeStyle = col.fig; ctx.lineWidth = 1.3; ctx.beginPath();
    for (k = 0; k < n; k++) {
      var yy = yb - Math.min(1, sm[(t - n + k) % WIN] / cap) * (rH - 6), xx = lab + (WIN - n + k) * px;
      if (k) ctx.lineTo(xx, yy); else ctx.moveTo(xx, yy);
    }
    ctx.stroke();
    ctx.fillStyle = col.ink2; ctx.strokeStyle = col.ink3; ctx.lineWidth = 1; ctx.font = fontSz() + 'px ' + col.font; ctx.textBaseline = 'middle';
    [[0, S, L.sens], [S, S + C, L.cen], [S + C, N, L.desc]].forEach(function (g) {
      var a = yOf(g[0]), b = yOf(g[1] - 1) + rh, bx = Math.round(lab - 9) + 0.5;
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
  /* un solo getComputedStyle per tutte le variabili; la prima lettura avviene nel ResizeObserver, a layout gia' fatto */
  function colors() { var cs = getComputedStyle(root), v = function (n) { return cs.getPropertyValue(n).trim(); }; col = { fig: v('--fig'), ink: v('--ink'), ink2: v('--ink-2'), ink3: v('--ink-3'), inh: v('--inh'), rule: v('--rule'), font: getComputedStyle(D.body).fontFamily, mono: v('--mono') }; FILL = [col.fig, col.ink, col.inh]; }
  function size() {
    if (!col) colors();
    var b = box.getBoundingClientRect(), nw = Math.round(b.width), old = W; W = nw; H = Math.round(b.height); dpr = Math.min(2, devicePixelRatio || 1);
    c.width = Math.round(W * dpr); c.height = Math.round(H * dpr);
    measure();
    /* riscaldamento e primo disegno in due task separati, cosi' nessuno dei due blocca a lungo il caricamento */
    if (!old || (old < 560) !== (W < 560) || !hist) { build(); geo(); setTimeout(function () { warm(); setTimeout(function () { draw(); readout(0, true); }, 0); }, 0); }
    else { geo(); draw(); readout(0, true); }
  }
  function ok() { return armed && vis && !rm && D.visibilityState === 'visible'; }
  function start() { if (!run && ok()) { run = true; last = 0; settle = -1; need(); } }
  function stop() { run = false; draw(); readout(0, true); }
  function frame(now) {
    if (!run) return;
    if (!ok()) { stop(); return; }
    if (last && now - last < 33) return;
    var dt = last ? Math.min(50, now - last) : 33; last = now;
    for (var i = 0, st = Math.max(1, Math.round(dt * 0.2)); i < st; i++) step();
    draw(); readout(now);
    /* pagina ferma da 7 s: si aspetta il prossimo token e 360 ms simulati (raffica a meta' finestra), poi stop */
    if (performance.now() - idle > 7000) {
      if (settle < 0) { settle = t; settleTok = -1; }
      if (settleTok < 0 && lastTok >= settle) settleTok = lastTok;
      if (settleTok >= 0 && t - settleTok >= 360) stop();
    }
  }
  function arm() { armed = true; idle = performance.now(); start(); }
  function later() { if (window.requestIdleCallback) requestIdleCallback(arm, { timeout: 2500 }); else setTimeout(arm, 1200); }
  c.setAttribute('width', 1);
  new ResizeObserver(size).observe(box);
  new IntersectionObserver(function (e) { vis = e[0].isIntersecting; if (vis) start(); }).observe(box);
  box.addEventListener('pointerenter', function () { idle = performance.now(); start(); });
  D.addEventListener('visibilitychange', function () { if (D.visibilityState === 'visible') { idle = performance.now(); start(); } });
  if (D.readyState === 'complete') later(); else addEventListener('load', later);
  return {
    kick: function (vel) { if (rm) return; drive = Math.min(6, drive + vel * 0.08); idle = performance.now(); settle = -1; start(); },
    frame: frame, live: function () { return run; },
    redraw: function () { if (col) colors(); if (W) { measure(); geo(); draw(); } },
    motion: function () { run = false; drive = 0; build(); geo(); warm(); draw(); readout(0, true); if (!rm) { idle = performance.now(); start(); } }
  };
})();

/* Fig. 2: connettoma schematico, raggiungibilita' per salti (SVG)
   Sagoma: un solo contorno chiuso (Catmull-Rom su 36 punti per lato). Punti a disco di Poisson dentro il contorno,
   grafo dei 3 vicini (non disegnato), salti contati dalle porte d'ingresso: lobi ottici esterni e fascia dorsale.
   Il readout (quadratini) sta dove il grafo e' a 2 salti. Si genera solo quando la figura si avvicina. */
(function () {
  var svg = $('#cns'); if (!svg) return;
  var fig = svg.parentNode, G = 6, groups = [], leads = [], ann = null, loop = null, arw = null, portrait = null, P = null, hop = null, lastP = -1, OUT = '', built = false;
  var R = [[200, 74], [226, 72], [252, 66], [276, 56], [300, 40], [330, 30], [362, 38], [384, 62], [394, 98], [396, 140], [388, 182], [368, 210], [340, 224], [312, 218], [290, 202],
    [268, 192], [246, 196], [226, 206], [216, 222], [218, 240], [244, 250], [262, 270], [266, 298], [256, 322], [244, 334], [262, 352], [268, 380], [258, 406], [244, 416],
    [254, 432], [256, 458], [246, 478], [234, 496], [228, 522], [218, 548], [200, 562]];
  function cr(q, k, u) { var a = q[0][k], b = q[1][k], c = q[2][k], d = q[3][k]; return 0.5 * (2 * b + (c - a) * u + (2 * a - 5 * b + 4 * c - d) * u * u + (3 * b - a - 3 * c + d) * u * u * u); }
  /* contorno campionato: meta' destra, poi la sinistra specchiata */
  function outline() {
    var K = R.slice(0, -1).concat(R.slice(1).reverse().map(function (p) { return [400 - p[0], p[1]]; })), n = K.length, pts = [];
    for (var i = 0; i < n; i++) {
      var q = [K[(i - 1 + n) % n], K[i], K[(i + 1) % n], K[(i + 2) % n]];
      for (var s = 0; s < 6; s++) pts.push([cr(q, 0, s / 6), cr(q, 1, s / 6)]);
    }
    return pts;
  }
  function region(x, y) { var a = (Math.abs(x - 200) - 145) / 55, b = (y - 127) / 99; if (a * a + b * b <= 1) return 'ol'; return y < 214 ? 'cb' : y < 246 ? 'nk' : 'v'; }
  function gen() {
    OUT = outline();
    /* maschera del contorno: un canvas 400x570 riempito una volta, poi lookup per pixel */
    var mc = D.createElement('canvas'), mx = mc.getContext('2d'); mc.width = 400; mc.height = 570;
    mx.beginPath(); OUT.forEach(function (p, i) { if (i) mx.lineTo(p[0], p[1]); else mx.moveTo(p[0], p[1]); }); mx.closePath(); mx.fill();
    var M = mx.getImageData(0, 0, 400, 570).data;
    var r = rng(166700), md = 9.6, cs = md / Math.SQRT2, gw = Math.ceil(400 / cs) + 1, gh = Math.ceil(570 / cs) + 1, grid = new Int32Array(gw * gh).fill(-1), tries = 0, i, j; P = [];
    while (tries++ < 26000) {
      var x = r() * 400, y = r() * 570; if (M[((y | 0) * 400 + (x | 0)) * 4 + 3] < 128) continue;
      var gx = x / cs | 0, gy = y / cs | 0, okp = true;
      for (var a = -2; a <= 2 && okp; a++) for (var b = -2; b <= 2; b++) { var X = gx + a, Y = gy + b; if (X < 0 || Y < 0 || X >= gw || Y >= gh) continue; var id = grid[Y * gw + X]; if (id >= 0) { var q = P[id], dx = q.x - x, dy = q.y - y; if (dx * dx + dy * dy < md * md) { okp = false; break; } } }
      if (okp) { grid[gy * gw + gx] = P.length; P.push({ x: x, y: y, rg: region(x, y), role: 1 }); }
    }
    /* porte: bordo esterno dei lobi ottici e fascia dorsale del cervello */
    P.forEach(function (p) { if ((p.rg === 'ol' && Math.abs(p.x - 200) > 158 && r() < 0.6) || (p.rg === 'cb' && p.y < 92 && r() < 0.5)) p.role = 0; });
    /* 3 vicini per punto, cercati nella griglia (raggio 3 celle) */
    var A = P.map(function () { return []; });
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
    /* readout: discendenti fra i punti a 2 salti, sotto il cervello e nel collo */
    for (i = 0; i < P.length; i++) if (hop[i] === 2 && P[i].role && (P[i].rg === 'nk' || (P[i].rg === 'cb' && P[i].y > 176 && Math.abs(P[i].x - 200) < 44)) && r() < 0.7) P[i].role = 2;
  }
  function build() {
    if (!P) gen();
    var w = fig.getBoundingClientRect().width; portrait = w < 1100; fig.classList.toggle('portrait', portrait);
    var sc = portrait ? 1 : 1.25, VW = portrait ? 440 : 1200, VH = portrait ? 880 : 808, ox = portrait ? 10 : 350, oy = portrait ? 206 : 18;
    svg.setAttribute('viewBox', '0 0 ' + VW + ' ' + VH); svg.setAttribute('preserveAspectRatio', portrait ? 'xMidYMid meet' : 'xMinYMid meet');
    var ng = [], g, i, s = '', X = function (x) { return f1(x * sc + ox); }, Y = function (y) { return f1(y * sc + oy); };
    for (g = 0; g < G; g++) ng.push('');
    for (i = 0; i < P.length; i++) {
      var p = P[i], hi = hop[i];
      ng[hi] += p.role === 2 ? '<rect class="d" x="' + f1(p.x * sc + ox - 2.6) + '" y="' + f1(p.y * sc + oy - 2.6) + '" width="5.2" height="5.2"/>'
        : '<circle class="' + (p.role ? 'c' : 's') + '" cx="' + X(p.x) + '" cy="' + Y(p.y) + '" r="' + (p.role ? (1.35 + sc * 0.45) * (1.12 - 0.05 * hi) : 2 + sc * 0.6).toFixed(2) + '"/>';
    }
    /* lesione = lobo ottico (ellisse della regione 'ol') intersecato con la sagoma: tratteggio solo sul confine vero */
    var od = 'M' + OUT.map(function (q) { return X(q[0]) + ' ' + Y(q[1]); }).join('L') + 'z', el = '';
    [55, 345].forEach(function (x) { el += '<ellipse cx="' + X(x) + '" cy="' + Y(127) + '" rx="' + f1(57 * sc) + '" ry="' + f1(101 * sc) + '"/>'; });
    s += '<clipPath id="cO"><path d="' + od + '"/></clipPath><clipPath id="cE">' + el + '</clipPath><path class="olc" d="' + od + '"/><g class="les" clip-path="url(#cO)">' + el + '</g><path class="les" clip-path="url(#cE)" d="' + od + '"/>';
    for (g = 0; g < G; g++) s += '<g class="hg h' + g + '">' + ng[g] + '</g>';
    /* legenda: fuori dall'anello dell'attention, sotto le note di destra (orizzontale) o a destra del cordone (verticale, titolo su due righe
       per restare a sinistra della scritta ruotata); numeri sotto i pallini */
    var lx = portrait ? 282 : 888, ly = portrait ? 620 : 560, st = portrait ? 20 : 28, l2 = portrait ? 16 : 0, lg = '<g class="lgd">' + (portrait ? T3(lx, ly, 16, L.hop2, ['t-m', 't-m']) : T(lx, ly, L.hop, 't-m'));
    for (g = 0; g < G; g++) lg += '<circle class="lg' + g + '" cx="' + (lx + 6 + g * st) + '" cy="' + (ly + l2 + 16) + '" r="' + (g ? 3.6 * (1.12 - 0.05 * g) : 4).toFixed(2) + '"/>' + T(lx + 6 + g * st, ly + l2 + 36, g > 4 ? '5+' : g, 't-m', 'middle');
    lg += '<circle class="s" cx="' + (lx + 6) + '" cy="' + (ly + l2 + 54) + '" r="3.4"/>' + T(lx + 16, ly + l2 + 58, L.pin, 't-m') + '<rect class="d lgd2" x="' + (lx + 3) + '" y="' + (ly + l2 + 69) + '" width="6" height="6"/>' + T(lx + 16, ly + l2 + 76, L.pout, 't-m') + '</g>';
    var an = '', ld = '', lp, ah;
    function lead(d) { ld += '<path class="ld" pathLength="1" stroke-dasharray="1 1" d="' + d + '"/>'; }
    if (!portrait) {
      an += T(330, 168, L.tok, 't-m', 'end') + T3(330, 192, 20, [L.in1, L.in2], ['', ''], 'end'); lead('M336 188H352L' + X(18) + ' ' + Y(126));
      an += T3(330, 380, 20, [L.les1, L.les2, L.les3], ['t-r', 't-r', 't-r'], 'end'); lead('M336 396H352L' + X(34) + ' ' + Y(214));
      an += T(880, 40, L.core, 't-i') + T3(880, 64, 20, [L.c2, L.c3], ['t-m', 't-m']); lead('M872 35.5H' + X(216) + 'V' + Y(110));
      an += '<circle class="ldo" cx="' + X(216) + '" cy="' + Y(110) + '" r="3"/>';
      an += T(880, 392, L.o1) + T(880, 412, L.o2) + T(880, 438, L.o3, 't-m'); lead('M874 404H852L' + X(214) + ' ' + Y(226));
      an += T(+X(166), +Y(234), L.two, 't-m two', 'end');
      lp = '<path class="loop" pathLength="1" stroke-dasharray="1 1" d="M868 452V728Q868 764 832 764H156Q120 764 120 728V224Q120 188 156 188H196"/>'; ah = 'M189 183.5L199 188L189 192.5z'; an += T(494, 794, L.att, 't-a', 'middle');
    } else {
      an += T(12, 104, L.tok, 't-m') + T(12, 126, L.in1 + ' ' + L.in2); lead('M40 134V' + Y(66));
      an += T3(428, 150, 19, [L.core, L.c2, L.c3], ['t-i', 't-m', 't-m'], 'end'); lead('M300 196L' + X(200) + ' ' + Y(110));
      an += '<circle class="ldo" cx="' + X(200) + '" cy="' + Y(110) + '" r="3"/>';
      an += T(12, 826, L.o1 + ' ' + L.o2) + T(12, 848, L.o3, 't-m'); lead('M24 806V448H' + X(186));
      an += T(+X(236), +Y(232), L.two, 't-m two');
      an += T3(428, 478, 18, [L.les1, L.les2, L.les3], ['t-r', 't-r', 't-r'], 'end'); lead('M404 462L' + X(350) + ' ' + Y(212));
      /* l'anello rientra sopra l'etichetta d'ingresso, dalle stesse porte */
      lp = '<path class="loop" pathLength="1" stroke-dasharray="1 1" d="M320 862Q436 862 436 760V96Q436 80 420 80H52Q40 80 40 84"/>'; ah = 'M35.5 83L40 91L44.5 83z'; an += T(0, 0, L.attS, 't-a', 'middle', ' transform="translate(428 660) rotate(-90)"');
    }
    /* punta di freccia separata dal tracciato: compare solo a curva completa (un marker-end sarebbe visibile da subito) */
    svg.innerHTML = s + '<g>' + ld + lp + '<path class="arw" opacity="0" d="' + ah + '"/></g>' + lg + '<g class="ann">' + an + '</g>';
    groups = $$('.hg', svg); leads = $$('.ld', svg); loop = $('.loop', svg); arw = $('.arw', svg); ann = $('.ann', svg);
    var pd = nf(Math.round(166700 / P.length), 0); $$('.pd').forEach(function (e) { e.textContent = pd; });
    lastP = -1;
  }
  function set(p) {
    if (!built || p === lastP) return; lastP = p;
    groups.forEach(function (g, k) { g.style.opacity = clamp(p * 7.2 - k, 0.06, 1); });
    var lp = clamp(p * 2.4 - 0.35, 0, 1); leads.forEach(function (l) { l.setAttribute('stroke-dashoffset', f1(1 - lp)); });
    ann.style.opacity = portrait ? 1 : clamp(p * 3 - 0.5, 0, 1);
    var q = clamp(p * 2 - 1, 0, 1); loop.setAttribute('stroke-dashoffset', (1 - q).toFixed(3)); loop.style.opacity = q ? 1 : 0;
    arw.setAttribute('opacity', q >= 0.97 ? '1' : '0');
  }
  var sc = scrubber(svg, function (r, vh) { return (vh * 0.95 - r.top) / (r.height * 0.75 + vh * 0.2); }, set);
  var lastW = 0;
  function go() { if (built) return; built = true; lastW = fig.getBoundingClientRect().width; build(); scrubNow(sc); }
  /* con movimento ridotto e in stampa la figura si genera subito: le catture a pagina intera e la carta non passano dall'observer */
  near(fig, go); addEventListener('beforeprint', go); if (rm) setTimeout(go, 0);
  new ResizeObserver(function () { var w = fig.getBoundingClientRect().width; if (built && (w < 1100) !== (lastW < 1100)) { build(); scrubNow(sc); } lastW = w; }).observe(fig);
})();

/* Fig. 3: linea del tempo dei kernel CUDA */
(function () {
  var svg = $('#kt'); if (!svg) return;
  var box = svg, rows = [], lastP = -1, W0 = 0;
  var pairs = [[27721, 1.40, 0.60], [27722, 1.07, 0.90]], n = 18;
  function kpath(x, y, ws, g) { var d = ''; for (var i = 0; i < n; i++) { x += g; d += 'M' + f1(x) + ' ' + y + 'h' + f1(ws[i]) + 'v16h' + f1(-ws[i]) + 'z'; x += ws[i]; } return [d, x]; }
  function build() {
    var w = wOf(box); if (!w) return; W0 = w;
    var narrow = w < 700, labW = narrow ? 0 : 204, ro = 58, x0 = labW, W = w - labW - ro, y = narrow ? 22 : 6, s = '', li = 0;
    rows = [];
    pairs.forEach(function (pr, pi) {
      var r = rng(pr[0]), k = pr[2], ws = [], sum = 0, i;
      for (i = 0; i < n; i++) { ws.push(0.6 + 1.4 * r()); sum += ws[i]; }
      ws = ws.map(function (x) { return x / sum * k * W; });
      var g0 = (1 - k) * W / n - 2, g1 = (W / pr[1] - k * W - 2) / n;
      for (var rr = 0; rr < 2; rr++) {
        if (narrow) s += T(x0, y - 9, L.k[li], 'fl'); else s += T(0, y + 12, L.k[li], 'fl');
        if (rr === 0) {
          var x = x0, d = '', tk = '';
          for (i = 0; i < n; i++) { tk += 'M' + f1(x) + ' ' + (y - 3) + 'h2v22h-2z'; x += 2 + g0; d += 'M' + f1(x) + ' ' + y + 'h' + f1(ws[i]) + 'v16h' + f1(-ws[i]) + 'z'; x += ws[i]; }
          s += '<path class="tk" d="' + tk + '"/><path class="kn" d="' + d + '"/>';
        } else {
          s += '<path class="tk" d="M' + f1(x0) + ' ' + (y - 3) + 'h2v22h-2z"/><path class="kn" data-r="' + rows.length + '"/>' + '<line class="endl" data-r="' + rows.length + '" y1="' + (y - 6) + '" y2="' + (y + 22) + '"/>' + T(w, y + 12, '', 'fv', '', ' data-r="' + rows.length + '"');
          rows.push({ x0: x0, y: y, ws: ws, g0: g0, g1: g1, R: pr[1] });
        }
        li++; y += narrow ? 48 : 30;
      }
      y += narrow ? 12 : 14;
    });
    y += 4;
    var ticks = narrow ? [0, 0.5, 1] : [0, 0.25, 0.5, 0.75, 1];
    s += ln(x0, y, x0 + W, y, 'ax');
    ticks.forEach(function (tv) { var x = x0 + tv * W; s += ln(x, y, x, y + 5, 'ax') + T(x, y + 18, tv === 0 || tv === 1 ? nf(tv, 0) : nf(tv, tv === 0.5 ? 1 : 2), 'fm', tv === 1 ? 'end' : tv === 0 ? 'start' : 'middle'); });
    s += T(x0, y + 38, L.kax, 'fl');
    var H = y + 46;
    vb(svg, w, H);
    svg.innerHTML = s;
    rows.forEach(function (rw, i) { rw.path = $('.kn[data-r="' + i + '"]', svg); rw.line = $('.endl[data-r="' + i + '"]', svg); rw.txt = $('text[data-r="' + i + '"]', svg); });
    lastP = -1;
  }
  function set(p) {
    if (!W0 || p === lastP) return; lastP = p;
    rows.forEach(function (rw) {
      var o = kpath(rw.x0 + 2, rw.y, rw.ws, lerp(rw.g0, rw.g1, p));
      /* la lettura segue la fine della riga */
      rw.path.setAttribute('d', o[0]); rw.line.setAttribute('x1', f1(o[1])); rw.line.setAttribute('x2', f1(o[1])); rw.txt.setAttribute('x', f1(o[1] + 8));
      /* solo i due valori misurati: 1,00x fino a meta' corsa, poi il rapporto finale */
      rw.txt.textContent = nf(p < 0.5 ? 1 : 1 / rw.R, 2) + '×';
    });
  }
  var sc = scrubber(svg, function (r, vh) { return sst((vh * 0.9 - r.top) / (vh * 0.5)); }, set);
  live(box, build, sc);
})();

/* Fig. 4: asse logaritmico dell'errore
   L'asse e' 1 - coseno; ogni punto porta il suo valore di 1 - coseno e, accanto, il coseno misurato. */
(function () {
  var svg = $('#err'); if (!svg) return;
  var box = svg, W0 = 0, lastP = -1, X, ya, pt, lk, fl, arc, ah, rt;
  function build() {
    var w = wOf(box); if (!w) return; W0 = w;
    var narrow = w < 600, x0 = narrow ? 8 : 12, x1 = w - (narrow ? 22 : 40), s = '';
    ya = 126; var H = ya + (narrow ? 58 : 46);
    X = function (l) { return x0 + (-l) / 5 * (x1 - x0); };
    s += ln(x0, ya, x1, ya, 'ax');
    for (var d = 0; d <= 5; d++) {
      var x = X(-d); s += ln(x, ya, x, ya + 6, 'ax');
      s += d === 0 ? T(x, ya + 22, '1', 'fm', 'start') : '<text x="' + f1(x) + '" y="' + (ya + 22) + '" class="fm" text-anchor="middle">10<tspan dy="-5" class="ex">−' + d + '</tspan></text>';
    }
    var xf = X(-4.36), xp = X(-0.62), mx = (xp + xf) / 2;
    s += ln(xf, ya - 10, xf, ya + 10, 'tgt');
    s += T(x0, ya + (narrow ? 44 : 40), L.cosax, 'fl', 'start');
    /* etichette a due righe: nome e coseno, poi 1 - coseno (la grandezza dell'asse) */
    s += T(xp - 4, ya - 58, L.pad, 'fl', 'start') + T(xp - 4, ya - 42, L.padv, 'fm', 'start');
    s += '<g class="fixl" opacity="0">' + T(xf + 4, ya - 30, L.fix, 'fl', 'end', ' id="err-v"') + '<text x="' + f1(xf + 4) + '" y="' + (ya - 14) + '" class="fm" text-anchor="end">' + L.fixv + '<tspan dy="-5" class="ex">−5</tspan></text></g>';
    /* arco del miglioramento: da sopra l'etichetta del padding alla punta sopra il fix */
    var ex = xf - 2, ey = ya - 46, cy = ya - 128, ang = Math.atan2(ey - cy, ex - mx), c = Math.cos(ang), n = Math.sin(ang);
    s += '<path class="arc" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" d="M' + f1(xp + 2) + ' ' + (ya - 76) + 'Q' + f1(mx) + ' ' + cy + ' ' + f1(ex) + ' ' + ey + '"/>';
    s += '<path class="arh" opacity="0" d="M' + f1(ex + c * 3) + ' ' + f1(ey + n * 3) + 'L' + f1(ex - c * 7 - n * 4.5) + ' ' + f1(ey - n * 7 + c * 4.5) + 'L' + f1(ex - c * 7 + n * 4.5) + ' ' + f1(ey - n * 7 - c * 4.5) + 'z"/>';
    s += T(mx, ya - 106, L.ratio, 'fl2 rt', 'middle', ' opacity="0"');
    s += '<line class="lk" x1="' + f1(xp) + '" y1="' + ya + '" x2="' + f1(xp) + '" y2="' + ya + '"/>';
    s += '<circle class="p0" cx="' + f1(xp) + '" cy="' + ya + '" r="4.5"/><circle class="p1" cx="' + f1(xp) + '" cy="' + ya + '" r="5"/>';
    vb(svg, w, H);
    svg.innerHTML = s; pt = $('.p1', svg); lk = $('.lk', svg); fl = $('.fixl', svg); arc = $('.arc', svg); ah = $('.arh', svg); rt = $('.rt', svg); lastP = -1;
  }
  function set(p) {
    if (!W0 || p === lastP) return; lastP = p;
    /* si muove solo il punto; le etichette mostrano solo i valori misurati */
    var x = X(lerp(-0.62, -4.36, p)), done = p >= 0.9 ? '1' : '0';
    pt.setAttribute('cx', f1(x)); lk.setAttribute('x2', f1(x));
    arc.setAttribute('stroke-dashoffset', (1 - clamp((p - 0.3) / 0.6, 0, 1)).toFixed(3));
    fl.setAttribute('opacity', done); ah.setAttribute('opacity', done); rt.setAttribute('opacity', done);
  }
  var sc = scrubber(svg, function (r, vh) { return (vh * 0.85 - r.top) / (vh * 0.5); }, set);
  live(box, build, sc);
})();

/* Fig. 5: il recinto di Vergilius */
(function () {
  var svg = $('#fence'); if (!svg) return;
  var box = svg, W0 = 0, lastP = -1, path, cells = [], stamped = rm, closed = false;
  var A = { cols: 7, n: 35, red: [9, 20, 31] }, B = { cols: 6, n: 36, red: [22] };
  var pt = 21, cz = 17;
  function waffle(x, y, cfg, out) {
    var s = '';
    for (var i = 0; i < cfg.n; i++) {
      var red = cfg.red.indexOf(i) >= 0;
      s += cell(x + (i % cfg.cols) * pt, y + Math.floor(i / cfg.cols) * pt, cz, red, stamped ? ' in' : '');
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
    /* freccia disegnata, non glifo: tratto lungo gap - 16 a meta' altezza dei blocchi */
    var ay = f1(wy + (6 * pt - pt + cz) / 2), ax = rx0 + wA + 8;
    s += '<path class="arr" d="M' + f1(ax) + ' ' + ay + 'h' + (gap - 16) + 'm-5 -3.5l5 3.5l-5 3.5"/>';
    s += waffle(bx, wy, B, reds);
    s += T(rx0, wy + 6 * pt + 20, '3/35', 'fv') + T(bx, wy + 6 * pt + 20, '1/36', 'fv');
    H = wy + 6 * pt + 38;
    if (!st) H = Math.max(H, ry + 44);
    s += '<rect class="lbx" x="12" y="' + (top - 9) + '" width="10" height="18"/>' + T(20, top + 4.5, L.fence, 'fl lbt');
    vb(svg, w, H);
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
    if (!W0 || p === lastP) return; lastP = p;
    var f = lerp(40 / 360, 1, sst(p / 0.6));
    path.setAttribute('stroke-dasharray', f.toFixed(4) + ' 1');
    if (f >= 1 && !closed) { closed = true; svg.classList.add('chiuso'); }
  }
  function stamp() { if (stamped) return; stamped = true; cells.forEach(function (c, i) { c.style.transitionDelay = rm ? '0ms' : (i * 10) + 'ms'; c.classList.add('in'); }); }
  var sc = scrubber(svg, function (r, vh) { return (vh * 0.9 - r.top) / (vh * 0.6); }, set);
  new IntersectionObserver(function (es, o) { if (es[0].isIntersecting) { stamp(); o.disconnect(); } }, { threshold: 0.4 }).observe(svg);
  /* un solo build, dopo il caricamento dei font (la larghezza dell'etichetta del recinto dipende dal font) */
  var ready = !(D.fonts && D.fonts.ready), go = live(box, build, sc, function () { return ready; });
  if (!ready) D.fonts.ready.then(function () { ready = true; go(); });
  RMq.addEventListener('change', function () { if (rm) { stamp(); closed = true; svg.classList.add('chiuso'); } });
})();

/* Fig. 6: FantaOracle, tetto d'asta contro prezzo pagato
   Dati del replay pubblico (fantaoracle, reports/asta_20260913/VERIFICA.md par. 3): 28 attaccanti battuti a 40+ crediti.
   TET = tetto proposto dal bot, PAG = prezzo di aggiudicazione, SP = massimo spendibile in quel momento.
   Il tetto non supera mai SP per costruzione (min nella formula); il dato e' quante volte arriva al prezzo: 8 su 28.
   Sotto: 44 assegnazioni del ponte, 1 diversa. */
(function () {
  var svg = $('#lots'); if (!svg) return;
  var TET = [289, 74, 300, 55, 36, 48, 201, 251, 219, 90, 71, 101, 60, 22, 62, 49, 25, 40, 46, 21, 57, 1, 1, 1, 1, 1, 1, 1],
    PAG = [275, 60, 255, 41, 137, 52, 205, 80, 200, 146, 80, 140, 50, 90, 46, 74, 61, 66, 60, 42, 63, 127, 41, 40, 47, 61, 56, 47], SP = [], i;
  [[311, 9], [112, 4], [63, 8], [1, 7]].forEach(function (r) { for (i = 0; i < r[1]; i++) SP.push(r[0]); });
  var box = svg, W0 = 0, lastP = -1, lots = [], line, cells = [], yb, Yv;
  function build() {
    var w = wOf(box); if (!w) return; W0 = w;
    var narrow = w < 600, x0 = 40, x1 = w - 4, top = 44, ch = narrow ? 150 : 190, s = '', n = TET.length, dx = (x1 - x0) / n, bw = Math.max(3, Math.min(9, dx * 0.42)), hw = bw / 2 + 3;
    yb = top + ch; Yv = function (v) { return yb - v / 320 * ch; };
    s += T(0, 16, L.cr, 'fl');
    [0, 100, 200, 300].forEach(function (v) { s += ln(x0 - 4, Yv(v), x0, Yv(v), 'ax') + T(x0 - 8, Yv(v) + 4, nf(v, 0), 'fm', 'end'); });
    s += ln(x0, yb, x1, yb, 'ax');
    var d = 'M' + f1(x0) + ' ' + f1(Yv(SP[0]));
    for (i = 0; i < n; i++) { d += 'H' + f1(x0 + (i + 1) * dx); if (i < n - 1 && SP[i + 1] !== SP[i]) d += 'V' + f1(Yv(SP[i + 1])); }
    s += '<path class="spl" pathLength="1" stroke-dasharray="1 1" d="' + d + '"/>';
    s += T(x0 + 2, Yv(311) - 9, L.sp, 'fl');
    for (i = 0; i < n; i++) {
      var cx = x0 + (i + 0.5) * dx;
      s += '<rect class="tt" x="' + f1(cx - bw / 2) + '" y="' + f1(yb) + '" width="' + f1(bw) + '" height="0"/><line class="pp" opacity="0" x1="' + f1(cx - hw) + '" x2="' + f1(cx + hw) + '" y1="' + f1(Yv(PAG[i])) + '" y2="' + f1(Yv(PAG[i])) + '"/>' + (TET[i] > 1 ? '' : '<circle class="b1" opacity="0" cx="' + f1(cx) + '" cy="' + f1(yb - 3) + '" r="2.2"/>');
    }
    /* legenda accanto ai dati, nel vuoto sopra i lotti 13-28 (prezzi e tetti sotto 150) */
    var lx = x0 + 12 * dx + 10, ly = top + 12, tx = lx + bw + 10;
    s += '<rect class="tt0" x="' + f1(lx + 3) + '" y="' + (ly - 10) + '" width="' + f1(bw) + '" height="11"/>' + T(tx, ly, L.tet, 'fl');
    s += ln(lx + 3 + bw / 2 - hw, ly + 16, lx + 3 + bw / 2 + hw, ly + 16, 'pp') + T(tx, ly + 20, L.pag, 'fl');
    s += T(lx, ly + 46, '8/28', 'fv') + T(lx + 44, ly + 46, L.hit, 'fl');
    s += T(x0, yb + 20, L.lots, 'fl');
    /* ponte: 44 celle in riga (due righe se stretto), prima le identiche */
    var cz = narrow ? 11 : 13, pt = cz + (narrow ? 3 : 4), per = Math.min(44, Math.floor((x1 - x0 + (pt - cz)) / pt)), cy = yb + 62, cx0 = x0;
    s += T(x0, yb + 50, L.bridge, 'fl');
    for (i = 0; i < 44; i++) s += cell(cx0 + (i % per) * pt, cy + Math.floor(i / per) * pt, cz, i === 43);
    var rows = Math.ceil(44 / per), H = cy + rows * pt + 22;
    s += T(x0, cy + rows * pt + 16, '43/44', 'fv');
    vb(svg, w, H);
    svg.innerHTML = s; line = $('.spl', svg); cells = $$('.cell', svg); lastP = -1;
    lots = $$('.tt', svg).map(function (b) { var t = b.nextSibling; return { b: b, t: t, d: t.nextSibling && t.nextSibling.tagName === 'circle' ? t.nextSibling : null }; });
  }
  function set(p) {
    if (!W0 || p === lastP) return; lastP = p;
    /* prima si traccia il massimo spendibile, poi per ogni lotto sale il tetto e, a barra completa, compare il prezzo */
    line.setAttribute('stroke-dashoffset', (1 - clamp(p / 0.35, 0, 1)).toFixed(3));
    lots.forEach(function (o, k) {
      var q = sst((p - 0.25 - k * 0.012) / 0.3), h = Math.max(1.5, yb - Yv(TET[k])) * q;
      o.b.setAttribute('y', f1(yb - h)); o.b.setAttribute('height', f1(h));
      o.t.setAttribute('opacity', q >= 1 ? '1' : '0'); if (o.d) o.d.setAttribute('opacity', q > 0 ? '1' : '0');
    });
    cells.forEach(function (c, k) { c.setAttribute('opacity', p >= 0.62 + k * 0.008 ? '1' : '0'); });
  }
  var sc = scrubber(svg, function (r, vh) { return (vh * 0.9 - r.top) / (vh * 0.6); }, set);
  live(box, build, sc);
})();

/* note a margine: evidenziatore quando il testo entra */
var noteIO = new IntersectionObserver(function (es) {
  es.forEach(function (e) {
    if (!e.isIntersecting) return;
    e.target.classList.add('on');
    (e.target.getAttribute('data-notes') || '').split(' ').forEach(function (id) { var n = id && D.getElementById(id); if (n) n.classList.add('on'); });
    noteIO.unobserve(e.target);
  });
}, { rootMargin: '0px 0px -35% 0px' });
$$('[data-notes]').forEach(function (e) { if (rm) { e.classList.add('on'); e.getAttribute('data-notes').split(' ').forEach(function (id) { var n = D.getElementById(id); if (n) n.classList.add('on'); }); } else noteIO.observe(e); });

/* scroll */
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

/* testata: barra fissa dopo l'hero, testatina corrente */
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

/* indice a comparsa (details) */
$$('details.toc').forEach(function (d) {
  $$('a', d).forEach(function (a) { a.addEventListener('click', function () { d.open = false; }); });
});
D.addEventListener('keydown', function (e) { if (e.key === 'Escape') $$('details.toc[open]').forEach(function (d) { d.open = false; $('summary', d).focus(); }); });
D.addEventListener('click', function (e) { $$('details.toc[open]').forEach(function (d) { if (!d.contains(e.target)) d.open = false; }); });

/* tema */
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

/* lingua: conserva l'ancora */
$$('.lang a').forEach(function (a) { a.addEventListener('click', function () { if (location.hash) a.href = a.getAttribute('href').split('#')[0] + location.hash; }); });

/* mostra la griglia */
var gb = $('#gridbtn');
if (gb) gb.addEventListener('click', function () { var on = root.classList.toggle('show-grid'); gb.setAttribute('aria-pressed', String(on)); gb.textContent = L.grid[on ? 1 : 0]; });

if (D.fonts && D.fonts.ready) D.fonts.ready.then(function () { Ras.redraw(); });
dirty = 1; need();
})();
