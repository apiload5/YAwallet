import os
import dj_database_url
from pathlib import Path
from decouple import config
from cryptography.fernet import Fernet
import sys

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================
# SECURITY SETTINGS
# ============================================
SECRET_KEY = config('SECRET_KEY', default='django-insecure-key')
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    'yawallet.onrender.com',
    '*.onrender.com',
    '*',  # Temporary for testing
]

# ============================================
# INSTALLED APPS
# ============================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'jazzmin',
    'apps.core',
    'apps.accounts',
    'apps.wallet',
    'apps.transactions',
    'apps.audit',
    'apps.payments',
    'apps.qr',
    'apps.bills',
    'apps.notifications',
]

# ============================================
# MIDDLEWARE
# ============================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ============================================
# TEMPLATES
# ============================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

# ============================================
# URL & WSGI
# ============================================
ROOT_URLCONF = 'yawallet.urls'
WSGI_APPLICATION = 'yawallet.wsgi.application'

# ============================================
# DATABASE - FIXED with error handling
# ============================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Try to use PostgreSQL if DATABASE_URL is set
try:
    if os.environ.get('DATABASE_URL'):
        print("🔍 DATABASE_URL found, connecting to PostgreSQL...")
        DATABASES['default'] = dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=True
        )
        print("✅ PostgreSQL configured successfully!")
    else:
        print("⚠️ DATABASE_URL not found, using SQLite")
except Exception as e:
    print(f"❌ Database configuration error: {e}")
    print("⚠️ Falling back to SQLite")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ============================================
# AUTH USER MODEL
# ============================================
AUTH_USER_MODEL = 'accounts.User'

# ============================================
# AUTHENTICATION BACKENDS
# ============================================
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# ============================================
# STATIC & MEDIA FILES
# ============================================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Only use WhiteNoise if not DEBUG
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# REST FRAMEWORK
# ============================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
}

# ============================================
# CORS
# ============================================
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:19006",
    "https://yawallet.onrender.com",
    "http://yawallet.onrender.com",
]

# ============================================
# TRANSACTION FEES
# ============================================
TRANSACTION_FEE_PERCENT = float(config('TRANSACTION_FEE_PERCENT', default=1.0))
TRANSACTION_FEE_MIN = float(config('TRANSACTION_FEE_MIN', default=10.0))

# ============================================
# ENCRYPTION
# ============================================
ENCRYPTION_KEY = config('ENCRYPTION_KEY', default=Fernet.generate_key().decode())

# ============================================
# CSRF & SECURITY
# ============================================
CSRF_TRUSTED_ORIGINS = [
    'https://yawallet.onrender.com',
    'http://yawallet.onrender.com',
]

# ============================================
# SESSION SETTINGS
# ============================================
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = True

# ============================================
# LOGIN URLS
# ============================================
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/admin/'

# ============================================
# JAZZMIN ADMIN THEME
# ============================================
JAZZMIN_SETTINGS = {
    "site_title": "YaWallet Admin",
    "site_header": "YaWallet",
    "site_brand": "YaWallet Admin",
    "welcome_sign": "Welcome to YaWallet Admin Panel",
    "copyright": "YaWallet",
    "search_model": "accounts.User",
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Support", "url": "https://yawallet.com/support", "new_window": True},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth": "fas fa-users-cog",
        "accounts.User": "fas fa-user",
        "accounts.KYCDocument": "fas fa-id-card",
        "wallet.Wallet": "fas fa-wallet",
        "transactions.Transaction": "fas fa-exchange-alt",
        "audit.AuditLog": "fas fa-history",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": True,
    "use_google_fonts_cdn": True,
    "show_ui_builder": True,
}

# ============================================
# LOGGING
# ============================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

print("✅ YaWallet settings loaded!")
