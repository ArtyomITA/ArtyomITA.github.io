"""Calcola size-adjust e override metrici per "Newsreader Fallback" su Georgia.

Media delle larghezze di "abcdefghijklmnopqrstuvwxyz" a parità di em: il ripiego
occupa lo stesso spazio del font vero e lo swap non sposta il testo (CLS).
Uso: python tools/fallback-metrics.py   (legge fonts/newsreader-roman-latin.woff2)
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


nr = TTFont(os.path.join(ROOT, "fonts", "newsreader-roman-latin.woff2"))
ge = TTFont(r"C:\Windows\Fonts\georgia.ttf")
a1, u1 = avg(nr)
a2, _ = avg(ge)
sa = a1 / a2
hh = nr["hhea"]
print("@font-face{font-family:\"Newsreader Fallback\";src:local(\"Georgia\");"
      "size-adjust:%.2f%%;ascent-override:%.2f%%;descent-override:%.2f%%;line-gap-override:%.2f%%}"
      % (sa * 100, hh.ascent / u1 / sa * 100, -hh.descent / u1 / sa * 100, hh.lineGap / u1 / sa * 100))
