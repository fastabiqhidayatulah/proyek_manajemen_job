# 🔧 SYSTEM-LEVEL DEPENDENCIES ANALYSIS

## Overview

**Good News**: This Django application has **MINIMAL** system-level dependencies.

No need to install:
- ❌ wkhtmltopdf (PDF from HTML)
- ❌ LibreOffice (Document conversion)
- ❌ FFmpeg (Video/Audio processing)
- ❌ Ghostscript (PostScript processing)
- ❌ Tesseract (OCR)
- ❌ ImageMagick (Image manipulation)
- ❌ ODBC Driver (SQL Server - using PostgreSQL instead)

---

## Required System-Level Packages

### 1. Python 3.11

**Windows Server 2022 Installation**:

```powershell
# Option 1: Download and install manually
# https://www.python.org/downloads/release/python-3110/

# Option 2: Using Chocolatey
choco install python --version=3.11.8

# Verify
python --version

# Should output: Python 3.11.x
```

**Add to PATH** (if not automatically done):
```powershell
# Check if python command works
where python

# If not found, add to PATH manually:
# C:\Users\<username>\AppData\Local\Programs\Python\Python311\
```

---

### 2. PostgreSQL 16

**Windows Server 2022 Installation**:

```powershell
# Option 1: Download installer
# https://www.postgresql.org/download/windows/

# Option 2: Using Chocolatey
choco install postgresql16

# During installation:
# - Port: 5432 (default)
# - Superuser password: (set strong password)
# - Service account: postgres (default)
# - Install pgAdmin: Yes (recommended)
```

**Post-installation**:

```powershell
# Check service is running
Get-Service postgresql-x64-16

# Should show: Running

# Test connection
psql -U postgres -c "SELECT 1;"

# Should work without errors
```

**Create Application Database User**:

```powershell
# Connect as postgres superuser
psql -U postgres

# Then run in psql:
CREATE USER manajemen_app_user WITH PASSWORD 'your-strong-password';
ALTER USER manajemen_app_user CREATEDB;
CREATE DATABASE proyek_management_job OWNER manajemen_app_user;
GRANT ALL PRIVILEGES ON DATABASE proyek_management_job TO manajemen_app_user;
```

---

### 3. Redis (Cache & Task Broker)

**Windows Server 2022 Installation**:

```powershell
# Option 1: Using Chocolatey (recommended)
choco install redis

# Option 2: Download MSI installer
# https://github.com/microsoftarchive/redis/releases

# Verify Redis installed
redis-cli --version

# Should output version
```

**Start Redis Service**:

```powershell
# Start Redis service
Start-Service Redis

# Test connection
redis-cli ping

# Should respond: PONG

# Check configuration
redis-cli info server
```

---

### 4. Visual C++ Build Tools

**Required for**: Building Python packages like psycopg2

```powershell
# Download from Microsoft
# https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Or install via Chocolatey
choco install visualcpp-build-tools

# Verify
# You should see "C++ Build Tools" in "Programs and Features"
```

---

### 5. Node.js (For PM2 Service Management)

**Optional but Recommended** for production service management:

```powershell
# Download and install
# https://nodejs.org/ (LTS version)

# Or via Chocolatey
choco install nodejs

# Verify
node --version
npm --version

# Should output: v18.x.x or higher
```

---

## PDF Generation with WeasyPrint

WeasyPrint is a **Python library** that generates PDFs from HTML/CSS without system dependencies.

**What WeasyPrint Needs**:
- Python 3.11 ✓ (already installing)
- Python packages (installed via pip) ✓
- NO external system dependencies ✓

**How it works**:

```python
from weasyprint import HTML, CSS

# Convert HTML to PDF directly
html_string = "<h1>Hello World</h1>"
PDF = HTML(string=html_string).write_pdf()

# Or from URL
PDF = HTML('http://example.com').write_pdf()

# Or from file
PDF = HTML('document.html').write_pdf(CSS('style.css'))
```

**Benefits Over wkhtmltopdf**:
- ✓ Pure Python (no system binary needed)
- ✓ Better CSS support (CSS3)
- ✓ Smaller memory footprint
- ✓ Better performance
- ✓ Easier to manage in containers/cloud

---

## Database Drivers

### PostgreSQL

**Driver**: psycopg2-binary

```bash
# Installed via requirements.txt
pip install psycopg2-binary==2.9.9

# No separate PostgreSQL client needed (binary includes it)
# But optionally install psql client tools:
choco install postgresql16

# Then you can use:
psql -U user -d database
```

**Connection**:

```python
# Django handles via psycopg2-binary
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'proyek_management_job',
        'USER': 'manajemen_app_user',
        'PASSWORD': 'xxx',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## Google APIs

### Credentials

The application uses **Google Service Account** for Google Calendar API.

**File**: `config/credentials/google-calendar-sa.json`

**How to get**:
1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a service account
3. Generate JSON key
4. Download and place in `config/credentials/`

**No system-level dependencies** - Just a JSON file ✓

---

## QR Code Generation

**Library**: qrcode + Pillow

```bash
# Installed via requirements.txt
pip install qrcode[pil]==7.4.2
pip install Pillow==10.1.0

# Pure Python, no system dependencies
```

**Usage**:

```python
import qrcode

# Generate QR code
qr = qrcode.QRCode(version=1, box_size=10, border=5)
qr.add_data('Your data here')
qr.make(fit=True)

# Save as image
img = qr.make_image(fill_color="black", back_color="white")
img.save("qr_code.png")
```

---

## Image Processing

**Library**: Pillow

```bash
# Installed via requirements.txt
pip install Pillow==10.1.0

# Pure Python with C extensions (handles most image formats)
# No ImageMagick or GraphicsMagick needed
```

**Supported Formats**: JPEG, PNG, GIF, BMP, TIFF, ICO, WebP, etc.

---

## Data Export

### Excel Export

**Library**: openpyxl

```bash
# Pure Python, no system dependencies
pip install openpyxl==3.1.5

# Supports .xlsx format (modern Excel)
```

### PDF Reports

**Library**: reportlab

```bash
# Pure Python, no system dependencies
pip install reportlab==4.0.9

# Generates PDF from scratch (code-based)
```

---

## Environment Configuration

**Library**: python-dotenv

```bash
# Pure Python, no system dependencies
pip install python-dotenv==1.0.0

# Reads .env file and sets environment variables
```

**Usage**:

```python
from dotenv import load_dotenv
load_dotenv()

# Now environment variables are available
import os
db_password = os.environ.get('DB_PASSWORD')
```

---

## WSGI Server

**Library**: gunicorn

```bash
# Pure Python, no system dependencies
pip install gunicorn==21.2.0

# Run as standalone Python application
```

**Execution**:

```bash
gunicorn config.wsgi:application --workers 4 --bind 127.0.0.1:8001
```

---

## Complete System Setup Script

Create file: `install_system_dependencies.ps1`

```powershell
# Run as Administrator

Write-Host "Installing System-Level Dependencies for Proyek Manajemen Job" -ForegroundColor Green

# 1. Python 3.11
Write-Host "`nInstalling Python 3.11..." -ForegroundColor Cyan
choco install python --version=3.11.8 -y

# 2. PostgreSQL 16
Write-Host "`nInstalling PostgreSQL 16..." -ForegroundColor Cyan
choco install postgresql16 -y

# 3. Redis
Write-Host "`nInstalling Redis..." -ForegroundColor Cyan
choco install redis -y

# 4. Visual C++ Build Tools
Write-Host "`nInstalling Visual C++ Build Tools..." -ForegroundColor Cyan
choco install visualcpp-build-tools -y

# 5. Node.js (Optional, for PM2)
Write-Host "`nInstalling Node.js (Optional)..." -ForegroundColor Cyan
choco install nodejs -y

# Verify installations
Write-Host "`n=== VERIFICATION ===" -ForegroundColor Green
Write-Host "Python: $(python --version)"
Write-Host "PostgreSQL: $(psql --version)"
Write-Host "Redis: $(redis-cli --version)"
Write-Host "Node.js: $(node --version)"

Write-Host "`n✓ System dependencies installed!" -ForegroundColor Green
```

---

## Dependency Tree Summary

```
System-Level
├── Windows Server 2022 (OS)
├── Python 3.11 (Runtime)
├── PostgreSQL 16 (Database)
├── Redis (Cache/Broker)
├── Visual C++ Build Tools (Compiler)
└── Node.js (PM2 management - optional)

Python Level (via pip)
├── Django 5.2.8
├── psycopg2-binary (PostgreSQL driver)
├── Celery + Redis client
├── WeasyPrint (PDF generation)
├── Pillow (Image processing)
├── qrcode (QR code generation)
├── openpyxl (Excel export)
├── Google APIs
└── 20+ other packages

Application Level
├── PostgreSQL database
├── Redis cache
├── Google Calendar API
├── Fontte WhatsApp API
└── File system (media, logs, backups)
```

---

## Troubleshooting System Dependencies

### Issue: Python not found in PATH

```powershell
# Check where Python is installed
where python

# If not found, add to PATH manually
$env:Path += ";C:\Program Files\Python311"

# Make it permanent
[Environment]::SetEnvironmentVariable(
    "Path",
    "$env:Path;C:\Program Files\Python311",
    "User"
)

# Restart PowerShell and test
python --version
```

### Issue: PostgreSQL service won't start

```powershell
# Check service status
Get-Service postgresql-x64-16 | Select-Object Status, StartType

# Try to start it
Start-Service postgresql-x64-16

# Check for errors
Get-EventLog -LogName Application -Newest 10 | Where-Object Source -match "postgres"
```

### Issue: Redis won't respond

```powershell
# Check service status
Get-Service Redis | Select-Object Status

# Test port
netstat -ano | findstr :6379

# Restart service
Restart-Service Redis

# Test connection
redis-cli ping
```

### Issue: Visual C++ Build Tools installation fails

```powershell
# Try manual installation
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Or update Chocolatey and retry
choco upgrade visualcpp-build-tools -f

# Then reinstall psycopg2 if needed
pip install --upgrade psycopg2-binary
```

---

## Final Checklist

- [ ] Python 3.11 installed and in PATH
- [ ] PostgreSQL 16 installed and service running
- [ ] Redis installed and service running  
- [ ] Visual C++ Build Tools installed
- [ ] Node.js installed (for PM2 - optional)
- [ ] `python --version` returns 3.11.x
- [ ] `psql --version` works
- [ ] `redis-cli ping` returns PONG
- [ ] Database user `manajemen_app_user` created
- [ ] Database `proyek_management_job` created
- [ ] All firewall rules configured

Once complete, proceed to: **DEPLOYMENT_CLEAN_SETUP.md**

