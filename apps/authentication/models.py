from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        CONTADOR = 'CONTADOR', 'Contador'
        ASISTENTE = 'ASISTENTE', 'Asistente'
        CLIENTE = 'CLIENTE', 'Cliente Viewer'

    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.CONTADOR,
        verbose_name="Rol en el Sistema"
    )
    celular = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"