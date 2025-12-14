import os
import socket
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-@f*bff3e&j(v$@9d59!w&2r2h56ufco6)13g+3-984bfr+zriv'

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '*']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'rest_framework',
    'drf_yasg',
    'corsheaders',
    
    'drugs_estimation',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'drugs_estimation.middleware.RedisUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'application.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': True,
        },
    },
]

WSGI_APPLICATION = 'application.wsgi.application'

# Determine DB host: priority
# 1) DJANGO_DB_HOST env var
# 2) host.docker.internal if it resolves (Docker Desktop case)
# 3) 'db' (typical docker-compose service name)
DB_HOST = os.environ.get('DJANGO_DB_HOST')
if not DB_HOST:
    try:
        # quick DNS check - does host.docker.internal resolve here?
        socket.getaddrinfo('host.docker.internal', None)
        DB_HOST = 'host.docker.internal'
    except Exception:
        DB_HOST = os.environ.get('POSTGRES_HOST', 'db')

DB_PORT = int(os.environ.get('DJANGO_DB_PORT', os.environ.get('POSTGRES_PORT', 5432)))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DJANGO_DB_NAME', 'RIP'),
        'USER': os.environ.get('DJANGO_DB_USER', 'root'),
        'PASSWORD': os.environ.get('DJANGO_DB_PASSWORD', 'root'),
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'drugs_estimation' / 'static',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AWS_STORAGE_BUCKET_NAME = 'images'
AWS_ACCESS_KEY_ID = 'root'
AWS_SECRET_ACCESS_KEY = 'rootroot'
AWS_S3_ENDPOINT_URL = 'http://minio:9000'
MINIO_USE_SSL = False

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'drugs_estimation.authentication.RedisTokenAuthentication',  # For API clients (Authorization: Token xxx)
        'drugs_estimation.authentication.RedisCookieAuthentication',  # For browser clients (Cookie)
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'UNAUTHENTICATED_USER': None,
    'UNAUTHENTICATED_TOKEN': None,
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'basic': {
            'type': 'basic'
        },
        'session': {
            'type': 'apiKey',
            'name': 'sessionid',
            'in': 'cookie'
        }
    },
    'USE_SESSION_AUTH': True,
    'LOGIN_URL': '/api-auth/login/',
    'LOGOUT_URL': '/api-auth/logout/',
}

REDIS_HOST = 'redis'
REDIS_PORT = 6379
REDIS_PASSWORD = 'password'

# Токен для асинхронного сервиса
ASYNC_SERVICE_TOKEN = 'a1b2c3d4e5f6g7h8'
ASYNC_SERVICE_URL = 'http://localhost:8081'

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/1',
    }
}

SESSION_COOKIE_AGE = 86400
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
