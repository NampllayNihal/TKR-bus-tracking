from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-6_5w7je7*+q-pm2)280-a^u-_run7+w_4k22#^0ose)8pmn+l('

DEBUG = False

# ✅ Allow local testing safely
ALLOWED_HOSTS = [
    "tkr-bus-tracking.onrender.com",
    "localhost",
    "127.0.0.1"
]



INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # ✅ New modular apps
    'users',
    'transport',
    'payments',
    'tracking',
    
    # ✅ REST Framework for future APIs
    'rest_framework',
    
    # ✅ Legacy app (gradual deprecation)
    'busapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ✅ ADD THIS
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'busproject.urls'


# ✅ TEMPLATE CONFIGURATION — PERFECT
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'busapp' / 'templates'],   # ✅ CUSTOM TEMPLATE DIR
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


WSGI_APPLICATION = 'busproject.wsgi.application'


# ✅ DATABASE — PERFECT
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ✅ PASSWORD VALIDATION — DISABLED FOR TESTING (OK FOR COLLEGE PROJECT)
AUTH_PASSWORD_VALIDATORS = []


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'   # ✅ Correct for Hyderabad

USE_I18N = True
USE_TZ = True


# ===============================
# ✅ STATIC FILES CONFIG (VERY IMPORTANT)
# ===============================
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "busapp" / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"



DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
