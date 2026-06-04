# Data Extraction Pipeline — Scraper Module

This document covers the full implementation of the automated data extraction pipeline for Auralis Tech. The pipeline is split into two independent phases: HTML scraping to JSON, and JSON loading into PostgreSQL.

-----

## Overview

The scraper follows a strict two-phase ETL architecture required by the project specification:

|Phase|Script         |Input             |Output                      |
|-----|---------------|------------------|----------------------------|
|1    |`scraper.py`   |CoolMod live pages|`productos.json`            |
|2    |`json_to_db.py`|`productos.json`  |PostgreSQL `productos` table|

This separation ensures the JSON file acts as a recoverable intermediate checkpoint — if the database load fails, the scraped data is not lost.

-----

## Directory Structure

```
scraper/
├── scraper.py          # Phase 1 — HTTP scraping → productos.json
├── json_to_db.py       # Phase 2 — JSON → PostgreSQL upsert
├── database_utils.py   # Data access layer (connection, upsert logic)
├── requirements.txt    # Python dependencies
├── productos.json      # Auto-generated intermediate file
└── scraper.log         # Auto-generated execution log
```

-----

## Libraries Used

|Library          |Purpose                                      |Content type|
|-----------------|---------------------------------------------|------------|
|`requests`       |Send HTTP requests to CoolMod                |Static HTML |
|`beautifulsoup4` |Parse HTML and extract data via CSS selectors|Static HTML |
|`psycopg2-binary`|Connect to PostgreSQL and execute queries    |Database    |


> Selenium was evaluated but not required — CoolMod’s product listings are fully rendered in static HTML without JavaScript interaction.

-----

## Scraped Categories

The scraper targets four product categories from CoolMod:

|Category |URL                                                     |
|---------|--------------------------------------------------------|
|Keyboards|`https://www.coolmod.com/perifericos-teclados/`         |
|Mice     |`https://www.coolmod.com/perifericos-ratones/`          |
|Monitors |`https://www.coolmod.com/perifericos-monitores/`        |
|Software |`https://www.coolmod.com/componentes-hardware-software/`|

-----

## Data Fields Extracted

For each product the scraper extracts:

|Field        |CSS Selector                                     |Notes                                          |
|-------------|-------------------------------------------------|-----------------------------------------------|
|`nombre`     |`p.card-title`                                   |Product name                                   |
|`precio`     |`span.product_price.int_price` + `span.dec_price`|Split across two spans — joined as float       |
|`url_imagen` |`figure img[src]`                                |Original CDN URL — no rehosting                |
|`descripcion`|—                                                |Reuses product name if no description available|
|`fuente`     |—                                                |Category URL hardcoded as source               |
|`categoria`  |—                                                |Category name hardcoded per scraping target    |

### Price parsing detail

CoolMod splits the price across two separate `<span>` elements:

```html
<span class="product_price int_price">82</span>
<span class="dec_price">95</span>
```

These are joined programmatically: `float("82.95")` → `82.95`

-----

## Ethical Scraping Compliance

The scraper implements two mandatory ethical controls:

**1. robots.txt check** — before making any request, the scraper reads `https://www.coolmod.com/robots.txt` using `urllib.robotparser`. If the target URL is disallowed, the scraper aborts immediately.

**2. Throttling** — a 2-second delay (`time.sleep(2)`) is applied between every page request and between categories, to avoid overloading the server.

-----

## Virtual Environment Setup

Executed on **VM-Web (10.109.99.11)**:

```bash
cd ~/proyecto-final-1daw/scraper/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Contents of `requirements.txt`:

```
requests==2.32.3
beautifulsoup4==4.12.3
psycopg2-binary==2.9.9
```

-----

## Phase 1 — Running the Scraper

```bash
cd ~/proyecto-final-1daw/scraper/
source venv/bin/activate
python3 scraper.py
```

Expected output:

```
2026-05-28 19:18:32 [INFO] robots.txt allows scraping: https://www.coolmod.com/perifericos-teclados/
2026-05-28 19:18:32 [INFO] === Starting category: Teclados ===
2026-05-28 19:18:32 [INFO] [Teclados] Scraping page 1 → https://www.coolmod.com/perifericos-teclados/
2026-05-28 19:18:34 [INFO] [Teclados] Products detected on page 1: 25
2026-05-28 19:18:34 [INFO] [OK] Keychron Q10 ISO-ES RGB...              82.95 EUR
...
2026-05-28 19:49:55 [INFO] === Scraping complete: 425 total products ===
2026-05-28 19:49:55 [INFO] Data saved to productos.json (425 records)
```

The output file `productos.json` contains an array of product objects:

```json
[
  {
    "nombre": "Keychron Q10 ISO-ES RGB Hot-Swappable Switch Gateron Mechanical G Pro Red",
    "descripcion": "Keychron Q10 ISO-ES RGB Hot-Swappable Switch Gateron Mechanical G Pro Red",
    "precio": 82.95,
    "url_imagen": "https://www.coolmod.com/images/product/normal/PROD-031641_1.jpg",
    "fuente": "https://www.coolmod.com/perifericos-teclados/",
    "categoria": "Teclados"
  },
  ...
]
```

-----

## Phase 2 — Loading JSON into PostgreSQL

```bash
python3 json_to_db.py
```

Expected output:

```
2026-05-28 [INFO] DB connection OK → 10.109.99.115:5432/Auralis_Tech
2026-05-28 [INFO] JSON loaded: 425 records from productos.json
2026-05-28 [INFO] [1/425] OK → Keychron Q10 ISO-ES...    82.95 €
...
2026-05-28 [INFO] ── Load complete: 425 upserted, 0 errors ──
```

### Duplicate control

The upsert strategy uses PostgreSQL’s `ON CONFLICT` clause on the `nombre` field:

```sql
INSERT INTO productos (nombre, descripcion, precio, url_imagen, fuente, categoria)
VALUES (...)
ON CONFLICT (nombre)
DO UPDATE SET
    precio     = EXCLUDED.precio,
    url_imagen = EXCLUDED.url_imagen;
```

This means running the pipeline again updates existing prices instead of inserting duplicates.

-----

## Troubleshooting

|Error                          |Cause                    |Fix                                                                                           |
|-------------------------------|-------------------------|----------------------------------------------------------------------------------------------|
|`ModuleNotFoundError: requests`|venv not activated       |Run `source venv/bin/activate`                                                                |
|`0 products collected`         |CSS selectors outdated   |Inspect live HTML with browser DevTools and update selectors in `_parsear_producto()`         |
|`DB connection FAILED`         |VM-BBDD unreachable      |Check PostgreSQL is running: `sudo systemctl status postgresql` on VM-BBDD                    |
|`ON CONFLICT error`            |UNIQUE constraint missing|Run `ALTER TABLE productos ADD CONSTRAINT productos_nombre_unique UNIQUE (nombre);` on VM-BBDD|