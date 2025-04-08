# NewEdu API Deployment Reference

This document provides a complete reference for deploying the NewEdu API in a production environment.

## Table of Contents

1. [Server Requirements](#server-requirements)
2. [Directory Structure](#directory-structure)
3. [Database Setup](#database-setup)
4. [Application Setup](#application-setup)
5. [SystemD Service Configuration](#systemd-service-configuration)
6. [Nginx Configuration](#nginx-configuration)
7. [SSL Configuration (Let's Encrypt)](#ssl-configuration)
8. [Security Considerations](#security-considerations)
9. [Backup and Maintenance](#backup-and-maintenance)
10. [Monitoring](#monitoring)

## Server Requirements

- Ubuntu 20.04 LTS or newer (recommended)
- Python 3.8+ with venv module
- PostgreSQL 12+ 
- Nginx 1.18+
- 2GB RAM minimum (4GB recommended)
- 20GB storage minimum

## Directory Structure

Recommended directory structure:

```
/var/www/api.newedu.uz/
├── app/                 # Application code
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   └── utils/
├── .env                # Environment variables (secured)
├── .env.example        # Example environment file
├── main.py             # Application entry point
├── create_superuser.py # Superuser creation script
├── create_tables.py    # Database tables creation script
├── .venv/              # Python virtual environment
├── requirements.txt    # Python dependencies
└── logs/               # Application logs
```

## Database Setup

### Installing PostgreSQL

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

### Creating the Database and User

```bash
sudo -u postgres psql
```

In the PostgreSQL prompt, run:

```sql
CREATE DATABASE newedu;
CREATE USER newedu_user WITH PASSWORD 'strong_password_here';
GRANT ALL PRIVILEGES ON DATABASE newedu TO newedu_user;
\c newedu
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO newedu_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO newedu_user;
```

### PostgreSQL Performance Optimization

Edit the PostgreSQL configuration file:

```bash
sudo nano /etc/postgresql/12/main/postgresql.conf
```

Add or modify these settings:

```ini
# Memory settings
shared_buffers = 1GB                  # 25% of RAM for dedicated server
work_mem = 32MB                       # Adjust based on complex queries
maintenance_work_mem = 256MB          # For maintenance operations

# Write settings
wal_buffers = 16MB                    # Helps with write performance
commit_delay = 1000                   # Microseconds to wait for commit
commit_siblings = 5                   # Min concurrent transactions before commit delay

# Query planner
effective_cache_size = 3GB            # Set to 75% of RAM
random_page_cost = 1.1                # Lower for SSDs (4.0 is default)

# Connection settings
max_connections = 100                 # Adjust based on expected load
```

Restart PostgreSQL:

```bash
sudo systemctl restart postgresql
```

## Application Setup

### Clone the Repository

```bash
sudo mkdir -p /var/www/api.newedu.uz
sudo chown -R $USER:$USER /var/www/api.newedu.uz
git clone https://github.com/yourusername/newedu-api.git /var/www/api.newedu.uz
cd /var/www/api.newedu.uz
```

### Set Up Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Configure Environment Variables

Create and secure `.env` file:

```bash
cp .env.example .env
nano .env
```

Add the following content (modify as needed):

```
DATABASE_URL=postgresql://newedu_user:strong_password_here@localhost/newedu
JWT_SECRET_KEY=your_very_long_and_secure_random_key_here
```

Secure the file:

```bash
chmod 600 .env
```

### Create Database Tables

```bash
source .venv/bin/activate
python create_tables.py
```

### Create a Superuser

```bash
source .venv/bin/activate
python create_superuser.py --phone="+998XXXXXXXXX" --name="Admin Name"
```

## SystemD Service Configuration

Create service file:

```bash
sudo nano /etc/systemd/system/api_newedu.service
```

Add the following content:

```ini
[Unit]
Description=NewEdu FastAPI Service
After=network.target postgresql.service
Wants=postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/api.newedu.uz
ExecStart=/var/www/api.newedu.uz/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=5

# Output handling
StandardOutput=append:/var/log/api_newedu.log
StandardError=append:/var/log/api_newedu_error.log

# Security measures
NoNewPrivileges=yes
PrivateTmp=yes

# Resource limits
LimitNOFILE=4096

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable api_newedu
sudo systemctl start api_newedu
sudo systemctl status api_newedu
```

## Nginx Configuration

Create Nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/api.newedu.uz
```

Add the following content:

```nginx
server {
    listen 80;
    server_name api.newedu.uz;

    access_log /var/log/nginx/api_newedu_access.log;
    error_log /var/log/nginx/api_newedu_error.log;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Cache static assets
    location /static/ {
        alias /var/www/api.newedu.uz/static/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options SAMEORIGIN;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/api.newedu.uz /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL Configuration

### Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx
```

### Obtain SSL Certificate

```bash
sudo certbot --nginx -d api.newedu.uz
```

Follow the prompts to complete the certificate setup.

### Auto-renewal Configuration

Certbot sets up a systemd timer automatically. Verify with:

```bash
sudo systemctl list-timers
```

## Security Considerations

### Firewall Setup

```bash
sudo apt install ufw
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
sudo ufw status
```

### Fail2Ban Installation

```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### Regular Updates

```bash
sudo apt update
sudo apt upgrade
```

### Database Backups

Create a backup script at `/var/www/api.newedu.uz/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/newedu"
DATETIME=$(date +"%Y-%m-%d_%H-%M-%S")
PG_USER="newedu_user"
PG_PASS="strong_password_here"
DATABASE="newedu"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Set environment variable for password
export PGPASSWORD="$PG_PASS"

# Database backup
pg_dump -U "$PG_USER" -h localhost "$DATABASE" | gzip > "$BACKUP_DIR/newedu_db_$DATETIME.sql.gz"

# Code backup
tar -czvf "$BACKUP_DIR/newedu_code_$DATETIME.tar.gz" -C /var/www api.newedu.uz

# Delete backups older than 30 days
find "$BACKUP_DIR" -type f -name "*.gz" -mtime +30 -delete

# Clear password from environment
unset PGPASSWORD
```

Make it executable and set up a cron job:

```bash
sudo chmod +x /var/www/api.newedu.uz/backup.sh
sudo crontab -e
```

Add the following line to run daily at 2 AM:

```
0 2 * * * /var/www/api.newedu.uz/backup.sh
```

## Monitoring

### Log Rotation

Create a log rotation configuration:

```bash
sudo nano /etc/logrotate.d/newedu
```

Add the following content:

```
/var/log/api_newedu*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload api_newedu
    endscript
}
```

### Basic Monitoring Setup

Install monitoring tools:

```bash
sudo apt install htop iotop netstat
```

### PostgreSQL Monitoring

Create a simple monitoring script at `/var/www/api.newedu.uz/monitor_db.sh`:

```bash
#!/bin/bash

# Connect to PostgreSQL and get stats
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"
sudo -u postgres psql -c "SELECT datname, numbackends, xact_commit, xact_rollback, blks_read, blks_hit, tup_returned, tup_fetched, tup_inserted, tup_updated, tup_deleted FROM pg_stat_database WHERE datname='newedu';"
sudo -u postgres psql -c "SELECT pid, usename, application_name, client_addr, state, query_start, wait_event_type, query FROM pg_stat_activity WHERE datname='newedu';"
```

Make it executable:

```bash
sudo chmod +x /var/www/api.newedu.uz/monitor_db.sh
```

### Consider Advanced Monitoring

For a more robust solution, consider setting up:

- Prometheus + Grafana for metrics
- ELK Stack for log analysis
- Uptime Robot or similar service for external monitoring
- pgAdmin for PostgreSQL monitoring

## Additional Recommendations

### File Permissions

Ensure proper permissions:

```bash
sudo chown -R www-data:www-data /var/www/api.newedu.uz
sudo find /var/www/api.newedu.uz -type d -exec chmod 755 {} \;
sudo find /var/www/api.newedu.uz -type f -exec chmod 644 {} \;
sudo chmod 600 /var/www/api.newedu.uz/.env
```

### Regular Maintenance Checklist

- Update OS packages weekly
- Run `VACUUM ANALYZE` on PostgreSQL regularly
- Monitor disk space
- Check service status
- Review application logs
- Test backups periodically
