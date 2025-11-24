# Setup Project Django di Server Lokal dengan PostgreSQL

## 📋 Daftar Lengkap Setup

### 1. ✅ Install PostgreSQL
### 2. ✅ Buat Database & User di PostgreSQL
### 3. ✅ Clone/Setup Project dari GitHub
### 4. ✅ Konfigurasi Django Settings
### 5. ✅ Migrasi Database
### 6. ✅ Setup Auto-Running dengan Windows Service

---

## 1️⃣ INSTALL POSTGRESQL

### Download & Install
1. Download PostgreSQL installer dari: https://www.postgresql.org/download/windows/
2. Pilih versi terbaru (saat ini: 15 atau 16)
3. Jalankan installer
4. **PENTING**: Ingat password untuk user `postgres` yang dibuat saat install

**Default Setup:**
- Port: 5432
- Username: postgres
- Password: (sesuai yang Anda input saat install)

---

## 2️⃣ BUAT DATABASE & USER DI POSTGRESQL

### Buka pgAdmin atau Command Line
Buka **pgAdmin 4** (aplikasi GUI) atau **psql** (command line)

### Opsi A: Menggunakan pgAdmin 4 (GUI - Lebih Mudah)
```
1. Buka pgAdmin 4 (biasanya di http://localhost:5050)
2. Login dengan email/password Anda
3. Expand "Servers" → "PostgreSQL 15" (atau versi Anda)
4. Klik kanan "Databases" → Create → Database
5. Masukkan nama: proyek_manajemen_job
6. Click Save
```

### Opsi B: Menggunakan psql (Command Line)
```powershell
# Buka PowerShell Administrator
psql -U postgres

# Masukkan password saat diminta

# Jalankan command berikut di psql prompt (ditandai dengan =#):
CREATE DATABASE proyek_manajemen_job;
CREATE USER django_user WITH PASSWORD 'django_password_123';
ALTER ROLE django_user SET client_encoding TO 'utf8';
ALTER ROLE django_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE django_user SET default_transaction_deferrable TO on;
ALTER ROLE django_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE proyek_manajemen_job TO django_user;

# Keluar dari psql
\q
```

**Hasil yang diharapkan:**
```
Database: proyek_manajemen_job
User: django_user
Password: django_password_123
```

---

## 3️⃣ CLONE/SETUP PROJECT DARI GITHUB

### Di Server Lokal Anda:
```powershell
# Buat folder untuk project
mkdir D:\server_apps
cd D:\server_apps

# Clone dari GitHub
git clone https://github.com/fastabiqhidayatulah/proyek_manajemen_job.git
cd proyek_manajemen_job

# Buat virtual environment
python -m venv venv

# Activate venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Jika belum ada requirements.txt, install manual:
pip install django==5.2.8
pip install psycopg2-binary
pip install pillow
pip install weasyprint
pip install django-mptt
pip install requests
```

---

## 4️⃣ KONFIGURASI DJANGO SETTINGS

### Edit `config/settings.py`

Ubah database configuration:

```python
# SEBELUMNYA (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# MENJADI (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'proyek_manajemen_job',
        'USER': 'django_user',
        'PASSWORD': 'django_password_123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Tambahkan Allowed Hosts:
```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.x.x']  # Sesuaikan IP server lokal Anda
```

---

## 5️⃣ MIGRASI DATABASE

### Jalankan migrasi ke PostgreSQL:
```powershell
# Pastikan venv sudah activate
cd D:\server_apps\proyek_manajemen_job

# Migrasi database
python manage.py migrate

# Buat superuser (admin)
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: (pilih password yang aman)

# Collect static files (untuk production)
python manage.py collectstatic --noinput
```

---

## 6️⃣ TEST MANUAL DULU

### Jalankan development server di port 1234:
```powershell
python manage.py runserver 0.0.0.0:1234
```

### Akses:
- http://localhost:1234
- http://127.0.0.1:1234
- http://192.168.x.x:1234 (dari komputer lain di jaringan)

Jika berjalan OK, lanjut ke step auto-running.

---

## 7️⃣ SETUP AUTO-RUNNING DENGAN WINDOWS SERVICE

### Opsi A: Menggunakan NSSM (Non-Sucking Service Manager)

#### Download NSSM:
1. Download dari: https://nssm.cc/download
2. Extract ke folder, misal: `C:\nssm`
3. Tambahkan path ke environment variable

#### Install Service dengan NSSM:
```powershell
# Buka PowerShell sebagai Administrator

# Navigate ke folder NSSM
cd C:\nssm\win64

# Install service
nssm install ProyekManajemenJob "D:\server_apps\proyek_manajemen_job\venv\Scripts\python.exe" "D:\server_apps\proyek_manajemen_job\manage.py runserver 0.0.0.0:1234"

# Set startup type ke Automatic
nssm set ProyekManajemenJob Start SERVICE_AUTO_START

# Set working directory
nssm set ProyekManajemenJob AppDirectory "D:\server_apps\proyek_manajemen_job"

# Start service
nssm start ProyekManajemenJob
```

#### Verify Service:
```powershell
# Cek status
nssm status ProyekManajemenJob

# Harus return: SERVICE_RUNNING

# Lihat event log jika error
nssm query ProyekManajemenJob
```

---

### Opsi B: Menggunakan Python Script + Task Scheduler (Alternatif)

#### Buat file: `start_server.bat`
```batch
@echo off
cd /d D:\server_apps\proyek_manajemen_job
call venv\Scripts\activate.bat
python manage.py runserver 0.0.0.0:1234
pause
```

#### Setup Task Scheduler:
1. Buka **Task Scheduler** (Win + S, ketik "Task Scheduler")
2. Klik "Create Basic Task" di sebelah kanan
3. Nama: "Proyek Manajemen Job"
4. Trigger: Pilih "At startup"
5. Action: Start a program → Browse ke file `start_server.bat`
6. Finish

---

### Opsi C: Menggunakan Windows Batch Auto-Start (Paling Sederhana)

#### Buat file: `start_django.ps1`
```powershell
# Set working directory
Set-Location "D:\server_apps\proyek_manajemen_job"

# Activate venv
& .\venv\Scripts\Activate.ps1

# Run server
python manage.py runserver 0.0.0.0:1234
```

#### Buat shortcut di Startup folder:
```powershell
# Path ke startup folder
$startupFolder = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"

# Buat shortcut (gunakan: Win + R, ketik shell:startup untuk buka folder)
# Copy shortcut yang menjalankan PowerShell script
```

---

## 8️⃣ VERIFIKASI & TROUBLESHOOTING

### Check Status Service:
```powershell
# Lihat services yang berjalan
Get-Service | findstr Django

# Atau gunakan Task Manager:
# Buka Task Manager → Services tab
```

### Test Akses:
```powershell
# Test dari lokal
Invoke-WebRequest -Uri "http://localhost:1234" -UseBasicParsing

# Test dari komputer lain (ganti IP sesuai server Anda)
# Buka browser: http://192.168.1.100:1234
```

### Jika Error Connection Database:
```powershell
# Cek PostgreSQL running
Get-Service postgresql-x64-15  # atau versi Anda

# Jika tidak running, start manual
Start-Service postgresql-x64-15

# Test koneksi PostgreSQL
psql -U django_user -d proyek_manajemen_job -h localhost -p 5432
```

---

## 📝 CHECKLIST FINAL

- [ ] PostgreSQL sudah install & running
- [ ] Database `proyek_manajemen_job` sudah dibuat
- [ ] User `django_user` sudah dibuat
- [ ] Project di-clone dari GitHub ke `D:\server_apps\proyek_manajemen_job`
- [ ] Virtual environment sudah dibuat & dependency terinstall
- [ ] `config/settings.py` sudah di-update dengan PostgreSQL config
- [ ] `python manage.py migrate` sudah sukses
- [ ] `python manage.py createsuperuser` sudah dibuat
- [ ] Test manual dengan `python manage.py runserver 0.0.0.0:1234` - OK
- [ ] Service/Auto-start sudah dikonfigurasi
- [ ] Auto-start test: Restart komputer dan check apakah service running

---

## 🔗 Akses Application

**Setelah semua setup:**
- **Local Access:** http://localhost:1234
- **Network Access:** http://192.168.x.x:1234 (dari PC lain)
- **Admin Panel:** http://localhost:1234/admin

---

## 🆘 Bantuan Cepat

| Problem | Solusi |
|---------|--------|
| "ModuleNotFoundError: No module named 'django'" | Jalankan `pip install -r requirements.txt` |
| "could not connect to database" | Check PostgreSQL running, cek config di settings.py |
| "Address already in use :1234" | Ubah port atau kill process yang pakai port 1234 |
| "Service tidak auto-start" | Cek task scheduler atau NSSM service status |
| "Static files not loading" | Jalankan `python manage.py collectstatic` |

---

**Created:** November 24, 2025
**Project:** Proyek Manajemen Job
**Tech Stack:** Django 5.2.8 + PostgreSQL + Bootstrap 5
