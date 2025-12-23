# Deployment Guide - Student Information System

## Prerequisites

### System Requirements
- Ubuntu 20.04 LTS or higher
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Nginx 1.24+
- 4GB RAM minimum (8GB recommended)
- 50GB disk space

### Required Software
```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y redis-server
sudo apt install -y nginx
sudo apt install -y git
```

## Step 1: Database Setup

### PostgreSQL Installation & Configuration
```bash
# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql <<EOF
CREATE DATABASE sis_db;
CREATE USER sis_user WITH PASSWORD 'your_secure_password';
ALTER ROLE sis_user SET client_encoding TO 'utf8';
ALTER ROLE sis_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE sis_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE sis_db TO sis_user;
\q
EOF
```

### Redis Configuration
```bash
# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis
redis-cli ping  # Should return PONG
```

## Step 2: Application Setup

### Clone Repository
```bash
cd /var/www
sudo git clone https://github.com/yourorg/sis-backend.git
cd sis-backend
sudo chown -R $USER:$USER /var/www/sis-backend
```

### Create Virtual Environment
```bash
python3.11 -m venv venv
source venv/bin/activate
```

### Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Environment Configuration
```bash
# Create .env file
cat > .env <<EOF
# Django Settings
SECRET_KEY='your-secret-key-here-generate-new-one'
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DB_NAME=sis_db
DB_USER=sis_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=604800

# Email (Gmail Example)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@your-domain.com

# URLs
SITE_URL=https://your-domain.com
FRONTEND_URL=https://app.your-domain.com

# CORS
CORS_ALLOWED_ORIGINS=https://app.your-domain.com

# Security
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
EOF
```

### Database Migration
```bash
# Create logs directory
mkdir -p logs

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

## Step 3: Gunicorn Setup

### Create Gunicorn Configuration
```bash
sudo nano /etc/systemd/system/sis-gunicorn.service
```

Add the following content:
```ini
[Unit]
Description=Academia Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/sis-backend
Environment="PATH=/var/www/sis-backend/venv/bin"
ExecStart=/var/www/sis-backend/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/var/www/sis-backend/sis.sock \
    --timeout 120 \
    --access-logfile /var/www/sis-backend/logs/gunicorn-access.log \
    --error-logfile /var/www/sis-backend/logs/gunicorn-error.log \
    sis_backend.wsgi:application

[Install]
WantedBy=multi-user.target
```

### Start Gunicorn
```bash
sudo systemctl start sis-gunicorn
sudo systemctl enable sis-gunicorn
sudo systemctl status sis-gunicorn
```

## Step 4: Nginx Configuration

### Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/sis
```

Add the following:
```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=sis_limit:10m rate=10r/s;

upstream sis_backend {
    server unix:/var/www/sis-backend/sis.sock fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL Configuration (Use certbot for Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Client body size (for file uploads)
    client_max_body_size 10M;
    
    # Rate limiting
    limit_req zone=sis_limit burst=20 nodelay;
    
    # Static files
    location /static/ {
        alias /var/www/sis-backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /var/www/sis-backend/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    # API endpoints
    location / {
        proxy_pass http://sis_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

### Enable Site and Restart Nginx
```bash
sudo ln -s /etc/nginx/sites-available/sis /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 5: SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

## Step 6: Celery Setup (Optional - For Background Tasks)

### Create Celery Service
```bash
sudo nano /etc/systemd/system/sis-celery.service
```

```ini
[Unit]
Description=Academia Celery Worker
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/sis-backend
Environment="PATH=/var/www/sis-backend/venv/bin"
ExecStart=/var/www/sis-backend/venv/bin/celery -A sis_backend worker --loglevel=info

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start sis-celery
sudo systemctl enable sis-celery
```

## Step 7: Security Hardening

### Firewall Configuration
```bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### File Permissions
```bash
sudo chown -R www-data:www-data /var/www/sis-backend
sudo chmod -R 755 /var/www/sis-backend
sudo chmod 600 /var/www/sis-backend/.env
```

## Step 8: Monitoring & Logging

### Log Rotation
```bash
sudo nano /etc/logrotate.d/sis
```

```
/var/www/sis-backend/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload sis-gunicorn
    endscript
}
```

### System Monitoring
```bash
# Install monitoring tools
sudo apt install -y htop

# Monitor logs
sudo tail -f /var/www/sis-backend/logs/django.log
sudo tail -f /var/www/sis-backend/logs/gunicorn-error.log
```

## Step 9: Backup Strategy

### Database Backup Script
```bash
sudo nano /usr/local/bin/sis-backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/sis"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U sis_user sis_db > $BACKUP_DIR/db_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/sis-backend/media/

# Remove backups older than 30 days
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

```bash
sudo chmod +x /usr/local/bin/sis-backup.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/sis-backup.sh
```

## Step 10: Deployment Checklist

- [ ] Database created and migrated
- [ ] Environment variables configured
- [ ] Static files collected
- [ ] Gunicorn service running
- [ ] Nginx configured and running
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] File permissions set correctly
- [ ] Backup script configured
- [ ] Log rotation configured
- [ ] Monitoring set up

## Maintenance Commands

### Update Application
```bash
cd /var/www/sis-backend
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart sis-gunicorn
```

### View Logs
```bash
# Application logs
tail -f logs/django.log

# Gunicorn logs
tail -f logs/gunicorn-error.log

# Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Restart Services
```bash
sudo systemctl restart sis-gunicorn
sudo systemctl restart nginx
sudo systemctl restart redis-server
```

## Troubleshooting

### Service not starting
```bash
# Check service status
sudo systemctl status sis-gunicorn

# Check logs
sudo journalctl -u sis-gunicorn -n 50
```

### Database connection issues
```bash
# Test database connection
psql -U sis_user -d sis_db -h localhost

# Check PostgreSQL status
sudo systemctl status postgresql
```

### Permission errors
```bash
# Fix permissions
sudo chown -R www-data:www-data /var/www/sis-backend
sudo chmod -R 755 /var/www/sis-backend
```

## Support

For issues, contact: support@your-domain.com
Documentation: https://docs.your-domain.com
