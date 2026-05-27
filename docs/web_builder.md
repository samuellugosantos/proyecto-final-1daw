### Módulo 4 ### Web Generation Subsystem (Web Builder)

This section details the architecture, the design and the deployment of the software from the system dedicated to read the database to compile statically the visible catalog from the e-shop.

1. General vision of the Modular Web Builder
The purpose of the Web Builder is to establush a layer of preservation on this proyect. It's main purpose is to read the data on each product (Hardware) on the PostgreSQL engine to generate an index.html file that will be given by Nginx's server that's configured in the Virtual Machine for the Web-Server


| Component | Function | IP |
| :--- | :--- | :--- |
| **Aplication** | `web_builder_app.py` | Executed in the Web-Server Virtual Machine (IP: 10.109.99.11) |
| **Data Origin** | Database `Auralis_Tech` (producto table) | VM MINT-BBDD-CATALAGO (IP: 10.109.99.115, Puerto 5432) |
| **End-point** | Static HTML Catalog | `/var/www/html/index.html` (Nginx Root) |

2. Configuration and dependencies of the Virtual Enviroment
To maintain a robust structure of cleanliness, we use a Virtual Python Enviroment which will deal and fix the required dependencies, mostly `psycopg2-binary`. Every command was executed on the Web-Server Virtual Machine

2.1. Folder Structure
We will create a structure with the sole purpose to separate the logical responsability of the Web Builder:

```bash
cd ~/proyecto-auralis/
mkdir -p web_builder
cd web_builder
```

2.2. Virtual Enviroment (venv)
We create and activate this Virtual Enviroment to install the PostgreSQL library properly.

```bash
# Crear el Entorno Virtual
python3 -m venv entorno_web

# Activar el Entorno Virtual
source entorno_web/bin/activate

# Crear requirements.txt
echo "psycopg2-binary" > requirements.txt

# Instalar Dependencias
pip install -r requirements.txt
```

3. The body of the Application(web_builder_app.py)
This application contains all the connections to the PostgreSQL, the SELECT over the producto table and the generation of the products with the usage of basic HTML and CSS.


```python
import psycopg2
import os
import sys

DB_CONFIG = {
    'host': '10.109.99.115',
    'database': 'Auralis_Tech',
    'user': 'isaac_admin', 
    'password': '1234',
    'port': '5432'
}

NGINX_WEB_ROOT = '/var/www/html/index.html'

def fetch_products():
    conn = None
    products = []
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
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

def generate_html(products):
    if not products:
        return """
        <!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Auralis Tech - Catálogo</title>
        <style>body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }</style>
        </head><body><h1>Auralis Tech Catálogo</h1>
        <p>Aún no hay productos disponibles. Ejecute la aplicación de scraping.</p></body></html>
        """

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
    
    for nombre, descripcion, precio, url_imagen, categoria, fuente in products:
        descripcion = descripcion if descripcion else "Sin descripción disponible."
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

    html_content += """
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def write_html_to_nginx(html_content):
    try:
        with open(NGINX_WEB_ROOT, 'w') as f:
            f.write(html_content)
        print(f"Éxito: Catálogo HTML generado y escrito en {NGINX_WEB_ROOT}")
        return True
    except IOError as e:
        print(f"ERROR: No se pudo escribir el archivo. Revise los permisos. Error: {e}", file=sys.stderr)
        return False

def main():
    print("--- Auralis Tech Web Builder App Iniciada ---")
    products = fetch_products()
    if products is None:
        sys.exit(1)
    print(f"Productos recuperados de la BBDD: {len(products)}")
    html = generate_html(products)
    if write_html_to_nginx(html):
        print("Proceso completado. El catálogo está listo para ser servido por Nginx.")

if __name__ == "__main__":
    main()
```

4. Execution and Verification

4.1. Execution manual
To allow python to write on the `index.html` file in the Nginx directory (`/var/www/html/`), we will use `sudo` command to clear all the dependencies of the Enviroment.


```bash
# Navegar al directorio e iniciar ejecución del componente
cd ~/proyecto-auralis/web_builder
sudo ../entorno_web/bin/python3 web_builder_app.py
```

**Expected result:**
```text
--- Auralis Tech Web Builder App Iniciada ---
Database items: [Amount]
Passed: HTML catalog written in /var/www/html/
Completed process. Nginex is waiting
```

4.2. Verification of Deactivation

```bash
deactivate
```

* **Verification of Content in Nginex**: Access your web browser and input the IP address of the web server to validate the contents from the database. 
* **Access URL**: `https://10.109.99.11`

