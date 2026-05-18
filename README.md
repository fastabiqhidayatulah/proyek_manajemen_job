# 🔧 Proyek Manajemen Job

Aplikasi **Preventive Job Management System** berbasis Django untuk mengelola pekerjaan preventif, penjadwalan maintenance, tracking eksekusi, dan checklist inspeksi dengan sistem recycle bin terintegrasi.

> **Production-Ready**: Fully environment-based configuration, zero hardcoded secrets, deployment-ready with PM2 orchestration.

## ✨ Fitur Utama

### 🎯 Job Management
- **Template Management** - Buat dan kelola template preventive job
- **Execution Tracking** - Track semua eksekusi job dengan timeline status
- **Schedule Customization** - Support interval harian/mingguan/custom dates
- **Asset Assignment** - Assign job ke multiple aset/mesin
- **Soft Delete & Recycle Bin** - Hapus job dengan opsi restore

### ✅ Checklist System
- **Dynamic Checklist** - Support 3 tipe item: Numeric, Free Text, Dropdown
- **Result Tracking** - Simpan hasil checklist dengan status OK/NG
- **Attachment Support** - Upload foto/dokumen pendukung
- **WhatsApp Integration** - Kirim checklist link via WhatsApp (no login required)
- **Compliance Report** - Generate laporan compliance berdasarkan hasil checklist

### 📊 Dashboard & Reports
- **Real-time Dashboard** - Overview job status, completion rate, compliance
- **Daily/Project Reports** - Export PDF & Excel dengan filtering
- **Status History** - Track perubahan status dengan reason & timestamp
- **Execution Timeline** - Visual timeline dari semua job executions

### 👥 User Management
- **Role-Based Access** - PIC, Technician, Admin roles
- **Team Assignment** - Assign personil berdasarkan hierarki atasan
- **Audit Trail** - Log semua perubahan dengan user info & timestamp

### 🔐 Advanced Features
- **Google Calendar Sync** - Auto-sync job schedule ke Google Calendar
- **Maintenance Mode** - Pause/resume sistem tanpa downtime
- **Multi-tenant Support** - Support multiple lines & divisions
- **Data Export** - Export execution data ke Excel & PDF

## 🛠 Tech Stack

**Backend:**
- Django 5.2.8
- Python 3.11+
- PostgreSQL 16

**Production Stack:**
- Gunicorn 21.2.0 (WSGI server)
- Celery 5.3.4 (task queue)
- Redis 5.0.1 (message broker & cache)
- WhiteNoise 6.6.0 (static files)
- PM2 (process manager)

**Frontend:**
- Bootstrap 5.3.3
- Bootstrap Icons
- Font Awesome 6
- JavaScript ES6+

**External Services:**
- Google Calendar API
- WhatsApp Business API (Fontte)
- Google Sheets API

## 📋 Requirements

- **Python** 3.11+
- **PostgreSQL** 16
- **Redis** 6.0+ (untuk production)
- **pip** (Python package manager)
- **Git**
- **PM2** (optional, untuk production orchestration)

Semua dependencies Python sudah didefinisikan di `requirements.txt`

## 🚀 Quick Start - Development

### 1. Clone Repository
```bash
git clone https://github.com/fastabiqhidayatulah/proyek_manajemen_job.git
cd proyek_manajemen_job
```

### 2. Setup Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
# Copy template
cp .env.example .env

# Edit .env dengan nilai development (atau gunakan defaults)
```

**Development defaults** (sudah tersedia di `.env.example`):
```bash
DJANGO_ENVIRONMENT=development
DEBUG=True
DB_NAME=proyek_management_job
DB_USER=manajemen_app_user
DB_PASSWORD=<your-password>
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 6. Run Development Server
```bash
python manage.py runserver
```
Akses: `http://localhost:8000`

---

## 🚀 Production Deployment

### Environment Setup
```bash
# Copy template
cp .env.example .env

# Edit .env dengan production values:
DJANGO_ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<generate-strong-key>
DB_HOST=<database-server>
DB_PASSWORD=<secure-password>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECURE_SSL_REDIRECT=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
```

### Option 1: Using PM2 (Recommended)

**Install PM2:**
```bash
npm install -g pm2
```

**Start Services:**
```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

**View Logs:**
```bash
pm2 logs
pm2 monit
```

### Option 2: Using Batch Scripts (Windows)

**Terminal 1 - Gunicorn:**
```bash
run_gunicorn.bat
```

**Terminal 2 - Celery Worker:**
```bash
run_celery_worker.bat
```

**Terminal 3 - Celery Beat:**
```bash
run_celery_beat.bat
```

### Option 3: Using Direct Commands

```bash
# Set environment
set DJANGO_ENVIRONMENT=production

# Collect static files
python manage.py collectstatic --noinput

# Run Gunicorn
gunicorn config.wsgi:application --bind 127.0.0.1:8001 --workers 4

# In another terminal - Celery worker
celery -A config worker --loglevel=info --concurrency=4

# In another terminal - Celery beat
celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Reverse Proxy Setup (Caddy)

```bash
# Copy template
cp Caddyfile.example Caddyfile

# Edit with your domain:
# yourdomain.com {
#   reverse_proxy localhost:8001
# }

# Run Caddy
caddy run
```

---

## 📁 Project Structure

```
proyek_manajemen_job/
├── config/                          # Django configuration
│   ├── settings.py                 # Environment-based settings ⭐
│   ├── settings_production.py      # Production wrapper
│   ├── wsgi.py                     # WSGI application
│   ├── asgi.py                     # ASGI application
│   ├── celery.py                   # Celery configuration
│   ├── urls.py                     # URL routing
│   └── credentials/                # 🔒 Credentials (git-ignored)
│
├── core/                            # Core application
│   ├── models.py                   # Database models
│   ├── views.py                    # View functions
│   ├── forms.py                    # Django forms
│   ├── admin.py                    # Admin customization
│   ├── services/                   # Business logic services
│   ├── templatetags/               # Custom template tags
│   ├── management/                 # Django management commands
│   ├── migrations/                 # Database migrations
│   ├── templates/
│   │   ├── base.html              # Base template
│   │   ├── dashboard.html         # Main dashboard
│   │   └── core/                  # App-specific templates
│   └── static/                     # CSS, JS, images
│
├── preventive_jobs/                 # Preventive Job Management
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── recycle_bin_views.py        # Soft delete logic
│   ├── whatsapp_utils.py           # WhatsApp integration
│   ├── migrations/
│   ├── templates/
│   ├── static/
│   └── management/
│
├── meetings/                        # Meeting Management
├── inventory/                       # Inventory Management
├── toolkeeper/                      # Toolkeeper Management
│
├── scripts/                         # Automation scripts
│   ├── backup.bat                  # Database backup (batch)
│   ├── backup_automation.ps1       # Automated backup (PowerShell)
│   ├── backup_gdrive.bat           # Backup to Google Drive
│   ├── setup_ngrok.ps1             # ngrok setup
│   ├── setup_scheduler.ps1         # Windows Task Scheduler
│   ├── start_django_service.bat    # Django service starter
│   └── test_backup.bat             # Backup testing
│
├── panduan/                         # Documentation & Guides
├── documentation/                   # Technical documentation
│
├── .env.example ⭐                 # Environment variables template
├── ecosystem.config.js ⭐          # PM2 configuration
├── Caddyfile.example ⭐            # Reverse proxy template
├── run_gunicorn.bat ⭐             # Gunicorn startup
├── run_celery_worker.bat ⭐        # Celery worker startup
├── run_celery_beat.bat ⭐          # Celery beat startup
├── requirements.txt                 # Python dependencies
├── manage.py                        # Django CLI
└── README.md                        # This file
```

⭐ = New in production-ready release

## 🔑 Environment Variables

All configuration via `.env` file. See `.env.example` for complete reference.

**Critical Settings:**
```bash
# Deployment
DJANGO_ENVIRONMENT=production        # development, staging, production
DEBUG=False                          # Must be False in production
SECRET_KEY=your-50-char-key         # Generate with secrets.token_urlsafe(50)

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=proyek_management_job
DB_USER=manajemen_app_user
DB_PASSWORD=<secure-password>
DB_HOST=localhost                    # Or your database server
DB_PORT=5432

# Cache & Message Queue
REDIS_URL=redis://localhost:6379/0
CACHE_BACKEND=django_redis          # Or locmem for development

# Security (Production)
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000        # 1 year

# Storage & Files
STATIC_ROOT=/data/management-job/static
MEDIA_ROOT=/data/management-job/media
LOG_DIR=/logs/management-job

# External APIs
GOOGLE_CALENDAR_CREDENTIALS_FILE=config/credentials/google-calendar-sa.json
FONTTE_API_TOKEN=<your-fontte-token>
WABOT_API_URL=<your-wabot-url>
```

Complete list available in `.env.example` (59+ variables)

---

## 💾 Database Backups

Automated backup scripts provided:

**Automatic Backups (Windows Task Scheduler):**
```bash
# Setup scheduled backup (daily at 02:00)
scripts\setup_scheduler.ps1
```

**Manual Backup:**
```bash
# Full backup with Google Drive upload
scripts\backup_gdrive.bat

# Simple local backup
scripts\backup.bat

# Test backup
scripts\test_backup.bat
```

Backup files stored in: `C:\backup\management-job\`
(Configurable via `BACKUP_PATH` in `.env`)

---

## 📊 Database Information

**Database Name:** `proyek_management_job`
**Default User:** `manajemen_app_user`
**Default Port:** 5432

**Supported Versions:**
- PostgreSQL 12+
- Recommended: PostgreSQL 16

**Connection Features:**
- Connection pooling with CONN_MAX_AGE
- Health checks enabled
- Transaction isolation: read_committed

---

## 🔄 Key Features Explanation

### Preventive Job Management
- **Template-based Jobs** - Create reusable job templates with checklists
- **Automatic Scheduling** - System generates executions berdasarkan schedule configuration
- **Status Workflow** - Scheduled → In Progress → Done → Closed
- **Soft Delete** - Delete dengan opsi restore via recycle bin
- **Compliance Tracking** - Track completion rate per job/template

### WhatsApp Integration
- **Share Checklist via WhatsApp** - Generate share link, kirim ke personil via WhatsApp
- **Anonymous Fill** - Personil bisa isi checklist tanpa login
- **Result Tracking** - Semua submissions ter-track dengan nama/timestamp

### Execution Tracking
- **Real-time Status** - Update status dari Scheduled → Done → Closed
- **Assignment Management** - Assign ke personil/team
- **Audit Trail** - Track semua status changes dengan reason
- **Attachments** - Upload supporting documents/photos

### Recycle Bin System
- **Soft Delete** - Template/Job tidak langsung dihapus, masuk recycle bin
- **Restore Option** - Restore dari recycle bin dengan related data
- **Permanent Delete** - Hard delete jika tidak perlu lagi
- **Audit Trail** - Track deleted_by + deleted_at

## 📊 Database Models

### Core Models
- `CustomUser` - Extended user model dengan nomor telepon
- `Personil` - Employee/technician data
- `Aset` - Machine/equipment inventory
- `Mesin` - Sub-asset details

### Preventive Job Models
- `PreventiveJobTemplate` - Master job template
- `PreventiveJobExecution` - Individual job execution
- `ChecklistTemplate` - Checklist definition
- `ChecklistItem` - Individual checklist item
- `ChecklistResult` - Checklist submission result

### Supporting Models
- `ExecutionStatusLog` - Status change history
- `ChecklistShareLog` - WhatsApp share tracking
- `WhatsAppContact` - WhatsApp recipient list

## 🔐 Security Features

- **CSRF Protection** - All forms protected dengan CSRF token
- **Permission System** - Role-based access control
- **Input Validation** - Server-side validation untuk semua inputs
- **Soft Delete** - Prevent accidental permanent deletion
- **Audit Trail** - Complete change history

## 📱 API Endpoints

### Execution Management
- `GET /preventive/execution/` - List semua execution
- `GET /preventive/execution/{id}/detail/` - Detail execution
- `POST /preventive/execution/{id}/assign/` - Assign execution
- `GET /preventive/execution/{id}/checklist-modal/` - Load checklist items
- `POST /preventive/execution/{id}/save-checklist/` - Save checklist result

### Template Management
- `GET /preventive/template/` - List templates
- `POST /preventive/template/` - Create template
- `GET /preventive/template/{id}/detail/` - Template detail
- `DELETE /preventive/template/{id}/delete/` - Soft delete template

### Recycle Bin
- `GET /preventive/recycle-bin/` - View deleted items
- `POST /preventive/recycle-bin/{id}/restore/` - Restore item
- `DELETE /preventive/recycle-bin/{id}/delete/` - Permanent delete

## 🏗️ Troubleshooting & Support

### Common Issues

**Port Already in Use**
```bash
# Find what's using port 8001
netstat -ano | findstr :8001

# Kill process (replace PID)
taskkill /PID <PID> /F
```

**Database Connection Error**
```bash
# Verify PostgreSQL is running
# Check .env database credentials
# Ensure database exists and user has permissions
psql -h localhost -U manajemen_app_user -d proyek_management_job
```

**Static Files Not Loading**
```bash
# Recollect static files
python manage.py collectstatic --clear --noinput

# Check STATIC_ROOT path in .env
```

**Celery Tasks Not Running**
```bash
# Check Redis connection
redis-cli ping

# Verify Celery worker is running
# Check logs in C:\logs\management-job\celery_worker.log

# Clear celery tasks
celery -A config purge
```

**Permission Denied on Windows Services**
```bash
# Run terminal as Administrator
# Check log files: C:\logs\management-job\
```

### Logs Location

```
C:\logs\management-job\
├── django.log          # Django application logs
├── errors.log          # Error logs only
├── celery.log          # Celery task logs
└── gunicorn_*.log      # Gunicorn server logs (if using PM2)
```

### Monitoring

**PM2 Dashboard:**
```bash
pm2 monit
pm2 logs
pm2 save
```

**Database Monitoring:**
```bash
# Check active connections
SELECT * FROM pg_stat_activity;

# Check slow queries (enable query logging in settings)
```

**Log Monitoring:**
```bash
# Watch Django logs in real-time
tail -f C:\logs\management-job\django.log
```

---

## 📚 Documentation Files

Key documentation provided:

| File | Description |
|------|-------------|
| `.env.example` | Complete environment variables reference |
| `DEPLOYMENT_CLEAN_SETUP.md` | Fresh server deployment guide |
| `WINDOWS_SERVICE_PM2_SETUP.md` | PM2 setup for Windows services |
| `PERMISSION_GUIDE.md` | User roles and permissions documentation |
| `COMPATIBILITY_CHECKLIST.md` | Server compatibility requirements |
| `panduan/` | Indonesian setup guides |

---

## 🔄 Version History

### v2.0.0 - Production-Ready Release (May 2026)
- ✅ Environment-based configuration (.env system)
- ✅ Production WSGI server (Gunicorn)
- ✅ Task queue (Celery + Redis)
- ✅ PM2 process management
- ✅ Zero hardcoded secrets
- ✅ Automated backups with scheduling
- ✅ Reverse proxy support (Caddy)
- ✅ Complete logging infrastructure
- ✅ Deployment-ready with guides

### v1.0.0 - Initial Release (December 2025)
- ✅ Preventive Job Management System
- ✅ Recycle Bin Implementation
- ✅ WhatsApp Integration
- ✅ Google Calendar Sync
- ✅ Compliance Reporting

---

## 🤝 Contributing

1. Fork repository ini
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

Project ini menggunakan lisensi MIT. Lihat file `LICENSE` untuk details.

## 👨‍💻 Author

**Fastabiq Hidayatulah**
- GitHub: [@fastabiqhidayatulah](https://github.com/fastabiqhidayatulah)

## 🐛 Issues & Support

Jika menemukan bug atau ada pertanyaan:
1. Buka GitHub Issue
2. Sertakan screenshot/error message
3. Jelaskan steps untuk reproduce issue

## 🎓 Resources & Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.0/)
- [Google Calendar API](https://developers.google.com/calendar)

## 📦 Latest Version

**v1.0.0** - December 2025

### Latest Changes
- ✅ Recycle Bin System Implementation
- ✅ Checklist Preview Modal
- ✅ WhatsApp Integration untuk Share Checklist
- ✅ Compliance Report Generation
- ✅ Google Calendar Sync
- ✅ Database Soft Delete Support

---

**Last Updated:** December 13, 2025

Made with ❤️ for better preventive maintenance management
