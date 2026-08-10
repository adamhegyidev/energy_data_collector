# Energy Data Collector

🇭🇺 Magyar | 🇬🇧 English

---

# 🇭🇺 Magyar

## Áttekintés

Az **Energy Data Collector** egy moduláris adatgyűjtő és elemző rendszer energiaipari és meteorológiai idősorok automatizált gyűjtésére, feldolgozására, tárolására és vizualizációjára.

A projekt jelenleg két fő adatforrást kezel:

- **MAVIR** – magyar villamosenergia-rendszer adatai
- **Copernicus ERA5** – meteorológiai adatok

A rendszer támogatja a historikus adatok visszatöltését (backfill), az aktuális adatok napi automatikus frissítését, valamint az összegyűjtött idősorok interaktív összehasonlítását.

---

## Főbb képességek

- MAVIR adatok automatizált gyűjtése
- Copernicus ERA5 meteorológiai adatok gyűjtése
- historikus adatok visszatöltése (backfill)
- havi adatcsomagok kezelése
- napi automatikus adatfrissítés
- MAVIR rate limit kezelése
- nyers adatok megőrzése
- feldolgozott adatok Parquet formátumban
- SQLite alapú letöltési naplózás
- több évnyi idősor kezelése
- több földrajzi helyszín kezelése
- Streamlit alapú interaktív dashboard
- több adatsor egyidejű összehasonlítása
- mértékegység alapú grafikonkezelés
- konfigurációvezérelt adatforrás-kezelés

---

# Adatforrások

## MAVIR

A rendszer a MAVIR publikus adatforrásaiból villamosenergia-rendszeri idősorokat gyűjt.

A kezelt adatok között többek között megtalálhatók:

- erőművi termelési adatok
- hálózati frekvencia
- rendszeradatok
- rendszerterhelési adatok
- határmetszéki áramlások
- import/export adatok
- megújulóenergia-termelés
- napelemes termelés
- szélerőművi termelés
- CO₂-kibocsátási adatok
- szabályozási adatok
- kiegyenlítő szabályozási adatok

Az adatforrások konfigurációja a következő fájlban található:

```text
config/sources.yaml
```

A konfiguráció többek között meghatározza:

- MAVIR chart ID
- kategória
- lekérési periódus
- adatfrekvencia
- engedélyezett/letiltott állapot
- megjelenítési név
- csoport
- leírás
- mértékegység
- oszlopok megjelenítési neve

### Rate limit kezelés

A MAVIR szerver nem tolerálja jól a nagyszámú, gyors egymás utáni lekérést.

Ezért a MAVIR backfill és napi adatgyűjtés a lekérések között véletlenszerű várakozást alkalmaz.

Alapértelmezett várakozási idő:

```text
25–45 másodperc
```

Ez parancssori paraméterekkel módosítható.

---

## Copernicus ERA5

A meteorológiai adatok forrása a **Copernicus Climate Change Service ERA5 reanalysis** adatbázisa.

A rendszer több magyarországi földrajzi pontra képes meteorológiai idősorokat gyűjteni.

A jelenlegi konfiguráció többek között az alábbi változókat tartalmazza:

- 2 méteres hőmérséklet
- 2 méteres harmatpont
- 10 méteres U szélkomponens
- 10 méteres V szélkomponens
- 100 méteres U szélkomponens
- 100 méteres V szélkomponens
- felszíni napsugárzás
- nettó felszíni napsugárzás
- teljes felhőborítottság
- teljes csapadék
- havazás
- hómélység
- felszíni légnyomás
- tengerszinti légnyomás

A nyers U/V szélkomponensek is megőrzésre kerülnek, így később származtatott meteorológiai értékek is számíthatók belőlük.

---

# Adattárolás

A projekt külön kezeli a nyers és a feldolgozott adatokat.

## Nyers adatok

```text
data/raw/
├── mavir/
└── copernicus/
```

MAVIR esetén a nyers adatok jellemzően XLSX formátumban kerülnek tárolásra.

Copernicus esetén a nyers ERA5 adatok NetCDF (`.nc`) formátumban kerülnek tárolásra.

---

## Feldolgozott adatok

A feldolgozott idősorok havi **Parquet** fájlokban kerülnek tárolásra:

```text
data/processed/
├── mavir/
└── copernicus/
```

Példa:

```text
data/processed/
├── mavir/
│   └── frekvencia/
│       └── 2026/
│           └── 2026-08.parquet
│
└── copernicus/
    └── era5_hungary_points/
        └── budapest/
            └── 2026/
                └── 2026-08.parquet
```

A havi fájlstruktúra lehetővé teszi több évnyi idősor hatékony kezelését anélkül, hogy minden adatot egyetlen nagy fájlban kellene tárolni.

---

# Historikus adatok visszatöltése

A projekt támogatja korábbi időszakok havi bontású visszatöltését.

## MAVIR backfill

Egy teljes időszak összes engedélyezett MAVIR datasetjének letöltése:

```bash
python -m tools.backfill_mavir \
    --from 2024-01 \
    --to 2024-12
```

Egyetlen dataset:

```bash
python -m tools.backfill_mavir \
    --from 2024-01 \
    --to 2024-12 \
    --dataset frekvencia
```

Meglévő fájlok felülírása:

```bash
python -m tools.backfill_mavir \
    --from 2024-01 \
    --to 2024-12 \
    --overwrite
```

A MAVIR lekérések közötti várakozás módosítható:

```bash
python -m tools.backfill_mavir \
    --from 2024-01 \
    --to 2024-12 \
    --sleep-min 25 \
    --sleep-max 45
```

---

## Copernicus backfill

Egy időszak összes konfigurált helyszínére:

```bash
python -m tools.backfill_copernicus \
    --from 2024-01 \
    --to 2024-12
```

Egyetlen helyszín:

```bash
python -m tools.backfill_copernicus \
    --from 2024-01 \
    --to 2024-12 \
    --location budapest
```

Meglévő fájlok felülírása:

```bash
python -m tools.backfill_copernicus \
    --from 2024-01 \
    --to 2024-12 \
    --overwrite
```

---

# Napi adatfrissítés

A napi adatgyűjtő eszközök külön modulban találhatók:

```text
tools/daily/
├── __init__.py
├── update_mavir.py
├── update_copernicus.py
└── update_all.py
```

A napi frissítés nem külön napi fájlokat hoz létre.

Ehelyett az **aktuális havi adatcsomagot frissíti**.

Például 2026 augusztusában:

```text
2026-08.xlsx
2026-08.nc
2026-08.parquet
```

fájlok kerülnek folyamatosan frissítésre az új adatokkal.

---

## Csak MAVIR frissítése

```bash
python -m tools.daily.update_mavir
```

Egyetlen MAVIR dataset:

```bash
python -m tools.daily.update_mavir \
    --dataset frekvencia
```

---

## Csak Copernicus frissítése

```bash
python -m tools.daily.update_copernicus
```

Egyetlen helyszín:

```bash
python -m tools.daily.update_copernicus \
    --location budapest
```

---

## Minden adatforrás frissítése

```bash
python -m tools.daily.update_all
```

Az `update_all` sorrendben lefuttatja:

```text
MAVIR
  ↓
Copernicus
  ↓
összesítés
```

A folyamat hibakóddal is jelzi, ha valamelyik adatforrás frissítése nem volt teljesen sikeres.

---

# Automatikus napi futtatás

Linux rendszeren a napi adatgyűjtés cron segítségével automatizálható.

A crontab megnyitása:

```bash
crontab -e
```

Példa minden nap 06:00-kor történő futtatásra:

```cron
0 6 * * * cd /home/adam/projects/energy_data_collector && /home/adam/projects/energy_data_collector/venv/bin/python -m tools.daily.update_all >> /home/adam/projects/energy_data_collector/logs/daily_update.log 2>&1
```

A virtual environment aktiválása nem szükséges, mivel a cron közvetlenül a projekt `venv` Python interpreterét használja.

A futási log:

```text
logs/daily_update.log
```

A log megtekintése:

```bash
tail -100 logs/daily_update.log
```

Élő követés:

```bash
tail -f logs/daily_update.log
```

---

# Streamlit dashboard

Az összegyűjtött adatok egy interaktív Streamlit dashboard segítségével vizsgálhatók.

A dashboard belépési pontja:

```text
dashboards/app.py
```

Indítása:

```bash
streamlit run dashboards/app.py
```

A virtual environmentből közvetlenül:

```bash
./venv/bin/streamlit run dashboards/app.py
```

A dashboard többek között támogatja:

- tetszőleges dátumtartomány kiválasztását
- MAVIR adatsorok böngészését
- Copernicus meteorológiai adatok böngészését
- több helyszín kiválasztását
- több változó egyidejű kiválasztását
- MAVIR és meteorológiai adatok összehasonlítását
- több adatsor egy grafikonon történő megjelenítését
- azonos mértékegységű adatsorok közös Y tengelyen történő megjelenítését
- különböző mértékegységek külön Y tengelyen történő kezelését
- interaktív Plotly grafikonokat

Ez lehetővé teszi például:

- hőmérséklet és erőművi termelés
- felhőborítottság és napelemes termelés
- széladatok és szélerőművi termelés
- hálózati frekvencia és rendszeradatok

együttes vizsgálatát.

---

# Projektstruktúra

```text
energy_data_collector/
├── collectors/
│   ├── mavir.py
│   └── copernicus.py
│
├── processors/
│   ├── mavir.py
│   └── copernicus.py
│
├── config/
│   └── sources.yaml
│
├── database/
│
├── dashboards/
│   └── app.py
│
├── tools/
│   ├── backfill_mavir.py
│   ├── backfill_copernicus.py
│   ├── inspect_copernicus.py
│   └── daily/
│       ├── __init__.py
│       ├── update_mavir.py
│       ├── update_copernicus.py
│       └── update_all.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── logs/
│
├── utils/
│
└── venv/
```

---

# Tervezési alapelvek

## Megbízhatóság

Egyetlen adatforrás vagy dataset hibája lehetőség szerint nem állítja le a teljes adatgyűjtési folyamatot.

A hibás lekérések elkülönítve kezelhetők és naplózhatók.

## Bővíthetőség

Az adatforrások és megjelenítési metaadataik konfigurációvezérelten kezelhetők.

Új datasetek és helyszínek hozzáadása nagyrészt a konfiguráció módosításával megoldható.

## Reprodukálhatóság

A nyers adatok megőrzése lehetővé teszi:

- az eredeti adatok visszaellenőrzését
- újrafeldolgozást
- hibakeresést
- későbbi feldolgozási logika alkalmazását

## Hatékony tárolás

A feldolgozott adatok havi Parquet fájlokban kerülnek tárolásra.

Ez lehetővé teszi a több évnyi idősor hatékony és részleges betöltését.

## Collector és processor réteg szétválasztása

A collector réteg az adatok megszerzéséért felel.

A processor réteg a nyers adatok egységes idősoros formátummá alakításáért és Parquet tárolásáért felel.

---

# Fejlesztési irányok

- PostgreSQL / TimescaleDB
- fejlettebb retry mechanizmus
- automatikus adatminőség-ellenőrzés
- hiányzó adatok automatikus felismerése
- adatfolytonosság ellenőrzése
- monitoring és riasztások
- futási statisztikák
- Docker támogatás
- további meteorológiai helyszínek
- további energiaipari adatforrások
- elemzési modellek
- előrejelzési modellek

---

# Adatforrás és licenc

## Copernicus

Meteorológiai adatforrás:

**Copernicus Climate Change Service (C3S), ERA5 reanalysis**

A meteorológiai változók a Copernicus Climate Change Service ERA5 reanalysis datasetből származnak.

Data used under **CC BY 4.0**.

https://creativecommons.org/licenses/by/4.0/

---

# 🇬🇧 English

## Overview

**Energy Data Collector** is a modular data collection and analytics framework for automated acquisition, processing, storage and visualization of energy and meteorological time-series data.

The project currently integrates two primary data sources:

- **MAVIR** – Hungarian electricity system data
- **Copernicus ERA5** – meteorological reanalysis data

The system supports historical backfills, automated daily updates, monthly data packages and interactive time-series analysis.

---

## Core capabilities

- automated MAVIR data acquisition
- Copernicus ERA5 meteorological data acquisition
- historical backfills
- automated daily updates
- monthly raw and processed datasets
- rate-limit-aware MAVIR collection
- raw data preservation
- Parquet-based processed storage
- SQLite-based download logging
- multi-year time-series management
- multiple meteorological locations
- interactive Streamlit dashboard
- multi-series comparison
- unit-aware chart visualization
- configuration-driven data sources

---

# Data sources

## MAVIR

The system collects public Hungarian electricity-system time series from MAVIR.

Datasets include electricity generation, grid frequency, system load, cross-border flows, import/export, renewable generation, photovoltaic generation, wind generation, CO₂-related data and balancing/regulation data.

Source configuration is stored in:

```text
config/sources.yaml
```

MAVIR requests use configurable randomized delays to avoid excessive request frequency.

---

## Copernicus ERA5

Meteorological data is obtained from the **Copernicus Climate Change Service ERA5 reanalysis** dataset.

Variables include:

- 2 m temperature
- 2 m dew point temperature
- 10 m U wind component
- 10 m V wind component
- 100 m U wind component
- 100 m V wind component
- surface solar radiation
- surface net solar radiation
- total cloud cover
- total precipitation
- snowfall
- snow depth
- surface pressure
- mean sea-level pressure

Multiple geographical locations can be configured.

---

# Data storage

Raw data:

```text
data/raw/
├── mavir/
└── copernicus/
```

Processed monthly Parquet datasets:

```text
data/processed/
├── mavir/
└── copernicus/
```

Example:

```text
data/processed/
├── mavir/
│   └── frekvencia/
│       └── 2026/
│           └── 2026-08.parquet
│
└── copernicus/
    └── era5_hungary_points/
        └── budapest/
            └── 2026/
                └── 2026-08.parquet
```

---

# Historical backfill

## MAVIR

```bash
python -m tools.backfill_mavir \
    --from 2024-01 \
    --to 2024-12
```

Single dataset:

```bash
python -m tools.backfill_mavir \
    --from 2024-01 \
    --to 2024-12 \
    --dataset frekvencia
```

## Copernicus

```bash
python -m tools.backfill_copernicus \
    --from 2024-01 \
    --to 2024-12
```

Single location:

```bash
python -m tools.backfill_copernicus \
    --from 2024-01 \
    --to 2024-12 \
    --location budapest
```

---

# Daily updates

Update MAVIR:

```bash
python -m tools.daily.update_mavir
```

Update Copernicus:

```bash
python -m tools.daily.update_copernicus
```

Update all data sources:

```bash
python -m tools.daily.update_all
```

The current monthly packages are regenerated as new data becomes available.

---

# Automated scheduling

The complete daily pipeline can be scheduled using cron.

Example: run every day at 06:00:

```cron
0 6 * * * cd /home/adam/projects/energy_data_collector && /home/adam/projects/energy_data_collector/venv/bin/python -m tools.daily.update_all >> /home/adam/projects/energy_data_collector/logs/daily_update.log 2>&1
```

---

# Dashboard

The Streamlit dashboard is located at:

```text
dashboards/app.py
```

Start the dashboard with:

```bash
streamlit run dashboards/app.py
```

The dashboard supports:

- arbitrary date ranges
- multiple MAVIR datasets
- multiple Copernicus locations
- multiple meteorological variables
- simultaneous time-series comparison
- unit-aware Y axes
- interactive Plotly charts

---

# Project status

Active development.

Planned improvements include:

- PostgreSQL / TimescaleDB
- advanced retry mechanisms
- automated data-quality validation
- missing-data detection
- monitoring and alerting
- Docker support
- additional energy and meteorological data sources
- analytical and forecasting models

---

# Data attribution

Meteorological data source:

**Copernicus Climate Change Service (C3S), ERA5 reanalysis**

Meteorological variables are obtained from the Copernicus Climate Change Service ERA5 reanalysis dataset.

Data used under **CC BY 4.0**.

https://creativecommons.org/licenses/by/4.0/