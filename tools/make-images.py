"""Immagini del sito: avatar, favicon, apple-touch-icon, immagini Open Graph.

  python tools/make-images.py        avatar + favicon (Pillow)
  python tools/make-images.py og     og-it.png / og-en.png (Playwright, server locale): card composta,
                                     da rifare dopo ogni build (check.py confronta le date)

Sorgente dell'avatar: https://github.com/ArtyomITA.png?size=460, scaricato una volta
in ../artyomita-redesign/font-src/avatar-github.png. A runtime la pagina non chiama github.com.
"""
import http.server
import os
import socketserver
import sys
import threading
import urllib.request

from PIL import Image, ImageDraw, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "img")
SRC = os.path.join(ROOT, "..", "artyomita-redesign", "font-src", "avatar-github.png")

# favicon: cinque tratti di spike irregolari, come una colonna del raster di Fig. 1 (x, y, altezza su 32 px)
TICKS = ((4, 9, 10), (9.5, 15, 12), (15, 5, 9), (20.5, 12, 15), (26, 8, 9))
FAVICON = ("""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
<style>.b{fill:#EEF0EC}.s{fill:#1B3E9A}@media (prefers-color-scheme:dark){.b{fill:#0C2136}.s{fill:#8FC6F4}}</style>
<rect class="b" width="32" height="32"/>
"""
           + "".join('<rect class="s" x="%g" y="%g" width="2.5" height="%g"/>' % t for t in TICKS) + "\n</svg>\n")


def avatar():
    if not os.path.exists(SRC):
        os.makedirs(os.path.dirname(SRC), exist_ok=True)
        urllib.request.urlretrieve("https://github.com/ArtyomITA.png?size=460", SRC)
    im = Image.open(SRC).convert("L")
    im = ImageOps.autocontrast(im, cutoff=1)
    im = im.resize((192, 192), Image.LANCZOS)
    dst = os.path.join(IMG, "avatar-192.webp")
    im.save(dst, "WEBP", quality=78, method=6)
    print("avatar", os.path.getsize(dst), "B")


def icons():
    with open(os.path.join(IMG, "favicon.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(FAVICON)
    for size, name in ((32, "favicon-32.png"), (180, "apple-touch-icon.png")):
        k = 8  # supercampionamento
        im = Image.new("RGB", (32 * k, 32 * k), "#EEF0EC")
        d = ImageDraw.Draw(im)
        for x, y, h in TICKS:
            d.rectangle([x * k, y * k, (x + 2.5) * k - 1, (y + h) * k - 1], fill="#1B3E9A")
        im = im.resize((size, size), Image.LANCZOS)
        im.save(os.path.join(IMG, name), optimize=True)
        print(name, os.path.getsize(os.path.join(IMG, name)), "B")


OG_HTML = """<!DOCTYPE html><html lang="{lang}"><head><meta charset="utf-8"><link rel="stylesheet" href="css/site.css"><style>
html,body{{margin:0;width:1200px;height:630px;overflow:hidden;background:#EEF0EC;color:#15181C}}
.card{{position:absolute;inset:0;padding:40px 64px 0;box-sizing:border-box}}
.top{{display:flex;justify-content:space-between;align-items:baseline;border-top:3px solid #15181C;padding-top:12px;font:400 22px/1.3 "Tavola Mono",monospace;color:#5F6770}}
.nm{{font:400 150px/.9 "Besley",Georgia,serif;letter-spacing:-.035em;margin:34px 0 0;padding-bottom:8px;border-bottom:1px solid #15181C;white-space:nowrap}}
.role{{font:400 29px/1.35 "Newsreader",Georgia,serif;margin:18px 0 0;max-width:1060px}}
.role b{{font-weight:600}}
.ras{{position:absolute;left:64px;right:64px;bottom:0;height:{rh}px;background:url({img}) left bottom/100% auto no-repeat}}
.cap{{position:absolute;right:64px;bottom:{cb}px;font:400 17px/1 "Newsreader",Georgia,serif;color:#4B535C;background:#EEF0EC;padding:4px 0 4px 10px}}
</style></head><body><div class="card"><div class="top"><span>artyomita.github.io</span><span>{folio}</span></div>
<div class="nm">Adrian Iancu</div><p class="role">{role}</p></div><div class="ras"></div><p class="cap">{cap}</p></body></html>"""
OG_TXT = {"it": ("aggiornata settembre 2026", "Fig. 1 · raster di neuroni leaky integrate-and-fire simulati nella pagina"),
          "en": ("updated September 2026", "Fig. 1 · raster of leaky integrate-and-fire neurons simulated in the page")}


def role():
    import importlib.util
    spec = importlib.util.spec_from_file_location("bp", os.path.join(ROOT, "tools", "build-pages.py"))
    bp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bp)
    return bp.ROLE_H


def og():
    """Card Open Graph composta (non uno screenshot dell'interfaccia): nome in Besley, riga di ruolo,
    una fetta del raster di Fig. 1 presa dalla pagina vera (movimento ridotto, tema carta)."""
    import base64
    import io
    from playwright.sync_api import sync_playwright

    class Q(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=ROOT, **k)

        def log_message(self, *a):
            pass

    srv = socketserver.TCPServer(("127.0.0.1", 0), Q)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    tmp = os.path.join(ROOT, "_og.html")
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(channel="chrome")
            for lang, path in (("it", "/"), ("en", "/en/")):
                # 1. fetta del raster dalla pagina vera
                pg = b.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=2, reduced_motion="reduce", color_scheme="light")
                pg.goto("http://127.0.0.1:%d%s" % (port, path))
                pg.evaluate("document.fonts.ready")
                pg.wait_for_timeout(400)
                shot = Image.open(io.BytesIO(pg.locator("#raster").screenshot())).convert("RGB")
                pg.close()
                w, h = shot.size
                # via le etichette di riga a sinistra, la barra dei 100 ms in basso: resta il raster con il tasso
                sl = shot.crop((int(w * 0.13), int(h * 0.22), w, int(h * 0.93)))
                sl = sl.resize((1072, int(1072 * sl.size[1] / sl.size[0])), Image.LANCZOS)
                buf = io.BytesIO()
                sl.save(buf, "PNG")
                rh = min(250, sl.size[1])
                html = OG_HTML.format(lang=lang, folio=OG_TXT[lang][0], cap=OG_TXT[lang][1], role=role(), rh=rh, cb=rh + 6,
                                      img="data:image/png;base64," + base64.b64encode(buf.getvalue()).decode())
                with open(tmp, "w", encoding="utf-8") as f:
                    f.write(html)
                # 2. la card
                pg = b.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
                pg.goto("http://127.0.0.1:%d/_og.html" % port)
                pg.evaluate("document.fonts.ready")
                pg.wait_for_timeout(300)
                raw = os.path.join(IMG, "og-%s.raw.png" % lang)
                pg.screenshot(path=raw)
                pg.close()
                im = Image.open(raw).convert("RGB").quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
                dst = os.path.join(IMG, "og-%s.png" % lang)
                im.save(dst, optimize=True)
                os.remove(raw)
                print(os.path.basename(dst), os.path.getsize(dst), "B")
            b.close()
    finally:
        srv.shutdown()
        if os.path.exists(tmp):
            os.remove(tmp)


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "og":
        og()
    else:
        avatar()
        icons()
