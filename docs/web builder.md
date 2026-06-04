# Static Site Generator — Web Builder Module

This document describes the design, implementation and deployment of the static site generator for Auralis Tech. The web builder reads product data from PostgreSQL and produces static HTML files served directly by Nginx over HTTPS.

-----

## Overview

The web builder is **Phase 3** of the Auralis Tech pipeline. It connects to the PostgreSQL database on VM-BBDD, retrieves all products, and renders them into static HTML files using a template system. The generated files are written directly to Nginx’s serving directory.

```
PostgreSQL (VM-BBDD)
        │
        ▼  main.py
templates/index.html + templates/producto.html
        │
        ▼
/var/www/html/index.html
/var/www/html/teclados.html
/var/www/html/ratones.html
/var/www/html/monitores.html
/var/www/html/software.html
/var/www/html/styles.css
        │
        ▼
Nginx HTTPS → Browser
```

-----

## Directory Structure

```
web_builder/
├── main.py             # Static site generator — entry point
├── database.py         # DB query layer (SELECT from productos)
├── templates/
│   ├── index.html      # Main page template with category nav
│   └── producto.html   # Product card template
├── static/
│   └── styles.css      # Catalogue stylesheet
└── venv/               # Python virtual environment (not tracked in Git)
```

-----

## Component Responsibilities

|File                     |Responsibility                                                                                   |
|-------------------------|-------------------------------------------------------------------------------------------------|
|`main.py`                |Orchestrates the generation: reads DB, renders templates, writes HTML and CSS to `/var/www/html/`|
|`database.py`            |Single function `obtener_productos()` — connects to PostgreSQL and returns all products          |
|`templates/index.html`   |Page layout with header, category filter navigation, product grid and footer                     |
|`templates/producto.html`|Single product card template — uses `{field}` placeholders                                       |
|`static/styles.css`      |Dark-theme stylesheet with responsive grid and hover effects                                     |

-----

## Category Navigation

The site generates one HTML file per category plus `index.html` with all products:

|Button   |File generated  |Products shown  |
|---------|----------------|----------------|
|All      |`index.html`    |All 425 products|
|Keyboards|`teclados.html` |Teclados only   |
|Mice     |`ratones.html`  |Ratones only    |
|Monitors |`monitores.html`|Monitores only  |
|Software |`software.html` |Software only   |

Each page uses the same template and stylesheet. The active button is highlighted with a blue underline matching the card hover effect.

-----

## Virtual Environment Setup

Executed on **VM-Web (10.109.99.11)**:

```bash
cd ~/proyecto-final-1daw/web_builder/
python3 -m venv venv
source venv/bin/activate
pip install psycopg2-binary
```

-----

## File Permissions

Nginx serves from `/var/www/html/`. The system user needs write access:

```bash
sudo chown -R $USER:www-data /var/www/html/
sudo chmod -R 775 /var/www/html/
```

-----

## Running the Generator

```bash
cd ~/proyecto-final-1daw/web_builder/
source venv/bin/activate
python3 main.py
```

Expected output:

```
[INFO] 425 products retrieved from database.
[OK] index.html → 425 products
[OK] teclados.html → 125 products
[OK] ratones.html → 96 products
[OK] monitores.html → 109 products
[OK] software.html → 95 products
[OK] styles.css copied to /var/www/html/styles.css
```

-----

## Viewing the Catalogue

Open in the host browser:

```
https://10.109.99.11
```

The browser receives plain HTML and CSS — no server-side code runs at request time. This is the Static Site Generation (SSG) pattern.

-----

## Template System

### `templates/producto.html`

Each product is rendered by replacing `{field}` placeholders:

```html
<div class="card" data-categoria="{categoria}">
    <div class="card-img-wrap">
        <img src="{imagen}" alt="{nombre}" loading="lazy"
             onerror="this.parentElement.classList.add('no-img')">
    </div>
    <div class="card-body">
        <h2 class="card-name">{nombre}</h2>
        <p class="card-desc">{descripcion}</p>
        <span class="precio">{precio} €</span>
    </div>
</div>
```

### `templates/index.html`

The `{{ productos_html }}` placeholder is replaced with the concatenated product cards:

```html
<main class="productos" id="product-grid">
    {{ productos_html }}
</main>
```

-----

## Database Query

`database.py` retrieves products ordered by category and name:

```python
cursor.execute("""
    SELECT nombre, descripcion, precio, url_imagen, categoria
    FROM productos
    ORDER BY categoria, nombre
""")
```

-----

## Troubleshooting

|Error                                      |Cause                   |Fix                                                                                  |
|-------------------------------------------|------------------------|-------------------------------------------------------------------------------------|
|`PermissionError: /var/www/html/styles.css`|Nginx owns the directory|Run `sudo chown -R $USER:www-data /var/www/html/ && sudo chmod -R 775 /var/www/html/`|
|`ModuleNotFoundError: psycopg2`            |venv not activated      |Run `source venv/bin/activate`                                                       |
|`connection refused (127.0.0.1:5432)`      |DB host set to localhost|Check `database.py` — host must be `10.109.99.115`                                   |
|`0 products retrieved`                     |productos table is empty|Run the scraper pipeline first: `python3 scraper.py` then `python3 json_to_db.py`    |