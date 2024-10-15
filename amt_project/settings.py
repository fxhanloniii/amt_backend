"""
Django settings for amt_project project.

Generated by 'django-admin startproject' using Django 4.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from decouple import config
# from channels.middleware import WebSocketMiddleware

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '3.101.60.200', 'ec2-3-101-60-200.us-west-1.compute.amazonaws.com']



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'main_app', # main app
    # Rest Framework
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    # OAUTH Apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'channels',
    
    
    'django_extensions',
    'storages', # AWS S3
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'channels.middleware.WebSocketMiddleware',
    'corsheaders.middleware.CorsMiddleware', # CORS
]

# AWS settings
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME')
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = 'public-read'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'


AUTHENTICATION_BACKENDS = (
    'allauth.account.auth_backends.AuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'amt_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Pointing to the custom templates directory
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

WSGI_APPLICATION = 'amt_project.wsgi.application'

# ASGI application
ASGI_APPLICATION = "amt_project.routing.application"

# Channels layer settings (using Redis as a message broker)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  
        'NAME': config('DB_NAME'),  
        'USER': config('DB_USER'), 
        'PASSWORD': config('DB_PASSWORD'),  
        'HOST': config('DB_HOST'),  
        'PORT': config('DB_PORT'),  
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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-email-password'
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN = 180

# CORS
# ALLOWED_HOSTS = ['3.101.60.200', 'ec2-3-101-60-200.us-west-1.compute.amazonaws.com']

# ALLOWED_HOSTS = ['localhost', '127.0.0.1']

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    'http://localhost:3000',  
    'http://127.0.0.1:3000',
    'http://3.101.60.200',
]

# REST FRAMEWORK 
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# Custom User Registration Serializer
REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'main_app.serializers.CustomRegisterSerializer',
}

# SOCIALS

SOCIALACCOUNT_PROVIDERS = {
    #Google
    'google': {
        'APP': {
            'client_id': config('GOOGLE_CLIENT_ID'),
            'secret': config('GOOGLE_SECRET_KEY'),
            'key': 'KEY'
        }
    },
    #META
    'meta': {
        'APP': {
            'client_id': config('META_CLIENT_ID'),
            'secret': config('META_SECRET_KEY'),
            'key': 'KEY'
        }
    }

}

SITE_ID = 1