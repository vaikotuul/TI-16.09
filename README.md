# Punktid ja Kastid (Dots and Boxes)

Pythonis teostatud Punktid ja Kastid (Dots and Boxes) mängumootor, bitmask-olekuesitus, juhuslik agent ning käsurealiides.

## Kiirstart

### 1. Sõltuvuste paigaldamine (testide jaoks)

```bash
pip install -r requirements.txt
```

### 2. Mängu käivitamine (CLI)

Käivita käsurealt:

```bash
python -m src.cli
```

Käivitamisel küsitakse:
- Mängulaua suurust: kastide arv ridades ja veergudes (vaikimisi `3 3`).
- Esimest käijat: kas alustad sina (Inimene) või vastane (Juhuslik agent).

#### Käigu sisestamine

Käike saab sisestada kahel viisil:
1. **Koordinaatidena:**
   - Horisontaalne serv: `H <rida> <veerg>` (nt `H 0 1`)
   - Vertikaalne serv: `V <rida> <veerg>` (nt `V 1 2`)
2. **Serva indeksina:** täisarv `0` kuni `N - 1` (nt `5`).

Mängust väljumiseks kirjuta `q` või `quit`.

## Testid

Testide ja katvuse raporti käivitamiseks:

```bash
pytest
# või
python -m pytest
```

## Arenduspäevik

Vaata detailset etappide arengut ja mõõtmistulemusi failis [LOG.md](LOG.md).

