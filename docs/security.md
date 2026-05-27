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


## Secure Server Configuration (HTTPS / SSL)

To protect traffic for the hardware and software catalog, a self-signed SSL/TLS certificate was generated and deployed onto the Nginx architecture.

### 1. SSL/TLS Generation
Created a dedicated directory and executed `openssl` to establish a 2048-bit RSA private key along with an X.509 certificate valid for one year:
```bash
sudo mkdir -p /etc/ssl/nginx
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/nginx/nginx-selfsigned.key -out /etc/ssl/nginx/nginx-selfsigned.crt
```
### 2. Nginx Server Block Update
Modified `/etc/nginx/sites-available/default` to listen on port `443 ssl` and linked the generated file pathways (`ssl_certificate` and `ssl_certificate_key`).

### 3. Service Reload
* Configuration syntax validated with `sudo nginx -t`.
* Nginx process refreshed via `sudo systemctl restart nginx`.

## Troubleshooting: Resolving Directory Index Forbidden

Log analysis from `/var/log/nginx/error.log` indicated specific `directory index of "/var/www/html/" is forbidden` errors. This confirmed that the network and SSL handshakes were successful, but Nginx lacked a valid target index file or sufficient file permissions to fulfill the request.

### Applied Solution:
1. **Target Initialization:** Forced a standardized static file generation by executing `echo "<h1>Catalog HTTPS Server Live</h1>" | sudo tee /var/www/html/index.html`.
2. **Permission Alignment:** Set specific permissions (`644`) and ownership (`www-data:www-data`) on the target file to grant Nginx explicit read rights.
3. **Verification:** Validated directory contents using `ls -la /var/www/html/` to confirm the accurate creation of the resource.

## Remote Management (SSH Setup)

By default, Linux Mint does not package an active SSH daemon wrapper. OpenSSH was manually compiled and activated on the web node to facilitate remote management.

### Installation Process:
1. **Package Deployment:** Installed the secure shell engine via `sudo apt install openssh-server -y`.
2. **Daemon Initialization:** Configured the environment to start the service natively on boot:
```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```
3. **Connectivity Verification:** Established a secure connection channel from the host machine using:
```bash
ssh admin-server@10.109.99.11
```
- [x] SSH server active on port 22. Remote console shell verification complete.

