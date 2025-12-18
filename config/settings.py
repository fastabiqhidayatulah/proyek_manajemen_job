"""
Django settings for config project.
"""

from pathlib import Path
import os # Kita butuh ini untuk Media files

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Anda bisa biarkan ini dulu untuk development
SECRET_KEY = 'django-insecure-@d)c*7x8h2)d5$)%2j5c_7q1o(u-7-3q=6s#g4y@z+@c7q+c%x'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '192.168.1.*',  # Ganti dengan subnet network Anda
    '*'  # Untuk development saja, jangan di production
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'import_export',

    # Aplikasi pihak ketiga
    'mptt', # Untuk Aset Mesin Tree

    # Aplikasi kita
    'core.apps.CoreConfig', # Nama lengkap aplikasi kita
    'preventive_jobs.apps.PreventiveJobsConfig', # V2 - Preventive Job Management
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.MaintenanceModeMiddleware',  # Maintenance Mode Middleware
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Beritahu Django di mana mencari template HTML global
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.overdue_jobs_context',  # Custom context processor for overdue jobs
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# INI BAGIAN PENTING: Konfigurasi ke PostgreSQL Anda
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'manajemen_pekerjaan_db', # Nama DB yg Anda buat di pgAdmin
        'USER': 'manajemen_app_user',      # User owner DB Anda
        'PASSWORD': 'AppsPassword123!',# GANTI DENGAN PASSWORD ANDA
        'HOST': 'localhost',               # Biarkan 'localhost'
        'PORT': '5432',                    # Port default PostgreSQL
    }
}


# ==============================================================================
# CACHE CONFIGURATION - Performance Optimization
# ==============================================================================
# For development: Use in-memory cache (LocMemCache)
# For production: Use Redis for distributed caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 3600,  # Default cache timeout: 1 hour
        'OPTIONS': {
            'MAX_ENTRIES': 10000  # Maximum cached items
        }
    }
}

# Uncomment below for production with Redis
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#             'CONNECTION_POOL_KWARGS': {'max_connections': 50},
#             'SOCKET_CONNECT_TIMEOUT': 5,
#             'SOCKET_TIMEOUT': 5,
#         },
#         'TIMEOUT': 3600,
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'id-id' # Kita ganti ke Bahasa Indonesia

TIME_ZONE = 'Asia/Jakarta' # Kita ganti ke zona waktu Jakarta

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # Untuk produksi
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')] # Untuk development

# Media files (File Upload dari User)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Memberitahu Django untuk menggunakan model User kustom kita
# Ini HARUS DITAMBAHKAN
AUTH_USER_MODEL = 'core.CustomUser'


# ==============================================================================
# PENGATURAN URL LOGIN & LOGOUT (PERBAIKAN ERROR 404)
# ==============================================================================

# Ke mana user dilempar SETELAH BERHASIL LOGIN
# Kita arahkan ke nama URL 'dashboard' di dalam app 'core'
LOGIN_REDIRECT_URL = 'core:dashboard' 

# Ke mana user dilempar JIKA MENCOBA MENGAKSES HALAMAN YG BUTUH LOGIN
LOGIN_URL = 'core:login'


# ==============================================================================
# PENGATURAN WHATSAPP INTEGRATION (FONTTE atau Custom WABot)
# ==============================================================================
FONTTE_API_TOKEN = 'E6CwLwwzuP8Db6Dud5mn'
FONTTE_API_BASE_URL = 'https://api.fontte.com/v1'

# Custom WABot API Configuration (Preferred jika tersedia)
# Uncomment untuk menggunakan WABot API lokal
WABOT_API_URL = 'http://192.168.10.20:8000'
WABOT_API_KEY = 'e8a3b7d1f9c0e5a6d3b1f8c2e7a4d6b9f2c0e8a5d3b1f7c4e9a6d3b2f8c0e7a5'

# Share Link Configuration
PREVENTIVE_SHARE_TOKEN_MAX_AGE = 7 * 24 * 3600  # 7 hari
PREVENTIVE_SHARE_SIGN_SALT = 'preventive-checklist-share'

# Untuk Ngrok/Public URL (set saat production)
# Format: https://your-ngrok-url.ngrok.io
# Bisa di-set via environment variable DJANGO_PUBLIC_URL
DJANGO_PUBLIC_URL = os.environ.get('DJANGO_PUBLIC_URL', 'http://192.168.10.239:4321')

# Untuk Development: Set False untuk disable actual API sending (just generate links)
# Set True untuk production setelah configure API credentials
FONTTE_API_ENABLED = os.environ.get('FONTTE_API_ENABLED', 'true').lower() == 'true'


# ==============================================================================
# PENGATURAN CSRF - TRUSTED ORIGINS (untuk Ngrok & CORS)
# ==============================================================================
CSRF_TRUSTED_ORIGINS = [
    'https://one-chimp-hardly.ngrok-free.app',
    'https://*.ngrok-free.app',
    'http://192.168.10.239:4321',
    'http://localhost:4321',
    'http://127.0.0.1:4321',
]

# Enable CSRF cookie untuk cross-domain requests
CSRF_COOKIE_SECURE = False  # Set to True di production dengan HTTPS
CSRF_COOKIE_HTTPONLY = False  # Perlu False agar JS bisa akses CSRF token


# ==============================================================================
# PENGATURAN GOOGLE CALENDAR API
# ==============================================================================
GOOGLE_CALENDAR_CREDENTIALS_FILE = os.path.join(BASE_DIR, 'config/credentials/google-calendar-sa.json')
GOOGLE_CALENDAR_ID = 'ges3ra8851qk05jqlsfgjct3h4@group.calendar.google.com'  # Calendar ID Anda