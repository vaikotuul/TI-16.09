# Arenduspäevik

Iga etapi kohta üks kirje. Ole aus ebaõnnestumiste osas — need on
hindamise osa.

## Etapp 1 — Baaslahendus
**Prompt:** `prompts/01_baaslahendus.md`
**Mida agent tegi:**
- Lõi servade indekseerimise lepingu ja teisendusfunktsioonid `edge_to_index` ning `index_to_edge` (`src/game.py`).
- Implementeeris `GameState` klassi bitmaski-põhise olekuesitusega, kastide valmimise kontrolli (sh korraga 2 kasti valmimine sisemise serva sulgemisel), käiguvahetuse ja lisakäigu reeglid ning laua tekstipõhise renderdamise.
- Implementeeris juhusliku agendi `RandomAgent` (`src/agents/random_agent.py`).
- Implementeeris käsurea liidese `src/cli.py`, mis toetab inimese ja agendi vahelist mängu, käikude sisestamist nii indeksite kui koordinaatidena (`H r c`, `V r c`) ja tulemuste kuvamist.
- Kirjutas 19 ühiktesti (`tests/test_game.py`, `tests/test_random_agent.py`, `tests/test_cli.py`), saavutades `src/game.py` puhul 100% ja kogu projekti puhul 95% testikattuvuse.
**Mis läks katki / vajas parandust:**
- Töökeskkonnas puudusid algselt `pytest` ja `pytest-cov`, mis paigaldati `requirements.txt` alusel.
- Mängumootori loogikas ja reeglite realiseerimises tõrkeid ei tekkinud — kood läbis kõik koostatud testid koheselt.
**Mitu katset kulus:** 1 katse.

## Etapp 2 — Minimax
**Prompt:** `prompts/02_minimax.md`
**Mida agent tegi:**
- Implementeeris piiratud sügavusega minimax agendi (`src/agents/minimax_agent.py`) ja klassi `MinimaxAgent`.
- Realiseeris kriitilise lisakäigu reegli: kasti valmimisel saab sama mängija lisakäigu (`g + child_val`), ilma skoori negeerimata; skoori perspektiivi negeeritakse (`-child_val`) ainult kasti mittevalmimisel, kui käiguõigus läheb vastasele üle.
- Lisas globaalse ja agendi-tasemel lähtestatava sõlmede loenduri (`node_counter`), mis suureneb täpselt 1 võrra iga rekursiivse väljakutse alguses (kõik külastatud positsioonid, sh lehed).
- Implementeeris lehe hindamise funktsiooni, mis tagastab suhtelise seisu ja sobib oma täisarvulisuse tõttu 1-baidisesse transpositsioonitabelisse.
- Optimeeris mängumootorit (`src/game.py`), lisades `@functools.lru_cache` funktsioonidele `box_edges` ja `edge_boxes`, mis kiirendas otsingut üle 2 korra.
- Kirjutas 6 ühiktesti (`tests/test_minimax_agent.py`), sh fikseeritud 2x2 lõppmängu testi, mis kontrollib lisakäigu märgi korrektsust (vigane märk viigistab 2-2, õige võidab 4-0). Testikattuvus `minimax_agent.py` puhul 100%, kogu projektil 96%.
- Mõõtis baasjoone sõlmede arvud tühjal 3x3 laual:
  - Sügavus 1: 25 sõlme (0.0002 s)
  - Sügavus 2: 577 sõlme (0.0040 s)
  - Sügavus 3: 12 721 sõlme (0.0880 s)
  - Sügavus 4: 267 745 sõlme (1.83 s)
  - Sügavus 5: 5 368 225 sõlme (~35 s)
  - Sügavus 6: ~1.02 × 10^8 sõlme (~11 min puhtas Pythonis, puhta minimaxi praktiline lagi)
  - Sügavus 8: ~3.06 × 10^10 sõlme (ilma alpha-beta pügamiseta arvutuslikult teostamatu)
  - Sügavus 10: ~7.35 × 10^12 sõlme (ilma alpha-beta pügamiseta arvutuslikult teostamatu)
**Mis läks katki / vajas parandust:**
- Esialgses `choose_move` koodis oli mittevajalik varukontroll `if best_move is None: ...`, mis ei olnud saavutatav ja langetas testikattuvust; see asendati range `assert best_move is not None` kontrolliga.
- Puhta minimaxi kombinatoorne plahvatus tühjal 3x3 laual alates sügavusest 6 näitab selgelt alpha-beta pügamise (Etapp 3) hädavajalikkust.
**Mitu katset kulus:** 1 katse.


## Etapp 3a — Ebamäärane optimeerimisprompt
**Prompt:** `prompts/03_optimeerimine_ebamaarane.md` (esimene osa)
**Mida agent omal algatusel pakkus:**
- Analüüsis otsingu aegluse põhjuseid ja pakkus välja viis peamist optimeerimissuunda, mis tagavad identse käiguvaliku:
  1. Alpha-beta pügamine (pügab harud, mis ei saa lõpptulemust muuta).
  2. Käikude järjestamine (move ordering: kasti sulgevad käigud ja ohutud käigud enne ohverdamisi), mis tõstab alpha-beta pügamise efektiivsust.
  3. Transpositsioonitabel (olekute bitmask-vahemälu korduvate harude vältimiseks).
  4. Laua sümmeetriate kanoniseerimine (D4 dihedraalne rühm: pöörded ja peegeldused).
  5. Kiired bitboard-tehted (kastide valmimise kontroll eelarvutatud bitimaskidega ilma tsükliteta).
**Kas haaras iseseisvalt alpha-beta järele?** Jah, esimese ja peamise meetodina, sest see säilitab 100% matemaatiliselt minimax tulemuse, vähendades puu suurust parimal juhul $O(b^d)$ tasemelt $O(b^{d/2})$ tasemele.
**Kas pakkus ka move ordering'ut?** Jah, eraldi välja toodud, et alpha-beta saavutaks maksimaalse pügamisefekti (kasti sulgemised ja ohutud käigud esimesena).
**Kas pakkus midagi muud (bitboardid, TT, sümmeetria)?** Jah, pakkus nii transpositsioonitabelit (TT), sümmeetriate kanoniseerimist (D4 rühm) kui ka bitboard-kiirendusi.


## Etapp 3b — Selge alpha-beta prompt
**Prompt:** `prompts/03_optimeerimine_ebamaarane.md` (teine osa)
**Mida agent tegi:**
- Implementeeris `src/agents/alphabeta_agent.py` ja klassi `AlphaBetaAgent` depth-limited alpha-beta otsinguga.
- Realiseeris matemaatiliselt korrektse lisakäigu akna nihke: kasti sulgemisel (`g > 0`) perspektiiv ei muutu ning otsinguakent nihutatakse vastavalt $\alpha' = \alpha - g$ ja $\beta' = \beta - g$; käigu üleminemisel vastasele (`g == 0`) pööratakse aken ümber: $\alpha' = -\beta$, $\beta' = -\alpha$. See lahendab mängu tüüpilise lisakäigu "piiride vea" (bounds error).
- Lisas staatilise käikude järjestamise (`order_moves`):
  1. Ohutud käigud (servad, mis ei sulge kasti ega tekita ühegi kasti 3. külge).
  2. Kasti valmistavad käigud (`g > 0`).
  3. Kõik muud käigud (käigud, mis loovad kasti 3. külje ja ohverdavad kasti vastasele).
- Säilitas Etapp 2-ga täpselt samasuguse globaalse ja agendi-tasemel sõlmede loenduri (`node_counter`).
- Kirjutas ühiktestid (`tests/test_alphabeta_agent.py`), kontrollides muuhulgas 5 fikseeritud keskmängu positsioonil sügavusel 6 käiguvaliku ja hinnangu 100% identsust Etapp 2 minimaxiga. Testikattuvus `alphabeta_agent.py` puhul 100%, kogu projektil 97%.
**Mis läks katki / vajas parandust:**
- Algne kahtlus oli, kas staatiline käikude järjestamine võib viigiseisude korral valida minimaxist teistsuguse käigu. Test 5 fikseeritud keskmängu positsioonil näitas, et nii hinnangud kui valitud käigud langesid 100% kokku, kinnitades piiride ja otsinguloogika veatut toimimist.
**Sõlmede vähenemine (%):**
- Mõõdetud 5 fikseeritud keskmängu positsiooni baasil:
  - **Sügavusel 6:**
    - Minimax: 773 665 sõlme / positsioon (kokku 3 868 325 sõlme, aeg ~22 s)
    - Alpha-Beta: 7 374 sõlme / positsioon (kokku 36 871 sõlme, aeg 0.77 s)
    - **Sõlmede vähenemine: 99.05%** (üle 100x kiirem).
  - **Sügavusel 8:**
    - Minimax: arvutuslikult teostamatu (~3.06 × 10^10 sõlme)
    - Alpha-Beta: 47 238 sõlme / positsioon (kokku 236 190 sõlme, aeg 4.51 s)
    - **Sõlmede vähenemine: > 99.999%**.
  - **Sügavusel 10:**
    - Minimax: arvutuslikult teostamatu (~7.35 × 10^12 sõlme)
    - Alpha-Beta: 190 738 sõlme / positsioon (kokku 953 691 sõlme, aeg 16.30 s)
    - **Sõlmede vähenemine: > 99.9999%**.


## Etapp 4 — Transpositsioonitabel
**Prompt:** `prompts/04_transpositsioonitabel.md`
**Mida agent tegi:**
**Mis läks katki / vajas parandust:**
**Mõõdetud: aeg, tipp-mälu, tabeli suurus:**

## Etapp 5 — Sümmeetria
**Prompt:** `prompts/05_summeetria.md`
**Mida agent tegi:**
**Mis läks katki / vajas parandust:**
**Vähenemistegur:**

## Etapp 6 — Testid ja dokumentatsioon
**Prompt:** `prompts/06_testid_ja_dokumentatsioon.md`
**Mida agent tegi:**
**Katvuse protsent:**
**Kas clean clone + README juhised töötasid?**
