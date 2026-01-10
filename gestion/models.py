from django.db import models
from django.contrib.auth.models import User
from encrypted_model_fields.fields import EncryptedCharField

class Cliente(models.Model):
    # --- Identificación ---
    razon_social = models.CharField(max_length=255)
    ruc = models.CharField(max_length=11, unique=True)
    codigo_control = models.IntegerField(null=True, blank=True, help_text="Código administrativo interno")
    
    propietario = models.CharField(max_length=255)
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_ingreso = models.DateField()
    
    # --- Clasificación ---
    estado = models.CharField(max_length=20, default='ACTIVO')
    categoria = models.CharField(max_length=50, blank=True) # A, B, C
    
    # --- Finanzas (Foto actual) ---
    ingreso_anual = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ingreso_mensual = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # --- Auditoría ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.razon_social} ({self.ruc})"

class DatosTributarios(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='datos_tributarios')
    
    # Clave SOL
    usuario_sol = models.CharField(max_length=50, blank=True)
    clave_sol = EncryptedCharField(max_length=100, blank=True) # Encriptado
    
    class Regimen(models.TextChoices):
        RMT = 'RMT', 'Régimen Mype Tributario'
        GENERAL = 'GENERAL', 'Régimen General'
        ESPECIAL = 'ESPECIAL', 'Régimen Especial'
        RUS = 'RUS', 'Nuevo RUS'
        
    regimen_tributario = models.CharField(choices=Regimen.choices, max_length=20, blank=True)
    
    # Datos Laborales
    regimen_laboral = models.CharField(max_length=50, blank=True) # Micro Emp., Pequeña Emp.
    fecha_acreditacion_remype = models.DateField(null=True, blank=True)
    
    # --- Auditoría ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Datos Tributarios de {self.cliente}"

class CuentaDetraccion(models.Model):
    
    # --- Auditoría ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='cuenta_detraccion')
    numero_cuenta = models.CharField(max_length=50)
    dni_titular = models.CharField(max_length=15, null=True, blank=True)
    clave = EncryptedCharField(max_length=50, blank=True) # Encriptado

    def __str__(self):
        return self.numero_cuenta

class CredencialPlataforma(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='credenciales')
    
    class Plataforma(models.TextChoices):
        INEI = 'INEI', 'INEI'
        OSCE = 'OSCE', 'OSCE'
        SENSICO = 'SENSICO', 'SENSICO'
        AFP = 'AFP', 'AFP NET'
        SIS = 'SIS', 'SIS'
        ESSALUD = 'ESSALUD', 'Viva Essalud'
        # Puedes agregar más aquí fácilmente
        
    plataforma = models.CharField(choices=Plataforma.choices, max_length=20)
    
    # --- Soft Delete ---
    activo = models.BooleanField(default=True)
    
    # --- Auditoría ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    usuario = models.CharField(max_length=100, blank=True)
    clave = EncryptedCharField(max_length=100) # Encriptado
    
    url_acceso = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.plataforma} - {self.cliente}"