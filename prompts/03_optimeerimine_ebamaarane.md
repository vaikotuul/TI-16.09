# Etapp 3a — Ebamäärane optimeerimisprompt (kasuta seda ESIMESENA, sõna-sõnalt)

See mootor on 3x3-kasti laual sügavusel 7 liiga aeglane. Tee see
kiiremaks. Ära muuda, millist käiku see lõpuks valib, võrreldes Etapp 2
minimax agendiga.

---

# Kirjuta enne edasiminekut üles:

- Mida agent omal algatusel pakkus?
- Kas ta haaras iseseisvalt alpha-beta pügamise järele?
- Kas ta pakkus ka käikude järjestamist (move ordering) ilma, et talle
  seda öeldaks?
- Kas ta pakkus midagi muud (bitboardid, transpositsioonitabel,
  sümmeetria)?

Kirjuta see LOG.md faili enne allolevale selgele promptile üleminekut —
see võrdlus ongi harjutuse mõte.

---

# Etapp 3b — Selge alpha-beta prompt (kasuta seda TEISENA)

Lisa Etapp 2 minimax agendile alpha-beta pügamine.

## Nõuded

- Implementeeri `src/agents/alphabeta_agent.py` (või laienda minimax
  agenti lipuga) lisades sama sügavuspiiratud otsingule alpha-beta
  pügamise.
- Lisa käikude järjestamine: proovi esmalt servi, mis ei loo ühegi kasti
  3. külge (ohutud käigud), seejärel servi, mis valmistavad kasti, ja
  siis kõike muud. See on lihtne staatiline järjestus, mitte
  killer-move tabel.
- Säilita sama sõlmede loendur Etapp 2-st, sama moodi suurenedes, et
  sõlmede arvud oleksid minimaxi ja alpha-beta vahel samal sügavusel ja
  positsioonil otseselt võrreldavad.
- Korrektsuse test: vähemalt 5 fikseeritud keskmängu positsiooni ja
  sügavuse 6 juures kontrolli, et alpha-beta agent ja Etapp 2 minimax
  agent valivad sama käigu. Kui ei vali, on alpha-beta valesti
  implementeeritud (piiride viga) — paranda see, ära leevenda testi.

## Piirangud

- Ära lisa veel transpositsioonitabelit (Etapp 4).
- Ära muuda Etapp 2 hindamisfunktsiooni.
- Benchmarki sama fikseeritud positsioonide komplekti vastu, mida Etapp 2,
  ja raporteeri sõlmede arvu vähenemine (%) sügavustel 6, 8, 10.
