import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Variables que debes configurar en Railway o hardcodear aquí para una sola ejecución
username = os.environ.get("ADMIN_USERNAME", "admin")
email = os.environ.get("ADMIN_EMAIL", "admin@wj.com")
password = os.environ.get("ADMIN_PASSWORD", "987654321")

if not User.objects.filter(username=username).exists():
    print(f"Creando superusuario: {username}...")
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superusuario creado con éxito.")
else:
    print(f"El usuario {username} ya existe.")