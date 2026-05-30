# 📋 Manajemen Pekerjaan - Job Management System

Sistem manajemen pekerjaan terintegrasi berbasis web untuk perusahaan manufaktur dengan fitur planning, tracking, dan reporting yang komprehensif.

## 🎯 Fitur Utama

### 1. **Dashboard & Planning**
- 📊 Dashboard dengan visualisasi job status
- 📅 Perencanaan pekerjaan harian/bulanan
- 🔄 Tracking real-time status pekerjaan
- 📈 Statistik dan reporting pekerjaan

### 2. **Multi-Departemen**
- 👥 Manajemen pengguna per departemen
- 🔐 Role-based access control (RBAC)
- 📊 Hierarchical departemen structure (Teknik, Operasional, dll)
- 🎫 Cascading job permissions antar departemen

### 3. **Job Management**
- ✏️ CRUD pekerjaan (Create, Read, Update, Delete)
- 🏷️ Kategori job: Daily Jobs, Project Jobs, Preventive Jobs
- 📎 Attachments support (PDF, image, dokumen)
- 🏗️ Project-based job organization
- ⏰ Overdue job tracking & notifications

### 4. **Preventive Jobs**
- 🔧 Manajemen preventive maintenance schedule
- 📝 Equipment & line management
- 🎯 Task automation dengan kategori pekerjaan
- 📊 Preventive vs maintenance tracking

### 5. **Meetings & Notulen**
- 📅 Meeting scheduling & management
- 📝 Notulen documentation
- 🔄 Auto-sync dengan Google Sheets
- 📧 Email notifications via WhatsApp (Fontte API)
- ⏰ Meeting reminders setiap 5 menit via Celery

### 6. **Ijin/Cuti (Leave Management)**
- 📅 Calendar view untuk leave events
- 🗓️ Google Calendar integration
- 🔄 Auto-sync dari Google Calendar
- 📋 Leave request tracking

### 7. **Inventory Management**
- 📦 Barang inventory system
- 🔍 Stock tracking
- 📥 Batch import via Excel
- 📊 Inventory reports

### 8. **Tool Keeper**
- 🔧 Tool rental/peminjaman system
- 📋 Asset management
- 📅 Rental history tracking
- 🔔 Return notifications

### 9. **Database Management**
- 💾 Database backup & restore
- 🏥 Health monitoring
- 📊 Database statistics
- ⚡ Auto-backup sebelum restore

### 10. **Export & Reporting**
- 📄 Export ke PDF (daily jobs, project jobs)
- 📊 Export ke Excel
- 🗂️ Batch export functionality
- 📈 Custom report generation

---

## 🏗️ Tech Stack

### Backend
- **Framework**: Django 5.2.8
- **Language**: Python 3.10+
- **Database**: PostgreSQL 16
- **Task Queue**: Celery 5.3.4 + Redis 5.0.1
- **API Integration**: Google Calendar, Google Sheets, Fontte WhatsApp

### Frontend
- **Framework**: Bootstrap 5.3.3
- **UI Components**: Bootstrap Icons
- **JS Enhancements**: Select2, Flatpickr, jQuery
- **Template Engine**: Django Templates

### DevOps & Services
- **Process Manager**: PM2
- **Server**: Gunicorn
- **Cache**: Redis
- **Message Broker**: Redis
- **Web Server**: Caddy (optional)
- **OS**: Windows Server 2022

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.10+
- PostgreSQL 16
- Redis 5.0.1
- Node.js (untuk PM2)
- Git

### Quick Start - Fresh Installation

Lihat panduan detail di: [SETUP_FRESH_INSTALL.md](SETUP_FRESH_INSTALL.md)

```bash
# 1. Clone repository
git clone <repository-url>
cd proyek_manajemen_job

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file (copy dari .env.example)
cp .env.example .env
# Edit .env dengan konfigurasi lokal Anda

# 5. Database migrations
python manage.py migrate

# 6. Create superuser (admin)
python manage.py createsuperuser

# 7. Run development server
python manage.py runserver 0.0.0.0:8000
```

### Production Setup with PM2

Lihat: [SETUP_PM2_DOKUMENTASI.md](SETUP_PM2_DOKUMENTASI.md)

```bash
# Install PM2 globally
npm install -g pm2

# Start all services with PM2
pm2 start ecosystem.config.js

# Monitor services
pm2 monit
```

---

## 🔧 Configuration

### Environment Variables (.env)
```
DJANGO_ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database
DB_NAME=proyek_management_job
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/1
CELERY_BROKER_URL=redis://localhost:6379/0

# Google Calendar & Sheets
GOOGLE_CALENDAR_CREDENTIALS_FILE=path/to/credentials.json
GOOGLE_CALENDAR_ID=calendar-id-here

# Paths
MEDIA_ROOT=C:/data/management-job/media
LOG_DIR=C:/logs/management-job

# Fontte WhatsApp API (untuk notifikasi meeting)
FONTTE_TOKEN=your-fontte-token
```

### Database
- Host: `localhost:5432`
- Database: `proyek_management_job`
- User: `postgres`
- Password: Stored in `.env` (not in git)

### Redis
- Cache: `localhost:6379/1`
- Celery Broker: `localhost:6379/0`

---

## 📁 Project Structure

```
proyek_manajemen_job/
├── config/              # Django project settings
│   ├── settings.py      # Main settings
│   ├── urls.py          # URL routing
│   ├── wsgi.py          # WSGI config
│   ├── celery.py        # Celery config
│   └── asgi.py          # ASGI config
│
├── core/                # Main app (jobs, leave, etc)
│   ├── models.py        # Data models
│   ├── views.py         # Main views
│   ├── views_backup.py  # Backup/restore views
│   ├── forms.py         # Form validation
│   ├── urls.py          # Core app URLs
│   └── management/      # Django management commands
│
├── meetings/            # Meetings & Notulen app
│   ├── models.py        # Meeting models
│   ├── views.py         # Meeting views
│   ├── tasks.py         # Celery tasks (reminders)
│   └── urls.py          # Meeting URLs
│
├── preventive_jobs/     # Preventive maintenance app
│   ├── models.py        # Preventive job models
│   ├── views.py         # Preventive job views
│   └── urls.py          # Preventive URLs
│
├── inventory/           # Inventory management app
│   ├── models.py        # Inventory models
│   ├── views.py         # Inventory views
│   └── urls.py          # Inventory URLs
│
├── toolkeeper/          # Tool rental system
│   ├── models.py        # Tool models
│   ├── views.py         # Tool views
│   └── urls.py          # Tool URLs
│
├── templates/           # Django templates
│   ├── base.html        # Base template with navbar
│   ├── backup_restore.html
│   └── ... (other templates)
│
├── static/              # Static files (CSS, JS, images)
├── scripts/             # Utility scripts
├── backups/             # Database backups
│
├── requirements.txt     # Python dependencies
├── manage.py            # Django management
├── ecosystem.config.js  # PM2 configuration
├── README.md            # This file
└── ... (config files)
```

---

## 🚀 Running the Application

### Development Mode
```bash
# Terminal 1 - Django
python manage.py runserver 0.0.0.0:8000

# Terminal 2 - Celery Worker
celery -A config worker -l info --pool=solo

# Terminal 3 - Celery Beat
celery -A config beat -l info
```

Access: `http://localhost:8000`

### Production Mode (PM2)
```bash
# Start all services
pm2 start ecosystem.config.js

# View logs
pm2 logs

# Monitor
pm2 monit

# Stop/restart
pm2 stop/restart management-django
```

Access: `http://192.168.111.130:4321` (adjust IP for your network)

---

## 📊 Key Models

### Core Models
- **Job**: Pekerjaan harian/proyek
- **DailyJob**: Pekerjaan per hari
- **ProjectJob**: Pekerjaan dalam proyek
- **Departemen**: Struktur departemen
- **CustomUser**: User dengan departemen assignment
- **LeaveEvent**: Ijin/cuti calendar events

### Preventive Models
- **PreventiveJob**: Preventive maintenance tasks
- **Equipment**: Peralatan untuk maintenance
- **Line**: Produksi line/area

### Meetings Models
- **Meeting**: Meeting schedule
- **Notulen**: Meeting notes
- **MeetingReminder**: Reminder configuration

### Inventory Models
- **Barang**: Inventory items
- **BarangStok**: Stock tracking

### Tool Keeper Models
- **Tool**: Tools available for rent
- **ToolRental**: Rental transactions

---

## 🔐 Authentication & Permissions

### User Roles
- **Superuser/Admin**: Full access ke semua fitur
- **Staff**: Access terbatas berdasarkan departemen
- **Regular User**: Access ke dashboard dan leave management

### Departemen-Based Permissions
- Teknik, Operasional, dll
- Jobs visible berdasarkan user's departemen
- Hierarchical: Parent job visible ke child departemen
- Admin dapat melihat semua jobs

### Feature Permissions
- Per-user feature toggle
- Stored di CustomUser.user_features JSON field

---

## 💾 Database Backup & Restore

### Automatic Backup
- Auto-backup sebelum restore operation
- File: `/backups/backup_before_restore_<datetime>.sql`

### Manual Backup
1. Login sebagai admin
2. Go to: **Admin → Backup & Restore**
3. Click **"Buat Backup"**
4. File akan disimpan di `/backups/` folder

### Restore dari Backup
1. Login sebagai admin
2. Go to: **Admin → Backup & Restore**
3. Upload file `.sql`
4. Check confirmation checkbox
5. Click **"Restore Database"**
6. Wait untuk proses selesai (dapat 5-10 menit)

---

## 🐛 Troubleshooting

### Django Server Issues
```bash
# Check if running
pm2 status

# View logs
pm2 logs management-django

# Restart
pm2 restart management-django
```

### Celery Issues
```bash
# Check worker
pm2 logs management-celery-worker

# Restart worker
pm2 restart management-celery-worker

# Check beat scheduler
pm2 logs management-celery-beat
```

### Database Connection
```bash
# Check PostgreSQL running
psql -U postgres -d postgres -c "SELECT 1"

# Check Django connection
python manage.py dbshell
```

### Redis Issues
```bash
# Test Redis connection
redis-cli ping
# Should return: PONG
```

---

## 📚 Documentation

- [SETUP_FRESH_INSTALL.md](SETUP_FRESH_INSTALL.md) - Fresh setup guide
- [SETUP_PM2_DOKUMENTASI.md](SETUP_PM2_DOKUMENTASI.md) - PM2 production setup
- [KONFIGURASI_RINGKAS.md](KONFIGURASI_RINGKAS.md) - Quick configuration
- [REFERENSI_KONFIGURASI.md](REFERENSI_KONFIGURASI.md) - Detailed config reference
- [QUICK_START.md](QUICK_START.md) - Quick start guide

---

## 📞 Support

Untuk pertanyaan atau issue:
1. Check troubleshooting section
2. Review documentation files
3. Check application logs: `C:/logs/management-job/`
4. Database logs di PostgreSQL

---

## 📝 License

Proprietary - Internal Use Only

---

## ✅ Checklist

Untuk fresh installation, pastikan:
- ✅ Python 3.10+ installed
- ✅ PostgreSQL 16 running
- ✅ Redis 5.0.1 running
- ✅ Node.js & PM2 installed
- ✅ `.env` file configured
- ✅ Database migrations completed
- ✅ Superuser created
- ✅ Google Calendar credentials (if needed)
- ✅ All services running via PM2

---

**Last Updated**: May 31, 2026
**Version**: 1.0.0
**Status**: Production Ready
