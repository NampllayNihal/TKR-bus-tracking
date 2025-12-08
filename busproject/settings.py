from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-6_5w7je7*+q-pm2)280-a^u-_run7+w_4k22#^0ose)8pmn+l('

DEBUG = True

# ✅ Allow local testing safely
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'busapp',   # ✅ Your app
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',   # ✅ CSRF protection ON

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
    BASE_DIR / 'busapp' / 'static'
]


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
