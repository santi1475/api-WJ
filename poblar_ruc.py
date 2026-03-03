import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.gestion.models import Cliente

def poblar_ultimo_digito():
    clientes = Cliente.objects.all()
    count = 0
    for cliente in clientes:
        if cliente.ruc and len(cliente.ruc) == 11:
            cliente.ultimo_digito_ruc = cliente.ruc[-1]
            cliente.save(update_fields=['ultimo_digito_ruc'])
            count += 1
            
    print(f"Se actualizaron {count} clientes con éxito.")

if __name__ == '__main__':
    poblar_ultimo_digito()
