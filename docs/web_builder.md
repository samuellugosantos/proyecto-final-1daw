### Módulo 4 ### Web Generation Subsystem (Web Builder)

Esta sección detalla la arquitectura, el diseño y el despliegue del componente de software del sistema dedicado a realizar la lectura de la base de datos relacional y compilar estáticamente el catálogo web visible de la e-shop (Requerimiento Funcional RF-005).

1. Visión General del Módulo Web Builder
El propósito de la aplicación Web Builder es establecer la capa de presentación del proyecto. Su función principal es leer los datos persistidos de los productos (hardware y software) en el motor PostgreSQL y generar un archivo estático index.html que será servido por el servidor web Nginx configurado en la VM Web-Server-Catalago.



| Componente | Función | IP / Ruta de Conexión |
| :--- | :--- | :--- |
| **Aplicación** | `web_builder_app.py` | Ejecutada en VM Web-Server-Catalago (IP: 10.109.99.11) |
| **Origen de Datos** | Base de Datos `Auralis_Tech` (Tabla productos) | VM MINT-BBDD-CATALAGO (IP: 10.109.99.115, Puerto 5432) |
| **Destino** | Catálogo HTML estático | `/var/www/html/index.html` (Nginx Root) |

2. Configuración del Entorno Virtual y Dependencias
Para mantener una estructura de proyecto profesional y limpia, se utiliza un entorno virtual de Python (venv) que aísla las dependencias requeridas (principalmente `psycopg2-binary`). Todos los comandos se ejecutan en la VM Web-Server-Catalago (Linux Mint).

2.1. Estructura de Carpetas
Se asegura la separación lógica de responsabilidades creando la estructura necesaria para el Web Builder:

```bash
# Navegar a la carpeta raíz del proyecto y crear la estructura
cd ~/proyecto-auralis/
mkdir -p web_builder
cd web_builder
```

2.2. Entorno Virtual (venv)
Se crea y activa el entorno virtual para instalar `psycopg2-binary` de manera aislada.

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

3. Código de la Aplicación (web_builder_app.py)
Esta aplicación contiene la lógica de conexión al clúster PostgreSQL, la consulta SELECT sobre la tabla productos, y la generación de una cuadrícula de productos con HTML semántico y CSS básico.

3.1. Listado de Código
Crea el archivo `web_builder_app.py` y pega el siguiente código. Advertencia: Asegúrate de reemplazar `'TU_CONTRASENA_SEGURA'` con la contraseña del usuario administrador que corresponda (ej. `isaac_admin`).

```python
import psycopg2
import os
import sys

DB_CONFIG = {
    'host': '10.109.99.115',
    'database': 'Auralis_Tech',
    'user': 'isaac_admin', 
    'password': 'TU_CONTRASENA_SEGURA',
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

4. Ejecución del Despliegue y Verificación

4.1. Ejecución Reproducible
Para que la aplicación Python pueda escribir el archivo `index.html` en el directorio de Nginx (`/var/www/html/`), que generalmente pertenece a `root` y `www-data`, el script debe ejecutarse con privilegios de superusuario (`sudo`) garantizando que invoque de forma directa las dependencias del entorno virtual aislado.

```bash
# Navegar al directorio e iniciar ejecución del componente
cd ~/proyecto-auralis/web_builder
sudo ../entorno_web/bin/python3 web_builder_app.py
```

**Resultado Esperado en Consola:**
```text
--- Auralis Tech Web Builder App Iniciada ---
Productos recuperados de la BBDD: [Número de productos]
Éxito: Catálogo HTML generado y escrito en /var/www/html/index.html
Proceso completado. El catálogo está listo para ser servido por Nginx.
```

4.2. Verificación del Despliegue

```bash
# Desactivar el Entorno Virtual (opcional, al finalizar el despliegue local)
deactivate
```

* **Verificación del Contenido Servido por Nginx**: Acceda a un navegador web externo e introduzca la dirección del servidor web para validar que el contenido mapeado desde la base de datos se despliega de forma íntegra bajo la conexión SSL segura (HTTPS), tal como se estableció en el requisito de seguridad **RF-006**.
* **URL de Acceso**: `https://10.109.99.11`

