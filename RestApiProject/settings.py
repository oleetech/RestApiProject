"""
Django settings for RestApiProject project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-^8ag+cl75j$!soezrs+z-z9mjuz5+iibt))x7*zuu%1@%)i_!t'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',  # CORS ব্যবস্থাপনার জন্য
    'rest_framework',  # Django Rest Framework
    'rest_framework_simplejwt',  # JWT Token Authentication
    'drf_yasg',  # API ডকুমেন্টেশনের জন্য Swagger
    'djoser',  # Djoser কাস্টম ইউজার ম্যানেজমেন্টের জন্য
    'authentication', # My Authentication App
    'attendance', # Attendance App
]

AUTH_USER_MODEL = 'authentication.CustomUser'  # আপনার অ্যাপের নাম দিয়ে 'your_app_name' রিপ্লেস করুন 

LANGUAGE_CODE = 'en-us'  # Default language
TIME_ZONE = 'UTC'
USE_I18N = True  # Enable internationalization (i18n)
USE_L10N = True  # Enable localization (l10n)
USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    ('bn', 'Bengali'),
    ('hi', 'Hindi'),
    ('zh', 'Chinese'),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),  # Global locale directory if translations are global
    os.path.join(BASE_DIR, 'attendance', 'locale'),  # App-specific locale directory
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS Middleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',


]

# RestApiProject/settings.py

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # সব API-তে অটেনটিকেশন আবশ্যক
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # JWT টোকেন ব্যবহৃত হবে
        'rest_framework.authentication.SessionAuthentication',  # সেশন ব্যবহৃত হবে
    ),

    'DEFAULT_THROTTLE_RATES': {
        'user': '100/day',  # Limit authenticated users to 100 requests per day
        'anon': '10/hour',  # Limit unauthenticated users to 10 requests per hour
    }
}

# JWT Token-এর সময়সীমা নির্ধারণ
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=240),  # JWT Access Token এর সময়সীমা
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),  # JWT Refresh Token এর সময়সীমা
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
}






# Add the following if not already present
LOGIN_URL = 'login'  # Redirect to login if not logged in
LOGOUT_URL = 'logout'  # Redirect to logout
LOGIN_REDIRECT_URL = 'home'  # Redirect after login
LOGOUT_REDIRECT_URL = 'home'  # Redirect after logout

# RestApiProject/settings.py

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # SMTP ব্যবহার
EMAIL_HOST = 'business39.web-hosting.com'  # আপনার SMTP সার্ভারের ঠিকানা
EMAIL_PORT = 465  # SSL এর জন্য পোর্ট
EMAIL_USE_SSL = True  # SSL এনক্রিপশন সক্রিয়
EMAIL_HOST_USER = 'olee@kreatech.ca'  # আপনার ইমেল অ্যাড্রেস
EMAIL_HOST_PASSWORD = 'olee@kreatech'  # ইমেলের পাসওয়ার্ড
DEFAULT_FROM_EMAIL = 'olee@kreatech.ca'  # ডিফল্ট প্রেরক ইমেল

CORS_ALLOW_ALL_ORIGINS = True  # সব উত্সকে অনুমতি দেওয়া
# CORS_ALLOWED_ORIGINS = [

# 'http://127.0.0.1:4000',

# ] # Add other allowed origins as needed



ROOT_URLCONF = 'RestApiProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  

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

WSGI_APPLICATION = 'RestApiProject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# Add this line
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# You might also want to ensure you have these settings
STATIC_URL = '/static/'

# Additional settings for static files if necessary
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # where your static files are during development
]
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
