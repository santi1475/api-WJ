from django.db import models
from django.conf import settings
from django.utils import timezone

class Cliente(models.Model):
    class RegimenTributario(models.TextChoices):
        RMT = 'RMT', 'Régimen MYPE Tributario'
        ESPECIAL = 'ESPECIAL', 'Régimen Especial'
        RUS = 'RUS', 'Nuevo RUS'
        GENERAL = 'GENERAL', 'Régimen General'

    class TipoEmpresa(models.TextChoices):
        SAC = 'SAC', 'Sociedad Anónima Cerrada'
        EIRL = 'EIRL', 'Empresa Individual de Resp. Ltda.'
        SRL = 'SRL', 'Sociedad Comercial de Resp. Ltda.'
        SA = 'SA', 'Sociedad Anónima'
        PN = 'PN', 'Persona Natural'

    class Categoria(models.TextChoices):
        A = 'A', 'Categoría A'
        B = 'B', 'Categoría B'
        C = 'C', 'Categoría C'

    # IDENTIFICACIÓN
    ruc = models.CharField(max_length=11, unique=True, primary_key=True)
    razon_social = models.CharField(max_length=255)
    propietario = models.CharField(max_length=255)
    dni_propietario = models.CharField(max_length=8, blank=True, null=True)
    fecha_ingreso = models.DateField(blank=True, null=True, verbose_name='Fecha de Ingreso')

    # GESTIÓN
    estado = models.BooleanField(default=True)
    codigo_control = models.IntegerField(null=True, blank=True)
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="clientes_asignados"
    )

    # CLASIFICACIÓN
    regimen_tributario = models.CharField(max_length=20, choices=RegimenTributario.choices, default=RegimenTributario.RMT)
    tipo_empresa = models.CharField(max_length=20, choices=TipoEmpresa.choices, default=TipoEmpresa.PN)
    categoria = models.CharField(max_length=20, choices=Categoria.choices, blank=True, null=True)

    # RÉGIMEN LABORAL
    regimen_laboral_tipo = models.CharField(max_length=100, blank=True, null=True)
    regimen_laboral_fecha = models.DateField(blank=True, null=True)

    # FINANCIERO
    ingresos_mensuales = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    ingresos_anuales = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    libros_societarios = models.IntegerField(default=0)
    selectivo_consumo = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    #Fecha de baja
    fecha_baja = models.DateField(null=True, blank=True, verbose_name='Fecha de Baja')

    def __str__(self):
        return f"{self.ruc} - {self.razon_social}"

class Credenciales(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name="credenciales")
    pe = models.CharField(max_length=50, blank=True, null=True)

    # SUNAT
    sol_usuario = models.CharField(max_length=100, blank=True, null=True)
    sol_clave = models.CharField(max_length=100, blank=True, null=True)

    # DETRACCIONES (J, K, L)
    detraccion_cuenta = models.CharField(max_length=50, blank=True, null=True)
    detraccion_usuario = models.CharField(max_length=100, blank=True, null=True)
    detraccion_clave = models.CharField(max_length=100, blank=True, null=True)

    # INEI (M, N)
    inei_usuario = models.CharField(max_length=100, blank=True, null=True)
    inei_clave = models.CharField(max_length=100, blank=True, null=True)

    # AFP NET
    afp_net_usuario = models.CharField(max_length=100, blank=True, null=True)
    afp_net_clave = models.CharField(max_length=100, blank=True, null=True)

    # VIVA ESSALUD
    viva_essalud_usuario = models.CharField(max_length=100, blank=True, null=True)
    viva_essalud_clave = models.CharField(max_length=100, blank=True, null=True)

    # OTROS
    sis_usuario = models.CharField(max_length=100, blank=True, null=True)
    sis_clave = models.CharField(max_length=100, blank=True, null=True)
    clave_osce = models.CharField(max_length=100, blank=True, null=True)
    clave_sencico = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Creds: {self.cliente.ruc}"


class HistorialBaja(models.Model):
    """Modelo para registrar el historial de todas las bajas de clientes"""
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='historial_bajas')
    fecha_baja = models.DateTimeField(auto_now_add=True)
    fecha_reactivacion = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Reactivación')
    usuario_baja = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="bajas_registradas"
    )
    razon = models.CharField(max_length=255, blank=True, null=True, verbose_name='Razón de la Baja')
    estado = models.CharField(
        max_length=20,
        choices=[('BAJA', 'En Baja'), ('REACTIVADO', 'Reactivado')],
        default='BAJA'
    )

    class Meta:
        ordering = ['-fecha_baja']
        verbose_name = 'Historial de Baja'
        verbose_name_plural = 'Historiales de Bajas'

    def __str__(self):
        return f"{self.cliente.ruc} - {self.cliente.razon_social} ({self.estado})"
