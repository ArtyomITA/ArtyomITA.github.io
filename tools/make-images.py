"""Immagini del sito: avatar, favicon, apple-touch-icon, immagini Open Graph.

  python tools/make-images.py        avatar + favicon (Pillow)
  python tools/make-images.py og     og-it.png / og-en.png (Playwright, server locale): card composta,
                                     da rifare dopo una modifica ai numeri o ai testi della hero

Sorgente dell'avatar: https://github.com/ArtyomITA.png?size=460, scaricato una volta
in ../artyomita-redesign/font-src/avatar-github.png. A runtime la pagina non chiama github.com.
"""
import http.server
import importlib.util
import os
import random
import re
import socketserver
import sys
import threading
import urllib.request

from PIL import Image, ImageDraw, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "img")
SRC = os.path.join(ROOT, "..", "artyomita-redesign", "font-src", "avatar-github.png")

# favicon: una griglia 3x3 di "SM" su fondo grafite, alcune accese di menta, una corallo (come la scena della hero)
TILES = ((0, 0, "d"), (1, 0, "m"), (2, 0, "d"), (0, 1, "m"), (1, 1, "m"), (2, 1, "c"), (0, 2, "d"), (1, 2, "d"), (2, 2, "m"))
COL = {"d": "#1D4B3F", "m": "#2EF2B0", "c": "#FF6A57"}
FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">\n<rect width="32" height="32" rx="7" fill="#0D0F13"/>\n'
           + "".join('<rect x="%g" y="%g" width="6.4" height="6.4" rx="1.2" fill="%s"/>\n' % (5 + x * 8.4, 5 + y * 8.4, COL[k]) for x, y, k in TILES) + "</svg>\n")


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
        im = Image.new("RGB", (32 * k, 32 * k), "#0D0F13")
        d = ImageDraw.Draw(im)
        for x, y, kind in TILES:
            x0, y0 = (5 + x * 8.4) * k, (5 + y * 8.4) * k
            d.rounded_rectangle([x0, y0, x0 + 6.4 * k, y0 + 6.4 * k], radius=1.2 * k, fill=COL[kind])
        im = im.resize((size, size), Image.LANCZOS)
        im.save(os.path.join(IMG, name), optimize=True)
        print(name, os.path.getsize(os.path.join(IMG, name)), "B")


OG_HTML = """<!DOCTYPE html><html lang="{lang}"><head><meta charset="utf-8"><style>
@font-face{{font-family:Geist;font-weight:400 700;src:url(fonts/geist-latin.woff2) format("woff2")}}
@font-face{{font-family:"JetBrains Mono";font-weight:400 600;src:url(fonts/jetbrains-mono-latin.woff2) format("woff2")}}
html,body{{margin:0;width:1200px;height:630px;overflow:hidden;background:#0d0f13;color:#eceff4;font-family:Geist,sans-serif;font-feature-settings:"ss05"}}
.bg{{position:absolute;inset:0;background:radial-gradient(55% 60% at 80% 62%,rgba(46,242,176,.2),transparent 70%),radial-gradient(35% 40% at 96% 18%,rgba(255,106,87,.14),transparent 70%)}}
.die{{position:absolute;right:-170px;top:70px;width:760px;height:560px;transform:perspective(760px) rotateX(58deg) rotateZ(-14deg);transform-origin:50% 55%;display:grid;grid-template-columns:repeat(11,1fr);gap:16px;
  -webkit-mask-image:radial-gradient(closest-side,#000 40%,transparent 100%);mask-image:radial-gradient(closest-side,#000 40%,transparent 100%)}}
.die i{{background:rgba(46,242,176,.08);border:1.5px solid rgba(46,242,176,.38);border-radius:4px}}
.die i.on{{background:rgba(46,242,176,.5);box-shadow:0 0 30px rgba(46,242,176,.7)}}
.die i.cr{{background:rgba(255,106,87,.55);border-color:#ff6a57;box-shadow:0 0 30px rgba(255,106,87,.6)}}
.dot{{position:absolute;width:5px;height:5px;border-radius:50%;background:#2ef2b0;box-shadow:0 0 12px #2ef2b0}}
.card{{position:absolute;inset:0;padding:56px 72px;box-sizing:border-box}}
.pill{{display:inline-block;padding:9px 18px;border-radius:99px;border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.04);font:500 20px/1 "JetBrains Mono",monospace;color:#aeb7c4}}
.nm{{margin:34px 0 0;font-weight:640;font-size:106px;line-height:.95;letter-spacing:-.05em}}
.nm span{{display:block;background:linear-gradient(100deg,#2ef2b0 10%,#b8ffe6 90%);-webkit-background-clip:text;color:transparent}}
.role{{margin:24px 0 0;font-size:29px;line-height:1.35;max-width:760px;color:#eceff4}}
.role b{{color:#2ef2b0;font-weight:600}}
.st{{position:absolute;left:72px;bottom:44px;display:flex;gap:44px}}
.st div{{font:500 46px/1 "JetBrains Mono",monospace;letter-spacing:-.05em}}
.st small{{display:block;margin-top:10px;font:400 17px/1.3 Geist,sans-serif;letter-spacing:0;color:#8b95a5;max-width:210px}}
</style></head><body><div class="bg"></div><div class="die">{cells}</div>{dots}
<div class="card"><span class="pill">artyomita.github.io</span><div class="nm">Adrian Ciprian<span>Iancu</span></div><p class="role">{role}</p></div>
<div class="st">{stats}</div></body></html>"""


def pages_module():
    sys.dont_write_bytecode = True  # niente __pycache__ nel repository del sito
    spec = importlib.util.spec_from_file_location("bp", os.path.join(ROOT, "tools", "build-pages.py"))
    bp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bp)
    return bp


def og():
    """Card Open Graph composta (non uno screenshot dell'interfaccia): nome, ruolo, tre numeri e la griglia di SM della hero,
    con gli stessi font e colori del sito."""
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
    r = random.Random(27721)
    cells = "".join('<i class="%s"></i>' % ("cr" if r.random() > 0.96 else "on" if r.random() > 0.78 else "") for _ in range(11 * 8))
    dots = "".join('<span class="dot" style="left:%dpx;top:%dpx;opacity:%.2f"></span>' % (r.randint(520, 1180), r.randint(120, 560), r.uniform(.3, 1)) for _ in range(40))
    bp = pages_module()
    plain = lambda x: re.sub(r"<[^>]+>", "", x).replace("&nbsp;", " ")
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(channel="chrome")
            for lang in ("it", "en"):
                t = bp.T[lang]
                st = "".join("<div>%s<small>%s</small></div>" % (plain(n), plain(lb)) for n, lb, _, _ in (t["stats"][0], t["stats"][2], t["stats"][3]))
                with open(tmp, "w", encoding="utf-8") as f:
                    f.write(OG_HTML.format(lang=lang, role=t["role"], cells=cells, dots=dots, stats=st))
                pg = b.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=2)
                pg.goto("http://127.0.0.1:%d/_og.html" % port)
                pg.evaluate("document.fonts.ready")
                pg.wait_for_timeout(400)
                raw = os.path.join(IMG, "og-%s.raw.png" % lang)
                pg.screenshot(path=raw)
                pg.close()
                dst = os.path.join(IMG, "og-%s.png" % lang)
                Image.open(raw).convert("RGB").resize((1200, 630), Image.LANCZOS).save(dst, optimize=True)
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
