# 🚀 Production Deployment Guide

## 📋 Prerequisites

- Linux server (Ubuntu 22.04+ recommended)
- Docker & Docker Compose
- SSL certificates (Let's Encrypt recommended)
- Domain name configured
- At least 4GB RAM, 2 CPU cores
- 50GB+ storage

## 🔐 Security Pre-Deployment Checklist

### Environment Variables ✅
- [ ] Change `SECRET_KEY` to a secure random string
- [ ] Set strong database passwords
- [ ] Configure secure Redis password
- [ ] Set Elasticsearch password
- [ ] Update CORS origins to your domain
- [ ] Configure rate limiting settings
- [ ] Set up email credentials (SMTP)

### SSL/TLS Configuration ✅
- [ ] Obtain SSL certificates for your domain
- [ ] Configure Nginx with SSL certificates
- [ ] Enable HTTP to HTTPS redirect
- [ ] Configure SSL cipher suites
- [ ] Set up HSTS headers

### Database Security ✅
- [ ] Change default PostgreSQL passwords
- [ ] Enable database connection encryption
- [ ] Configure database backups
- [ ] Set up database user permissions
- [ ] Enable query logging

### Application Security ✅
- [ ] Review and update security headers
- [ ] Configure IP whitelist if needed
- [ ] Set up rate limiting
- [ ] Enable CSRF protection
- [ ] Configure session security

### Monitoring & Logging ✅
- [ ] Set up centralized logging
- [ ] Configure error tracking (Sentry)
- [ ] Set up performance monitoring
- [ ] Configure health checks
- [ ] Set up alerting

## 🛠️ Deployment Steps

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create application user
sudo useradd -m -s /bin/bash aicp
sudo usermod -aG docker aicp

# Create directories
sudo mkdir -p /opt/aicp
sudo chown aicp:aicp /opt/aicp
```

### 2. Clone Repository

```bash
# Clone repository
cd /opt/aicp
git clone https://github.com/AjmalDanish/AI-Research-Competitive-Intelligence-Platform.git .
git checkout main

# Set permissions
chmod -R 755 .
chown -R aicp:aicp .
```

### 3. Configure Environment Variables

```bash
# Copy production environment template
cp backend/.env.production backend/.env

# Generate secure secrets
openssl rand -hex 32  # For SECRET_KEY
openssl rand -hex 16  # For DB password
openssl rand -hex 16  # For Redis password
openssl rand -hex 16  # For Elasticsearch password

# Edit environment file
nano backend/.env
```

### 4. Configure SSL Certificates

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificates
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates to project
sudo mkdir -p docker/nginx/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem docker/nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem docker/nginx/ssl/
sudo chown -R aicp:aicp docker/nginx/ssl
```

### 5. Configure Nginx

```bash
# Create Nginx configuration
cat > docker/nginx/nginx.conf << 'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;

    # Upstream backend
    upstream backend {
        server backend:8000;
    }

    # HTTP server (redirect to HTTPS)
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        # Frontend
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }

        # Backend API
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health {
            proxy_pass http://backend/health;
            access_log off;
        }

        # Static files caching
        location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
EOF
```

### 6. Build and Deploy

```bash
# Build Docker images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f
```

### 7. Configure Backups

```bash
# Create backup script
cat > /opt/aicp/scripts/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/aicp"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker exec aicp_postgres pg_dump -U aicp_user aicp | gzip > $BACKUP_DIR/postgres_$DATE.sql.gz

# Backup Redis
docker exec aicp_redis redis-cli --rdb /data/dump.rdb
docker cp aicp_redis:/data/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

# Backup Elasticsearch
curl -X PUT "elastic:secure_password@localhost:9200/_snapshot/backup/snapshot_$DATE?wait_for_completion=true"

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /opt/aicp/scripts/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /opt/aicp/scripts/backup.sh
```

### 8. Set Up Monitoring

```bash
# Access Grafana
# URL: https://yourdomain.com:3000
# Default credentials: admin / secure_grafana_password

# Configure Prometheus datasource
# Import dashboard templates
# Set up alerting rules
```

### 9. Health Checks

```bash
# Check all services
curl https://yourdomain.com/health

# Check specific services
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs nginx
```

## 🔧 Maintenance Tasks

### Daily
- Monitor application logs
- Check error rates
- Review security alerts

### Weekly
- Review and rotate logs
- Check disk space
- Review backup status
- Update dependencies

### Monthly
- Security audit
- Performance review
- Database optimization
- SSL certificate renewal check

### Quarterly
- Disaster recovery testing
- Security updates
- Performance tuning
- Capacity planning

## 🚨 Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs service_name

# Check resource usage
docker stats

# Restart services
docker-compose -f docker-compose.prod.yml restart service_name
```

### Database Issues
```bash
# Connect to database
docker exec -it aicp_postgres psql -U aicp_user -d aicp

# Check connections
SELECT count(*) FROM pg_stat_activity;

# Kill idle connections
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle';
```

### Performance Issues
```bash
# Check resource usage
docker stats

# Analyze slow queries
docker exec -it aicp_postgres psql -U aicp_user -d aicp -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Check Redis memory
docker exec aicp_redis redis-cli INFO memory
```

## 📊 Monitoring Endpoints

- **Application**: https://yourdomain.com/health
- **Prometheus**: https://yourdomain.com:9090
- **Grafana**: https://yourdomain.com:3000
- **API Docs**: https://yourdomain.com/docs

## 🔄 Updates and Rollbacks

### Update Application
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build backend

# Health check
curl https://yourdomain.com/health
```

### Rollback
```bash
# Checkout previous version
git checkout <previous_commit_hash>

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build backend
```

## 📞 Support

For issues and support:
- GitHub Issues: https://github.com/AjmalDanish/AI-Research-Competitive-Intelligence-Platform/issues
- Documentation: https://github.com/AjmalDanish/AI-Research-Competitive-Intelligence-Platform/blob/main/README.md

---

**🎉 Your application is now production-ready!**