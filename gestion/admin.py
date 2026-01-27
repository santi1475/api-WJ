from django.contrib import admin
from .models import Cliente, Credenciales, HistorialEstado

class CredencialesInline(admin.StackedInline):
    model = Credenciales
    can_delete = False
    verbose_name_plural = 'Claves y Accesos'
    
class HistorialInline(admin.TabularInline):
    model = HistorialEstado
    extra = 0
    readonly_fields = ('fecha', 'tipo_evento', 'usuario_responsable', 'created_at')
    can_delete = False
    ordering = ('-fecha',)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    inlines = [CredencialesInline, HistorialInline]
        
    list_display = ('ruc', 'razon_social', 'estado', 'fecha_ingreso', 'responsable')
    search_fields = ('ruc', 'razon_social')
    list_filter = ('estado', 'regimen_tributario')
