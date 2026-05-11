# Auralis Tech

## Group Components
* **Isaac Fuentes Florez**
* **Samuel Lugo Santos**

---

## Project Overview
**Name of the shop:** Auralis Tech

### Project Rationale & Sourcing
For Auralis Tech, our core business focuses on the distribution of both hardware and software. After evaluating several industry-leading platforms, we established the following criteria for our product sourcing:

* **PCComponentes:** Although recognized for its extensive catalog of laptops and licenses, its massive inventory was deemed beyond the current scope of this project.

* **CoolMod (Primary Source):** Selected as our main target for web scraping. Its interface is clean and well-structured, providing a curated selection of products that perfectly fits our e-shop's requirements.

* **Newegg:** While a global standard for hardware, it was ultimately excluded to maintain a more manageable and focused product database.

---

## Security Implementation

This section outlines the protocols for ensuring data integrity and account security within the Auralis Tech infrastructure.

### 1. Secure Server Implementation (HTTPS)
To protect data in transit between the client and our Web Server, we implement the Hypertext Transfer Protocol Secure (HTTPS) using SSL/TLS encryption.

#### Certificate Acquisition
We utilize **Let's Encrypt** as our Certificate Authority (CA) due to its automated and open nature. The tool **Certbot** is employed for the retrieval and renewal of these certificates.

#### Deployment Steps
1. **Install Certbot:**
   ```bash
   sudo apt update
   sudo apt install certbot python3-certbot-nginx -y
   ```
2. **Configure Firewall:**
   Ensure that traffic is allowed through port 443.
   ```bash
   sudo ufw allow 'Nginx Full'
   sudo ufw delete allow 'Nginx HTTP'
   ```
3. **Generate Certificate:**
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

This configuration ensures that all traffic is automatically redirected from HTTP to HTTPS, providing an encrypted tunnel for user credentials and scraped product data.

---

## Scraping Web For Items

**Website we will be using for this proyect**: https://www.coolmod.com/

To execute the scraping process, we will first need a few python libraries.
1. **Requests:** To send HTTP requests and get the HTML contents from the website
2. **BeautifulSoup4:** To parse the HTML and navigate the document we receive from this using CSS selectors
3. **JSON:** To structure and gather all of the data into a consistent format

### Targetted Data Points

Based on the site, the piece of code we will create will focus primarily on the following attributes for each product:
1. **Product Name**
2. **Category**
3. **Current Price**
4. **Original Price**
5. **Availability**

The output file that comes from the python code we created will follow the usual JSON format for compatibility.

## Virtual Machine Creation

### Virtual Machine 1: Database Server (PostgreSQL)
This section details the setup and configuration of the first node, dedicated to hosting the PostgreSQL database.

#### 1. Virtual Hardware Specifications
* **Operating System:** Linux Mint (Cinnamon/XFCE)
* **Virtualization Platform:** VirtualBox / VMware
* **RAM:** 12069 MB
* **Storage:** 25 GB VDI (Dynamically allocated)
* **Network Adapter:** NAT Network / Bridged (Subject to IP assignment)

#### 2. Operating System Installation
Installed using the official Linux Mint ISO:
* **Installation Mode:** Full disk installation (Erase disk and install).
* **System User:** admin-server
* **Password:** 1234
* **Privileges:** admin-server added to the sudo group.

#### 3. Initial System Preparation
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install net-tools -y
```

#### 4. Database Engine Installation (PostgreSQL)
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Verify Service Status
sudo systemctl status postgresql
```

#### 5. Current Progress
- [x] VM Created with specified hardware.
- [x] Linux Mint OS installed successfully.
- [x] User admin-server configured.
- [x] PostgreSQL service is active and running.

---

### Virtual Machine 2: Web Server

#### 1. Virtual Hardware Specifications
* **Operating System:** Linux Mint (Cinnamon/XFCE)
* **Virtualization Platform:** VirtualBox / VMware
* **RAM:** 13306 MB
* **Storage:** 25 GB VDI (Dynamically allocated)
* **Network Adapter:** NAT Network (Matches Database VM for connectivity)

#### 2. Operating System Installation
Consistency maintained with the first node:
* **Installation Mode:** Full disk installation.
* **System User:** admin-server
* **Password:** 1234
* **Hostname:** web-server
* **Privileges:** Full sudo access.

#### 3. Initial System Preparation
```bash
# Update and upgrade system packages
sudo apt update && sudo apt upgrade -y

# Install network discovery tools
sudo apt install net-tools -y
```
## Network Infrastructure Setup

Initially, VMs were using default NAT mode, causing IP conflicts. A dedicated virtual network was created to allow inter-VM communication.

### Steps Taken:
1. **Created NAT Network:** Established a global "NatNetwork" in VirtualBox settings with DHCP enabled.
2. **Adapter Configuration:** Switched both VMs' network adapters from "NAT" to "NAT Network".
3. **MAC Unification:** Regenerated the MAC address for the Web Server VM to ensure the DHCP server assigns a unique IP.
4. **Verification:** Confirmed unique IP assignment via `hostname -I`.


## Connectivity Confirmed

The "Destination Host Unreachable" issue was resolved by ensuring both virtual machines were correctly bridged to the same NAT Network.

### Final Verification:
* **Source VM (Web):** Successfully reached the Database VM.
* **Network Status:** 0% packet loss.
* **Environment:** Ready for secure service deployment (HTTPS and PostgreSQL remote access).

## Project Architecture
![Estructura del Host](images/Estructura_del_host.png)
