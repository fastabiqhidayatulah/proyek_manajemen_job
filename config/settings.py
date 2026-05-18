"""
Django settings for config project.
"""

from pathlib import Path
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment detection
DJANGO_ENVIRONMENT = os.environ.get('DJANGO_ENVIRONMENT', 'development')
IS_PRODUCTION = DJANGO_ENVIRONMENT == 'production'
IS_STAGING = DJANGO_ENVIRONMENT == 'staging'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-@d)c*7x8h2)d5$)%2j5c_7q1o(u-7-3q=6s#g4y@z+@c7q+c%x'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True' if not IS_PRODUCTION else 'False').lower() in ['true', '1', 'yes']

# ALLOWED_HOSTS - Comma-separated list from environment
ALLOWED_HOSTS_STR = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',')]


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
    'meetings.apps.MeetingsConfig', # Meetings & Notulen Management
    'inventory.apps.InventoryConfig', # Inventory Management (Spare Parts)
    'toolkeeper.apps.ToolkeeperConfig', # Tool Keeper Management (Tool Lending System)
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
                'core.context_processors.departemen_context',    # Custom context processor for departemen & bagian
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Database - Configuration from environment variables
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.environ.get('DB_NAME', 'proyek_management_job'),
        'USER': os.environ.get('DB_USER', 'manajemen_app_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', '600')),
    }
}


# ==============================================================================
# CACHE CONFIGURATION - Performance Optimization
# ==============================================================================
CACHE_BACKEND = os.environ.get('CACHE_BACKEND', 'django.core.cache.backends.locmem.LocMemCache')

if 'redis' in CACHE_BACKEND.lower():
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {'max_connections': 50},
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 5,
            },
            'TIMEOUT': int(os.environ.get('CACHE_TIMEOUT', '3600')),
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'management-job-cache',
            'TIMEOUT': int(os.environ.get('CACHE_TIMEOUT', '3600')),
            'OPTIONS': {
                'MAX_ENTRIES': 10000
            }
        }
    }


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
STATIC_URL = '/static/'

if IS_PRODUCTION or IS_STAGING:
    STATIC_ROOT = os.environ.get('STATIC_ROOT', os.path.join(BASE_DIR, 'staticfiles'))
else:
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# Media files (File Upload dari User)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', os.path.join(BASE_DIR, 'media'))


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
# PENGATURAN WHATSAPP INTEGRATION (FONNTE atau Custom WABot)
# ==============================================================================
FONTTE_API_TOKEN = os.environ.get('FONTTE_API_TOKEN', '')
FONTTE_API_BASE_URL = os.environ.get('FONTTE_API_BASE_URL', 'https://api.fontte.com/v1')

# Custom WABot API Configuration (Preferred jika tersedia)
WABOT_API_URL = os.environ.get('WABOT_API_URL', '')
WABOT_API_KEY = os.environ.get('WABOT_API_KEY', '')

# Share Link Configuration
PREVENTIVE_SHARE_TOKEN_MAX_AGE = 7 * 24 * 3600  # 7 hari
PREVENTIVE_SHARE_SIGN_SALT = 'preventive-checklist-share'

# Untuk Ngrok/Public URL (set saat production)
DJANGO_PUBLIC_URL = os.environ.get('DJANGO_PUBLIC_URL', 'http://localhost:8000')

# Untuk Development: Set False untuk disable actual API sending (just generate links)
# Set True untuk production setelah configure API credentials
FONTTE_API_ENABLED = os.environ.get('FONTTE_API_ENABLED', 'true').lower() == 'true'


# ==============================================================================
# PENGATURAN CSRF - TRUSTED ORIGINS
# ==============================================================================
CSRF_TRUSTED_ORIGINS_STR = os.environ.get(
    'CSRF_TRUSTED_ORIGINS',
    'http://localhost:8000,http://127.0.0.1:8000'
)
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in CSRF_TRUSTED_ORIGINS_STR.split(',')]


# ==============================================================================
# PENGATURAN GOOGLE CALENDAR API
# ==============================================================================
GOOGLE_CALENDAR_CREDENTIALS_FILE = os.environ.get(
    'GOOGLE_CALENDAR_CREDENTIALS_FILE',
    os.path.join(BASE_DIR, 'config/credentials/google-calendar-sa.json')
)
GOOGLE_CALENDAR_ID = os.environ.get(
    'GOOGLE_CALENDAR_ID',
    'default@group.calendar.google.com'
)


# ==============================================================================
# CELERY CONFIGURATION (Async Task Queue & Scheduling)
# ==============================================================================
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Celery settings
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Jakarta'
CELERY_ENABLE_UTC = False

# Task configuration
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = int(os.environ.get('CELERY_TASK_TIME_LIMIT', 1800))
CELERY_TASK_SOFT_TIME_LIMIT = int(os.environ.get('CELERY_TASK_SOFT_TIME_LIMIT', 1500))


# ==============================================================================
# EMAIL CONFIGURATION
# ==============================================================================
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'webmaster@localhost')


# ==============================================================================
# SECURITY HEADERS
# ==============================================================================
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True' if IS_PRODUCTION else 'False').lower() == 'true'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True' if IS_PRODUCTION else 'False').lower() == 'true'
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'True' if IS_PRODUCTION else 'False').lower() == 'true'
CSRF_COOKIE_HTTPONLY = os.environ.get('CSRF_COOKIE_HTTPONLY', 'False').lower() == 'true'
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', 31536000 if IS_PRODUCTION else 0))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'True' if IS_PRODUCTION else 'False').lower() == 'true'
SECURE_HSTS_PRELOAD = os.environ.get('SECURE_HSTS_PRELOAD', 'True' if IS_PRODUCTION else 'False').lower() == 'true'
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = os.environ.get('X_FRAME_OPTIONS', 'DENY')


# ==============================================================================
# LOGGING
# ==============================================================================
LOG_DIR = os.environ.get('LOG_DIR', os.path.join(BASE_DIR, 'logs'))
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] %(name)s %(process)d %(thread)d %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(name)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'django_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'django.log'),
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'errors.log'),
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10,
            'level': 'ERROR',
            'formatter': 'verbose',
        },
        'celery_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'celery.log'),
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'django_file', 'error_file'],
        'level': os.environ.get('LOG_LEVEL', 'INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'django_file', 'error_file'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'celery_file', 'error_file'],
            'level': os.environ.get('CELERY_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}