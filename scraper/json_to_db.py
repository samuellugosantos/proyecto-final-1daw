"""
json_to_db.py
=============
Phase 2 of 2 — Load scraped data from JSON into PostgreSQL.

Responsibilities:
    - Read 'productos.json' produced by scraper.py.
    - Validate that each record has the required fields.
    - Call the data access layer (database_utils) to upsert each product.
    - Report a summary: inserted/updated vs. errors.

Does NOT perform any HTTP requests or HTML parsing.

Usage (inside the venv, on VM-Web):
    python3 json_to_db.py

Run AFTER scraper.py has produced productos.json.
"""

import json
import logging
from pathlib import Path

from database_utils import insertar_o_actualizar_producto, verificar_conexion


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("json_to_db.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

JSON_PATH     = Path(__file__).parent / "productos.json"
REQUIRED_KEYS = {"nombre", "precio", "categoria"}


def _validar(producto: dict, idx: int) -> bool:
    missing = REQUIRED_KEYS - producto.keys()
    if missing:
        log.warning("Record #%d skipped — missing fields: %s", idx, missing)
        return False
    if not str(producto["nombre"]).strip():
        log.warning("Record #%d skipped — empty nombre.", idx)
        return False
    return True


def cargar_json_en_bbdd() -> None:
    if not verificar_conexion():
        log.error("Aborting — cannot reach the database.")
        return

    if not JSON_PATH.exists():
        log.error("JSON file not found: %s — run scraper.py first.", JSON_PATH)
        return

    with open(JSON_PATH, encoding="utf-8") as f:
        productos = json.load(f)

    log.info("JSON loaded: %d records from %s", len(productos), JSON_PATH)

    ok = 0
    errores = 0

    for idx, producto in enumerate(productos, start=1):
        if not _validar(producto, idx):
            errores += 1
            continue
        try:
            insertar_o_actualizar_producto(producto)
            log.info("[%d/%d] OK → %-50s %.2f €",
                     idx, len(productos), producto["nombre"][:50], producto["precio"])
            ok += 1
        except Exception as e:
            log.warning("[%d/%d] FAILED → %s | Error: %s",
                        idx, len(productos), producto.get("nombre"), e)
            errores += 1

    log.info("── Load complete: %d upserted, %d errors ──", ok, errores)


if __name__ == "__main__":
    cargar_json_en_bbdd()
