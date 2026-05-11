# Project: Hardware & Software Catalog - Infrastructure Documentation

## Virtual Machine 2: Web Server

This document details the setup and configuration of the second node in our infrastructure, which will host the web application/catalog.

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
