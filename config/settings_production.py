"""
Deprecated: Production settings wrapper for backward compatibility.

All production configuration is now handled in config/settings.py using environment variables.
This file is kept for backward compatibility only - it simply imports from settings.py.

To use production settings:
    1. Set DJANGO_ENVIRONMENT=production in .env
    2. Use config.settings (not config.settings_production)

Usage:
    - Development: python manage.py runserver (uses config.settings)
    - Production: DJANGO_ENVIRONMENT=production python manage.py runserver (uses config.settings with production config)
"""

# Import all settings from the main settings module
from config.settings import *  # noqa: F401, F403

__all__ = [
    'DEBUG', 'SECRET_KEY', 'ALLOWED_HOSTS', 'INSTALLED_APPS', 'MIDDLEWARE',
    'DATABASES', 'CACHES', 'LOGGING', 'STATIC_URL', 'MEDIA_ROOT', 'MEDIA_URL',
    'CSRF_TRUSTED_ORIGINS', 'SECURE_SSL_REDIRECT', 'SESSION_COOKIE_SECURE',

    DEBUG = False
    ALLOWED_HOSTS = [host.strip() for host in os.environ.get('ALLOWED_HOSTS', '').split(',')]
    
    # Require HTTPS
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Optional: Enable HSTS after testing
    # SECURE_HSTS_SECONDS = 31536000  # 1 year
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_HSTS_PRELOAD = True

elif IS_STAGING:
    # Staging configuration
    DEBUG = False
    # Staging can use HTTP with clear indication
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False

else:  # Development
    DEBUG = True
    ALLOWED_HOSTS = ['*']
    CSRF_COOKIE_SECURE = False

# ============================================================================
# SYSTEM CHECK SETTINGS
# ============================================================================
# Silence specific Django checks if needed
SILENCED_SYSTEM_CHECKS = []

# ============================================================================
# DEPLOYMENT CHECKS
# ============================================================================
if IS_PRODUCTION:
    if not SECRET_KEY or SECRET_KEY.startswith('django-insecure'):
        raise ValueError("SECRET_KEY is insecure in production. Set DJANGO_SECRET_KEY environment variable.")
    
    if not os.environ.get('DB_PASSWORD'):
        raise ValueError("DB_PASSWORD must be set in production.")
    
    if ALLOWED_HOSTS == ['*']:
        raise ValueError("ALLOWED_HOSTS must be explicitly configured in production.")
