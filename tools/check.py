"""Controlli di accettazione del sito (Playwright + server locale, mai file://).

  python tools/check.py [CARTELLA_REPORT]

Budget di peso, rete, font, id IT/EN, cliché (03-cliche.md), contrasto, accessibilità (axe-core
iniettato da file locale, non dalla pagina), movimento (rAF a pagina ferma e con reduced motion),
tema senza localStorage, griglia contro tacche. Scrive report.json e stampa i punti falliti.
"""
import base64
import hashlib
import http.server
import json
import os
import re
import socketserver
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AXE = os.path.join(ROOT, "..", "artyomita-redesign", "tools", "axe.min.js")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "..", "artyomita-redesign", "shots", "check")
BUDGET = {"html": 60 * 1024, "css": 35 * 1024, "js": 45 * 1024, "font": 180 * 1024, "img": 80 * 1024, "total": 400 * 1024}

PAGE_JS = r"""() => {
  const R = {}, all = [...document.querySelectorAll('body *')];
  const vis = e => { const s = getComputedStyle(e); const r = e.getBoundingClientRect(); return s.visibility !== 'hidden' && s.display !== 'none' && r.width > 0 && r.height > 0; };
  R.uppercase = all.filter(e => getComputedStyle(e).textTransform === 'uppercase').length;
  R.boxShadow = all.filter(e => getComputedStyle(e).boxShadow !== 'none').map(e => e.tagName + '.' + e.className);
  R.backdrop = all.filter(e => { const s = getComputedStyle(e); return (s.backdropFilter && s.backdropFilter !== 'none'); }).length;
  R.radius = [...new Set(all.filter(e => { const s = getComputedStyle(e); return parseFloat(s.borderTopLeftRadius) > 0 && !(e instanceof SVGElement); }).map(e => e.tagName.toLowerCase() + '.' + e.className))];
  R.cursor = all.filter(e => { const c = getComputedStyle(e).cursor; return c && !['auto', 'pointer', 'default', 'text'].includes(c); }).length;
  R.infiniteAnim = all.filter(e => getComputedStyle(e).animationIterationCount === 'infinite').length;
  const fams = new Set(); all.forEach(e => { if (vis(e) && [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) fams.add(getComputedStyle(e).fontFamily.split(',')[0].replace(/"/g, '').trim()); });
  R.fonts = [...fams];
  const text = document.body.innerText;
  R.emdash = (text.match(/—/g) || []).length;
  R.emoji = (text.match(/\p{Extended_Pictographic}/gu) || []).filter(c => !'©®™↔'.includes(c));
  R.firstLine = text.trim().split('\n')[0];
  R.banned = ['passionate about', 'crafting', 'building the future', 'best-in-class', 'cutting-edge', 'all-in-one', 'next-generation', 'COMING SOON', 'IN ARRIVO', '★', 'Scopri di più', 'Learn More', 'Get Started'].filter(s => text.includes(s));
  R.italicInHeading = document.querySelectorAll('h1 em,h1 i,h2 em,h2 i,h3 em,h3 i').length;
  const lt = {}; document.querySelectorAll('a').forEach(a => { const t = a.textContent.trim(); lt[t] = (lt[t] || 0) + 1; });
  R.repeatedLinks = Object.entries(lt).filter(([t, n]) => n > 2);
  R.figures = [...document.querySelectorAll('figure')].map(f => ({ id: f.id, cap: !!f.querySelector('figcaption'), named: [...f.querySelectorAll('svg[role=img],canvas[role=img]')].every(x => x.getAttribute('aria-label') || x.getAttribute('aria-labelledby')) }));
  // contrasto
  function rgb(s) { const m = s.match(/[\d.]+/g); return m ? m.map(Number) : [0, 0, 0, 1]; }
  function lum(c) { const a = c.slice(0, 3).map(v => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }); return .2126 * a[0] + .7152 * a[1] + .0722 * a[2]; }
  function bg(e) { while (e) { const c = rgb(getComputedStyle(e).backgroundColor); if (c.length < 4 || c[3] > .5) { if (!(c.length >= 4 && c[3] === 0)) return c; } e = e.parentElement; } return rgb(getComputedStyle(document.body).backgroundColor); }
  const low = [];
  all.forEach(e => {
    if (!vis(e) || e.closest('svg') || e.closest('[aria-hidden=true]')) return;
    if (![...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) return;
    const s = getComputedStyle(e), fg = rgb(s.color), b = bg(e), op = parseFloat(s.opacity);
    const L1 = lum(fg), L2 = lum(b), cr = (Math.max(L1, L2) + .05) / (Math.min(L1, L2) + .05);
    const big = parseFloat(s.fontSize) >= 24 || (parseFloat(s.fontSize) >= 18.66 && parseInt(s.fontWeight) >= 700);
    if (cr < (big ? 3 : 4.5) || op < 1) low.push([e.tagName, e.className, e.textContent.trim().slice(0, 30), cr.toFixed(2)]);
  });
  R.lowContrast = low;
  // bersagli interattivi
  R.smallTargets = [...document.querySelectorAll('button,summary,.lang a,.nav a')].filter(vis).map(e => { const r = e.getBoundingClientRect(); return [e.textContent.trim(), Math.round(r.width), Math.round(r.height)]; }).filter(x => x[1] < 24 || x[2] < 24);
  R.ids = [...document.querySelectorAll('[id]')].map(e => e.id).sort();
  R.h1 = { sw: document.querySelector('h1').scrollWidth, cw: document.querySelector('h1').clientWidth };
  R.fig3 = [...document.querySelectorAll('#kt text.fv')].map(t => t.textContent);
  R.fig4 = document.getElementById('err-v') ? document.getElementById('err-v').textContent : null;
  R.fig5 = document.getElementById('fence').classList.contains('chiuso');
  return R;
}"""

RAF = """() => new Promise(res => { let n = 0; const o = window.requestAnimationFrame; window.requestAnimationFrame = f => { n++; return o(f); }; setTimeout(() => res(n), 2000); })"""


def serve():
    class Q(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=ROOT, **k)

        def log_message(self, *a):
            pass
    srv = socketserver.TCPServer(("127.0.0.1", 0), Q)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def kind(u):
    ext = u.split("?")[0].rsplit(".", 1)[-1].lower()
    return {"woff2": "font", "css": "css", "js": "js", "webp": "img", "png": "img", "svg": "img"}.get(ext, "html")


def main():
    from playwright.sync_api import sync_playwright
    os.makedirs(OUT, exist_ok=True)
    srv = serve()
    base = "http://127.0.0.1:%d/" % srv.server_address[1]
    rep, fail = {}, []

    # hash della CSP
    for rel in ("index.html", "en/index.html"):
        html = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        boot = re.search(r"<script>(.*?)</script>", html, re.S).group(1)
        h = base64.b64encode(hashlib.sha256(boot.encode()).digest()).decode()
        if ("sha256-" + h) not in html:
            fail.append("CSP: hash dello script di avvio non corrisponde in " + rel)
        if "style=" in html:
            fail.append("style= inline in " + rel)
        if re.search(r"adriandj|@gmail|vergilius-privato", html):
            fail.append("dato privato in " + rel)

    with sync_playwright() as p:
        br = p.chromium.launch(channel="chrome")
        for lang, path in (("it", ""), ("en", "en/")):
            for theme in ("light", "dark"):
                ctx = br.new_context(viewport={"width": 1440, "height": 900}, color_scheme=theme)
                pg = ctx.new_page()
                msgs, reqs = [], []
                pg.on("console", lambda m: msgs.append(m.type + ": " + m.text) if m.type in ("error", "warning") else None)
                pg.on("pageerror", lambda e: msgs.append("pageerror: " + str(e)))
                pg.on("requestfinished", lambda r: reqs.append(r))
                pg.goto(base + path)
                pg.evaluate("document.fonts.ready")
                pg.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                pg.wait_for_timeout(800)
                sizes = {}
                for r in reqs:
                    if not r.url.startswith(base):
                        fail.append("%s %s richiesta esterna %s" % (lang, theme, r.url))
                        continue
                    try:
                        b = len(r.response().body())
                    except Exception:
                        b = 0
                    sizes[r.url.replace(base, "/")] = b
                tot = {}
                for u, b in sizes.items():
                    tot[kind(u)] = tot.get(kind(u), 0) + b
                tot["total"] = sum(sizes.values())
                for k, lim in BUDGET.items():
                    if tot.get(k, 0) > lim:
                        fail.append("%s budget %s %d > %d" % (lang, k, tot.get(k, 0), lim))
                if any("latin-ext" in u for u in sizes):
                    fail.append("%s latin-ext scaricato" % lang)
                # scorre tutta la pagina a passi per portare le figure a p = 1 dove previsto
                pg.evaluate("window.scrollTo(0,0)")
                for id_ in ("fig3", "fig4", "fig5"):
                    pg.evaluate("(id)=>{const e=document.getElementById(id);window.scrollTo(0,e.getBoundingClientRect().top+scrollY-innerHeight*0.25)}", id_)
                    pg.wait_for_timeout(500)
                    v = pg.evaluate(PAGE_JS)
                    if id_ == "fig3":
                        exp = ["0,71×", "0,93×"] if lang == "it" else ["0.71×", "0.93×"]
                        if v["fig3"] != exp:
                            fail.append("%s %s Fig.3 %s" % (lang, theme, v["fig3"]))
                    if id_ == "fig4" and v["fig4"] != ("0,999956" if lang == "it" else "0.999956"):
                        fail.append("%s %s Fig.4 %s" % (lang, theme, v["fig4"]))
                    if id_ == "fig5" and not v["fig5"]:
                        fail.append("%s %s Fig.5 recinto aperto" % (lang, theme))
                v = pg.evaluate(PAGE_JS)
                # pagina ferma: dopo 10 s nessun rAF
                pg.evaluate("window.scrollTo(0,0)")
                pg.wait_for_timeout(10500)
                idle = pg.evaluate(RAF)
                if idle:
                    fail.append("%s %s rAF a pagina ferma: %d" % (lang, theme, idle))
                # axe
                if os.path.exists(AXE):
                    pg.evaluate("(src)=>{(0,eval)(src)}", open(AXE, encoding="utf-8").read())
                    ax = pg.evaluate("async()=>{const r=await axe.run(document,{resultTypes:['violations']});return r.violations.map(v=>[v.id,v.impact,v.nodes.length,v.nodes.slice(0,2).map(n=>n.target.join(' '))])}")
                    for a in ax:
                        if a[1] in ("serious", "critical"):
                            fail.append("%s %s axe %s" % (lang, theme, a))
                    v["axe"] = ax
                if msgs:
                    fail.append("%s %s console %s" % (lang, theme, msgs[:4]))
                v.update({"bytes": tot, "files": sizes, "idle_raf": idle})
                rep["%s-%s" % (lang, theme)] = v
                for key, bad in (("uppercase", v["uppercase"]), ("boxShadow", v["boxShadow"]), ("backdrop", v["backdrop"]), ("cursor", v["cursor"]),
                                 ("infiniteAnim", v["infiniteAnim"]), ("emdash", v["emdash"]), ("emoji", v["emoji"]), ("banned", v["banned"]),
                                 ("italicInHeading", v["italicInHeading"]), ("repeatedLinks", v["repeatedLinks"]), ("lowContrast", v["lowContrast"]),
                                 ("smallTargets", v["smallTargets"])):
                    if bad:
                        fail.append("%s %s %s: %s" % (lang, theme, key, str(bad)[:300]))
                if [r for r in v["radius"] if not r.startswith("sup.n")]:
                    fail.append("%s %s radius: %s" % (lang, theme, v["radius"]))
                if set(v["fonts"]) - {"Newsreader", "Besley", "Tavola Mono"}:
                    fail.append("%s %s font: %s" % (lang, theme, v["fonts"]))
                if re.match(r"^(Hi|Ciao|Hey)", v["firstLine"]):
                    fail.append("prima riga " + v["firstLine"])
                if not all(f["cap"] and f["named"] for f in v["figures"]):
                    fail.append("%s figure senza didascalia o nome" % lang)
                ctx.close()

        # id uguali IT/EN
        if rep["it-light"]["ids"] != rep["en-light"]["ids"]:
            fail.append("id diversi IT/EN: %s" % (set(rep["it-light"]["ids"]) ^ set(rep["en-light"]["ids"])))

        # reduced motion: zero rAF dopo il load, figure al fotogramma finale
        for lang, path in (("it", ""), ("en", "en/")):
            ctx = br.new_context(viewport={"width": 390, "height": 844}, reduced_motion="reduce")
            pg = ctx.new_page()
            pg.goto(base + path)
            pg.wait_for_timeout(600)
            n = pg.evaluate(RAF)
            v = pg.evaluate(PAGE_JS)
            if n:
                fail.append("%s reduced motion: %d rAF" % (lang, n))
            if v["fig4"] != ("0,999956" if lang == "it" else "0.999956") or not v["fig5"]:
                fail.append("%s reduced motion: figure non al fotogramma finale" % lang)
            # tastiera: primo Tab sul salto al contenuto
            pg.keyboard.press("Tab")
            f = pg.evaluate("document.activeElement.className")
            if f != "skip":
                fail.append("%s primo Tab su %s" % (lang, f))
            ctx.close()

        # localStorage che lancia: la pagina funziona e il tema si cambia
        ctx = br.new_context(viewport={"width": 1024, "height": 800})
        ctx.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new Error('blocked')}})")
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(base)
        pg.click("button[data-set=dark]")
        th = pg.evaluate("document.documentElement.getAttribute('data-theme')")
        if errs or th != "dark":
            fail.append("localStorage bloccato: %s %s" % (errs, th))
        ctx.close()

        # griglia contro tacche e zoom del testo
        for w in (1440, 768):
            ctx = br.new_context(viewport={"width": w, "height": 900})
            pg = ctx.new_page()
            pg.goto(base)
            pg.click("#gridbtn")
            d = pg.evaluate("""()=>{const r=document.querySelector('#ricerca .rule');const ticks=[...r.children].filter(i=>getComputedStyle(i).display!=='none').map(i=>i.getBoundingClientRect().left);
              const s=getComputedStyle(document.body,'::after');const cw=r.getBoundingClientRect().width;const cols=+getComputedStyle(document.documentElement).getPropertyValue('--cols');
              const gap=parseFloat(getComputedStyle(r).columnGap);const x0=r.getBoundingClientRect().left;const exp=[...Array(cols).keys()].map(k=>x0+k*((cw-(cols-1)*gap)/cols+gap));
              return Math.max(...ticks.map((t,i)=>Math.abs(t-exp[i])))}""")
            if d > 1:
                fail.append("griglia %d: scarto %.2f px" % (w, d))
            ctx.close()
        ctx = br.new_context(viewport={"width": 1280, "height": 900})
        pg = ctx.new_page()
        pg.goto(base)
        pg.evaluate("document.documentElement.style.fontSize='200%'")
        pg.wait_for_timeout(300)
        o = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
        if o > 0:
            fail.append("zoom testo 200%%: overflow %d px" % o)
        ctx.close()
        br.close()
    srv.shutdown()
    rep["fail"] = fail
    with open(os.path.join(OUT, "report.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=1, ensure_ascii=False)
    print(json.dumps({"fail": fail, "bytes_it": rep["it-light"]["bytes"], "bytes_en": rep["en-light"]["bytes"]}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
