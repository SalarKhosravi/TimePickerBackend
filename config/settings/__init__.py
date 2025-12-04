import os

settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)