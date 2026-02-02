import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get("ADMIN_USERNAME", "admin")
email = os.environ.get("ADMIN_EMAIL", "admin@wj.com")
password = os.environ.get("ADMIN_PASSWORD", "987654321")

if not User.objects.filter(username=username).exists():
    print(f"Iniciando creación de superusuario: {username}")
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superusuario creado exitosamente.")
else:
    print(f"El superusuario '{username}' ya existe. Saltando paso.")