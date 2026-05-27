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

### Steps Implemented:
1. **Machine Shutdown:** Issued `sudo poweroff` to allow modifications to the virtual network adapter hardware interface.
2. **Bridged Adapter Deployment:** Adjusted the hypervisor hardware configuration, changing the network adapter binding from the virtual isolated network to the physical host interface (Bridged Adapter).
3. **Gateway IP Acquisition:** Enabled the VM to query the local network DHCP server for a standard LAN IP address.

During diagnostic testing, the internal Linux Mint firewall (UFW) was verified to be inactive, ruling out any local software-level packet filtering.

## Web Server Verification

### Final Verification Results:
* **Host Browser Test:** Navigated to the newly assigned Bridged IP address from the physical host.
* **Outcome:** The default Nginx welcome page ("Welcome to nginx!") rendered successfully with no latency.
* **Network Status:** The web server layer is officially live and ready to route HTTP traffic.