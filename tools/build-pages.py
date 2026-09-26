"""Genera index.html (italiano) e en/index.html (inglese) dallo stesso modello.

Stessa struttura e stessi id nelle due pagine; cambiano solo i testi.
Dopo la scrittura, con --bake, apre le pagine in Playwright (movimento ridotto) e
incolla nell'HTML le figure 3, 4, 5 e 6 al fotogramma finale, cosi' si leggono anche senza JS.

Uso:  python tools/build-pages.py [--bake]
"""
import base64
import hashlib
import http.server
import os
import re
import socketserver
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://artyomita.github.io/"
GH = "https://github.com/ArtyomITA/"
PR = "https://github.com/ggml-org/llama.cpp/pull/27721"
LI = "https://www.linkedin.com/in/adrian-ciprian-iancu-a2a477391/"

BOOT = "(function(d){d.className='js';try{var t=localStorage.getItem('ai-theme');if(t==='light'||t==='dark')d.setAttribute('data-theme',t)}catch(e){}})(document.documentElement);"
BOOT_HASH = base64.b64encode(hashlib.sha256(BOOT.encode("utf-8")).digest()).decode()
CSP = ("default-src 'self'; script-src 'self' 'sha256-%s'; style-src 'self'; img-src 'self' data:; "
       "font-src 'self'; connect-src 'none'; object-src 'none'; base-uri 'self'; form-action 'none'") % BOOT_HASH

TICKS = '<div class="rule" aria-hidden="true">' + "<i></i>" * 12 + "</div>"
# filetto semplice per le sezioni senza progetto guida (RL, indice, nota)
RULE = '<div class="rule plain" aria-hidden="true"></div>'


def m(x):
    return '<span class="m">%s</span>' % x


def nav_items(t):
    return [("#ricerca", t["nav"][0]), ("#inferenza", t["nav"][1]), ("#motion", t["nav"][2]), ("#locale", t["nav"][3]),
            ("#ml", t["nav"][4]), ("#rl", t["nav"][5]), ("#indice", t["nav"][6])]


# linguaggio principale e sua quota in byte, da GET /repos/ArtyomITA/<repo>/languages (26 settembre 2026)
LANGS = {"flytollm": ("Python", 100), "hildanext": ("Python", 73), "bonsai-webgpu-tiled-vae-fix": ("JavaScript", 82),
         "llm2vec-8gb-offload-lossless-batching": ("Python", 100), "vergilius": ("Python", 90), "stt-whisper-pad": ("Python", 94),
         "fantaoracle": ("Python", 87), "fantacalcio-advisor": ("TypeScript", 79), "K-Forecast": ("Python", 96),
         "sp500-predictability-lab": ("TypeScript", 57), "storico": ("Python", 99), "supermario-1-1-rl": ("TypeScript", 99),
         "idle-isekai-trials": ("JavaScript", 99)}


def lsh(name):
    if name not in LANGS:
        return ""
    lg, pc = LANGS[name]
    return ('<span class="lsh"><svg aria-hidden="true" width="48" height="4"><rect class="b0" width="48" height="4"/>'
            '<rect class="b1" width="%s" height="4"/></svg>%s %d%%</span>') % (round(48 * pc / 100.0, 1), lg, pc)


# neuroni per punto in Fig. 2: 166.700 diviso i punti generati da js/site.js (seme 166700).
# Il bake lo ricontrolla contro il valore calcolato a runtime.
PD = {"it": "260", "en": "260"}

T = {}

T["it"] = dict(
    lang="it", ogloc="it_IT", ogalt="en_GB", canon=SITE, P="", og="img/og-it.png",
    desc="AI engineer: ottimizzazione dell'inferenza su GPU consumer (CUDA, Pascal sm_61), ricerca su attention e memoria nei language model, pipeline ML locali e privacy-first. Tutto open source.",
    ogimgalt="Il nome Adrian Iancu in grande, la riga del ruolo e una fascia del raster di neuroni simulati della figura 1.",
    skip="Vai al contenuto", navlabel="Sezioni", toc="Indice", langlabel="Lingua", themelabel="Tema",
    th=("chiaro", "scuro", "auto"), thtitle=("Tema chiaro (carta)", "Tema scuro (cianotipia)", "Tema auto (come il sistema)"),
    nav=["ricerca", "inferenza", "motion ed embedding", "strumenti locali", "ML applicato", "ambienti RL", "indice"], navnote="nota sulle figure",
    folio="aggiornata settembre 2026",
    abs='<span class="runin">Sommario.</span> <b>Ottimizzazione CUDA su GPU consumer</b>, <b>ricerca su attention e memoria nei language model</b> (fino a un nucleo ricorrente preso da un connettoma reale), <b>pipeline ML locali</b> senza cloud. Tutto open&nbsp;source.',
    rasterlabel="Raster di neuroni leaky integrate-and-fire simulati: tratti di spike nel tempo per neuroni sensoriali, centrali e discendenti, con il tasso di popolazione sotto.",
    cap1='<b>Fig. 1.</b> Raster di <span class="nn">128</span> neuroni leaky integrate-and-fire simulati in questa pagina (dt = 1 ms), ordinati per distanza dalle porte d\'ingresso. Ogni tratto è uno spike. Circa ogni 120 ms un token entra dai neuroni sensoriali; scorrere la pagina aumenta l\'ingresso. È un\'illustrazione: il modello vero ha 166.700 neuroni (<a href="#fig2">fig.&nbsp;2</a>).',
    legend=["sensoriale (porta d'ingresso)", "eccitatorio", "inibitorio", "discendente (uscita)", "tasso di popolazione"],
    kw='CUDA, CUDA Graphs; PyTorch; llama.cpp, GGML; WebGPU, WGSL; Spiking NN, surrogate gradient; LLM inference, quantizzazione, offload; Diffusion LM; Embedding, LLM2Vec; Time series, probabilistic forecasting; Python, C++, TypeScript; Unity, Phaser; faster-whisper, Piper.',
    tcap="<b>Tab. 1.</b> Numeri di riferimento, ciascuno con la sua fonte.", thq="grandezza", thv="valore", ths="fonte",
    rows=[("Hardware di riferimento", "GTX&nbsp;1080|8&nbsp;GB|sm_61", "ogni benchmark della pagina"),
          ("Speedup MoE in llama.cpp", "+40%", '<a href="%s">PR upstream #27721, aperta</a>' % PR),
          ("Neuroni simulati con gradiente", "166.700", '<a href="%sflytollm">repository flytollm</a>, male-cns:v1.0' % GH),
          ("Modelli portati su 8&nbsp;GB", "Llama-3-8B|Bonsai&nbsp;4B|Kimodo", '<a href="#motion">Motion ed embedding</a>; <a href="#inferenza">Inferenza</a>')],
    # Ricerca
    k1="Ricerca su attention e memoria", h1s="Language model su un connettoma reale",
    lead1="Quanto del contesto lo tiene l'attention e quanto un nucleo ricorrente? Banco di prova: il connettoma completo del sistema nervoso di Drosophila (male-cns:v1.0, " + m("166.700") + " neuroni, " + m("2,75 M") + ' sinapsi a soglia 10)<sup class="n">1</sup> come nucleo ricorrente LIF di un language model: segni sinaptici fissati dal neurotrasmettitore, magnitudini inizializzate dal conteggio di sinapsi, gradiente surrogato, CUDA Graph FP32. Protocollo con null model a gradi conservati, baseline a pari token e lesioni in silico.',
    n1="Connettoma male-cns:v1.0 (Janelia FlyEM · Google Research, licenza CC-BY): 25,6 M connessioni in totale, 2.753.975 sopra la soglia di 10 sinapsi.",
    cap2='<b>Fig. 2.</b> Pipeline di FlyToLLM. I punti sono un\'illustrazione generata in questa pagina dentro la sagoma del sistema nervoso centrale (cervello, lobi ottici, cordone ventrale): ogni punto vale circa <span class="pd">' + PD["it"] + '</span> neuroni. I punti pieni più grandi sono le porte d\'ingresso, sul bordo dei lobi ottici e sul dorso del cervello; la tinta si schiarisce con la distanza in salti dalle porte e lo scorrimento rivela un salto alla volta. I quadratini sono il readout: nel connettoma vero sta a 2 salti dalle porte, per questo la profondità 4+4 basta.',
    dl1="ricerca · 2026",
    d1="Ingresso del testo tramite i " + m("17.937") + " neuroni sensoriali reali, lettura dai " + m("2.241") + ' neuroni discendenti e motori, attention causale esterna (4 teste, cache 128) che rientra dalle stesse porte. Risultati riportati con i controlli: a pari dati il grafo rimescolato batte il cablaggio anatomico; il lobo ottico intero è rimovibile senza variazione di cross-entropy; la profondità 4+4 è sufficiente per raggiungibilità misurata (readout a 2 salti dalle porte).<sup class="n">2</sup>',
    go1="pipeline animata e numeri", fork="fork di llama.cpp",
    m1="PyTorch · CUDA Graphs; LIF · surrogate gradient; TBPTT · Adam; TinyStories · BPE 4096",
    n2="4+4 sottopassi per token, TBPTT 8, CUDA Graph FP32: 0,65 s per update su GTX&nbsp;1080, 0,38 s con il kernel fuso; 5,46 M parametri.",
    # Inferenza
    k2="Ottimizzazione dell'inferenza CUDA", h2s="Architettura Pascal (sm_61)",
    lead2="Nessun tensor core, FP16 a 1/64 del throughput FP32, 8&nbsp;GB di VRAM. Profilazione, root cause analysis, patch minime con benchmark riproducibili, contributi upstream.",
    dl2="llama.cpp · PR upstream",
    d2="Abilitazione dei CUDA Graphs su sm_61 in llama.cpp: " + m("+40%") + " di throughput sui modelli Mixture-of-Experts, " + m("+7%") + " sui densi, nessuna regressione misurata. Diff di una riga con benchmark allegati.",
    md=("Dove", "Stack", "Stato"), mdv=("llama.cpp (ggml-org)", "C++ · CUDA; GGML", "aperta, non ancora integrata"),
    cap3="<b>Fig. 3.</b> CUDA Graphs su sm_61 in llama.cpp (PR #27721). Schema, non traccia di profilazione: stessi kernel, un solo lancio del grafo al posto di uno per kernel. Scorrendo, la riga del grafo si accorcia fino a 1/1,40 della prima sui modelli MoE (+40% misurato) e a 1/1,07 sui densi (+7%).",
    hild="Conversione di un LLM autoregressivo (Qwen3-0.6B) in modello a diffusione discreta secondo la ricetta LLaDA 2.1, con backend di training e inferenza eseguibile su Pascal.",
    hilds="Python · PyTorch; diffusion LM",
    bons="Root cause analysis del decoder VAE tiled di Bonsai-Image 4B in WebGPU su GPU prive di shader-f16: patch da " + m("1,4 KB") + " che abilita 512px e oltre su Pascal e precedenti, senza perdita di qualità sui dispositivi f16.",
    bonss="JavaScript · WebGPU · WGSL; 2 stelle",
    # Motion
    k3="Pipeline text-to-motion ed embedding", h3s="Modelli da 8 B su 8&nbsp;GB di VRAM",
    lead3="Generazione di movimento 3D con Kimodo-SOMA (NVIDIA) guidata da un encoder LLM2Vec da 8 miliardi di parametri, interamente in locale: offload CPU/GPU, batching senza degradazione numerica, integrazione in Unity con sintesi vocale.",
    l2v="LLM2Vec (Llama-3-8B) su una GPU da 8&nbsp;GB via offload in RAM; batching senza alterare gli embedding: il padding li sposta (similarità coseno " + m("0,76") + " contro il riferimento), il fix li riporta a " + m("0,999956") + ".",
    m3="Python · PyTorch; encoder testuale per Kimodo",
    cap4="<b>Fig. 4.</b> Distanza degli embedding di LLM2Vec calcolati in batch dal riferimento calcolato senza batch, su scala logaritmica di 1 − coseno: con il padding 1 − cos = 0,24 (coseno 0,76), con il fix 4,4·10<sup>−5</sup> (coseno 0,999956), circa 5.500 volte più vicino.",
    npc="NPC conversazionale in Unity", soon="in arrivo",
    npcd="Personaggio 3D locale: LLM per il dialogo, Piper per la voce, Kimodo-SOMA per le animazioni del corpo, su GTX&nbsp;1080 e CPU a 4 core. Pubblicazione in preparazione.",
    npcs="Unity · Python; text-to-motion · TTS",
    # Strumenti locali
    k4="Strumenti locali", h4s="Speech-to-text locale e strumenti privacy-first",
    lead4="Applicazioni desktop che elaborano audio e testo sulla macchina dell'utente, senza servizi esterni.",
    # testo precedente di Vergilius, non piu' pubblicato: sostituito dal testo del README pubblico (verg)
    vold="Assistente personale che non comunica con servizi esterni: schema architetturale pubblicato, codice in arrivo.",
    verg="Assistente personale che non comunica con servizi esterni: gira in locale su GTX&nbsp;1080 (8&nbsp;GB), senza chiavi API e senza che una conversazione lasci la macchina. Modello predefinito LFM2.5-2.6B con drafter speculativo: " + m("64&nbsp;tok/s") + " in decodifica, " + m("78-100") + "&nbsp;tok/s con il drafter attivo. Un controllo di groundedness confronta le cifre delle risposte con i risultati degli strumenti: le cifre non supportate sono scese da " + m("3") + " turni su " + m("35") + " a " + m("1") + "&nbsp;su&nbsp;" + m("36") + '.<sup class="n">3</sup>',
    n3="Il repository include come submodule due progetti di terzi, Odysseus (assistente) e ShadowBroker (intelligence da fonti aperte), con licenza AGPL-3.0: sono dipendenze, non lavoro originale.",
    cap5="<b>Fig. 5.</b> Vergilius su GTX&nbsp;1080, dentro un recinto: nessuna chiamata esce dalla macchina (127.0.0.1). A sinistra la velocità di decodifica, 64&nbsp;tok/s e 78-100&nbsp;tok/s con il drafter; a destra i turni con cifre non supportate dai risultati degli strumenti, da 3 su 35 a 1 su 36.",
    stt="Applicazione Windows per trascrizione vocale locale basata su faster-whisper (CTranslate2, int8 su CUDA): registrazione, trascrizione e incolla nel campo attivo.",
    stts="Python; 1 stella",
    # ML
    k5="Progetti di machine learning applicato", h5s="Predizione, ottimizzazione, serie storiche",
    lead5="Modelli con intervalli di incertezza, ottimizzazione sotto vincoli in tempo reale, valutazione fuori campione o su simulazione.",
    dl5="codice completo",
    fo="Sistema decisionale per l'asta del fantacalcio: modello di prezzo con forchetta d'incertezza, ottimizzazione della rosa al tavolo sotto vincoli di budget e slot, valutazione su campionati simulati (probabilità di arrivare primi " + m("56%") + " sulle 100 simulazioni usate per la scelta dei parametri, " + m("57% ± 5") + " su simulazioni di verifica separate, contro archetipi interni del modello). Con arena interattiva per sfidarlo.<sup class=\"n\">4</sup>",
    m5="Python; 2 stelle; predizione · ottimizzazione · Monte Carlo",
    n4="Dal README: la probabilità di arrivare primi è un numero interno del modello contro i suoi archetipi, non una promessa sul tavolo vero. Tetto d'asta dinamico, che su 28 lotti simulati arriva al prezzo di aggiudicazione in 8, e ponte con FantaAsta Live, 43 assegnazioni corrette su 44: <a href=\"#fig6\">fig.&nbsp;6</a>.",
    cap6="<b>Fig. 6.</b> FantaOracle, replay del tetto d'asta su 28 lotti simulati (attaccanti battuti a 40 crediti o più, in ordine d'asta). Le barre sono il tetto proposto dal bot, le tacche il prezzo a cui il giocatore è stato aggiudicato; la linea a gradini è il massimo spendibile in quel momento, cioè la cassa meno un credito per ogni altro slot ancora vuoto. Il dato è che il tetto arriva al prezzo in 8 lotti su 28. Gli 0 sfori (nessuna barra sopra la linea, anche sugli altri 24 lotti del campione) sono garantiti dalla formula, che taglia il tetto al massimo spendibile: non sono un risultato. Negli ultimi 7 lotti il massimo spendibile è 1 credito e il tetto con lui (punti sulla base). Sotto, il ponte con FantaAsta Live su un'asta di prova: 43 assegnazioni su 44 identiche per giocatore, squadra e prezzo; le celle sono ordinate, non in sequenza d'asta. Dati dai report pubblici del repository.",
    fca="Motore di analisi e raccomandazione multi-algoritmo con front-end React; il predecessore di FantaOracle.", fcas="React · TypeScript · Python",
    kf="Dashboard di previsione probabilistica: DeepAR, ARIMA/SARIMA e AutoGluon confrontati sulla stessa serie con intervalli di confidenza.", kfs="Python; time series",
    sp="Laboratorio full-stack (React + Flask) per l'analisi e la predizione di serie storiche dell'S&amp;P 500, con test di prevedibilità fuori campione.", sps="TypeScript · Python; time series",
    sto="Pipeline supervisionata e non supervisionata su fatture aperte: apprendimento dei pattern di pagamento e ranking del rischio per la gestione del credito.", stos="Python; credit risk",
    # RL
    k6="Ambienti RL", h6s="Game engine e ambienti per reinforcement learning",
    lead6="Ambienti simulati costruiti da zero come banco di prova per agenti.",
    sm="Clone del livello 1-1 in Phaser 3 e TypeScript progettato come ambiente di training per reinforcement learning, con osservazioni e ricompense esposte.", sms="TypeScript · Phaser 3; RL",
    idle="Idle RPG nel browser con Phaser 3 e Three.js: loop di progressione, prestigio e rendering 3D.", idles="JavaScript · Three.js",
    # Indice
    kapp="Appendice", hidx="Indice dei repository", idxm="14 repository e 1 progetto in arrivo · 6 aree",
    idxcap="Repository pubblici raggruppati per area; ogni nome linkato porta al codice. Sotto lo stack, la quota del linguaggio principale nel codice del repository (GitHub, settembre 2026).",
    ih=("repository", "stack", "note"), fk="(fork)", pra="PR #27721 aperta", st1="1 stella", st2="2 stelle",
    # Nota
    hnote="Nota sulle figure",
    note='Tutte le figure sono calcolate in questa pagina con canvas e SVG scritti a mano, senza immagini né librerie. I generatori pseudo-casuali hanno seme fisso (27721, il numero della PR, per <a href="#fig1">Fig. 1</a> e <a href="#fig3">Fig. 3</a>; 166700, il numero di neuroni, per <a href="#fig2">Fig. 2</a>), quindi ogni lettore vede lo stesso disegno. Lo scorrimento è un ingresso: in Fig. 1 alza la corrente sensoriale, nelle altre fa avanzare la figura, che torna indietro se si risale. Con la riduzione del movimento attiva ogni figura mostra un solo fotogramma scelto. Fig. 1, 2 e 3 sono schemi; <a href="#fig4">Fig. 4</a>, <a href="#fig5">Fig. 5</a> e <a href="#fig6">Fig. 6</a> riportano numeri misurati; i numeri di testo, didascalie e Tab. 1 vengono dai repository.',
    haut="L'autore", avalt="Avatar GitHub di Adrian Iancu", notelabel="Nota",
    foot=("niente tracker, niente pubblicità", "pagina fatta in casa"), grid="mostra la griglia",
)

T["en"] = dict(
    lang="en", ogloc="en_GB", ogalt="it_IT", canon=SITE + "en/", P="../", og="img/og-en.png",
    desc="AI engineer: inference optimization on consumer GPUs (CUDA, Pascal sm_61), research on attention and memory in language models, local and privacy-first ML pipelines. Everything open source.",
    ogimgalt="The name Adrian Iancu set large, the role line and a strip of the simulated neuron raster from figure 1.",
    skip="Skip to content", navlabel="Sections", toc="Contents", langlabel="Language", themelabel="Theme",
    th=("light", "dark", "auto"), thtitle=("Light theme (paper)", "Dark theme (cyanotype)", "Auto theme (follow the system)"),
    nav=["research", "inference", "motion and embeddings", "local tools", "applied ML", "reinforcement learning", "index"], navnote="a note on the figures",
    folio="updated September 2026",
    abs='<span class="runin">Abstract.</span> <b>CUDA optimization on consumer GPUs</b>, <b>research on attention and memory in language models</b> (down to a recurrent core taken from a real connectome), <b>local ML pipelines</b> with no cloud. Everything open&nbsp;source.',
    rasterlabel="Raster of simulated leaky integrate-and-fire neurons: spike ticks over time for sensory, central and descending neurons, with the population rate below.",
    cap1='<b>Fig. 1.</b> Raster of <span class="nn">128</span> leaky integrate-and-fire neurons simulated in this page (dt = 1 ms), ordered by distance from the input ports. Each tick is a spike. Roughly every 120 ms a token enters through the sensory neurons; scrolling the page raises the input. An illustration: the real model has 166,700 neurons (<a href="#fig2">fig.&nbsp;2</a>).',
    legend=["sensory (input port)", "excitatory", "inhibitory", "descending (output)", "population rate"],
    kw='CUDA, CUDA Graphs; PyTorch; llama.cpp, GGML; WebGPU, WGSL; Spiking NN, surrogate gradient; LLM inference, quantization, offload; Diffusion LM; Embeddings, LLM2Vec; Time series, probabilistic forecasting; Python, C++, TypeScript; Unity, Phaser; faster-whisper, Piper.',
    tcap="<b>Table 1.</b> Reference numbers, each with its source.", thq="quantity", thv="value", ths="source",
    rows=[("Reference hardware", "GTX&nbsp;1080|8&nbsp;GB|sm_61", "every benchmark on this page"),
          ("MoE speedup in llama.cpp", "+40%", '<a href="%s">upstream PR #27721, open</a>' % PR),
          ("Neurons trained by gradient", "166,700", '<a href="%sflytollm">flytollm repository</a>, male-cns:v1.0' % GH),
          ("Models fitted into 8&nbsp;GB", "Llama-3-8B|Bonsai&nbsp;4B|Kimodo", '<a href="#motion">Motion and embeddings</a>; <a href="#inferenza">Inference</a>')],
    k1="Research on attention and memory", h1s="A language model on a real connectome",
    lead1="How much of the context is held by attention, and how much by a recurrent core? Test bed: the complete connectome of the Drosophila nervous system (male-cns:v1.0, " + m("166,700") + " neurons, " + m("2.75 M") + ' synapses at threshold 10)<sup class="n">1</sup> as the recurrent LIF core of a language model: synaptic signs fixed by the neurotransmitter, magnitudes initialised from synapse counts, surrogate gradient, FP32 CUDA Graph. Protocol with degree-preserving null models, token-matched baselines and in-silico lesions.',
    n1="male-cns:v1.0 connectome (Janelia FlyEM · Google Research, CC-BY licence): 25.6 M connections in total, 2,753,975 above the 10-synapse threshold.",
    cap2='<b>Fig. 2.</b> The FlyToLLM pipeline. The dots are an illustration generated in this page inside the outline of the central nervous system (brain, optic lobes, ventral nerve cord): each dot stands for about <span class="pd">' + PD["en"] + '</span> neurons. The larger solid dots are the input ports, on the rim of the optic lobes and along the top of the brain; the shade fades with the distance in hops from the ports, and scrolling reveals one hop at a time. The small squares are the readout: in the real connectome it sits 2 hops from the ports, which is why 4+4 depth is enough.',
    dl1="research · 2026",
    d1="Text enters through the " + m("17,937") + " real sensory neurons and is read out from the " + m("2,241") + ' descending and motor neurons; an external causal attention (4 heads, cache 128) re-enters through the same ports. Results are reported with their controls: at equal data the shuffled graph beats the anatomical wiring; the whole optic lobe can be removed with no change in cross-entropy; 4+4 depth is enough for the measured reachability (readout 2 hops from the ports).<sup class="n">2</sup>',
    go1="animated pipeline and numbers", fork="llama.cpp fork",
    m1="PyTorch · CUDA Graphs; LIF · surrogate gradient; TBPTT · Adam; TinyStories · BPE 4096",
    n2="4+4 substeps per token, TBPTT 8, FP32 CUDA Graph: 0.65 s per update on a GTX&nbsp;1080, 0.38 s with the fused kernel; 5.46 M parameters.",
    k2="CUDA inference optimization", h2s="Pascal architecture (sm_61)",
    lead2="No tensor cores, FP16 at 1/64 of FP32 throughput, 8&nbsp;GB of VRAM. Profiling, root cause analysis, minimal patches with reproducible benchmarks, upstream contributions.",
    dl2="llama.cpp · upstream PR",
    d2="Enabling CUDA Graphs on sm_61 in llama.cpp: " + m("+40%") + " throughput on Mixture-of-Experts models, " + m("+7%") + " on dense ones, no measured regression. A one-line diff with benchmarks attached.",
    md=("Where", "Stack", "Status"), mdv=("llama.cpp (ggml-org)", "C++ · CUDA; GGML", "open, not yet merged"),
    cap3="<b>Fig. 3.</b> CUDA Graphs on sm_61 in llama.cpp (PR #27721). A schematic, not a profiling trace: same kernels, one graph launch instead of one per kernel. As you scroll, the graph row shortens to 1/1.40 of the first on MoE models (+40% measured) and to 1/1.07 on dense models (+7%).",
    hild="Conversion of an autoregressive LLM (Qwen3-0.6B) into a discrete diffusion model following the LLaDA 2.1 recipe, with a training and inference backend that runs on Pascal.",
    hilds="Python · PyTorch; diffusion LM",
    bons="Root cause analysis of the tiled VAE decoder of Bonsai-Image 4B in WebGPU on GPUs without shader-f16: a " + m("1.4 KB") + " patch that enables 512px and above on Pascal and older GPUs, with no quality loss on f16 devices.",
    bonss="JavaScript · WebGPU · WGSL; 2 stars",
    k3="Text-to-motion and embedding pipelines", h3s="8 B models on 8&nbsp;GB of VRAM",
    lead3="3D motion generation with Kimodo-SOMA (NVIDIA) driven by an 8-billion-parameter LLM2Vec encoder, entirely local: CPU/GPU offload, batching without numerical degradation, Unity integration with speech synthesis.",
    l2v="LLM2Vec (Llama-3-8B) on an 8&nbsp;GB GPU via RAM offload; batching without altering the embeddings: padding shifts them (cosine similarity " + m("0.76") + " against the reference), the fix brings them back to " + m("0.999956") + ".",
    m3="Python · PyTorch; text encoder for Kimodo",
    cap4="<b>Fig. 4.</b> Distance of batched LLM2Vec embeddings from the unbatched reference, on a logarithmic scale of 1 − cosine: with padding 1 − cos = 0.24 (cosine 0.76), with the fix 4.4·10<sup>−5</sup> (cosine 0.999956), about 5,500 times closer.",
    npc="Conversational NPC in Unity", soon="coming soon",
    npcd="A local 3D character: an LLM for dialogue, Piper for the voice, Kimodo-SOMA for body animation, on a GTX&nbsp;1080 and a 4-core CPU. Release in preparation.",
    npcs="Unity · Python; text-to-motion · TTS",
    k4="Local tools", h4s="Local speech-to-text and privacy-first tools",
    lead4="Desktop applications that process audio and text on the user's machine, with no external services.",
    vold="Personal assistant that does not talk to external services: architecture schema published, code coming.",
    verg="A personal assistant that does not talk to external services: it runs locally on a GTX&nbsp;1080 (8&nbsp;GB), with no API keys and no conversation leaving the machine. Default model LFM2.5-2.6B with a speculative drafter: " + m("64&nbsp;tok/s") + " in decoding, " + m("78-100") + "&nbsp;tok/s with the drafter on. A groundedness check compares the numbers in each answer with the tool results: unsupported numbers dropped from " + m("3") + " turns out of " + m("35") + " to " + m("1") + "&nbsp;out&nbsp;of&nbsp;" + m("36") + '.<sup class="n">3</sup>',
    n3="The repository includes two third-party projects as submodules, Odysseus (assistant) and ShadowBroker (open-source intelligence), under AGPL-3.0: they are dependencies, not original work.",
    cap5="<b>Fig. 5.</b> Vergilius on a GTX&nbsp;1080, fenced in: no call leaves the machine (127.0.0.1). Left, decoding speed, 64&nbsp;tok/s and 78-100&nbsp;tok/s with the drafter; right, turns with numbers not supported by the tool results, from 3 out of 35 to 1 out of 36.",
    stt="Windows application for local voice transcription based on faster-whisper (CTranslate2, int8 on CUDA): record, transcribe and paste into the active field.",
    stts="Python; 1 star",
    k5="Applied machine learning projects", h5s="<span class=\"nw\">Prediction, optimization,</span> time series",
    lead5="Models with uncertainty intervals, real-time optimization under constraints, out-of-sample or simulation-based evaluation.",
    dl5="full source code",
    fo="Decision system for fantasy football auctions: a price model with an uncertainty band, squad optimization at the table under budget and slot constraints, evaluation on simulated leagues (a " + m("56%") + " chance of finishing first on the 100 simulations used for tuning, " + m("57% ± 5") + " on held-out validation runs, against the model's own archetypes). With an interactive arena to challenge it.<sup class=\"n\">4</sup>",
    m5="Python; 2 stars; prediction · optimization · Monte Carlo",
    n4="From the README: the probability of finishing first is the model's own number against its archetypes, not a promise at the real table. Dynamic auction cap, which reaches the winning price in 8 of 28 simulated lots, and bridge to FantaAsta Live, 43 correct assignments out of 44: <a href=\"#fig6\">fig.&nbsp;6</a>.",
    cap6="<b>Fig. 6.</b> FantaOracle, replay of the auction cap on 28 simulated lots (forwards sold for 40 credits or more, in auction order). Bars are the cap proposed by the bot, ticks the price the player was sold for; the stepped line is the maximum spendable at that moment, the budget minus one credit for every other empty slot. The finding is that the cap reaches the price in 8 of 28 lots. The 0 overruns (no bar above the line, on the other 24 lots of the sample too) are guaranteed by the formula, which clips the cap at the maximum spendable: they are not a result. In the last 7 lots the maximum spendable is 1 credit and so is the cap (dots on the baseline). Below, the bridge to FantaAsta Live on a test auction: 43 of 44 assignments identical in player, team and price; the cells are sorted, not in auction order. Data from the public reports in the repository.",
    fca="Multi-algorithm analysis and recommendation engine with a React front end; the predecessor of FantaOracle.", fcas="React · TypeScript · Python",
    kf="Probabilistic forecasting dashboard: DeepAR, ARIMA/SARIMA and AutoGluon compared on the same series with confidence intervals.", kfs="Python; time series",
    sp="Full-stack lab (React + Flask) for analysing and predicting S&amp;P 500 time series, with out-of-sample predictability tests.", sps="TypeScript · Python; time series",
    sto="Supervised and unsupervised pipeline on open invoices: learning payment patterns and ranking risk for credit management.", stos="Python; credit risk",
    k6="RL environments", h6s="Game engines and reinforcement learning environments",
    lead6="Simulated environments built from scratch as test beds for agents.",
    sm="A clone of level 1-1 in Phaser 3 and TypeScript, designed as a training environment for reinforcement learning, with observations and rewards exposed.", sms="TypeScript · Phaser 3; RL",
    idle="Browser idle RPG with Phaser 3 and Three.js: progression loop, prestige and 3D rendering.", idles="JavaScript · Three.js",
    kapp="Appendix", hidx="Repository index", idxm="14 repositories and 1 upcoming project · 6 areas",
    idxcap="Public repositories grouped by area; each linked name leads to the code. Under the stack, the share of the main language in the repository's code (GitHub, September 2026).",
    ih=("repository", "stack", "notes"), fk="(fork)", pra="PR #27721 open", st1="1 star", st2="2 stars",
    hnote="A note on the figures",
    note='Every figure is computed in this page with hand-written canvas and SVG, with no images or libraries. The pseudo-random generators have fixed seeds (27721, the PR number, for <a href="#fig1">Fig. 1</a> and <a href="#fig3">Fig. 3</a>; 166700, the neuron count, for <a href="#fig2">Fig. 2</a>), so every reader sees the same drawing. Scrolling is an input: in Fig. 1 it raises the sensory current, in the others it advances the figure, which rewinds if you scroll back. With reduced motion on, each figure shows a single chosen frame. Fig. 1, 2 and 3 are schematics; <a href="#fig4">Fig. 4</a>, <a href="#fig5">Fig. 5</a> and <a href="#fig6">Fig. 6</a> plot measured numbers; the numbers in the text, captions and Table 1 come from the repositories.',
    haut="About the author", avalt="Adrian Iancu's GitHub avatar", notelabel="Note",
    foot=("no trackers, no ads", "home-made page"), grid="show the grid",
)

ROLE = "AI Engineer · inference optimization · attention mechanisms research (transformer) · local-first&nbsp;systems"
ROLE_H = ROLE.replace("AI Engineer", "<b>AI Engineer</b>", 1)


def page(t):
    L = t["lang"]
    P = t["P"]
    other = "en" if L == "it" else "it"
    en_attr = ' lang="en"' if L == "it" else ""
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

    def brief(name, desc, stack, href=None, mono=True, dateline=None, lang_en=False):
        # il nome e' il link al codice: niente "-> repository" ripetuto
        inner = '<a href="%s">%s</a>' % (href, name) if href else name
        h = '<h3 class="%s"%s>%s</h3>' % ("bn" if mono else "bn bt", ' lang="en"' if lang_en else "", inner)
        if dateline:
            h += '<p class="dateline soon">%s</p>' % dateline
        foot = '<p class="bf"><span class="stk">%s</span></p>' % stack
        return '<article class="brief">%s<p>%s</p>%s</article>' % (h, desc, foot)

    def note(n, text):
        return '<aside class="notes" aria-label="%s %d"><p id="n%d"><sup class="n">%d</sup>%s</p></aside>' % (t["notelabel"], n, n, n, text)

    # colonna valore: un valore per riga (niente elenco inline che va a capo sul separatore)
    rows = "".join('<tr><td>%s</td><td class="v">%s</td><td class="src">%s</td></tr>' % (q, "".join("<span>%s</span>" % x for x in v.split("|")), f) for q, v, f in t["rows"])
    legend = ('<ul class="legend">'
              '<li><svg aria-hidden="true" width="8" height="14"><rect class="lg-f" x="3" y="2" width="1.6" height="10"/></svg>%s</li>'
              '<li><svg aria-hidden="true" width="8" height="14"><rect class="lg-i" x="3" y="2" width="1.6" height="10"/></svg>%s</li>'
              '<li><svg aria-hidden="true" width="8" height="14"><rect class="lg-r" x="3" y="2" width="1.6" height="10"/></svg>%s</li>'
              '<li><svg aria-hidden="true" width="8" height="14"><rect class="lg-f" x="3" y="2" width="1.6" height="10"/></svg>%s</li>'
              '<li><svg aria-hidden="true" width="20" height="14"><path class="lg-c" d="M0 11 C4 11 5 3 8 3 S12 11 15 9 S18 6 20 7"/></svg>%s</li></ul>') % tuple(t["legend"])

    def idx_row(name, stack, note="", href=True, fork=False, en=False):
        cell = ('<a href="%s%s">%s</a>' % (GH, name, name)) if href else '<span%s>%s</span>' % (' lang="en"' if en else "", name)
        if fork:
            cell += ' <span class="fk">%s</span>' % t["fk"]
        return '<tr%s><td class="nm">%s</td><td class="sk">%s%s</td><td class="nt">%s</td></tr>' % ("" if href else ' class="nolink"', cell, stack, lsh(name) if href and not fork else "", note)

    def grp(hid, label):
        return '<tr class="grp"><th colspan="3" scope="rowgroup"><a href="#%s">%s</a></th></tr>' % (hid, label)

    idx = ("".join([
        '<tbody>', grp("ricerca", t["k1"]), idx_row("flytollm", "PyTorch · CUDA"), '</tbody>',
        '<tbody>', grp("inferenza", t["k2"]), idx_row("llama.cpp", "C++ · CUDA", t["pra"], fork=True),
        idx_row("hildanext", "Python · PyTorch"), idx_row("bonsai-webgpu-tiled-vae-fix", "JavaScript · WebGPU", t["st2"]), '</tbody>',
        '<tbody>', grp("motion", t["k3"]), idx_row("llm2vec-8gb-offload-lossless-batching", "Python · PyTorch"),
        idx_row(t["npc"], "Unity · Python", '<span class="soon">%s</span>' % t["soon"], href=False, en=(L == "it" and False)), '</tbody>',
        '<tbody>', grp("locale", t["k4"]), idx_row("vergilius", "Python · llama.cpp"), idx_row("stt-whisper-pad", "Python", t["st1"]), '</tbody>',
        '<tbody>', grp("ml", t["k5"]), idx_row("fantaoracle", "Python", t["st2"]), idx_row("fantacalcio-advisor", "React · TypeScript · Python"),
        idx_row("K-Forecast", "Python"), idx_row("sp500-predictability-lab", "TypeScript · Python"), idx_row("storico", "Python"), '</tbody>',
        '<tbody>', grp("rl", t["k6"]), idx_row("supermario-1-1-rl", "TypeScript · Phaser 3"), idx_row("idle-isekai-trials", "JavaScript · Three.js"), '</tbody>',
    ]))

    head = """<!DOCTYPE html>
<html lang="{L}" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Adrian Iancu · AI Engineer</title>
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
<meta property="og:title" content="Adrian Iancu · AI Engineer">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{site}{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{ogimgalt}">
<meta property="og:locale" content="{ogloc}">
<meta property="og:locale:alternate" content="{ogalt}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{P}img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="{P}img/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="{P}img/apple-touch-icon.png">
<link rel="preload" href="{P}fonts/newsreader-roman-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{P}fonts/besley-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{P}fonts/tavola-mono-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{P}css/site.css">
<script>{boot}</script>
<script src="{P}js/site.min.js" defer></script>
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Person","name":"Adrian Iancu","jobTitle":"AI Engineer","url":"{site}","sameAs":["https://github.com/ArtyomITA","{li}"]}}</script>
</head>
""".format(L=L, desc=t["desc"], csp=CSP, canon=t["canon"], site=SITE, og=t["og"], ogimgalt=t["ogimgalt"], ogloc=t["ogloc"], ogalt=t["ogalt"], P=P, boot=BOOT, li=LI)

    body = f"""<body>
<a class="skip" href="#main">{t['skip']}</a>
<div class="mast-slot" id="mast-slot">
<header class="mast" id="mast">
<div class="mast-in wrap">
<a class="mast-name" href="#top">Adrian Iancu</a>
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
<p class="role"{en_attr}>{ROLE_H}</p>
<p class="folio">{t['folio']}</p>
<h1><span>Adrian</span> <span>Iancu</span></h1>
<div class="abstract"><p class="abs">{t['abs']}</p>
<p class="go contacts"><a href="https://github.com/ArtyomITA">GitHub</a><a href="{LI}">LinkedIn</a><a href="{PR}">llama.cpp · PR #27721</a></p></div>
<figure class="fig1" id="fig1">
<div class="rbox"><canvas id="raster" role="img" aria-label="{t['rasterlabel']}"></canvas></div>
<p class="readout" id="readout" aria-hidden="true"></p>
{legend}
<figcaption>{t['cap1']}</figcaption>
</figure>
<div class="more">
<p class="kw">{t['kw']}</p>
</div>
<table class="tab1">
<caption>{t['tcap']}</caption>
<thead><tr><th scope="col">{t['thq']}</th><th scope="col">{t['thv']}</th><th scope="col">{t['ths']}</th></tr></thead>
<tbody>{rows}</tbody>
</table>
</section>

<section class="sec wrap grid" id="ricerca" data-k="{t['k1']}" aria-labelledby="h-ricerca">
{TICKS}
<div class="runhead"><p class="kicker">{t['k1']}</p></div>
<div class="sec-main"><h2 id="h-ricerca">{t['h1s']}</h2><p class="lead" data-notes="n1">{t['lead1']}</p></div>
{note(1, t['n1'])}
<figure class="fig fig2" id="fig2">
<svg class="cns" id="cns" role="img" aria-labelledby="cap2"></svg>
<figcaption id="cap2">{t['cap2']}</figcaption>
</figure>
<article class="proj">
<h3><a href="{GH}flytollm">FlyToLLM</a></h3>
<p class="dateline">{t['dl1']}</p>
<p data-notes="n2">{t['d1']}</p>
{go(("https://artyomita.github.io/flytollm/", t['go1']))}
<p class="meth">{t['m1']}</p>
</article>
{note(2, t['n2'])}
</section>

<section class="sec wrap grid" id="inferenza" data-k="{t['k2']}" aria-labelledby="h-inferenza">
{TICKS}
<div class="runhead"><p class="kicker">{t['k2']}</p></div>
<div class="sec-main"><h2 id="h-inferenza">{t['h2s']}</h2><p class="lead">{t['lead2']}</p></div>
<article class="proj withmeta">
<h3 lang="en">CUDA graphs on Pascal</h3>
<p class="dateline">{t['dl2']}</p>
<dl class="meta"><div><dt>{t['md'][0]}</dt><dd>{t['mdv'][0]}</dd></div><div><dt>{t['md'][1]}</dt><dd>{t['mdv'][1]}</dd></div><div><dt>{t['md'][2]}</dt><dd>{t['mdv'][2]}</dd></div></dl>
<p>{t['d2']}</p>
{go((PR, "PR #27721"), (GH + "llama.cpp", t['fork']))}
</article>
<figure class="fig fig3" id="fig3">
<svg class="kt" id="kt" role="img" aria-labelledby="cap3"></svg>
<figcaption id="cap3">{t['cap3']}</figcaption>
</figure>
<div class="briefs">
{brief("hildanext", t['hild'], t['hilds'], GH + "hildanext")}
{brief("bonsai-webgpu-tiled-vae-fix", t['bons'], t['bonss'], GH + "bonsai-webgpu-tiled-vae-fix")}
</div>
</section>

<section class="sec wrap grid" id="motion" data-k="{t['k3']}" aria-labelledby="h-motion">
{TICKS}
<div class="runhead"><p class="kicker">{t['k3']}</p></div>
<div class="sec-main"><h2 id="h-motion">{t['h3s']}</h2><p class="lead">{t['lead3']}</p></div>
<article class="proj">
<h3 class="h3m"><a href="{GH}llm2vec-8gb-offload-lossless-batching">llm2vec-8gb-offload-lossless-batching</a></h3>
<p>{t['l2v']}</p>
<p class="meth">{t['m3']}</p>
</article>
<figure class="fig fig4" id="fig4">
<svg class="err" id="err" role="img" aria-labelledby="cap4"></svg>
<figcaption id="cap4">{t['cap4']}</figcaption>
</figure>
<div class="briefs">
{brief(t['npc'], t['npcd'], t['npcs'], None, mono=False, dateline=t['soon'])}
</div>
</section>

<section class="sec wrap grid" id="locale" data-k="{t['k4']}" aria-labelledby="h-locale">
{TICKS}
<div class="runhead"><p class="kicker">{t['k4']}</p><p class="epi" aria-hidden="true">127.0.0.1</p></div>
<div class="sec-main"><h2 id="h-locale">{t['h4s']}</h2><p class="lead">{t['lead4']}</p></div>
<article class="proj">
<h3><a href="{GH}vergilius">Vergilius</a></h3>
<p class="dateline">local-first</p>
<p data-notes="n3">{t['verg']}</p>
</article>
{note(3, t['n3'])}
<figure class="fig fig5" id="fig5">
<svg class="f5" id="fence" role="img" aria-labelledby="cap5"></svg>
<figcaption id="cap5">{t['cap5']}</figcaption>
</figure>
<div class="briefs">
{brief("stt-whisper-pad", t['stt'], t['stts'], GH + "stt-whisper-pad")}
</div>
</section>

<section class="sec wrap grid" id="ml" data-k="{t['k5']}" aria-labelledby="h-ml">
{TICKS}
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

<section class="sec sec-rl wrap grid" id="rl" data-k="{t['k6']}" aria-labelledby="h-rl">
{RULE}
<div class="runhead"><p class="kicker">{t['k6']}</p></div>
<div class="sec-main"><h2 id="h-rl">{t['h6s']}</h2><p class="lead">{t['lead6']}</p></div>
<div class="briefs">
{brief("supermario-1-1-rl", t['sm'], t['sms'], GH + "supermario-1-1-rl")}
{brief("idle-isekai-trials", t['idle'], t['idles'], GH + "idle-isekai-trials")}
</div>
</section>

<section class="sec sec-idx wrap grid" id="indice" data-k="{t['hidx']}" aria-labelledby="h-indice">
{RULE}
<div class="runhead"><p class="kicker">{t['kapp']}</p><p class="count">{t['idxm']}</p></div>
<div class="idx">
<h2 id="h-indice">{t['hidx']}</h2>
<table>
<caption>{t['idxcap']}</caption>
<thead><tr><th scope="col">{t['ih'][0]}</th><th scope="col">{t['ih'][1]}</th><th scope="col">{t['ih'][2]}</th></tr></thead>
{idx}
</table>
</div>
</section>

<section class="sec sec-note wrap grid" id="note" data-k="{t['hnote']}" aria-labelledby="h-note">
{RULE}
<div class="runhead"><h2 class="kicker" id="h-note">{t['hnote']}</h2></div>
<div class="sec-main"><p class="notetext">{t['note']}</p></div>
</section>

<section class="sec sec-aut wrap grid" id="autore" data-k="{t['haut']}" aria-labelledby="h-autore">
<div class="runhead"><h2 class="kicker" id="h-autore">{t['haut']}</h2></div>
<div class="sec-main author">
<img src="{P}img/avatar-192.webp" width="96" height="96" alt="{t['avalt']}" loading="lazy" decoding="async">
<div><p class="aname">Adrian Iancu</p>
<p class="go"><a href="https://github.com/ArtyomITA">GitHub</a><a href="{LI}">LinkedIn</a></p></div>
</div>
</section>
</main>

<footer class="foot wrap">
<p><span>{t['foot'][0]}</span><span>{t['foot'][1]}</span><button type="button" id="gridbtn" aria-pressed="false">{t['grid']}</button></p>
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
