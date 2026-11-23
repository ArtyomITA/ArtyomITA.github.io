// One world of teal cubes that rebuilds itself into a shape for each project while you scroll.
// Stages: 0 wall (hero), 1 globe (Vergilius), 2 agents (chatroom), 3 waveform (Quest 3S), 4 GPU die (Blackwell + 1080).
import {
  Scene, PerspectiveCamera, WebGLRenderer, BoxGeometry, MeshStandardMaterial, InstancedMesh, Object3D, Color, Fog,
  DirectionalLight, AmbientLight, PointLight, BufferGeometry, Float32BufferAttribute, LineSegments, LineBasicMaterial,
  Vector3, InstancedBufferAttribute, DynamicDrawUsage, SRGBColorSpace,
} from '../../../artyomita-redesign/vendor-src/three.module.js';

const N = 1600;
const TEAL = new Color('#1f8f78'), TEAL_HI = new Color('#4fd6b9'), AMBER = new Color('#f2c14e'), DEEP = new Color('#0f4a3f');

function rng(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const R = rng(424);
const delay = Float32Array.from({ length: N }, () => R());

// ---- layouts: N target positions (x, y, z) and a scale per stage
function wall() {
  const p = new Float32Array(N * 3), s = new Float32Array(N); const C = 50, Rr = 32;
  for (let i = 0; i < N; i++) {
    const c = i % C, r = Math.floor(i / C);
    p[i * 3] = (c - C / 2) * 1.08; p[i * 3 + 1] = 0; p[i * 3 + 2] = (r - Rr / 2) * 1.08; s[i] = r < Rr ? 1 : 0;
  }
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
    } else {  // the room: a flat disc in the middle
      const j = i - 4 * per, a = j * 0.39, r = 1.2 + 0.07 * j;
      p[i * 3] = Math.cos(a) * r * 0.55; p[i * 3 + 1] = 0; p[i * 3 + 2] = Math.sin(a) * r * 0.55 + 1.5; s[i] = r < 8 ? 0.7 : 0;
    }
  }
  return { p, s };
}
const WC = 64;
function wave() {
  const p = new Float32Array(N * 3), s = new Float32Array(N);
  for (let i = 0; i < N; i++) {
    const c = i % WC, r = Math.floor(i / WC);
    p[i * 3] = (c - WC / 2) * 0.9; p[i * 3 + 1] = r * 0.9; p[i * 3 + 2] = 0; s[i] = 0.78;
  }
  return { p, s };
}
function die() {
  const p = new Float32Array(N * 3), s = new Float32Array(N); const C = 40;
  for (let i = 0; i < N; i++) {
    const c = i % C, r = Math.floor(i / C);
    const gx = Math.floor(c / 5), gz = Math.floor(r / 5);  // 8 x 8 blocks of 5 x 5 cubes, a gap between blocks
    p[i * 3] = (c - C / 2) * 0.95 + gx * 0.7 - 2.6; p[i * 3 + 1] = 0; p[i * 3 + 2] = (r - C / 2) * 0.95 + gz * 0.7 - 2.6; s[i] = 0.9;
  }
  return { p, s };
}
const L = [wall(), globe(), agents(), wave(), die()];

// camera per stage: position and look-at
const CAM = [
  [new Vector3(4, 24, 34), new Vector3(-4, -3, 2)],
  [new Vector3(-8, 13, 44), new Vector3(-10, 5, 0)],
  [new Vector3(-16, 26, 34), new Vector3(-4, 4, 1)],
  [new Vector3(-14, 18, 40), new Vector3(-8, 10, 0)],
  [new Vector3(-12, 34, 30), new Vector3(-6, 0, 0)],
];

export function start(canvas, getProgress, reduced) {
  const renderer = new WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.75));
  renderer.outputColorSpace = SRGBColorSpace;
  const scene = new Scene();
  scene.fog = new Fog('#0a1514', 34, 92);
  const cam = new PerspectiveCamera(42, 1, 0.1, 200);
  scene.add(new AmbientLight('#6fd9c4', 0.55));
  const key = new DirectionalLight('#e8fff8', 1.6); key.position.set(18, 40, 22); scene.add(key);
  const rim = new DirectionalLight('#f2c14e', 0.55); rim.position.set(-30, 10, -20); scene.add(rim);
  const glow = new PointLight('#f2c14e', 0, 40); scene.add(glow);

  const geo = new BoxGeometry(0.86, 0.86, 0.86);
  const mat = new MeshStandardMaterial({ roughness: 0.42, metalness: 0.18, vertexColors: false });
  const mesh = new InstancedMesh(geo, mat, N);
  mesh.instanceMatrix.setUsage(DynamicDrawUsage);
  mesh.instanceColor = new InstancedBufferAttribute(new Float32Array(N * 3), 3).setUsage(DynamicDrawUsage);
  scene.add(mesh);

  // links between the agent towers (chatroom)
  const lg = new BufferGeometry();
  const lp = []; const top = 8.4;
  for (let a = 0; a < 4; a++) for (let b = a + 1; b < 4; b++) lp.push(TOWERS[a][0], top, TOWERS[a][1], TOWERS[b][0], top, TOWERS[b][1]);
  lg.setAttribute('position', new Float32BufferAttribute(lp, 3));
  const lmat = new LineBasicMaterial({ color: '#f2c14e', transparent: true, opacity: 0 });
  scene.add(new LineSegments(lg, lmat));

  const d = new Object3D(), col = new Color(), camPos = new Vector3(), camAt = new Vector3(), at = new Vector3();
  let mx = 0, my = 0, tx = 0, ty = 0, w = 0, h = 0, running = true;
  addEventListener('pointermove', (e) => { tx = e.clientX / innerWidth - 0.5; ty = e.clientY / innerHeight - 0.5; }, { passive: true });
  function resize() {
    w = canvas.clientWidth; h = canvas.clientHeight;
    renderer.setSize(w, h, false); cam.aspect = w / h; cam.updateProjectionMatrix();
  }
  addEventListener('resize', resize); resize();
  document.addEventListener('visibilitychange', () => { running = !document.hidden; if (running) requestAnimationFrame(frame); });

  const ease = (t) => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  const clamp = (v) => v < 0 ? 0 : v > 1 ? 1 : v;
  const t0 = performance.now();

  function frame(now) {
    if (!running) return;
    const time = reduced ? 0 : (now - t0) / 1000;
    const pr = Math.min(Math.max(getProgress(), 0), L.length - 1);
    const si = Math.min(Math.floor(pr), L.length - 2), f = pr - si;
    const A = L[si], B = L[si + 1];
    mx += (tx - mx) * 0.05; my += (ty - my) * 0.05;
    const lit = Math.round(pr);  // the stage the camera is closest to decides the accents
    for (let i = 0; i < N; i++) {
      const k = clamp((f * 1.5) - delay[i] * 0.5), e = ease(k);
      let x = A.p[i * 3] + (B.p[i * 3] - A.p[i * 3]) * e;
      let y = A.p[i * 3 + 1] + (B.p[i * 3 + 1] - A.p[i * 3 + 1]) * e;
      let z = A.p[i * 3 + 2] + (B.p[i * 3 + 2] - A.p[i * 3 + 2]) * e;
      let sc = A.s[i] + (B.s[i] - A.s[i]) * e;
      const mid = Math.sin(k * Math.PI);  // cubes lift and turn while they travel
      y += mid * (3 + delay[i] * 6);
      let heat = 0;
      if (lit === 0) {  // hero: an amber wave runs diagonally across the wall
        const c = i % 50, r = Math.floor(i / 50), ph = ((c + r) * 0.16 - time * 2.2) % 9;
        const wv = ph > -1.2 && ph < 0 ? Math.sin((ph + 1.2) / 1.2 * Math.PI) : 0;
        y += wv * 1.4 * (1 - e); heat = wv;
      } else if (lit === 1) {  // globe: a few points light up in turn like a radar
        heat = (i % 41 === 0) ? Math.max(0, Math.sin(time * 1.4 + i * 0.37)) : 0;
      } else if (lit === 3) {  // waveform: speech-like columns
        const c = i % WC, r = Math.floor(i / WC);
        const amp = 0.5 + 0.5 * Math.sin(c * 0.33 + time * 3.1) * Math.sin(c * 0.09 - time * 1.3);
        const on = r < amp * 25;
        sc *= on ? 1 : 0.0001; heat = on && r > amp * 25 - 2 ? 1 : 0;
      } else if (lit === 4) {  // die: blocks light up like streaming multiprocessors
        const c = i % 40, r = Math.floor(i / 40), b = Math.floor(c / 5) + Math.floor(r / 5) * 8;
        heat = Math.max(0, Math.sin(time * 2 + b * 1.7)) > 0.92 ? 1 : 0;
      }
      const gw = Math.max(0, 1 - Math.abs(pr - 1) * 1.4);  // the globe turns slowly while it is on screen
      if (gw > 0) { const an = time * 0.22 * gw, cx = 0, cz = 0, ox = x - cx, oz = z - cz; x = cx + ox * Math.cos(an) - oz * Math.sin(an); z = cz + ox * Math.sin(an) + oz * Math.cos(an); }
      d.position.set(x, y, z);
      d.rotation.set(mid * delay[i] * 3, mid * 2.2, 0);
      d.scale.setScalar(Math.max(sc, 0.0001));
      d.updateMatrix(); mesh.setMatrixAt(i, d.matrix);
      col.copy(TEAL).lerp(TEAL_HI, 0.25 + 0.25 * Math.sin(i * 0.7 + time * 0.6)).lerp(DEEP, delay[i] * 0.35);
      if (heat > 0) col.lerp(AMBER, Math.min(1, heat));
      mesh.setColorAt(i, col);
    }
    mesh.instanceMatrix.needsUpdate = true; mesh.instanceColor.needsUpdate = true;

    const ce = ease(clamp(f));
    camPos.lerpVectors(CAM[si][0], CAM[si + 1][0], ce); camAt.lerpVectors(CAM[si][1], CAM[si + 1][1], ce);
    cam.position.set(camPos.x + mx * 4, camPos.y - my * 3, camPos.z);
    at.copy(camAt); cam.lookAt(at);
    lmat.opacity = Math.max(0, 1 - Math.abs(pr - 2) * 1.6) * (0.55 + 0.45 * Math.sin(time * 4));
    glow.intensity = lit === 0 ? 0 : 0; glow.position.set(camAt.x, camAt.y + 6, camAt.z);
    renderer.render(scene, cam);
    if (!reduced) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
  return { redraw: () => requestAnimationFrame(frame) };
}
