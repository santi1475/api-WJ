from django.contrib import admin
from .models import Cliente, Credenciales, HistorialBaja, Responsable

class CredencialesInline(admin.StackedInline):
    model = Credenciales
    can_delete = False
    verbose_name_plural = 'Claves y Accesos'
    
class HistorialInline(admin.TabularInline):
    model = HistorialBaja
    extra = 0
    readonly_fields = ('fecha_baja', 'fecha_reactivacion', 'usuario_baja', 'razon', 'estado')
    can_delete = False
    ordering = ('-fecha_baja',)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    inlines = [CredencialesInline, HistorialInline]
        
    list_display = ('ruc', 'razon_social', 'estado', 'fecha_ingreso', 'responsable')
    search_fields = ('ruc', 'razon_social')
    list_filter = ('estado', 'regimen_tributario')

@admin.register(Responsable)
class ResponsableAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'celular', 'activo')
    search_fields = ('nombre',)