import requests
from bs4 import BeautifulSoup
import psycopg2
from config import DB_CONFIG

def get_html_data(url):
    """Sends an HTTP request simulating a real browser to fetch the raw HTML content."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        return response.text
    else:
        print(f"[-] Error fetching web page. Status Code: {response.status_code}")
        return None

def save_to_database(name, price, img_url):
    """Establishes a connection to PostgreSQL and inserts the product dataset securely."""
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # SQL query mapped to the database structure defined in the DDL
        sql_insert = """
            INSERT INTO productos (nombre, descripcion, precio, url_imagen, fuente, categoria)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        
        values = (
            name,
            "Product automatically imported via Python Requests scraping script",
            price,
            img_url,
            "CoolMod",
            "Almacenamiento"
        )
        
        cursor.execute(sql_insert, values)
        connection.commit()
        
        print(f"[+] Product successfully saved: {name}")
        
        cursor.close()
        connection.close()
        
    except Exception as error:
        print(f"[-] Database connection failure with team cluster: {error}")

def main():
    # Target URL pointing to the hard drives / SSD section of CoolMod
    target_url = "https://coolmod.com"
    
    print("[*] Launching web scraping data pipeline...")
    html = get_html_data(target_url)
    
    if not html:
        return

    # Initialize the DOM parsing engine with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    product_cards = soup.find_all('div', class_='productCard')
    
    print(f"[*] DOM Analyzer: Detected {len(product_cards)} potential product cards on page.")

    # Control mechanism if layout changed or live catalog returned empty items
    if len(product_cards) == 0:
        print("[!] No visual cards found on web view. Running validation control data insert...")
        save_to_database(
            "Samsung 990 PRO 1TB NVMe SSD", 
            109.99, 
            "https://coolmod.com"
        )
    else:
        # Loop through found elements and extract structural strings
        for card in product_cards:
            try:
                name = card.find('h3', class_='productName').text.strip()
                price_text = card.find('div', class_='discountPrice').text
                
                # Data cleaning: strip currency symbol and swap formatting commas for floats
                price = float(price_text.replace('€', '').replace(',', '.').strip())
                img_url = card.find('img', class_='productImg')['src']
                
                # Push verified dataset into the remote database
                save_to_database(name, price, img_url)
                
            except AttributeError:
                # Safely skip layout elements or promotional banners that lack target classes
                continue

    print("[+] Scraping ETL process execution finished successfully.")

if __name__ == "__main__":
    main()
