"""
database.py
===========
Database query layer for the static site generator.

Connects to PostgreSQL on VM-BBDD and retrieves all products
to be rendered into the HTML catalogue.
"""

import psycopg2


def obtener_productos() -> list[tuple]:
    """
    Fetch all products from the productos table.
    Returns a list of tuples: (nombre, descripcion, precio, url_imagen).
    """
    conn = psycopg2.connect(
        host="10.109.99.115",
        port=5432,
        database="Auralis_Tech",
        user="isaac_admin",
        password="Isaac0905"
    )

    cursor = conn.cursor()
    cursor.execute("""
        SELECT nombre, descripcion, precio, url_imagen, categoria
        FROM productos
        ORDER BY categoria, nombre
    """)

    productos = cursor.fetchall()
    cursor.close()
    conn.close()

    return productos
