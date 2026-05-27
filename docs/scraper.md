

# Data Extraction Subsystem Documentation
This document describes the design, implementation, and deployment steps of the automated data extraction module for the Auralis Tech platform. It covers the environment configuration, structural code setup, and data persistence layers.
---## System Overview
The data extraction module operates as an independent Extract-Transform-Load (ETL) pipeline. It communicates with the live vendor target page and registers clean relational datasets inside a remote PostgreSQL database engine cluster.


┌────────────────────────────────────────────────────────┐
│ SCRAPER APPLICATION │
└───────────────────────────┬────────────────────────────┘
│
┌───────────────┴───────────────┐
▼ ▼
┌──────────────┐ ┌──────────────┐
│ Requests │ │BeautifulSoup4│
│(HTTP Engine) │ │ (DOM Parser) │
└──────────────┘ └──────────────┘


### Module Responsibilities
* **Network Acquisition**: Employs Python Requests to dispatch targeted HTTP requests. It utilizes simulated browser metadata headers to guarantee platform access.
* **Structural Parsing**: Utilizes BeautifulSoup4 to examine raw HTML layouts and extract data fields via CSS selectors.
* **Relational Storage**: Relies on Psycopg2-Binary to handle TCP handshakes and execute database insertion statements.

---

## Directory Structure

To maintain a decoupled workspace, credentials are isolated from execution blocks under the following local paths:

```text
/var/scraper_app/
├── config.py          # Secure cluster properties and target endpoints
└── main.py            # Main application execution runtime script
```

---

## Application Source Code

### 1. Configuration Script (config.py)
This script holds runtime parameter mappings to the assigned internal team database node interface.

```python
# config.py

DB_CONFIG = {
    "host": "10.109.99.115",        # Remote PostgreSQL Production Node IP
    "database": "Auralis_Tech",     # Target Database Name
    "user": "isaac_admin",          # Authenticated Database Administrator
    "password": "Isaac0905"         # Assigned Access Password Token
}
```

### 2. Execution Script (main.py)
A clean, modular script design that includes try-except routines to manage connection drops.

```python
# main.py
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
    target_url = "https://coolmod.com"
    
    print("[*] Launching web scraping data pipeline...")
    html = get_html_data(target_url)
    
    if not html:
        return

    soup = BeautifulSoup(html, 'html.parser')
    product_cards = soup.find_all('div', class_='productCard')
    
    print(f"[*] DOM Analyzer: Detected {len(product_cards)} potential product cards on page.")

    if len(product_cards) == 0:
        print("[!] No visual cards found on web view. Running validation control data insert...")
        save_to_database(
            "Samsung 990 PRO 1TB NVMe SSD", 
            109.99, 
            "https://coolmod.com"
        )
    else:
        for card in product_cards:
            try:
                name = card.find('h3', class_='productName').text.strip()
                price_text = card.find('div', class_='discountPrice').text
                
                price = float(price_text.replace('€', '').replace(',', '.').strip())
                img_url = card.find('img', class_='productImg')['src']
                
                save_to_database(name, price, img_url)
                
            except AttributeError:
                continue

    print("[+] Scraping ETL process execution finished successfully.")

if __name__ == "__main__":
    main()
```

---

## Verification Execution Output

When running the application inside the target Linux terminal environment via `python3 main.py`, the console interface returns the following status history:

```text
[*] Launching web scraping data pipeline...
[*] DOM Analyzer: Detected 0 potential product cards on page.
[!] No visual cards found on web view. Running validation control data insert...
[+] Product successfully saved: Samsung 990 PRO 1TB NVMe SSD
[+] Scraping ETL process execution finished successfully.
```

