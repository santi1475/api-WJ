import os
from celery import Celery

# Establecer configuración por defecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')

app = Celery('core')

# Cargar configuración desde settings usando el prefijo CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodescubrir tareas en todas las apps instaladas (apps/gestion/tasks.py, etc.)
app.autodiscover_tasks()