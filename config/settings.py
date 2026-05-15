# config/settings.py  — Sipán Trans
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY    = config('SECRET_KEY')
DEBUG         = config('DEBUG', cast=bool, default=False)
ALLOWED_HOSTS = [h.strip() for h in config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',') if h.strip()]


# ── Apps ─────────────────────────────────────────────────────────
INSTALLED_APPS = [
    # Daphne debe ir PRIMERO para reemplazar el servidor ASGI por defecto
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'django_filters',
    'drf_spectacular',
    # ── Sesión 07: Django Channels (WebSockets) ───────────────
    'channels',
    # Nuestras apps del proyecto encomiendas
    'envios',
    'clientes',
    'rutas',
]

# ── Django REST Framework ─────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # útil en desarrollo
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    # Autenticación: JWT primero, luego sesión Django (para la Browsable API)
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    # Permiso global: sólo usuarios autenticados pueden usar la API
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # Filtros globales: DjangoFilter + búsqueda + ordenamiento
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    # Paginación global
    'DEFAULT_PAGINATION_CLASS': 'envios.api.pagination.EncomiendaPagination',
    'PAGE_SIZE': 10,
}

# ── Spectacular (Swagger API Docs) ────────────────────────────────
SPECTACULAR_SETTINGS = {
    'TITLE': 'API Sistema de Gestión de Encomiendas',
    'DESCRIPTION': 'API REST para gestionar el ciclo de vida de encomiendas.\n'
                   'Incluye registro de envíos, cambio de estado, historial y estadísticas.\n\n'
                   '**Cómo autenticarse:**\n'
                   '1. Ejecuta POST /api/v1/auth/token/ con usuario y contraseña\n'
                   '2. Copia el valor del campo "access"\n'
                   '3. Haz clic en "Authorize" (arriba a la derecha)\n'
                   '4. Pega SOLO el token (sin "Bearer ") en el campo y haz clic en Authorize',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}

# ── JWT — Simple JWT ──────────────────────────────────────────────
from datetime import timedelta

SIMPLE_JWT = {
    # Access token válido 8 horas (jornada laboral completa)
    'ACCESS_TOKEN_LIFETIME' : timedelta(hours=8),
    # Refresh token válido 7 días (semana laboral)
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS' : True,   # emite nuevo refresh al usar el anterior
    'BLACKLIST_AFTER_ROTATION': False, # no requiere app extra de blacklist
    'ALGORITHM'             : 'HS256',
    'AUTH_HEADER_TYPES'     : ('Bearer',),
    'AUTH_HEADER_NAME'      : 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD'         : 'id',
    'USER_ID_CLAIM'         : 'user_id',
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise debe ir justo después de SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
        'DIRS': [BASE_DIR / 'templates'],
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

# ── ASGI — Django Channels ────────────────────────────────────────
ASGI_APPLICATION = 'config.asgi.application'

# ── Channel Layers — Redis Backend ───────────────────────────────
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('redis', 6379)],
            'capacity': 1500,          # mensajes máx. en cola por canal
            'expiry': 10,              # segundos antes de descartar mensajes
        },
    },
}


# ── Base de datos ─────────────────────────────────────────────────
DB_ENGINE = config('DB_ENGINE', default='django.db.backends.postgresql')

if DB_ENGINE == 'django.db.backends.sqlite3':
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': BASE_DIR / config('SQLITE_NAME', default='db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE':   DB_ENGINE,
            'NAME':     config('DB_NAME'),
            'USER':     config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST':     config('DB_HOST', default='db'),
            'PORT':     config('DB_PORT', default='5432'),
        }
    }


# ── Validaciones de contraseña ────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ── Internacionalización ──────────────────────────────────────────
LANGUAGE_CODE = 'es-pe'
TIME_ZONE     = 'America/Lima'
USE_I18N      = True
USE_TZ        = True


# ── Archivos estáticos ────────────────────────────────────────────────
STATIC_URL        = 'static/'
STATIC_ROOT       = BASE_DIR / 'staticfiles'
STATICFILES_DIRS  = [BASE_DIR / 'static']
MEDIA_URL         = '/media/'
MEDIA_ROOT        = BASE_DIR / 'media'

# WhiteNoise: sirve archivos estáticos comprimidos con Daphne
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ── Autenticación ────────────────────────────────────────────────
LOGIN_URL           = '/login/'
LOGIN_REDIRECT_URL  = '/'
LOGOUT_REDIRECT_URL = '/login/'


# ── Sesiones (8 horas de jornada laboral) ───────────────────────
SESSION_ENGINE                  = 'django.contrib.sessions.backends.db'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE              = 60 * 60 * 8   # 8 horas
SESSION_COOKIE_SECURE           = False           # True en producción
SESSION_COOKIE_NAME             = 'sipantrans_session'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ── Caché con Redis ──────────────────────────────────────────────
REDIS_URL = config('REDIS_URL', default='redis://redis:6379/0')

CACHES = {
    'default': {
        'BACKEND' : 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS' : {
            'CLIENT_CLASS'         : 'django_redis.client.DefaultClient',
            'IGNORE_EXCEPTIONS'    : True,   # Si Redis cae, la API sigue funcionando
            'COMPRESSOR'           : 'django_redis.compressors.zlib.ZlibCompressor',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50},
        },
        'KEY_PREFIX': 'sipantrans',          # Prefijo para evitar colisiones
        'TIMEOUT'   : 60 * 5,               # 5 minutos por defecto
    }
}

# Tiempos de expiración por tipo de dato (en segundos)
CACHE_TTL = {
    'encomiendas_list'   : 60 * 2,    # Listados: 2 minutos (datos cambian frecuente)
    'encomienda_detail'  : 60 * 5,    # Detalle: 5 minutos
    'empleados_list'     : 60 * 30,   # Empleados: 30 minutos (datos estables)
}
