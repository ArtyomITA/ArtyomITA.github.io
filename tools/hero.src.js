/* Scena della pagina: un mondo di cubi teal che, mentre si scorre, si ricompone in una forma per ogni progetto.
   Tappe ([data-stage]): 0 parete (hero), 1 globo (Vergilius), 2 torri di agenti (chatroom), 3 die della GPU (kernel), 4 onda sonora (Quest 3S).
   Sorgente di js/hero.js (three.js incluso): python tools/build-hero.py. Seme fisso 424. Stesso contratto della scena di prima:
   host.gl al primo fotogramma, canvas.dataset.run 1/0, pausa fuori vista e con la scheda nascosta. */
import {
  Scene, PerspectiveCamera, WebGLRenderer, BoxGeometry, MeshStandardMaterial, InstancedMesh, Object3D, Color, Fog,
  DirectionalLight, AmbientLight, BufferGeometry, Float32BufferAttribute, LineSegments, LineBasicMaterial,
  Vector3, InstancedBufferAttribute, DynamicDrawUsage, SRGBColorSpace,
} from 'three';

const N = 1600;
const TEAL = new Color('#1f8f78'), TEAL_HI = new Color('#4fd6b9'), AMBER = new Color('#f2c14e'), DEEP = new Color('#0f4a3f');

function rng(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const R = rng(424);
const delay = Float32Array.from({ length: N }, () => R());

function wall() {
  const p = new Float32Array(N * 3), s = new Float32Array(N); const C = 50, Rr = 32;
  for (let i = 0; i < N; i++) { const c = i % C, r = Math.floor(i / C); p[i * 3] = (c - C / 2) * 1.08; p[i * 3 + 2] = (r - Rr / 2) * 1.08; s[i] = 1; }
  return { p, s };
}
function globe() {
  const p = new Float32Array(N * 3), s = new Float32Array(N); const g = Math.PI * (3 - Math.sqrt(5)), rad = 11;
  for (let i = 0; i < N; i++) {
    const y = 1 - (i / (N - 1)) * 2, r = Math.sqrt(1 - y * y), th = g * i;
    p[i * 3] = Math.cos(th) * r * rad; p[i * 3 + 1] = y * rad + 6; p[i * 3 + 2] = Math.sin(th) * r * rad; s[i] = 0.5;
  }
  return { p, s };
}
const TOWERS = [[-13, -6], [13, -6], [-13, 9], [13, 9]];
function agents() {
  const p = new Float32Array(N * 3), s = new Float32Array(N); const per = 300;
  for (let i = 0; i < N; i++) {
    const k = Math.floor(i / per);
    if (k < 4) {
      const j = i % per, layer = Math.floor(j / 25), q = j % 25, x = q % 5, z = Math.floor(q / 5);
      p[i * 3] = TOWERS[k][0] + (x - 2) * 1.1; p[i * 3 + 1] = layer * 1.1; p[i * 3 + 2] = TOWERS[k][1] + (z - 2) * 1.1; s[i] = 1;
    } else {
      const j = i - 4 * per, a = j * 0.39, r = 1.2 + 0.07 * j;
      p[i * 3] = Math.cos(a) * r * 0.55; p[i * 3 + 2] = Math.sin(a) * r * 0.55 + 1.5; s[i] = r < 8 ? 0.7 : 0;
    }
  }
  return { p, s };
}
const WC = 64;
function wave() {
  const p = new Float32Array(N * 3), s = new Float32Array(N);
  for (let i = 0; i < N; i++) { const c = i % WC, r = Math.floor(i / WC); p[i * 3] = (c - WC / 2) * 0.9; p[i * 3 + 1] = r * 0.9; s[i] = 0.78; }
  return { p, s };
}
function die() {
  const p = new Float32Array(N * 3), s = new Float32Array(N); const C = 40;
  for (let i = 0; i < N; i++) {
    const c = i % C, r = Math.floor(i / C), gx = Math.floor(c / 5), gz = Math.floor(r / 5);
    p[i * 3] = (c - C / 2) * 0.95 + gx * 0.7 - 2.6; p[i * 3 + 2] = (r - C / 2) * 0.95 + gz * 0.7 - 2.6; s[i] = 0.9;
  }
  return { p, s };
}
const L = [wall(), globe(), agents(), die(), wave()];
// telecamera per tappa (posizione, punto guardato); su schermi stretti la scena si centra e si allontana
const CAM = [
  [[4, 24, 34], [-4, -3, 2]], [[-8, 13, 44], [-10, 5, 0]], [[-16, 26, 34], [-4, 4, 1]], [[-12, 34, 30], [-6, 0, 0]], [[-14, 18, 40], [-8, 10, 0]],
].map(([a, b]) => [new Vector3(...a), new Vector3(...b)]);

export function start(canvas, host) {
  const stages = [...document.querySelectorAll('[data-stage]')];
  const story = host.closest('.story') || host;
  const renderer = new WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
  let pr = Math.min(devicePixelRatio, 1.75);
  renderer.setPixelRatio(pr);
  renderer.outputColorSpace = SRGBColorSpace;
  const scene = new Scene();
  scene.fog = new Fog('#0a1514', 34, 92);
  const cam = new PerspectiveCamera(42, 1, 0.1, 200);
  scene.add(new AmbientLight('#6fd9c4', 0.55));
  const key = new DirectionalLight('#e8fff8', 1.6); key.position.set(18, 40, 22); scene.add(key);
  const rim = new DirectionalLight('#f2c14e', 0.55); rim.position.set(-30, 10, -20); scene.add(rim);

  const mesh = new InstancedMesh(new BoxGeometry(0.86, 0.86, 0.86), new MeshStandardMaterial({ roughness: 0.42, metalness: 0.18 }), N);
  mesh.instanceMatrix.setUsage(DynamicDrawUsage);
  mesh.instanceColor = new InstancedBufferAttribute(new Float32Array(N * 3), 3).setUsage(DynamicDrawUsage);
  scene.add(mesh);
  const lp = [];
  for (let a = 0; a < 4; a++) for (let b = a + 1; b < 4; b++) lp.push(TOWERS[a][0], 8.4, TOWERS[a][1], TOWERS[b][0], 8.4, TOWERS[b][1]);
  const lg = new BufferGeometry(); lg.setAttribute('position', new Float32BufferAttribute(lp, 3));
  const lmat = new LineBasicMaterial({ color: '#f2c14e', transparent: true, opacity: 0 });
  scene.add(new LineSegments(lg, lmat));

  // scroll -> tappa con soste: la forma resta mentre si legge il pannello, poi si trasforma
  let progress = 0, past = 0;
  function measure() {
    const y = scrollY + innerHeight * 0.5;
    const tops = stages.map((s) => s.offsetTop + s.offsetHeight * 0.5);
    const last = stages[stages.length - 1];
    past = Math.min(1, Math.max(0, (scrollY + innerHeight * 0.35 - (last.offsetTop + last.offsetHeight)) / (innerHeight * 0.5)));
    if (y <= tops[0]) { progress = 0; return; }
    for (let i = 0; i < tops.length - 1; i++) {
      if (y < tops[i + 1]) { const f = (y - tops[i]) / (tops[i + 1] - tops[i]); progress = i + Math.min(1, Math.max(0, (f - 0.2) / 0.6)); return; }
    }
    progress = tops.length - 1;
  }
  addEventListener('scroll', measure, { passive: true }); measure();

  const d = new Object3D(), col = new Color(), camPos = new Vector3(), camAt = new Vector3();
  let mx = 0, my = 0, tx = 0, ty = 0, narrow = false;
  addEventListener('pointermove', (e) => { tx = e.clientX / innerWidth - 0.5; ty = e.clientY / innerHeight - 0.5; }, { passive: true });
  function size() {
    const w = canvas.clientWidth, h = canvas.clientHeight;
    renderer.setSize(w, h, false); cam.aspect = w / h; narrow = w < 900; cam.fov = narrow ? 58 : 42; cam.updateProjectionMatrix(); measure();
  }
  addEventListener('resize', size); size();

  const ease = (t) => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  const clamp = (v) => v < 0 ? 0 : v > 1 ? 1 : v;
  let t0 = 0, last = 0, raf = 0, running = false, fr = 0, acc = 0, slow = 0;

  function frame(now) {
    const time = (now - t0) / 1000;
    const p = Math.min(Math.max(progress, 0), L.length - 1);
    const si = Math.min(Math.floor(p), L.length - 2), f = p - si, A = L[si], B = L[si + 1], lit = Math.round(p);
    mx += (tx - mx) * 0.05; my += (ty - my) * 0.05;
    const gw = Math.max(0, 1 - Math.abs(p - 1) * 1.4);
    for (let i = 0; i < N; i++) {
      const k = clamp(f * 1.5 - delay[i] * 0.5), e = ease(k);
      let x = A.p[i * 3] + (B.p[i * 3] - A.p[i * 3]) * e, y = A.p[i * 3 + 1] + (B.p[i * 3 + 1] - A.p[i * 3 + 1]) * e, z = A.p[i * 3 + 2] + (B.p[i * 3 + 2] - A.p[i * 3 + 2]) * e;
      let sc = A.s[i] + (B.s[i] - A.s[i]) * e;
      const mid = Math.sin(k * Math.PI);
      y += mid * (3 + delay[i] * 6);
      let heat = 0;
      if (lit === 0) {  // un'onda ambra attraversa la parete in diagonale
        const c = i % 50, r = Math.floor(i / 50), ph = ((c + r) * 0.16 - time * 2.2) % 9;
        const wv = ph > -1.2 && ph < 0 ? Math.sin((ph + 1.2) / 1.2 * Math.PI) : 0;
        y += wv * 1.4 * (1 - e); heat = wv;
      } else if (lit === 1) {  // punti del globo che si accendono a turno, come un radar
        heat = i % 41 === 0 ? Math.max(0, Math.sin(time * 1.4 + i * 0.37)) : 0;
      } else if (lit === 4) {  // colonne che si muovono come un parlato
        const c = i % WC, r = Math.floor(i / WC), amp = 0.5 + 0.5 * Math.sin(c * 0.33 + time * 3.1) * Math.sin(c * 0.09 - time * 1.3);
        const on = r < amp * 25; sc *= on ? 1 : 0.0001; heat = on && r > amp * 25 - 2 ? 1 : 0;
      } else if (lit === 3) {  // blocchi del die che si accendono come multiprocessori
        const c = i % 40, r = Math.floor(i / 40), b = Math.floor(c / 5) + Math.floor(r / 5) * 8;
        heat = Math.sin(time * 2 + b * 1.7) > 0.92 ? 1 : 0;
      }
      if (gw > 0) { const an = time * 0.22 * gw, ox = x, oz = z; x = ox * Math.cos(an) - oz * Math.sin(an); z = ox * Math.sin(an) + oz * Math.cos(an); }
      d.position.set(x, y, z); d.rotation.set(mid * delay[i] * 3, mid * 2.2, 0); d.scale.setScalar(Math.max(sc, 0.0001));
      d.updateMatrix(); mesh.setMatrixAt(i, d.matrix);
      col.copy(TEAL).lerp(TEAL_HI, 0.25 + 0.25 * Math.sin(i * 0.7 + time * 0.6)).lerp(DEEP, delay[i] * 0.35);
      if (heat > 0) col.lerp(AMBER, Math.min(1, heat));
      mesh.setColorAt(i, col);
    }
    mesh.instanceMatrix.needsUpdate = true; mesh.instanceColor.needsUpdate = true;
    const ce = ease(clamp(f));
    camPos.lerpVectors(CAM[si][0], CAM[si + 1][0], ce); camAt.lerpVectors(CAM[si][1], CAM[si + 1][1], ce);
    if (narrow) { camAt.x += 8; camPos.x += 4; camPos.y += 6; camPos.z += 12; }
    cam.position.set(camPos.x + mx * 4, camPos.y - my * 3, camPos.z); cam.lookAt(camAt);
    lmat.opacity = Math.max(0, 1 - Math.abs(p - 2) * 1.6) * (0.55 + 0.45 * Math.sin(time * 4));
    canvas.style.opacity = String(1 - past);
    renderer.render(scene, cam);
    if (!fr++) host.classList.add('gl');
    // se i primi fotogrammi sono lenti si abbassa la risoluzione
    if (last && fr > 8 && fr < 200 && !slow) { acc += now - last; if (fr % 60 === 0) { if (acc / 60 > 30) { slow = 1; pr = 1; renderer.setPixelRatio(1); size(); } acc = 0; } }
    last = now; canvas.dataset.run = '1';
    raf = requestAnimationFrame(frame);
  }
  function go(on) {
    if (on === running) return; running = on; canvas.dataset.run = on ? '1' : '0';
    if (on) { t0 = t0 ? performance.now() - (last - t0) : performance.now(); last = 0; if (!raf) raf = requestAnimationFrame(frame); } else if (raf) { cancelAnimationFrame(raf); raf = 0; }
  }
  let vis = true;
  const upd = () => go(vis && document.visibilityState === 'visible');
  new IntersectionObserver((es) => { vis = es[0].isIntersecting; upd(); }).observe(story);
  document.addEventListener('visibilitychange', upd);
  canvas.addEventListener('webglcontextlost', (e) => { e.preventDefault(); go(false); host.classList.remove('gl'); });
  upd();
}
