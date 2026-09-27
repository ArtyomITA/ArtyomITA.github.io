# Font del sito

Tutti i font sono sotto SIL Open Font License 1.1 (testi in `OFL-newsreader.txt`, `OFL-cascadia.txt` e `OFL-besley.txt`).
Sorgente: repository ufficiale google/fonts su GitHub, a commit fissati. Nessun file di sistema.
Generati il 2026-09-26 con `python tools/build-fonts.py`.

## Sorgenti

| famiglia | file | URL | SHA-256 |
|---|---|---|---|
| newsreader | Newsreader[opsz,wght].ttf | https://raw.githubusercontent.com/google/fonts/8b0a1d0f5983c89bc2b93f1b5fb55f9e252744b5/ofl/newsreader/Newsreader%5Bopsz%2Cwght%5D.ttf | `8a08d13f8a6c0d51be379a60af84f945f65369a67e509ee3c3bdcc421254d7c1` |
| newsreader | OFL.txt | https://raw.githubusercontent.com/google/fonts/8b0a1d0f5983c89bc2b93f1b5fb55f9e252744b5/ofl/newsreader/OFL.txt | `fdfad38143ec470553cae82a1e45320bdd1b9ec70415d37bd0171051d8a4ded8` |
| cascadiamono | CascadiaMono[wght].ttf | https://raw.githubusercontent.com/google/fonts/3dd78844021e948ceb633d1dcee3f7885561b5d9/ofl/cascadiamono/CascadiaMono%5Bwght%5D.ttf | `78864a1b4d03767a44731454a6f24c6b7d6e93fb5f62932860eb02e409cd50cb` |
| cascadiamono | OFL.txt | https://raw.githubusercontent.com/google/fonts/3dd78844021e948ceb633d1dcee3f7885561b5d9/ofl/cascadiamono/OFL.txt | `82c05d6c53dfa0c9025985c19e371810020b74ed2c61d51d370f2a8ab2506d52` |
| besley | Besley[wght].ttf | https://raw.githubusercontent.com/google/fonts/c13390277dfb1fcc7415d84ef7ef9cfc1e52f8c1/ofl/besley/Besley%5Bwght%5D.ttf | `71f352d8859c787631a0978161d48497a72caa69dcae6996d6712a564df86c1e` |
| besley | OFL.txt | https://raw.githubusercontent.com/google/fonts/c13390277dfb1fcc7415d84ef7ef9cfc1e52f8c1/ofl/besley/OFL.txt | `e8d81ba3b06080b764626d4385f319344e102ddf2c08bb4209412ac22d695f69` |

Controllo: SHA-256 di `C:\Windows\Fonts\CascadiaMono.ttf` = `0e141cb99609f6f10ad05313fd1807d5cc9e28658dcbb35ab162e52ff67dc718` (diverso dai sorgenti sopra: il file di sistema non è usato).

## Reserved Font Name

- Newsreader: RFN nel file di licenza = no, il nome resta Newsreader.
- Besley: RFN nel file di licenza = no, il nome resta Besley.
- Cascadia Mono: RFN nel file di licenza = sì. Il sottoinsieme modificato è quindi rinominato **Tavola Mono** (nameID 1 "Tavola Mono", 4 "Tavola Mono Regular", 6 "TavolaMono-Regular"; nameID 16, 17, 21, 22, 25 rimossi). Copyright e licenza restano quelli originali.

## File prodotti

| file | byte | istanza |
|---|---|---|
| newsreader-roman-latin.woff2 | 92184 | opsz (6, 72), wght (400, 600) |
| newsreader-roman-latin-ext.woff2 | 61148 | opsz (6, 72), wght (400, 600) |
| tavola-mono-latin.woff2 | 11360 | wght 400 |
| tavola-mono-latin-ext.woff2 | 11252 | wght 400 |
| besley-latin.woff2 | 18672 | wght 400 |
| besley-latin-ext.woff2 | 9288 | wght 400 |

## Procedura

1. `fontTools.varLib.instancer.instantiateVariableFont` con i limiti d'asse della tabella.
2. `fontTools.subset` con unicode-range latin e latin-ext (vedi `tools/build-fonts.py`),
   feature `kern,liga,onum,lnum,tnum,pnum,sups,frac,ss01`, `--flavor=woff2 --desubroutinize --no-hinting`.
3. Rinomina dei nameID se la licenza dichiara un Reserved Font Name.
