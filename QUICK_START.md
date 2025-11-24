# QUICK START GUIDE - Setup Server Lokal

## 🚀 Quick Setup (5 Langkah)

### PRASYARAT:
- Windows 10/11
- Python 3.10+ terinstall
- PostgreSQL terinstall

---

## LANGKAH DEMI LANGKAH

### 1️⃣ CLONE PROJECT DARI GITHUB

```powershell
mkdir D:\server_apps
cd D:\server_apps
git clone https://github.com/fastabiqhidayatulah/proyek_manajemen_job.git
cd proyek_manajemen_job
```

---

### 2️⃣ SETUP DATABASE POSTGRESQL

**CARA MANUAL:**
```powershell
# Buka Command Prompt sebagai Administrator
psql -U postgres

# Ketik command ini (ganti password sesuai keinginan):
CREATE DATABASE proyek_manajemen_job;
CREATE USER django_user WITH PASSWORD 'django_password_123';
ALTER ROLE django_user SET client_encoding TO 'utf8';
ALTER ROLE django_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE django_user SET default_transaction_deferrable TO on;
ALTER ROLE django_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE proyek_manajemen_job TO django_user;
\q
```

**ATAU GUNAKAN SCRIPT (Lebih Mudah):**
```powershell
# Jalankan ini sebagai Administrator
.\setup_database.bat
```

---

### 3️⃣ SETUP ENVIRONMENT & INSTALL DEPENDENCIES

**OTOMATIS (Rekomendasi):**
```powershell
# Jalankan sebagai Administrator
.\setup_environment.bat
```

**ATAU MANUAL:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

---

### 4️⃣ UPDATE DATABASE CREDENTIALS DI settings.py

Edit file: `config/settings.py`

Cari bagian DATABASES dan ubah:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'proyek_manajemen_job',
        'USER': 'django_user',
        'PASSWORD': 'django_password_123',  # ← SESUAIKAN PASSWORD
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Sesuaikan dengan database credentials yang Anda buat di step 2.

---

### 5️⃣ TEST MANUAL

```powershell
# Activate venv (jika belum)
.\venv\Scripts\Activate.ps1

# Jalankan server di port 1234
python manage.py runserver 0.0.0.0:1234
```

Akses: **http://localhost:1234**

Jika berhasil, tekan Ctrl+C untuk stop, lanjut ke step 6.

---

### 6️⃣ SETUP AUTO-START (Saat Komputer Nyala)

**PILIHAN A: NSSM Service (Recommended)**

```powershell
# Download NSSM dari: https://nssm.cc/download
# Extract ke folder, misal: C:\nssm

# Buka PowerShell sebagai Administrator:
cd C:\nssm\win64

nssm install ProyekManajemenJob "D:\server_apps\proyek_manajemen_job\venv\Scripts\python.exe" "D:\server_apps\proyek_manajemen_job\manage.py runserver 0.0.0.0:1234"

nssm set ProyekManajemenJob Start SERVICE_AUTO_START
nssm set ProyekManajemenJob AppDirectory "D:\server_apps\proyek_manajemen_job"
nssm start ProyekManajemenJob

# Cek status:
nssm status ProyekManajemenJob
```

---

**PILIHAN B: Task Scheduler (Lebih Sederhana)**

1. Buka **Task Scheduler** (Ctrl+Shift+Esc → Task Scheduler)
2. Klik **"Create Basic Task"**
3. **Name:** Proyek Manajemen Job
4. **Trigger:** At startup
5. **Action:** 
   - Program: `powershell.exe`
   - Arguments: `-WindowStyle Hidden -Command "& D:\server_apps\proyek_manajemen_job\run_server.bat"`
6. **Finish**

Atau lebih simpel, copy `run_server.bat` ke folder Startup:
```powershell
# Buka folder startup:
explorer "C:\Users\YourUsername\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"

# Copy file run_server.bat ke sini
```

---

### 7️⃣ VERIFY SETUP BERHASIL

**Restart komputer**, kemudian:

```powershell
# Cek apakah service berjalan
Get-Process python

# Buka browser:
# http://localhost:1234
```

---

## 📝 QUICK REFERENCE

| Command | Fungsi |
|---------|--------|
| `.\venv\Scripts\Activate.ps1` | Activate virtual environment |
| `python manage.py runserver 0.0.0.0:1234` | Run server di port 1234 |
| `python manage.py migrate` | Migrasi database |
| `python manage.py createsuperuser` | Buat admin account |
| `python manage.py collectstatic` | Collect static files |
| `.\setup_environment.bat` | Setup otomatis (jalankan sekali) |
| `.\run_server.bat` | Run server (gampang) |

---

## 🆘 TROUBLESHOOTING

### ❌ "ModuleNotFoundError: No module named 'django'"
**Solusi:** Jalankan `pip install -r requirements.txt`

### ❌ "could not connect to database"
**Solusi:**
1. Cek PostgreSQL running: `Get-Service postgresql-x64-15`
2. Cek credentials di `config/settings.py`
3. Cek database sudah dibuat: `psql -U django_user -d proyek_manajemen_job`

### ❌ "Address already in use :1234"
**Solusi:**
```powershell
# Kill process yang pakai port 1234
netstat -ano | findstr :1234
taskkill /PID <PID> /F

# Atau ubah port di run_server.bat: s/1234/5000/
```

### ❌ "Service tidak auto-start"
**Solusi:**
- Cek Task Scheduler atau NSSM service status
- Check Windows Event Viewer untuk error logs
- Jalankan setup script dengan Administrator privileges

---

## 🔗 AKSES APPLICATION

Setelah setup selesai:
- **Web App:** http://localhost:1234
- **Admin Panel:** http://localhost:1234/admin
- **Export Jobs:** http://localhost:1234/job-per-day/
- **Network Access:** http://192.168.1.x:1234 (dari PC lain)

---

## 📞 SUPPORT

Untuk bantuan lebih lanjut, lihat:
- `SETUP_SERVER_LOKAL.md` - Dokumentasi lengkap
- `settings_production_example.py` - Contoh settings production
- GitHub Issues: https://github.com/fastabiqhidayatulah/proyek_manajemen_job/issues

---

**Last Updated:** November 24, 2025
