"""
Django settings for school_api project, optimized for Railway production deployment.
"""
import os
import dj_database_url
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- CORE SETTINGS ---

# 1. DEBUG Status: Read from environment, default to False (production mode)
DEBUG = os.environ.get('DJANGO_DEBUG') == 'True'

# 2. SECRET_KEY: Read from Railway environment variables
# If DEBUG is True, it uses the fallback key for local testing.
# If DEBUG is False (production), it MUST load the key from the environment.
SECRET_KEY = os.environ.get(
    'SECRET_KEY', 
    'a-safe-fallback-key-for-local-use-only-do-not-use-in-production' 
) 

# Security check: Raise an error if we are in production but the secret key is missing/default.
if not SECRET_KEY or (SECRET_KEY.endswith('-do-not-use-in-production') and not DEBUG):
    raise Exception("SECRET_KEY environment variable is not set correctly for production!")

# ALLOWED_HOSTS for Railway deployment
ALLOWED_HOSTS = ['school-backend-cf1o.onrender.com',  # <--- YOUR LIVE RENDER DOMAIN
    '.onrender.com',                      # <--- Allows any Render subdomain
    '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'corsheaders',   
    'django.contrib.admin',
    'django.contrib.auth',
    'core', # Assuming this is your main app
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',   
    'rest_framework.authtoken',
    'background_task',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Whitenoise is essential for serving static files in production on Railway
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'school_api.urls'
WSGI_APPLICATION = 'school_api.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ... (Password validation settings remain unchanged)

# Internationalization settings remain unchanged
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# --- DATABASE CONFIGURATION ---
# This block replaces the old SQLite configuration. 
# It uses dj_database_url to parse the DATABASE_URL environment variable provided by Railway.
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'), 
        conn_max_age=600
    )
}

# --- STATIC FILES CONFIGURATION ---
# Essential for production deployment with Whitenoise
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# --- REST FRAMEWORK / CORS CONFIGURATION ---
# Allow all origins for CORS (be more restrictive in a final production app)
CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication', 
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'