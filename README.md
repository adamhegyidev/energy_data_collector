# Energy Data Collector

🇭🇺 Magyar | 🇬🇧 English

---

# 🇭🇺 Magyar

## Áttekintés

Az Energy Data Collector egy moduláris, skálázható adatgyűjtő keretrendszer energiaipari és egyéb időfüggő adatforrások automatizált gyűjtésére, tárolására és hosszú távú feldolgozására.

A projekt célja egy megbízható és bővíthető architektúra kialakítása heterogén adatforrások folyamatos gyűjtésére, historikus adatok visszamenőleges rekonstrukciójára, valamint későbbi elemzési és modellezési felhasználás támogatására.

## Főbb képességek

- automatizált adatgyűjtés
- historikus adatok visszatöltése (backfill)
- ütemezett adatfrissítés
- hibatűrő működés
- rate limit kezelés
- nyers adatok megőrzése
- SQLite alapú állapotkezelés
- több adatforrás támogatása
- bővíthető collector architektúra

## Architektúra

main.py → collector → HTTP layer → storage → state → backup

## Tervezési alapelvek

### Megbízhatóság
Az adatgyűjtési hibák kezelése nem okozhat teljes rendszerleállást.

### Bővíthetőség
Új adatforrások minimális implementációs költséggel integrálhatók.

### Reprodukálhatóság
A nyers adatok megőrzése biztosítja a visszaellenőrizhetőséget.

### Karbantarthatóság
A közös funkcionalitások absztrakciója csökkenti a rendszer komplexitását.

## Fejlesztési irányok

- PostgreSQL / TimescaleDB
- retry mechanizmusok
- monitorozás
- Docker

# 🇬🇧 English

## Overview

Energy Data Collector is a modular and scalable framework designed for automated collection, storage and long-term processing of energy-domain datasets.

The framework supports heterogeneous data acquisition, historical reconstruction workflows and analytical pipelines.

## Core capabilities

- automated data acquisition
- historical backfill
- scheduled collection
- fault tolerance
- rate limit handling
- raw data preservation
- SQLite-based persistence
- extensible architecture

## Project status

Early-stage development.
