# PANDUAN BACKUP OTOMATIS KE GOOGLE DRIVE
# =======================================

## 1. PRASYARAT
- ✓ PostgreSQL installed (pg_dump tersedia)
- ✓ rclone installed di: C:\Program Files\rclone
- ✓ rclone sudah dikonfigurasi dengan remote "gdrive"
- ✓ PowerShell 5.0+

## 2. VERIFIKASI KONFIGURASI RCLONE

### Test Remote Connection:
```powershell
# Buka PowerShell dan jalankan:
C:\Program Files\rclone\rclone.exe ls gdrive:/

# Output yang diharapkan:
#     -1 2025-12-19 10:30:00    -1 proyek_management_backup
```

### Jika belum ada folder backup di GDrive:
```powershell
C:\Program Files\rclone\rclone.exe mkdir gdrive:/proyek_management_backup
```

## 3. SETUP BACKUP SCRIPT

### Step 1: Buka PowerShell sebagai Administrator
```
1. Klik tombol Start
2. Ketik "PowerShell"
3. Klik kanan "Windows PowerShell" → "Run as administrator"
```

### Step 2: Test Manual Backup (Jalankan sekali untuk verifikasi)
```powershell
# Navigate ke project directory
cd D:\proyek_management_job\scripts

# Jalankan backup script
powershell -ExecutionPolicy Bypass -File .\backup_to_gdrive.ps1
```

### Contoh Output yang Diharapkan:
```
Backup selesai! Cek log di: D:\proyek_management_job\backups\backup_log.txt
File backup: backup_proyek_management_2025-12-19_140530.sql.gz
Tersimpan di Google Drive: proyek_management_backup
```

### Step 3: Verifikasi File di Google Drive
```
1. Buka https://drive.google.com
2. Cari folder "proyek_management_backup"
3. Pastikan file backup_proyek_management_YYYY-MM-DD_HHMMSS.sql.gz ada
```

## 4. SETUP AUTOMATIC BACKUP (TASK SCHEDULER)

### Step 1: Jalankan Scheduling Script sebagai Administrator
```powershell
cd D:\proyek_management_job\scripts

# Jalankan scheduling script
powershell -ExecutionPolicy Bypass -File .\schedule_gdrive_backup.ps1
```

### Contoh Output:
```
Membuat scheduled task untuk backup otomatis...
✓ Scheduled task berhasil dibuat!
  Task Name: Proyek_Management_Backup_GDrive
  Waktu eksekusi: 02:00 setiap hari
  Script: D:\proyek_management_job\scripts\backup_to_gdrive.ps1
```

### Step 2: Verifikasi Task di Task Scheduler
```powershell
# Cara 1: Via PowerShell
Get-ScheduledTask -TaskName "Proyek_Management_Backup_GDrive" | Select-Object *

# Cara 2: Via GUI
# Buka Task Scheduler: Win + R → taskschd.msc → Enter
# Navigasi: Task Scheduler Library → Cari "Proyek_Management_Backup_GDrive"
```

## 5. KUSTOMISASI

### Ubah Waktu Backup
Edit file: `D:\proyek_management_job\scripts\schedule_gdrive_backup.ps1`
```powershell
$Time = "02:00"  # Ubah ke waktu yang diinginkan, misalnya "22:00" untuk jam 10 malam
```
Kemudian jalankan ulang scheduling script.

### Ubah Database Name
Edit file: `D:\proyek_management_job\scripts\backup_to_gdrive.ps1`
```powershell
$DBName = "proyek_management"  # Ubah jika nama database berbeda
```

### Ubah Retensi Backup (Berapa lama disimpan di lokal)
Edit file: `D:\proyek_management_job\scripts\backup_to_gdrive.ps1`
```powershell
$CutoffDate = (Get-Date).AddDays(-7)  # Ubah -7 ke jumlah hari yang diinginkan
```

## 6. MONITORING & TROUBLESHOOTING

### Cek Log Backup
```powershell
# Buka log file
notepad D:\proyek_management_job\backups\backup_log.txt

# Atau lihat realtime di PowerShell:
Get-Content -Path D:\proyek_management_job\backups\backup_log.txt -Wait
```

### List Backup Files di Lokal
```powershell
Get-ChildItem D:\proyek_management_job\backups\backup_*.gz | Format-Table Name, @{N='Size(MB)';E={[math]::Round($_.Length/1MB, 2)}}
```

### List Backup Files di Google Drive
```powershell
C:\Program Files\rclone\rclone.exe ls gdrive:/proyek_management_backup
```

### Error: "pg_dump not found"
**Solusi:**
```powershell
# Tambahkan PostgreSQL bin ke PATH
$env:Path += ";C:\Program Files\PostgreSQL\<version>\bin"

# Ganti <version> dengan versi PostgreSQL, misal: 15, 16, dll
# Cek versi: Start Menu → PostgreSQL → pgAdmin atau cmd → psql --version
```

### Error: "permission denied" saat backup
**Solusi:**
- Jalankan PowerShell sebagai Administrator
- Atau ubah ownership folder backups

### Error: "rclone not found"
**Solusi:**
```powershell
# Verifikasi rclone path
Test-Path "C:\Program Files\rclone\rclone.exe"

# Jika False, install atau ubah path di backup_to_gdrive.ps1
$RclonePath = "C:\Program Files\rclone\rclone.exe"
```

## 7. RESTORE DATABASE DARI BACKUP

### Download dari Google Drive
```powershell
# Download backup terbaru
C:\Program Files\rclone\rclone.exe copy gdrive:/proyek_management_backup/ D:\proyek_management_job\backups\ --max-age 1d

# Ekstrak file
$BackupFile = "D:\proyek_management_job\backups\backup_proyek_management_YYYY-MM-DD_HHMMSS.sql.gz"
Expand-Archive -Path $BackupFile -DestinationPath D:\proyek_management_job\backups\ -Force
```

### Restore Database
```bash
# Di Command Prompt atau PowerShell
cd D:\proyek_management_job

# Restore dari file SQL
psql -U postgres -d proyek_management < D:\proyek_management_job\backups\backup_proyek_management_YYYY-MM-DD_HHMMSS.sql

# Atau dengan dropdb dulu jika ada yang sudah
dropdb -U postgres -h localhost proyek_management
createdb -U postgres -h localhost proyek_management
psql -U postgres -d proyek_management < backup_file.sql
```

## 8. REMOTE VSCode EXECUTION

Karena menjalankan via VSCode Remote (LAN), pastikan:

✓ **PowerShell tersedia di remote machine** (biasanya sudah ada di Windows)
✓ **pg_dump akses PostgreSQL** (biasanya lokal di 127.0.0.1:5432)
✓ **Rclone bisa akses network** (Google Drive via internet)
✓ **Task Scheduler berjalan** di background

Untuk menjalankan manual via VSCode terminal:
```powershell
# Via VSCode integrated terminal (remote)
cd D:\proyek_management_job\scripts
powershell -ExecutionPolicy Bypass -File .\backup_to_gdrive.ps1
```

## 9. SUMMARY

### Sekali Setup:
```powershell
# Terminal 1: Test manual backup
powershell -ExecutionPolicy Bypass -File D:\proyek_management_job\scripts\backup_to_gdrive.ps1

# Terminal 2: Setup automatic scheduling
powershell -ExecutionPolicy Bypass -File D:\proyek_management_job\scripts\schedule_gdrive_backup.ps1
```

### Hasil:
- ✓ Backup database otomatis setiap hari jam 02:00
- ✓ File dicompres (SQL → SQL.GZ)
- ✓ Otomatis upload ke Google Drive
- ✓ Backup lama (>7 hari) dihapus otomatis dari lokal
- ✓ Log tercatat untuk monitoring

### Maintenance:
- Cek log weekly: `D:\proyek_management_job\backups\backup_log.txt`
- Verifikasi folder GDrive: https://drive.google.com → proyek_management_backup
- Test restore backup sebulan sekali (best practice)

---
**Last Updated:** 2025-12-19
**Version:** 1.0
