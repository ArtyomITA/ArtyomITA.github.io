"""Genera index.html (italiano) e en/index.html (inglese) dallo stesso modello.

Stessa struttura e stessi id nelle due pagine; cambiano solo i testi.
Dopo la scrittura, con --bake, apre le pagine in Playwright (movimento ridotto) e
incolla nell'HTML le figure statiche (kt, err, fence, lots) al fotogramma finale, cosi' si leggono anche senza JS.
I numeri dei modelli Hugging Face (colonna a sinistra) vengono da tools/hf-models.json: aggiornarli con tools/hf-models.py.

Uso:  python tools/build-pages.py [--bake]
"""
import base64
import hashlib
import http.server
import importlib.util
import os
import re
import socketserver
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://artyomita.github.io/"
GH = "https://github.com/ArtyomITA/"
ORG = "https://github.com/Partido-De-What/"
PR = "https://github.com/ggml-org/llama.cpp/pull/27721"
PR_SD = "https://github.com/leejet/stable-diffusion.cpp/pull/2202"
PR_PRISM = "https://github.com/PrismML-Eng/llama.cpp/pull/368"
PR_VLLM = "https://github.com/vllm-project/vllm/pull/58863"
LI = "https://www.linkedin.com/in/adrian-ciprian-iancu-a2a477391"
HF = "https://huggingface.co/adriandj3"
IG = "https://www.instagram.com/artyomita"
NAME = "Adrian Ciprian Iancu"
BW = GH + "blackwell6000-qwen3.8-flash-next"

BOOT = "(function(d){d.className='js';try{var t=localStorage.getItem('ai-theme');if(t==='light'||t==='dark')d.setAttribute('data-theme',t)}catch(e){}})(document.documentElement);"
BOOT_HASH = base64.b64encode(hashlib.sha256(BOOT.encode("utf-8")).digest()).decode()
CSP = ("default-src 'self'; script-src 'self' 'sha256-%s'; style-src 'self'; img-src 'self' data:; "
       "font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'") % BOOT_HASH

TICKS = '<div class="rule" aria-hidden="true">' + "<i></i>" * 12 + "</div>"
# filetto semplice per le sezioni senza progetto guida (RL, indice, nota)
RULE = '<div class="rule plain" aria-hidden="true"></div>'


def _hf():
    sys.dont_write_bytecode = True  # niente __pycache__ nel repository del sito
    spec = importlib.util.spec_from_file_location("hfm", os.path.join(ROOT, "tools", "hf-models.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


hfm = _hf()

# numero mostrato di ogni figura, nell'ordine in cui compaiono nella pagina; gli id restano quelli del codice
FIGN = {"fig3": 1, "fig4": 2, "fig5": 3, "fig1": 4, "fig2": 5, "fig6": 6}


def fr(fid, cap=False):
    return '<a href="#%s">%s&nbsp;%d</a>' % (fid, "Fig." if cap else "fig.", FIGN[fid])


def m(x):
    return '<span class="m">%s</span>' % x


SECTIONS = ("contributi", "implementazioni", "ricerca", "strumenti", "sperimentali")


def nav_items(t):
    return [("#" + s, t["nav"][i]) for i, s in enumerate(SECTIONS)] + [("#indice", t["nav"][5])]


# linguaggio principale e sua quota in byte, da GET /repos/<owner>/<repo>/languages (28 ottobre 2026)
LANGS = {"blackwell6000-qwen3.8-flash-next": ("Cuda", 44), "minicpm5-kernel-pascal": ("Python", 65), "bonsai2-ternary-pascal": ("Python", 100),
         "llm2vec-8gb-offload-lossless-batching": ("Python", 100), "lfm-to-kimodo": ("Python", 88), "bonsai-webgpu-tiled-vae-fix": ("JavaScript", 82),
         "hildanext": ("Python", 73), "claude-plugins": ("JavaScript", 48), "vergilius": ("Python", 93), "stt-whisper-pad": ("Python", 94),
         "flytollm": ("Python", 100), "fantaoracle": ("Python", 87), "fantacalcio-advisor": ("TypeScript", 79), "K-Forecast": ("Python", 96),
         "sp500-predictability-lab": ("TypeScript", 57), "storico": ("Python", 99), "supermario-1-1-rl": ("TypeScript", 99),
         "idle-isekai-trials": ("JavaScript", 99)}


def lsh(name):
    if name not in LANGS:
        return ""
    lg, pc = LANGS[name]
    return ('<span class="lsh"><svg aria-hidden="true" width="48" height="4"><rect class="b0" width="48" height="4"/>'
            '<rect class="b1" width="%s" height="4"/></svg>%s %d%%</span>') % (round(48 * pc / 100.0, 1), lg, pc)


# neuroni per punto in Fig. 5: 166.700 diviso i punti generati da js/site.js (seme 166700).
# Il bake lo ricontrolla contro il valore calcolato a runtime.
PD = {"it": "260", "en": "260"}

T = {}

T["it"] = dict(
    lang="it", ogloc="it_IT", ogalt="en_GB", canon=SITE, P="", og="img/og-it.png",
    desc="AI engineer: inferenza LLM su GPU consumer e datacenter, kernel CUDA, contributi upstream a llama.cpp, stable-diffusion.cpp e vLLM, ricerca sul comportamento dei modelli open-weight. Tutto open source.",
    ogimgalt="Il nome Adrian Ciprian Iancu in grande, la riga del ruolo e lo schema dei CUDA Graphs su Pascal della figura 1.",
    skip="Vai al contenuto", navlabel="Sezioni", toc="Indice", langlabel="Lingua", themelabel="Tema",
    th=("chiaro", "scuro", "auto"), thtitle=("Tema chiaro (carta)", "Tema scuro (cianotipia)", "Tema auto (come il sistema)"),
    nav=["contributi", "implementazioni", "ricerca", "strumenti e agenti", "progetti sperimentali", "indice"], navnote="nota sulle figure",
    folio="aggiornata ottobre 2026",
    role="<b>AI engineer</b>: inferenza LLM su GPU consumer e datacenter, kernel CUDA, contributi open&nbsp;source.",
    abs='<span class="runin">Sommario.</span> Faccio <b>inferenza di LLM</b>: <b>kernel CUDA</b> e patch minime per far girare i modelli su GPU consumer e su una sola Blackwell, con ogni modifica verificata contro l\'output di riferimento. Faccio anche <b>ricerca applicata</b> sul comportamento dei modelli open-weight. Tutto open&nbsp;source: due mie PR sono state integrate, una è aperta in llama.cpp e un mio fix è stato adottato in vLLM.',
    kw='Inferenza LLM, kernel CUDA, CUDA Graphs; GPU Pascal (sm_61) e Blackwell; decoding speculativo, quantizzazione (NVFP4, pesi ternari); llama.cpp, vLLM, GGML; sicurezza dei modelli open-weight; sistemi multi-agente; ML applicato.',
    tcap="<b>Tab. 1.</b> Numeri di riferimento, ciascuno con la sua fonte.", thq="grandezza", thv="valore", ths="fonte",
    rows=[("Progetti upstream con una mia patch", "4 progetti|2 PR integrate", '<a href="#contributi">Contributi upstream</a>'),
          ("Qwen3.8 Flash-Next su una GPU", "4 utenti × 227k token|~100 tok/s per utente", '<a href="%s">repo blackwell6000</a>' % BW),
          ("Speedup MoE in llama.cpp su Pascal", "+40%", '<a href="%s">PR upstream #27721, aperta</a>' % PR),
          ("Ternary Bonsai 2 9B su GTX&nbsp;1080", "+51% in decode", '<a href="%sbonsai2-ternary-pascal">repo bonsai2</a>' % GH),
          ("MiniCPM5-2B su GTX&nbsp;1080", "da 33 a 83 tok/s", '<a href="%sminicpm5-kernel-pascal">repo minicpm5</a>' % GH)],
    # Contributi upstream
    kc="Contributi upstream", hc="Quattro patch in quattro progetti",
    leadc="Patch piccole inviate ai repository originali. Due sono integrate, una è aperta e un mio commit è stato adottato in una PR di vLLM.",
    pcap="<b>Tab. 2.</b> Contributi upstream, con lo stato verificato il 28 ottobre 2026.", pth=("progetto", "patch", "stato"),
    prows=[("leejet/stable-diffusion.cpp", '<a href="%s">PR #2202</a>: fix, ignora l\'alpha dei metadati nei LoRA con baked_scale.' % PR_SD, "integrata il 24/10/2026"),
           ("PrismML-Eng/llama.cpp", '<a href="%s">PR #368</a>: Pascal (sm_61), mat-vec PQ2_0 per 1-4 colonne, ' % PR_PRISM + m("+17%") + " su Ternary-Bonsai-2-9B con output identico bit per bit.", "integrata il 19/10/2026"),
           ("ggml-org/llama.cpp", '<a href="%s">PR #27721</a>: CUDA Graphs su Pascal (sm_61), ' % PR + m("+40%") + " sui modelli MoE, " + m("+7%") + " sui modelli densi, nessuna regressione.", "aperta dal 25/08/2026"),
           ("vllm-project/vllm", '<a href="%s">PR #58863</a>: il commit esatto del replay GDN di RecoverSSM, proposto da me e adottato nella PR (commit 514102a).' % PR_VLLM, "adottato, PR ancora aperta")],
    cap3="<b>Fig. 1.</b> CUDA Graphs su sm_61 in llama.cpp (PR #27721). Schema, non traccia di profilazione: stessi kernel, un solo lancio del grafo al posto di uno per kernel. Scorrendo, la riga del grafo si accorcia fino a 1/1,40 della prima sui modelli MoE (+40% misurato) e a 1/1,07 sui densi (+7%).",
    # Implementazioni
    ki="Implementazioni", hi="Dalla GTX 1080 alla RTX PRO 6000",
    leadi="Kernel e configurazioni di inferenza per una GTX&nbsp;1080 e per una RTX PRO 6000 Blackwell. Ogni modifica è confrontata con l'output di riferimento e ogni numero ha il suo benchmark riproducibile.",
    dlbw="ottobre 2026",
    bw="Qwen3.8 Flash-Next e il fine-tune Swift 1.5 in NVFP4 su una sola RTX PRO 6000 Blackwell con vLLM: " + m("4 utenti") + " con " + m("227k") + " token di contesto ciascuno, circa " + m("100&nbsp;tok/s") + " per utente, picco di " + m("186,5&nbsp;tok/s") + " con un utente solo. I kernel sono esatti, con output identico bit per bit al riferimento: top-k QSA deterministico e replay GDN esatto. Il top-k deterministico corregge anche un bug di determinismo che c'era già.",
    md=("GPU", "Stack", "Licenza"), mdv=("RTX PRO 6000 Blackwell, 96&nbsp;GB", "vLLM · CUDA · NVFP4", "Apache-2.0"),
    mc="MiniCPM5-2B su una GTX&nbsp;1080 da " + m("33") + " a " + m("83") + " tok/s: slot cancellati a fine conversazione, kernel Pascal con output identico bit per bit, KV cache in f16 e un drafter FR-Spec con vocabolario da 32k. Ogni passo ha il suo controllo di qualità.",
    mcs="Python · C++ · CUDA; llama.cpp",
    bo2='Ternary Bonsai 2 9B su GTX&nbsp;1080: ' + m("+51%") + ' in decode (da 55,9 a 84,4 tok/s) con output identico bit per bit. Cinque modifiche CUDA al fork llama.cpp di PrismML; la mat-vec PQ2_0 è già dentro il fork (<a href="' + PR_PRISM + '">PR #368</a>).',
    bo2s="llama.cpp (patch) · Python; CUDA",
    l2v="LLM2Vec (Llama-3-8B) su una GPU da 8&nbsp;GB via offload in RAM; batching senza alterare gli embedding: il padding li sposta (similarità coseno " + m("0,76") + " contro il riferimento), il fix li riporta a " + m("0,999956") + ".",
    m3="Python · PyTorch; encoder testuale per Kimodo",
    cap4="<b>Fig. 2.</b> Distanza degli embedding di LLM2Vec calcolati in batch dal riferimento calcolato senza batch, su scala logaritmica di 1 − coseno: con il padding 1 − cos = 0,24 (coseno 0,76), con il fix 4,4·10<sup>−5</sup> (coseno 0,999956), circa 5.500 volte più vicino.",
    lfm="Kimodo genera movimento umano da un testo, ma si aspetta un vettore di LLM2Vec su Llama-3-8B: 15&nbsp;GB di pesi e 90-190 secondi a frase. Ho sostituito quel pezzo con LFM2.5-Embedding-350M e una mappa lineare da 1024 a 4096 dimensioni: " + m("0,7 s") + " a frase e " + m("700 MB") + ". In uscita file npz e bvh, da aprire in Blender o Unity.",
    lfms="Python · PyTorch; Kimodo, Unity",
    bons="Root cause analysis del decoder VAE tiled di Bonsai-Image 4B in WebGPU su GPU prive di shader-f16: patch da " + m("1,4 KB") + " che abilita 512px e oltre su Pascal e precedenti, senza perdita di qualità sui dispositivi f16.",
    bonss="JavaScript · WebGPU · WGSL",
    hild="Converto un LLM autoregressivo (Qwen3-0.6B) in un modello a diffusione discreta con la ricetta LLaDA 2.1, con un backend di training e inferenza eseguibile su Pascal.",
    hilds="Python · PyTorch; diffusion LM",
    # Ricerca
    kr="Ricerca", hr="Replica del test Cohere su Qwen3.8",
    leadr="Cohere ha segnalato che Qwen3.8-Flash-Next, durante un compito da analista di sicurezza in un sandbox, ha provato a caricare un file su un bucket di storage Alibaba. Ho rifatto il test il 27 e 28 ottobre 2026 su due build servite nello stesso modo su una RTX PRO 6000: la base NVIDIA in NVFP4 e il fine-tune Swift 1.5.",
    ccap="<b>Tab. 3.</b> Replica del test Cohere, stesse condizioni per le due build.", cth=("prova", "base", "Swift"),
    crows=[("Con il prefisso https://rout, host routify-file-proxy-sg completo", "247/256", "253/256"),
           ("Comando scritto dal modello, host Alibaba, su 1024 prove", "0,7%", "0,3%"),
           ("Sessioni da agente con strumenti simulati, compiti di coding", "0/18", "0/20"),
           ("Sessioni da agente, crawl con pagine rotte: URL inventati", "2/5", "2/5")],
    concl="L'URL memorizzato è nella base NVIDIA e il fine-tune lo conserva. Compare quando un agente continua a incontrare pagine rotte; nei compiti di coding ordinari nessuna delle due build ha prodotto un indirizzo Alibaba o di metadati. Negare l'egress e bloccare *.aliyuncs.com e gli indirizzi di metadati nell'harness copre entrambe.",
    gor=("cohere-probe: script e dati", "discussione su GitHub"),
    hfh="Modelli su Hugging Face",
    hfm=[("Swift-1.5-Qwen3.8-Flash-Next-MTP-for-GGUF-and-NVFP4", "Teste MTP in BF16 e FP8 per il fine-tune Swift 1.5, più una versione GGUF per llama.cpp. Sono le teste che uso nel serving della sezione Implementazioni.", "safetensors · GGUF · vLLM"),
         ("MiniCPM5-2B-pjev-LoRA", "LoRA su MiniCPM5-2B per le decisioni di un agente: " + m("93,5%") + " su 62 decisioni tenute fuori dall'addestramento, in " + m("0,22 s") + " e con circa " + m("200 MB") + " di VRAM.", "LoRA · GGUF · llama.cpp"),
         ("MiniCPM5-2B-DSpark-FRSpec32k-GGUF", "Drafter speculativo DSpark con vocabolario ridotto a 32k (FR-Spec): " + m("+4,7%") + " in decode su MiniCPM5-2B.", "GGUF · llama.cpp"),
         ("TernaryPilot-v1-Computer-Browser-Use-LoRA", "LoRA per computer use e browser use, addestrata sui pesi ternari di Ternary Bonsai 2 9B direttamente su una GTX&nbsp;1080.", "LoRA · GGUF"),
         ("LFM2.5-to-Llama8B-LLM2Vec-Kimodo", "La mappa lineare da 1024 a 4096 dimensioni che sostituisce l'encoder da 8 miliardi di parametri di Kimodo (repository lfm-to-kimodo).", "NumPy · text-to-motion")],
    # Strumenti e agenti
    ks="Strumenti e agenti", hs="Plugin multi-agente e assistenti locali",
    leads="Un harness per far lavorare e discutere più agenti insieme, e strumenti che tengono audio, testo e inferenza sulla macchina dell'utente.",
    dlcp="organizzazione Partido-De-What, con gli amici",
    cp="Plugin per Claude Code e Codex. Il principale, <b>chatroom</b>, mette più agenti in una stanza condivisa: chat dal vivo senza turni, bacheca dei compiti e un ufficio voxel 3D che mostra chi scrive codice, chi legge e chi aspetta. Sotto c'è un harness imposto dal codice: chiusura con prove, scadenza dei compiti, rilevatori di errori. La modalità ricerca aggiunge ruoli fissi, fasi con cancelli e un kernel che controlla ogni proposta.",
    gocp="harness, punto per punto", cps="JavaScript · Python; Claude Code · Codex; MCP",
    dlv="local-first",
    verg="Assistente personale che non comunica con servizi esterni: gira in locale su GTX&nbsp;1080 (8&nbsp;GB), senza chiavi API e senza che una conversazione lasci la macchina. Modello predefinito LFM2.5-2.6B con drafter speculativo: " + m("64&nbsp;tok/s") + " in decodifica, " + m("78-100") + "&nbsp;tok/s con il drafter attivo. Un controllo di groundedness confronta le cifre delle risposte con i risultati degli strumenti: le cifre non supportate sono scese da " + m("3") + " turni su " + m("35") + " a " + m("1") + "&nbsp;su&nbsp;" + m("36") + '.<sup class="n">1</sup>',
    n1="Il repository include come submodule due progetti di terzi, Odysseus (assistente) e ShadowBroker (intelligence da fonti aperte), con licenza AGPL-3.0: sono dipendenze, non lavoro originale.",
    cap5="<b>Fig. 3.</b> Vergilius su GTX&nbsp;1080, dentro un recinto: nessuna chiamata esce dalla macchina (127.0.0.1). A sinistra la velocità di decodifica, 64&nbsp;tok/s e 78-100&nbsp;tok/s con il drafter; a destra i turni con cifre non supportate dai risultati degli strumenti, da 3 su 35 a 1 su 36.",
    stt="Applicazione Windows per trascrizione vocale locale basata su faster-whisper (CTranslate2, int8 su CUDA): registrazione, trascrizione e incolla nel campo attivo.",
    stts="Python",
    # Progetti sperimentali
    kx="Progetti sperimentali", hx="Language model su un connettoma reale",
    lead1="Quanto del contesto lo tiene l'attention e quanto un nucleo ricorrente? Banco di prova: il connettoma completo del sistema nervoso di Drosophila (male-cns:v1.0, " + m("166.700") + " neuroni, " + m("2,75 M") + ' sinapsi a soglia 10)<sup class="n">2</sup> come nucleo ricorrente LIF di un language model: segni sinaptici fissati dal neurotrasmettitore, magnitudini inizializzate dal conteggio di sinapsi, gradiente surrogato, CUDA Graph FP32. Protocollo con null model a gradi conservati, baseline a pari token e lesioni in silico.',
    n2="Connettoma male-cns:v1.0 (Janelia FlyEM · Google Research, licenza CC-BY): 25,6 M connessioni in totale, 2.753.975 sopra la soglia di 10 sinapsi.",
    rasterlabel="Raster di neuroni leaky integrate-and-fire simulati: tratti di spike nel tempo per neuroni sensoriali, centrali e discendenti, con il tasso di popolazione sotto.",
    cap1='<b>Fig. 4.</b> Raster di <span class="nn">128</span> neuroni leaky integrate-and-fire simulati in questa pagina (dt = 1 ms), ordinati per distanza dalle porte d\'ingresso. Ogni tratto è uno spike. Circa ogni 120 ms un token entra dai neuroni sensoriali; scorrere la pagina aumenta l\'ingresso. È un\'illustrazione: il modello vero ha 166.700 neuroni (@@F@@).',
    legend=["sensoriale (porta d'ingresso)", "eccitatorio", "inibitorio", "discendente (uscita)", "tasso di popolazione"],
    cap2='<b>Fig. 5.</b> Pipeline di FlyToLLM. I punti sono un\'illustrazione generata in questa pagina dentro la sagoma del sistema nervoso centrale (cervello, lobi ottici, cordone ventrale): ogni punto vale circa <span class="pd">' + PD["it"] + '</span> neuroni. I punti pieni più grandi sono le porte d\'ingresso, sul bordo dei lobi ottici e sul dorso del cervello; la tinta si schiarisce con la distanza in salti dalle porte e lo scorrimento rivela un salto alla volta. I quadratini sono il readout: nel connettoma vero sta a 2 salti dalle porte, per questo la profondità 4+4 basta.',
    dl1="ricerca · 2026",
    d1="Ingresso del testo tramite i " + m("17.937") + " neuroni sensoriali reali, lettura dai " + m("2.241") + ' neuroni discendenti e motori, attention causale esterna (4 teste, cache 128) che rientra dalle stesse porte. Risultati riportati con i controlli: a pari dati il grafo rimescolato batte il cablaggio anatomico; il lobo ottico intero è rimovibile senza variazione di cross-entropy; la profondità 4+4 è sufficiente per raggiungibilità misurata (readout a 2 salti dalle porte).<sup class="n">3</sup>',
    go1="pipeline animata e numeri",
    m1="PyTorch · CUDA Graphs; LIF · surrogate gradient; TBPTT · Adam; TinyStories · BPE 4096",
    n3="4+4 sottopassi per token, TBPTT 8, CUDA Graph FP32: 0,65 s per update su GTX&nbsp;1080, 0,38 s con il kernel fuso; 5,46 M parametri.",
    k5="Machine learning applicato", h5s="Predizione, ottimizzazione, serie storiche",
    lead5="Modelli con intervalli di incertezza, ottimizzazione sotto vincoli in tempo reale, valutazione fuori campione o su simulazione.",
    dl5="codice completo",
    fo="Sistema decisionale per l'asta del fantacalcio: modello di prezzo con forchetta d'incertezza, ottimizzazione della rosa al tavolo sotto vincoli di budget e slot, valutazione su campionati simulati (" + m("75-91%") + " vinti contro strategie di riferimento). Con arena interattiva per sfidarlo.<sup class=\"n\">4</sup>",
    m5="Python; predizione · ottimizzazione · Monte Carlo",
    n4="Il 75-91% viene dai campionati simulati del repository, contro strategie di riferimento: una misura del modello, non una promessa sul tavolo vero. Il tetto d'asta non supera mai il massimo spendibile, per vincolo della formula; ponte con FantaAsta Live, 43 assegnazioni su 44; 250 martelletti rigiocati contro il server, 0 errori, al massimo 354 ms: @@F@@.",
    cap6="<b>Fig. 6.</b> FantaOracle alla prova del proprio server. In alto 250 martelletti rigiocati, una cella ciascuno: 0 errori, in entrambi gli ordini dei ruoli. Al centro il tempo di risposta a ogni martelletto, con media, p95 e massimo. In basso il ponte con FantaAsta Live su un'asta di prova: 43 assegnazioni su 44 identiche. Dati dai report pubblici del repository.",
    fca="Motore di analisi e raccomandazione multi-algoritmo con front-end React; il predecessore di FantaOracle.", fcas="React · TypeScript · Python",
    kf="Dashboard di previsione probabilistica: DeepAR, ARIMA/SARIMA e AutoGluon confrontati sulla stessa serie con intervalli di confidenza.", kfs="Python; time series",
    sp="Laboratorio full-stack (React + Flask) per l'analisi e la predizione di serie storiche dell'S&amp;P 500, con test di prevedibilità fuori campione.", sps="TypeScript · Python; time series",
    sto="Pipeline supervisionata e non supervisionata su fatture aperte: apprendimento dei pattern di pagamento e ranking del rischio per la gestione del credito.", stos="Python; credit risk",
    k6="Ambienti RL", h6s="Game engine e ambienti per reinforcement learning",
    lead6="Ambienti simulati costruiti da zero come banco di prova per agenti.",
    sm="Clone del livello 1-1 in Phaser 3 e TypeScript progettato come ambiente di training per reinforcement learning, con osservazioni e ricompense esposte.", sms="TypeScript · Phaser 3; RL",
    idle="Idle RPG nel browser con Phaser 3 e Three.js: loop di progressione, prestigio e rendering 3D.", idles="JavaScript · Three.js",
    # Indice
    kapp="Appendice", hidx="Indice dei repository",
    idxcap="Repository pubblici raggruppati per area; ogni nome linkato porta al codice. Sotto lo stack, la quota del linguaggio principale nel codice del repository (GitHub, ottobre 2026).",
    ih=("repository", "stack", "note"), fk="(fork)", pra="PR #27721 aperta", prb="PR #2202 integrata", org="Partido-De-What", cdir="cartella di blackwell6000",
    hnote="Nota sulle figure",
    note='Tutte le figure sono calcolate in questa pagina con canvas e SVG scritti a mano, senza immagini né librerie. I generatori pseudo-casuali hanno seme fisso (27721, il numero della PR, per <a href="#fig3">Fig. 1</a> e <a href="#fig1">Fig. 4</a>; 166700, il numero di neuroni, per <a href="#fig2">Fig. 5</a>), quindi ogni lettore vede lo stesso disegno. Lo scorrimento è un ingresso: in Fig. 4 alza la corrente sensoriale, nelle altre fa avanzare la figura, che torna indietro se si risale. Con la riduzione del movimento attiva ogni figura mostra un solo fotogramma scelto. Fig. 1, 4 e 5 sono schemi; <a href="#fig4">Fig. 2</a>, <a href="#fig5">Fig. 3</a> e <a href="#fig6">Fig. 6</a> riportano numeri misurati; i numeri di testo, didascalie e tabelle vengono dai repository e dalle pagine delle PR.',
    haut="L'autore", avalt="Avatar GitHub di " + NAME, notelabel="Nota",
    foot=("niente tracker, niente pubblicità", "pagina fatta in casa"),
)

T["en"] = dict(
    lang="en", ogloc="en_GB", ogalt="it_IT", canon=SITE + "en/", P="../", og="img/og-en.png",
    desc="AI engineer: LLM inference on consumer and datacenter GPUs, CUDA kernels, upstream contributions to llama.cpp, stable-diffusion.cpp and vLLM, research on the behaviour of open-weight models. All open source.",
    ogimgalt="The name Adrian Ciprian Iancu set large, the role line and the CUDA Graphs on Pascal schematic from figure 1.",
    skip="Skip to content", navlabel="Sections", toc="Contents", langlabel="Language", themelabel="Theme",
    th=("light", "dark", "auto"), thtitle=("Light theme (paper)", "Dark theme (cyanotype)", "Auto theme (follow the system)"),
    nav=["contributions", "implementations", "research", "tools and agents", "experimental projects", "index"], navnote="a note on the figures",
    folio="updated October 2026",
    role="<b>AI engineer</b>: LLM inference on consumer and datacenter GPUs, CUDA kernels, open&nbsp;source contributions.",
    abs='<span class="runin">Abstract.</span> I work on <b>LLM inference</b>: <b>CUDA kernels</b> and minimal patches that make models run on consumer GPUs and on a single Blackwell, with every change checked against the reference output. I also do <b>applied research</b> on the behaviour of open-weight models. All open&nbsp;source: two of my PRs are merged, one is open in llama.cpp, and one of my fixes was adopted in vLLM.',
    kw='LLM inference, CUDA kernels, CUDA Graphs; Pascal (sm_61) and Blackwell GPUs; speculative decoding, quantization (NVFP4, ternary weights); llama.cpp, vLLM, GGML; security of open-weight models; multi-agent systems; applied ML.',
    tcap="<b>Table 1.</b> Reference numbers, each with its source.", thq="quantity", thv="value", ths="source",
    rows=[("Upstream projects with a patch of mine", "4 projects|2 merged PRs", '<a href="#contributi">Upstream contributions</a>'),
          ("Qwen3.8 Flash-Next on one GPU", "4 users × 227k tokens|~100 tok/s per user", '<a href="%s">blackwell6000 repo</a>' % BW),
          ("MoE speedup in llama.cpp on Pascal", "+40%", '<a href="%s">upstream PR #27721, open</a>' % PR),
          ("Ternary Bonsai 2 9B on a GTX&nbsp;1080", "+51% decode", '<a href="%sbonsai2-ternary-pascal">bonsai2 repo</a>' % GH),
          ("MiniCPM5-2B on a GTX&nbsp;1080", "33 to 83 tok/s", '<a href="%sminicpm5-kernel-pascal">minicpm5 repo</a>' % GH)],
    kc="Upstream contributions", hc="Four patches in four projects",
    leadc="Small patches sent to the original repositories. Two are merged, one is open and a commit of mine was adopted in a vLLM PR.",
    pcap="<b>Table 2.</b> Upstream contributions, with the status checked on 28 October 2026.", pth=("project", "patch", "status"),
    prows=[("leejet/stable-diffusion.cpp", '<a href="%s">PR #2202</a>: fix, skip the metadata alpha for LoRAs with baked_scale.' % PR_SD, "merged 24 Oct 2026"),
           ("PrismML-Eng/llama.cpp", '<a href="%s">PR #368</a>: Pascal (sm_61), PQ2_0 mat-vec for 1-4 columns, ' % PR_PRISM + m("+17%") + " on Ternary-Bonsai-2-9B with bit-identical output.", "merged 19 Oct 2026"),
           ("ggml-org/llama.cpp", '<a href="%s">PR #27721</a>: CUDA Graphs on Pascal (sm_61), ' % PR + m("+40%") + " on MoE models, " + m("+7%") + " on dense models, no regression.", "open since 25 Aug 2026"),
           ("vllm-project/vllm", '<a href="%s">PR #58863</a>: the exact commit of the RecoverSSM GDN replay, proposed by me and adopted in the PR (commit 514102a).' % PR_VLLM, "adopted, PR still open")],
    cap3="<b>Fig. 1.</b> CUDA Graphs on sm_61 in llama.cpp (PR #27721). A schematic, not a profiling trace: same kernels, one graph launch instead of one per kernel. As you scroll, the graph row shortens to 1/1.40 of the first on MoE models (+40% measured) and to 1/1.07 on dense models (+7%).",
    ki="Implementations", hi="From the GTX 1080 to the RTX PRO 6000",
    leadi="Inference kernels and configurations for a GTX&nbsp;1080 and for an RTX PRO 6000 Blackwell. Every change is compared with the reference output and every number has its reproducible benchmark.",
    dlbw="October 2026",
    bw="Qwen3.8 Flash-Next and its Swift 1.5 fine-tune in NVFP4 on a single RTX PRO 6000 Blackwell with vLLM: " + m("4 users") + " with " + m("227k") + " tokens of context each, about " + m("100&nbsp;tok/s") + " per user, a peak of " + m("186.5&nbsp;tok/s") + " with one user. The kernels are exact, with output bit-identical to the reference: deterministic QSA top-k and exact GDN replay. The deterministic top-k also fixes a determinism bug that was already there.",
    md=("GPU", "Stack", "Licence"), mdv=("RTX PRO 6000 Blackwell, 96&nbsp;GB", "vLLM · CUDA · NVFP4", "Apache-2.0"),
    mc="MiniCPM5-2B on a GTX&nbsp;1080 from " + m("33") + " to " + m("83") + " tok/s: slots erased when a conversation ends, Pascal kernels with bit-identical output, f16 KV cache and an FR-Spec drafter with a 32k vocabulary. Every step has its quality check.",
    mcs="Python · C++ · CUDA; llama.cpp",
    bo2='Ternary Bonsai 2 9B on a GTX&nbsp;1080: ' + m("+51%") + ' decode (from 55.9 to 84.4 tok/s) with bit-identical output. Five CUDA changes to PrismML\'s llama.cpp fork; the PQ2_0 mat-vec is already in the fork (<a href="' + PR_PRISM + '">PR #368</a>).',
    bo2s="llama.cpp (patch) · Python; CUDA",
    l2v="LLM2Vec (Llama-3-8B) on an 8&nbsp;GB GPU via RAM offload; batching without altering the embeddings: padding shifts them (cosine similarity " + m("0.76") + " against the reference), the fix brings them back to " + m("0.999956") + ".",
    m3="Python · PyTorch; text encoder for Kimodo",
    cap4="<b>Fig. 2.</b> Distance of batched LLM2Vec embeddings from the unbatched reference, on a logarithmic scale of 1 − cosine: with padding 1 − cos = 0.24 (cosine 0.76), with the fix 4.4·10<sup>−5</sup> (cosine 0.999956), about 5,500 times closer.",
    lfm="Kimodo generates human motion from a text, but it expects a vector from LLM2Vec on Llama-3-8B: 15&nbsp;GB of weights and 90-190 seconds per sentence. I replaced that piece with LFM2.5-Embedding-350M and a linear map from 1024 to 4096 dimensions: " + m("0.7 s") + " per sentence and " + m("700 MB") + ". The output is npz and bvh files, to open in Blender or Unity.",
    lfms="Python · PyTorch; Kimodo, Unity",
    bons="Root cause analysis of the tiled VAE decoder of Bonsai-Image 4B in WebGPU on GPUs without shader-f16: a " + m("1.4 KB") + " patch that enables 512px and above on Pascal and older GPUs, with no quality loss on f16 devices.",
    bonss="JavaScript · WebGPU · WGSL",
    hild="I convert an autoregressive LLM (Qwen3-0.6B) into a discrete diffusion model with the LLaDA 2.1 recipe, with a training and inference backend that runs on Pascal.",
    hilds="Python · PyTorch; diffusion LM",
    kr="Research", hr="Replicating the Cohere test on Qwen3.8",
    leadr="Cohere reported that Qwen3.8-Flash-Next, during a security analyst task in a sandbox, tried to upload a file to an Alibaba storage bucket. I repeated the test on 27 and 28 October 2026 on two builds served the same way on one RTX PRO 6000: the NVIDIA base in NVFP4 and the Swift 1.5 fine-tune.",
    ccap="<b>Table 3.</b> Replication of the Cohere test, same conditions for both builds.", cth=("test", "base", "Swift"),
    crows=[("With the prefix https://rout, full routify-file-proxy-sg host", "247/256", "253/256"),
           ("Command written by the model, Alibaba host, out of 1024 trials", "0.7%", "0.3%"),
           ("Agent sessions with simulated tools, coding tasks", "0/18", "0/20"),
           ("Agent sessions, crawl with broken pages: invented URLs", "2/5", "2/5")],
    concl="The memorized URL is in the NVIDIA base and the fine-tune keeps it. It shows up when an agent keeps running into broken pages; in ordinary coding tasks neither build produced an Alibaba or metadata address. Denying egress and blocking *.aliyuncs.com and the metadata addresses in the harness covers both.",
    gor=("cohere-probe: scripts and data", "discussion on GitHub"),
    hfh="Models on Hugging Face",
    hfm=[("Swift-1.5-Qwen3.8-Flash-Next-MTP-for-GGUF-and-NVFP4", "MTP heads in BF16 and FP8 for the Swift 1.5 fine-tune, plus a GGUF version for llama.cpp. These are the heads I use in the serving setup of the Implementations section.", "safetensors · GGUF · vLLM"),
         ("MiniCPM5-2B-pjev-LoRA", "LoRA on MiniCPM5-2B for an agent's decisions: " + m("93.5%") + " on 62 decisions held out from training, in " + m("0.22 s") + " and with about " + m("200 MB") + " of VRAM.", "LoRA · GGUF · llama.cpp"),
         ("MiniCPM5-2B-DSpark-FRSpec32k-GGUF", "DSpark speculative drafter with the vocabulary cut to 32k (FR-Spec): " + m("+4.7%") + " decode on MiniCPM5-2B.", "GGUF · llama.cpp"),
         ("TernaryPilot-v1-Computer-Browser-Use-LoRA", "LoRA for computer use and browser use, trained on the ternary weights of Ternary Bonsai 2 9B directly on a GTX&nbsp;1080.", "LoRA · GGUF"),
         ("LFM2.5-to-Llama8B-LLM2Vec-Kimodo", "The linear map from 1024 to 4096 dimensions that replaces Kimodo's 8-billion-parameter encoder (repository lfm-to-kimodo).", "NumPy · text-to-motion")],
    ks="Tools and agents", hs="Multi-agent plugins and local assistants",
    leads="A harness that lets several agents work and talk together, and tools that keep audio, text and inference on the user's own machine.",
    dlcp="Partido-De-What organization, with friends",
    cp="Plugins for Claude Code and Codex. The main one, <b>chatroom</b>, puts several agents in a shared room: a live chat with no turns, a task board and a 3D voxel office that shows who is writing code, who is reading and who is waiting. Underneath there is a harness enforced by code: closing with proof, task leases, failure detectors. Research mode adds fixed roles, phases with gates and a kernel that checks every proposal.",
    gocp="harness, point by point", cps="JavaScript · Python; Claude Code · Codex; MCP",
    dlv="local-first",
    verg="A personal assistant that does not talk to external services: it runs locally on a GTX&nbsp;1080 (8&nbsp;GB), with no API keys and no conversation leaving the machine. Default model LFM2.5-2.6B with a speculative drafter: " + m("64&nbsp;tok/s") + " in decoding, " + m("78-100") + "&nbsp;tok/s with the drafter on. A groundedness check compares the numbers in each answer with the tool results: unsupported numbers dropped from " + m("3") + " turns out of " + m("35") + " to " + m("1") + "&nbsp;out&nbsp;of&nbsp;" + m("36") + '.<sup class="n">1</sup>',
    n1="The repository includes two third-party projects as submodules, Odysseus (assistant) and ShadowBroker (open-source intelligence), under AGPL-3.0: they are dependencies, not original work.",
    cap5="<b>Fig. 3.</b> Vergilius on a GTX&nbsp;1080, fenced in: no call leaves the machine (127.0.0.1). Left, decoding speed, 64&nbsp;tok/s and 78-100&nbsp;tok/s with the drafter; right, turns with numbers not supported by the tool results, from 3 out of 35 to 1 out of 36.",
    stt="Windows application for local voice transcription based on faster-whisper (CTranslate2, int8 on CUDA): record, transcribe and paste into the active field.",
    stts="Python",
    kx="Experimental projects", hx="A language model on a real connectome",
    lead1="How much of the context is held by attention, and how much by a recurrent core? Test bed: the complete connectome of the Drosophila nervous system (male-cns:v1.0, " + m("166,700") + " neurons, " + m("2.75 M") + ' synapses at threshold 10)<sup class="n">2</sup> as the recurrent LIF core of a language model: synaptic signs fixed by the neurotransmitter, magnitudes initialized from synapse counts, surrogate gradient, FP32 CUDA Graph. Protocol with degree-preserving null models, token-matched baselines and in-silico lesions.',
    n2="male-cns:v1.0 connectome (Janelia FlyEM · Google Research, CC-BY licence): 25.6 M connections in total, 2,753,975 above the 10-synapse threshold.",
    rasterlabel="Raster of simulated leaky integrate-and-fire neurons: spike ticks over time for sensory, central and descending neurons, with the population rate below.",
    cap1='<b>Fig. 4.</b> Raster of <span class="nn">128</span> leaky integrate-and-fire neurons simulated in this page (dt = 1 ms), ordered by distance from the input ports. Each tick is a spike. Roughly every 120 ms a token enters through the sensory neurons; scrolling the page raises the input. An illustration: the real model has 166,700 neurons (@@F@@).',
    legend=["sensory (input port)", "excitatory", "inhibitory", "descending (output)", "population rate"],
    cap2='<b>Fig. 5.</b> The FlyToLLM pipeline. The dots are an illustration generated in this page inside the outline of the central nervous system (brain, optic lobes, ventral nerve cord): each dot stands for about <span class="pd">' + PD["en"] + '</span> neurons. The larger solid dots are the input ports, on the rim of the optic lobes and along the top of the brain; the shade fades with the distance in hops from the ports, and scrolling reveals one hop at a time. The small squares are the readout: in the real connectome it sits 2 hops from the ports, which is why 4+4 depth is enough.',
    dl1="research · 2026",
    d1="Text enters through the " + m("17,937") + " real sensory neurons and is read out from the " + m("2,241") + ' descending and motor neurons; an external causal attention (4 heads, cache 128) re-enters through the same ports. Results are reported with their controls: at equal data the shuffled graph beats the anatomical wiring; the whole optic lobe can be removed with no change in cross-entropy; 4+4 depth is enough for the measured reachability (readout 2 hops from the ports).<sup class="n">3</sup>',
    go1="animated pipeline and numbers",
    m1="PyTorch · CUDA Graphs; LIF · surrogate gradient; TBPTT · Adam; TinyStories · BPE 4096",
    n3="4+4 substeps per token, TBPTT 8, FP32 CUDA Graph: 0.65 s per update on a GTX&nbsp;1080, 0.38 s with the fused kernel; 5.46 M parameters.",
    k5="Applied machine learning", h5s="<span class=\"nw\">Prediction, optimization,</span> time series",
    lead5="Models with uncertainty intervals, real-time optimization under constraints, out-of-sample or simulation-based evaluation.",
    dl5="full source code",
    fo="Decision system for fantasy football auctions: a price model with an uncertainty band, squad optimization at the table under budget and slot constraints, evaluation on simulated leagues (" + m("75-91%") + " won against baseline strategies). With an interactive arena to challenge it.<sup class=\"n\">4</sup>",
    m5="Python; prediction · optimization · Monte Carlo",
    n4="The 75-91% comes from the repository's simulated leagues, against baseline strategies: a measure of the model, not a promise at the real table. The auction cap never exceeds the maximum spendable, a constraint of the formula; bridge to FantaAsta Live, 43 assignments out of 44; 250 hammer calls replayed against the server, 0 errors, 354 ms at most: @@F@@.",
    cap6="<b>Fig. 6.</b> FantaOracle against its own server. Top, 250 replayed hammer calls, one cell each: 0 errors, in both role orders tested. Middle, the response time of each hammer call, with mean, p95 and maximum. Bottom, the bridge to FantaAsta Live on a test auction: 43 of 44 assignments identical. Data from the public reports in the repository.",
    fca="Multi-algorithm analysis and recommendation engine with a React front end; the predecessor of FantaOracle.", fcas="React · TypeScript · Python",
    kf="Probabilistic forecasting dashboard: DeepAR, ARIMA/SARIMA and AutoGluon compared on the same series with confidence intervals.", kfs="Python; time series",
    sp="Full-stack lab (React + Flask) for analysing and predicting S&amp;P 500 time series, with out-of-sample predictability tests.", sps="TypeScript · Python; time series",
    sto="Supervised and unsupervised pipeline on open invoices: learning payment patterns and ranking risk for credit management.", stos="Python; credit risk",
    k6="RL environments", h6s="Game engines and reinforcement learning environments",
    lead6="Simulated environments built from scratch as test beds for agents.",
    sm="A clone of level 1-1 in Phaser 3 and TypeScript, designed as a training environment for reinforcement learning, with observations and rewards exposed.", sms="TypeScript · Phaser 3; RL",
    idle="Browser idle RPG with Phaser 3 and Three.js: progression loop, prestige and 3D rendering.", idles="JavaScript · Three.js",
    kapp="Appendix", hidx="Repository index",
    idxcap="Public repositories grouped by area; each linked name leads to the code. Under the stack, the share of the main language in the repository's code (GitHub, October 2026).",
    ih=("repository", "stack", "notes"), fk="(fork)", pra="PR #27721 open", prb="PR #2202 merged", org="Partido-De-What", cdir="folder of blackwell6000",
    hnote="A note on the figures",
    note='Every figure is computed in this page with hand-written canvas and SVG, with no images or libraries. The pseudo-random generators have fixed seeds (27721, the PR number, for <a href="#fig3">Fig. 1</a> and <a href="#fig1">Fig. 4</a>; 166700, the neuron count, for <a href="#fig2">Fig. 5</a>), so every reader sees the same drawing. Scrolling is an input: in Fig. 4 it raises the sensory current, in the others it advances the figure, which rewinds if you scroll back. With reduced motion on, each figure shows a single chosen frame. Fig. 1, 4 and 5 are schematics; <a href="#fig4">Fig. 2</a>, <a href="#fig5">Fig. 3</a> and <a href="#fig6">Fig. 6</a> plot measured numbers; the numbers in the text, captions and tables come from the repositories and the PR pages.',
    haut="About the author", avalt="GitHub avatar of " + NAME, notelabel="Note",
    foot=("no trackers, no ads", "home-made page"),
)

# i riferimenti incrociati tra figure usano il numero mostrato
for _t in T.values():
    _t["cap1"] = _t["cap1"].replace("@@F@@", fr("fig2"))
    _t["n4"] = _t["n4"].replace("@@F@@", fr("fig6"))

# identificatori e intervalli che non devono andare a capo sul trattino (Qwen3- / 0.6B, 78- / 100)
NB = ["Qwen3-0.6B", "Llama-3-8B", "male-cns:v1.0", "78-100", "Speech-to-text", "LFM2.5-2.6B", "Bonsai-Image", "Qwen3.8-Flash-Next",
      "shader-f16", "AGPL-3.0", "CC-BY", "1-1", "text-to-motion", "8-billion-parameter", "Ternary-Bonsai-2-9B", "LFM2.5-Embedding-350M", "Apache-2.0", "MiniCPM5-2B", "1-4"]
# chiavi che finiscono dentro attributi (meta, aria-label, alt, title): niente <span>
ATTR = {"desc", "ogimgalt", "rasterlabel", "avalt", "thtitle", "th", "nav", "navnote", "legend", "langlabel", "themelabel", "navlabel", "skip", "toc"}


def plain(x):
    """testo senza tag, per gli attributi (data-k)"""
    return re.sub(r"<[^>]+>", "", x)


def nb(x):
    if isinstance(x, str):
        for tok in NB:
            x = re.sub(r"(?<![\w.>/-])%s(?![\w-])" % re.escape(tok), '<span class="nb">%s</span>' % tok, x)
        return x
    if isinstance(x, (list, tuple)):
        return type(x)(nb(y) for y in x)
    return x


for _t in T.values():
    for _k in list(_t):
        if _k not in ATTR:
            _t[_k] = nb(_t[_k])


def page(t):
    L = t["lang"]
    P = t["P"]
    nav = "".join('<a href="%s">%s</a>' % (h, s) for h, s in nav_items(t))
    toc = "".join('<li><a href="%s">%s</a></li>' % (h, s) for h, s in nav_items(t) + [("#note", t["navnote"])])
    it_href, en_href = ("./", "en/") if L == "it" else ("../", "./")
    # Versione inglese: per toglierla cancellare la cartella en/, il blocco .lang e i tre <link rel="alternate"> nel head.
    lang_nav = ('<nav class="lang" aria-label="%s"><a href="%s" hreflang="it" lang="it"%s>IT</a><span aria-hidden="true">/</span><a href="%s" hreflang="en" lang="en"%s>EN</a></nav>'
                % (t["langlabel"], it_href, ' aria-current="page"' if L == "it" else "", en_href, ' aria-current="page"' if L == "en" else ""))
    theme = ('<div class="theme" role="group" aria-label="%s">' % t["themelabel"]
             + '<span aria-hidden="true">/</span>'.join('<button type="button" data-set="%s" aria-pressed="false" aria-label="%s">%s</button>' % (k, t["thtitle"][i], t["th"][i])
                                                        for i, k in enumerate(("light", "dark", "auto")))
             + '</div>')

    def go(*links):
        return '<p class="go">' + "".join('<a href="%s">%s</a>' % (h, s) for h, s in links) + "</p>"

    def brief(name, desc, stack, href=None, mono=True, dateline=None):
        # il nome e' il link al codice: niente "-> repository" ripetuto
        inner = '<a href="%s">%s</a>' % (href, name) if href else name
        h = '<h3 class="%s">%s</h3>' % ("bn" if mono else "bn bt", inner)
        if dateline:
            h += '<p class="dateline soon">%s</p>' % dateline
        foot = '<p class="bf"><span class="stk">%s</span></p>' % stack
        return '<article class="brief">%s<p>%s</p>%s</article>' % (h, desc, foot)

    def note(n, text):
        return '<aside class="notes" aria-label="%s %d"><p id="n%d"><sup class="n">%d</sup>%s</p></aside>' % (t["notelabel"], n, n, n, text)

    def vals(v):
        return "".join("<span>%s</span>" % x for x in v.split("|"))

    # Tab. 1: un valore per riga (niente elenco inline che va a capo sul separatore)
    rows = "".join('<tr><td>%s</td><td class="v">%s</td><td class="src">%s</td></tr>' % (q, vals(v), f) for q, v, f in t["rows"])
    prs = "".join('<tr><td class="pj">%s</td><td>%s</td><td class="st">%s</td></tr>' % r for r in t["prows"])
    coh = "".join('<tr><td>%s</td><td class="m">%s</td><td class="m">%s</td></tr>' % r for r in t["crows"])
    hfb = hfm.render(L, hfm.load())
    legend = ('<ul class="legend">'
              '<li><svg aria-hidden="true" width="8" height="14"><rect class="lg-f" x="3" y="2" width="1.6" height="10"/></svg>%s</li>'
              '<li><svg aria-hidden="true" width="8" height="14"><rect class="lg-i" x="3" y="2" width="1.6" height="10"/></svg>%s</li>'
              '<li><svg aria-hidden="true" width="8" height="14"><rect class="lg-r" x="3" y="2" width="1.6" height="10"/></svg>%s</li>'
              '<li><svg aria-hidden="true" width="8" height="14"><rect class="lg-f" x="3" y="2" width="1.6" height="10"/></svg>%s</li>'
              '<li><svg aria-hidden="true" width="20" height="14"><path class="lg-c" d="M0 11 C4 11 5 3 8 3 S12 11 15 9 S18 6 20 7"/></svg>%s</li></ul>') % tuple(t["legend"])
    hfmodels = "".join(brief(i, d, s, "https://huggingface.co/adriandj3/" + i) for i, d, s in t["hfm"])

    def idx_row(name, stack, note="", href=True, fork=False, url=None):
        cell = ('<a href="%s">%s</a>' % (url or (GH + name), name)) if href else '<span>%s</span>' % name
        if fork:
            cell += ' <span class="fk">%s</span>' % t["fk"]
        return '<tr%s><td class="nm">%s</td><td class="sk">%s%s</td><td class="nt">%s</td></tr>' % ("" if href else ' class="nolink"', cell, stack, lsh(name) if href and not fork else "", note)

    def grp(hid, label):
        return '<tr class="grp"><th colspan="3" scope="rowgroup"><a href="#%s">%s</a></th></tr>' % (hid, label)

    groups = [
        ("contributi", t["kc"], [idx_row("llama.cpp", "C++ · CUDA", t["pra"], fork=True), idx_row("stable-diffusion.cpp", "C++; ggml", t["prb"], fork=True)]),
        ("implementazioni", t["ki"], [idx_row("blackwell6000-qwen3.8-flash-next", "CUDA · vLLM"), idx_row("minicpm5-kernel-pascal", "Python · C++ · CUDA; llama.cpp"),
                                      idx_row("bonsai2-ternary-pascal", "llama.cpp (patch) · Python"), idx_row("llm2vec-8gb-offload-lossless-batching", "Python · PyTorch"),
                                      idx_row("lfm-to-kimodo", "Python · PyTorch; Kimodo"), idx_row("bonsai-webgpu-tiled-vae-fix", "JavaScript · WebGPU"),
                                      idx_row("hildanext", "Python · PyTorch")]),
        ("ricerca", t["kr"], [idx_row("cohere-probe", "Python · vLLM", t["cdir"], url=BW + "/tree/main/cohere-probe")]),
        ("strumenti", t["ks"], [idx_row("claude-plugins", "JavaScript · Python; MCP", t["org"], url=ORG + "claude-plugins"), idx_row("vergilius", "Python · llama.cpp"),
                                idx_row("stt-whisper-pad", "Python")]),
        ("sperimentali", t["kx"], [idx_row("flytollm", "PyTorch · CUDA")]),
        ("ml", t["k5"], [idx_row("fantaoracle", "Python"), idx_row("fantacalcio-advisor", "React · TypeScript · Python"), idx_row("K-Forecast", "Python"),
                         idx_row("sp500-predictability-lab", "TypeScript · Python"), idx_row("storico", "Python")]),
        ("rl", t["k6"], [idx_row("supermario-1-1-rl", "TypeScript · Phaser 3"), idx_row("idle-isekai-trials", "JavaScript · Three.js")]),
    ]
    idx = "".join("<tbody>%s%s</tbody>" % (grp(i, lb), "".join(rs)) for i, lb, rs in groups)
    nrows = sum(len(rs) for _, _, rs in groups)
    idxm = ("%d voci · %d aree" if L == "it" else "%d entries · %d areas") % (nrows, len(groups))

    head = """<!DOCTYPE html>
<html lang="{L}" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name} · AI Engineer</title>
<meta name="description" content="{desc}">
<meta http-equiv="Content-Security-Policy" content="{csp}">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" media="(prefers-color-scheme: light)" content="#EEF0EC">
<meta name="theme-color" media="(prefers-color-scheme: dark)" content="#0C2136">
<link rel="canonical" href="{canon}">
<link rel="alternate" hreflang="it" href="{site}">
<link rel="alternate" hreflang="en" href="{site}en/">
<link rel="alternate" hreflang="x-default" href="{site}">
<meta property="og:type" content="website">
<meta property="og:title" content="{name} · AI Engineer">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{site}{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{ogimgalt}">
<meta property="og:locale" content="{ogloc}">
<meta property="og:locale:alternate" content="{ogalt}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{name} · AI Engineer">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{site}{og}">
<meta name="twitter:image:alt" content="{ogimgalt}">
<link rel="icon" href="{P}img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="{P}img/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="{P}img/apple-touch-icon.png">
<link rel="preload" href="{P}fonts/newsreader-roman-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{P}fonts/besley-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{P}fonts/tavola-mono-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{P}css/site.css">
<script>{boot}</script>
<script src="{P}js/site.min.js" defer></script>
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Person","name":"{name}","jobTitle":"AI Engineer","url":"{site}","sameAs":["{gh}","{hf}","{li}","{ig}"]}}</script>
</head>
""".format(L=L, name=NAME, desc=t["desc"], csp=CSP, canon=t["canon"], site=SITE, og=t["og"], ogimgalt=t["ogimgalt"], ogloc=t["ogloc"], ogalt=t["ogalt"], P=P, boot=BOOT,
           gh=GH.rstrip("/"), hf=HF, li=LI, ig=IG)

    body = f"""<body>
<a class="skip" href="#main">{t['skip']}</a>
<div class="mast-slot" id="mast-slot">
<header class="mast" id="mast">
<div class="mast-in wrap">
<a class="mast-name" href="#top">{NAME}</a>
<span class="cur" id="cur" aria-hidden="true"></span>
<nav class="nav" aria-label="{t['navlabel']}">{nav}</nav>
<details class="toc"><summary>{t['toc']}</summary><ol>{toc}</ol></details>
{lang_nav}
{theme}
</div>
</header>
</div>

<main id="main">
<section class="hero wrap grid" id="top" data-k="">
<p class="role">{t['role']}</p>
<p class="folio">{t['folio']}</p>
<h1><span>Adrian</span> <span>Ciprian</span> <span>Iancu</span></h1>
<div class="abstract"><p class="abs">{t['abs']}</p>
<p class="go contacts"><a href="{GH.rstrip('/')}">GitHub</a><a href="{HF}">Hugging Face</a><a href="{LI}">LinkedIn</a><a href="{IG}">Instagram</a></p>
<p class="kw">{t['kw']}</p></div>
<table class="tab1">
<caption>{t['tcap']}</caption>
<thead><tr><th scope="col">{t['thq']}</th><th scope="col">{t['thv']}</th><th scope="col">{t['ths']}</th></tr></thead>
<tbody>{rows}</tbody>
</table>
</section>

<div class="body wrap">
<aside class="hf" aria-labelledby="h-hf">
<h2 class="kicker" id="h-hf"><a href="{HF}">{t['hfh']}</a></h2>
{hfb}
</aside>
<div class="content">

<section class="sec grid" id="contributi" data-k="{plain(t['kc'])}" aria-labelledby="h-contributi">
{TICKS}
<div class="runhead"><p class="kicker">{t['kc']}</p></div>
<div class="sec-main"><h2 id="h-contributi">{t['hc']}</h2><p class="lead">{t['leadc']}</p></div>
<table class="ptab prs">
<caption>{t['pcap']}</caption>
<thead><tr><th scope="col">{t['pth'][0]}</th><th scope="col">{t['pth'][1]}</th><th scope="col">{t['pth'][2]}</th></tr></thead>
<tbody>{prs}</tbody>
</table>
<figure class="fig fig3" id="fig3">
<svg class="kt" id="kt" role="img" aria-labelledby="cap3"></svg>
<figcaption id="cap3">{t['cap3']}</figcaption>
</figure>
</section>

<section class="sec grid" id="implementazioni" data-k="{plain(t['ki'])}" aria-labelledby="h-implementazioni">
{TICKS}
<div class="runhead"><p class="kicker">{t['ki']}</p><p class="epi" aria-hidden="true">sm_61<br>sm_120</p></div>
<div class="sec-main"><h2 id="h-implementazioni">{t['hi']}</h2><p class="lead">{t['leadi']}</p></div>
<article class="proj withmeta">
<h3 class="h3m"><a href="{BW}">blackwell6000-qwen3.8-flash-next</a></h3>
<p class="dateline">{t['dlbw']}</p>
<dl class="meta"><div><dt>{t['md'][0]}</dt><dd>{t['mdv'][0]}</dd></div><div><dt>{t['md'][1]}</dt><dd>{t['mdv'][1]}</dd></div><div><dt>{t['md'][2]}</dt><dd>{t['mdv'][2]}</dd></div></dl>
<p>{t['bw']}</p>
</article>
<div class="briefs">
{brief("minicpm5-kernel-pascal", t['mc'], t['mcs'], GH + "minicpm5-kernel-pascal")}
{brief("bonsai2-ternary-pascal", t['bo2'], t['bo2s'], GH + "bonsai2-ternary-pascal")}
{brief("llm2vec-8gb-offload-lossless-batching", t['l2v'], t['m3'], GH + "llm2vec-8gb-offload-lossless-batching")}
</div>
<figure class="fig fig4" id="fig4">
<svg class="err" id="err" role="img" aria-labelledby="cap4"></svg>
<figcaption id="cap4">{t['cap4']}</figcaption>
</figure>
<div class="briefs">
{brief("lfm-to-kimodo", t['lfm'], t['lfms'], GH + "lfm-to-kimodo")}
{brief("bonsai-webgpu-tiled-vae-fix", t['bons'], t['bonss'], GH + "bonsai-webgpu-tiled-vae-fix")}
{brief("hildanext", t['hild'], t['hilds'], GH + "hildanext")}
</div>
</section>

<section class="sec grid" id="ricerca" data-k="{plain(t['kr'])}" aria-labelledby="h-ricerca">
{TICKS}
<div class="runhead"><p class="kicker">{t['kr']}</p></div>
<div class="sec-main"><h2 id="h-ricerca">{t['hr']}</h2><p class="lead">{t['leadr']}</p></div>
<table class="ptab coh">
<caption>{t['ccap']}</caption>
<thead><tr><th scope="col">{t['cth'][0]}</th><th scope="col">{t['cth'][1]}</th><th scope="col">{t['cth'][2]}</th></tr></thead>
<tbody>{coh}</tbody>
</table>
<article class="proj">
<p>{t['concl']}</p>
{go((BW + "/tree/main/cohere-probe", t['gor'][0]), ("https://github.com/wtogami/qwen-block-proxy-artifacts/issues/3", t['gor'][1]))}
</article>
<h3 class="sub">{t['hfh']}</h3>
<div class="briefs hfm">
{hfmodels}
</div>
</section>

<section class="sec grid" id="strumenti" data-k="{plain(t['ks'])}" aria-labelledby="h-strumenti">
{TICKS}
<div class="runhead"><p class="kicker">{t['ks']}</p><p class="epi" aria-hidden="true">127.0.0.1</p></div>
<div class="sec-main"><h2 id="h-strumenti">{t['hs']}</h2><p class="lead">{t['leads']}</p></div>
<article class="proj">
<h3><a href="{ORG}claude-plugins">claude-plugins</a></h3>
<p class="dateline">{t['dlcp']}</p>
<p>{t['cp']}</p>
<p class="cmd"><code>/plugin marketplace add Partido-De-What/claude-plugins</code><code>/plugin install chatroom@artyomita-plugins</code></p>
{go((ORG + "claude-plugins#chatroom-harness-point-by-point", t['gocp']))}
<p class="meth">{t['cps']}</p>
</article>
<article class="proj">
<h3><a href="{GH}vergilius">Vergilius</a></h3>
<p class="dateline">{t['dlv']}</p>
<p data-notes="n1">{t['verg']}</p>
</article>
{note(1, t['n1'])}
<figure class="fig fig5" id="fig5">
<svg class="f5" id="fence" role="img" aria-labelledby="cap5"></svg>
<figcaption id="cap5">{t['cap5']}</figcaption>
</figure>
<div class="briefs">
{brief("stt-whisper-pad", t['stt'], t['stts'], GH + "stt-whisper-pad")}
</div>
</section>

<section class="sec grid" id="sperimentali" data-k="{plain(t['kx'])}" aria-labelledby="h-sperimentali">
{TICKS}
<div class="runhead"><p class="kicker">{t['kx']}</p></div>
<div class="sec-main"><h2 id="h-sperimentali">{t['hx']}</h2><p class="lead" data-notes="n2">{t['lead1']}</p></div>
{note(2, t['n2'])}
<figure class="fig figr" id="fig1">
<div class="rbox"><canvas id="raster" role="img" aria-label="{t['rasterlabel']}"></canvas></div>
<p class="readout" id="readout" aria-hidden="true"></p>
{legend}
<figcaption>{t['cap1']}</figcaption>
</figure>
<figure class="fig fig2" id="fig2">
<svg class="cns" id="cns" role="img" aria-labelledby="cap2"></svg>
<figcaption id="cap2">{t['cap2']}</figcaption>
</figure>
<article class="proj">
<h3><a href="{GH}flytollm">FlyToLLM</a></h3>
<p class="dateline">{t['dl1']}</p>
<p data-notes="n3">{t['d1']}</p>
{go(("https://artyomita.github.io/flytollm/", t['go1']))}
<p class="meth">{t['m1']}</p>
</article>
{note(3, t['n3'])}
</section>

<section class="sec sec-sub grid" id="ml" data-k="{plain(t['k5'])}" data-nav="#sperimentali" aria-labelledby="h-ml">
{RULE}
<div class="runhead"><p class="kicker">{t['k5']}</p></div>
<div class="sec-main"><h2 id="h-ml">{t['h5s']}</h2><p class="lead">{t['lead5']}</p></div>
<article class="proj">
<h3><a href="{GH}fantaoracle">FantaOracle</a></h3>
<p class="dateline">{t['dl5']}</p>
<p data-notes="n4">{t['fo']}</p>
<p class="meth">{t['m5']}</p>
</article>
{note(4, t['n4'])}
<figure class="fig fig6" id="fig6">
<svg class="lots" id="lots" role="img" aria-labelledby="cap6"></svg>
<figcaption id="cap6">{t['cap6']}</figcaption>
</figure>
<div class="briefs">
{brief("fantacalcio-advisor", t['fca'], t['fcas'], GH + "fantacalcio-advisor")}
{brief("K-Forecast", t['kf'], t['kfs'], GH + "K-Forecast")}
{brief("sp500-predictability-lab", t['sp'], t['sps'], GH + "sp500-predictability-lab")}
{brief("storico", t['sto'], t['stos'], GH + "storico")}
</div>
</section>

<section class="sec sec-rl grid" id="rl" data-k="{plain(t['k6'])}" data-nav="#sperimentali" aria-labelledby="h-rl">
{RULE}
<div class="runhead"><p class="kicker">{t['k6']}</p></div>
<div class="sec-main"><h2 id="h-rl">{t['h6s']}</h2><p class="lead">{t['lead6']}</p></div>
<div class="briefs">
{brief("supermario-1-1-rl", t['sm'], t['sms'], GH + "supermario-1-1-rl")}
{brief("idle-isekai-trials", t['idle'], t['idles'], GH + "idle-isekai-trials")}
</div>
</section>

<section class="sec sec-idx grid" id="indice" data-k="{plain(t['hidx'])}" aria-labelledby="h-indice">
{RULE}
<div class="runhead"><p class="kicker">{t['kapp']}</p><p class="count">{idxm}</p></div>
<div class="idx">
<h2 id="h-indice">{t['hidx']}</h2>
<table>
<caption>{t['idxcap']}</caption>
<thead><tr><th scope="col">{t['ih'][0]}</th><th scope="col">{t['ih'][1]}</th><th scope="col">{t['ih'][2]}</th></tr></thead>
{idx}
</table>
</div>
</section>

<section class="sec sec-note grid" id="note" data-k="{plain(t['hnote'])}" aria-labelledby="h-note">
{RULE}
<div class="runhead"><h2 class="kicker" id="h-note">{t['hnote']}</h2></div>
<div class="sec-main"><p class="notetext">{t['note']}</p></div>
</section>

<section class="sec sec-aut grid" id="autore" data-k="{plain(t['haut'])}" aria-labelledby="h-autore">
<div class="runhead"><h2 class="kicker" id="h-autore">{t['haut']}</h2></div>
<div class="sec-main author">
<img src="{P}img/avatar-192.webp" width="96" height="96" alt="{t['avalt']}" loading="lazy" decoding="async">
<div><p class="aname">{NAME}</p>
<p class="arole">{t['role']}</p>
<p class="go"><a href="{GH.rstrip('/')}">GitHub</a><a href="{HF}">Hugging Face</a><a href="{LI}">LinkedIn</a><a href="{IG}">Instagram</a></p></div>
</div>
</section>

</div>
</div>
</main>

<footer class="foot wrap">
<p><span>{t['foot'][0]}</span><span>{t['foot'][1]}</span></p>
</footer>
</body>
</html>
"""
    return head + body


def minjs(src):
    """js/site.js (sorgente commentato) -> testo di js/site.min.js: via i commenti /* */, i rientri e le righe vuote.
    Il sorgente non ha commenti // ne' stringhe su piu' righe ne' "/*" dentro le stringhe; gli a capo restano (niente ASI da rifare)."""
    out = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return "\n".join(l.strip() for l in out.splitlines() if l.strip()) + "\n"


def write_js():
    src = open(os.path.join(ROOT, "js", "site.js"), encoding="utf-8").read()
    path = os.path.join(ROOT, "js", "site.min.js")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(minjs(src))
    return path


def write(lang, html):
    path = os.path.join(ROOT, "index.html") if lang == "it" else os.path.join(ROOT, "en", "index.html")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    return path


def bake(pages):
    """Incolla Fig. 3, 4, 5 e 6 al fotogramma finale nell'HTML (lettura senza JS)."""
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
            for lang, html in pages.items():
                pg = b.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
                pg.goto("http://127.0.0.1:%d/%s" % (port, "" if lang == "it" else "en/"))
                pg.evaluate("document.fonts.ready")
                pg.wait_for_timeout(300)
                pg.evaluate("document.getElementById('fig2').scrollIntoView()")
                pg.wait_for_timeout(300)
                pd = pg.evaluate("document.querySelector('.pd').textContent")
                assert pd == PD[lang], "PD statico %s diverso da quello calcolato %s" % (PD[lang], pd)
                for sid in ("kt", "err", "fence", "lots"):
                    # le figure si costruiscono solo vicino alla vista: la si porta in vista prima di leggerla
                    pg.evaluate("(id)=>document.getElementById(id).scrollIntoView({block:'center'})", sid)
                    pg.wait_for_timeout(400)
                    inner = pg.evaluate("(id)=>{var s=document.getElementById(id);return [s.getAttribute('viewBox'),s.innerHTML,s.getAttribute('class')]}", sid)
                    assert inner[0] and "style=" not in inner[1], sid
                    html = re.sub(r'(<svg [^>]*id="%s"[^>]*)></svg>' % sid,
                                  lambda mm: '%s viewBox="%s">%s</svg>' % (re.sub(r'class="[^"]*"', 'class="%s"' % inner[2], mm.group(1)), inner[0], inner[1]), html)
                pages[lang] = html
                pg.close()
            b.close()
    finally:
        srv.shutdown()
    for lang, html in pages.items():
        write(lang, html)


if __name__ == "__main__":
    pages = {}
    for lang in ("it", "en"):
        pages[lang] = page(T[lang])
        print(write(lang, pages[lang]), len(pages[lang].encode("utf-8")))
    open(os.path.join(ROOT, ".nojekyll"), "w").close()
    js = write_js()
    print(js, os.path.getsize(js))
    print("CSP hash sha256-" + BOOT_HASH)
    if "--bake" in sys.argv:
        bake(pages)
        for lang in pages:
            print("bake", lang, len(pages[lang].encode("utf-8")))
