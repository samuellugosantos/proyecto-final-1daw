# Auralis Tech - Functional Requirements Specification

## Module 1: Data Extraction & Web Scraping Subsystem (Scraper)

### RF-001: Automated Product Data Extraction
* **Description:** The system must automatically connect to the CoolMod website using `Requests` and `BeautifulSoup4` libraries to extract updated hardware and software catalog data.
* **Actor / Role:** System (Scraping Script).
* **Acceptance Criteria:** 
  * For each parsed item, the system must collect 5 mandatory attributes: Product Name, Category, Current Price, Original Price, and Availability.
  * The script must skip HTML elements that do not match a valid commercial product layout.
* **Priority:** High.

### RF-002: Data Structuring in Interchangeable Format
* **Description:** The extraction module must process raw HTML data and structure it into a compatible JSON interchange file.
* **Actor / Role:** System (JSON Module).
* **Acceptance Criteria:**
  * The generated file must validate without errors under the standard JSON specification.
  * JSON object keys must map exactly to the required fields (e.g., `{"product_name": "...", "category": "...", "current_price": ...}`).
* **Priority:** High.

---

## Module 2: Database Layer (PostgreSQL Server)

### RF-003: Persistent Catalog Storage
* **Description:** The PostgreSQL database server must receive the processed data from the scraper and persist it into relational tables while maintaining data integrity.
* **Actor / Role:** System (Database Engine).
* **Acceptance Criteria:**
  * The system must support bulk insertion of catalog records without breaking existing constraints.
  * It must perform an *upsert* operation (update price and availability if the product already exists).
* **Priority:** High.

### RF-004: Secure Remote Connection Management
* **Description:** The database must allow and process read/write requests coming exclusively from the verified IP address of the Web Server (`web-server`), rejecting all unauthorized connections.
* **Actor / Role:** System Administrator / Network Subsystem.
* **Acceptance Criteria:**
  * The database must respond successfully (0% packet loss) to queries sent from the internal bridged network (`Bridged / NAT Network`).
* **Priority:** High.

---

## Module 3: Web Server & Application Layer (Nginx)

### RF-005: Catalog Rendering on User Interface
* **Description:** The web application must read stored data from PostgreSQL and render it onto a graphical user interface for end-users to browse the Auralis Tech e-shop.
* **Actor / Role:** Client / Web Visitor.
* **Acceptance Criteria:**
  * The UI must clearly display the list of available hardware components and software licenses.
  * No directory indexing errors (`403 Forbidden`) shall be displayed when accessing the root domain.
* **Priority:** High.

### RF-006: Traffic Encryption via HTTPS
* **Description:** The Nginx web server must enforce secure connections using the HTTPS protocol with SSL/TLS certificates to protect browsing data and credentials.
* **Actor / Role:** System (Nginx Server).
* **Acceptance Criteria:**
  * Any incoming request on the HTTP port (80) must automatically redirect to the HTTPS port (443).
  * The server must successfully establish connections using the certificate path `/etc/ssl/nginx/nginx-selfsigned.crt`.
* **Priority:** High.