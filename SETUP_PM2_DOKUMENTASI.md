# 📋 DOKUMENTASI SETUP PM2 - Sistem Manajemen Pekerjaan

**Last Updated:** 30 Mei 2026  
**Environment:** Windows Server 2022 VM  
**Status:** ✅ Production Ready

---

## 📌 **Daftar Isi**

1. [System Overview](#system-overview)
2. [Environment Configuration](#environment-configuration)
3. [PM2 Configuration](#pm2-configuration)
4. [Setup Instructions](#setup-instructions)
5. [Running Services](#running-services)
6. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
7. [Backup & Recovery](#backup--recovery)

---

## 🏗️ **System Overview**

### **Architecture**

```
┌─────────────────────────────────────────────┐
│     Windows Server 2022 - 192.168.111.130   │
├─────────────────────────────────────────────┤
│                                             │
│  PM2 (Process Manager)                      │
│  ├── Django 5.2.8 (Port 4321)               │
│  ├── Celery Worker (Redis broker)           │
│  └── Celery Beat (Task scheduler)           │
│                                             │
│  PostgreSQL 16 (Port 5432)                  │
│  Redis 5.0.1 (Port 6379)                    │
│  Google Calendar API (Service Account)      │
│                                             │
└─────────────────────────────────────────────┘
```

### **Technology Stack**

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Web Framework** | Django | 5.2.8 | Main application |
| **Process Manager** | PM2 | Latest | Auto-restart, logging |
| **Task Queue** | Celery | 5.3.4 | Background jobs |
| **Message Broker** | Redis | 5.0.1 | Celery broker + cache |
| **Database** | PostgreSQL | 16 | Data persistence |
| **API Integration** | Google Calendar | v3 | Leave event sync |
| **Notification** | Fonnte API | v1 | WhatsApp messages |

---

## ⚙️ **Environment Configuration**

### **.env File - Current Configuration**

**Location:** `C:\repos\proyek_manajemen_job\.env`

```env
# ============================================================================
# DJANGO CORE SETTINGS
# ============================================================================
DJANGO_ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your-super-secret-key-change-this-in-production-min-50-chars-12345678
SECURE_SSL_REDIRECT=False
CSRF_COOKIE_SECURE=False
SESSION_COOKIE_SECURE=False

# Hosts
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.100

# ============================================================================
# DATABASE CONFIGURATION - PostgreSQL 16
# ============================================================================
DB_ENGINE=django.db.backends.postgresql
DB_NAME=proyek_management_job
DB_USER=postgres
DB_PASSWORD=PostgresAdmin2026!
DB_HOST=localhost
DB_PORT=5432
DB_CONN_MAX_AGE=600
DB_CONN_HEALTH_CHECK=true

# ============================================================================
# REDIS CONFIGURATION
# ============================================================================
REDIS_URL=redis://localhost:6379/1
CACHE_TIMEOUT=3600

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_TIMEZONE=Asia/Jakarta

# ============================================================================
# LOGGING & STORAGE
# ============================================================================
LOG_DIR=C:/logs/management-job
LOG_LEVEL=INFO
DJANGO_LOG_LEVEL=INFO
CELERY_LOG_LEVEL=INFO

MEDIA_ROOT=C:/data/management-job/media
MEDIA_URL=/media/
STATIC_ROOT=C:/data/management-job/static
STATIC_URL=/static/

# ============================================================================
# GOOGLE CALENDAR API
# ============================================================================
GOOGLE_CALENDAR_CREDENTIALS_FILE=config/credentials/google-calendar-sa.json
GOOGLE_CALENDAR_ID=ges3ra8851qk05jqlsfgjct3h4@group.calendar.google.com

# ============================================================================
# FONTTE WHATSAPP API
# ============================================================================
FONTTE_API_TOKEN=your-fontte-api-token-here
FONTTE_API_BASE_URL=https://api.fontte.com/v1
FONTTE_API_ENABLED=true

# ============================================================================
# PUBLIC URL
# ============================================================================
DJANGO_PUBLIC_URL=http://localhost:4321
CSRF_TRUSTED_ORIGINS=http://localhost:4321,http://192.168.111.130:4321
```

### **Key Settings untuk Production**

```env
# Production changes needed:
DJANGO_ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<generate-new-secure-key>
SECURE_SSL_REDIRECT=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
DJANGO_PUBLIC_URL=https://yourdomain.com
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

---

## 🚀 **PM2 Configuration**

### **ecosystem.config.js - Current Setup**

**Location:** `C:\repos\proyek_manajemen_job\ecosystem.config.js`

```javascript
module.exports = {
  apps: [
    // ================================================================
    // DJANGO WEB SERVER
    // ================================================================
    {
      name: "management-django",
      cwd: "C:\\repos\\proyek_manajemen_job",
      script: "venv\\Scripts\\pythonw.exe",
      args: "manage.py runserver 0.0.0.0:4321",
      interpreter: "none",
      autorestart: true,
      restart_delay: 5000,
      max_memory_restart: "500M",
      output: "C:/logs/management-job/django.log",
      error: "C:/logs/management-job/django-error.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss Z"
    },

    // ================================================================
    // CELERY WORKER - Background Tasks
    // ================================================================
    {
      name: "management-celery-worker",
      cwd: "C:\\repos\\proyek_manajemen_job",
      script: "venv\\Scripts\\pythonw.exe",
      args: "-m celery -A config worker -l info",
      interpreter: "none",
      autorestart: true,
      restart_delay: 5000,
      max_memory_restart: "500M",
      output: "C:/logs/management-job/celery-worker.log",
      error: "C:/logs/management-job/celery-worker-error.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss Z"
    },

    // ================================================================
    // CELERY BEAT - Task Scheduler
    // ================================================================
    {
      name: "management-celery-beat",
      cwd: "C:\\repos\\proyek_manajemen_job",
      script: "venv\\Scripts\\pythonw.exe",
      args: "-m celery -A config beat -l info",
      interpreter: "none",
      autorestart: true,
      restart_delay: 5000,
      max_memory_restart: "300M",
      output: "C:/logs/management-job/celery-beat.log",
      error: "C:/logs/management-job/celery-beat-error.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss Z"
    }
  ]
};
```

### **Key Configuration Explained**

| Parameter | Value | Purpose |
|-----------|-------|---------|
| **script** | pythonw.exe | Python executable (w = no console window) |
| **cwd** | Project directory | Working directory |
| **autorestart** | true | Auto-restart on crash |
| **restart_delay** | 5000ms | Delay before restart |
| **max_memory_restart** | 500M | Restart if exceeds memory |
| **output** | C:/logs/... | Stdout log file |
| **error** | C:/logs/... | Stderr log file |

---

## 📥 **Setup Instructions**

### **Prerequisites**

```
✅ Windows Server 2022+
✅ Python 3.11+
✅ PostgreSQL 16
✅ Redis 5.0.1
✅ PM2 (npm install -g pm2)
✅ Node.js 18+
```

### **Step 1: Clone Repository**

```powershell
cd C:\repos
git clone <repo-url> proyek_manajemen_job
cd proyek_manajemen_job
```

### **Step 2: Setup Python Virtual Environment**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### **Step 3: Configure Environment Variables**

```powershell
# Copy and edit .env
cp .env.example .env
# Edit .env dengan values yang sesuai
```

### **Step 4: Setup Database**

```powershell
# Create database (PostgreSQL)
psql -U postgres
> CREATE DATABASE proyek_management_job;
> \q

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
# Username: admin
# Password: <your-secure-password>
```

### **Step 5: Collect Static Files**

```powershell
python manage.py collectstatic --noinput
```

### **Step 6: Setup Google Calendar Credentials**

```powershell
# Copy service account JSON ke config/credentials/
mkdir config/credentials
# Download dari Google Cloud Console sebagai google-calendar-sa.json
```

### **Step 7: Create Log Directories**

```powershell
mkdir C:/logs/management-job
mkdir C:/data/management-job/media
mkdir C:/data/management-job/static
```

### **Step 8: Start PM2 Services**

```powershell
# Initialize PM2
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save

# Create Windows startup script (optional)
pm2 startup windows-startup --user Administrator
```

---

## 🎯 **Running Services**

### **Start All Services**

```powershell
pm2 start ecosystem.config.js
```

### **Check Status**

```powershell
pm2 status
pm2 logs
```

### **Individual Service Management**

```powershell
# Start specific service
pm2 start management-django
pm2 start management-celery-worker
pm2 start management-celery-beat

# Stop
pm2 stop management-django

# Restart
pm2 restart management-django

# Delete
pm2 delete management-django
```

### **Monitor Services**

```powershell
# Real-time monitoring
pm2 monit

# View logs
pm2 logs management-django
pm2 logs management-celery-worker --lines 100

# Clear logs
pm2 flush
```

---

## 🔍 **Monitoring & Troubleshooting**

### **Check Service Health**

```powershell
# Verify Django is running
(Invoke-WebRequest -Uri "http://127.0.0.1:4321/" -UseBasicParsing).StatusCode
# Expected: 302 (redirect to login) or 200

# Verify Database
psql -U postgres -d proyek_management_job -c "SELECT COUNT(*) FROM core_job;"

# Verify Redis
redis-cli -p 6379 ping
# Expected: PONG

# Verify Celery
python manage.py shell
>>> from celery.app.control import Inspect
>>> i = Inspect(app=None)
>>> i.active()
```

### **Common Issues & Solutions**

#### **Issue: Django not starting**

```powershell
# Check logs
pm2 logs management-django

# Common causes:
# 1. Port 4321 already in use
netstat -ano | findstr :4321

# 2. Database connection failed
# Check .env DB credentials

# 3. Missing migrations
python manage.py migrate
```

#### **Issue: Celery worker not processing tasks**

```powershell
# Check Celery logs
pm2 logs management-celery-worker

# Verify Redis connection
redis-cli -p 6379
> ping
> DBSIZE

# Restart Celery
pm2 restart management-celery-worker
```

#### **Issue: Celery Beat not scheduling tasks**

```powershell
# Check scheduler database
python manage.py shell
>>> from django.core.cache import cache
>>> cache.get('celerybeat')

# Verify task configuration
python manage.py inspect_celery_beat

# Reset scheduler
rm celerybeat-schedule*
pm2 restart management-celery-beat
```

#### **Issue: High memory usage**

```powershell
# Check memory per service
pm2 status

# Restart service with memory limit
pm2 restart management-django

# Check logs for memory leaks
pm2 logs management-celery-worker | grep -i memory
```

---

## 💾 **Backup & Recovery**

### **Database Backup**

```powershell
# Backup PostgreSQL
pg_dump -U postgres -d proyek_management_job > backups/backup_$(Get-Date -Format yyyy-MM-dd_HHmmss).sql

# Restore PostgreSQL
psql -U postgres -d proyek_management_job < backups/backup_2026-05-26.sql
```

### **Backup Media Files**

```powershell
# Backup media directory
robocopy C:/data/management-job/media D:/backup/media /S /E
```

### **PM2 Logs Backup**

```powershell
# Backup logs
robocopy C:/logs/management-job D:/backup/logs /S /E
```

### **Database Restore Procedure**

```powershell
# 1. Stop Django
pm2 stop management-django

# 2. Backup current database
pg_dump -U postgres -d proyek_management_job > backups/backup_before_restore.sql

# 3. Drop and restore
psql -U postgres -d proyek_management_job -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
psql -U postgres -d proyek_management_job < backups/backup_2026-05-26.sql

# 4. Restart Django
pm2 restart management-django
```

---

## 📊 **System Performance Baseline**

### **Expected Resource Usage**

```
Django:              ~80-150 MB RAM
Celery Worker:       ~150-250 MB RAM
Celery Beat:         ~60-100 MB RAM
PostgreSQL:          ~300-500 MB RAM
Redis:               ~50-100 MB RAM
──────────────────────────────
Total:               ~700-1000 MB RAM
```

### **Performance Tuning Tips**

1. **Increase Celery concurrency** (if CPU allows):
   ```powershell
   # Edit ecosystem.config.js
   args: "-m celery -A config worker -l info -c 8"
   ```

2. **Database connection pooling** (already configured in .env):
   ```env
   DB_CONN_MAX_AGE=600
   DB_CONN_HEALTH_CHECK=true
   ```

3. **Redis caching enabled**:
   ```env
   REDIS_URL=redis://localhost:6379/1
   CACHE_TIMEOUT=3600
   ```

---

## 🔐 **Security Checklist**

- [ ] Change SECRET_KEY in .env
- [ ] Set DEBUG=False for production
- [ ] Update ALLOWED_HOSTS
- [ ] Configure HTTPS/SSL
- [ ] Secure database credentials
- [ ] Restrict Google Calendar credentials file
- [ ] Setup firewall rules for port 4321
- [ ] Enable automatic backups
- [ ] Rotate logs regularly

---

## 📞 **Support & Maintenance**

### **Regular Maintenance Tasks**

```powershell
# Daily
pm2 status                    # Check all services running

# Weekly
pm2 logs                      # Review logs for errors
pg_dump ... > backup.sql     # Weekly database backup

# Monthly
pm2 kill && pm2 start ecosystem.config.js  # Full restart
rm -r C:/logs/*.log*          # Archive old logs
```

### **Service URLs**

```
Django Web:     http://192.168.111.130:4321
Admin Panel:    http://192.168.111.130:4321/admin/
API Docs:       http://192.168.111.130:4321/api/docs/
Celery Flower:  http://192.168.111.130:5555 (if installed)
```

---

## 📝 **Change Log**

| Date | Changes |
|------|---------|
| 2026-05-30 | Ported Django to PM2, port changed 8000→4321, logs moved to C:/logs/ |
| 2026-05-27 | Database restored with 400 leave events, Google Calendar integration fixed |
| 2026-05-26 | Initial system setup, Celery Beat configured |

---

**Document Version:** 1.0  
**Last Updated:** 30 Mei 2026  
**Maintainer:** System Administrator
