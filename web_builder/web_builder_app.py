import psycopg2
import os
import sys
from typing import List, Tuple

# --- CONFIGURACIÓN DE LA BASE DE DATOS (DB Layer) ---

# Configuración de la conexión remota a la VM MINT-BBDD-CATALAGO (10.109.99.115)
DB_CONFIG = {
    'host': '10.109.99.115',  # IP del servidor PostgreSQL
    'database': 'Auralis_Tech', # Nombre de la base de datos de producción
    'user': 'samu_admin', # Usuario administrador provisto
    'password': '1234', 
    'port': '5432'
}

# Ruta donde Nginx sirve el archivo HTML
NGINX_WEB_ROOT = '/var/www/html/index.html'


def fetch_products() -> Optional[List[Tuple]]:
    """
    Se conecta a la BBDD, consulta todos los productos y devuelve la lista.
    Los campos recuperados coinciden con el schema de la tabla productos.
    """
    conn = None
    products = []
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Selecciona todos los campos necesarios para el renderizado del catálogo
        query = "SELECT nombre, descripcion, precio, url_imagen, categoria, fuente FROM productos ORDER BY categoria, nombre;"
        cur.execute(query)
        
        products = cur.fetchall()
        cur.close()
    except (Exception, psycopg2.Error) as error:
        print(f"Error al conectar o consultar la BBDD: {error}", file=sys.stderr)
        return None
    finally:
        if conn:
            conn.close()
    
    return products


def generate_html(products: List[Tuple]) -> str:
    """
    Genera el contenido HTML de la página web (RF-005).
    Se utiliza HTML semántico y un diseño limpio.
    """
    if not products:
        # Mensaje si la tabla está vacía
        return """
        <!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Auralis Tech - Catálogo</title>
        <style>body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }</style>
        </head><body><h1>Auralis Tech Catálogo</h1>
        <p>Aún no hay productos disponibles. Ejecute la aplicación de scraping primero.</p></body></html>
        """

    # --- Estructura HTML y CSS Básico para el Catálogo ---
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Auralis Tech - Catálogo de Componentes</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f4f7f6; color: #333; }
            .header { background-color: #007bff; color: white; padding: 20px 0; text-align: center; }
            .container { width: 90%; max-width: 1200px; margin: 40px auto; }
            .product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 30px; }
            .product-card { background-color: white; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); overflow: hidden; transition: transform 0.2s; }
            .product-card:hover { transform: translateY(-5px); }
            .product-image-container { height: 200px; overflow: hidden; }
            .product-card img { width: 100%; height: 100%; object-fit: cover; }
            .product-info { padding: 15px; }
            .product-info h3 { margin-top: 0; color: #007bff; font-size: 1.3em; }
            .category { color: #6c757d; font-size: 0.9em; margin-bottom: 5px; }
            .price { font-size: 1.5em; color: #dc3545; font-weight: bold; margin: 10px 0; }
            .description { font-size: 0.9em; color: #666; height: 40px; overflow: hidden; text-overflow: ellipsis; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Auralis Tech - Catálogo de Componentes</h1>
            <p>Su tienda de confianza para hardware y software.</p>
        </div>
        <div class="container">
            <div class="product-grid">
    """
    
    # Mapeo de índices de la tupla: 0:nombre, 1:descripcion, 2:precio, 3:url_imagen, 4:fuente, 5:categoria
    for product in products:
        nombre = product[0]
        descripcion = product[1] if product[1] else "Sin descripción disponible."
        # Formato de precio a dos decimales
        precio = product[2] if product[2] is not None else 0.00 
        url_imagen = product[3] if product[3] else 'http://placeholder.com/image.jpg'
        fuente = product[4]
        categoria = product[5]
        
        product_html = f"""
                <div class="product-card">
                    <div class="product-image-container">
                        <img src="{url_imagen}" alt="Imagen de {nombre}">
                    </div>
                    <div class="product-info">
                        <p class="category">Categoría: {categoria} (Fuente: {fuente})</p>
                        <h3>{nombre}</h3>
                        <p class="price">{precio:.2f} €</p>
                        <p class="description">{descripcion}</p>
                    </div>
                </div>
        """
        html_content += product_html

    # Cerrar la estructura HTML
    html_content += """
            </div>
        </div>
    </body>
    </html>
    """
    return html_content


def write_html_to_nginx(html_content: str) -> bool:
    """
    Escribe el contenido HTML generado en el directorio raíz de Nginx.
    """
    try:
        # Esto requiere permisos de escritura en /var/www/html/, por lo que debe
        # ejecutarse con 'sudo' fuera de este script.
        with open(NGINX_WEB_ROOT, 'w') as f:
            f.write(html_content)
        
        print(f"Éxito: Catálogo HTML generado y escrito en {NGINX_WEB_ROOT}")
        return True
    except IOError as e:
        print(f"ERROR: No se pudo escribir el archivo en {NGINX_WEB_ROOT}. Ejecute el script con 'sudo'. Error: {e}", file=sys.stderr)
        return False


def main():
    print("--- Auralis Tech Web Builder App Iniciada ---")
    
    products = fetch_products()
    
    if products is None:
        print("Fallo en la obtención de datos desde la BBDD. Abortando generación HTML.")
        sys.exit(1)

    print(f"Productos recuperados de la BBDD: {len(products)}")

    html = generate_html(products)
    
    if write_html_to_nginx(html):
        print("Proceso completado. El catálogo está listo para ser servido por Nginx.")

if __name__ == "__main__":
    main()
