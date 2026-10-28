/* Scena della hero: token (punti) che attraversano una griglia 3D di "SM" di una GPU.
   Sorgente di js/hero.js (three.js incluso, ridotto alle classi usate): python tools/build-hero.py
   Tutto e' calcolato negli shader dal tempo; la CPU aggiorna solo gli uniform. Seme fisso 27721 (numero della PR). */
import {
  WebGLRenderer, Scene, PerspectiveCamera, Group, BufferGeometry, BufferAttribute, InstancedBufferAttribute,
  InstancedMesh, PlaneGeometry, ShaderMaterial, Points, LineSegments, Mesh, Object3D, Vector3, AdditiveBlending
} from 'three';

const COLS = 16, ROWS = 9, PITCH = 0.9, TILE = 0.7, DIE_W = COLS * PITCH;
const MINT = [0.18, 0.95, 0.69], CORAL = [1.0, 0.42, 0.34];

function rng(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

const TILE_VS = `
attribute vec3 aTile;
uniform float uTime; uniform vec2 uMouse;
varying vec2 vUv; varying float vAct; varying float vRnd;
void main(){
  vUv = uv; vRnd = aTile.z;
  vec4 wp = modelMatrix * instanceMatrix * vec4(position, 1.0);
  vec4 c0 = modelMatrix * instanceMatrix * vec4(0.0, 0.0, 0.0, 1.0);
  float travel = fract(uTime * 0.2 + aTile.y * 5.3 - aTile.x * 1.7);
  float pulse = smoothstep(0.0, 0.03, travel) * exp(-travel * 7.0);
  float flick = pow(0.5 + 0.5 * sin(uTime * (0.4 + aTile.z * 1.1) + aTile.z * 61.0), 20.0);
  float m = exp(-distance(c0.xz, uMouse) * 0.75);
  vAct = clamp(pulse * 0.95 + flick * 0.8 + m * 0.9, 0.0, 1.0);
  gl_Position = projectionMatrix * viewMatrix * wp;
}`;
const TILE_FS = `
uniform vec3 uMint; uniform vec3 uCoral; uniform float uOpacity;
varying vec2 vUv; varying float vAct; varying float vRnd;
void main(){
  vec2 e = min(vUv, 1.0 - vUv);
  float edge = 1.0 - smoothstep(0.0, 0.07, min(e.x, e.y));
  vec3 col = mix(uMint * 0.55, uMint, vAct);
  col = mix(col, uCoral * (0.65 + 0.35 * vAct), step(0.93, vRnd));
  float a = (0.035 + edge * 0.22 + vAct * (0.5 + edge * 0.5)) * uOpacity;
  gl_FragColor = vec4(col, a);
}`;
const FLOOR_VS = `varying vec3 vW; void main(){ vW = (modelMatrix * vec4(position, 1.0)).xyz; gl_Position = projectionMatrix * viewMatrix * vec4(vW, 1.0); }`;
const FLOOR_FS = `
uniform vec3 uMint; uniform float uOpacity; uniform vec2 uOrigin;
varying vec3 vW;
void main(){
  vec2 q = (vW.xz - uOrigin) / ${PITCH.toFixed(2)} + 0.5;
  vec2 g = abs(fract(q) - 0.5) / fwidth(q);
  float line = 1.0 - min(min(g.x, g.y), 1.0);
  float fade = exp(-length(vW.xz - uOrigin) * 0.085);
  gl_FragColor = vec4(uMint, line * 0.11 * fade * uOpacity);
}`;
const PART_VS = `
attribute float aW; attribute float aTr;
uniform float uTime; uniform float uPR; uniform float uScale; uniform float uOpacity; uniform float uDieW;
varying vec3 vCol; varying float vA;
const float L = 40.0;
void main(){
  vec3 sd = position;
  float spd = 0.8 + 1.5 * sd.y;
  float x = mod(sd.x * L + uTime * spd, L) - 0.5 * L - aTr * 0.17 * (0.8 + spd);
  float lane = floor(sd.z * 9.0);
  float z = (lane - 4.0) * 0.9 + (aW - 0.5) * 0.5;
  float hd = uDieW * 0.5;
  float inDie = smoothstep(-hd - 1.2, -hd + 0.8, x) * (1.0 - smoothstep(hd - 0.8, hd + 1.2, x));
  float after = smoothstep(hd - 0.5, hd + 3.0, x);
  float before = 1.0 - smoothstep(-hd - 3.0, -hd + 0.5, x);
  float r2 = fract(aW * 17.31 + sd.y * 5.7);
  float isOut = step(0.86, fract(aW * 13.7));
  float y = mix(0.9 + 2.6 * r2, 0.16 + 0.5 * fract(aW * 5.13), inDie);
  y += sin(x * 0.55 + uTime * 0.7 + sd.x * 40.0) * 0.22 * (1.0 - inDie);
  y += after * after * (0.5 + r2 * 2.4) * isOut;
  z += sin(x * 0.4 + sd.y * 30.0) * 0.35 * (1.0 - inDie) * (before * 0.8 + after);
  vec4 mv = modelViewMatrix * vec4(x, y, z, 1.0);
  gl_Position = projectionMatrix * mv;
  float size = (1.5 + 3.0 * fract(aW * 9.3)) * (0.85 + 0.9 * inDie) * (1.0 - aTr * 0.16);
  gl_PointSize = clamp(size * uPR * uScale / -mv.z, 1.0, 12.0 * uPR);
  vec3 col = mix(vec3(0.62, 0.74, 0.80), vec3(0.18, 0.95, 0.69), clamp(inDie + after * 0.55, 0.0, 1.0));
  col = mix(col, vec3(1.0, 0.42, 0.34), isOut * after);
  float ef = smoothstep(-0.5 * L, -0.5 * L + 5.0, x) * (1.0 - smoothstep(0.5 * L - 6.0, 0.5 * L, x));
  vA = (0.16 + 0.7 * inDie + 0.3 * after) * ef * uOpacity * (1.0 - aTr * 0.27);
  vCol = col;
}`;
const PART_FS = `
varying vec3 vCol; varying float vA;
void main(){
  float d = length(gl_PointCoord - 0.5);
  float a = smoothstep(0.5, 0.0, d); a = a * a * 1.25;
  if (a * vA < 0.004) discard;
  gl_FragColor = vec4(vCol, a * vA);
}`;
const ARC_VS = `
attribute float aT; attribute float aOff; attribute float aC;
uniform float uTime; uniform float uOpacity;
varying float vI; varying float vC;
void main(){
  float k = fract(uTime * 0.16 + aOff - aT);
  vI = (0.06 + exp(-k * 9.0)) * uOpacity; vC = aC;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}`;
const ARC_FS = `
uniform vec3 uMint; uniform vec3 uCoral;
varying float vI; varying float vC;
void main(){ gl_FragColor = vec4(mix(uMint, uCoral, vC), vI * 0.85); }`;

function mat(vs, fs, uniforms) {
  return new ShaderMaterial({ vertexShader: vs, fragmentShader: fs, uniforms, transparent: true, depthWrite: false, blending: AdditiveBlending });
}

export function start(canvas, host) {
  const renderer = new WebGLRenderer({ canvas, antialias: false, alpha: true, powerPreference: 'high-performance' });
  const small = matchMedia('(max-width: 700px)').matches;
  let pr = Math.min(window.devicePixelRatio || 1, small ? 1.5 : 2);
  renderer.setPixelRatio(pr);
  const scene = new Scene(), camera = new PerspectiveCamera(42, 1, 0.1, 120), world = new Group();
  scene.add(world);
  const r = rng(27721);
  const U = {
    uTime: { value: 0 }, uMint: { value: MINT }, uCoral: { value: CORAL }, uOpacity: { value: 1 },
    uMouse: { value: [99, 99] }, uPR: { value: pr }, uScale: { value: 1 }, uDieW: { value: DIE_W }, uOrigin: { value: [0, 0] }
  };

  /* griglia degli SM: un solo InstancedMesh, il bordo e la luce sono nello shader */
  const tg = new PlaneGeometry(TILE, TILE).rotateX(-Math.PI / 2), n = COLS * ROWS, aTile = new Float32Array(n * 3), o = new Object3D();
  const tiles = new InstancedMesh(tg, mat(TILE_VS, TILE_FS, U), n);
  for (let c = 0, i = 0; c < COLS; c++) for (let rr = 0; rr < ROWS; rr++, i++) {
    o.position.set((c - (COLS - 1) / 2) * PITCH, 0, (rr - (ROWS - 1) / 2) * PITCH); o.updateMatrix(); tiles.setMatrixAt(i, o.matrix);
    aTile.set([c / COLS, rr / ROWS, r()], i * 3);
  }
  tg.setAttribute('aTile', new InstancedBufferAttribute(aTile, 3));
  tiles.frustumCulled = false; world.add(tiles);
  const floor = new Mesh(new PlaneGeometry(90, 90).rotateX(-Math.PI / 2), mat(FLOOR_VS, FLOOR_FS, U));
  floor.position.y = -0.02; floor.frustumCulled = false; world.add(floor);

  /* archi di attention: comete di luce fra coppie di SM */
  const ap = [], at = [], ao = [], ac = [], S = 26;
  for (let a = 0; a < 46; a++) {
    const c1 = r() * (COLS - 1), r1 = r() * (ROWS - 1), dx = (r() < 0.5 ? -1 : 1) * (2 + r() * 5), dz = (r() - 0.5) * 6;
    const c2 = Math.max(0, Math.min(COLS - 1, c1 + dx)), r2 = Math.max(0, Math.min(ROWS - 1, r1 + dz));
    const A = [(c1 - (COLS - 1) / 2) * PITCH, 0.05, (r1 - (ROWS - 1) / 2) * PITCH], B = [(c2 - (COLS - 1) / 2) * PITCH, 0.05, (r2 - (ROWS - 1) / 2) * PITCH];
    const h = 0.7 + Math.hypot(B[0] - A[0], B[2] - A[2]) * 0.28, off = r(), col = r() < 0.16 ? 1 : 0;
    const P = t => [A[0] + (B[0] - A[0]) * t, A[1] + Math.sin(Math.PI * t) * h, A[2] + (B[2] - A[2]) * t];
    for (let s = 0; s < S; s++) { ap.push(...P(s / S), ...P((s + 1) / S)); at.push(s / S, (s + 1) / S); ao.push(off, off); ac.push(col, col); }
  }
  const ag = new BufferGeometry();
  ag.setAttribute('position', new BufferAttribute(new Float32Array(ap), 3));
  ag.setAttribute('aT', new BufferAttribute(new Float32Array(at), 1));
  ag.setAttribute('aOff', new BufferAttribute(new Float32Array(ao), 1));
  ag.setAttribute('aC', new BufferAttribute(new Float32Array(ac), 1));
  const arcs = new LineSegments(ag, mat(ARC_VS, ARC_FS, U)); arcs.frustumCulled = false; world.add(arcs);

  /* token: ogni punto ha tre semi (in position) e uno in aW; il percorso e' tutto nello shader */
  const N = small ? 3000 : 8000, TR = 4, ps = new Float32Array(N * TR * 3), pw = new Float32Array(N * TR), pt = new Float32Array(N * TR);
  for (let i = 0; i < N; i++) {
    const a = r(), b = r(), c = r(), w = r();
    for (let k = 0; k < TR; k++) { const j = i * TR + k; ps.set([a, b, c], j * 3); pw[j] = w; pt[j] = k; }
  }
  const pg = new BufferGeometry();
  pg.setAttribute('position', new BufferAttribute(ps, 3));
  pg.setAttribute('aW', new BufferAttribute(pw, 1));
  pg.setAttribute('aTr', new BufferAttribute(pt, 1));
  const pts = new Points(pg, mat(PART_VS, PART_FS, U)); pts.frustumCulled = false; world.add(pts);

  /* inquadratura: larga con il testo a sinistra, stretta con la scena sotto il testo */
  let W = 1, H = 1, wide = true;
  function size() {
    W = host.clientWidth; H = host.clientHeight; wide = W / H > 1.15;
    renderer.setSize(W, H, false); camera.aspect = W / H; camera.fov = wide ? 42 : 68;
    if (wide) camera.clearViewOffset(); else camera.setViewOffset(W, H, 0, H * 0.2, W, H);
    camera.updateProjectionMatrix();
    U.uScale.value = H * 0.0125 * (wide ? 1 : 0.85);
    world.position.set(wide ? Math.min(3.8, W / 380) : 0, -0.2, wide ? 0 : -1);
    U.uOrigin.value = [world.position.x, world.position.z];
  }
  new ResizeObserver(size).observe(host); size();

  let mx = 0, my = 0, cx = 0, cy = 0, hasPtr = false;
  const fine = matchMedia('(hover:hover) and (pointer:fine)').matches;
  if (fine) addEventListener('pointermove', e => { const b = host.getBoundingClientRect(); mx = (e.clientX - b.left) / b.width * 2 - 1; my = -((e.clientY - b.top) / b.height * 2 - 1); hasPtr = true; }, { passive: true });

  const ray = new Vector3(), tgt = new Vector3(0, 0.3, 0);
  let running = false, raf = 0, t0 = 0, acc = 0, fr = 0, last = 0, tier = 0;
  function frame(now) {
    raf = 0; if (!running) return;
    const t = (now - t0) / 1000, sc = Math.min(1, Math.max(0, scrollY / (H || 1)));
    cx += (mx - cx) * 0.045; cy += (my - cy) * 0.045;
    camera.position.set(cx * 1.4 + Math.sin(t * 0.07) * 0.5, (wide ? 6.6 : 7.4) + cy * 0.8 + sc * 1.8, (wide ? 13.6 : 17) + sc * 3);
    camera.lookAt(tgt.x + cx * 0.3, tgt.y + sc * 0.6, tgt.z); camera.updateMatrixWorld();
    if (hasPtr && wide) {
      ray.set(mx, my, 0.5).unproject(camera).sub(camera.position).normalize();
      const k = -camera.position.y / ray.y; U.uMouse.value = k > 0 ? [camera.position.x + ray.x * k, camera.position.z + ray.z * k] : [99, 99];
    }
    U.uTime.value = t; U.uOpacity.value = 1 - sc * 0.85;
    renderer.render(scene, camera);
    if (!fr++) host.classList.add('gl');
    /* se i primi 60 fotogrammi sono lenti: prima si abbassa la risoluzione, poi i token */
    if (last && fr > 8 && tier < 2 && fr < 200) {
      acc += now - last;
      if (fr % 60 === 0) {
        if (acc / 60 > 30) { tier++; if (tier === 1) { pr = 1; renderer.setPixelRatio(1); U.uPR.value = 1; size(); } else { pg.setDrawRange(0, (N * TR) >> 1); } }
        acc = 0;
      }
    }
    last = now; canvas.dataset.run = '1';
    raf = requestAnimationFrame(frame);
  }
  function go(on) {
    if (on === running) return; running = on; canvas.dataset.run = on ? '1' : '0';
    if (on) { t0 = t0 ? performance.now() - (last - t0) : performance.now(); last = 0; if (!raf) raf = requestAnimationFrame(frame); } else if (raf) { cancelAnimationFrame(raf); raf = 0; }
  }
  let vis = true;
  const upd = () => go(vis && document.visibilityState === 'visible');
  new IntersectionObserver(es => { vis = es[0].isIntersecting; upd(); }).observe(host);
  document.addEventListener('visibilitychange', upd);
  canvas.addEventListener('webglcontextlost', e => { e.preventDefault(); go(false); host.classList.remove('gl'); });
  upd();
}
