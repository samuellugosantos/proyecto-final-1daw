import requests
from bs4 import BeautifulSoup
import psycopg2
import sys
import re 
from typing import List, Tuple, Optional

# --- CONFIGURACIÓN GLOBAL (Basado en README.pdf) ---

# URL de la categoría que quieres scrapear (ejemplo: Tarjetas Gráficas)
COOLMOD_URL = 'https://www.coolmod.com/tarjetas-graficas' 

# Configuración de la conexión a la Base de Datos (VM-BBDD: 10.109.99.115)
DB_CONFIG = {
    'host': '10.109.99.115',  
    'database': 'Auralis_Tech', 
    'user': 'samu_admin', # O isaac_admin
    # !!! REEMPLAZA 'TU_CONTRASENA_SEGURA' CON LA CONTRASEÑA REAL.
    'password': 'TU_CONTRASENA_SEGURA', 
    'port': '5432'
}
FUENTE_PRODUCTO = 'CoolMod'
CATEGORIA_PRINCIPAL = 'Tarjeta Gráfica' 

def clean_price(price_str: str) -> float:
    """Limpia la cadena de precio para obtener un valor numérico (FLOAT)."""
    if not price_str:
        return 0.00
    # Eliminar símbolos de moneda (€) y reemplazar comas por puntos.
    clean_str = re.sub(r'[€$]', '', price_str).replace(',', '.')
    try:
        return float(clean_str)
    except ValueError:
        print(f"Advertencia: No se pudo convertir el precio '{price_str}' a float.")
        return 0.00

def scrape_coolmod(url: str) -> List[Tuple]:
    """
    Realiza la extracción de datos de CoolMod utilizando Requests y BeautifulSoup.
    Extrae los 5 atributos mandatorios (RF-001) y prepara los datos para la BBDD.
    """
    products_data = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"Iniciando scraping en: {url}")
        # Petición HTTP para obtener el HTML
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() # Lanza HTTPError para 4xx/5xx
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la página {url}: {e}", file=sys.stderr)
        return products_data

    # Parsing del contenido (BeautifulSoup4)
    soup = BeautifulSoup(response.content, 'html.parser')

    # !!! AQUÍ DEBES AJUSTAR LOS SELECTORES CSS PARA COOLMOD !!!
    # Buscar todos los contenedores de producto. Ejemplo:
    product_containers = soup.find_all('div', class_='product-list-item') 
    
    if not product_containers:
        print("ADVERTENCIA: No se encontraron contenedores de productos. Revisar selectores CSS.")
        return products_data

    for container in product_containers:
        try:
            # 1. Product Name (Nombre)
            name_element = container.find('a', class_='product-name-link')
            nombre = name_element.text.strip() if name_element else 'N/A'
            
            # 2. Category (Categoría) - Usamos la definida para la URL
            categoria = CATEGORIA_PRINCIPAL
            
            # 3. Current Price (Precio Actual)
            # Selector de precio actual (Ejemplo: .price-value)
            current_price_element = container.find('span', class_='price-value')
            precio_actual_str = current_price_element.text.strip() if current_price_element else '0.00 €'
            precio_actual = clean_price(precio_actual_str)

            # 4. Original Price (Precio Original) - Precio tachado si hay oferta (Ejemplo: .price-old)
            original_price_element = container.find('span', class_='price-old')
            # Si no hay precio original, usamos el actual.
            precio_original_str = original_price_element.text.strip() if original_price_element else precio_actual_str 
            # precio_original = clean_price(precio_original_str) # No se usa en la BBDD final, pero se extrae para RF-001

            # 5. Availability (Disponibilidad) - Selector específico (Ejemplo: .stock-status)
            availability_element = container.find('span', class_='stock-status')
            disponibilidad = availability_element.text.strip() if availability_element else 'N/A'
            
            # Campos adicionales para la BBDD: descripcion, url_imagen
            descripcion = container.find('p', class_='product-short-desc').text.strip() if container.find('p', class_='product-short-desc') else nombre

            img_element = container.find('img', class_='product-thumbnail')
            url_imagen = img_element.get('data-src') or img_element.get('src') if img_element else 'http://placeholder.com/image.jpg'
            
            # Se guardan los campos necesarios para la tabla 'productos'
            products_data.append((
                nombre, 
                descripcion, 
                precio_actual, 
                url_imagen, 
                FUENTE_PRODUCTO, 
                categoria
            ))

        except Exception as e:
            print(f"Error al procesar un producto (posible HTML mal formado): {e}", file=sys.stderr)
            continue
            
    print(f"Extracción finalizada. Productos encontrados: {len(products_data)}")
    return products_data

def persist_products(products: List[Tuple]):
    """
    Guarda los datos en la BBDD Auralis_Tech, implementando la lógica UPSERT (RF-003).
    """
    if not products:
        print("No hay productos para guardar en la BBDD.")
        return

    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Query de UPSERT (INSERT OR UPDATE) para garantizar RF-003
        # CONFLICT TARGET: Asumimos que el 'nombre' es el identificador único.
        upsert_query = """
        INSERT INTO productos (nombre, descripcion, precio, url_imagen, fuente, categoria)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (nombre) DO UPDATE
        SET 
            descripcion = EXCLUDED.descripcion,
            precio = EXCLUDED.precio,
            url_imagen = EXCLUDED.url_imagen,
            fuente = EXCLUDED.fuente,
            categoria = EXCLUDED.categoria;
        """
        
        # Ejecución en lote
        cur.executemany(upsert_query, products)
        
        # Confirmar la transacción
        conn.commit()
        print(f"Éxito: Se procesaron {cur.rowcount} registros (inserciones/actualizaciones) en la BBDD.")
        
        cur.close()
    except (Exception, psycopg2.Error) as error:
        print(f"Error fatal en la persistencia de datos (RF-003): {error}", file=sys.stderr)
        if conn:
            conn.rollback() 
    finally:
        if conn:
            conn.close()

def main():
    print("--- Auralis Tech Scraper App Iniciada ---")
    
    # 1. Extracción de datos (RF-001)
    scraped_products = scrape_coolmod(COOLMOD_URL)
    
    # 2. Persistencia en BBDD (RF-003)
    if scraped_products:
        persist_products(scraped_products)
        
    print("--- Proceso de Scraping Finalizado ---")

if __name__ == "__main__":
    main()
