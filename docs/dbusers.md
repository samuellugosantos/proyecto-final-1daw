## Database User Provisioning & Connection Test

The PostgreSQL cluster instance was provisioned with a custom administrator role and a testing schema database instance to verify remote handshake capabilities.

### 1. Database Creation
Executed securely within the administrative `psql` shell on the **VM-BBDD** node:
```sql
CREATE USER isaac_admin WITH PASSWORD 'Isaac0905';
CREATE DATABASE prueba OWNER isaac_admin;
```

### 2. Remote Access Handshake Verification
To confirm that the web application layer can communicate with the data node, the terminal interface on **VM-Web** initiated a remote validation query:
```bash
# Executed via SSH on the Web Node
sudo apt update && sudo apt install postgresql-client -y
psql -h [DB_VM_IP] -U isaac_admin -d prueba
```

### 3. Connection Status Results
* **Database Target:** `prueba`
* **Authorized User:** `isaac_admin`
* **Outcome:** Connection accepted. The PostgreSQL service successfully authenticates network connections originating from the web server.

### Client Dependency Resolution
During the connection validation phase, the web node lacked the explicit binary environment for database queries. The utility was deployed cleanly via:
```bash
sudo apt update && sudo apt install postgresql-client -y
```

### Troubleshooting: Explicit Client Version Dependency Exception

The package manager triggered an environment exception: `Error: You must install at least one postgresql-client-<version> package`. This occurs because the meta-package layer requires a hardcoded structural version configuration.

#### Resolution Steps:
1. **Repository Index Query:** Ran `apt-cache search postgresql-client-` to discover version-controlled binary maps available within the OS mirrors.
2. **Explicit Dependency Injection:** Executed explicit targeting deployment (e.g., `sudo apt install -y postgresql-client-14` or newer) to supply the environment with the precise database communication toolchain.
3. **Status:** Core `psql` binary successfully mapped to the application shell layer.

### Troubleshooting: Connection Refused on Port 5432

The web node encountered a `psql: error: connection to server at "10.109.99.115", port 5432 failed: Connection refused` exception. This indicates that the remote database machine was reachable over the LAN layer, but the network sockets on port 5432 were rejecting packets.

#### Diagnostics & Remediation:
1. **Socket Inspection:** Executed `sudo ss -nltp | grep 5432` on the database node to check the active network bindings.
2. **Configuration Enforcement:** Confirmed that the `listen_addresses = '*'` parameters within `postgresql.conf` were parsed accurately.
3. **Process Refresh:** Issued `sudo systemctl restart postgresql` to force the daemon cluster engine to open port 5432 globally to incoming TCP/IP requests.

### Troubleshooting: Resolving pg_hba.conf Access Entry Exception

The web node successfully connected to port 5432 on the data node but triggered a `FATAL: no pg_hba.conf entry for host "10.109.99.11", user "isaac_admin", database "prueba"` exception. This security block confirms that PostgreSQL network routing is operative but requires an explicit Access Control List entry to authenticate the session.

#### Remediation Steps:
1. **ACL Policy Update:** Edited `/etc/postgresql/14/main/pg_hba.conf` on the database server.
2. **Rule Implementation:** Appended an explicit host configuration rule matching the production environment variables:
   ```conf
   host    prueba          isaac_admin     10.109.99.11/32         md5
   ```
3. **Daemon Reload:** Executed `sudo systemctl restart postgresql` to safely load the security rules into active memory.
4. **Status:** Secure remote handshake validated successfully.

## Milestone Achieved: Full Core Infrastructure Operational

The core architecture for the hardware and software catalog project is now fully deployed, secured, and validated across both Linux Mint nodes.

### Verification Matrix Summary:
*   **Encrypted Web Gateway:** Verified via secure remote browser handshakes over `https://10.109.99.11`, serving pages with encrypted SSL contexts.
*   **Remote Database Handshake:** Validated via isolated psql routing (`psql -h 10.109.99.115 -U isaac_admin -d prueba`), granting the application layer an exclusive communication highway to the data cluster.
*   **Operational Management:** Active administrative tunnels are fully operational over SSH channels.

- [x] Secure Multi-Node Infrastructure Baseline Completed.


# Database Management Suite & Production DB Setup

This document outlines the step-by-step process for deploying the graphical database administration client (pgAdmin4) and initializing the official production database cluster.
