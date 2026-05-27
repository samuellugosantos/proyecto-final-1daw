## 1. pgAdmin4 Graphical Suite Installation (Desktop Mode)

To facilitate visual administration, database monitoring, and query executions, pgAdmin4 was successfully deployed in its native **Desktop Mode** directly inside the Database Virtual Machine environment.

### Installation Steps:
Executed via the package manager terminal on the **VM-BBDD** node:
```bash
# Import the official pgAdmin4 repository GPG key
curl -fsS https://pgadmin.org | sudo gpg --dearmor -o /usr/share/keyrings/packages-pgadmin-org.gpg

# Add the official apt repository configuration
sudo sh -c 'echo "deb [signed-by=/usr/share/keyrings/packages-pgadmin-org.gpg] https://postgresql.org pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list'

# Refresh package lists and install the desktop package
sudo apt update && sudo apt install pgadmin4-desktop -y
```

---

## 2. Multi-Administrator Role Provisioning

Before compiling the production database container, a secondary administrative role was established alongside `isaac_admin` to ensure infrastructure redundancy and multi-user administration capabilities.

### Cluster Execution via SSH Terminal:
```bash
# Access the PostgreSQL root interpreter
sudo -i -u postgres psql
```

```sql
-- Grant broad administration rights (Superuser and DB Creation capabilities)
ALTER ROLE isaac_admin WITH SUPERUSER CREATEDB;

-- Provision the secondary administrator account with full rights
CREATE USER [REPLACE_WITH_NEW_USER] WITH PASSWORD '[REPLACE_WITH_PASSWORD]';
ALTER ROLE [REPLACE_WITH_NEW_USER] WITH SUPERUSER CREATEDB;
\q
```

---

## 3. Global Access Policy Realignment

Since new administrators and a production environment were introduced, the network access rules were upgraded from a single-target setup to a broad multi-database structure, enabling secure connections from the trusted Web Server node.

### File Modifications on VM-BBDD:
1. Opened the Host-Based Authentication file: `sudo nano /etc/postgresql/14/main/pg_hba.conf`
2. Appended a broad cluster rule mapping incoming connections securely:
   ```conf
   # IPv4 Remote Connections: Allow all users to access all databases from Web Server
   host    all             all             10.109.99.11/32         md5
   ```
3. Applied the active network policies cleanly by running:
   ```bash
   sudo systemctl restart postgresql
   ```

---

## 4. Local Server Registration in pgAdmin4

Upon launching the fresh pgAdmin4 desktop interface for the first time, a master protection password was configured, and a new local loopback connection was registered to map the cluster engine.

### Connection Profile Settings:
* **Server Group Profile Name:** `Servidor-Local`
* **Host Interface Binding:** `127.0.0.1` (Localhost configuration)
* **Port Allocation:** `5432` (PostgreSQL interface)
* **Maintenance Target Database:** `postgres`
* **Authentication Identity:** User `isaac_admin` (Password securely stored in vault)

---

## 5. Troubleshooting & Production DB Initialization (Auralis Tech)

### The Issue:
During the initial graphical dashboard navigation, the context menu on the `Databases` folder tree restricted database generation to 'Refresh' only, indicating a temporary GUI role-parsing or rendering mismatch.

### The Resolution (Direct Engine Compilation):
To bypass the graphical client interface constraints, the official production database **Auralis Tech** was initialized manually using core terminal queries on the database host node:

```bash
# Execute direct DDL commands via terminal
sudo -i -u postgres psql
```

```sql
-- Compile the official enterprise catalog container and assign ownership
CREATE DATABASE "Auralis_Tech" OWNER isaac_admin;

-- Grant explicit global privileges to both active administrative roles
GRANT ALL PRIVILEGES ON DATABASE "Auralis_Tech" TO isaac_admin;
GRANT ALL PRIVILEGES ON DATABASE "Auralis_Tech" TO [REPLACE_WITH_NEW_USER];
\q
```

### Final Validation:
* **Action:** Executed the active `Refresh` option over the `Databases` folder node inside the pgAdmin4 GUI.
* **Result:** The `Auralis_Tech` cluster instance rendered immediately under the object navigation tree, completely active and ready for relational mapping.

---

## 6. Remote Application-Layer Verification

To confirm the entire operational chain functions successfully, a network query handshake was performed from the external application stack.

```bash
# Executed from VM-Web via SSH terminal
psql -h 10.109.99.115 -U isaac_admin -d Auralis_Tech
```
* **Status:** Connection **ACCEPTED** after successful credentials input.
* **Prompt Output:** `Auralis_Tech=>`
* **Conclusion:** The Web Server has seamless, exclusive administrative data access to the production node environment.
