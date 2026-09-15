# Etapp 6 — Testikomplekt, Benchmark, README

Vii projekt esitamiseks lõplikule kujule.

## Nõuded

### Testid (`tests/`)
- Kasuta `pytest`.
- Kata: servade indekseerimise ümbertegemine (round-trip), kastide
  valmimise tuvastamine (sh topelt-kasti juhtum), lisakäigu loogika,
  minimax vs alpha-beta käiguvaliku kokkulangevus (Etapp 3 test),
  transpositsioonitabeli korrektsus (Etapp 4), sümmeetria
  kanoniseerimise korrektsus (Etapp 5).
- Lisa `pytest-cov` konfiguratsioon ja raporteeri katvuse protsent.

### Benchmark (`bench/benchmark.py`)
- Määratle üks fikseeritud komplekt ~20 keskmängu 3x3-kasti
  positsioonist (servade maskidena), genereeritud üks kord ja
  salvestatud `bench/positions.json` faili, et iga etapp mõõdetaks
  täpselt sama komplekti vastu.
- Iga etapi agendi jaoks (random / minimax / alpha-beta / TT /
  symmetry) käivita kõik 20 positsiooni sügavustel 6, 8, 10 (kus
  kohaldatav) ja salvesta `bench/results.csv` faili:
  `stage, depth, position_id, nodes, seconds, nodes_per_sec, peak_kb`
- Kasuta ajastamiseks `time.perf_counter()` ja tipp-mälu jaoks
  `tracemalloc`, järgides sama mustrit, mida kasutati varasemates
  etappides — ära too selles etapis sisse teistsugust mõõtmismeetodit.
- Prindi stdout'i kokkuvõtlik tabel, kui käivitada otse.

### README.md
- Ühelõiguline kirjeldus mängust ja agendist.
- Kuidas käivitada: CLI mäng, testid, benchmark.
- Tulemuste tabel (etapp vs. sõlmed sügavusel 8 vs. sõlmed/sekundis
  vs. tipp-mälu), genereeritud `bench/results.csv` põhjal.
- Lühike "optimeerimised" sektsioon, mis loetleb iga etapi
  optimeerimise ja selle mõõdetud mõju — see on sektsioon, mida
  õppejõud loeb esimesena, seega tee numbrid pealkirjaks, mitte proosaks.
- Link `LOG.md` failile täieliku arendus-päeviku jaoks.

### GitHub
- Veendu, et repo on avalik (või õppejõule ligipääsetav) ja et
  `git clone` + README-s toodud käivitusjuhised töötavad puhtal
  kloonimisel — testi seda sõna otseses mõttes (nt puhtas kaustas
  või konteineris) enne esitamist.
- Märgista iga etapi lõplik commit (`v1-baseline` ... `v6-final`), et
  hindaja saaks iga etapi otse checkout'ida ja diffida.

## Piirangud

- Ära lisa selles etapis uusi mänguomadusi — see on ainult
  konsolideerimine.
- Ära muuda agendi loogikat, välja arvatud testikomplekti poolt
  esile toodud vigade parandamiseks; logi iga selline parandus
  eraldi kirjena LOG.md faili.
