# Complete Hostinger Deployment Guide - Step by Step

**Server Details:**
- Domain: oncoesthetics.ca
- IP: 72.62.86.111
- Server: srv1211362.hstgr.cloud
- OS: Ubuntu 22.04 LTS

---

## STEP 1: Prepare Your Code on Windows

### 1.1 Generate Django Secret Key
```powershell
C:/Users/dts17/Documents/Oncoone/.venv/Scripts/python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
**Copy this key - you'll need it later!**

### 1.2 Push to GitHub
```powershell
cd C:\Users\dts17\Documents\Oncoone
git add .
git commit -m "Prepare for production deployment"
git push origin main
```

---

## STEP 2: Connect to Your Hostinger VPS

### 2.1 Get Your SSH Password
1. Login to **Hostinger Panel** (hpanel.hostinger.com)
2. Go to **VPS** → Click on your VPS
3. Click **Overview** → Find **Root Password** or reset it

### 2.2 Connect via SSH
Open PowerShell on Windows:
```powershell
ssh root@72.62.86.111
```
Enter your root password when prompted.

✅ **You're now connected to your server!**

---

## STEP 3: Update System and Install Software

### 3.1 Update System
```bash
apt update
apt upgrade -y
```

### 3.2 Install Python and Dependencies
```bash
apt install python3-pip python3-venv python3-dev nginx postgresql postgresql-contrib libpq-dev git -y
```

### 3.3 Verify Installations
```bash
python3 --version
nginx -v
psql --version
git --version
```

---

## STEP 4: Set Up PostgreSQL Database

### 4.1 Enter PostgreSQL
```bash
sudo -u postgres psql
```

### 4.2 Create Database and User
In the PostgreSQL prompt, type these commands **one by one**:
POSTGRES_DB=businessdb
POSTGRES_USER=businessusers
POSTGRES_PASSWORD=dts@1#2#3
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

```sql
CREATE DATABASE businessdb;
CREATE USER businessusers WITH PASSWORD 'dts@1#2#3';
ALTER ROLE businessusers SET client_encoding TO 'utf8';
ALTER ROLE businessusers SET default_transaction_isolation TO 'read committed';
ALTER ROLE businessusers SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE businessdb TO businessusers;
\q
```

**Remember the password you used!**

---

## STEP 5: Clone Your Project

### 5.1 Create Project Directory
```bash
mkdir -p /var/www/oncoone
cd /var/www/oncoone
```

### 5.2 Clone from GitHub
```bash
git clone https://github.com/MahinHameem/Oncoone.git .
```

### 5.3 Verify Files
```bash
ls -la
```
You should see manage.py, backend/, core/, etc.

---

## STEP 6: Set Up Python Environment

### 6.1 Create Virtual Environment
```bash
cd /var/www/oncoone
python3 -m venv venv
```

### 6.2 Activate Virtual Environment
```bash
source venv/bin/activate
```
Your prompt should now show `(venv)` at the beginning.

### 6.3 Install Python Packages
```bash
pip install --upgrade pip
pip install -r requirements-production.txt
```

---

## STEP 7: Configure Environment Variables

### 7.1 Create .env File
```bash
nano .env
```

### 7.2 Paste This Content (Edit the values!)
```env
# Django Settings
DJANGO_SECRET_KEY=ms0n14madan50ph7o=ym(w8ju-udc(be2#%+6x*tlklu$7yiit
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=oncoesthetics.ca,www.oncoesthetics.ca,72.62.86.111

# Database
POSTGRES_DB=businessdb
POSTGRES_USER=POSTGRES_USER=businessusers
POSTGRES_PASSWORD=dts@1#2#3
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Email (use your email settings)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.hostinger.com
EMAIL_PORT=587
EMAIL_HOST_USER=mahinham@gmail.com
EMAIL_HOST_PASSWORD=dxbjicmmdaxpcngf
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=mahinham@gmail.com
ADMIN_EMAIL=mahinham@gmail.com
```

**Press Ctrl+X, then Y, then Enter to save**

---

## STEP 8: Set Up Django

### 8.1 Collect Static Files
```bash
source venv/bin/activate
python manage.py collectstatic --noinput
```

### 8.2 Run Database Migrations
```bash
python manage.py migrate
```

### 8.3 Create Admin User
```bash
python manage.py createsuperuser
```
Enter:
- Username (e.g., admin)
- Email
- Password (twice)

---

## STEP 9: Configure Gunicorn (Application Server)

### 9.1 Test Gunicorn Works
```bash
source venv/bin/activate
gunicorn --bind 0.0.0.0:8000 backend.wsgi:application
```
Press **Ctrl+C** to stop after testing.

### 9.2 Create Systemd Service
```bash
nano /etc/systemd/system/oncoone.service
```

### 9.3 Paste This Content
```ini
[Unit]
Description=Oncoone Django Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/oncoone
Environment="PATH=/var/www/oncoone/venv/bin"
ExecStart=/var/www/oncoone/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/var/www/oncoone/oncoone.sock \
          backend.wsgi:application

[Install]
WantedBy=multi-user.target
```

**Press Ctrl+X, then Y, then Enter to save**

### 9.4 Start Gunicorn Service
```bash
systemctl daemon-reload
systemctl start oncoone
systemctl enable oncoone
systemctl status oncoone
```

Press **Q** to exit status view.

---

## STEP 10: Configure Nginx (Web Server)

### 10.1 Create Nginx Configuration
```bash
nano /etc/nginx/sites-available/oncoone
```

### 10.2 Paste This Content
```nginx
server {
    listen 80;
    server_name oncoesthetics.ca www.oncoesthetics.ca 72.62.86.111;

    client_max_body_size 10M;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }
    
    location /static/ {
        alias /var/www/oncoone/staticfiles/;
    }

    location /media/ {
        alias /var/www/oncoone/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/oncoone/oncoone.sock;
    }
}
```

**Press Ctrl+X, then Y, then Enter to save**

### 10.3 Enable the Site
```bash
ln -s /etc/nginx/sites-available/oncoone /etc/nginx/sites-enabled/
```

### 10.4 Test Nginx Configuration
```bash
nginx -t
```
Should say "syntax is ok" and "test is successful"

### 10.5 Restart Nginx
```bash
systemctl restart nginx
```

---

## STEP 11: Set File Permissions

```bash
chown -R www-data:www-data /var/www/oncoone
chmod -R 755 /var/www/oncoone
```

---

## STEP 12: Configure Domain DNS (In Hostinger Panel)

### 12.1 Point Domain to VPS
1. Go to **Hostinger Panel** → **Domains**
2. Select **oncoesthetics.ca**
3. Go to **DNS / Nameservers**
4. Add/Update these records:

**A Record:**
- Type: `A`
- Name: `@`
- Points to: `72.62.86.111`
- TTL: `14400`

**A Record (www):**
- Type: `A`
- Name: `www`
- Points to: `72.62.86.111`
- TTL: `14400`

### 12.2 Wait for DNS Propagation
DNS can take 5-30 minutes to propagate. Check at: https://dnschecker.org

---

## STEP 13: Install SSL Certificate (HTTPS)

### 13.1 Install Certbot
```bash
apt install certbot python3-certbot-nginx -y
```

### 13.2 Get SSL Certificate
```bash
certbot --nginx -d oncoesthetics.ca -d www.oncoesthetics.ca
```

Follow the prompts:
- Enter your email
- Agree to terms
- Choose redirect HTTP to HTTPS (option 2)

### 13.3 Test Auto-Renewal
```bash
certbot renew --dry-run
```

---

## STEP 14: Configure Firewall

### 14.1 Set Up UFW
```bash
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
```
Type `y` to confirm.

### 14.2 Check Firewall Status
```bash
ufw status
```

---

## STEP 15: Test Your Website!

### 15.1 Visit Your Site
Open browser and go to:
- **https://oncoesthetics.ca**
- **https://oncoesthetics.ca/admin/**

### 15.2 Login to Admin
Use the superuser credentials you created in Step 8.3

---

## USEFUL COMMANDS

### View Logs
```bash
# Gunicorn/Django logs
journalctl -u oncoone -f

# Nginx error logs
tail -f /var/log/nginx/error.log

# Nginx access logs
tail -f /var/log/nginx/access.log
```

### Restart Services
```bash
systemctl restart oncoone
systemctl restart nginx
```

### Update Your Code
```bash
cd /var/www/oncoone
git pull origin main
source venv/bin/activate
pip install -r requirements-production.txt
python manage.py migrate
python manage.py collectstatic --noinput
systemctl restart oncoone
```

### Check Service Status
```bash
systemctl status oncoone
systemctl status nginx
systemctl status postgresql
```

---

## TROUBLESHOOTING

### Site Not Loading?
```bash
# Check if Gunicorn is running
systemctl status oncoone

# Check if Nginx is running
systemctl status nginx

# Check socket file exists
ls -la /var/www/oncoone/oncoone.sock
```

### 502 Bad Gateway?
```bash
# Check Gunicorn logs
journalctl -u oncoone -n 50

# Restart Gunicorn
systemctl restart oncoone
```

### Permission Errors?
```bash
chown -R www-data:www-data /var/www/oncoone
chmod -R 755 /var/www/oncoone
```

### Database Connection Error?
```bash
# Check PostgreSQL is running
systemctl status postgresql

# Check .env file has correct credentials
cat /var/www/oncoone/.env
```

---

## SECURITY CHECKLIST

- ✅ DEBUG=False in .env
- ✅ Strong SECRET_KEY
- ✅ PostgreSQL with strong password
- ✅ Firewall enabled (UFW)
- ✅ SSL certificate installed
- ✅ Regular system updates (`apt update && apt upgrade`)
- ✅ Regular backups of database

### Backup Database
```bash
sudo -u postgres pg_dump oncoone_db > backup_$(date +%Y%m%d).sql
```

---

## SUPPORT

If you get stuck:
1. Check the logs (commands above)
2. Google the specific error message
3. Check Django/Nginx/Gunicorn documentation

**Your site should now be live at https://oncoesthetics.ca! 🎉**
