"""Numeri dei modelli Hugging Face per la colonna a sinistra (IT ed EN).

  python tools/hf-models.py            legge l'API, aggiorna tools/hf-models.json e riscrive il blocco in index.html e en/index.html
  python tools/hf-models.py --dry      stampa i numeri senza scrivere niente

La pagina non chiama Hugging Face: i numeri sono scritti nell'HTML, tra i commenti <!--hf--> e <!--/hf-->.
Rilanciarlo prima di pubblicare. tools/build-pages.py legge lo stesso file JSON, quindi una ricostruzione non perde i numeri.
Il campo `downloads` dell'API sono i download degli ultimi 30 giorni.
"""
import datetime
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = os.path.join(ROOT, "tools", "hf-models.json")
AUTHOR = "adriandj3"
API = "https://huggingface.co/api/models?author=" + AUTHOR
# nome breve per ogni modello; uno nuovo senza voce qui compare con l'id intero e un avviso
SHORT = {
    "Swift-1.5-Qwen3.8-Flash-Next-MTP-for-GGUF-and-NVFP4": "Swift 1.5 MTP",
    "MiniCPM5-2B-DSpark-FRSpec32k-GGUF": "MiniCPM5-2B DSpark FR-Spec 32k",
    "MiniCPM5-2B-pjev-LoRA": "MiniCPM5-2B pjev LoRA",
    "TernaryPilot-v1-Computer-Browser-Use-LoRA": "TernaryPilot v1 LoRA",
    "LFM2.5-to-Llama8B-LLM2Vec-Kimodo": "LFM2.5 to LLM2Vec Kimodo",
}
TXT = {
    "it": dict(model="modello", dl="download", total="totale", note="ultimi 30 giorni, aggiornato al %s", like="%d like", date="%d/%m/%Y", sep="."),
    "en": dict(model="model", dl="downloads", total="total", note="last 30 days, updated %s", like="%d like", date="%d %b %Y", sep=","),
}


def fetch():
    with urllib.request.urlopen(API, timeout=30) as r:
        data = json.load(r)
    return [{"id": m["id"], "downloads": int(m.get("downloads") or 0), "likes": int(m.get("likes") or 0)} for m in data]


def render(lang, snap):
    t = TXT[lang]
    d = datetime.date.fromisoformat(snap["date"])
    num = lambda n: format(n, ",").replace(",", t["sep"])
    models = sorted(snap["models"], key=lambda m: (-m["downloads"], m["id"]))
    rows = []
    for m in models:
        key = m["id"].split("/", 1)[1]
        if key not in SHORT:
            print("avviso: nessun nome breve per", m["id"], "in SHORT", file=sys.stderr)
        like = "" if not m["likes"] else '<span class="lk">%s</span>' % ((t["like"] % m["likes"]) + ("s" if lang == "en" and m["likes"] != 1 else ""))
        name = re.sub(r"\S+-\S+", lambda x: '<span class="nb">%s</span>' % x.group(0), SHORT.get(key, key))  # niente a capo sul trattino
        rows.append('<tr><td><a href="https://huggingface.co/%s">%s</a>%s</td><td class="m">%s</td></tr>' % (m["id"], name, like, num(m["downloads"])))
    return ('<!--hf--><table class="hft"><thead><tr><th scope="col">%s</th><th scope="col">%s</th></tr></thead><tbody>%s</tbody>'
            '<tfoot><tr><th scope="row">%s</th><td class="m">%s</td></tr></tfoot></table><p class="hfd">%s</p><!--/hf-->'
            % (t["model"], t["dl"], "".join(rows), t["total"], num(sum(m["downloads"] for m in models)), t["note"] % d.strftime(t["date"])))


def load():
    with open(SNAP, encoding="utf-8") as f:
        return json.load(f)


def patch(path, block):
    with open(path, encoding="utf-8") as f:
        html = f.read()
    new, n = re.subn(r"<!--hf-->.*?<!--/hf-->", lambda _: block, html, flags=re.S)
    assert n == 1, "marcatori <!--hf--> non trovati in " + path
    if new != html:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(new)
    return new != html


if __name__ == "__main__":
    snap = {"date": datetime.date.today().isoformat(), "models": fetch()}
    assert snap["models"], "l'API non ha restituito modelli"
    for m in sorted(snap["models"], key=lambda m: -m["downloads"]):
        print("%6d download  %2d like  %s" % (m["downloads"], m["likes"], m["id"]))
    print("totale", sum(m["downloads"] for m in snap["models"]))
    if "--dry" not in sys.argv:
        with open(SNAP, "w", encoding="utf-8", newline="\n") as f:
            json.dump(snap, f, indent=1)
            f.write("\n")
        for lang, rel in (("it", "index.html"), ("en", os.path.join("en", "index.html"))):
            print(rel, "aggiornato" if patch(os.path.join(ROOT, rel), render(lang, snap)) else "invariato")
