import os
from django.core.wsgi import get_wsgi_application

# Actualizar ruta settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.production') 

application = get_wsgi_application()