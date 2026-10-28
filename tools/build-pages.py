"""Genera index.html (italiano) e en/index.html (inglese) dallo stesso modello.

Stessa struttura e stessi id nelle due pagine; cambiano solo i testi. Le visualizzazioni (barre, celle, scala logaritmica)
sono HTML e CSS scritti qui, senza immagini. I numeri dei modelli Hugging Face (colonna a sinistra) vengono da
tools/hf-models.json: aggiornarli con tools/hf-models.py.

Uso:  python tools/build-pages.py
"""
import base64
import hashlib
import importlib.util
import os
import math
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://artyomita.github.io/"
GH = "https://github.com/ArtyomITA/"
GUIDE = GH + "nvidia-gtx1080-sm61-ai-full-guide"
GUIDE_H3 = GUIDE + "/blob/main/docs/06-diffusion-image-and-motion.md#64-video-and-image-generation-minimax-h3-on-8-gb"
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

# tema scuro se non c'e' una scelta salvata; "auto" segue il sistema
BOOT = "(function(d){d.className='js';try{var t=localStorage.getItem('ai-theme');if(t==='auto')t=matchMedia('(prefers-color-scheme: light)').matches?'light':'dark';if(t==='light')d.setAttribute('data-theme','light')}catch(e){}})(document.documentElement);"
BOOT_HASH = base64.b64encode(hashlib.sha256(BOOT.encode("utf-8")).digest()).decode()
# style-src-attr: gli attributi style="--w:.71" delle barre e delle celle; nessuno script inline oltre al boot
CSP = ("default-src 'self'; script-src 'self' 'sha256-%s'; style-src 'self'; style-src-attr 'unsafe-inline'; img-src 'self' data:; "
       "font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'") % BOOT_HASH


def _hf():
    sys.dont_write_bytecode = True  # niente __pycache__ nel repository del sito
    spec = importlib.util.spec_from_file_location("hfm", os.path.join(ROOT, "tools", "hf-models.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


hfm = _hf()


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
    return '<span class="lsh"><i style="--p:%d%%"></i>%s %d%%</span>' % (pc, lg, pc)


# neuroni per punto della figura FlyToLLM: 166.700 diviso i punti generati da js/site.js (seme 166700); check.py lo ricontrolla
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
    
    # Contributi upstream
    kc="Contributi upstream", hc="Quattro patch in quattro progetti",
    leadc="Patch piccole inviate ai repository originali. Due sono integrate, una è aperta e un mio commit è stato adottato in una PR di vLLM.",
    prows=[("leejet/stable-diffusion.cpp", '<a href="%s">PR #2202</a>: fix, ignora l\'alpha dei metadati nei LoRA con baked_scale.' % PR_SD, "integrata il 24/10/2026"),
           ("PrismML-Eng/llama.cpp", '<a href="%s">PR #368</a>: Pascal (sm_61), mat-vec PQ2_0 per 1-4 colonne, ' % PR_PRISM + m("+17%") + " su Ternary-Bonsai-2-9B con output identico bit per bit.", "integrata il 19/10/2026"),
           ("ggml-org/llama.cpp", '<a href="%s">PR #27721</a>: CUDA Graphs su Pascal (sm_61), ' % PR + m("+40%") + " sui modelli MoE, " + m("+7%") + " sui modelli densi, nessuna regressione.", "aperta dal 25/08/2026"),
           ("vllm-project/vllm", '<a href="%s">PR #58863</a>: il commit esatto del replay GDN di RecoverSSM, proposto da me e adottato nella PR (commit 514102a).' % PR_VLLM, "adottato, PR ancora aperta")],
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
    fk="(fork)", pra="PR #27721 aperta", prb="PR #2202 integrata", org="Partido-De-What", cdir="cartella di blackwell6000",
    hnote="Nota sulle figure",
    note='Tutte le figure sono calcolate in questa pagina con canvas e SVG scritti a mano, senza immagini né librerie. I generatori pseudo-casuali hanno seme fisso (27721, il numero della PR, per <a href="#fig3">Fig. 1</a> e <a href="#fig1">Fig. 4</a>; 166700, il numero di neuroni, per <a href="#fig2">Fig. 5</a>), quindi ogni lettore vede lo stesso disegno. Lo scorrimento è un ingresso: in Fig. 4 alza la corrente sensoriale, nelle altre fa avanzare la figura, che torna indietro se si risale. Con la riduzione del movimento attiva ogni figura mostra un solo fotogramma scelto. Fig. 1, 4 e 5 sono schemi; <a href="#fig4">Fig. 2</a>, <a href="#fig5">Fig. 3</a> e <a href="#fig6">Fig. 6</a> riportano numeri misurati; i numeri di testo, didascalie e tabelle vengono dai repository e dalle pagine delle PR.',
    haut="L'autore", avalt="Avatar GitHub di " + NAME, 
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
    
    kc="Upstream contributions", hc="Four patches in four projects",
    leadc="Small patches sent to the original repositories. Two are merged, one is open and a commit of mine was adopted in a vLLM PR.",
    prows=[("leejet/stable-diffusion.cpp", '<a href="%s">PR #2202</a>: fix, skip the metadata alpha for LoRAs with baked_scale.' % PR_SD, "merged 24 Oct 2026"),
           ("PrismML-Eng/llama.cpp", '<a href="%s">PR #368</a>: Pascal (sm_61), PQ2_0 mat-vec for 1-4 columns, ' % PR_PRISM + m("+17%") + " on Ternary-Bonsai-2-9B with bit-identical output.", "merged 19 Oct 2026"),
           ("ggml-org/llama.cpp", '<a href="%s">PR #27721</a>: CUDA Graphs on Pascal (sm_61), ' % PR + m("+40%") + " on MoE models, " + m("+7%") + " on dense models, no regression.", "open since 25 Aug 2026"),
           ("vllm-project/vllm", '<a href="%s">PR #58863</a>: the exact commit of the RecoverSSM GDN replay, proposed by me and adopted in the PR (commit 514102a).' % PR_VLLM, "adopted, PR still open")],
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
    fk="(fork)", pra="PR #27721 open", prb="PR #2202 merged", org="Partido-De-What", cdir="folder of blackwell6000",
    hnote="A note on the figures",
    note='Every figure is computed in this page with hand-written canvas and SVG, with no images or libraries. The pseudo-random generators have fixed seeds (27721, the PR number, for <a href="#fig3">Fig. 1</a> and <a href="#fig1">Fig. 4</a>; 166700, the neuron count, for <a href="#fig2">Fig. 5</a>), so every reader sees the same drawing. Scrolling is an input: in Fig. 4 it raises the sensory current, in the others it advances the figure, which rewinds if you scroll back. With reduced motion on, each figure shows a single chosen frame. Fig. 1, 4 and 5 are schematics; <a href="#fig4">Fig. 2</a>, <a href="#fig5">Fig. 3</a> and <a href="#fig6">Fig. 6</a> plot measured numbers; the numbers in the text, captions and tables come from the repositories and the PR pages.',
    haut="About the author", avalt="GitHub avatar of " + NAME, 
    foot=("no trackers, no ads", "home-made page"),
)


# testi nuovi del design (numeri e didascalie dei grafici, hero, nota); sostituiscono le chiavi con lo stesso nome
NEW = {}
NEW["it"] = dict(
    thtitle=("Tema chiaro", "Tema scuro", "Tema automatico (come il sistema)"),
    ogimgalt="Il nome Adrian Ciprian Iancu in grande su fondo scuro, la riga del ruolo e una griglia luminosa di unità di calcolo di una GPU.",
    stats=[('4×<span class="cn">227</span>k', "token di contesto, 4 utenti su una sola GPU", BW, "repo blackwell6000"),
           ('~<span class="cn">100</span>', "tok/s per utente, Qwen3.8 Flash-Next su Blackwell", BW, "repo blackwell6000"),
           ('+<span class="cn">51</span>%', "in decode, Ternary Bonsai 2 9B su GTX&nbsp;1080", GH + "bonsai2-ternary-pascal", "repo bonsai2"),
           ('+<span class="cn">40</span>%', "sui modelli MoE in llama.cpp su Pascal", PR, "PR #27721, aperta")],
    kt_t="CUDA Graphs su sm_61 in llama.cpp, PR #27721", kt_ax="tempo per token, relativo", kt_moe="MoE", kt_dense="denso", kt_a="un lancio per kernel", kt_b="CUDA graph",
    kt_cap="Schema, non traccia di profilazione: stessi kernel, un solo lancio del grafo al posto di uno per kernel. Il tempo per token scende a 1/1,40 sui modelli MoE (+40% misurato) e a 1/1,07 sui densi (+7%).",
    er_t="Embedding di LLM2Vec calcolati in batch, distanza dal riferimento", er_ax="1 − coseno, scala logaritmica", er_big="volte più vicino",
    er_a="padding · cos 0,76", er_a2="1 − cos = 0,24", er_b="fix · cos 0,999956", er_b2="1 − cos = 4,4·10<sup>−5</sup>",
    fe_t="Vergilius su GTX&nbsp;1080", fe_speed="tok/s su GTX 1080", fe_dec="decodifica", fe_dr="con drafter", fe_turns="turni con cifre non supportate",
    fe_tag="GTX 1080 · nessuna chiamata esterna",
    lo_t="martelletti rigiocati contro il server · una cella ciascuno", lo_big="senza errori, in entrambi gli ordini dei ruoli", lo_lat="tempo di risposta a ogni martelletto, in millisecondi",
    lo_o=("ordine 1", "ordine 2"), lo_v=("media 102,7 · p95 249,1 · max 354,3", "media 95,6 · p95 254,0 · max 348,6"),
    lo_br="ponte FantaAsta Live · assegnazioni identiche",
    fly_label="Illustrazione del sistema nervoso centrale di Drosophila: nuvola di punti con un'onda di attività che parte dalle porte d'ingresso e avanza un salto alla volta fino ai quadratini di lettura.",
    fly_leg=("porte d'ingresso (sensoriali)", "neuroni, per salti dalle porte", "lettura (discendenti)"),
    fly_cap='Illustrazione generata in questa pagina dentro la sagoma del sistema nervoso centrale (cervello, lobi ottici, cordone ventrale): ogni punto vale circa <span class="pd">' + PD["it"] + '</span> neuroni. I punti coralli, più grandi, sono le porte d\'ingresso, sul bordo dei lobi ottici e sul dorso del cervello; da lì un\'onda avanza un salto alla volta e la luce segue la distanza in salti. I quadratini sono il readout: nel connettoma vero sta a 2 salti dalle porte, per questo la profondità 4+4 basta.',
    note="I grafici sono disegnati in questa pagina con HTML, CSS e canvas, senza immagini. La scena 3D in testa, fatta con three.js, è un'illustrazione di token che attraversano le unità di calcolo di una GPU: non è una misura e non parte con la riduzione del movimento attiva. Anche la figura di FlyToLLM è un'illustrazione: i punti nascono da un seme fisso (166700, il numero di neuroni), quindi ogni lettore vede lo stesso disegno. Il grafico dei CUDA Graphs è uno schema; quelli su LLM2Vec, Vergilius e FantaOracle riportano numeri misurati. I numeri nei testi vengono dai repository e dalle pagine delle PR.",
)
NEW["en"] = dict(
    thtitle=("Light theme", "Dark theme", "Auto theme (follow the system)"),
    ogimgalt="The name Adrian Ciprian Iancu set large on a dark background, the role line and a glowing grid of GPU compute units.",
    stats=[('4×<span class="cn">227</span>k', "context tokens, 4 users on a single GPU", BW, "blackwell6000 repo"),
           ('~<span class="cn">100</span>', "tok/s per user, Qwen3.8 Flash-Next on Blackwell", BW, "blackwell6000 repo"),
           ('+<span class="cn">51</span>%', "decode, Ternary Bonsai 2 9B on a GTX&nbsp;1080", GH + "bonsai2-ternary-pascal", "bonsai2 repo"),
           ('+<span class="cn">40</span>%', "on MoE models in llama.cpp on Pascal", PR, "PR #27721, open")],
    kt_t="CUDA Graphs on sm_61 in llama.cpp, PR #27721", kt_ax="time per token, relative", kt_moe="MoE", kt_dense="dense", kt_a="one launch per kernel", kt_b="CUDA graph",
    kt_cap="A schematic, not a profiling trace: same kernels, one graph launch instead of one per kernel. Time per token drops to 1/1.40 on MoE models (+40% measured) and to 1/1.07 on dense models (+7%).",
    er_t="Batched LLM2Vec embeddings, distance from the reference", er_ax="1 − cosine, logarithmic scale", er_big="times closer",
    er_a="padding · cos 0.76", er_a2="1 − cos = 0.24", er_b="fix · cos 0.999956", er_b2="1 − cos = 4.4·10<sup>−5</sup>",
    fe_t="Vergilius on a GTX&nbsp;1080", fe_speed="tok/s on GTX 1080", fe_dec="decoding", fe_dr="with drafter", fe_turns="turns with unsupported numbers",
    fe_tag="GTX 1080 · no external calls",
    lo_t="hammer calls replayed against the server · one cell each", lo_big="with no errors, in both role orders", lo_lat="response time of each hammer call, in milliseconds",
    lo_o=("order 1", "order 2"), lo_v=("mean 102.7 · p95 249.1 · max 354.3", "mean 95.6 · p95 254.0 · max 348.6"),
    lo_br="FantaAsta Live bridge · identical assignments",
    fly_label="Illustration of the Drosophila central nervous system: a cloud of dots with a wave of activity that starts at the input ports and advances one hop at a time to the readout squares.",
    fly_leg=("input ports (sensory)", "neurons, by hops from the ports", "readout (descending)"),
    fly_cap='An illustration generated in this page inside the outline of the central nervous system (brain, optic lobes, ventral nerve cord): each dot stands for about <span class="pd">' + PD["en"] + '</span> neurons. The larger coral dots are the input ports, on the rim of the optic lobes and along the top of the brain; from there a wave advances one hop at a time and the light follows the distance in hops. The small squares are the readout: in the real connectome it sits 2 hops from the ports, which is why 4+4 depth is enough.',
    note="The charts are drawn in this page with HTML, CSS and canvas, with no images. The 3D scene at the top, built with three.js, is an illustration of tokens flowing through the compute units of a GPU: it is not a measurement, and it does not start when reduced motion is on. The FlyToLLM figure is an illustration too: the dots come from a fixed seed (166700, the neuron count), so every reader sees the same drawing. The CUDA Graphs chart is a schematic; the ones on LLM2Vec, Vergilius and FantaOracle plot measured numbers. The numbers in the text come from the repositories and the PR pages.",
)
NEW["it"].update(dict(
    ov_k="In questa pagina", ov_pin="In evidenza", ov_idx="Indice e contatti",
    ov_l=("Assistente OSINT locale · 64 tok/s su GTX 1080", "Tutto quello che gira veloce su una GTX 1080, misurato e con le fonti", "4 PR in 4 progetti · 2 integrate",
          "%d progetti, dalla GTX 1080 alla RTX PRO 6000", "Replica del test Cohere · %d modelli su Hugging Face", "claude-plugins · stt-whisper-pad", "FlyToLLM, ML applicato, ambienti RL",
          "%d repository · %d aree · contatti"),
    pin_b=("In evidenza", "OSINT", "locale"), pin_s="Assistente OSINT locale",
    pin_p1="Un assistente locale che mette insieme un modello linguistico sulla scheda video, fonti aperte per capire cosa succede nel mondo e un'interfaccia che le tiene insieme. Interroga da solo le fonti quando la domanda lo richiede: notizie per soggetto e luogo, mercati, contratti militari, movimenti degli insider, mappe, archivio storico degli eventi. Lavora sul computer (file, terminale, browser, documenti) e ricorda: memorie, documenti indicizzati, procedure che impara e riusa.",
    pin_p2="Nessuna chiave API verso fornitori di AI e nessuna conversazione che esce dal computer. Pensato per macchine modeste: modello predefinito LFM2.5-2.6B con drafter speculativo DSpark su una GTX&nbsp;1080 con 8&nbsp;GB. Un controllo contro le invenzioni verifica che numeri e nomi della risposta compaiano nei risultati degli strumenti. Integra Odysseus (assistente) e ShadowBroker (fonti).<sup class=\"n\">1</sup>",
    pin_lab="Ottimizzazione custom per la GTX 1080",
    pin_st=(('<span class="cn">64</span>', "tok/s in decodifica"), ("78-100", "tok/s con il drafter"), ('<span class="cn">8</span>&nbsp;GB', "di memoria video bastano"), ("1/36", "turni con cifre non supportate, prima 3/35")),
    pin_go="Repository su GitHub",
    vref="Assistente OSINT locale, in evidenza in cima alla pagina.",
    gd_b=("In evidenza", "Guida"), gd_t="NVIDIA GTX 1080 (sm_61) AI Full Guide",
    gd_s="Tutto quello che ho fatto girare veloce su una GPU del 2016 con 8&nbsp;GB, misurato e con le fonti.",
    gd_rows=("LoRA ternario, addestramento per esempio", "MiniMax-H3, clip di prova", "MiniCPM5-2B, decodifica", "Attention int8, kernel di H3", "Ternary Bonsai 2 9B, decodifica", "CUDA graphs, MoE Ling-3.0-tiny"),
    gd_ax="la lunghezza della barra è il rapporto tra prima e dopo",
    gd_chips=("kernel llama.cpp", "decoding speculativo", "quantizzazione", "8 GB", "LoRA", "video diffusion", "speech"),
    gd_go="Apri la guida su GitHub",
    h3_t="MiniMax H3 su GTX&nbsp;1080", h3_dl="video e audio generativi su 8&nbsp;GB · codice in uscita",
    h3_meta=("GPU", "GTX 1080, 8&nbsp;GB", "Stack", "stable-diffusion.cpp · CUDA", "Clip di prova", "320x576, 39 fotogrammi"),
    h3_p1="MiniMax-H3 è un transformer a diffusione che genera video con audio sincronizzato. Qui solo testo e numeri: nessun fotogramma generato. Sulla clip di prova da 39 fotogrammi il tempo scende da <span class=\"m\">674,5</span> a <span class=\"m\">175,5&nbsp;s</span> (<span class=\"m\">−74%</span>): pesi letti dal disco in sovrapposizione al calcolo, VAE a gruppi di tile, ricetta Q3 con turbo.",
    h3_p2="Il kernel di attention int8 con DP4A passa da <span class=\"m\">1875</span> a <span class=\"m\">944&nbsp;ms</span> (<span class=\"m\">2,0x</span>), senza differenze visibili da f32 su più seed.",
    h3_sp="L'attention sparsa a blocchi ha due misure distinte:",
    h3_sp1=("su una clip da 15 s, senza il prefisso: <span class=\"m\">1,65x</span> sui passi turbo (da 397-404 a 240-245 s per passo);",
            "il prefisso di condizionamento, sempre visibile, conserva il parlato. Misurato a parte su clip più corte (56 fotogrammi): errore sulle parole <span class=\"m\">0</span> a 544x960 e <span class=\"m\">0,2</span> a 384x672, contro <span class=\"m\">1,0</span> con la sola attention sparsa."),
    h3_p3="Il fix LoRA <code>baked_scale</code> è integrato (<a href=\"" + PR_SD + "\">PR #2202</a> di stable-diffusion.cpp). Il resto del codice è in uscita.",
    h3_go="Sezione della guida su H3",
))
NEW["en"].update(dict(
    ov_k="On this page", ov_pin="Pinned", ov_idx="Index and contacts",
    ov_l=("Local OSINT assistant · 64 tok/s on a GTX 1080", "Everything that runs fast on a GTX 1080, measured and sourced", "4 PRs in 4 projects · 2 merged",
          "%d projects, from the GTX 1080 to the RTX PRO 6000", "Cohere test replication · %d models on Hugging Face", "claude-plugins · stt-whisper-pad", "FlyToLLM, applied ML, RL environments",
          "%d repositories · %d areas · contacts"),
    pin_b=("Pinned", "OSINT", "local"), pin_s="Local OSINT assistant",
    pin_p1="A local assistant that combines a language model on the graphics card, open sources to see what is going on in the world, and an interface that ties them together. It queries the sources by itself when a question needs them: news by subject and place, markets, military contracts, insider moves, maps, a historical archive of events. It works on the computer (files, terminal, browser, documents) and remembers: memories, indexed documents, procedures it learns and reuses.",
    pin_p2="No API keys for AI providers and no conversation leaves the computer. Built for modest machines: default model LFM2.5-2.6B with the DSpark speculative drafter on a GTX&nbsp;1080 with 8&nbsp;GB. A check against made-up answers verifies that the numbers and names in a reply appear in the tool results. It integrates Odysseus (assistant) and ShadowBroker (sources).<sup class=\"n\">1</sup>",
    pin_lab="Custom optimization for the GTX 1080",
    pin_st=(('<span class="cn">64</span>', "tok/s decoding"), ("78-100", "tok/s with the drafter"), ('<span class="cn">8</span>&nbsp;GB', "of video memory is enough"), ("1/36", "turns with unsupported numbers, down from 3/35")),
    pin_go="Repository on GitHub",
    vref="Local OSINT assistant, pinned at the top of the page.",
    gd_b=("Pinned", "Guide"), gd_t="NVIDIA GTX 1080 (sm_61) AI Full Guide",
    gd_s="Everything I made run fast on a 2016 GPU with 8&nbsp;GB, measured and sourced.",
    gd_rows=("Ternary LoRA, training per example", "MiniMax-H3, test clip", "MiniCPM5-2B, decoding", "Int8 attention, H3 kernel", "Ternary Bonsai 2 9B, decoding", "CUDA graphs, MoE Ling-3.0-tiny"),
    gd_ax="bar length is the before/after ratio",
    gd_chips=("llama.cpp kernels", "speculative decoding", "quantization", "8 GB", "LoRA", "video diffusion", "speech"),
    gd_go="Open the guide on GitHub",
    h3_t="MiniMax H3 on a GTX&nbsp;1080", h3_dl="generative video and audio on 8&nbsp;GB · code release pending",
    h3_meta=("GPU", "GTX 1080, 8&nbsp;GB", "Stack", "stable-diffusion.cpp · CUDA", "Test clip", "320x576, 39 frames"),
    h3_p1="MiniMax-H3 is a diffusion transformer that generates video with synchronised audio. Text and numbers only here: no generated frames. On the 39-frame test clip the time drops from <span class=\"m\">674.5</span> to <span class=\"m\">175.5&nbsp;s</span> (<span class=\"m\">−74%</span>): weights read from disk overlapped with the compute, VAE in tile groups, Q3 recipe with turbo.",
    h3_p2="The int8 DP4A attention kernel goes from <span class=\"m\">1875</span> to <span class=\"m\">944&nbsp;ms</span> (<span class=\"m\">2.0x</span>), with no visible difference from f32 on several seeds.",
    h3_sp="Block-sparse attention has two separate measurements:",
    h3_sp1=("on a 15 s clip, without the prefix: <span class=\"m\">1.65x</span> on the turbo steps (397-404 down to 240-245 s per step);",
            "the always-visible conditioning prefix keeps the speech. Measured separately on shorter clips (56 frames): word error rate <span class=\"m\">0</span> at 544x960 and <span class=\"m\">0.2</span> at 384x672, against <span class=\"m\">1.0</span> with pure sparse attention."),
    h3_p3="The LoRA <code>baked_scale</code> fix is merged (<a href=\"" + PR_SD + "\">PR #2202</a> in stable-diffusion.cpp). The rest of the code is on its way.",
    h3_go="Guide section on H3",
))
for _l, _t in T.items():
    _t.update(NEW[_l])
    _t["n4"] = _t["n4"].replace(": @@F@@", "")

# identificatori e intervalli che non devono andare a capo sul trattino (Qwen3- / 0.6B, 78- / 100)
NB = ["Qwen3-0.6B", "Llama-3-8B", "male-cns:v1.0", "78-100", "Speech-to-text", "LFM2.5-2.6B", "Bonsai-Image", "Qwen3.8-Flash-Next",
      "shader-f16", "AGPL-3.0", "CC-BY", "1-1", "text-to-motion", "8-billion-parameter", "Ternary-Bonsai-2-9B", "LFM2.5-Embedding-350M", "Apache-2.0", "MiniCPM5-2B", "1-4"]
# chiavi che finiscono dentro attributi (meta, aria-label, alt, title) o non sono testo: niente <span>
ATTR = {"desc", "ogimgalt", "fly_label", "avalt", "thtitle", "th", "nav", "navnote", "langlabel", "themelabel", "navlabel", "skip", "toc", "stats", "lang", "ogloc", "ogalt", "canon", "P", "og"}


def plain(x):
    """testo senza tag, per gli attributi"""
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


def strip(cap):
    """didascalia senza il prefisso "Fig. N." / "Tab. N." """
    return re.sub(r"^<b>[^<]*</b>\s*", "", cap)


def frac(s):
    s = s.replace(",", ".")
    if "/" in s:
        a, b = s.split("/")
        return float(a) / float(b)
    return float(s.rstrip("%")) / 100


def stack(s):
    """"Python · C++ · CUDA; llama.cpp" -> etichette per la parte prima del punto e virgola, il resto in grigio"""
    a, _, b = s.partition(";")
    chips = "".join('<span class="chip">%s</span>' % x.strip() for x in a.split("·") if x.strip())
    return '<p class="bf">%s%s</p>' % (chips, (' <span class="rel">%s</span>' % b.strip()) if b.strip() else "")


def hb(label, w, val, tone="", seg=False, l=None, marks="", d=0, cls=""):
    st = "--w:%.4f" % w + (";--l:%.4f" % l if l is not None else "") + (";--d:%d" % d if d else "")
    return ('<div class="hb %s%s"><span class="hb-l">%s</span><span class="hb-t"><i%s style="%s"></i>%s</span><span class="hb-v">%s</span></div>'
            % (tone, (" " + cls) if cls else "", label, ' class="seg"' if seg else "", st, marks, val))


def cells(n, bad=(), out=()):
    return "".join('<i%s style="--i:%d"></i>' % (' class="x"' if i in bad else ' class="o"' if i in out else "", i) for i in range(n))


def page(t):
    L = t["lang"]
    P = t["P"]
    dec = "," if L == "it" else "."
    fx = lambda v, k=2: ("%." + str(k) + "f") % v
    num = lambda v, k=2: fx(v, k).replace(".", dec)
    nav = "".join('<a href="%s">%s</a>' % (h, s) for h, s in nav_items(t))
    toc = "".join('<li><a href="%s">%s</a></li>' % (h, s) for h, s in nav_items(t) + [("#note", t["navnote"])])
    it_href, en_href = ("./", "en/") if L == "it" else ("../", "./")
    # Versione inglese: per toglierla cancellare la cartella en/, il blocco .lang e i tre <link rel="alternate"> nel head.
    lang_nav = ('<nav class="lang" aria-label="%s"><a href="%s" hreflang="it" lang="it"%s>IT</a><span aria-hidden="true">/</span><a href="%s" hreflang="en" lang="en"%s>EN</a></nav>'
                % (t["langlabel"], it_href, ' aria-current="page"' if L == "it" else "", en_href, ' aria-current="page"' if L == "en" else ""))
    theme = ('<div class="theme" role="group" aria-label="%s">' % t["themelabel"]
             + "".join('<button type="button" data-set="%s" aria-pressed="false" aria-label="%s">%s</button>' % (k, t["thtitle"][i], t["th"][i])
                       for i, k in enumerate(("light", "dark", "auto")))
             + '</div>')

    def head(n, kick, h2, hid, lead=""):
        return ('<header class="sec-h rv"><p class="kick"><span>%s</span><i></i>%s</p><h2 id="h-%s">%s</h2>%s</header>'
                % (n, plain(kick), hid, h2, ('<p class="lead">%s</p>' % lead) if lead else ""))

    def go(*links):
        return '<p class="go">' + "".join('<a href="%s">%s</a>' % (h, s) for h, s in links) + "</p>"

    def brief(name, desc, st, href):
        return '<article class="brief card tilt rv"><h3 class="bn"><a href="%s">%s</a></h3><p>%s</p>%s</article>' % (href, name, desc, stack(st))

    def note(n, text):
        return '<p class="fn" id="n%d"><sup class="n">%d</sup>%s</p>' % (n, n, text)

    def fig(fid, title, big, body, cap):
        return ('<figure class="viz card rv" id="%s"><div class="viz-h"><p class="viz-t">%s</p>%s</div>%s<figcaption>%s</figcaption></figure>'
                % (fid, title, big, body, cap))

    # contributi: linea del tempo con lo stato di ogni PR (integrata, adottata, aperta)
    kinds = ("ok", "ok", "open", "adopt")
    prs = "".join('<li class="st-%s-i rv" style="--d:%d"><article class="pr card"><div class="pr-h"><span class="pj">%s</span><span class="st st-%s">%s</span></div><p>%s</p></article></li>'
                  % (k, i * 60, r[0], k, r[2], r[1]) for i, (k, r) in enumerate(zip(kinds, t["prows"])))
    ktrows = ""
    for i, (nm, v) in enumerate(((t["kt_moe"], 1 / 1.40), (t["kt_dense"], 1 / 1.07))):
        ktrows += ('<div class="vz-g"><p class="vz-lab">%s</p>%s%s</div>'
                   % (nm, hb(t["kt_a"], 1, "1×", "hb-n", True, d=i * 180), hb(t["kt_b"], round(v, 2), num(round(v, 2)) + "×", "", True, d=i * 180 + 160)))
    kt = fig("kt", t["kt_t"] + ' <span class="rel">· ' + t["kt_ax"] + "</span>",
             '<div class="big"><div><b>+<span class="cn">40</span>%%</b><span>%s</span></div><div><b>+<span class="cn">7</span>%%</b><span>%s</span></div></div>' % (t["kt_moe"], t["kt_dense"]),
             ktrows, t["kt_cap"])

    # implementazioni
    err_ax = "".join('<span style="--p:%s">%s</span>' % (p, "1" if k == 0 else "10<sup>−%d</sup>" % k) for k, p in enumerate(("0", ".2", ".4", ".6", ".8", "1")))
    err = fig("err", t["er_t"], '<div class="big"><div><b>≈ <span class="cn">%s</span></b><span>%s</span></div></div>' % ("5.500" if L == "it" else "5,500", t["er_big"]),
              '<div class="ls" style="--a:.124;--b:.871"><p class="ls-n a" style="--p:.124"><b>%s</b>%s</p><p class="ls-n b" style="--p:.871"><b>%s</b>%s</p>'
              '<div class="ls-t"><i></i><u class="a" style="--p:.124"></u><u class="b" style="--p:.871"></u></div><div class="ls-ax" aria-hidden="true">%s</div></div><p class="ls-u">%s</p>'
              % (t["er_a"], t["er_a2"], t["er_b"], t["er_b2"], err_ax, t["er_ax"]), strip(t["cap4"]))
    meta = '<dl class="meta">' + "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (a, b) for a, b in zip(t["md"], t["mdv"])) + "</dl>"

    # ricerca
    trials = "".join('<li class="rv"><p>%s</p>%s%s</li>' % (lb, hb("base", frac(a), a, "hb-n", d=0), hb("Swift", frac(b), b, "", d=140)) for lb, a, b in t["crows"])
    hfmodels = "".join(brief(i, d, s, "https://huggingface.co/adriandj3/" + i) for i, d, s in t["hfm"])

    # strumenti: velocita' e turni con cifre non supportate
    fence = fig("fence", t["fe_t"], '<span class="viz-tag">%s</span>' % t["fe_tag"],
                '<div class="cols2"><div class="vz-g"><p class="vz-lab">%s</p>%s%s</div><div class="vz-g"><p class="vz-lab">%s</p><div class="pairs">'
                '<div><span class="v">3/35</span><div class="wf" style="--cols:7;--mw:190px">%s</div></div><span class="arr" aria-hidden="true"></span>'
                '<div><span class="v">1/36</span><div class="wf" style="--cols:6;--mw:190px">%s</div></div></div></div></div>'
                % (t["fe_speed"], hb(t["fe_dec"], 64 / 110, "64", "hb-n", d=0), hb(t["fe_dr"], 22 / 110, "78-100", "", l=78 / 110, d=160),
                   t["fe_turns"], cells(35, bad=(9, 20, 31)), cells(36, bad=(22,))), strip(t["cap5"]))

    # machine learning applicato: FantaOracle contro il proprio server
    lat = ""
    for i, (lb, v, (mean, p95, mx)) in enumerate(zip(t["lo_o"], t["lo_v"], ((102.7, 249.1, 354.3), (95.6, 254.0, 348.6)))):
        mk = '<u style="--p:%.4f"></u><u class="mean" style="--p:%.4f"></u>' % (p95 / 400, mean / 400)
        lat += hb(lb, mx / 400, v, "hb-soft", marks=mk, d=i * 160, cls="hb-s")
    scale = '<div class="sc" aria-hidden="true">' + "".join("<span>%s</span>" % x for x in ("0", "100", "200", "300", "400 ms")) + "</div>"
    lots = fig("lots", t["lo_t"], '<div class="big"><div><b><span class="cn">250</span>/250</b><span>%s</span></div></div>' % t["lo_big"],
               '<div class="wf wf-250">%s</div><div class="vz-g" style="margin-top:28px"><p class="vz-lab">%s</p>%s%s</div><div class="vz-g"><p class="vz-lab">%s</p><div class="wf wf-44">%s</div><p class="ls-u">43/44</p></div>'
               % (cells(250), t["lo_lat"], lat, scale, t["lo_br"], cells(44, out=(43,))), strip(t["cap6"]))

    # indice dei repository
    def idx_row(name, st, nt="", fork=False, url=None):
        cell = '<span class="nmw"><a class="nm" href="%s">%s</a>%s</span>' % (url or (GH + name), name, (' <span class="fk">%s</span>' % t["fk"]) if fork else "")
        return '<li>%s<span class="sk">%s</span>%s<span class="nt">%s</span></li>' % (cell, st, "" if fork else lsh(name), nt)

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
    idx = "".join('<div class="idx-c card rv"><h3><a href="#%s">%s</a></h3><ul>%s</ul></div>' % (i, lb, "".join(rs)) for i, lb, rs in groups)
    nrows = sum(len(rs) for _, _, rs in groups)
    idxm = ("%d voci · %d aree" if L == "it" else "%d entries · %d areas") % (nrows, len(groups))
    kw = "".join('<span class="chip">%s</span>' % k.strip() for k in re.split(r"[;,](?![^(]*\))", t["kw"].rstrip(".")) if k.strip())

    # panoramica: un riquadro per sezione (i primi due sono i progetti fissati in alto)
    na = len(groups[1][2]) + 1  # i sette repository dell'indice piu' H3, che non ha ancora un repository
    lines = t["ov_l"]
    ov_t = [("vergilius", t["ov_pin"], "Vergilius", lines[0]), ("guida", t["ov_pin"], t["gd_t"], lines[1]), ("contributi", "01", t["kc"], lines[2]),
            ("implementazioni", "02", t["ki"], lines[3] % na), ("ricerca", "03", t["kr"], lines[4] % len(t["hfm"])), ("strumenti", "04", t["ks"], lines[5]),
            ("sperimentali", "05", t["kx"], lines[6]), ("indice", "06", t["ov_idx"], lines[7] % (nrows, len(groups)))]
    bento = "".join('<li class="rv" style="--d:%d"><a class="tile card tilt%s" href="#%s"><span class="tn">%s</span><h3>%s</h3><p>%s</p></a></li>'
                    % (i * 60, " tile-pin" if i < 2 else "", h, n, ti, ln) for i, (h, n, ti, ln) in enumerate(ov_t))
    # Vergilius fissato: radar sobrio, i punti si accendono al passaggio del raggio (7 s, come la rotazione)
    blips = ""
    for ang, rad, c in ((25, .55, 0), (70, .8, 0), (118, .35, 0), (160, .7, 0), (205, .5, 1), (250, .85, 0), (310, .6, 0)):
        x, y = 50 + 50 * rad * math.sin(math.radians(ang)), 50 - 50 * rad * math.cos(math.radians(ang))
        blips += '<span class="bl%s" style="--x:%.1f%%;--y:%.1f%%;--d:%.2fs"></span>' % (" c" if c else "", x, y, ang / 360 * 7)
    pst = "".join('<li><span class="pn">%s</span><span class="pl">%s</span></li>' % (n, lb) for n, lb in t["pin_st"])
    pin_v = ('<section class="pin" id="vergilius" aria-labelledby="h-vergilius"><article class="pin-c card rv"><div class="radar" aria-hidden="true">%s</div>'
             '<p class="pin-b"><span class="badge b-pin">%s</span><span class="badge">%s</span><span class="badge">%s</span></p>'
             '<h2 id="h-vergilius">Vergilius</h2><p class="pin-s">%s</p><p>%s</p><p>%s</p>%s%s'
             '<p class="pin-lab">%s</p><ul class="pin-st">%s</ul></article></section>'
             % (blips, *t["pin_b"], t["pin_s"], t["pin_p1"], t["pin_p2"], note(1, t["n1"]), go((GH + "vergilius", t["pin_go"])), t["pin_lab"], pst))
    # guida GTX 1080 fissata: classifica a barre (lunghezza = rapporto prima/dopo), riempita all'ingresso in vista
    fmt = lambda v: ("%g" % v).replace(".", dec)
    rows = ((20.2, 2.7, "s", 20.2 / 2.7, "7.5x"), (674.5, 175.5, "s", 674.5 / 175.5, "\u221274%"), (33, 83.5, "tok/s", 83.5 / 33, "2.5x"),
            (1875, 944, "ms", 1875 / 944, "2.0x"), (55.9, 84.4, "tok/s", 84.4 / 55.9, "+51%"), (41.2, 57.6, "tok/s", 57.6 / 41.2, "+40%"))
    top = max(r[3] for r in rows)
    lb = "".join('<li class="lb"><p class="lb-h"><span class="lb-l">%s</span><span class="lb-v">%s \u2192 %s %s <b>%s</b></span></p><span class="hb-t"><i style="--w:%.3f;--d:%d"></i></span></li>'
                 % (t["gd_rows"][i], fmt(b), fmt(a), u, d.replace(".", dec), r / top, i * 110) for i, (b, a, u, r, d) in enumerate(rows))
    gchips = "".join('<span class="chip">%s</span>' % c for c in t["gd_chips"])
    pin_g = ('<section class="pin" id="guida" aria-labelledby="h-guida"><article class="pin-c card rv"><p class="pin-b"><span class="badge b-pin">%s</span><span class="badge">%s</span></p>'
             '<h2 id="h-guida">%s</h2><p class="pin-s">%s</p><ol class="lbs">%s</ol><p class="lb-ax">%s</p><p class="bf">%s</p>%s</article></section>'
             % (*t["gd_b"], t["gd_t"], t["gd_s"], lb, t["gd_ax"], gchips, go((GUIDE, t["gd_go"]))))
    pin = '<div class="pins wrap">' + pin_v + pin_g + '</div>'

    h3m = t["h3_meta"]
    h3meta = "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (h3m[i], h3m[i + 1]) for i in (0, 2, 4))
    head_html = """<!DOCTYPE html>
<html lang="{L}" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name} · AI Engineer</title>
<meta name="description" content="{desc}">
<meta http-equiv="Content-Security-Policy" content="{csp}">
<meta name="color-scheme" content="dark light">
<meta name="theme-color" content="#0d0f13">
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
<link rel="preload" href="{P}fonts/geist-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{P}fonts/jetbrains-mono-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{P}css/site.css">
<script>{boot}</script>
<script src="{P}js/site.js" defer></script>
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Person","name":"{name}","jobTitle":"AI Engineer","url":"{site}","sameAs":["{gh}","{hf}","{li}","{ig}"]}}</script>
</head>
""".format(L=L, name=NAME, desc=t["desc"], csp=CSP, canon=t["canon"], site=SITE, og=t["og"], ogimgalt=t["ogimgalt"], ogloc=t["ogloc"], ogalt=t["ogalt"], P=P, boot=BOOT,
           gh=GH.rstrip("/"), hf=HF, li=LI, ig=IG)

    abs_ = re.sub(r'<span class="runin">.*?</span>\s*', "", t["abs"])
    stats = "".join('<li><a class="stat tilt" href="%s"><span class="num">%s</span><span class="lab">%s</span><span class="src">%s</span></a></li>' % (h, n, lb, s) for n, lb, h, s in t["stats"])
    legend = "".join('<li><i%s></i>%s</li>' % (c, x) for c, x in zip((' class="g"', "", ' class="r"'), t["fly_leg"]))

    body = f"""<body>
<a class="skip" href="#main">{t['skip']}</a>
<header class="bar" id="mast"><div class="bar-in">
<a class="brand" href="#top">{NAME}</a>
<nav class="nav" aria-label="{t['navlabel']}">{nav}</nav>
<div class="bar-tools">{lang_nav}{theme}</div>
<details class="toc"><summary>{t['toc']}</summary><div class="toc-panel"><ol>{toc}</ol><div class="toc-tools">{lang_nav}{theme}</div></div></details>
</div></header>

<main id="main">
<section class="hero" id="top">
<div class="hero-bg" aria-hidden="true"></div>
<canvas class="hero-cv" id="hero-cv" aria-hidden="true"></canvas>
<div class="hero-in wrap">
<p class="folio" style="--i:0">{t['folio']}</p>
<h1 style="--i:1"><span>Adrian</span> <span>Ciprian</span> <span>Iancu</span></h1>
<p class="role" style="--i:2">{t['role']}</p>
<p class="abs" style="--i:3">{abs_}</p>
<p class="links" style="--i:4"><a class="btn btn-main" href="{GH.rstrip('/')}">GitHub</a><a class="btn" href="{HF}">Hugging Face</a><a class="btn" href="{LI}">LinkedIn</a><a class="btn" href="{IG}">Instagram</a></p>
<ul class="stats" style="--i:5">{stats}</ul>
</div>
</section>

<section class="ov wrap" id="panoramica" aria-labelledby="h-panoramica">
<h2 class="kick rv" id="h-panoramica"><i></i>{t['ov_k']}</h2>
<ul class="bento">{bento}</ul>
</section>

{pin}

<div class="body wrap">
<aside class="hf rv" aria-labelledby="h-hf">
<h2 class="kick" id="h-hf"><a href="{HF}">{t['hfh']}</a></h2>
{hfm.render(L, hfm.load())}
</aside>
<div class="content">

<section class="sec" id="contributi" aria-labelledby="h-contributi">
{head('01', t['kc'], t['hc'], 'contributi', t['leadc'])}
<ol class="tl">{prs}</ol>
{kt}
</section>

<section class="sec" id="implementazioni" aria-labelledby="h-implementazioni">
{head('02', t['ki'], t['hi'], 'implementazioni', t['leadi'])}
<article class="feat card tilt rv">
<h3><a href="{BW}">blackwell6000-qwen3.8-flash-next</a></h3>
<p class="dateline">{t['dlbw']}</p>
{meta}
<p>{t['bw']}</p>
</article>
<article class="feat card tilt rv" id="h3">
<h3><a href="{GUIDE_H3}">{t['h3_t']}</a></h3>
<p class="dateline">{t['h3_dl']}</p>
<dl class="meta">{h3meta}</dl>
<p>{t['h3_p1']}</p>
<p>{t['h3_p2']}</p>
<p>{t['h3_sp']}</p>
<ul class="pts"><li>{t['h3_sp1'][0]}</li><li>{t['h3_sp1'][1]}</li></ul>
<p>{t['h3_p3']}</p>
{go((GUIDE_H3, t['h3_go']))}
</article>
<div class="grid3">
{brief('minicpm5-kernel-pascal', t['mc'], t['mcs'], GH + 'minicpm5-kernel-pascal')}
{brief('bonsai2-ternary-pascal', t['bo2'], t['bo2s'], GH + 'bonsai2-ternary-pascal')}
{brief('llm2vec-8gb-offload-lossless-batching', t['l2v'], t['m3'], GH + 'llm2vec-8gb-offload-lossless-batching')}
</div>
{err}
<div class="grid3">
{brief('lfm-to-kimodo', t['lfm'], t['lfms'], GH + 'lfm-to-kimodo')}
{brief('bonsai-webgpu-tiled-vae-fix', t['bons'], t['bonss'], GH + 'bonsai-webgpu-tiled-vae-fix')}
{brief('hildanext', t['hild'], t['hilds'], GH + 'hildanext')}
</div>
</section>

<section class="sec" id="ricerca" aria-labelledby="h-ricerca">
{head('03', t['kr'], t['hr'], 'ricerca', t['leadr'])}
<ul class="trials card rv">{trials}</ul>
<article class="proj rv">
<p>{t['concl']}</p>
{go((BW + '/tree/main/cohere-probe', t['gor'][0]), ('https://github.com/wtogami/qwen-block-proxy-artifacts/issues/3', t['gor'][1]))}
</article>
<h3 class="sub rv">{t['hfh']}</h3>
<div class="grid3 hfm">
{hfmodels}
</div>
</section>

<section class="sec" id="strumenti" aria-labelledby="h-strumenti">
{head('04', t['ks'], t['hs'], 'strumenti', t['leads'])}
<article class="feat card tilt rv">
<h3><a href="{ORG}claude-plugins">claude-plugins</a></h3>
<p class="dateline">{t['dlcp']}</p>
<p>{t['cp']}</p>
<p class="cmd"><code>/plugin marketplace add Partido-De-What/claude-plugins</code><code>/plugin install chatroom@artyomita-plugins</code></p>
{go((ORG + 'claude-plugins#chatroom-harness-point-by-point', t['gocp']))}
<p class="meth">{t['cps']}</p>
</article>
{fence}
<div class="grid3">
{brief('Vergilius', t['vref'], 'Python · llama.cpp', '#vergilius')}
{brief('stt-whisper-pad', t['stt'], t['stts'], GH + 'stt-whisper-pad')}
</div>
</section>

<section class="sec" id="sperimentali" aria-labelledby="h-sperimentali">
{head('05', t['kx'], t['hx'], 'sperimentali', t['lead1'])}
{note(2, t['n2'])}
<div class="fly">
<figure class="stage-w rv"><div class="stage"><canvas id="cns" width="400" height="570" role="img" aria-label="{t['fly_label']}"></canvas></div><ul class="legend">{legend}</ul><figcaption>{t['fly_cap']}</figcaption></figure>
<article class="feat card tilt rv">
<h3><a href="{GH}flytollm">FlyToLLM</a></h3>
<p class="dateline">{t['dl1']}</p>
<p>{t['d1']}</p>
{note(3, t['n3'])}
{go(('https://artyomita.github.io/flytollm/', t['go1']))}
<p class="meth">{t['m1']}</p>
</article>
</div>
</section>

<section class="sec sec-sub" id="ml" data-nav="#sperimentali" aria-labelledby="h-ml">
{head('05.1', t['k5'], t['h5s'], 'ml', t['lead5'])}
<article class="feat card tilt rv">
<h3><a href="{GH}fantaoracle">FantaOracle</a></h3>
<p class="dateline">{t['dl5']}</p>
<p>{t['fo']}</p>
{note(4, t['n4'])}
<p class="meth">{t['m5']}</p>
</article>
{lots}
<div class="grid3">
{brief('fantacalcio-advisor', t['fca'], t['fcas'], GH + 'fantacalcio-advisor')}
{brief('K-Forecast', t['kf'], t['kfs'], GH + 'K-Forecast')}
{brief('sp500-predictability-lab', t['sp'], t['sps'], GH + 'sp500-predictability-lab')}
{brief('storico', t['sto'], t['stos'], GH + 'storico')}
</div>
</section>

<section class="sec sec-sub" id="rl" data-nav="#sperimentali" aria-labelledby="h-rl">
{head('05.2', t['k6'], t['h6s'], 'rl', t['lead6'])}
<div class="grid3">
{brief('supermario-1-1-rl', t['sm'], t['sms'], GH + 'supermario-1-1-rl')}
{brief('idle-isekai-trials', t['idle'], t['idles'], GH + 'idle-isekai-trials')}
</div>
</section>

<section class="sec" id="indice" aria-labelledby="h-indice">
{head('06', t['kapp'] + ' · ' + idxm, t['hidx'], 'indice', t['idxcap'])}
<div class="idx-g">{idx}</div>
</section>

<section class="sec sec-sub" id="note" aria-labelledby="h-note">
<h2 class="kick rv" id="h-note"><i></i>{t['hnote']}</h2>
<p class="notetext rv">{t['note']}</p>
</section>

<section class="sec sec-sub" id="autore" aria-labelledby="h-autore">
<div class="author card rv">
<img src="{P}img/avatar-192.webp" width="96" height="96" alt="{t['avalt']}" loading="lazy" decoding="async">
<div><h2 class="kick" id="h-autore" style="margin:0 0 10px"><i></i>{t['haut']}</h2><p class="aname">{NAME}</p>
<p class="arole">{t['role']}</p>
<p class="kw">{kw}</p>
{go((GH.rstrip('/'), 'GitHub'), (HF, 'Hugging Face'), (LI, 'LinkedIn'), (IG, 'Instagram'))}</div>
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
    return head_html + body


def write(lang, html):
    path = os.path.join(ROOT, "index.html") if lang == "it" else os.path.join(ROOT, "en", "index.html")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    return path


if __name__ == "__main__":
    for lang in ("it", "en"):
        html = page(T[lang])
        print(write(lang, html), len(html.encode("utf-8")))
    open(os.path.join(ROOT, ".nojekyll"), "w").close()
    print("CSP hash sha256-" + BOOT_HASH)
