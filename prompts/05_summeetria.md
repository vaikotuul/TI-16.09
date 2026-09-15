# Etapp 5 — Sümmeetria kanoniseerimine

Vähenda tegelikku olekuruumi, tunnistades, et paljud servade maskid
esindavad sama strateegilist positsiooni mängulaua sümmeetriate tõttu.

## Nõuded

- Ristkülikukujulisel Punktid ja Kastid laual on kuni 8 sümmeetriat
  (dihedraalne rühm D4): identiteet, 3 pööret ja 4 peegeldust — vähem,
  kui rows != cols (mittekandiline laud omab ainult neid 4
  peegeldust/identiteeti, mis säilitavad selle küljesuhet; 90-kraadised
  pöörded kehtivad ainult siis, kui rows == cols).
- Iga sümmeetria jaoks implementeeri servade indeksite permutatsioon:
  antud Etapp 1 servade-indekseerimise skeemi puhul arvuta, kuhu iga
  serva indeks selle teisenduse all kaardistub. Arvuta need
  permutatsioonitabelid ette (üks kord käivitamisel), mitte iga
  otsingu ajal.
- Enne transpositsioonitabelisse päringu tegemist või sinna kirjutamist
  arvuta kõik praeguse maski kehtivad sümmeetrilised variandid
  (rakendades iga permutatsiooni) ja kasuta tulemusena saadud
  leksikograafiliselt vähimat maski kanoonilise võtmena.
- Korrektsuse test: konstrueeri positsioon ja selle käsitsi pööratud/
  peegeldatud vaste, kontrolli, et mõlemad kanoniseeruvad samaks
  võtmeks, ja kontrolli, et agent hindab neid võrdse väärtusega.
- Käivita uuesti Etapp 4 korrektsuse testid (samad käiguvalikud, mis
  Etapp 3-s) — kanoniseerimine ei tohi muuta, milline käik valitakse,
  ainult seda, mitu olekut salvestatakse.

## Mõõda ja raporteeri

- Tegelike kanooniliste olekute arv, mis salvestati 3x3-kasti laual,
  võrreldes Etapp 4 toore maski arvuga, samal otsingusügavusel/
  ajaeelarvel.
- Tegelik täheldatud vähenemistegur (peaks olema lähedal, kuid mitte
  täpselt 8x, kuna mõned positsioonid on ise-sümmeetrilised ühe või
  mitme teisenduse all ja kollapseeruvad ainult osaliselt).
- Iga muutus sõlmed/sekundis või kellaajas lisandunud kanoniseerimise
  ülekulu tõttu iga päringu kohta — see on juhtum, kus "väiksem
  olekuruum" optimeerimine võib ikkagi olla netokahjum, kui päringu
  hind on liiga kõrge — raporteeri, kumb suund see selles
  implementatsioonis on.

## Piirangud

- Ära muuda Etapp 1 servade indekseerimise skeemi.
- Hoia lameda massiivi transpositsioonitabeli valik töökorras;
  kanoniseerimine peaks vähendama, mitu erinevat kirjet sinna kunagi
  kirjutatakse, mitte muutma selle salvestusmehhanismi.
