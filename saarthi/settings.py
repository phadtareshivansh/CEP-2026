"""
Django settings for saarthi project.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Environment detection
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'  # Default to True for development

# Build ALLOWED_HOSTS - WSGI wrapper handles dynamic Vercel preview URLs
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'cep-2026-ivory.vercel.app']

# Support environment variable for explicit hosts
env_hosts = os.environ.get('ALLOWED_HOSTS', '')
if env_hosts:
    ALLOWED_HOSTS.extend(env_hosts.split(','))

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Security: Load from environment variables
# In production, SECRET_KEY MUST be set via environment variable
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        # Development fallback - NEVER use in production
        SECRET_KEY = 'django-insecure-dev-key-only-for-development-never-use-in-production'
    else:
        raise ValueError('SECRET_KEY environment variable is required for production')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'quiz',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'quiz.middleware.SessionTimeoutMiddleware',  # ERP-style session timeout
]

ROOT_URLCONF = 'saarthi.urls'

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

WSGI_APPLICATION = 'saarthi.wsgi.application'

# Database configuration for local dev (SQLite) and production (PostgreSQL)
database_url = os.environ.get('DATABASE_URL')

if database_url and database_url.strip():  # Only use if DATABASE_URL is actually set and not empty
    # Production: Use PostgreSQL (from environment variable)
    import dj_database_url
    try:
        DATABASES = {
            'default': dj_database_url.config(
                default=database_url,
                conn_max_age=600,
                conn_health_checks=True,
            )
        }
    except ValueError:
        # Fallback to SQLite if DATABASE_URL is invalid (e.g., during build without env vars)
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
else:
    # Development/Build: Use SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files configuration for production
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# WhiteNoise configuration for efficient static file serving
# Use CompressedStaticFilesStorage (no manifest) - WhiteNoise serves files directly
# Manifest-based storage causes issues in serverless environments (Vercel/Lambda)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS Configuration for API access
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:8000",
    "http://localhost:8080",
]

# Add Vercel URLs for production
if not DEBUG:
    CORS_ALLOWED_ORIGINS.extend([
        "https://cep-2026-ivory.vercel.app",
        "https://*.vercel.app",
    ])

# Backend API URL (environment-aware)
if DEBUG:
    BACKEND_API_URL = os.environ.get('BACKEND_API_URL', 'http://localhost:5000/api')
else:
    BACKEND_API_URL = os.environ.get('BACKEND_API_URL', 'https://cep-2026-ivory.vercel.app/api')

# =============== ERP-STYLE SECURITY SETTINGS ===============

# Session Configuration (30-minute timeout like ERP systems)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Store in database for security
SESSION_COOKIE_AGE = 1800  # 30 minutes in seconds
SESSION_COOKIE_HTTPONLY = True  # Prevent JS access to session cookie
SESSION_COOKIE_SECURE = not DEBUG  # True in production, False in development
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Session expires when browser closes
SESSION_SAVE_EVERY_REQUEST = True  # Update last activity timestamp

# CSRF Protection
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = not DEBUG  # True in production, False in development
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:5000',
    'http://127.0.0.1:5000',
    'http://localhost:8080',
]

# Add Vercel URLs for production
if not DEBUG:
    CSRF_TRUSTED_ORIGINS.extend([
        'https://cep-2026-ivory.vercel.app',
        'https://*.vercel.app',
    ])

# Security Headers
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
}

# Login Attempt Tracking (ERP-style account lockout)
MAX_LOGIN_ATTEMPTS = 5
LOCK_TIME_MINUTES = 15
