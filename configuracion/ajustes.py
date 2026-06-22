import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

_archivo_env = BASE_DIR / '.env'
if _archivo_env.exists():
    with open(_archivo_env, encoding='utf-8') as _f:
        for _linea in _f:
            _linea = _linea.strip()
            if not _linea or _linea.startswith('#') or '=' not in _linea:
                continue
            _clave, _, _valor = _linea.partition('=')
            _clave = _clave.strip()
            _valor = _valor.strip().strip('"').strip("'")
            if _clave and _clave not in os.environ:
                os.environ[_clave] = _valor

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-dev-key-change-in-production')

DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.empleados',
    'apps.asistencia',
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

ROOT_URLCONF = 'configuracion.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'frontend' / 'plantillas'],
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

WSGI_APPLICATION = 'configuracion.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', os.environ.get('DB_NOMBRE', 'acceso_scanner')),
        'USER': os.environ.get('DB_USER', os.environ.get('DB_USUARIO', 'root')),
        'PASSWORD': os.environ.get('DB_PASSWORD', os.environ.get('DB_CLAVE', 'G@RR0M')),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', os.environ.get('DB_PUERTO', '3306')),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'frontend' / 'estatico']

IP_DISPOSITIVO = os.environ.get('FCX_IP', '10.10.0.237')
PUERTO_DISPOSITIVO = int(os.environ.get('FCX_PUERTO', '4370'))
CLAVE_DISPOSITIVO = int(os.environ.get('FCX_CLAVE', '0'))
TIMEOUT_DISPOSITIVO = int(os.environ.get('FCX_TIMEOUT', '30'))
SERIAL_DISPOSITIVO = os.environ.get('FCX_SERIAL', 'AEYU194660027')

import logging.config
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'archivo': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'registros' / 'django.log',
            'maxBytes': 1048576,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'sincronizacion': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'registros' / 'sincronizacion.log',
            'maxBytes': 1048576,
            'backupCount': 3,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'archivo'],
            'level': 'INFO',
        },
        'apps.asistencia.extraccion': {
            'handlers': ['console', 'sincronizacion'],
            'level': 'INFO',
        },
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
