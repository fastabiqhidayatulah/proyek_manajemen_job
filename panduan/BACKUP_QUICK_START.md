# BACKUP SETUP SUMMARY - LANGKAH DEMI LANGKAH
# ============================================

## KONFIGURASI ANDA:
- Remote: gdrive
- Lokasi rclone: C:\Program Files\rclone
- Project Path: D:\proyek_management_job
- Database: proyek_management
- Akses: VSCode Remote via LAN (192.168.10.239)

## SCRIPT YANG SUDAH DIBUAT:

### 1. `backup_to_gdrive.ps1`
Script untuk manual backup database ke Google Drive
- Dump database PostgreSQL
- Kompres file backup (SQL → SQL.GZ)
- Upload ke gdrive:/proyek_management_backup/
- Bersihkan backup lama (>7 hari)
- Log ke file

### 2. `schedule_gdrive_backup.ps1`
Script untuk membuat Windows Task Scheduler
- Jadwal: Setiap hari jam 02:00
- Otomatis jalankan backup_to_gdrive.ps1

### 3. `verify_backup_config.ps1`
Script untuk verifikasi konfigurasi
- Cek pg_dump
- Cek rclone
- Cek remote gdrive
- Cek koneksi ke Google Drive
- Cek folder backup
- Cek scheduled task
- Cek database connectivity

### 4. `GDRIVE_BACKUP_SETUP.md`
Panduan lengkap (di folder panduan/)

---

## CARA SETUP (3 LANGKAH MUDAH):

### LANGKAH 1: Verifikasi Konfigurasi
```powershell
# Buka PowerShell sebagai Administrator:
# 1. Click Start
# 2. Ketik: PowerShell
# 3. Klik Kanan "Windows PowerShell" → Run as administrator
# 4. Paste:

powershell -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/search?q=placeholder' | Out-Null; \\192.168.10.239\proyek_management_job\scripts\verify_backup_config.ps1"

# ATAU akses via UNC path di VSCode terminal atau remote connection:
\\192.168.10.239\proyek_management_job\scripts\verify_backup_config.ps1
```

### LANGKAH 2: Test Manual Backup (Jalankan Sekali)
```powershell
# PowerShell Administrator:
\\192.168.10.239\proyek_management_job\scripts\backup_to_gdrive.ps1

# Output harapan:
# Backup selesai! Cek log di: D:\proyek_management_job\backups\backup_log.txt
# File backup: backup_proyek_management_2025-12-19_140530.sql.gz
# Tersimpan di Google Drive: proyek_management_backup
```

### LANGKAH 3: Setup Automatic Scheduling
```powershell
# PowerShell Administrator:
\\192.168.10.239\proyek_management_job\scripts\schedule_gdrive_backup.ps1

# Output harapan:
# ✓ Scheduled task berhasil dibuat!
# Task Name: Proyek_Management_Backup_GDrive
# Waktu eksekusi: 02:00 setiap hari
```

---

## VERIFIKASI SETELAH SETUP:

### 1. Cek Log Backup
```
D:\proyek_management_job\backups\backup_log.txt
```

### 2. Cek Backup Files di Google Drive
```
https://drive.google.com → Folder "proyek_management_backup"
```

### 3. Cek Scheduled Task
```
Windows Start → Task Scheduler → Search "Proyek_Management_Backup_GDrive"
```

---

## TROUBLESHOOTING:

### Error: pg_dump not found
```powershell
# Solusi: Tambahkan ke PATH di backup_to_gdrive.ps1
$env:Path += ";C:\Program Files\PostgreSQL\16\bin"
```

### Error: Permission Denied
- Jalankan PowerShell sebagai Administrator
- Cek folder D:\proyek_management_job\backups bisa diakses

### Error: Rclone not found
- Verifikasi: `Test-Path "C:\Program Files\rclone\rclone.exe"`
- Jika False, update path di backup_to_gdrive.ps1

### Error: Remote 'gdrive' not configured
```powershell
# Config ulang rclone:
C:\Program Files\rclone\rclone.exe config
```

---

## BACKUP STRATEGY YANG DIREKOMENDASIKAN:

✓ Otomatis backup setiap hari jam 02:00 (server biasanya tidak sibuk)
✓ Database di-dump ke SQL format (mudah restore)
✓ Dikompres otomatis (hemat storage)
✓ Upload ke Google Drive (redundancy)
✓ Backup lama dihapus setelah 7 hari (hemat local storage)
✓ Log tercatat untuk monitoring

---

## MONITORING HARIAN:

### Minggu pertama: Cek daily
```
Every day: Open backup_log.txt → Pastikan "SUCCESS" muncul
Setiap 3 hari: Check Google Drive folder → Pastikan file ada
```

### Minggu ke-2 dan seterusnya: Cek weekly
```
Setiap Jumat: Open backup_log.txt
Setiap Minggu: List files di Google Drive
```

---

## RESTORE DATABASE (JIKA DIPERLUKAN):

### 1. Download backup dari Google Drive
```powershell
C:\Program Files\rclone\rclone.exe copy gdrive:/proyek_management_backup/ D:\proyek_management_job\backups\ --max-age 7d
```

### 2. Ekstrak file
```powershell
$BackupFile = "D:\proyek_management_job\backups\backup_proyek_management_YYYY-MM-DD_HHMMSS.sql.gz"
Expand-Archive -Path $BackupFile -DestinationPath D:\proyek_management_job\backups\
```

### 3. Restore ke database
```bash
# Di Command Prompt:
psql -U postgres -d proyek_management < D:\proyek_management_job\backups\backup_proyek_management_YYYY-MM-DD_HHMMSS.sql
```

---

## NEXT STEPS:

1. ✓ Jalankan verify_backup_config.ps1 untuk test konfigurasi
2. ✓ Jalankan backup_to_gdrive.ps1 untuk test manual backup
3. ✓ Verifikasi file muncul di Google Drive
4. ✓ Jalankan schedule_gdrive_backup.ps1 untuk setup otomatis
5. ✓ Verifikasi task di Task Scheduler
6. ✓ Monitor log file setiap hari selama 1 minggu

---

**Dibuat:** 19 Desember 2025
**Status:** Siap diimplementasikan
**Durasi Setup:** ~5 menit
**Durasi Test:** ~2 menit per test
