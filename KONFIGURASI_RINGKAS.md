# ✅ RINGKASAN KONFIGURASI TERKINI - Sistem Manajemen Pekerjaan

**Updated:** 30 Mei 2026 | **Status:** Production Ready

---

## 🎯 **Quick Reference**

### **Access Points**

```
🌐 Main Application:    http://192.168.111.130:4321
🔑 Admin Panel:         http://192.168.111.130:4321/admin/
📊 Dashboard:           http://192.168.111.130:4321/dashboard/
📋 Leave/Cuti:          http://192.168.111.130:4321/leave/
```

### **Default Credentials**

```
Username: admin
Password: admin123
```

---

## 📦 **Services Status**

| Service | Port | Status | Process |
|---------|------|--------|---------|
| Django Web Server | 4321 | ✅ Running | management-django |
| Celery Worker | - | ✅ Running | management-celery-worker |
| Celery Beat | - | ✅ Running | management-celery-beat |
| PostgreSQL | 5432 | ✅ Running | (Auto-start) |
| Redis | 6379 | ✅ Running | (Auto-start) |
| Google Calendar API | HTTPS | ✅ Connected | External |

---

## 🔧 **Environment Variables (.env) - Current Values**

```ini
# DJANGO
DJANGO_ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your-super-secret-key-change-this-in-production-min-50-chars-12345678

# DATABASE - PostgreSQL 16
DB_ENGINE=django.db.backends.postgresql
DB_NAME=proyek_management_job
DB_USER=postgres
DB_PASSWORD=PostgresAdmin2026!
DB_HOST=localhost
DB_PORT=5432

# CACHE & CELERY - Redis
REDIS_URL=redis://localhost:6379/1
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_TIMEZONE=Asia/Jakarta

# STORAGE
MEDIA_ROOT=C:/data/management-job/media
STATIC_ROOT=C:/data/management-job/static
LOG_DIR=C:/logs/management-job

# GOOGLE CALENDAR
GOOGLE_CALENDAR_CREDENTIALS_FILE=config/credentials/google-calendar-sa.json
GOOGLE_CALENDAR_ID=ges3ra8851qk05jqlsfgjct3h4@group.calendar.google.com

# FONTTE WHATSAPP
FONTTE_API_ENABLED=true
FONTTE_API_BASE_URL=https://api.fontte.com/v1
```

---

## 🚀 **PM2 Configuration - ecosystem.config.js**

```javascript
{
  apps: [
    {
      name: "management-django",
      cwd: "C:\\repos\\proyek_manajemen_job",
      script: "venv\\Scripts\\pythonw.exe",
      args: "manage.py runserver 0.0.0.0:4321",
      autorestart: true,
      restart_delay: 5000,
      max_memory_restart: "500M",
      output: "C:/logs/management-job/django.log",
      error: "C:/logs/management-job/django-error.log"
    },
    {
      name: "management-celery-worker",
      cwd: "C:\\repos\\proyek_manajemen_job",
      script: "venv\\Scripts\\pythonw.exe",
      args: "-m celery -A config worker -l info",
      autorestart: true,
      restart_delay: 5000,
      max_memory_restart: "500M",
      output: "C:/logs/management-job/celery-worker.log",
      error: "C:/logs/management-job/celery-worker-error.log"
    },
    {
      name: "management-celery-beat",
      cwd: "C:\\repos\\proyek_manajemen_job",
      script: "venv\\Scripts\\pythonw.exe",
      args: "-m celery -A config beat -l info",
      autorestart: true,
      restart_delay: 5000,
      max_memory_restart: "300M",
      output: "C:/logs/management-job/celery-beat.log",
      error: "C:/logs/management-job/celery-beat-error.log"
    }
  ]
}
```

---

## 📁 **Directory Structure**

```
C:\repos\proyek_manajemen_job\
├── config/
│   ├── settings.py (Django configuration)
│   ├── celery.py (Celery setup)
│   ├── urls.py
│   ├── wsgi.py
│   └── credentials/
│       └── google-calendar-sa.json (Service account)
├── core/
│   ├── models.py (Database models)
│   ├── views.py (View logic)
│   ├── forms.py
│   └── management/commands/
├── meetings/
│   ├── models.py
│   ├── tasks.py (Celery tasks)
│   └── management/commands/
├── preventive_jobs/
├── inventory/
├── templates/ (HTML templates)
├── static/ (CSS, JS, images)
├── manage.py
├── requirements.txt
├── ecosystem.config.js (PM2 config) ✅ UPDATED
├── .env (Environment config) ✅ UPDATED
├── venv/ (Python virtual environment)
└── backups/
    └── backup_manajemen_pekerjaan_db_2026-05-26_020017.sql

C:\logs\management-job\ (Log directory)
├── django.log
├── django-error.log
├── celery-worker.log
├── celery-worker-error.log
├── celery-beat.log
└── celery-beat-error.log

C:\data\management-job\
├── media/ (User uploads)
└── static/ (Collected static files)
```

---

## 💾 **Database Information**

### **PostgreSQL Configuration**

```
Host:       localhost
Port:       5432
Database:   proyek_management_job
User:       postgres
Password:   PostgresAdmin2026!
Version:    PostgreSQL 16
```

### **Database Tables** (Key ones)

| Table | Records | Purpose |
|-------|---------|---------|
| core_leaveevent | 400 | Leave/Cuti events from Google Calendar |
| core_job | 10,265 | Maintenance jobs |
| core_karyawan | 239 | Employee records |
| core_customuser | 46 | User accounts |
| core_project | 51 | Projects |
| meetings_meeting | - | Meeting records |
| meetings_meetingreminder | - | WhatsApp reminders queue |

---

## 🔑 **Key Features & Integration**

### **✅ Google Calendar Integration**

```
Departemen Calendar IDs:
├── Teknik: ges3ra8851qk05jqlsfgjct3h4@group.calendar.google.com
└── Operasional: cf892c70f9aa44239432adfa5229038fd7fe6e6a5d048a38c630cc5d67b706c2@group.calendar.google.com

Status: ✅ Connected & Syncing
Data: 400 leave events imported
```

### **✅ Celery Task Scheduling**

```
Celery Beat Schedule:
├── Meeting Reminders: Every 5 minutes
│   └── Command: send_meeting_reminders
├── Job Sync: Configurable
└── Calendar Sync: On-demand

Broker: Redis (localhost:6379/0)
Result Backend: Redis (localhost:6379/0)
```

### **✅ WhatsApp Notifications (Fontte)**

```
Status: ✅ Configured
API: https://api.fontte.com/v1
Used for: Meeting reminder notifications
```

---

## 🎛️ **PM2 Common Commands**

```powershell
# Management
pm2 start ecosystem.config.js          # Start all apps
pm2 stop all                           # Stop all apps
pm2 restart all                        # Restart all apps
pm2 delete all                         # Delete all apps

# Monitoring
pm2 status                             # Check status
pm2 logs                               # View all logs
pm2 logs management-django             # View specific app logs
pm2 monit                              # Real-time monitoring

# Individual Service
pm2 start management-django
pm2 restart management-celery-worker
pm2 stop management-celery-beat
pm2 delete management-celery-worker

# Saving Configuration
pm2 save                               # Save current config
pm2 startup                            # Auto-start on system boot
```

---

## 📊 **System Performance**

### **Resource Usage (Baseline)**

```
Django:           80-150 MB
Celery Worker:    150-250 MB
Celery Beat:      60-100 MB
PostgreSQL:       300-500 MB
Redis:            50-100 MB
────────────────────────
Total:            700-1000 MB
```

### **Uptime & Reliability**

```
Auto-restart:     ✅ Enabled (5s delay)
Memory limit:     ✅ Set (300-500MB per app)
Log rotation:     ✅ Enabled
Backup schedule:  ✅ Daily recommended
```

---

## 🔐 **Security Configuration**

| Setting | Current | Recommended (Prod) |
|---------|---------|-------------------|
| DEBUG | True | False |
| SECURE_SSL_REDIRECT | False | True |
| SESSION_COOKIE_SECURE | False | True |
| CSRF_COOKIE_SECURE | False | True |
| ALLOWED_HOSTS | localhost,127.0.0.1 | yourdomain.com |

---

## 📝 **Recent Changes (This Session)**

| Date | Component | Change | Status |
|------|-----------|--------|--------|
| 2026-05-30 | ecosystem.config.js | Port 8000→4321, logs→C:/logs/ | ✅ Done |
| 2026-05-27 | .env | GOOGLE_CALENDAR_ID updated | ✅ Done |
| 2026-05-27 | core/views.py | Fixed admin leave event filter | ✅ Done |
| 2026-05-26 | Database | Restored with 400 events | ✅ Done |
| 2026-05-26 | Firewall | Port 4321 rule added | ✅ Done |

---

## ✅ **Health Check Checklist**

Run these regularly:

```powershell
# Check services running
pm2 status

# Test web access
(Invoke-WebRequest -Uri "http://127.0.0.1:4321/" -UseBasicParsing).StatusCode

# Test database
psql -U postgres -d proyek_management_job -c "SELECT COUNT(*) FROM core_job;"

# Test Redis
redis-cli -p 6379 ping

# Check logs for errors
pm2 logs --err

# Check disk space
Get-Volume

# Check memory usage
Get-Process | Where-Object {$_.ProcessName -eq "python"} | Select-Object ProcessName, WorkingSet
```

---

## 📞 **Quick Troubleshooting**

### **"Port 4321 already in use"**
```powershell
netstat -ano | findstr :4321
taskkill /PID <PID> /F
pm2 restart management-django
```

### **"Database connection failed"**
```powershell
# Verify PostgreSQL running
Get-Service PostgreSQL*
# Verify credentials in .env
psql -U postgres -d proyek_management_job -c "\q"
```

### **"Celery tasks not running"**
```powershell
pm2 restart management-celery-worker
# Check Redis
redis-cli DBSIZE
```

### **"High memory usage"**
```powershell
pm2 status  # Check which app
pm2 restart management-django  # Or whichever is high
```

---

**For detailed setup instructions, refer to: SETUP_PM2_DOKUMENTASI.md**

---

Version: 1.0 | Updated: 30 Mei 2026
