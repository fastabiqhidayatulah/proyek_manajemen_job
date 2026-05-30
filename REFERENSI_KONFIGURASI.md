# 📄 REFERENSI FILE KONFIGURASI AKTIF

**Status:** ✅ Current & Working  
**Last Updated:** 30 Mei 2026

---

## 📋 **.env File (Complete)**

**Location:** `C:\repos\proyek_manajemen_job\.env`

```env
# ============================================================================
# DJANGO CORE SETTINGS
# ============================================================================
DJANGO_ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your-super-secret-key-change-this-in-production-min-50-chars-12345678

# SSL/HTTPS Settings (disable for development)
SECURE_SSL_REDIRECT=False
CSRF_COOKIE_SECURE=False
SESSION_COOKIE_SECURE=False
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False

# Allowed hosts
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.100

# ============================================================================
# DATABASE CONFIGURATION
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
# CACHING CONFIGURATION
# ============================================================================
CACHE_BACKEND=django.core.cache.backends.locmem.LocMemCache
REDIS_URL=redis://localhost:6379/1
CACHE_TIMEOUT=3600

# Optional cache/log directories
LOG_DIR=C:/logs/management-job
LOG_LEVEL=INFO
DJANGO_LOG_LEVEL=INFO
CELERY_LOG_LEVEL=INFO

# ============================================================================
# CELERY & TASK QUEUE CONFIGURATION
# ============================================================================
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_TIMEZONE=Asia/Jakarta

# ============================================================================
# STATIC & MEDIA FILES CONFIGURATION
# ============================================================================
MEDIA_ROOT=C:/data/management-job/media
MEDIA_URL=/media/
STATIC_ROOT=C:/data/management-job/static
STATIC_URL=/static/

# ============================================================================
# GOOGLE CALENDAR API INTEGRATION
# ============================================================================
GOOGLE_CALENDAR_CREDENTIALS_FILE=config/credentials/google-calendar-sa.json
GOOGLE_CALENDAR_ID=ges3ra8851qk05jqlsfgjct3h4@group.calendar.google.com

# ============================================================================
# WHATSAPP INTEGRATION - FONTTE API
# ============================================================================
FONTTE_API_TOKEN=your-fontte-api-token-here
FONTTE_API_BASE_URL=https://api.fontte.com/v1
FONTTE_API_ENABLED=true

# ============================================================================
# PUBLIC URL CONFIGURATION
# ============================================================================
DJANGO_PUBLIC_URL=http://localhost:8000

# ============================================================================
# CSRF & CORS CONFIGURATION
# ============================================================================
CSRF_TRUSTED_ORIGINS=http://localhost:8000,https://yourdomain.com
CSRF_COOKIE_SECURE=False
CSRF_COOKIE_HTTPONLY=false
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False
X_FRAME_OPTIONS=DENY

# ============================================================================
# LOGGING & EMAIL CONFIGURATION
# ============================================================================
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
```

**⚠️ IMPORTANT NOTES:**
- `DB_PASSWORD=PostgresAdmin2026!` - Change in production
- `SECRET_KEY` - Generate new in production
- `GOOGLE_CALENDAR_ID=ges3ra8851qk05jqlsfgjct3h4@group.calendar.google.com` - Teknik departemen calendar
- `FONTTE_API_TOKEN` - Add your actual token when configured
- `DJANGO_PUBLIC_URL` - Update for production domain

---

## ⚙️ **ecosystem.config.js (Complete)**

**Location:** `C:\repos\proyek_manajemen_job\ecosystem.config.js`

```javascript
module.exports = {
  apps: [
    // ================================================================
    // DJANGO WEB SERVER - Port 4321
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
    // CELERY WORKER - Background Task Processing
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
    // CELERY BEAT - Task Scheduler (Meeting Reminders, etc)
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

**Key Configuration Explained:**

| Parameter | Value | Explanation |
|-----------|-------|-------------|
| **name** | "management-*" | Service identifier |
| **cwd** | C:\\repos\\... | Working directory |
| **script** | pythonw.exe | Python executable (w = no console) |
| **args** | manage.py runserver ... | Command to run |
| **autorestart** | true | Auto-restart on crash |
| **restart_delay** | 5000 | 5 second delay before restart |
| **max_memory_restart** | 500M / 300M | Restart if exceeds memory |
| **output** | C:/logs/... | Stdout log file |
| **error** | C:/logs/... | Stderr log file |

---

## 🔄 **Django Settings Snippet (config/settings.py)**

```python
# ============================================================================
# ALLOWED HOSTS - Auto-includes wildcard in DEBUG mode
# ============================================================================
DEBUG = os.environ.get('DEBUG', 'True').lower() in ['true', '1', 'yes']
ALLOWED_HOSTS_STR = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',')]

if DEBUG:
    ALLOWED_HOSTS.extend(['*', '127.0.0.1', 'localhost'])
    ALLOWED_HOSTS = list(dict.fromkeys(ALLOWED_HOSTS))

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOG_DIR = os.environ.get('LOG_DIR', 'logs')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
DJANGO_LOG_LEVEL = os.environ.get('DJANGO_LOG_LEVEL', 'INFO').upper()
CELERY_LOG_LEVEL = os.environ.get('CELERY_LOG_LEVEL', 'INFO').upper()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': DJANGO_LOG_LEVEL,
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'django.log'),
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'errors.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file'],
            'level': DJANGO_LOG_LEVEL,
            'propagate': False,
        },
        'celery': {
            'handlers': ['file'],
            'level': CELERY_LOG_LEVEL,
            'propagate': False,
        },
    },
}

# ============================================================================
# GOOGLE CALENDAR SETTINGS
# ============================================================================
GOOGLE_CALENDAR_CREDENTIALS_FILE = os.environ.get(
    'GOOGLE_CALENDAR_CREDENTIALS_FILE',
    'config/credentials/google-calendar-sa.json'
)
GOOGLE_CALENDAR_ID = os.environ.get(
    'GOOGLE_CALENDAR_ID',
    'your-calendar-id@group.calendar.google.com'
)

# ============================================================================
# CELERY CONFIGURATION
# ============================================================================
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_TIMEZONE = os.environ.get('CELERY_TIMEZONE', 'Asia/Jakarta')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_POOL_LIMIT = 1
```

---

## 🗂️ **Celery Beat Schedule (config/celery.py)**

```python
from celery.schedules import crontab

beat_schedule = {
    'send-meeting-reminders': {
        'task': 'meetings.tasks.send_meeting_reminders_task',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
        'options': {'queue': 'celery'}
    },
}

app.conf.beat_schedule = beat_schedule
```

**Scheduled Tasks:**
- **Meeting Reminders**: Every 5 minutes via Fonnte WhatsApp API
- Add more schedules as needed in `config/celery.py`

---

## 📊 **Database Models - Key Tables**

### **Leave Events (Google Calendar Sync)**
```
Table: core_leaveevent
Columns:
  - id (PK)
  - google_event_id (External ID)
  - karyawan (FK to Karyawan)
  - departemen (FK to Departemen)
  - tipe_leave (Cuti/Ijin)
  - tanggal (Leave date)
  - deskripsi (Description)
  - created_at (Timestamp)
  - created_by (FK to CustomUser)

Records: 400 (as of 2026-05-26)
```

### **Users (Access Control)**
```
Table: core_customuser
Columns:
  - id (PK)
  - username
  - email
  - departemen (FK - can be NULL for admin)
  - is_staff, is_superuser
  - password (hashed)

Records: 46 users
```

### **Jobs (Preventive Maintenance)**
```
Table: core_job
Columns:
  - id (PK)
  - nama_pekerjaan (Job name)
  - kategori (Category)
  - priority (Priority level)
  - status (Status)
  - assigned_to (FK to Karyawan)
  - created_at, due_date

Records: 10,265 jobs
```

---

## 🔐 **Credentials & Secrets**

### **PostgreSQL**
```
Username: postgres
Password: PostgresAdmin2026!
Host: localhost:5432
Database: proyek_management_job
```

### **Google Calendar Service Account**
```
Location: config/credentials/google-calendar-sa.json
Project: cuti-gcal
Service Account: django-calendar-app@cuti-gcal.iam.gserviceaccount.com
Type: Service Account (JSON key)
Permissions: Google Calendar API read/write
```

### **Admin User**
```
Username: admin
Password: admin123
Email: (set via Django admin)
Permissions: Superuser (all access)
```

---

## 📌 **Important Notes for Future Maintenance**

1. **Never commit .env to Git** - Contains passwords
2. **Backup database weekly** - Use `pg_dump`
3. **Monitor logs daily** - Check `C:/logs/management-job/`
4. **Update Django & packages quarterly** - Keep security patched
5. **Test backups monthly** - Verify restoration works
6. **Rotate secrets annually** - Change SECRET_KEY and passwords

---

**Reference Document Version:** 1.0  
**Last Updated:** 30 Mei 2026  
**For Issues:** See SETUP_PM2_DOKUMENTASI.md or QUICK_START.md
