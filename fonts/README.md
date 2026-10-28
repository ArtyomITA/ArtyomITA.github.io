# Font del sito

Tutti i font sono sotto SIL Open Font License 1.1 (testi in `OFL-geist.txt` e `OFL-jetbrains-mono.txt`).
Sorgente: repository ufficiale google/fonts su GitHub, a commit fissati. Nessun file di sistema.
Generati il 2026-10-28 con `python tools/build-fonts.py`.

## Sorgenti

| famiglia | file | URL | SHA-256 |
|---|---|---|---|
| geist | Geist[wght].ttf | https://raw.githubusercontent.com/google/fonts/718e1db4deb9e4d9d85a0ead1b9f5fde2761ccfd/ofl/geist/Geist%5Bwght%5D.ttf | `73894e0448cae90a92b6c2f8732b7bb9acb7b94c418bff559dad4a18e1de9659` |
| geist | OFL.txt | https://raw.githubusercontent.com/google/fonts/718e1db4deb9e4d9d85a0ead1b9f5fde2761ccfd/ofl/geist/OFL.txt | `1781d2806a07d91c4edf4740b88449fab7d0eadad53f7c351b94cd4d4eb8c00f` |
| jetbrainsmono | JetBrainsMono[wght].ttf | https://raw.githubusercontent.com/google/fonts/6e4b84c976cadb3c49a40fd9a1c203e4f7fcf2da/ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf | `48715a42ec242c21e9f02692891e147d022299a52e48d5e413e1a942193ffeda` |
| jetbrainsmono | OFL.txt | https://raw.githubusercontent.com/google/fonts/6e4b84c976cadb3c49a40fd9a1c203e4f7fcf2da/ofl/jetbrainsmono/OFL.txt | `b2fe5e8987594e9ffd1d2ca52a2f5d73eb8335243893c5d6254b5ad69269591d` |

## Reserved Font Name

- Geist: RFN nel file di licenza = no, il nome resta Geist.
- JetBrains Mono: RFN nel file di licenza = no, il nome resta JetBrains Mono.

## File prodotti

| file | byte | istanza |
|---|---|---|
| geist-latin.woff2 | 19880 | wght (400, 700) |
| jetbrains-mono-latin.woff2 | 14816 | wght (400, 600) |

## Procedura

1. `fontTools.varLib.instancer.instantiateVariableFont` con i limiti d'asse della tabella (l'asse wght resta variabile).
2. `fontTools.subset` con unicode-range latin (gli accenti italiani sono in Latin-1; vedi `tools/build-fonts.py`),
   feature `kern,liga,onum,lnum,tnum,pnum,sups,frac,ss01,ss05`, `--flavor=woff2 --desubroutinize --no-hinting`.
3. Rinomina dei nameID se la licenza dichiara un Reserved Font Name.
