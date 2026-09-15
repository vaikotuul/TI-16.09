# Etapp 1 — Punktid ja Kastid (Dots and Boxes) baasversioon

Loo Punktid ja Kastid mängu mootor Pythonis.

## Nõuded

- Mängulaua suurus on parameeter: `rows` ja `cols` (kastide arv), nt 3x3
  kasti tähendab 4x4 punkti grid'i.
- Esita mängulaud servade (edges) hulgana. Iga serv on kas horisontaalne
  või vertikaalne, identifitseeritud oma (row, col) asukohaga vastavas
  grid'is. Kasuta ühte täisarvu bitmaski kanoonilise olekuna: bitt `i`
  märgib, et serv `i` on joonistatud. Määra igale servale stabiilne indeks
  juba alguses ja kirjuta funktsioon, mis teisendab (serva_tüüp, row, col)
  <-> indeks mõlemas suunas.
- Kast saab valmis, kui kõik 4 selle serva on joonistatud. Kirjuta
  funktsioon, mis antud maski ja äsja lisatud serva põhjal tagastab, mitu
  kasti see serv valmis tegi (0, 1 või 2 — sisemine serv võib korraga
  valmis teha kaks kasti).
- Käigureegel: mängija, kes oma käiguga valmistab vähemalt ühe kasti,
  saab lisakäigu ja liigub uuesti. Mängija, kes ei valmista ühtegi kasti,
  annab käigu vastasele. See peab kehtima ka siis, kui üks käik valmistab
  korraga kaks kasti.
- Jälgi mõlema mängija skoori (valmistatud kastide arv).
- Mäng lõpeb, kui kõik servad on joonistatud. Võitja on see, kellel on
  rohkem kaste.
- Implementeeri juhuslike käikude agent (valib ühtlase tõenäosusega
  ülejäänud lubatud servade seast).
- Ehita käsurea liides (CLI), mis lubab inimesel mängida juhusliku agendi
  vastu, printides mängulaua oleku pärast igat käiku (punktid, joonistatud
  servad ja kastid koos neid võitnud mängija tähisega).
- Ei mingeid väliseid sõltuvusi — ainult Pythoni standardteek.
- Hoia funktsioonid fokusseeritud; ükski klass ega funktsioon üle ~100 rea.

## Väljundid

- `src/game.py` — mängulaua esitus, servade indekseerimine,
  kastide valmimise loogika, käigureeglid, mängu lõpu/võitja loogika.
- `src/agents/random_agent.py` — juhuslik agent.
- `src/cli.py` — mängitav CLI tsükkel.
- Lühike docstring `game.py` alguses, mis selgitab bitmaski servade
  indekseerimise skeemi, kuna hilisemad etapid sõltuvad selle stabiilsusest.

## Piirangud

- Ära implementeeri veel otsingut ega heuristikaid — ainult juhuslik agent.
- Ära lisa graafilist liidest (GUI).
- Siin valitud servade indekseerimise skeem on leping kõikide hilisemate
  etappide jaoks — dokumenteeri see selgelt ja ära muuda seda hiljem ilma
  sellest teatamata.
