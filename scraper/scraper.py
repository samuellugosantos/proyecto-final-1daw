"""
scraper.py
==========
Phase 1 of 2 — Data extraction from CoolMod.

Responsibilities:
    - Check robots.txt before scraping.
    - Fetch product listings from multiple CoolMod categories.
    - Parse each product: name, description, price, image URL, source, category.
    - Apply throttling (time.sleep) between requests to be a polite scraper.
    - Save all collected products to 'productos.json' as an intermediate file.

Does NOT touch the database. That is handled by json_to_db.py (Phase 2).

Selectors verified against live CoolMod HTML on 2026-05-28.

Usage (inside the venv, on VM-Web):
    python3 scraper.py
"""

import json
import time
import logging
from pathlib import Path
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup


# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("scraper.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


# ─── Configuración ────────────────────────────────────────────────────────────
ROBOTS_URL  = "https://www.coolmod.com/robots.txt"
MAX_PAGINAS = 5
DELAY_SEG   = 2
OUTPUT_JSON = Path(__file__).parent / "productos.json"

# Categories to scrape: (display name, URL)
CATEGORIAS = [
    ("Teclados",   "https://www.coolmod.com/perifericos-teclados/"),
    ("Ratones",    "https://www.coolmod.com/perifericos-ratones/"),
    ("Monitores",  "https://www.coolmod.com/perifericos-monitores/"),
    ("Software",   "https://www.coolmod.com/componentes-hardware-software/"),
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


# ─── robots.txt check ─────────────────────────────────────────────────────────

def _check_robots(url: str) -> bool:
    """
    Returns True if scraping the given URL is allowed by robots.txt.
    Defaults to True with a warning if robots.txt cannot be fetched.
    """
    try:
        rp = RobotFileParser()
        rp.set_url(ROBOTS_URL)
        rp.read()
        allowed = rp.can_fetch("*", url)
        if not allowed:
            log.warning("robots.txt DISALLOWS scraping: %s", url)
        else:
            log.info("robots.txt allows scraping: %s", url)
        return allowed
    except Exception as e:
        log.warning("Could not read robots.txt (%s) — proceeding with caution.", e)
        return True


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _limpiar_precio(entero: str, decimales: str) -> float | None:
    """
    Reconstruct price from the two separate spans CoolMod uses.
        <span class="product_price int_price">82</span>
        <span class="dec_price">95</span>
    Joins them into a proper float: 82.95
    """
    try:
        return float(f"{entero.strip()}.{decimales.strip()}")
    except (ValueError, AttributeError):
        return None


def _parsear_producto(item, categoria: str, base_url: str) -> dict | None:
    """
    Extract product fields from a CoolMod <article> tag.
    Returns None if the element does not match the expected product layout.

    Selectors verified against live CoolMod HTML on 2026-05-28:
        name  -> p.card-title
        price -> span.product_price.int_price + span.dec_price
        image -> figure img[src]
    """
    # Name
    nombre_tag = item.select_one("p.card-title")
    if not nombre_tag:
        return None
    nombre = nombre_tag.get_text(strip=True)
    if not nombre:
        return None

    # Price
    entero_tag    = item.select_one("span.product_price.int_price")
    decimales_tag = item.select_one("span.dec_price")
    if not entero_tag or not decimales_tag:
        return None
    precio = _limpiar_precio(entero_tag.get_text(), decimales_tag.get_text())
    if precio is None:
        return None

    # Image
    img_tag    = item.select_one("figure img")
    url_imagen = img_tag.get("src") if img_tag else None

    # Description
    descripcion = nombre

    return {
        "nombre":      nombre,
        "descripcion": descripcion,
        "precio":      precio,
        "url_imagen":  url_imagen,
        "fuente":      base_url,
        "categoria":   categoria,
    }


# ─── Scraper por categoría ────────────────────────────────────────────────────

def scrape_categoria(categoria: str, base_url: str, session: requests.Session) -> list[dict]:
    """
    Scrape all pages of a single CoolMod category.
    Returns a list of product dicts for that category.
    """
    productos = []
    errores   = 0

    for pagina in range(1, MAX_PAGINAS + 1):
        url = base_url if pagina == 1 else f"{base_url}?page={pagina}"
        log.info("[%s] Scraping page %d -> %s", categoria, pagina, url)

        try:
            response = session.get(url, timeout=15)
            response.raise_for_status()
        except requests.RequestException as e:
            log.error("[%s] Failed to fetch page %d: %s", categoria, pagina, e)
            break

        soup  = BeautifulSoup(response.text, "html.parser")
        items = soup.select("article")

        if not items:
            log.info("[%s] No products on page %d — end of pagination.", categoria, pagina)
            break

        log.info("[%s] Products detected on page %d: %d", categoria, pagina, len(items))

        for item in items:
            try:
                datos = _parsear_producto(item, categoria, base_url)
                if datos is None:
                    log.debug("[%s] Element skipped (unrecognised layout).", categoria)
                    continue
                productos.append(datos)
                log.info("[OK] %-50s %.2f EUR", datos["nombre"][:50], datos["precio"])
            except Exception as e:
                log.warning("[%s] Error parsing product: %s", categoria, e)
                errores += 1

        if pagina < MAX_PAGINAS:
            log.info("Waiting %ds before next page (throttling)...", DELAY_SEG)
            time.sleep(DELAY_SEG)

    log.info("[%s] Done: %d products, %d errors.", categoria, len(productos), errores)
    return productos


# ─── Main scraper ─────────────────────────────────────────────────────────────

def scrape_coolmod() -> list[dict]:
    """
    Scrape all configured CoolMod categories.
    Returns a combined list of product dicts.
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    todos = []

    for categoria, base_url in CATEGORIAS:
        if not _check_robots(base_url):
            log.warning("Skipping %s — disallowed by robots.txt.", categoria)
            continue

        log.info("=== Starting category: %s ===", categoria)
        productos = scrape_categoria(categoria, base_url, session)
        todos.extend(productos)

        log.info("Waiting %ds before next category...", DELAY_SEG)
        time.sleep(DELAY_SEG)

    log.info("=== Scraping complete: %d total products ===", len(todos))
    return todos


def guardar_json(productos: list[dict]) -> None:
    """Serialize the product list to productos.json."""
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(productos, f, ensure_ascii=False, indent=2)
    log.info("Data saved to %s (%d records)", OUTPUT_JSON, len(productos))


# ─── Entry point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    productos = scrape_coolmod()
    if productos:
        guardar_json(productos)
    else:
        log.warning("No products were collected — JSON file not written.")
