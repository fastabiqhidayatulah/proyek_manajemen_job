# Production Settings untuk Server Lokal
# Copy ke config/settings.py dan modify sesuai environment Anda

"""
Django settings for Proyek Manajemen Job - PRODUCTION (Server Lokal)
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================================
# SECURITY SETTINGS - UNTUK PRODUCTION
# ============================================================================

SECRET_KEY = 'django-insecure-change-this-in-production'  # Ganti dengan SECRET_KEY yang aman

DEBUG = False  # Ubah ke False untuk production!

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '192.168.1.100',  # Ubah sesuai IP server Anda
    # Tambahkan IP/hostname lain yang perlu akses
]

# ============================================================================
# DATABASE - PostgreSQL
# ============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'proyek_manajemen_job',
        'USER': 'django_user',
        'PASSWORD': 'django_password_123',  # Ganti dengan password Anda
        'HOST': 'localhost',  # atau IP PostgreSQL server
        'PORT': '5432',
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 600,
    }
}

# ============================================================================
# STATIC FILES - UNTUK PRODUCTION
# ============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# ============================================================================
# MEDIA FILES
# ============================================================================

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ============================================================================
# LOGGING - DEBUG
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Buat folder logs jika belum ada
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)

# ============================================================================
# TIMEZONE & LANGUAGE
# ============================================================================

TIME_ZONE = 'Asia/Jakarta'  # Ubah sesuai timezone Anda
USE_I18N = True
USE_TZ = True
LANGUAGE_CODE = 'id-id'

# ============================================================================
# SESSION & CACHE SETTINGS
# ============================================================================

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 minggu
SESSION_COOKIE_SECURE = False  # Ubah ke True jika pakai HTTPS
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = False  # Ubah ke True jika pakai HTTPS

# ============================================================================
# INSTALLED APPS (Custom)
# ============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mptt',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ============================================================================
# PASSWORD VALIDATION
# ============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================================================
# CUSTOM USER MODEL
# ============================================================================

AUTH_USER_MODEL = 'core.CustomUser'

# ============================================================================
# MISC SETTINGS
# ============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email configuration (optional)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Untuk production, ganti dengan SMTP provider Anda

# ============================================================================
# SECURITY HEADERS (Untuk Production)
# ============================================================================

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": ("'self'", "cdn.jsdelivr.net"),
    "style-src": ("'self'", "cdn.jsdelivr.net", "'unsafe-inline'"),
}
