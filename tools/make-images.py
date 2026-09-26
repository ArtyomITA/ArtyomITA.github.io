"""Immagini del sito: avatar, favicon, apple-touch-icon, immagini Open Graph.

  python tools/make-images.py        avatar + favicon (Pillow)
  python tools/make-images.py og     og-it.png / og-en.png (Playwright, server locale)

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

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
<style>.b{fill:#EEF0EC}.s{fill:#1B3E9A}@media (prefers-color-scheme:dark){.b{fill:#0C2136}.s{fill:#8FC6F4}}</style>
<rect class="b" width="32" height="32"/>
<rect class="s" x="8" y="18" width="3" height="8"/><rect class="s" x="14.5" y="12" width="3" height="14"/><rect class="s" x="21" y="6" width="3" height="20"/>
</svg>
"""


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
        for x, y, h in ((8, 18, 8), (14.5, 12, 14), (21, 6, 20)):
            d.rectangle([x * k, y * k, (x + 3) * k - 1, (y + h) * k - 1], fill="#1B3E9A")
        im = im.resize((size, size), Image.LANCZOS)
        im.save(os.path.join(IMG, name), optimize=True)
        print(name, os.path.getsize(os.path.join(IMG, name)), "B")


def og():
    from playwright.sync_api import sync_playwright

    class Q(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=ROOT, **k)

        def log_message(self, *a):
            pass

    srv = socketserver.TCPServer(("127.0.0.1", 0), Q)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(channel="chrome")
            for lang, path in (("it", "/"), ("en", "/en/")):
                pg = b.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1,
                                reduced_motion="reduce", color_scheme="light")
                pg.goto("http://127.0.0.1:%d%s?og" % (port, path))
                pg.evaluate("document.fonts.ready")
                pg.wait_for_timeout(400)
                raw = os.path.join(IMG, "og-%s.raw.png" % lang)
                pg.screenshot(path=raw)
                im = Image.open(raw).convert("RGB").quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
                dst = os.path.join(IMG, "og-%s.png" % lang)
                im.save(dst, optimize=True)
                os.remove(raw)
                print(os.path.basename(dst), os.path.getsize(dst), "B")
                pg.close()
            b.close()
    finally:
        srv.shutdown()


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "og":
        og()
    else:
        avatar()
        icons()
