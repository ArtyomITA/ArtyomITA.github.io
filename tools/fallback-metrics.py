"""Calcola size-adjust e override metrici per "Geist Fallback" su Arial.

Media delle larghezze di "abcdefghijklmnopqrstuvwxyz" a parita' di em: il ripiego
occupa lo stesso spazio del font vero e lo swap non sposta il testo (CLS).
Uso: python tools/fallback-metrics.py   (legge fonts/geist-latin.woff2; stampa la regola @font-face per css/site.css)
"""
import os

from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXT = "abcdefghijklmnopqrstuvwxyz"


def avg(font):
    cmap = font.getBestCmap()
    hm = font["hmtx"]
    upm = font["head"].unitsPerEm
    return sum(hm[cmap[ord(c)]][0] for c in TXT) / len(TXT) / upm, upm


a2, _ = avg(TTFont("C:/Windows/Fonts/arial.ttf"))
nr = TTFont(os.path.join(ROOT, "fonts", "geist-latin.woff2"))
a1, u1 = avg(nr)
sa = a1 / a2
hh = nr["hhea"]
print('@font-face{font-family:"Geist Fallback";src:local("Arial");'
      "size-adjust:%.2f%%;ascent-override:%.2f%%;descent-override:%.2f%%;line-gap-override:%.2f%%}"
      % (sa * 100, hh.ascent / u1 / sa * 100, -hh.descent / u1 / sa * 100, hh.lineGap / u1 / sa * 100))
