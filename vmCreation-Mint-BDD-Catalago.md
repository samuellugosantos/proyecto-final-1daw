# Project: Hardware & Software Catalog - Infrastructure Documentation

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
