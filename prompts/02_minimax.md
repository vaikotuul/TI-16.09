# Etapp 2 — Piiratud sügavusega Minimax

Lisa olemasolevale Punktid ja Kastid mootorile (`src/game.py`) minimax agent.

## Nõuded

- Implementeeri `src/agents/minimax_agent.py`, mis teeb piiratud
  sügavusega minimax otsingut Etapp 1 servade-maski esituse peal.
- Kriitiline reegel: kasti valmistamine annab lisakäigu SAMALE mängijale.
  Rekursiivne kutse EI TOHI skoori negeerida, kui äsja tehtud käik
  valmistas ühe või mitu kasti — negeeri (vaheta perspektiivi) ainult
  siis, kui käik tegelikult läheb vastasele üle. See on selle mängu
  otsingus kõige levinum viga, tee see kindlasti õigesti.
- Heuristiline hindamisfunktsioon sügavuspiiri saavutamisel: vähemalt
  (minu kastid - vastase kastid), soovi korral täiendatud "ohutute"
  servadega (servad, mis ei loo ühegi kasti 3. külge, kuna 3. külg
  kingib vastasele kasti).
- Lisa globaalne, lähtestatav sõlmede loendur (node counter), mis
  suureneb üks kord iga rekursiivse kutse kohta (iga läbitud positsioon,
  sh lehed), ja tee see kättesaadavaks, et benchmark saaks selle pärast
  igat `choose_move` kutset välja lugeda.
- `choose_move(mask, player, depth)` tagastab parima lubatud serva
  indeksi.
- Kirjuta ühiktest, mis mängib läbi väikese fikseeritud 2x2-kasti mängu
  lõpuni (depth = kogu mängu pikkus) ja kontrollib, et tulemus vastab
  käsitsi kontrollitud oodatud võitjale — see püüab kinni lisakäigu
  märgi vea.

## Piirangud

- Veel ei mingit alpha-beta pügamist — ainult puhas minimax, et Etapp 3
  pügamise tulemusi saaks mõõta reaalse baasjoone vastu.
- Veel ei mingit transpositsioonitabelit.
- Kasuta uuesti Etapp 1 servade indekseerimist ja kastide valmimise
  funktsioone; ära implementeeri neid uuesti.
- Kirjuta lühikese kommentaari või docstring'una üles sõlmede arv, mida
  näed sügavusel 6, 8 ja 10 tühjal 3x3-kasti laual — sellest saab
  Etapp 3/4 baasjoon.
