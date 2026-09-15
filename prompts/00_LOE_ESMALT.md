# Promptide järjekord

Kasuta neid promptfaile järjekorras, üks korraga. Iga etapi järel:
1. Kontrolli, et kood töötab (`pytest`, käivita CLI ise läbi).
2. Kirjuta LOG.md faili lühike kokkuvõte: mis prompt kasutati, mida agent
   tegi, mis läks valesti, mitu katset kulus parandamiseks.
3. Tee commit ja tag: `git add -A && git commit -m "stage N: ..." && git tag vN-...`
4. Alles siis liigu järgmise faili juurde.

1. `01_baaslahendus.md` — mängu tuum, servade esitus, juhuslik agent, CLI
2. `02_minimax.md` — piiratud sügavusega minimax
3. `03_optimeerimine_ebamaarane.md` — SISALDAB KAHTE osa (3a ja 3b),
   kasuta 3a esimesena, ilma alpha-beta't mainimata
4. `04_transpositsioonitabel.md` — transpositsioonitabel + iteratiivne süvenemine
5. `05_summeetria.md` — sümmeetria kanoniseerimine
6. `06_testid_ja_dokumentatsioon.md` — testid, benchmark, README, GitHub

Servade indekseerimise skeem, mis luuakse Etapp 1-s, on kõigi hilisemate
etappide jaoks fikseeritud leping — seda hiljem ei muudeta.
