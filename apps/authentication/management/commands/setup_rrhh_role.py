from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Configura el rol y permisos para el usuario RRHH'

    def handle(self, *args, **kwargs):
        role_name = "RRHH"
        self.stdout.write(f"Configurando rol '{role_name}'...")

        # 1. Crear o obtener el Grupo
        group, created = Group.objects.get_or_create(name=role_name)
        if created:
            self.stdout.write(self.style.SUCCESS(f"Grupo '{role_name}' creado."))
        else:
            self.stdout.write(f"Grupo '{role_name}' ya existe.")

        # 2. Definir permisos requeridos (codenames y sus apps si es necesario ser específico)
        # Basado en lo que se vio en front-wj/features/auth/types/permissions.ts
        # y apps/gestion/models.py
        
        # Lista de codenames que el RRHH debería tener
        permissions_codenames = [
            # Cliente
            'view_cliente', 'add_cliente', 'change_cliente',
            # LogEntry (Auditoría - si aplica)
            'view_logentry',
            # Usuarios y Grupos (Para ver sección configuración)
            'view_user', 'change_user',
            'view_group',
            # Historiales
            'view_historialbaja', 'add_historialbaja',
            'view_historialestado',
            # Responsables
            'view_responsable', 'add_responsable',
        ]

        # Buscar los permisos en la base de datos
        perms_to_add = []
        for codename in permissions_codenames:
            try:
                # Intentamos buscar por codename.
                # Si hay duplicados en diferentes apps, esto podria ser ambiguo, 
                # pero usualmente 'view_cliente' es único para el modelo Cliente.
                p = Permission.objects.filter(codename=codename).first()
                if p:
                    perms_to_add.append(p)
                else:
                    self.stdout.write(self.style.WARNING(f"Permiso no encontrado: {codename}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error buscando {codename}: {e}"))

        # 3. Asignar permisos al grupo
        group.permissions.set(perms_to_add)
        self.stdout.write(self.style.SUCCESS(f"Asignados {len(perms_to_add)} permisos al grupo '{role_name}'."))

        # 4. Asignar usuario RRHH al grupo
        User = get_user_model()
        username = "RRHH"
        try:
            user = User.objects.get(username=username)
            user.groups.add(group)
            
            # Limpiar permisos directos para asegurar que use los del grupo
            user.user_permissions.clear()
            
            # Asegurarse que tenga is_staff para entrar al admin si es necesario, 
            # o solo acceso a API. Para API no necesita is_staff, pero si usa Django Admin sí.
            # Por ahora no tocamos is_staff a menos que sea necesario.
            
            self.stdout.write(self.style.SUCCESS(f"Usuario '{username}' añadido al grupo '{role_name}' y permisos directos limpiados."))
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Usuario '{username}' no encontrado. Crea el usuario primero."))

        self.stdout.write(self.style.SUCCESS('Configuración completada.'))
