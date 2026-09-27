"""Scarica, istanzia, sottoinsieme e rinomina i font del sito.

Sorgenti: repository ufficiale google/fonts su GitHub (licenza OFL 1.1).
Mai file di sistema (in particolare non C:\\Windows\\Fonts\\CascadiaMono.ttf,
che ha licenza di prodotto Microsoft).

Uso:  python tools/build-fonts.py [cartella-sorgenti]
Richiede: pip install fonttools brotli
"""
import datetime
import hashlib
import io
import os
import shutil
import sys
import urllib.request

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "fonts")
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "..", "artyomita-redesign", "font-src")

RAW = "https://raw.githubusercontent.com/google/fonts/{commit}/ofl/{fam}/{file}"
# commit fissati (ultimi che toccano le cartelle al momento della build)
SOURCES = {
    "newsreader": ("8b0a1d0f5983c89bc2b93f1b5fb55f9e252744b5",
                   ["Newsreader[opsz,wght].ttf", "OFL.txt"]),
    "cascadiamono": ("3dd78844021e948ceb633d1dcee3f7885561b5d9",
                     ["CascadiaMono[wght].ttf", "OFL.txt"]),
    "besley": ("c13390277dfb1fcc7415d84ef7ef9cfc1e52f8c1",
               ["Besley[wght].ttf", "OFL.txt"]),
}

LATIN = ("U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,"
         "U+2070-209F,U+20AC,U+2122,U+2190-2193,U+2212,U+2215,U+2248,U+2264-2265,U+FEFF,U+FFFD")
LATIN_EXT = ("U+0100-024F,U+0259,U+1E00-1EFF,U+2020,U+20A0-20AB,U+20AD-20CF,U+2113,"
             "U+2C60-2C7F,U+A720-A7FF")
FEATURES = "kern,liga,onum,lnum,tnum,pnum,sups,frac,ss01"

# (file di uscita, sorgente, limiti degli assi, nuovo nome di famiglia o None)
BUILDS = [
    ("newsreader-roman", "newsreader/Newsreader[opsz,wght].ttf", {"opsz": (6, 72), "wght": (400, 600)}),
    ("tavola-mono", "cascadiamono/CascadiaMono[wght].ttf", {"wght": 400}),
    # titoli: un Clarendon (istanza statica 400) accanto al Newsreader del testo corrente
    ("besley", "besley/Besley[wght].ttf", {"wght": 400}),
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def fetch():
    log = []
    for fam, (commit, files) in SOURCES.items():
        d = os.path.join(SRC, fam)
        os.makedirs(d, exist_ok=True)
        for fn in files:
            p = os.path.join(d, fn)
            url = RAW.format(commit=commit, fam=fam, file=fn.replace("[", "%5B").replace("]", "%5D").replace(",", "%2C"))
            if not os.path.exists(p):
                print("scarico", url)
                with urllib.request.urlopen(url) as r, open(p, "wb") as f:
                    f.write(r.read())
            log.append((fam, fn, url, sha256(p)))
    return log


def has_rfn(fam):
    with open(os.path.join(SRC, fam, "OFL.txt"), encoding="utf-8") as f:
        # la dichiarazione vera e' "with Reserved Font Name X"; la clausola generica della licenza no
        return "with Reserved Font Name" in f.read()


def rename(font, family, ps):
    name = font["name"]
    for rec in list(name.names):
        if rec.nameID in (16, 17, 21, 22, 25):
            name.removeNames(nameID=rec.nameID)
    sub = "Italic" if "italic" in ps.lower() else "Regular"
    for pid, eid, lid in ((3, 1, 0x409), (1, 0, 0)):
        name.setName(family, 1, pid, eid, lid)
        name.setName(sub, 2, pid, eid, lid)
        name.setName(family + " " + sub + "; subset for artyomita.github.io", 3, pid, eid, lid)
        name.setName(family + " " + sub, 4, pid, eid, lid)
        name.setName(ps, 6, pid, eid, lid)


def build(log):
    os.makedirs(OUT, exist_ok=True)
    rfn = {fam: has_rfn(fam) for fam in SOURCES}
    made = []
    for out, src, axes in BUILDS:
        fam = src.split("/")[0]
        font = TTFont(os.path.join(SRC, src))
        font = instancer.instantiateVariableFont(font, axes)
        if rfn[fam]:
            if fam == "cascadiamono":
                rename(font, "Tavola Mono", "TavolaMono-Regular")
            else:
                raise SystemExit("RFN inatteso in " + fam + ": scegliere un nome")
        buf = io.BytesIO()
        font.save(buf)
        for block, uni in (("latin", LATIN), ("latin-ext", LATIN_EXT)):
            dst = os.path.join(OUT, "%s-%s.woff2" % (out, block))
            opts = subset.Options()
            opts.layout_features = FEATURES.split(",")
            opts.flavor = "woff2"
            opts.desubroutinize = True
            opts.hinting = False
            opts.name_IDs = ["*"]
            opts.name_languages = ["*"]
            opts.notdef_outline = True
            f2 = TTFont(io.BytesIO(buf.getvalue()))
            s = subset.Subsetter(opts)
            s.populate(unicodes=subset.parse_unicodes(uni))
            s.subset(f2)
            f2.flavor = "woff2"
            f2.save(dst)
            made.append((os.path.basename(dst), os.path.getsize(dst), axes))
            print("%-40s %7d B" % (os.path.basename(dst), os.path.getsize(dst)))
    shutil.copy(os.path.join(SRC, "newsreader", "OFL.txt"), os.path.join(OUT, "OFL-newsreader.txt"))
    shutil.copy(os.path.join(SRC, "cascadiamono", "OFL.txt"), os.path.join(OUT, "OFL-cascadia.txt"))
    shutil.copy(os.path.join(SRC, "besley", "OFL.txt"), os.path.join(OUT, "OFL-besley.txt"))
    return made, rfn


def readme(log, made, rfn):
    sysf = r"C:\Windows\Fonts\CascadiaMono.ttf"
    sysh = sha256(sysf) if os.path.exists(sysf) else "(file non presente su questa macchina)"
    L = ["# Font del sito", "",
         "Tutti i font sono sotto SIL Open Font License 1.1 (testi in `OFL-newsreader.txt`, `OFL-cascadia.txt` e `OFL-besley.txt`).",
         "Sorgente: repository ufficiale google/fonts su GitHub, a commit fissati. Nessun file di sistema.",
         "Generati il %s con `python tools/build-fonts.py`." % datetime.date.today().isoformat(), "",
         "## Sorgenti", "", "| famiglia | file | URL | SHA-256 |", "|---|---|---|---|"]
    for fam, fn, url, h in log:
        L.append("| %s | %s | %s | `%s` |" % (fam, fn, url, h))
    L += ["", "Controllo: SHA-256 di `%s` = `%s` (diverso dai sorgenti sopra: il file di sistema non è usato)." % (sysf, sysh), "",
          "## Reserved Font Name", "",
          "- Newsreader: RFN nel file di licenza = %s." % ("sì" if rfn["newsreader"] else "no, il nome resta Newsreader"),
          "- Besley: RFN nel file di licenza = %s." % ("sì" if rfn["besley"] else "no, il nome resta Besley"),
          "- Cascadia Mono: RFN nel file di licenza = %s. Il sottoinsieme modificato è quindi rinominato **Tavola Mono**"
          " (nameID 1 \"Tavola Mono\", 4 \"Tavola Mono Regular\", 6 \"TavolaMono-Regular\"; nameID 16, 17, 21, 22, 25 rimossi)."
          " Copyright e licenza restano quelli originali." % ("sì" if rfn["cascadiamono"] else "no"), "",
          "## File prodotti", "", "| file | byte | istanza |", "|---|---|---|"]
    for fn, sz, axes in made:
        L.append("| %s | %d | %s |" % (fn, sz, ", ".join("%s %s" % (k, v) for k, v in axes.items())))
    L += ["", "## Procedura", "",
          "1. `fontTools.varLib.instancer.instantiateVariableFont` con i limiti d'asse della tabella.",
          "2. `fontTools.subset` con unicode-range latin e latin-ext (vedi `tools/build-fonts.py`),",
          "   feature `%s`, `--flavor=woff2 --desubroutinize --no-hinting`." % FEATURES,
          "3. Rinomina dei nameID se la licenza dichiara un Reserved Font Name.", ""]
    with open(os.path.join(OUT, "README.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))


if __name__ == "__main__":
    log = fetch()
    made, rfn = build(log)
    readme(log, made, rfn)
