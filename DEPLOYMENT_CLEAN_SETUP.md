# ============================================================================
# DATABASE MIGRATION & DEPLOYMENT GUIDE FOR WINDOWS SERVER 2022
# ============================================================================
# Project: Proyek Manajemen Job
# Target: Windows Server 2022 Standard Desktop Experience
# Date: May 18, 2026

---

## 📋 PRE-DEPLOYMENT CHECKLIST

### System Requirements
- [ ] Python 3.11 installed and in PATH
- [ ] PostgreSQL 16 installed and service running
- [ ] Redis service running (for Celery)
- [ ] Folder structure created:
  - `C:\repos\proyek_manajemen_job` (Application)
  - `C:\data\management-job\media` (Uploaded files)
  - `C:\data\management-job\static` (Static assets)
  - `C:\logs\management-job` (Log files)
  - `C:\backup\management-job` (Database backups)
- [ ] Git installed for deployment automation

### Database Verification
- [ ] PostgreSQL 16 service running
- [ ] Database `proyek_management_job` exists
- [ ] Database user `manajemen_app_user` exists with proper permissions
- [ ] Database backup `backup_*.sql` restored
- [ ] Database connection verified locally

---

## 🚀 DEPLOYMENT STEPS

### STEP 1: Prepare Environment

```powershell
# 1.1 Navigate to project folder
cd C:\repos\proyek_manajemen_job

# 1.2 Create and activate Python virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 1.3 Verify Python version
python --version  # Should be Python 3.11.x

# 1.4 Upgrade pip, setuptools, wheel
python -m pip install --upgrade pip setuptools wheel
```

### STEP 2: Install Dependencies

```powershell
# 2.1 Install requirements
pip install -r requirements.txt

# 2.2 Verify critical packages installed
pip show Django psycopg2-binary celery redis gunicorn weasyprint
```

### STEP 3: Configure Environment

```powershell
# 3.1 Copy and edit .env file
Copy-Item .env.example .env

# 3.2 Edit .env with your values (use Notepad or VSCode)
# IMPORTANT SETTINGS TO CHANGE:
#   - DEBUG=False (production)
#   - SECRET_KEY (generate new one: python manage.py shell)
#   - DB_PASSWORD (your PostgreSQL password)
#   - DJANGO_PUBLIC_URL (your domain or IP)
#   - FONTTE_API_TOKEN (if using WhatsApp)
#   - GOOGLE_CALENDAR_CREDENTIALS_FILE (if using calendar)
#
notepad .env
```

### STEP 4: Generate Secret Key

```powershell
# Generate new SECRET_KEY for production
python manage.py shell

# Then in Python shell:
# >>> from django.core.management.utils import get_random_secret_key
# >>> print(get_random_secret_key())
# Copy the output and paste into .env
# >>> exit()
```

### STEP 5: Prepare Database

```powershell
# 5.1 Run migrations
python manage.py migrate

# 5.2 Review migration plan (if needed)
python manage.py migrate --plan

# 5.3 Verify migrations applied
python manage.py showmigrations core

# 5.4 Create superuser (if not exists from restored database)
python manage.py createsuperuser
```

### STEP 6: Collect Static Files

```powershell
# 6.1 Collect all static files to STATIC_ROOT
python manage.py collectstatic --noinput --clear

# 6.2 Verify static files collected
dir C:\data\management-job\static

# Expected: css, js, admin, bootstrap, etc.
```

### STEP 7: Database Backup

```powershell
# 7.1 Create backup before going live
python manage.py dumpdata > C:\backup\management-job\backup_pre-deploy_$(Get-Date -Format 'yyyyMMdd_HHmmss').json

# 7.2 Verify backup size (should be > 1MB)
dir C:\backup\management-job\backup_*.json

# 7.3 Keep backup for at least 1 week
```

### STEP 8: Test Application

```powershell
# 8.1 Run tests
python manage.py test --verbosity=2

# 8.2 Run development server for local test
python manage.py runserver 0.0.0.0:8000

# 8.3 Open browser: http://localhost:8000
# 8.4 Login with superuser credentials
# 8.5 Verify:
#   - Dashboard loads
#   - Database queries work
#   - Static files load (CSS/JS)
#   - Media upload works
#   - Admin interface accessible
```

### STEP 9: Setup Gunicorn WSGI Server

```powershell
# 9.1 Create Gunicorn startup script
# File: C:\repos\proyek_manajemen_job\run_gunicorn.bat

@echo off
cd C:\repos\proyek_manajemen_job
call venv\Scripts\activate.bat
gunicorn config.wsgi:application --workers 4 --bind 127.0.0.1:8001 --timeout 60 --access-logfile C:\logs\management-job\gunicorn_access.log --error-logfile C:\logs\management-job\gunicorn_error.log

# 9.2 Test Gunicorn
python -m gunicorn config.wsgi:application --workers 4 --bind 0.0.0.0:8001

# 9.3 Verify: http://localhost:8001 should work
```

### STEP 10: Setup Celery Beat Scheduler

```powershell
# 10.1 Create Celery Beat startup script
# File: C:\repos\proyek_manajemen_job\run_celery_beat.bat

@echo off
cd C:\repos\proyek_manajemen_job
call venv\Scripts\activate.bat
celery -A config worker -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

# 10.2 Or use Windows Task Scheduler (see STEP 11)
```

### STEP 11: Setup Celery Worker

```powershell
# 11.1 Create Celery worker startup script
# File: C:\repos\proyek_manajemen_job\run_celery_worker.bat

@echo off
cd C:\repos\proyek_manajemen_job
call venv\Scripts\activate.bat
celery -A config worker -l info --concurrency 4

# 11.2 Test Celery Worker
# In another terminal:
# celery -A config worker -l info
```

### STEP 12: Setup Windows Services / PM2

**Option A: Using PM2 (Recommended for cluster deployments)**

```powershell
# 12.1 Install PM2 globally (requires Node.js)
npm install -g pm2

# 12.2 Create ecosystem.config.js
# File: C:\repos\proyek_manajemen_job\ecosystem.config.js
module.exports = {
  apps: [
    {
      name: 'gunicorn',
      script: 'run_gunicorn.bat',
      cwd: 'C:\\repos\\proyek_manajemen_job',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production'
      }
    },
    {
      name: 'celery-worker',
      script: 'run_celery_worker.bat',
      cwd: 'C:\\repos\\proyek_manajemen_job',
      instances: 1,
      autorestart: true,
      watch: false
    },
    {
      name: 'celery-beat',
      script: 'run_celery_beat.bat',
      cwd: 'C:\\repos\\proyek_manajemen_job',
      instances: 1,
      autorestart: true,
      watch: false
    }
  ]
};

# 12.3 Start services
pm2 start ecosystem.config.js

# 12.4 Save PM2 configuration to auto-start on reboot
pm2 save
pm2 startup

# 12.5 Monitor services
pm2 monit
pm2 logs
```

**Option B: Using Windows Services (Native)**

```powershell
# See documentation in: panduan/WINDOWS_SERVICE_SETUP.md
```

### STEP 13: Setup Caddy Reverse Proxy

```plaintext
# File: C:\caddy\Caddyfile

management-job.local:80 {
    reverse_proxy 127.0.0.1:8001 {
        # Preserve host header for Django
        header_up X-Forwarded-For {http.request.remote.host}
        header_up X-Forwarded-Proto {http.request.proto}
        header_up X-Forwarded-Host {http.request.host}
    }
}

# Uncomment for HTTPS (requires domain):
# management-job.yourdomain.com {
#     reverse_proxy 127.0.0.1:8001 {
#         header_up X-Forwarded-For {http.request.remote.host}
#         header_up X-Forwarded-Proto {http.request.proto}
#         header_up X-Forwarded-Host {http.request.host}
#     }
# }
```

Start Caddy:
```powershell
cd C:\caddy
.\caddy.exe run

# Or install as Windows Service for auto-start
.\caddy.exe.caddyfile windows-service install
```

### STEP 14: Database Maintenance

```powershell
# 14.1 Regular backups (daily via Task Scheduler)
# Command: python manage.py dumpdata > backup_$(date +\%Y\%m\%d_\%H\%M\%S).json

# 14.2 Database optimization (monthly)
python manage.py shell << EOF
from django.db import connection
cursor = connection.cursor()
cursor.execute("VACUUM ANALYZE;")
print("Database optimized!")
EOF

# 14.3 Log cleanup (weekly)
Get-ChildItem C:\logs\management-job\*.log | 
  Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | 
  Remove-Item
```

---

## 🔍 TROUBLESHOOTING

### Issue: Database Connection Refused
```powershell
# Check PostgreSQL service
Get-Service postgresql-x64-*  # Should show Running

# Verify connection string in .env
# Restart PostgreSQL
Stop-Service postgresql-x64-*
Start-Service postgresql-x64-*
```

### Issue: Static Files Not Loading
```powershell
# Recollect static files
python manage.py collectstatic --clear --noinput

# Verify static files location
dir C:\data\management-job\static
```

### Issue: Celery Tasks Not Running
```powershell
# Check Redis
redis-cli ping  # Should reply PONG

# Check Celery status
celery -A config inspect active

# Check Celery worker logs
celery -A config worker -l debug
```

### Issue: 503 Service Unavailable Behind Caddy
```powershell
# Check Gunicorn is running
Get-Process gunicorn

# Check Gunicorn logs
cat C:\logs\management-job\gunicorn_error.log

# Verify Django settings
python manage.py check
```

---

## 📊 MONITORING & HEALTH CHECKS

```powershell
# Check Django health
curl http://localhost:8000/admin/  # Should return 200

# Check Celery tasks
celery -A config inspect active
celery -A config inspect registered

# Check database connections
python manage.py shell << EOF
from django.db import connection
print(f"Database: {connection.settings_dict['NAME']}")
print(f"User: {connection.settings_dict['USER']}")
cursor = connection.cursor()
cursor.execute("SELECT version();")
print(cursor.fetchone())
EOF

# Monitor processes
Get-Process | Where-Object {$_.ProcessName -match 'python|redis|postgres'} | Select-Object ProcessName, CPU, Memory
```

---

## 🔐 SECURITY CHECKLIST

- [ ] DEBUG=False in production
- [ ] SECRET_KEY is unique and strong
- [ ] Database password is strong (25+ chars)
- [ ] HTTPS enabled in Caddy (if public)
- [ ] CSRF_TRUSTED_ORIGINS configured correctly
- [ ] ALLOWED_HOSTS doesn't contain wildcards
- [ ] Google credentials file has restricted permissions
- [ ] Fontte API token in secure storage
- [ ] Regular database backups enabled
- [ ] Log files rotated and old logs deleted
- [ ] File permissions set correctly (no world-readable)

---

## 📝 ENVIRONMENT VARIABLES REFERENCE

See `.env.example` for all available variables and their descriptions.

Key production variables:
- `DJANGO_ENVIRONMENT=production`
- `DEBUG=False`
- `SECRET_KEY=<generate new>`
- `DB_PASSWORD=<strong password>`
- `ALLOWED_HOSTS=<your domains>`
- `DJANGO_PUBLIC_URL=<your public URL>`

---

## 🆘 ROLLBACK PROCEDURE

If deployment fails:

```powershell
# 1. Stop all services
pm2 stop all

# 2. Restore from backup
python manage.py loaddata backup_pre-deploy_*.json

# 3. Restart services
pm2 start all

# 4. Verify
curl http://localhost:8000/admin/
```

---

## 📞 SUPPORT

For issues or questions:
1. Check logs in `C:\logs\management-job\`
2. Run `python manage.py check` to diagnose
3. Test in local development first
4. Review settings in `.env`

