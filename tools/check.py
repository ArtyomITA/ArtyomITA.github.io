"""Controlli di accettazione del sito (Playwright + Chrome + server locale, mai file://).

Ordine: python tools/hf-models.py (se serve), python tools/build-pages.py, python tools/build-hero.py, python tools/make-images.py og, poi

  python tools/check.py [CARTELLA_REPORT]

Controlli: console senza errori (con WebGL e senza), nessuna richiesta a domini esterni, nessuno scroll orizzontale da 320 a 1920 px,
contrasto AA del testo (DOM, sui due temi) e del testo della hero sopra la scena 3D (pixel), reduced-motion (scena non caricata,
nessuna animazione), pausa della scena fuori vista, tema (predefinito scuro, persistente), id uguali in IT ed EN, nessun trattino lungo
(U+2014, U+2013), pesi, LCP, axe-core (file locale). Scrive report.json e stampa i punti falliti; esce con 1 se ce n'e' uno.
"""
import gzip
import http.server
import io
import json
import os
import re
import socketserver
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AXE = os.path.join(ROOT, "..", "artyomita-redesign", "tools", "axe.min.js")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "..", "artyomita-redesign", "shots", "check")
WIDTHS = (320, 360, 375, 390, 414, 600, 768, 900, 1024, 1180, 1280, 1440, 1920)
# byte (non KiB); hero.js e' three.js ridotto e si carica a pagina finita, non conta nel peso iniziale
BUDGET = {"html": 70000, "css": 40000, "js": 30000, "font": 60000, "initial": 200000, "hero": 600000}
DASH = "—–"

PAGE_JS = r"""() => {
  const R = {}, all = [...document.querySelectorAll('body *')];
  const vis = e => { const s = getComputedStyle(e), r = e.getBoundingClientRect(); return s.visibility !== 'hidden' && s.display !== 'none' && r.width > 0 && r.height > 0; };
  const text = document.body.innerText;
  R.dash = (text.match(/[—–]/g) || []).length;
  R.emoji = (text.match(/\p{Extended_Pictographic}/gu) || []).filter(c => !'©®™↗'.includes(c));
  R.h1 = document.querySelectorAll('h1').length;
  R.h1text = document.querySelector('h1').textContent.replace(/\s+/g, ' ').trim();
  R.banned = ['in produzione', 'in production', 'passionate', 'cutting-edge', 'Scopri di pi', 'Learn More'].filter(w => text.includes(w));
  R.likes = (document.querySelector('.hf') || { innerText: '' }).innerText.match(/\blike/i);
  R.ids = [...document.querySelectorAll('[id]')].map(e => e.id).sort();
  R.deadAnchors = [...document.querySelectorAll('a[href^="#"]')].map(a => a.getAttribute('href')).filter(h => h.length > 1 && !document.getElementById(h.slice(1)));
  R.imgNoAlt = [...document.querySelectorAll('img:not([alt])')].length;
  R.canvasNoLabel = [...document.querySelectorAll('canvas[role=img]')].filter(c => !c.getAttribute('aria-label')).length;
  R.hfLinks = [...document.querySelectorAll('.hf a')].map(a => a.textContent.trim());
  R.pd = (document.querySelector('.pd') || {}).textContent;
  R.hasLd = (() => { try { return JSON.parse(document.querySelector('script[type="application/ld+json"]').textContent).name; } catch (e) { return null; } })();
  R.lang = document.documentElement.lang;
  R.hreflang = [...document.querySelectorAll('link[rel=alternate]')].map(l => l.hreflang).sort();
  // overflow orizzontale: pagina e ogni elemento visibile
  R.sw = document.documentElement.scrollWidth; R.iw = innerWidth;
  R.over = all.filter(e => vis(e) && !e.closest('svg') && e.getBoundingClientRect().right > innerWidth + 1 && !e.closest('.hero-bg,.hero-cv')).slice(0, 6).map(e => e.tagName + '.' + e.className + ' ' + Math.round(e.getBoundingClientRect().right));
  return R;
}"""

CONTRAST_JS = r"""() => {
  function rgb(s) { const m = s.match(/[\d.]+/g); return m ? m.map(Number) : [0, 0, 0, 1]; }
  function lum(c) { const a = c.slice(0, 3).map(v => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }); return .2126 * a[0] + .7152 * a[1] + .0722 * a[2]; }
  function bg(e) {
    const L = [];
    while (e) { const c = rgb(getComputedStyle(e).backgroundColor); const al = c.length < 4 ? 1 : c[3]; if (al > 0) { L.push([c[0], c[1], c[2], al]); if (al >= 0.99) break; } e = e.parentElement; }
    let out = [255, 255, 255];
    for (let i = L.length - 1; i >= 0; i--) { const [r, g, b, a] = L[i]; out = [r * a + out[0] * (1 - a), g * a + out[1] * (1 - a), b * a + out[2] * (1 - a)]; }
    return out;
  }
  const low = [];
  document.querySelectorAll('body *').forEach(e => {
    const s = getComputedStyle(e), r = e.getBoundingClientRect();
    if (s.visibility === 'hidden' || s.display === 'none' || !r.width || !r.height || e.closest('[aria-hidden=true]') || e.closest('svg')) return;
    if (![...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) return;
    const fg = rgb(s.color); if (fg[3] === 0 || e.closest('.hero')) return;  // la hero si controlla sui pixel
    const b = bg(e), L1 = lum(fg), L2 = lum(b), cr = (Math.max(L1, L2) + .05) / (Math.min(L1, L2) + .05);
    const big = parseFloat(s.fontSize) >= 24 || (parseFloat(s.fontSize) >= 18.66 && parseInt(s.fontWeight) >= 700);
    if (cr < (big ? 3 : 4.5)) low.push([e.tagName + '.' + e.className, e.textContent.trim().slice(0, 28), cr.toFixed(2)]);
  });
  return low;
}"""

# contrasto del testo della hero sopra la scena: si nasconde il testo, si legge lo sfondo vero nei suoi rettangoli
HERO_BOXES = r"""() => [...document.querySelectorAll('.hero .role,.hero .abs,.hero .folio,.hero h1 span:first-child,.hero .stat')].map(e => {
  const r = e.getBoundingClientRect(), c = getComputedStyle(e).color.match(/[\d.]+/g).map(Number);
  return { cls: e.className || e.tagName, x: r.x, y: r.y, w: r.width, h: r.height, color: c };
})"""


def serve():
    class Q(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=ROOT, **k)

        def log_message(self, *a):
            pass
    srv = socketserver.TCPServer(("127.0.0.1", 0), Q)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def lum(c):
    a = [v / 255 for v in c[:3]]
    a = [v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4 for v in a]
    return .2126 * a[0] + .7152 * a[1] + .0722 * a[2]


def main():
    from playwright.sync_api import sync_playwright
    from PIL import Image
    os.makedirs(OUT, exist_ok=True)
    srv = serve()
    base = "http://127.0.0.1:%d/" % srv.server_address[1]
    rep, fail = {}, []

    def ck(name, ok, detail=""):
        rep[name] = {"ok": bool(ok), "detail": detail}
        if not ok:
            fail.append(name)
            print("FAIL", name, detail)
        else:
            print("ok  ", name, detail if len(str(detail)) < 100 else "")

    PAGES = (("it", ""), ("en", "en/"))

    # --- file: pesi, trattini, hash CSP, dipendenze esterne scritte nell'HTML
    sizes = {}
    for rel in ("index.html", "en/index.html", "css/site.css", "js/site.js", "js/hero.js", "fonts/geist-latin.woff2", "fonts/jetbrains-mono-latin.woff2"):
        data = open(os.path.join(ROOT, rel), "rb").read()
        sizes[rel] = (len(data), len(gzip.compress(data)))
    ck("peso html", max(sizes["index.html"][0], sizes["en/index.html"][0]) <= BUDGET["html"], sizes["index.html"][0])
    ck("peso css", sizes["css/site.css"][0] <= BUDGET["css"], sizes["css/site.css"][0])
    ck("peso js iniziale", sizes["js/site.js"][0] <= BUDGET["js"], sizes["js/site.js"][0])
    ck("peso font", sizes["fonts/geist-latin.woff2"][0] + sizes["fonts/jetbrains-mono-latin.woff2"][0] <= BUDGET["font"], sizes["fonts/geist-latin.woff2"][0] + sizes["fonts/jetbrains-mono-latin.woff2"][0])
    init = sizes["index.html"][1] + sizes["css/site.css"][1] + sizes["js/site.js"][1] + 2 * 0 + sizes["fonts/geist-latin.woff2"][0] + sizes["fonts/jetbrains-mono-latin.woff2"][0] + 17000
    ck("peso iniziale (gzip + font + avatar)", init <= BUDGET["initial"], init)
    ck("peso hero.js (a pagina finita)", sizes["js/hero.js"][0] <= BUDGET["hero"], "%d B, gzip %d B" % sizes["js/hero.js"])
    for rel in ("index.html", "en/index.html", "css/site.css", "js/site.js", "tools/hero.src.js"):
        t = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        ck("trattini U+2014/U+2013 in " + rel, not re.search("[%s]" % DASH, t), len(re.findall("[%s]" % DASH, t)))
    for rel in ("index.html", "en/index.html"):
        t = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        h = re.findall(r'<(?:script|link|img|source)\b[^>]*?(?:src|href)="(https?://[^"]+)"', t)
        h = [u for u in h if not re.search(r'rel="(canonical|alternate)"', t[max(0, t.find(u) - 80):t.find(u)])]
        ck("nessuna risorsa esterna nell'HTML " + rel, not h, h[:3])
        ck("CSP presente " + rel, "Content-Security-Policy" in t)
    css = open(os.path.join(ROOT, "css/site.css"), encoding="utf-8").read()
    ck("nessun url() esterno nel css", not re.search(r"url\(\s*['\"]?https?:", css))
    for f in ("fonts/OFL-geist.txt", "fonts/OFL-jetbrains-mono.txt", "js/LICENSE-three.txt"):
        ck("licenza " + f, os.path.exists(os.path.join(ROOT, f)))

    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", args=["--enable-unsafe-swiftshader"])

        def newpage(w=1440, h=900, theme="dark", rm=False, nogl=False, store=True, scheme=None):
            ctx = b.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce" if rm else "no-preference", color_scheme=scheme or "dark")
            pg = ctx.new_page()
            pg.logs, pg.reqs = [], []
            pg.on("console", lambda m: pg.logs.append(m.type + ": " + m.text) if m.type in ("error", "warning") else None)
            pg.on("pageerror", lambda e: pg.logs.append("pageerror: " + str(e)))
            pg.on("request", lambda r: pg.reqs.append(r.url))
            if store:
                pg.add_init_script("try{if(!localStorage.getItem('ai-theme'))localStorage.setItem('ai-theme','%s')}catch(e){}" % theme)
            if nogl:
                pg.add_init_script("(function(){var o=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(t){if(/webgl/.test(t))return null;return o.apply(this,arguments)}})()")
            return ctx, pg

        # --- pagine con WebGL, tema scuro e chiaro
        data = {}
        for lang, path in PAGES:
            for theme in ("dark", "light"):
                ctx, pg = newpage(theme=theme)
                pg.goto(base + path, wait_until="load")
                pg.wait_for_timeout(3500)
                R = pg.evaluate(PAGE_JS)
                gl = pg.evaluate("[document.getElementById('hero-cv').dataset.run||'', document.getElementById('top').classList.contains('gl')]")
                ext = [u for u in pg.reqs if not u.startswith(base)]
                ck("console pulita %s %s" % (lang, theme), not pg.logs, pg.logs[:3])
                ck("nessuna richiesta esterna %s %s" % (lang, theme), not ext, ext[:3])
                ck("scena WebGL attiva %s %s" % (lang, theme), gl == ["1", True], gl)
                ck("tema %s applicato %s" % (theme, lang), pg.evaluate("document.documentElement.getAttribute('data-theme')") == ("light" if theme == "light" else None))
                low = pg.evaluate(CONTRAST_JS)
                ck("contrasto testo AA %s %s" % (lang, theme), not low, low[:4])
                if theme == "dark":
                    data[lang] = R
                    ck("un solo h1 e nome %s" % lang, R["h1"] == 1 and R["h1text"] == "Adrian Ciprian Iancu", R["h1text"])
                    ck("trattini nel testo visibile %s" % lang, R["dash"] == 0, R["dash"])
                    ck("emoji %s" % lang, not R["emoji"], R["emoji"])
                    ck("frasi vietate %s" % lang, not R["banned"], R["banned"])
                    ck("nessun like nella colonna HF %s" % lang, not R["likes"], R["hfLinks"])
                    ck("ancore valide %s" % lang, not R["deadAnchors"], R["deadAnchors"])
                    ck("alt e aria-label %s" % lang, R["imgNoAlt"] == 0 and R["canvasNoLabel"] == 0)
                    ck("JSON-LD e hreflang %s" % lang, R["hasLd"] == "Adrian Ciprian Iancu" and R["hreflang"] == ["en", "it", "x-default"] and R["lang"] == lang)
                    # contatori: il testo finale e' quello dell'HTML
                    final = pg.evaluate("[...document.querySelectorAll('.stat .num')].map(e=>e.textContent)")
                    ck("contatori hero al valore finale %s" % lang, final == ["4×227k", "~100", "+51%", "+40%"], final)
                    # FlyToLLM: neuroni per punto uguale al valore scritto nel testo
                    pg.evaluate("document.getElementById('cns').scrollIntoView({block:'center'})")
                    pg.wait_for_timeout(1200)
                    pd = pg.evaluate("document.querySelector('.pd').textContent")
                    px = pg.evaluate("(()=>{const c=document.getElementById('cns'),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let n=0;for(let i=3;i<d.length;i+=4)if(d[i]>20)n++;return n})()")
                    ck("figura FlyToLLM: 260 neuroni per punto e disegno presente %s" % lang, pd == "260" and px > 5000, [pd, px])
                    # scena in pausa fuori vista, di nuovo attiva al ritorno
                    pg.evaluate("window.scrollTo(0, 3000)")
                    pg.wait_for_timeout(700)
                    off = pg.evaluate("document.getElementById('hero-cv').dataset.run")
                    pg.evaluate("window.scrollTo(0, 0)")
                    pg.wait_for_timeout(700)
                    on = pg.evaluate("document.getElementById('hero-cv').dataset.run")
                    ck("scena in pausa fuori vista, riparte al ritorno %s" % lang, (off, on) == ("0", "1"), [off, on])
                    # tilt e luce sulle schede
                    pg.evaluate("document.querySelector('#implementazioni .feat').scrollIntoView({block:'center'})")
                    pg.wait_for_timeout(1500)
                    box = pg.evaluate("(()=>{const r=document.querySelector('#implementazioni .feat').getBoundingClientRect();return [r.x+r.width*.7,r.y+r.height*.3]})()")
                    pg.mouse.move(box[0] - 40, box[1] - 10)
                    pg.mouse.move(box[0], box[1], steps=4)
                    pg.wait_for_timeout(300)
                    tf = pg.evaluate("document.querySelector('#implementazioni .feat').style.transform")
                    ck("tilt delle schede al passaggio del mouse %s" % lang, "perspective" in tf, tf)
                    # comparsa allo scroll
                    pg.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
                    pg.wait_for_timeout(1500)
                    ck("comparsa allo scroll %s" % lang, pg.evaluate("document.querySelectorAll('.rv:not(.in)').length") <= 6, pg.evaluate("document.querySelectorAll('.rv:not(.in)').length"))
                if lang == "it" and os.path.exists(AXE):
                    pg.evaluate(open(AXE, encoding="utf-8").read())
                    ax = pg.evaluate("axe.run(document,{rules:{'color-contrast':{enabled:false}}}).then(r=>r.violations.map(v=>[v.id,v.impact,v.nodes.length]))")
                    ck("axe-core %s (senza contrasto, controllato a parte)" % theme, not [v for v in ax if v[1] in ("serious", "critical")], ax)
                ctx.close()
        ck("id uguali in IT ed EN", data["it"]["ids"] == data["en"]["ids"], set(data["it"]["ids"]) ^ set(data["en"]["ids"]))

        # --- contrasto del testo della hero sopra la scena (pixel, hero con testo nascosto)
        for w, h in ((1440, 900), (390, 844)):
            ctx, pg = newpage(w, h)
            pg.goto(base, wait_until="load")
            pg.wait_for_timeout(3500)
            boxes = pg.evaluate(HERO_BOXES)
            pg.evaluate("""()=>document.querySelectorAll('.hero-in *').forEach(e=>{for(const [k,v] of [['color','transparent'],['-webkit-text-fill-color','transparent'],['border-color','transparent'],['background','none'],['box-shadow','none'],['text-shadow','none']])e.style.setProperty(k,v,'important')})""")
            pg.wait_for_timeout(300)
            im = Image.open(io.BytesIO(pg.screenshot())).convert("RGB")
            worst = []
            for bx in boxes:
                if bx["y"] + bx["h"] > h or bx["w"] < 20:
                    continue
                crop = im.crop((int(bx["x"]), int(bx["y"]), int(bx["x"] + bx["w"]), int(bx["y"] + bx["h"])))
                ls = sorted(lum(px) for px in crop.resize((max(1, crop.width // 3), max(1, crop.height // 3))).getdata())
                bgl = ls[int(len(ls) * 0.92)]  # il 92esimo percentile: qualche particella luminosa non conta, una zona chiara si
                fg = lum(bx["color"])
                cr = (max(fg, bgl) + .05) / (min(fg, bgl) + .05)
                big = "span" in str(bx["cls"]).lower() or "num" in str(bx["cls"])
                if cr < (3 if big else 4.5):
                    worst.append((bx["cls"], round(cr, 2)))
            ck("contrasto testo hero sopra la scena %dx%d" % (w, h), not worst, worst)
            ctx.close()

        # --- nessuno scroll orizzontale
        for lang, path in PAGES:
            bad = []
            for w in WIDTHS:
                ctx, pg = newpage(w, 800)
                pg.goto(base + path, wait_until="load")
                pg.wait_for_timeout(1200)
                R = pg.evaluate(PAGE_JS)
                if R["sw"] > R["iw"] or R["over"]:
                    bad.append((w, R["sw"], R["over"][:3]))
                ctx.close()
            ck("nessuno scroll orizzontale 320-1920 %s" % lang, not bad, bad)

        # --- reduced motion: scena non caricata, nessuna animazione
        for lang, path in PAGES:
            ctx, pg = newpage(rm=True)
            pg.goto(base + path, wait_until="load")
            pg.wait_for_timeout(3000)
            st = pg.evaluate("""()=>({gl:document.getElementById('top').classList.contains('gl'),run:document.getElementById('hero-cv').dataset.run||'',
              rv:document.documentElement.classList.contains('rv-on'),anims:document.getAnimations().length,hidden:[...document.querySelectorAll('.rv')].filter(e=>getComputedStyle(e).opacity!=='1').length,
              num:[...document.querySelectorAll('.stat .num')].map(e=>e.textContent)})""")
            ext = [u for u in pg.reqs if "hero.js" in u]
            ck("reduced-motion: scena non caricata %s" % lang, not st["gl"] and not st["run"] and not ext, [st["gl"], st["run"], ext])
            ck("reduced-motion: nessuna animazione, tutto visibile %s" % lang, st["anims"] == 0 and not st["rv"] and st["hidden"] == 0, st)
            ck("reduced-motion: contatori finali %s" % lang, st["num"] == ["4×227k", "~100", "+51%", "+40%"], st["num"])
            ck("reduced-motion: console %s" % lang, not pg.logs, pg.logs[:3])
            ctx.close()

        # --- senza WebGL: fallback statico, niente errori
        ctx, pg = newpage(nogl=True)
        pg.goto(base, wait_until="load")
        pg.wait_for_timeout(2500)
        st = pg.evaluate("({gl:document.getElementById('top').classList.contains('gl'),bg:getComputedStyle(document.querySelector('.hero-bg')).opacity,h1:document.querySelector('h1').getBoundingClientRect().height})")
        ck("senza WebGL: fallback statico e console pulita", not pg.logs and not st["gl"] and st["bg"] == "1" and st["h1"] > 50 and not [u for u in pg.reqs if "hero.js" in u], [pg.logs[:2], st])
        ctx.close()

        # --- tema: predefinito scuro anche con sistema chiaro, selettore persistente
        ctx, pg = newpage(store=False, scheme="light")
        pg.goto(base, wait_until="load")
        pg.wait_for_timeout(800)
        d0 = pg.evaluate("document.documentElement.getAttribute('data-theme')")
        pg.click(".bar-tools .theme button[data-set=light]")
        pg.reload(wait_until="load")
        pg.wait_for_timeout(500)
        d1 = pg.evaluate("document.documentElement.getAttribute('data-theme')")
        pg.click(".bar-tools .theme button[data-set=auto]")
        pg.reload(wait_until="load")
        pg.wait_for_timeout(500)
        d2 = pg.evaluate("document.documentElement.getAttribute('data-theme')")
        ck("tema: scuro di default, chiaro persistente, auto segue il sistema", (d0, d1, d2) == (None, "light", "light"), [d0, d1, d2])
        ctx.close()

        # --- LCP e tempi: il testo della hero e' il contenuto piu' grande, la scena arriva dopo il load
        ctx, pg = newpage()
        pg.add_init_script("window.__lcp=0;new PerformanceObserver(l=>{for(const e of l.getEntries())window.__lcp=[e.startTime,e.element?e.element.tagName+'.'+e.element.className:''];}).observe({type:'largest-contentful-paint',buffered:true})")
        pg.goto(base, wait_until="load")
        pg.wait_for_timeout(3000)
        t = pg.evaluate("""()=>({lcp:window.__lcp,load:performance.timing.loadEventEnd-performance.timing.navigationStart,
          hero:(performance.getEntriesByType('resource').find(r=>r.name.includes('hero.js'))||{}).startTime||0,
          fcp:(performance.getEntriesByType('paint').find(p=>p.name==='first-contentful-paint')||{}).startTime})""")
        ck("LCP sotto 2500 ms (localhost, CPU piena)", t["lcp"] and t["lcp"][0] < 2500, t["lcp"])
        ck("hero.js parte dopo il load", t["hero"] >= t["load"] - 5, [round(t["hero"]), t["load"]])
        rep["tempi"] = t
        ctx.close()
        b.close()

    rep["pesi"] = sizes
    with open(os.path.join(OUT, "report.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=1, ensure_ascii=False, default=list)
    srv.shutdown()
    print("\n%d controlli, %d falliti" % (sum(1 for k, v in rep.items() if isinstance(v, dict) and "ok" in v), len(fail)))
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
