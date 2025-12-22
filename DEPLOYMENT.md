# Deployment Guide for Hostinger VPS

## Server Information
- **Domain**: oncoesthetics.ca
- **Server IP**: 72.62.86.111
- **OS**: Ubuntu 22.04 LTS
- **Server**: srv1211362.hstgr.cloud

## Prerequisites on Server

### 1. Update System
```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install Required Software
```bash
# Install Python and dependencies
sudo apt install python3-pip python3-venv python3-dev nginx postgresql postgresql-contrib libpq-dev -y

# Install Git
sudo apt install git -y
```

### 3. Set Up PostgreSQL Database
```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL prompt, run:
CREATE DATABASE oncoone_db;
CREATE USER oncoone_user WITH PASSWORD 'your-strong-password';
ALTER ROLE oncoone_user SET client_encoding TO 'utf8';
ALTER ROLE oncoone_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE oncoone_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE oncoone_db TO oncoone_user;
\q
```

## Deployment Steps

### 1. Clone Your Repository
```bash
cd /var/www/
sudo mkdir oncoone
sudo chown $USER:$USER oncoone
cd oncoone
git clone https://github.com/MahinHameem/Oncoone.git .
```

### 2. Set Up Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-production.txt
```

### 3. Configure Environment Variables
```bash
# Copy and edit the .env file
cp .env.production .env
nano .env

# Generate a new secret key:
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
# Paste this into DJANGO_SECRET_KEY in .env
```

### 4. Run Django Setup
```bash
source venv/bin/activate
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py createsuperuser
```

### 5. Set Up Gunicorn (Application Server)

Create systemd service file:
```bash
sudo nano /etc/systemd/system/oncoone.service
```

Paste this content:
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

Start the service:
```bash
sudo systemctl start oncoone
sudo systemctl enable oncoone
sudo systemctl status oncoone
```

### 6. Configure Nginx (Web Server)

Create Nginx configuration:
```bash
sudo nano /etc/nginx/sites-available/oncoone
```

Paste this content:
```nginx
server {
    listen 80;
    server_name oncoesthetics.ca www.oncoesthetics.ca 72.62.86.111;

    client_max_body_size 10M;

    location = /favicon.ico { access_log off; log_not_found off; }
    
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

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/oncoone /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. Set Up SSL Certificate (HTTPS)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d oncoesthetics.ca -d www.oncoesthetics.ca
```

### 8. Set Correct Permissions
```bash
sudo chown -R www-data:www-data /var/www/oncoone
sudo chmod -R 755 /var/www/oncoone
```

## After Deployment

### Update Code
```bash
cd /var/www/oncoone
git pull origin main
source venv/bin/activate
pip install -r requirements-production.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart oncoone
```

### View Logs
```bash
# Gunicorn logs
sudo journalctl -u oncoone -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Restart Services
```bash
sudo systemctl restart oncoone
sudo systemctl restart nginx
```

## Security Checklist
- ✅ Set DEBUG=False in .env
- ✅ Use strong SECRET_KEY
- ✅ Set up PostgreSQL with strong password
- ✅ Configure firewall (UFW):
  ```bash
  sudo ufw allow OpenSSH
  sudo ufw allow 'Nginx Full'
  sudo ufw enable
  ```
- ✅ Set up SSL certificate
- ✅ Regular backups of database
- ✅ Keep system updated

## Access Points
- **Website**: https://oncoesthetics.ca
- **Admin Panel**: https://oncoesthetics.ca/admin/
- **SSH**: `ssh root@72.62.86.111`
