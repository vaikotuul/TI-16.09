# Etapp 4 — Transpositsioonitabel

Lisa alpha-beta agendile transpositsioonitabel, et erinevate käikude
järjekordade kaudu saavutatud korduvaid servade maske lahendataks ainult
üks kord.

## Nõuded

- Kasuta võtmena AINULT servade maski. Selleks, et see kehtiks, peab
  otsingufunktsioon tagastama skoori, mis on väljendatud selle mängija
  suhtes, kelle käik parasjagu on (samasugune konventsioon nagu
  negamaxis) — mitte absoluutset "mängija 1 miinus mängija 2" skoori.
  Kui skoor on võtmestatud ainult maski järgi, aga arvutatud absoluutse
  mängija konventsiooniga, tagastab vahemälu valesid väärtusi — saa see
  perspektiivi-suhteline konventsioon esimesena õigesti, siis on vahemälu
  lihtsalt tavaline memo.
- Kasuta lamedat massiivi (nt `array('b', ...)` või bytearray) suurusega
  `2**num_edges` piisavalt väikeste laudade jaoks, kus see täielikult
  lahendatud kujul mällu mahub (2x2 ja 3x3 kasti), nii et indeks ongi
  mask ise — ei mingit hashimist, ei mingit kollisiooni. Implementeeri
  võrdluseks ka dict-põhine versioon.
- Salvesta iga kirje juures piisavalt infot, et teada, kas salvestatud
  väärtus on täpne või alumine/ülemine piir (vajalik, kuna alpha-beta
  võib toota piiratud väärtusi, mitte ainult täpseid) — standardne
  alpha-beta transpositsioonitabeli kirje formaat: (depth, flag, value).
- Lisa iteratiivne süvenemine (iterative deepening) kellaajapõhise
  eelarvega (vaikimisi 1 sekund): otsi sügavusi 1, 2, 3, ... kasutades
  transpositsioonitabelit iteratsioonide vahel, peata ja tagasta parim
  seni leitud käik, kui eelarve ületatakse.
- Lahenda 2x2-kasti mäng täielikult (piisavalt väike, et olla ammendav)
  ja raporteeri kellaaeg ning tipp-mälukasutus (`tracemalloc` abil) nii
  lameda massiivi kui dict-põhise transpositsioonitabeli jaoks.
- Proovi lahendada 3x3-kasti mäng täielikult. Raporteeri, kas see
  lõpetab mõistliku ajaeelarve sees (nt 5 minutit), ja kui mitte, kui
  kaugele iteratiivne süvenemine jõudis 1, 10 ja 60 sekundiga.

## Piirangud

- Ära implementeeri veel sümmeetria vähendamist (Etapp 5) — see tuleb
  pärast seda, kui sul on puhas baasjoon tabeli suuruse ja tabamuste
  määra (hit rate) võrdlemiseks.
- Raporteeri lameda massiivi versiooni tabeli suurus MB-des laudadel 2x2
  ja 3x3 (peaks olema täpselt `2**num_edges` baiti, kui kasutad 1 baiti
  kirje kohta — arvuta ja too see number välja, ära lihtsalt profileerija
  väljundit kopeeri).
- Hoia kõik Etapp 3 korrektsuse testid läbivana (samad käiguvalikud).
