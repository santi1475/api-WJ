
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.gestion.models import TipoRegimenLaboral

regimenes = ["Pequeña Emp.", "Micro Empresa", "ETC."]

print("Iniciando carga de regímenes laborales...")

for reg in regimenes:
    obj, created = TipoRegimenLaboral.objects.get_or_create(descripcion=reg)
    if created:
        print(f"Creado: {reg}")
    else:
        print(f"Ya existe: {reg}")

print("Carga completada.")
