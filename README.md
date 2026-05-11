# Auralis Tech

# Group components

1. Isaac Fuentes Florez
2. Samuel Lugo Santos

## Name of the shop

### Auralis Tech

## Reasoning for options

In this shop, we have decided to primarily sell hardware and software alike, we have found the following online stores to get our products from:

1. PCComponentes

Mostly for it's vast inventory and loads of different items like laptops and software licenses, although it truly is a lot. Almost a little excessive for our proyect.

2. CoolMod

For us, this is the one we are gonna choose to scrape for products, it's a clean and concise website with just enough products and variation to fill an e-shop with.

3. Newegg

We had this one into consideration as well because it's your standard hardware shop, although we did not choose it because there is way too many items for what we had in mind.

# Virtual Machine Creation

---------------------------

## Virtual Machine 1: Database Server (PostgreSQL)

This document details the setup and configuration of the first node in our infrastructure, dedicated to hosting the PostgreSQL database.

### 1. Virtual Hardware Specifications
*   **Operating System:** Linux Mint (Cinnamon/XFCE)
*   **Virtualization Platform:** VirtualBox / VMware
*   **RAM:** 12069 MB 
*   **Storage:** 25 GB VDI (Dynamically allocated)
*   **Network Adapter:** NAT Network / Bridged (to be confirmed by IP assignment)

### 2. Operating System Installation
The installation was performed using the official Linux Mint ISO.
*   **Installation Mode:** Full disk installation (Erase disk and install).
*   **System User:**
    *   **Username:** `admin-server`
    *   **Password:** `1234`
*   **Privileges:** The user `admin-server` has been added to the `sudo` group for administrative tasks.

### 3. Initial System Preparation
Once the OS was installed, the system was updated and basic networking tools were added:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install net-tools -y
```

### 4. Database Engine Installation (PostgreSQL)
We installed the PostgreSQL server and its additional utilities:
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Verify Service Status
sudo systemctl status postgresql
```

### 5. Current Progress
- [x] VM Created with specified hardware.
- [x] Linux Mint OS installed successfully.
- [x] User `admin-server` configured.
- [x] PostgreSQL service is active and running.

## Virtual Machine 2: Web Server

### 1. Virtual Hardware Specifications
*   **Operating System:** Linux Mint (Cinnamon/XFCE)
*   **Virtualization Platform:** VirtualBox / VMware
*   **RAM:** 13306 MB 
*   **Storage:** 25 GB VDI (Dynamically allocated)
*   **Network Adapter:** NAT Network (Must match the Database VM for connectivity)

### 2. Operating System Installation
The installation followed the same procedure as the first node to ensure environment consistency.
*   **Installation Mode:** Full disk installation.
*   **System User:**
    *   **Username:** `admin-server`
    *   **Password:** `1234`
*   **Hostname:** `web-server` (or as assigned during setup)
*   **Privileges:** The user `admin-server` has full `sudo` access.

### 3. Initial System Preparation
After the first boot, the system repositories were updated to the latest versions:
```bash
# Update and upgrade system packages
sudo apt update && sudo apt upgrade -y

# Install network discovery tools
sudo apt install net-tools -y
```

### 4. Current Progress
- [x] VM Created with matching network configuration.
- [x] Linux Mint OS installed and functional.
- [x] User `admin-server` configured with administrative rights.
- [x] System environment updated and ready for Web Server (Apache/Nginx) installation.
