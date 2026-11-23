import { start } from './world.js';

const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const { gsap, ScrollTrigger } = window;
gsap.registerPlugin(ScrollTrigger);

// words inside a mask, keeping <b>, <em> and <br>
function split(el) {
  const walk = (node) => {
    [...node.childNodes].forEach((n) => {
      if (n.nodeType === 3) {
        const frag = document.createDocumentFragment();
        n.textContent.split(/(\s+)/).forEach((part) => {
          if (!part) return;
          if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(' ')); return; }
          const w = document.createElement('span'); w.className = 'w';
          const s = document.createElement('span'); s.textContent = part; w.appendChild(s); frag.appendChild(w);
        });
        n.replaceWith(frag);
      } else if (n.nodeType === 1 && n.tagName !== 'BR') walk(n);
    });
  };
  walk(el);
  return el.querySelectorAll('.w>span');
}

// scroll position -> stage number with holds: the world stays on a shape while its panel is read, then morphs
const stages = [...document.querySelectorAll('[data-stage]')];
let progress = 0;
function measure() {
  const y = scrollY + innerHeight * 0.5;
  const tops = stages.map((s) => s.offsetTop + s.offsetHeight * 0.5);
  if (y <= tops[0]) { progress = 0; return; }
  for (let i = 0; i < tops.length - 1; i++) {
    if (y < tops[i + 1]) {
      const f = (y - tops[i]) / (tops[i + 1] - tops[i]);
      progress = i + Math.min(1, Math.max(0, (f - 0.2) / 0.6));
      return;
    }
  }
  progress = tops.length - 1;
}
addEventListener('scroll', measure, { passive: true }); addEventListener('resize', measure); measure();

start(document.getElementById('world'), () => progress, reduced);

if (!reduced) {
  // hero: the name lands word by word, decelerating, then the line and the buttons
  const hw = split(document.querySelector('h1'));
  const hl = split(document.querySelector('.hero .split-l'));
  gsap.timeline({ defaults: { ease: 'expo.out' } })
    .from('.hero .tag', { y: 20, opacity: 0, duration: 0.9 }, 0.1)
    .from(hw, { yPercent: 115, rotate: 4, duration: 1.4, stagger: 0.08 }, 0.15)
    .from(hl, { yPercent: 110, duration: 1.1, stagger: 0.012 }, 0.6)
    .from('.hero .go .btn', { y: 26, opacity: 0, duration: 1, stagger: 0.06 }, 0.9)
    .from('.cue', { opacity: 0, duration: 1 }, 1.4);

  // panels: title and catch line rise word by word, the rest follows, numbers count up
  document.querySelectorAll('.st[data-stage]:not(.hero)').forEach((sec) => {
    const t = split(sec.querySelector('h2')), c = split(sec.querySelector('.catch'));
    const tl = gsap.timeline({ defaults: { ease: 'expo.out' }, scrollTrigger: { trigger: sec, start: 'top 62%', toggleActions: 'play none none reverse' } });
    tl.from(sec.querySelector('.panel'), { y: 60, opacity: 0, scale: 0.97, duration: 1.2 }, 0)
      .from(sec.querySelector('.k'), { x: -20, opacity: 0, duration: 0.8 }, 0.1)
      .from(t, { yPercent: 115, duration: 1.2, stagger: 0.06 }, 0.15)
      .from(c, { yPercent: 110, duration: 1, stagger: 0.02 }, 0.35)
      .from(sec.querySelectorAll('.reveal'), { y: 24, opacity: 0, duration: 1, stagger: 0.08 }, 0.5);
    sec.querySelectorAll('[data-n]').forEach((b) => {
      const end = parseFloat(b.dataset.n), dec = +(b.dataset.d || 0), pre = b.textContent.startsWith('+') ? '+' : '';
      const o = { v: 0 };
      tl.to(o, { v: end, duration: 1.6, ease: 'power3.out', onUpdate: () => { b.textContent = pre + o.v.toFixed(dec); } }, 0.6);
    });
  });
}

// nav: highlight the section in view
const links = [...document.querySelectorAll('.nav nav a')];
stages.slice(1).forEach((sec, i) => ScrollTrigger.create({ trigger: sec, start: 'top center', end: 'bottom center',
  onToggle: (s) => links[i].classList.toggle('on', s.isActive) }));
