# Deployment Guide

Complete guide for deploying Client Intelligence Monitor in various environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Running Locally](#running-locally)
- [Running on a Server](#running-on-a-server)
- [Systemd Service Setup](#systemd-service-setup)
- [Docker Deployment](#docker-deployment)
- [Environment Variables Reference](#environment-variables-reference)
- [Troubleshooting](#troubleshooting)
- [Performance Tuning](#performance-tuning)
- [Security Considerations](#security-considerations)
- [Monitoring & Logging](#monitoring--logging)

---

## Prerequisites

### Minimum Requirements

- **Python**: 3.8 or higher
- **RAM**: 512 MB minimum, 2 GB recommended
- **Disk Space**: 500 MB minimum, 2 GB recommended
- **OS**: Windows, Linux, or macOS

### Software Dependencies

```bash
# Check Python version
python --version  # Should be 3.8+

# Check pip
pip --version
```

---

## Running Locally

### Quick Start

Perfect for development and testing.

```bash
# 1. Navigate to project directory
cd client-monitor

# 2. Create virtual environment (recommended)
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create data directory
mkdir -p data

# 6. Configure environment (optional)
cp .env.example .env
# Edit .env with your settings

# 7. Seed demo data (optional)
python scripts/seed_demo_data.py --clients 15 --events 50

# 8. Run application
streamlit run app.py
```

The application will be available at `http://localhost:8501`

### Running on Custom Port

```bash
# Run on port 8080
streamlit run app.py --server.port 8080

# Run on all interfaces (accessible from network)
streamlit run app.py --server.address 0.0.0.0
```

### Development Mode

```bash
# Enable auto-reload on file changes
streamlit run app.py --server.runOnSave true

# Disable CORS (for development only)
streamlit run app.py --server.enableCORS false
```

---

## Running on a Server

### Linux Server Deployment

#### 1. Initial Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.8+
sudo apt install python3 python3-pip python3-venv -y

# Create application user
sudo useradd -m -s /bin/bash clientmonitor
sudo su - clientmonitor
```

#### 2. Application Setup

```bash
# Clone or upload application
cd ~
# Upload files via scp, rsync, or git clone

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create data directory
mkdir -p data

# Set up configuration
cp .env.example .env
nano .env  # Edit configuration
```

#### 3. Create Streamlit Configuration

```bash
# Create Streamlit config directory
mkdir -p ~/.streamlit

# Create config file
cat > ~/.streamlit/config.toml << EOF
[server]
port = 8501
address = "0.0.0.0"
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
serverAddress = "your-domain.com"
serverPort = 8501

[theme]
primaryColor = "#1976d2"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
EOF
```

#### 4. Test Application

```bash
# Run application
streamlit run app.py

# Test from another terminal
curl http://localhost:8501
```

### Windows Server Deployment

```powershell
# Install Python 3.8+ from python.org

# Create application directory
New-Item -ItemType Directory -Path "C:\ClientMonitor"
cd C:\ClientMonitor

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt

# Create data directory
New-Item -ItemType Directory -Path "data"

# Configure environment
Copy-Item .env.example .env
notepad .env

# Run application
streamlit run app.py
```

---

## Systemd Service Setup

Create a systemd service to run the application automatically on Linux servers.

### 1. Create Service File

```bash
sudo nano /etc/systemd/system/client-monitor.service
```

### 2. Service Configuration

```ini
[Unit]
Description=Client Intelligence Monitor
After=network.target

[Service]
Type=simple
User=clientmonitor
Group=clientmonitor
WorkingDirectory=/home/clientmonitor/client-monitor
Environment="PATH=/home/clientmonitor/client-monitor/venv/bin"
ExecStart=/home/clientmonitor/client-monitor/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0

# Restart policy
Restart=on-failure
RestartSec=10
StartLimitInterval=400
StartLimitBurst=5

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=client-monitor

[Install]
WantedBy=multi-user.target
```

### 3. Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable client-monitor

# Start service
sudo systemctl start client-monitor

# Check status
sudo systemctl status client-monitor

# View logs
sudo journalctl -u client-monitor -f
```

### 4. Service Management Commands

```bash
# Start service
sudo systemctl start client-monitor

# Stop service
sudo systemctl stop client-monitor

# Restart service
sudo systemctl restart client-monitor

# Check status
sudo systemctl status client-monitor

# View logs (last 100 lines)
sudo journalctl -u client-monitor -n 100

# Follow logs in real-time
sudo journalctl -u client-monitor -f

# Disable service (don't start on boot)
sudo systemctl disable client-monitor
```

---

## Docker Deployment

### Using Docker Compose (Recommended)

#### 1. Project Structure

```
client-monitor/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── app.py
├── requirements.txt
└── ...
```

#### 2. Run with Docker Compose

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

#### 3. Access Application

Open browser to `http://localhost:8501`

### Using Docker Directly

```bash
# Build image
docker build -t client-monitor:latest .

# Run container
docker run -d \
  --name client-monitor \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -e DEMO_MODE=false \
  -e GOOGLE_API_KEY=your-key \
  client-monitor:latest

# View logs
docker logs -f client-monitor

# Stop container
docker stop client-monitor

# Remove container
docker rm client-monitor
```

### Docker Management

```bash
# List running containers
docker ps

# List all containers
docker ps -a

# View container logs
docker logs client-monitor

# Execute command in container
docker exec -it client-monitor bash

# Restart container
docker restart client-monitor

# Update application
docker-compose down
docker-compose pull
docker-compose up -d
```

### Persistent Data with Docker

The Docker configuration mounts the `data/` directory as a volume to persist:
- SQLite database
- Settings
- Cache files

**Backup database from Docker:**

```bash
# Copy database from container
docker cp client-monitor:/app/data/client_intelligence.db ./backup.db

# Or backup entire data directory
docker cp client-monitor:/app/data ./data-backup
```

---

## Environment Variables Reference

### Application Mode

```bash
# Demo mode (uses sample data)
DEMO_MODE=true

# Application mode (Development/Production)
APP_MODE=Production
```

### Database Configuration

```bash
# Database path
DATABASE_PATH=data/client_intelligence.db

# Connection timeout (seconds)
DB_TIMEOUT=30
```

### API Configuration

```bash
# Use mock APIs (for testing without API keys)
USE_MOCK_APIS=true

# Google Custom Search API
GOOGLE_API_KEY=your-api-key-here
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id

# NewsAPI
NEWSAPI_KEY=your-newsapi-key-here

# API rate limiting
MAX_API_CALLS_PER_HOUR=100
```

### Monitoring Configuration

```bash
# Minimum relevance score (0.0 to 1.0)
MIN_RELEVANCE_SCORE=0.5

# Scan lookback period (days)
SCAN_LOOKBACK_DAYS=7

# Events to fetch per scan
EVENTS_PER_SCAN=50

# Auto-scan interval (minutes)
AUTO_SCAN_INTERVAL=60
```

### Email Notifications

```bash
# SMTP server configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true

# SMTP authentication
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Email settings
EMAIL_FROM=noreply@yourdomain.com
EMAIL_REPLY_TO=support@yourdomain.com
```

### Streamlit Configuration

```bash
# Streamlit server settings
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true

# Disable telemetry
STREAMLIT_TELEMETRY=false
STREAMLIT_EMAIL_CAPTURE=false
```

### Performance Tuning

```bash
# Cache TTL (seconds)
CACHE_TTL=3600

# Maximum cache entries
MAX_CACHE_ENTRIES=1000

# Events per page
EVENTS_PER_PAGE=50

# Search result limit
SEARCH_LIMIT=100
```

### Security

```bash
# Enable/disable features
ENABLE_BACKUP=true
ENABLE_EXPORT=true
ENABLE_DELETE=true

# Session timeout (minutes)
SESSION_TIMEOUT=60
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Port Already in Use

**Error**: `OSError: [Errno 98] Address already in use`

**Solution**:
```bash
# Find process using port 8501
lsof -i :8501  # Linux/Mac
netstat -ano | findstr :8501  # Windows

# Kill process
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows

# Or use different port
streamlit run app.py --server.port 8080
```

#### Issue 2: Database Locked

**Error**: `sqlite3.OperationalError: database is locked`

**Solution**:
```bash
# Close all connections to database
# Stop application
sudo systemctl stop client-monitor

# Check for lock file
ls -la data/*.db-*
rm data/*.db-journal  # If safe to do so

# Restart application
sudo systemctl start client-monitor
```

#### Issue 3: Module Not Found

**Error**: `ModuleNotFoundError: No module named 'streamlit'`

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep streamlit
```

#### Issue 4: Permission Denied

**Error**: `PermissionError: [Errno 13] Permission denied: 'data/client_intelligence.db'`

**Solution**:
```bash
# Fix directory permissions
sudo chown -R clientmonitor:clientmonitor /home/clientmonitor/client-monitor
chmod -R 755 /home/clientmonitor/client-monitor
chmod -R 775 /home/clientmonitor/client-monitor/data
```

#### Issue 5: Application Crashes on Startup

**Check logs**:
```bash
# Systemd service
sudo journalctl -u client-monitor -n 100

# Docker
docker logs client-monitor

# Manual run (for debugging)
streamlit run app.py --logger.level debug
```

### Network Issues

#### Can't Access from Other Machines

**Solution**:
```bash
# Check firewall
sudo ufw status
sudo ufw allow 8501/tcp

# Check server binding
netstat -tuln | grep 8501

# Ensure bound to 0.0.0.0 not 127.0.0.1
streamlit run app.py --server.address 0.0.0.0
```

#### SSL/HTTPS Issues

**Reverse Proxy Setup** (Recommended for production):

```nginx
# Nginx configuration
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### API Issues

#### Google API Not Working

**Check**:
```bash
# Verify API key
echo $GOOGLE_API_KEY

# Test API manually
curl "https://www.googleapis.com/customsearch/v1?key=YOUR_KEY&cx=YOUR_CX&q=test"

# Check quota
# Visit: https://console.cloud.google.com/apis/dashboard
```

#### NewsAPI Not Working

**Check**:
```bash
# Verify API key
echo $NEWSAPI_KEY

# Test API manually
curl "https://newsapi.org/v2/everything?q=test&apiKey=YOUR_KEY"

# Check plan limits
# Visit: https://newsapi.org/account
```

---

## Performance Tuning

### Database Optimization

#### 1. Vacuum Database

```bash
# Run vacuum to reclaim space and optimize
sqlite3 data/client_intelligence.db "VACUUM;"

# Run analyze to update query planner statistics
sqlite3 data/client_intelligence.db "ANALYZE;"
```

#### 2. Add Indices (if needed)

```sql
-- Check existing indices
.indices

-- Add index for common queries (if not exists)
CREATE INDEX IF NOT EXISTS idx_events_relevance
ON events(relevance_score DESC, detected_date DESC);

CREATE INDEX IF NOT EXISTS idx_events_client_date
ON events(client_id, detected_date DESC);
```

#### 3. Monitor Database Size

```bash
# Check database size
du -h data/client_intelligence.db

# Check table sizes
sqlite3 data/client_intelligence.db << EOF
SELECT
    name,
    SUM("pgsize") / 1024.0 / 1024.0 as size_mb
FROM "dbstat"
GROUP BY name
ORDER BY size_mb DESC;
EOF
```

### Application Performance

#### 1. Caching Strategy

```python
# Adjust cache settings in .env
CACHE_TTL=3600  # 1 hour
MAX_CACHE_ENTRIES=1000

# Clear cache if needed (in Settings page)
```

#### 2. Pagination

```python
# Reduce events per page for faster loading
EVENTS_PER_PAGE=30  # Default is 50
```

#### 3. Concurrent Users

For multiple concurrent users:

```bash
# Use gunicorn or similar WSGI server
# Note: Streamlit is designed for single-threaded use
# For multi-user, consider:
# - Multiple instances behind load balancer
# - Streamlit Cloud
# - Streamlit for Teams
```

### Memory Management

#### Monitor Memory Usage

```bash
# Check application memory
ps aux | grep streamlit

# Monitor in real-time
top -p $(pgrep -f streamlit)

# Docker memory usage
docker stats client-monitor
```

#### Limit Docker Memory

```yaml
# docker-compose.yml
services:
  app:
    mem_limit: 512m
    memswap_limit: 1g
```

### Network Performance

#### 1. Enable Compression

```toml
# ~/.streamlit/config.toml
[server]
enableStaticServing = true
enableGzip = true
```

#### 2. CDN for Static Assets

```bash
# If deploying at scale, serve static assets via CDN
# Configure in Streamlit config or reverse proxy
```

### Monitoring Performance

#### Built-in Metrics

```python
# Enable performance monitoring in Settings page
# View in System Testing page
```

#### External Monitoring

```bash
# Use tools like:
# - Prometheus + Grafana
# - New Relic
# - DataDog
# - Custom logging
```

---

## Security Considerations

### API Keys

```bash
# NEVER commit API keys to version control
# Use environment variables or secrets management

# Example: Using .env (NOT committed)
GOOGLE_API_KEY=your-key-here

# Or: Using secrets manager
# - AWS Secrets Manager
# - HashiCorp Vault
# - Azure Key Vault
```

### File Permissions

```bash
# Restrict access to sensitive files
chmod 600 .env
chmod 600 settings.json
chmod 644 data/*.db  # Read-only for group/others
```

### Network Security

```bash
# Run behind reverse proxy (Nginx, Apache)
# Enable HTTPS with SSL certificate (Let's Encrypt)
# Configure firewall rules
# Restrict database access
```

### Input Validation

The application includes:
- Input sanitization in forms
- SQL injection prevention (parameterized queries)
- XSS protection (Streamlit built-in)

### Backup Strategy

```bash
# Automated daily backups
0 2 * * * /usr/local/bin/backup-client-monitor.sh

# backup-client-monitor.sh:
#!/bin/bash
DATE=$(date +%Y%m%d)
cp /path/to/data/client_intelligence.db /backup/db_$DATE.db
find /backup -name "db_*.db" -mtime +30 -delete
```

---

## Monitoring & Logging

### Application Logs

#### Systemd Service Logs

```bash
# View all logs
sudo journalctl -u client-monitor

# View recent logs
sudo journalctl -u client-monitor -n 100

# Follow logs
sudo journalctl -u client-monitor -f

# Filter by date
sudo journalctl -u client-monitor --since "2024-01-01"

# Export logs
sudo journalctl -u client-monitor > logs.txt
```

#### Docker Logs

```bash
# View logs
docker logs client-monitor

# Follow logs
docker logs -f client-monitor

# Last 100 lines
docker logs --tail 100 client-monitor

# With timestamps
docker logs -t client-monitor
```

### Log Rotation

```bash
# Configure logrotate
sudo nano /etc/logrotate.d/client-monitor

# Content:
/var/log/client-monitor/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 clientmonitor clientmonitor
}
```

### Health Checks

#### Create Health Check Endpoint

Monitor application health:

```bash
# Check if application is responding
curl -f http://localhost:8501 || exit 1

# In systemd service:
[Service]
ExecStartPost=/usr/local/bin/health-check.sh
```

#### Docker Health Check

```dockerfile
# In Dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501 || exit 1
```

### Monitoring Tools

#### System Metrics

```bash
# CPU, Memory, Disk
htop
vmstat 1
iostat 1

# Network
nethogs
iftop
```

#### Application Metrics

Use the built-in System Testing page:
- Navigate to Settings > System Testing
- View API status, database stats, performance metrics

---

## Production Checklist

Before deploying to production:

- [ ] Configure `.env` with production settings
- [ ] Set `DEMO_MODE=false`
- [ ] Configure real API keys (if using)
- [ ] Set up database backups
- [ ] Configure systemd service or Docker
- [ ] Set up reverse proxy with HTTPS
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerting
- [ ] Configure log rotation
- [ ] Test backup and restore procedures
- [ ] Document recovery procedures
- [ ] Set up automated updates (with testing)
- [ ] Configure email notifications
- [ ] Test with production-like data volume
- [ ] Perform security audit
- [ ] Set up health checks
- [ ] Document deployment procedures
- [ ] Train team on operations
- [ ] Prepare rollback plan

---

## Additional Resources

- **Streamlit Deployment**: https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app
- **Docker Documentation**: https://docs.docker.com/
- **Systemd Documentation**: https://systemd.io/
- **Nginx Documentation**: https://nginx.org/en/docs/
- **Let's Encrypt SSL**: https://letsencrypt.org/

---

**Last Updated**: 2025-10-15
**Version**: 1.0.0
