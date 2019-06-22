"""
Django settings for sentinel project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from django.urls import reverse_lazy

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


LOGIN_REDIRECT_URL = reverse_lazy('dashboard')
LOGIN_URL = reverse_lazy('login')
LOGOUT_URL = reverse_lazy('logout')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$^pp)rt=a&hi6qe$!x!6m4@&1k8i1z!bj2v4ocx7e8il65bd=i'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['47.100.23.235']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'huey.contrib.djhuey',

    'djmail',

    'api',
    'ui'
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


ROOT_URLCONF = 'sentinel.urls'

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

WSGI_APPLICATION = 'sentinel.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        "HOST": os.environ['MYSQL_HOST'],
        'PORT': 3306,
        'USER': os.environ['MYSQL_USER'],
        "PASSWORD": os.environ['MYSQL_ROOT_PASSWORD'],
        'NAME': os.environ['MYSQL_DATABASE'],
        'TEST': {'CHARSET': 'UTF8'}
    }
}

CORS_ORIGIN_ALLOW_ALL = True

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'Zh-cn'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# djmail设置
DJMAIL_REAL_BACKEND = "djmail.backends.async.EmailBackend"
DEFAULT_FROM_EMAIL = '528194763@qq.com'
EMAIL_HOST = 'smtp.qq.com'
EMAIL_HOST_USER = '528194763'
EMAIL_PORT = 587
EMAIL_HOST_PASSWORD = 'gfnthuakqdkmbida'
EMAIL_USE_TLS = True

# InfluxDB 设置
INFLUXDB = {
    'host': os.environ['INFLUXDB_HOST'],
    'port': 8086,
    'database': os.environ['INFLUXDB_DB']
}

SERVER_IP = os.environ['SERVER_IP']

# huey 配置

HUEY = {
    'name': 'sentinel-huey',
    'immediate': False,
    'connection': {
            'host': os.environ['REDIS_HOST'],
            'port': 6379,
            'db': 0
    },
    'huey_class': 'huey.RedisHuey',  # Huey implementation to use.
    'consumer': {
        'blocking': True,  # Use blocking list pop instead of polling Redis.
        'workers': 4,  # 默认是线程,表示4个线程
        'scheduler_interval': 1,  # 1s调度一次

    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'static')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

LOG_DIR = os.path.join(BASE_DIR, "log")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            '()': 'sentinel.fm.ExceptionFormatter',
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s'}
    },
    'filters': {
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'default': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, "default.log"),  # 日志输出文件
            'maxBytes': 1024 * 1024 * 20,  # 文件大小
            'backupCount': 5,  # 备份份数
            'formatter': 'simple',  # 使用哪种formatters日志格式
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, "error.log"),
            'maxBytes': 1024 * 1024 * 20,
            'backupCount': 5,
            'formatter': 'simple',
        },
        'api_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, "api.log"),
            'maxBytes': 1024 * 1024 * 20,
            'backupCount': 5,
            'formatter': 'simple',
        }, 'ui_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, "ui.log"),
            'maxBytes': 1024 * 1024 * 20,
            'backupCount': 5,
            'formatter': 'simple',
        },
        'huey_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, "huey.log"),
            'maxBytes': 1024 * 1024 * 20,
            'backupCount': 5,
            'formatter': 'simple',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['default', 'error'],
            'level': 'INFO',
            'propagate': False
        },
        'api': {
            'handlers': ['api_handler'],
            'level': 'INFO',
            'propagate': False
        },   'ui': {
            'handlers': ['ui_handler'],
            'level': 'INFO',
            'propagate': False
        },
        'huey': {
            'handlers': ['huey_handler'],
            'level': 'INFO',
            'propagate': False
        }

    }
}
