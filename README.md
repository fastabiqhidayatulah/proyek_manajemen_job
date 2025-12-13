# 🔧 Proyek Manajemen Job

Aplikasi **Preventive Job Management System** berbasis Django untuk mengelola pekerjaan preventif, penjadwalan maintenance, tracking eksekusi, dan checklist inspeksi dengan sistem recycle bin terintegrasi.

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

```
Backend:
- Django 5.2.8
- Python 3.11+
- PostgreSQL 12+

Frontend:
- Bootstrap 5.3.3
- Bootstrap Icons
- Font Awesome 6
- JavaScript ES6+

External Services:
- Google Calendar API
- WhatsApp Business API
- ngrok (untuk local development)
```

## 📋 Requirements

- **Python** 3.11 atau lebih tinggi
- **PostgreSQL** 12 atau lebih tinggi
- **pip** (Python package manager)
- **Git**

### Dependencies
Semua dependencies sudah didefinisikan di `requirements.txt`

## 🚀 Installation

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
Buat file `.env` di root directory:
```
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_URL=postgresql://user:password@localhost:5432/proyek_management_job

GOOGLE_CALENDAR_CREDENTIALS_PATH=config/credentials/google-calendar-sa.json

WHATSAPP_API_KEY=your-whatsapp-api-key
WHATSAPP_PHONE_ID=your-phone-id
```

### 5. Database Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load fixtures (opsional)
python manage.py loaddata initial_data
```

### 6. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

## 🎯 Running the Application

### Development Server
```bash
python manage.py runserver
```
Akses di: `http://localhost:8000`

### Production (using Gunicorn)
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Setup sebagai Windows Service (NSSM)
```bash
# Install NSSM (use provided scripts)
scripts\install_nssm_service.bat

# Start service
net start DjangoPreventiveJobService
```

### Using ngrok untuk Local Tunnel
```bash
# Setup ngrok
scripts\setup_ngrok.ps1

# Run ngrok
ngrok http 8000
```

## 📁 Project Structure

```
proyek_manajemen_job/
├── config/                          # Django configuration
│   ├── settings.py                 # Settings
│   ├── urls.py                     # URL routing
│   ├── wsgi.py                     # WSGI config
│   └── credentials/                # Google Calendar credentials
│
├── core/                            # Core application
│   ├── models.py                   # Database models
│   ├── views.py                    # View functions
│   ├── forms.py                    # Django forms
│   ├── admin.py                    # Admin interface
│   ├── urls.py                     # App URLs
│   ├── templates/                  # HTML templates
│   └── static/                     # CSS, JS, images
│
├── preventive_jobs/                 # Preventive Job Management
│   ├── models.py                   # Job models
│   ├── views.py                    # Job views
│   ├── forms.py                    # Job forms
│   ├── recycle_bin_views.py        # Recycle bin logic
│   ├── whatsapp_utils.py           # WhatsApp integration
│   ├── templates/                  # Job templates
│   ├── static/                     # Job static files
│   ├── migrations/                 # Database migrations
│   └── management/                 # Django management commands
│
├── templates/                       # Global templates
│   ├── base.html                   # Base template
│   ├── dashboard.html              # Dashboard
│   └── core/                       # Core app templates
│
├── static/                          # Global static files
│   ├── css/
│   └── js/
│
├── media/                           # User uploaded files
│   ├── attachments/                # Job attachments
│   ├── logos/                      # Company logos
│   └── preventive_jobs/            # Job related images
│
├── scripts/                         # Utility scripts
│   ├── setup_ngrok.ps1            # ngrok setup
│   ├── install_nssm_service.bat    # Windows service setup
│   └── ...
│
├── panduan/                         # Setup guides
│   ├── QUICK_START_NGROK.md
│   └── NGROK_SETUP_GUIDE.md
│
├── requirements.txt                 # Python dependencies
├── manage.py                        # Django management
└── README.md                        # This file
```

## 🔑 Key Features Explanation

### Preventive Job Management
- **Template-based Jobs** - Create reusable job templates
- **Automatic Scheduling** - System automatically generates executions berdasarkan schedule
- **Status Workflow** - Scheduled → In Progress → Done → Closed
- **Compliance Tracking** - Track compliance rate per job/template

### Checklist System
- **Three Item Types:**
  - **Numeric** - Input nilai dengan min/max validation
  - **Free Text** - Open text untuk observasi/notes
  - **Dropdown** - Select dari predefined options
  
- **Result Storage** - Simpan nilai + status (OK/NG) per item
- **Compliance Report** - Auto-calculate overall status berdasarkan item results

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
