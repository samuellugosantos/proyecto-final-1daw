"""
main.py
=======
Static Site Generator — Phase 3 of the Auralis Tech pipeline.

Generates one HTML file per category plus index.html with all products.
All files are written directly to /var/www/html/ for Nginx to serve.

Usage (inside the venv, on VM-Web):
    python3 main.py
"""

from database import obtener_productos

# ─── Config ───────────────────────────────────────────────────────────────────
OUTPUT_DIR       = "/var/www/html/"
CSS_OUTPUT       = OUTPUT_DIR + "styles.css"
TEMPLATE_INDEX   = "templates/index.html"
TEMPLATE_PRODUCT = "templates/producto.html"
STATIC_CSS       = "static/styles.css"

# Maps categoria value in DB → output filename
PAGINAS = {
    "all":       "index.html",
    "Teclados":  "teclados.html",
    "Ratones":   "ratones.html",
    "Monitores": "monitores.html",
    "Software":  "software.html",
}


def generar_web():
    # 1. Fetch all products from PostgreSQL
    productos = obtener_productos()
    print(f"[INFO] {len(productos)} products retrieved from database.")

    # 2. Load templates
    with open(TEMPLATE_PRODUCT, encoding="utf-8") as f:
        template_producto = f.read()
    with open(TEMPLATE_INDEX, encoding="utf-8") as f:
        template_index = f.read()

    # 3. Group products by category
    por_categoria = {"all": productos}
    for producto in productos:
        _, _, _, _, categoria = producto
        if categoria not in por_categoria:
            por_categoria[categoria] = []
        por_categoria[categoria].append(producto)

    # 4. Generate one HTML per category + index
    for clave, filename in PAGINAS.items():
        lista = por_categoria.get(clave, [])

        tarjetas = ""
        for producto in lista:
            nombre, descripcion, precio, imagen, categoria = producto
            tarjeta = template_producto.format(
                nombre=nombre,
                descripcion=descripcion or nombre,
                precio=precio,
                imagen=imagen or "",
                categoria=categoria
            )
            tarjetas += tarjeta

        html_final = template_index.replace("{{ productos_html }}", tarjetas)

        output_path = OUTPUT_DIR + filename
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_final)
        print(f"[OK] {filename} → {len(lista)} products")

    # 5. Copy CSS
    with open(STATIC_CSS, encoding="utf-8") as f:
        css = f.read()
    with open(CSS_OUTPUT, "w", encoding="utf-8") as f:
        f.write(css)
    print(f"[OK] styles.css copied to {CSS_OUTPUT}")


if __name__ == "__main__":
    generar_web()
