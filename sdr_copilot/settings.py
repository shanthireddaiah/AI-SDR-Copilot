"""
Django settings for sdr_copilot project.
AI SDR Research Copilot - Enterprise & Fresher Portfolio Edition
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Environment Variable Validation ---
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-ai-sdr-copilot-default-key')
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')

ALLOWED_HOSTS_RAW = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver,*')
ALLOWED_HOSTS = ['*'] if DEBUG else [host.strip() for host in ALLOWED_HOSTS_RAW.split(',')]

AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailOrUsernameModelBackend',
]

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'demo')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

if not SECRET_KEY or SECRET_KEY == 'django-insecure-ai-sdr-copilot-default-key':
    sys.stderr.write("WARNING: Using default Django SECRET_KEY. Set SECRET_KEY in .env for production deployment.\n")

if OPENAI_API_KEY.strip().lower() in ('demo', 'your_openai_api_key_here', ''):
    sys.stdout.write("[INFO] AI SDR Copilot running in zero-dependency Demo Mode (built-in mock intelligence).\n")


# Application definition

INSTALLED_APPS = [
    # Django default core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # AI SDR Custom Apps (7 Modular Apps)
    'accounts.apps.AccountsConfig',
    'dashboard.apps.DashboardConfig',
    'research.apps.ResearchConfig',
    'rag.apps.RagConfig',
    'chat.apps.ChatConfig',
    'outreach.apps.OutreachConfig',
    'settings.apps.SettingsConfig',
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
]

ROOT_URLCONF = 'sdr_copilot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Global templates folder
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

WSGI_APPLICATION = 'sdr_copilot.wsgi.application'


# Database Configuration - Flexible Engine (MySQL / SQLite / PostgreSQL)
_db_engine = os.getenv('DB_ENGINE', 'django.db.backends.sqlite3')
_db_config = {
    'ENGINE': _db_engine,
    'NAME': os.getenv('DB_NAME', BASE_DIR / 'db.sqlite3' if 'sqlite' in _db_engine else 'ai_sdr_db'),
    'USER': os.getenv('DB_USER', 'root'),
    'PASSWORD': os.getenv('DB_PASSWORD', ''),
    'HOST': os.getenv('DB_HOST', '127.0.0.1'),
    'PORT': os.getenv('DB_PORT', '3306'),
}
if 'mysql' in _db_engine:
    _db_config['OPTIONS'] = {
        'charset': 'utf8mb4',
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
    }

DATABASES = {'default': _db_config}


# Password validation
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


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (Uploaded PDF documents)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Authentication URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:index'
LOGOUT_REDIRECT_URL = 'accounts:login'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- Python Logging Configuration ---
LOGS_DIR = BASE_DIR / 'logs'
os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} [{name}:{lineno}] {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'sdr_copilot.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'accounts': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'research': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'outreach': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'rag': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'chat': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
