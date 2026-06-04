"""
database_utils.py
=================
Data Access Layer — isolated from scraping logic.

Responsibilities:
    - Open and close PostgreSQL connections safely.
    - Execute parameterised upsert queries (no SQL injection risk).
    - Handle duplicate control via ON CONFLICT.
    - Manage transactions with explicit commit/rollback.

This module is imported by json_to_db.py. It never calls the scraper.

Connection target: VM-BBDD (10.109.99.115), database Auralis_Tech.
"""

import logging
import psycopg2

log = logging.getLogger(__name__)

# ─── Connection config ────────────────────────────────────────────────────────
# In a production environment these would come from environment variables.
DB_CONFIG = {
    "host":     "10.109.99.115",
    "port":     5432,
    "dbname":   "Auralis_Tech",
    "user":     "isaac_admin",
    "password": "Isaac0905",
}

# ─── SQL ──────────────────────────────────────────────────────────────────────
# ON CONFLICT (nombre): if a product with the same name already exists,
# update its price and image URL instead of inserting a duplicate.
# Requires the UNIQUE constraint on productos.nombre — see README.
_SQL_UPSERT = """
    INSERT INTO productos
        (nombre, descripcion, precio, url_imagen, fuente, categoria)
    VALUES
        (%(nombre)s, %(descripcion)s, %(precio)s,
         %(url_imagen)s, %(fuente)s, %(categoria)s)
    ON CONFLICT (nombre)
    DO UPDATE SET
        precio     = EXCLUDED.precio,
        url_imagen = EXCLUDED.url_imagen;
"""


# ─── Public interface ─────────────────────────────────────────────────────────

def insertar_o_actualizar_producto(datos: dict) -> None:
    """
    Insert a product row or update price/image if the name already exists.

    Args:
        datos: dict with keys nombre, descripcion, precio,
               url_imagen, fuente, categoria.

    Raises:
        psycopg2.DatabaseError: propagated after logging so the caller
        can decide whether to abort or continue with the next product.
    """
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn:                    # auto-commit on success, rollback on error
            with conn.cursor() as cur:
                cur.execute(_SQL_UPSERT, datos)
        log.debug("Upsert OK → %s", datos["nombre"])
    except psycopg2.DatabaseError as e:
        log.error("DB error on upsert [%s]: %s", datos.get("nombre"), e)
        raise
    finally:
        if conn and not conn.closed:
            conn.close()


def verificar_conexion() -> bool:
    """
    Quick connectivity check — useful to call before a bulk load.
    Returns True if the database is reachable, False otherwise.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.close()
        log.info("DB connection OK → %s:%s/%s",
                 DB_CONFIG["host"], DB_CONFIG["port"], DB_CONFIG["dbname"])
        return True
    except psycopg2.OperationalError as e:
        log.error("DB connection FAILED: %s", e)
        return False
