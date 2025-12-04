# config/settings/prod.py
from .base import *
from decouple import config

DEBUG = False
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = '/home1/salidevl/api.salidevlab.ir/public_html/static'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home1/salidevl/api.salidevlab.ir/public_html/media'
