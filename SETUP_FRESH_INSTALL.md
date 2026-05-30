# 🚀 SETUP FRESH INSTALL - Django + PM2 di Server Baru

**Untuk menjalankan aplikasi di server lain setelah clone dari GitHub**

---

## 📋 **Prerequisites**

Pastikan sudah install di server baru:

```powershell
✅ Windows Server 2022+ atau Windows 10/11
✅ Python 3.11+ 
✅ PostgreSQL 16
✅ Redis 5.0.1
✅ Node.js 18+ (untuk PM2)
✅ Git (untuk clone)
```

---

## 🎯 **Step-by-Step Setup**

### **Step 1: Clone Repository**

```powershell
cd C:\repos
git clone https://github.com/fastabiqhidayatulah/proyek_manajemen_job.git
cd proyek_manajemen_job
```

### **Step 2: Create & Activate Virtual Environment**

```powershell
# Create venv
python -m venv venv

# Activate
.\venv\Scripts\Activate.ps1

# Verify
python --version
pip --version
```

### **Step 3: Install Python Dependencies**

```powershell
# Make sure venv is activated first
pip install -r requirements.txt

# Verify Django installed
python -c "import django; print(django.__version__)"
# Expected: 5.2.8
```

### **Step 4: Setup Database (PostgreSQL)**

```powershell
# Open PostgreSQL shell
psql -U postgres

# Create database
CREATE DATABASE proyek_management_job;

# Create user (if needed)
CREATE USER postgres_app WITH PASSWORD 'secure_password_123';
ALTER ROLE postgres_app WITH CREATEDB;

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE proyek_management_job TO postgres_app;

# Exit
\q
```

**Atau gunakan commands ini:**

```powershell
# Create database
createdb -U postgres proyek_management_job

# Verify
psql -U postgres -l | findstr proyek_management_job
```

### **Step 5: Create .env File**

```powershell
# Copy template
cp .env.example .env

# Edit dengan nilai yang sesuai
notepad .env
```

**Minimal values needed:**

```env
# Django
DJANGO_ENVIRONMENT=development
DEBUG=True
SECRET_KEY=django-insecure-generate-new-key-min-50-chars

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=proyek_management_job
DB_USER=postgres
DB_PASSWORD=your_postgres_password_here
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/1
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Google Calendar (update dengan nilai actual)
GOOGLE_CALENDAR_CREDENTIALS_FILE=config/credentials/google-calendar-sa.json
GOOGLE_CALENDAR_ID=ges3ra8851qk05jqlsfgjct3h4@group.calendar.google.com

# Storage paths
MEDIA_ROOT=C:/data/management-job/media
STATIC_ROOT=C:/data/management-job/static
LOG_DIR=C:/logs/management-job
```

### **Step 6: Create Required Directories**

```powershell
# Media directory
mkdir C:\data\management-job\media
mkdir C:\data\management-job\static

# Logs directory
mkdir C:\logs\management-job

# Credentials directory
mkdir config\credentials
```

### **Step 7: Setup Google Calendar Credentials**

```powershell
# Download dari Google Cloud Console:
# 1. Go to: https://console.cloud.google.com/
# 2. Select project (atau create baru: cuti-gcal)
# 3. Go to "Credentials" → "Create Service Account"
# 4. Download JSON key
# 5. Save to: config/credentials/google-calendar-sa.json

# Verify file ada
Test-Path config\credentials\google-calendar-sa.json
# Expected: True
```

### **Step 8: Run Django Migrations**

```powershell
# Activate venv if not already
.\venv\Scripts\Activate.ps1

# Run migrations
python manage.py migrate

# Verify database created
psql -U postgres -d proyek_management_job -c "SELECT COUNT(*) FROM core_job;"
```

### **Step 9: Create Superuser (Admin)**

```powershell
python manage.py createsuperuser

# Prompt akan minta:
# Username: admin
# Email: admin@example.com
# Password: secure_password_123
# Password (again): secure_password_123
```

### **Step 10: Collect Static Files**

```powershell
python manage.py collectstatic --noinput

# Verify
Test-Path C:\data\management-job\static\admin
# Expected: True
```

### **Step 11: Install PM2 (Global)**

```powershell
# If not already installed
npm install -g pm2

# Verify
pm2 --version
```

### **Step 12: Start Services with PM2**

```powershell
# Go to project directory
cd C:\repos\proyek_manajemen_job

# Start all apps from ecosystem.config.js
pm2 start ecosystem.config.js

# Save PM2 config to auto-start on reboot
pm2 save

# Optional: Setup Windows startup
pm2 startup windows-startup --user Administrator
```

### **Step 13: Verify All Services**

```powershell
# Check status
pm2 status

# Expected output:
# ✅ management-django       online
# ✅ management-celery-worker online
# ✅ management-celery-beat   online

# Check logs
pm2 logs

# Test web server
(Invoke-WebRequest -Uri "http://127.0.0.1:4321/" -UseBasicParsing).StatusCode
# Expected: 302 or 200
```

### **Step 14: Setup Windows Firewall (Optional)**

```powershell
# Allow port 4321 for LAN access
New-NetFirewallRule -DisplayName "Django Port 4321" `
  -Direction Inbound -Action Allow -Protocol TCP -LocalPort 4321

# Verify
Get-NetFirewallRule -DisplayName "*4321*" | Select-Object DisplayName, Enabled
```

### **Step 15: Access Application**

```
🌐 Web App:     http://127.0.0.1:4321
🌐 From LAN:    http://<SERVER_IP>:4321
🔑 Admin Panel: http://127.0.0.1:4321/admin/

Username: admin
Password: (yang Anda set di Step 9)
```

---

## ✅ **Post-Setup Verification Checklist**

Run these commands untuk verify semuanya:

```powershell
# 1. Check PM2 services
pm2 status
# Expected: All 3 apps online

# 2. Test web access
(Invoke-WebRequest -Uri "http://127.0.0.1:4321/").StatusCode
# Expected: 302 or 200

# 3. Test database
psql -U postgres -d proyek_management_job -c "SELECT COUNT(*) FROM core_job;"
# Expected: return job count

# 4. Test Redis
redis-cli ping
# Expected: PONG

# 5. Test Celery
python manage.py shell
>>> from celery.app.control import Inspect
>>> i = Inspect()
>>> print(i.active())
# Expected: Dictionary with active tasks

# 6. Check logs for errors
pm2 logs --err
# Expected: Minimal to no errors
```

---

## 🔄 **Database Restore (If Using Backup)**

Jika punya database backup:

```powershell
# Restore dari backup file
psql -U postgres -d proyek_management_job < backups/backup_2026-05-26.sql

# Verify
psql -U postgres -d proyek_management_job -c "SELECT COUNT(*) FROM core_leaveevent;"
# Expected: 400 (atau sesuai backup)
```

---

## ⚙️ **Configuration Changes for Production**

Sebelum go-live, update `.env`:

```env
# Security
DJANGO_ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<generate-new-secure-key>

# SSL
SECURE_SSL_REDIRECT=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000

# Domain
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DJANGO_PUBLIC_URL=https://yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com

# Database (use strong password!)
DB_PASSWORD=<strong-production-password>
```

---

## 🛠️ **Troubleshooting Fresh Install**

### **"ModuleNotFoundError: No module named 'django'"**
```powershell
# Make sure venv is activated
.\venv\Scripts\Activate.ps1

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### **"psql: command not found"**
```powershell
# Add PostgreSQL to PATH
$env:PATH += ";C:\Program Files\PostgreSQL\16\bin"

# Or in .env add psql path
# Verify
psql --version
```

### **"Port 4321 already in use"**
```powershell
# Find what's using port
netstat -ano | findstr :4321

# Kill process
taskkill /PID <number> /F

# Change port in ecosystem.config.js if needed
```

### **"Redis connection refused"**
```powershell
# Check Redis running
Get-Service Redis | Select-Object Status

# Start if needed
Start-Service Redis

# Verify
redis-cli ping
# Expected: PONG
```

### **"Google Calendar credentials error"**
```powershell
# Verify file exists
Test-Path config\credentials\google-calendar-sa.json

# Check permissions
Get-Item config\credentials\google-calendar-sa.json | Select-Object FullName

# Try test in Django shell
python manage.py shell
>>> import json
>>> with open('config/credentials/google-calendar-sa.json') as f:
...     creds = json.load(f)
...     print(creds['project_id'])
# Expected: cuti-gcal
```

---

## 📊 **File Structure After Setup**

```
C:\repos\proyek_manajemen_job\
├── venv/                              ← Virtual environment
├── config/
│   ├── credentials/
│   │   └── google-calendar-sa.json   ← Service account (dari Google)
│   ├── settings.py                   ← Django config
│   └── celery.py                     ← Celery config
├── core/                              ← Main app
├── meetings/                          ← Meetings module
├── preventive_jobs/                   ← Jobs module
├── inventory/                         ← Inventory module
├── templates/                         ← HTML templates
├── static/                            ← CSS, JS, images
├── .env                              ← Environment variables (CREATE!)
├── requirements.txt                  ← Python dependencies
├── ecosystem.config.js               ← PM2 configuration
├── manage.py                         ← Django management
└── README.md, documentation files

C:\data\management-job\
├── media/                            ← User uploads
└── static/                           ← Collected static files

C:\logs\management-job\
├── django.log                        ← Web server logs
├── django-error.log
├── celery-worker.log                 ← Background task logs
├── celery-worker-error.log
├── celery-beat.log                   ← Scheduler logs
└── celery-beat-error.log
```

---

## 🚀 **Quick Start After Initial Setup**

Next time Anda start server:

```powershell
cd C:\repos\proyek_manajemen_job

# Check services running
pm2 status

# If not running
pm2 start ecosystem.config.js

# View logs
pm2 logs

# Access
http://127.0.0.1:4321
```

---

## 📚 **Reference Documents**

Setelah setup selesai, lihat:

- **QUICK_START.md** - Daily operations
- **KONFIGURASI_RINGKAS.md** - Configuration reference
- **SETUP_PM2_DOKUMENTASI.md** - Detailed guide
- **DOKUMENTASI_INDEX.md** - All documentation

---

## 💡 **Tips**

1. **Save .env securely** - Don't commit to Git
2. **Backup database regularly** - Use `pg_dump`
3. **Monitor logs daily** - Check for errors
4. **Test backups monthly** - Verify restore works
5. **Keep Python updated** - Security patches
6. **Document changes** - For team reference

---

**Setup selesai? Go to http://127.0.0.1:4321 untuk test!** 🎉

Atau jika ada error, check QUICK_START.md troubleshooting section.

---

Version: 1.0 | Updated: 30 Mei 2026
