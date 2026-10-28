"""Costruisce js/hero.js: la scena three.js della hero, con three.js incluso (vendorizzato) e ridotto alle classi usate.

Sorgenti three.js 0.186.1 (MIT, pubblicata su npm il 2026-09-24) da jsDelivr, a versione fissata e con SHA-256 controllato,
scaricate una volta in ../artyomita-redesign/vendor-src. A runtime la pagina non chiama nessun CDN.

Uso:  python tools/build-hero.py        (richiede node e npx; esbuild viene scaricato da npx)
"""
import hashlib
import os
import subprocess
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "..", "artyomita-redesign", "vendor-src")
VER = "0.186.1"
FILES = {
    "three.module.js": "9052042d676cb0fdc1ddfefe193053f34b7ac0513a616fdac4535d49987812ea",
    "three.core.js": "9edde002b066a9a05676a6127f67735b62baf399bdea529f2f7e31657da769e6",
    "LICENSE-three": "8b378ebe60e2fe500158cb0ac71cb5e8b7d92953c2abcc63a0eb90499653b5bc",
}


def fetch():
    os.makedirs(SRC, exist_ok=True)
    for fn, want in FILES.items():
        p = os.path.join(SRC, fn)
        if not os.path.exists(p):
            url = "https://cdn.jsdelivr.net/npm/three@%s/%s" % (VER, "LICENSE" if fn == "LICENSE-three" else "build/" + fn)
            print("scarico", url)
            urllib.request.urlretrieve(url, p)
        got = hashlib.sha256(open(p, "rb").read()).hexdigest()
        assert got == want, "%s: SHA-256 diverso (%s)" % (fn, got)


if __name__ == "__main__":
    fetch()
    out = os.path.join(ROOT, "js", "hero.js")
    cmd = ["npx", "--yes", "esbuild@0.25.10", os.path.join(ROOT, "tools", "hero.src.js"), "--bundle", "--minify", "--format=esm", "--target=es2020",
           "--alias:three=" + os.path.join(SRC, "three.module.js"), "--legal-comments=inline", "--outfile=" + out]
    subprocess.run(cmd, check=True, shell=(os.name == "nt"))
    print(out, os.path.getsize(out), "B")
    with open(os.path.join(ROOT, "js", "LICENSE-three.txt"), "wb") as f:
        f.write(open(os.path.join(SRC, "LICENSE-three"), "rb").read())
