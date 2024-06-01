from pathlib import Path
import os
import mimetypes
mimetypes.add_type("text/css", ".css", False)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-11=nxj2bwcp3!1ga3p8c1r+=5i)+t13!j4fqa+xpf%^uyg@-++'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*','127.0.0.1','localhost','tokoharapanjaya.com','www.tokoharapanjaya.com']

#MY ADDED SETTINGS
LOGIN_URL = "/"
LOGIN_REDIRECT_URL = "index"
LOGOUT_REDIRECT_URL = 'index'

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
#         'LOCATION': '127.0.0.1:11211',
#     }
# }
#
# CACHE_MIDDLEWARE_SECONDS  = 60 * 5  # 15 minutes

# Application definition

INSTALLED_APPS = [
    # CONFIG FOR APPS
    'Inventory.apps.InventoryConfig',
    'Purchasing.apps.PurcashingConfig',
    'Sales.apps.SalesConfig',
    'Management.apps.ManagementConfig',
    # DEFAULT APPS
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # MY ADDED APPS
    'django.contrib.humanize',
    'mathfilters',
    'django_crontab',
]

MIDDLEWARE = [
    # MY ADDED MIDDLEWARE
    'crum.CurrentRequestUserMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # 'django.middleware.cache.UpdateCacheMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',
    # DEFAULT MIDDLEWARE
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ERP_Harapan.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'ERP_Harapan.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'id'
DATE_FORMAT = "j F"
TIME_FORMAT = "H:i"

USE_L10N = False
USE_I18N = True
USE_TZ = True
TIME_ZONE = 'Asia/Makassar'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/Static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'Static')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'Static'),
)

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
