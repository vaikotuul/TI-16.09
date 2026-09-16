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
- Implementeeris faili `src/agents/transposition_agent.py` ja agendiklassi `TranspositionAgent`.
- Kasutas transpositsioonitabeli võtmena AINULT servade maski, tagades otsingufunktsiooni tulemuse väljendamise käigul oleva mängija suhtes (negamax konventsioon).
- Implementeeris kaks transpositsioonitabeli varianti:
  1. `FlatTranspositionTable` — lame massiiv (`bytearray`) otsese indekseerimisega ilma räsifunktsiooni ega kollisioonideta.
  2. `DictTranspositionTable` — Pythoni sõnastikupõhine (`dict`) võrdlusversioon.
- Salvestas standardse alpha-beta kirje formaadi: `(depth, flag, value, best_move)`, toetades lipukesi `FLAG_EXACT`, `FLAG_LOWERBOUND` ja `FLAG_UPPERBOUND`. Lisaks kasutatakse tabelisse salvestatud parimat käiku otsingu esimese proovitava käiguna (`tt_move`).
- Realiseeris iteratiivse süvenemise (`choose_move_iterative_deepening`) kellaajapõhise eelarvega (vaikimisi 1.0 sekund), säilitades ja taaskasutades transpositsioonitabeli kirjeid järjest sügavamate iteratsioonide vahel.
- Kirjutas 7 ühiktesti (`tests/test_transposition_agent.py`), saavutades `transposition_agent.py` testikattuvuseks 99%.
**Mis läks katki / vajas parandust:**
- Iteratiivse süvenemise ajapiirangu kontrollimisel tuli tagada, et kui viimane iteratsioon ületab ajalimiidi, ei tagastataks pooleli jäänud ebausaldusväärset käiku, vaid eelmise täielikult lõpetatud sügavuse parim käik.
**Mõõdetud: aeg, tipp-mälu, tabeli suurus:**
- **Lameda massiivi (Flat TT) teoreetiline ja tegelik suurus:**
  - 1 baiti kirje kohta (teoreetiline lahendatud väärtuse tabel):
    - 2x2 laud: $2^{12}$ baiti = 4 096 B = **0.0039 MiB** (0.0041 MB)
    - 3x3 laud: $2^{24}$ baiti = 16 777 216 B = **16.0000 MiB** (16.78 MB)
  - 4 baiti kirje kohta (`depth, flag, val, move`):
    - 2x2 laud: 16 384 B = **0.0156 MiB** (16 KB)
    - 3x3 laud: 67 108 864 B = **64.0000 MiB** (64 MB)
- **2x2 laua ammendav lahendamine (depth = 12, ammendav lõpplahendus):**
  - Optimaalne väärtus: +2 (Player 1 võidab 3 kasti 1 vastu), avakäik = 0.
  - Sõlmi kokku: 7 670
  - **Flat TT:** aeg = **1.01 s**, tipp-mälu (`tracemalloc`) = **19.5 KB**
  - **Dict TT:** aeg = **1.09 s**, tipp-mälu (`tracemalloc`) = **249.0 KB** (1 614 kirjet)
  - Lame massiiv saavutas üle 12x väiksema tipp-mälukasutuse ja oli kiirem.
- **3x3 laua lahendamise katse ja iteratiivne süvenemine:**
  - Täielik ammendav lahendamine 5 minuti jooksul ei lõpe (24 serva olekuruum ilma sümmeetriata nõuab miljardeid haruhindamisi).
  - Iteratiivse süvenemise saavutatud sügavused tühjal 3x3 laual:
    - **1 s eelarve:** saavutatud sügavus **6**, 83 750 sõlme, 4 652 TT kirjet (aeg 1.91 s)
    - **10 s eelarve:** saavutatud sügavus **9**, 741 766 sõlme, 53 026 TT kirjet (aeg 17.91 s)
    - **60 s eelarve:** saavutatud sügavus **12**, 4 301 471 sõlme, 354 801 TT kirjet (aeg 105.06 s)


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
