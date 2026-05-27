## Multi-Administrator Role Provisioning

Before compiling the production database container, a secondary administrative role was established alongside `isaac_admin` to ensure infrastructure management redundancy and team collaboration capabilities.

### 1. Second Administrator Deployment
The new administrator account was provisioned securely via the cluster console on the **VM-BBDD** architecture using the following structure:
```sql
-- Access granted with full administrative rights (Superuser & DB Creation capabilities)
CREATE USER samu_admin WITH PASSWORD '1234';
ALTER ROLE samu_admin WITH SUPERUSER CREATEDB;
```

### 2. Global Access Policy Expansion
To ensure both administrators can manage the environment seamlessly from the application layer, the network access rules inside `/etc/postgresql/14/main/pg_hba.conf` were upgraded to accept any verified database user matching the secure Web Server host:
```conf
# IPv4 Remote Connections: Allow all authorized admin roles from the Web Server node
host    all             all             10.109.99.11/32         md5
```
* The configuration policies were safely parsed into active system memory executing `sudo systemctl restart postgresql`.

### 3. Production Database Ownership Alignment
* **Database Target:** `Auralis_Tech`
* **Privilege Matrix:** Both `isaac_admin` and `samu_admin` hold full `SUPERUSER` inheritance status, meaning either account can execute data definitions (DDL), modify tables, or perform structural maintenance remotely.
- [x] Administrative role redundancy successfully mapped for Isaac and Samuel.

### 1. Data Definition Language (DDL) Deployment Script
```sql
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    rol VARCHAR(30) NOT NULL DEFAULT 'usuario'
);

CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    precio NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    url_imagen VARCHAR(255),
    fuente VARCHAR(255),
    categoria VARCHAR(50) NOT NULL
);

CREATE TABLE pedido (
    id_usuario INT REFERENCES usuarios(id) ON DELETE CASCADE,
    id_productos INT REFERENCES productos(id) ON DELETE CASCADE,
    fecha_compra TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    PRIMARY KEY (id_usuario, id_productos)
);
```

## Unified Database Schema Blueprint (DDL Script)

The following production script compiles the entire storage infrastructure for **Auralis Tech**, integrating Role-Based Access Control (`rol`) within a clean, multi-user identity model.

## Optimized Relational Model & Unified Catalog Architecture

The database architecture for **Auralis Tech** has been refactored into a standardized N:M (Many-to-Many) transaction paradigm to allow users to generate orders containing multiple software licenses or hardware components.

### Architectural Improvements:
1. **Catalog Polymorphism:** Consolidated legacy `productos_hardware` and `productos_software` into a unified `productos` table. An explicit `categoria` column controls business logic segmentation.
2. **Transactional Normalization:** Introduced the associative table `pedido`. It maps historical logs using compound primary keys, ensuring strict relational reference constraints.

### Script Execution Execution Status
* **Platform:** pgAdmin4 SQL Query Editor Dashboard [INDEX: 1.1.5].
* **Integrity Constraints:** Primary keys (`PK`) and unique indicators (`UK`) are natively validated.
* **Seed Data:** Initial mock parameters were successfully appended to verify dynamic schema reads.
