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
**Mis läks katki / vajas parandust:**
**Mitu katset kulus:**

## Etapp 3a — Ebamäärane optimeerimisprompt
**Prompt:** `prompts/03_optimeerimine_ebamaarane.md` (esimene osa)
**Mida agent omal algatusel pakkus:**
**Kas haaras iseseisvalt alpha-beta järele?**
**Kas pakkus ka move ordering'ut?**
**Kas pakkus midagi muud (bitboardid, TT, sümmeetria)?**

## Etapp 3b — Selge alpha-beta prompt
**Prompt:** `prompts/03_optimeerimine_ebamaarane.md` (teine osa)
**Mida agent tegi:**
**Mis läks katki / vajas parandust:**
**Sõlmede vähenemine (%):**

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
